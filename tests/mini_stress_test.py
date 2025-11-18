#!/usr/bin/env python3
"""
Mini stress test - very small scale to get quick data points for extrapolation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stress_tests import (
    run_instrumented_simulation,
    generate_pathological_star,
    generate_pathological_ring,
    generate_pathological_bipartite
)
from generate_graph import generate_sparse_graph, generate_complete_graph
import json
import random
import time


def mini_test():
    """Run mini stress test with very small graphs for quick feedback."""
    print("="*70)
    print("MINI STRESS TEST - Quick Data Collection")
    print("Small scale for fast results and extrapolation")
    print("="*70)

    output_dir = "output/mini_stress"
    os.makedirs(output_dir, exist_ok=True)

    all_results = {}

    # 1. Sparse scaling - very small increments
    print("\n[1/5] Testing sparse graph scaling...")
    sparse_results = []
    for num_nodes in [100, 200, 300, 500, 750, 1000]:
        print(f"  Testing {num_nodes} nodes...", end=" ", flush=True)
        start = time.time()
        graph = generate_sparse_graph(num_nodes, 3, 8, 0.7, seed=42)
        gen_time = time.time() - start

        random.seed(42)
        scapegoat = random.choice(list(graph.nodes))
        neighbors = graph.neighbors(scapegoat)
        if neighbors:
            accuser = random.choice(neighbors)
            metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
            sparse_results.append(metrics.to_dict())
            print(f"✓ {metrics.simulation_time:.2f}s")

    all_results['sparse'] = sparse_results

    # 2. Complete graphs - tiny sizes
    print("\n[2/5] Testing complete graphs...")
    complete_results = []
    for num_nodes in [20, 30, 50, 75, 100]:
        print(f"  Testing {num_nodes} nodes...", end=" ", flush=True)
        start = time.time()
        graph = generate_complete_graph(num_nodes, 'random', 0.7, seed=42)
        gen_time = time.time() - start

        random.seed(42)
        scapegoat = random.choice(list(graph.nodes))
        accuser = random.choice(graph.neighbors(scapegoat))
        metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
        complete_results.append(metrics.to_dict())
        print(f"✓ {metrics.simulation_time:.2f}s")

    all_results['complete'] = complete_results

    # 3. Pathological structures - small
    print("\n[3/5] Testing pathological structures...")
    pathological_results = []
    num_nodes = 300

    for name, generator in [
        ('star', lambda: generate_pathological_star(num_nodes, 0.7, 42)),
        ('ring', lambda: generate_pathological_ring(num_nodes, 0.7, 42)),
        ('bipartite', lambda: generate_pathological_bipartite(num_nodes, 0.7, 42))
    ]:
        print(f"  Testing {name}...", end=" ", flush=True)
        start = time.time()
        graph = generator()
        gen_time = time.time() - start

        random.seed(42)
        scapegoat = random.choice([n for n in graph.nodes if graph.neighbors(n)])
        accuser = random.choice(graph.neighbors(scapegoat))

        metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
        result = metrics.to_dict()
        result['structure_type'] = name
        pathological_results.append(result)
        print(f"✓ {metrics.simulation_time:.2f}s")

    all_results['pathological'] = pathological_results

    # 4. Density variations
    print("\n[4/5] Testing density variations...")
    density_results = []
    num_nodes = 300

    for name, min_deg, max_deg in [
        ('ultra_sparse', 2, 3),
        ('sparse', 3, 8),
        ('medium', 8, 15),
        ('dense', 15, 20)
    ]:
        print(f"  Testing {name}...", end=" ", flush=True)
        start = time.time()
        graph = generate_sparse_graph(num_nodes, min_deg, max_deg, 0.7, seed=42)
        gen_time = time.time() - start

        random.seed(42)
        scapegoat = random.choice(list(graph.nodes))
        neighbors = graph.neighbors(scapegoat)
        if neighbors:
            accuser = random.choice(neighbors)
            metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
            result = metrics.to_dict()
            result['density_config'] = name
            density_results.append(result)
            print(f"✓ {metrics.simulation_time:.2f}s")

    all_results['density'] = density_results

    # 5. Positivity variations
    print("\n[5/5] Testing positivity variations...")
    positivity_results = []
    num_nodes = 300

    for p_pos in [0.1, 0.3, 0.5, 0.7, 0.9]:
        print(f"  Testing p_positive={p_pos}...", end=" ", flush=True)
        start = time.time()
        graph = generate_sparse_graph(num_nodes, 3, 8, p_pos, seed=42)
        gen_time = time.time() - start

        random.seed(42)
        scapegoat = random.choice(list(graph.nodes))
        neighbors = graph.neighbors(scapegoat)
        if neighbors:
            accuser = random.choice(neighbors)
            metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
            result = metrics.to_dict()
            result['p_positive'] = p_pos
            positivity_results.append(result)
            print(f"✓ {metrics.simulation_time:.2f}s")

    all_results['positivity'] = positivity_results

    # Save all results
    print("\nSaving results...")
    for category, results in all_results.items():
        filename = f"{output_dir}/{category}_results.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"  ✓ {category}_results.json")

    # Generate summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    total = sum(len(r) for r in all_results.values())
    print(f"\nTotal tests completed: {total}")

    # Scaling analysis
    print("\nSparse Graph Scaling:")
    print(f"{'Nodes':>6} {'Edges':>6} {'Time(s)':>8} {'Decisions':>10} {'D/N':>6} {'Depth':>6}")
    print("-" * 55)
    for r in sparse_results:
        print(f"{r['graph']['num_nodes']:6d} {r['graph']['num_edges']:6d} "
              f"{r['timing']['simulation_time']:8.3f} {r['decisions']['total']:10d} "
              f"{r['decisions']['decisions_per_node']:6.2f} {r['bfs']['depth']:6d}")

    # Complete graph scaling
    print("\nComplete Graph Scaling (Worst-Case):")
    print(f"{'Nodes':>6} {'Edges':>6} {'Time(s)':>8} {'Decisions':>10}")
    print("-" * 40)
    for r in complete_results:
        print(f"{r['graph']['num_nodes']:6d} {r['graph']['num_edges']:6d} "
              f"{r['timing']['simulation_time']:8.3f} {r['decisions']['total']:10d}")

    # Structure comparison
    print("\nPathological Structures ({} nodes):".format(num_nodes))
    print(f"{'Structure':>12} {'Edges':>6} {'Time(s)':>8} {'Accusers':>9}")
    print("-" * 40)
    for r in pathological_results:
        print(f"{r['structure_type']:>12} {r['graph']['num_edges']:6d} "
              f"{r['timing']['simulation_time']:8.3f} {r['outcomes']['accusers']:9d}")

    # Density impact
    print("\nDensity Impact ({} nodes):".format(num_nodes))
    print(f"{'Density':>15} {'Edges':>6} {'Time(s)':>8} {'Decisions':>10}")
    print("-" * 50)
    for r in density_results:
        print(f"{r['density_config']:>15} {r['graph']['num_edges']:6d} "
              f"{r['timing']['simulation_time']:8.3f} {r['decisions']['total']:10d}")

    # Positivity impact
    print("\nPositivity Impact ({} nodes):".format(num_nodes))
    print(f"{'p_positive':>11} {'Time(s)':>8} {'Decisions':>10} {'Unity':>6}")
    print("-" * 40)
    for r in positivity_results:
        unity = '✓' if r['outcomes']['unity_achieved'] else '✗'
        print(f"{r['p_positive']:11.1f} {r['timing']['simulation_time']:8.3f} "
              f"{r['decisions']['total']:10d} {unity:>6}")

    print(f"\nAll results saved to: {output_dir}/")

    return 0


if __name__ == '__main__':
    sys.exit(mini_test())
