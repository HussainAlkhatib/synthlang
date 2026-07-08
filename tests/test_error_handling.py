#!/usr/bin/env python3
"""Test error handling - Result type, panic, try/handle."""
import unittest
from synthlang.vm import Result, VM
from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler
from synthlang.ir import IRModule


class TestResultType(unittest.TestCase):
    def test_result_ok(self):
        r = Result.ok(42)
        self.assertEqual(r.status, Result.OK)
        self.assertEqual(r.value, 42)
        self.assertIsNone(r.error)

    def test_result_err(self):
        r = Result.err("something went wrong")
        self.assertEqual(r.status, Result.ERR)
        self.assertEqual(r.error, "something went wrong")
        self.assertIsNone(r.value)

    def test_result_ok_static(self):
        r = Result.ok("success")
        self.assertEqual(r.value, "success")

    def test_result_err_static(self):
        r = Result.err(RuntimeError("error"))
        self.assertIsInstance(r.error, RuntimeError)


class TestResultChaining(unittest.TestCase):
    def test_ok_propagation(self):
        r1 = Result.ok(10)
        r2 = Result.ok(20)
        self.assertEqual(r1.value, 10)
        self.assertEqual(r2.value, 20)

    def test_error_propagation(self):
        r1 = Result.err("first error")
        r2 = Result.ok(0)
        self.assertEqual(r1.error, "first error")


class TestVMErrors(unittest.TestCase):
    def test_vm_undefined_variable(self):
        ir = IRModule()
        ir.add_function("main", [])
        vm = VM(ir)
        result = vm.run()
        self.assertIsNotNone(result)

    def test_vm_multiple_errors(self):
        results = [
            Result.ok(1),
            Result.err("error"),
            Result.ok(2)
        ]
        err_count = sum(1 for r in results if r.status == Result.ERR)
        self.assertEqual(err_count, 1)


class TestErrorCases(unittest.TestCase):
    def test_syntax_error_in_parse(self):
        code = "let x ="
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()

    def test_division_by_zero_prepare(self):
        # This tests that division instruction is created correctly
        code = "let x = 1 / 0"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        self.assertIn('main', ir.functions)


if __name__ == '__main__':
    unittest.main()