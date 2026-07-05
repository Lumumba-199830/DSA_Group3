"""
========================================================
  ICS 1201 — Data Structures and Algorithms
  Lab: Depth-First Search (DFS)
========================================================

THEORY RECAP
------------
From the lecture:
  - DFS visits a node, then immediately dives as deep
    as possible into one branch before backtracking
  - It uses a STACK (Last In, First Out — LIFO)
  - Most recently discovered = explored first
  - Analogy: exploring a cave — go deep into one tunnel,
    hit a dead end, come back, try the next tunnel
  - DFS is the engine behind: cycle detection,
    topological sort, strongly connected components

THE GRAPH WE ARE USING (same as BFS lab)
------------------------------------------
    A ──► B ──► E
    │           │
    ▼           ▼
    C ──────────► F
    │
    ▼
    D ──► E

QUESTION TO THINK ABOUT BEFORE RUNNING
----------------------------------------
  BFS gave us: A, B, C, D, E, F
  
  DFS will be different. Why?
  DFS picks ONE neighbour of A (say B) and follows
  it as deep as it goes BEFORE coming back to try C or D.
  
  Trace: A → B (go deep) → E (go deep) → F (dead end)
         backtrack to A → C → (F already visited)
         backtrack to A → D → (E already visited)
  
  Your prediction: ___________________________________
"""


# ─────────────────────────────────────────────
# STEP 1 — Same graph as BFS lab
# ─────────────────────────────────────────────

graph = {
    'A': ['B', 'C', 'D'],
    'B': ['E'],
    'C': ['F'],
    'D': ['E'],
    'E': ['F'],
    'F': []
}


# ─────────────────────────────────────────────
# STEP 2 — DFS using an explicit Stack
# ─────────────────────────────────────────────
# Compare this to bfs() in bfs.py.
# The ONLY difference:
#   BFS uses deque + popleft()  → QUEUE (FIFO)
#   DFS uses list  + pop()      → STACK (LIFO)

def dfs_stack(graph, start):
    """
    DFS using an explicit stack (iterative version).
    
    Parameters:
        graph (dict): adjacency list
        start (str):  the node to begin from
        
    Returns:
        list: nodes in the order they were visited
    """
    visited = set()          # Theory: prevents revisiting — enforces simple paths
    stack   = [start]        # Theory: STACK (LIFO) — most recently discovered first
    order   = []

    while stack:

        node = stack.pop()   # ← POP from the TOP (LIFO)
                             #   This is what makes it DFS — newest discovery first

        if node not in visited:
            visited.add(node)
            order.append(node)

            for neighbour in graph[node]:
                if neighbour not in visited:
                    stack.append(neighbour)   # ← PUSH onto the TOP

    return order


# ─────────────────────────────────────────────
# STEP 3 — DFS using Recursion
# ─────────────────────────────────────────────
# Recursion uses Python's own CALL STACK.
# Each function call is a "push".
# Each return is a "pop".
# Same logic — different implementation.

def dfs_recursive(graph, node, visited=None, order=None):
    """
    DFS using recursion (Python's call stack does the work).
    
    Parameters:
        graph   (dict): adjacency list
        node    (str):  current node being visited
        visited (set):  shared set of visited nodes
        order   (list): shared list recording visit sequence
        
    Returns:
        list: nodes in the order they were visited
    """
    # Initialise on first call
    if visited is None:
        visited = set()
    if order is None:
        order = []

    visited.add(node)       # Mark current node
    order.append(node)      # Record it

    for neighbour in graph[node]:
        if neighbour not in visited:
            dfs_recursive(graph, neighbour, visited, order)   # ← GO DEEPER (recursion = push)
            # When this returns, we backtrack automatically

    return order


# ─────────────────────────────────────────────
# STEP 4 — Verbose DFS (shows stack at each step)
# ─────────────────────────────────────────────

def dfs_verbose(graph, start):
    """DFS with step-by-step output showing the stack state."""
    visited = set()
    stack   = [start]
    order   = []

    print(f"\n{'='*50}")
    print(f"  DFS (stack) starting from node '{start}'")
    print(f"{'='*50}")

    step = 1
    while stack:
        print(f"\n  Step {step} | Stack (top→bottom): {list(reversed(stack))}")
        node = stack.pop()                         # pop from TOP

        if node not in visited:
            visited.add(node)
            order.append(node)
            print(f"  ✓ Visiting '{node}' | Path so far: {order}")

            added = []
            for neighbour in graph[node]:
                if neighbour not in visited:
                    stack.append(neighbour)
                    added.append(neighbour)

            if added:
                print(f"    → Pushed onto stack: {added}")
            else:
                print(f"    → Dead end — will backtrack")

        step += 1

    print(f"\n{'='*50}")
    print(f"  DFS complete! Final order: {order}")
    print(f"{'='*50}\n")
    return order


