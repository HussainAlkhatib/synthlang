# SynthLang Phase 2: Go FFI and Scheduler

This document describes the Go-based FFI and Scheduler implementation for SynthLang.

## Overview

Phase 2 introduces a Go shared library (`libgoffi`) that provides:

1. **Foreign Function Interface (FFI)** - Low-latency calls to libraries in Python, Rust, C, Go, and JavaScript
2. **Scheduler** - Goroutine-based task management for `go` and `await` primitives

## Architecture

### Go Package Structure

```
src/go/
├── ffi.go          # FFI implementation with C exports
├── scheduler.go    # Goroutine scheduler implementation
├── ffi_test.go     # FFI unit tests
├── scheduler_test.go # Scheduler unit tests
├── build.go        # Build script for cross-platform compilation
├── go.mod          # Go module definition
├── Makefile        # Build automation
└── libgoffi.h      # Generated C header (after build)
```

### FFI Module Loading

The FFI supports loading modules from multiple languages:

| Language    | Function              | Returns |
|-------------|----------------------|---------|
| Python      | `LoadPythonModule`    | Module ID |
| Rust        | `LoadRustModule`      | Module ID |
| C           | `LoadCModule`         | Module ID |
| Go          | `LoadGoModule`        | Module ID |
| JavaScript  | `LoadJavaScriptModule`| Module ID |

All load functions follow the signature:
```c
ulonglong LoadXxxModule(char* name, char* path);
```

### FFI Function Calling

```c
char* CallFunction(char* module, char* function, char* args);
```

- Returns JSON-encoded response with `status` and `result` fields
- Args should be JSON-encoded array

### Scheduler Functions

| Function    | Description |
|-------------|-------------|
| `SpawnTask` | Creates a new task in a goroutine |
| `AwaitTask` | Waits for task completion, returns JSON result |
| `YieldTask` | Cooperative yield (no-op in Go) |

### Task States

- `pending` - Task created but not yet started
- `running` - Task is executing
- `completed` - Task finished successfully
- `failed` - Task finished with error

## Building

### Requirements

- Go 1.21+ installed
- CGO enabled

### Build Commands

```bash
# Build shared library
cd src/go
go build -buildmode=c-shared -o libgoffi.so .

# On Windows
go build -buildmode=c-shared -o libgoffi.dll .

# On macOS
go build -buildmode=c-shared -o libgoffi.dylib .
```

Or use the Makefile:
```bash
make build
make install
```

## Python Integration

The Go library is loaded in `cli.py` and `ffi.py`:

```python
# In cli.py
if GO_AVAILABLE:
    go_ffi.LoadPythonModule(b"module_name", b"/path/to/module")
    task_id = go_ffi.SpawnTask(b"func", b'[]')

# In ffi.py
from .ffi import go_spawn_task, go_await_task
```

## Performance Targets

- FFI call overhead: ≤ 1 microsecond
- Concurrent tasks: 10,000+
- Throughput: > 100,000 calls/second

## Next Steps (Phase 3+)

- Full Python C API integration for actual FFI calls
- JavaScript/V8 integration via v8go
- JNI integration for Java
- CGo for direct C library loading