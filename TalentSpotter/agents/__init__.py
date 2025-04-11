"""
Intelligent agents package for the AI Recruitment System

This module provides factory functions to get instances of the various
intelligent agents used in the recruitment system, with support for
different LLM providers through Langchain.
"""

import logging
import os
from typing import Dict, Any, Optional, Union

# Import agent classes
from .jd_summarizer import JDSummarizerAgent
from .cv_analyzer import CVAnalyzerAgent
from .matcher import MatcherAgent
from .shortlister import ShortlisterAgent
from .scheduler import SchedulerAgent
from .insights_generator import InsightsGeneratorAgent
from .ranking_algorithm import RankingAlgorithmAgent

# Configure logging
logger = logging.getLogger(__name__)

# Cache for agent instances
_agent_cache = {}

# Get default settings from environment or config
DEFAULT_MODEL_PROVIDER = os.environ.get("DEFAULT_MODEL_PROVIDER", "ollama")
DEFAULT_MODEL_NAME = {
    "ollama": os.environ.get("DEFAULT_OLLAMA_MODEL", "phi-2"),
    "openai": os.environ.get("DEFAULT_OPENAI_MODEL", "gpt-4o")
}

def get_jd_summarizer(model_name: Optional[str] = None, provider: Optional[str] = None) -> JDSummarizerAgent:
    """
    Get an instance of the JD Summarizer agent.
    
    Args:
        model_name: Name of the model to use (defaults to environment setting or phi-2 for ollama)
        provider: Provider of the LLM ('ollama' or 'openai', defaults to environment setting)
        
    Returns:
        JDSummarizerAgent instance
    """
    # Use defaults if parameters are not provided
    provider = provider or DEFAULT_MODEL_PROVIDER
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME.get(provider, "phi-2")
    
    cache_key = f"jd_summarizer_{provider}_{model_name}"
    if cache_key not in _agent_cache:
        logger.info(f"Creating new JD Summarizer agent with model: {model_name} (provider: {provider})")
        _agent_cache[cache_key] = JDSummarizerAgent(model_name=model_name, provider=provider)
    
    return _agent_cache[cache_key]

def get_cv_analyzer(model_name: Optional[str] = None, provider: Optional[str] = None) -> CVAnalyzerAgent:
    """
    Get an instance of the CV Analyzer agent.
    
    Args:
        model_name: Name of the model to use (defaults to environment setting or phi-2 for ollama)
        provider: Provider of the LLM ('ollama' or 'openai', defaults to environment setting)
        
    Returns:
        CVAnalyzerAgent instance
    """
    # Use defaults if parameters are not provided
    provider = provider or DEFAULT_MODEL_PROVIDER
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME.get(provider, "phi-2")
    
    cache_key = f"cv_analyzer_{provider}_{model_name}"
    if cache_key not in _agent_cache:
        logger.info(f"Creating new CV Analyzer agent with model: {model_name} (provider: {provider})")
        _agent_cache[cache_key] = CVAnalyzerAgent(model_name=model_name, provider=provider)
    
    return _agent_cache[cache_key]

def get_matcher(model_name: Optional[str] = None, provider: Optional[str] = None) -> MatcherAgent:
    """
    Get an instance of the Matcher agent.
    
    Args:
        model_name: Name of the model to use (defaults to environment setting or phi-2 for ollama)
        provider: Provider of the LLM ('ollama' or 'openai', defaults to environment setting)
        
    Returns:
        MatcherAgent instance
    """
    # Use defaults if parameters are not provided
    provider = provider or DEFAULT_MODEL_PROVIDER
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME.get(provider, "phi-2")
    
    cache_key = f"matcher_{provider}_{model_name}"
    if cache_key not in _agent_cache:
        logger.info(f"Creating new Matcher agent with model: {model_name} (provider: {provider})")
        _agent_cache[cache_key] = MatcherAgent(model_name=model_name, provider=provider)
    
    return _agent_cache[cache_key]

def get_shortlister(model_name: Optional[str] = None, provider: Optional[str] = None) -> ShortlisterAgent:
    """
    Get an instance of the Shortlister agent.
    
    Args:
        model_name: Name of the model to use (defaults to environment setting or phi-2 for ollama)
        provider: Provider of the LLM ('ollama' or 'openai', defaults to environment setting)
        
    Returns:
        ShortlisterAgent instance
    """
    # Use defaults if parameters are not provided
    provider = provider or DEFAULT_MODEL_PROVIDER
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME.get(provider, "phi-2")
    
    cache_key = f"shortlister_{provider}_{model_name}"
    if cache_key not in _agent_cache:
        logger.info(f"Creating new Shortlister agent with model: {model_name} (provider: {provider})")
        _agent_cache[cache_key] = ShortlisterAgent(model_name=model_name, provider=provider)
    
    return _agent_cache[cache_key]

