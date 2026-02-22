"""Agent implementation"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Agent:
    """Represents an AgentLang agent"""
    name: str
    model: str
    prompt: str
    tools: List[str] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 2000
    on_error: Optional[Dict[str, Any]] = None
    
    def __repr__(self):
        return f"Agent({self.name}, model={self.model}, tools={len(self.tools)})"
