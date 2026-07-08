# SynthLang Syntax Guide

## Core Language Features

### Variables
```
let x = 5           // Immutable variable
var y = 10          // Mutable variable
let z: int = 15     // With type annotation
```

### Functions
```
fn add(a: int, b: int): int
    return a + b

let result = add(3, 4)
```

### Control Flow
```
if x > 0:
    let y = 1
elif x < 0:
    let y = -1
else:
    let y = 0

for i in [1, 2, 3]:
    print(i)

while flag:
    process()
```

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Logical: `&&`, `||`, `!`

### Literals
- Integers: `42`, `-10`
- Floats: `3.14`, `-0.5`
- Strings: `"hello"`
- Booleans: `true`, `false`
- Lists: `[1, 2, 3]`
- Dicts: `{a: 1, b: 2}`

## Memory Management

```
@gc     // Default: mark-and-sweep garbage collector
fn gc_func(): int
    return 42

@rc
fn rc_func(): int
    return 42

@manual
fn manual_func(): int
    alloc x
    free x
    return 0
```

## Concurrency

```
go worker(data)
let result = await task_id

let ch = channel<int>(10)
ch <- 5
let val = <- ch
```

## Error Handling

> **Note:** `match`, `defer`, `try/handle` are planned features for future versions. Currently, error handling is limited to basic control flow.

```
# Future syntax for error handling:
try risky_operation():
    # Not yet implemented
```

## FFI

```
@c
fn c_func(x: int): int
    // C function declaration
    return 0

@rust module "lib.rs" as crypto
fn rust_func(): int
    // Rust module integration
    return 0
```

## CLI Commands

```
slang run file.sl         # Run a file
slang run --debug file.sl # Run with debug output (IR and stack trace)
slang init [name]         # Initialize project
slang build [--release]   # Build executable
slang test [file]         # Run tests
slang fmt [path]          # Format code
slang eval "code"         # Evaluate string
slang repl                # Interactive REPL
slang pip install pkg     # Install PyPI package
slang npm install pkg     # Install npm package
slang install             # Install all dependencies
slang list                # List dependencies
slang doctor              # Check environment
slang watch file.sl       # Watch and re-run
slang --version           # Show version
```

## Known Limitations (v1.1.1)

The following features are **planned but not yet fully implemented**:

- **`go`/`await` full support**: Currently parsed but requires event loop integration
- **`@web`, `@mobile`, `@desktop` annotations**: Parsed but not yet functional - stub implementations
- **`@cli` annotation**: Registers function as main entry point
- **`match` statement**: Not implemented (use `if`/`elif`/`else` instead)
- **`defer` statement**: Not implemented
- **`try`/`handle` error handling**: Not implemented (use control flow instead)
- **Global `@rc`, `@manual`, `@event_loop` annotations**: Partially implemented

## slangs.json Manifest

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "dependencies": {
    "pip": {"requests": "^2.28.0"},
    "npm": {"axios": "^1.4.0"}
  }
}
```