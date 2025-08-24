# backend/core/memory_manager.py
from typing import Dict, Any
import threading

_lock = threading.Lock()
_store: Dict[str, Dict[str, Any]] = {}

class InMemoryStore:
    def __init__(self):
        self.store = _store
        self.lock = _lock

    def get(self, key: str, default=None):
        with self.lock:
            return self.store.get(key, default)

    def set(self, key: str, value):
        with self.lock:
            self.store[key] = value

    def delete(self, key: str):
        with self.lock:
            if key in self.store:
                del self.store[key]

    # dict-like access
    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

MEMORY = InMemoryStore()
