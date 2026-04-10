"""
Smart Network Logistics Engine (SNLE)
Trie Module

Implements:
- Prefix search
- Autocomplete for depot and zone names

Created by: Judilyn Lucena
"""

from __future__ import annotations

from typing import Dict, List


class TrieNode:
    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end = False


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word.lower():
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def autocomplete(self, prefix: str) -> List[str]:
        node = self.root
        normalized = prefix.lower()
        for ch in normalized:
            if ch not in node.children:
                return []
            node = node.children[ch]
        results: List[str] = []
        self._collect(node, normalized, results)
        return sorted(results)

    def _collect(self, node: TrieNode, current: str, results: List[str]) -> None:
        if node.is_end:
            results.append(current)
        for ch, child in node.children.items():
            self._collect(child, current + ch, results)
