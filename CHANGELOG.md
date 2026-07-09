# SynthLang v1.0.0 - Universal Polyglot Foundation Release

## Breaking Changes

- **FFI Import Syntax Standardized**: The canonical import syntax is `@python module "path" as alias` and `@python module "path" import func1, func2`
- **No more Python adapters**: All wrapper files have been removed. Use `@python module "std/discord"` for Discord bots.
- **Version aligned to 1.0.0**: All version numbers across all files now use 1.0.0.

## New Features

### Universal FFI Import Syntax
```sl
# Full module import with alias
@python module "discord.py" as discord

# Selective import
@python module "os" import getenv, path

# Standard library imports (same syntax!)
@python module "std/discord" as discord
@python module "std/fs" as fs
```

### Inline Language Tags (NEW)
Write code from 20 languages directly in your SynthLang files:

```sl
<py>
result = x + y
</py>

<r>
x <- c(1, 2, 3)
plot(x)
</r>

<rust>
println!("Hello from Rust!");
</rust>
```

Supported languages: Python, R, Rust, Go, C++, C, JavaScript, TypeScript, Kotlin, Swift, PHP, Ruby, Java, C#, Lua, Julia, Haskell, Elixir, Dart, Zig.

### Pattern Matching (NEW)
```sl
match value:
    case 1:
        print("One")
    case 2, 3:
        print("Two or Three")
    case _:
        print("Other")
```

### Deferred Execution (NEW)
```sl
fn process():
    defer cleanup()
    print("Processing...")
    # cleanup() runs automatically on return
```

### Error Handling (NEW)
```sl
try risky_operation():
    handle error:
        print("Failed:", error)
```

### SynthLang Standard Library (std/)
The `std/` directory contains SynthLang modules that wrap native libraries:

| Module | Functions | Native Backend |
|--------|-----------|--------------|
| `std/fs.sl` | `read()`, `write()`, `exists()`, `list_dir()` | C++ |
| `std/crypto.sl` | `hash_sha256()`, `hash_sha512()`, `random_bytes()` | Rust |
| `std/image.sl` | `load()`, `resize()`, `crop()` | C |
| `std/http.sl` | `http_get()`, `http_post()`, `http_put()`, `http_delete()` | Python |
| `std/env.sl` | `env_get()`, `env_set()` | Python |
| `std/process.sl` | `spawn()`, `run()`, `get_input()` | Python |
| `std/network.sl` | `create_socket()`, `bind()`, `listen()`, `accept()`, `connect()` | Python |
| `std/discord.sl` | `run()`, `get_token()` | Python |

### Language Support (20 Languages)
| Language | Status | Use Case |
|----------|--------|----------|
| **Python** | ✅ Full Support | Discord bots, data science, automation, AI |
| **Rust** | ✅ Full Support | Cryptography, system programming, performance |
| **Go** | ✅ Full Support | High-concurrency servers, CLI tools, microservices |
| **C** | ✅ Full Support | Low-level system access, image processing, hardware |
| **JavaScript** | ✅ Full Support | Web interfaces, APIs, frontend tooling |
| **TypeScript** | ✅ Full Support | Typed JavaScript development |
| **C++** | ✅ Full Support | High-performance systems, file I/O |
| **R** | ✅ Full Support | Statistics, data analysis, visualization |
| **Java** | ✅ Full Support | Enterprise applications, Android |
| **C#** | ✅ Full Support | .NET applications, Windows development |
| **Kotlin** | ✅ Full Support | Android, JVM development |
| **Swift** | ✅ Full Support | iOS/macOS development |
| **PHP** | ✅ Full Support | Web backend development |
| **Ruby** | ✅ Full Support | Scripting, web development |
| **Lua** | ✅ Full Support | Game scripting, embedded systems |
| **Julia** | ✅ Full Support | Scientific computing, machine learning |
| **Haskell** | ✅ Full Support | Functional programming, type safety |
| **Elixir** | ✅ Full Support | Concurrent web applications |
| **Dart** | ✅ Full Support | Mobile development, Flutter |
| **Zig** | ✅ Full Support | Systems programming, performance |

### Persistent Async Event Loop
The FFI includes a persistent background event loop that handles async operations transparently.

### Universal Syntax Highlighting
All major editors now support SynthLang syntax highlighting out-of-the-box.

### File Icons
`.sl` files now display custom icons in all file explorers.

## Installation

The installer now automatically:
1. Installs the `slang` binary
2. Creates the `colors/` directory with syntax definitions
3. Attempts to auto-install for detected editors

## Migration Guide

### Old v0.x Code
```sl
@python module "discord_adapter" as adapter
adapter.run_sync(token)
```

### New v1.0.0 Code
```sl
@python module "std/discord" as discord
discord.run(token, process_message)
```

### SynthLang Standard Library (std/)
The `std/` directory contains SynthLang modules that wrap native libraries:

| Module | Functions |
|--------|-----------|
| `std/discord.sl` | `run()`, `get_token()` |
| `std/fs.sl` | `read()`, `write()`, `read_json()`, `write_json()`, `exists()`, `delete()`, `list_dir()` |
| `std/crypto.sl` | `hash_sha256()`, `hash_md5()`, `random_int()`, `generate_token()` |
| `std/http.sl` | `http_get()`, `http_post()`, `http_put()`, `http_delete()` |
| `std/env.sl` | `env_get()`, `env_set()` |
| `std/process.sl` | `spawn()`, `run()`, `get_input()` |
| `std/network.sl` | `create_socket()`, `bind()`, `listen()`, `accept()`, `connect()` |

### Persistent Async Event Loop
The FFI includes a persistent background event loop that handles async operations transparently. Discord bots and other async libraries now work without wrapper code.

### Universal Syntax Highlighting
All major editors now support SynthLang syntax highlighting out-of-the-box:

- VS Code (extension included with icon)
- Antigravity IDE (VS Code fork, uses same extension)
- Vim/Neovim
- Sublime Text
- Emacs
- JetBrains IDEs (IntelliJ, PyCharm, etc.)
- Notepad++

### File Icons
`.sl` files now display custom icons in all file explorers:
- Windows File Explorer shows SynthLang icon
- Linux file managers (Nautilus, Dolphin, etc.) show themed icon
- VS Code file tree displays the SynthLang icon

## Installation

The installer now automatically:
1. Installs the `slang` binary
2. Creates the `colors/` directory with syntax definitions
3. Attempts to auto-install for detected editors
4. Falls back to manual installation instructions if auto-install fails

Colors are installed to `/usr/local/lib/slang/colors/` on Unix and `C:\slang\colors\` on Windows.

## Language Support (Phase 1)

| Language | Status | Use Case |
|----------|--------|----------|
| **Python** | ✅ Full Support | Discord bots, data science, automation, AI |
| **Rust** | ✅ Full Support | Cryptography, system programming, performance |
| **Go** | ✅ Full Support | High-concurrency servers, CLI tools, microservices |
| **C** | ✅ Full Support | Low-level system access, image processing, hardware |
| **JavaScript** | ✅ Full Support | Web interfaces, APIs, frontend tooling |

## Migration Guide

### Old v0.x Code
```sl
@python module "discord_adapter" as adapter
adapter.run_sync(token)
```

### New v1.0.0 Code
```sl
@python module "std/discord" as discord
discord.run(token, process_message)
```