# SynthLang Design Notes

## Architecture

```
Source Code (.sl)
      │
      ▼
┌───────────┐
│   Lexer   │  → Tokens
└───────────┘
      │
      ▼
┌───────────┐
│  Parser   │  → AST
└───────────┘
      │
      ▼
┌───────────┐
│ Compiler  │  → IR
└───────────┘
      │
      ▼
┌───────────┐
│    VM     │  → Execution
└───────────┘
```

## Final Architecture (v1.0.0)

The SynthLang v1.0.0 architecture consists of:

### Frontend (Lexer & Parser)
- **Lexer** (`src/synthlang/lexer.py`): Tokenizes source code into a stream of tokens
- **Parser** (`src/synthlang/parser.py`): Recursive descent parser producing AST nodes

### Middle-end (Compiler)
- **Compiler** (`src/synthlang/compiler.py`): Transforms AST to Linear IR
- **IR** (`src/synthlang/ir.py`): Intermediate representation with explicit instructions

### Backend (VM)
- **VM** (`src/synthlang/vm.py`): Stack-based interpreter executing IR
- **GC** (`src/synthlang/gc.py`): Mark-and-sweep garbage collector
- **Scheduler** (`src/synthlang/scheduler.py`): Cooperative threading

### Runtime Features
- **Type System** (`src/synthlang/type_system.py`): Optional static typing
- **FFI** (`src/synthlang/ffi.py`): Foreign function interface (C/Rust/Java)
- **Formatter** (`src/synthlang/formatter.py`): Code formatting
- **Tester** (`src/synthlang/tester.py`): Built-in testing framework
- **LSP** (`src/synthlang/lsp.py`): Language server protocol support

## CLI (`src/synthlang/cli.py`)

Full subcommand support:
- `slang run file.sl` - Run a file
- `slang init [name]` - Initialize new project
- `slang build [--release]` - Build executable
- `slang test [file]` - Run tests
- `slang fmt [path]` - Format code
- `slang eval "code"` - Evaluate string
- `slang repl` - Start REPL
- `slang pip install <pkg>` - Install PyPI package
- `slang npm install <pkg>` - Install npm package
- `slang install` - Install all dependencies
- `slang list` - List dependencies
- `slang make slangs` - Create manifest
- `slang doctor` - Check environment

## Dependency Manager (`src/synthlang/dependency.py`)

- Parses `slangs.json` manifest
- Supports pip and npm dependencies
- Generates `slangs.lock` for reproducibility
- Version constraint parsing (^, >=, etc.)

## FFI (`src/synthlang/ffi.py`)

Foreign Function Interface for:
- C (`ctypes.CDLL`)
- Rust (compiled as shared library)
- Java (JNI stubs)

Annotations: `@rust`, `@c`, `@java`, `@web`, `@mobile`, `@cli`, `@desktop`

## Type System (`src/synthlang/type_system.py`)

- TypeKind enum: INT, FLOAT, STRING, BOOL, VOID, ARRAY, DICT, STRUCT, INTERFACE, FUNCTION, GENERIC
- TypeInferer for automatic type inference
- Struct and interface support
- Generic function support (planned)

## Scheduler (`src/synthlang/scheduler.py`)

Cooperative threading with goroutine-like semantics:
- `go func()` spawns a task via SPAWN_THREAD IR instruction
- Work queue for task management
- SystemThread wrapper for native threads

## Memory Management (`src/synthlang/gc.py`)

Three modes supported:
- **GC** (default): Mark-and-sweep in GC class
- **RC**: `RefCounted` objects with `RCManager`
- **Manual**: `@manual` annotation with explicit `alloc`/`free`

IR instructions: `ALLOC`, `FREE`, `INCREMENT_RC`, `DECREMENT_RC`

## VM (`src/synthlang/vm.py`)

Stack-based interpreter with Result type:
- Value stack for expression evaluation
- Variable store for bindings
- Function call stack
- `Ok`/`Err` variants for error handling
- Built-in `print` function support

## Decisions and Trade-offs

1. **Linear IR vs SSA**: Chose linear IR for simplicity and ease of debugging
2. **Stack-based VM**: Chose stack-based for straightforward implementation
3. **Python implementation**: v1.0.0 in Python for rapid prototyping; future Rust rewrite planned
4. **Indentation-based syntax**: Familiar to Python developers, clean and readable
5. **Optional typing**: Flexibility for scripting, safety for production

## Future Work (v2.0.0)

- Native code generation (LLVM/Cranelift)
- Full Rust implementation
- WebAssembly target
- Enhanced type inference
- Package manager (slangs.io)