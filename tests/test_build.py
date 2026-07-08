#!/usr/bin/env python3
"""Test build functionality."""
import unittest
import tempfile
from pathlib import Path


class TestBuild(unittest.TestCase):
    def test_build_function_exists(self):
        from synthlang.cli import cmd_build
        self.assertTrue(callable(cmd_build))

    def test_temp_build_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            build_dir = Path(tmpdir) / "build"
            build_dir.mkdir(parents=True, exist_ok=True)
            self.assertTrue(build_dir.exists())

    def test_project_structure_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "myproject"
            project_dir.mkdir()
            (project_dir / "main.sl").write_text('print("hello")\n')
            self.assertTrue((project_dir / "main.sl").exists())


if __name__ == '__main__':
    unittest.main()