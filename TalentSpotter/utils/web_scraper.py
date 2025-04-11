"""
Ethical Web Scraping Utility

This module provides utility functions for ethically scraping web content
in accordance with best practices for respecting website terms, data privacy,
and load considerations.
"""

import os
import time
import logging
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
import trafilatura
import random

# Configure logging
logger = logging.getLogger(__name__)

# Define a global default delay between requests (in seconds)
DEFAULT_DELAY = 2.0

class EthicalWebScraper:
    """A class for ethical web scraping that respects robots.txt and website load."""
    
    def __init__(self, 
                min_delay: float = 1.0, 
                max_delay: float = 3.0,
                user_agent: str = "EthicalRecruitmentBot/1.0"):
        """
        Initialize the web scraper with ethical settings.
        
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
            user_agent: User agent string to use for requests
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.user_agent = user_agent
        self.last_request_time = 0
        self.robots_cache = {}  # Cache robots.txt rules
    
    def _respect_robots_txt(self, url: str) -> bool:
        """
        Check if scraping the given URL is allowed by robots.txt.
        
        Args:
            url: URL to check against robots.txt
            
        Returns:
            True if scraping is allowed, False if disallowed
        """
        try:
            # Parse the URL to get the domain
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            path = parsed_url.path
            
            # Check if we've already cached the robots.txt for this domain
            if domain not in self.robots_cache:
                # Fetch robots.txt
                robots_url = urljoin(domain, "/robots.txt")
                response = httpx.get(robots_url, 
                                  headers={"User-Agent": self.user_agent},
                                  follow_redirects=True,
                                  timeout=10.0)
                
                if response.status_code == 200:
                    # Parse the robots.txt content
                    disallowed_paths = []
                    current_agent = None
                    our_agent_rules = []
                    all_agent_rules = []
                    
                    for line in response.text.split('\n'):
                        line = line.strip().lower()
                        
                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue
                        
                        # Parse User-agent
                        if line.startswith('user-agent:'):
                            agent = line.split(':', 1)[1].strip()
                            current_agent = agent
                            continue
                        
                        # Parse Disallow
                        if line.startswith('disallow:') and current_agent:
                            disallowed_path = line.split(':', 1)[1].strip()
                            
                            if current_agent == '*':
                                all_agent_rules.append(disallowed_path)
                            elif self.user_agent.lower().startswith(current_agent):
                                our_agent_rules.append(disallowed_path)
                    
                    # Combine rules, with specific agent rules taking precedence
                    disallowed_paths = our_agent_rules if our_agent_rules else all_agent_rules
                    self.robots_cache[domain] = disallowed_paths
                else:
                    # If robots.txt doesn't exist or can't be fetched, assume everything is allowed
                    self.robots_cache[domain] = []
            
            # Check if the URL path is disallowed
            disallowed_paths = self.robots_cache.get(domain, [])
            for disallowed_path in disallowed_paths:
                if disallowed_path and path.startswith(disallowed_path):
                    logger.warning(f"URL {url} is disallowed by robots.txt")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {str(e)}")
            # If there's an error, err on the side of caution
            return False
    
    def _respect_rate_limits(self):
        """Apply rate limiting to avoid overloading servers."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # If we made a request recently, wait before making another
        if time_since_last_request < self.min_delay:
            # Calculate a random delay between min and max
            delay = random.uniform(self.min_delay, self.max_delay)
            remaining_delay = max(0, delay - time_since_last_request)
            
            if remaining_delay > 0:
                logger.debug(f"Rate limiting: waiting {remaining_delay:.2f} seconds")
                time.sleep(remaining_delay)
        
        # Update the last request time
        self.last_request_time = time.time()
    
    def fetch_url(self, url: str, respect_robots: bool = True) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Fetch content from a URL in an ethical manner.
        
        Args:
            url: URL to fetch
            respect_robots: Whether to check and respect robots.txt
            
        Returns:
            Tuple containing (success, content or None, error message or None)
        """
        # Check if scraping is allowed by robots.txt
        if respect_robots and not self._respect_robots_txt(url):
            return (False, None, "Scraping disallowed by robots.txt")
        
        # Apply rate limiting
        self._respect_rate_limits()
        
        try:
            # Fetch the URL
            response = httpx.get(
                url,
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
                timeout=15.0
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                return (True, response.text, None)
            else:
                logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                return (False, None, f"HTTP error {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return (False, None, str(e))
    
    def extract_main_content(self, html_content: str) -> str:
        """
        Extract the main content from HTML using trafilatura.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Extracted main text content
        """
        try:
            extracted_text = trafilatura.extract(html_content)
            if extracted_text:
                return extracted_text
            
            # Fallback to BeautifulSoup if trafilatura fails
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unnecessary elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Extract the text
            text = soup.get_text(separator=' ')
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            # Return the original HTML as a fallback
            return html_content
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a URL with ethical considerations.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped content or error information
        """
        success, content, error = self.fetch_url(url)
        
        if not success:
            return {
                "success": False,
                "error": error,
                "url": url
            }
        
        # Extract main content
        extracted_text = self.extract_main_content(content)
        
        return {
            "success": True,
            "url": url,
            "text": extracted_text,
            "timestamp": time.time()
        }


def get_website_text_content(url: str) -> Dict[str, Any]:
    """
    Helper function to extract the main text content from a website.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dictionary with scraped content or error information
    """
    scraper = EthicalWebScraper()
    return scraper.scrape_url(url)