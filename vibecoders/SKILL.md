# SynthLang VibeCoders Skill Guide

**Version:** 1.0.0  
**Author:** Hussain Alkhatib  
**License:** MIT

---

## Section 1: Introduction

### What is SynthLang?

SynthLang (pronounced "sin-th-lang") is a revolutionary polyglot programming language designed with a singular vision: to unify the world's programming languages into one coherent, expressive system. Created by Hussain Alkhatib, SynthLang offers developers three distinct layers of control:

1. **Beginner Layer** - Automatic garbage collection with simplified syntax
2. **Intermediate Layer** - Reference counting and FFI imports for experienced developers  
3. **Expert Layer** - Manual memory management and inline assembly for systems programmers

### The Philosophy

SynthLang's core philosophy centers on three principles:

1. **Ease** - Writing code should be as natural as thinking
2. **Power** - No language should be outside your reach
3. **Control** - You should always know what's happening under the hood

This creates a language that scales with your expertise, growing from simple scripting to complex systems programming without requiring a rewrite or language switch.

### Who Created It?

SynthLang was created by Hussain Alkhatib in 2024. The language represents years of experience working across multiple programming ecosystems and the recognition that developers shouldn't need to master dozens of languages to be effective.

### Why Was It Created?

Modern development requires fluency in Python for data science, JavaScript for web, Rust for systems, Go for concurrency, and countless other languages for specialized tasks. SynthLang eliminates this fragmentation by providing:

- A universal syntax that works everywhere
- Native FFI to any language
- Inline code execution without context switching
- Performance without sacrificing readability

---

## Section 2: Language Overview

### Syntax Basics

SynthLang uses indentation-based syntax similar to Python but with cleaner semantics. Every file should have a `main` function or top-level statements.

```sl
# Basic structure
fn main():
    print("Hello, SynthLang!")
```

### Variables and Data Types

Variables are declared with `let` (immutable) or `var` (mutable):

```sl
let x: int = 42      # Immutable integer
var y: str = "hello" # Mutable string
let z = 3.14         # Type inference
```

Supported types:
- `int` - 64-bit integers
- `float` - 64-bit floating point
- `str` - Unicode strings
- `bool` - Boolean values
- `list` - Ordered collections
- `dict` - Key-value mappings
- `null` - Null/missing value

### Functions

Functions are declared with `fn`:

```sl
fn add(a: int, b: int): int
    return a + b

fn greet(name: str): str
    return f"Hello, {name}!"
```

### Control Flow

#### If/Elif/Else

```sl
if x > 10:
    print("Greater than 10")
elif x > 5:
    print("Between 6 and 10")
else:
    print("5 or less")
```

#### For Loops

```sl
for item in [1, 2, 3]:
    print(item)

for i in 0..10:
    print(i)
```

#### While Loops

```sl
while x < 100:
    x = x * 2
```

### Pattern Matching (match statement)

The `match` statement provides powerful pattern matching:

```sl
match value:
    case 1:
        print("One")
    case 2, 3:
        print("Two or Three")
    case _:
        print("Other")
```

Multiple patterns in a single case are supported, with `_` as a wildcard.

### Deferred Execution (defer statement)

The `defer` statement schedules execution on function exit:

```sl
fn process_file():
    defer close_file()
    defer print("Cleanup done")
    open_file("data.txt")
    # Operations...
    # Cleanup happens automatically on return
```

### Error Handling (try/handle)

SynthLang uses `try/handle` for error handling:

```sl
try risky_operation():
    handle error:
        print("Failed:", error)
```

The built-in `panic` function throws exceptions:

```sl
fn validate(x: int):
    if x < 0:
        panic("Value must be positive")
```

---

## Section 3: The Three-Layer Philosophy

### Beginner Layer (GC - Automatic Memory Management)

Default mode for new developers:

```sl
@default  # Default annotation, GC enabled
fn process_data():
    let items = [1, 2, 3]
    # Items automatically cleaned up when out of scope
```

### Intermediate Layer (RC - Reference Counting)

For developers who want more control:

```sl
@rc
fn process_with_rc():
    let items: RcList = [1, 2, 3]
    # Reference counted - cleaned up immediately
```

### Expert Layer (Manual Memory Management)

For systems programming:

```sl
@manual
fn kernel_module():
    let ptr = alloc(1024)
    # Custom memory management
    free(ptr)
```

---

## Section 4: The Universal FFI

### Importing Libraries from Any Language

SynthLang's FFI allows importing libraries from 20+ languages:

