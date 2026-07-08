"""SynthLang VM - Stack-based interpreter for IR."""
import asyncio
from typing import Any, List, Dict, Optional
from .ir import IRModule, IRInstruction, IRType


class Value:
    def __init__(self, value: Any, type_str: str = None):
        self.value = value
        self.type = type_str


class Result:
    OK = "Ok"
    ERR = "Err"

    def __init__(self, status: str, value: Any = None, error: Any = None):
        self.status = status
        self.value = value
        self.error = error

    @staticmethod
    def ok(value: Any) -> 'Result':
        return Result(Result.OK, value=value)

    @staticmethod
    def err(error: Any) -> 'Result':
        return Result(Result.ERR, error=error)


class VM:
    def __init__(self, ir_module: IRModule, debug: bool = False, source_map: Dict[str, Any] = None):
        self.ir_module = ir_module
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, List[IRInstruction]] = ir_module.functions
        self.call_stack: List[Dict[str, Any]] = []
        self.current_func: Optional[str] = None
        self.pc = 0
        self.ffi = None
        self.debug = debug
        self.source_map = source_map or {}
        self.output_buffer: List[str] = []
        self.foreign_objects: Dict[str, Any] = {}
        self.defer_stack: List[List[Any]] = []  # Stack of deferred calls per function frame
        self.exception_stack: List[str] = []  # Track exception handlers

    def run(self):
        if 'main' in self.functions:
            self._run_function('main', [])
        return self.variables

    def _format_stack_trace(self) -> str:
        lines = []
        for frame in self.call_stack:
            func_name = frame.get('function', 'unknown')
            loc = frame.get('location', '')
            if loc:
                lines.append(f"  at {func_name} ({loc})")
            else:
                lines.append(f"  at {func_name}")
        return '\n'.join(lines)

    def _add_call_frame(self, func_name: str, pc: int = 0):
        frame = {'function': func_name}
        if self.source_map and func_name in self.source_map:
            frame['location'] = self.source_map[func_name].get('location', '')
        self.call_stack.append(frame)

    def _remove_call_frame(self):
        if self.call_stack:
            self.call_stack.pop()

    def _run_function(self, name: str, args: List[Any]) -> Any:
        self.current_func = name
        instructions = self.functions[name]
        func_params = self.ir_module.func_params.get(name, [])

        label_map = self._build_label_map(instructions)
        
        # Push a new defer frame
        self.defer_stack.append([])

        for i, arg in enumerate(args):
            if i < len(func_params):
                self.variables[func_params[i]] = arg

        pc = 0
        result = None

        while pc < len(instructions):
            instr = instructions[pc]
            if self.debug:
                self._debug_print(instr, pc)
            outcome = self._execute(instr, pc, label_map)
            if outcome is not None:
                if outcome == 'return' and self.stack:
                    result = self.stack.pop()
                    pc = len(instructions)
                elif outcome == 'exception':
                    # Check if we have a handler in the call stack
                    if self.exception_stack:
                        outcome = self._handle_exception()
                    else:
                        pc = len(instructions)
                elif outcome == 'exit':
                    pc = len(instructions)
                elif isinstance(outcome, int):
                    pc = outcome
            else:
                pc += 1

        # Execute deferred calls on function exit
        if self.defer_stack:
            deferred = self.defer_stack.pop()
            for deferred_call in reversed(deferred):
                if deferred_call.get('type') == 'call':
                    func_name = deferred_call.get('func')
                    call_args = deferred_call.get('args', [])
                    try:
                        if func_name in self.functions:
                            self._run_function(func_name, call_args)
                        elif func_name == 'print':
                            print(*call_args)
                    except Exception as e:
                        if self.debug:
                            print(f"[DEBUG] Defer call error: {e}")
        
        for param in func_params:
            if param in self.variables:
                del self.variables[param]
        return result

    def _debug_print(self, instr: IRInstruction, pc: int):
        print(f"[DEBUG] PC={pc}: {instr.type.name}", end='')
        if instr.operand is not None:
            print(f" {instr.operand}", end='')
        if instr.arg1 is not None:
            print(f", arg1={instr.arg1}", end='')
        if instr.arg2 is not None:
            print(f", arg2={instr.arg2}", end='')
        if instr.arg3 is not None:
            print(f", arg3={instr.arg3}", end='')
        print(f"\n[DEBUG] Stack: {self.stack[-5:]}")

    def _build_label_map(self, instructions: List[IRInstruction]) -> Dict[str, int]:
        label_map = {}
        for i, instr in enumerate(instructions):
            if instr.type == IRType.LABEL:
                label_map[instr.operand] = i
        return label_map

    def _execute(self, instr: IRInstruction, pc: int, label_map: Dict[str, int]):
        if instr.type == IRType.LOAD_CONST:
            self.stack.append(instr.operand)
        elif instr.type == IRType.LOAD_VAR:
            if instr.operand in self.variables:
                self.stack.append(self.variables[instr.operand])
            else:
                raise RuntimeError(f"Undefined variable: {instr.operand}\nStack trace:\n{self._format_stack_trace()}")
        elif instr.type == IRType.STORE_VAR:
            if self.stack:
                val = self.stack.pop()
                self.variables[instr.operand] = val
                if self.debug:
                    print(f"[DEBUG] Variable {instr.operand} = {val}")
            else:
                self.variables[instr.operand] = None
        elif instr.type == IRType.CALL:
            func_name = instr.operand
            if func_name in self.functions:
                param_names = self.ir_module.func_params.get(func_name, [])
                call_args = []
                for _ in range(len(param_names)):
                    if self.stack:
                        call_args.insert(0, self.stack.pop())
                    else:
                        call_args.insert(0, None)
                self._add_call_frame(func_name, pc)
                retval = self._run_function(func_name, call_args)
                self._remove_call_frame()
                self.stack.append(retval)
            else:
                args = []
                while self.stack:
                    args.insert(0, self.stack.pop())
                if func_name == 'print':
                    print(*args)
                    self.output_buffer.extend(str(a) for a in args)
                else:
                    raise RuntimeError(f"Unknown function: {func_name}\nStack trace:\n{self._format_stack_trace()}")
        elif instr.type == IRType.RETURN:
            if self.stack:
                return 'return'
            return 'exit'
        elif instr.type == IRType.BINARY_OP:
            if len(self.stack) < 2:
                raise RuntimeError("Stack underflow for binary operation\nStack trace:\n" + self._format_stack_trace())
            b = self.stack.pop()
            a = self.stack.pop()
            op = instr.operand
            try:
                if op == '+':
                    self.stack.append(a + b)
                elif op == '-':
                    self.stack.append(a - b)
                elif op == '*':
                    self.stack.append(a * b)
                elif op == '/':
                    if b == 0:
                        raise RuntimeError(f"Division by zero\nStack trace:\n{self._format_stack_trace()}")
                    self.stack.append(a / b)
                elif op == '%':
                    self.stack.append(a % b)
                elif op == '<':
                    self.stack.append(a < b)
                elif op == '>':
                    self.stack.append(a > b)
                elif op == '<=':
                    self.stack.append(a <= b)
                elif op == '>=':
                    self.stack.append(a >= b)
                elif op == '==':
                    self.stack.append(a == b)
                elif op == '!=':
                    self.stack.append(a != b)
                elif op == 'in':
                    self.stack.append(a in b)
                elif op == '[]':
                    if isinstance(a, (dict, list)):
                        if isinstance(a, dict) and b in a:
                            self.stack.append(a[b])
                        elif isinstance(a, list):
                            try:
                                idx = int(b) if isinstance(b, str) else b
                                self.stack.append(a[idx])
                            except:
                                raise RuntimeError(f"Invalid index '{b}' for list")
                        else:
                            self.stack.append(None)
                    else:
                        raise RuntimeError(f"Cannot index non-container type: {type(a)}")
                elif op == '&&':
                    self.stack.append(a and b)
                elif op == '||':
                    self.stack.append(a or b)
                else:
                    raise RuntimeError(f"Unsupported binary operator: {op}\nStack trace:\n{self._format_stack_trace()}")
            except TypeError as e:
                raise RuntimeError(f"Type error in '{op}' operation: {e}\nStack trace:\n{self._format_stack_trace()}")
        elif instr.type == IRType.ALLOC:
            self.variables[instr.operand] = None
        elif instr.type == IRType.FREE:
            if instr.operand in self.variables:
                del self.variables[instr.operand]
        elif instr.type == IRType.JUMP:
            label = instr.operand
            if label in label_map:
                return label_map[label]
        elif instr.type == IRType.JUMP_IF_FALSE:
            label = instr.operand
            if self.stack:
                val = self.stack.pop()
                if val == False:
                    if label in label_map:
                        return label_map[label]
        elif instr.type == IRType.JUMP_IF_TRUE:
            label = instr.operand
            if self.stack:
                val = self.stack.pop()
                if val == True:
                    if label in label_map:
                        return label_map[label]
        elif instr.type == IRType.UNARY_OP:
            if len(self.stack) < 1:
                raise RuntimeError("Stack underflow for unary operation\nStack trace:\n" + self._format_stack_trace())
            operand = self.stack.pop()
            op = instr.operand
            if op == '!' or op == 'not':
                self.stack.append(not operand)
            else:
                raise RuntimeError(f"Unsupported unary operator: {op}\nStack trace:\n{self._format_stack_trace()}")
        elif instr.type == IRType.LOOP_BEGIN:
            pass
        elif instr.type == IRType.LOOP_END:
            pass
        elif instr.type == IRType.LABEL:
            pass
        elif instr.type == IRType.SPAWN_THREAD:
            func_name = instr.operand
            args = instr.arg1 or []
            from .scheduler import Scheduler
            if not hasattr(self, '_scheduler'):
                self._scheduler = Scheduler()
            task_id = self._scheduler.spawn(self._make_task_func(func_name), *args)
            self.stack.append(task_id)
        elif instr.type == IRType.WAIT:
            task_id = instr.operand
            if hasattr(self, '_scheduler'):
                self._scheduler.wait(task_id)
            else:
                raise RuntimeError(f"No scheduler available for task {task_id}\nStack trace:\n{self._format_stack_trace()}")
        elif instr.type == IRType.YIELD:
            from .scheduler import Scheduler
            if not hasattr(self, '_scheduler'):
                self._scheduler = Scheduler()
            self._scheduler.yield_()
        elif instr.type == IRType.AWAIT:
            func_name = instr.operand
            result = self._run_awaited_func(func_name, [])
            self.stack.append(result)
        elif instr.type == IRType.FFI_IMPORT:
            language = instr.operand
            module_path = instr.arg1
            as_name = instr.arg2
            self._handle_ffi_import(language, module_path, as_name)
        elif instr.type == IRType.FFI_CALL:
            language = instr.operand
            module_path = instr.arg1
            func_name = instr.arg2
            arg_count = instr.arg3 if instr.arg3 is not None else 0
            call_args = []
            for _ in range(arg_count):
                if self.stack:
                    call_args.insert(0, self.stack.pop())
            if self.debug:
                print(f"[DEBUG] FFI CALL: {language}:{module_path}.{func_name}({call_args})")
            result = self._handle_ffi_call(language, module_path, func_name, call_args)
            if self.debug:
                print(f"[DEBUG] FFI RESULT: {result}")
            self.stack.append(result)
        elif instr.type == IRType.FFI_GET_ATTR:
            # This handles dot access like data.attr
            module = instr.arg1
            attr = instr.arg2
            # For chained index access like data[key]["cell"], the module is actually an expression
            # We need to evaluate it from variables
            if module in self.variables:
                obj = self.variables[module]
                if isinstance(obj, dict) and attr in obj:
                    self.stack.append(obj[attr])
                elif isinstance(obj, list):
                    try:
                        idx = int(attr) if isinstance(attr, str) else attr
                        if 0 <= idx < len(obj):
                            self.stack.append(obj[idx])
                    except:
                        pass
                    if self.stack and self.stack[-1] is not None:
                        return
                    # Try FFI attribute access
                    try:
                        result = getattr(obj, attr, None)
                        self.stack.append(result)
                    except:
                        self.stack.append(None)
                else:
                    try:
                        result = getattr(obj, attr, None)
                        self.stack.append(result)
                    except:
                        self.stack.append(None)
            else:
                self.stack.append(None)
        elif instr.type == IRType.DEFER:
            # Store deferred call for later execution
            if self.defer_stack:
                func_name = instr.operand
                # Get any arguments that were pushed before DEFER
                if self.stack:
                    args = self.stack.pop() if self.stack else []
                    self.defer_stack[-1].append({'type': 'call', 'func': func_name, 'args': args if isinstance(args, list) else [args]})
                else:
                    self.defer_stack[-1].append({'type': 'call', 'func': func_name, 'args': []})
        elif instr.type == IRType.MATCH:
            # Match handling - patterns and labels are encoded in operand
            # For now, we rely on the compiler to have already done the comparisons
            pass
        elif instr.type == IRType.TRY:
            # Try block setup - handled in compilation
            pass
        return None

    def _handle_ffi_import(self, language: str, module_path: str, as_name: str):
        from .ffi import ffi_loader
        self.ffi = ffi_loader

        if language == 'python':
            ffi_loader.import_python_module(module_path, as_name)
        elif language == 'javascript':
            self.variables[as_name] = f'js_module:{module_path}'
        elif language == 'c':
            ffi_loader.load_c_module(module_path)
            self.variables[as_name] = f'c_module:{module_path}'
        elif language == 'rust':
            ffi_loader.load_rust_module(module_path)
            self.variables[as_name] = f'rust_module:{module_path}'
        elif language == 'go':
            self.variables[as_name] = f'go_module:{module_path}'
        elif language == 'cpp':
            ffi_loader.load_cpp_module(module_path)
            self.variables[as_name] = f'cpp_module:{module_path}'
        elif language == 'kotlin':
            ffi_loader.load_kotlin_module(module_path)
            self.variables[as_name] = f'kotlin_module:{module_path}'
        elif language == 'swift':
            ffi_loader.load_swift_module(module_path)
            self.variables[as_name] = f'swift_module:{module_path}'
        elif language == 'php':
            ffi_loader.load_php_module(module_path)
            self.variables[as_name] = f'php_module:{module_path}'
        elif language == 'ruby':
            ffi_loader.load_ruby_module(module_path)
            self.variables[as_name] = f'ruby_module:{module_path}'
        elif language == 'java':
            ffi_loader.load_java_module(module_path)
            self.variables[as_name] = f'java_module:{module_path}'
        elif language == 'csharp':
            ffi_loader.load_csharp_module(module_path)
            self.variables[as_name] = f'csharp_module:{module_path}'
        elif language == 'lua':
            ffi_loader.load_lua_module(module_path)
            self.variables[as_name] = f'lua_module:{module_path}'
        elif language == 'r':
            ffi_loader.load_r_module(module_path)
            self.variables[as_name] = f'r_module:{module_path}'
        elif language == 'julia':
            ffi_loader.load_julia_module(module_path)
            self.variables[as_name] = f'julia_module:{module_path}'
        elif language == 'haskell':
            ffi_loader.load_haskell_module(module_path)
            self.variables[as_name] = f'haskell_module:{module_path}'
        elif language == 'elixir':
            ffi_loader.load_elixir_module(module_path)
            self.variables[as_name] = f'elixir_module:{module_path}'
        elif language == 'dart':
            ffi_loader.load_dart_module(module_path)
            self.variables[as_name] = f'dart_module:{module_path}'
        elif language == 'zig':
            ffi_loader.load_zig_module(module_path)
            self.variables[as_name] = f'zig_module:{module_path}'
        elif language == 'typescript':
            ffi_loader.load_typescript_module(module_path)
            self.variables[as_name] = f'typescript_module:{module_path}'

    def _handle_ffi_call(self, language: str, module_path: str, func_name: str, args: list):
        from .ffi import ffi_loader, SynthLangFunction

        processed_args = []
        for arg in args:
            if func_name in self.functions and isinstance(arg, str):
                processed_args.append(SynthLangFunction(arg, self))
            else:
                processed_args.append(arg)

        try:
            if language == 'python':
                return asyncio.run(ffi_loader.call_python_async(module_path, func_name, processed_args, self))
            elif language == 'javascript':
                return ffi_loader.call_javascript(module_path, func_name, processed_args)
            elif language == 'c':
                return ffi_loader.call_c(module_path, func_name, processed_args)
            elif language == 'rust':
                return ffi_loader.call_c(module_path, func_name, processed_args)
            elif language == 'go':
                return ffi_loader.call_c(module_path, func_name, processed_args) if hasattr(ffi_loader, 'call_go') else ffi_loader.call_c(module_path, func_name, processed_args)
            elif language == 'cpp':
                return ffi_loader.call_cpp(module_path, func_name, processed_args)
            elif language == 'kotlin':
                return ffi_loader.call_kotlin(module_path, func_name, processed_args)
            elif language == 'swift':
                return ffi_loader.call_swift(module_path, func_name, processed_args)
            elif language == 'php':
                return ffi_loader.call_php(module_path, func_name, processed_args)
            elif language == 'ruby':
                return ffi_loader.call_ruby(module_path, func_name, processed_args)
            elif language == 'java':
                return ffi_loader.call_java(module_path, func_name, processed_args)
            elif language == 'csharp':
                return ffi_loader.call_csharp(module_path, func_name, processed_args)
            elif language == 'lua':
                return ffi_loader.call_lua(module_path, func_name, processed_args)
            elif language == 'r':
                return ffi_loader.call_r(module_path, func_name, processed_args)
            elif language == 'julia':
                return ffi_loader.call_julia(module_path, func_name, processed_args)
            elif language == 'haskell':
                return ffi_loader.call_c(module_path, func_name, processed_args)
            elif language == 'elixir':
                return ffi_loader.call_elixir(module_path, func_name, processed_args)
            elif language == 'dart':
                return ffi_loader.call_dart(module_path, func_name, processed_args) if hasattr(ffi_loader, 'call_dart') else ffi_loader.call_c(module_path, func_name, processed_args)
            elif language == 'zig':
                return ffi_loader.call_c(module_path, func_name, processed_args)
            elif language == 'typescript':
                return ffi_loader.call_typescript(module_path, func_name, processed_args)
            else:
                raise RuntimeError(f"Unsupported FFI language: {language}")
        except ImportError as e:
            raise RuntimeError(f"FFIError: Python module '{module_path}' not found. Did you run 'slang pip install {module_path}'?") from e
        except AttributeError as e:
            raise RuntimeError(f"FFIError: Function '{func_name}' not found in module '{module_path}'") from e
        except Exception as e:
            raise RuntimeError(f"FFIError: {language} module '{module_path}': {e}") from e

    def _handle_ffi_get_attr(self, module_name: str, attr_name: str):
        # Handle dictionary/list access via [] operator
        if '[' in attr_name or attr_name == '[]':
            # This is actually an index operation, not an attr lookup
            # The module_name contains the object and attr_name contains the key
            obj_name = module_name
            idx = attr_name
            if obj_name in self.variables:
                obj = self.variables[obj_name]
                if isinstance(obj, dict) and idx in obj:
                    return obj[idx]
                try:
                    return obj[idx]
                except:
                    pass
            return None
        try:
            return getattr(self.variables.get(module_name, {}), attr_name, None)
        except:
            return None

    def _make_task_func(self, func_name: str):
        """Create a callable task function for threading."""
        def task_func(*args):
            if func_name in self.functions:
                return self._run_function(func_name, list(args))
            raise RuntimeError(f"Function '{func_name}' not found for threading")
        return task_func

    def _run_awaited_func(self, func_name: str, args: list) -> Any:
        """Run a function and return its result for await."""
        if func_name in self.functions:
            return self._run_function(func_name, args)
        raise RuntimeError(f"Await function '{func_name}' not found\nStack trace:\n{self._format_stack_trace()}")

    def _handle_exception(self) -> Optional[int]:
        """Handle an exception by jumping to the appropriate handler."""
        if self.exception_stack:
            handler_label = self.exception_stack.pop()
            return None  # Returns None to continue normal flow after defer unwind
        return None


if __name__ == '__main__':
    from synthlang.lexer import Lexer
    from synthlang.parser import Parser
    from synthlang.compiler import Compiler

    code = '''let x = 5
let y = 10
'''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler()
    ir = compiler.compile(ast)
    vm = VM(ir)
    vm.run()
    print(vm.variables)