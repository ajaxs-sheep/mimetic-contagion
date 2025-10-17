# Mimetic Scapegoating: Theoretical Foundations

## Abstract

This document formalizes the theory of mimetic scapegoating contagion in signed social graphs, based on René Girard's theory of the scapegoat mechanism and structural balance theory. We prove that scapegoating propagates through friendship networks as information contagion, creating both social isolation (all-against-one) and local structural balance through a single-pass, BFS-ordered process.

---

## 1. Theoretical Foundations

### 1.1 Girard's Scapegoat Mechanism

René Girard's mimetic theory posits that:

1. **Mimetic desire**: Humans imitate each other's desires, leading to rivalry
2. **Mimetic crisis**: Undifferentiated rivalries create social instability
3. **Scapegoat mechanism**: Groups resolve crisis by uniting against a single victim
4. **Sacred violence**: The collective murder creates temporary peace and social order

**Key insight**: Scapegoating is a **contagious social process**, not a rational optimization.

### 1.2 Structural Balance Theory (Heider, 1946)

In signed graphs with edges {+1, -1} representing friend/enemy relationships:

**Balanced triangles** (even number of negative edges):
- `(+, +, +)`: Friends of friends are friends ✓
- `(+, -, -)`: Enemy of enemy is friend ✓

**Unbalanced triangles** (odd number of negative edges):
- `(+, +, -)`: Friends disagree about third party ✗
- `(-, -, -)`: Mutual enemies with common enemy ✗

**Balance Theorem** (Cartwright & Harary, 1956): A balanced graph partitions into at most 2 factions where:
- All intra-faction edges are positive
- All inter-faction edges are negative

**All-against-one** is a degenerate case of structural balance: one faction of size 1, one of size N-1.

---

## 2. Mathematical Formalization

### 2.1 Definitions

**Signed Graph**: `G = (V, E, σ)` where:
- `V`: Set of nodes (actors)
- `E ⊆ V × V`: Set of undirected edges
- `σ: E → {-1, +1}`: Sign function (enemy/friend)

**Triangle**: For nodes `{u, v, w}`, triangle `T = {(u,v), (v,w), (u,w)}`

**Balance**: Triangle `T` is balanced iff `∏_{e ∈ T} σ(e) = +1`

**Social score**: For node `v`, `score(v) = |{e : e = (v,w), σ(e) = +1}| - |{e : e = (v,w), σ(e) = -1}|`

**Scapegoat state**: Node `s` is scapegoated iff `∀v ∈ V \ {s}: σ((v,s)) = -1`

### 2.2 Information Propagation Model

Scapegoating is **information contagion** through the friendship network:

**Definition (Accusation Awareness)**: At time `t`, let `A_t ⊆ V` be the set of nodes aware that `s` is the scapegoat.

**Initial state**: `A_0 = {a}` where `a` is the initial accuser.

**Propagation rule**: `A_{t+1} = A_t ∪ {v : ∃u ∈ A_t, σ((u,v)) = +1}`

Information spreads through **friendship edges only** because:
1. You hear gossip from friends, not enemies
2. You believe accusations from friends (mimetic trust)
3. Enemy communication channels are closed

**Observation**: This is standard BFS on the friendship subgraph `G^+ = (V, E^+, σ|_{E^+})` where `E^+ = {e : σ(e) = +1}`.

---

## 3. Contagion Rules

When node `v` hears about scapegoat `s`, it responds according to social pressure:

### Rule 1: Forced Choice (Friend Dilemma)

**Condition**: `v` is friend of both accuser `u ∈ A` and scapegoat `s`
- Triangle: `(v, u, s)` with edges `(v-u: +, v-s: +, u-s: -)`
- Note: Edge `u-s` is always `-` because `u ∈ A` (accusers are enemies of scapegoat)
- This forms an unbalanced `(+, +, -)` triangle

**Action**: Flip `σ((v,s)) = -1` (join accusers)

**Justification**:
- Mimetic pressure: "My friend hates them, so I must too"
- Social survival: Choosing scapegoat over friend = social death
- Preserves existing friendships (keeps edge to `u` positive)

**Result**: `v ∈ A_{t+1}`

### Rule 2: Balance Restoration (Enemy's Enemy)

