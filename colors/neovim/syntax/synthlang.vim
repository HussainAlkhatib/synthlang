" Vim syntax file for SynthLang (Neovim)
if exists("b:current_syntax")
    finish
endif

syn keyword synthlangKeyword let var fn if elif else for while return go await match defer try handle panic in as module
syn keyword synthlangBoolean true false
syn keyword synthlangType int float string str bool void list dict object
syn match synthlangAnnotation /@[a-zA-Z_][a-zA-Z0-9_]*/
syn match synthlangFFIImport /@\(python\|javascript\|rust\|c\|go\|java\)\s\+module\s\+"[^"]*"\s\+\(as\|import\)\s\+[a-zA-Z_][a-zA-Z0-9_, ]*/
syn match synthlangComment /#.*$/
syn match synthlangComment /\/\/.*$/
syn region synthlangComment start="/\*" end="\*/"
syn region synthlangString start='"' end='"' contains=@Spell
syn region synthlangString start="'" end="'" contains=@Spell
syn match synthlangOperator /[\+\-*/%]/
syn match synthlangCompare /[<>=!]\+/
syn match synthlangLogical /&&\|||/
syn match synthlangNumber /\<\d\+\>/
syn match synthlangFloat /\<\d\+\.\d\+\>/

hi def link synthlangKeyword Keyword
hi def link synthlangBoolean Boolean
hi def link synthlangType Type
hi def link synthlangAnnotation PreProc
hi def link synthlangFFIImport Include
hi def link synthlangComment Comment
hi def link synthlangString String
hi def link synthlangOperator Operator
hi def link synthlangCompare Operator
hi def link synthlangLogical Operator
hi def link synthlangNumber Number
hi def link synthlangFloat Float

let b:current_syntax = "synthlang"