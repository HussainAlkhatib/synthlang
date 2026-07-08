#!/usr/bin/env python3
"""Test runner - discovers and runs all tests, generates coverage report."""
import unittest
import os
import sys
from io import StringIO
from pathlib import Path


def run_all_tests():
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


def generate_report(result, output_path="TEST_REPORT.md"):
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    report = f"""# SynthLang Test Report

## Summary
- Total tests: {total}
- Passed: {passed}
- Failed: {failures}
- Errors: {errors}
- Success rate: {(passed/total*100) if total > 0 else 0:.1f}%

## Test Results

"""
    if result.failures:
        report += "### Failures\n"
        for test, traceback in result.failures:
            report += f"- **{test}**: {traceback[:200]}...\n"

    if result.errors:
        report += "### Errors\n"
        for test, traceback in result.errors:
            report += f"- **{test}**: {traceback[:200]}...\n"

    Path(output_path).write_text(report)
    print(f"Report written to {output_path}")


if __name__ == '__main__':
    result = run_all_tests()
    generate_report(result)
    sys.exit(0 if result.wasSuccessful() else 1)