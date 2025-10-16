# Architecture & Design Philosophy

## Theoretical Foundation

### Girard's Mimetic Theory

This simulator is grounded in René Girard's theory of mimetic desire and scapegoating:

> "Balance is the mathematical shadow of a sacrificial mechanism."

Key insights:
- **Scapegoating is not optimization** - it emerges from cascading social contagion, not rational global planning
- **Unanimity creates victims** - scapegoating requires coordinated exclusion, not individual calculation
- **Mimetic behavior** - people imitate others' attitudes, leading to pile-on effects

### Structural Balance Theory

A signed graph is **structurally balanced** when all triangles satisfy the balance condition:

- **Balanced triangles**: Even number of negative edges
  - `+++` - Three mutual friends
  - `+--` - "The enemy of my enemy is my friend"

- **Unbalanced triangles**: Odd number of negative edges
  - `++-` - Two friends who share an enemy (pressure to pick sides)
  - `---` - Three mutual enemies (pressure to ally)

Unbalanced triangles create **social pressure** that drives actors to change relationships.

## Core Philosophy: Contagion vs Optimization

### What This Is NOT

This is **not** an optimization algorithm. Traditional approaches model balance-seeking as:
1. Count all unbalanced triangles in the graph
2. Find the edge flip that minimizes global imbalance
3. Repeat until fully balanced

This treats actors as omniscient optimizers with perfect information.

### What This IS

This **is** a contagion model:
1. Actors only see their **local** unbalanced triangles
2. They make **greedy, myopic decisions** based on social scores
3. Decisions are **irreversible** (no take-backs)
4. Rationality is **tunable** (from random to optimal)
5. Cascades emerge from **sequential reactions**, not global planning

This models humans making local decisions under social pressure, leading to emergent collective outcomes like scapegoating.

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI (cli.py)                        │
│  • Parse arguments                                          │
│  • Initialize graph                                         │
│  • Run simulation                                           │
│  • Format & output results                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Simulator (simulator.py)                    │
│  • Introduce perturbation                                   │
│  • Propagate cascade (round-based)                          │
│  • Track actor-edge history                                 │
│  • Select moves via rationality parameter                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ├──────────┬──────────┬─────────────────┐
                      ▼          ▼          ▼                 ▼
              ┌─────────────┐ ┌─────────┐ ┌──────────────┐ ┌──────────┐
              │   Graph     │ │Analyzer │ │  Decision    │ │Formatter │
              │ (graph.py)  │ │(.py)    │ │ (decision.py)│ │(.py)     │
              ├─────────────┤ ├─────────┤ ├──────────────┤ ├──────────┤
              │• Add/flip   │ │• Find   │ │• Choose flip │ │• Human   │
              │  edges      │ │  triangles│ │• Hate lowest│ │• JSON    │
              │• Get sign   │ │• Detect │ │  score      │ │• Chain   │
              │• Neighbors  │ │  pressure│ │• Love highest│ │          │
              │• Copy       │ │• Compute│ │  score      │ │          │
              │             │ │  scores │ │• Triangle   │ │          │
              │             │ │• Triangle│ │  delta      │ │          │
              │             │ │  delta  │ │             │ │          │
              └─────────────┘ └─────────┘ └──────────────┘ └──────────┘
```

### Data Flow

1. **Initialization**
   - Create complete graph (all positive or all negative)
   - Parse perturbation edge

2. **Perturbation**
   - Flip specified edge
   - Lock both actors from touching this edge (bidirectional lock)

3. **Cascade Loop** (round-based)
   - Find all pressured nodes (in unbalanced triangles)
   - For each pressured node:
     - Determine preferred flip (based on decision rules)
     - Calculate triangle delta for that flip
   - Select one move based on rationality (softmax weighting)
   - Execute selected flip
   - Record actor-edge pair (no-reversal tracking)
   - Repeat until stable or max steps

4. **Output**
   - Format cascade history
   - Generate human/JSON/chain outputs

## Key Design Decisions

### Decision 1: Per-Actor No-Reversal (Not Per-Edge)

**Problem**: Early implementation used per-edge tracking, preventing BOTH actors from touching an edge after one flip.

**Example**:
- Alice flips Alice↔Charlie from + to -
- Old rule: Neither Alice nor Charlie can touch this edge again
- Problem: Charlie can't respond to Alice's action

**Solution**: Track (actor, edge) pairs instead of just edges.

**Result**:
- Alice flips Alice↔Charlie: + → -
- Alice is locked from this edge
- Charlie can still respond: - → +
- Maximum 2 flips per edge total

**Rationale**: Models real human behavior where "taking back a decision" is distinct from "responding to someone else's decision."

### Decision 2: Bidirectional Perturbation Lock

**Problem**: Initial perturbation represents an external shock, not an actor's decision.

**Example**:
- Perturb Alice:Betty from + to -
- Should Alice be able to immediately flip it back?

**Solution**: Lock BOTH Alice and Betty from touching the perturbed edge.

**Rationale**: The perturbation is the inciting incident that starts the cascade. Allowing immediate reversal would defeat the purpose of studying cascade dynamics.

### Decision 3: Round-Based Selection (Not FIFO Queue)

**Problem**: Initial FIFO implementation was too myopic.

**Example (seed 42, step 4)**:
```
State: Alice-Betty(-), Betty-Charlie(-), Charlie-David(+), David-Alice(+),
       Alice-Charlie(+), Betty-David(+)

