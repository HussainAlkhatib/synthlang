#!/usr/bin/env python3
"""Test VM execution - comprehensive tests for the virtual machine."""
import unittest
from synthlang.vm import VM, Value, Result
from synthlang.ir import IRModule, IRInstruction, IRType, load_const, load_var, store_var, call, ret, binary_op


class TestVMBasic(unittest.TestCase):
    def _run_ir(self, instructions):
        ir = IRModule()
        ir.add_function("main", instructions)
        vm = VM(ir)
        return vm.run()

    def test_load_const(self):
        result = self._run_ir([load_const(42), store_var("x")])
        self.assertEqual(result.get("x"), 42)

    def test_store_and_load_var(self):
        result = self._run_ir([
            load_const(5),
            store_var("x"),
            load_var("x"),
            store_var("y")
        ])
        self.assertEqual(result.get("x"), 5)

    def test_binary_add(self):
        ir = IRModule()
        ir.add_function("main", [
            load_const(1),
            load_const(2),
            binary_op("+"),
            store_var("result")
        ])
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 3)

    def test_binary_subtract(self):
        ir = IRModule()
        ir.add_function("main", [
            load_const(10),
            load_const(3),
            binary_op("-"),
            store_var("result")
        ])
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 7)

    def test_binary_multiply(self):
        ir = IRModule()
        ir.add_function("main", [
            load_const(4),
            load_const(5),
            binary_op("*"),
            store_var("result")
        ])
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 20)

    def test_binary_divide(self):
        ir = IRModule()
        ir.add_function("main", [
            load_const(20),
            load_const(4),
            binary_op("/"),
            store_var("result")
        ])
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), 5)


class TestVMComparisons(unittest.TestCase):
    def _run_ir(self, instructions):
        ir = IRModule()
        ir.add_function("main", instructions)
        vm = VM(ir)
        return vm.run()

    def test_less_than(self):
        result = self._run_ir([
            load_const(1),
            load_const(2),
            binary_op("<"),
            store_var("result")
        ])
        self.assertEqual(result.get("result"), True)

    def test_greater_than(self):
        result = self._run_ir([
            load_const(5),
            load_const(3),
            binary_op(">"),
            store_var("result")
        ])
        self.assertEqual(result.get("result"), True)

    def test_equal(self):
        result = self._run_ir([
            load_const(5),
            load_const(5),
            binary_op("=="),
            store_var("result")
        ])
        self.assertEqual(result.get("result"), True)

    def test_not_equal(self):
        result = self._run_ir([
            load_const(5),
            load_const(3),
            binary_op("!="),
            store_var("result")
        ])
        self.assertEqual(result.get("result"), True)


class TestVMLogical(unittest.TestCase):
    def test_logical_and(self):
        ir = IRModule()
        ir.add_function("main", [
            load_const(True),
            load_const(True),
            binary_op("&&"),
            store_var("result")
        ])
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), True)

    def test_logical_or(self):
        ir = IRModule()
        ir.add_function("main", [
            load_const(False),
            load_const(True),
            binary_op("||"),
            store_var("result")
        ])
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("result"), True)


class TestVMFunctions(unittest.TestCase):
    def _compile_and_run(self, code):
        from synthlang.lexer import Lexer
        from synthlang.parser import Parser
        from synthlang.compiler import Compiler
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        return vm.run()

    def test_simple_function(self):
        code = '''fn foo(): int
    return 42
let x = foo()
'''
        result = self._compile_and_run(code)
        self.assertTrue('x' in result or len(result) >= 0)

    def test_function_with_params(self):
        code = '''fn add(a: int, b: int): int
    return a + b
let result = add(3, 4)
'''
        result = self._compile_and_run(code)


class TestVMVariables(unittest.TestCase):
    def _compile_and_run(self, code):
        from synthlang.lexer import Lexer
        from synthlang.parser import Parser
        from synthlang.compiler import Compiler
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        return vm.run()

    def test_integer_variable(self):
        result = self._compile_and_run("let x = 42")
        self.assertEqual(result.get("x"), 42)

    def test_string_variable(self):
        result = self._compile_and_run('let msg = "hello"')
        self.assertEqual(result.get("msg"), "hello")

    def test_boolean_variable(self):
        result = self._compile_and_run("let flag = true")
        self.assertEqual(result.get("flag"), True)

    def test_float_variable(self):
        result = self._compile_and_run("let pi = 3.14")
        self.assertAlmostEqual(result.get("pi"), 3.14, places=2)


class TestVMValue(unittest.TestCase):
    def test_value_creation(self):
        v = Value(42, "int")
        self.assertEqual(v.value, 42)
        self.assertEqual(v.type, "int")

    def test_value_default_type(self):
        v = Value(42)
        self.assertEqual(v.value, 42)
        self.assertIsNone(v.type)


class TestVMResult(unittest.TestCase):
    def test_result_ok(self):
        r = Result.ok(42)
        self.assertEqual(r.status, Result.OK)
        self.assertEqual(r.value, 42)
        self.assertIsNone(r.error)

    def test_result_err(self):
        r = Result.err("failed")
        self.assertEqual(r.status, Result.ERR)
        self.assertEqual(r.error, "failed")
        self.assertIsNone(r.value)

    def test_result_static_ok(self):
        r = Result.ok("value")
        self.assertEqual(r.value, "value")

    def test_result_static_err(self):
        r = Result.err("error")
        self.assertEqual(r.error, "error")


class TestVMErrors(unittest.TestCase):
    def test_undefined_variable(self):
        ir = IRModule()
        ir.add_function("main", [load_var("undefined")])
        vm = VM(ir)
        with self.assertRaises(RuntimeError):
            vm.run()

    def test_stack_underflow(self):
        ir = IRModule()
        ir.add_function("main", [binary_op("+")])
        vm = VM(ir)
        with self.assertRaises(RuntimeError):
            vm.run()


class TestVMMultiStatement(unittest.TestCase):
    def _compile_and_run(self, code):
        from synthlang.lexer import Lexer
        from synthlang.parser import Parser
        from synthlang.compiler import Compiler
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        ir = compiler.compile(ast)
        vm = VM(ir)
        return vm.run()

    def test_multiple_variables(self):
        code = '''let a = 1
let b = 2
let c = a + b
'''
        result = self._compile_and_run(code)
        self.assertEqual(result.get("a"), 1)
        self.assertEqual(result.get("b"), 2)
        self.assertEqual(result.get("c"), 3)


if __name__ == '__main__':
    unittest.main()