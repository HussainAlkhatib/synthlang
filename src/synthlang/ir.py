"""SynthLang Intermediate Representation - Linear IR for the VM."""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional, Dict, List


class IRType(Enum):
    LOAD_CONST = auto()
    LOAD_VAR = auto()
    STORE_VAR = auto()
    CALL = auto()
    FFI_GET_ATTR = auto()
    FFI_CALL = auto()
    FFI_IMPORT = auto()
    RETURN = auto()
    JUMP = auto()
    JUMP_IF_FALSE = auto()
    JUMP_IF_TRUE = auto()
    LOOP = auto()
    LOOP_BEGIN = auto()
    LOOP_END = auto()
    ITER = auto()
    ITER_INIT = auto()
    ALLOC = auto()
    FREE = auto()
    INCREMENT_RC = auto()
    DECREMENT_RC = auto()
    SPAWN_THREAD = auto()
    WAIT = auto()
    YIELD = auto()
    AWAIT = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    NOP = auto()
    LABEL = auto()
    DEFER = auto()
    MATCH = auto()
    TRY = auto()
    EXEC_CODE_BLOCK = auto()
    MAKE_CHANNEL = auto()
    CHAN_SEND = auto()
    CHAN_RECV = auto()
    BUILD_KWARGS = auto()


@dataclass
class IRInstruction:
    type: IRType
    operand: Any = None
    arg1: Any = None
    arg2: Any = None
    arg3: Any = None
    result: Any = None

    def __repr__(self):
        parts = [f"{self.type.name}"]
        if self.operand is not None:
            parts.append(f"operand={self.operand}")
        if self.arg1 is not None:
            parts.append(f"arg1={self.arg1}")
        if self.arg2 is not None:
            parts.append(f"arg2={self.arg2}")
        if self.arg3 is not None:
            parts.append(f"arg3={self.arg3}")
        if self.result is not None:
            parts.append(f"result={self.result}")
        return f"IR({', '.join(parts)})"


class IRModule:
    def __init__(self, name: str = "main"):
        self.name = name
        self.functions: dict = {}
        self.variables: dict = {}
        self.imports: Dict[str, tuple] = {}
        self.annotations: list = []
        self.func_params: Dict[str, List[str]] = {}
        self.annotation_registry: Dict[str, Any] = {}

    def add_function(self, name: str, instructions: list):
        self.functions[name] = instructions

    def add_variable(self, name: str, type_str: str = None):
        self.variables[name] = type_str

    def register_annotation(self, annotation_name: str, target: str):
        self.annotation_registry[annotation_name] = target

    def __repr__(self):
        return f"IRModule({self.name}, {len(self.functions)} functions, {len(self.variables)} variables)"


def load_const(value: Any) -> IRInstruction:
    return IRInstruction(IRType.LOAD_CONST, operand=value)


def load_var(name: str) -> IRInstruction:
    return IRInstruction(IRType.LOAD_VAR, operand=name)


def store_var(name: str) -> IRInstruction:
    return IRInstruction(IRType.STORE_VAR, operand=name)


def call(func: str, args: list) -> IRInstruction:
    return IRInstruction(IRType.CALL, operand=func, arg1=args)


def ret() -> IRInstruction:
    return IRInstruction(IRType.RETURN)


def jump(label: str, result: str = None) -> IRInstruction:
    return IRInstruction(IRType.JUMP, operand=label, result=result)


def jump_if_false(label: str) -> IRInstruction:
    return IRInstruction(IRType.JUMP_IF_FALSE, operand=label)


def jump_if_true(label: str) -> IRInstruction:
    return IRInstruction(IRType.JUMP_IF_TRUE, operand=label)


def loop_begin(label: str) -> IRInstruction:
    return IRInstruction(IRType.LOOP_BEGIN, operand=label)


def loop_end(label: str) -> IRInstruction:
    return IRInstruction(IRType.LOOP_END, operand=label)


def alloc(name: str) -> IRInstruction:
    return IRInstruction(IRType.ALLOC, operand=name)


def free(name: str) -> IRInstruction:
    return IRInstruction(IRType.FREE, operand=name)


def increment_rc(name: str) -> IRInstruction:
    return IRInstruction(IRType.INCREMENT_RC, operand=name)


def decrement_rc(name: str) -> IRInstruction:
    return IRInstruction(IRType.DECREMENT_RC, operand=name)


def spawn_thread(func: str, args: list) -> IRInstruction:
    return IRInstruction(IRType.SPAWN_THREAD, operand=func, arg1=args)


def wait(task_id: int) -> IRInstruction:
    return IRInstruction(IRType.WAIT, operand=task_id)


def yield_op() -> IRInstruction:
    return IRInstruction(IRType.YIELD)


def await_op(func: str) -> IRInstruction:
    return IRInstruction(IRType.AWAIT, operand=func)


def binary_op(op: str) -> IRInstruction:
    return IRInstruction(IRType.BINARY_OP, operand=op)


def unary_op(op: str) -> IRInstruction:
    return IRInstruction(IRType.UNARY_OP, operand=op)


def iter_init(var_name: str) -> IRInstruction:
    return IRInstruction(IRType.ITER_INIT, operand=var_name)


def ffi_import(language: str, module: str, as_name: str = None) -> IRInstruction:
    return IRInstruction(IRType.FFI_IMPORT, operand=language, arg1=module, arg2=as_name)


def ffi_get_attr(module: str, attr: str) -> IRInstruction:
    return IRInstruction(IRType.FFI_GET_ATTR, operand='python', arg1=module, arg2=attr)


def ffi_call(language: str, module: str, func: str, args: list) -> IRInstruction:
    return IRInstruction(IRType.FFI_CALL, operand=language, arg1=module, arg2=func, arg3=args)


def label(name: str) -> IRInstruction:
    return IRInstruction(IRType.LABEL, operand=name)

def defer_op(expr: str) -> IRInstruction:
    return IRInstruction(IRType.DEFER, operand=expr)

def match_op(cases: list) -> IRInstruction:
    return IRInstruction(IRType.MATCH, operand=str(cases))

def try_op() -> IRInstruction:
    return IRInstruction(IRType.TRY)

def exec_code_block(lang: str, code: str) -> IRInstruction:
    return IRInstruction(IRType.EXEC_CODE_BLOCK, operand=lang, arg1=code)

def make_channel(size: int = 0) -> IRInstruction:
    return IRInstruction(IRType.MAKE_CHANNEL, operand=size)

def chan_send(chan_name: str) -> IRInstruction:
    return IRInstruction(IRType.CHAN_SEND, operand=chan_name)

def chan_recv(chan_name: str) -> IRInstruction:
    return IRInstruction(IRType.CHAN_RECV, operand=chan_name)

def build_kwargs(keys: list) -> IRInstruction:
    return IRInstruction(IRType.BUILD_KWARGS, operand=keys)