# ─────────────────────────────────────────────
# STEP 5 — Cycle detection using DFS
# ─────────────────────────────────────────────
# Theory link: DFS can detect cycles because if
# you visit a node that is ALREADY in your current
# exploration path, you have found a cycle.
# This is one of the core applications of DFS
# mentioned in the lecture.

def dfs_has_cycle(graph):
    """
    Detect if the graph contains any cycle using DFS.
    Uses a 'recursion stack' to track the current path.
    
    Returns:
        bool: True if cycle found, False otherwise
    """
    visited    = set()
    rec_stack  = set()   # nodes currently in the DFS call stack (current path)

    def dfs_visit(node):
        visited.add(node)
        rec_stack.add(node)        # add to current path

        for neighbour in graph[node]:
            if neighbour not in visited:
                if dfs_visit(neighbour):   # go deeper
                    return True
            elif neighbour in rec_stack:   # already on current path = cycle!
                return True

        rec_stack.remove(node)     # backtrack — remove from current path
        return False

    for node in graph:
        if node not in visited:
            if dfs_visit(node):
                return True

    return False


# ─────────────────────────────────────────────
# STEP 6 — Topological sort using DFS
# ─────────────────────────────────────────────
# Theory link: from the lecture — topological sort
# orders nodes so every edge A→B has A before B.
# DFS finds this ordering using FINISH TIMES:
# a node goes into the result AFTER all its
# descendants have been fully explored.

def topological_sort(graph):
    """
    Topological sort using DFS and finish times.
    Only valid on a DAG (Directed Acyclic Graph).
    
    Returns:
        list: nodes in topological order
    """
    visited = set()
    result  = []

    def dfs_visit(node):
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                dfs_visit(neighbour)
        result.append(node)       # add AFTER all descendants — finish time

    for node in graph:
        if node not in visited:
            dfs_visit(node)

    return list(reversed(result))  # reverse gives topological order


# ─────────────────────────────────────────────
# RUN EVERYTHING
# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("\n" + "="*50)
    print("  ICS 1201 — DFS Lab")
    print("="*50)

    # Stack-based DFS
    print("\n[1] DFS (explicit stack) from A:")
    result_stack = dfs_stack(graph, 'A')
    print(f"    Order: {result_stack}")

    # Recursive DFS
    print("\n[2] DFS (recursive) from A:")
    result_rec = dfs_recursive(graph, 'A')
    print(f"    Order: {result_rec}")

    # Compare
    print("\n[3] Comparison:")
    print(f"    DFS stack    : {result_stack}")
    print(f"    DFS recursive: {result_rec}")
    print(f"    BFS would be : ['A', 'B', 'C', 'D', 'E', 'F']")
    print("    (Different orders — same graph. Why?)")

    # Verbose DFS
    print("\n[4] Verbose DFS (watch the stack):")
    dfs_verbose(graph, 'A')

    # Cycle detection
    print("\n[5] Cycle detection:")
    graph_no_cycle  = graph   # our original graph (DAG)
    graph_has_cycle = {       # add a cycle: F → A
        'A': ['B', 'C', 'D'],
        'B': ['E'],
        'C': ['F'],
        'D': ['E'],
        'E': ['F'],
        'F': ['A']            # ← this creates a cycle F→A→...→F
    }
    print(f"    Original graph has cycle: {dfs_has_cycle(graph_no_cycle)}")
    print(f"    Modified graph (F→A) has cycle: {dfs_has_cycle(graph_has_cycle)}")

    # Topological sort
    print("\n[6] Topological sort (DFS finish times):")
    topo = topological_sort(graph)
    print(f"    Result: {topo}")
    print("    Verify: every edge A→B should have A appear before B")

    print("\n" + "="*50)
    print("  EXERCISES")
    print("="*50)
    print("""
  Exercise 1 (Warm up):
    Trace dfs_verbose by hand before running it.
    Draw the stack state after each step on paper.
    Then run it and check your trace.

  Exercise 2 (Medium):
    Modify dfs_recursive to print the depth
    (how many levels deep) at each node.
    Hint: add a 'depth' parameter, start at 0,
    increment by 1 on each recursive call.

  Exercise 3 (Challenge):
    Add a node G with edge F→G to create a longer path.
    Modify topological_sort to detect a cycle and
    print "ERROR: cycle detected, cannot sort"
    instead of returning a wrong result.
    Hint: combine dfs_has_cycle with topological_sort.
""")
