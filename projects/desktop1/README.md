# Desktop Application Stub

A simple desktop application demonstration for SynthLang. (v1.1.0)

## Description

This project demonstrates that SynthLang can be used for desktop apps via FFI to GUI libraries like Qt or Tkinter, or using the `@desktop` annotation.

## How to Run

```bash
slang run desktop1/desktop1.sl
```

## Extension Notes

To turn this stub into a full desktop application:

1. **Option A - FFI Integration**:
   - Use `@c` annotation to call platform-native GUI APIs
   - Example: `@c fn create_window(title: str, width: int, height: int): int`

2. **Option B - Tkinter via Python**:
   - Use `@python` annotation to import tkinter
   - Example: `@python module "tkinter_gui.py" as gui`

3. **Option C - Qt via Rust**:
   - Use `@rust` annotation for a Rust Qt backend
   - Example: `@rust module "qt_gui.rs" as gui`

## Features to Add

- Window creation and management
- Button click handlers
- Text input fields
- Menu systems
- Native file dialogs