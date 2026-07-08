"""SynthLang FFI - Foreign Function Interface for Python/JavaScript/Rust/C/Go/Java modules."""
import ctypes
import subprocess
import os
import sys
import asyncio
import importlib
import json
from pathlib import Path
from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass, field
import inspect
import threading


class FFIError(Exception):
    """Enhanced FFI error with language, module, and function context."""
    def __init__(self, message: str, language: str = None, module: str = None, function: str = None, original_error: str = None):
        self.language = language
        self.module = module
        self.function = function
        self.original_error = original_error
        super().__init__(message)


@dataclass
class ImportedModule:
    language: str
    module_path: str
    as_name: str
    module_obj: Any = None
    cached_functions: Dict[str, Callable] = field(default_factory=dict)


class FFILoader:
    def __init__(self):
        self.loaded_modules: Dict[str, ImportedModule] = {}
        self.py_modules: Dict[str, Any] = {}
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._event_loop_thread: Optional[threading.Thread] = None
        self._start_async_loop()
    
    def _start_async_loop(self):
        """Start a background thread with a persistent event loop for async FFI calls."""
        self._event_loop = asyncio.new_event_loop()
        def run_loop():
            asyncio.set_event_loop(self._event_loop)
            self._event_loop.run_forever()
        self._event_loop_thread = threading.Thread(target=run_loop, daemon=True)
        self._event_loop_thread.start()

    def import_python_module(self, module_path: str, as_name: str = None) -> ImportedModule:
        key = f"python:{module_path}:{as_name or module_path}"
        if key in self.loaded_modules:
            return self.loaded_modules[key]
        
        # Check if this is a std module (.sl file)
        if module_path.startswith('std/') or module_path.endswith('.sl'):
            # Load SynthLang std module
            slang_path = Path(__file__).parent.parent.parent / module_path.replace('std/', 'std/' if module_path.startswith('std/') else '')
            if not slang_path.suffix:
                slang_path = slang_path.with_suffix('.sl')
            if slang_path.exists():
                # For std modules, we compile and execute them to extract functions
                from .cli import run_file
                result = run_file(str(slang_path))
                # Create a synthetic module object that wraps the VM
                class SlangStdModule:
                    def __init__(self, vm_vars):
                        self._vm_vars = vm_vars
                    def __getattr__(self, name):
                        if name in self._vm_vars:
                            return self._vm_vars[name]
                        raise AttributeError(f"Function '{name}' not found in std module")
                
                imported = ImportedModule(
                    language='python',
                    module_path=module_path,
                    as_name=as_name or module_path.split('/')[-1].replace('.sl', ''),
                    module_obj=SlangStdModule(result)
                )
                self.loaded_modules[key] = imported
                self.py_modules[as_name or module_path] = imported.module_obj
                return imported
            else:
                raise FFIError(
                    f"Cannot find SynthLang std module '{module_path}'",
                    language='python', module=module_path, original_error="File not found"
                )
        
        try:
            module = importlib.import_module(module_path)
            imported = ImportedModule(
                language='python',
                module_path=module_path,
                as_name=as_name or module_path,
                module_obj=module
            )
            self.loaded_modules[key] = imported
            self.py_modules[as_name or module_path] = module
            return imported
        except ImportError as e:
            raise FFIError(
                f"Cannot import Python module '{module_path}': {e}. Did you run 'slang pip install {module_path}'?",
                language='python', module=module_path, original_error=str(e)
            )

    def call_python(self, module_name: str, func_name: str, args: list = None, slang_vm=None) -> Any:
        if module_name not in self.py_modules:
            raise FFIError(
                f"Python module '{module_name}' not loaded. Use @python module \"{module_name}\" first.",
                language='python', module=module_name
            )
        
        module = self.py_modules[module_name]
        
        obj = module
        for part in func_name.split('.'):
            obj = getattr(obj, part, None)
            if obj is None:
                raise FFIError(
                    f"Attribute '{part}' not found in '{func_name}' path",
                    language='python', module=module_name, function=func_name
                )
        
        if isinstance(obj, SynthLangFunction):
            return obj.call_with_vm(slang_vm, args or [])
        
        if not callable(obj):
            raise FFIError(
                f"'{func_name}' is not callable in module '{module_name}'",
                language='python', module=module_name, function=func_name
            )
        
        processed_args = []
        for arg in (args or []):
            if isinstance(arg, SynthLangFunction):
                processed_args.append(arg.create_python_callback(slang_vm))
            else:
                processed_args.append(arg)
        
        try:
            return obj(*processed_args)
        except Exception as e:
            raise FFIError(
                f"Error calling {module_name}.{func_name}: {e}",
                language='python', module=module_name, function=func_name, original_error=str(e)
            )
    
    def call_python_async(self, module_name: str, func_name: str, args: list = None, slang_vm=None) -> Any:
        """Call Python function with async support - handles coroutines automatically."""
        if module_name not in self.py_modules:
            raise FFIError(
                f"Python module '{module_name}' not loaded. Use @python module \"{module_name}\" first.",
                language='python', module=module_name
            )
        
        module = self.py_modules[module_name]
        
        obj = module
        for part in func_name.split('.'):
            obj = getattr(obj, part, None)
            if obj is None:
                raise FFIError(
                    f"Attribute '{part}' not found in '{func_name}' path",
                    language='python', module=module_name, function=func_name
                )
        
        if isinstance(obj, SynthLangFunction):
            return obj.call_with_vm(slang_vm, args or [])
        
        processed_args = []
        for arg in (args or []):
            if isinstance(arg, SynthLangFunction):
                processed_args.append(arg.create_python_callback(slang_vm))
            elif callable(arg) and hasattr(arg, '__call__'):
                processed_args.append(arg)
            else:
                processed_args.append(arg)
        
        if not callable(obj):
            raise FFIError(
                f"'{func_name}' is not callable in module '{module_name}'",
                language='python', module=module_name, function=func_name
            )
        
        try:
            result = obj(*processed_args)
            # Handle async coroutines using persistent event loop
            if inspect.iscoroutine(result):
                if self._event_loop and not self._event_loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(result, self._event_loop)
                    return future.result(timeout=30)
                else:
                    return result
            elif inspect.iscoroutinefunction(obj):
                # For coroutine functions, we need to await them
                async_result = obj(*processed_args)
                if self._event_loop and not self._event_loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(async_result, self._event_loop)
                    return future.result(timeout=30)
                else:
                    loop = asyncio.new_event_loop()
                    return loop.run_until_complete(async_result)
            return result
        except Exception as e:
            raise FFIError(
                f"Error calling {module_name}.{func_name}: {e}",
                language='python', module=module_name, function=func_name, original_error=str(e)
            )

    def get_python_attr(self, module_name: str, attr_name: str) -> Any:
        if module_name not in self.py_modules:
            raise FFIError(
                f"Python module '{module_name}' not loaded",
                language='python', module=module_name
            )
        return getattr(self.py_modules[module_name], attr_name)

    def load_c_module(self, path: str) -> ctypes.CDLL:
        key = f"c:{path}"
        if key in self.loaded_modules:
            return self.loaded_modules[key].module_obj
        try:
            lib = ctypes.CDLL(path)
            imported = ImportedModule(
                language='c',
                module_path=path,
                as_name=os.path.basename(path),
                module_obj=lib
            )
            self.loaded_modules[key] = imported
            return lib
        except Exception as e:
            raise FFIError(
                f"Cannot load C module '{path}': {e}",
                language='c', module=path, original_error=str(e)
            )

    def load_rust_module(self, path: str) -> ctypes.CDLL:
        key = f"rust:{path}"
        if key in self.loaded_modules:
            return self.loaded_modules[key].module_obj
        return self.load_c_module(path)

    def call_c(self, lib_path: str, func_name: str, args: list, arg_types: list = None, return_type: type = None) -> Any:
        try:
            lib = self.load_c_module(lib_path)
            func = getattr(lib, func_name)
            if arg_types:
                func.argtypes = arg_types
            if return_type:
                func.restype = return_type
            return func(*args)
        except AttributeError:
            raise FFIError(
                f"Function '{func_name}' not found in C module '{lib_path}'",
                language='c', module=lib_path, function=func_name
            )
        except Exception as e:
            raise FFIError(
                f"Error calling C function {func_name}: {e}",
                language='c', module=lib_path, function=func_name, original_error=str(e)
            )

    def call_javascript(self, module_path: str, func_name: str, args: list = None) -> Any:
        import tempfile
        
        js_code = f'''const module = require("{module_path}");
const result = module.{func_name}({json.dumps(args or [])});
console.log(JSON.stringify(result));'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            os.unlink(temp_file)
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout.strip())
                except json.JSONDecodeError:
                    return result.stdout.strip()
            raise FFIError(
                f"JavaScript error: {result.stderr}",
                language='javascript', module=module_path, function=func_name, original_error=result.stderr
            )
        except FileNotFoundError:
            raise FFIError(
                "'node' not found - JavaScript FFI requires Node.js installed",
                language='javascript'
            )
        except subprocess.TimeoutExpired:
            raise FFIError(
                f"JavaScript call timed out after 30 seconds",
                language='javascript', module=module_path, function=func_name
            )

    def compile_rust_module(self, source_path: str, output_path: str = None) -> str:
        if not output_path:
            base = os.path.splitext(source_path)[0]
            output_path = f"{base}.so"
        
        result = subprocess.run(
            ['cargo', 'build', '--release', '--target', 'x86_64-unknown-linux-gnu'],
            cwd=os.path.dirname(source_path) or '.',
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise FFIError(
                f"Rust compilation failed: {result.stderr}",
                language='rust', module=source_path, original_error=result.stderr
            )
        return output_path

    def compile_go_module(self, source_path: str, output_path: str = None) -> str:
        if not output_path:
            base = os.path.splitext(source_path)[0]
            output_path = f"{base}.so"
        
        result = subprocess.run(
            ['go', 'build', '-buildmode=c-shared', '-o', output_path, source_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise FFIError(
                f"Go compilation failed: {result.stderr}",
                language='go', module=source_path, original_error=result.stderr
            )
        return output_path


ffi_loader = FFILoader()

# Try to load Go FFI library
try:
    import platform
    _go_lib_path = str(Path(__file__).parent / ("libgoffi.dll" if platform.system() == "Windows" else "libgoffi.so" if platform.system() != "Darwin" else "libgoffi.dylib"))
    _go_ffi = ctypes.CDLL(_go_lib_path)
    _go_ffi.LoadPythonModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _go_ffi.LoadPythonModule.restype = ctypes.c_ulonglong
    _go_ffi.LoadRustModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _go_ffi.LoadRustModule.restype = ctypes.c_ulonglong
    _go_ffi.LoadCModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _go_ffi.LoadCModule.restype = ctypes.c_ulonglong
    _go_ffi.LoadGoModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _go_ffi.LoadGoModule.restype = ctypes.c_ulonglong
    _go_ffi.LoadJavaScriptModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _go_ffi.LoadJavaScriptModule.restype = ctypes.c_ulonglong
    _go_ffi.CallFunction.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    _go_ffi.CallFunction.restype = ctypes.c_char_p
    _go_ffi.SpawnTask.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _go_ffi.SpawnTask.restype = ctypes.c_ulonglong
    _go_ffi.AwaitTask.argtypes = [ctypes.c_ulonglong]
    _go_ffi.AwaitTask.restype = ctypes.c_char_p
    GO_FFI_AVAILABLE = True
except Exception:
    GO_FFI_AVAILABLE = False
    _go_ffi = None


class SynthLangFunction:
    """Represents a SynthLang function that can be passed as a callback to Python."""
    def __init__(self, name: str, vm: Any = None):
        self.name = name
        self.vm = vm

    def call_with_vm(self, vm: Any, args: list) -> Any:
        """Call this function using the provided VM."""
        if vm is None:
            raise RuntimeError("Cannot call SynthLang function without VM context")
        if self.name in vm.functions:
            return vm._run_function(self.name, args)
        raise RuntimeError(f"SynthLang function '{self.name}' not found in VM")

    def create_python_callback(self, vm: Any) -> Callable:
        """Create a Python callable that invokes this SynthLang function."""
        def callback(*args):
            return self.call_with_vm(vm, list(args))
        return callback


def rust_module(path, as_name=None):
    if as_name is None:
        as_name = os.path.basename(path).split('.')[0]
    ffi_loader.load_rust_module(path)
    return as_name

def c_module(path, as_name=None):
    if as_name is None:
        as_name = os.path.basename(path).split('.')[0]
    ffi_loader.load_c_module(path)
    return as_name

def java_module(path, as_name=None):
    pass

# Go FFI wrapper functions
def go_load_python_module(name: str, path: str) -> int:
    if GO_FFI_AVAILABLE and _go_ffi:
        return _go_ffi.LoadPythonModule(name.encode('utf-8'), path.encode('utf-8'))
    raise FFIError("Go FFI not available", language='go')

def go_load_rust_module(name: str, path: str) -> int:
    if GO_FFI_AVAILABLE and _go_ffi:
        return _go_ffi.LoadRustModule(name.encode('utf-8'), path.encode('utf-8'))
    raise FFIError("Go FFI not available", language='go')

def go_load_c_module(name: str, path: str) -> int:
    if GO_FFI_AVAILABLE and _go_ffi:
        return _go_ffi.LoadCModule(name.encode('utf-8'), path.encode('utf-8'))
    raise FFIError("Go FFI not available", language='go')

def go_load_go_module(name: str, path: str) -> int:
    if GO_FFI_AVAILABLE and _go_ffi:
        return _go_ffi.LoadGoModule(name.encode('utf-8'), path.encode('utf-8'))
    raise FFIError("Go FFI not available", language='go')

def go_load_javascript_module(name: str, path: str) -> int:
    if GO_FFI_AVAILABLE and _go_ffi:
        return _go_ffi.LoadJavaScriptModule(name.encode('utf-8'), path.encode('utf-8'))
    raise FFIError("Go FFI not available", language='go')

def go_call_function(module: str, function: str, args: str) -> str:
    if GO_FFI_AVAILABLE and _go_ffi:
        result = _go_ffi.CallFunction(module.encode('utf-8'), function.encode('utf-8'), args.encode('utf-8'))
        return result.decode('utf-8') if result else ""
    raise FFIError("Go FFI not available", language='go')

def go_spawn_task(func: str, args: str) -> int:
    if GO_FFI_AVAILABLE and _go_ffi:
        return _go_ffi.SpawnTask(func.encode('utf-8'), args.encode('utf-8'))
    raise FFIError("Go FFI not available", language='go')

def go_await_task(task_id: int) -> str:
    if GO_FFI_AVAILABLE and _go_ffi:
        result = _go_ffi.AwaitTask(task_id)
        return result.decode('utf-8') if result else ""
    raise FFIError("Go FFI not available", language='go')