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
    MATCH = auto()
    CASE = auto()
    DEFER = auto()
    TRY = auto()
    INLINE_CODE = auto()
    CHANNEL = auto()
    CHAN_SEND = auto()
    CHAN_RECV = auto()
    AWAIT = auto()
    KWARG = auto()


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
        elif self.current_token.type == TokenType.ASYNC:
            self._advance() # consume async
            if self.current_token and self.current_token.type == TokenType.FN:
                return self._parse_function_decl(annotations, is_async=True)
            else:
                raise ParseError("Expected 'fn' after 'async'", self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 0, "fn", None, "", self.source)
        elif self.current_token.type == TokenType.IF:
            return self._parse_if_stmt()
        elif self.current_token.type == TokenType.MATCH:
            return self._parse_match_stmt()
        elif self.current_token.type == TokenType.DEFER:
            return self._parse_defer_stmt()
        elif self.current_token.type == TokenType.TRY:
            return self._parse_try_stmt()
        elif self.current_token.type == TokenType.PANIC:
            return self._parse_panic_stmt()
        elif self.current_token.type == TokenType.FOR:
            return self._parse_for_stmt()
        elif self.current_token.type == TokenType.WHILE:
            return self._parse_while_stmt()
        elif self.current_token.type == TokenType.RETURN:
            return self._parse_return_stmt()
        elif self.current_token.type == TokenType.ANNOT_MODULE:
            return self._parse_module_import(annotations)
        elif self.current_token.type == TokenType.INLINE_CODE:
            return self._parse_inline_code()
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
            TokenType.ANNOT_CPP, TokenType.ANNOT_KOTLIN, TokenType.ANNOT_SWIFT,
            TokenType.ANNOT_PHP, TokenType.ANNOT_RUBY, TokenType.ANNOT_CSHARP,
            TokenType.ANNOT_LUA, TokenType.ANNOT_R, TokenType.ANNOT_JULIA,
            TokenType.ANNOT_HASKELL, TokenType.ANNOT_ELIXIR, TokenType.ANNOT_DART,
            TokenType.ANNOT_ZIG, TokenType.ANNOT_TYPESCRIPT,
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

    def _parse_function_decl(self, annotations: List[Annotation], is_async: bool = False) -> ASTNode:
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

        node = ASTNode(NodeType.FUNCTION, value={'name': name_tok.value, 'params': params, 'return_type': return_type, 'is_async': is_async})
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
        while self.current_token and self.current_token.type not in (TokenType.ELSE, TokenType.ELIF, TokenType.DEDENT, TokenType.EOF):
            if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                then_branch.append(stmt)

        # After then_branch ends on DEDENT, consume DEDENTs to find else/elif at same indent level
        # We peek: if there are DEDENTs followed by ELSE/ELIF, those DEDENTs are from nested blocks
        # and we should consume them. But if DEDENTs lead to something else, they close this if.
        saved_pos = self.pos
        saved_tok = self.current_token
        dedents_consumed = 0
        while self.current_token and self.current_token.type in (TokenType.DEDENT, TokenType.NEWLINE):
            self._advance()
            dedents_consumed += 1
        # If next token is NOT else/elif, restore position so outer scope can handle DEDENTs
        if self.current_token and self.current_token.type not in (TokenType.ELSE, TokenType.ELIF):
            self.pos = saved_pos
            self.current_token = saved_tok

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
                while self.current_token and self.current_token.type not in (TokenType.ELSE, TokenType.ELIF, TokenType.DEDENT, TokenType.EOF):
                    if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                        self._advance()
                        continue
                    stmt = self._parse_statement()
                    if stmt:
                        elif_body.append(stmt)
                # After elif_body ends on DEDENT, peek to see if there is else/elif at same level
                saved_pos2 = self.pos
                saved_tok2 = self.current_token
                while self.current_token and self.current_token.type in (TokenType.DEDENT, TokenType.NEWLINE):
                    self._advance()
                if self.current_token and self.current_token.type not in (TokenType.ELSE, TokenType.ELIF):
                    self.pos = saved_pos2
                    self.current_token = saved_tok2
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
        elif self.current_token and self.current_token.type == TokenType.AWAIT:
            self._advance()
            operand = self._parse_unary()
            return ASTNode(NodeType.AWAIT, value=None, children=[operand])
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
        kwargs = {}
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            if self.current_token.type == TokenType.COMMA:
                self._advance()
                continue
            
            if (self.current_token.type == TokenType.IDENTIFIER and 
                    self.pos < len(self.tokens) and 
                    self.tokens[self.pos].type == TokenType.ASSIGN):
                kw_name = self.current_token.value
                self._advance()  # consume identifier
                self._advance()  # consume '='
                kw_val = self._parse_expression()
                kwargs[kw_name] = kw_val
            else:
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
            
        if kwargs:
            args.append(ASTNode(NodeType.KWARG, value=kwargs))
            
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
            kwargs = {}
            self._advance()  # consume LPAREN
            while self.current_token and self.current_token.type != TokenType.RPAREN:
                if self.current_token.type == TokenType.COMMA:
                    self._advance()
                    continue
                if (self.current_token.type == TokenType.IDENTIFIER and 
                        self.pos < len(self.tokens) and 
                        self.tokens[self.pos].type == TokenType.ASSIGN):
                    kw_name = self.current_token.value
                    self._advance()  # consume identifier
                    self._advance()  # consume '='
                    kw_val = self._parse_expression()
                    kwargs[kw_name] = kw_val
                else:
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
            if kwargs:
                args.append(ASTNode(NodeType.KWARG, value=kwargs))
            # split method_path into module and method
            parts = method_path.split('.')
            module = parts[0]
            method = ".".join(parts[1:])
            return ASTNode(NodeType.FFI_CALL, value={"module": module, "method": method, "args": args})
        
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
        """Parse a simple assignment, subscript assignment, or expression statement.

        Handles:
            name = expr
            name[key] = expr
            name[key][key2] = expr
            name.attr = expr   (attribute set via FFI)
            expr (standalone call / expression)
        """
        # Simple assignment: name = expr
        if self._peek() == TokenType.ASSIGN:
            name = self.current_token.value
            self._advance()  # consume identifier
            self._advance()  # consume =
            expr = self._parse_expression()
            return ASTNode(NodeType.ASSIGNMENT, value=name, children=[expr])

        # Parse the left-hand side as an expression first
        lhs = self._parse_expression()

        # Check for assignment after subscript/attr: lhs = rhs
        if self.current_token and self.current_token.type == TokenType.ASSIGN:
            self._advance()  # consume =
            rhs = self._parse_expression()
            return ASTNode(NodeType.ASSIGN_SUBSCRIPT, value=None, children=[lhs, rhs])

        # Not an assignment — return as an expression statement
        return lhs

    def _parse_match_stmt(self) -> Optional[ASTNode]:
        """Parse a match statement with pattern matching.
        
        Syntax:
            match value:
                case pattern1:
                    statements
                case pattern2, pattern3:
                    statements
                case _:
                    statements
        """
        self._advance()  # consume match
        value_expr = self._parse_expression()
        
        if not self._expect(TokenType.COLON):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected ':' after match expression\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                ":", None, context, self.source
            )
        
        if not self._expect(TokenType.NEWLINE):
            pass
        
        cases = []
        while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
            if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                self._advance()
                continue
            
            if self.current_token and self.current_token.type == TokenType.CASE:
                self._advance()  # consume case
                
                # Parse patterns (comma-separated)
                patterns = []
                patterns.append(self._parse_expression())
                
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self._advance()  # consume comma
                    patterns.append(self._parse_expression())
                
                if not self._expect(TokenType.COLON):
                    context = self._get_line_context(self.current_token.line if self.current_token else 0)
                    raise ParseError(
                        "Expected ':' after case patterns\n"
                        f"    {context}",
                        self.current_token.line if self.current_token else 0,
                        self.current_token.column if self.current_token else 0,
                        ":", None, context, self.source
                    )
                if not self._expect(TokenType.NEWLINE):
                    pass
                
                # Parse case body
                body = []
                while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.CASE, TokenType.EOF):
                    if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                        self._advance()
                        continue
                    stmt = self._parse_statement()
                    if stmt:
                        body.append(stmt)
                
                if self.current_token and self.current_token.type == TokenType.DEDENT:
                    self._advance()
                
                cases.append((patterns, ASTNode(NodeType.BLOCK, children=body)))
        
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self._advance()
        
        node = ASTNode(NodeType.MATCH, value=None)
        node.children = [value_expr]
        for patterns, body in cases:
            for pattern in patterns:
                node.children.append(pattern)
            node.children.append(body)
        return node

    def _parse_defer_stmt(self) -> Optional[ASTNode]:
        """Parse a defer statement for deferred execution.
        
        Syntax:
            defer expression
        """
        self._advance()  # consume defer
        expr = self._parse_expression()
        return ASTNode(NodeType.DEFER, children=[expr])

    def _parse_try_stmt(self) -> Optional[ASTNode]:
        """Parse a try/handle statement for error handling.
        
        Syntax:
            try expression:
                statements
            handle error:
                statements
        """
        self._advance()  # consume try
        try_expr = self._parse_expression()
        
        if not self._expect(TokenType.COLON):
            context = self._get_line_context(self.current_token.line if self.current_token else 0)
            raise ParseError(
                "Expected ':' after try expression\n"
                f"    {context}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
                ":", None, context, self.source
            )
        if not self._expect(TokenType.NEWLINE):
            pass
        
        try_body = []
        while self.current_token and self.current_token.type not in (TokenType.HANDLE, TokenType.DEDENT, TokenType.EOF):
            if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                try_body.append(stmt)
        
        handle_error_name = "_error"
        handle_body = []
        
        if self.current_token and self.current_token.type == TokenType.HANDLE:
            self._advance()  # consume handle
            
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                handle_error_name = self.current_token.value
                self._advance()  # consume error variable name
            
            if not self._expect(TokenType.COLON):
                context = self._get_line_context(self.current_token.line if self.current_token else 0)
                raise ParseError(
                    "Expected ':' after handle clause\n"
                    f"    {context}",
                    self.current_token.line if self.current_token else 0,
                    self.current_token.column if self.current_token else 0,
                    ":", None, context, self.source
                )
            if not self._expect(TokenType.NEWLINE):
                pass
            
            while self.current_token and self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
                if self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
                    self._advance()
                    continue
                stmt = self._parse_statement()
                if stmt:
                    handle_body.append(stmt)
        
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self._advance()
        
        node = ASTNode(NodeType.TRY, value={'error_var': handle_error_name})
        node.children = [try_expr, ASTNode(NodeType.BLOCK, children=try_body), ASTNode(NodeType.BLOCK, children=handle_body)]
        return node

    def _parse_panic_stmt(self) -> ASTNode:
        self._advance()  # consume panic
        has_paren = self._expect(TokenType.LPAREN)
        expr = self._parse_expression()
        if has_paren:
            if not self._expect(TokenType.RPAREN):
                context = self._get_line_context(self.current_token.line if self.current_token else 0)
                raise ParseError("Expected ')' after panic expression", self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 0, ")", None, context, self.source)
        return ASTNode(NodeType.CALL, value="panic", children=[expr])

    def _parse_inline_code(self) -> Optional[ASTNode]:
        """Parse inline code block from another language.
        
        Syntax:
            <py>
            print("Hello from Python!")
            </py>
        """
        import json
        token_value = self.current_token.value
        code_info = json.loads(token_value)
        lang = code_info['lang']
        code = code_info['code']
        self._advance()  # consume INLINE_CODE token
        return ASTNode(NodeType.INLINE_CODE, value={'language': lang, 'code': code})


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