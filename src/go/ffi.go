package main

// SynthLang Core Go Library - FFI and Scheduler combined
// This file provides C-callable functions for FFI and goroutine scheduling

import "C"
import (
	"encoding/json"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// Module represents a loaded foreign module
type Module struct {
	ID       int64
	Language string
	Path     string
}

// TaskState represents the state of a task
type TaskState int

const (
	StatePending TaskState = iota
	StateRunning
	StateCompleted
	StateFailed
)

// GoTask represents a scheduled goroutine task
type GoTask struct {
	ID     int64
	Status string
	Result interface{}
	Error  error
	Done   chan struct{}
}

var (
	moduleRegistry = make(map[string]*Module)
	moduleMutex    sync.RWMutex
	taskRegistry   = make(map[int64]*GoTask)
	taskMutex      sync.RWMutex
	taskIDCounter  int64
)

// FFIError represents an FFI error
type FFIError struct {
	Message  string `json:"message"`
	Language string `json:"language,omitempty"`
	Module   string `json:"module,omitempty"`
	Function string `json:"function,omitempty"`
}

func (e *FFIError) Error() string {
	return e.Message
}

// --- FFI Module Loading Functions ---

//export LoadPythonModule
func LoadPythonModule(name *C.char, path *C.char) C.ulonglong {
	nameStr := C.GoString(name)
	pathStr := C.GoString(path)

	moduleMutex.Lock()
	defer moduleMutex.Unlock()

	id := atomic.AddInt64(&taskIDCounter, 1)
	moduleRegistry[nameStr] = &Module{
		ID:       id,
		Language: "python",
		Path:     pathStr,
	}
	return C.ulonglong(id)
}

//export LoadRustModule
func LoadRustModule(name *C.char, path *C.char) C.ulonglong {
	nameStr := C.GoString(name)
	pathStr := C.GoString(path)

	moduleMutex.Lock()
	defer moduleMutex.Unlock()

	id := atomic.AddInt64(&taskIDCounter, 1)
	moduleRegistry[nameStr] = &Module{
		ID:       id,
		Language: "rust",
		Path:     pathStr,
	}
	return C.ulonglong(id)
}

//export LoadCModule
func LoadCModule(name *C.char, path *C.char) C.ulonglong {
	nameStr := C.GoString(name)
	pathStr := C.GoString(path)

	moduleMutex.Lock()
	defer moduleMutex.Unlock()

	id := atomic.AddInt64(&taskIDCounter, 1)
	moduleRegistry[nameStr] = &Module{
		ID:       id,
		Language: "c",
		Path:     pathStr,
	}
	return C.ulonglong(id)
}

//export LoadGoModule
func LoadGoModule(name *C.char, path *C.char) C.ulonglong {
	nameStr := C.GoString(name)
	pathStr := C.GoString(path)

	moduleMutex.Lock()
	defer moduleMutex.Unlock()

	id := atomic.AddInt64(&taskIDCounter, 1)
	moduleRegistry[nameStr] = &Module{
		ID:       id,
		Language: "go",
		Path:     pathStr,
	}
	return C.ulonglong(id)
}

//export LoadJavaScriptModule
func LoadJavaScriptModule(name *C.char, path *C.char) C.ulonglong {
	nameStr := C.GoString(name)
	pathStr := C.GoString(path)

	moduleMutex.Lock()
	defer moduleMutex.Unlock()

	id := atomic.AddInt64(&taskIDCounter, 1)
	moduleRegistry[nameStr] = &Module{
		ID:       id,
		Language: "javascript",
		Path:     pathStr,
	}
	return C.ulonglong(id)
}

// --- FFI Call Functions ---

//export CallFunction
func CallFunction(module *C.char, function *C.char, args *C.char) *C.char {
	moduleStr := C.GoString(module)
	funcStr := C.GoString(function)
	argsStr := C.GoString(args)

	moduleMutex.RLock()
	mod, exists := moduleRegistry[moduleStr]
	moduleMutex.RUnlock()

	if !exists {
		resp, _ := json.Marshal(map[string]interface{}{
			"error": fmt.Sprintf("Module '%s' not found", moduleStr),
		})
		return C.CString(string(resp))
	}

	resp, _ := json.Marshal(map[string]interface{}{
		"language": mod.Language,
		"path":     mod.Path,
		"function": funcStr,
		"args":     argsStr,
		"status":   "success",
	})
	return C.CString(string(resp))
}

// --- Scheduler Functions ---

//export SpawnTask
func SpawnTask(funcName *C.char, args *C.char) C.ulonglong {
	nameStr := C.GoString(funcName)

	taskMutex.Lock()
	defer taskMutex.Unlock()

	id := atomic.AddInt64(&taskIDCounter, 1)
	task := &GoTask{
		ID:     id,
		Status: "pending",
		Done:   make(chan struct{}),
	}
	taskRegistry[id] = task

	go func() {
		taskMutex.Lock()
		task.Status = "running"
		taskMutex.Unlock()

		// Simulate task execution - real implementation would invoke actual functions
		result := map[string]interface{}{
			"task_id":  id,
			"func":     nameStr,
			"args":     C.GoString(args),
			"executed": true,
		}

		taskMutex.Lock()
		task.Result = result
		task.Status = "completed"
		taskMutex.Unlock()

		close(task.Done)
	}()

	return C.ulonglong(id)
}

//export AwaitTask
func AwaitTask(taskID C.ulonglong) *C.char {
	id := int64(taskID)

	taskMutex.RLock()
	task, exists := taskRegistry[id]
	taskMutex.RUnlock()

	if !exists {
		resp, _ := json.Marshal(map[string]interface{}{
			"error": fmt.Sprintf("Task %d not found", id),
		})
		return C.CString(string(resp))
	}

	// Wait for task completion
	<-task.Done

	taskMutex.RLock()
	defer taskMutex.RUnlock()

	if task.Status == "completed" {
		resp, _ := json.Marshal(map[string]interface{}{
			"status": "completed",
			"result": task.Result,
		})
		return C.CString(string(resp))
	}

	resp, _ := json.Marshal(map[string]interface{}{
		"status": "failed",
		"error":  task.Error,
	})
	return C.CString(string(resp))
}

//export YieldTask
func YieldTask() {
	time.Sleep(0)
}

//export GetLastError
func GetLastError() *C.char {
	return C.CString("")
}

//export ClearError
func ClearError() {}

func main() {}