Optimal move: Alice flips Alice-Charlie to scapegoat Betty
But FIFO selected: David acts first, can't make optimal move
```

**Old Approach (FIFO)**:
```python
queue = [Alice, Betty, Charlie, David]
while queue:
    actor = queue.pop(0)  # Sequential
    flip = choose_flip(actor)
    execute(flip)
    add_new_pressured_to_queue()
```

**New Approach (Round-Based)**:
```python
while not_stable:
    pressured = find_all_pressured()  # All at once

    moves = []
    for actor in pressured:
        flip = choose_flip(actor)
        delta = calculate_triangle_delta(flip)
        moves.append((actor, flip, delta))

    best_move = select_via_rationality(moves)  # Weighted by delta
    execute(best_move)
```

**Rationale**: Humans can "see around the corner" and recognize when they're one move from optimal scapegoating. Round-based evaluation with rationality parameter models this collective intelligence.

### Decision 4: Triangle Delta Scoring

**Metric**: For each potential move, calculate how many triangles it would balance vs. unbalance.

```python
def calculate_triangle_delta(graph, edge):
    unbalanced_before = count_unbalanced_triangles(graph)

    # Simulate flip
    graph_copy = graph.copy()
    graph_copy.flip_edge(edge)

    unbalanced_after = count_unbalanced_triangles(graph_copy)

    # Positive delta = improvement
    return unbalanced_before - unbalanced_after
```

**Usage**: During round-based selection, moves with higher delta are weighted more heavily.

**Rationale**: Provides a global quality metric while maintaining local decision-making. Rationality parameter controls how much actors consider this global impact.

### Decision 5: Rationality Parameter with Softmax

**Problem**: How much global foresight should actors have?

**Solution**: Tunable rationality parameter (0.0 to 1.0) with softmax weighting.

```python
def select_move(moves, rationality):
    if rationality == 1.0:
        # Fully optimal: always pick best delta
        return max(moves, key=lambda m: m.delta)

    elif rationality == 0.0:
        # Fully myopic: random choice
        return random.choice(moves)

    else:
        # Probabilistic: softmax with temperature
        temperature = 1.0 / (rationality + 0.01)

        deltas = [m.delta for m in moves]
        weights = softmax(deltas, temperature)

        return weighted_random_choice(moves, weights)
```

**Temperature scaling**:
- High rationality (→ 1.0) = low temperature = sharper distribution (favors best moves)
- Low rationality (→ 0.0) = high temperature = flatter distribution (more random)

**Rationale**: Models spectrum from purely emotional/random behavior to intelligent strategic behavior.

## Decision-Making Logic

### Core Heuristics

Actors under pressure choose based on **social scores** (friends - enemies):

#### Rule 1: In ++- Triangles (Two Friends, One Enemy)

**"Pile-on Effect"**

```
Example: (Alice, Betty, Charlie)
  Alice-Betty: -  (enemies)
  Betty-Charlie: +  (friends)
  Alice-Charlie: +  (friends)

Alice is pressured. Options:
  1. Ally with Betty (turn --- triangle)
  2. Break with Charlie (turn +-- triangle)

Decision: Hate the person with LOWEST score
```

**Rationale**: "Easier to hate someone who's already disliked." Mimetic scapegoating - join the pile-on.

#### Rule 2: In --- Triangles (All Enemies)

**"Strategic Alliance"**

```
Example: (Alice, Betty, Charlie)
  Alice-Betty: -
  Betty-Charlie: -
  Alice-Charlie: -

Alice is pressured. Options:
  1. Ally with Betty (turn +-- triangle)
  2. Ally with Charlie (turn +-- triangle)

