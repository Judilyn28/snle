"""
Smart Network Logistics Engine (SNLE)

Course: COMP 251
Project: Final Capstone – Graph-Based Logistics System

Description:
This application models a city-wide courier delivery network using
weighted, directed graphs and custom data structures.

Created by: Judilyn Lucena
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from utils import SNLESystem


def print_menu() -> None:
    print("\n----- Smart Network Logistics Engine -----")
    print("Created by: Judilyn Lucena")
    print("1. Display Network Summary")
    print("2. Find Shortest Path")
    print("3. Detect Cycles")
    print("4. Dispatch Highest-Priority Package")
    print("5. Search Depot by Name")
    print("6. Autocomplete Depot Name")
    print("7. Exit")
    print("------------------------------------------")


def prompt_bool(message: str) -> bool:
    while True:
        value = input(message).strip().lower()
        if value in {"y", "yes", "true", "1"}:
            return True
        if value in {"n", "no", "false", "0"}:
            return False
        print("Please enter yes or no.")


def handle_action(action: Callable[[], None]) -> None:
    try:
        action()
    except Exception as exc:
        print(f"Error: {exc}")


def network_summary(system: SNLESystem, current_file: str) -> None:
    summary = system.graph.graph_summary()
    print("\nNetwork Summary")
    print(f"Source file: {current_file}")
    print(f"Nodes: {summary['nodes']}")
    print(f"Edges: {summary['edges']}")
    print(f"Weakly Connected Components: {summary['connected_components']}")
    print(f"Loaded packages: {len(system.dispatch_queue)}")

    if input("Show ASCII graph view? (y/n): ").strip().lower() in {"y", "yes"}:
        print(system.graph.ascii_art())

    if input("Save matplotlib plot? (y/n): ").strip().lower() in {"y", "yes"}:
        output_path = input("Output file [network_plot.png]: ").strip() or "network_plot.png"
        saved = system.graph.plot_network_matplotlib(output_path)
        print(f"Saved to: {saved}")

    if input("Compute MST of undirected version? (y/n): ").strip().lower() in {"y", "yes"}:
        result = system.graph.minimum_spanning_tree_undirected()
        label = "Minimum spanning tree" if result["is_connected"] else "Minimum spanning forest"
        print(label)
        print(f"Components: {result['components']}")
        print(f"Total weight: {result['total_weight']}")
        for src, dest, weight in result["edges"]:
            print(f"- {src} -- {dest} ({weight})")


def shortest_path_menu(system: SNLESystem) -> None:
    print("\nShortest Path Options")
    print("1. Dijkstra")
    print("2. Bellman-Ford")
    print("3. Memoized All-Pairs Shortest Paths")
    choice = input("Choose an option: ").strip()

    if choice in {"1", "2"}:
        src = input("Source: ").strip()
        dest = input("Destination: ").strip()
        if choice == "1":
            cost, path = system.graph.dijkstra(src, dest)
            method = "Dijkstra"
        else:
            cost, path = system.graph.bellman_ford(src, dest)
            method = "Bellman-Ford"
        print(f"Method: {method}")
        if not path:
            print("No path found.")
        else:
            print(f"Shortest path: {' -> '.join(path)}")
            print(f"Total cost: {cost}")
            if input("Count routes within stop limit? (y/n): ").strip().lower() in {"y", "yes"}:
                max_stops = int(input("Maximum stops: ").strip())
                count = system.graph.count_routes_memo(src, dest, max_stops)
                print(f"Possible routes within {max_stops} stops: {count}")
    elif choice == "3":
        result = system.graph.all_pairs_shortest_paths_memoized()
        nodes = result["nodes"]
        if not nodes:
            print("Graph is empty.")
            return
        print("Nodes:", ", ".join(nodes))
        header = "From/To".ljust(16) + "".join(node.ljust(16) for node in nodes)
        print(header)
        for src in nodes:
            row = src.ljust(16)
            for dest in nodes:
                distance = result["distance_matrix"][src][dest]
                row += ("INF" if distance == float("inf") else str(distance)).ljust(16)
            print(row)
        src = input("Source for reconstructed path: ").strip()
        dest = input("Destination for reconstructed path: ").strip()
        path = result["paths"].get(src, {}).get(dest, [])
        if not path:
            print("No path found.")
        else:
            print(f"Shortest path: {' -> '.join(path)}")
            print(f"Total cost: {result['distance_matrix'][src][dest]}")
    else:
        print("Invalid option.")


def cycle_menu(system: SNLESystem) -> None:
    print("\nCycle Detection Options")
    print("1. Standard DFS cycle detection")
    print("2. Negative-weight cycle detection")
    choice = input("Choose an option: ").strip()
    if choice == "1":
        cycles = system.graph.find_cycles()
        if not cycles:
            print("No cycles detected.")
        else:
            for i, cycle in enumerate(cycles, start=1):
                print(f"{i}. {' -> '.join(cycle)}")
    elif choice == "2":
        scope = input("Start node (blank = whole graph): ").strip() or None
        cycles = system.graph.detect_negative_weight_cycles(scope)
        if not cycles:
            print("No negative-weight cycles detected.")
        else:
            for i, cycle in enumerate(cycles, start=1):
                print(f"{i}. {' -> '.join(cycle)}")
    else:
        print("Invalid option.")


def dispatch_menu(system: SNLESystem) -> None:
    top_package = system.dispatch_queue.peek()
    if top_package is None:
        print("Dispatch queue is empty.")
        return
    print(f"Next package: {top_package}")
    if input("Dispatch now? (y/n): ").strip().lower() in {"y", "yes"}:
        print(f"Dispatched: {system.dispatch_top_package()}")
    elif input("Add package instead? (y/n): ").strip().lower() in {"y", "yes"}:
        package_id = input("Package ID: ").strip()
        priority = int(input("Priority (1-10): ").strip())
        destination = input("Destination: ").strip()
        weight = float(input("Weight (kg): ").strip())
        system.enqueue_package(package_id, priority, destination, weight)
        print(f"New top-priority package: {system.dispatch_queue.peek()}")


def search_depot_menu(system: SNLESystem) -> None:
    name = input("Depot name to search: ").strip()
    depot = system.search_depot(name)
    if depot is None:
        print("Depot not found.")
        if input("Add depot metadata now? (y/n): ").strip().lower() in {"y", "yes"}:
            location = input("Location: ").strip()
            capacity = int(input("Capacity: ").strip())
            active = prompt_bool("Active? (yes/no): ")
            system.add_depot(name, location, capacity, active)
            print("Depot inserted successfully.")
    else:
        print(depot)
        if input("Delete this depot metadata? (y/n): ").strip().lower() in {"y", "yes"}:
            print("Depot deleted." if system.delete_depot(name) else "Depot not found.")


def autocomplete_menu(system: SNLESystem) -> None:
    prefix = input("Prefix: ").strip()
    matches = system.autocomplete_nodes(prefix)
    if matches:
        for match in matches:
            print(f"- {match}")
    else:
        print("No matches found.")


def main() -> None:
    system = SNLESystem()
    default_network = Path(__file__).resolve().parent.parent / "data" / "network.txt"
    current_file = str(default_network)
    system.load_network(current_file)

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            handle_action(lambda: network_summary(system, current_file))
        elif choice == "2":
            handle_action(lambda: shortest_path_menu(system))
        elif choice == "3":
            handle_action(lambda: cycle_menu(system))
        elif choice == "4":
            handle_action(lambda: dispatch_menu(system))
        elif choice == "5":
            handle_action(lambda: search_depot_menu(system))
        elif choice == "6":
            handle_action(lambda: autocomplete_menu(system))
        elif choice == "7":
            print("Exiting SNLE. Goodbye.")
            break
        else:
            print("Invalid choice. Please choose 1-7.")


if __name__ == "__main__":
    main()
