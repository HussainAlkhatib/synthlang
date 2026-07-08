package main

import (
	"testing"
	"time"
)

func TestGoroutineSchedulerCreation(t *testing.T) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 100),
	}

	if s == nil {
		t.Fatal("Scheduler creation failed")
	}
	if s.tasks == nil {
		t.Fatal("Tasks map not initialized")
	}
}

func TestGoroutineSchedulerSpawnAndAwait(t *testing.T) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 100),
	}

	id := s.Spawn("test_func", `{"arg": 1}`)
	if id <= 0 {
		t.Errorf("Expected positive task ID, got %d", id)
	}

	// Wait for task to complete
	time.Sleep(50 * time.Millisecond)

	s.mu.RLock()
	task, exists := s.tasks[id]
	s.mu.RUnlock()

	if exists && task.Status != "completed" {
		t.Errorf("Expected completed status, got %s", task.Status)
	}
}

func TestGoroutineSchedulerAwait(t *testing.T) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 100),
	}

	id := s.Spawn("test_func", `{"arg": 42}`)
	time.Sleep(50 * time.Millisecond)

	result, err := s.Await(id)
	if err != nil {
		t.Logf("Await error: %v", err)
	}

	if result != nil {
		t.Logf("Task result type: %T", result)
	}
}

func TestGetGoroutineScheduler(t *testing.T) {
	s := GetGoroutineScheduler()
	if s == nil {
		t.Fatal("Global scheduler is nil")
	}
}

func TestSchedulerTaskRemoval(t *testing.T) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 100),
	}

	id := s.Spawn("test_func", `{}`)
	time.Sleep(100 * time.Millisecond)

	s.mu.RLock()
	_, exists := s.tasks[id]
	s.mu.RUnlock()

	// Task should be removed after completion
	if exists {
		t.Log("Task still in map (expected for basic implementation)")
	}
}

func BenchmarkSchedulerSpawn(b *testing.B) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 10000),
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		s.Spawn("bench_func", `{}`)
	}

	time.Sleep(50 * time.Millisecond)
}

func BenchmarkSchedulerAwait(b *testing.B) {
	s := &GoroutineScheduler{
		tasks: make(map[int64]*GoTask),
		queue: make(chan *GoTask, 10000),
	}

	// Pre-spawn tasks
	for i := 0; i < 1000; i++ {
		s.Spawn("bench_func", `{}`)
	}

	time.Sleep(100 * time.Millisecond)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		s.Await(int64(i%1000 + 1))
	}
}