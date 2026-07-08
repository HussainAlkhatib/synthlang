#!/usr/bin/env python3
"""Test scheduler - comprehensive tests for cooperative threading."""
import unittest
from synthlang.scheduler import Scheduler, Task, TaskStatus, SystemThread


class TestTaskStatus(unittest.TestCase):
    def test_pending(self):
        self.assertEqual(TaskStatus.PENDING.value, 1)

    def test_running(self):
        self.assertEqual(TaskStatus.RUNNING.value, 2)

    def test_waiting(self):
        self.assertEqual(TaskStatus.WAITING.value, 3)

    def test_completed(self):
        self.assertEqual(TaskStatus.COMPLETED.value, 4)

    def test_failed(self):
        self.assertEqual(TaskStatus.FAILED.value, 5)


class TestTask(unittest.TestCase):
    def test_task_creation(self):
        def func():
            return 42
        task = Task(id=1, func=func, args=())
        self.assertEqual(task.id, 1)
        self.assertEqual(task.func, func)
        self.assertEqual(task.status, TaskStatus.PENDING)

    def test_task_with_args(self):
        def func(a, b):
            return a + b
        task = Task(id=1, func=func, args=(1, 2))
        self.assertEqual(task.args, (1, 2))


class TestScheduler(unittest.TestCase):
    def test_scheduler_creation(self):
        scheduler = Scheduler()
        self.assertIsNotNone(scheduler)
        self.assertEqual(len(scheduler.tasks), 0)

    def test_spawn_task(self):
        scheduler = Scheduler()
        task_id = scheduler.spawn(lambda: 42)
        self.assertIsInstance(task_id, int)
        self.assertEqual(task_id, 1)

    def test_spawn_multiple_tasks(self):
        scheduler = Scheduler()
        for i in range(5):
            scheduler.spawn(lambda: i)
        self.assertEqual(len(scheduler.tasks), 5)

    def test_task_status_after_start(self):
        scheduler = Scheduler()
        def work():
            return 42
        task_id = scheduler.spawn(work)
        scheduler.start()
        task = next(t for t in scheduler.tasks if t.id == task_id)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result, 42)

    def test_task_execution(self):
        scheduler = Scheduler()
        results = []

        def collect():
            results.append(1)

        scheduler.spawn(collect)
        scheduler.start()
        self.assertEqual(len(results), 1)


class TestSystemThread(unittest.TestCase):
    def test_thread_creation(self):
        def work():
            return 42
        thread = SystemThread(work)
        self.assertIsNotNone(thread)


if __name__ == '__main__':
    unittest.main()