```sl
@python module "requests" as req
@javascript module "axios" as axios
@rust module "./crypto" as crypto
@c module "libcurl" as curl
@go module "gql" as graphql
@cpp module "./fs" as fs
@r module "ggplot2" as ggplot
@ruby module "json" as json
@java module "java.util" as util
@swift module "Foundation" as foundation
@kotlin module "./app" as app
@php module "./api" as api
@lua module "./game" as game
@julia module "Plots" as plots
@haskell module "./logic" as logic
@elixir module "./web" as web
@dart module "./mobile" as mobile
@zig module "./kernel" as kernel
@typescript module "./utils" as utils
@csharp module "./system" as system
```

### Selective Imports

Import only specific functions:

```sl
@python module "os" import getenv, path, environ
let home = getenv("HOME")
```

### Inline Imports

Use code directly without separate files:

```sl
<py>
import json
result = json.dumps({"key": "value"})
</py>
```

---

## Section 5: Inline Language Tags

### Syntax

Inline code blocks use XML-style tags:

```sl
<py>
print("Python code here")
</py>

<r>
x <- c(1, 2, 3)
print(x)
</r>

<rust>
fn main() {
    println!("Rust code here");
}
</rust>
```

### Supported Languages

All 20 languages are supported inline:

| Tag | Language |
|-----|----------|
| `<py>` | Python |
| `<r>` | R |
| `<rust>` | Rust |
| `<go>` | Go |
| `<cpp>` | C++ |
| `<c>` | C |
| `<js>` | JavaScript |
| `<ts>` | TypeScript |
| `<kotlin>` | Kotlin |
| `<swift>` | Swift |
| `<php>` | PHP |
| `<ruby>` | Ruby |
| `<java>` | Java |
| `<csharp>` | C# |
| `<lua>` | Lua |
| `<julia>` | Julia |
| `<haskell>` | Haskell |
| `<elixir>` | Elixir |
| `<dart>` | Dart |
| `<zig>` | Zig |

### Variable Passing

Variables are automatically passed to inline code:

```sl
let x = 10
let y = 20

<py>
result = x + y  # Uses SynthLang variables
print(result)
</py>

let sum = result  # Returns result to SynthLang
```

### Capturing Results

Inline code results are accessible in the parent scope:

```sl
let data = <py>
import json
return json.dumps({"computed": 42})
</py>
```

---

## Section 6: Standard Library

### File System (std/fs.sl)

```sl
@python module "std/fs" as fs

fn read_config():
    return fs.read("config.json")

fn write_log(msg):
    fs.write("app.log", msg)
```

Functions:
- `fs.read(path)` - Read file contents
- `fs.write(path, content)` - Write to file
- `fs.exists(path)` - Check existence
- `fs.is_file(path)` - Check if file
- `fs.is_dir(path)` - Check if directory
- `fs.list_dir(path)` - List directory contents
- `fs.join_path(a, b)` - Join path components
- `fs.get_parent(path)` - Get parent directory
- `fs.get_name(path)` - Get filename

### Cryptography (std/crypto.sl)

```sl
@rust module "std/crypto" as crypto

fn hash_password(pw: str):
    return crypto.hash_sha256(pw)
```

Functions:
- `crypto.hash_sha256(data)` - SHA-256 hash
- `crypto.hash_sha512(data)` - SHA-512 hash
- `crypto.random_bytes(len)` - Random bytes
- `crypto.constant_time_compare(a, b)` - Secure comparison

### HTTP Client (std/http.sl)

```sl
@python module "std/http" as http

fn fetch_data(url: str):
    return http.get(url)
```

Functions:
- `http.get(url)` - HTTP GET
- `http.post(url, data)` - HTTP POST
- `http.put(url, data)` - HTTP PUT
- `http.delete(url)` - HTTP DELETE

### Image Processing (std/image.sl)

```sl
@c module "std/image" as img

fn process_image(path: str):
    return img.load(path)
```

Functions:
- `img.load(path)` - Load image
- `img.resize(path, width, height)` - Resize
- `img.rotate(path, degrees)` - Rotate
- `img.crop(path, x, y, w, h)` - Crop
- `img.save(path, image)` - Save image

### Environment (std/env.sl)

```sl
@python module "std/env" as env

fn run_command(cmd: str):
    return env.exec(cmd)
```

Functions:
- `env.get(name)` - Get environment variable
- `env.set(name, value)` - Set environment variable
- `env.exec(cmd)` - Execute shell command
- `env.args()` - Get command line arguments

### Process Management (std/process.sl)

```sl
@python module "std/process" as proc

fn spawn_worker():
    go worker()
```

Functions:
- `proc.spawn(fn, args)` - Spawn process
- `proc.wait(pid)` - Wait for process
- `proc.kill(pid)` - Kill process
- `proc.exit(code)` - Exit program

### Discord Bot (std/discord.sl)

```sl
@python module "std/discord" as discord

fn main():
    discord.run("TOKEN", on_message)
```

Functions:
- `discord.run(token, handler)` - Run bot
- `discord.send(channel, msg)` - Send message
- `discord.get_token()` - Get bot token

