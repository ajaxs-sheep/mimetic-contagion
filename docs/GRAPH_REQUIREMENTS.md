# Graph Structure Requirements for Unity Achievement

## TL;DR

**For guaranteed unity achievement, every node must have at least 2 positive edges (2 friends).**

## The Fundamental Constraint

### Simple Statement
"Every node must have degree ≥ 2 in the positive edge subgraph"

### Formal Statement
For any choice of scapegoat S, every other node v must have at least one positive edge to some node other than S:

```
∀ S ∈ V, ∀ v ∈ V \ {S}: ∃ w ∈ V \ {S, v} : edge(v, w) = +1
```

## Why This Matters

### The Dead End Problem

If ANY node v has the scapegoat as their ONLY friend:

1. When v joins the accusers, the edge v↔scapegoat flips to negative
2. Node v now has **zero positive edges** (isolated)
3. BFS can only propagate through positive edges
4. BFS **cannot continue through** node v
5. Any nodes reachable **only via** v will never hear the accusation
6. **Unity fails** for that portion of the graph

### This Applies to ALL Nodes, Not Just the Accuser

The original observation was about accuser isolation, but the problem is **general**:
- **Accuser** with only 1 friend (scapegoat) → contagion cannot start
- **Intermediate node** with only 1 friend (scapegoat) → contagion cannot continue through them
- **Leaf node** with only 1 friend (scapegoat) → leaf is unreachable but doesn't block others

## Examples

### Fails: Star Graph (Periphery Nodes Have Degree 1)
```
       P1
        |
    P2--H--P3
        |
       P4
```
If scapegoat is hub H, periphery nodes (P1-P4) each have only H as friend.
After joining accusers, they become isolated.

### Fails: Chain Where Nodes Only Friend Scapegoat
```
A → B → C → D
    ↓   ↓   ↓
    S   S   S
```
If each of B, C, D has scapegoat S as only friend, contagion stops after B.

### Works: Ring Graph (Every Node Has Degree 2)
```
n0 - n1 - n2
|         |
n5 - n4 - n3
```
Every node has 2 friends. After any node joins accusers, they still have 1 friend remaining for BFS propagation.

### Works: Sparse Graph with min_degree ≥ 2
Every node guaranteed to have at least 2 friends, ensuring no dead ends.

## Sufficient Conditions

### Strong Sufficient Condition
1. Every node has ≥2 positive edges
2. Positive edge subgraph is connected

**Guarantees**: Unity will be achieved (assuming reasonably high p_positive)

### Weaker Sufficient Condition
1. Positive edge subgraph is connected
2. No node has scapegoat as their only friend (for any choice of scapegoat)

## Implications for Graph Generation

### For Testing/Simulation

When generating graphs for testing:

**Option 1: Enforce min_degree ≥ 2**
```python
graph = generate_sparse_graph(
    num_nodes=1000,
    min_degree=2,  # Critical!
    max_degree=10,
    p_positive=0.7
)
```

**Option 2: Check Prerequisites Before Simulation**
```python
def is_scapegoating_viable(graph, scapegoat):
    """Check if unity is achievable for this scapegoat."""
    for node in graph.nodes:
        if node == scapegoat:
            continue

        friends = [n for n in graph.neighbors(node)
                   if graph.get_edge(node, n) == 1]

        # Check if scapegoat is their only friend
        if len(friends) == 1 and scapegoat in friends:
            return False, f"{node} has scapegoat as only friend"

    return True, "Prerequisites satisfied"
```

**Option 3: Accept Failures as Realistic**

Acknowledge that some social structures naturally resist scapegoating. This is realistic behavior!

### For Real-World Analysis

When analyzing actual social networks:
- Low-degree nodes are vulnerability points for contagion propagation
- Network topology determines scapegoating success
- Bridge nodes with few friends can block entire subgraphs
- Dense, well-connected networks support scapegoating better

## Ring Graph Special Case

Ring graphs are interesting:
- Every node has exactly degree 2 ✓
- **Should work** if all edges are positive
- **Can fail** if there are negative edges breaking connectivity

In the 300-node ring that failed in stress tests:
- With p_positive=0.7, ~30% of edges were negative
- Negative edges break the ring into multiple chains
- If chains are connected only through scapegoat, isolation occurs

## Minimum Viable Graph

The smallest graph that guarantees unity for any scapegoat choice:
- **3 nodes, all connected with positive edges** (complete graph K₃)
- All nodes have degree 2
- Removing any node leaves a connected graph
- Unity always achieved

## Theoretical Implications

### Social Structure Prerequisites

This reveals that scapegoating is not inevitable - it requires:
1. **Sufficient social connectivity** (min degree ≥ 2)
2. **Cohesive community structure** (connected positive subgraph)
3. **No critical bridge individuals** (nodes with single friends)

### Girardian Interpretation

Aligns with René Girard's theory:
- **Community cohesion is prerequisite** for collective scapegoating
- **Isolated individuals cannot rally others** against scapegoat
- **Social structure determines scapegoating viability**
- **Failed scapegoating attempts** are realistic in fragmented communities

### Information Contagion Limits

BFS propagation through friendship networks has natural limits:
- Information cannot cross negative edges (enemies don't gossip)
- Single-friend nodes become information dead ends
- Network topology creates natural barriers to contagion

## Documentation Locations

This constraint should be documented in:
1. **README.md** - User-facing requirements for valid input graphs
2. **THEORY.md** - Formal prerequisites section
3. **IMPLEMENTATION.md** - Edge case handling for isolated nodes
4. **Graph generators** - Default to min_degree ≥ 2
5. **Simulator warnings** - Detect and warn about potential dead ends

## Summary

**Original (Incomplete)**: "Each node must have at least one positive edge"

**Corrected (Complete)**: "Each node must have at least TWO positive edges, or more precisely, at least one positive edge to a node OTHER than the scapegoat (for any choice of scapegoat)"

**Practical**: Use min_degree ≥ 2 when generating graphs to guarantee unity is achievable.

**Realistic**: Graphs that violate this constraint model social structures where scapegoating naturally fails - this is correct behavior, not a bug.
