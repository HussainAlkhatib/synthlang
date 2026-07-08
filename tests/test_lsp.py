"""Tests for LSP implementation."""
import unittest
from synthlang.lsp import LSPServer, Position, Range


class TestLSP(unittest.TestCase):
    def test_server_creation(self):
        server = LSPServer()
        self.assertIsNotNone(server)

    def test_position(self):
        pos = Position(1, 5)
        self.assertEqual(pos.line, 1)
        self.assertEqual(pos.character, 5)

    def test_range(self):
        start = Position(0, 0)
        end = Position(0, 10)
        r = Range(start, end)
        self.assertEqual(r.start.line, 0)
        self.assertEqual(r.end.line, 0)

    def test_completion(self):
        server = LSPServer()
        result = server.completion({'textDocument': {'uri': 'test'}, 'position': {'line': 0, 'character': 0}})
        self.assertIn('items', result)
        self.assertTrue(len(result['items']) > 0)


if __name__ == '__main__':
    unittest.main()