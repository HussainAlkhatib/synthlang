# SynthLang Syntax Highlighting & File Icons

This directory contains syntax highlighting definitions and icons for all major code editors. The installer automatically copies these to the appropriate locations.

## Structure

```
colors/
├── vscode/           # Visual Studio Code extension
│   ├── package.json
│   ├── synthlang.png  # 128x128 icon
│   ├── syntaxes/
│   │   └── synthlang.tmLanguage.json
│   └── language-configuration.json
├── antigravity/      # Antigravity IDE extension (VS Code fork)
│   ├── package.json
│   ├── synthlang.png  # 128x128 icon
│   ├── syntaxes/
│   │   └── synthlang.tmLanguage.json
│   └── language-configuration.json
├── sublime/          # Sublime Text
│   └── synthlang.sublime-syntax
├── vim/              # Vim
│   ├── syntax/
│   │   └── synthlang.vim
│   └── ftdetect/
│       └── synthlang.vim
├── neovim/           # Neovim
│   ├── syntax/
│   │   └── synthlang.vim
│   └── ftdetect/
│       └── synthlang.vim
├── emacs/            # Emacs
│   └── synthlang-mode.el
├── jetbrains/        # JetBrains IDEs (IntelliJ, PyCharm, etc.)
│   └── filetypes.xml
├── notepadpp/        # Notepad++
│   └── synthlang.xml
├── synthlang.xml     # MIME type definition (Linux)
└── synthlang.desktop # Desktop entry (Linux)
```

## Icon Registration

### Windows (set-slang.exe)
The installer automatically:
- Registers `.sl` file extension in Windows Registry
- Sets the SynthLang icon for `.sl` files
- Associates `.sl` files with `slang.exe`

### Linux
After installation, run:
```bash
xdg-icon-resource install --size 128 assets/icon.png application-x-synthlang
xdg-mime install colors/synthlang.xml
```

### macOS
Icons are automatically associated with the app bundle.

## Supported Language Elements

- Keywords: `let`, `var`, `fn`, `if`, `elif`, `else`, `for`, `while`, `return`, `go`, `await`, `match`, `defer`, `try`, `handle`, `panic`, `in`, `as`, `module`
- Types: `int`, `float`, `str`, `string`, `bool`, `void`, `list`, `dict`, `object`
- FFI Imports: `@python module "x" as y`, `@python module "x" import a, b, c`
- Comments: `# line comment`, `// line comment`, `/* block comment */`
- Strings: `"double"`, `'single'`
- Numbers: integers and floats
- Booleans: `true`, `false`