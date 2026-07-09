# SynthLang Usage Guide

Version: 1.0.0

## Quick Start

```sl
# hello.sl
fn main():
    print("Hello, SynthLang!")
```

Run with: `slang hello.sl`

## Inline Language Tags

SynthLang supports writing code from 20 languages inline:

### Python

```sl
<py>
import json
result = {"message": "Hello from Python!"}
return json.dumps(result)
</py>
```

### R

```sl
<r>
x <- c(1, 2, 3)
mean(x)
</r>
```

### Rust

```sl
<rust>
fn main() {
    println!("Hello from Rust!");
}
</rust>
```

### All Supported Languages

- `<py>` - Python
- `<r>` - R
- `<rust>` - Rust
- `<go>` - Go
- `<cpp>` - C++
- `<c>` - C
- `<js>` - JavaScript
- `<ts>` - TypeScript
- `<kotlin>` - Kotlin
- `<swift>` - Swift
- `<php>` - PHP
- `<ruby>` - Ruby
- `<java>` - Java
- `<csharp>` - C#
- `<lua>` - Lua
- `<julia>` - Julia
- `<haskell>` - Haskell
- `<elixir>` - Elixir
- `<dart>` - Dart
- `<zig>` - Zig

## Pattern Matching

```sl
match value:
    case 1:
        print("One")
    case 2, 3, 4:
        print("Two, Three, or Four")
    case _:
        print("Other")
```

## Deferred Execution

```sl
fn process():
    defer cleanup()
    defer print("Done")
    print("Processing...")
```

## Error Handling

```sl
try risky_operation():
    handle error:
        print("Error:", error)
```

## FFI Examples

```sl
# Import Python library
@python module "requests" as req
let response = req.get("https://api.example.com")

# Import C library
@c module "libcurl" as curl
let data = curl.download("https://example.com")

# Import Rust library
@rust module "./crypto" as crypto
let hash = crypto.sha256("password")
```

## Standard Library

```sl
# File system
@python module "std/fs" as fs
fs.read("config.json")

# Crypto
@python module "std/crypto" as crypto
crypto.hash_sha256("data")

# HTTP
@python module "std/http" as http
http.get("https://api.example.com")
```

## Concurrency

```sl
# Spawn concurrent task
go background_task()

# Wait for completion
await background_task()
```

## Memory Management

```sl
# Automatic GC (default)
let x = [1, 2, 3]

# Reference counting
@rc
let y = [4, 5, 6]

# Manual memory
@manual
let ptr = alloc(1024)
free(ptr)
```