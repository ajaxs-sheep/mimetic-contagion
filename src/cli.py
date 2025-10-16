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


def main():
    parser = argparse.ArgumentParser(
        description="Simulate mimetic contagion in signed social graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic 4-node Salem scenario (outputs to output/ directory)
  python cli.py --nodes Alice Betty Charlie David \\
                --initial all-positive \\
                --perturb Alice:Betty \\
                --seed 42

  # Print to stdout instead of files
  python cli.py --nodes Alice Betty Charlie David \\
                --initial all-positive \\
                --perturb Alice:Betty \\
                --seed 42 \\
                --no-files

  # Only generate specific format
  python cli.py --nodes Alice Betty Charlie David \\
                --initial all-positive \\
                --perturb Alice:Betty \\
                --seed 42 \\
                --format chain

  # Use custom output directory
  python cli.py --nodes Alice Betty Charlie David \\
                --initial all-positive \\
                --perturb Alice:Betty \\
                --seed 42 \\
                --output-dir results

Notes:
  - Without --seed, results are non-deterministic (random tie-breaking)
  - Default format is 'all' (generates human.txt, json.json, chain.txt)
  - Files are automatically saved to output/ directory
  - Use --no-files to print to stdout instead
        """
    )

    parser.add_argument(
        "--nodes",
        nargs="+",
        required=True,
        help="List of node names"
    )

    parser.add_argument(
        "--initial",
        choices=["all-positive", "all-negative"],
        default="all-positive",
        help="Initial graph state (default: all-positive)"
    )

    parser.add_argument(
        "--perturb",
        required=True,
        help="Edge to flip as perturbation (format: Node1:Node2)"
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

    args = parser.parse_args()

    # Warn if no seed provided (non-deterministic behavior)
    if args.seed is None:
        print("WARNING: No --seed provided. Results will be non-deterministic.", file=sys.stderr)
        print("         Use --seed <number> for reproducible results.\n", file=sys.stderr)
    else:
        random.seed(args.seed)

    # Create initial graph
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

    # Parse perturbation edge
    try:
        node1, node2 = args.perturb.split(":")
        if node1 not in graph.nodes or node2 not in graph.nodes:
            print(f"Error: Nodes in perturbation must be from: {args.nodes}", file=sys.stderr)
            sys.exit(1)
        if not graph.has_edge(node1, node2):
            print(f"Error: No edge between {node1} and {node2}", file=sys.stderr)
            sys.exit(1)
        perturbation = (node1, node2)
    except ValueError:
        print("Error: Perturbation must be in format Node1:Node2", file=sys.stderr)
        sys.exit(1)

    # Run simulation
    simulator = MimeticCascadeSimulator(graph, max_steps=args.max_steps, rationality=args.rationality)
    result = simulator.introduce_perturbation(perturbation)

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
        nodes_str = "-".join(args.nodes)
        perturb_str = args.perturb.replace(":", "-")
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
