"""
Smart Network Logistics Engine (SNLE)
Utility Module

Includes:
- Package and depot data models
- Structured file parsing
- High-level SNLE system orchestration

Created by: Judilyn Lucena
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from graph import Graph
from hashmap import HashMap
from heap import MaxHeap
from trie import Trie


@dataclass
class DepotMetadata:
    location: str
    capacity: int
    active_status: bool


@dataclass(order=False)
class Package:
    package_id: str
    priority: int
    destination: str
    weight_kg: float

    def __post_init__(self) -> None:
        self.priority = int(self.priority)
        self.weight_kg = float(self.weight_kg)

    def __repr__(self) -> str:
        return (
            f"Package(id={self.package_id}, priority={self.priority}, "
            f"destination={self.destination}, weight_kg={self.weight_kg:g})"
        )


def load_network_file(filepath: str, graph: Graph, dispatch_queue: MaxHeap) -> None:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Network file not found: {filepath}")

    content = path.read_text(encoding="utf-8")
    stripped_lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
    graph.adj.clear()
    graph.edge_count = 0
    dispatch_queue._data.clear()

    if not stripped_lines:
        return

    first_token = stripped_lines[0].upper()
    if first_token not in {"NODES", "EDGES", "PACKAGES"}:
        graph.load_from_file(filepath)
        return

    section = None
    for line_number, line in enumerate(stripped_lines, start=1):
        upper = line.upper()
        if upper in {"NODES", "EDGES", "PACKAGES"}:
            section = upper
            continue
        if section is None:
            raise ValueError(f"Content found before a section header at logical line {line_number}: {line}")

        if section == "NODES":
            for node in line.split():
                graph.add_node(node)
        elif section == "EDGES":
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Invalid edge line at logical line {line_number}: {line}")
            src, dest, weight_str = parts
            graph.add_edge(src, dest, float(weight_str))
        elif section == "PACKAGES":
            parts = line.split()
            if len(parts) != 4:
                raise ValueError(f"Invalid package line at logical line {line_number}: {line}")
            package = Package(parts[0], int(parts[1]), parts[2], float(parts[3]))
            if package.destination not in graph.adj:
                raise ValueError(f"Package destination '{package.destination}' does not exist in the graph.")
            dispatch_queue.enqueue(package)


class SNLESystem:
    def __init__(self) -> None:
        self.graph = Graph()
        self.dispatch_queue = MaxHeap()
        self.depots = HashMap()
        self.trie = Trie()
        self.dispatch_log: List[Package] = []

    def load_network(self, filepath: str) -> None:
        load_network_file(filepath, self.graph, self.dispatch_queue)
        self.rebuild_trie_from_graph()

    def rebuild_trie_from_graph(self) -> None:
        self.trie = Trie()
        for node in self.graph.get_nodes():
            self.trie.insert(node)

    def add_depot(self, name: str, location: str, capacity: int, active_status: bool) -> None:
        self.depots.insert(name, DepotMetadata(location, capacity, active_status))
        self.trie.insert(name)

    def search_depot(self, name: str) -> DepotMetadata | None:
        return self.depots.search(name)

    def delete_depot(self, name: str) -> bool:
        return self.depots.delete(name)

    def autocomplete_nodes(self, prefix: str) -> List[str]:
        return self.trie.autocomplete(prefix)

    def enqueue_package(self, package_id: str, priority: int, destination: str, weight_kg: float) -> None:
        if destination not in self.graph.adj:
            raise ValueError("Destination does not exist in the graph.")
        self.dispatch_queue.enqueue(Package(package_id, priority, destination, weight_kg))

    def dispatch_top_package(self) -> Package | None:
        package = self.dispatch_queue.dequeue()
        if package is not None:
            self.dispatch_log.append(package)
        return package
