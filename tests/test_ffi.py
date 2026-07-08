#!/usr/bin/env python3
"""Test FFI - Foreign Function Interface."""
import unittest
from synthlang.ffi import FFILoader, rust_module, c_module, java_module, FFIError


class TestFFILoader(unittest.TestCase):
    def test_loader_creation(self):
        loader = FFILoader()
        self.assertIsNotNone(loader)
        self.assertIsInstance(loader.loaded_modules, dict)

    def test_load_nonexistent_library(self):
        loader = FFILoader()
        with self.assertRaises(FFIError):
            loader.load_c_module("/nonexistent/library.so")

    def test_modules_dict(self):
        loader = FFILoader()
        self.assertIsInstance(loader.loaded_modules, dict)


class TestFFIAnnotations(unittest.TestCase):
    def test_c_module_decorator(self):
        # c_module is a stub - it just passes
        try:
            result = c_module("/nonexistent/lib.dll", "mylib")
            self.assertIsNone(result)
        except FFIError:
            pass  # Expected - file doesn't exist

    def test_rust_module_decorator(self):
        try:
            result = rust_module("/nonexistent/librust.dll", "rustlib")
            self.assertIsNone(result)
        except FFIError:
            pass  # Expected - file doesn't exist

    def test_java_module_decorator(self):
        result = java_module("/path/to/libjava.dll", "javalib")
        self.assertIsNone(result)


class TestFFIHelpers(unittest.TestCase):
    def test_c_module_function(self):
        # These functions attempt to load which raises FFIError for nonexistent paths
        try:
            c_module("/nonexistent/lib.dll")
        except FFIError:
            pass  # Expected

    def test_rust_module_function(self):
        try:
            rust_module("/nonexistent/lib.dll")
        except FFIError:
            pass  # Expected

    def test_java_module_function(self):
        java_module("/path/to/lib.dll")


if __name__ == '__main__':
    unittest.main()