**Condition**: `v` is already enemy of scapegoat `s` and enemy of accuser `u ∈ A`, forming `(-, -, -)` triangle with third party `w`

**Action**: Flip `σ((v,w)) = +1` (befriend `w`)

**Justification**:
- "Enemy of my enemy is my friend"
- Resolves unbalanced triangle
- Creates coalition against scapegoat

**Result**: Local structural balance improves

### Rule 3: Hearing Accusation (Information Creation)

**Condition**: `v` hears from friend `u ∈ A`, but has no edge to `s` yet

**Action**: Create edge `σ((v,s)) = -1`

**Justification**:
- "My friend says `s` is bad, I believe them"
- Scapegoat becomes **famous through infamy**
- Creates new negative edge (increases connectivity of `s`)

**Result**: `v ∈ A_{t+1}`, scapegoat becomes hyper-connected

---

## 4. Core Assumptions

### A1. Information Locality
Nodes make decisions based **only** on:
- Their local triangle structures
- Which neighbors are in `A_t` (accusers)
- Their relationship to scapegoat `s`

**No global optimization, no foresight**.

### A2. Friendship Propagation
Information spreads **only through positive edges** (friendships).

**Rationale**: Enemies don't share information or coordinate.

### A3. Irreversibility
Edge flips are **one-time and permanent**.

**Rationale**: "You can't un-betray someone" - social trust is fragile.

### A4. Instantaneous Decision
When node `v` is reached via BFS, it processes **immediately** before BFS continues.

**Rationale**: Ensures friends can hear from `v` if `v` becomes an accuser.

### A5. Pre-existing Enemies Count as Accusers
Nodes already hostile to `s` are in `A_0`.

**Rationale**: They were already against `s`, just waiting for a signal.

### A6. Minimal Connectivity
Graph is connected via friendship paths: `∀u,v ∈ V: ∃ path P` where `∀e ∈ P: σ(e) = +1`

**Rationale**: Disconnected components cannot coordinate scapegoating.

### A7. Accused Has Edges
Scapegoat `s` has at least one edge initially.

**Rationale**: Can't scapegoat someone who doesn't exist in social network.

---

## 5. The Algorithm

```
Algorithm: SCAPEGOAT-CONTAGION(G, s, a)
Input:
  - G = (V, E, σ): signed graph
  - s ∈ V: scapegoat
  - a ∈ V: initial accuser, σ((a,s)) ≠ 0

Output: Modified graph G' where s is isolated

1. Initialize:
   σ((a,s)) ← -1                          // Initial accusation
   A ← {a} ∪ {v : σ((v,s)) = -1}          // Include pre-existing enemies

2. BFS Traversal:
   Q ← queue([a])
   visited ← {s, a}

   while Q not empty:
     v ← Q.dequeue()

     // Process v's response to scapegoat accusation
     PROCESS-NODE(G, v, s, A)

     // Add v's friends to queue (information spreads)
     for each neighbor w of v:
       if σ((v,w)) = +1 and w ∉ visited:
         visited ← visited ∪ {w}
         Q.enqueue(w)

3. Process unreachable nodes (disconnected components)
   for each v ∈ V \ visited:
     PROCESS-NODE(G, v, s, A)

4. Return G


PROCESS-NODE(G, v, s, A):
  // Rule 3: Hear accusation
  if σ((v,s)) = 0 and ∃u ∈ A: σ((v,u)) = +1:
    CREATE-EDGE((v,s), -1)
    A ← A ∪ {v}
    return

  // Rule 1: Forced choice
  if σ((v,s)) = +1 and ∃u ∈ A: σ((v,u)) = +1:
    σ((v,s)) ← -1
    A ← A ∪ {v}
    return

  // Rule 2: Resolve all (-, -, -) triangles
  if σ((v,s)) = -1:
    for each triangle (v, s, w) where σ((v,w)) = -1 and σ((s,w)) = -1:
      σ((v,w)) ← +1                       // Befriend enemy's enemy
```

---

## 6. Properties and Guarantees

### Theorem 1: All-Against-One Convergence

**Statement**: If `G^+` (friendship subgraph) is connected, then SCAPEGOAT-CONTAGION produces all-against-one:

`∀v ∈ V \ {s}: σ((v,s)) = -1`

**Proof sketch**:

1. **Base case**: Initial accuser `a` has `σ((a,s)) = -1`, so `a ∈ A`

