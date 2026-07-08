use crate::token::{Token, TokenType};

#[derive(Debug, Clone)]
pub enum NodeType {
    MODULE, FUNCTION, VARIABLE, ASSIGNMENT, IF, ELIF, ELSE, FOR, WHILE,
    RETURN, EXPRESSION, FFI_CALL, LOAD_VAR, MATCH, CASE, DEFER, TRY,
}

#[derive(Debug, Clone)]
pub struct ASTNode {
    pub ty: NodeType,
    pub value: Option<String>,
    pub children: Vec<ASTNode>,
}

pub struct Parser {
    tokens: Vec<Token>,
    pos: usize,
    current_token: Option<Token>,
}

impl Parser {
    pub fn new(tokens: Vec<Token>, _source: &str) -> Self {
        let mut parser = Parser { tokens, pos: 0, current_token: None };
        parser.advance();
        parser
    }

    fn advance(&mut self) {
        if self.pos < self.tokens.len() { self.current_token = Some(self.tokens[self.pos].clone()); self.pos += 1; }
        else { self.current_token = None; }
    }

    pub fn parse(&mut self) -> Vec<ASTNode> {
        let mut nodes = Vec::new();
        while self.current_token.is_some() && self.current_token.as_ref().unwrap().ty != TokenType::EOF {
            let node = self.parse_statement();
            if node.is_some() { nodes.push(node.unwrap()); }
        }
        nodes
    }

    fn parse_statement(&mut self) -> Option<ASTNode> { None }
}