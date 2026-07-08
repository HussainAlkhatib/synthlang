#!/usr/bin/env python3
"""Test control flow execution."""
import unittest
from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler
from synthlang.vm import VM


class TestControlFlow(unittest.TestCase):
    def test_if_simple(self):
        code = '''let x = 10
if x > 5:
    let result = 1
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 1)

    def test_if_false_branch(self):
        code = '''let x = 10
if x < 5:
    let result = 1
else:
    let result = 2
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 2)

    def test_if_true_branch(self):
        code = '''let x = 10
if x > 5:
    let result = 1
else:
    let result = 2
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 1)

    def test_elif_branch(self):
        code = '''let x = 10
if x < 0:
    let result = 1
elif x > 5:
    let result = 2
else:
    let result = 3
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 2)

    def test_elif_falls_through(self):
        code = '''let x = 10
if x < 0:
    let result = 1
elif x < 5:
    let result = 2
elif x > 5:
    let result = 3
else:
    let result = 4
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 3)

    def test_while_compiles(self):
        code = '''let i = 0
while i < 3:
    let i = 1
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        # For now, just verify it compiles
        self.assertIn('main', ir.functions)

    def test_for_compiles(self):
        code = '''let sum = 0
for n in [1]:
    let sum = 1
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        self.assertIn('main', ir.functions)


if __name__ == '__main__':
    unittest.main()