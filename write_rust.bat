@echo off
echo use std::collections::HashMap; > src\rust\ir.rs
echo. >> src\rust\ir.rs
echo #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)] >> src\rust\ir.rs
echo pub enum IRType { >> src\rust\ir.rs
echo     LOAD_CONST, >> src\rust\ir.rs
echo } >> src\rust\ir.rs
