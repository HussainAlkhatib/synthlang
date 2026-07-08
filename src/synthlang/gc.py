"""SynthLang Garbage Collector - Simple mark-and-sweep implementation."""
from typing import Any, Dict, Set, List, Optional


class GC:
    def __init__(self, vm):
        self.vm = vm
        self.roots: Set[str] = set()

    def collect(self, *roots: str):
        self.roots = set(roots)
        marked = set()
        for obj in self.roots:
            if obj in self.vm.variables:
                marked.add(obj)
        for obj in self.vm.stack:
            if isinstance(obj, str):
                marked.add(obj)
        
        # Clean up unmarked variables
        for var in list(self.vm.variables.keys()):
            if var not in marked:
                del self.vm.variables[var]

    def mark(self, obj: Any, visited: Set[int]):
        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)
        
        if isinstance(obj, dict):
            for k, v in obj.items():
                self.mark(v, visited)
        elif isinstance(obj, list):
            for item in obj:
                self.mark(item, visited)


class RefCounted:
    def __init__(self, value: Any = None):
        self.value = value
        self.ref_count = 1

    def add_ref(self):
        self.ref_count += 1

    def release(self) -> bool:
        self.ref_count -= 1
        return self.ref_count <= 0


class RCManager:
    def __init__(self):
        self.objects: Dict[str, RefCounted] = {}

    def create(self, name: str, value: Any) -> RefCounted:
        obj = RefCounted(value)
        self.objects[name] = obj
        return obj

    def increment(self, name: str):
        if name in self.objects:
            self.objects[name].add_ref()

    def decrement(self, name: str) -> bool:
        if name in self.objects:
            if self.objects[name].release():
                del self.objects[name]
                return True
        return False

    def get(self, name: str) -> Any:
        if name in self.objects:
            return self.objects[name].value
        return None


if __name__ == '__main__':
    print("GC module loaded successfully")