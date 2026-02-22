"""OpenAI provider implementation"""

import os
import logging
from typing import List, Dict, Any, Optional, Iterator

from .provider import LLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (if None, read from OPENAI_API_KEY env var)
            **kwargs: Additional options (base_url, organization, etc.)
        """
        super().__init__(api_key, **kwargs)
        
        # Get API key from env if not provided
        if self.api_key is None:
            self.api_key = os.environ.get('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("No OpenAI API key found. Set OPENAI_API_KEY env var or pass api_key parameter.")
        
        # Lazy import to avoid dependency if not using OpenAI
        self._client = None
    
    def _get_client(self):
        """Lazy initialize OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    **self.options
                )
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
        return self._client
    
    def _convert_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Convert LLMMessage to OpenAI format"""
        openai_messages = []
        
        for msg in messages:
            openai_msg = {
                "role": msg.role,
                "content": msg.content
            }
            
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls
            
            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id
            
            openai_messages.append(openai_msg)
        
        return openai_messages
    
    def _convert_tools(self, tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        """Convert AgentLang tools to OpenAI function calling format"""
        if not tools:
            return None
        
        openai_tools = []
        for tool in tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name"),
                    "description": tool.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            # Convert params to OpenAI schema
            params = tool.get("params", {})
            for param_name, param_spec in params.items():
                param_type = param_spec.get("type", "string")
                
                # Map AgentLang types to JSON schema types
                type_map = {
                    "string": "string",
                    "int": "integer",
                    "float": "number",
                    "bool": "boolean",
                    "list": "array",
                    "dict": "object"
                }
                
                openai_tools[-1]["function"]["parameters"]["properties"][param_name] = {
                    "type": type_map.get(param_type, "string"),
                    "description": param_spec.get("description", "")
                }
                
                if param_spec.get("required"):
                    openai_tools[-1]["function"]["parameters"]["required"].append(param_name)
            
            openai_tools.append(openai_tool)
        
        return openai_tools
    
    def complete(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Get completion from OpenAI"""
        client = self._get_client()
        
        openai_messages = self._convert_messages(messages)
        openai_tools = self._convert_tools(tools)
        
        try:
            # Build request params
            request_params = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            if openai_tools:
                request_params["tools"] = openai_tools
            
            # Make API call
            response = client.chat.completions.create(**request_params)
            
            # Extract response
            choice = response.choices[0]
            message = choice.message
            
            # Extract tool calls if present
            tool_calls = None
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            
            return LLMResponse(
                content=message.content or "",
                tool_calls=tool_calls,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                finish_reason=choice.finish_reason
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def stream(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Iterator[str]:
        """Stream completion from OpenAI"""
        client = self._get_client()
        
        openai_messages = self._convert_messages(messages)
        openai_tools = self._convert_tools(tools)
        
        try:
            # Build request params
            request_params = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }
            
            if openai_tools:
                request_params["tools"] = openai_tools
            
            # Stream API call
            stream = client.chat.completions.create(**request_params)
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
            
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
