#!/usr/bin/env python3
"""SynthLang main - Backward compatible entry point."""
import sys
import os
from pathlib import Path
from .cli import run_file

__version__ = "1.0.0"

def run(filepath: str) -> dict:
    return run_file(filepath)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        result = run(sys.argv[1])
        if result:
            for k, v in result.items():
                print(f"{k} = {v}")