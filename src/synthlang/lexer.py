"""SynthLang Lexer - Tokenizes SynthLang source code."""
import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    LET = auto()
    VAR = auto()
    FN = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    IN = auto()
    RETURN = auto()
    GO = auto()
    AWAIT = auto()
    TRY = auto()
    HANDLE = auto()
    PANIC = auto()
    DEFER = auto()
    MATCH = auto()
    CASE = auto()
    AS = auto()

    ANNOT_MANUAL = auto()
    ANNOT_RC = auto()
    ANNOT_SYSTEM_THREAD = auto()
    ANNOT_EVENT_LOOP = auto()
    ANNOT_INLINE_ASM = auto()
    ANNOT_RUST = auto()
    ANNOT_GO_LANG = auto()
    ANNOT_C = auto()
    ANNOT_JAVA = auto()
    ANNOT_PYTHON = auto()
    ANNOT_JAVASCRIPT = auto()
    ANNOT_WEB = auto()
    ANNOT_MOBILE = auto()
    ANNOT_CLI = auto()
    ANNOT_DESKTOP = auto()
    ANNOT_MODULE = auto()
    ANNOT_CPP = auto()
    ANNOT_KOTLIN = auto()
    ANNOT_SWIFT = auto()
    ANNOT_PHP = auto()
    ANNOT_RUBY = auto()
    ANNOT_CSHARP = auto()
    ANNOT_LUA = auto()
    ANNOT_R = auto()
    ANNOT_JULIA = auto()
    ANNOT_HASKELL = auto()
    ANNOT_ELIXIR = auto()
    ANNOT_DART = auto()
    ANNOT_ZIG = auto()
    ANNOT_TYPESCRIPT = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    ANDAND = auto()
    OROR = auto()
    NOT = auto()
    QMARK = auto()
    COLON = auto()
    SEMI = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    DOT = auto()

    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()
    IDENTIFIER = auto()

    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        if self.type == TokenType.BOOLEAN:
            return f"Token({self.type.name}, {self.value}, line={self.line})"
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


class LexerError(SyntaxError):
    """Enhanced syntax error with line, column, and context."""
    def __init__(self, message: str, line: int, column: int, char: str = None, context: str = None):
        self.lineno = line
        self.column = column
        self.char = char
        self.context = context
        super().__init__(message)


