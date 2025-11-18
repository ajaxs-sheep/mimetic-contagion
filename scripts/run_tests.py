#!/usr/bin/env python3
"""
Comprehensive test suite for scapegoating contagion.
Tests networks from 3 to 1000 nodes, verifying complete community unity.
"""

import sys
import time
import json
from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
from src.analyzer import find_unbalanced_triangles

def generate_test_graph(num_nodes, seed=42):
    """Generate a sparse graph with good connectivity."""
    import random
    random.seed(seed)

    if num_nodes <= 5:
        # Small graphs: complete graph with mostly positive edges
        graph = SignedGraph.create_complete_positive([f"n{i}" for i in range(num_nodes)])
    else:
        # Larger graphs: sparse with controlled degree
        from generate_graph import generate_sparse_graph
        min_degree = min(3, num_nodes - 1)
        max_degree = min(8, num_nodes - 1)
        p_positive = 0.75
        graph = generate_sparse_graph(num_nodes, min_degree, max_degree, p_positive, seed)

    return graph

def run_test(num_nodes, seed=42):
    """Run a single test and return metrics."""
    print(f"\n{'='*60}")
    print(f"Testing {num_nodes} nodes...")
    print(f"{'='*60}")

    # Generate graph
    start_time = time.time()
    graph = generate_test_graph(num_nodes, seed)
    gen_time = time.time() - start_time

    print(f"  Graph generated: {len(graph.edges)} edges ({gen_time:.3f}s)")

    # Select random scapegoat and accuser
    import random
    random.seed(seed)
    scapegoat = random.choice(list(graph.nodes))
    neighbors = graph.neighbors(scapegoat)
    if not neighbors:
        print(f"  ERROR: Scapegoat {scapegoat} has no neighbors!")
        return None
    accuser = random.choice(neighbors)

    print(f"  Scapegoat: {scapegoat}, Accuser: {accuser}")

    # Run simulation
    start_time = time.time()
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, accuser)
    sim_time = time.time() - start_time

    # Analyze results
    final_edges = result.final_state.edges
    scapegoat_edges = [e for e, sign in final_edges.items() if scapegoat in e]
    community_edges = [e for e, sign in final_edges.items() if scapegoat not in e]

    neg_to_scapegoat = sum(1 for e in scapegoat_edges if final_edges[e] == -1)
    neg_in_community = sum(1 for e in community_edges if final_edges[e] == -1)
    pos_in_community = sum(1 for e in community_edges if final_edges[e] == 1)

    # Count decisions by phase
    bfs_decisions = [d for d in result.decisions if 'Community unity' not in d.reason]
    cleanup_decisions = [d for d in result.decisions if 'Community unity' in d.reason]

    # Verify complete unity
    unity_achieved = neg_in_community == 0 and result.is_balanced

    metrics = {
        'num_nodes': num_nodes,
        'num_edges': len(graph.edges),
        'generation_time': gen_time,
        'simulation_time': sim_time,
        'total_decisions': len(result.decisions),
        'bfs_decisions': len(bfs_decisions),
        'cleanup_decisions': len(cleanup_decisions),
        'accusers': len(result.accusers),
        'defenders': len(result.defenders),
        'all_against_one': result.is_all_against_one,
        'balanced': result.is_balanced,
        'neg_to_scapegoat': neg_to_scapegoat,
        'neg_in_community': neg_in_community,
        'pos_in_community': pos_in_community,
        'unity_achieved': unity_achieved,
        'scapegoat': scapegoat,
        'accuser': accuser
    }

    # Print results
    print(f"  Simulation time: {sim_time:.3f}s")
    print(f"  Decisions: {len(result.decisions)} (BFS: {len(bfs_decisions)}, Cleanup: {len(cleanup_decisions)})")
    print(f"  Accusers: {len(result.accusers)}/{num_nodes-1}")
    print(f"  Defenders: {len(result.defenders)}")
    print(f"  Community edges: {pos_in_community} positive, {neg_in_community} negative")
    print(f"  All-against-one: {result.is_all_against_one}")
    print(f"  Balanced: {result.is_balanced}")
    print(f"  {'✓ COMPLETE UNITY' if unity_achieved else '✗ UNITY FAILED'}")

    return metrics, result

def main():
    """Run comprehensive test suite."""
    print("SCAPEGOATING CONTAGION TEST SUITE")
    print("Testing complete community unity from small to large networks")
    print("="*60)

    # Test sizes
    test_sizes = [3, 4, 5, 10, 20, 30, 50, 100, 200, 500, 1000]
    seed = 42

    all_metrics = []
    failed_tests = []

    for num_nodes in test_sizes:
        try:
            metrics, result = run_test(num_nodes, seed)
            if metrics:
                all_metrics.append(metrics)

                # Save JSON for visualization (small graphs only)
                if num_nodes <= 30:
                    from src.formatter import format_json
                    json_output = format_json(result)
                    filename = f"output/test_{num_nodes}nodes_seed{seed}_json.json"
                    with open(filename, 'w') as f:
                        f.write(json_output)
                    print(f"  Saved: {filename}")

                # Check for failures
                if not metrics['unity_achieved']:
                    failed_tests.append(num_nodes)
        except Exception as e:
            print(f"  ERROR: {e}")
            failed_tests.append(num_nodes)

    # Summary report
    print(f"\n{'='*60}")
    print("SUMMARY REPORT")
    print(f"{'='*60}\n")

    print(f"Total tests: {len(test_sizes)}")
    print(f"Successful: {len(all_metrics)}")
    print(f"Failed: {len(failed_tests)}")

    if failed_tests:
        print(f"\nFailed test sizes: {failed_tests}")
    else:
        print(f"\n✓ ALL TESTS PASSED - Complete unity achieved for all sizes!")

    # Performance table
    print(f"\n{'Nodes':<8} {'Edges':<8} {'Gen(s)':<10} {'Sim(s)':<10} {'Decisions':<12} {'Unity':<8}")
    print("-" * 60)
    for m in all_metrics:
        unity_symbol = "✓" if m['unity_achieved'] else "✗"
        print(f"{m['num_nodes']:<8} {m['num_edges']:<8} {m['generation_time']:<10.3f} "
              f"{m['simulation_time']:<10.3f} {m['total_decisions']:<12} {unity_symbol:<8}")

    # Save full report
    with open('output/test_report.json', 'w') as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nFull report saved to: output/test_report.json")

    return 0 if not failed_tests else 1

if __name__ == '__main__':
    sys.exit(main())
