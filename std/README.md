# SynthLang Standard Library

The `std/` directory contains SynthLang modules that wrap native libraries for easy import.

## Available Modules

| Module | Description | FFI Target |
|--------|-------------|----------|
| `discord.sl` | Discord bot framework wrapper | Python `discord.py` |
| `fs.sl` | File system operations | C++ native (via `@cpp`) |
| `http.sl` | HTTP client for APIs | Python `requests` |
| `crypto.sl` | Cryptographic functions | Rust native (via `@rust`) |
| `image.sl` | Image processing | C native (via `@c`) |
| `process.sl` | Process management | Python `subprocess` |
| `network.sl` | Socket programming | Python `socket` |
| `env.sl` | Environment variables | Python `os` |
| `io.sl` | Input/output utilities | Python `builtins`, `json` |

## Usage

Import SynthLang standard library modules using the unified FFI syntax:

```sl
@python module "std/discord" as discord
@cpp module "std/fs" as fs
@rust module "std/crypto" as crypto
@python module "std/http" as http
```

### File System (fs.sl)

```sl
let content = fs.read("data.txt")
fs.write("output.txt", "Hello World")
let data = fs.read_json("config.json")
fs.write_json("config.json", {"key": "value"})
if fs.exists("file.txt"):
    print("File exists!")
```

### HTTP Client (http.sl)

```sl
let response = http.http_get("https://api.example.com/users")
let post_data = http.http_post("https://api.example.com/data", {"name": "Alice"})
```

### Cryptography (crypto.sl)

```sl
let hash = crypto.hash_sha256("password")
let token = crypto.generate_token(32)
let roll = crypto.random_int(1, 100)
```

### Environment (env.sl)

```sl
let token = env.getenv("DISCORD_TOKEN")
env.setenv("MY_VAR", "value")
```

### Process Management (process.sl)

```sl
let pid = process.spawn(["ls", "-la"])
let result = process.run("echo hello")
```

### Network (network.sl)

```sl
let sock = network.create_socket("inet", "stream")
sock.connect(("example.com", 80))
```

### Discord Bot (discord.sl)

```sl
fn process_message(content, author):
    if content == "!ping":
        return "Pong!"
    return ""

fn main():
    let token = discord.get_token()
    discord.run(token, process_message)
```