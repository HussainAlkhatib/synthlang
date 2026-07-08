#!/usr/bin/env python3
"""Test IR (Intermediate Representation) generation and instructions."""
import unittest
from synthlang.ir import (
    IRType, IRInstruction, IRModule,
    load_const, load_var, store_var, call, ret,
    jump, jump_if_false, jump_if_true, loop_begin, loop_end,
    alloc, free, increment_rc, decrement_rc,
    spawn_thread, wait, yield_op, binary_op
)


class TestIRTypes(unittest.TestCase):
    def test_ir_type_values(self):
        self.assertTrue(hasattr(IRType, 'LOAD_CONST'))
        self.assertTrue(hasattr(IRType, 'STORE_VAR'))
        self.assertTrue(hasattr(IRType, 'CALL'))
        self.assertTrue(hasattr(IRType, 'RETURN'))
        self.assertTrue(hasattr(IRType, 'JUMP'))
        self.assertTrue(hasattr(IRType, 'JUMP_IF_FALSE'))
        self.assertTrue(hasattr(IRType, 'JUMP_IF_TRUE'))
        self.assertTrue(hasattr(IRType, 'LOOP_BEGIN'))
        self.assertTrue(hasattr(IRType, 'LOOP_END'))
        self.assertTrue(hasattr(IRType, 'ALLOC'))
        self.assertTrue(hasattr(IRType, 'FREE'))
        self.assertTrue(hasattr(IRType, 'INCREMENT_RC'))
        self.assertTrue(hasattr(IRType, 'DECREMENT_RC'))
        self.assertTrue(hasattr(IRType, 'SPAWN_THREAD'))
        self.assertTrue(hasattr(IRType, 'WAIT'))
        self.assertTrue(hasattr(IRType, 'BINARY_OP'))


class TestIRInstruction(unittest.TestCase):
    def test_instruction_creation(self):
        instr = IRInstruction(IRType.LOAD_CONST, operand=42)
        self.assertEqual(instr.type, IRType.LOAD_CONST)
        self.assertEqual(instr.operand, 42)

    def test_instruction_with_result(self):
        instr = IRInstruction(IRType.LOAD_CONST, operand=42, result="x")
        self.assertEqual(instr.result, "x")

    def test_instruction_repr(self):
        instr = IRInstruction(IRType.LOAD_CONST, operand=42)
        repr_str = repr(instr)
        self.assertIn("LOAD_CONST", repr_str)


class TestIRModule(unittest.TestCase):
    def test_module_creation(self):
        module = IRModule("test_module")
        self.assertEqual(module.name, "test_module")

    def test_module_default_name(self):
        module = IRModule()
        self.assertEqual(module.name, "main")

    def test_add_function(self):
        module = IRModule()
        module.add_function("foo", [IRInstruction(IRType.NOP)])
        self.assertIn("foo", module.functions)
        self.assertEqual(len(module.functions["foo"]), 1)

    def test_add_variable(self):
        module = IRModule()
        module.add_variable("x", "int")
        self.assertEqual(module.variables["x"], "int")

    def test_func_params(self):
        module = IRModule()
        self.assertIsInstance(module.func_params, dict)


class TestIRUtilityFunctions(unittest.TestCase):
    def test_load_const(self):
        instr = load_const(42)
        self.assertEqual(instr.type, IRType.LOAD_CONST)
        self.assertEqual(instr.operand, 42)

    def test_load_var(self):
        instr = load_var("x")
        self.assertEqual(instr.type, IRType.LOAD_VAR)
        self.assertEqual(instr.operand, "x")

    def test_store_var(self):
        instr = store_var("y")
        self.assertEqual(instr.type, IRType.STORE_VAR)
        self.assertEqual(instr.operand, "y")

    def test_call(self):
        instr = call("foo", [1, 2, 3])
        self.assertEqual(instr.type, IRType.CALL)
        self.assertEqual(instr.operand, "foo")
        self.assertEqual(instr.arg1, [1, 2, 3])

    def test_ret(self):
        instr = ret()
        self.assertEqual(instr.type, IRType.RETURN)

    def test_jump(self):
        instr = jump("L1")
        self.assertEqual(instr.type, IRType.JUMP)
        self.assertEqual(instr.operand, "L1")

    def test_jump_if_false(self):
        instr = jump_if_false("L2")
        self.assertEqual(instr.type, IRType.JUMP_IF_FALSE)
        self.assertEqual(instr.operand, "L2")

    def test_jump_if_true(self):
        instr = jump_if_true("L3")
        self.assertEqual(instr.type, IRType.JUMP_IF_TRUE)
        self.assertEqual(instr.operand, "L3")

    def test_loop_begin(self):
        instr = loop_begin("loop_start")
        self.assertEqual(instr.type, IRType.LOOP_BEGIN)

    def test_loop_end(self):
        instr = loop_end("loop_end")
        self.assertEqual(instr.type, IRType.LOOP_END)

    def test_alloc(self):
        instr = alloc("buffer")
        self.assertEqual(instr.type, IRType.ALLOC)
        self.assertEqual(instr.operand, "buffer")

    def test_free(self):
        instr = free("buffer")
        self.assertEqual(instr.type, IRType.FREE)
        self.assertEqual(instr.operand, "buffer")

    def test_increment_rc(self):
        instr = increment_rc("obj")
        self.assertEqual(instr.type, IRType.INCREMENT_RC)

    def test_decrement_rc(self):
        instr = decrement_rc("obj")
        self.assertEqual(instr.type, IRType.DECREMENT_RC)

    def test_spawn_thread(self):
        instr = spawn_thread("task", [1, 2])
        self.assertEqual(instr.type, IRType.SPAWN_THREAD)

    def test_wait(self):
        instr = wait(42)
        self.assertEqual(instr.type, IRType.WAIT)
        self.assertEqual(instr.operand, 42)

    def test_yield_op(self):
        instr = yield_op()
        self.assertEqual(instr.type, IRType.YIELD)

    def test_binary_op(self):
        instr = binary_op("+")
        self.assertEqual(instr.type, IRType.BINARY_OP)
        self.assertEqual(instr.operand, "+")


class TestIRInstructionCombinations(unittest.TestCase):
    def test_simple_sequence(self):
        module = IRModule()
        module.add_function("main", [
            load_const(5),
            store_var("x"),
            load_var("x"),
            ret()
        ])
        self.assertEqual(len(module.functions["main"]), 4)

    def test_nested_instructions(self):
        module = IRModule()
        module.add_function("add", [
            load_const(1),
            load_const(2),
            binary_op("+"),
            ret()
        ])
        self.assertEqual(module.functions["add"][2].operand, "+")


if __name__ == '__main__':
    unittest.main()