"""Tests for code formatter."""
import unittest
from synthlang.formatter import Formatter


class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = Formatter()

    def test_format_variable(self):
        code = 'let x=5'
        result = self.formatter.format(code)
        self.assertIn('let x', result)

    def test_format_function(self):
        code = '''fn add(a:int,b:int):int
return a+b'''
        result = self.formatter.format(code)
        self.assertIn('fn add', result)

    def test_format_if(self):
        code = '''if x>0:
let y=1'''
        result = self.formatter.format(code)
        self.assertIn('if', result)


if __name__ == '__main__':
    unittest.main()