use std::collections::{HashMap, HashSet};

pub struct GC;

impl GC {
    pub fn collect(roots: &[String]) -> HashSet<String> {
        let mut marked = HashSet::new();
        for obj in roots { marked.insert(obj.clone()); }
        marked
    }

    pub fn mark(obj: &String, visited: &mut HashSet<usize>) {}
}

pub struct RefCounted {
    pub value: Option<String>,
    pub ref_count: usize,
}

impl RefCounted {
    pub fn new(value: Option<String>) -> Self { RefCounted { value, ref_count: 1 } }

    pub fn add_ref(&mut self) { self.ref_count += 1; }

    pub fn release(&mut self) -> bool { self.ref_count -= 1; self.ref_count <= 0 }
}

pub struct RCManager {
    objects: HashMap<String, RefCounted>,
}

impl RCManager {
    pub fn new() -> Self { RCManager { objects: HashMap::new() } }

    pub fn create(&mut self, name: &str, value: Option<String>) -> &mut RefCounted {
        self.objects.insert(name.to_string(), RefCounted::new(value));
        self.objects.get_mut(name).unwrap()
    }

    pub fn increment(&mut self, name: &str) { if let Some(obj) = self.objects.get_mut(name) { obj.add_ref(); } }

    pub fn decrement(&mut self, name: &str) -> bool {
        if let Some(obj) = self.objects.get_mut(name) {
            if obj.release() { self.objects.remove(name); return true; }
        }
        false
    }
}

impl Default for RCManager {
    fn default() -> Self {
        Self::new()
    }
}