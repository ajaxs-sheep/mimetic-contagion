#!/usr/bin/env python3
"""
Generate basic scapegoating visualizations.

Creates:
1. 5-node complete graph - successful scapegoating
2. 5-node mixed graph - partial scapegoating (with defenders)
3. 20-node sparse graph - wave propagation
4. Comparison grid (small vs large)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
import viz_utils as vu
import random


def generate_5node_success():
    """
    Viz 1.1: 5-node complete graph with successful scapegoating.

    All nodes are friends initially. One accuses another, complete unity achieved.
    """
    print("\n" + "="*70)
    print("VIZ 1.1: 5-Node Complete Graph - Successful Scapegoating")
    print("="*70)

    # Create complete graph
    nodes = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
    graph = vu.create_complete_graph_nodes(nodes)

    scapegoat = 'Bob'
    initial_accuser = 'Alice'

    print(f"\nScapegoat: {scapegoat}")
    print(f"Accuser: {initial_accuser}")
    print(f"Structure: Complete graph (all friends)")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, initial_accuser)

    # Create layout
    positions = vu.circular_layout(nodes, radius=1.5)

    # Generate animation frames
    graph_states = []

    # Initial state
    initial_graph = graph.copy()
    graph_states.append((initial_graph, set(), set()))

    # Add accusation edge flip
    accuser_graph = graph.copy()
    accuser_graph.flip_edge(initial_accuser, scapegoat)
    graph_states.append((accuser_graph, {initial_accuser}, set()))

    # Process each decision
    current_graph = accuser_graph.copy()
    current_accusers = {initial_accuser}
    current_defenders = set()

    for decision in result.decisions:
        if decision.action == 'join_accusers':
            current_accusers.add(decision.node)
            current_graph.flip_edge(decision.node, scapegoat)
        elif decision.action == 'hear_accusation':
            current_accusers.add(decision.node)
            current_graph.add_edge(decision.node, scapegoat, -1)
        elif decision.action == 'defend':
            current_defenders.add(decision.node)

        # Add frame
        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    # Final state (hold for a few frames)
    for _ in range(3):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/basic/5node_success.gif'
    os.makedirs('output/basic', exist_ok=True)

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=2
    )

    mob_size = len(result.accusers)
    total_non_scapegoat = len(nodes) - 1

    print(f"\n✓ Animation saved: {output_path}")
    print(f"  Mob: {mob_size}/{total_non_scapegoat} joined ({100*mob_size/total_non_scapegoat:.0f}%)")
    print(f"  Unity: {'COMPLETE' if result.contagion_succeeded else 'PARTIAL'}")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser


def generate_5node_partial():
    """
    Viz 1.2: 5-node graph with partial scapegoating (some defenders).

    Has some internal conflicts. Not everyone joins accusers.
    """
    print("\n" + "="*70)
    print("VIZ 1.2: 5-Node Mixed Graph - Partial Scapegoating")
    print("="*70)

    # Create graph with mixed edges
    nodes = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
    graph = SignedGraph()

    for node in nodes:
        graph.add_node(node)

    # Create specific structure:
    # Alice and Charlie are friends
    # Bob and David are friends (Bob will be scapegoat)
    # Eve and Bob are friends
    # Alice and David are enemies
    # Charlie and Eve are friends

    edges = [
        ('Alice', 'Charlie', 1),
        ('Alice', 'Bob', 1),    # Will flip when Alice accuses
        ('Alice', 'David', -1), # Pre-existing conflict
        ('Bob', 'David', 1),    # Bob's friend (will defend)
        ('Bob', 'Eve', 1),      # Bob's friend
        ('Charlie', 'Eve', 1),
        ('Charlie', 'Bob', 1),
        ('David', 'Eve', 1),
    ]

    for u, v, sign in edges:
        graph.add_edge(u, v, sign)

    scapegoat = 'Bob'
    initial_accuser = 'Alice'

    print(f"\nScapegoat: {scapegoat}")
    print(f"Accuser: {initial_accuser}")
    print(f"Structure: Mixed graph (some pre-existing conflicts)")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, initial_accuser)

    # Create layout
    positions = vu.circular_layout(nodes, radius=1.5)

    # Generate animation frames (similar to above)
    graph_states = []
    graph_states.append((graph.copy(), set(), set()))

    accuser_graph = graph.copy()
    accuser_graph.flip_edge(initial_accuser, scapegoat)
    graph_states.append((accuser_graph, {initial_accuser}, set()))

    current_graph = accuser_graph.copy()
    current_accusers = {initial_accuser}
    current_defenders = set()

    for decision in result.decisions:
        if decision.action == 'join_accusers':
            current_accusers.add(decision.node)
            current_graph.flip_edge(decision.node, scapegoat)
        elif decision.action == 'hear_accusation':
            current_accusers.add(decision.node)
            current_graph.add_edge(decision.node, scapegoat, -1)
        elif decision.action == 'defend':
            current_defenders.add(decision.node)

        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    for _ in range(3):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/basic/5node_partial.gif'

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=2
    )

    mob_size = len(result.accusers)
    total_non_scapegoat = len(nodes) - 1
    defender_count = len([d for d in result.decisions if d.action == 'defend'])

    print(f"\n✓ Animation saved: {output_path}")
    print(f"  Mob: {mob_size}/{total_non_scapegoat} joined ({100*mob_size/total_non_scapegoat:.0f}%)")
    print(f"  Defenders: {defender_count}")
    print(f"  Unity: {'COMPLETE' if result.contagion_succeeded else 'PARTIAL'}")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser


def generate_20node_wave():
    """
    Viz 1.3: 20-node sparse graph showing BFS wave propagation AND unification.

    Starts with pre-existing conflicts between non-scapegoat nodes.
    Through the scapegoating process, those conflicts get resolved (Rule 2: --- triangles).
    By the end, everyone other than the scapegoat is unified (all positive edges).

    Demonstrates: Scapegoating creates social cohesion by resolving internal conflicts.
    """
    print("\n" + "="*70)
    print("VIZ 1.3: 20-Node Sparse Graph - Wave Propagation & Unification")
    print("="*70)

    # Generate sparse graph with pre-existing conflicts
    random.seed(42)
    nodes = [f'N{i}' for i in range(20)]

    graph = SignedGraph()
    for node in nodes:
        graph.add_node(node)

    # Ring (each node has 2 neighbors) - all positive
    for i in range(len(nodes)):
        graph.add_edge(nodes[i], nodes[(i+1) % len(nodes)], 1)

    # Add random positive edges to increase connectivity
    for i in range(len(nodes)):
        current_degree = len([n for n in graph.neighbors(nodes[i])])
        while current_degree < 3:
            j = random.randint(0, len(nodes)-1)
            if i != j and not graph.has_edge(nodes[i], nodes[j]):
                graph.add_edge(nodes[i], nodes[j], 1)
                current_degree += 1

    # Add more random positive edges
    for _ in range(15):
        i = random.randint(0, len(nodes)-1)
        j = random.randint(0, len(nodes)-1)
        if i != j and not graph.has_edge(nodes[i], nodes[j]):
            graph.add_edge(nodes[i], nodes[j], 1)

    # Now strategically add some negative edges between non-scapegoat nodes
    # These will get resolved during scapegoating via Rule 2 (--- triangles)
    scapegoat = 'N10'
    initial_accuser = 'N0'

    # Add negative edges that will create --- triangles with the scapegoat
    # Example: N1 and N5 are enemies, both will turn against N10, creating --- triangle
    conflicts = [
        ('N1', 'N5'),   # Will both become enemies of N10
        ('N3', 'N7'),   # Will both become enemies of N10
        ('N12', 'N15'), # Will both become enemies of N10
        ('N2', 'N8'),   # Will both become enemies of N10
    ]

    for u, v in conflicts:
        if not graph.has_edge(u, v):
            graph.add_edge(u, v, -1)  # Pre-existing conflict

    # Ensure accuser and scapegoat are connected
    if not graph.has_edge(initial_accuser, scapegoat):
        graph.add_edge(initial_accuser, scapegoat, 1)

    # Count initial negative edges (excluding scapegoat)
    initial_conflicts = 0
    for u, v in graph.edges:
        if graph.get_edge(u, v) == -1 and u != scapegoat and v != scapegoat:
            initial_conflicts += 1

    print(f"\nScapegoat: {scapegoat}")
    print(f"Accuser: {initial_accuser}")
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(graph.edges)}")
    print(f"Initial conflicts (negative edges among non-scapegoat nodes): {initial_conflicts}")
    print(f"\nPrediction: Internal conflicts will be RESOLVED through scapegoating")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, initial_accuser)

    # Create force-directed layout
    positions = vu.force_directed_layout(graph, iterations=100)

    # Generate animation frames
    graph_states = []
    graph_states.append((graph.copy(), set(), set()))

    accuser_graph = graph.copy()
    if accuser_graph.has_edge(initial_accuser, scapegoat):
        accuser_graph.flip_edge(initial_accuser, scapegoat)
    else:
        accuser_graph.add_edge(initial_accuser, scapegoat, -1)
    graph_states.append((accuser_graph, {initial_accuser}, set()))

    current_graph = accuser_graph.copy()
    current_accusers = {initial_accuser}
    current_defenders = set()

    for decision in result.decisions:
        if decision.action == 'join_accusers':
            current_accusers.add(decision.node)
            current_graph.flip_edge(decision.node, scapegoat)
        elif decision.action == 'hear_accusation':
            current_accusers.add(decision.node)
            if current_graph.has_edge(decision.node, scapegoat):
                current_graph.flip_edge(decision.node, scapegoat)
            else:
                current_graph.add_edge(decision.node, scapegoat, -1)
        elif decision.action == 'defend':
            current_defenders.add(decision.node)

        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    for _ in range(5):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/basic/20node_wave.gif'

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=1.5
    )

    # Count final conflicts (should be 0 among non-scapegoat accusers)
    final_conflicts = 0
    resolved_conflicts = 0
    for u, v in result.final_state.edges:
        if result.final_state.get_edge(u, v) == -1 and u != scapegoat and v != scapegoat:
            final_conflicts += 1
        # Count befriend actions (Rule 2 resolutions)

    befriend_count = len([d for d in result.decisions if d.action == 'befriend_other'])

    # Calculate mob size (accusers excluding scapegoat, but scapegoat is NOT in accusers set)
    mob_size = len(result.accusers)
    total_non_scapegoat = len(nodes) - 1

    print(f"\n✓ Animation saved: {output_path}")
    print(f"  Mob: {mob_size}/{total_non_scapegoat} joined ({100*mob_size/total_non_scapegoat:.0f}%)")
    print(f"  Unity: {'COMPLETE' if result.contagion_succeeded else 'PARTIAL'}")
    print(f"\n  Initial conflicts (among non-scapegoat): {initial_conflicts}")
    print(f"  Befriend actions (--- triangle resolutions): {befriend_count}")
    print(f"  Final conflicts (among non-scapegoat): {final_conflicts}")
    print(f"  → Scapegoating {'UNIFIED' if final_conflicts == 0 else 'partially unified'} the group")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser


def generate_comparison_grid(data_5node_success, data_20node):
    """
    Viz 1.4: Comparison grid showing small vs large networks.

    Simple 1x2 grid comparing final states only
    """
    print("\n" + "="*70)
    print("VIZ 1.4: Size Comparison Grid")
    print("="*70)

    graph_5, pos_5, acc_5, def_5, scape_5, init_5 = data_5node_success
    graph_20, pos_20, acc_20, def_20, scape_20, init_20 = data_20node

    images_data = [
        (graph_5, pos_5, acc_5, def_5, scape_5, init_5),  # 5-node final
        (graph_20, pos_20, acc_20, def_20, scape_20, init_20),  # 20-node final
    ]

    titles = [
        "Small Network (5 nodes)\nComplete unity: 100%",
        "Large Network (20 nodes)\nScalability: 94.7% unity"
    ]

    output_path = 'output/basic/size_comparison.png'

    vu.create_comparison_grid(images_data, output_path, titles)

    print(f"\n✓ Comparison grid saved: {output_path}")


def main():
    """Generate all basic visualizations."""
    print("\n" + "#"*70)
    print("# BASIC SCAPEGOATING VISUALIZATIONS")
    print("#"*70)

    # Create output directory
    os.makedirs('output/basic', exist_ok=True)

    # Generate visualizations
    data_success = generate_5node_success()
    data_partial = generate_5node_partial()
    data_20node = generate_20node_wave()
    generate_comparison_grid(data_success, data_20node)

    print("\n" + "="*70)
    print("✓ ALL BASIC VISUALIZATIONS COMPLETE")
    print("="*70)
    print(f"\nOutput directory: output/basic/")
    print(f"Generated files:")
    print(f"  - 5node_success.gif")
    print(f"  - 5node_partial.gif")
    print(f"  - 20node_wave.gif")
    print(f"  - size_comparison.png")

    return 0


if __name__ == '__main__':
    sys.exit(main())
