"""Test suite for AgentLang tokenizer/lexer."""

import unittest
from agentlang.lexer.tokenizer import Tokenizer, TokenType


class TestTokenizer(unittest.TestCase):
    """Test the tokenizer component."""

    def test_keywords(self):
        """Test recognition of language keywords."""
        code = "agent tool pipeline run with config let"
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.AGENT)
        self.assertEqual(tokens[1].type, TokenType.TOOL)
        self.assertEqual(tokens[2].type, TokenType.PIPELINE)
        self.assertEqual(tokens[3].type, TokenType.RUN)
        self.assertEqual(tokens[4].type, TokenType.WITH)
        self.assertEqual(tokens[5].type, TokenType.CONFIG)
        self.assertEqual(tokens[6].type, TokenType.LET)

    def test_identifiers(self):
        """Test identifier recognition."""
        code = "my_agent researcher simple_tool"
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "my_agent")
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "researcher")

    def test_strings(self):
        """Test string literal parsing."""
        code = '"hello world" "multi\\nline"'
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "hello world")
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].value, "multi\\nline")

    def test_numbers(self):
        """Test number parsing."""
        code = "42 3.14 0.5"
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, 42)
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].value, 3.14)
        self.assertEqual(tokens[2].type, TokenType.NUMBER)
        self.assertEqual(tokens[2].value, 0.5)

    def test_symbols(self):
        """Test symbol recognition."""
        code = "{ } [ ] : , = ->"
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.LBRACE)
        self.assertEqual(tokens[1].type, TokenType.RBRACE)
        self.assertEqual(tokens[2].type, TokenType.LBRACKET)
        self.assertEqual(tokens[3].type, TokenType.RBRACKET)
        self.assertEqual(tokens[4].type, TokenType.COLON)
        self.assertEqual(tokens[5].type, TokenType.COMMA)
        self.assertEqual(tokens[6].type, TokenType.EQUALS)
        self.assertEqual(tokens[7].type, TokenType.ARROW)

    def test_comments(self):
        """Test comment handling."""
        code = """
        // Single line comment
        agent test {}
        /* Multi-line
           comment */
        tool test {}
        """
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        # Comments should be stripped, only agent and tool remain
        keywords = [t for t in tokens if t.type in (TokenType.AGENT, TokenType.TOOL)]
        self.assertEqual(len(keywords), 2)

    def test_complex_expression(self):
        """Test tokenizing a complex agent definition."""
        code = """
        agent researcher {
            model: "gpt-4"
            temperature: 0.7
        }
        """
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.AGENT)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "researcher")
        self.assertEqual(tokens[2].type, TokenType.LBRACE)
        # model: "gpt-4"
        self.assertTrue(any(t.type == TokenType.STRING and t.value == "gpt-4" for t in tokens))

    def test_empty_input(self):
        """Test handling of empty input."""
        tokenizer = Tokenizer("")
        tokens = tokenizer.tokenize()
        self.assertEqual(len(tokens), 1)  # Should have EOF
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_whitespace_handling(self):
        """Test that whitespace is properly ignored."""
        code1 = "agent researcher{model:\"gpt-4\"}"
        code2 = "agent   researcher  {  model : \"gpt-4\"  }"
        
        tokens1 = Tokenizer(code1).tokenize()
        tokens2 = Tokenizer(code2).tokenize()
        
        # Both should produce same token sequence (ignoring whitespace)
        self.assertEqual(len(tokens1), len(tokens2))


if __name__ == '__main__':
    unittest.main()
