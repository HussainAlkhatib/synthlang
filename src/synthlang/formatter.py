"""SynthLang Formatter - slang fmt implementation."""
import os
import re
from typing import List, Optional
from .lexer import Lexer
from .parser import Parser, ASTNode, NodeType


class Formatter:
    INDENT_SIZE = 4
    indent_str = " " * INDENT_SIZE

    def __init__(self):
        self.indent_level = 0

    def format(self, source: str) -> str:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return self._format_ast(ast)

    def _format_ast(self, ast: List[ASTNode]) -> str:
        lines = []
        for node in ast:
            lines.extend(self._format_node(node))
        return "\n".join(lines)

    def _format_node(self, node: ASTNode) -> List[str]:
        if node.type == NodeType.VARIABLE:
            return self._format_variable(node)
        elif node.type == NodeType.FUNCTION:
            return self._format_function(node)
        elif node.type == NodeType.IF:
            return self._format_if(node)
        elif node.type == NodeType.FOR:
            return self._format_for(node)
        elif node.type == NodeType.WHILE:
            return self._format_while(node)
        elif node.type == NodeType.RETURN:
            return self._format_return(node)
        elif node.type == NodeType.ASSIGNMENT:
            return self._format_assignment(node)
        elif node.type == NodeType.CALL:
            return self._format_call(node)
        elif node.type == NodeType.BLOCK:
            return self._format_block(node)
        elif node.type == NodeType.EXPRESSION:
            return self._format_expression(node)
        elif node.type == NodeType.BINARY_OP:
            return self._format_binary_op(node)
        elif node.type == NodeType.LOAD_VAR:
            return self._format_load_var(node)
        else:
            return [""]

    def _indent(self) -> str:
        return self.indent_str * self.indent_level

    def _format_variable(self, node: ASTNode) -> List[str]:
        info = node.value
        kind = info.get('kind', 'let')
        name = info.get('name', '')
        var_type = info.get('type')
        
        lines = []
        parts = [kind]
        if var_type:
            parts.append(f": {var_type}")
        parts.append(f" {name}")
        
        if node.children:
            expr_str = self._expr_to_str(node.children[0])
            parts.append(f" = {expr_str}")
        
        lines.append(self._indent() + "".join(parts))
        return lines

    def _format_function(self, node: ASTNode) -> List[str]:
        info = node.value
        name = info.get('name', '')
        params = info.get('params', [])
        return_type = info.get('return_type')
        
        parts = ["fn", f" {name}("]
        param_strs = []
        for p in params:
            param = p.get('name', '')
            if p.get('type'):
                param += f": {p.get('type')}"
            param_strs.append(param)
        parts.append(", ".join(param_strs))
        parts.append(")")
        
        if return_type:
            parts.append(f": {return_type}")
        
        lines = [self._indent() + "".join(parts)]
        
        self.indent_level += 1
        for child in node.children:
            child_lines = self._format_node(child)
            lines.extend(child_lines)
        self.indent_level -= 1
        
        return lines

    def _format_if(self, node: ASTNode) -> List[str]:
        lines = []
        cond_str = self._expr_to_str(node.children[0])
        lines.append(self._indent() + f"if {cond_str}:")
        
        self.indent_level += 1
        then_block = node.children[1]
        for child in then_block.children:
            lines.extend(self._format_node(child))
        self.indent_level -= 1
        
        remaining = node.children[2:]
        for i in range(0, len(remaining), 2):
            if i + 1 < len(remaining):
                cond = remaining[i]
                body = remaining[i + 1]
                if cond.type.name == "EXPRESSION" and cond.value is None:
                    lines.append(self._indent() + "else:")
                else:
                    elif_cond_str = self._expr_to_str(cond)
                    lines.append(self._indent() + f"elif {elif_cond_str}:")
                self.indent_level += 1
                for child in body.children:
                    lines.extend(self._format_node(child))
                self.indent_level -= 1
        
        return lines

    def _format_for(self, node: ASTNode) -> List[str]:
        var_name = node.value.get('var', 'item')
        iterable = self._expr_to_str(node.children[0])
        lines = [self._indent() + f"for {var_name} in {iterable}:"]
        
        self.indent_level += 1
        body = node.children[1]
        for child in body.children:
            lines.extend(self._format_node(child))
        self.indent_level -= 1
        
        return lines

    def _format_while(self, node: ASTNode) -> List[str]:
        cond = self._expr_to_str(node.children[0])
        lines = [self._indent() + f"while {cond}:"]
        
        self.indent_level += 1
        body = node.children[1]
        for child in body.children:
            lines.extend(self._format_node(child))
        self.indent_level -= 1
        
        return lines

    def _format_return(self, node: ASTNode) -> List[str]:
        if node.children and node.children[0].value is not None:
            expr_str = self._expr_to_str(node.children[0])
            return [self._indent() + f"return {expr_str}"]
        return [self._indent() + "return"]

    def _format_assignment(self, node: ASTNode) -> List[str]:
        name = node.value
        expr = self._expr_to_str(node.children[0])
        return [self._indent() + f"{name} = {expr}"]

    def _format_call(self, node: ASTNode) -> List[str]:
        name = node.value
        args = ", ".join(self._expr_to_str(c) for c in node.children)
        return [self._indent() + f"{name}({args})"]

    def _format_load_var(self, node: ASTNode) -> List[str]:
        return [self._indent() + str(node.value)]

    def _format_block(self, node: ASTNode) -> List[str]:
        lines = []
        self.indent_level += 1
        for child in node.children:
            lines.extend(self._format_node(child))
        self.indent_level -= 1
        return lines

    def _format_expression(self, node: ASTNode) -> List[str]:
        return [self._indent() + str(node.value)]

    def _format_binary_op(self, node: ASTNode) -> List[str]:
        left = self._expr_to_str(node.children[0])
        right = self._expr_to_str(node.children[1])
        return [self._indent() + f"{left} {node.value} {right}"]

    def _expr_to_str(self, node: ASTNode) -> str:
        if node.type == NodeType.EXPRESSION:
            val = node.value
            if isinstance(val, bool):
                return "true" if val else "false"
            elif isinstance(val, str):
                return f'"{val}"'
            return str(val)
        elif node.type == NodeType.CALL:
            name = node.value
            args = ", ".join(self._expr_to_str(c) for c in node.children)
            return f"{name}({args})"
        elif node.type == NodeType.BINARY_OP:
            left = self._expr_to_str(node.children[0])
            right = self._expr_to_str(node.children[1])
            return f"{left} {node.value} {right}"
        elif node.type == NodeType.LIST:
            elems = ", ".join(self._expr_to_str(c) for c in node.children)
            return f"[{elems}]"
        elif node.type == NodeType.DICT:
            return "{}"
        return ""


def format_file(filepath: str) -> str:
    with open(filepath, 'r') as f:
        source = f.read()
    formatter = Formatter()
    return formatter.format(source)


def format_directory(dirpath: str = ".") -> int:
    count = 0
    for root, dirs, files in os.walk(dirpath):
        for f in files:
            if f.endswith('.sl'):
                filepath = os.path.join(root, f)
                formatted = format_file(filepath)
                with open(filepath, 'w') as wf:
                    wf.write(formatted)
                count += 1
    return count


if __name__ == '__main__':
    code = '''let x:int=5
fn add(a:int,b:int):int
return a+b
'''
    f = Formatter()
    print(f.format(code))