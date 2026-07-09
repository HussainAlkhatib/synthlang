use crate::parser::ASTNode;
use crate::parser::NodeType;
use crate::ir::IRModule;
use crate::ir::exec_code_block;

pub struct Compiler {
    ir_module: IRModule,
    current_function: Option<String>,
    label_count: usize,
}

impl Compiler {
    pub fn new() -> Self {
        Compiler { ir_module: IRModule::default(), current_function: None, label_count: 0 }
    }

    pub fn compile(&mut self, ast: Vec<ASTNode>) -> IRModule {
        for node in &ast { self.compile_node(node); }
        self.ir_module.clone()
    }

    fn new_label(&mut self, prefix: &str) -> String {
        self.label_count += 1;
        format!("{}{}", prefix, self.label_count)
    }

    fn compile_node(&mut self, node: &ASTNode) {
        match node.ty {
            NodeType::INLINE_CODE => {
                if let Some(lang) = &node.value {
                    let code = node.value.as_ref().unwrap_or(&String::new());
                    let _ = exec_code_block(lang, code);
                }
            }
            _ => {}
        }
    }
}

impl Default for Compiler {
    fn default() -> Self {
        Self::new()
    }
}