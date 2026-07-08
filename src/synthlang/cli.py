#!/usr/bin/env python3
"""SynthLang CLI - Main entry point with full subcommand support."""
import sys
import os
import argparse
import json
import time
import hashlib
import subprocess
import tempfile
import shutil
import platform
import zipfile
from pathlib import Path
from typing import Optional, Any
from urllib.request import urlopen
import urllib.error

# Try to import Rust core for performance
try:
    import synthlang_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    synthlang_core = None

from .lexer import Lexer
from .ir import IRModule
from .parser import Parser
from .compiler import Compiler
from .vm import VM
from .evaluator import evaluate
from .formatter import format_file, format_directory
from .tester import test_main
from .dependency import DependencyManager, init_project, init_manifest, get_slangs_cache_path
from .packager import build_project


def get_install_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        return Path(os.environ.get("PROGRAMFILES", "C:\\")) / "SynthLang"
    return Path.home() / ".slang"


def get_cache_path(filepath: str) -> Optional[Any]:
    source_hash = hashlib.md5(filepath.encode()).hexdigest()[:16]
    cache_dir = Path.home() / ".synthlang" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{source_hash}.slir"


def load_cached_ir(filepath: str) -> Optional[Any]:
    cache_path = get_cache_path(filepath)
    if cache_path and cache_path.exists():
        source_stat = os.stat(filepath)
        cache_stat = os.stat(cache_path)
        if cache_stat.st_mtime > source_stat.st_mtime:
            return cache_path
    return None


def save_cached_ir(filepath: str, ir: Any):
    cache_path = get_cache_path(filepath)
    if cache_path:
        with open(cache_path, 'w') as f:
            f.write(str(ir))


def _process_ffi_imports(vm: VM, ir: IRModule):
    for as_name, (language, module_path) in ir.imports.items():
        vm._handle_ffi_import(language, module_path, as_name)


def run_file(filepath: str, verbose: bool = False, use_cache: bool = True, debug: bool = False, use_python: bool = False) -> dict:
    if use_cache:
        cache = load_cached_ir(filepath)
        if cache:
            if verbose:
                print(f"Using cached IR from {cache}")
    
    with open(filepath, 'r') as f:
        source = f.read()
    
    if use_python or not RUST_AVAILABLE:
        if verbose:
            print(f"Compiling {filepath}...")
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens, source)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        
        if use_cache:
            save_cached_ir(filepath, ir)
        
        if verbose:
            print(f"Executing...")
        
        vm = VM(ir, debug=debug)
        _process_ffi_imports(vm, ir)
        return vm.run()
    else:
        if verbose:
            print(f"Executing with Rust backend...")
        result = synthlang_core.execute(source, debug)
        return dict(result)


def read_current_version() -> str:
    # First check the local version.txt
    version_file = Path(__file__).parent.parent / "version.txt"
    if version_file.exists():
        return version_file.read_text().strip()
    install_dir = get_install_dir()
    version_file = install_dir / "version.txt"
    if version_file.exists():
        return version_file.read_text().strip()
    return "1.0.0"


def get_latest_release_info() -> dict:
    try:
        with urlopen("https://api.github.com/repos/synthlang/synthlang/releases/latest", timeout=10) as response:
            data = json.loads(response.read().decode())
            return {
                "tag_name": data.get("tag_name", ""),
                "download_url": data.get("assets", [{}])[0].get("browser_download_url", ""),
                "checksum": ""
            }
    except Exception:
        return {"tag_name": "", "download_url": "", "checksum": ""}


