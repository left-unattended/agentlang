"""Test suite for AgentLang runtime."""

import unittest
from agentlang.runtime.runtime import Runtime
from agentlang.runtime.agent import Agent
from agentlang.runtime.tool import Tool


class TestRuntime(unittest.TestCase):
    """Test the runtime component."""

    def setUp(self):
        """Create a fresh runtime for each test."""
        self.runtime = Runtime()

    def test_register_tool(self):
        """Test tool registration."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            params={"param1": {"type": "string", "required": True}},
            handler=lambda x: f"Result: {x}"
        )
        
        self.runtime.register_tool(tool)
        self.assertIn("test_tool", self.runtime.tools)
        self.assertEqual(self.runtime.tools["test_tool"], tool)

    def test_register_agent(self):
        """Test agent registration."""
        agent = Agent(
            name="test_agent",
            model="gpt-4",
            prompt="You are a test agent",
            tools=[]
        )
        
        self.runtime.register_agent(agent)
        self.assertIn("test_agent", self.runtime.agents)
        self.assertEqual(self.runtime.agents["test_agent"], agent)

    def test_builtin_tools_loaded(self):
        """Test that built-in tools are automatically loaded."""
        # Runtime should have built-in tools
        self.assertIn("web_search", self.runtime.tools)
        self.assertIn("read_file", self.runtime.tools)
        self.assertIn("write_file", self.runtime.tools)
        self.assertIn("http_get", self.runtime.tools)

    def test_run_agent_simple(self):
        """Test running a simple agent."""
        agent = Agent(
            name="greeter",
            model="gpt-4",
            prompt="You say hello",
            tools=[]
        )
        
        self.runtime.register_agent(agent)
        result = self.runtime.run_agent("greeter", {"task": "Say hello"})
        
        self.assertIsNotNone(result)
        self.assertEqual(result["agent"], "greeter")
        self.assertIn("output", result)

    def test_run_nonexistent_agent(self):
        """Test running an agent that doesn't exist."""
        with self.assertRaises(Exception):
            self.runtime.run_agent("nonexistent", {})

    def test_config_update(self):
        """Test updating runtime config."""
        self.runtime.update_config({
            "default_model": "gpt-3.5-turbo",
            "log_level": "debug"
        })
        
        self.assertEqual(self.runtime.config.get("default_model"), "gpt-3.5-turbo")
        self.assertEqual(self.runtime.config.get("log_level"), "debug")

    def test_agent_with_tools(self):
        """Test agent with tool access."""
        tool = Tool(
            name="test_tool",
            description="Test",
            params={},
            handler=lambda: "tool result"
        )
        
        agent = Agent(
            name="agent_with_tool",
            model="gpt-4",
            prompt="You use tools",
            tools=["test_tool"]
        )
        
        self.runtime.register_tool(tool)
        self.runtime.register_agent(agent)
        
        result = self.runtime.run_agent("agent_with_tool", {"task": "Use the tool"})
        self.assertIsNotNone(result)

    def test_multiple_agents(self):
        """Test registering and running multiple agents."""
        agent1 = Agent("agent1", "gpt-4", "Agent 1", [])
        agent2 = Agent("agent2", "gpt-4", "Agent 2", [])
        
        self.runtime.register_agent(agent1)
        self.runtime.register_agent(agent2)
        
        self.assertEqual(len(self.runtime.agents), 2)
        
        result1 = self.runtime.run_agent("agent1", {"task": "test"})
        result2 = self.runtime.run_agent("agent2", {"task": "test"})
        
        self.assertEqual(result1["agent"], "agent1")
        self.assertEqual(result2["agent"], "agent2")

    def test_agent_output_contains_metadata(self):
        """Test that agent output includes metadata."""
        agent = Agent("test", "gpt-4", "Test", [])
        self.runtime.register_agent(agent)
        
        result = self.runtime.run_agent("test", {"task": "test"})
        
        self.assertIn("agent", result)
        self.assertIn("model", result)
        self.assertIn("output", result)
        self.assertIn("params", result)


class TestAgent(unittest.TestCase):
    """Test the Agent class."""

    def test_agent_creation(self):
        """Test creating an agent."""
        agent = Agent(
            name="test",
            model="gpt-4",
            prompt="You are a test",
            tools=["tool1", "tool2"]
        )
        
        self.assertEqual(agent.name, "test")
        self.assertEqual(agent.model, "gpt-4")
        self.assertEqual(agent.prompt, "You are a test")
        self.assertEqual(len(agent.tools), 2)

    def test_agent_with_optional_params(self):
        """Test agent with temperature and max_tokens."""
        agent = Agent(
            name="test",
            model="gpt-4",
            prompt="Test",
            tools=[],
            temperature=0.5,
            max_tokens=500
        )
        
        self.assertEqual(agent.temperature, 0.5)
        self.assertEqual(agent.max_tokens, 500)


class TestTool(unittest.TestCase):
    """Test the Tool class."""

    def test_tool_creation(self):
        """Test creating a tool."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            params={"param1": {"type": "string", "required": True}},
            handler=lambda x: f"Result: {x}"
        )
        
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.description, "A test tool")
        self.assertIn("param1", tool.params)

    def test_tool_execution(self):
        """Test executing a tool."""
        def my_handler(x, y):
            return x + y
        
        tool = Tool(
            name="add",
            description="Add two numbers",
            params={},
            handler=my_handler
        )
        
        result = tool.execute(2, 3)
        self.assertEqual(result, 5)


if __name__ == '__main__':
    unittest.main()