2. **Inductive step**:
   - BFS discovers all nodes reachable via friendship paths from `a`
   - When node `v` is discovered:
     - Either `σ((v,s)) = -1` already (pre-existing enemy → already in `A`)
     - Or `σ((v,s)) = +1` (friend of `s`)
       - Since `v` was reached via friend `u ∈ A`, Rule 1 applies
       - `v` flips to `σ((v,s)) = -1`, joins `A`
     - Or `σ((v,s)) = 0` (no edge yet)
       - Since `v` has friend in `A`, Rule 3 applies
       - Creates `σ((v,s)) = -1`, joins `A`

3. **Connectivity**: Since `G^+` is connected, all nodes reachable via BFS

4. **Conclusion**: All nodes end with `σ((v,s)) = -1` ∎

### Theorem 2: Scapegoat Hyper-Connectivity

**Statement**: Scapegoat `s` becomes the most connected (or tied for most connected) node:

`deg(s) ≥ deg(v)` for most `v ∈ V`

**Proof**:
- Initial degree: `deg_0(s) = k` for some `k ≥ 1`
- Rule 3 creates new edges to `s` for nodes with no prior connection
- If node `v` hears about `s` but has no edge, creates negative edge
- Since BFS reaches all connected nodes, and most weren't enemies initially (sparse graphs), Rule 3 fires frequently
- Final degree: `deg_f(s) → |V| - 1` (approaches complete connectivity)
- Other nodes don't systematically gain edges (only via Rule 2, which is local)

**"Famous through infamy"**: The scapegoat becomes maximally visible in the social network. ∎

### Theorem 3: Local Balance Improvement

**Statement**: The number of unbalanced triangles involving `s` decreases to zero.

**Proof**:
- Unbalanced triangles involving `s`:
  - Type `(+, +, -)`: Node is friend of both accuser and scapegoat
    - Resolved by Rule 1 (flip to `-`)
  - Type `(-, -, -)`: Two enemies of scapegoat who are mutual enemies
    - Resolved by Rule 2 (befriend third party)

- After all rules fire:
  - All edges to `s` are negative (Theorem 1)
  - All triangles involving `s` have form `(-, -, σ)` for some `σ`
  - These are balanced: `(-1) × (-1) × σ = σ` (even if `σ = -1`)

**Note**: Triangles NOT involving `s` may remain unbalanced. The algorithm creates local order around the scapegoat, not global balance. ∎

### Theorem 4: Single-Pass Convergence

**Statement**: The algorithm terminates in one BFS traversal (no iteration required).

**Proof**:
- BFS processes each node exactly once
- Nodes make irreversible decisions when processed
- No feedback loops or re-evaluation needed
- Termination: BFS terminates when queue empty (standard BFS property) ∎

---

## 7. Time Complexity Analysis

### 7.1 Worst Case

**BFS traversal**: `O(|V| + |E|)`
- Visit each node once: `O(|V|)`
- Examine each edge once: `O(|E|)`

**Per-node processing**:
- Rule 1/3 check: `O(degree(v))` to find accuser friend
- Rule 2 check: Find all `(-, -, -)` triangles
  - For each neighbor `w` of `v`: check if triangle exists
  - Triangle check: `O(1)` with adjacency list + hash set
  - Total per node: `O(degree(v)^2)` in worst case

**Total complexity**: `O(|V| + |E| + Σ_v degree(v)^2)`

For sparse graphs where `degree(v) ≤ d` (constant max degree):
- `O(|V| + |E| + |V| × d^2) = O(|V| + |E|)`

For complete graphs (`|E| = O(|V|^2)`):
- `O(|V|^3)` worst case (checking all triangles)

### 7.2 Expected Case (Sparse Graphs)

For random sparse graphs with:
- Average degree `⟨k⟩ = Θ(1)`
- `|E| = Θ(|V|)`

**Expected complexity**: `O(|V|)`

**Justification**:
- BFS visits `O(|V|)` nodes
- Average `O(1)` edges per node
- Rule 2 fires rarely in sparse graphs (few `(-, -, -)` triangles)

### 7.3 Comparison to Optimization Approaches

Traditional balance optimization via iterative flipping:
- `O(T × |V|^3)` where `T` is number of iterations to convergence
- `T` can be unbounded (no convergence guarantee)

