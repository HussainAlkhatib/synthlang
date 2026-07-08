#!/usr/bin/env python3
"""Test CLI commands."""
import unittest
import subprocess
import sys
from pathlib import Path


class TestCLIBasic(unittest.TestCase):
    def test_cli_module_imports(self):
        from synthlang.cli import main, run_file
        self.assertTrue(callable(main))
        self.assertTrue(callable(run_file))


class TestCLICommands(unittest.TestCase):
    def test_version_command(self):
        result = subprocess.run(
            [sys.executable, "-m", "synthlang.cli", "--version"],
            capture_output=True,
            text=True
        )
        self.assertIn("SynthLang", result.stdout)


class TestCLIHelpers(unittest.TestCase):
    def test_get_cache_path(self):
        from synthlang.cli import get_cache_path
        path = get_cache_path("test.sl")
        self.assertIsNotNone(path)


class TestCLIFile(unittest.TestCase):
    def test_run_nonexistent_file(self):
        from synthlang.cli import run_file
        with self.assertRaises(FileNotFoundError):
            run_file("/nonexistent/file.sl")


class TestCLIInit(unittest.TestCase):
    def test_init_function_exists(self):
        from synthlang.cli import cmd_init
        self.assertTrue(callable(cmd_init))


class TestCLIBuild(unittest.TestCase):
    def test_build_function_exists(self):
        from synthlang.cli import cmd_build
        self.assertTrue(callable(cmd_build))


class TestCLITest(unittest.TestCase):
    def test_test_function_exists(self):
        from synthlang.cli import cmd_test
        self.assertTrue(callable(cmd_test))


class TestCLIFmt(unittest.TestCase):
    def test_fmt_function_exists(self):
        from synthlang.cli import cmd_fmt
        self.assertTrue(callable(cmd_fmt))


class TestCLIEval(unittest.TestCase):
    def test_eval_function_exists(self):
        from synthlang.cli import cmd_eval
        self.assertTrue(callable(cmd_eval))


if __name__ == '__main__':
    unittest.main()