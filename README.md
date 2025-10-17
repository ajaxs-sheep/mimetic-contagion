# Mimetic Scapegoating Simulator

A Python-based simulator for modeling scapegoating contagion in signed social graphs, based on René Girard's theory of the scapegoat mechanism and structural balance theory.

## What is This?

This tool simulates how scapegoating accusations propagate through social networks as **information contagion**. Given an initial accusation against a scapegoat, it models how the accusation spreads through friendship networks, potentially leading to:

- **All-against-one**: Complete social isolation of the scapegoat
- **Partial scapegoating**: Some defenders remain loyal
- **Defender strongholds**: Coordinated resistance to the accusation

Unlike optimization-based approaches, this models scapegoating as **single-pass information contagion** through BFS traversal, where actors make local decisions based on mimetic social pressure.

## Installation

No external dependencies required. Uses Python 3 standard library only.

```bash
git clone <repository>
cd mimetic-contagion
```

## Quick Start

### Basic Usage

```bash
python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --scapegoat Betty \
              --accuser Alice \
              --seed 42
```

This simulates:
1. Start with 4 people who are all friends
2. Alice accuses Betty (flips Alice↔Betty to negative)
3. Information spreads through friendship network (BFS from Alice)
4. Friends of Alice hear the accusation and must choose
5. System converges to stable state (usually all-against-one)

### Output

By default, generates 3 files in `output/` directory:

- `*_human.txt` - Human-readable step-by-step narrative with reasoning
- `*_json.json` - Machine-readable JSON with complete graph states
- `*_chain.txt` - Concise event log

Example output (chain format):
```
INITIAL ACCUSATION: Alice accuses Betty
  Edge Alice↔Betty: + → -

CONTAGION (BFS order from Alice):
  Charlie: Friend of Alice, chose them over Betty
    → Charlie↔Betty: + → -
  David: Friend of Alice, chose them over Betty
    → David↔Betty: + → -

FINAL: 3 accusers, 0 defenders, ALL-AGAINST-ONE
```

## Command-Line Options

### Graph Creation

**Option 1: Complete graphs** (everyone connected to everyone):
```bash
--nodes Alice Betty Charlie David --initial all-positive
--nodes Alice Betty Charlie David --initial all-negative
```

**Option 2: Load from file**:
```bash
--graph-file graphs/my_network.json
```

Supported formats: JSON, CSV, TXT (see examples in `graphs/`)

### Scapegoat and Accuser Selection

```bash
--scapegoat Betty      # Node to be scapegoated
--accuser Alice        # Initial accuser
```

If not provided, randomly selected (requires `--seed` for reproducibility).

### Output Control

- `--format {human,json,chain,all}` - Output format (default: all)
- `--output-dir DIR` - Output directory (default: `output/`)
- `--no-files` - Print to stdout instead of saving files

### Reproducibility

```bash
--seed 42              # Random seed for deterministic results
```

**IMPORTANT**: Without `--seed`, results are non-deterministic.

### Debugging

```bash
--verbose              # Print BFS traversal order and decisions to stderr
```

## Examples

### Deterministic Scapegoating

```bash
python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --scapegoat Betty \
              --accuser Alice \
              --seed 42
```

Output: Betty completely isolated (all-against-one)

### Random Selection

```bash
python run.py --nodes Alice Betty Charlie David Eve Frank \
              --initial all-positive \
              --seed 123
```

Output: Random scapegoat and accuser chosen, contagion spreads

### Load Custom Graph

```bash
python run.py --graph-file graphs/sparse_30.json \
              --scapegoat n15 \
              --accuser n23 \
              --seed 42
```

### Print to Terminal

```bash
python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --scapegoat Betty \
              --accuser Alice \
              --seed 42 \
              --format chain \
              --no-files
```

## Understanding Output

### Human-Readable Format

Shows detailed BFS traversal and decision-making:

```
=== CONTAGION (BFS order from Alice) ===

Charlie:
  Friend of accuser Alice, chose them over scapegoat Betty
  Action: Charlie↔Betty: + → -
  → Charlie joins accusers

David:
  Heard from Charlie about Betty (no prior edge)
  Action: David↔Betty: ∅ → -
  → David joins accusers
```

### Chain Format

Concise event log:
```
INITIAL: Alice accuses Betty (Alice↔Betty: + → -)
STEP 1: Charlie flips Charlie↔Betty: + → -
STEP 2: David hears from Charlie, creates David↔Betty: ∅ → -
FINAL: ALL-AGAINST-ONE (Betty isolated)
```

### JSON Format

Machine-readable complete history including:
- Initial and final graph states (nodes, edges, signs)
- Every BFS step with node decisions
- Rule applied (join_accusers, hear_accusation, befriend_other)
- Accusers set, defenders set, balance metrics

## Key Concepts

### Information Contagion Model

Scapegoating spreads as **information through friendship networks**:

1. **Initial accusation**: Accuser flips edge to scapegoat negative
2. **BFS propagation**: Information spreads through friendship edges (you hear gossip from friends)
3. **Mimetic decisions**: Nodes choose based on local triangles and social pressure
4. **Single-pass convergence**: One BFS traversal, no iteration required

### Three Contagion Rules

**Rule 1: Forced Choice** (Friend Dilemma)
- **Condition**: You're friend of both accuser and scapegoat
- **Triangle**: `(you, accuser, scapegoat)` with `[+, +, -]` (unbalanced)
- **Action**: Flip against scapegoat (join accusers)
- **Rationale**: "My friend hates them, so I must too" (mimetic pressure)