def update_slang(download_url: str):
    if not download_url:
        print("No download URL available")
        return
    
    install_dir = get_install_dir()
    backup_dir = install_dir / ".backup"
    
    print("Downloading update...")
    tmp_path = os.path.join(tempfile.gettempdir(), "slang-update.zip")
    
    try:
        with urlopen(download_url, timeout=60) as response:
            with open(tmp_path, 'wb') as f:
                f.write(response.read())
        
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        if install_dir.exists():
            shutil.move(str(install_dir), str(backup_dir))
        
        install_dir.mkdir(parents=True, exist_ok=True)
        print("Installing update...")
        
        # Extract the archive
        extract_dir = os.path.join(tempfile.gettempdir(), "slang-extract")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(tmp_path, 'r') as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            print("Downloaded file is not a valid zip archive")
            raise
        
        # Find and copy the slang executable
        # Look for slang binary in the extracted directory
        for root, dirs, files in os.walk(extract_dir):
            for f in files:
                if f == 'slang' or f == 'slang.exe' or f.startswith('slang'):
                    src_file = Path(root) / f
                    if platform.system() == "Windows":
                        dest = install_dir / "bin" / f
                        dest.parent.mkdir(parents=True, exist_ok=True)
                    else:
                        dest = Path("/usr/local/bin") / f
                        dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest)
                    # Make executable on Unix
                    if platform.system() != "Windows":
                        os.chmod(dest, 0o755)
                    print(f"Installed {f} to {dest}")
                    break
        
        print("Update complete! Restart slang to use the new version.")
        
    except Exception as e:
        print(f"Update failed: {e}")
        # Restore from backup if available
        if backup_dir.exists():
            if install_dir.exists():
                shutil.rmtree(install_dir)
            shutil.move(str(backup_dir), str(install_dir))
            print("Restored from backup")
        elif backup_dir.exists():
            shutil.move(str(backup_dir), str(install_dir))
    finally:
        # Clean up temp files
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        extract_dir = os.path.join(tempfile.gettempdir(), "slang-extract")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)


def cmd_version(args):
    current = read_current_version()
    if args.subcommand == "check":
        print(f"SynthLang v{current}")
        info = get_latest_release_info()
        latest = info.get("tag_name", "").lstrip("v")
        if latest and latest != current:
            print(f"Update available: v{latest}")
        elif latest == current:
            print("You are running the latest version")
        else:
            print("Could not check for updates")
    elif args.subcommand == "update":
        print(f"SynthLang v{current}")
        info = get_latest_release_info()
        latest = info.get("tag_name", "").lstrip("v")
        if not latest:
            print("Could not fetch latest version")
            return
        if latest == current:
            print("Already running the latest version")
            return
        print(f"Updating to v{latest}...")
        download_url = info.get("download_url", "")
        if download_url:
            update_slang(download_url)
            # Update the version file after successful download
            install_dir = get_install_dir()
            install_dir.mkdir(parents=True, exist_ok=True)
            (install_dir / "version.txt").write_text(latest)
            print(f"Updated to v{latest}")
        else:
            print("No download URL available for this release")
    else:
        print(f"SynthLang v{current}")


def cmd_run(args):
    if not args.file:
        print("Error: No file specified", file=sys.stderr)
        sys.exit(1)
    
    debug = getattr(args, 'debug', False)
    use_python = getattr(args, 'python', False)
    
    try:
        result = run_file(args.file, args.verbose, debug=debug, use_python=use_python)
        if result:
            for k, v in result.items():
                print(f"{k} = {v}")
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_init(args):
    project_name = args.project_name or Path.cwd().name
    init_project(project_name, args.directory if args.directory else None)


def cmd_build(args):
    print("Building project...")
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not installed. Install with: pip install pyinstaller")
        sys.exit(1)
    
    output = getattr(args, 'output', 'slang')
    release = getattr(args, 'release', False)
    
    try:
        build_project(output, release)
        print(f"Build complete: ./dist/{output}")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Build error: {e}")
        sys.exit(1)


def cmd_test(args):
    if args.file:
        test_main(args.file)
    else:
        test_main(directory=".")


def cmd_fmt(args):
    path = args.path or "."
    if Path(path).is_file():
        formatted = format_file(path)
        if args.write:
            with open(path, 'w') as f:
                f.write(formatted)
        else:
            print(formatted)
    else:
        count = format_directory(path)
        print(f"Formatted {count} files")


