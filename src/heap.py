"""
Smart Network Logistics Engine (SNLE)
Heap Module

Implements:
- MinHeap for Dijkstra's algorithm
- MaxHeap for package dispatching

Created by: Judilyn Lucena
"""

from __future__ import annotations

from typing import Generic, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class MinHeap(Generic[T]):
    def __init__(self) -> None:
        self._data: List[Tuple[float, T]] = []

    def __len__(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def push(self, priority: float, value: T) -> None:
        self._data.append((priority, value))
        self._sift_up(len(self._data) - 1)

    def peek(self) -> Optional[Tuple[float, T]]:
        return None if self.is_empty() else self._data[0]

    def pop(self) -> Optional[Tuple[float, T]]:
        if self.is_empty():
            return None
        self._swap(0, len(self._data) - 1)
        item = self._data.pop()
        if self._data:
            self._sift_down(0)
        return item

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left(self, i: int) -> int:
        return 2 * i + 1

    def _right(self, i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i: int) -> None:
        while i > 0:
            p = self._parent(i)
            if self._data[i][0] < self._data[p][0]:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._data)
        while True:
            left = self._left(i)
            right = self._right(i)
            smallest = i
            if left < n and self._data[left][0] < self._data[smallest][0]:
                smallest = left
            if right < n and self._data[right][0] < self._data[smallest][0]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest


class MaxHeap:
    def __init__(self) -> None:
        self._data: List[object] = []

    def __len__(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def enqueue(self, item: object) -> None:
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def peek(self) -> Optional[object]:
        return None if self.is_empty() else self._data[0]

    def dequeue(self) -> Optional[object]:
        if self.is_empty():
            return None
        self._swap(0, len(self._data) - 1)
        item = self._data.pop()
        if self._data:
            self._sift_down(0)
        return item

    def _higher_priority(self, i: int, j: int) -> bool:
        a = self._data[i]
        b = self._data[j]
        if a.priority != b.priority:
            return a.priority > b.priority
        return str(a.package_id) < str(b.package_id)

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left(self, i: int) -> int:
        return 2 * i + 1

    def _right(self, i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i: int) -> None:
        while i > 0:
            p = self._parent(i)
            if self._higher_priority(i, p):
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._data)
        while True:
            left = self._left(i)
            right = self._right(i)
            largest = i
            if left < n and self._higher_priority(left, largest):
                largest = left
            if right < n and self._higher_priority(right, largest):
                largest = right
            if largest == i:
                break
            self._swap(i, largest)
            i = largest
