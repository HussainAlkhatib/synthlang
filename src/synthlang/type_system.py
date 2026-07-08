"""SynthLang Type System - Type hierarchy and inference."""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List, Optional, Dict, Set


class TypeKind(Enum):
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    VOID = auto()
    ARRAY = auto()
    DICT = auto()
    STRUCT = auto()
    INTERFACE = auto()
    FUNCTION = auto()
    GENERIC = auto()
    UNKNOWN = auto()


@dataclass
class Type:
    kind: TypeKind
    name: str = ""
    params: List['Type'] = None

    def __post_init__(self):
        if self.params is None:
            self.params = []

    def __repr__(self):
        if self.params:
            return f"{self.name}<{', '.join(str(p) for p in self.params)}>"
        return self.name or self.kind.name


@dataclass
class StructField:
    name: str
    type: Type


@dataclass
class StructType(Type):
    fields: List[StructField] = None

    def __post_init__(self):
        super().__post_init__()
        if self.fields is None:
            self.fields = []


@dataclass  
class FunctionType(Type):
    params: List[Type] = None
    return_type: Type = None


@dataclass
class GenericType(Type):
    type_param: str = ""


PRIMITIVE_TYPES = {
    'int': Type(TypeKind.INT, 'int'),
    'float': Type(TypeKind.FLOAT, 'float'),
    'str': Type(TypeKind.STRING, 'str'),
    'string': Type(TypeKind.STRING, 'str'),
    'bool': Type(TypeKind.BOOL, 'bool'),
    'void': Type(TypeKind.VOID, 'void'),
}


class TypeInferer:
    def __init__(self):
        self.variables: Dict[str, Type] = {}
        self.functions: Dict[str, FunctionType] = {}
        self.structs: Dict[str, StructType] = {}
        self.errors: List[str] = []

    def infer_literal(self, value: Any) -> Type:
        if isinstance(value, bool):
            return PRIMITIVE_TYPES['bool']
        elif isinstance(value, int):
            return PRIMITIVE_TYPES['int']
        elif isinstance(value, float):
            return PRIMITIVE_TYPES['float']
        elif isinstance(value, str):
            return PRIMITIVE_TYPES['str']
        elif isinstance(value, list):
            return Type(TypeKind.ARRAY, 'array', [PRIMITIVE_TYPES['unknown']])
        elif isinstance(value, dict):
            return Type(TypeKind.DICT, 'dict')
        return Type(TypeKind.UNKNOWN, 'unknown')

    def infer_binary_op(self, left_type: Type, op: str, right_type: Type) -> Type:
        if left_type.kind in (TypeKind.INT, TypeKind.FLOAT) and right_type.kind in (TypeKind.INT, TypeKind.FLOAT):
            if op in ('+', '-', '*', '/', '%'):
                return left_type if left_type.kind == TypeKind.FLOAT else PRIMITIVE_TYPES['int']
            return PRIMITIVE_TYPES['bool']
        if left_type.kind == TypeKind.STRING and op == '+':
            return PRIMITIVE_TYPES['str']
        return PRIMITIVE_TYPES['unknown']

    def infer_call(self, func_name: str, arg_types: List[Type]) -> Optional[Type]:
        if func_name in self.functions:
            func_type = self.functions[func_name]
            return func_type.return_type
        return None

    def register_variable(self, name: str, type_hint: Optional[Type] = None):
        if type_hint:
            self.variables[name] = type_hint

    def register_function(self, name: str, params: List[Dict], return_type: Optional[Type] = None):
        param_types = [PRIMITIVE_TYPES.get(p.get('type', 'unknown'), Type(TypeKind.UNKNOWN, 'unknown')) for p in params]
        self.functions[name] = FunctionType(
            kind=TypeKind.FUNCTION,
            name=name,
            params=param_types,
            return_type=return_type or Type(TypeKind.UNKNOWN, 'unknown')
        )

    def get_variable_type(self, name: str) -> Type:
        return self.variables.get(name, Type(TypeKind.UNKNOWN, 'unknown'))


if __name__ == '__main__':
    inferer = TypeInferer()
    print(f"Type system loaded - {len(PRIMITIVE_TYPES)} primitive types")