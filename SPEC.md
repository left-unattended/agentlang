# AgentLang Specification v0.1

## Philosophy

**AgentLang is a declarative language for AI agent orchestration that prioritizes simplicity over flexibility.**

If it takes more than 10 lines to define an agent with tools and chain it into a pipeline, we've failed.

## Core Concepts

### 1. Agents

An agent is a named AI entity with a model, system prompt, and optional tools.

```agentlang
agent researcher {
  model: "gpt-4"
  prompt: "You are a research assistant. Find accurate information."
  tools: [web_search, read_file]
}
```

### 2. Tools

Tools are functions that agents can call. They have a name, description, and parameters.

```agentlang
tool web_search {
  description: "Search the web for information"
  params: {
    query: string required
    max_results: int default=5
  }
  handler: python("handlers/web_search.py")
}
```

### 3. Pipelines

Pipelines chain agents together. Output from one becomes input to the next.

```agentlang
pipeline research_and_summarize {
  researcher -> summarizer -> formatter
  
  on_error: {
    retry: 2
    fallback: simple_formatter
  }
}
```

### 4. Messages

Agents communicate through typed messages.

```agentlang
run researcher with {
  task: "Find the latest AI news"
  context: previous_results
}
```

## Syntax

### Agent Definition

```
agent <name> {
  model: <string>           // Required: LLM model to use
  prompt: <string>          // Required: system prompt
  tools: [<tool_names>]     // Optional: available tools
  temperature: <float>      // Optional: default 0.7
  max_tokens: <int>         // Optional: default 2000
}
```

### Tool Definition

```
tool <name> {
  description: <string>     // Required: what the tool does
  params: {                 // Required: parameter schema
    <name>: <type> [required|default=<value>]
  }
  handler: <handler_spec>   // Required: python(...) or builtin(...)
}
```

Handler types:
- `python("path/to/file.py")` - Python function in a file
- `builtin("function_name")` - Built-in AgentLang function

### Pipeline Definition

```
pipeline <name> {
  <agent> -> <agent> -> <agent>  // Chain of agents
  
  on_error: {                    // Optional error handling
    retry: <int>                 // Number of retries
    fallback: <agent_name>       // Fallback agent
  }
}
```

### Running Agents

```
run <agent|pipeline> with {
  <key>: <value>
  <key>: <value>
}
```

### Variables

```
let results = run researcher with { task: "AI news" }
let summary = run summarizer with { text: results.output }
```

## Built-in Tools

AgentLang provides these tools out of the box:

- `web_search(query)` - Search the web
- `read_file(path)` - Read a file
- `write_file(path, content)` - Write to a file
- `exec(command)` - Execute shell command
- `http_get(url)` - HTTP GET request
- `http_post(url, data)` - HTTP POST request

## Inter-Agent Communication

Agents can message each other directly:

```agentlang
agent coordinator {
  model: "gpt-4"
  prompt: "You coordinate tasks between agents."
  tools: [send_message]
}

send researcher message {
  task: "Research AI trends"
  priority: "high"
}
```

## Error Handling

Three levels of error handling:

1. **Agent-level**: Define fallback behavior per agent
```agentlang
agent researcher {
  model: "gpt-4"
  prompt: "..."
  on_error: {
    retry: 3
    fallback: simple_search
  }
}
```

2. **Pipeline-level**: Handle errors in the chain
```agentlang
pipeline process {
  agent1 -> agent2 -> agent3
  on_error: {
    retry: 2
    fallback: backup_pipeline
  }
}
```

3. **Global**: Catch-all in the runtime
```agentlang
config {
  default_retry: 2
  error_handler: log_and_continue
}
```

## Configuration

Global configuration for the runtime:

```agentlang
config {
  default_model: "gpt-4"
  default_temperature: 0.7
  default_max_tokens: 2000
  default_retry: 1
  log_level: "info"
  timeout: 300
}
```

## Comments

```agentlang
// Single line comment

/* 
  Multi-line comment
*/
```

## Complete Example

```agentlang
// Configuration
config {
  default_model: "gpt-4"
  log_level: "info"
}

// Define tools
tool web_search {
  description: "Search the web"
  params: {
    query: string required
    max_results: int default=5
  }
  handler: builtin("web_search")
}

// Define agents
agent researcher {
  model: "gpt-4"
  prompt: "You are a research assistant. Find accurate information and cite sources."
  tools: [web_search, read_file]
  temperature: 0.3
}

agent summarizer {
  model: "gpt-4"
  prompt: "You create concise summaries of research findings."
  temperature: 0.5
}

agent formatter {
  model: "gpt-3.5-turbo"
  prompt: "You format text into clean markdown."
}

// Define pipeline
pipeline research_pipeline {
  researcher -> summarizer -> formatter
  
  on_error: {
    retry: 2
    fallback: summarizer
  }
}

// Run it
let results = run research_pipeline with {
  task: "What are the latest breakthroughs in quantum computing?"
  format: "markdown"
}

// Output results
write_file("output.md", results.output)
```

## File Extension

AgentLang files use `.agent` extension: `pipeline.agent`

## Interpreter Requirements

The Python interpreter must:

1. Parse `.agent` files into an AST
2. Validate agent/tool/pipeline definitions
3. Execute agents using configured LLM APIs
4. Handle tool calls and return results to agents
5. Chain agents in pipelines with proper data flow
6. Implement error handling and retries
7. Support variable assignment and references
8. Log execution for debugging

## Design Principles

1. **Declarative over imperative**: Describe what you want, not how to do it
2. **Convention over configuration**: Smart defaults, minimal boilerplate
3. **Composable**: Agents and pipelines are building blocks
4. **Readable**: Anyone should understand a .agent file in 30 seconds
5. **Debuggable**: Clear error messages and execution logs

---

**Status**: Draft v0.1  
**Next**: Implement parser and interpreter in Python
