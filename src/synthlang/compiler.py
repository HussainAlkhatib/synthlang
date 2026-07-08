"""SynthLang Compiler - AST to IR transformation."""
from typing import List, Dict, Optional, Any
from .lexer import Lexer
from .parser import ASTNode, NodeType, Parser, Annotation
from .ir import (
    IRInstruction, IRModule, IRType,
    load_const, load_var, store_var, call, ret,
    jump, jump_if_false, jump_if_true, loop_begin, loop_end,
    alloc, free, increment_rc, decrement_rc,
    spawn_thread, wait, yield_op, await_op, binary_op, unary_op,
    ffi_import, ffi_call, ffi_get_attr, label
)


class Compiler:
    def __init__(self):
        self.ir_module = IRModule()
        self.current_function: Optional[str] = None
        self.function_instructions: Dict[str, List[IRInstruction]] = {}
        self.top_level_instructions: List[IRInstruction] = []
        self.label_count = 0
        self.func_params: Dict[str, List[str]] = {}
        self.pending_labels: Dict[str, List[int]] = {}

    def compile(self, ast: List[ASTNode]) -> IRModule:
        for node in ast:
            self._compile_node(node)
        for name, instrs in self.function_instructions.items():
            self.ir_module.add_function(name, instrs)
        if 'main' not in self.function_instructions:
            self.ir_module.add_function('main', self.top_level_instructions)
        # Store function parameters
        for name, params in self.func_params.items():
            if name in self.ir_module.functions:
                self.ir_module.functions[name + '_params'] = params
        return self.ir_module

    def _new_label(self, prefix: str = "L") -> str:
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def _add_instruction(self, instr: IRInstruction):
        if self.current_function and self.current_function in self.function_instructions:
            self.function_instructions[self.current_function].append(instr)
        else:
            self.top_level_instructions.append(instr)

    def _get_current_instrs(self) -> List[IRInstruction]:
        if self.current_function and self.current_function in self.function_instructions:
            return self.function_instructions[self.current_function]
        return self.top_level_instructions

    def _compile_node(self, node: ASTNode) -> Optional[IRInstruction]:
        if node.type == NodeType.VARIABLE:
            self._compile_variable(node)
        elif node.type == NodeType.FUNCTION:
            self._compile_function(node)
        elif node.type == NodeType.RETURN:
            return self._compile_return(node)
        elif node.type == NodeType.IF:
            self._compile_if(node)
        elif node.type == NodeType.FOR:
            self._compile_for(node)
        elif node.type == NodeType.WHILE:
            self._compile_while(node)
        elif node.type == NodeType.ASSIGNMENT:
            instr = self._compile_assignment(node)
            if instr:
                self._add_instruction(instr)
        elif node.type == NodeType.CALL:
            instrs = self._compile_expression(node)
            for instr in instrs:
                self._add_instruction(instr)
        elif node.type == NodeType.IMPORT:
            self._compile_import(node)
        elif node.type == NodeType.FFI_IMPORT_SELECTIVE:
            self._compile_selective_import(node)
        elif node.type == NodeType.BLOCK:
            for child in node.children:
                self._compile_node(child)

    def _compile_variable(self, node: ASTNode):
        var_info = node.value
        name = var_info['name']
        var_type = var_info.get('type')
        kind = var_info.get('kind', 'let')
        self.ir_module.add_variable(name, var_type)

        if node.children:
            expr = node.children[0]
            instrs = self._compile_expression(expr)
            for instr in instrs:
                self._add_instruction(instr)
            self._add_instruction(store_var(name))

    def _compile_function(self, node: ASTNode):
        prev_func = self.current_function
        func_info = node.value
        name = func_info['name']
        params = [p['name'] for p in func_info.get('params', [])]
        self.ir_module.func_params[name] = params
        self.current_function = name
        self.function_instructions[name] = []

        for child in node.children:
            self._compile_node(child)
        
        # Handle annotations after compiling body
        for annot in node.annotations:
            if annot.name == 'web':
                self.ir_module.register_annotation('web', name)
            elif annot.name == 'cli':
                self.ir_module.register_annotation('cli', name)
        
        self.current_func = prev_func

    def _compile_expression(self, node: ASTNode) -> List[IRInstruction]:
        instructions = []
        if node.type == NodeType.EXPRESSION:
            val = node.value
            if isinstance(val, bool):
                instructions.append(load_const(val))
            elif isinstance(val, (int, float)):
                instructions.append(load_const(val))
            elif isinstance(val, str):
                instructions.append(load_const(val))
            elif val is None:
                instructions.append(load_const(None))
            else:
                instructions.append(load_const(val))
        elif node.type == NodeType.LOAD_VAR:
            instructions.append(load_var(node.value))
        elif node.type == NodeType.UNARY_OP:
            operand_instrs = self._compile_expression(node.children[0])
            instructions.extend(operand_instrs)
            instructions.append(unary_op(node.value))
        elif node.type == NodeType.BINARY_OP:
            left_instrs = self._compile_expression(node.children[0])
            right_instrs = self._compile_expression(node.children[1])
            instructions.extend(left_instrs)
            instructions.extend(right_instrs)
            instructions.append(binary_op(node.value))
        elif node.type == NodeType.CALL:
            func_name = node.value
            args_instrs = []
            call_args = []
            for arg in node.children:
                args_instrs.extend(self._compile_expression(arg))
                if arg.type == NodeType.EXPRESSION and isinstance(arg.value, (int, float, str, bool)):
                    call_args.append(arg.value)
            instructions.extend(args_instrs)
            instructions.append(call(func_name, call_args))
        elif node.type == NodeType.FFI_CALL:
            module = node.value['module']
            method = node.value['method']
            args_instrs = []
            for arg in node.value.get('args', []):
                args_instrs.extend(self._compile_expression(arg))
            instructions.extend(args_instrs)
            instructions.append(ffi_call('python', module, method, len(node.value.get('args', []))))
        elif node.type == NodeType.FFI_GET_ATTR:
            module = node.value['module']
            attr = node.value['attr']
            instructions.append(ffi_get_attr(module, attr))
        elif node.type == NodeType.LIST:
            elements = [self._eval_expr(elem) for elem in node.children]
            instructions.append(load_const(elements))
        elif node.type == NodeType.DICT:
            entries = {}
            for key_node, value_node in node.children:
                key = self._eval_expr(key_node)
                value = self._eval_expr(value_node)
                if key is not None:
                    entries[key] = value
            instructions.append(load_const(entries))
        return instructions

    def _compile_assignment(self, node: ASTNode) -> Optional[IRInstruction]:
        name = node.value
        if node.children:
            expr_instrs = self._compile_expression(node.children[0])
            for instr in expr_instrs:
                self._add_instruction(instr)
            return store_var(name)
        return None

    def _compile_return(self, node: ASTNode) -> Optional[IRInstruction]:
        if not node.children:
            self._add_instruction(ret())
            return None
        expr = node.children[0]
        instrs = self._compile_expression(expr)
        for instr in instrs:
            self._add_instruction(instr)
        self._add_instruction(ret())
        return None

    def _compile_if(self, node: ASTNode):
        final_end_label = self._new_label('end')
        condition = node.children[0]
        then_block = node.children[1]
        
        remaining = node.children[2:]
        has_else = remaining and remaining[-1].type == NodeType.BLOCK
        elif_branches = []
        
        # Extract elif branches (pairs of: condition, body)
        if has_else:
            for i in range(0, len(remaining) - 1, 2):
                if i + 1 < len(remaining):
                    elif_branches.append((remaining[i], remaining[i+1]))
        else:
            for i in range(0, len(remaining), 2):
                if i + 1 < len(remaining):
                    elif_branches.append((remaining[i], remaining[i+1]))
        
        # Pre-generate all labels we'll need
        elif_labels = [self._new_label(f'elif{i+1}') for i in range(len(elif_branches))]
        else_label = self._new_label('else') if has_else else final_end_label
        
        # Compile: condition
        for instr in self._compile_expression(condition):
            self._add_instruction(instr)
        
        # Jump to first elif if condition is false
        if elif_branches:
            self._add_instruction(jump_if_false(elif_labels[0]))
        elif has_else:
            self._add_instruction(jump_if_false(else_label))
        else:
            self._add_instruction(jump_if_false(final_end_label))

        # Compile then block
        for child in then_block.children:
            self._compile_node(child)
        
        # Jump to final end (skip all elif/else)
        self._add_instruction(jump(final_end_label))

        # Compile elif branches
        for i, (elif_cond, elif_body) in enumerate(elif_branches):
            # Label for this elif branch
            self._add_instruction(label(elif_labels[i]))
            
            for instr in self._compile_expression(elif_cond):
                self._add_instruction(instr)
            
            # If last elif and else exists: jump to else, else jump to next elif or end
            if has_else and i == len(elif_branches) - 1:
                self._add_instruction(jump_if_false(else_label))
            elif i < len(elif_branches) - 1:
                self._add_instruction(jump_if_false(elif_labels[i + 1]))
            else:
                self._add_instruction(jump_if_false(final_end_label))
            
            for child in elif_body.children:
                self._compile_node(child)
            
            self._add_instruction(jump(final_end_label))

        # Compile else block (if any)
        if has_else:
            self._add_instruction(label(else_label))
            else_block = remaining[-1]
            for child in else_block.children:
                self._compile_node(child)

        # Final end label
        self._add_instruction(label(final_end_label))

    def _compile_for(self, node: ASTNode):
        var_name = (node.value or {}).get('var', 'item')
        iterable = node.children[0]
        body_block = node.children[1]

        if iterable.type == NodeType.LIST:
            elements = [self._eval_expr(elem) for elem in iterable.children]
        else:
            elements = []

        # Unroll the loop for each element
        for elem in elements:
            self._add_instruction(load_const(elem))
            self._add_instruction(store_var(var_name))
            for child in body_block.children:
                self._compile_node(child)

    def _eval_expr(self, node: ASTNode) -> Any:
        if node.type == NodeType.EXPRESSION:
            val = node.value
            if val is None:
                return None
            return val
        elif node.type == NodeType.BINARY_OP:
            left = self._eval_expr(node.children[0])
            right = self._eval_expr(node.children[1])
            op = node.value
            if left is None or right is None:
                return None
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '%': return left % right
        return None

    def _compile_while(self, node: ASTNode):
        condition = node.children[0]
        body_block = node.children[1]

        loop_start_label = self._new_label('while_start')
        loop_end_label = self._new_label('while_end')

        self._add_instruction(loop_begin(loop_start_label))

        for instr in self._compile_expression(condition):
            self._add_instruction(instr)

        self._add_instruction(jump_if_false(loop_end_label))

        for child in body_block.children:
            self._compile_node(child)

        self._add_instruction(jump(loop_start_label, loop_end_label))

        self._add_instruction(loop_end(loop_end_label))

    def _compile_import(self, node: ASTNode):
        import_info = node.value
        language = import_info['language']
        module_path = import_info['module']
        as_name = import_info.get('as') or module_path
        self.ir_module.imports[as_name] = (language, module_path)
        self._add_instruction(ffi_import(language, module_path, as_name))
    
    def _compile_selective_import(self, node: ASTNode):
        import_info = node.value
        language = import_info['language']
        module_path = import_info['module']
        imports = import_info.get('imports', [])
        for func_name in imports:
            full_name = f"{module_path}.{func_name}"
            self._add_instruction(ffi_import(language, full_name, func_name))


if __name__ == '__main__':
    code = '''let x = 5
let y = 10

fn add(a: int, b: int): int
    return a + b
'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    print(ir)
    print("Functions:", list(ir.functions.keys()))
    for name, instrs in ir.functions.items():
        print(f"  {name}: {[i.type.name for i in instrs]}")