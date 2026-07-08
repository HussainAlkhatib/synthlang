# Foreign Function Interface (FFI) Guide

SynthLang's Universal FFI allows you to import and use libraries from Python, JavaScript, Rust, C, Go, and Java seamlessly.

## Import Syntax

### Module Import

Import an entire module:

```sl
@python module "json" as json
let data = json.loads(text)
```

### Selective Import

Import specific functions or classes:

```sl
@python module "os" import getenv, path, environ

@javascript module "fs" import readFile, writeFile, exists

@rust module "math_utils" import factorial, fibonacci
```

### Inline Import

For one-off usage:

```sl
let response = @python module "requests" import get
```

## Supported Languages

| Language | Syntax | Example |
|----------|--------|---------|
| **Python** | `@python module "pkg"` | `@python module "requests" as http` |
| **JavaScript** | `@javascript module "pkg"` | `@javascript module "axios" as axios` |
| **Rust** | `@rust module "./path"` | `@rust module "./crypto" as crypto` |
| **C** | `@c module "libname"` | `@c module "libcurl" as curl` |
| **Go** | `@go module "pkg"` | `@go module "processor" as proc` |
| **Java** | `@java module "pkg"` | `@java module "org.apache.commons" as commons` |

## Usage Examples

### Python FFI

```sl
@python module "discord.py" as discord

fn create_bot(token: string): void
    intents = discord.Intents.default()
    intents.message_content = true
    client = discord.Client(intents=intents)
    client.run(token)
```

### JavaScript FFI

```sl
@javascript module "axios" import get

fn fetch_data(url: string): dict
    response = get(url)
    return response.data
```

### Passing SynthLang Functions as Callbacks

```sl
@python module "event_system" as events

fn my_handler(data: dict): void
    print("Received:", data)

# Pass SynthLang function to Python
events.on("event", my_handler)
```

## Package Management

Install packages to the global cache:

```bash
slang pip install requests
slang npm install lodash
slang cargo install my_rust_lib
```

The packages are installed to:
- **Windows**: `C:\slang\lib\slangs\python\` or `C:\slang\lib\slangs\node\`
- **Unix**: `~/.slang/slangs/python/` or `~/.slang/slangs/node/`

## Error Handling

FFI errors include full context:

```
FFIError: Python module 'discord.py' not found
  Language: python
  Module: discord.py
  Suggestion: Run 'slang pip install discord.py'
```

## Memory Management with FFI

Use `@rc` for reference-counted FFI objects:

```sl
@rc
@python module "numpy" as np

fn process_array(): void
    arr = np.array([1, 2, 3])
    # Reference counting manages cleanup
```

Use `@manual` for explicit control:

```sl
@manual
@rust module "custom_alloc" as mem

fn main(): void
    alloc buffer
    # ... use buffer ...
    free buffer
```

## Async Support

For async libraries like `discord.py`, SynthLang automatically handles event loops:

```sl
@python module "discord_client" as client

fn main(): void
    client.run(token)  # Handles async internally
```

The FFI detects coroutine functions and wraps them appropriately.