# Mimetic Contagion Simulator

A Python-based simulator for modeling mimetic contagion in signed social graphs, inspired by René Girard's theory of scapegoating and structural balance theory.

## What is This?

This tool simulates how social conflicts propagate through networks of relationships. Given an initial perturbation (e.g., two friends becoming enemies), it models how other actors respond to structural imbalances, potentially leading to:

- **Scapegoating**: Unanimous exclusion of one victim
- **Factional splits**: Fragmentation into opposing groups
- **Stable configurations**: Balanced relationship structures

Unlike optimization-based approaches, this models **contagion as cascading events** where actors make local decisions based on social pressure.

## Installation

No external dependencies required. Uses Python 3 standard library only.

```bash
git clone <repository>
cd mimetic-contagion
```

## Quick Start

### Basic Usage

```bash
python cli.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42
```

This simulates a "Salem witch trial" scenario:
1. Starts with 4 people who are all friends
2. Alice and Betty have a falling out (perturbation)
3. Others must choose sides under social pressure
4. System converges to a stable state (often scapegoating)

### Output

By default, generates 3 files in `output/` directory:

- `*_human.txt` - Human-readable step-by-step narrative
- `*_json.json` - Machine-readable JSON format
- `*_chain.txt` - Concise event chain

Example output (chain format):
```
PERTURB: Alice↔Betty +→-
STEP 1: David flips David↔Alice +→-
STEP 2: Alice flips Alice↔Charlie +→-
```

Final state: Alice scapegoated (score: -3)

## Command-Line Options

### Required Arguments

- `--nodes` - List of node names (space-separated)
  ```bash
  --nodes Alice Betty Charlie David Eve Frank
  ```

- `--perturb` - Initial edge to flip (format: `Node1:Node2`)
  ```bash
  --perturb Alice:Betty
  ```

### Optional Arguments

- `--initial` - Initial graph state (default: `all-positive`)
  - `all-positive`: Everyone starts as friends
  - `all-negative`: Everyone starts as enemies

- `--seed` - Random seed for reproducibility (default: none)
  ```bash
  --seed 42  # Deterministic results
  ```
  **Warning**: Without `--seed`, results are non-deterministic due to random tie-breaking.

- `--rationality` - Decision rationality (default: `0.5`)
  - `0.0` = Myopic/random choices
  - `0.5` = Balanced (weighted by global impact)
  - `1.0` = Globally optimal (always picks best move)
  ```bash
  --rationality 1.0  # Efficient scapegoating
  ```

- `--max-steps` - Maximum cascade steps (default: `1000`)
  ```bash
  --max-steps 500
  ```

- `--format` - Output format (default: `all`)
  - `human` - Human-readable narrative only
  - `json` - JSON only
  - `chain` - Concise chain only
  - `all` - Generate all three formats

- `--output-dir` - Output directory (default: `output/`)
  ```bash
  --output-dir results/
  ```

- `--no-files` - Print to stdout instead of saving files
  ```bash
  --no-files  # Print results to terminal
  ```

## Examples

### Deterministic Scapegoating

```bash
# High rationality → efficient path to scapegoating
python cli.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42 \
              --rationality 1.0
```

Output: Alice scapegoated in 2 steps (score: -3)

### Chaotic/Random Behavior

```bash
# Low rationality → random, chaotic decisions
python cli.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42 \
              --rationality 0.0
```

Output: 10+ steps with potentially stuck states

### Large Graph

```bash
# 6-node graph with balanced rationality
python cli.py --nodes Alice Betty Charlie David Eve Frank \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 123 \
              --rationality 0.5
```

### Print to Terminal

```bash
# Quick testing without saving files
python cli.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42 \
              --format chain \
              --no-files
```

### Custom Output Directory

```bash
# Save to specific directory
python cli.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42 \
              --output-dir experiments/trial1/
```

## Understanding Output

### Human-Readable Format

Shows detailed decision-making process for each step:

```
--- STEP 1 ---
DAVID under pressure

  Unbalanced triangles: 1
    • (Alice, Betty, David) [-++]

  Options to resolve (++- → break friendship with lowest score):
    • Break with Alice: score = 1
    • Break with Betty: score = 1

  Decision: TIE → random choice
  → Easier to hate: Alice
  Action: David→Alice: + → -
```

### Chain Format

Concise event log:
```
PERTURB: Alice↔Betty +→-
STEP 1: David flips David↔Alice +→-
STEP 2: Alice flips Alice↔Charlie +→-
```

### JSON Format

Machine-readable complete history including:
- Initial and final graph states
- Every cascade step with decision context
- Triangle counts and social scores

### Social Scores

Final social scores indicate outcomes:
- **Score -3** in 4-node graph = scapegoated (all enemies)
- **Score +3** in 4-node graph = popular (all friends)
- **Score ±1** = factional split or partial exclusion

## Key Concepts

### Structural Balance

Triangles are **balanced** when they have an even number of negative edges:
- `+++` (all friends) - balanced
- `+--` (two enemies share enemy) - balanced
- `++-` (two friends share enemy) - **unbalanced**
- `---` (all enemies) - **unbalanced**

### Social Pressure

Nodes in unbalanced triangles are "under pressure" and must act to resolve the imbalance.

### Decision Rules

When under pressure, actors choose based on social scores:

- **In ++- triangles** (two friends, one enemy): Hate the person with the lowest score (pile-on effect)
- **In --- triangles** (all enemies): Ally with the person with the highest score (easiest to reconcile)

### No Reversals

Each actor can only flip an edge once - no taking back decisions. However, the other actor can respond (max 2 flips per edge total).

### Rationality Parameter

Controls how intelligently actors choose moves:
- High rationality = considers global impact (triangle delta)
- Low rationality = myopic/random choices
- Affects convergence speed and outcome quality

## Common Scenarios

### Scapegoating (Unanimous Victimization)

```bash
python cli.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 1 \
              --rationality 0.8
```

Result: One person with score -3, others at +1

### Factional Split

```bash
python cli.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 10
```

Result: Two opposing factions, scores around ±1

### Stuck States

With low rationality or complex graphs, actors may get "stuck" (under pressure but no valid moves due to no-reversal constraint).

## File Structure

```
mimetic-contagion/
├── cli.py           # Command-line interface
├── simulator.py     # Cascade simulation engine
├── graph.py         # Signed graph data structure
├── analyzer.py      # Triangle detection & pressure analysis
├── decision.py      # Mimetic decision-making logic
├── formatter.py     # Output formatters (human/json/chain)
├── output/          # Default output directory
├── README.md        # This file
└── ARCHITECTURE.md  # Design philosophy and decisions
```

## Troubleshooting

### Non-Deterministic Results

Always use `--seed` for reproducible results:
```bash
--seed 42
```

### Infinite Loops

Should not occur with current implementation. If cascade exceeds `--max-steps`, it will stop and report non-convergence.

### Stuck States

Normal behavior when actors have no valid moves. Indicates cascade has reached a local minimum but not full balance.

## Further Reading

- `ARCHITECTURE.md` - Design philosophy and implementation details
- `seed.md` - Original design document on contagion vs optimization

## References

- René Girard - *The Scapegoat* (mimetic theory)
- Structural Balance Theory (Heider, Cartwright & Harary)
- Signed social networks and conflict resolution
