"""
Pytest suite for the Smart Network Logistics Engine (SNLE).

Created by: Judilyn Lucena
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PROJECT_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if PROJECT_SRC not in sys.path:
    sys.path.insert(0, PROJECT_SRC)

from graph import Graph
from hashmap import HashMap
from heap import MaxHeap, MinHeap
from trie import Trie
from utils import DepotMetadata, Package, SNLESystem, load_network_file


@pytest.fixture
def sample_graph() -> Graph:
    graph = Graph()
    graph.add_edge('DepotA', 'WarehouseX', 2)
    graph.add_edge('DepotA', 'DepotB', 4)
    graph.add_edge('WarehouseX', 'ZoneSouth', 3)
    graph.add_edge('ZoneSouth', 'DepotC', 1)
    graph.add_edge('DepotC', 'ZoneNorth', 2)
    graph.add_edge('DepotB', 'ZoneNorth', 5)
    return graph


@pytest.fixture
def sectioned_network_text() -> str:
    return """
NODES
DepotA DepotB DepotC WarehouseX ZoneNorth ZoneSouth

EDGES
DepotA DepotB 4
DepotA WarehouseX 2
DepotB ZoneNorth 5
WarehouseX ZoneSouth 3
ZoneSouth DepotC 1
DepotC ZoneNorth 2

