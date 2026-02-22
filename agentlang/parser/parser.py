"""Parser for AgentLang"""

from typing import List, Dict, Any, Optional
from ..lexer import Token, TokenType
from .ast_nodes import *


class Parser:
    """Recursive descent parser for AgentLang"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]  # Filter out newlines
        self.pos = 0
    
    def current_token(self) -> Optional[Token]:
        """Get current token"""
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]
    
    def peek_token(self, offset=1) -> Optional[Token]:
        """Peek ahead"""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Consume and return current token"""
        token = self.current_token()
        self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error"""
        token = self.current_token()
        if not token or token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type.name}, got {token.type.name if token else 'EOF'} "
                f"at {token.line if token else '?'}:{token.column if token else '?'}"
            )
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        token = self.current_token()
        return token and token.type in token_types
    
    def parse(self) -> Program:
        """Parse entire program"""
        program = Program()
        
        while self.current_token() and self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                program.statements.append(stmt)
        
        return program
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a top-level statement"""
        token = self.current_token()
        
        if not token or token.type == TokenType.EOF:
            return None
        
        if token.type == TokenType.AGENT:
            return self.parse_agent()
        elif token.type == TokenType.TOOL:
            return self.parse_tool()
        elif token.type == TokenType.PIPELINE:
            return self.parse_pipeline()
        elif token.type == TokenType.RUN:
            return self.parse_run()
        elif token.type == TokenType.LET:
            return self.parse_let()
        elif token.type == TokenType.CONFIG:
            return self.parse_config()
        elif token.type == TokenType.SEND:
            return self.parse_send()
        else:
            raise SyntaxError(f"Unexpected token {token.type.name} at {token.line}:{token.column}")
    
    def parse_agent(self) -> AgentDef:
        """Parse agent definition"""
        start = self.expect(TokenType.AGENT)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.expect(TokenType.LBRACE)
        properties = self.parse_properties()
        self.expect(TokenType.RBRACE)
        
        return AgentDef(name=name, properties=properties, line=start.line, column=start.column)
    
    def parse_tool(self) -> ToolDef:
        """Parse tool definition"""
        start = self.expect(TokenType.TOOL)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.expect(TokenType.LBRACE)
        properties = self.parse_properties()
        self.expect(TokenType.RBRACE)
        
        tool = ToolDef(
            name=name,
            description=properties.get('description', ''),
            params=properties.get('params', {}),
            handler=properties.get('handler', ''),
            line=start.line,
            column=start.column
        )
        
        return tool
    
    def parse_pipeline(self) -> PipelineDef:
        """Parse pipeline definition"""
        start = self.expect(TokenType.PIPELINE)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.expect(TokenType.LBRACE)
        
        # Parse agent chain (agent1 -> agent2 -> agent3)
        agents = []
        agents.append(self.expect(TokenType.IDENTIFIER).value)
        
        while self.match(TokenType.ARROW):
            self.advance()  # consume ->
            agents.append(self.expect(TokenType.IDENTIFIER).value)
        
        # Optional error handling
        error_handling = None
        if self.match(TokenType.ON_ERROR):
            self.advance()
            self.expect(TokenType.COLON)
            self.expect(TokenType.LBRACE)
            error_handling = self.parse_properties()
            self.expect(TokenType.RBRACE)
        
        self.expect(TokenType.RBRACE)
        
        return PipelineDef(
            name=name,
            agents=agents,
            error_handling=error_handling,
            line=start.line,
            column=start.column
        )
    
    def parse_run(self) -> RunStatement:
        """Parse run statement"""
        start = self.expect(TokenType.RUN)
        target = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.WITH)
        self.expect(TokenType.LBRACE)
        params = self.parse_properties()
        self.expect(TokenType.RBRACE)
        
        return RunStatement(target=target, params=params, line=start.line, column=start.column)
    
    def parse_let(self) -> LetStatement:
        """Parse let statement"""
        start = self.expect(TokenType.LET)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.EQUALS)
        
        # Value can be a run statement or literal
        if self.match(TokenType.RUN):
            value = self.parse_run()
        else:
            value = self.parse_value()
        
        return LetStatement(name=name, value=value, line=start.line, column=start.column)
    
    def parse_config(self) -> ConfigBlock:
        """Parse config block"""
        start = self.expect(TokenType.CONFIG)
        self.expect(TokenType.LBRACE)
        settings = self.parse_properties()
        self.expect(TokenType.RBRACE)
        
        return ConfigBlock(settings=settings, line=start.line, column=start.column)
    
    def parse_send(self) -> SendMessage:
        """Parse send message statement"""
        start = self.expect(TokenType.SEND)
        target = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.MESSAGE)
        self.expect(TokenType.LBRACE)
        message = self.parse_properties()
        self.expect(TokenType.RBRACE)
        
        return SendMessage(target=target, message=message, line=start.line, column=start.column)
    
    def parse_properties(self) -> Dict[str, Any]:
        """Parse property block (key: value pairs)"""
        properties = {}
        
        while not self.match(TokenType.RBRACE):
            if not self.match(TokenType.IDENTIFIER):
                break
            
            key = self.advance().value
            self.expect(TokenType.COLON)
            value = self.parse_value()
            properties[key] = value
            
            # Optional comma
            if self.match(TokenType.COMMA):
                self.advance()
        
        return properties
    
    def parse_value(self) -> Any:
        """Parse a value (string, number, boolean, list, dict, function call)"""
        token = self.current_token()
        
        if not token:
            raise SyntaxError("Unexpected end of input")
        
        # String
        if token.type == TokenType.STRING:
            return self.advance().value
        
        # Number
        if token.type in (TokenType.INTEGER, TokenType.FLOAT, TokenType.NUMBER):
            return self.advance().value
        
        # Boolean
        if token.type == TokenType.BOOLEAN:
            return self.advance().value
        
        # List [item1, item2, ...]
        if token.type == TokenType.LBRACKET:
            return self.parse_list()
        
        # Dict or function call
        if token.type == TokenType.IDENTIFIER:
            identifier = self.advance().value
            
            # Function call: identifier(args)
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                
                while not self.match(TokenType.RPAREN):
                    args.append(self.parse_value())
                    if self.match(TokenType.COMMA):
                        self.advance()
                
                self.expect(TokenType.RPAREN)
                return f"{identifier}({', '.join(repr(arg) for arg in args)})"
            
            # Property access: identifier.property
            if self.match(TokenType.DOT):
                self.advance()
                property_name = self.expect(TokenType.IDENTIFIER).value
                return f"{identifier}.{property_name}"
            
            # Just an identifier reference
            return identifier
        
        # Dict {key: value, ...}
        if token.type == TokenType.LBRACE:
            self.advance()
            properties = self.parse_properties()
            self.expect(TokenType.RBRACE)
            return properties
        
        raise SyntaxError(f"Unexpected token {token.type.name} at {token.line}:{token.column}")
    
    def parse_list(self) -> List[Any]:
        """Parse list [item1, item2, ...]"""
        self.expect(TokenType.LBRACKET)
        items = []
        
        while not self.match(TokenType.RBRACKET):
            items.append(self.parse_value())
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RBRACKET)
        return items


def parse(tokens: List[Token]) -> Program:
    """Convenience function to parse tokens"""
    return Parser(tokens).parse()
