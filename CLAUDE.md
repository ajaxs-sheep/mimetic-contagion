# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python simulator for scapegoating contagion in signed social graphs, based on René Girard's scapegoating theory and structural balance theory. Models scapegoating as **information contagion** through friendship networks using single-pass BFS traversal, where actors make local, mimetic decisions under social pressure.

**Core Concept**: Models how scapegoating accusations propagate through social networks. An initial accuser blames a scapegoat, and this accusation spreads through the friendship network (BFS order). Friends of accusers must choose sides under social pressure, potentially leading to all-against-one isolation, partial scapegoating, or defender strongholds.

## Running the Simulator

### Basic Command

```bash
python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --scapegoat Betty \
              --accuser Alice \
              --seed 42
```

Or use the CLI directly:

```bash
python -m src.cli [arguments]
```

### Common Options

**Graph creation**:
- `--nodes` - Space-separated list of node names (required with --initial)
- `--initial {all-positive,all-negative}` - Initial complete graph state
- `--graph-file PATH` - Load graph from file (JSON/CSV/TXT format)

**Scapegoat selection**:
- `--scapegoat NAME` - Node to be scapegoated (required or random)
- `--accuser NAME` - Initial accuser (required or random neighbor of scapegoat)

**Output**:
- `--format {human,json,chain,all}` - Output format (default: all)
- `--output-dir DIR` - Output directory (default: output/)
- `--no-files` - Print to stdout instead of saving files

**Other**:
- `--seed N` - Random seed for reproducibility (IMPORTANT: without this, results are non-deterministic)
- `--verbose` - Print BFS traversal order and decisions to stderr

### Output Files

Generates 3 files in `output/` directory:
- `*_human.txt` - Step-by-step BFS narrative with reasoning
- `*_json.json` - Machine-readable complete history with graph states
- `*_chain.txt` - Concise event log (format: `Alice: Friend of accuser, flips Alice↔Betty +→-`)

Filename format: `{nodes}_{scapegoat}-scapegoat_{accuser}-accuser_seed{seed}_{format}.{ext}`

## Architecture

### Component Structure

```
src/
├── graph.py           SignedGraph data structure (+1/-1 edges)
├── analyzer.py        Triangle detection and balance analysis
├── decision.py        Contagion rule logic (Rules 1-3)
├── simulator.py       BFS-based contagion engine (single-pass)
├── formatter.py       Output formatters (human/json/chain)
├── cli.py             Command-line interface
└── graph_loader.py    Load/save graphs from files

Tools/
├── run.py                Main entry point
├── generate_graph.py     Generate complete/sparse graphs
└── visualize_cascade.py  Create animated GIFs (requires matplotlib)
```

### Key Concepts

**Information Contagion Model**: Scapegoating spreads as information through friendship networks:
1. Initial accuser flips edge to scapegoat negative
2. Information spreads via BFS through friendship edges (you hear from friends)
3. Nodes process in BFS order, make mimetic decisions based on local triangles
4. Single-pass convergence (no iteration)

**Three Contagion Rules** (applied in order):

1. **Rule 3: Hear Accusation** (highest priority)
   - Condition: Friend of accuser, no edge to scapegoat yet
   - Action: Create negative edge to scapegoat
   - Reason: "Heard from [accuser] about [scapegoat], formed negative opinion"
   - Result: Node joins accusers, scapegoat becomes hyper-connected ("famous through infamy")

2. **Rule 1: Forced Choice** (friend dilemma)
   - Condition: Friend of both accuser and scapegoat
   - Triangle: `(node, accuser, scapegoat)` with `[+, +, -]` (unbalanced)
   - Action: Flip edge to scapegoat negative (join accusers)
   - Reason: "Friend of [accuser], chose them over [scapegoat]" (mimetic pressure)
   - Result: Node joins accusers

