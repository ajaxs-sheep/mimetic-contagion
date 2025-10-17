#!/usr/bin/env python3
"""
Command-line interface for mimetic cascade simulation.
"""

import argparse
import sys
import random
import os
from datetime import datetime
from .graph import SignedGraph
from .simulator import MimeticCascadeSimulator
from .formatter import format_json, format_human_readable, format_simple_chain
from .graph_loader import GraphLoader


def main():
    parser = argparse.ArgumentParser(
        description="Simulate mimetic contagion in signed social graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete positive graph (small networks)
  python cli.py --nodes Alice Betty Charlie David \\
                --initial all-positive \\
                --perturb Alice:Betty \\
                --seed 42

  # Load custom graph from file
  python cli.py --graph-file graphs/my_network.json \\
                --perturb A:B \\
                --seed 42

  # Load from CSV edge list
  python cli.py --graph-file graphs/network.csv \\
                --perturb NodeX:NodeY \\
                --seed 42 \\
                --rationality 0.8

  # Load from text file and print to stdout
  python cli.py --graph-file graphs/edges.txt \\
                --perturb A:C \\
                --seed 42 \\
                --no-files

Graph file formats:
  - JSON: {"nodes": [...], "edges": [{"source": "A", "target": "B", "sign": 1}, ...]}
  - CSV: source,target,sign (header required, sign can be 1/-1 or +/-)
  - TXT: Space/tab-separated "A B +" format (one edge per line, # for comments)

Notes:
  - Use --initial for complete graphs OR --graph-file for custom graphs
  - Without --seed, results are non-deterministic (random tie-breaking)
  - Default format is 'all' (generates human.txt, json.json, chain.txt)
  - Files are automatically saved to output/ directory
  - Use --no-files to print to stdout instead
        """
    )

    parser.add_argument(
        "--nodes",
        nargs="+",
        help="List of node names (required with --initial, ignored with --graph-file)"
    )

    parser.add_argument(
        "--initial",
        choices=["all-positive", "all-negative"],
        help="Initial graph state: all-positive or all-negative (requires --nodes)"
    )

    parser.add_argument(
        "--graph-file",
        help="Load graph from file (.json, .csv, or .txt format)"
    )

    parser.add_argument(
        "--perturb",
        help="Edge to flip as perturbation (format: Node1:Node2). Optional - if not provided, starts cascade from initial imbalanced state"
    )

    parser.add_argument(
        "--format",
        choices=["human", "json", "chain", "all"],
        default="all",
        help="Output format (default: all)"
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory (default: output/)"
    )

    parser.add_argument(
        "--no-files",
        action="store_true",
        help="Print to stdout instead of saving files"
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility"
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
        help="Maximum cascade steps (default: 1000)"
    )

    parser.add_argument(
        "--rationality",
        type=float,
        default=0.5,
        help="Decision rationality: 0.0=random, 1.0=optimal, 0.5=balanced (default: 0.5)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show progress updates during simulation (useful for large graphs)"
    )

    args = parser.parse_args()

    # Validate that either --initial or --graph-file is provided (but not both)
    if args.initial and args.graph_file:
        print("Error: Cannot use both --initial and --graph-file. Choose one.", file=sys.stderr)
        sys.exit(1)
    if not args.initial and not args.graph_file:
        print("Error: Must provide either --initial or --graph-file", file=sys.stderr)
        sys.exit(1)

    # If using --initial, --nodes is required
    if args.initial and not args.nodes:
        print("Error: --nodes is required when using --initial", file=sys.stderr)
        sys.exit(1)

    # Warn if no seed provided (non-deterministic behavior)
    if args.seed is None:
        print("WARNING: No --seed provided. Results will be non-deterministic.", file=sys.stderr)
        print("         Use --seed <number> for reproducible results.\n", file=sys.stderr)
    else:
        random.seed(args.seed)

    # Create initial graph
    if args.initial:
        if args.initial == "all-positive":
            graph = SignedGraph.create_complete_positive(args.nodes)
        else:
            # All negative - create complete graph with negative edges
            graph = SignedGraph()
            for node in args.nodes:
                graph.add_node(node)
            for i, u in enumerate(args.nodes):
                for v in args.nodes[i+1:]:
                    graph.add_edge(u, v, -1)
    else:
        # Load graph from file
        try:
            graph = GraphLoader.load_from_file(args.graph_file)
            print(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges", file=sys.stderr)
        except FileNotFoundError:
            print(f"Error: Graph file not found: {args.graph_file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error loading graph file: {e}", file=sys.stderr)
            sys.exit(1)

    # Parse perturbation edge (if provided)
    perturbation = None
    if args.perturb:
        try:
            node1, node2 = args.perturb.split(":")
            if node1 not in graph.nodes or node2 not in graph.nodes:
                print(f"Error: Nodes in perturbation must be from the graph nodes", file=sys.stderr)
                sys.exit(1)
            if not graph.has_edge(node1, node2):
                print(f"Error: No edge between {node1} and {node2}", file=sys.stderr)
                sys.exit(1)
            perturbation = (node1, node2)
        except ValueError:
            print("Error: Perturbation must be in format Node1:Node2", file=sys.stderr)
            sys.exit(1)

    # Run simulation
    simulator = MimeticCascadeSimulator(graph, max_steps=args.max_steps, rationality=args.rationality, verbose=args.verbose)
    if perturbation:
        result = simulator.introduce_perturbation(perturbation)
    else:
        print("No perturbation - running cascade from initial state imbalances...", file=sys.stderr)
        result = simulator.run_from_current_state()

    # Format output
    outputs = []

    if args.format == "human" or args.format == "all":
        outputs.append(("human", "txt", format_human_readable(result)))

    if args.format == "json" or args.format == "all":
        outputs.append(("json", "json", format_json(result)))

    if args.format == "chain" or args.format == "all":
        outputs.append(("chain", "txt", format_simple_chain(result)))

    # Write output
    if args.no_files:
        # Print to stdout
        for label, ext, content in outputs:
            if args.format == "all":
                print(f"\n{'='*70}")
                print(f"{label.upper()} FORMAT")
                print(f"{'='*70}\n")
            print(content)
    else:
        # Write to files in output directory
        os.makedirs(args.output_dir, exist_ok=True)

        # Generate base filename
        if args.graph_file:
            # Use graph filename as base
            from os.path import splitext, basename
            graph_basename = splitext(basename(args.graph_file))[0]
            nodes_str = graph_basename
        else:
            nodes_str = "-".join(args.nodes) if args.nodes else "graph"

        perturb_str = args.perturb.replace(":", "-") if args.perturb else "no-perturb"
        seed_str = f"seed{args.seed}" if args.seed is not None else "random"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        base_name = f"{nodes_str}_{perturb_str}_{seed_str}"

        written_files = []
        for label, ext, content in outputs:
            filename = f"{base_name}_{label}.{ext}"
            filepath = os.path.join(args.output_dir, filename)

            with open(filepath, "w") as f:
                f.write(content)

            written_files.append(filepath)
            print(f"✓ {label}: {filepath}")

        print(f"\nAll outputs written to: {args.output_dir}/")
        print(f"Steps: {len(result.cascade_steps)}")
        print(f"Converged: {result.converged}")


if __name__ == "__main__":
    main()
