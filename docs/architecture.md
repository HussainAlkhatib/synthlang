# Architecture

SynthLang uses a three-backend architecture for optimal performance and flexibility.

## Three-Backend Design

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Layer (Python)                  │
│                   - User interface                      │
│                   - Command parsing                     │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                 Backend Router                            │
│           Routes to appropriate backend                     │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼             ▼               ▼
┌───────────┐  ┌───────────┐  ┌────────────┐
│ Rust Core │  │  Go FFI   │  │ Python Core│
│  (Primary)│  │ (Primary) │  │  (Fallback)│
└───────────┘  └───────────┘  └────────────┘
```

## Rust Core (`synthlang_core`)

The Rust Core handles the entire compilation pipeline:

- **Lexer**: Tokenization of source code
- **Parser**: AST generation
- **Compiler**: IR (Intermediate Representation) generation
- **VM**: Virtual Machine execution
- **GC**: Garbage Collection

When available, this is the default execution engine for maximum performance.

## Go FFI (`libgoffi`)

The Go FFI layer handles:

- **Foreign Function Interface**: Loading modules from Python, JavaScript, Rust, C, Go
- **Scheduler**: Goroutine-based concurrency with `go` and `await`
- **Task Management**: Spawn and manage parallel tasks

This layer is used for all FFI operations and concurrent execution.

## Python Fallback

The Python implementation serves as:

- **Backward compatibility**: Original SynthLang behavior
- **Development**: When native libraries are not built
- **Debugging**: Easier to trace and debug

All Python modules mirror the Rust/Go functionality:
- `lexer.py` - Tokenization
- `parser.py` - AST generation  
- `compiler.py` - IR generation
- `vm.py` - Virtual Machine
- `gc.py` - Garbage Collection
- `ffi.py` - Foreign Function Interface
- `scheduler.py` - Task scheduling

## Module Loading Priority

1. Check for Rust Core availability → use if available
2. Check for Go FFI availability → use for FFI/scheduling
3. Fall back to Python implementations

## FFI Implementation

When FFI is needed:
1. If Go FFI is available, delegate to `libgoffi`
2. Otherwise, use Python `ffi.py` implementation
3. Both provide the same interface for module loading

## Concurrency Model

```
┌─────────┐     ┌──────────┐     ┌────────────┐
│ Slang   │────▶│ Go       │────▶│ Goroutine  │
│ Source  │     │ Scheduler│     │ Pool       │
└─────────┘     └──────────┘     └────────────┘
     │                │                │
     ▼                ▼                ▼
┌────────────┐  ┌──────────┐  ┌────────────┐
│ SpawnTask  │  │ AwaitTask│  │ TaskResult │
│ (nonblock) │  │ (wait)   │  │ (complete) │
└────────────┘  └──────────┘  └────────────┘
```

## Memory Management

SynthLang supports three memory management modes:

| Mode | Flag | Description |
|------|------|-------------|
| **GC** | `@gc` | Automatic garbage collection (default) |
| **RC** | `@rc` | Reference counted - deterministic cleanup |
| **Manual** | `@manual` | Manual allocation/deallocation |

## Extension Points

- **Custom backends**: Implement `lex()`, `parse()`, `compile()`, `execute()`
- **FFI modules**: Add new language support via Go FFI or Python FFI
- **Standard library**: Extend via `std/` directory