3. **Rule 2: Resolve --- Triangles** (enemy's enemy)
   - Condition: Already enemy of scapegoat, in `[-, -, -]` triangle with third party
   - Triangle: `(node, scapegoat, third)` with `[-, -, -]` (unbalanced)
   - Action: Befriend third party (flip to +1)
   - Reason: "In --- triangle, befriend [third] (enemy's enemy is friend)"
   - Result: Local balance improvement, coalition formation against scapegoat

**Structural Balance**: Triangles are balanced with even number of negative edges:
- `[+, +, +]` and `[+, -, -]` are balanced
- `[+, +, -]` and `[-, -, -]` are unbalanced (create social pressure)

**BFS Traversal Order**:
- Start at initial accuser
- Process nodes as they're discovered (friends first)
- Information spreads through friendship edges only (enemies don't share gossip)
- Mimics real-world rumor spreading (close friends hear first)

**Pre-existing Enemies**:
- Nodes already hostile to scapegoat are added to accusers set BEFORE BFS starts
- Ensures Rule 3 fires correctly when checking "do I have accuser friends?"

### Critical Implementation Details

1. **BFS with Immediate Processing**:
   - Process nodes AS they're dequeued (not after building full BFS list)
   - Ensures friends can hear from node if it just became an accuser
   - Queue only contains friendship edges (positive edges)

2. **Accusers Set Modified In-Place**:
   - Initialized with: initial accuser + all pre-existing enemies
   - Updated as nodes join via Rules 1 or 3
   - Other nodes check membership to determine if they've heard accusation

3. **Single-Pass Convergence**:
   - Each node processed exactly once (in BFS order)
   - No iteration, no re-evaluation
   - O(|V| + |E|) time for sparse graphs

4. **Disconnected Components**:
   - After BFS completes, process unreachable nodes separately
   - Nodes without friendship path to accuser may not hear accusation
   - Results in partial scapegoating or defender strongholds

5. **Edge Case: Accuser With No Friends**:
   - If accuser has only enemies, BFS doesn't propagate
   - Warning printed in verbose mode
   - Contagion fails (only accuser turns against scapegoat)

## Data Flow

1. **Initialize**: Create or load signed graph
2. **Select scapegoat and accuser**: Random or specified
3. **Flip initial accusation**: Accuser↔Scapegoat becomes negative
4. **Add pre-existing enemies to accusers set**
5. **BFS Traversal**:
   - Start queue with initial accuser
   - While queue not empty:
     - Dequeue current node
     - Apply contagion rules (decision.py:apply_contagion_rule)
     - Update graph (flip edges, create edges)
     - Add current's friends to queue (if not visited)
6. **Process unreachable nodes** (disconnected components)
7. **Analyze final state**: accusers, defenders, balance, all-against-one
8. **Output**: Generate human/json/chain formats

## Working with the Code

### Modifying Contagion Rules

Rules are in `src/decision.py`:
- `apply_contagion_rule(graph, node, scapegoat, accusers)`: Main entry point
  - Returns: List of `(action, reason, target_node)` tuples
  - Actions: `"join_accusers"`, `"hear_accusation"`, `"befriend_other"`, `None`
- Rule priority: 3 (hear) → 1 (forced choice) → 2 (resolve ---)
- Rules 1 and 3 return immediately (one action)
- Rule 2 returns list (all --- triangles resolved simultaneously)

### Modifying BFS Traversal

BFS is in `src/simulator.py`:
- `introduce_accusation(scapegoat, accuser)`: Main entry point
- `_propagate_scapegoat_contagion(scapegoat, accusers)`: BFS loop
  - Process nodes as dequeued (not after)
  - Queue only friendship edges
  - Modify accusers set in-place

### Triangle Analysis

Triangle operations in `src/analyzer.py`:
- `find_all_triangles(graph)`: O(N³) brute force enumeration
- `find_unbalanced_triangles(graph)`: Filter triangles by balance
- `is_triangle_balanced(graph, triangle)`: Check balance (even # of negatives)

### Graph Operations

`SignedGraph` in `src/graph.py`:
- `add_node(name)`: Add node to set
- `add_edge(u, v, sign)`: Create edge (+1 or -1)
- `flip_edge(u, v)`: Multiply sign by -1
- `get_edge(u, v)`: Returns +1, -1, or 0 (no edge)
- `has_edge(u, v)`: Check existence
- `neighbors(node)`: Return all connected nodes
- `_canonical_edge(u, v)`: Returns `(min, max)` alphabetically (undirected)

## Performance Characteristics

**Time Complexity**:
- BFS traversal: O(|V| + |E|)
- Per-node processing:
  - Rules 1/3: O(degree) to check neighbors
  - Rule 2: O(degree²) to find --- triangles
- Total: O(|V| + |E|) for sparse graphs (degree bounded)
- Complete graphs: O(|V|³) worst case

**Scalability**:
- 4-50 nodes: Instant
- 50-200 nodes: < 1 second
- 200-1000 nodes: < 10 seconds
- 1000+ nodes: Bottleneck in triangle detection

## Testing & Reproducibility

**Always use `--seed` for deterministic results**. Without seed, random selection is non-deterministic.

Known test cases:
```bash
# All-against-one (Betty isolated)
python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --scapegoat Betty \
              --accuser Alice \
              --seed 42

# Random selection
python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --seed 123

# Load custom graph
python run.py --graph-file graphs/sparse_30.json \
              --seed 42
```

## Design Philosophy

This is a **contagion model**, not an optimization algorithm:
- **Information spreads** through friendship networks (BFS)
- Actors make **local, mimetic decisions** based on triangles and accusers
- Decisions are **irreversible** (no re-evaluation)
- **Single-pass convergence** (no iteration)
- Scapegoating emerges from **cascading reactions**, not global planning

See THEORY.md for mathematical formalization and proofs.
See IMPLEMENTATION.md for detailed edge case handling and design decisions.

## Common Development Scenarios

### Analyzing Specific Contagion Behavior

Use human format with specific scapegoat/accuser:
```bash
python run.py --nodes Alice Betty Charlie David \
              --scapegoat Betty \
              --accuser Alice \
              --seed 42 \
              --format human \
              --verbose
```

### Testing Edge Cases

```bash
# Accuser with no friends (contagion fails)
python run.py --graph-file graphs/isolated_accuser.json \
              --scapegoat S \
              --accuser A \
              --seed 42

# Disconnected friendship components
python run.py --graph-file graphs/disconnected.json \
              --seed 42 \
              --verbose
```

### Generating Visualizations

```bash
# Run simulation
python run.py --nodes Alice Betty Charlie David \
              --scapegoat Betty \
              --accuser Alice \
              --seed 42

# Create animated GIF
python visualize_cascade.py \
  output/Alice-Betty-Charlie-David_Betty-scapegoat_Alice-accuser_seed42_json.json \
  -o plots/contagion_seed42.gif \
  --fps 2
```

### Batch Experiments

Generate JSON for multiple seeds and analyze programmatically:
```bash
for seed in 1 5 10 42 100; do
  python run.py --nodes Alice Betty Charlie David \
                --scapegoat Betty \
                --accuser Alice \
                --seed $seed \
                --format json
done
```

## Important Notes

- This is a **research/educational tool** for studying emergent scapegoating
- Uses only Python 3 standard library (no external dependencies for simulation)
- Visualization requires `matplotlib` and `numpy` (install separately)
- All simulation files are in `src/` package
- Use `python run.py` or `python -m src.cli` as entry point
- File naming: `{nodes}_{scapegoat}-scapegoat_{accuser}-accuser_seed{seed}_{format}.{ext}`

## Differences from Optimization-Based Approaches

**Traditional structural balance optimization**:
- Iterative edge flipping to minimize unbalanced triangles globally
- No traversal order (random or degree-based)
- May not converge, requires multiple iterations
- O(T × |V|³) where T is iteration count

**Our BFS contagion model**:
- Single-pass BFS traversal (information propagation)
- Processes nodes in friendship-first order
- Guaranteed convergence in one pass
- O(|V| + |E|) for sparse graphs
- Mimics real-world scapegoating dynamics (rumor spreading)

## Output Format Details

### Human Format
```
SCAPEGOATING CONTAGION SIMULATION

=== INITIAL STATE ===
Nodes: 4, Edges: 6 (5 positive, 1 negative)

=== INITIAL ACCUSATION ===
Scapegoat: Betty
Initial Accuser: Alice
  Edge Alice↔Betty: + → -

=== CONTAGION (BFS order from Alice) ===

Charlie:
  Friend of accuser Alice, chose them over scapegoat Betty
  Action: Charlie↔Betty: + → -
  → Charlie joins accusers

=== FINAL ANALYSIS ===
Accusers: [Alice, Charlie, David]
Defenders: None
✓ CONTAGION SUCCEEDED (all-against-one)
```

### Chain Format
```
SCAPEGOAT CONTAGION CHAIN
Scapegoat: Betty | Initial Accuser: Alice

INITIAL: Alice accuses Betty (Alice↔Betty: + → -)
STEP 1: Charlie flips Charlie↔Betty: + → -
STEP 2: David creates David↔Betty: ∅ → -
FINAL: 3 accusers, 0 defenders, ALL-AGAINST-ONE
```

### JSON Format
```json
{
  "initial_state": {"nodes": [...], "edges": [...]},
  "scapegoat": "Betty",
  "initial_accuser": "Alice",
  "decisions": [
    {
      "node": "Charlie",
      "action": "join_accusers",
      "reason": "Friend of Alice, chose them over Betty",
      "edge_flipped": ["Charlie", "Betty"],
      "from_sign": 1,
      "to_sign": -1
    }
  ],
  "final_state": {"nodes": [...], "edges": [...]},
  "accusers": ["Alice", "Charlie", "David"],
  "defenders": [],
  "is_balanced": true,
  "is_all_against_one": true,
  "contagion_succeeded": true
}
```

## Glossary

- **Scapegoat**: The victim node being isolated
- **Accuser**: Initial node that starts the accusation
- **Accusers set**: Nodes that have turned against the scapegoat
- **Defender**: Node still friendly with scapegoat
- **All-against-one**: Complete isolation (all nodes enemy of scapegoat)
- **Contagion succeeded**: True if no defenders remain
- **BFS order**: Breadth-first search traversal through friendship edges
- **Friendship edge**: Positive edge (+1)
- **Enmity edge**: Negative edge (-1)
- **Triangle**: Three nodes with all three edges present
- **Balanced triangle**: Even number of negative edges
- **Unbalanced triangle**: Odd number of negative edges
- **Social pressure**: Being in unbalanced triangle (must act to resolve)
