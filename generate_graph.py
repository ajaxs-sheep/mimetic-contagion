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


def main():
    parser = argparse.ArgumentParser(
        description="Generate signed graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 100-node all-positive graph (Salem scenario)
  python generate_graph.py --nodes 100 --mode all-positive --output graphs/harmony_100.json --seed 42

  # Generate 50-node all-negative graph
  python generate_graph.py --nodes 50 --mode all-negative --output graphs/conflict_50.json --seed 42

  # Generate 100-node random graph (50% positive)
  python generate_graph.py --nodes 100 --mode random --output graphs/random_100.json --seed 42

  # Generate graph with 70% positive edges
  python generate_graph.py --nodes 50 --mode random --p-positive 0.7 --output graphs/random_50_pos.csv --seed 42
        """
    )

    parser.add_argument(
        "--nodes",
        type=int,
        required=True,
        help="Number of nodes in the graph"
    )

    parser.add_argument(
        "--mode",
        choices=['random', 'all-positive', 'all-negative'],
        default='random',
        help="Graph mode: random, all-positive, or all-negative (default: random)"
    )

    parser.add_argument(
        "--p-positive",
        type=float,
        default=0.5,
        help="Probability of positive edge for random mode (0.0-1.0, default: 0.5)"
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
    print(f"Generating {args.nodes}-node complete graph ({args.mode})...", file=sys.stderr)
    graph = generate_complete_graph(args.nodes, args.mode, args.p_positive, args.seed)

    # Count edges
    pos_edges = sum(1 for _, _, s in graph.get_all_edges() if s == 1)
    neg_edges = sum(1 for _, _, s in graph.get_all_edges() if s == -1)
    total_edges = len(graph.edges)

    print(f"Generated graph:", file=sys.stderr)
    print(f"  Nodes: {len(graph.nodes)}", file=sys.stderr)
    print(f"  Edges: {total_edges}", file=sys.stderr)
    print(f"    Positive: {pos_edges} ({pos_edges/total_edges*100:.1f}%)", file=sys.stderr)
    print(f"    Negative: {neg_edges} ({neg_edges/total_edges*100:.1f}%)", file=sys.stderr)

    # Save
    GraphLoader.save_to_file(graph, args.output, format)
    print(f"\nSaved to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
