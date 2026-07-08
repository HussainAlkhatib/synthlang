# Getting Started with SynthLang

## Installation

```bash
pip install synthlang
```

Or from source:
```bash
git clone https://github.com/synthlang/synthlang.git
cd synthlang
pip install -e .
```

## Your First Program

Create `hello.sl`:
```sl
# Your first SynthLang program
print("Hello, World!")
```

Run it:
```bash
slang hello.sl
```

## Build a Web Server

Create `server.sl`:
```sl
# Web Server using built-in web capabilities
@web
fn index(): str
    return "Welcome to SynthLang!"

@web
fn api_users(): list
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]

fn main(): void
    print("Server starting on http://localhost:8080")
```

## Build a CLI Tool

Create `tool.sl`:
```sl
# CLI Tool example
fn greet(name: str): str
    return "Hello, " + name + "!"

fn main(): void
    let user = "World"
    print(greet(user))
```

## Build a Concurrent Task Runner

Create `tasks.sl`:
```sl
# Concurrent task runner using goroutines
fn worker(id: int): int
    return id * 2

fn main(): void
    go worker(1)
    go worker(2)
    go worker(3)
    print("Tasks dispatched!")
```

## Core Concepts

### Variables

Use `let` for immutable bindings and `var` for mutable ones.

```sl
let x = 10        # Immutable
var y = 20        # Mutable
let z: int = 30   # With type annotation
```

### Functions

Functions are declared with `fn`.

```sl
fn add(a: int, b: int): int
    return a + b

let result = add(3, 4)
print(result)
```

### Control Flow

Uses Python-style indentation.

```sl
if x > 0:
    print("positive")
else:
    print("non-positive")

for i in [1, 2, 3]:
    print(i)

while flag:
    process()
```

### Memory Management

Three modes available:

```sl
@gc
fn gc_func(): int
    return 42

@rc
fn rc_func(): int
    return 42
```

### Concurrency

Goroutine-like lightweight threads:

```sl
go background_task()
await task_id
```

## VS Code Setup

1. Install the SynthLang extension from the VS Code Marketplace
2. Open any `.sl` file for syntax highlighting
3. LSP features include:
   - Auto-completion
   - Hover documentation
   - Go to definition

## Next Steps

- Read [syntax.md](syntax.md) for complete language reference
- Check [design_notes.md](design_notes.md) for architecture
- Run `examples/` for working programs