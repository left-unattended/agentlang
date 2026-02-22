# AgentLang Quick Start Guide

Get up and running with AgentLang in 5 minutes!

## Installation

### Step 1: Clone the repo

```bash
git clone https://github.com/left-unattended/agentlang.git
cd agentlang
```

### Step 2: Install dependencies

```bash
# Install OpenAI support
pip install openai

# OR install Anthropic support
pip install anthropic

# OR install both
pip install openai anthropic
```

### Step 3: Set your API key

```bash
# For OpenAI (GPT models)
export OPENAI_API_KEY=sk-...

# OR for Anthropic (Claude models)
export ANTHROPIC_API_KEY=sk-ant-...
```

**💡 Tip:** Add this to your `~/.bashrc` or `~/.zshrc` so you don't have to set it every time.

## Your First Agent

### 1. Create a file called `hello.agent`:

```agentlang
agent greeter {
  model: "gpt-4"
  prompt: "You are a friendly assistant who gives warm greetings."
}

run greeter with {
  task: "Say hello to the world and wish everyone a great day!"
}
```

### 2. Run it:

```bash
python3 -m agentlang hello.agent
```

### 3. Watch the magic happen! 🎉

You should see:
- The agent calling GPT-4
- Getting a response
- Printing the result

Output will look like:
```
15:30:45 [INFO] Running hello.agent
15:30:45 [INFO] Using openai provider for model gpt-4
15:30:46 [INFO] Agent greeter completed with 145 tokens
15:30:46 [INFO] Execution complete

Result: {'agent': 'greeter', 'model': 'gpt-4', 'output': 'Hello, world! I hope you all have a wonderful and productive day filled with positivity and success! 🌟', ...}
```

## Agent with Tools

Tools are where AgentLang really shines. Let's make an agent that can search the web!

### Create `researcher.agent`:

```agentlang
agent researcher {
  model: "gpt-4"
  prompt: "You are a research assistant. When asked to find information, use the web_search tool to get accurate, up-to-date information."
  tools: [web_search]
  temperature: 0.3
}

run researcher with {
  task: "What are the latest major developments in AI in 2024? Give me 3 specific examples with details."
}
```

### Run it:

```bash
python3 -m agentlang researcher.agent
```

### What happens:

1. Agent gets your task
2. **Automatically calls `web_search` tool** to find information
3. Reads the search results
4. Formulates a comprehensive answer
5. Returns the result

**This is the killer feature** - the agent actually USES tools without you writing any code!

## Multi-Agent Pipeline

Want to chain multiple agents together? Easy!

### Create `pipeline.agent`:

```agentlang
// Define specialized agents
agent researcher {
  model: "gpt-4"
  prompt: "You are a research assistant. Find accurate information."
  tools: [web_search]
}

agent summarizer {
  model: "gpt-4"
  prompt: "You create concise, well-organized summaries."
}

agent formatter {
  model: "gpt-3.5-turbo"
  prompt: "You format text into clean markdown with headers and bullet points."
}

// Chain them together
pipeline research_pipeline {
  researcher -> summarizer -> formatter
  
  on_error: {
    retry: 2
  }
}

// Run the pipeline
run research_pipeline with {
  task: "Research the latest developments in quantum computing"
}
```

### Run it:

```bash
python3 -m agentlang pipeline.agent
```

The pipeline will:
1. **Researcher** searches and gathers information
2. **Summarizer** condenses it into key points
3. **Formatter** makes it pretty

## Using Different Models

AgentLang auto-detects the provider from the model name:

```agentlang
// OpenAI models - auto-uses OpenAI provider
agent gpt_agent {
  model: "gpt-4"
  // or "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview", etc.
}

// Anthropic models - auto-uses Anthropic provider
agent claude_agent {
  model: "claude-3-opus"
  // or "claude-sonnet-4", "claude-3-haiku", etc.
}
```

No configuration needed! Just name the model and AgentLang handles the rest.

## Common Patterns

### Temperature Control

```agentlang
agent creative_writer {
  model: "gpt-4"
  temperature: 0.9  // Higher = more creative
}

agent data_analyst {
  model: "gpt-4"
  temperature: 0.1  // Lower = more deterministic
}
```

### Token Limits

```agentlang
agent concise {
  model: "gpt-4"
  max_tokens: 100  // Short responses
}

agent detailed {
  model: "gpt-4"
  max_tokens: 4000  // Long responses
}
```

### Multiple Tools

```agentlang
agent power_user {
  model: "gpt-4"
  tools: [web_search, read_file, write_file, http_get]
}
```

## Testing Without API Keys

Want to test without burning tokens?

```bash
export AGENTLANG_MOCK_LLM=true
python3 -m agentlang your_file.agent
```

This uses mock responses instead of real API calls.

## Troubleshooting

### "No API key found"

Make sure you've set the environment variable:
```bash
echo $OPENAI_API_KEY
```

If empty, set it:
```bash
export OPENAI_API_KEY=sk-your-key-here
```

### "Module not found"

Install the dependencies:
```bash
pip install openai anthropic
```

### "Import error"

Make sure you're in the agentlang directory and running:
```bash
python3 -m agentlang your_file.agent
```

Not:
```bash
python3 agentlang your_file.agent  # Wrong!
```

## Next Steps

1. **Check out examples/**
   - `examples/hello.agent` - Simple greeting
   - `examples/tool_usage.agent` - Agent using web search
   - `examples/research_pipeline.agent` - Multi-agent pipeline

2. **Read the docs**
   - `README.md` - Full feature documentation
   - `SPEC.md` - Language specification
   - `tests/README.md` - Test documentation

3. **Join the community**
   - Report issues on GitHub
   - Contribute new features
   - Share your .agent files!

## Tips & Tricks

**Verbose mode** to see what's happening:
```bash
python3 -m agentlang -v your_file.agent
```

**Keep files short** - split complex workflows into multiple files

**Use pipelines** for multi-step tasks

**Start simple** - get one agent working before chaining them

**Mock mode** for development - `AGENTLANG_MOCK_LLM=true`

## That's It!

You now know enough to build powerful AI agent systems with AgentLang. Have fun! 🚀
