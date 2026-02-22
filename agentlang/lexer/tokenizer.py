"""Tokenizer for AgentLang"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Keywords
    AGENT = auto()
    TOOL = auto()
    PIPELINE = auto()
    RUN = auto()
    WITH = auto()
    LET = auto()
    CONFIG = auto()
    ON_ERROR = auto()
    SEND = auto()
    MESSAGE = auto()
    
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    
    # Operators & Punctuation
    ARROW = auto()        # ->
    COLON = auto()        # :
    EQUALS = auto()       # =
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    COMMA = auto()        # ,
    DOT = auto()          # .
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"


class Tokenizer:
    """Lexical analyzer for AgentLang"""
    
    KEYWORDS = {
        'agent': TokenType.AGENT,
        'tool': TokenType.TOOL,
        'pipeline': TokenType.PIPELINE,
        'run': TokenType.RUN,
        'with': TokenType.WITH,
        'let': TokenType.LET,
        'config': TokenType.CONFIG,
        'on_error': TokenType.ON_ERROR,
        'send': TokenType.SEND,
        'message': TokenType.MESSAGE,
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
        'required': TokenType.IDENTIFIER,  # Special parameter keyword
        'default': TokenType.IDENTIFIER,   # Special parameter keyword
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Get current character without advancing"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset=1) -> Optional[str]:
        """Peek ahead at character"""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Consume and return current character"""
        char = self.current_char()
        if char is None:
            return None
        
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace except newlines"""
        while self.current_char() in ' \t\r':
            self.advance()
    
    def skip_line_comment(self):
        """Skip // comment"""
        while self.current_char() and self.current_char() != '\n':
            self.advance()
    
    def skip_block_comment(self):
        """Skip /* */ comment"""
        self.advance()  # /
        self.advance()  # *
        
        while self.current_char():
            if self.current_char() == '*' and self.peek_char() == '/':
                self.advance()  # *
                self.advance()  # /
                return
            self.advance()
    
    def read_string(self) -> str:
        """Read string literal (double quotes)"""
        quote = self.advance()  # Opening quote
        chars = []
        
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\':
                self.advance()
                escaped = self.current_char()
                if escaped == 'n':
                    chars.append('\n')
                elif escaped == 't':
                    chars.append('\t')
                elif escaped == '\\':
                    chars.append('\\')
                elif escaped == quote:
                    chars.append(quote)
                else:
                    chars.append(escaped)
                self.advance()
            else:
                chars.append(self.current_char())
                self.advance()
        
        if self.current_char() == quote:
            self.advance()  # Closing quote
        
        return ''.join(chars)
    
    def read_number(self) -> Token:
        """Read integer or float"""
        start_line = self.line
        start_col = self.column
        chars = []
        is_float = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if is_float:
                    break  # Second dot, not part of number
                is_float = True
            chars.append(self.current_char())
            self.advance()
        
        num_str = ''.join(chars)
        if is_float:
            return Token(TokenType.FLOAT, float(num_str), start_line, start_col)
        else:
            return Token(TokenType.INTEGER, int(num_str), start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read identifier or keyword"""
        start_line = self.line
        start_col = self.column
        chars = []
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() in '_'):
            chars.append(self.current_char())
            self.advance()
        
        text = ''.join(chars)
        
        # Check for boolean literals
        if text == 'true':
            return Token(TokenType.BOOLEAN, True, start_line, start_col)
        elif text == 'false':
            return Token(TokenType.BOOLEAN, False, start_line, start_col)
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        return Token(token_type, text, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """Tokenize entire source"""
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            char = self.current_char()
            if char is None:
                break
            
            start_line = self.line
            start_col = self.column
            
            # Comments
            if char == '/' and self.peek_char() == '/':
                self.skip_line_comment()
                continue
            
            if char == '/' and self.peek_char() == '*':
                self.skip_block_comment()
                continue
            
            # Newline
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', start_line, start_col))
                self.advance()
                continue
            
            # Strings
            if char == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, start_line, start_col))
                continue
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers & Keywords
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Operators & Punctuation
            if char == '-' and self.peek_char() == '>':
                self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_col))
                self.advance()
                self.advance()
                continue
            
            if char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_col))
                self.advance()
                continue
            
            if char == '=':
                self.tokens.append(Token(TokenType.EQUALS, '=', start_line, start_col))
                self.advance()
                continue
            
            if char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_col))
                self.advance()
                continue
            
            if char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_col))
                self.advance()
                continue
            
            if char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
                self.advance()
                continue
            
            if char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_col))
                self.advance()
                continue
            
            if char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_col))
                self.advance()
                continue
            
            if char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_col))
                self.advance()
                continue
            
            if char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_col))
                self.advance()
                continue
            
            if char == '.':
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_col))
                self.advance()
                continue
            
            # Unknown character
            raise SyntaxError(f"Unexpected character '{char}' at {start_line}:{start_col}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


def tokenize(source: str) -> List[Token]:
    """Convenience function to tokenize source"""
    return Tokenizer(source).tokenize()
