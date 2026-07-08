#!/usr/bin/env python3
"""Test interpreter execution."""
import unittest
from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler
from synthlang.vm import VM


class TestInterpreter(unittest.TestCase):
    def test_basic_execution(self):
        code = "let x = 5"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get('x'), 5)

    def test_expression(self):
        code = "let x = 1 + 2"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get('x'), 3)


if __name__ == '__main__':
    unittest.main()