def get_scheduler(model_name: Optional[str] = None, provider: Optional[str] = None) -> SchedulerAgent:
    """
    Get an instance of the Scheduler agent.
    
    Args:
        model_name: Name of the model to use (defaults to environment setting or phi-2 for ollama)
        provider: Provider of the LLM ('ollama' or 'openai', defaults to environment setting)
        
    Returns:
        SchedulerAgent instance
    """
    # Use defaults if parameters are not provided
    provider = provider or DEFAULT_MODEL_PROVIDER
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME.get(provider, "phi-2")
    
    cache_key = f"scheduler_{provider}_{model_name}"
    if cache_key not in _agent_cache:
        logger.info(f"Creating new Scheduler agent with model: {model_name} (provider: {provider})")
        _agent_cache[cache_key] = SchedulerAgent(model_name=model_name, provider=provider)
    
    return _agent_cache[cache_key]

def get_insights_generator(model_name: Optional[str] = None, provider: Optional[str] = None) -> InsightsGeneratorAgent:
    """
    Get an instance of the Insights Generator agent.
    
    Args:
        model_name: Name of the model to use (defaults to environment setting or phi-2 for ollama)
        provider: Provider of the LLM ('ollama' or 'openai', defaults to environment setting)
        
    Returns:
        InsightsGeneratorAgent instance
    """
    # Use defaults if parameters are not provided
    provider = provider or DEFAULT_MODEL_PROVIDER
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME.get(provider, "phi-2")
    
    cache_key = f"insights_generator_{provider}_{model_name}"
    if cache_key not in _agent_cache:
        logger.info(f"Creating new Insights Generator agent with model: {model_name} (provider: {provider})")
        _agent_cache[cache_key] = InsightsGeneratorAgent(model_name=model_name, provider=provider)
    
    return _agent_cache[cache_key]

def get_ranking_algorithm(model_name: Optional[str] = None, provider: Optional[str] = None) -> RankingAlgorithmAgent:
    """
    Get an instance of the Ranking Algorithm agent.
    
    Args:
        model_name: Name of the model to use (defaults to environment setting or phi-2 for ollama)
        provider: Provider of the LLM ('ollama' or 'openai', defaults to environment setting)
        
    Returns:
        RankingAlgorithmAgent instance
    """
    # Use defaults if parameters are not provided
    provider = provider or DEFAULT_MODEL_PROVIDER
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME.get(provider, "phi-2")
    
    cache_key = f"ranking_algorithm_{provider}_{model_name}"
    if cache_key not in _agent_cache:
        logger.info(f"Creating new Ranking Algorithm agent with model: {model_name} (provider: {provider})")
        _agent_cache[cache_key] = RankingAlgorithmAgent(model_name=model_name, provider=provider)
    
    return _agent_cache[cache_key]

def clear_agent_cache():
    """Clear the agent cache to force new instances to be created."""
    global _agent_cache
    _agent_cache = {}
    logger.info("Agent cache cleared")

def set_default_provider(provider: str):
    """
    Set the default provider for all agents.
    
    Args:
        provider: The provider to use ('ollama' or 'openai')
    """
    global DEFAULT_MODEL_PROVIDER
    if provider not in ['ollama', 'openai']:
        logger.error(f"Invalid provider: {provider}. Must be 'ollama' or 'openai'.")
        return False
    
    DEFAULT_MODEL_PROVIDER = provider
    logger.info(f"Default model provider set to: {provider}")
    
    # Clear cache to force new instances with new provider
    clear_agent_cache()
    return True

def set_default_model(provider: str, model_name: str):
    """
    Set the default model name for a specific provider.
    
    Args:
        provider: The provider to set the default model for
        model_name: The model name to use as default
    """
    global DEFAULT_MODEL_NAME
    if provider not in ['ollama', 'openai']:
        logger.error(f"Invalid provider: {provider}. Must be 'ollama' or 'openai'.")
        return False
    
    DEFAULT_MODEL_NAME[provider] = model_name
    logger.info(f"Default {provider} model set to: {model_name}")
    
    # Clear cache if this affects the current default provider
    if provider == DEFAULT_MODEL_PROVIDER:
        clear_agent_cache()
    
    return True