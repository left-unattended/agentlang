# AgentLang Test Suite

Comprehensive test coverage for the AgentLang interpreter.

## Test Structure

```
tests/
├── test_tokenizer.py    # Lexer/tokenizer tests
├── test_parser.py       # Parser tests (AST generation)
├── test_runtime.py      # Runtime/agent/tool tests
├── test_integration.py  # End-to-end integration tests
├── run_tests.py         # Test runner script
└── README.md           # This file
```

## Running Tests

### All Tests
```bash
# From project root
python3 tests/run_tests.py

# Or using unittest
python3 -m unittest discover tests
```

### Specific Test Files
```bash
python3 -m unittest tests.test_tokenizer
python3 -m unittest tests.test_parser
python3 -m unittest tests.test_runtime
python3 -m unittest tests.test_integration
```

### Single Test Case
```bash
python3 -m unittest tests.test_tokenizer.TestTokenizer.test_keywords
```

## Test Coverage

### Tokenizer Tests (`test_tokenizer.py`)
- [x] Keyword recognition
- [x] Identifier parsing
- [x] String literals
- [x] Number parsing (integers and floats)
- [x] Symbol/operator tokenization
- [x] Comment handling (single-line and multi-line)
- [x] Complex expressions
- [x] Whitespace handling
- [x] Empty input

### Parser Tests (`test_parser.py`)
- [x] Simple agent definitions
- [x] Agents with tools
- [x] Agents with optional parameters (temperature, max_tokens)
- [x] Tool definitions with params and handlers
- [x] Config blocks
- [x] Run statements
- [x] Variable assignment (let statements)
- [x] Pipeline definitions
- [x] Pipeline error handling (on_error)
- [x] Multiple statements
- [x] Nested objects
- [x] Empty blocks

### Runtime Tests (`test_runtime.py`)
- [x] Tool registration
- [x] Agent registration
- [x] Built-in tools loaded
- [x] Running agents
- [x] Error handling for nonexistent agents
- [x] Config updates
- [x] Agents with tools
- [x] Multiple agents
- [x] Output metadata
- [x] Agent creation
- [x] Tool creation and execution

### Integration Tests (`test_integration.py`)
- [x] Hello world program
- [x] Agents with built-in tools
- [x] Config overrides
- [x] Multiple agents
- [x] Custom temperature/max_tokens
- [x] Complex parameters
- [x] Comments in code
- [x] Multiple tools
- [x] Empty tools list
- [x] Minimal agent definitions
- [x] Example programs (hello.agent, research_pipeline.agent)

## Test Status

**Total Tests:** 47  
**Currently Passing:** ~16 (34%)  
**Known Issues:** 31 (66%)

## Known Issues

### Critical Fixes Needed
1. **Tokenizer newline handling** - `skip_whitespace()` throws TypeError with None
2. **Interpreter API** - Tests expect `run_file()` method, but it's a standalone function
3. **Runtime API** - `update_config()` method doesn't exist
4. **Tool API** - `execute()` method doesn't exist

These are test/implementation mismatches that need to be resolved.

## Contributing

When adding new features to AgentLang:

1. Write tests FIRST (TDD approach)
2. Add test cases to the appropriate test file
3. Ensure all tests pass before committing
4. Update this README with new test coverage

## Test Philosophy

- **Unit tests** should test individual components in isolation
- **Integration tests** should test complete programs end-to-end
- Tests should be fast, deterministic, and independent
- Mock external dependencies (LLM API calls, file I/O where appropriate)
- Test both happy path and error cases
