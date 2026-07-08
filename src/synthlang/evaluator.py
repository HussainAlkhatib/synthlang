"""SynthLang Evaluator - slang eval implementation."""
from typing import Any
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler
from .vm import VM

# Try to import Rust core for performance
try:
    import synthlang_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    synthlang_core = None


def evaluate(code: str, use_python: bool = False) -> Any:
    if not use_python and RUST_AVAILABLE:
        try:
            result = synthlang_core.execute(code, False)
            return dict(result)
        except Exception:
            pass
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    vm = VM(ir)
    for as_name, (language, module_path) in ir.imports.items():
        vm._handle_ffi_import(language, module_path, as_name)
    return vm.run()


def eval_main(code: str) -> Any:
    if not code.strip():
        return None
    try:
        result = evaluate(code)
        return result
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    result = evaluate("let x = 5; print(x)")
    print(result)