class Lexer:
    KEYWORDS = {
        'let': TokenType.LET, 'var': TokenType.VAR, 'fn': TokenType.FN,
        'if': TokenType.IF, 'elif': TokenType.ELIF, 'else': TokenType.ELSE,
        'for': TokenType.FOR, 'while': TokenType.WHILE, 'in': TokenType.IN,
        'return': TokenType.RETURN, 'go': TokenType.GO, 'await': TokenType.AWAIT,
        'try': TokenType.TRY, 'handle': TokenType.HANDLE, 'panic': TokenType.PANIC,
        'defer': TokenType.DEFER, 'match': TokenType.MATCH, 'case': TokenType.CASE, 'module': TokenType.ANNOT_MODULE,
        'as': TokenType.AS,
    }

    def is_keyword(self, value: str) -> bool:
        return value in self.KEYWORDS or value == 'not'

    ANNOTATIONS = {
        'manual': TokenType.ANNOT_MANUAL, 'rc': TokenType.ANNOT_RC,
        'system_thread': TokenType.ANNOT_SYSTEM_THREAD, 'event_loop': TokenType.ANNOT_EVENT_LOOP,
        'inline_asm': TokenType.ANNOT_INLINE_ASM, 'rust': TokenType.ANNOT_RUST,
        'go': TokenType.ANNOT_GO_LANG, 'c': TokenType.ANNOT_C, 'java': TokenType.ANNOT_JAVA,
        'python': TokenType.ANNOT_PYTHON, 'javascript': TokenType.ANNOT_JAVASCRIPT,
        'web': TokenType.ANNOT_WEB, 'mobile': TokenType.ANNOT_MOBILE,
        'cli': TokenType.ANNOT_CLI, 'desktop': TokenType.ANNOT_DESKTOP,
        'module': TokenType.ANNOT_MODULE, 'cpp': TokenType.ANNOT_CPP,
        'kotlin': TokenType.ANNOT_KOTLIN, 'swift': TokenType.ANNOT_SWIFT,
        'php': TokenType.ANNOT_PHP, 'ruby': TokenType.ANNOT_RUBY,
        'csharp': TokenType.ANNOT_CSHARP, 'lua': TokenType.ANNOT_LUA,
        'r': TokenType.ANNOT_R, 'julia': TokenType.ANNOT_JULIA,
        'haskell': TokenType.ANNOT_HASKELL, 'elixir': TokenType.ANNOT_ELIXIR,
        'dart': TokenType.ANNOT_DART, 'zig': TokenType.ANNOT_ZIG,
        'typescript': TokenType.ANNOT_TYPESCRIPT,
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self._indent_stack = [0]

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self._tokenize_one()
        while len(self._indent_stack) > 1:
            self._indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, '', self.line, self.column))
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens

    def _get_line_context(self) -> str:
        """Get the current line for error context."""
        lines = self.source.split('\n')
        if self.line <= len(lines):
            return lines[self.line - 1]
        return ""

    def _tokenize_one(self):
        char = self.source[self.pos]

        if char == '\n':
            self._handle_newline()
        elif char == '#' or (char == '/' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/'):
            self._skip_single_line_comment()
        elif char == '/' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '*':
            self._skip_multi_line_comment()
        elif char.isspace():
            self._skip_whitespace()
        elif char == '@':
            self._handle_annotation()
        elif char == '"':
            self._handle_string()
        elif char.isdigit() or (char == '-' and self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit()):
            self._handle_number()
        elif char.isalpha() or char == '_' or ord(char) > 127:
            self._handle_identifier_or_keyword()
        elif char in '+-*/%=<>!:;.(){}[],&|?':
            self._handle_operator()
        else:
            context = self._get_line_context()
            caret = ' ' * (self.column - 1) + '^'
            raise LexerError(
                f"Unexpected character '{char}' at line {self.line}, column {self.column}\n"
                f"    {context}\n"
                f"    {caret}",
                self.line, self.column, char, context
            )

    def _handle_newline(self):
        self.pos += 1
        self.line += 1
        self.column = 1
        self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))

        # Check for indentation on next line
        indent = self._get_indent_level()
        prev = self._indent_stack[-1]
        if indent > prev:
            self._indent_stack.append(indent)
            self.tokens.append(Token(TokenType.INDENT, '', self.line, self.column))
        elif indent < prev:
            while self._indent_stack and self._indent_stack[-1] > indent:
                self._indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, '', self.line, self.column))

    def _get_indent_level(self) -> int:
        col = 0
        while self.pos < len(self.source) and (self.source[self.pos] == ' ' or self.source[self.pos] == '\t'):
            if self.source[self.pos] == '\t':
                col += 4
            else:
                col += 1
            self.pos += 1
        return col

    def _skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r':
            if self.source[self.pos] == '\t':
                self.column += 4
            else:
                self.column += 1
            self.pos += 1

    def _skip_single_line_comment(self):
        self.pos += 2
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.pos += 1

    def _skip_multi_line_comment(self):
        start_line = self.line
        self.pos += 2
        while self.pos + 1 < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
            if self.source[self.pos:self.pos + 2] == '*/':
                self.pos += 2
                break
            self.pos += 1
        else:
            raise LexerError(
                f"Unterminated multi-line comment starting at line {start_line}",
                start_line, 1, None, None
            )

    def _handle_annotation(self):
        start = self.pos
        self.pos += 1
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.pos += 1
        name = self.source[start + 1:self.pos]
        if name in self.ANNOTATIONS:
            self.tokens.append(Token(self.ANNOTATIONS[name], f'@{name}', self.line, self.column))
        else:
            raise LexerError(
                f"Unknown annotation '@{name}' at line {self.line}, column {self.column}\n"
                f"    {self._get_line_context()}\n"
                f"    {' ' * (self.column - 1)}^",
                self.line, self.column, f'@{name}', self._get_line_context()
            )
        self.column += len(name) + 1

    def _handle_string(self):
        start = self.pos
        self.pos += 1
        value_start = self.pos
        while self.pos < len(self.source):
            if self.source[self.pos] == '\\':
                self.pos += 2
            elif self.source[self.pos] == '"':
                break
            elif self.source[self.pos] == '\n':
                raise LexerError(
                    f"Unterminated string at line {self.line}, column {self.column}",
                    self.line, self.column, '"', self._get_line_context()
                )
            else:
                self.pos += 1
        else:
            raise LexerError(
                f"Unterminated string at line {self.line}, column {self.column}",
                self.line, self.column, '"', self._get_line_context()
            )
        value = self.source[value_start:self.pos]
        self.pos += 1
        self.tokens.append(Token(TokenType.STRING, value, self.line, self.column))
        self.column += len(value) + 2

    def _handle_number(self):
        start = self.pos
        if self.source[self.pos] == '-':
            self.pos += 1
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.pos += 1
        if self.pos < len(self.source) and self.source[self.pos] == '.':
            self.pos += 1
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                self.pos += 1
            value = self.source[start:self.pos]
            self.tokens.append(Token(TokenType.FLOAT, float(value), self.line, self.column))
        else:
            value = self.source[start:self.pos]
            self.tokens.append(Token(TokenType.INTEGER, int(value), self.line, self.column))
        self.column += len(value)

    def _handle_identifier_or_keyword(self):
        start = self.pos
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char.isalnum() or char in '_-' or ord(char) > 127:
                self.pos += 1
            else:
                break
        value = self.source[start:self.pos]
        if value in self.KEYWORDS:
            self.tokens.append(Token(self.KEYWORDS[value], value, self.line, self.column))
        elif value == 'not':
            self.tokens.append(Token(TokenType.NOT, value, self.line, self.column))
        elif value == 'true':
            self.tokens.append(Token(TokenType.BOOLEAN, True, self.line, self.column))
        elif value == 'false':
            self.tokens.append(Token(TokenType.BOOLEAN, False, self.line, self.column))
        elif value == 'null':
            self.tokens.append(Token(TokenType.NULL, value, self.line, self.column))
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, value, self.line, self.column))
        self.column += len(value)

    def _handle_operator(self):
        op_start = self.pos
        char = self.source[self.pos]
        two_char = self.source[self.pos:self.pos + 2] if self.pos + 1 < len(self.source) else ''

        if two_char in ('==', '!=', '<=', '>=', '&&', '||'):
            self.pos += 2
            if two_char == '&&':
                tok_type = TokenType.ANDAND
            elif two_char == '||':
                tok_type = TokenType.OROR
            else:
                tok_type = self._get_op_type(two_char)
            self.tokens.append(Token(tok_type, two_char, self.line, self.column))
        elif char in '+-*/%=<>!:;.(){}[],&|?':
            self.pos += 1
            tok_type = self._get_op_type(char)
            self.tokens.append(Token(tok_type, char, self.line, self.column))
        else:
            raise LexerError(
                f"Unknown operator '{char}' at line {self.line}, column {self.column}",
                self.line, self.column, char, self._get_line_context()
            )
        self.column += self.pos - op_start

    def _get_op_type(self, op: str) -> TokenType:
        op_map = {
            '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.STAR, '/': TokenType.SLASH,
            '%': TokenType.PERCENT, '=': TokenType.ASSIGN, '<': TokenType.LT, '>': TokenType.GT,
            '!': TokenType.NOT, '?': TokenType.QMARK, ':': TokenType.COLON, ';': TokenType.SEMI,
            '(': TokenType.LPAREN, ')': TokenType.RPAREN, '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE, '}': TokenType.RBRACE, ',': TokenType.COMMA, '.': TokenType.DOT,
            '==': TokenType.EQ, '!=': TokenType.NE, '<=': TokenType.LE, '>=': TokenType.GE,
        }
        return op_map[op]


if __name__ == '__main__':
    test_code = '''let x: int = 5
let y = 10.5
let msg = "hello"
let flag = true

fn add(a: int, b: int): int
    return a + b

if x > 0:
    let result = x + y
else:
    let result = 0

for i in [1, 2, 3]:
    print(i)

@manual
fn manual_alloc():
    // manual memory code
    return 0
'''
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    for tok in tokens:
        print(tok)