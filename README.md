# AgentLang

**A declarative language for AI agent orchestration.**

Dead simple. Actually works. Better than LangChain.

## What is AgentLang?

AgentLang lets you define AI agents that **actually use tools** with <10 lines of code. No boilerplate. No complexity. Just agents that work.

```agentlang
agent researcher {
  model: "gpt-4"
  prompt: "You are a research assistant."
  tools: [web_search]
}

run researcher with {
  task: "What are the latest AI breakthroughs in 2024?"
}
```

**That's it.** The agent will:
1. Use web_search tool to find information
2. Read the results
3. Answer your question

No 20+ lines of LangChain boilerplate. No wrestling with callbacks. Just declarative simplicity.

## Installation

### Option 1: Quick Start (from GitHub)

```bash
git clone https://github.com/left-unattended/agentlang.git
cd agentlang
pip install -r requirements.txt
```

### Option 2: From PyPI (coming soon)

```bash
pip install agentlang
```

## Setup

Set your API key:

```bash
# For OpenAI (GPT models)
export OPENAI_API_KEY=sk-...

# For Anthropic (Claude models)
export ANTHROPIC_API_KEY=sk-ant-...
```

## Quick Start

### 1. Create a file `hello.agent`:

```agentlang
agent greeter {
  model: "gpt-4"
  prompt: "You are a friendly assistant."
}

run greeter with {
  task: "Say hello to the world"
}
```

### 2. Run it:

```bash
python3 -m agentlang hello.agent
```

### 3. Watch it work! 🎉

The agent will call the real GPT-4 API and respond.

## Features

✅ **Fully Working:**
- ✓ Real LLM integration (OpenAI GPT-*, Anthropic Claude-*)
- ✓ **Tool execution loop** (agents actually use their tools!)
- ✓ Multi-provider support (auto-detects from model name)
- ✓ Built-in tools (web_search, read_file, write_file, http_get)
- ✓ Function calling / tool use (both OpenAI and Anthropic)
- ✓ Pipeline composition (chain agents)
- ✓ Error handling with retry and fallback
- ✓ Token usage tracking
- ✓ Streaming support (implemented, not exposed yet)
- ✓ 52 comprehensive tests (all passing)

📋 **Roadmap:**
- PyPI package distribution
- More examples (real-world use cases)
- Better error messages
- Streaming API
- Custom tool handlers from files
- Inter-agent messaging
- REPL/interactive mode

## Examples

### Simple Agent

```agentlang
config {
  default_model: "gpt-4"
}

agent assistant {
  model: "gpt-4"
  prompt: "You are helpful and concise."
  temperature: 0.7
}

run assistant with {
  task: "Explain quantum computing in one sentence."
}
```

### Agent with Tools

```agentlang
agent researcher {
  model: "gpt-4"
  prompt: "You are a research assistant. Use web_search to find accurate information."
  tools: [web_search]
  temperature: 0.3
}

run researcher with {
  task: "What are the latest major developments in AI in 2024? Give me 3 specific examples."
}
```

The agent will **actually call web_search**, read results, and answer based on real data!

### Multi-Agent Pipeline

```agentlang
agent researcher {
  model: "gpt-4"
  prompt: "You research topics thoroughly."
  tools: [web_search]
}

agent summarizer {
  model: "gpt-4"
  prompt: "You create concise summaries."
}

agent formatter {
  model: "gpt-3.5-turbo"
  prompt: "You format text into clean markdown."
}

pipeline research_pipeline {
  researcher -> summarizer -> formatter
  
  on_error: {
    retry: 2
  }
}

run research_pipeline with {
  task: "Latest breakthroughs in quantum computing"
}
```

See `examples/` for more.

## Language Syntax

### Agent Definition

```agentlang
agent <name> {
  model: "<model-name>"       // Required (e.g., "gpt-4", "claude-sonnet-4")
  prompt: "<system-prompt>"   // Required
  tools: [tool1, tool2]       // Optional
  temperature: 0.7            // Optional (default: 0.7)
  max_tokens: 2000            // Optional (default: 2000)
}
```

