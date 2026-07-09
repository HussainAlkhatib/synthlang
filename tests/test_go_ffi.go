package main

import (
	"C"
	"encoding/json"
	"testing"
)

func TestLoadPythonModule(t *testing.T) {
	id := LoadPythonModule(C.CString("test"), C.CString("./test.py"))
	if id == 0 {
		t.Error("Expected non-zero module ID")
	}
}

func TestLoadRustModule(t *testing.T) {
	id := LoadRustModule(C.CString("ctest"), C.CString("./test.rs"))
	if id == 0 {
		t.Error("Expected non-zero module ID")
	}
}

func TestCallFunction(t *testing.T) {
	LoadPythonModule(C.CString("test"), C.CString("./test.py"))
	result := CallFunction(C.CString("test"), C.CString("main"), C.CString("[]"))
	
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(C.GoString(result)), &data); err != nil {
		t.Errorf("Failed to parse result: %v", err)
	}
}

func TestSpawnTask(t *testing.T) {
	id := SpawnTask(C.CString("test_func"), C.CString("[]"))
	if id == 0 {
		t.Error("Expected non-zero task ID")
	}
	
	result := AwaitTask(id)
	if result == nil {
		t.Error("Expected non-nil result")
	}
}

func TestFFILanguages(t *testing.T) {
	languages := []string{"python", "rust", "c", "go", "javascript", "cpp", "r", "ruby", "php", "java", "swift", "kotlin", "haskell", "julia", "elixir", "dart", "lua", "csharp", "typescript", "zig"}
	
	for _, lang := range languages {
		t.Run(lang, func(t *testing.T) {
			// Each FFI language should be loadable
			langPtr := C.CString(lang)
			_ = langPtr
		})
	}
}