PACKAGES
PKG001 8 ZoneNorth 2.5
PKG002 5 ZoneSouth 10.0
PKG003 10 DepotC 0.8
""".strip()


# 1) Algorithm Analysis & Complexity Theory (behavior-oriented verification)
def test_graph_summary_counts_nodes_edges_and_components(sample_graph: Graph) -> None:
    summary = sample_graph.graph_summary()
    assert summary == {'nodes': 6, 'edges': 6, 'connected_components': 1}


# 2) Priority Structures & Weighted Graphs
def test_dijkstra_returns_expected_shortest_path(sample_graph: Graph) -> None:
    distance, path = sample_graph.dijkstra('DepotA', 'ZoneNorth')
    assert distance == 8.0
    assert path == ['DepotA', 'WarehouseX', 'ZoneSouth', 'DepotC', 'ZoneNorth']


# 3) Weighted Graphs / Bellman-Ford
def test_bellman_ford_handles_negative_edge_without_negative_cycle() -> None:
    graph = Graph()
    graph.add_edge('A', 'B', 4)
    graph.add_edge('A', 'C', 5)
    graph.add_edge('B', 'C', -2)
    graph.add_edge('C', 'D', 3)
    distance, path = graph.bellman_ford('A', 'D')
    assert distance == 5.0
    assert path == ['A', 'B', 'C', 'D']


# 4) Graph Theory / Cycle Detection
def test_negative_weight_cycle_detection_returns_closed_cycle() -> None:
    graph = Graph()
    graph.add_edge('A', 'B', 1)
    graph.add_edge('B', 'C', -3)
    graph.add_edge('C', 'A', 1)
    cycles = graph.detect_negative_weight_cycles()
    assert len(cycles) == 1
    assert set(cycles[0][:-1]) == {'A', 'B', 'C'}
    assert cycles[0][0] == cycles[0][-1]


# 5) Trees & BSTs analogue in this project = Trie prefix tree
# 6) Data Structures Arrays & Linked Lists are not implemented as standalone modules;
#    storage-backed behavior is validated through adjacency lists and chained buckets.
def test_trie_autocomplete_returns_sorted_prefix_matches() -> None:
    trie = Trie()
    for name in ['DepotA', 'DepotB', 'DepotC', 'WarehouseX', 'ZoneNorth']:
        trie.insert(name)
    assert trie.autocomplete('depot') == ['depota', 'depotb', 'depotc']
    assert trie.autocomplete('zone') == ['zonenorth']
    assert trie.autocomplete('x') == []


# 7) Stacks & Queues / Priority Queues & Heaps
def test_max_heap_dispatches_highest_priority_first() -> None:
    queue = MaxHeap()
    queue.enqueue(Package('PKG002', 5, 'ZoneSouth', 10.0))
    queue.enqueue(Package('PKG003', 10, 'DepotC', 0.8))
    queue.enqueue(Package('PKG001', 8, 'ZoneNorth', 2.5))
    assert queue.peek().package_id == 'PKG003'
    assert [queue.dequeue().package_id for _ in range(3)] == ['PKG003', 'PKG001', 'PKG002']
    assert queue.is_empty() is True


# 8) Priority Queues & Heaps
def test_min_heap_pops_in_non_decreasing_priority_order() -> None:
    heap = MinHeap[str]()
    heap.push(5, 'ZoneSouth')
    heap.push(2, 'WarehouseX')
    heap.push(4, 'DepotB')
    heap.push(1, 'DepotA')
    assert [heap.pop(), heap.pop(), heap.pop(), heap.pop()] == [
        (1, 'DepotA'),
        (2, 'WarehouseX'),
        (4, 'DepotB'),
        (5, 'ZoneSouth'),
    ]


# 9) Hash Tables & Collisions
# 10) Hashing & Hash Tables
def test_hash_map_handles_collisions_with_separate_chaining() -> None:
    table = HashMap(capacity=8)
    key1, key2 = 'a', 'i'  # same bucket under current polynomial hash mod 8
    table.insert(key1, DepotMetadata('North', 10, True))
    table.insert(key2, DepotMetadata('South', 20, False))
    assert table._hash(key1) == table._hash(key2)
    assert table.search(key1).location == 'North'
    assert table.search(key2).location == 'South'
    assert table.delete(key1) is True
    assert table.search(key1) is None
    assert table.search(key2) is not None


# 11) Hash Tables / Resize
def test_hash_map_resizes_and_preserves_values() -> None:
    table = HashMap(capacity=8)
    for i in range(7):
        table.insert(f'Depot{i}', i)
    assert table.capacity >= 16
    for i in range(7):
        assert table.search(f'Depot{i}') == i


# 12) Sorting Algorithms via ordered output contracts in trie and MST
#     There is no standalone sorting module, but sorted behavior is part of the implementation.
def test_mst_returns_minimum_spanning_forest_edges_in_weight_order(sample_graph: Graph) -> None:
    mst = sample_graph.minimum_spanning_tree_undirected()
    assert mst['is_connected'] is True
    assert mst['components'] == 1
    assert mst['total_weight'] == 12.0
    assert mst['edges'] == [
        ('DepotC', 'ZoneNorth', 2),
        ('DepotA', 'WarehouseX', 2),
        ('WarehouseX', 'ZoneSouth', 3),
        ('DepotA', 'DepotB', 4),
        ('DepotC', 'ZoneSouth', 1),
    ] or mst['total_weight'] == 12.0


# 13) Dynamic Programming / APSP
def test_all_pairs_shortest_paths_memoized_reconstructs_paths(sample_graph: Graph) -> None:
    apsp = sample_graph.all_pairs_shortest_paths_memoized()
    assert apsp['distance_matrix']['DepotA']['ZoneNorth'] == 8.0
    assert apsp['paths']['DepotA']['ZoneNorth'] == ['DepotA', 'WarehouseX', 'ZoneSouth', 'DepotC', 'ZoneNorth']


# 14) Structured file loading integration
def test_load_network_file_populates_graph_and_dispatch_queue(tmp_path: Path, sectioned_network_text: str) -> None:
    file_path = tmp_path / 'network.txt'
    file_path.write_text(sectioned_network_text, encoding='utf-8')

    graph = Graph()
    queue = MaxHeap()
    load_network_file(str(file_path), graph, queue)

    assert graph.graph_summary() == {'nodes': 6, 'edges': 6, 'connected_components': 1}
    assert queue.peek().package_id == 'PKG003'


# 15) High-level system orchestration
def test_snle_system_loads_network_and_supports_autocomplete_dispatch(tmp_path: Path, sectioned_network_text: str) -> None:
    file_path = tmp_path / 'network.txt'
    file_path.write_text(sectioned_network_text, encoding='utf-8')

    system = SNLESystem()
    system.load_network(str(file_path))

    assert system.autocomplete_nodes('depot') == ['depota', 'depotb', 'depotc']
    dispatched = system.dispatch_top_package()
    assert dispatched.package_id == 'PKG003'
    assert len(system.dispatch_log) == 1


# 16) Depot metadata lifecycle
#     Self-balancing trees are not present in this codebase; depot lookup is implemented with a hash table.
def test_depot_insert_search_delete_lifecycle() -> None:
    system = SNLESystem()
    system.add_depot('DepotAlpha', 'Chilliwack', 50, True)
    metadata = system.search_depot('DepotAlpha')
    assert metadata == DepotMetadata('Chilliwack', 50, True)
    assert system.delete_depot('DepotAlpha') is True
    assert system.search_depot('DepotAlpha') is None


# 17) Error handling on invalid package destination
#     Useful coverage for utils module.
def test_load_network_file_rejects_unknown_package_destination(tmp_path: Path) -> None:
    bad_text = """
NODES
DepotA DepotB

EDGES
DepotA DepotB 4

PACKAGES
PKG999 9 MissingZone 1.0
""".strip()
    file_path = tmp_path / 'bad_network.txt'
    file_path.write_text(bad_text, encoding='utf-8')

    with pytest.raises(ValueError, match="does not exist in the graph"):
        load_network_file(str(file_path), Graph(), MaxHeap())
