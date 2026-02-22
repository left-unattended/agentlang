"""AgentLang Runtime - Executes programs"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from .agent import Agent
from .tool import Tool
from ..llm import LLMProvider, OpenAIProvider, AnthropicProvider, LLMMessage

logger = logging.getLogger(__name__)


class Runtime:
    """Runtime environment for AgentLang"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents: Dict[str, Agent] = {}
        self.tools: Dict[str, Tool] = {}
        self.pipelines: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        
        # Initialize built-in tools
        self._init_builtin_tools()
    
    def _init_builtin_tools(self):
        """Initialize built-in tools"""
        # web_search
        self.register_tool(Tool(
            name="web_search",
            description="Search the web",
            params={
                "query": {"type": "string", "required": True},
                "max_results": {"type": "int", "default": 5}
            },
            handler=self._builtin_web_search
        ))
        
        # read_file
        self.register_tool(Tool(
            name="read_file",
            description="Read a file",
            params={
                "path": {"type": "string", "required": True}
            },
            handler=self._builtin_read_file
        ))
        
        # write_file
        self.register_tool(Tool(
            name="write_file",
            description="Write to a file",
            params={
                "path": {"type": "string", "required": True},
                "content": {"type": "string", "required": True}
            },
            handler=self._builtin_write_file
        ))
        
        # http_get
        self.register_tool(Tool(
            name="http_get",
            description="HTTP GET request",
            params={
                "url": {"type": "string", "required": True}
            },
            handler=self._builtin_http_get
        ))
    
    def _builtin_web_search(self, query: str, max_results: int = 5) -> str:
        """Built-in web search (placeholder)"""
        logger.info(f"web_search({query}, max_results={max_results})")
        return f"[MOCK] Search results for: {query}"
    
    def _builtin_read_file(self, path: str) -> str:
        """Built-in file read"""
        with open(path, 'r') as f:
            return f.read()
    
    def _builtin_write_file(self, path: str, content: str) -> str:
        """Built-in file write"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Wrote {len(content)} bytes to {path}"
    
    def _builtin_http_get(self, url: str) -> str:
        """Built-in HTTP GET (placeholder)"""
        logger.info(f"http_get({url})")
        return f"[MOCK] Response from {url}"
    
    def register_agent(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def register_tool(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def register_pipeline(self, name: str, agents: List[str], error_handling: Optional[Dict] = None):
        """Register a pipeline"""
        self.pipelines[name] = {
            "agents": agents,
            "error_handling": error_handling
        }
        logger.info(f"Registered pipeline: {name}")
    
    def update_config(self, config: Dict[str, Any]):
        """Update runtime configuration"""
        self.config.update(config)
        logger.info(f"Updated config: {config}")
    
    def run_agent(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent"""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent = self.agents[agent_name]
        logger.info(f"Running agent {agent_name} with params: {params}")
        
        # Build message
        user_message = params.get('task') or params.get('message') or str(params)
        
        # Check if we should use real LLM or mock
        use_mock = os.environ.get('AGENTLANG_MOCK_LLM', 'false').lower() == 'true'
        
        if use_mock or (not os.environ.get('OPENAI_API_KEY') and not os.environ.get('ANTHROPIC_API_KEY')):
            # Use mock response
            logger.info(f"Using mock LLM for {agent_name}")
            response = {
                "agent": agent_name,
                "model": agent.model,
                "output": f"[MOCK RESPONSE from {agent_name}] Task: {user_message}",
                "params": params
            }
            logger.info(f"Agent {agent_name} completed")
            return response
        
        # Use real LLM
        try:
            # Auto-detect provider from model name
            provider_name = LLMProvider.detect_provider(agent.model)
            
            # Initialize provider
            if provider_name == 'anthropic':
                provider = AnthropicProvider()
            else:  # Default to OpenAI
                provider = OpenAIProvider()
            
            logger.info(f"Using {provider_name} provider for model {agent.model}")
            
            # Build messages
            messages = []
            if agent.prompt:
                messages.append(LLMMessage(role="system", content=agent.prompt))
            messages.append(LLMMessage(role="user", content=user_message))
            
            # Build tools if agent has them
            tools = None
            if agent.tools:
                tools = []
                for tool_name in agent.tools:
                    if tool_name in self.tools:
                        tool = self.tools[tool_name]
                        tools.append({
                            "name": tool.name,
                            "description": tool.description,
                            "params": tool.params
                        })
            
            # Get completion
            llm_response = provider.complete(
                messages=messages,
                model=agent.model,
                temperature=agent.temperature if hasattr(agent, 'temperature') else 0.7,
                max_tokens=agent.max_tokens if hasattr(agent, 'max_tokens') else 2000,
                tools=tools
            )
            
            # Handle tool calls if present
            output = llm_response.content
            if llm_response.tool_calls:
                logger.info(f"Agent requested {len(llm_response.tool_calls)} tool calls")
                # TODO: Execute tools and continue conversation
                # For now, just include tool calls in response
                output += f"\n[Tool calls requested: {llm_response.tool_calls}]"
            
            response = {
                "agent": agent_name,
                "model": llm_response.model,
                "output": output,
                "params": params,
                "usage": llm_response.usage,
                "tool_calls": llm_response.tool_calls
            }
            
            logger.info(f"Agent {agent_name} completed with {llm_response.usage.get('total_tokens', 0)} tokens")
            return response
            
        except Exception as e:
            logger.error(f"Error running agent {agent_name}: {e}")
            # Fall back to mock on error
            return {
                "agent": agent_name,
                "model": agent.model,
                "output": f"[ERROR: {str(e)}] Fallback mock response for: {user_message}",
                "params": params,
                "error": str(e)
            }
    
    def run_pipeline(self, pipeline_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a pipeline"""
        if pipeline_name not in self.pipelines:
            raise ValueError(f"Unknown pipeline: {pipeline_name}")
        
        pipeline = self.pipelines[pipeline_name]
        agents = pipeline["agents"]
        error_handling = pipeline.get("error_handling", {})
        
        logger.info(f"Running pipeline {pipeline_name} with {len(agents)} agents")
        
        # Execute agents in sequence
        current_output = params
        results = []
        
        for agent_name in agents:
            try:
                result = self.run_agent(agent_name, current_output)
                results.append(result)
                # Pass output to next agent
                current_output = {"task": result["output"], "context": result}
            except Exception as e:
                logger.error(f"Error in pipeline {pipeline_name} at agent {agent_name}: {e}")
                
                # Handle error
                retry = error_handling.get("retry", 0)
                fallback = error_handling.get("fallback")
                
                if retry > 0:
                    logger.info(f"Retrying {agent_name} ({retry} attempts left)")
                    # TODO: Implement retry logic
                
                if fallback:
                    logger.info(f"Using fallback: {fallback}")
                    result = self.run_agent(fallback, current_output)
                    results.append(result)
                    current_output = {"task": result["output"], "context": result}
                else:
                    raise
        
        return {
            "pipeline": pipeline_name,
            "output": current_output,
            "results": results
        }
    
    def set_variable(self, name: str, value: Any):
        """Set a variable"""
        self.variables[name] = value
        logger.info(f"Set variable {name} = {value}")
    
    def get_variable(self, name: str) -> Any:
        """Get a variable"""
        if name not in self.variables:
            raise ValueError(f"Unknown variable: {name}")
        return self.variables[name]
