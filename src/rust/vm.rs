use crate::ir::{IRModule, IRInstruction, IRType};
use std::collections::HashMap;

pub struct VM {
    ir_module: IRModule,
    stack: Vec<String>,
    variables: HashMap<String, String>,
    debug: bool,
    defer_stack: Vec<Vec<String>>,
}

impl VM {
    pub fn new(ir_module: IRModule, debug: bool) -> Self {
        VM { 
            ir_module, 
            stack: Vec::new(), 
            variables: HashMap::new(), 
            debug,
            defer_stack: Vec::new(),
        }
    }

    pub fn run(&mut self) -> HashMap<String, String> {
        if let Some(instructions) = self.ir_module.functions.get("main").cloned() {
            self.run_function("main", instructions);
        }
        self.variables.clone()
    }

    fn run_function(&mut self, _name: &str, instructions: Vec<IRInstruction>) {
        let mut pc = 0;
        self.defer_stack.push(Vec::new());
        
        while pc < instructions.len() {
            let instr = &instructions[pc];
            self.execute(instr);
            pc += 1;
        }
        
        // Execute deferred calls on function exit
        if let Some(deferred) = self.defer_stack.pop() {
            for deferred_call in deferred.iter().rev() {
                // Execute deferred call (simplified)
            }
        }
    }

    fn execute(&mut self, instr: &IRInstruction) {
        match instr.ty {
            IRType::LOAD_CONST => { if let Some(ref val) = instr.operand { self.stack.push(val.clone()); } }
            IRType::LOAD_VAR => { if let Some(ref name) = instr.operand { if let Some(val) = self.variables.get(name) { self.stack.push(val.clone()); } } }
            IRType::DEFER => { 
                if let Some(ref func) = instr.operand {
                    if let Some(frame) = self.defer_stack.last_mut() {
                        frame.push(func.clone());
                    }
                }
            }
            IRType::MATCH => { /* Handled by pattern matching logic */ }
            IRType::TRY => { /* Handled by try/handle logic */ }
            IRType::RETURN => { /* Return from function */ }
            _ => {}
        }
    }
}

impl Default for VM {
    fn default() -> Self {
        VM { ir_module: IRModule::default(), stack: Vec::new(), variables: HashMap::new(), debug: false, defer_stack: Vec::new() }
    }
}