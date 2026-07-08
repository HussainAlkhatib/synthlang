# SynthLang Fixes Log

## Fixed Issues (v1.1.1)

### 1. Compiler/VM: Critical if/else JUMP control flow (C1)
- **File**: `src/synthlang/compiler.py`, `src/synthlang/vm.py`, `src/synthlang/ir.py`
- **Issue**: `else` in `if`/`elif` did not generate JUMP instructions, causing both branches to execute
- **Fix**: Implemented proper label placement with pre-generated labels. Added LABEL instruction support. VM builds label map and jumps correctly.

### 2. VM: Logical operators (&& and ||) now supported (C2)
- **File**: `src/synthlang/vm.py`
- **Issue**: Binary operations for `&&` and `||` were not implemented in the VM
- **Fix**: Added support for `&&` (and) and `||` (or) binary operations

### 3. VM: Stack traces on runtime errors (E3 - Critical)
- **File**: `src/synthlang/vm.py`
- **Issue**: VM errors had no stack traces
- **Fix**: Added `call_stack` tracking and `_format_stack_trace()` method. All runtime errors now include stack trace.

### 4. Lexer: Enhanced error details (E1)
- **File**: `src/synthlang/lexer.py`
- **Issue**: Lexer errors lacked column numbers and context
- **Fix**: Created `LexerError` class with line, column, char, and context. Added `_get_line_context()` for source snippets.

### 5. Parser: Expected vs Found errors (E2)
- **File**: `src/synthlang/parser.py`
- **Issue**: Parser errors lacked "expected vs found" details
- **Fix**: Created `ParseError` class with expected/found context and line snippets.

### 6. CLI: Debug flag for verbose execution (E4)
- **File**: `src/synthlang/cli.py`
- **Issue**: No debug mode existed
- **Fix**: Added `--debug` flag that prints IR instructions and stack state during execution.

### 7. CLI: slang version update fixed (M1)
- **File**: `src/synthlang/cli.py`
- **Issue**: Version update did not extract/copy files properly
- **Fix**: Added zip extraction, executable copying with proper OS-specific paths, and chmod on Unix.

### 8. FFI: Callbacks and FFIError (M4)
- **File**: `src/synthlang/ffi.py`
- **Issue**: Cannot pass SynthLang functions as Python callbacks
- **Fix**: Added `SynthLangFunction` wrapper class for callback support. Created `FFIError` for detailed FFI error messages.

### 9. FFI: AWAIT instruction added (F1)
- **File**: `src/synthlang/ir.py`
- **Issue**: No AWAIT IR type for async support
- **Fix**: Added `IRType.AWAIT` and `await_op()` function. Partial async support implemented.

### 10. Annotations: Registry support (F2)
- **File**: `src/synthlang/compiler.py`, `src/synthlang/ir.py`
- **Issue**: @web, @cli, @desktop annotations did nothing
- **Fix**: Added `IRModule.annotation_registry` and compiler handler for @web and @cli annotations.

## Test Results

- All tests passing: **279 passed**
- Control flow tests: 7 passed (including if/else/elif)
- VM tests: 27 passed (including logical operators)

## Added Examples

- `projects/discord1/discord1.sl` - Discord bot demo with FFI
- `projects/discord1/run_bot.py` - Full Discord bot implementation
- `projects/go_integration/go_ffi.sl` - Go FFI integration example
- `projects/rust_integration/rust_ffi.sl` - Rust FFI integration example