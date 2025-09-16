# AI_Module2_NCE

Greedy Best First Search (GBFS) – Student Notes

Subject: Artificial Intelligence / Search Algorithms
Topic: Greedy Best First Search
Reference: Stuart Russell – Artificial Intelligence: A Modern Approach

1. What is Greedy Best First Search?
 - GBFS is an informed search algorithm.
 - It uses a heuristic function h(n) to estimate the cost from the current node to the goal.
 - Strategy: Always expand the node that appears closest to the goal based on the heuristic.

Key feature: Greedy—it only looks at estimated cost to goal, ignoring the path cost so far.

2. How GBFS Works
 - Start at the initial node.
 - Evaluate heuristic h(n) for all neighbors.
 - Choose the neighbor with the lowest heuristic value.
 - Repeat until the goal node is reached.
 - Keep track of visited nodes to avoid cycles.

3. Pros and Cons
Pros
- Fast for finding a path
- Simple to implement
- Useful when heuristic is accurate	
Cons
- Not guaranteed to find the shortest path
- Can get stuck in loops if not careful
- May explore unnecessary nodes if heuristic is misleading

4. Example: Romania Map Problem
Goal: Find a path from Arad → Bucharest
Heuristic (Straight-line distance to Bucharest):
City	h(n)
Arad	366
Sibiu	253
Timisoara	329
Zerind	374
Fagaras	176
Rimnicu Vilcea	193
Bucharest	0

Graph representation (adjacency list):
Arad: Sibiu, Timisoara, Zerind
Sibiu: Arad, Fagaras, Rimnicu Vilcea, Oradea
Fagaras: Sibiu, Bucharest
Rimnicu Vilcea: Sibiu, Pitesti
Pitesti: Rimnicu Vilcea, Craiova, Bucharest
...

5. Step-by-Step GBFS Path
Start at Arad → Neighbors: Sibiu(253), Timisoara(329), Zerind(374)
Choose Sibiu (lowest h = 253)
At Sibiu → Neighbors: Arad(366), Fagaras(176), Rimnicu Vilcea(193), Oradea(380)
Choose Fagaras (h = 176)
At Fagaras → Neighbors: Sibiu(253), Bucharest(0)
Choose Bucharest (h = 0)

Path Found:
Arad → Sibiu → Fagaras → Bucharest
Note: This is not necessarily the shortest path, but GBFS chose nodes based on heuristic.

6. Key Observations
GBFS prioritizes nodes that look closest to the goal.
Does not consider total path cost (unlike A* or UCS).
Works best when heuristic is accurate and consistent.

7. Visualization (Optional for Students)
Graph nodes = cities
Edges = roads connecting cities
Heuristic values can be shown on nodes to understand GBFS decisions
GBFS path can be highlighted to see the path the algorithm took

8. Python Implementation Overview
Use a priority queue (min-heap) based on h(n).
Keep a visited set to avoid revisiting nodes.
Expand nodes step by step, always choosing the one with the lowest heuristic value.
Optional: Visualize using NetworkX + Matplotlib for better understanding.

9. Summary
GBFS = “Follow the heuristic greedily”
Fast, simple, but may not give optimal paths
Works well when heuristic is a good estimate
