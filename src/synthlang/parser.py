"""SynthLang Parser - Recursive descent parser for AST generation."""
import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Any
from .lexer import Lexer, Token, TokenType


class NodeType(Enum):
    MODULE = auto()
    FUNCTION = auto()
    VARIABLE = auto()
    ASSIGNMENT = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    RETURN = auto()
    EXPRESSION = auto()
    BINARY_OP = auto()
    FFI_CALL = auto()
    FFI_GET_ATTR = auto()
    FFI_IMPORT = auto()
    FFI_IMPORT_SELECTIVE = auto()
    UNARY_OP = auto()
    CALL = auto()
    LIST = auto()
    DICT = auto()
    BLOCK = auto()
    LOAD_VAR = auto()
    IMPORT = auto()


@dataclass
class Annotation:
    name: str
    params: List[Any] = None


@dataclass
class ASTNode:
    type: NodeType
    value: Any = None
    children: List['ASTNode'] = None
    annotations: List[Annotation] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.annotations is None:
            self.annotations = []

    def __repr__(self):
        return f"ASTNode({self.type.name}, {self.value!r})"


class ParseError(SyntaxError):
    """Enhanced parse error with expected vs found details."""
    def __init__(self, message: str, line: int, column: int, expected: str = None, found: str = None, context: str = None, source: str = None):
        self.lineno = line
        self.column = column
        self.expected = expected
        self.found = found
        self.context = context
        self.source = source
        super().__init__(message)


