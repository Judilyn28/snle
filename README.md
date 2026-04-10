# Smart Network Logistics Engine (SNLE)

**Created by: Judilyn Lucena**

## Overview
SNLE is a command-line logistics simulator that models a city delivery network as a weighted, directed graph. It combines core COMP 251 topics into one project, including graph algorithms, custom heaps, hashing, tries, memoization, and unit testing.

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

