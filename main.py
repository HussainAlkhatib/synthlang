#!/usr/bin/env python3
"""SynthLang main entry point for PyInstaller builds."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from synthlang.cli import main

if __name__ == '__main__':
    main()