# Installation Guide

## Windows

### Prerequisites
- Python 3.10 or later
- pip (Python package manager)

### Install via pip
```powershell
pip install synthlang
```

### Verify Installation
```powershell
slang --version
# Should output: SynthLang v1.0.0
```

### Add to PATH (if needed)
If `slang` is not recognized, add to PATH:
```powershell
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Roaming\Python\Python312\Scripts"
```

## macOS

### Prerequisites
- Python 3.10 or later (via Homebrew recommended)

### Install via Homebrew (Recommended)
```bash
brew install python@3.12
pip3 install synthlang
```

### Install via pip
```bash
pip3 install synthlang
```

### Verify Installation
```bash
slang --version
```

## Linux

### Prerequisites
- Python 3.10 or later
- pip

### Install via pip
```bash
pip install synthlang
# or
pip3 install synthlang
```

### Install on Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install synthlang
```

### Install on Fedora/RHEL
```bash
sudo dnf install python3 python3-pip
pip3 install synthlang
```

## From Source

### Clone and Install
```bash
git clone https://github.com/synthlang/synthlang.git
cd synthlang
pip install -e .
```

### Build Standalone Executable
```bash
pip install pyinstaller
python scripts/build_exe.py
```

The executable will be in `dist/slang`.

## Offline Installation

Download pre-built executables from [GitHub Releases](https://github.com/synthlang/synthlang/releases) and extract to a directory in your PATH.

## Troubleshooting

### Command not found
Add the Scripts directory to your PATH or use `python -m synthlang` as an alternative.

### Import errors
Ensure you have Python 3.10+ and reinstall:
```bash
pip uninstall synthlang
pip install synthlang
```

### Permission denied
Use `--user` flag:
```bash
pip install --user synthlang
```