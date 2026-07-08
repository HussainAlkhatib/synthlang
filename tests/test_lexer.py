#!/usr/bin/env python3
"""Test lexer tokenization - comprehensive tests for all token types and edge cases."""
import unittest
from synthlang.lexer import Lexer, TokenType


class TestLexerKeywords(unittest.TestCase):
    def test_let_keyword(self):
        lexer = Lexer("let x = 1")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.LET)

    def test_var_keyword(self):
        lexer = Lexer("var y = 2")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.VAR)

    def test_fn_keyword(self):
        lexer = Lexer("fn add(): int")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.FN)

    def test_if_keyword(self):
        lexer = Lexer("if x > 0:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.IF)

    def test_elif_keyword(self):
        lexer = Lexer("elif x < 0:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ELIF)

    def test_else_keyword(self):
        lexer = Lexer("else:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ELSE)

    def test_for_keyword(self):
        lexer = Lexer("for i in list:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.FOR)

    def test_while_keyword(self):
        lexer = Lexer("while x < 10:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.WHILE)

    def test_in_keyword(self):
        lexer = Lexer("for i in [1]:")
        tokens = lexer.tokenize()
        in_tokens = [t for t in tokens if t.type == TokenType.IN]
        self.assertTrue(len(in_tokens) > 0)

    def test_return_keyword(self):
        lexer = Lexer("return x")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.RETURN)

    def test_go_keyword(self):
        lexer = Lexer("go spawn()")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.GO)

    def test_await_keyword(self):
        lexer = Lexer("await task")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.AWAIT)

    def test_try_keyword(self):
        lexer = Lexer("try:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.TRY)

    def test_handle_keyword(self):
        lexer = Lexer("handle:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.HANDLE)

    def test_panic_keyword(self):
        lexer = Lexer('panic "error"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.PANIC)

    def test_defer_keyword(self):
        lexer = Lexer("defer cleanup()")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.DEFER)

    def test_match_keyword(self):
        lexer = Lexer("match x:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.MATCH)


class TestLexerOperators(unittest.TestCase):
    def test_plus(self):
        lexer = Lexer("1 + 2")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.INTEGER)
        self.assertEqual(tokens[1].type, TokenType.PLUS)
        self.assertEqual(tokens[2].type, TokenType.INTEGER)

    def test_minus(self):
        lexer = Lexer("5 - 3")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.MINUS)

    def test_star(self):
        lexer = Lexer("2 * 3")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.STAR)

    def test_slash(self):
        lexer = Lexer("6 / 2")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.SLASH)

    def test_percent(self):
        lexer = Lexer("7 % 3")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.PERCENT)

    def test_assign(self):
        lexer = Lexer("x = 5")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.ASSIGN)

    def test_eq(self):
        lexer = Lexer("x == y")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.EQ)

    def test_ne(self):
        lexer = Lexer("x != y")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.NE)

    def test_lt(self):
        lexer = Lexer("x < y")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.LT)

    def test_gt(self):
        lexer = Lexer("x > y")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.GT)

    def test_le(self):
        lexer = Lexer("x <= y")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.LE)

    def test_ge(self):
        lexer = Lexer("x >= y")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.GE)

    def test_andand(self):
        lexer = Lexer("a && b")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.ANDAND)

    def test_oror(self):
        lexer = Lexer("a || b")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.OROR)

    def test_not(self):
        lexer = Lexer("!x")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.NOT)

    def test_qmark(self):
        lexer = Lexer("result?")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.QMARK)

    def test_colon(self):
        lexer = Lexer("if x:")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[2].type, TokenType.COLON)


