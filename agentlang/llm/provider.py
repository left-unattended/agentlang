"""Base LLM provider interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Iterator
from dataclasses import dataclass


@dataclass
class LLMMessage:
    """Standard message format across providers"""
    role: str  # system, user, assistant, tool
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class LLMResponse:
    """Standard response format"""
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    model: str = ""
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize provider.
        
        Args:
            api_key: API key (if None, read from env var)
            **kwargs: Provider-specific options
        """
        self.api_key = api_key
        self.options = kwargs
    
    @abstractmethod
    def complete(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Get completion from LLM.
        
        Args:
            messages: Conversation history
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Available tools for function calling
            **kwargs: Provider-specific options
            
        Returns:
            LLMResponse with content and optional tool calls
        """
        pass
    
    @abstractmethod
    def stream(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream completion from LLM.
        
        Args:
            Same as complete()
            
        Yields:
            Content chunks as they arrive
        """
        pass
    
    @staticmethod
    def detect_provider(model: str) -> str:
        """
        Auto-detect provider from model name.
        
        Args:
            model: Model identifier
            
        Returns:
            Provider name (openai, anthropic, etc.)
        """
        model_lower = model.lower()
        
        if any(x in model_lower for x in ['gpt', 'o1', 'o3']):
            return 'openai'
        elif any(x in model_lower for x in ['claude', 'sonnet', 'opus', 'haiku']):
            return 'anthropic'
        else:
            # Default to OpenAI for unknown models
            return 'openai'