**Our approach**: `O(|V| + |E|)` for sparse graphs, single pass, guaranteed convergence.

---

## 8. Limitations and Edge Cases

### 8.1 Disconnected Friendship Components

**Problem**: If `G^+` has multiple connected components, nodes in component without accuser don't hear accusation.

**Handling**: Process unreachable nodes separately (Step 3 of algorithm). They may:
- Already be enemies (counted as accusers)
- Remain neutral (no accuser friends, no action)

**Result**: Incomplete scapegoating possible if components isolated.

### 8.2 Accuser With No Friends

**Problem**: If accuser `a` has only enemies (`∀v: σ((a,v)) = -1`), BFS doesn't propagate.

**Interpretation**: An outcast cannot credibly scapegoat others.

**Handling**: Algorithm detects and warns. Scapegoating fails (only accuser turns against `s`).

### 8.3 Defender Strongholds (Future Work)

**Defender**: Node `v` where:
- `σ((v,s)) = +1` (friend of scapegoat)
- `∀u ∈ A: σ((v,u)) = -1` (enemy of all accusers)

**Property**: Immune to contagion (Rule 1 doesn't apply, no accuser friends).

**Status**: Not addressed in current model. Requires additional mechanisms:
- Coalition formation
- Strategic alliance building
- Counter-accusation dynamics

---

## 9. Theoretical Implications

### 9.1 Why Single-Pass Works

Traditional structural balance optimization requires iteration because:
- Global objective (minimize all unbalanced triangles)
- Flips can create new imbalances elsewhere

**Scapegoating converges in one pass because**:
1. **Directional flow**: Information spreads outward from accuser (acyclic)
2. **Local greedy + monotonic**: Each flip strictly improves balance around `s`
3. **No side effects**: Flipping edge to `s` doesn't create triangles involving other nodes
4. **Mimetic coordination**: All actors optimize same local objective (align with friends)

### 9.2 Order Through Violence

Girard's key insight: **Violence creates order**.

Our formalization shows:
- Scapegoating reduces social complexity (many opinions → one target)
- Creates local balance (all triangles involving `s` balanced)
- Requires no central coordination (emergent from local rules)
- Produces degenerate factional structure (N-1 vs 1)

This is **efficient** (linear time) but **unjust** (victim arbitrary).

### 9.3 Information Topology Matters

The friendship network `G^+` determines information flow, which determines scapegoating success.

**Dense friendship network**: High connectivity → rapid spread → complete isolation

**Sparse, clustered network**: Isolated communities → partial spread → incomplete scapegoating

**Insight**: Social media amplifies scapegoating by creating dense information networks.

---

## 10. Open Questions

1. **Multi-scapegoat dynamics**: Can multiple simultaneous accusations lead to factional splits instead of all-against-one?

2. **Resistance strategies**: What network structures or intervention rules prevent scapegoating contagion?

3. **Stochastic extensions**: What if Rules 1-3 fire probabilistically rather than deterministically?

4. **Dynamic graphs**: How does scapegoating interact with edge creation/deletion over time?

5. **Empirical validation**: Do real social media pile-ons follow these dynamics?

---

## 11. Conclusion

We have formalized Girardian scapegoating as **information contagion on signed graphs**, proving:

1. **Convergence**: Single BFS pass achieves all-against-one under connectivity assumptions
2. **Efficiency**: `O(|V| + |E|)` time for sparse graphs
3. **Local balance**: Resolves all triangles involving scapegoat
4. **Hyper-connectivity**: Scapegoat becomes maximally visible through infamy
5. **No global coordination**: Emerges from local mimetic rules

This bridges **social theory** (Girard), **graph theory** (structural balance), and **algorithmic complexity**, providing a rigorous foundation for understanding collective scapegoating as a computational social process.

---

## References

- Girard, R. (1986). *The Scapegoat*. Johns Hopkins University Press.
- Heider, F. (1946). Attitudes and cognitive organization. *Journal of Psychology*, 21, 107-112.
- Cartwright, D., & Harary, F. (1956). Structural balance: A generalization of Heider's theory. *Psychological Review*, 63(5), 277-293.
- Facchetti, G., Iacono, G., & Altafini, C. (2011). Computing global structural balance in large-scale signed social networks. *PNAS*, 108(52), 20953-20958.