class TestLexerLiterals(unittest.TestCase):
    def test_integer_positive(self):
        lexer = Lexer("let x = 42")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.INTEGER)
        self.assertEqual(tokens[3].value, 42)

    def test_integer_negative(self):
        lexer = Lexer("let x = -42")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.INTEGER)
        self.assertEqual(tokens[3].value, -42)

    def test_integer_zero(self):
        lexer = Lexer("let x = 0")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.INTEGER)
        self.assertEqual(tokens[3].value, 0)

    def test_float_positive(self):
        lexer = Lexer("let x = 3.14")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.FLOAT)
        self.assertAlmostEqual(tokens[3].value, 3.14)

    def test_float_negative(self):
        lexer = Lexer("let x = -2.5")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.FLOAT)
        self.assertEqual(tokens[3].value, -2.5)

    def test_string_simple(self):
        lexer = Lexer('let msg = "hello"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.STRING)
        self.assertEqual(tokens[3].value, "hello")

    def test_string_empty(self):
        lexer = Lexer('let msg = ""')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.STRING)
        self.assertEqual(tokens[3].value, "")

    def test_string_with_spaces(self):
        lexer = Lexer('let msg = "hello world"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].value, "hello world")

    def test_string_escape(self):
        lexer = Lexer(r'let msg = "hello\nworld"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.STRING)

    def test_boolean_true(self):
        lexer = Lexer("let flag = true")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.BOOLEAN)
        self.assertEqual(tokens[3].value, True)

    def test_boolean_false(self):
        lexer = Lexer("let flag = false")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].type, TokenType.BOOLEAN)
        self.assertEqual(tokens[3].value, False)

    def test_list_empty(self):
        lexer = Lexer("let items = []")
        tokens = lexer.tokenize()
        lbracket_tokens = [t for t in tokens if t.type == TokenType.LBRACKET]
        self.assertTrue(len(lbracket_tokens) > 0)

    def test_list_with_elements(self):
        lexer = Lexer("let items = [1, 2, 3]")
        tokens = lexer.tokenize()
        lbracket_tokens = [t for t in tokens if t.type == TokenType.LBRACKET]
        self.assertTrue(len(lbracket_tokens) > 0)

    def test_dict_empty(self):
        lexer = Lexer("let obj = {}")
        tokens = lexer.tokenize()
        lbrace_tokens = [t for t in tokens if t.type == TokenType.LBRACE]
        self.assertTrue(len(lbrace_tokens) > 0)

    def test_identifier_simple(self):
        lexer = Lexer("let x = 1")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "x")

    def test_identifier_with_underscore(self):
        lexer = Lexer("let _var = 1")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "_var")

    def test_identifier_with_dash(self):
        lexer = Lexer("let my_var = 1")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].value, "my_var")


class TestLexerAnnotations(unittest.TestCase):
    def test_manual_annotation(self):
        lexer = Lexer("@manual")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_MANUAL)

    def test_rc_annotation(self):
        lexer = Lexer("@rc")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_RC)

    def test_system_thread_annotation(self):
        lexer = Lexer("@system_thread")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_SYSTEM_THREAD)

    def test_event_loop_annotation(self):
        lexer = Lexer("@event_loop")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_EVENT_LOOP)

    def test_inline_asm_annotation(self):
        lexer = Lexer("@inline_asm")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_INLINE_ASM)

    def test_rust_annotation(self):
        lexer = Lexer("@rust")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_RUST)

    def test_go_annotation(self):
        lexer = Lexer("@go")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_GO_LANG)

    def test_c_annotation(self):
        lexer = Lexer("@c")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_C)

    def test_java_annotation(self):
        lexer = Lexer("@java")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_JAVA)

    def test_web_annotation(self):
        lexer = Lexer("@web")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_WEB)

    def test_mobile_annotation(self):
        lexer = Lexer("@mobile")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_MOBILE)

    def test_cli_annotation(self):
        lexer = Lexer("@cli")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_CLI)

    def test_desktop_annotation(self):
        lexer = Lexer("@desktop")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.ANNOT_DESKTOP)


