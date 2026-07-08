use crate::ir::{IRModule, IRInstruction, IRType};
use std::collections::HashMap;

pub struct VM {
    ir_module: IRModule,
    stack: Vec<String>,
    variables: HashMap<String, String>,
    debug: bool,
}

impl VM {
    pub fn new(ir_module: IRModule, debug: bool) -> Self {
        VM { ir_module, stack: Vec::new(), variables: HashMap::new(), debug }
    }

    pub fn run(&mut self) -> HashMap<String, String> {
        if let Some(instructions) = self.ir_module.functions.get("main").cloned() {
            self.run_function("main", instructions);
        }
        self.variables.clone()
    }

    fn run_function(&mut self, _name: &str, instructions: Vec<IRInstruction>) {
        let mut pc = 0;
        while pc < instructions.len() {
            let instr = &instructions[pc];
            self.execute(instr);
            pc += 1;
        }
    }

    fn execute(&mut self, instr: &IRInstruction) {
        match instr.ty {
            IRType::LOAD_CONST => { if let Some(ref val) = instr.operand { self.stack.push(val.clone()); } }
            IRType::LOAD_VAR => { if let Some(ref name) = instr.operand { if let Some(val) = self.variables.get(name) { self.stack.push(val.clone()); } } }
            _ => {}
        }
    }
}

impl Default for VM {
    fn default() -> Self {
        VM { ir_module: IRModule::default(), stack: Vec::new(), variables: HashMap::new(), debug: false }
    }
}