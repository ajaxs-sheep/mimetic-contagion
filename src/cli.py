#!/usr/bin/env python3
"""
Command-line interface for mimetic scapegoating simulation.
"""

import argparse
import sys
import random
import os
from datetime import datetime
from .graph import SignedGraph
from .simulator import MimeticContagionSimulator
from .formatter import format_json, format_human_readable, format_simple_chain
from .graph_loader import GraphLoader


def main():
    parser = argparse.ArgumentParser(
        description="Simulate scapegoating contagion in signed social graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete positive graph with specified scapegoat and accuser
  python run.py --nodes Alice Betty Charlie David \\
                --initial all-positive \\
                --scapegoat Betty \\
                --accuser Alice \\
                --seed 42

  # Random scapegoat and accuser selection
  python run.py --nodes Alice Betty Charlie David \\
                --initial all-positive \\
                --seed 42

  # Load custom graph from file
  python run.py --graph-file graphs/my_network.json \\
                --scapegoat NodeA \\
                --accuser NodeB \\
                --seed 42

Graph file formats:
  - JSON: {"nodes": [...], "edges": [{"source": "A", "target": "B", "sign": 1}, ...]}
  - CSV: source,target,sign (header required, sign can be 1/-1 or +/-)
  - TXT: Space/tab-separated "A B +" format (one edge per line, # for comments)

Notes:
  - Use --initial for complete graphs OR --graph-file for custom graphs
  - If --scapegoat and --accuser not provided, random selection is used
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
        "--scapegoat",
        help="Node to mark as scapegoat (if not provided, randomly selected)"
    )

    parser.add_argument(
        "--accuser",
        help="Initial accuser node (if not provided, randomly selected from scapegoat's neighbors)"
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

    # Set random seed if provided
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

    # Select scapegoat and accuser
    if args.scapegoat:
        scapegoat = args.scapegoat
        if scapegoat not in graph.nodes:
            print(f"Error: Scapegoat '{scapegoat}' not in graph nodes", file=sys.stderr)
            sys.exit(1)
    else:
        # Pick random node as scapegoat
        scapegoat = random.choice(list(graph.nodes))
        print(f"Randomly selected scapegoat: {scapegoat}", file=sys.stderr)

    if args.accuser:
        accuser = args.accuser
        if accuser not in graph.nodes:
            print(f"Error: Accuser '{accuser}' not in graph nodes", file=sys.stderr)
            sys.exit(1)
        if accuser == scapegoat:
            print("Error: Accuser and scapegoat cannot be the same node", file=sys.stderr)
            sys.exit(1)
        if not graph.has_edge(accuser, scapegoat):
            print(f"Error: No edge between accuser '{accuser}' and scapegoat '{scapegoat}'", file=sys.stderr)
            sys.exit(1)
    else:
        # Pick random neighbor of scapegoat as accuser
        neighbors = graph.neighbors(scapegoat)
        if not neighbors:
            print(f"Error: Scapegoat '{scapegoat}' has no neighbors (isolated node)", file=sys.stderr)
            sys.exit(1)
        accuser = random.choice(neighbors)
        print(f"Randomly selected accuser: {accuser} (neighbor of {scapegoat})", file=sys.stderr)

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=args.verbose)
    result = simulator.introduce_accusation(scapegoat, accuser)

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

        scapegoat_str = scapegoat
        accuser_str = accuser
        seed_str = f"seed{args.seed}" if args.seed is not None else "random"

        base_name = f"{nodes_str}_{scapegoat_str}-scapegoat_{accuser_str}-accuser_{seed_str}"

        written_files = []
        for label, ext, content in outputs:
            filename = f"{base_name}_{label}.{ext}"
            filepath = os.path.join(args.output_dir, filename)

            with open(filepath, "w") as f:
                f.write(content)

            written_files.append(filepath)
            print(f"✓ {label}: {filepath}")

        print(f"\nAll outputs written to: {args.output_dir}/")
        print(f"Scapegoat: {scapegoat}")
        print(f"Accuser: {accuser}")
        print(f"Accusers: {len(result.accusers)}")
        print(f"Defenders: {len(result.defenders)}")
        print(f"Contagion succeeded: {result.contagion_succeeded}")
        print(f"Is balanced: {result.is_balanced}")
        print(f"Is all-against-one: {result.is_all_against_one}")


if __name__ == "__main__":
    main()
