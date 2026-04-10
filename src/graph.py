"""
Smart Network Logistics Engine (SNLE)
Graph Module

Implements:
- Directed weighted graph using an adjacency list
- Dijkstra's algorithm
- Bellman-Ford algorithm
- DFS cycle detection
- Negative-weight cycle detection
- Minimum spanning forest on the undirected projection
- Memoized all-pairs shortest paths using dynamic programming
- ASCII and matplotlib visualization

Created by: Judilyn Lucena
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from heap import MinHeap

WHITE = 0
GRAY = 1
BLACK = 2


class Graph:
    def __init__(self) -> None:
        self.adj: Dict[str, List[Tuple[str, float]]] = {}
        self.edge_count = 0

    def add_node(self, node: str) -> None:
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, src: str, dest: str, weight: float) -> None:
        self.add_node(src)
        self.add_node(dest)
        self.adj[src].append((dest, weight))
        self.edge_count += 1

    def load_from_file(self, file_path: str) -> None:
        self.adj.clear()
        self.edge_count = 0
        with open(file_path, "r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [part.strip() for part in line.split(",")]
                if len(parts) != 3:
                    raise ValueError(f"Invalid network format at line {line_number}: {raw_line.rstrip()}")
                src, dest, weight_str = parts
                self.add_edge(src, dest, float(weight_str))

    def get_nodes(self) -> List[str]:
        return list(self.adj.keys())

    def _get_edges(self) -> List[Tuple[str, str, float]]:
        edges: List[Tuple[str, str, float]] = []
        for src, neighbors in self.adj.items():
            for dest, weight in neighbors:
                edges.append((src, dest, weight))
        return edges

    def graph_summary(self) -> dict:
        return {
            "nodes": len(self.adj),
            "edges": self.edge_count,
            "connected_components": self.count_weakly_connected_components(),
        }

    def count_weakly_connected_components(self) -> int:
        undirected: Dict[str, List[str]] = {node: [] for node in self.adj}
        for src, neighbors in self.adj.items():
            for dest, _ in neighbors:
                undirected[src].append(dest)
                undirected[dest].append(src)

        visited: Set[str] = set()
        components = 0
        for node in undirected:
            if node in visited:
                continue
            components += 1
            stack = [node]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                for neighbor in undirected[current]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        return components

    def dijkstra(self, start: str, end: str) -> Tuple[float, List[str]]:
        if start not in self.adj or end not in self.adj:
            raise ValueError("Source or destination node does not exist.")

        distances = {node: float("inf") for node in self.adj}
        previous: Dict[str, Optional[str]] = {node: None for node in self.adj}
        distances[start] = 0.0
        heap: MinHeap[str] = MinHeap()
        heap.push(0.0, start)

        while not heap.is_empty():
            item = heap.pop()
            if item is None:
                break
            current_distance, current = item
            if current_distance > distances[current]:
                continue
            if current == end:
                break
            for neighbor, weight in self.adj[current]:
                candidate = current_distance + weight
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    previous[neighbor] = current
                    heap.push(candidate, neighbor)

        if distances[end] == float("inf"):
            return float("inf"), []

        path: List[str] = []
        current: Optional[str] = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return distances[end], path

    def _normalize_cycle_signature(self, cycle_nodes: List[str]) -> Tuple[str, ...]:
        if not cycle_nodes:
            return tuple()
        core = cycle_nodes[:-1] if len(cycle_nodes) > 1 and cycle_nodes[0] == cycle_nodes[-1] else cycle_nodes[:]
        if not core:
            return tuple()
        rotations = [tuple(core[i:] + core[:i]) for i in range(len(core))]
        reversed_core = list(reversed(core))
        rotations += [tuple(reversed_core[i:] + reversed_core[:i]) for i in range(len(reversed_core))]
        return min(rotations)

    def _reconstruct_cycle_from_predecessor(
        self,
        predecessor: Dict[str, Optional[str]],
        cycle_node: str,
    ) -> List[str]:
        current = cycle_node
        for _ in range(len(self.adj)):
            parent = predecessor.get(current)
            if parent is None:
                return []
            current = parent

        cycle_start = current
        cycle = [cycle_start]
        current = predecessor[cycle_start]
        while current is not None and current != cycle_start:
            cycle.append(current)
            current = predecessor[current]
        if current is None:
            return []
        cycle.append(cycle_start)
        cycle.reverse()
        return cycle

    def detect_negative_weight_cycles(self, start: Optional[str] = None) -> List[List[str]]:
        if not self.adj:
            return []
        if start is not None and start not in self.adj:
            raise ValueError("Start node does not exist.")

        nodes = self.get_nodes()
        edges = self._get_edges()
        distances = {node: 0.0 if start is None else float("inf") for node in nodes}
        predecessor: Dict[str, Optional[str]] = {node: None for node in nodes}
        if start is not None:
            distances[start] = 0.0

        for _ in range(len(nodes) - 1):
            updated = False
            for src, dest, weight in edges:
                if distances[src] == float("inf"):
                    continue
                candidate = distances[src] + weight
                if candidate < distances[dest]:
                    distances[dest] = candidate
                    predecessor[dest] = src
                    updated = True
            if not updated:
                break

        cycles: List[List[str]] = []
        seen_signatures: Set[Tuple[str, ...]] = set()
        for src, dest, weight in edges:
            if distances[src] == float("inf"):
                continue
            if distances[src] + weight < distances[dest]:
                predecessor[dest] = src
                cycle = self._reconstruct_cycle_from_predecessor(predecessor, dest)
                signature = self._normalize_cycle_signature(cycle)
                if cycle and signature not in seen_signatures:
                    seen_signatures.add(signature)
                    cycles.append(cycle)
        return cycles

    def bellman_ford(self, start: str, end: str) -> Tuple[float, List[str]]:
        if start not in self.adj or end not in self.adj:
            raise ValueError("Source or destination node does not exist.")

        distances = {node: float("inf") for node in self.adj}
        previous: Dict[str, Optional[str]] = {node: None for node in self.adj}
        distances[start] = 0.0
        edges = self._get_edges()

        for _ in range(len(self.adj) - 1):
            updated = False
            for src, dest, weight in edges:
                if distances[src] == float("inf"):
                    continue
                candidate = distances[src] + weight
                if candidate < distances[dest]:
                    distances[dest] = candidate
                    previous[dest] = src
                    updated = True
            if not updated:
                break

        negative_cycles = self.detect_negative_weight_cycles(start)
        if negative_cycles:
            formatted = "; ".join(" -> ".join(cycle) for cycle in negative_cycles)
            raise ValueError(f"Negative-weight cycle detected: {formatted}")

        if distances[end] == float("inf"):
            return float("inf"), []

        path: List[str] = []
        current: Optional[str] = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return distances[end], path

    def find_cycles(self) -> List[List[str]]:
        color = {node: WHITE for node in self.adj}
        parent: Dict[str, Optional[str]] = {node: None for node in self.adj}
        cycles: List[List[str]] = []
        seen_signatures: Set[Tuple[str, ...]] = set()

        def dfs(node: str) -> None:
            color[node] = GRAY
            for neighbor, _ in self.adj[node]:
                if color[neighbor] == WHITE:
                    parent[neighbor] = node
                    dfs(neighbor)
                elif color[neighbor] == GRAY:
                    cycle = [neighbor]
                    current = node
                    while current is not None and current != neighbor:
                        cycle.append(current)
                        current = parent[current]
                    cycle.append(neighbor)
                    cycle.reverse()
                    signature = self._normalize_cycle_signature(cycle)
                    if signature and signature not in seen_signatures:
                        seen_signatures.add(signature)
                        cycles.append(cycle)
            color[node] = BLACK

        for node in self.adj:
            if color[node] == WHITE:
                dfs(node)
        return cycles

    def _get_undirected_unique_edges(self) -> List[Tuple[str, str, float]]:
        edge_map: Dict[Tuple[str, str], float] = {}
        for src, neighbors in self.adj.items():
            for dest, weight in neighbors:
                a, b = sorted((src, dest))
                key = (a, b)
                if key not in edge_map or weight < edge_map[key]:
                    edge_map[key] = weight
        return [(src, dest, weight) for (src, dest), weight in edge_map.items()]

    def minimum_spanning_tree_undirected(self) -> dict:
        nodes = self.get_nodes()
        if not nodes:
            return {"total_weight": 0.0, "edges": [], "components": 0, "is_connected": True}

        parent: Dict[str, str] = {node: node for node in nodes}
        rank: Dict[str, int] = {node: 0 for node in nodes}

        def find(node: str) -> str:
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        def union(a: str, b: str) -> bool:
            root_a = find(a)
            root_b = find(b)
            if root_a == root_b:
                return False
            if rank[root_a] < rank[root_b]:
                parent[root_a] = root_b
            elif rank[root_a] > rank[root_b]:
                parent[root_b] = root_a
            else:
                parent[root_b] = root_a
                rank[root_a] += 1
            return True

        mst_edges: List[Tuple[str, str, float]] = []
        total_weight = 0.0
        for src, dest, weight in sorted(self._get_undirected_unique_edges(), key=lambda edge: (edge[2], edge[0], edge[1])):
            if union(src, dest):
                mst_edges.append((src, dest, weight))
                total_weight += weight

        roots = {find(node) for node in nodes}
        return {
            "total_weight": total_weight,
            "edges": mst_edges,
            "components": len(roots),
            "is_connected": len(roots) == 1,
        }

    def all_pairs_shortest_paths_memoized(self) -> dict:
        if not self.adj:
            return {"nodes": [], "distance_matrix": {}, "next_hop_matrix": {}, "paths": {}}

        negative_cycles = self.detect_negative_weight_cycles()
        if negative_cycles:
            formatted = "; ".join(" -> ".join(cycle) for cycle in negative_cycles)
            raise ValueError(f"Cannot compute all-pairs shortest paths: negative-weight cycle detected: {formatted}")

        nodes = sorted(self.get_nodes())
        edge_weight: Dict[Tuple[str, str], float] = {}
        next_direct: Dict[Tuple[str, str], Optional[str]] = {}

        for node in nodes:
            edge_weight[(node, node)] = 0.0
            next_direct[(node, node)] = node

        for src, neighbors in self.adj.items():
            for dest, weight in neighbors:
                key = (src, dest)
                if key not in edge_weight or weight < edge_weight[key]:
                    edge_weight[key] = weight
                    next_direct[key] = dest

        memo: Dict[Tuple[int, str, str], float] = {}
        choice: Dict[Tuple[int, str, str], Tuple[str, Optional[int]]] = {}

        def solve(k: int, src: str, dest: str) -> float:
            state = (k, src, dest)
            if state in memo:
                return memo[state]
            if k < 0:
                base = edge_weight.get((src, dest), float("inf"))
                memo[state] = base
                if base != float("inf"):
                    next_hop = next_direct.get((src, dest))
                    if next_hop is not None:
                        choice[state] = (next_hop, None)
                return base

            pivot = nodes[k]
            without_pivot = solve(k - 1, src, dest)
            via_left = solve(k - 1, src, pivot)
            via_right = solve(k - 1, pivot, dest)
            via_pivot = via_left + via_right if via_left != float("inf") and via_right != float("inf") else float("inf")

            if via_pivot < without_pivot:
                memo[state] = via_pivot
                first_hop_state = (k - 1, src, pivot)
                if first_hop_state in choice:
                    choice[state] = choice[first_hop_state]
            else:
                memo[state] = without_pivot
                prev_state = (k - 1, src, dest)
                if prev_state in choice:
                    choice[state] = choice[prev_state]
            return memo[state]

        max_k = len(nodes) - 1
        distance_matrix: Dict[str, Dict[str, float]] = {src: {} for src in nodes}
        next_hop_matrix: Dict[str, Dict[str, Optional[str]]] = {src: {} for src in nodes}
        paths: Dict[str, Dict[str, List[str]]] = {src: {} for src in nodes}

        for src in nodes:
            for dest in nodes:
                distance = solve(max_k, src, dest)
                distance_matrix[src][dest] = distance
                hop = choice.get((max_k, src, dest), (None, None))[0] if distance != float("inf") else None
                next_hop_matrix[src][dest] = hop

        for src in nodes:
            for dest in nodes:
                distance = distance_matrix[src][dest]
                if distance == float("inf"):
                    paths[src][dest] = []
                    continue
                path = [src]
                if src == dest:
                    paths[src][dest] = path
                    continue
                current = src
                visited_steps = 0
                while current != dest:
                    next_hop = next_hop_matrix[current].get(dest)
                    if next_hop is None:
                        path = []
                        break
                    path.append(next_hop)
                    current = next_hop
                    visited_steps += 1
                    if visited_steps > len(nodes):
                        raise ValueError("Path reconstruction failed due to unexpected cycle.")
                paths[src][dest] = path

        return {
            "nodes": nodes,
            "distance_matrix": distance_matrix,
            "next_hop_matrix": next_hop_matrix,
            "paths": paths,
        }

    def ascii_art(self) -> str:
        if not self.adj:
            return "[empty graph]"
        lines: List[str] = []
        for src in sorted(self.adj):
            neighbors = self.adj[src]
            if not neighbors:
                lines.append(f"{src} -> (no outgoing edges)")
                continue
            formatted = ", ".join(f"{dest}({weight:g})" for dest, weight in sorted(neighbors, key=lambda item: item[0]))
            lines.append(f"{src} -> {formatted}")
        return "\n".join(lines)

    def plot_network_matplotlib(self, output_path: str = "network_plot.png") -> str:
        if not self.adj:
            raise ValueError("Graph is empty.")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        nodes = sorted(self.get_nodes())
        total_nodes = len(nodes)
        radius = max(3.0, total_nodes / 2)
        positions: Dict[str, Tuple[float, float]] = {}
        for i, node in enumerate(nodes):
            angle = (2 * math.pi * i) / max(1, total_nodes)
            positions[node] = (radius * math.cos(angle), radius * math.sin(angle))

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_title("SNLE Network")
        ax.axis("off")

        for src, neighbors in self.adj.items():
            x1, y1 = positions[src]
            for dest, weight in neighbors:
                x2, y2 = positions[dest]
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0 and dy == 0:
                    continue
                ax.annotate(
                    "",
                    xy=(x2, y2),
                    xytext=(x1, y1),
                    arrowprops={"arrowstyle": "->", "shrinkA": 14, "shrinkB": 14, "lw": 1.2},
                )
                ax.text((x1 + x2) / 2, (y1 + y2) / 2, f"{weight:g}", fontsize=9)

        for node, (x, y) in positions.items():
            ax.scatter([x], [y], s=900)
            ax.text(x, y, node, ha="center", va="center", fontsize=9, wrap=True)

        fig.tight_layout()
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=200, bbox_inches="tight")
        plt.close(fig)
        return str(output.resolve())

    def count_routes_memo(self, start: str, end: str, max_stops: int) -> int:
        memo: Dict[Tuple[str, int], int] = {}

        def helper(node: str, remaining_stops: int) -> int:
            state = (node, remaining_stops)
            if state in memo:
                return memo[state]
            if remaining_stops < 0:
                return 0
            if node == end:
                return 1
            total = 0
            for neighbor, _ in self.adj.get(node, []):
                total += helper(neighbor, remaining_stops - 1)
            memo[state] = total
            return total

        return helper(start, max_stops)