**Rule 2: Resolve --- Triangles** (Enemy's Enemy)
- **Condition**: You're enemy of both scapegoat and some third party
- **Triangle**: `(you, scapegoat, third)` with `[-, -, -]` (unbalanced)
- **Action**: Befriend third party
- **Rationale**: "Enemy of my enemy is my friend" (strategic alliance)

**Rule 3: Hear Accusation** (Information Creation)
- **Condition**: You hear from accuser friend, no edge to scapegoat yet
- **Action**: Create negative edge to scapegoat
- **Rationale**: "My friend says they're bad, I believe them" (mimetic trust)

### Structural Balance

Triangles are **balanced** with even number of negative edges:
- `(+, +, +)` - All friends (balanced)
- `(+, -, -)` - Two enemies share enemy (balanced)
- `(+, +, -)` - Two friends disagree (unbalanced → social pressure)
- `(-, -, -)` - All enemies (unbalanced → alliance opportunity)

### BFS Traversal Order

Information spreads through friendship network:
1. Start at initial accuser
2. Process accuser's friends (Level 1)
3. Process their friends (Level 2)
4. Continue until all reachable nodes processed
5. Process disconnected components separately

**Why BFS?** Mimics real-world rumor spreading (close friends hear first).

### Single-Pass Convergence

**Unlike iterative optimization**, this algorithm:
- ✓ Processes each node exactly once (in BFS order)
- ✓ Makes irreversible decisions when processed
- ✓ Completes in O(|V| + |E|) time for sparse graphs
- ✓ No feedback loops or re-evaluation needed

## Common Scenarios

### Complete Isolation (All-Against-One)

```bash
python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --scapegoat Betty \
              --accuser Alice \
              --seed 42
```

Result:
- Betty's score: -3 (all enemies)
- Accusers: Alice, Charlie, David
- Defenders: None
- Contagion succeeded: Yes

### Partial Scapegoating (Defenders Remain)

With complex graphs or disconnected components, some defenders may remain loyal to the scapegoat.

### Accuser With No Friends (Contagion Fails)

If the accuser has only enemies, BFS doesn't propagate. The accusation fails (only accuser turns against scapegoat).

## Architecture

### Module Structure

```
src/
├── graph.py           # SignedGraph data structure (+1/-1 edges)
├── analyzer.py        # Triangle detection and balance analysis
├── decision.py        # Contagion rule logic (Rules 1-3)
├── simulator.py       # BFS-based contagion engine
├── formatter.py       # Human/JSON/chain output formatters
├── cli.py             # Command-line interface
└── graph_loader.py    # Load/save graphs from files
```

### Key Classes

**`SignedGraph`** (graph.py)
- Stores nodes and signed edges (+1/-1)
- Edges in canonical alphabetical order (undirected)
- Methods: `add_edge()`, `flip_edge()`, `get_edge()`, `neighbors()`

**`MimeticContagionSimulator`** (simulator.py)
- Main simulation engine
- `introduce_accusation()`: Run BFS contagion from accuser
- `_propagate_scapegoat_contagion()`: BFS traversal with rule application

**`ContagionDecision`** (simulator.py)
- Represents one node's decision
- Records: node, action, reason, edge flipped, sign changes

**`ScapegoatResult`** (simulator.py)
- Final simulation results
- Contains: initial/final states, decisions, accusers, defenders, balance metrics

## Performance Characteristics

**Time Complexity**:
- BFS traversal: O(|V| + |E|)
- Per-node triangle checks: O(degree²) for Rule 2
- Total: O(|V| + |E|) for sparse graphs (degree bounded)
- Complete graphs: O(|V|³) worst case

**Works well for**:
- 4-50 nodes: Instant results
- 50-200 nodes: < 1 second
- 200-1000 nodes: < 10 seconds

## Visualization

Use `visualize_cascade.py` to create animated GIFs:

```bash
python visualize_cascade.py output/..._json.json -o plots/contagion.gif --fps 2
```

Requirements: `matplotlib`, `numpy` (install separately)

Features:
- Circular node layout
- Green edges (friendship), red edges (enmity)
- Node colors: Red (scapegoat), Blue (accusers), Green (defenders)
- Frame-by-frame BFS propagation
- Final state pause

## Troubleshooting

### Non-Deterministic Results

Always use `--seed` for reproducible results:
```bash
--seed 42
```

### Accuser Has No Friends Warning

```
⚠ WARNING: Alice has no friends (only enemies)!
  → Accusation cannot spread through friendship network
```

**Solution**: Choose different accuser with friends, or this is expected (isolated accuser can't credibly scapegoat).

### Disconnected Friendship Components

If graph has isolated friendship clusters, nodes unreachable via BFS won't hear the accusation. They may remain neutral or be counted as defenders.

## Further Reading

- **THEORY.md** - Mathematical formalization, theorems, proofs
- **IMPLEMENTATION.md** - Implementation details, edge cases, design decisions
- **ARCHITECTURE.md** - High-level design philosophy
- **CLAUDE.md** - Development guide for AI assistants

## References

- René Girard - *The Scapegoat* (mimetic theory)
- René Girard - *Violence and the Sacred*
- Structural Balance Theory (Heider 1946, Cartwright & Harary 1956)
- Signed social networks and conflict resolution

## License

(Add your license here)
