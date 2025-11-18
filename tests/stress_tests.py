#!/usr/bin/env python3
"""
Comprehensive stress testing suite for scapegoating contagion simulator.
Tests large graphs, pathological structures, and analyzes computational efficiency.
"""

import sys
import os
import time
import json
import random
import tracemalloc
from collections import defaultdict
from typing import Dict, List, Tuple, Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
from src.analyzer import find_all_triangles, find_unbalanced_triangles
from generate_graph import generate_sparse_graph, generate_complete_graph


class PerformanceMetrics:
    """Detailed performance metrics for a single simulation run."""

    def __init__(self):
        self.num_nodes = 0
        self.num_edges = 0
        self.avg_degree = 0.0
        self.edge_positivity = 0.0  # Fraction of positive edges

        # Timing
        self.generation_time = 0.0
        self.simulation_time = 0.0
        self.bfs_phase_time = 0.0
        self.cleanup_phase_time = 0.0

        # Memory
        self.peak_memory_mb = 0.0
        self.memory_per_node_kb = 0.0

        # Decision statistics
        self.total_decisions = 0
        self.bfs_decisions = 0
        self.cleanup_decisions = 0
        self.rule1_count = 0  # Forced choice
        self.rule2_count = 0  # Resolve --- triangles
        self.rule3_count = 0  # Hear accusation

        # BFS traversal
        self.bfs_depth = 0
        self.bfs_depth_distribution = []  # Nodes at each level

        # Outcomes
        self.accusers_count = 0
        self.defenders_count = 0
        self.all_against_one = False
        self.balanced = False
        self.unity_achieved = False
        self.contagion_succeeded = False

        # Graph properties
        self.scapegoat = None
        self.accuser = None
        self.initial_triangles = 0
        self.final_triangles = 0
        self.initial_unbalanced = 0
        self.final_unbalanced = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'graph': {
                'num_nodes': self.num_nodes,
                'num_edges': self.num_edges,
                'avg_degree': round(self.avg_degree, 2),
                'edge_positivity': round(self.edge_positivity, 3),
                'initial_triangles': self.initial_triangles,
                'initial_unbalanced': self.initial_unbalanced,
                'final_triangles': self.final_triangles,
                'final_unbalanced': self.final_unbalanced
            },
            'timing': {
                'generation_time': round(self.generation_time, 4),
                'simulation_time': round(self.simulation_time, 4),
                'bfs_phase_time': round(self.bfs_phase_time, 4),
                'cleanup_phase_time': round(self.cleanup_phase_time, 4),
                'total_time': round(self.generation_time + self.simulation_time, 4)
            },
            'memory': {
                'peak_memory_mb': round(self.peak_memory_mb, 2),
                'memory_per_node_kb': round(self.memory_per_node_kb, 2)
            },
            'decisions': {
                'total': self.total_decisions,
                'bfs_phase': self.bfs_decisions,
                'cleanup_phase': self.cleanup_decisions,
                'rule1_forced_choice': self.rule1_count,
                'rule2_befriend_enemy': self.rule2_count,
                'rule3_hear_accusation': self.rule3_count,
                'decisions_per_node': round(self.total_decisions / self.num_nodes, 2) if self.num_nodes > 0 else 0
            },
            'bfs': {
                'depth': self.bfs_depth,
                'depth_distribution': self.bfs_depth_distribution
            },
            'outcomes': {
                'accusers': self.accusers_count,
                'defenders': self.defenders_count,
                'all_against_one': self.all_against_one,
                'balanced': self.balanced,
                'unity_achieved': self.unity_achieved,
                'contagion_succeeded': self.contagion_succeeded
            },
            'scenario': {
                'scapegoat': self.scapegoat,
                'accuser': self.accuser
            }
        }


def count_rule_types(decisions):
    """Count how many times each rule fired."""
    rule1 = 0  # "chose them over"
    rule2 = 0  # "befriend"
    rule3 = 0  # "Heard from"

    for d in decisions:
        if "chose them over" in d.reason:
            rule1 += 1
        elif "befriend" in d.reason:
            rule2 += 1
        elif "Heard from" in d.reason:
            rule3 += 1

    return rule1, rule2, rule3


