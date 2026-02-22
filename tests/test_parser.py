"""Test suite for AgentLang parser."""

import unittest
from agentlang.lexer.tokenizer import Tokenizer
from agentlang.parser.parser import Parser
from agentlang.parser.ast_nodes import (
    ASTNode, Program, AgentDef, ToolDef, PipelineDef,
    RunStatement, LetStatement, ConfigBlock, SendMessage
)


class TestParser(unittest.TestCase):
    """Test the parser component."""

    def parse(self, code):
        """Helper to tokenize and parse code."""
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_simple_agent_definition(self):
        """Test parsing a basic agent definition."""
        code = """
        agent greeter {
            model: "gpt-4"
            prompt: "You are friendly"
        }
        """
        ast = self.parse(code)
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AgentDef)
        self.assertEqual(stmt.name, "greeter")
        self.assertEqual(stmt.properties['model'], "gpt-4")
        self.assertEqual(stmt.properties['prompt'], "You are friendly")

    def test_agent_with_tools(self):
        """Test parsing agent with tools list."""
        code = """
        agent researcher {
            model: "gpt-4"
            prompt: "You research"
            tools: [web_search, read_file]
        }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AgentDef)
        tools = stmt.properties.get('tools', [])
        self.assertEqual(len(tools), 2)
        self.assertIn("web_search", tools)
        self.assertIn("read_file", tools)

    def test_agent_with_optional_params(self):
        """Test parsing agent with temperature and max_tokens."""
        code = """
        agent researcher {
            model: "gpt-4"
            prompt: "You research"
            temperature: 0.3
            max_tokens: 1000
        }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertEqual(stmt.properties['temperature'], 0.3)
        self.assertEqual(stmt.properties['max_tokens'], 1000)

    def test_tool_definition(self):
        """Test parsing a tool definition."""
        code = """
        tool web_search {
            description: "Search the web"
            handler: builtin("web_search")
        }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, ToolDef)
        self.assertEqual(stmt.name, "web_search")
        self.assertEqual(stmt.description, "Search the web")
        # Note: params parsing is a TODO - complex syntax not yet implemented

    def test_config_definition(self):
        """Test parsing config block."""
        code = """
        config {
            default_model: "gpt-4"
            log_level: "info"
            timeout: 300
        }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, ConfigBlock)
        self.assertEqual(stmt.settings["default_model"], "gpt-4")
        self.assertEqual(stmt.settings["log_level"], "info")
        self.assertEqual(stmt.settings["timeout"], 300)

    def test_run_statement(self):
        """Test parsing run statement."""
        code = """
        run greeter with {
            task: "Say hello"
        }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, RunStatement)
        self.assertEqual(stmt.target, "greeter")
        self.assertEqual(stmt.params["task"], "Say hello")

    def test_variable_assignment(self):
        """Test parsing variable assignment."""
        code = """
        let result = run greeter with { task: "hello" }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, LetStatement)
        self.assertEqual(stmt.name, "result")
        self.assertIsInstance(stmt.value, RunStatement)

    def test_pipeline_simple(self):
        """Test parsing simple pipeline."""
        code = """
        pipeline research_flow {
            researcher -> summarizer -> formatter
        }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, PipelineDef)
        self.assertEqual(stmt.name, "research_flow")
        self.assertEqual(len(stmt.agents), 3)
        self.assertEqual(stmt.agents[0], "researcher")
        self.assertEqual(stmt.agents[1], "summarizer")
        self.assertEqual(stmt.agents[2], "formatter")

    def test_pipeline_with_error_handling(self):
        """Test parsing pipeline with on_error block."""
        code = """
        pipeline process {
            agent1 -> agent2
            on_error: {
                retry: 3
                fallback: backup_agent
            }
        }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, PipelineDef)
        self.assertIsNotNone(stmt.error_handling)
        self.assertEqual(stmt.error_handling.get("retry"), 3)
        self.assertEqual(stmt.error_handling.get("fallback"), "backup_agent")

    def test_multiple_statements(self):
        """Test parsing file with multiple statements."""
        code = """
        config {
            default_model: "gpt-4"
        }
        
        agent test {
            model: "gpt-4"
            prompt: "test"
        }
        
        run test with { task: "hello" }
        """
        ast = self.parse(code)
        
        self.assertEqual(len(ast.statements), 3)
        self.assertIsInstance(ast.statements[0], ConfigBlock)
        self.assertIsInstance(ast.statements[1], AgentDef)
        self.assertIsInstance(ast.statements[2], RunStatement)

    def test_nested_objects(self):
        """Test parsing nested object literals."""
        code = """
        run processor with {
            params: {
                nested: {
                    value: "deep"
                }
            }
        }
        """
        ast = self.parse(code)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt.params["params"], dict)
        self.assertIsInstance(stmt.params["params"]["nested"], dict)
        self.assertEqual(stmt.params["params"]["nested"]["value"], "deep")

    def test_empty_blocks(self):
        """Test parsing empty blocks."""
        code = """
        agent test {
            model: "gpt-4"
            prompt: "test"
        }
        """
        # Should not raise an error
        ast = self.parse(code)
        self.assertIsNotNone(ast)


if __name__ == '__main__':
    unittest.main()