def cmd_eval(args):
    code = ' '.join(args.code) if isinstance(args.code, list) else args.code
    use_python = getattr(args, 'python', False) or not RUST_AVAILABLE
    if not use_python and RUST_AVAILABLE:
        try:
            result = synthlang_core.execute(code, False)
            if result:
                print(dict(result))
            return
        except Exception as e:
            print(f"Error: {e}")
            return
    result = evaluate(code)
    if result:
        print(result)


def cmd_repl(args):
    use_python = getattr(args, 'python', False) or not RUST_AVAILABLE
    print("SynthLang REPL v1.0.0 - Type 'exit' to quit")
    while True:
        try:
            line = input(">>> ")
            if line.strip() in ('exit', 'quit'):
                break
            if line.strip():
                try:
                    if use_python:
                        result = evaluate(line)
                        if result:
                            print(result)
                    else:
                        result = synthlang_core.execute(line, False)
                        if result:
                            print(dict(result))
                except Exception as e:
                    print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break


def cmd_pip(args):
    name = args.package
    dm = DependencyManager()
    dm.create_default_manifest(Path.cwd().name)
    dm.save_manifest()
    dm.install_pip_package(name, args.version or "", args.global_install if hasattr(args, 'global_install') else False)
    if args.version:
        dm.manifest.dependencies.setdefault("pip", {})[name] = args.version
    else:
        dm.manifest.dependencies.setdefault("pip", {})[name] = "*"
    dm.save_manifest()
    print(f"Installed {name}")


def cmd_npm(args):
    dm = DependencyManager()
    dm.create_default_manifest(Path.cwd().name)
    dm.save_manifest()
    dm.install_npm_package(args.package, args.version or "", args.global_install if hasattr(args, 'global_install') else False)
    if args.version:
        dm.manifest.dependencies.setdefault("npm", {})[args.package] = args.version
    else:
        dm.manifest.dependencies.setdefault("npm", {})[args.package] = "*"
    dm.save_manifest()
    print(f"Installed {args.package}")


def cmd_install(args):
    dm = DependencyManager()
    dm.load_manifest()
    dm.install_all()
    print("Dependencies installed")


def cmd_list(args):
    dm = DependencyManager()
    try:
        dm.load_manifest()
        deps = dm.list_installed()
        for dep in deps:
            print(f"{dep.name}@{dep.version} ({dep.source})")
    except FileNotFoundError:
        print("No slangs.json found")


def cmd_make(args):
    if args.what == 'slangs':
        init_manifest(".")
    else:
        print(f"Unknown make target: {args.what}")


def cmd_doc(args):
    print("Documentation generation stub - use clang-style comments for now")


def cmd_doctor(args):
    print("Checking environment...")
    checks = [
        ("Python", lambda: sys.version.split()[0]),
        ("pip", lambda: subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True).returncode == 0),
        ("Node", lambda: subprocess.run(["node", "--version"], capture_output=True).returncode == 0),
    ]
    for name, check in checks:
        try:
            result = check()
            status = "[OK]" if result else "[MISSING]"
            print(f"{status} {name}")
        except Exception:
            print(f"[MISSING] {name}")


def cmd_watch(args):
    filepath = args.file
    print(f"Watching {filepath}...")
    last_mtime = 0
    while True:
        try:
            mtime = os.stat(filepath).st_mtime
            if mtime > last_mtime:
                print(f"\nFile changed, re-running...")
                try:
                    run_file(filepath, args.verbose, use_cache=False)
                except Exception as e:
                    print(f"Error: {e}")
                last_mtime = mtime
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopped watching.")
            break


def cmd_optimize(args):
    print("Code optimization not yet implemented")


def cmd_profile(args):
    print("Profiling not yet implemented")


