#!/usr/bin/env python3
"""
Generate signed graphs for experimentation.
"""

import argparse
import random
import sys
from src.graph import SignedGraph
from src.graph_loader import GraphLoader


def generate_complete_graph(num_nodes: int, mode: str = 'random', p_positive: float = 0.5, seed: int = None) -> SignedGraph:
    """
    Generate a complete graph with specified edge pattern.

    Args:
        num_nodes: Number of nodes
        mode: 'random', 'all-positive', or 'all-negative'
        p_positive: Probability of positive edge (used for 'random' mode, default 0.5)
        seed: Random seed for reproducibility

    Returns:
        SignedGraph with specified sign pattern
    """
    if seed is not None:
        random.seed(seed)

    graph = SignedGraph()

    # Add nodes
    for i in range(num_nodes):
        graph.add_node(f"n{i}")

    # Add edges based on mode
    nodes = list(graph.nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if mode == 'all-positive':
                sign = 1
            elif mode == 'all-negative':
                sign = -1
            elif mode == 'random':
                # Random sign based on probability
                sign = 1 if random.random() < p_positive else -1
            else:
                raise ValueError(f"Invalid mode: {mode}. Must be 'random', 'all-positive', or 'all-negative'")

            graph.add_edge(nodes[i], nodes[j], sign)

    return graph


def generate_sparse_graph(num_nodes: int, min_degree: int = 3, max_degree: int = 10,
                          p_positive: float = 0.6, seed: int = None) -> SignedGraph:
    """
    Generate a sparse graph where each node has between min_degree and max_degree edges.

    Args:
        num_nodes: Number of nodes
        min_degree: Minimum number of edges per node (default: 3)
        max_degree: Maximum number of edges per node (default: 10)
        p_positive: Probability of positive edge (default: 0.6 for mostly positive)
        seed: Random seed for reproducibility

    Returns:
        SignedGraph with sparse connectivity
    """
    if seed is not None:
        random.seed(seed)

    if min_degree < 2:
        raise ValueError("min_degree must be at least 2")
    if max_degree < min_degree:
        raise ValueError("max_degree must be >= min_degree")
    if num_nodes < 2:
        raise ValueError("num_nodes must be at least 2")

    graph = SignedGraph()

    # Add nodes
    nodes = [f"n{i}" for i in range(num_nodes)]
    for node in nodes:
        graph.add_node(node)

    # Track degree for each node
    degree = {node: 0 for node in nodes}

    # First pass: ensure minimum degree for all nodes
    for node in nodes:
        while degree[node] < min_degree:
            # Find candidates (nodes with degree < max_degree and no edge to current node)
            candidates = [
                other for other in nodes
                if other != node
                and degree[other] < max_degree
                and not graph.has_edge(node, other)
            ]

            if not candidates:
                # If no candidates, try to find ANY node without an edge (even if at max degree)
                candidates = [
                    other for other in nodes
                    if other != node and not graph.has_edge(node, other)
                ]

            if not candidates:
                break  # No more possible edges

            # Pick random candidate
            other = random.choice(candidates)
            sign = 1 if random.random() < p_positive else -1
            graph.add_edge(node, other, sign)
            degree[node] += 1
            degree[other] += 1

    # Second pass: add random edges to increase connectivity (up to max_degree)
    # This makes the graph more interesting
    for node in nodes:
        if degree[node] >= max_degree:
            continue

        # Randomly decide how many more edges to add (up to max_degree)
        target_degree = random.randint(degree[node], max_degree)

        while degree[node] < target_degree:
            candidates = [
                other for other in nodes
                if other != node
                and degree[other] < max_degree
                and not graph.has_edge(node, other)
            ]

            if not candidates:
                break

            other = random.choice(candidates)
            sign = 1 if random.random() < p_positive else -1
            graph.add_edge(node, other, sign)
            degree[node] += 1
            degree[other] += 1

    return graph


def main():
    parser = argparse.ArgumentParser(
        description="Generate signed graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate sparse 100-node graph (3-10 edges per node, 60% positive)
  python generate_graph.py --nodes 100 --type sparse --output graphs/sparse_100.txt --seed 42

  # Generate sparse with custom degree range
  python generate_graph.py --nodes 50 --type sparse --min-degree 5 --max-degree 15 \\
      --p-positive 0.7 --output graphs/sparse_50.txt --seed 42

  # Generate complete 30-node all-positive graph
  python generate_graph.py --nodes 30 --type complete --mode all-positive \\
      --output graphs/harmony_30.txt --seed 42

  # Generate complete random graph (50% positive)
  python generate_graph.py --nodes 30 --type complete --mode random --output graphs/random_30.txt --seed 42
        """
    )

    parser.add_argument(
        "--nodes",
        type=int,
        required=True,
        help="Number of nodes in the graph"
    )

    parser.add_argument(
        "--type",
        choices=['sparse', 'complete'],
        default='sparse',
        help="Graph type: sparse or complete (default: sparse)"
    )

    # Complete graph options
    parser.add_argument(
        "--mode",
        choices=['random', 'all-positive', 'all-negative'],
        default='random',
        help="[Complete graphs only] Edge pattern: random, all-positive, or all-negative (default: random)"
    )

    # Sparse graph options
    parser.add_argument(
        "--min-degree",
        type=int,
        default=3,
        help="[Sparse graphs only] Minimum edges per node (default: 3)"
    )

    parser.add_argument(
        "--max-degree",
        type=int,
        default=10,
        help="[Sparse graphs only] Maximum edges per node (default: 10)"
    )

    parser.add_argument(
        "--p-positive",
        type=float,
        default=0.6,
        help="Probability of positive edge (0.0-1.0, default: 0.6 for sparse, 0.5 for complete)"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (.json, .csv, or .txt)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    # Validate
    if args.nodes < 2:
        print("Error: Must have at least 2 nodes", file=sys.stderr)
        sys.exit(1)

    if not (0.0 <= args.p_positive <= 1.0):
        print("Error: --p-positive must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)

    if args.type == 'sparse':
        if args.min_degree < 2:
            print("Error: --min-degree must be at least 2", file=sys.stderr)
            sys.exit(1)
        if args.max_degree < args.min_degree:
            print("Error: --max-degree must be >= --min-degree", file=sys.stderr)
            sys.exit(1)

    # Determine format from extension
    if args.output.endswith('.json'):
        format = 'json'
    elif args.output.endswith('.csv'):
        format = 'csv'
    elif args.output.endswith('.txt') or args.output.endswith('.edges'):
        format = 'txt'
    else:
        print("Error: Output file must have extension .json, .csv, or .txt", file=sys.stderr)
        sys.exit(1)

    # Generate graph
    if args.type == 'sparse':
        print(f"Generating {args.nodes}-node sparse graph (degree {args.min_degree}-{args.max_degree})...", file=sys.stderr)
        graph = generate_sparse_graph(
            args.nodes,
            min_degree=args.min_degree,
            max_degree=args.max_degree,
            p_positive=args.p_positive,
            seed=args.seed
        )
    else:  # complete
        print(f"Generating {args.nodes}-node complete graph ({args.mode})...", file=sys.stderr)
        p_pos = args.p_positive if args.mode == 'random' else 0.5
        graph = generate_complete_graph(args.nodes, args.mode, p_pos, args.seed)

    # Count edges and analyze degree
    pos_edges = sum(1 for _, _, s in graph.get_all_edges() if s == 1)
    neg_edges = sum(1 for _, _, s in graph.get_all_edges() if s == -1)
    total_edges = len(graph.edges)

    # Calculate degree stats for sparse graphs
    if args.type == 'sparse':
        degrees = {}
        for node in graph.nodes:
            degrees[node] = len(list(graph.neighbors(node)))
        min_deg = min(degrees.values())
        max_deg = max(degrees.values())
        avg_deg = sum(degrees.values()) / len(degrees)

    print(f"Generated graph:", file=sys.stderr)
    print(f"  Nodes: {len(graph.nodes)}", file=sys.stderr)
    print(f"  Edges: {total_edges}", file=sys.stderr)
    if args.type == 'sparse':
        print(f"  Degree: min={min_deg}, max={max_deg}, avg={avg_deg:.1f}", file=sys.stderr)
    print(f"    Positive: {pos_edges} ({pos_edges/total_edges*100:.1f}%)", file=sys.stderr)
    print(f"    Negative: {neg_edges} ({neg_edges/total_edges*100:.1f}%)", file=sys.stderr)

    # Save
    GraphLoader.save_to_file(graph, args.output, format)
    print(f"\nSaved to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
