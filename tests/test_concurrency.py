#!/usr/bin/env python3
"""Test concurrency scheduler."""
import unittest
from synthlang.scheduler import Scheduler, Task, TaskStatus


class TestConcurrency(unittest.TestCase):
    def test_spawn_task(self):
        scheduler = Scheduler()
        
        def hello():
            return "hello"
        
        task_id = scheduler.spawn(hello)
        self.assertIsInstance(task_id, int)

    def test_task_status(self):
        scheduler = Scheduler()
        
        def work():
            return 42
        
        task_id = scheduler.spawn(work)
        scheduler.start()
        
        for task in scheduler.tasks:
            if task.id == task_id:
                self.assertEqual(task.status, TaskStatus.COMPLETED)


if __name__ == '__main__':
    unittest.main()