### Network (std/network.sl)

```sl
@python module "std/network" as net

fn fetch(url: str):
    return net.http_get(url)
```

Functions:
- `net.http_get(url)` - HTTP GET
- `net.http_post(url, data)` - HTTP POST
- `net.tcp_connect(host, port)` - TCP connect
- `net.udp_send(host, port, data)` - UDP send

---

## Section 7: CLI Commands

```bash
slang file.sl             # Run a file
slang run file.sl         # Same as above
slang init myproject       # Initialize new project
slang build --release      # Build executable
slang test                 # Run tests
slang fmt                  # Format code
slang repl                 # Interactive REPL
slang pip install pkg      # Install PyPI package
slang npm install pkg      # Install npm package
slang --debug file.sl      # Debug mode
```

### Backend Flags

```bash
slang script.sl --rust --go      # Rust Core + Go FFI
slang script.sl --python --pyffi # Python Core + Python FFI
slang script.sl --rust --pyffi   # Rust Core + Python FFI
```

---

## Section 8: Backends

### Python Core

Original implementation, uses Python for:
- Lexer
- Parser
- Compiler
- VM

Best for: Development, debugging, rapid iteration

### Rust Core

High-performance implementation:
- Native lexer
- Native parser
- Native compiler
- Native VM with manual memory management

Best for: Production, performance-critical applications

### Go FFI

Concurrent FFI scheduler for:
- Parallel FFI calls
- Thread management
- Task spawning

Best for: High-concurrency applications

---

## Section 9: Advanced Topics

### Writing FFI Bindings

To create an FFI binding for a new language:

```sl
# In ffi.py
def load_mylang_module(self, path: str):
    # Implementation
    pass

def call_mylang(self, module: str, func: str, args: list):
    # Implementation
    pass
```

### Extending the Language

Add custom AST nodes:

```rust
// In token.rs
pub enum TokenType {
    MY_CUSTOM,
}

// In parser.rs
fn parse_my_custom(&mut self) -> Option<ASTNode> {
    // Implementation
}
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Submit pull request

---

## Section 10: Examples

### Discord Bot

```sl
@python module "std/discord" as discord

fn on_message(content, author):
    if content == "!hello":
        return f"Hello, {author}!"
    return ""

fn main():
    discord.run(discord.get_token(), on_message)
```

### CLI Tool

```sl
@python module "std/fs" as fs
@python module "std/process" as proc

fn main():
    let args = proc.args()
    match args[0]:
        case "init":
            print("Initializing...")
        case "build":
            print("Building...")
        case _:
            print("Unknown command")
```

### Web Server

```sl
@python module "std/http" as http

fn handle_request(req):
    return {"status": 200, "body": "Hello from SynthLang!"}

fn main():
    http.listen(8080, handle_request)
```

### Data Analysis Script

```sl
<r>
library(ggplot2)
data <- data.frame(x = 1:10, y = 1:10)
plot <- ggplot(data, aes(x, y)) + geom_point()
print(plot)
</r>
```

### Machine Learning

```sl
<py>
import numpy as np
from sklearn.linear_model import LinearRegression

X = np.array([[1], [2], [3]])
y = np.array([2, 4, 6])
model = LinearRegression().fit(X, y)
return model.predict([[4]])[0]
</py>

let prediction = result
print("Prediction:", prediction)
```

### Game with Rust/C++

```sl
<cpp>
#include <iostream>
int main() {
    std::cout << "Game engine running!" << std::endl;
    return 0;
}
</cpp>
```

---

## Section 11: FAQ

**Q: What languages are supported?**  
A: Python, JavaScript, TypeScript, Rust, Go, C, C++, Java, C#, Kotlin, Swift, PHP, Ruby, R, Lua, Julia, Haskell, Elixir, Dart, and Zig.

**Q: How do I install SynthLang?**  
A: Run `pip install synthlang` or use the install script at synthlang.com/install.sh

**Q: Can I mix languages in one file?**  
A: Yes! Use inline code tags to combine multiple languages.

**Q: What's the performance compared to native languages?**  
A: Rust Core provides near-native performance. Python Core is suitable for development.

---

## Section 12: Troubleshooting

**Error: Module not found**  
Solution: Use `slang pip install module_name` or check the import path.

**Error: Compiler not found**  
Solution: Install the required compiler (rustc, g++, node, etc.)

**Error: Syntax error**  
Solution: Check indentation and token placement.

---

## Section 13: Changelog

**v1.0.0** - Final release
- Added inline language tags for all 20 languages
- Implemented match/defer/try statements
- Complete FFI for all supported languages
- C++ file system module
- Rust crypto module

---

## Section 14: License

MIT License - See LICENSE file for details.

---

*End of VibeCoders Skill Guide*