Decision: Love the person with HIGHEST score
```

**Rationale**: "Easiest to reconcile with the most popular person." Strategic opportunism.

### Tie-Breaking

When multiple options have the same score:
1. **With seed**: Deterministic (first in sorted order)
2. **Without seed**: Random choice

This introduces realistic variability in outcomes.

## Convergence & Termination

### Stable States

Cascade converges when **no nodes are pressured** (all triangles balanced).

Possible outcomes:
1. **Perfect scapegoat**: One node with score -N, others with score +X
2. **Factional split**: Two opposing groups with internal positive edges
3. **Complex balance**: Mixed structure with all triangles balanced

### Non-Convergence

Cascade stops at `max_steps` if:
- Stuck state: All pressured actors have no valid moves (due to no-reversal)
- Oscillation: Should be impossible with current no-reversal implementation

### Stuck States

Actor is "stuck" when:
- Under pressure (in unbalanced triangles)
- All potential flips are locked (already flipped those edges)

**Handling**: Stuck actors get -1000 penalty in triangle delta, avoiding selection.

## Output Formats

### Human-Readable (human.txt)

**Purpose**: Explain decision-making process to human observers.

**Content**:
- Initial state summary
- Each step shows:
  - Which actor is pressured
  - What unbalanced triangles they're in
  - Available options with social scores
  - Decision rationale
  - Action taken
  - New pressured nodes created
- Final state with social scores

**Use case**: Understanding why scapegoating emerged, educational analysis.

### JSON (json.json)

**Purpose**: Machine-readable complete history.

**Content**:
- Full initial and final graph states
- Every cascade step with:
  - Actor, edge, signs
  - Decision context
  - New pressured nodes
  - Stuck status
- Metadata (total steps, convergence)

**Use case**: Quantitative analysis, visualization, batch experiments.

### Chain (chain.txt)

**Purpose**: Concise event log.

**Format**:
```
PERTURB: Alice↔Betty +→-
STEP 1: David flips David↔Alice +→-
STEP 2: Alice flips Alice↔Charlie +→-
```

**Use case**: Quick pattern recognition, debugging, minimal output.

## Performance Characteristics

### Time Complexity

For graph with N nodes:
- **Triangle detection**: O(N³) - check all 3-node combinations
- **Pressure detection**: O(N³) - find all unbalanced triangles
- **Per-step cost**: O(N³) - recompute pressured nodes
- **Total cascade**: O(S × N³) where S = number of steps

### Space Complexity

- **Graph storage**: O(N²) - complete graph has N(N-1)/2 edges
- **History tracking**: O(S) - one CascadeStep per step
- **Actor-edge tracking**: O(S) - one (actor, edge) pair per flip

### Scalability

Works well for small-to-medium graphs (4-20 nodes):
- 4 nodes: ~instant
- 10 nodes: < 1 second
- 20 nodes: few seconds

For large graphs (100+ nodes), triangle detection becomes bottleneck.

## Testing & Reproducibility

### Deterministic Testing

Always use `--seed` for reproducible results:

```bash
python cli.py --nodes Alice Betty Charlie David \
              --perturb Alice:Betty \
              --seed 42  # Same result every time
```

### Known Test Cases

**Seed 42, rationality=1.0**: Alice scapegoated in 2 steps
**Seed 1, rationality=0.5**: Betty scapegoated in 2 steps
**Seed 10**: Factional split (fragmented state)

## Future Extensions

### Potential Enhancements

1. **Weighted relationships**: Edge weights beyond ±1
2. **Directed edges**: Asymmetric relationships (A likes B, B hates A)
3. **Multi-agent selection**: Multiple actors move simultaneously per round
4. **Adaptive rationality**: Rationality changes over time
5. **External interventions**: Forced reconciliations mid-cascade
6. **Network topology**: Start from non-complete graphs
7. **Visualization**: Real-time graph rendering
8. **Batch experiments**: Automated parameter sweeps

### Research Questions

- How does graph size affect scapegoating vs. fragmentation?
- What is the relationship between rationality and convergence speed?
- Can we predict which node will be scapegoated from initial topology?
- How do different perturbations affect outcomes?
- What is the critical rationality threshold for efficient scapegoating?

## References & Further Reading

### Mimetic Theory
- Girard, René. *The Scapegoat*. Johns Hopkins University Press, 1986.
- Girard, René. *Violence and the Sacred*. Johns Hopkins University Press, 1977.

### Structural Balance
- Heider, Fritz. "Attitudes and Cognitive Organization." *Journal of Psychology*, 1946.
- Cartwright & Harary. "Structural Balance: A Generalization of Heider's Theory." *Psychological Review*, 1956.

### Signed Networks
- Leskovec et al. "Signed Networks in Social Media." *CHI*, 2010.
- Marvel et al. "Continuous-Time Model of Structural Balance." *PNAS*, 2011.

## Design Philosophy Summary

This simulator prioritizes:

1. **Contagion over optimization** - Model emergent behavior, not rational planning
2. **Local decisions, global outcomes** - Actors see only their triangles, not the whole graph
3. **Irreversibility** - No take-backs, mimicking real social commitments
4. **Tunability** - Rationality parameter allows exploring spectrum of behaviors
5. **Transparency** - Human-readable output explains every decision
6. **Reproducibility** - Seed-based determinism for scientific validity

The goal is not to find optimal solutions, but to understand how **scapegoating emerges naturally** from simple local rules and social pressure.
