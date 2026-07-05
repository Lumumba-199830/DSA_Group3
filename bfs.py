
"""
========================================================
  ICS 1201 — Data Structures and Algorithms
  Lab: Breadth-First Search (BFS)
========================================================

THEORY RECAP
------------
From the lecture:
  - BFS visits nodes in order of increasing distance from the start
  - It uses a QUEUE (First In, First Out — FIFO)
  - First discovered = first explored
  - Analogy: ripples in water — closest nodes first, then further out
  - Key: BFS guarantees the SHORTEST path in unweighted graphs

THE GRAPH WE ARE USING
-----------------------
    A ──► B ──► E
    │           │
    ▼           ▼
    C ──────────► F
    │
    ▼
    D ──► E

Adjacency list representation:
  A → [B, C, D]
  B → [E]
  C → [F]
  D → [E]
  E → [F]
  F → []   (no outgoing edges — this is a "sink")

QUESTION TO THINK ABOUT BEFORE RUNNING
----------------------------------------
  If we start at A, predict the BFS order.
  Remember: BFS finishes ALL nodes at distance 1
  before visiting ANY node at distance 2.
  
  Distance 0: A
  Distance 1: B, C, D      (direct neighbours of A)
  Distance 2: E, F         (neighbours of B, C, D)

  Your prediction: ___________________________________
"""

from collections import deque


# STEP 1- Define the graph as an adjacency list
# Theory link: G = (V, E)
#   V = the keys of this dictionary
#   E = the edges stored in each list
#
# This is the Digraph ADT from the lecture,
# implemented in Python.

graph = {
    'A': ['B', 'C', 'D'],    # A connects to B, C, D
    'B': ['E'],              # B connects to E
    'C': ['F'],              # C connects to F
    'D': ['E'],              # D connects to E
    'E': ['F'],              # E connects to F
    'F': []                  # F has no outgoing edges (outdegree = 0)
}


# ---------------------------------------------
# STEP 2 - The BFS function
#  ---------------------------------------------
# Notice these three ingredients:
#   visited  - a SET  (ensures simple paths- no node visited twice)
#   queue    - a DEQUE (the Queue data structure from last week)
#   order    - a LIST  (records the sequence we visit nodes)

def bfs(graph, start):
    """
    Perform Breadth-First Search on a graph.
    
    Parameters:
        graph (dict): adjacency list
        start (str):  the node to begin from
        
    Returns:
        list: nodes in the order they were visited
    """
    visited = set()              # Theory: prevents revisiting - enforces simple paths
    queue   = deque([start])     # Theory: QUEUE (FIFO) - first discovered, first explored
    order   = []                 # Records visit sequence

    while queue:                 # Keep going while there are nodes to process

        node = queue.popleft()   # - DEQUEUE from the FRONT (FIFO)
                                 #   This is what makes it BFS - oldest discovery first

        if node not in visited:
            visited.add(node)    # Mark as visited
            order.append(node)   # Record it

            # Look at all neighbours of this node
            for neighbour in graph[node]:
                if neighbour not in visited:
                    queue.append(neighbour)  # - ENQUEUE to the BACK (FIFO)

    return order


#  ---------------------------------------------
# STEP 3 - Verbose BFS (shows queue at each step)
#  ---------------------------------------------
# Run this version to SEE the queue changing.
# Compare with your hand-trace prediction above.

def bfs_verbose(graph, start):
    """BFS with step-by-step output showing the queue state."""
    visited = set()
    queue   = deque([start])
    order   = []

    print(f"\n{'='*50}")
    print(f"  BFS starting from node '{start}'")
    print(f"{'='*50}")

    step = 1
    while queue:
        print(f"\n  Step {step} | Queue contents: {list(queue)}")
        node = queue.popleft()

        if node not in visited:
            visited.add(node)
            order.append(node)
            print(f"  ✓ Visiting '{node}' | Path so far: {order}")

            added = []
            for neighbour in graph[node]:
                if neighbour not in visited:
                    queue.append(neighbour)
                    added.append(neighbour)

            if added:
                print(f"    → Added to queue: {added}")
            else:
                print(f"    → No new neighbours to add")

        step += 1

    print(f"\n{'='*50}")
    print(f"  BFS complete! Final order: {order}")
    print(f"{'='*50}\n")
    return order


#  ---------------------------------------------
# STEP 4 — BFS with distance levels
#  ---------------------------------------------
# This extends BFS to also record HOW FAR each
# node is from the start — the shortest distance.
# Theory link: distance(u,v) = length of shortest path from u to v

def bfs_with_distance(graph, start):
    """BFS that also computes shortest distance from start to every node."""
    visited   = set()
    queue     = deque([(start, 0)])   # store (node, distance) pairs
    distances = {}

    while queue:
        node, dist = queue.popleft()

        if node not in visited:
            visited.add(node)
            distances[node] = dist

            for neighbour in graph[node]:
                if neighbour not in visited:
                    queue.append((neighbour, dist + 1))   # distance increases by 1

    return distances


#  ---------------------------------------------
# STEP 5 - Path existence check (the Lars/Lene problem)
#  ---------------------------------------------
# From the lecture: "Can Lars view Lene's photos?"
# = Is there a path from Lars to Lene?
# This function answers that question for any two nodes.

def bfs_path_exists(graph, start, target):
    """
    Check if a path exists from start to target using BFS.
    Returns True if reachable, False if not.
    """
    visited = set()
    queue   = deque([start])

    while queue:
        node = queue.popleft()

        if node == target:
            return True          # Found it - stop immediately

        if node not in visited:
            visited.add(node)
            for neighbour in graph[node]:
                if neighbour not in visited:
                    queue.append(neighbour)

    return False                 # Emptied the queue without finding target


#  ---------------------------------------------
# RUN EVERYTHING
#  ---------------------------------------------

if __name__ == "__main__":

    print("\n" + "="*50)
    print("  ICS 1201 — BFS Lab")
    print("="*50)

    # Basic BFS
    print("\n[1] Basic BFS from A:")
    result = bfs(graph, 'A')
    print(f"    Order: {result}")

    # Verbose BFS — watch the queue
    print("\n[2] Verbose BFS (watch the queue):")
    bfs_verbose(graph, 'A')

    # BFS with distances
    print("\n[3] BFS with distances from A:")
    distances = bfs_with_distance(graph, 'A')
    for node, dist in sorted(distances.items()):
        bar = "─" * (dist * 4)
        print(f"    {node}: distance = {dist}  {bar}► {node}")

    # Path existence
    print("\n[4] Path existence checks (the Lars/Lene problem):")
    pairs = [('A', 'F'), ('A', 'E'), ('F', 'A'), ('C', 'B')]
    for src, tgt in pairs:
        result = bfs_path_exists(graph, src, tgt)
        symbol = "✓  Path EXISTS" if result else "✗  No path"
        print(f"    {src} → {tgt}: {symbol}")

    print("\n" + "="*50)
    print("  EXERCISES")
    print("="*50)
    print("""
  Exercise 1 (Warm up):
    Add node G with an edge from F to G.
    Re-run BFS from A. Where does G appear?
    Predict first, then run.

  Exercise 2 (Medium):
    Modify bfs_path_exists to also RETURN the
    actual path (list of nodes), not just True/False.
    Hint: store {node: parent} and trace back.

  Exercise 3 (Challenge):
    Modify bfs_with_distance to also print
    which nodes are at each level, grouped:
      Level 0: ['A']
      Level 1: ['B', 'C', 'D']
      Level 2: ['E', 'F']
""")
