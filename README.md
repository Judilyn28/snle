# Smart Network Logistics Engine (SNLE)

**Created by: Judilyn Lucena**

## Overview
SNLE is a command-line logistics simulator that models a city delivery network as a weighted, directed graph. It combines core COMP 251 topics into one project, including graph algorithms, custom heaps, hashing, tries, memoization, and unit testing.

## Repository Structure
```text
snle/
├── src/
│   ├── main.py
│   ├── graph.py
│   ├── heap.py
│   ├── hashmap.py
│   ├── trie.py
│   └── utils.py
├── data/
│   └── network.txt
├── tests/
├── README.md
└── requirements.txt
```

## Features
- Directed weighted graph using an adjacency list
- Dijkstra's algorithm with a custom `MinHeap`
- Bellman-Ford with negative-weight cycle detection
- DFS cycle detection using node coloring
- Max-heap package dispatch queue
- Custom hash map with collision handling and resizing
- Trie-based autocomplete for depot and zone names
- Minimum spanning forest of the undirected graph projection
- Memoized all-pairs shortest paths using dynamic programming
- ASCII graph view and matplotlib visualization

## Input File Format
```text
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
```

## How to Run
From the project root:

```bash
python src/main.py
```

## CLI Menu
When launched, `src/main.py` opens the required interactive menu:

```text
1. Display Network Summary
2. Find Shortest Path
3. Detect Cycles
4. Dispatch Highest-Priority Package
5. Search Depot by Name
6. Autocomplete Depot Name
7. Exit
```

## Running Tests
```bash
python -m unittest discover -s tests -v
```

## Complexity Summary
- Graph construction: `O(V + E)`
- Dijkstra with custom min-heap: `O((V + E) log V)`
- Bellman-Ford: `O(VE)`
- DFS cycle detection: `O(V + E)`
- Max-heap enqueue/dequeue: `O(log n)`
- Hash map insert/search/delete average case: `O(1)`
- Trie insert/autocomplete: `O(L)` for insert and prefix traversal, plus output size for collection
- Kruskal MST on the undirected projection: `O(E log E)`
- Memoized all-pairs shortest paths: `O(V^3)` time and `O(V^3)` space

## Notes
- `tests/` is optional in the original structure, but included here for grading support.
- The project uses only custom heap and hash-table implementations for the required algorithms and lookups.
