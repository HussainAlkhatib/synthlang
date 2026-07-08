# SynthLang Grammar Reference

## Lexical Structure

### Tokens

| Token | Pattern |
|-------|---------|
| LET | `let` |
| VAR | `var` |
| FN | `fn` |
| IF | `if` |
| ELIF | `elif` |
| ELSE | `else` |
| FOR | `for` |
| WHILE | `while` |
| IN | `in` |
| RETURN | `return` |
| GO | `go` |
| AWAIT | `await` |
| TRY | `try` |
| HANDLE | `handle` |
| PANIC | `panic` |
| DEFER | `defer` |
| MATCH | `match` |

### Operators

| Operator | Token Type |
|----------|------------|
| `+` | PLUS |
| `-` | MINUS |
| `*` | STAR |
| `/` | SLASH |
| `%` | PERCENT |
| `=` | ASSIGN |
| `==` | EQ |
| `!=` | NE |
| `<` | LT |
| `>` | GT |
| `<=` | LE |
| `>=` | GE |
| `&&` | ANDAND |
| `\|\|` | OROR |
| `!` | NOT |

### Literals

- **Integer**: Decimal numbers (`-?[0-9]+`)
- **Float**: Decimal with fractional part (`-?[0-9]+\.[0-9]+`)
- **String**: Double-quoted (`"..."`)
- **Boolean**: `true` or `false`

## Grammar (EBNF)

```
program        ::= statement* EOF

statement      ::= annotation* variable_decl
                 | annotation* function_decl
                 | if_stmt
                 | for_stmt
                 | while_stmt
                 | return_stmt
                 | assignment
                 | expression NEWLINE

variable_decl  ::= ("let" | "var") IDENTIFIER (":" IDENTIFIER)? "=" expression
function_decl  ::= "fn" IDENTIFIER "(" parameters? ")" (":" IDENTIFIER)? NEWLINE INDENT statement* DEDENT
parameters     ::= parameter ("," parameter)*
parameter      ::= IDENTIFIER (":" IDENTIFIER)?

if_stmt        ::= "if" expression ":" NEWLINE INDENT statement* DEDENT
                   ("elif" expression ":" NEWLINE INDENT statement* DEDENT)*
                   ("else" ":" NEWLINE INDENT statement* DEDENT)?

for_stmt       ::= "for" IDENTIFIER "in" expression ":" NEWLINE INDENT statement* DEDENT

while_stmt     ::= "while" expression ":" NEWLINE INDENT statement* DEDENT

return_stmt    ::= "return" expression? NEWLINE

assignment     ::= IDENTIFIER "=" expression NEWLINE

expression     ::= logical_or
logical_or     ::= logical_and ("||" logical_and)*
logical_and    ::= equality ("&&" equality)*
equality       ::= comparison (("==" | "!=") comparison)*
comparison     ::= term (("<" | ">" | "<=" | ">=") term)*
term           ::= factor (("+" | "-") factor)*
factor         ::= unary (("*" | "/" | "%") unary)*
unary          ::= ("!" | "-") unary | primary
primary        ::= INTEGER | FLOAT | STRING | BOOLEAN | IDENTIFIER
                 | IDENTIFIER "(" arguments? ")"
                 | "[" list_elements? "]"
                 | "{" dict_entries? "}"
                 | "(" expression ")"

arguments      ::= expression ("," expression)*
list_elements  ::= expression ("," expression)*
dict_entries   ::= dict_entry ("," dict_entry)*
dict_entry     ::= IDENTIFIER ":" expression

annotation     ::= "@" IDENTIFIER
```