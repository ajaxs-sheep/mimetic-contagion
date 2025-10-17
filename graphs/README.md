# Graph File Formats

This directory contains example graph files for the mimetic contagion simulator. The simulator supports three file formats:

## Supported Formats

### 1. JSON Format (.json)

Full graph specification with explicit nodes and edges:

```json
{
  "nodes": ["A", "B", "C", "D"],
  "edges": [
    {"source": "A", "target": "B", "sign": 1},
    {"source": "A", "target": "C", "sign": -1}
  ]
}
```

- **Sign values**: `1` or `+` for friendship, `-1` or `-` for enmity
- **Best for**: Complete graph specifications, human-readable configs

### 2. CSV Format (.csv)

Edge list with header row:

```csv
source,target,sign
A,B,1
A,C,-1
B,C,+
```

- **Sign values**: `1/-1`, `+/-`, `positive/negative`, or `friend/enemy`
- **Best for**: Large graphs, spreadsheet editing, data export

### 3. Text Format (.txt, .edges)

Space/tab-separated edge list:

```
# Comments start with #
A B +
A C -
B C +
```

- **Sign values**: `+` or `1` for friendship, `-` or `-1` for enmity
- **Best for**: Simple manual editing, quick prototyping

## Example Files

- `example_4node.{json,csv,txt}`: 4-node graph with mixed relationships
- `example_6node_scapegoat.json`: 6-node graph with pre-existing scapegoat pattern (5 vs 1)

## Usage

```bash
# Load from JSON
python run.py --graph-file graphs/example_4node.json --perturb A:B --seed 42

# Load from CSV
python run.py --graph-file graphs/example_6node_scapegoat.csv --perturb A:B --seed 42 --rationality 0.8

# Load from text file
python run.py --graph-file graphs/network.txt --perturb Node1:Node2 --seed 42
```

## Creating Custom Graphs

### For small networks (< 10 nodes):
Use JSON format for clarity and explicit node lists

### For medium networks (10-100 nodes):
Use CSV format - easier to generate programmatically

### For large networks (100+ nodes):
Use CSV or text format, generate with scripts:

```python
from src.graph_loader import GraphLoader

# Create graph programmatically
graph = SignedGraph()
for i in range(1000):
    graph.add_node(f"node_{i}")

# Add edges...
# Then save
GraphLoader.save_to_file(graph, "large_network.csv", format="csv")
```

## Node Naming

- Node names can be any string (alphanumeric recommended)
- Avoid special characters that might conflict with file format delimiters
- Use descriptive names for readability

## Graph Properties

**Complete graphs**: All possible edges present
**Sparse graphs**: Only subset of edges defined
**Signed graphs**: Every edge has +1 (friend) or -1 (enemy) sign

**Balanced configurations**:
- Scapegoat: n-1 nodes allied against 1
- Factions: Two groups, internal friendship, cross-group enmity
- Harmony: All positive edges (rare stable state after perturbation)

## Validation

The graph loader validates:
- File format syntax
- Node existence (edges must reference defined nodes in JSON)
- Sign values (must be valid friendship/enmity indicators)
- File existence and readability

Errors are reported with clear messages indicating the problem.
