#!/usr/bin/env python3
"""Test running all examples."""
import unittest
import os
from pathlib import Path
from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler


class TestExamples(unittest.TestCase):
    def _compile_example(self, filepath):
        with open(filepath, 'r') as f:
            source = f.read()
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        return ir

    def test_hello_example(self):
        example_path = Path("examples/hello.sl")
        if example_path.exists():
            # Just verify it tokenizes without error
            with open(example_path) as f:
                source = f.read()
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            self.assertTrue(len(tokens) > 0)

    def test_controlflow_example(self):
        example_path = Path("examples/controlflow.sl")
        if example_path.exists():
            with open(example_path) as f:
                source = f.read()
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            compiler = Compiler()
            ir = compiler.compile(ast)
            self.assertIn('main', ir.functions)

    def test_game_example(self):
        example_path = Path("examples/game.sl")
        if example_path.exists():
            with open(example_path) as f:
                source = f.read()
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            self.assertTrue(len(tokens) > 0)

    def test_web_server_example(self):
        example_path = Path("examples/web_server.sl")
        if example_path.exists():
            with open(example_path) as f:
                source = f.read()
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            self.assertTrue(len(tokens) > 0)

    def test_cli_tool_example(self):
        example_path = Path("examples/cli_tool.sl")
        if example_path.exists():
            with open(example_path) as f:
                source = f.read()
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            self.assertTrue(len(tokens) > 0)


if __name__ == '__main__':
    unittest.main()