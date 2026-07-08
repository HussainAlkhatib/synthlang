#!/usr/bin/env python3
"""Test Go FFI integration - Tests the Go library from Python."""

import unittest
import sys
from pathlib import Path

try:
    import ctypes
    import platform
    
    if platform.system() == "Windows":
        go_lib_name = "libgoffi.dll"
    elif platform.system() == "Darwin":
        go_lib_name = "libgoffi.dylib"
    else:
        go_lib_name = "libgoffi.so"
    
    go_lib_path = str(Path(__file__).parent.parent / "src" / "synthlang" / go_lib_name)
    go_ffi = ctypes.CDLL(go_lib_path)
    go_ffi.LoadPythonModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    go_ffi.LoadPythonModule.restype = ctypes.c_ulonglong
    go_ffi.LoadRustModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    go_ffi.LoadRustModule.restype = ctypes.c_ulonglong
    go_ffi.LoadCModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    go_ffi.LoadCModule.restype = ctypes.c_ulonglong
    go_ffi.LoadGoModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    go_ffi.LoadGoModule.restype = ctypes.c_ulonglong
    go_ffi.LoadJavaScriptModule.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    go_ffi.LoadJavaScriptModule.restype = ctypes.c_ulonglong
    go_ffi.CallFunction.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    go_ffi.CallFunction.restype = ctypes.c_char_p
    go_ffi.SpawnTask.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    go_ffi.SpawnTask.restype = ctypes.c_ulonglong
    go_ffi.AwaitTask.argtypes = [ctypes.c_ulonglong]
    go_ffi.AwaitTask.restype = ctypes.c_char_p
    GO_AVAILABLE = True
except Exception:
    GO_AVAILABLE = False
    go_ffi = None


@unittest.skipIf(not GO_AVAILABLE, "Go FFI library not available")
class TestGoFFILoader(unittest.TestCase):
    def test_load_python_module(self):
        if not GO_AVAILABLE:
            return
        result = go_ffi.LoadPythonModule(b"test_module", b"/path/to/module.py")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_load_rust_module(self):
        if not GO_AVAILABLE:
            return
        result = go_ffi.LoadRustModule(b"test_rust", b"/path/to/lib.rs")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_load_c_module(self):
        if not GO_AVAILABLE:
            return
        result = go_ffi.LoadCModule(b"test_c", b"/path/to/lib.so")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_load_go_module(self):
        if not GO_AVAILABLE:
            return
        result = go_ffi.LoadGoModule(b"test_go", b"/path/to/lib.go")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_load_javascript_module(self):
        if not GO_AVAILABLE:
            return
        result = go_ffi.LoadJavaScriptModule(b"test_js", b"/path/to/lib.js")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)


@unittest.skipIf(not GO_AVAILABLE, "Go FFI library not available")
class TestGoScheduler(unittest.TestCase):
    def test_spawn_task(self):
        if not GO_AVAILABLE:
            return
        result = go_ffi.SpawnTask(b"test_func", b'{"arg": 1}')
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_await_task(self):
        if not GO_AVAILABLE:
            return
        task_id = go_ffi.SpawnTask(b"test_func", b'{}')
        result = go_ffi.AwaitTask(task_id)
        self.assertIsNotNone(result)
        
        result_str = result.decode('utf-8') if isinstance(result, bytes) else result
        self.assertIn('status', result_str)


if __name__ == '__main__':
    unittest.main()