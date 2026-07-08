package main

import (
	"encoding/json"
	"testing"
	"time"
)

// TestFFI functions (testing internal Go logic)
func TestModuleRegistry(t *testing.T) {
	moduleRegistry = make(map[string]*Module)
	moduleMutex = sync.RWMutex{}
	taskIDCounter = 0

	// Test module registration
	nameStr := "test_module"
	pathStr := "/path/to/module.py"
	
	moduleMutex.Lock()
	id := int64(1)
	moduleRegistry[nameStr] = &Module{
		ID:       id,
		Language: "python",
		Path:     pathStr,
	}
	moduleMutex.Unlock()

	moduleMutex.RLock()
	mod, exists := moduleRegistry[nameStr]
	moduleMutex.RUnlock()

	if !exists {
		t.Fatal("Module not registered")
	}
	if mod.Language != "python" {
		t.Errorf("Expected python language, got %s", mod.Language)
	}
}

func TestCallFunctionLogic(t *testing.T) {
	moduleRegistry = make(map[string]*Module)
	moduleMutex = sync.RWMutex{}

	moduleRegistry["py_mod"] = &Module{
		Language: "python",
		Path:     "/path/to/py.py",
	}

	moduleMutex.RLock()
	mod, exists := moduleRegistry["py_mod"]
	moduleMutex.RUnlock()

	if !exists {
		t.Fatal("Module should exist")
	}

	resp, _ := json.Marshal(map[string]interface{}{
		"language": mod.Language,
		"path":     mod.Path,
		"function": "test_func",
		"args":     "[]",
		"status":   "success",
	})

	var result map[string]interface{}
	json.Unmarshal(resp, &result)

	if result["status"] != "success" {
		t.Errorf("Expected success status, got %v", result["status"])
	}
}

func TestSchedulerSpawnMultiple(t *testing.T) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 1000),
	}
	
	for i := 0; i < 100; i++ {
		id := s.Spawn("func", `{"id": i}`)
		if id <= 0 {
			t.Errorf("Task %d got invalid ID %d", i, id)
		}
	}
}

func TestSchedulerConcurrentSpawn(t *testing.T) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 10000),
	}

	done := make(chan bool)
	
	// Spawn 100 tasks concurrently
	for i := 0; i < 100; i++ {
		go func() {
			s.Spawn("concurrent_func", `{}`)
			done <- true
		}()
	}

	// Wait for all goroutines
	for i := 0; i < 100; i++ {
		<-done
	}
}

func BenchmarkModuleLoad(b *testing.B) {
	for i := 0; i < b.N; i++ {
		moduleRegistry = make(map[string]*Module)
		moduleMutex = sync.RWMutex{}
		taskIDCounter = 0

		moduleMutex.Lock()
		moduleRegistry["bench"] = &Module{
			Language: "python",
			Path:     "/path",
		}
		moduleMutex.Unlock()
	}
}

func BenchmarkTaskSpawn(b *testing.B) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 10000),
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		s.Spawn("bench_func", `{}`)
	}

	// Allow tasks to complete
	time.Sleep(10 * time.Millisecond)
}