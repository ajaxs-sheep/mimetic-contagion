#!/usr/bin/env python3
"""
Theoretical analysis: Compare actual algorithm performance to theoretical bounds.
"""

import json
import os
import sys


def analyze_theoretical_bounds(results_dir: str):
    """
    Analyze how actual performance compares to theoretical bounds.

    Theoretical bounds:
    - Minimum decisions: V-1 (if scapegoating spreads in tree-like BFS, everyone joins)
    - Maximum decisions: O(V²) for cleanup phase (all --- triangles)
    - Time complexity: O(V+E) for sparse graphs (BFS), O(V³) for complete graphs
    """

    print("="*70)
    print("THEORETICAL BOUNDS ANALYSIS")
    print("="*70)

    # Load results
    results_files = {
        'large_sparse': 'large_sparse_results.json',
        'complete': 'complete_graph_results.json',
        'pathological': 'pathological_structures_results.json'
    }

    all_analyses = {}

    for category, filename in results_files.items():
        filepath = os.path.join(results_dir, filename)
        if not os.path.exists(filepath):
            print(f"\nWarning: {filepath} not found, skipping {category}")
            continue

        with open(filepath) as f:
            results = json.load(f)

        if not results:
            continue

        print(f"\n{category.upper().replace('_', ' ')}")
        print("-" * 70)

        analyses = []

        for r in results:
            V = r['graph']['num_nodes']
            E = r['graph']['num_edges']
            actual_decisions = r['decisions']['total']
            bfs_decisions = r['decisions']['bfs_phase']
            cleanup_decisions = r['decisions']['cleanup_phase']
            actual_time = r['timing']['simulation_time']

            # Theoretical minimum: V-1 (everyone joins accusers via BFS)
            min_decisions = V - 1

            # Theoretical maximum: V-1 (BFS) + O(E) (cleanup, each edge examined once)
            # For dense graphs, this could be much higher
            max_decisions_estimate = V - 1 + E

            # Decision efficiency
            efficiency = min_decisions / actual_decisions if actual_decisions > 0 else 0

            # Time per decision
            time_per_decision = actual_time / actual_decisions if actual_decisions > 0 else 0

            # Time per node
            time_per_node = actual_time / V if V > 0 else 0

            # Sparsity (average degree)
            avg_degree = (2 * E) / V if V > 0 else 0

            analysis = {
                'nodes': V,
                'edges': E,
                'avg_degree': round(avg_degree, 2),
                'min_decisions_theoretical': min_decisions,
                'actual_decisions': actual_decisions,
                'efficiency_ratio': round(efficiency, 3),
                'overhead_ratio': round(actual_decisions / min_decisions, 2) if min_decisions > 0 else 0,
                'bfs_decisions': bfs_decisions,
                'cleanup_decisions': cleanup_decisions,
                'cleanup_ratio': round(cleanup_decisions / actual_decisions, 2) if actual_decisions > 0 else 0,
                'time_per_decision_ms': round(time_per_decision * 1000, 3),
                'time_per_node_ms': round(time_per_node * 1000, 3),
                'actual_time': round(actual_time, 3)
            }

            analyses.append(analysis)

            # Print analysis
            print(f"\n  {V} nodes, {E} edges (avg degree {avg_degree:.1f}):")
            print(f"    Min theoretical decisions: {min_decisions}")
            print(f"    Actual decisions: {actual_decisions}")
            print(f"    Overhead: {analysis['overhead_ratio']:.2f}x")
            print(f"    BFS: {bfs_decisions}, Cleanup: {cleanup_decisions} ({analysis['cleanup_ratio']*100:.0f}%)")
            print(f"    Time: {actual_time:.3f}s ({time_per_decision*1000:.3f} ms/decision, {time_per_node*1000:.3f} ms/node)")

        all_analyses[category] = analyses

    # Summary insights
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)

    print("\n1. ALGORITHMIC EFFICIENCY")
    print("   The algorithm is deterministic BFS, so actual steps ARE minimal for")
    print("   information propagation. Overhead comes from:")
    print("   - Rule 2 (cleanup phase): Resolving --- triangles for unity")
    print("   - Each node processed exactly once (optimal for single-pass)")

    print("\n2. DECISION OVERHEAD SOURCES")
    print("   - BFS phase: V-1 decisions (minimal - one per non-scapegoat node)")
    print("   - Cleanup phase: O(degree²) per enemy node (resolve all --- triangles)")
    print("   - Total overhead = cleanup overhead (depends on graph structure)")

    print("\n3. BEST CASE SCENARIO")
    print("   - Sparse graph with high positive edge ratio")
    print("   - Scapegoat well-connected (information spreads quickly)")
    print("   - Few pre-existing enemies (minimal cleanup)")
    print("   - Overhead ratio: ~1.0-1.5x")

    print("\n4. WORST CASE SCENARIO")
    print("   - Complete graph (maximum triangles)")
    print("   - Low positive edge ratio (many conflicts)")
    print("   - Many pre-existing enemies of scapegoat")
    print("   - Overhead ratio: ~2-4x (cleanup dominates)")

    print("\n5. TIME COMPLEXITY VERIFICATION")
    if all_analyses.get('large_sparse'):
        sparse = all_analyses['large_sparse']
        if len(sparse) >= 2:
            # Check if time scales sub-quadratically
            ratio1 = sparse[-1]['actual_time'] / sparse[0]['actual_time']
            ratio2 = (sparse[-1]['nodes'] / sparse[0]['nodes']) ** 2

            print(f"   Sparse graphs:")
            print(f"   - Time ratio: {ratio1:.1f}x")
            print(f"   - Nodes² ratio: {ratio2:.1f}x")

            if ratio1 < ratio2 * 0.8:
                print(f"   ✓ Scales better than O(V²) (closer to O(V+E) or O(V log V))")
            elif ratio1 < ratio2 * 1.2:
                print(f"   ~ Scales approximately O(V²)")
            else:
                print(f"   ✗ Scales worse than O(V²)")

    if all_analyses.get('complete'):
        complete = all_analyses['complete']
        if len(complete) >= 2:
            ratio1 = complete[-1]['actual_time'] / complete[0]['actual_time']
            ratio2 = (complete[-1]['nodes'] / complete[0]['nodes']) ** 2
            ratio3 = (complete[-1]['nodes'] / complete[0]['nodes']) ** 3

            print(f"\n   Complete graphs:")
            print(f"   - Time ratio: {ratio1:.1f}x")
            print(f"   - Nodes² ratio: {ratio2:.1f}x")
            print(f"   - Nodes³ ratio: {ratio3:.1f}x")

            if ratio1 < ratio2 * 1.2:
                print(f"   ✓ Scales approximately O(V²)")
            elif ratio1 < ratio3 * 1.2:
                print(f"   ~ Scales approximately O(V³)")
            else:
                print(f"   ✗ Scales worse than O(V³)")

    print("\n6. COMPARING TO THEORETICAL MINIMUM")
    print("   Q: Is there a way to reduce overhead?")
    print("   A: No - the two-phase algorithm is necessary:")
    print("      - Phase 1 (BFS): Information propagation (minimal, cannot reduce)")
    print("      - Phase 2 (Cleanup): Unity enforcement (necessary for guaranteed balance)")
    print("   The cleanup phase COULD be skipped if we only want scapegoat isolation")
    print("   without community unity, but that defeats the purpose (cohesion against scapegoat).")

    print("\n7. OPTIMIZATION POTENTIAL")
    print("   - Adjacency caching: Reduces time per decision, not decision count")
    print("   - Triangle optimization: Reduces cleanup time from O(V³) to O(V × d²)")
    print("   - These won't reduce decisions, but will reduce TIME significantly")

    # Save analysis
    output_file = os.path.join(results_dir, 'theoretical_analysis.json')
    with open(output_file, 'w') as f:
        json.dump(all_analyses, f, indent=2)

    print(f"\n✓ Analysis saved to: {output_file}")

    return all_analyses


def main():
    results_dir = "output/stress_tests"

    if not os.path.exists(results_dir):
        print(f"Error: {results_dir} not found")
        print("Please run stress_tests.py first")
        return 1

    analyze_theoretical_bounds(results_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
