"""Tool implementation"""

from dataclasses import dataclass, field
from typing import Dict, Any, Callable


@dataclass
class Tool:
    """Represents an AgentLang tool"""
    name: str
    description: str
    params: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    handler: Callable = None
    
    def __repr__(self):
        return f"Tool({self.name}, params={list(self.params.keys())})"
    
    def call(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        if not self.handler:
            raise RuntimeError(f"Tool {self.name} has no handler")
        
        # Validate parameters
        for param_name, param_spec in self.params.items():
            required = param_spec.get('required', False)
            default = param_spec.get('default')
            
            if required and param_name not in kwargs:
                raise ValueError(f"Missing required parameter: {param_name}")
            
            if param_name not in kwargs and default is not None:
                kwargs[param_name] = default
        
        return self.handler(**kwargs)
    
    def execute(self, *args, **kwargs) -> Any:
        """Alias for call() - execute the tool with given parameters"""
        # If positional args provided, call handler directly
        if args:
            return self.handler(*args, **kwargs)
        return self.call(**kwargs)