class Parser:
    def __init__(self, tokens: List[Token], source: str = None):
        self.tokens = tokens
        self.pos = 0
        self.current_token: Optional[Token] = None
        self.source = source or ""
        self._advance()

    def _get_line_context(self, line_num: int) -> str:
        if self.source:
            lines = self.source.split('\n')
            if line_num <= len(lines):
                return lines[line_num - 1]
        return ""

    def _advance(self):
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            self.pos += 1
        else:
            self.current_token = None

    def _expect(self, *token_types: TokenType) -> bool:
        if self.current_token and self.current_token.type in token_types:
            self._advance()
            return True
        return False

    def _expect_error(self, *token_types: TokenType):
        """Raise an error if expected token not found."""
        if self.current_token and self.current_token.type in token_types:
            return True
        
        expected = " or ".join([t.name for t in token_types])
        found = self.current_token.type.name if self.current_token else "EOF"
        found_val = f"'{self.current_token.value}'" if self.current_token and self.current_token.value else found
        line = self.current_token.line if self.current_token else 0
        column = self.current_token.column if self.current_token else 0
        
        context = self._get_line_context(line)
        caret = ' ' * (column - 1) + '^' if column > 0 else '^'
        
        raise ParseError(
            f"Expected '{expected}' at line {line}, column {column}. Found {found_val}\n"
            f"    {context}\n"
            f"    {caret}",
            line, column, expected, found_val, context, self.source
        )

    def _peek(self) -> Optional[TokenType]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos].type
        return None

    def parse(self) -> List[ASTNode]:
        nodes = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.NEWLINE:
                self._advance()
                continue
            if self.current_token.type == TokenType.DEDENT:
                self._advance()
                continue
            if self.current_token.type == TokenType.INDENT:
                self._advance()
                continue
            node = self._parse_statement()
            if node:
                nodes.append(node)
        return nodes

    def _parse_statement(self) -> Optional[ASTNode]:
        annotations = self._parse_annotations()

        if self.current_token.type == TokenType.LET or self.current_token.type == TokenType.VAR:
            return self._parse_variable_decl(annotations)
        elif self.current_token.type == TokenType.FN:
            return self._parse_function_decl(annotations)
        elif self.current_token.type == TokenType.IF:
            return self._parse_if_stmt()
        elif self.current_token.type == TokenType.FOR:
            return self._parse_for_stmt()
        elif self.current_token.type == TokenType.WHILE:
            return self._parse_while_stmt()
        elif self.current_token.type == TokenType.RETURN:
            return self._parse_return_stmt()
        elif self.current_token.type == TokenType.ANNOT_MODULE:
            return self._parse_module_import(annotations)
        elif self.current_token.type == TokenType.IDENTIFIER:
            return self._parse_assignment_or_expression()
        else:
            if self.current_token:
                context = self._get_line_context(self.current_token.line)
                caret = ' ' * (self.current_token.column - 1) + '^' if self.current_token.column > 0 else '^'
                raise ParseError(
                    f"Unexpected token {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}\n"
                    f"    {context}\n"
                    f"    {caret}",
                    self.current_token.line, self.current_token.column, None, self.current_token.type.name, context, self.source
                )
            return None

    def _parse_annotations(self) -> List[Annotation]:
        annotations = []
        while self.current_token and self.current_token.type in (
            TokenType.ANNOT_MANUAL, TokenType.ANNOT_RC, TokenType.ANNOT_SYSTEM_THREAD,
            TokenType.ANNOT_EVENT_LOOP, TokenType.ANNOT_INLINE_ASM, TokenType.ANNOT_RUST,
            TokenType.ANNOT_GO_LANG, TokenType.ANNOT_C, TokenType.ANNOT_JAVA,
            TokenType.ANNOT_PYTHON, TokenType.ANNOT_JAVASCRIPT, TokenType.ANNOT_WEB,
            TokenType.ANNOT_MOBILE, TokenType.ANNOT_CLI, TokenType.ANNOT_DESKTOP,
        ):
            name = self.current_token.value[1:]
            annotations.append(Annotation(name=name))
            self._advance()
        # Skip NEWLINE after annotations
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self._advance()
        return annotations

    def _parse_variable_decl(self, annotations: List[Annotation]) -> ASTNode:
        var_type = self.current_token.type  # LET or VAR
        self._advance()  # consume let/var
        name_tok = self.current_token
        self._advance()  # consume identifier

        type_annotation = None
        if self._expect(TokenType.COLON):
            type_tok = self.current_token
            type_annotation = type_tok.value
            self._advance()

        if not self._expect(TokenType.ASSIGN):
            context = self._get_line_context(name_tok.line)
            caret = ' ' * (name_tok.column - 1) + '^' if name_tok.column > 0 else '^'
            raise ParseError(
                f"Expected '=' after variable declaration at line {name_tok.line}, column {name_tok.column}\n"
                f"    {context}\n"
                f"    {caret}",
                name_tok.line, name_tok.column, "=", None, context, self.source
            )

        expr = self._parse_expression()

        node = ASTNode(NodeType.VARIABLE, value={'name': name_tok.value, 'type': type_annotation, 'kind': var_type.name.lower()})
        node.children = [expr]
        node.annotations = annotations
        return node

    def _parse_function_decl(self, annotations: List[Annotation]) -> ASTNode:
        self._advance()  # consume fn
        name_tok = self.current_token
        self._advance()

        if not self._expect(TokenType.LPAREN):
            context = self._get_line_context(name_tok.line)
            caret = ' ' * (name_tok.column - 1) + '^' if name_tok.column > 0 else '^'
            raise ParseError(
                f"Expected '(' after function name at line {name_tok.line}, column {name_tok.column}\n"
                f"    {context}\n"
                f"    {caret}",
                name_tok.line, name_tok.column, "(", None, context, self.source
            )

        params = []
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            if self.current_token.type == TokenType.COMMA:
                self._advance()
                continue
            param_name = self.current_token.value
            self._advance()
            param_type = None
            if self._expect(TokenType.COLON):
                param_type = self.current_token.value
                self._advance()
            params.append({'name': param_name, 'type': param_type})

        if not self._expect(TokenType.RPAREN):
            context = self._get_line_context(name_tok.line)
            raise ParseError(
                f"Expected ')' after function parameters at line {name_tok.line}\n"
                f"    {context}",
                name_tok.line, 0, ")", None, context, self.source
            )

        return_type = None
        if self._expect(TokenType.COLON):
            if self.current_token and self.current_token.type not in (TokenType.NEWLINE, TokenType.LBRACE):
                return_type = self.current_token.value
                self._advance()
            if not self._expect(TokenType.NEWLINE) and not self._expect(TokenType.LBRACE):
                if self.current_token and self.current_token.type != TokenType.EOF:
                    pass

        body = []
        while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
            if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self._advance()

        node = ASTNode(NodeType.FUNCTION, value={'name': name_tok.value, 'params': params, 'return_type': return_type})
        node.children = body
        node.annotations = annotations
        return node

    def _parse_module_import(self, annotations: List[Annotation]) -> ASTNode:
        if not annotations:
            raise ParseError(
                "'module' keyword must be preceded by a language annotation (@python, @javascript, etc.)",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                "@python, @javascript, etc.", "module", None, self.source
            )
        
        lang_annot = annotations[0].name if annotations else None
        
        self._advance()  # consume module
        
        if self.current_token.type != TokenType.STRING:
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected module name string after 'module'\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                "string", "module", context, self.source
            )
        
        module_path = self.current_token.value
        self._advance()  # consume STRING
        
        as_name = None
        imports = []
        
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.value == 'import':
            self._advance()  # consume 'import'
            imports.append(self.current_token.value)
            self._advance()
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self._advance()
                imports.append(self.current_token.value)
                self._advance()
            # Selective import node
            node = ASTNode(NodeType.FFI_IMPORT_SELECTIVE, value={'language': lang_annot, 'module': module_path, 'imports': imports})
            return node
        
        if self.current_token and self.current_token.type == TokenType.AS:
            self._advance()  # consume 'as'
            as_name = self.current_token.value
            self._advance()
        
        node = ASTNode(NodeType.IMPORT, value={'language': lang_annot, 'module': module_path, 'as': as_name or module_path.split('.')[-1].replace('/', '_').replace('-', '_')})
        return node

    def _parse_if_stmt(self) -> ASTNode:
        self._advance()  # consume if
        condition = self._parse_expression()

        if not self._expect(TokenType.COLON):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected ':' after if condition\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                ":", "expression", context, self.source
            )

        if not self._expect(TokenType.NEWLINE):
            pass

        then_branch = []
        while self.current_token and self.current_token.type not in (TokenType.ELSE, TokenType.ELIF, TokenType.EOF):
            if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                then_branch.append(stmt)

        elif_branches = []
        else_branch = []

        while self.current_token and self.current_token.type in (TokenType.ELIF, TokenType.ELSE):
            if self.current_token.type == TokenType.ELIF:
                self._advance()  # consume elif
                elif_cond = self._parse_expression()
                if not self._expect(TokenType.COLON):
                    context = self._get_line_context(self.current_token.line if self.current_token else 0)
                    raise ParseError(
                        "Expected ':' after elif condition\n"
                        f"    {context}",
                        self.current_token.line if self.current_token else 0,
                        self.current_token.column if self.current_token else 0,
                        ":", "expression", context, self.source
                    )
                if not self._expect(TokenType.NEWLINE):
                    pass
                elif_body = []
                while self.current_token and self.current_token.type not in (TokenType.ELSE, TokenType.ELIF, TokenType.EOF):
                    if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                        self._advance()
                        continue
                    stmt = self._parse_statement()
                    if stmt:
                        elif_body.append(stmt)
                elif_branches.append((elif_cond, ASTNode(NodeType.BLOCK, children=elif_body)))
            else:
                self._advance()  # consume else
                if not self._expect(TokenType.COLON):
                    context = self._get_line_context(self.current_token.line if self.current_token else 0)
                    raise ParseError(
                        "Expected ':' after else\n"
                        f"    {context}",
                        self.current_token.line if self.current_token else 0,
                        self.current_token.column if self.current_token else 0,
                        ":", "else", context, self.source
                    )
                if not self._expect(TokenType.NEWLINE):
                    pass
                while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
                    if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                        self._advance()
                        continue
                    stmt = self._parse_statement()
                    if stmt:
                        else_branch.append(stmt)

        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self._advance()

        node = ASTNode(NodeType.IF, value=None)
        node.children = [condition, ASTNode(NodeType.BLOCK, children=then_branch)]
        # Store elif branches with their conditions
        for cond, body in elif_branches:
            node.children.append(cond)
            node.children.append(body)
        if else_branch:
            node.children.append(ASTNode(NodeType.BLOCK, children=else_branch))
        return node

    def _parse_for_stmt(self) -> ASTNode:
        self._advance()  # consume for
        var_name = self.current_token.value
        self._advance()  # advance past identifier

        if not self._expect(TokenType.IN):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected 'in' in for loop\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                "in", None, context, self.source
            )

        iterable = self._parse_expression()

        if not self._expect(TokenType.COLON):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected ':' after for loop declaration\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                ":", None, context, self.source
            )

        if not self._expect(TokenType.NEWLINE):
            pass

        body = []
        while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
            if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self._advance()

        node = ASTNode(NodeType.FOR, value={'var': var_name})
        node.children = [iterable, ASTNode(NodeType.BLOCK, children=body)]
        return node

    def _parse_while_stmt(self) -> Optional[ASTNode]:
        self._advance()
        condition = self._parse_expression()
        if self._expect(TokenType.COLON):
            pass
        body = []
        while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
            if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self._advance()
        return ASTNode(NodeType.WHILE, value=None, children=[condition, ASTNode(NodeType.BLOCK, children=body)])

    def _parse_return_stmt(self) -> Optional[ASTNode]:
        self._advance()
        if self.current_token and self.current_token.type != TokenType.NEWLINE:
            expr = self._parse_expression()
        else:
            expr = ASTNode(NodeType.EXPRESSION, value=None)
        return ASTNode(NodeType.RETURN, children=[expr])

    def _parse_expression(self) -> ASTNode:
        return self._parse_logical_or()

    def _parse_logical_or(self) -> ASTNode:
        left = self._parse_logical_and()
        while self.current_token and self.current_token.type == TokenType.OROR:
            op = self.current_token.value
            self._advance()
            right = self._parse_logical_and()
            left = ASTNode(NodeType.BINARY_OP, value=op, children=[left, right])
        return left

    def _parse_logical_and(self) -> ASTNode:
        left = self._parse_equality()
        while self.current_token and self.current_token.type == TokenType.ANDAND:
            op = self.current_token.value
            self._advance()
            right = self._parse_equality()
            left = ASTNode(NodeType.BINARY_OP, value=op, children=[left, right])
        return left

    def _parse_equality(self) -> ASTNode:
        left = self._parse_comparison()
        while self.current_token and self.current_token.type in (TokenType.EQ, TokenType.NE):
            op = self.current_token.value
            self._advance()
            right = self._parse_comparison()
            left = ASTNode(NodeType.BINARY_OP, value=op, children=[left, right])
        return left

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_term()
        while self.current_token and self.current_token.type in (TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.IN):
            op = self.current_token.value
            self._advance()
            right = self._parse_term()
            left = ASTNode(NodeType.BINARY_OP, value=op, children=[left, right])
        return left

    def _parse_term(self) -> ASTNode:
        left = self._parse_factor()
        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self._advance()
            right = self._parse_factor()
            left = ASTNode(NodeType.BINARY_OP, value=op, children=[left, right])
        return left

    def _parse_factor(self) -> ASTNode:
        left = self._parse_unary()
        while self.current_token and self.current_token.type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.current_token.value
            self._advance()
            right = self._parse_unary()
            left = ASTNode(NodeType.BINARY_OP, value=op, children=[left, right])
        return left

    def _parse_unary(self) -> ASTNode:
        if self.current_token and self.current_token.type in (TokenType.MINUS, TokenType.NOT):
            op = self.current_token.value
            self._advance()
            operand = self._parse_unary()
            return ASTNode(NodeType.UNARY_OP, value=op, children=[operand])
        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        if not self.current_token:
            raise ParseError(
                "Unexpected end of input",
                0, 0, "expression", "EOF", None, self.source
            )

        tok = self.current_token

        if tok.type == TokenType.INTEGER:
            self._advance()
            return ASTNode(NodeType.EXPRESSION, value=tok.value)

        elif tok.type == TokenType.FLOAT:
            self._advance()
            return ASTNode(NodeType.EXPRESSION, value=tok.value)

        elif tok.type == TokenType.STRING:
            self._advance()
            return ASTNode(NodeType.EXPRESSION, value=tok.value)

        elif tok.type == TokenType.BOOLEAN:
            self._advance()
            return ASTNode(NodeType.EXPRESSION, value=tok.value)

        elif tok.type == TokenType.NULL:
            self._advance()
            return ASTNode(NodeType.EXPRESSION, value=None)

        elif tok.type == TokenType.NOT:  # 'not' as unary in expressions
            self._advance()
            operand = self._parse_unary()  # Parse full expression after 'not'
            return ASTNode(NodeType.UNARY_OP, value='!', children=[operand])

        elif tok.type == TokenType.IDENTIFIER:
            name = tok.value
            self._advance()

            if self.current_token and self.current_token.type == TokenType.LPAREN:
                return self._parse_call(name)
            elif self.current_token and self.current_token.type == TokenType.LBRACKET:
                return self._parse_index(name)
            elif self.current_token and self.current_token.type == TokenType.DOT:
                return self._parse_ffi_method(name)
            else:
                return ASTNode(NodeType.LOAD_VAR, value=name)

        elif tok.type == TokenType.LBRACKET:
            return self._parse_list()

        elif tok.type == TokenType.LBRACE:
            return self._parse_dict()

        elif tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            if not self._expect(TokenType.RPAREN):
                context = self._get_line_context(tok.line)
                raise ParseError(
                    "Expected ')' after parenthesized expression\n"
                    f"    {context}",
                    tok.line, tok.column, ")", None, context, self.source
                )
            return expr

        else:
            context = self._get_line_context(tok.line)
            caret = ' ' * (tok.column - 1) + '^' if tok.column > 0 else '^'
            raise ParseError(
                f"Unexpected token {tok.type} at line {tok.line}, column {tok.column}\n"
                f"    {context}\n"
                f"    {caret}",
                tok.line, tok.column, None, tok.type.name, context, self.source
            )

    def _parse_call(self, func_name: str) -> ASTNode:
        self._expect(TokenType.LPAREN)
        args = []
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            if self.current_token.type == TokenType.COMMA:
                self._advance()
                continue
            args.append(self._parse_expression())
        if not self._expect(TokenType.RPAREN):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected ')' after function call\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                ")", None, context, self.source
            )
        return ASTNode(NodeType.CALL, value=func_name, children=args)

    def _parse_index(self, name: str) -> ASTNode:
        self._expect(TokenType.LBRACKET)
        index = self._parse_expression()
        if not self._expect(TokenType.RBRACKET):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected ']' after index\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                "]", None, context, self.source
            )
        result = ASTNode(NodeType.BINARY_OP, value='[]', children=[ASTNode(NodeType.EXPRESSION, value=name), index])
        # Handle chained indexing like data[key]["cell"] or data[key].attr
        while self.current_token and self.current_token.type in (TokenType.LBRACKET, TokenType.DOT):
            if self.current_token.type == TokenType.LBRACKET:
                self._advance()
                idx = self._parse_expression()
                if not self._expect(TokenType.RBRACKET):
                    context = self._get_line_context(self.current_token.line if self.current_token else 0)
                    raise ParseError(
                        "Expected ']' after index\n"
                        f"    {context}",
                        self.current_token.line if self.current_token else 0,
                        self.current_token.column if self.current_token else 0,
                        "]", None, context, self.source
                    )
                result = ASTNode(NodeType.BINARY_OP, value='[]', children=[result, idx])
            else:  # DOT
                self._advance()
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    attr = self.current_token.value
                    self._advance()
                    result = ASTNode(NodeType.FFI_GET_ATTR, value={"module": name.split('[')[0] if '[' in name else name, "attr": attr})
        return result

    def _parse_ffi_method(self, module_name: str) -> ASTNode:
        # Handle chained FFI calls: module.method() or module.Class.method()
        # The key is that we need to track the full path but know which part is the module
        
        # First, consume DOT and get the next identifier
        self._advance()  # consume first DOT
        method_path = module_name
        
        while self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            method_path += "." + self.current_token.value
            self._advance()
            
            if self.current_token and self.current_token.type == TokenType.DOT:
                self._advance()
            else:
                break
        
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            args = []
            self._advance()  # consume LPAREN
            while self.current_token and self.current_token.type != TokenType.RPAREN:
                if self.current_token.type == TokenType.COMMA:
                    self._advance()
                    continue
                args.append(self._parse_expression())
            if not self._expect(TokenType.RPAREN):
                context = self._get_line_context(self.current_token.line if self.current_token else 0)
                raise ParseError(
                    "Expected ) after FFI method call\n"
                    f"    {context}",
                    self.current_token.line if self.current_token else 0,
                    self.current_token.column if self.current_token else 0,
                    ")", None, context, self.source
                )
            # Return the full method path - FFI loader will handle it
            return ASTNode(NodeType.FFI_CALL, value={"module": module_name, "method": method_path[len(module_name)+1:], "args": args})
        
        return ASTNode(NodeType.FFI_GET_ATTR, value={"module": module_name, "attr": method_path[len(module_name)+1:]})

    def _parse_list(self) -> ASTNode:
        elements = []
        if not self._expect(TokenType.LBRACKET):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected '[' to start list literal\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                "[", None, context, self.source
            )

        while self.current_token and self.current_token.type != TokenType.RBRACKET:
            if self.current_token.type == TokenType.COMMA:
                self._advance()
                continue
            elements.append(self._parse_expression())
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self._advance()
                continue

        if not self._expect(TokenType.RBRACKET):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected ']' to end list literal\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                "]", None, context, self.source
            )
        return ASTNode(NodeType.LIST, children=elements)

    def _parse_dict(self) -> ASTNode:
        entries = []
        if not self._expect(TokenType.LBRACE):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected '{' to start dict literal\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                "{", None, context, self.source
            )

        while self.current_token and self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.COMMA:
                self._advance()
                continue
            key = self._parse_expression()
            if not self._expect(TokenType.COLON):
                context = self._get_line_context(self.current_token.line if self.current_token else 0)
                raise ParseError(
                    "Expected ':' in dict literal\n"
                    f"    {context}",
                    self.current_token.line if self.current_token else 0,
                    self.current_token.column if self.current_token else 0,
                    ":", None, context, self.source
                )
            value = self._parse_expression()
            entries.append((key, value))

        if not self._expect(TokenType.RBRACE):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected '}' to end dict literal\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                "}", None, context, self.source
            )
        return ASTNode(NodeType.DICT, children=entries)

    def _parse_assignment_or_expression(self) -> Optional[ASTNode]:
        if self._peek() == TokenType.ASSIGN:
            name = self.current_token.value
            self._advance()  # consume identifier
            self._advance()  # consume =
            expr = self._parse_expression()
            return ASTNode(NodeType.ASSIGNMENT, value=name, children=[expr])
        return self._parse_expression()


if __name__ == '__main__':
    test_code = '''let x: int = 5
let y = 10.5

fn add(a: int, b: int): int
    return a + b

if x > 0:
    let result = x + y
'''
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, test_code)
    ast = parser.parse()
    for node in ast:
        print(node)