def measure_bfs_depth(graph: SignedGraph, accuser: str, accusers_set) -> Tuple[int, List[int]]:
    """
    Measure BFS depth and distribution.
    Returns (max_depth, nodes_per_level)
    """
    from collections import deque

    visited = {accuser}
    queue = deque([(accuser, 0)])  # (node, depth)
    depth_counts = defaultdict(int)
    max_depth = 0

    while queue:
        node, depth = queue.popleft()
        depth_counts[depth] += 1
        max_depth = max(max_depth, depth)

        # Add friends to queue
        for neighbor in graph.neighbors(node):
            if neighbor not in visited and graph.get_edge(node, neighbor) == 1:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))

    # Convert to list
    distribution = [depth_counts[i] for i in range(max_depth + 1)]
    return max_depth, distribution


def run_instrumented_simulation(
    graph: SignedGraph,
    scapegoat: str,
    accuser: str,
    graph_gen_time: float = 0.0
) -> PerformanceMetrics:
    """
    Run simulation with detailed instrumentation.
    """
    metrics = PerformanceMetrics()

    # Graph properties
    metrics.num_nodes = len(graph.nodes)
    metrics.num_edges = len(graph.edges)
    metrics.avg_degree = (2 * len(graph.edges)) / len(graph.nodes) if len(graph.nodes) > 0 else 0

    positive_edges = sum(1 for sign in graph.edges.values() if sign == 1)
    metrics.edge_positivity = positive_edges / len(graph.edges) if len(graph.edges) > 0 else 0

    metrics.scapegoat = scapegoat
    metrics.accuser = accuser
    metrics.generation_time = graph_gen_time

    # Count initial triangles
    initial_triangles = find_all_triangles(graph)
    metrics.initial_triangles = len(initial_triangles)
    initial_unbalanced = find_unbalanced_triangles(graph)
    metrics.initial_unbalanced = len(initial_unbalanced)

    # Start memory tracking
    tracemalloc.start()

    # Run simulation
    start_time = time.time()
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, accuser)
    metrics.simulation_time = time.time() - start_time

    # Memory stats
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    metrics.peak_memory_mb = peak / (1024 * 1024)
    metrics.memory_per_node_kb = peak / (1024 * metrics.num_nodes) if metrics.num_nodes > 0 else 0

    # Decision statistics
    bfs_decisions = [d for d in result.decisions if 'Community unity' not in d.reason]
    cleanup_decisions = [d for d in result.decisions if 'Community unity' in d.reason]

    metrics.total_decisions = len(result.decisions)
    metrics.bfs_decisions = len(bfs_decisions)
    metrics.cleanup_decisions = len(cleanup_decisions)

    # Estimate phase times (proportional to decisions, rough approximation)
    if metrics.total_decisions > 0:
        metrics.bfs_phase_time = metrics.simulation_time * (metrics.bfs_decisions / metrics.total_decisions)
        metrics.cleanup_phase_time = metrics.simulation_time * (metrics.cleanup_decisions / metrics.total_decisions)

    # Count rule types
    metrics.rule1_count, metrics.rule2_count, metrics.rule3_count = count_rule_types(result.decisions)

    # BFS depth (measure on initial graph before simulation)
    metrics.bfs_depth, metrics.bfs_depth_distribution = measure_bfs_depth(graph, accuser, result.accusers)

    # Outcomes
    metrics.accusers_count = len(result.accusers)
    metrics.defenders_count = len(result.defenders)
    metrics.all_against_one = result.is_all_against_one
    metrics.balanced = result.is_balanced
    metrics.contagion_succeeded = result.contagion_succeeded

    # Check unity (no negative edges within community)
    final_edges = result.final_state.edges
    community_edges = [e for e, sign in final_edges.items() if scapegoat not in e]
    neg_in_community = sum(1 for e in community_edges if final_edges[e] == -1)
    metrics.unity_achieved = neg_in_community == 0 and result.is_balanced

    # Count final triangles
    final_triangles = find_all_triangles(result.final_state)
    metrics.final_triangles = len(final_triangles)
    final_unbalanced = find_unbalanced_triangles(result.final_state)
    metrics.final_unbalanced = len(final_unbalanced)

    return metrics


