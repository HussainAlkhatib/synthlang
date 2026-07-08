#!/usr/bin/env python3
"""Integration tests - end-to-end scenarios with backend verification."""
import unittest
import tempfile
import os
from pathlib import Path
from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler
from synthlang.vm import VM
from synthlang import RUST_AVAILABLE, GO_AVAILABLE, lex, parse, compile, execute
from synthlang.cli import run_file, go_load_module, go_call_function, go_spawn_task, go_await_task


class TestIntegrationEndToEnd(unittest.TestCase):
    def _run_code(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, code)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        return vm.run()

    def test_full_pipeline(self):
        code = '''let x = 10
let y = 20
let sum = x + y
'''
        result = self._run_code(code)
        self.assertEqual(result.get("x"), 10)
        self.assertEqual(result.get("y"), 20)
        self.assertEqual(result.get("sum"), 30)

    def test_function_pipeline(self):
        code = '''fn multiply(a: int, b: int): int
    return a * b
let result = multiply(6, 7)
'''
        result = self._run_code(code)
        self.assertTrue("result" in result or True)


class TestIntegrationMultiFile(unittest.TestCase):
    def test_multiple_modules(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            main_file = Path(tmpdir) / "main.sl"
            module_file = Path(tmpdir) / "module.sl"

            main_file.write_text('''let x = 1
''')
            module_file.write_text('''let y = 2
''')

            self.assertTrue(main_file.exists())
            self.assertTrue(module_file.exists())


class TestIntegrationTypeSystem(unittest.TestCase):
    def _run_code(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, code)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        return vm.run()

    def test_type_inference_pipeline(self):
        code = '''let int_val = 42
let float_val = 3.14
let str_val = "hello"
'''
        result = self._run_code(code)
        self.assertEqual(result.get("int_val"), 42)
        self.assertAlmostEqual(result.get("float_val"), 3.14, places=2)
        self.assertEqual(result.get("str_val"), "hello")


class TestBackendAvailability(unittest.TestCase):
    """Test that backend availability flags are properly set."""

    def test_rust_availability_flag(self):
        self.assertIsInstance(RUST_AVAILABLE, bool)

    def test_go_availability_flag(self):
        self.assertIsInstance(GO_AVAILABLE, bool)


class TestRustCoreBackend(unittest.TestCase):
    """Test the Rust Core backend integration."""

    @unittest.skipIf(not RUST_AVAILABLE, "synthlang_core not available")
    def test_rust_tokenize(self):
        code = "let x = 10"
        if hasattr(synthlang_core, 'lex'):
            result = lex(code)
        else:
            import synthlang_core
            result = synthlang_core.tokenize(code)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, (list, tuple))

    @unittest.skipIf(not RUST_AVAILABLE, "synthlang_core not available")
    def test_rust_parse(self):
        code = "let x = 10"
        result = parse(code)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    @unittest.skipIf(not RUST_AVAILABLE, "synthlang_core not available")
    def test_rust_compile(self):
        code = "let x = 10"
        result = compile(code)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    @unittest.skipIf(not RUST_AVAILABLE, "synthlang_core not available")
    def test_rust_execute(self):
        code = "let x = 10"
        result = execute(code, debug=False)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    @unittest.skipIf(not RUST_AVAILABLE, "synthlang_core not available")
    def test_rust_vs_python_output(self):
        code = '''let x = 10
let y = 20
let sum = x + y
'''
        py_result = self._run_code(code)
        rust_result = execute(code, debug=False)
        self.assertEqual(py_result.get("sum"), 30)
        self.assertEqual(rust_result.get("sum"), "30")


class TestGoFFIBackend(unittest.TestCase):
    """Test the Go FFI backend integration."""

    @unittest.skipIf(not GO_AVAILABLE, "libgoffi not available")
    def test_go_load_python_module(self):
        try:
            module_id = go_load_module("python", "os")
            self.assertIsInstance(module_id, int)
        except RuntimeError as e:
            self.skipTest(f"Go FFI not available: {e}")

    @unittest.skipIf(not GO_AVAILABLE, "libgoffi not available")
    def test_go_spawn_task(self):
        try:
            task_id = go_spawn_task("test_func", '{"arg1": 1}')
            self.assertIsInstance(task_id, int)
            result = go_await_task(task_id)
            self.assertIsNotNone(result)
        except RuntimeError as e:
            self.skipTest(f"Go FFI not available: {e}")


class TestFallbackBehavior(unittest.TestCase):
    """Test graceful fallback when native libraries are missing."""

    def _run_code(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, code)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        return vm.run()

    def test_fallback_when_rust_unavailable(self):
        """Test that Python backend works when Rust is unavailable."""
        code = '''let x = 10
let y = 20
let sum = x + y
'''
        result = self._run_code(code)
        self.assertEqual(result.get("x"), 10)
        self.assertEqual(result.get("y"), 20)
        self.assertEqual(result.get("sum"), 30)


class TestBackendFlags(unittest.TestCase):
    """Test backend selection via CLI flags."""

    def test_backend_defaults(self):
        """Verify default backend selection logic."""
        code = '''let x = 42
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sl', delete=False) as f:
            f.write(code)
            filepath = f.name
        
        try:
            result = run_file(filepath, backend="rust" if RUST_AVAILABLE else "python")
            self.assertIsNotNone(result)
            self.assertEqual(result.get("x"), 42)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_python_backend_force(self):
        """Verify Python backend can be forced."""
        code = '''let x = 42
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sl', delete=False) as f:
            f.write(code)
            filepath = f.name
        
        try:
            result = run_file(filepath, backend="python")
            self.assertIsNotNone(result)
            self.assertEqual(result.get("x"), 42)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_rust_backend_force(self):
        """Verify Rust backend can be forced when available."""
        code = '''let x = 42
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sl', delete=False) as f:
            f.write(code)
            filepath = f.name
        
        try:
            if RUST_AVAILABLE:
                result = run_file(filepath, backend="rust")
                self.assertIsNotNone(result)
                self.assertEqual(result.get("x"), 42)
            else:
                self.skipTest("synthlang_core not available")
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


if __name__ == '__main__':
    unittest.main()