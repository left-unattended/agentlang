"""Anthropic provider implementation"""

import os
import logging
from typing import List, Dict, Any, Optional, Iterator

from .provider import LLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (if None, read from ANTHROPIC_API_KEY env var)
            **kwargs: Additional options
        """
        super().__init__(api_key, **kwargs)
        
        # Get API key from env if not provided
        if self.api_key is None:
            self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            logger.warning("No Anthropic API key found. Set ANTHROPIC_API_KEY env var or pass api_key parameter.")
        
        # Lazy import to avoid dependency if not using Anthropic
        self._client = None
    
    def _get_client(self):
        """Lazy initialize Anthropic client"""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(
                    api_key=self.api_key,
                    **self.options
                )
            except ImportError:
                raise ImportError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                )
        return self._client
    
    def _convert_messages(self, messages: List[LLMMessage]) -> tuple[str, List[Dict[str, Any]]]:
        """
        Convert LLMMessage to Anthropic format.
        Returns (system_prompt, messages) since Anthropic separates system messages.
        """
        system_prompt = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "system":
                # Extract system messages separately
                system_prompt += msg.content + "\n"
            else:
                anthropic_msg = {
                    "role": "assistant" if msg.role == "assistant" else "user",
                    "content": msg.content
                }
                anthropic_messages.append(anthropic_msg)
        
        return system_prompt.strip(), anthropic_messages
    
    def _convert_tools(self, tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        """Convert AgentLang tools to Anthropic tool use format"""
        if not tools:
            return None
        
        anthropic_tools = []
        for tool in tools:
            anthropic_tool = {
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Convert params to Anthropic schema
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
                
                anthropic_tool["input_schema"]["properties"][param_name] = {
                    "type": type_map.get(param_type, "string"),
                    "description": param_spec.get("description", "")
                }
                
                if param_spec.get("required"):
                    anthropic_tool["input_schema"]["required"].append(param_name)
            
            anthropic_tools.append(anthropic_tool)
        
        return anthropic_tools
    
    def complete(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Get completion from Anthropic"""
        client = self._get_client()
        
        system_prompt, anthropic_messages = self._convert_messages(messages)
        anthropic_tools = self._convert_tools(tools)
        
        try:
            # Build request params
            request_params = {
                "model": model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            if system_prompt:
                request_params["system"] = system_prompt
            
            if anthropic_tools:
                request_params["tools"] = anthropic_tools
            
            # Make API call
            response = client.messages.create(**request_params)
            
            # Extract content
            content = ""
            tool_calls = None
            
            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    if tool_calls is None:
                        tool_calls = []
                    tool_calls.append({
                        "id": block.id,
                        "type": "tool_use",
                        "function": {
                            "name": block.name,
                            "arguments": block.input
                        }
                    })
            
            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                finish_reason=response.stop_reason
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
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
        """Stream completion from Anthropic"""
        client = self._get_client()
        
        system_prompt, anthropic_messages = self._convert_messages(messages)
        anthropic_tools = self._convert_tools(tools)
        
        try:
            # Build request params
            request_params = {
                "model": model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }
            
            if system_prompt:
                request_params["system"] = system_prompt
            
            if anthropic_tools:
                request_params["tools"] = anthropic_tools
            
            # Stream API call
            with client.messages.stream(**request_params) as stream:
                for text in stream.text_stream:
                    yield text
            
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise
