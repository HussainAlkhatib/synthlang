"""SynthLang LSP - Language Server Protocol implementation."""
import json
import sys
import re
from typing import Any, Dict, List, Optional, Tuple
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler
from .vm import VM
from .formatter import Formatter
from pathlib import Path


class Position:
    def __init__(self, line: int, character: int):
        self.line = line
        self.character = character


class Range:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end


class LSPServer:
    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.version = 0
        self.content_provider = ContentProvider()

    def notify_initialized(self, params: dict):
        pass

    def text_document_did_open(self, params: dict):
        uri = params['textDocument']['uri']
        text = params['textDocument']['text']
        self.documents[uri] = text

    def text_document_did_change(self, params: dict):
        uri = params['textDocument']['uri']
        changes = params['contentChanges']
        for change in changes:
            if 'text' in change:
                self.documents[uri] = change['text']

    def text_document_did_close(self, params: dict):
        uri = params['textDocument']['uri']
        if uri in self.documents:
            del self.documents[uri]

    def code_action(self, params: dict) -> List[dict]:
        return []

    def completion(self, params: dict) -> dict:
        uri = params['textDocument']['uri']
        position = params['position']
        text = self.documents.get(uri, "")

        keywords = ['let', 'var', 'fn', 'if', 'elif', 'else', 'for', 'while', 'return', 'go', 'await', 'try', 'handle', 'panic', 'match']

        return {
            "isIncomplete": False,
            "items": [{"label": kw, "kind": 14} for kw in keywords]
        }

    def definition(self, params: dict) -> Optional[dict]:
        return None

    def hover(self, params: dict) -> Optional[dict]:
        uri = params['textDocument']['uri']
        position = params['position']
        text = self.documents.get(uri, "")

        return {
            "contents": {"kind": "markdown", "value": "SynthLang hover information"},
            "range": None
        }

    def diagnostic(self, uri: str) -> List[dict]:
        text = self.documents.get(uri, "")
        diagnostics = []

        try:
            lexer = Lexer(text)
            tokens = lexer.tokenize()
            parser = Parser(tokens, text)
            ast = parser.parse()
        except SyntaxError as e:
            line_num = 0
            column_num = 0
            
            # Extract line number from error
            if hasattr(e, 'lineno') and e.lineno is not None:
                line_num = e.lineno - 1
            elif hasattr(e, 'line') and e.line is not None:
                line_num = e.line - 1
            else:
                # Try to extract line number from error message
                match = re.search(r'line (\d+)', str(e))
                if match:
                    line_num = int(match.group(1)) - 1
            
            # Extract column number from error
            if hasattr(e, 'column') and e.column is not None:
                column_num = e.column
            
            diagnostics.append({
                "range": {"start": {"line": line_num, "character": column_num},
                         "end": {"line": line_num + 1 if line_num > 0 else 1, "character": 100}},
                "message": str(e),
                "severity": 1,
                "source": "synthlang"
            })
        except Exception as e:
            # Generic error handling
            line_num = 0
            if hasattr(e, 'lineno') and e.lineno is not None:
                line_num = e.lineno - 1
            elif hasattr(e, 'line') and e.line is not None:
                line_num = e.line - 1
            else:
                match = re.search(r'line (\d+)', str(e))
                if match:
                    line_num = int(match.group(1)) - 1
            
            diagnostics.append({
                "range": {"start": {"line": line_num, "character": 0},
                         "end": {"line": line_num + 1, "character": 100}},
                "message": str(e),
                "severity": 1,
                "source": "synthlang"
            })
        
        return diagnostics


class ContentProvider:
    def get_uri_path(self, uri: str) -> str:
        if uri.startswith('file:///'):
            return uri[8:]
        return uri

    def get_range(self, text: str, line: int, character: int) -> Range:
        lines = text.split('\n')
        start = Position(line, character)
        end = Position(line, character + 10)
        return Range(start, end)


def make_lsp_server():
    return LSPServer()


def serve():
    server = LSPServer()
    content_length = 0

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        
        if line.startswith('Content-Length:'):
            content_length = int(line.split(':')[1].strip())
        
        if line.strip() == '':
            content = sys.stdin.read(content_length)
            message = json.loads(content)
            method = message.get('method', '')
            params = message.get('params', {})
            
            response = {"jsonrpc": "2.0", "id": message.get('id')}
            
            if method == 'initialize':
                response['result'] = {"capabilities": {"textDocumentSync": 1, "completionProvider": True, "hoverProvider": True}}
            elif method == 'textDocument/didOpen':
                server.text_document_did_open(params)
                response['result'] = None
            elif method == 'textDocument/didChange':
                server.text_document_did_change(params)
                response['result'] = None
            elif method == 'textDocument/completion':
                response['result'] = server.completion(params)
            elif method == 'textDocument/hover':
                response['result'] = server.hover(params)
            elif method == 'textDocument/publishDiagnostics':
                response['result'] = None
            else:
                response['result'] = None
            
            output = json.dumps(response)
            sys.stdout.write(f"Content-Length: {len(output)}\r\n\r\n{output}")
            sys.stdout.flush()


if __name__ == '__main__':
    print("LSP server starting...")
    serve()