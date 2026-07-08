#!/usr/bin/env python3
"""Test Python FFI - Foreign Function Interface."""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler
from synthlang.vm import VM
from synthlang.ffi import FFILoader, FFIError


class TestPythonFFI(unittest.TestCase):
    def test_ffi_loader_creation(self):
        loader = FFILoader()
        self.assertIsNotNone(loader)
        self.assertIsInstance(loader.loaded_modules, dict)
        self.assertIsInstance(loader.py_modules, dict)

    def test_import_math_module(self):
        loader = FFILoader()
        math = loader.import_python_module('math')
        self.assertEqual(math.as_name, 'math')
        self.assertIsNotNone(math.module_obj)

    def test_call_python_sqrt(self):
        loader = FFILoader()
        loader.import_python_module('math', 'math')
        result = loader.call_python('math', 'sqrt', [16])
        self.assertEqual(result, 4.0)

    def test_call_python_pow(self):
        loader = FFILoader()
        loader.import_python_module('math', 'math')
        result = loader.call_python('math', 'pow', [2, 10])
        self.assertEqual(result, 1024.0)

    def test_get_python_attr(self):
        loader = FFILoader()
        loader.import_python_module('math', 'math')
        pi = loader.get_python_attr('math', 'pi')
        self.assertAlmostEqual(pi, 3.14159, places=4)


class TestJavaScriptFFI(unittest.TestCase):
    def test_js_ffi_stub(self):
        loader = FFILoader()
        with self.assertRaises(FFIError):
            loader.call_javascript('nonexistent', 'test', [1, 2])


if __name__ == '__main__':
    unittest.main()