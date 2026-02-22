"""AST Node definitions for AgentLang"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    line: int = 0
    column: int = 0


@dataclass
class Program(ASTNode):
    """Root node containing all definitions"""
    statements: List[ASTNode] = field(default_factory=list)


@dataclass
class AgentDef(ASTNode):
    """Agent definition"""
    name: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolDef(ASTNode):
    """Tool definition"""
    name: str = ""
    description: str = ""
    params: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    handler: str = ""


@dataclass
class PipelineDef(ASTNode):
    """Pipeline definition"""
    name: str = ""
    agents: List[str] = field(default_factory=list)
    error_handling: Optional[Dict[str, Any]] = None


@dataclass
class RunStatement(ASTNode):
    """Run statement"""
    target: str = ""  # Agent or pipeline name
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LetStatement(ASTNode):
    """Variable assignment"""
    name: str = ""
    value: Any = None


@dataclass
class ConfigBlock(ASTNode):
    """Global configuration"""
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SendMessage(ASTNode):
    """Send message to agent"""
    target: str = ""
    message: Dict[str, Any] = field(default_factory=dict)
