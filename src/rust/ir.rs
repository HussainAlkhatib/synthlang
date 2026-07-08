use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum IRType {
    LOAD_CONST,
    LOAD_VAR,
    STORE_VAR,
    CALL,
    FFI_GET_ATTR,
    FFI_CALL,
    FFI_IMPORT,
    RETURN,
    JUMP,
    JUMP_IF_FALSE,
    JUMP_IF_TRUE,
    LOOP,
    LOOP_BEGIN,
    LOOP_END,
    ITER,
    ITER_INIT,
    ALLOC,
    FREE,
    INCREMENT_RC,
    DECREMENT_RC,
    SPAWN_THREAD,
    WAIT,
    YIELD,
    AWAIT,
    BINARY_OP,
    UNARY_OP,
    NOP,
    LABEL,
    DEFER,
    MATCH,
    TRY,
}

impl Default for IRType {
    fn default() -> Self {
        IRType::NOP
    }
}

#[derive(Debug, Clone, Default)]
pub struct IRInstruction {
    pub ty: IRType,
    pub operand: Option<String>,
    pub arg1: Option<String>,
    pub arg2: Option<String>,
    pub arg3: Option<String>,
}

impl IRInstruction {
    pub fn new(ty: IRType) -> Self {
        IRInstruction { ty, operand: None, arg1: None, arg2: None, arg3: None }
    }

    pub fn with_operand(ty: IRType, operand: impl Into<String>) -> Self {
        IRInstruction { ty, operand: Some(operand.into()), arg1: None, arg2: None, arg3: None }
    }
}

#[derive(Debug, Clone)]
pub struct IRModule {
    pub name: String,
    pub functions: HashMap<String, Vec<IRInstruction>>,
    pub variables: HashMap<String, Option<String>>,
    pub imports: HashMap<String, (String, String)>,
    pub annotation_registry: HashMap<String, String>,
    pub func_params: HashMap<String, Vec<String>>,
}

impl Default for IRModule {
    fn default() -> Self {
        IRModule {
            name: "main".to_string(),
            functions: HashMap::new(),
            variables: HashMap::new(),
            imports: HashMap::new(),
            annotation_registry: HashMap::new(),
            func_params: HashMap::new(),
        }
    }
}

impl IRModule {
    pub fn add_function(&mut self, name: &str, instructions: Vec<IRInstruction>) {
        self.functions.insert(name.to_string(), instructions);
    }

    pub fn add_variable(&mut self, name: &str, type_str: Option<&str>) {
        self.variables.insert(name.to_string(), type_str.map(|s| s.to_string()));
    }
}

pub fn load_const(value: &str) -> IRInstruction { IRInstruction::with_operand(IRType::LOAD_CONST, value) }
pub fn load_var(name: &str) -> IRInstruction { IRInstruction::with_operand(IRType::LOAD_VAR, name) }
pub fn store_var(name: &str) -> IRInstruction { IRInstruction::with_operand(IRType::STORE_VAR, name) }
pub fn call(func: &str, _args: Vec<String>) -> IRInstruction { IRInstruction::with_operand(IRType::CALL, func) }
pub fn ret() -> IRInstruction { IRInstruction::new(IRType::RETURN) }
pub fn jump(label: &str) -> IRInstruction { IRInstruction::with_operand(IRType::JUMP, label) }
pub fn jump_if_false(label: &str) -> IRInstruction { IRInstruction::with_operand(IRType::JUMP_IF_FALSE, label) }
pub fn jump_if_true(label: &str) -> IRInstruction { IRInstruction::with_operand(IRType::JUMP_IF_TRUE, label) }
pub fn loop_begin(label: &str) -> IRInstruction { IRInstruction::with_operand(IRType::LOOP_BEGIN, label) }
pub fn loop_end(label: &str) -> IRInstruction { IRInstruction::with_operand(IRType::LOOP_END, label) }
pub fn alloc(name: &str) -> IRInstruction { IRInstruction::with_operand(IRType::ALLOC, name) }
pub fn free(name: &str) -> IRInstruction { IRInstruction::with_operand(IRType::FREE, name) }
pub fn increment_rc(name: &str) -> IRInstruction { IRInstruction::with_operand(IRType::INCREMENT_RC, name) }
pub fn decrement_rc(name: &str) -> IRInstruction { IRInstruction::with_operand(IRType::DECREMENT_RC, name) }
pub fn spawn_thread(func: &str, _args: Vec<String>) -> IRInstruction { IRInstruction::with_operand(IRType::SPAWN_THREAD, func) }
pub fn wait(task_id: &str) -> IRInstruction { IRInstruction::with_operand(IRType::WAIT, task_id) }
pub fn yield_op() -> IRInstruction { IRInstruction::new(IRType::YIELD) }
pub fn await_op(func: &str) -> IRInstruction { IRInstruction::with_operand(IRType::AWAIT, func) }
pub fn binary_op(op: &str) -> IRInstruction { IRInstruction::with_operand(IRType::BINARY_OP, op) }
pub fn unary_op(op: &str) -> IRInstruction { IRInstruction::with_operand(IRType::UNARY_OP, op) }
pub fn iter_init(var_name: &str) -> IRInstruction { IRInstruction::with_operand(IRType::ITER_INIT, var_name) }
pub fn ffi_import(language: &str, module: &str, as_name: &str) -> IRInstruction {
    IRInstruction { ty: IRType::FFI_IMPORT, operand: Some(language.to_string()), arg1: Some(module.to_string()), arg2: Some(as_name.to_string()), arg3: None }
}
pub fn ffi_get_attr(module: &str, attr: &str) -> IRInstruction {
    IRInstruction { ty: IRType::FFI_GET_ATTR, operand: Some("python".to_string()), arg1: Some(module.to_string()), arg2: Some(attr.to_string()), arg3: None }
}
pub fn ffi_call(language: &str, module: &str, func: &str, _arg_count: i64) -> IRInstruction {
    IRInstruction { ty: IRType::FFI_CALL, operand: Some(language.to_string()), arg1: Some(module.to_string()), arg2: Some(func.to_string()), arg3: None }
}
pub fn label(name: &str) -> IRInstruction { IRInstruction::with_operand(IRType::LABEL, name) }
pub fn defer_op(expr: &str) -> IRInstruction { IRInstruction::with_operand(IRType::DEFER, expr) }
pub fn match_op() -> IRInstruction { IRInstruction::new(IRType::MATCH) }
pub fn try_op() -> IRInstruction { IRInstruction::new(IRType::TRY) }