# Prerequisites for Unity Achievement

## Critical Finding

**The algorithm can fail to achieve unity even in connected graphs** if the accuser becomes isolated after the initial accusation.

## The Problem

When the accuser's **only positive edge** is to the scapegoat:

1. Initial accusation flips that edge to negative
2. Accuser now has **zero friends**
3. BFS cannot propagate (information only travels through positive edges)
4. Result: Only accuser turns against scapegoat, everyone else unreachable

## Example 1: Accuser Isolation (Your Original 4-Node Case)

```
Initial graph:
  Betty ↔ David: +1 (friends)
  David ↔ Charlie: -1 (enemies)
  Charlie ↔ Alice: +1 (friends)
  Alice ↔ Betty: 0 (no edge)
```

**Scapegoat**: Betty
**Accuser**: David

**What happens**:
1. David accuses Betty → flips David↔Betty to negative
2. David now has NO positive edges (only enemy: Charlie)
3. David cannot tell anyone about Betty
4. Alice and Charlie never hear the accusation
5. **Result**: 1 accuser out of 3, unity FAILS

## Fixed Version

Add **one edge**: David ↔ Alice: +1

**What happens**:
1. David accuses Betty → flips David↔Betty to negative
2. David still has friend: Alice
3. David tells Alice about Betty
4. Alice tells Charlie about Betty
5. David and Charlie become friends (Rule 2: enemy's enemy)
6. **Result**: All 3 turn against Betty, unity SUCCEEDS ✓

## Example 2: Intermediate Dead End (The General Problem)

**CRITICAL**: This is not just about the accuser! ANY node whose only friend is the scapegoat becomes a dead end.

```
Graph structure:
  Accuser → Node1 → Node2 → Node3
              ↓
          Scapegoat

Edges:
  Accuser ↔ OtherFriend: +1 (Accuser has other friends, so accuser is fine)
  Accuser ↔ Node1: +1
  Accuser ↔ Scapegoat: +1
  Node1 ↔ Scapegoat: +1 (Node1's ONLY friend!)
  Node1 ↔ Node2: -1 (enemies)
  Node2 ↔ Node3: +1
```

**What happens**:
1. Accuser accuses Scapegoat
2. Accuser tells Node1 and OtherFriend
3. Node1 joins accusers (Rule 1: friend of accuser + friend of scapegoat)
4. **Node1 now has ZERO friends** (Scapegoat edge is negative, Node2 is enemy)
5. BFS cannot propagate **through** Node1
6. Node2 and Node3 never hear about Scapegoat

**Result**: Only Accuser, OtherFriend, and Node1 turn against Scapegoat. Node2 and Node3 are unreachable.

**Lesson**: The dead end problem applies to **ANY** node in the propagation chain, not just the initial accuser.

## Formalized Prerequisites

### Necessary Condition 1: Universal Non-Isolation (CORRECTED)

**Original (Too Weak)**: "The accuser must have at least one friend besides the scapegoat"

**Corrected (General)**: "EVERY node (not just the accuser) must have at least one friend besides the scapegoat"

**Formal**: ∀ S ∈ V, ∀ v ∈ V \ {S}: ∃ w ∈ V \ {S, v} : edge(v, w) = +1

**Equivalent**: Every node must have degree ≥ 2 in the positive edge subgraph (at least 2 friends)

**English**: For any choice of scapegoat, every other node must have at least ONE positive edge to some node other than the scapegoat.

**Why This Matters**: If ANY node's only friend is the scapegoat:
1. When that node joins accusers, the edge flips negative
2. That node now has ZERO positive edges
3. BFS cannot propagate **through** that node
4. Any nodes reachable **only** via that node will never hear the accusation

**Violation**: Any node with degree 1 (only one friend) creates a potential dead end in BFS propagation.

### Necessary Condition 2: Friendship Connectivity

**Formal**: For all v ∈ V \ {scapegoat}, there exists a path from accuser to v using only positive edges (after initial flip).

**English**: The friendship subgraph must be connected.

**Violation**: Disconnected components mean some nodes cannot hear the accusation.

### Sufficient Condition (Simple)

**Each node has ≥2 positive edges** AND **friendship graph is connected**.

This guarantees:
- Accuser has at least one friend besides scapegoat
- Information can reach all nodes via BFS
- Unity will be achieved (assuming high positive edge ratio)

### Weaker Sufficient Condition

**Friendship graph is connected** AND **accuser has ≥1 friend besides scapegoat**.

This allows some nodes to have degree 1, as long as accuser isn't one of them.

## Observed Failures in Stress Tests

### Ring Graph (300 nodes)
- **Structure**: Circular chain, each node has exactly 2 neighbors
- **Problem**: If accuser's neighbors are both the scapegoat and one other node with negative edge, isolation occurs
- **Result**: 1 accuser out of 299 (catastrophic failure)
- **Actual data**:
  - Accusers: 1
  - Defenders: 1
  - Decisions: 1 (only initial flip)
  - Unity: FALSE

### Star Graph (300 nodes)
- **Structure**: Hub connected to all others, periphery nodes have no edges
- **Result**: Depends on who is scapegoat
  - If hub is scapegoat: Works (hub has many friends)
  - If periphery is scapegoat and accuser is periphery: FAILS (accuser isolated)
- **Actual data**: 213 accusers out of 299 (partial success)

## Why This Matters

### Realistic Behavior
This isn't a bug - it's **realistic social dynamics**:
- Scapegoating requires sufficient social connectivity
- An isolated accuser cannot spread their accusation
- This models "failed scapegoating attempts" in real life
- Some social structures are inherently resistant to scapegoating

### Theoretical Implications

1. **Connectivity threshold**: Scapegoating requires minimum social density
2. **Accuser selection matters**: Not all accusers are equally effective
3. **Graph structure affects dynamics**: Sparse graphs more vulnerable to failure
4. **Information bottlenecks**: Negative edges can block contagion

## Recommendations

### For Test Generation

When generating test graphs:
1. **Ensure min_degree ≥ 2** (sparse graphs)
2. **OR**: Manually verify accuser has friends besides scapegoat
3. **OR**: Pre-check prerequisites before running simulation
4. **OR**: Accept that some graphs will fail (document as realistic!)

### For Simulator Enhancement

Add **prerequisite checking**:

```python
def check_prerequisites(graph, scapegoat, accuser):
    """Check if unity is achievable."""
    # Check accuser's friends excluding scapegoat
    friends = [n for n in graph.neighbors(accuser)
               if graph.get_edge(accuser, n) == 1 and n != scapegoat]

    if len(friends) == 0:
        return False, "Accuser will become isolated after initial accusation"

    # Check friendship connectivity
    # ... (BFS reachability check)

    return True, "Prerequisites satisfied"
```

### For Random Accuser Selection

**Current**: Random selection from scapegoat's neighbors

**Better**: Filter to ensure accuser has other friends

```python
def select_viable_accuser(graph, scapegoat):
    """Select accuser who won't become isolated."""
    candidates = []

    for neighbor in graph.neighbors(scapegoat):
        if graph.get_edge(neighbor, scapegoat) == 1:  # Friend
            other_friends = [n for n in graph.neighbors(neighbor)
                           if n != scapegoat and graph.get_edge(neighbor, n) == 1]
            if len(other_friends) > 0:
                candidates.append(neighbor)

    return random.choice(candidates) if candidates else None
```

## Mathematical Characterization

### Graph Property: "Scapegoating-Viable"

A graph G = (V, E) with signed edges is **scapegoating-viable** for scapegoat s if:

∀ viable accusers a ∈ neighbors(s):
  - edge(a, s) = +1 (friends)
  - degree_positive(a) ≥ 2 (has other friends)
  - ∃ positive path from a to all v ∈ V \ {s}

### Minimum Viable Graph

For unity to be guaranteed, minimum requirements:
- |V| ≥ 3
- |E_positive| ≥ V (connected spanning tree of positive edges)
- degree_positive(accuser) ≥ 2
- Friendship graph is connected

## Implications for Girard's Theory

This finding aligns with Girard's scapegoat mechanism:

1. **Social cohesion prerequisite**: Community must have sufficient internal bonds
2. **Isolation paradox**: An isolated accuser cannot rally the community
3. **Structural requirements**: Scapegoating requires specific social topology
4. **Failed attempts**: Not all scapegoating attempts succeed in real life

The algorithm correctly captures that **scapegoating is not inevitable** - it requires favorable social conditions.

## Future Work

1. **Characterize failure modes**: Catalog graph structures that prevent unity
2. **Probability analysis**: Given random graph, P(unity | structure)
3. **Optimal accuser selection**: Algorithm to maximize unity probability
4. **Connectivity threshold**: Minimum edge density for guaranteed unity
5. **Resilience metrics**: How many edge removals before unity becomes impossible

---

**Key Takeaway**: Your observation is not just correct - it reveals a fundamental property of the scapegoating mechanism. The algorithm is working as intended, modeling realistic social dynamics where connectivity and structure determine whether scapegoating succeeds or fails.
