use synthish_lang::*;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tokenize_basic() {
        let source = r#"let x = 5"#;
        let mut lexer = Lexer::new(source);
        let tokens = lexer.tokenize();
        assert!(!tokens.is_empty());
    }

    #[test]
    fn test_parse_variable() {
        let source = r#"let x: int = 5"#;
        let mut lexer = Lexer::new(source);
        let tokens = lexer.tokenize();
        let mut parser = Parser::new(tokens, source);
        let ast = parser.parse();
        assert!(!ast.is_empty());
    }

    #[test]
    fn test_compile_function() {
        let source = r#"fn add(a: int, b: int): int
    return a + b"#;
        let mut lexer = Lexer::new(source);
        let tokens = lexer.tokenize();
        let mut parser = Parser::new(tokens, source);
        let ast = parser.parse();
        let mut compiler = Compiler::new();
        let ir = compiler.compile(ast);
        assert!(ir.functions.contains_key("add"));
    }

    #[test]
    fn test_exec_hello() {
        let source = r#"fn main():
    print("Hello")"#;
        let mut lexer = Lexer::new(source);
        let tokens = lexer.tokenize();
        let mut parser = Parser::new(tokens, source);
        let ast = parser.parse();
        let mut compiler = Compiler::new();
        let ir = compiler.compile(ast);
        let mut vm = VM::new(ir, false);
        vm.run();
    }

    #[test]
    fn test_inline_python() {
        let source = r#"<py>
x = 1 + 1
x
</py>"#;
        let mut lexer = Lexer::new(source);
        let tokens = lexer.tokenize();
        let mut parser = Parser::new(tokens, source);
        let ast = parser.parse();
        let mut compiler = Compiler::new();
        let ir = compiler.compile(ast);
        assert!(ir.functions.contains_key("main"));
    }

    #[test]
    fn test_match_statement() {
        let source = r#"match x:
    case 1:
        print("One")
    case _:
        print("Other")"#;
        let mut lexer = Lexer::new(source);
        let tokens = lexer.tokenize();
        let mut parser = Parser::new(tokens, source);
        let ast = parser.parse();
        let mut compiler = Compiler::new();
        let ir = compiler.compile(ast);
        assert!(ir.functions.contains_key("main"));
    }

    #[test]
    fn test_defer_statement() {
        let source = r#"defer print("cleanup")"#;
        let mut lexer = Lexer::new(source);
        let tokens = lexer.tokenize();
        let mut parser = Parser::new(tokens, source);
        let ast = parser.parse();
        let mut compiler = Compiler::new();
        let ir = compiler.compile(ast);
        assert!(ir.functions.contains_key("main"));
    }
}