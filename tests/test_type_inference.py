"""Tests for type inference system."""
import unittest
from synthlang.type_system import Type, TypeKind, TypeInferer, PRIMITIVE_TYPES


class TestTypeInference(unittest.TestCase):
    def setUp(self):
        self.inferer = TypeInferer()

    def test_primitive_types(self):
        self.assertEqual(PRIMITIVE_TYPES['int'].kind, TypeKind.INT)
        self.assertEqual(PRIMITIVE_TYPES['float'].kind, TypeKind.FLOAT)
        self.assertEqual(PRIMITIVE_TYPES['str'].kind, TypeKind.STRING)
        self.assertEqual(PRIMITIVE_TYPES['bool'].kind, TypeKind.BOOL)

    def test_infer_literal_int(self):
        t = self.inferer.infer_literal(42)
        self.assertEqual(t.kind, TypeKind.INT)

    def test_infer_literal_float(self):
        t = self.inferer.infer_literal(3.14)
        self.assertEqual(t.kind, TypeKind.FLOAT)

    def test_infer_literal_string(self):
        t = self.inferer.infer_literal("hello")
        self.assertEqual(t.kind, TypeKind.STRING)

    def test_infer_literal_bool(self):
        t = self.inferer.infer_literal(True)
        self.assertEqual(t.kind, TypeKind.BOOL)

    def test_infer_binary_op_numeric(self):
        int_type = PRIMITIVE_TYPES['int']
        result = self.inferer.infer_binary_op(int_type, '+', int_type)
        self.assertEqual(result.kind, TypeKind.INT)

    def test_register_and_lookup(self):
        self.inferer.register_variable('x', PRIMITIVE_TYPES['int'])
        t = self.inferer.get_variable_type('x')
        self.assertEqual(t.kind, TypeKind.INT)


if __name__ == '__main__':
    unittest.main()