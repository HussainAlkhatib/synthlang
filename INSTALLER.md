# SynthLang Installer Documentation

## Overview

The SynthLang installer (`set-slang.exe`) provides a one-click installation experience for Windows users, with optional silent mode for automated deployments.

## Installation

### GUI Mode (Default)

Double-click `set-slang.exe` and follow the wizard:

1. Accept the license agreement
2. Choose installation path (default: `C:\slang`)
3. Select options:
   - Add to PATH (enabled by default)
   - Install VS Code extension (optional)
4. Click Install

### Silent Mode

For automated installations, use command-line arguments:

```cmd
set-slang.exe /S /installpath="D:\MySlang" /addpath=yes /vscode=yes
```

#### Silent Mode Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `/S` | - | - | Run in silent mode (no UI) |
| `/installpath=` | Path | `C:\slang` | Installation directory |
| `/addpath=` | `yes`/`no` | `yes` | Add bin directory to PATH |
| `/vscode=` | `yes`/`no` | `yes` | Include VS Code extension |

## After Installation

### Installed Location

```
C:\slang\
├── bin\
│   └── slang.exe        # Main CLI executable
├── lib\
│   ├── core\            # Core Python modules
│   ├── stdlib\          # Standard library
│   └── slangs\          # Global dependency cache
│       ├── python\      # pip packages
│       └── node\        # npm packages
├── docs\                # Documentation
├── examples\            # Sample programs
├── tools\               # Additional tools
└── version.txt          # Installed version
```

### Using Global Dependencies

Install packages globally with `--global` flag:

```bash
slang pip install --global requests
slang npm install --global lodash
```

Global packages are stored in `C:\slang\lib\slangs\` and are available to all projects.

## Uninstallation

### GUI Uninstall

1. Open Add/Remove Programs
2. Find "SynthLang"
3. Click "Uninstall"

### Silent Uninstall

```cmd
C:\slang\uninstall.exe /S
```

## Cross-Platform Installation

### Linux/macOS

```bash
# Using pip (recommended)
pip install synthlang

# Or download binary
curl -L https://github.com/synthlang/synthlang/releases/latest/download/slang-linux-x86_64 -o slang
chmod +x slang
sudo mv slang /usr/local/bin/
```

## Update System

Check for updates:

```bash
slang version check
```

Update to latest version:

```bash
slang version update
```

Updates are stored in `C:\slang\.backup\` for rollback capability.