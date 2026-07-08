#!/usr/bin/env python3
"""Build standalone executables with PyInstaller."""
import os
import sys
import subprocess
import platform
import shutil

def build():
    import PyInstaller.__main__
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    entry_script = os.path.join(base_dir, 'slang_cli.py')
    
    # Clean dist directory
    dist_dir = os.path.join(project_root, 'dist')
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    PyInstaller.__main__.run([
        entry_script,
        '--onefile',
        '--name=slang',
        '--distpath', dist_dir,
        '--hidden-import=synthlang',
        '--hidden-import=synthlang.lexer',
        '--hidden-import=synthlang.parser',
        '--hidden-import=synthlang.compiler',
        '--hidden-import=synthlang.vm',
        '--hidden-import=synthlang.ir',
        '--hidden-import=synthlang.gc',
        '--hidden-import=synthlang.scheduler',
        '--hidden-import=synthlang.ffi',
    ])
    
    system = platform.system()
    exe_name = 'slang.exe' if system == 'Windows' else 'slang'
    print(f"Build complete: {dist_dir}/{exe_name}")

if __name__ == '__main__':
    build()