# ============================================================
# GRAPH GENERATORS
# ============================================================

def generate_pathological_star(num_nodes: int, p_positive: float = 0.6, seed: int = 42) -> SignedGraph:
    """
    Generate star graph: one central hub connected to all others.
    Peripheral nodes have no edges between them.
    """
    random.seed(seed)
    graph = SignedGraph()

    # Create nodes
    hub = "hub"
    nodes = [hub] + [f"n{i}" for i in range(num_nodes - 1)]

    for node in nodes:
        graph.add_node(node)

    # Connect hub to all others
    for i in range(1, num_nodes):
        sign = 1 if random.random() < p_positive else -1
        graph.add_edge(hub, nodes[i], sign)

    return graph


def generate_pathological_ring(num_nodes: int, p_positive: float = 0.6, seed: int = 42) -> SignedGraph:
    """
    Generate ring graph: nodes in a cycle.
    Minimal connectivity, longest possible paths.
    """
    random.seed(seed)
    graph = SignedGraph()

    nodes = [f"n{i}" for i in range(num_nodes)]

    for node in nodes:
        graph.add_node(node)

    # Create ring
    for i in range(num_nodes):
        next_i = (i + 1) % num_nodes
        sign = 1 if random.random() < p_positive else -1
        graph.add_edge(nodes[i], nodes[next_i], sign)

    return graph


def generate_pathological_bipartite(num_nodes: int, p_positive: float = 0.6, seed: int = 42) -> SignedGraph:
    """
    Generate bipartite graph: two factions with edges only between factions.
    Tests disconnected friendship components.
    """
    random.seed(seed)
    graph = SignedGraph()

    # Split into two groups
    size_a = num_nodes // 2
    size_b = num_nodes - size_a

    group_a = [f"a{i}" for i in range(size_a)]
    group_b = [f"b{i}" for i in range(size_b)]

    for node in group_a + group_b:
        graph.add_node(node)

    # Connect between groups (not within)
    for a in group_a:
        for b in group_b:
            if random.random() < 0.3:  # Sparse connections
                sign = 1 if random.random() < p_positive else -1
                graph.add_edge(a, b, sign)

    return graph


def generate_pathological_disconnected(num_nodes: int, num_components: int = 3, seed: int = 42) -> SignedGraph:
    """
    Generate graph with multiple disconnected components.
    Tests partial scapegoating (only reachable nodes affected).
    """
    random.seed(seed)
    graph = SignedGraph()

    # Split nodes into components
    nodes_per_component = num_nodes // num_components
    components = []

    node_idx = 0
    for c in range(num_components):
        size = nodes_per_component if c < num_components - 1 else (num_nodes - node_idx)
        component = [f"c{c}n{i}" for i in range(size)]
        components.append(component)
        node_idx += size

    # Add nodes
    for component in components:
        for node in component:
            graph.add_node(node)

    # Create edges within each component (complete subgraphs)
    for component in components:
        for i, node1 in enumerate(component):
            for node2 in component[i+1:]:
                sign = 1 if random.random() < 0.7 else -1
                graph.add_edge(node1, node2, sign)

    return graph


# ============================================================
# TEST SUITES
# ============================================================

