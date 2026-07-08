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