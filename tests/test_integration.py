"""Integration tests for AgentLang - full end-to-end testing."""

import unittest
import tempfile
import os
from agentlang.interpreter.interpreter import Interpreter


class TestIntegration(unittest.TestCase):
    """Test complete AgentLang programs end-to-end."""

    def run_agent_code(self, code):
        """Helper to run AgentLang code from string."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.agent', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            interpreter = Interpreter()
            result = interpreter.run_file(temp_file)
            return result
        finally:
            os.unlink(temp_file)

    def test_hello_world(self):
        """Test the simplest possible program."""
        code = """
        config {
            default_model: "gpt-4"
        }
        
        agent greeter {
            model: "gpt-4"
            prompt: "You are friendly"
        }
        
        run greeter with {
            task: "Say hello"
        }
        """
        
        result = self.run_agent_code(code)
        self.assertIsNotNone(result)
        self.assertEqual(result["agent"], "greeter")

    def test_agent_with_builtin_tools(self):
        """Test agent using built-in tools."""
        code = """
        agent researcher {
            model: "gpt-4"
            prompt: "You research things"
            tools: [web_search, read_file]
        }
        
        run researcher with {
            task: "Search for information"
        }
        """
        
        result = self.run_agent_code(code)
        self.assertIsNotNone(result)
        self.assertEqual(result["agent"], "researcher")

    def test_config_override(self):
        """Test that config settings are applied."""
        code = """
        config {
            default_model: "gpt-3.5-turbo"
            log_level: "debug"
        }
        
        agent test {
            model: "gpt-4"
            prompt: "Test"
        }
        
        run test with { task: "test" }
        """
        
        result = self.run_agent_code(code)
        self.assertIsNotNone(result)
        # Config should have been applied
        self.assertEqual(result["model"], "gpt-4")

    def test_multiple_agents(self):
        """Test defining and running multiple agents."""
        code = """
        agent agent1 {
            model: "gpt-4"
            prompt: "Agent 1"
        }
        
        agent agent2 {
            model: "gpt-4"
            prompt: "Agent 2"
        }
        
        run agent1 with { task: "Task 1" }
        """
        
        result = self.run_agent_code(code)
        self.assertEqual(result["agent"], "agent1")

    def test_agent_with_temperature(self):
        """Test agent with custom temperature setting."""
        code = """
        agent creative {
            model: "gpt-4"
            prompt: "You are creative"
            temperature: 0.9
        }
        
        run creative with { task: "Be creative" }
        """
        
        result = self.run_agent_code(code)
        self.assertIsNotNone(result)

    def test_agent_with_max_tokens(self):
        """Test agent with max_tokens limit."""
        code = """
        agent concise {
            model: "gpt-4"
            prompt: "Be brief"
            max_tokens: 100
        }
        
        run concise with { task: "Summarize" }
        """
        
        result = self.run_agent_code(code)
        self.assertIsNotNone(result)

    def test_complex_params(self):
        """Test running agent with complex nested parameters."""
        code = """
        agent processor {
            model: "gpt-4"
            prompt: "Process data"
        }
        
        run processor with {
            data: "test data"
            options: {
                format: "json"
                verbose: true
            }
        }
        """
        
        result = self.run_agent_code(code)
        self.assertIsNotNone(result)
        self.assertIn("params", result)

    def test_comments_ignored(self):
        """Test that comments don't affect execution."""
        code = """
        // This is a comment
        agent test {
            model: "gpt-4"
            prompt: "Test"  // inline comment
        }
        
        /* Multi-line
           comment */
        run test with { task: "test" }
        """
        
        result = self.run_agent_code(code)
        self.assertEqual(result["agent"], "test")

    def test_multiple_tools(self):
        """Test agent with multiple tools."""
        code = """
        agent multi_tool {
            model: "gpt-4"
            prompt: "You have many tools"
            tools: [web_search, read_file, write_file, http_get]
        }
        
        run multi_tool with { task: "Use tools" }
        """
        
        result = self.run_agent_code(code)
        self.assertIsNotNone(result)

    def test_empty_tools_list(self):
        """Test agent with empty tools list."""
        code = """
        agent no_tools {
            model: "gpt-4"
            prompt: "No tools needed"
            tools: []
        }
        
        run no_tools with { task: "Think" }
        """
        
        result = self.run_agent_code(code)
        self.assertIsNotNone(result)

    def test_minimal_agent(self):
        """Test the most minimal valid agent definition."""
        code = """
        agent minimal {
            model: "gpt-4"
            prompt: "Minimal"
        }
        
        run minimal with { task: "test" }
        """
        
        result = self.run_agent_code(code)
        self.assertEqual(result["agent"], "minimal")


class TestExamplePrograms(unittest.TestCase):
    """Test the example programs in the examples/ directory."""

    def test_hello_example(self):
        """Test examples/hello.agent runs successfully."""
        interpreter = Interpreter()
        result = interpreter.run_file("examples/hello.agent")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["agent"], "greeter")

    def test_research_pipeline_example(self):
        """Test examples/research_pipeline.agent runs successfully."""
        interpreter = Interpreter()
        result = interpreter.run_file("examples/research_pipeline.agent")
        
        self.assertIsNotNone(result)
        # Should have run the pipeline


if __name__ == '__main__':
    unittest.main()