def test_large_sparse_graphs(output_dir: str = "output/stress_tests"):
    """
    Test scaling with large sparse graphs (realistic social networks).
    Sizes: 2000, 3000, 5000 nodes
    """
    print("\n" + "="*70)
    print("STRESS TEST 1: Large Sparse Graphs")
    print("="*70)

    test_sizes = [2000, 3000, 5000]
    seed = 42
    results = []

    for num_nodes in test_sizes:
        print(f"\nTesting {num_nodes} nodes (sparse)...")

        # Generate graph
        start_time = time.time()
        graph = generate_sparse_graph(
            num_nodes=num_nodes,
            min_degree=3,
            max_degree=10,
            p_positive=0.7,
            seed=seed
        )
        gen_time = time.time() - start_time

        print(f"  Generated {len(graph.edges)} edges in {gen_time:.2f}s")

        # Select scapegoat and accuser
        random.seed(seed)
        scapegoat = random.choice(list(graph.nodes))
        neighbors = graph.neighbors(scapegoat)
        if not neighbors:
            print(f"  ERROR: Scapegoat has no neighbors, skipping")
            continue
        accuser = random.choice(neighbors)

        # Run simulation
        print(f"  Running simulation (scapegoat={scapegoat[:10]}..., accuser={accuser[:10]}...)...")
        metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
        results.append(metrics)

        # Print summary
        print(f"  ✓ Complete in {metrics.simulation_time:.2f}s")
        print(f"    Decisions: {metrics.total_decisions} (BFS: {metrics.bfs_decisions}, Cleanup: {metrics.cleanup_decisions})")
        print(f"    Rules: R1={metrics.rule1_count}, R2={metrics.rule2_count}, R3={metrics.rule3_count}")
        print(f"    BFS depth: {metrics.bfs_depth}")
        print(f"    Memory: {metrics.peak_memory_mb:.1f} MB ({metrics.memory_per_node_kb:.2f} KB/node)")
        print(f"    Unity: {'✓' if metrics.unity_achieved else '✗'}")

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/large_sparse_results.json", 'w') as f:
        json.dump([m.to_dict() for m in results], f, indent=2)

    print(f"\n✓ Results saved to {output_dir}/large_sparse_results.json")
    return results


def test_complete_graphs(output_dir: str = "output/stress_tests"):
    """
    Test worst-case O(V³) complete graphs.
    Sizes: 100, 200, 300 nodes
    """
    print("\n" + "="*70)
    print("STRESS TEST 2: Complete Graphs (Worst-Case O(V³))")
    print("="*70)

    test_sizes = [100, 200, 300]
    seed = 42
    results = []

    for num_nodes in test_sizes:
        print(f"\nTesting {num_nodes} nodes (complete graph)...")

        # Generate complete graph
        start_time = time.time()
        nodes = [f"n{i}" for i in range(num_nodes)]
        graph = generate_complete_graph(nodes, mode='random', p_positive=0.7, seed=seed)
        gen_time = time.time() - start_time

        print(f"  Generated {len(graph.edges)} edges in {gen_time:.2f}s")

        # Select scapegoat and accuser
        random.seed(seed)
        scapegoat = random.choice(list(graph.nodes))
        neighbors = graph.neighbors(scapegoat)
        accuser = random.choice(neighbors)

        # Run simulation
        print(f"  Running simulation...")
        metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
        results.append(metrics)

        # Print summary
        print(f"  ✓ Complete in {metrics.simulation_time:.2f}s")
        print(f"    Decisions: {metrics.total_decisions} (BFS: {metrics.bfs_decisions}, Cleanup: {metrics.cleanup_decisions})")
        print(f"    Rules: R1={metrics.rule1_count}, R2={metrics.rule2_count}, R3={metrics.rule3_count}")
        print(f"    BFS depth: {metrics.bfs_depth}")
        print(f"    Memory: {metrics.peak_memory_mb:.1f} MB")
        print(f"    Unity: {'✓' if metrics.unity_achieved else '✗'}")

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/complete_graph_results.json", 'w') as f:
        json.dump([m.to_dict() for m in results], f, indent=2)

    print(f"\n✓ Results saved to {output_dir}/complete_graph_results.json")
    return results


