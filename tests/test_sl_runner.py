#!/usr/bin/env python3
"""Run all .sl test files in test-sl/ directory."""
import unittest
import os
import sys
from pathlib import Path
from synthlang.evaluator import evaluate

class TestSLFile(unittest.TestCase):
    def run_sl_test(self, filepath):
        code = Path(filepath).read_text()
        try:
            result = evaluate(code)
            return result, None
        except Exception as e:
            return None, str(e)

def discover_and_run_sl_tests():
    test_dir = Path("test-sl")
    if not test_dir.exists():
        print("test-sl directory not found")
        return
    
    loader = unittest.TestLoader()
    suite = loader.discover("test-sl", pattern="*.sl")
    
    # Convert discovery failures to runs
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result

def run_sl_file(filepath):
    code = Path(filepath).read_text()
    try:
        result = evaluate(code)
        print(f"PASS: {filepath}")
        return True
    except Exception as e:
        print(f"FAIL: {filepath}")
        print(f"  Error: {e}")
        return False

def main():
    test_dir = Path("test-sl")
    if not test_dir.exists():
        print("test-sl directory not found")
        return
    
    sl_files = list(test_dir.glob("**/*.sl"))
    passed = 0
    failed = 0
    
    for filepath in sl_files:
        if run_sl_file(filepath):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(sl_files)} tests")
    
    if failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()