"""Test LLM integration and tool execution"""

import unittest
import os
from agentlang.runtime.runtime import Runtime
from agentlang.runtime.agent import Agent
from agentlang.runtime.tool import Tool


class TestLLMIntegration(unittest.TestCase):
    """Test real LLM integration"""
    
    def setUp(self):
        """Create a runtime for testing"""
        self.runtime = Runtime()
    
    def test_mock_mode_default(self):
        """Test that mock mode is used when no API keys"""
        # Ensure no API keys in env
        old_openai = os.environ.pop('OPENAI_API_KEY', None)
        old_anthropic = os.environ.pop('ANTHROPIC_API_KEY', None)
        
        try:
            agent = Agent(
                name="test",
                model="gpt-4",
                prompt="You are a test agent",
                tools=[]
            )
            
            self.runtime.register_agent(agent)
            result = self.runtime.run_agent("test", {"task": "Hello"})
            
            # Should get mock response
            self.assertIn("MOCK", result["output"])
            
        finally:
            # Restore env
            if old_openai:
                os.environ['OPENAI_API_KEY'] = old_openai
            if old_anthropic:
                os.environ['ANTHROPIC_API_KEY'] = old_anthropic
    
    def test_tool_execution_mock(self):
        """Test tool execution in mock mode"""
        # Force mock mode
        os.environ['AGENTLANG_MOCK_LLM'] = 'true'
        
        try:
            # Register agent with tool
            agent = Agent(
                name="worker",
                model="gpt-4",
                prompt="You use tools",
                tools=["test_tool"]
            )
            
            # Register a test tool
            def test_handler(x: int) -> int:
                return x * 2
            
            tool = Tool(
                name="test_tool",
                description="Doubles a number",
                params={"x": {"type": "int", "required": True}},
                handler=test_handler
            )
            
            self.runtime.register_tool(tool)
            self.runtime.register_agent(agent)
            
            result = self.runtime.run_agent("worker", {"task": "Double 5"})
            
            # Mock mode doesn't execute tools, just returns mock
            self.assertIsNotNone(result)
            
        finally:
            os.environ.pop('AGENTLANG_MOCK_LLM', None)
    
    def test_provider_detection(self):
        """Test auto provider detection from model name"""
        from agentlang.llm.provider import LLMProvider
        
        self.assertEqual(LLMProvider.detect_provider("gpt-4"), "openai")
        self.assertEqual(LLMProvider.detect_provider("gpt-3.5-turbo"), "openai")
        self.assertEqual(LLMProvider.detect_provider("o1-preview"), "openai")
        self.assertEqual(LLMProvider.detect_provider("claude-3-opus"), "anthropic")
        self.assertEqual(LLMProvider.detect_provider("claude-sonnet-4"), "anthropic")
        self.assertEqual(LLMProvider.detect_provider("unknown-model"), "openai")  # Default
    
    @unittest.skipIf(not os.environ.get('OPENAI_API_KEY'), "Requires OPENAI_API_KEY")
    def test_real_openai_integration(self):
        """Test real OpenAI API call (skipped if no API key)"""
        agent = Agent(
            name="greeter",
            model="gpt-4",
            prompt="You are friendly. Keep responses very short.",
            tools=[]
        )
        
        self.runtime.register_agent(agent)
        result = self.runtime.run_agent("greeter", {"task": "Say hi"})
        
        # Should get real response
        self.assertNotIn("MOCK", result["output"])
        self.assertIn("usage", result)
        self.assertGreater(result["usage"]["total_tokens"], 0)
    
    @unittest.skipIf(not os.environ.get('ANTHROPIC_API_KEY'), "Requires ANTHROPIC_API_KEY")
    def test_real_anthropic_integration(self):
        """Test real Anthropic API call (skipped if no API key)"""
        agent = Agent(
            name="claude_test",
            model="claude-3-haiku-20240307",
            prompt="You are helpful. Keep responses very short.",
            tools=[]
        )
        
        self.runtime.register_agent(agent)
        result = self.runtime.run_agent("claude_test", {"task": "Say hello"})
        
        # Should get real response
        self.assertNotIn("MOCK", result["output"])
        self.assertIn("usage", result)
        self.assertGreater(result["usage"]["total_tokens"], 0)


if __name__ == '__main__':
    unittest.main()
