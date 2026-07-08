#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="synthlang",
    version="1.1.2",
    description="SynthLang - A modern polyglot programming language",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "slang=synthlang.cli:main",
        ],
    },
)