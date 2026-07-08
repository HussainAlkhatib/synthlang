#!/usr/bin/env python3
"""Test garbage collection - GC and reference counting."""
import unittest
from synthlang.gc import GC, RefCounted, RCManager
from synthlang.vm import VM
from synthlang.ir import IRModule, load_const, store_var


class TestRefCounted(unittest.TestCase):
    def test_create_refcounted(self):
        obj = RefCounted(42)
        self.assertEqual(obj.ref_count, 1)
        self.assertEqual(obj.value, 42)

    def test_add_ref(self):
        obj = RefCounted(42)
        obj.add_ref()
        self.assertEqual(obj.ref_count, 2)

    def test_release(self):
        obj = RefCounted(42)
        obj.add_ref()
        released = obj.release()
        self.assertEqual(obj.ref_count, 1)
        self.assertFalse(released)

    def test_release_last_ref(self):
        obj = RefCounted(42)
        released = obj.release()
        self.assertEqual(obj.ref_count, 0)
        self.assertTrue(released)


class TestRCManager(unittest.TestCase):
    def test_create(self):
        manager = RCManager()
        obj = manager.create("obj1", 42)
        self.assertIsNotNone(obj)

    def test_increment(self):
        manager = RCManager()
        manager.create("obj1", 42)
        manager.increment("obj1")
        self.assertEqual(manager.objects["obj1"].ref_count, 2)

    def test_decrement(self):
        manager = RCManager()
        manager.create("obj1", 42)
        manager.increment("obj1")
        result = manager.decrement("obj1")
        self.assertFalse(result)

    def test_decrement_to_zero(self):
        manager = RCManager()
        manager.create("obj1", 42)
        result = manager.decrement("obj1")
        self.assertTrue(result)
        self.assertNotIn("obj1", manager.objects)

    def test_get(self):
        manager = RCManager()
        manager.create("obj1", 42)
        value = manager.get("obj1")
        self.assertEqual(value, 42)

    def test_get_not_found(self):
        manager = RCManager()
        value = manager.get("missing")
        self.assertIsNone(value)


class TestGC(unittest.TestCase):
    def test_gc_creation(self):
        vm = VM(IRModule())
        gc = GC(vm)
        self.assertIsNotNone(gc)

    def test_collect_with_roots(self):
        vm = VM(IRModule())
        vm.variables = {"a": 1, "b": 2, "c": 3}
        gc = GC(vm)
        gc.collect("a", "b")
        self.assertIn("a", vm.variables)
        self.assertIn("b", vm.variables)

    def test_mark_dict(self):
        vm = VM(IRModule())
        gc = GC(vm)
        visited = set()
        gc.mark({"key": "value"}, visited)
        self.assertTrue(len(visited) > 0)

    def test_mark_list(self):
        vm = VM(IRModule())
        gc = GC(vm)
        visited = set()
        gc.mark([1, 2, 3], visited)
        self.assertTrue(len(visited) > 0)


class TestGCMemory(unittest.TestCase):
    def test_vm_gc_integration(self):
        ir = IRModule()
        ir.add_function("main", [
            load_const(100),
            store_var("x"),
        ])
        vm = VM(ir)
        result = vm.run()
        self.assertEqual(result.get("x"), 100)


if __name__ == '__main__':
    unittest.main()