**Supported models:**
- OpenAI: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`, `o1-preview`, etc.
- Anthropic: `claude-3-opus`, `claude-sonnet-4`, `claude-3-haiku`, etc.

Auto-detects provider from model name!

### Built-in Tools

- `web_search(query)` - Search the web
- `read_file(path)` - Read a file
- `write_file(path, content)` - Write to a file
- `http_get(url)` - HTTP GET request

### Pipeline

```agentlang
pipeline <name> {
  agent1 -> agent2 -> agent3
  
  on_error: {
    retry: 2
    fallback: backup_agent
  }
}
```

### Variables

```agentlang
let result = run my_agent with { task: "Hello" }
```

### Configuration

```agentlang
config {
  default_model: "gpt-4"
  log_level: "info"
}
```

## CLI Usage

```bash
# Run a file
python3 -m agentlang script.agent

# Verbose mode (see LLM calls, token usage, etc.)
python3 -m agentlang -v script.agent

# Show version
python3 -m agentlang --version
```

## Why AgentLang vs LangChain/CrewAI?

### LangChain (Python):

```python
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

# Define tool
search_tool = Tool(
    name="web_search",
    func=web_search_function,
    description="Search the web"
)

# Initialize agent
llm = ChatOpenAI(model="gpt-4", temperature=0.7)
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Run
result = agent.run("Research AI trends")
```

**~25 lines of Python boilerplate**

### AgentLang:

```agentlang
agent researcher {
  model: "gpt-4"
  prompt: "You research topics."
  tools: [web_search]
}

run researcher with { task: "Research AI trends" }
```

**6 lines. Zero boilerplate. Same functionality.**

## How It Works

1. **Tokenizer** → converts `.agent` files to tokens
2. **Parser** → builds Abstract Syntax Tree (AST)
3. **Interpreter** → executes the AST
4. **Runtime** → manages agents, tools, and LLM calls
5. **LLM Providers** → handles OpenAI/Anthropic APIs with function calling

**Tool execution loop:**
- Agent requests tool → Runtime executes → Feeds result back to LLM → Continues until done
- Max 10 iterations to prevent infinite loops
- Full token usage tracking

## Testing

```bash
# Run all 52 tests
python3 tests/run_tests.py

# Run specific test modules
python3 -m unittest tests.test_tokenizer
python3 -m unittest tests.test_parser
python3 -m unittest tests.test_runtime
python3 -m unittest tests.test_integration
python3 -m unittest tests.test_llm_integration
```

**Test Coverage:**
- ✓ Tokenizer/lexer
- ✓ Parser/AST
- ✓ Runtime
- ✓ Integration (end-to-end)
- ✓ LLM providers (OpenAI, Anthropic)

All 52 tests passing!

## Development

### Project Structure

```
agentlang/
├── agentlang/
│   ├── lexer/           # Tokenization
│   ├── parser/          # AST generation
│   ├── interpreter/     # Execution
│   ├── runtime/         # Agent/tool management
│   └── llm/            # LLM provider abstraction
├── examples/            # Example programs
├── tests/              # Test suite
├── SPEC.md             # Language specification
└── README.md           # This file
```

### Contributing

Pull requests welcome! This is a collaborative project.

**Guidelines:**
- Keep it simple (complexity is a bug)
- Add tests for new features
- Update SPEC.md for language changes
- Follow existing code style

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (for GPT models)
- `ANTHROPIC_API_KEY` - Your Anthropic API key (for Claude models)
- `AGENTLANG_MOCK_LLM=true` - Use mock responses (for testing without API keys)

## License

MIT

## Links

- GitHub: https://github.com/left-unattended/agentlang
- Spec: [SPEC.md](SPEC.md)
- Tests: [tests/README.md](tests/README.md)
