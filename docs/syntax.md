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

### Match Statement (Pattern Matching)
```
match value:
    case 1:
        print("One")
    case 2, 3:
        print("Two or Three")
    case _:
        print("Default case")
```

### Defer Statement (Deferred Execution)
```
fn main():
    defer print("Goodbye!")
    print("Hello")
# Output: Hello, then Goodbye!
```

### Try/Handle (Error Handling)
```
try risky_operation():
    # code that may panic
handle error:
    print("Error:", error)
```

### Panic Function
```
if x == 0:
    panic("Cannot divide by zero")
```

## FFI

### Supported Languages
All 20 languages are supported:

| Language | Annotation | Example |
|----------|------------|---------|
| Python | `@python` | `@python module "os" as os` |
| JavaScript | `@javascript` | `@javascript module "fs" as fs` |
| Rust | `@rust` | `@rust module "./lib.rs" as lib` |
| Go | `@go` | `@go module "./main.go" as main` |
| C | `@c` | `@c module "./lib.c" as lib` |
| C++ | `@cpp` | `@cpp module "./lib.cpp" as lib` |
| Kotlin | `@kotlin` | `@kotlin module "./lib.kt" as lib` |
| Swift | `@swift` | `@swift module "./lib.swift" as lib` |
| PHP | `@php` | `@php module "./lib.php" as lib` |
| Ruby | `@ruby` | `@ruby module "./lib.rb" as lib` |
| Java | `@java` | `@java module "./Lib.java" as lib` |
| C# | `@csharp` | `@csharp module "./Lib.cs" as lib` |
| Lua | `@lua` | `@lua module "./lib.lua" as lib` |
| R | `@r` | `@r module "./lib.R" as lib` |
| Julia | `@julia` | `@julia module "./lib.jl" as lib` |
| Haskell | `@haskell` | `@haskell module "./lib.hs" as lib` |
| Elixir | `@elixir` | `@elixir module "./lib.ex" as lib` |
| Dart | `@dart` | `@dart module "./lib.dart" as lib` |
| Zig | `@zig` | `@zig module "./lib.zig" as lib` |
| TypeScript | `@typescript` | `@typescript module "./lib.ts" as lib` |

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

## Known Limitations (v1.2.0)

The following features are **implemented and functional**:

- **`match` statement**: Fully implemented with pattern matching support
- **`defer` statement**: Fully implemented with deferred execution on function exit
- **`try`/`handle` error handling**: Fully implemented with exception catching

Remaining limitations:

- **`go`/`await` full support**: Currently parsed but requires event loop integration
- **`@web`, `@mobile`, `@desktop` annotations**: Parsed but partial implementations
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