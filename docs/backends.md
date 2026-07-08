# Backends Guide

SynthLang supports three execution backends that can be combined for optimal performance and flexibility:

## Backend Overview

| Component | Language | Purpose | Status |
|-----------|----------|---------|--------|
| **Rust Core** | Rust | Lexing, Parsing, Compilation, VM, GC | Default for performance |
| **Go FFI** | Go | Foreign Function Interface, Scheduler | Default for concurrency |
| **Python Fallback** | Python | Backward compatibility, debugging | Fallback when native libs missing |

## CLI Flags

### Core Backend Selection

```bash
slang script.sl --rust      # Force Rust Core (default if available)
slang script.sl --python    # Force Python Core
```

### FFI Backend Selection

```bash
slang script.sl --go       # Force Go FFI (default if available)
slang script.sl --pyffi     # Force Python FFI
```

### Combined Examples

```bash
slang script.sl --rust --go      # Rust Core + Go FFI (default)
slang script.sl --python --go    # Python Core + Go FFI
slang script.sl --rust --pyffi   # Rust Core + Python FFI
slang script.sl --python --pyffi # Fully Python (original behavior)
```

## Architecture

```
┌─────────────────┐
│   CLI (Python)  │
├─────────────────┤
│ Backend Router  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ Rust  │ │ Python│
│ Core  │ │ Core  │
└───┬───┘ └───────┘
    │
    ▼
┌───────┐ ┌───────┐
│  Go   │ │Python │
│ FFI   │ │ FFI   │
└───────┘ └───────┘
```

## Rust Core Functions

When `synthlang_core` is available, the following functions are exported:

```python
from synthlang import lex, parse, compile, execute

# Tokenize source code
tokens = lex("let x = 10")

# Parse to AST
ast = parse("let x = 10")

# Compile to IR
ir = compile("let x = 10")

# Execute and get results
result = execute("let x = 10", debug=False)
```

## Go FFI Functions

When `libgoffi` is available, the following operations are supported:

```python
from synthlang.cli import go_load_module, go_call_function, go_spawn_task, go_await_task

# Load a module
module_id = go_load_module("python", "os")

# Call a function
result = go_call_function("os", "getenv", '["HOME"]')

# Spawn a concurrent task
task_id = go_spawn_task("process_data", '{"data": [1,2,3]}')

# Await task completion
result = go_await_task(task_id)
```

## Fallback Behavior

SynthLang gracefully degrades when native libraries are unavailable:

1. **Rust Core missing**: Falls back to Python implementation with a warning
2. **Go FFI missing**: Falls back to Python FFI implementation
3. **Both missing**: Uses pure Python for all operations

```python
# Example warning when Rust is unavailable
# Warning: synthlang_core not available, using Python backend
```

## Performance Comparison

| Operation | Rust Core | Python Core |
|-----------|-----------|-------------|
| Tokenization | ~10x faster | Baseline |
| Parsing | ~8x faster | Baseline |
| Compilation | ~5x faster | Baseline |
| Execution | ~3x faster | Baseline |

## Building Native Libraries

### Rust Core

```bash
cd src/rust
cargo build --release
# Output: synthlang_core.dll / .so / .dylib
```

### Go FFI

```bash
cd src/go
go build -buildmode=c-shared -o libgoffi.dll ffi.go
# Output: libgoffi.dll / .so / .dylib + libgoffi.h
```

## Debugging

Use `--debug` flag to see detailed execution information:

```bash
slang script.sl --debug --python
```

This shows IR generation and stack traces when using the Python backend.