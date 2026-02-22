"""Interpreter for AgentLang AST"""

import logging
from typing import Any
from pathlib import Path
from ..parser.ast_nodes import *
from ..runtime import Runtime, Agent, Tool
from ..lexer import tokenize
from ..parser import parse

logger = logging.getLogger(__name__)


class Interpreter:
    """Executes AgentLang AST"""
    
    def __init__(self, runtime: Runtime = None):
        self.runtime = runtime or Runtime()
    
    def run_file(self, filepath: str) -> Any:
        """Run an AgentLang file"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        source = path.read_text()
        tokens = tokenize(source)
        ast = parse(tokens)
        return self.execute(ast)
    
    def execute(self, program: Program) -> Any:
        """Execute a program"""
        result = None
        
        for statement in program.statements:
            result = self.execute_statement(statement)
        
        return result
    
    def execute_statement(self, stmt: ASTNode) -> Any:
        """Execute a single statement"""
        if isinstance(stmt, AgentDef):
            return self.execute_agent_def(stmt)
        elif isinstance(stmt, ToolDef):
            return self.execute_tool_def(stmt)
        elif isinstance(stmt, PipelineDef):
            return self.execute_pipeline_def(stmt)
        elif isinstance(stmt, RunStatement):
            return self.execute_run(stmt)
        elif isinstance(stmt, LetStatement):
            return self.execute_let(stmt)
        elif isinstance(stmt, ConfigBlock):
            return self.execute_config(stmt)
        elif isinstance(stmt, SendMessage):
            return self.execute_send(stmt)
        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt)}")
    
    def execute_agent_def(self, stmt: AgentDef):
        """Execute agent definition"""
        props = stmt.properties
        
        agent = Agent(
            name=stmt.name,
            model=props.get('model', self.runtime.config.get('default_model', 'gpt-4')),
            prompt=props.get('prompt', ''),
            tools=props.get('tools', []),
            temperature=props.get('temperature', 0.7),
            max_tokens=props.get('max_tokens', 2000),
            on_error=props.get('on_error')
        )
        
        self.runtime.register_agent(agent)
        return agent
    
    def execute_tool_def(self, stmt: ToolDef):
        """Execute tool definition"""
        # Parse handler string (e.g., "python(path)" or "builtin(name)")
        handler_str = stmt.handler
        
        # For now, use a placeholder handler
        # TODO: Implement handler loading from files
        def placeholder_handler(**kwargs):
            logger.info(f"Tool {stmt.name} called with {kwargs}")
            return f"[MOCK] {stmt.name} result"
        
        tool = Tool(
            name=stmt.name,
            description=stmt.description,
            params=stmt.params,
            handler=placeholder_handler
        )
        
        self.runtime.register_tool(tool)
        return tool
    
    def execute_pipeline_def(self, stmt: PipelineDef):
        """Execute pipeline definition"""
        self.runtime.register_pipeline(
            stmt.name,
            stmt.agents,
            stmt.error_handling
        )
        return stmt.name
    
    def execute_run(self, stmt: RunStatement):
        """Execute run statement"""
        target = stmt.target
        params = self.resolve_params(stmt.params)
        
        # Check if target is a pipeline or agent
        if target in self.runtime.pipelines:
            return self.runtime.run_pipeline(target, params)
        elif target in self.runtime.agents:
            return self.runtime.run_agent(target, params)
        else:
            raise ValueError(f"Unknown target: {target}")
    
    def execute_let(self, stmt: LetStatement):
        """Execute let statement"""
        # Evaluate the value
        if isinstance(stmt.value, RunStatement):
            value = self.execute_run(stmt.value)
        else:
            value = stmt.value
        
        self.runtime.set_variable(stmt.name, value)
        return value
    
    def execute_config(self, stmt: ConfigBlock):
        """Execute config block"""
        self.runtime.config.update(stmt.settings)
        logger.info(f"Updated config: {stmt.settings}")
        return None
    
    def execute_send(self, stmt: SendMessage):
        """Execute send message statement"""
        target = stmt.target
        message = self.resolve_params(stmt.message)
        
        logger.info(f"Sending message to {target}: {message}")
        # TODO: Implement inter-agent messaging
        return None
    
    def resolve_params(self, params: dict) -> dict:
        """Resolve parameter values (handle variable references)"""
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value in self.runtime.variables:
                resolved[key] = self.runtime.variables[value]
            else:
                resolved[key] = value
        
        return resolved


def interpret(program: Program, runtime: Runtime = None) -> Any:
    """Convenience function to interpret a program"""
    return Interpreter(runtime).execute(program)
