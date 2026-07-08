"""SynthLang Packager - slang build, install, init commands."""
import os
import sys
import subprocess
import tempfile
import shutil
from typing import Optional
from pathlib import Path


def build_project(output_path: Optional[str] = None, release: bool = False):
    output = output_path or "slang"
    
    if release:
        print("Building release mode with optimizations...")
    else:
        print("Building debug mode...")
    
    src_dir = Path(__file__).parent
    root_dir = Path(__file__).parent.parent
    
    main_script = root_dir / "main.py"
    
    build_script = f'''import sys
sys.path.insert(0, "{root_dir}")
from synthlang.cli import main
main()
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(build_script)
        temp_main = f.name
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            f"--name={output}",
            "--distpath", str(root_dir / "dist"),
            temp_main
        ]
        
        if release:
            cmd.insert(4, "--noconfirm")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Build complete: dist/{output}")
            return True
        else:
            print(f"Build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Build error: {e}")
        return False
    finally:
        if os.path.exists(temp_main):
            os.unlink(temp_main)


def main():
    import argparse
    parser = argparse.ArgumentParser(prog='slang-build')
    parser.add_argument('--release', action='store_true')
    parser.add_argument('--output', '-o')
    
    args = parser.parse_args()
    build_project(args.output, args.release)


if __name__ == '__main__':
    main()