def test_pathological_structures(output_dir: str = "output/stress_tests"):
    """
    Test pathological graph structures.
    """
    print("\n" + "="*70)
    print("STRESS TEST 3: Pathological Graph Structures")
    print("="*70)

    seed = 42
    num_nodes = 1000
    results = []

    structures = [
        ("star", lambda: generate_pathological_star(num_nodes, p_positive=0.7, seed=seed)),
        ("ring", lambda: generate_pathological_ring(num_nodes, p_positive=0.7, seed=seed)),
        ("bipartite", lambda: generate_pathological_bipartite(num_nodes, p_positive=0.7, seed=seed)),
        ("disconnected", lambda: generate_pathological_disconnected(num_nodes, num_components=5, seed=seed))
    ]

    for structure_name, generator in structures:
        print(f"\nTesting {structure_name} graph ({num_nodes} nodes)...")

        # Generate graph
        start_time = time.time()
        graph = generator()
        gen_time = time.time() - start_time

        print(f"  Generated {len(graph.edges)} edges in {gen_time:.2f}s")
        print(f"  Avg degree: {(2*len(graph.edges))/len(graph.nodes):.1f}")

        # Select scapegoat and accuser
        random.seed(seed)
        scapegoat = random.choice(list(graph.nodes))
        neighbors = graph.neighbors(scapegoat)

        if not neighbors:
            print(f"  WARNING: Scapegoat has no neighbors, selecting different scapegoat")
            # Find node with neighbors
            for node in graph.nodes:
                if graph.neighbors(node):
                    scapegoat = node
                    neighbors = graph.neighbors(scapegoat)
                    break

        if not neighbors:
            print(f"  ERROR: No node has neighbors, skipping")
            continue

        accuser = random.choice(neighbors)

        # Run simulation
        print(f"  Running simulation...")
        metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
        metrics_dict = metrics.to_dict()
        metrics_dict['structure_type'] = structure_name
        results.append(metrics_dict)

        # Print summary
        print(f"  ✓ Complete in {metrics.simulation_time:.2f}s")
        print(f"    Decisions: {metrics.total_decisions} (BFS: {metrics.bfs_decisions}, Cleanup: {metrics.cleanup_decisions})")
        print(f"    Rules: R1={metrics.rule1_count}, R2={metrics.rule2_count}, R3={metrics.rule3_count}")
        print(f"    BFS depth: {metrics.bfs_depth}")
        print(f"    Accusers: {metrics.accusers_count}/{num_nodes-1}")
        print(f"    Unity: {'✓' if metrics.unity_achieved else '✗'}")

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/pathological_structures_results.json", 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to {output_dir}/pathological_structures_results.json")
    return results


def test_density_variations(output_dir: str = "output/stress_tests"):
    """
    Test graphs with varying density (same node count).
    """
    print("\n" + "="*70)
    print("STRESS TEST 4: Density Variations")
    print("="*70)

    num_nodes = 1000
    seed = 42
    results = []

    density_configs = [
        ("ultra_sparse", 2, 3),
        ("sparse", 3, 8),
        ("medium", 8, 15),
        ("dense", 15, 30)
    ]

    for config_name, min_degree, max_degree in density_configs:
        print(f"\nTesting {config_name} (degree {min_degree}-{max_degree})...")

        # Generate graph
        start_time = time.time()
        graph = generate_sparse_graph(num_nodes, min_degree, max_degree, p_positive=0.7, seed=seed)
        gen_time = time.time() - start_time

        print(f"  Generated {len(graph.edges)} edges in {gen_time:.2f}s")
        print(f"  Avg degree: {(2*len(graph.edges))/len(graph.nodes):.1f}")

        # Select scapegoat and accuser
        random.seed(seed)
        scapegoat = random.choice(list(graph.nodes))
        neighbors = graph.neighbors(scapegoat)
        if not neighbors:
            print(f"  ERROR: Scapegoat has no neighbors, skipping")
            continue
        accuser = random.choice(neighbors)

        # Run simulation
        print(f"  Running simulation...")
        metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
        metrics_dict = metrics.to_dict()
        metrics_dict['density_config'] = config_name
        results.append(metrics_dict)

        # Print summary
        print(f"  ✓ Complete in {metrics.simulation_time:.2f}s")
        print(f"    Decisions: {metrics.total_decisions}")
        print(f"    Rules: R1={metrics.rule1_count}, R2={metrics.rule2_count}, R3={metrics.rule3_count}")
        print(f"    Unity: {'✓' if metrics.unity_achieved else '✗'}")

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/density_variation_results.json", 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to {output_dir}/density_variation_results.json")
    return results


