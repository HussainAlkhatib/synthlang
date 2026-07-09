# SynthLang

![SynthLang Icon](assets/icon.svg)

**SynthLang v1.0.0** - The zero-bridge polyglot programming language with universal syntax highlighting.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green)]()
[![Build Status](https://github.com/synthlang/synthlang/workflows/CI/badge.svg)](https://github.com/synthlang/synthlang/actions)

## The Three-Layer Philosophy

SynthLang gives you **three levels of control** in a single language:

| Layer | For | Memory | Concurrency |
|-------|-----|--------|-------------|
| **Beginner** | New developers | Automatic GC | Abstracted FFI |
| **Intermediate** | Experienced devs | RC option | `go`/`await` |
| **Expert** | Systems programmers | Manual mode | Full control |

## Quick Start (3 lines)

```sl
# hello.sl
fn main(): void
    print("Hello, SynthLang!")
```

```bash
slang hello.sl
```

## The Universal FFI

Import libraries from any language with a single syntax:

```sl
# Python
@python module "requests" as req
let data = req.get("https://api.example.com")

# JavaScript
@javascript module "axios" as axios

# Rust
@rust module "./crypto" as crypto

# C
@c module "libcurl" as curl
```

Selective imports for specific functions:

```sl
@python module "os" import getenv, path, environ
```

### Standard Library

Import SynthLang's std modules using the same FFI syntax:

```sl
@python module "std/discord" as discord
@python module "std/fs" as fs
@python module "std/crypto" as crypto
```

## Discord Prison Bot - Live Example (v1.0.0)

```sl
# discord1.sl - Pure SynthLang, no adapters
@python module "std/discord" as discord
@python module "std/fs" as fs
@python module "std/crypto" as crypto

fn process_message(content, author):
    if content == "!prison":
        return "User sent to prison!"
    return ""

fn main():
    let token = discord.get_token()
    discord.run(token, process_message)
```

Run it: `slang discord1.sl`

## Universal Syntax Highlighting

SynthLang supports syntax highlighting in **all major editors** out-of-the-box:

- **VS Code** - Extension auto-installed
- **Vim/Neovim** - Syntax files copied to `~/.vim/` or `~/.config/nvim/`
- **Sublime Text** - Auto-installed to Packages/User
- **Emacs** - Syntax file installed to `~/.emacs.d/`
- **JetBrains IDEs** - XML definition provided
- **Notepad++** - UserDefineLanguage XML provided

Colors directory: `/usr/local/lib/slang/colors/` (Unix) or `C:\slang\colors\` (Windows)

## Installation

### Windows
```powershell
pip install synthlang
```

### macOS/Linux
```bash
curl -sSL https://synthlang.com/install.sh | bash
# or
pip install synthlang
```

## Features

- **Polyglot FFI**: Python, JavaScript, TypeScript, Rust, C, C++, Go, Java, C#, Kotlin, Swift, PHP, Ruby, R, Lua, Julia, Haskell, Elixir, Dart, Zig libraries
- **Inline Code Tags**: Write code from 20 languages directly inline with `<py>`, `<r>`, `<rust>`, etc.
- **Pattern Matching**: `match`/`case` statements for clean conditional logic
- **Deferred Execution**: `defer` statement for automatic cleanup
- **Error Handling**: `try`/`handle` for robust error management
- **Memory Management**: `@gc` (default), `@rc`, `@manual`
- **Concurrency**: `go` and `await` for lightweight threading
- **Clean Syntax**: Minimal boilerplate, maximum expressiveness
- **Cross-Platform**: Windows, Linux, macOS
- **Universal Colors**: Works in every editor immediately

## CLI Commands

```bash
slang file.sl             # Run a file (uses Rust Core + Go FFI by default)
slang run file.sl         # Same as above
slang init myproject      # Initialize new project
slang build --release     # Build executable
slang test                # Run tests
slang fmt                 # Format code
slang repl                # Interactive REPL
slang pip install pkg     # Install PyPI package
slang npm install pkg     # Install npm package
```

### Backend Flags

```bash
slang script.sl --rust --go      # Rust Core + Go FFI (default if available)
slang script.sl --python --pyffi  # Python Core + Python FFI (original behavior)
slang script.sl --rust --pyffi    # Rust Core + Python FFI
slang --debug script.sl           # Debug mode - show IR and stack traces
```

## Documentation

- [Syntax Guide](docs/syntax.md)
- [FFI Guide](docs/ffi.md)
- [Tutorial](docs/tutorial.md)
- [Design Notes](docs/design_notes.md)
- [Standard Library](std/README.md)

## GitHub

[![Star](https://img.shields.io/github/stars/synthlang/synthlang?style=social)](https://github.com/synthlang/synthlang)

[Star SynthLang on GitHub](https://github.com/synthlang/synthlang) to show your support!

## License

MIT License - See [LICENSE](LICENSE) for details.