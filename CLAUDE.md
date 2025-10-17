# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python simulator for mimetic contagion in signed social graphs, based on René Girard's scapegoating theory and structural balance theory. Unlike optimization-based approaches, this models contagion as cascading social events where actors make local, greedy decisions under social pressure.

**Core Concept**: Models how social conflicts propagate through networks when an initial perturbation creates structural imbalance. Actors respond to social pressure by flipping relationships, potentially leading to scapegoating, factional splits, or balanced configurations.

## Running the Simulator

### Basic Command

```bash
python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42
```

Or use the CLI directly:

```bash
python -m src.cli [arguments]
```

### Common Options

- `--nodes` - Space-separated list of node names (required)
- `--perturb Node1:Node2` - Edge to flip as initial perturbation (required)
- `--initial {all-positive,all-negative}` - Initial graph state (default: all-positive)
- `--seed N` - Random seed for reproducibility (IMPORTANT: without this, results are non-deterministic)
- `--rationality 0.0-1.0` - Decision quality (0.0=random, 0.5=balanced, 1.0=optimal)
- `--max-steps N` - Maximum cascade steps (default: 1000)
- `--format {human,json,chain,all}` - Output format (default: all)
- `--output-dir DIR` - Output directory (default: output/)
- `--no-files` - Print to stdout instead of saving files

### Output Files

Generates 3 files in `output/` directory:
- `*_human.txt` - Step-by-step decision narrative with reasoning
- `*_json.json` - Machine-readable complete history with graph states
- `*_chain.txt` - Concise event log (format: `STEP N: Actor flips Actor↔Target +→-`)

## Architecture

### Component Structure

```
simulator.py          Main cascade engine (round-based selection with rationality)
├── graph.py          SignedGraph data structure (+1/-1 edges)
├── analyzer.py       Triangle detection, pressure analysis, social scoring
├── decision.py       Mimetic decision-making heuristics
├── formatter.py      Output formatters (human/json/chain)
└── cli.py            Command-line interface and argument parsing
```

### Key Concepts

**Structural Balance**: Triangles are balanced with even number of negative edges:
- `+++` and `+--` are balanced
- `++-` and `---` are unbalanced (create social pressure)

**Decision Rules**:
- In `++-` triangles: Break friendship with person with **lowest score** (pile-on effect)
- In `---` triangles: Ally with person with **highest score** (strategic reconciliation)
- Social score = (friends) - (enemies)

**No-Reversal Constraint**: Each actor can flip an edge **once** (tracked per actor-edge pair, not per edge). Other actors can still respond to that edge (max 2 flips per edge total).

**Rationality Parameter**: Controls move selection using softmax weighting on triangle deltas:
- `1.0` = Always pick move that balances the most triangles
- `0.5` = Weighted probabilistic (default)
- `0.0` = Random/myopic choice

### Critical Implementation Details

1. **Round-Based Selection** (not FIFO queue):
   - Each step: find ALL pressured nodes simultaneously
   - For each: compute preferred flip and triangle delta
   - Select ONE move based on rationality weighting
   - This allows actors to "see around corners" for efficient scapegoating

2. **Bidirectional Perturbation Lock**:
   - Initial perturbed edge is locked for BOTH actors (they can't touch it again)
   - Prevents immediate reversal of the inciting incident

3. **Actor-Edge Tracking**:
   - Track `(actor, edge)` pairs in `actor_flipped_edges` set
   - Alice flipping Alice↔Betty locks Alice from that edge, but Betty can still respond
   - This is the "no take-backs" rule: actors can't reverse their own decisions

4. **Stuck States**:
   - Actor is stuck when under pressure but all potential flips are locked
   - Stuck actors get -1000 penalty in triangle delta calculation
   - Cascade continues with other pressured actors

## Data Flow

1. **Initialize**: Create complete graph (all + or all - edges)
2. **Perturb**: Flip specified edge, lock both actors
3. **Cascade Loop**:
   - Find all pressured nodes (in unbalanced triangles)
   - Each pressured node determines preferred flip using decision heuristics
   - Calculate triangle delta for each potential move
   - Select move via rationality-weighted softmax
   - Execute flip, record (actor, edge) in `actor_flipped_edges`
   - Repeat until stable or max steps reached
4. **Output**: Generate human/json/chain formats

## Working with the Code

### Modifying Decision Logic

Decision rules are in `decision.py`:
- `choose_flip()`: Core heuristic (hate lowest score, love highest score)
- `get_flip_options()`: Generates valid moves respecting no-reversal constraint
- `get_decision_context()`: Extracts context for human-readable output

### Modifying Selection Strategy

Round-based selection is in `simulator.py` (`_propagate_cascade()` and `_select_move()`):
- `_propagate_cascade()`: Main cascade loop with round-based evaluation
- `_select_move()`: Rationality-based move selection using softmax

### Triangle Analysis

Triangle operations are in `analyzer.py`:
- `find_all_triangles()`: O(N³) enumeration of all 3-node combinations
- `find_pressured_nodes()`: Returns set of nodes in unbalanced triangles
- `calculate_triangle_delta()`: Simulates flip and counts balance improvement

### Graph Operations

`SignedGraph` (in `graph.py`) stores edges in canonical order (alphabetically sorted):
- `flip_edge(u, v)`: Multiplies edge sign by -1
- `get_edge(u, v)`: Returns +1, -1, or 0 (no edge)
- `_canonical_edge()`: Ensures consistent edge representation

## Performance Characteristics

- Time complexity per step: O(N³) for triangle detection
- Total cascade: O(S × N³) where S = number of steps
- Works well for 4-20 nodes; bottleneck at 100+ nodes

## Testing & Reproducibility

**Always use `--seed` for deterministic results**. Without seed, tie-breaking is random.

Known deterministic test cases:
- `--seed 42 --rationality 1.0`: Alice scapegoated in 2 steps
- `--seed 1 --rationality 0.5`: Betty scapegoated in 2 steps
- `--seed 10`: Factional split outcome

## Design Philosophy

This is a **contagion model**, not an optimization algorithm:
- Actors make **local, greedy decisions** based only on their triangles
- Decisions are **irreversible** (no take-backs)
- Rationality is **tunable** to explore behavior spectrum
- Scapegoating emerges from **cascading reactions**, not global planning

See ARCHITECTURE.md for detailed design rationale and theoretical foundations.

## Common Development Scenarios

### Analyzing Specific Cascade Behavior

Use human format with specific seed:
```bash
python run.py --nodes Alice Betty Charlie David \
              --perturb Alice:Betty \
              --seed 42 \
              --format human
```

### Testing Rationality Impact

Compare different rationality values with same seed:
```bash
# Myopic (random)
python run.py --nodes A B C D --perturb A:B --seed 42 --rationality 0.0

# Balanced
python run.py --nodes A B C D --perturb A:B --seed 42 --rationality 0.5

# Optimal
python run.py --nodes A B C D --perturb A:B --seed 42 --rationality 1.0
```

### Debugging Non-Convergence

Check for stuck states in human output, increase max-steps, or try different rationality.

### Batch Experiments

Generate JSON for multiple seeds and analyze programmatically:
```bash
for seed in 1 5 10 42 100; do
  python run.py --nodes A B C D --perturb A:B --seed $seed --format json
done
```

## Important Notes

- This is a **research/educational tool** for studying emergent scapegoating
- Uses only Python 3 standard library (no external dependencies)
- All files are in `src/` package; use `python run.py` or `python -m src.cli`
- Output files are named: `{nodes}_{perturb}_{seed}_{format}.{ext}`
