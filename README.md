# AgentLang

**A declarative language for AI agent orchestration.**

Simple. Composable. Readable.

## What is AgentLang?

AgentLang makes it dead simple to define AI agents, give them tools, chain them into pipelines, handle errors, and manage inter-agent communication.

If it's not simpler than writing raw Python, we've failed.

## Installation

```bash
git clone https://github.com/left-unattended/agentlang.git
cd agentlang
```

No dependencies required for basic usage!

## Quick Start

Create a file `hello.agent`:

```agentlang
agent greeter {
  model: "gpt-4"
  prompt: "You are a friendly assistant."
}

run greeter with {
  task: "Say hello to the world"
}
```

Run it:

```bash
python3 -m agentlang hello.agent
```

## Features

✅ **Working:**
- ✓ Declarative agent definitions
- ✓ Tool system with built-ins (web_search, read_file, write_file, http_get)
- ✓ Pipeline composition (chain agents)
- ✓ Error handling with retry and fallback
- ✓ Variable assignments
- ✓ Global configuration

🚧 **TODO:**
- LLM API integration (OpenAI, Anthropic, etc.) - currently mock responses
- Custom tool handlers (Python functions)
- Inter-agent messaging
- Streaming responses
- Parallel agent execution

## Example: Research Pipeline

```agentlang
// Define agents
agent researcher {
  model: "gpt-4"
  prompt: "You are a research assistant."
  tools: [web_search]
}

agent summarizer {
  model: "gpt-4"
  prompt: "You create concise summaries."
}

// Chain them
pipeline research_pipeline {
  researcher -> summarizer
  
  on_error: {
    retry: 2
  }
}

// Run it
let results = run research_pipeline with {
  task: "What are the latest breakthroughs in quantum computing?"
}
```

See `examples/` for more examples.

## Language Syntax

### Agent Definition

```agentlang
agent <name> {
  model: "<model-name>"       // Required
  prompt: "<system-prompt>"   // Required
  tools: [tool1, tool2]       // Optional
  temperature: 0.7            // Optional (default: 0.7)
  max_tokens: 2000            // Optional (default: 2000)
}
```

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

### Run Statement

```agentlang
run <agent|pipeline> with {
  task: "Do something"
  context: "Additional info"
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

## Architecture

```
agentlang/
├── lexer/        # Tokenizer
├── parser/       # AST builder
├── interpreter/  # AST executor
└── runtime/      # Agent/tool execution engine
```

## CLI Usage

```bash
python3 -m agentlang <file.agent>       # Run a file
python3 -m agentlang -v <file.agent>    # Verbose mode
python3 -m agentlang --version          # Show version
```

## Testing

AgentLang includes a comprehensive test suite covering all components:

```bash
# Run all tests
python3 tests/run_tests.py

# Run specific test module
python3 -m unittest tests.test_tokenizer
python3 -m unittest tests.test_parser
python3 -m unittest tests.test_runtime
python3 -m unittest tests.test_integration
```

**Test Coverage:**
- ✓ Tokenizer/lexer (keywords, literals, operators, comments)
- ✓ Parser (AST generation for all language constructs)
- ✓ Runtime (agent/tool registration and execution)
- ✓ Integration (end-to-end program execution)

See `tests/README.md` for detailed test documentation.

## Development

### Project Structure

```
agentlang/
├── agentlang/
│   ├── lexer/           # Tokenization (text → tokens)
│   │   └── tokenizer.py
│   ├── parser/          # Parsing (tokens → AST)
│   │   ├── parser.py
│   │   └── ast_nodes.py
│   ├── interpreter/     # Execution (AST → actions)
│   │   └── interpreter.py
│   └── runtime/         # Agent/tool runtime
│       ├── runtime.py
│       ├── agent.py
│       └── tool.py
├── examples/            # Example .agent programs
├── tests/              # Test suite
├── SPEC.md             # Language specification
└── README.md           # This file
```

### Adding New Features

1. **Update SPEC.md** with the new language feature
2. **Add tests** in `tests/` for the feature
3. **Implement** in lexer/parser/interpreter/runtime
4. **Verify** all tests pass
5. **Add examples** demonstrating the feature

### Adding New Tools

Built-in tools are defined in `agentlang/runtime/runtime.py`. To add a new tool:

```python
def my_tool_handler(**kwargs):
    """Your tool implementation"""
    return result

runtime.register_tool(Tool(
    name="my_tool",
    description="What it does",
    params={"param1": {"type": "string", "required": True}},
    handler=my_tool_handler
))
```

## Contributing

This is a collaborative project. Pull requests welcome!

**Guidelines:**
- Follow the existing code style
- Add tests for new features
- Update SPEC.md if adding language features
- Keep it simple - complexity is a bug

See `SPEC.md` for the language specification.

## Roadmap

**v0.2** (Next):
- Real LLM API integration (OpenAI/Anthropic)
- Custom Python tool handlers from files
- Better error messages
- Pipeline result passing

**v0.3** (Later):
- Inter-agent messaging
- Streaming responses
- Parallel execution
- REPL/interactive mode

## License

MIT
