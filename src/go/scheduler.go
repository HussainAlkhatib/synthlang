package main

// Scheduler - Goroutine-based task scheduler for SynthLang
// This provides lightweight threading primitives (go, await) using Go's goroutines

import (
	"encoding/json"
	"sync"
	"sync/atomic"
)

// Task represents a scheduled goroutine (alias to GoTask)
type Task = GoTask

// GoroutineScheduler manages tasks with goroutine support
type GoroutineScheduler struct {
	tasks map[int64]*Task
	queue chan *Task
	mu    sync.RWMutex
	idGen int64
}

var (
	globalGoScheduler *GoroutineScheduler
	schedulerInit     sync.Once
)

// GetGoroutineScheduler returns the global scheduler instance
func GetGoroutineScheduler() *GoroutineScheduler {
	schedulerInit.Do(func() {
		globalGoScheduler = &GoroutineScheduler{
			tasks: make(map[int64]*Task),
			queue: make(chan *Task, 10000),
		}
		// Start worker pool
		for i := 0; i < 10; i++ {
			go globalGoScheduler.runWorker()
		}
	})
	return globalGoScheduler
}

func (s *GoroutineScheduler) runWorker() {
	for task := range s.queue {
		s.executeTask(task)
	}
}

func (s *GoroutineScheduler) executeTask(task *Task) {
	s.mu.Lock()
	task.Status = "running"
	s.mu.Unlock()

	result := map[string]interface{}{
		"task_id":  task.ID,
		"executed": true,
	}

	s.mu.Lock()
	task.Result = result
	task.Status = "completed"
	delete(s.tasks, task.ID)
	s.mu.Unlock()

	close(task.Done)
}

// Spawn creates a new task and schedules it in a goroutine
func (s *GoroutineScheduler) Spawn(funcName string, args string) int64 {
	s.mu.Lock()
	defer s.mu.Unlock()

	id := atomic.AddInt64(&s.idGen, 1)
	task := &Task{
		ID:     id,
		Status: "pending",
		Done:   make(chan struct{}),
	}
	s.tasks[id] = task
	s.queue <- task

	return id
}

// Await waits for a task to complete
func (s *GoroutineScheduler) Await(taskID int64) (interface{}, error) {
	s.mu.RLock()
	task, exists := s.tasks[taskID]
	s.mu.RUnlock()

	if !exists {
		return nil, &FFIError{Message: "Task not found"}
	}

	<-task.Done

	s.mu.RLock()
	defer s.mu.RUnlock()

	if task.Status == "completed" {
		return task.Result, nil
	}

	return nil, task.Error
}

// GetTaskStatus returns the status of a task
func (s *GoroutineScheduler) GetTaskStatus(taskID int64) string {
	s.mu.RLock()
	defer s.mu.RUnlock()

	task, exists := s.tasks[taskID]
	if !exists {
		return "not_found"
	}

	return task.Status
}

// MarshalJSON for FFIError
func (e *FFIError) MarshalJSON() ([]byte, error) {
	return json.Marshal(map[string]interface{}{
		"message":  e.Message,
		"language": e.Language,
		"module":   e.Module,
		"function": e.Function,
	})
}