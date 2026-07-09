"""SynthLang VM - Stack-based interpreter for IR."""
import asyncio
import inspect
from typing import Any, List, Dict, Optional
from .ir import IRModule, IRInstruction, IRType
from .gc import GC, RCManager


class SynthLangKwargs(dict):
    pass


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


class Channel:
    def __init__(self, size: int = 0):
        self.size = size
        self.buffer: List[Any] = []
        self.lock = asyncio.Lock() if asyncio else None
        self.send_events: Dict[int, Any] = {}
        self.recv_events: Dict[int, Any] = {}

    async def send(self, value: Any):
        if self.size > 0 and len(self.buffer) >= self.size:
            await asyncio.sleep(0.001)
        self.buffer.append(value)

    def send_sync(self, value: Any):
        self.buffer.append(value)

    async def recv(self) -> Any:
        if len(self.buffer) == 0:
            raise RuntimeError("Channel is empty")
        return self.buffer.pop(0)

    def recv_sync(self) -> Any:
        if len(self.buffer) == 0:
            raise RuntimeError("Channel is empty")
        return self.buffer.pop(0)


class SynthLangPanic(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class VM:
    def __init__(self, ir_module: IRModule, debug: bool = False, source_map: Dict[str, Any] = None, memory_mode: str = "gc"):
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
        self.defer_stack: List[List[Any]] = []
        self.exception_stack: List[str] = []
        self.channels: Dict[str, Channel] = {}
        self.memory_mode = memory_mode
        self.rc_manager = RCManager() if memory_mode == "rc" else None
        self.gc = GC(self) if memory_mode == "gc" else None

    def _track_rc(self, name: str, value: Any):
        """Track variable for reference counting."""
        if self.rc_manager and name not in self.rc_manager.objects:
            self.rc_manager.create(name, value)  # Channel storage for concurrency

    def run(self):
        is_main_async = False
        if hasattr(self.ir_module, 'async_funcs'):
            is_main_async = self.ir_module.async_funcs.get('main', False)
        
        if 'main' in self.functions:
            if is_main_async:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running (e.g. from an FFI async callback), run it as task
                    task = loop.create_task(self._run_function('main', []))
                    # Wait for task completion blocking-ly or return task (here we run it via loop block if possible)
                    # Let's run it by calling a sync wrapper or using asyncio.run if no loop running
                    # Best approach for nested run inside active loop is creating a future and waiting:
                    try:
                        import nest_asyncio
                        nest_asyncio.apply()
                    except ImportError:
                        pass
                    loop.run_until_complete(self._run_function('main', []))
                else:
                    asyncio.run(self._run_function('main', []))
            else:
                self._run_sync_function('main', [])
        return self.variables

    def _run_sync_function(self, name: str, args: List[Any]) -> Any:
        self.current_func = name
        instructions = self.functions[name]
        func_params = self.ir_module.func_params.get(name, [])

        label_map = self._build_label_map(instructions)
        self.defer_stack.append([])

        for i, arg in enumerate(args):
            if i < len(func_params):
                self.variables[func_params[i]] = arg

        pc = 0
        result = None

        while pc < len(instructions):
            try:
                instr = instructions[pc]
                if self.debug:
                    self._debug_print(instr, pc)
                
                # Check if FFI call is async, if so we raise error in sync mode
                if instr.type == IRType.CALL and instr.operand in self.functions:
                    is_target_async = False
                    if hasattr(self.ir_module, 'async_funcs'):
                        is_target_async = self.ir_module.async_funcs.get(instr.operand, False)
                    if is_target_async:
                        raise RuntimeError(f"Cannot call async function '{instr.operand}' from sync function '{name}'. Use 'async fn'.")

                # Run execute (sync wrapper)
                # Since _execute is now async, we run it using a helper or loop if it yields coroutine
                coro = self._execute(instr, pc, label_map)
                if inspect.iscoroutine(coro):
                    loop = asyncio.get_event_loop()
                    outcome = loop.run_until_complete(coro)
                else:
                    outcome = coro

                if outcome is not None:
                    if outcome == 'return' and self.stack:
                        result = self.stack.pop()
                        pc = len(instructions)
                    elif outcome == 'exception':
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
            except SynthLangPanic as e:
                if self.exception_stack:
                    handler = self.exception_stack[-1]
                    if len(self.call_stack) > handler['call_stack_depth']:
                        raise e
                    self.exception_stack.pop()
                    while len(self.defer_stack) > handler['defer_stack_depth']:
                        self.defer_stack.pop()
                    self.stack.append(e.message)
                    if handler['label'] in label_map:
                        pc = label_map[handler['label']]
                    else:
                        raise RuntimeError(f"Handler label '{handler['label']}' not found in function '{name}'")
                else:
                    raise RuntimeError(f"Unhandled Panic: {e.message}\nStack trace:\n{self._format_stack_trace()}")

        if self.defer_stack:
            deferred = self.defer_stack.pop()
            for deferred_call in reversed(deferred):
                if deferred_call.get('type') == 'call':
                    func_name = deferred_call.get('func')
                    call_args = deferred_call.get('args', [])
                    if func_name in self.functions:
                        self._run_sync_function(func_name, call_args)
                    elif func_name == 'print':
                        print(*call_args)
        
        for param in func_params:
            if param in self.variables:
                del self.variables[param]
        return result

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

    async def _run_function(self, name: str, args: List[Any]) -> Any:
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
            try:
                instr = instructions[pc]
                if self.debug:
                    self._debug_print(instr, pc)
                outcome = await self._execute(instr, pc, label_map)
                if outcome is not None:
                    if outcome == 'return' and self.stack:
                        result = self.stack.pop()
                        pc = len(instructions)
                    elif outcome == 'exception':
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
            except SynthLangPanic as e:
                if self.exception_stack:
                    handler = self.exception_stack[-1]
                    if len(self.call_stack) > handler['call_stack_depth']:
                        raise e
                    self.exception_stack.pop()
                    while len(self.defer_stack) > handler['defer_stack_depth']:
                        self.defer_stack.pop()
                    self.stack.append(e.message)
                    if handler['label'] in label_map:
                        pc = label_map[handler['label']]
                    else:
                        raise RuntimeError(f"Handler label '{handler['label']}' not found in function '{name}'")
                else:
                    raise RuntimeError(f"Unhandled Panic: {e.message}\nStack trace:\n{self._format_stack_trace()}")

        # Execute deferred calls on function exit
        if self.defer_stack:
            deferred = self.defer_stack.pop()
            for deferred_call in reversed(deferred):
                if deferred_call.get('type') == 'call':
                    func_name = deferred_call.get('func')
                    call_args = deferred_call.get('args', [])
                    try:
                        if func_name in self.functions:
                            await self._run_function(func_name, call_args)
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

    async def _execute(self, instr: IRInstruction, pc: int, label_map: Dict[str, int]):
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
                try:
                    retval = await self._run_function(func_name, call_args)
                finally:
                    self._remove_call_frame()
                self.stack.append(retval)
            else:
                args = []
                while self.stack:
                    args.insert(0, self.stack.pop())
                if func_name == 'print':
                    print(*args)
                    self.output_buffer.extend(str(a) for a in args)
                elif func_name == 'panic':
                    msg = args[0] if args else "Panic"
                    raise SynthLangPanic(str(msg))
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
            elif op == '-':
                self.stack.append(-operand)
            elif op == '+':
                self.stack.append(+operand)
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
            # Get function/coroutine to await
            if func_name in self.functions:
                result = await self._run_function(func_name, [])
            elif func_name in self.variables:
                target = self.variables[func_name]
                if inspect.iscoroutine(target):
                    result = await target
                elif callable(target):
                    res = target()
                    if inspect.iscoroutine(res):
                        result = await res
                    else:
                        result = res
                else:
                    result = target
            else:
                # If there's a coroutine on top of the stack, await it
                if self.stack:
                    top = self.stack.pop()
                    if inspect.iscoroutine(top):
                        result = await top
                    else:
                        result = top
                else:
                    result = None
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
            result = await self._handle_ffi_call(language, module_path, func_name, call_args)
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
                        obj_curr = obj
                        for part in attr.split('.'):
                            obj_curr = getattr(obj_curr, part, None)
                        self.stack.append(obj_curr)
                    except:
                        self.stack.append(None)
                else:
                    try:
                        obj_curr = obj
                        for part in attr.split('.'):
                            obj_curr = getattr(obj_curr, part, None)
                        self.stack.append(obj_curr)
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
            pass
        elif instr.type == IRType.TRY:
            if instr.operand:
                self.exception_stack.append({
                    'label': instr.operand,
                    'call_stack_depth': len(self.call_stack),
                    'defer_stack_depth': len(self.defer_stack)
                })
            else:
                if self.exception_stack:
                    self.exception_stack.pop()
        elif instr.type == IRType.EXEC_CODE_BLOCK:
            lang = instr.operand
            code = instr.arg1
            result = self._execute_inline_code(lang, code)
            self.stack.append(result)
        elif instr.type == IRType.MAKE_CHANNEL:
            size = instr.operand if instr.operand else 0
            chan = Channel(size)
            chan_name = f"chan_{len(self.channels)}"
            self.channels[chan_name] = chan
            self.stack.append(chan_name)
        elif instr.type == IRType.BUILD_KWARGS:
            keys = instr.operand or []
            kwargs = SynthLangKwargs()
            for key in reversed(keys):
                if self.stack:
                    kwargs[key] = self.stack.pop()
                else:
                    kwargs[key] = None
            self.stack.append(kwargs)
        elif instr.type == IRType.CHAN_SEND:
            chan_expr = instr.operand
            if self.stack:
                value = self.stack.pop()
                # chan_expr could be a variable name or expression result
                chan_name = chan_expr
                if '_' in chan_expr or 'chan' in chan_expr:
                    if chan_expr in self.variables:
                        chan_name = self.variables[chan_expr]
                if chan_name in self.channels:
                    self.channels[chan_name].send_sync(value)
                elif chan_name in self.variables and isinstance(self.variables[chan_name], Channel):
                    self.variables[chan_name].send_sync(value)
        elif instr.type == IRType.CHAN_RECV:
            chan_expr = instr.operand
            chan_name = chan_expr
            if chan_expr in self.variables and isinstance(self.variables[chan_expr], Channel):
                chan_name = chan_expr
            if chan_name in self.channels:
                value = self.channels[chan_name].recv_sync()
                self.stack.append(value)
            elif chan_name in self.variables and isinstance(self.variables[chan_name], Channel):
                value = self.variables[chan_name].recv_sync()
                self.stack.append(value)
            elif '<-' in str(chan_expr):
                # Handle <- expr syntax
                expr = chan_expr.replace('<- ', '').strip()
                if expr in self.variables and isinstance(self.variables[expr], Channel):
                    value = self.variables[expr].recv_sync()
                    self.stack.append(value)
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

    async def _handle_ffi_call(self, language: str, module_path: str, func_name: str, args: list):
        from .ffi import ffi_loader, SynthLangFunction

        processed_args = []
        kwargs = {}
        if args and isinstance(args[-1], SynthLangKwargs):
            kwargs = args.pop()

        for arg in args:
            if func_name in self.functions and isinstance(arg, str):
                processed_args.append(SynthLangFunction(arg, self))
            else:
                processed_args.append(arg)

        try:
            if language == 'python':
                return await ffi_loader.call_python_async(module_path, func_name, processed_args, self, kwargs=kwargs)
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

    async def _run_awaited_func(self, func_name: str, args: list) -> Any:
        """Run a function and return its result for await."""
        if func_name in self.functions:
            return await self._run_function(func_name, args)
        raise RuntimeError(f"Await function '{func_name}' not found\nStack trace:\n{self._format_stack_trace()}")

    def _handle_exception(self) -> Optional[int]:
        if self.exception_stack:
            handler_label = self.exception_stack.pop()
            return None
        return None

    def _execute_inline_code(self, lang: str, code: str) -> Any:
        """Execute inline code block from another language."""
        import tempfile
        import json
        import subprocess
        import os

        if lang == 'py':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    return result.stdout.strip()
                raise RuntimeError(f"Python inline code error: {result.stderr}")
            except FileNotFoundError:
                os.unlink(temp_file) if os.path.exists(temp_file) else None
                raise RuntimeError("'python' not found - Python inline code requires Python installed")
        elif lang == 'r':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['Rscript', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    return result.stdout.strip()
                raise RuntimeError(f"R inline code error: {result.stderr}")
            except FileNotFoundError:
                os.unlink(temp_file) if os.path.exists(temp_file) else None
                raise RuntimeError("'Rscript' not found - R inline code requires R installed")
        elif lang == 'rust':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                exe_file = temp_file.replace('.rs', '.exe')
                compile_result = subprocess.run(
                    ['rustc', temp_file, '-o', exe_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                os.unlink(temp_file)
                if compile_result.returncode != 0:
                    raise RuntimeError(f"Rust compilation error: {compile_result.stderr}")
                run_result = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(exe_file)
                if run_result.returncode == 0:
                    return run_result.stdout.strip()
                raise RuntimeError(f"Rust inline code error: {run_result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'rustc' not found - Rust inline code requires Rust installed")
        elif lang == 'go':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                exe_file = temp_file.replace('.go', '')
                compile_result = subprocess.run(
                    ['go', 'run', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                os.unlink(temp_file)
                if compile_result.returncode == 0:
                    return compile_result.stdout.strip()
                raise RuntimeError(f"Go inline code error: {compile_result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'go' not found - Go inline code requires Go installed")
        elif lang == 'js' or lang == 'ts':
            js_code = code
            if lang == 'ts':
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                try:
                    js_file = temp_file.replace('.ts', '.js')
                    subprocess.run(['tsc', temp_file, '--outDir', os.path.dirname(temp_file) or '.'], capture_output=True)
                    with open(js_file, 'r') as f:
                        js_code = f.read()
                except FileNotFoundError:
                    raise RuntimeError("'tsc' not found - TypeScript inline code requires TypeScript")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(js_code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout.strip())
                    except:
                        return result.stdout.strip()
                raise RuntimeError(f"JavaScript inline code error: {result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'node' not found - JavaScript inline code requires Node.js")
        elif lang == 'cpp':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                exe_file = temp_file.replace('.cpp', '.exe')
                compile_result = subprocess.run(
                    ['g++', '-o', exe_file, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                os.unlink(temp_file)
                if compile_result.returncode != 0:
                    raise RuntimeError(f"C++ compilation error: {compile_result.stderr}")
                run_result = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(exe_file)
                if run_result.returncode == 0:
                    return run_result.stdout.strip()
                raise RuntimeError(f"C++ inline code error: {run_result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'g++' not found - C++ inline code requires g++")
        elif lang == 'c':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                exe_file = temp_file.replace('.c', '.exe')
                compile_result = subprocess.run(
                    ['gcc', '-o', exe_file, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                os.unlink(temp_file)
                if compile_result.returncode != 0:
                    raise RuntimeError(f"C compilation error: {compile_result.stderr}")
                run_result = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(exe_file)
                if run_result.returncode == 0:
                    return run_result.stdout.strip()
                raise RuntimeError(f"C inline code error: {run_result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'gcc' not found - C inline code requires gcc")
        elif lang == 'php':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['php', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout.strip())
                    except:
                        return result.stdout.strip()
                raise RuntimeError(f"PHP inline code error: {result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'php' not found - PHP inline code requires PHP installed")
        elif lang == 'ruby':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rb', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['ruby', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout.strip())
                    except:
                        return result.stdout.strip()
                raise RuntimeError(f"Ruby inline code error: {result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'ruby' not found - Ruby inline code requires Ruby installed")
        elif lang == 'lua':
            try:
                import lupa
                lua = lupa.LuaRuntime()
                result = lua.execute(code)
                if hasattr(result, 'pop'):
                    return result
                return str(result) if result else None
            except ImportError:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                try:
                    result = subprocess.run(
                        ['lua', temp_file],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    os.unlink(temp_file)
                    if result.returncode == 0:
                        return result.stdout.strip()
                    raise RuntimeError(f"Lua inline code error: {result.stderr}")
                except FileNotFoundError:
                    raise RuntimeError("'lua' or 'lupa' not found - Lua inline code requires Lua or lupa package")
        elif lang == 'julia':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jl', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['julia', '-q', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout.strip())
                    except:
                        return result.stdout.strip()
                raise RuntimeError(f"Julia inline code error: {result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'julia' not found - Julia inline code requires Julia installed")
        elif lang == 'haskell':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.hs', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                exe_file = temp_file.replace('.hs', '')
                compile_result = subprocess.run(
                    ['ghc', '-o', exe_file, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                os.unlink(temp_file)
                if compile_result.returncode != 0:
                    raise RuntimeError(f"Haskell compilation error: {compile_result.stderr}")
                run_result = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(exe_file)
                if run_result.returncode == 0:
                    try:
                        return json.loads(run_result.stdout.strip())
                    except:
                        return run_result.stdout.strip()
                raise RuntimeError(f"Haskell inline code error: {run_result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'ghc' not found - Haskell inline code requires GHC installed")
        elif lang == 'elixir':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.exs', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['elixir', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout.strip())
                    except:
                        return result.stdout.strip()
                raise RuntimeError(f"Elixir inline code error: {result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'elixir' not found - Elixir inline code requires Elixir installed")
        elif lang == 'dart':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.dart', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['dart', 'run', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout.strip())
                    except:
                        return result.stdout.strip()
                raise RuntimeError(f"Dart inline code error: {result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'dart' not found - Dart inline code requires Dart installed")
        elif lang == 'zig':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.zig', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                exe_file = temp_file.replace('.zig', '')
                compile_result = subprocess.run(
                    ['zig', 'build-exe', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if compile_result.returncode != 0:
                    raise RuntimeError(f"Zig compilation error: {compile_result.stderr}")
                run_result = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                os.unlink(exe_file)
                if run_result.returncode == 0:
                    return run_result.stdout.strip()
                raise RuntimeError(f"Zig inline code error: {run_result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'zig' not found - Zig inline code requires Zig installed")
        elif lang == 'kotlin':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.kt', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                exe_file = temp_file.replace('.kt', '')
                compile_result = subprocess.run(
                    ['kotlinc', '-script', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                os.unlink(temp_file)
                if compile_result.returncode == 0:
                    try:
                        return json.loads(compile_result.stdout.strip())
                    except:
                        return compile_result.stdout.strip()
                raise RuntimeError(f"Kotlin inline code error: {compile_result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'kotlinc' not found - Kotlin inline code requires Kotlin installed")
        elif lang == 'swift':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                result = subprocess.run(
                    ['swift', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout.strip())
                    except:
                        return result.stdout.strip()
                raise RuntimeError(f"Swift inline code error: {result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'swift' not found - Swift inline code requires Swift installed")
        elif lang == 'java':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                import jpype
                if not jpype.is_started():
                    jpype.startJVM()
                result = subprocess.run(
                    ['javac', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode != 0:
                    raise RuntimeError(f"Java compilation error: {result.stderr}")
                run_result = subprocess.run(
                    ['java', '-cp', os.path.dirname(temp_file) or '.', os.path.basename(temp_file).replace('.java', '')],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                if run_result.returncode == 0:
                    try:
                        return json.loads(run_result.stdout.strip())
                    except:
                        return run_result.stdout.strip()
                raise RuntimeError(f"Java inline code error: {run_result.stderr}")
            except ImportError:
                raise RuntimeError("Java inline code requires jpype package")
            except FileNotFoundError:
                raise RuntimeError("'javac'/'java' not found - Java inline code requires JDK")
        elif lang == 'asm':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
                f.write(code)
                temp_file = f.name
            try:
                exe_file = temp_file.replace('.s', '.exe')
                if platform.system() == 'Windows':
                    compile_result = subprocess.run(
                        ['ml64', '/c', temp_file],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                else:
                    compile_result = subprocess.run(
                        ['gcc', '-o', exe_file, temp_file],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                if compile_result.returncode != 0:
                    raise RuntimeError(f"Assembly compilation error: {compile_result.stderr}")
                run_result = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                os.unlink(temp_file)
                os.unlink(exe_file)
                if run_result.returncode == 0:
                    return run_result.stdout.strip()
                raise RuntimeError(f"Assembly inline code error: {run_result.stderr}")
            except FileNotFoundError:
                raise RuntimeError("'gcc' or 'ml64' not found - Assembly inline code requires a compiler")
        else:
            raise RuntimeError(f"Unsupported inline code language: {lang}")


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