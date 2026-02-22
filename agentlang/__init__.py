"""
AgentLang - A declarative language for AI agent orchestration

Simple. Composable. Readable.
"""

__version__ = "0.1.0"

from .lexer import tokenize
from .parser import parse
from .interpreter import interpret
from .runtime import Runtime, Agent, Tool

__all__ = [
    "tokenize",
    "parse",
    "interpret",
    "Runtime",
    "Agent",
    "Tool",
]