def main():
    parser = argparse.ArgumentParser(
        prog='slang',
        description='SynthLang - A modern polyglot programming language'
    )
    parser.add_argument('--version', '-V', action='store_true', help='Show version')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--debug', action='store_true', help='Debug mode - show IR and stack traces')
    parser.add_argument('--python', action='store_true', help='Force using Python backend instead of Rust')
    
    args, remaining = parser.parse_known_args()
    
    if args.version:
        print(f"SynthLang v{read_current_version()}")
        return
    
    if not remaining:
        parser.print_help()
        return
    
    use_python = args.python or not RUST_AVAILABLE
    if not RUST_AVAILABLE:
        print("Warning: synthlang_core not available, using Python backend", file=sys.stderr)
    
    first_arg = remaining[0]
    
    if first_arg in ('init', 'run', 'build', 'test', 'fmt', 'eval', 'repl',
                   'pip', 'npm', 'install', 'list', 'make', 'doc',
                   'doctor', 'watch', 'optimize', 'profile', 'version'):
        args = _build_subparser(first_arg, use_python).parse_args(remaining[1:])
        _dispatch(first_arg, args)
    elif first_arg.endswith('.sl') or not first_arg.startswith('-'):
        if Path(first_arg).exists():
            try:
                result = run_file(first_arg, args.verbose, debug=args.debug, use_python=use_python)
                if result:
                    for k, v in result.items():
                        print(f"{k} = {v}")
            except FileNotFoundError:
                print(f"Error: File '{first_arg}' not found", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            parser.print_help()
    else:
        parser.print_help()


def _build_subparser(cmd: str, use_python: bool = False):
    parser = argparse.ArgumentParser(prog=f'slang {cmd}')
    
    if cmd == 'init':
        parser.add_argument('project_name', nargs='?')
        parser.add_argument('--directory', '-d')
    elif cmd == 'run':
        parser.add_argument('file')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--debug', action='store_true', help='Debug mode')
        parser.add_argument('--python', action='store_true', help='Force using Python backend')
    elif cmd == 'build':
        parser.add_argument('--release', action='store_true')
        parser.add_argument('--output', '-o', default='slang')
    elif cmd == 'test':
        parser.add_argument('file', nargs='?')
    elif cmd == 'fmt':
        parser.add_argument('path', nargs='?')
        parser.add_argument('--write', action='store_true')
    elif cmd == 'eval':
        parser.add_argument('code', nargs='+')
        parser.add_argument('--python', action='store_true', help='Force using Python backend')
    elif cmd == 'repl':
        parser.add_argument('--python', action='store_true', help='Force using Python backend')
    elif cmd == 'pip':
        parser.add_argument('install', choices=['install'])
        parser.add_argument('package')
        parser.add_argument('--version', '-V')
        parser.add_argument('--global', dest='global_install', action='store_true', help='Install to global slangs cache')
    elif cmd == 'npm':
        parser.add_argument('install', choices=['install'])
        parser.add_argument('package')
        parser.add_argument('--version', '-V')
        parser.add_argument('--global', dest='global_install', action='store_true', help='Install to global slangs cache')
    elif cmd == 'watch':
        parser.add_argument('file')
        parser.add_argument('--python', action='store_true', help='Force using Python backend')
    elif cmd == 'optimize':
        parser.add_argument('file')
    elif cmd == 'profile':
        parser.add_argument('file')
    elif cmd == 'make':
        parser.add_argument('what', required=True)
    elif cmd == 'doc':
        parser.add_argument('file', nargs='?')
    elif cmd == 'version':
        parser.add_argument('subcommand', nargs='?', choices=['check', 'update'], default='')
    
    return parser


def _dispatch(cmd: str, args):
    cmd_map = {
        'run': cmd_run, 'init': cmd_init, 'build': cmd_build, 'test': cmd_test,
        'fmt': cmd_fmt, 'eval': cmd_eval, 'repl': cmd_repl, 'pip': cmd_pip,
        'npm': cmd_npm, 'install': cmd_install, 'list': cmd_list, 'make': cmd_make,
        'doc': cmd_doc, 'doctor': cmd_doctor, 'watch': cmd_watch,
        'optimize': cmd_optimize, 'profile': cmd_profile, 'version': cmd_version,
    }
    cmd_map[cmd](args)


if __name__ == '__main__':
    main()