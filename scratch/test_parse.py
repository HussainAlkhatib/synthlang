import sys
sys.path.insert(0, 'src')
from synthlang.lexer import Lexer, TokenType
from synthlang.parser import Parser

with open(r'c:\Users\h2311\Downloads\SynthLang\projects\discord1\discord1.sl', 'r') as f:
    src = f.read()

lexer = Lexer(src)
tokens = lexer.tokenize()

# Print all tokens with line numbers so we can see the exact token stream
print("=== TOKEN STREAM ===")
for i, tok in enumerate(tokens):
    print(f"[{i:4d}] L{tok.line:3d}:C{tok.column:3d}  {tok.type.name:<20} {repr(tok.value)}")

print("\n=== END TOKEN STREAM ===")
print(f"Total tokens: {len(tokens)}")
