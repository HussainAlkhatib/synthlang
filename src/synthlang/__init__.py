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
    
    # Re-export core functions if available
    _get_lex = lambda source: synthlang_core.lex(source) if hasattr(synthlang_core, 'lex') else synthlang_core.tokenize(source)
    
    def lex(source: str):
        return _get_lex(source)
    
    def parse(source: str):
        return synthlang_core.parse(source)
    
    def compile(source: str):
        return synthlang_core.compile(source)
    
    def execute(source: str, debug: bool = False):
        return dict(synthlang_core.execute(source, debug))
except ImportError:
    RUST_AVAILABLE = False
    synthlang_core = None
    
    def lex(source: str):
        from .lexer import Lexer
        return Lexer(source).tokenize()
    
    def parse(source: str):
        from .lexer import Lexer
        from .parser import Parser
        tokens = Lexer(source).tokenize()
        return Parser(tokens, source).parse()
    
    def compile(source: str):
        from .lexer import Lexer
        from .parser import Parser
        from .compiler import Compiler
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens, source).parse()
        return dict(Compiler().compile(ast))
    
    def execute(source: str, debug: bool = False):
        from .lexer import Lexer
        from .parser import Parser
        from .compiler import Compiler
        from .vm import VM
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens, source).parse()
        ir = Compiler().compile(ast)
        return dict(VM(ir, debug=debug).run())

# Export Go FFI availability
try:
    import ctypes
    import platform
    from pathlib import Path
    
    if platform.system() == "Windows":
        go_lib_path = str(Path(__file__).parent / ("libgoffi.dll"))
    elif platform.system() == "Darwin":
        go_lib_path = str(Path(__file__).parent / ("libgoffi.dylib"))
    else:
        go_lib_path = str(Path(__file__).parent / ("libgoffi.so"))
    
    ctypes.CDLL(go_lib_path)
    GO_AVAILABLE = True
except Exception:
    GO_AVAILABLE = False

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
    'RUST_AVAILABLE', 'synthlang_core',
    'lex', 'parse', 'compile', 'execute',
    'GO_AVAILABLE',
]