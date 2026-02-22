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

## Contributing

This is a collaborative project. See the spec in `SPEC.md`.

## License

MIT
