use logos::Logos;
use crate::token::{Token, TokenType};

#[derive(Logos, Debug, Clone, PartialEq)]
pub enum LexerToken {
    #[regex(r"[ \t]+", logos::skip)]
    __Error,
}

pub struct Lexer {
    source: String,
    pos: usize,
    line: usize,
    column: usize,
    tokens: Vec<Token>,
    indent_stack: Vec<usize>,
}

impl Lexer {
    pub fn new(source: &str) -> Self {
        Lexer {
            source: source.to_string(),
            pos: 0,
            line: 1,
            column: 1,
            tokens: Vec::new(),
            indent_stack: vec![0],
        }
    }

    pub fn tokenize(&mut self) -> Vec<Token> {
        while self.pos < self.source.len() {
            // Basic tokenization - consume characters
            self.pos += 1;
        }
        self.tokens.push(Token { ty: TokenType::EOF, value: String::new(), line: self.line, column: self.column });
        self.tokens.clone()
    }
}