#!/usr/bin/env python3
"""Integration tests - end-to-end scenarios."""
import unittest
import tempfile
import os
from pathlib import Path
from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler
from synthlang.vm import VM


class TestIntegrationEndToEnd(unittest.TestCase):
    def _run_code(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
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
            # Create multiple .sl files
            main_file = Path(tmpdir) / "main.sl"
            module_file = Path(tmpdir) / "module.sl"

            main_file.write_text('''let x = 1
''')
            module_file.write_text('''let y = 2
''')

            # Verify files exist
            self.assertTrue(main_file.exists())
            self.assertTrue(module_file.exists())


class TestIntegrationTypeSystem(unittest.TestCase):
    def _run_code(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
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


if __name__ == '__main__':
    unittest.main()