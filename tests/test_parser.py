#!/usr/bin/env python3
"""Test parser AST generation."""
import unittest
from synthlang.lexer import Lexer
from synthlang.parser import Parser, NodeType


class TestParser(unittest.TestCase):
    def test_variable(self):
        lexer = Lexer("let x = 5")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertEqual(len(ast), 1)
        self.assertEqual(ast[0].type, NodeType.VARIABLE)

    def test_function(self):
        code = '''fn add(a: int, b: int): int
    return a + b
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertEqual(len(ast), 1)
        self.assertEqual(ast[0].type, NodeType.FUNCTION)

    def test_if(self):
        code = '''if x > 0:
    let y = 1
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertEqual(len(ast), 1)
        self.assertEqual(ast[0].type, NodeType.IF)


if __name__ == '__main__':
    unittest.main()