class TestLexerComments(unittest.TestCase):
    def test_single_line_comment(self):
        lexer = Lexer("# this is a comment\nlet x = 1")
        tokens = lexer.tokenize()
        let_tokens = [t for t in tokens if t.type == TokenType.LET]
        self.assertTrue(len(let_tokens) > 0)

    def test_single_line_comment_with_double_slash(self):
        lexer = Lexer("// this is a comment\nlet x = 1")
        tokens = lexer.tokenize()
        let_tokens = [t for t in tokens if t.type == TokenType.LET]
        self.assertTrue(len(let_tokens) > 0)

    def test_multi_line_comment(self):
        lexer = Lexer("/* multi\n   line\n   comment */\nlet x = 1")
        tokens = lexer.tokenize()
        let_tokens = [t for t in tokens if t.type == TokenType.LET]
        self.assertTrue(len(let_tokens) > 0)

    def test_only_comments(self):
        lexer = Lexer("# only comments\n// more comments")
        tokens = lexer.tokenize()
        self.assertEqual(len([t for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)]), 0)


class TestLexerIndentation(unittest.TestCase):
    def test_indent_token(self):
        code = "let x = 1\n    let y = 2"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        indent_found = any(t.type == TokenType.INDENT for t in tokens)
        self.assertTrue(indent_found)

    def test_dedent_token(self):
        code = "let x = 1\n    let y = 2\nlet z = 3"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        dedent_found = any(t.type == TokenType.DEDENT for t in tokens)
        self.assertTrue(dedent_found)

    def test_nested_indentation(self):
        code = """if x > 0:
    if y > 0:
        let z = 1
    let w = 2
"""
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        indent_count = sum(1 for t in tokens if t.type == TokenType.INDENT)
        dedent_count = sum(1 for t in tokens if t.type == TokenType.DEDENT)
        self.assertEqual(indent_count, 2)
        self.assertEqual(dedent_count, 2)


class TestLexerEdgeCases(unittest.TestCase):
    def test_empty_file(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_unicode_identifier(self):
        lexer = Lexer("let π = 3.14")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "π")

    def test_large_integer(self):
        lexer = Lexer("let big = 12345678901234567890")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[3].value, 12345678901234567890)

    def test_multiple_statements(self):
        lexer = Lexer("let a = 1\nlet b = 2\nlet c = 3")
        tokens = lexer.tokenize()
        self.assertEqual(len([t for t in tokens if t.type == TokenType.LET]), 3)

    def test_eof_token_present(self):
        lexer = Lexer("let x = 1")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[-1].type, TokenType.EOF)

    def test_line_and_column_tracking(self):
        lexer = Lexer("let x = 1\nlet y = 2")
        tokens = lexer.tokenize()
        for tok in tokens:
            self.assertIsNotNone(tok.line)
            self.assertIsNotNone(tok.column)


class TestLexerErrors(unittest.TestCase):
    def test_unknown_annotation(self):
        lexer = Lexer("@unknown")
        with self.assertRaises(SyntaxError) as ctx:
            lexer.tokenize()
        self.assertIn("@unknown", str(ctx.exception))

    def test_unexpected_character(self):
        lexer = Lexer("let x = $1")
        with self.assertRaises(SyntaxError) as ctx:
            lexer.tokenize()
        self.assertIn("Unexpected character", str(ctx.exception))

    def test_unterminated_string(self):
        lexer = Lexer('let x = "unterminated')
        with self.assertRaises(SyntaxError) as ctx:
            lexer.tokenize()
        self.assertIn("Unterminated string", str(ctx.exception))

    def test_unterminated_multiline_comment(self):
        lexer = Lexer("/* unterminated")
        with self.assertRaises(SyntaxError) as ctx:
            lexer.tokenize()
        self.assertIn("Unterminated multi-line comment", str(ctx.exception))


class TestLexerFloatParsing(unittest.TestCase):
    def test_float_without_leading_digit(self):
        # Currently .5 is parsed as DOT + INTEGER, not as a FLOAT
        lexer = Lexer("let x = .5")
        tokens = lexer.tokenize()
        # Document current behavior: DOT followed by INTEGER
        self.assertEqual(tokens[3].type, TokenType.DOT)
        self.assertEqual(tokens[4].type, TokenType.INTEGER)


if __name__ == '__main__':
    unittest.main()