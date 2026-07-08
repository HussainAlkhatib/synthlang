"""Tests for FFI integration with all 20 languages."""
import pytest
from synthlang.lexer import Lexer
from synthlang.parser import Parser
from synthlang.compiler import Compiler
from synthlang.vm import VM

def test_cpp_ffi_syntax():
    code = '''@cpp module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('cpp', 'test')

def test_kotlin_ffi_syntax():
    code = '''@kotlin module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('kotlin', 'test')

def test_swift_ffi_syntax():
    code = '''@swift module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('swift', 'test')

def test_php_ffi_syntax():
    code = '''@php module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('php', 'test')

def test_ruby_ffi_syntax():
    code = '''@ruby module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('ruby', 'test')

def test_java_ffi_syntax():
    code = '''@java module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('java', 'test')

def test_csharp_ffi_syntax():
    code = '''@csharp module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('csharp', 'test')

def test_lua_ffi_syntax():
    code = '''@lua module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('lua', 'test')

def test_r_ffi_syntax():
    code = '''@r module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('r', 'test')

def test_julia_ffi_syntax():
    code = '''@julia module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('julia', 'test')

def test_haskell_ffi_syntax():
    code = '''@haskell module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('haskell', 'test')

def test_elixir_ffi_syntax():
    code = '''@elixir module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('elixir', 'test')

def test_dart_ffi_syntax():
    code = '''@dart module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('dart', 'test')

def test_zig_ffi_syntax():
    code = '''@zig module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('zig', 'test')

def test_typescript_ffi_syntax():
    code = '''@typescript module "test" as test'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    assert ir.imports.get('test') == ('typescript', 'test')