def test_positivity_variations(output_dir: str = "output/stress_tests"):
    """
    Test graphs with varying edge positivity (same structure).
    """
    print("\n" + "="*70)
    print("STRESS TEST 5: Edge Positivity Variations")
    print("="*70)

    num_nodes = 1000
    seed = 42
    results = []

    positivity_levels = [0.1, 0.3, 0.5, 0.7, 0.9]

    for p_positive in positivity_levels:
        print(f"\nTesting p_positive={p_positive} ({int(p_positive*100)}% positive edges)...")

        # Generate graph
        start_time = time.time()
        graph = generate_sparse_graph(num_nodes, min_degree=3, max_degree=10, p_positive=p_positive, seed=seed)
        gen_time = time.time() - start_time

        positive_count = sum(1 for sign in graph.edges.values() if sign == 1)
        print(f"  Generated {len(graph.edges)} edges ({positive_count} positive, {len(graph.edges)-positive_count} negative)")

        # Select scapegoat and accuser
        random.seed(seed)
        scapegoat = random.choice(list(graph.nodes))
        neighbors = graph.neighbors(scapegoat)
        if not neighbors:
            print(f"  ERROR: Scapegoat has no neighbors, skipping")
            continue
        accuser = random.choice(neighbors)

        # Run simulation
        print(f"  Running simulation...")
        metrics = run_instrumented_simulation(graph, scapegoat, accuser, gen_time)
        metrics_dict = metrics.to_dict()
        metrics_dict['p_positive'] = p_positive
        results.append(metrics_dict)

        # Print summary
        print(f"  ✓ Complete in {metrics.simulation_time:.2f}s")
        print(f"    Decisions: {metrics.total_decisions}")
        print(f"    Rules: R1={metrics.rule1_count}, R2={metrics.rule2_count}, R3={metrics.rule3_count}")
        print(f"    Unity: {'✓' if metrics.unity_achieved else '✗'}")

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/positivity_variation_results.json", 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to {output_dir}/positivity_variation_results.json")
    return results


# ============================================================
# MAIN
# ============================================================

def main():
    """Run comprehensive stress test suite."""
    print("="*70)
    print("COMPREHENSIVE STRESS TEST SUITE")
    print("Scapegoating Contagion Simulator - Performance Analysis")
    print("="*70)

    output_dir = "output/stress_tests"
    os.makedirs(output_dir, exist_ok=True)

    # Run all test suites
    all_results = {}

    try:
        all_results['large_sparse'] = test_large_sparse_graphs(output_dir)
    except Exception as e:
        print(f"\nERROR in large sparse tests: {e}")
        import traceback
        traceback.print_exc()

    try:
        all_results['complete_graphs'] = test_complete_graphs(output_dir)
    except Exception as e:
        print(f"\nERROR in complete graph tests: {e}")
        import traceback
        traceback.print_exc()

    try:
        all_results['pathological'] = test_pathological_structures(output_dir)
    except Exception as e:
        print(f"\nERROR in pathological structure tests: {e}")
        import traceback
        traceback.print_exc()

    try:
        all_results['density'] = test_density_variations(output_dir)
    except Exception as e:
        print(f"\nERROR in density variation tests: {e}")
        import traceback
        traceback.print_exc()

    try:
        all_results['positivity'] = test_positivity_variations(output_dir)
    except Exception as e:
        print(f"\nERROR in positivity variation tests: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("STRESS TESTING COMPLETE")
    print("="*70)
    print(f"\nAll results saved to: {output_dir}/")
    print("  - large_sparse_results.json")
    print("  - complete_graph_results.json")
    print("  - pathological_structures_results.json")
    print("  - density_variation_results.json")
    print("  - positivity_variation_results.json")

    return 0


if __name__ == '__main__':
    sys.exit(main())
