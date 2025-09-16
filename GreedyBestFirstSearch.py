import heapq
import matplotlib.pyplot as plt
import networkx as nx

# -------------------------
# Graph Representation of Romania Map
# -------------------------
# Each key represents a city (node) in the map.
# The corresponding value is a list of cities (neighbors) directly connected by a road (edges).
# This is called an adjacency list representation of a graph.
graph = {
    'Arad': ['Sibiu', 'Timisoara', 'Zerind'],        # Arad connected to Sibiu, Timisoara, Zerind
    'Sibiu': ['Arad', 'Fagaras', 'Rimnicu Vilcea', 'Oradea'],  # Sibiu connected to Arad, Fagaras, Rimnicu Vilcea, Oradea
    'Timisoara': ['Arad', 'Lugoj'],                 # Timisoara connected to Arad, Lugoj
    'Zerind': ['Arad', 'Oradea'],                   # Zerind connected to Arad, Oradea
    'Oradea': ['Zerind', 'Sibiu'],                 # Oradea connected to Zerind, Sibiu
    'Fagaras': ['Sibiu', 'Bucharest'],             # Fagaras connected to Sibiu, Bucharest
    'Rimnicu Vilcea': ['Sibiu', 'Pitesti'],        # Rimnicu Vilcea connected to Sibiu, Pitesti
    'Lugoj': ['Timisoara', 'Mehadia'],             # Lugoj connected to Timisoara, Mehadia
    'Mehadia': ['Lugoj', 'Drobeta'],               # Mehadia connected to Lugoj, Drobeta
    'Drobeta': ['Mehadia', 'Craiova'],             # Drobeta connected to Mehadia, Craiova
    'Craiova': ['Drobeta', 'Pitesti'],             # Craiova connected to Drobeta, Pitesti
    'Pitesti': ['Rimnicu Vilcea', 'Craiova', 'Bucharest'],  # Pitesti connected to Rimnicu Vilcea, Craiova, Bucharest
    'Bucharest': ['Fagaras', 'Pitesti']           # Bucharest connected to Fagaras, Pitesti
}

# -------------------------
# Heuristic values: straight-line distance to Bucharest
# -------------------------
# Each key = city
# Each value = estimated distance from that city to Bucharest (h(n))
heuristic = {
    'Arad': 366, 'Sibiu': 253, 'Timisoara': 329, 'Zerind': 374,
    'Oradea': 380, 'Fagaras': 176, 'Rimnicu Vilcea': 193,
    'Lugoj': 244, 'Mehadia': 241, 'Drobeta': 242, 'Craiova': 160,
    'Pitesti': 100, 'Bucharest': 0
}

# -------------------------
# Greedy Best First Search Algorithm
# -------------------------
def greedy_best_first_search(start, goal):
    visited = set()
    pq = [(heuristic[start], start, [start])]  # (h(n), current_node, path)
    step = 1

    while pq:
        h, current, path = heapq.heappop(pq)

        # Log the expansion step
        print(f"\nStep {step}: Expanding {current} (h={h}), Path so far: {' -> '.join(path)}")
        step += 1

        # Goal check
        if current == goal:
            print("\n🎯 Goal reached!")
            return path

        # Expand neighbors
        if current not in visited:
            visited.add(current)
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    heapq.heappush(pq, (heuristic[neighbor], neighbor, path + [neighbor]))

    return None

# -------------------------
# Run the Search
# -------------------------
start, goal = "Arad", "Bucharest"
path = greedy_best_first_search(start, goal)
print("\n✅ Final Greedy Best First Search Path:", " -> ".join(path))

# -------------------------
# Graph Visualization with Heuristic Labels
# -------------------------
G = nx.Graph()
for city, neighbors in graph.items():
    for neighbor in neighbors:
        G.add_edge(city, neighbor)

plt.figure(figsize=(12, 10))
pos = nx.spring_layout(G, seed=42)  # layout for better visualization

# Draw all nodes and edges
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue",
        font_size=10, font_weight="bold", edge_color="gray")

# Draw heuristic values as numeric labels below the city names
h_labels = {city: str(heuristic[city]) for city in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=h_labels, font_color="red", font_size=9, verticalalignment='bottom')

# Highlight the GBFS path if found
if path:
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='orange')   # path nodes
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2)  # path edges

plt.title("Romania Map Graph with GBFS Path and Heuristic Values", fontsize=14)
plt.show()
