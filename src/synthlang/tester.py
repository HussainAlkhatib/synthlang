"""SynthLang Tester - slang test implementation."""
import os
import re
import sys
from typing import List, Optional, Callable
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler
from .vm import VM


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []

    def run_test(self, code: str) -> bool:
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            compiler = Compiler()
            ir = compiler.compile(ast)
            vm = VM(ir)
            vm.run()
            return True
        except Exception as e:
            self.errors.append(str(e))
            return False

    def run_file(self, filepath: str) -> bool:
        with open(filepath, 'r') as f:
            code = f.read()
        return self.run_test(code)

    def discover_tests(self, directory: str = ".") -> List[str]:
        test_files = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'venv', 'node_modules')]
            for f in files:
                if f.endswith('_test.sl') or (f.endswith('.sl') and f.startswith('test_')):
                    test_files.append(os.path.join(root, f))
        return test_files

    def run_all(self, directory: str = ".") -> tuple:
        test_files = self.discover_tests(directory)
        for tf in test_files:
            print(f"Running: {tf}")
            if self.run_file(tf):
                self.passed += 1
                print("  PASS")
            else:
                self.failed += 1
                print(f"  FAIL: {self.errors[-1] if self.errors else 'Unknown error'}")
        return self.passed, self.failed


def test_main(filepath: Optional[str] = None, directory: str = ".") -> int:
    runner = TestRunner()
    if filepath:
        if runner.run_file(f"tests/{filepath}") or runner.run_file(filepath):
            runner.passed = 1
        else:
            runner.failed = 1
    else:
        runner.run_all(directory)
    
    print(f"\nResults: {runner.passed} passed, {runner.failed} failed")
    return runner.failed


if __name__ == '__main__':
    test_main()