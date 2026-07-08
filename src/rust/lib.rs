use pyo3::prelude::*;
use std::collections::HashMap;

mod token;
mod ir;
mod lexer;
mod parser;
mod compiler;
mod vm;
mod gc;

pub use token::{Token, TokenType};
pub use ir::{IRModule, IRInstruction, IRType};

#[pyfunction]
pub fn tokenize(_py: Python, source: &str) -> PyResult<Vec<String>> {
    let mut lexer = lexer::Lexer::new(source);
    let tokens = lexer.tokenize();
    Ok(tokens.iter().map(|t| format!("{:?}:{}", t.ty, t.value)).collect())
}

#[pyfunction]
pub fn parse(_py: Python, source: &str) -> PyResult<HashMap<String, String>> {
    let mut lexer = lexer::Lexer::new(source);
    let tokens = lexer.tokenize();
    let mut parser = parser::Parser::new(tokens, source);
    let ast = parser.parse();
    let mut result = HashMap::new();
    for (i, node) in ast.iter().enumerate() {
        result.insert(format!("node_{}", i), format!("{:?}", node.ty));
    }
    Ok(result)
}

#[pyfunction]
pub fn compile(_py: Python, source: &str) -> PyResult<HashMap<String, String>> {
    let mut lexer = lexer::Lexer::new(source);
    let tokens = lexer.tokenize();
    let mut parser = parser::Parser::new(tokens, source);
    let ast = parser.parse();
    let mut compiler = compiler::Compiler::new();
    let ir = compiler.compile(ast);
    let mut result = HashMap::new();
    for (name, instrs) in &ir.functions {
        let ops: Vec<String> = instrs.iter().map(|i| format!("{:?}", i.ty)).collect();
        result.insert(name.clone(), ops.join(", "));
    }
    Ok(result)
}

#[pyfunction]
pub fn execute(_py: Python, source: &str, debug: bool) -> PyResult<HashMap<String, String>> {
    let mut lexer = lexer::Lexer::new(source);
    let tokens = lexer.tokenize();
    let mut parser = parser::Parser::new(tokens, source);
    let ast = parser.parse();
    let mut compiler = compiler::Compiler::new();
    let ir = compiler.compile(ast);
    let mut vm = vm::VM::new(ir, debug);
    Ok(vm.run())
}

#[pymodule]
fn synthlang_core(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(tokenize, m)?)?;
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(compile, m)?)?;
    m.add_function(wrap_pyfunction!(execute, m)?)?;
    Ok(())
}
