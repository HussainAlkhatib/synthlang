#!/usr/bin/env python3
"""Cross-platform installer for SynthLang."""
import os
import sys
import shutil
import subprocess
import platform

def get_install_path():
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ.get('ProgramFiles', 'C:\\'), 'SynthLang')
    elif system in ('Linux', 'Darwin'):
        return '/usr/local/bin/slang'
    return None

def install_windows():
    install_dir = os.path.join(os.environ.get('ProgramFiles', 'C:\\'), 'SynthLang')
    os.makedirs(install_dir, exist_ok=True)
    
    exe_path = os.path.join(os.path.dirname(__file__), '..', 'dist', 'slang.exe')
    if os.path.exists(exe_path):
        shutil.copy(exe_path, install_dir)
        print(f"Installed to {install_dir}")
    else:
        print("Build the executable first: python scripts/build_exe.py")

def install_unix():
    install_path = get_install_path()
    exe_path = os.path.join(os.path.dirname(__file__), '..', 'dist', 'slang')
    
    if os.path.exists(exe_path):
        shutil.copy(exe_path, install_path)
        os.chmod(install_path, 0o755)
        print(f"Installed to {install_path}")
    else:
        print("Build the executable first: python scripts/build_exe.py")

def verify():
    result = subprocess.run(['slang', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Verification successful: {result.stdout.strip()}")
    else:
        print("Verification failed. Check your PATH.")

def main():
    system = platform.system()
    if system == "Windows":
        install_windows()
    elif system in ('Linux', 'Darwin'):
        install_unix()
    verify()

if __name__ == '__main__':
    main()