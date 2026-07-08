#!/usr/bin/env python3
"""Test performance - benchmarks for critical operations."""
import unittest
import time
from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler
from synthlang.vm import VM


class TestPerformanceLexer(unittest.TestCase):
    def test_lexer_speed_small(self):
        code = "let x = 1\nlet y = 2\nlet z = 3"
        start = time.perf_counter()
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        elapsed = time.perf_counter() - start
        self.assertTrue(elapsed < 1.0)  # Should complete in under 1 second

    def test_lexer_speed_medium(self):
        # Generate a medium-sized file
        lines = [f"let var_{i} = {i}" for i in range(100)]
        code = "\n".join(lines)
        start = time.perf_counter()
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        elapsed = time.perf_counter() - start
        self.assertTrue(elapsed < 1.0)


class TestPerformanceVM(unittest.TestCase):
    def test_vm_speed_simple(self):
        code = "let x = 1 + 2 + 3 + 4 + 5"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        start = time.perf_counter()
        vm = VM(ir)
        vm.run()
        elapsed = time.perf_counter() - start
        self.assertTrue(elapsed < 1.0)


class TestPerformanceMemory(unittest.TestCase):
    def test_variables_memory(self):
        code = "\n".join([f"let var_{i} = {i}" for i in range(100)])
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(len(result), 100)


if __name__ == '__main__':
    unittest.main()