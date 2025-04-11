"""
Base agent class for the AI Recruitment System.

This module provides the base agent class that all specialized
agents will inherit from, with common functionality for interacting
with LLMs via LangChain.
"""

import os
from typing import Optional, Dict, Any

from langchain.chat_models import ChatOpenAI
from langchain.llms import Ollama


class BaseAgent:
    """
    Base class for all agents in the AI Recruitment System.
    
    This class handles common functionality like LLM initialization and
    provider switching between Ollama and OpenAI.
    """
    
    def __init__(self, model_name: Optional[str] = None, provider: Optional[str] = None):
        """
        Initialize the base agent with an LLM.
        
        Args:
            model_name: Name of the model to use 
                (defaults to env value or "phi-2" for Ollama, "gpt-4o" for OpenAI)
            provider: Provider of the LLM ('ollama' or 'openai', defaults to env value)
        """
        # Determine provider from environment or parameter
        self.provider = provider or os.environ.get("LLM_PROVIDER", "ollama").lower()
        
        # Initialize LLM based on provider
        if self.provider == "openai":
            # For OpenAI, use ChatOpenAI
            self.model_name = model_name or os.environ.get("OPENAI_MODEL", "gpt-4o")
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.7,
                api_key=os.environ.get("OPENAI_API_KEY")
            )
        elif self.provider == "ollama":
            # For Ollama, use Ollama
            self.model_name = model_name or os.environ.get("OLLAMA_MODEL", "phi-2")
            self.llm = Ollama(
                model=self.model_name,
                temperature=0.7
            )
        else:
            # Default to OpenAI if the provider is not recognized
            self.provider = "openai"
            self.model_name = model_name or "gpt-4o"
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.7,
                api_key=os.environ.get("OPENAI_API_KEY")
            )
            
    def switch_provider(self, provider: str, model_name: Optional[str] = None) -> None:
        """
        Switch the LLM provider.
        
        Args:
            provider: Provider of the LLM ('ollama' or 'openai')
            model_name: Name of the model to use (optional)
        """
        self.__init__(model_name=model_name, provider=provider)
        
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration of the agent.
        
        Returns:
            Dictionary containing provider and model name
        """
        return {
            "provider": self.provider,
            "model_name": self.model_name
        }
