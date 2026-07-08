# SynthLang package
from .lexer import Lexer
from .parser import Parser, ASTNode
from .compiler import Compiler
from .vm import VM
from .ir import IRModule
from .type_system import Type, TypeKind, TypeInferer
from .gc import GC, RCManager, RefCounted
from .scheduler import Scheduler, Task, TaskStatus
from .ffi import FFILoader
from .dependency import DependencyManager, Manifest, init_project
from .evaluator import evaluate
from .formatter import Formatter, format_file, format_directory
from .tester import TestRunner

# Try to import Rust core for performance
try:
    import synthlang_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    synthlang_core = None

__version__ = "1.0.0"
__all__ = [
    'Lexer', 'Parser', 'ASTNode', 'Compiler', 'VM', 'IRModule',
    'Type', 'TypeKind', 'TypeInferer',
    'GC', 'RCManager', 'RefCounted',
    'Scheduler', 'Task', 'TaskStatus',
    'FFILoader',
    'DependencyManager', 'Manifest', 'init_project',
    'evaluate',
    'Formatter', 'format_file', 'format_directory',
    'TestRunner',
    'RUST_AVAILABLE', 'synthlang_core'
]