"""
Smart Network Logistics Engine (SNLE)
Hash Map Module

Implements:
- Custom hash table
- Collision handling using separate chaining
- Dynamic resizing

Created by: Judilyn Lucena
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple


class HashMap:
    def __init__(self, capacity: int = 8) -> None:
        self.capacity = max(8, capacity)
        self.size = 0
        self.buckets: List[List[Tuple[str, Any]]] = [[] for _ in range(self.capacity)]

    def _hash(self, key: str) -> int:
        value = 0
        for ch in key:
            value = (value * 31 + ord(ch)) % self.capacity
        return value

    def _load_factor(self) -> float:
        return self.size / self.capacity

    def insert(self, key: str, value: Any) -> None:
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1
        if self._load_factor() > 0.7:
            self._resize()

    def search(self, key: str) -> Optional[Any]:
        index = self._hash(key)
        for existing_key, value in self.buckets[index]:
            if existing_key == key:
                return value
        return None

    def delete(self, key: str) -> bool:
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                del bucket[i]
                self.size -= 1
                return True
        return False

    def items(self) -> List[Tuple[str, Any]]:
        return [item for bucket in self.buckets for item in bucket]

    def _resize(self) -> None:
        old_items = self.items()
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for key, value in old_items:
            self.insert(key, value)
