#!/usr/bin/env python3
"""
Generate graph requirements visualizations.

Demonstrates how negative edges block propagation.

Creates:
1. Ring with one negative edge - shows blocking
2. Ring all positive - shows complete success
3. Comparison side-by-side
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
import viz_utils as vu


def generate_ring_with_negative():
    """
    Viz 4.1: Ring with one negative edge blocks propagation.

    6-node ring: N0—N1—N2—N3—N4—N5—N0
    BUT: N2—N3 is negative (enemies)

    Scapegoat: N0
    Accuser: N3

    Propagation goes: N3 → N4 → N5 → N0 (reaches scapegoat directly)
    But CANNOT go: N3 ← N2 ← N1 ← N0 (blocked by N2-N3 enemy edge)

    Result: Only half the ring joins (N3, N4, N5)
    """
    print("\n" + "="*70)
    print("VIZ 4.1: Ring with Negative Edge - Blocks Propagation")
    print("="*70)

    nodes = [f'N{i}' for i in range(6)]
    graph = SignedGraph()

    for node in nodes:
        graph.add_node(node)

    # Ring edges - all positive EXCEPT N2-N3
    for i in range(len(nodes)):
        if i == 2:  # N2 to N3 edge
            graph.add_edge(nodes[i], nodes[(i+1) % len(nodes)], -1)  # NEGATIVE
        else:
            graph.add_edge(nodes[i], nodes[(i+1) % len(nodes)], 1)   # Positive

    scapegoat = 'N0'
    initial_accuser = 'N3'

    # Ensure accuser and scapegoat are connected
    if not graph.has_edge(initial_accuser, scapegoat):
        graph.add_edge(initial_accuser, scapegoat, 1)

    print(f"\nScapegoat: {scapegoat}")
    print(f"Accuser: {initial_accuser}")
    print(f"Structure: 6-node ring with ONE negative edge (N2—N3)")
    print(f"Prediction: Propagation blocked at negative edge")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, initial_accuser)

    # Create circular layout
    positions = vu.circular_layout(nodes, radius=1.5)

    # Generate animation frames
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
            if current_graph.has_edge(decision.node, scapegoat):
                current_graph.flip_edge(decision.node, scapegoat)
            else:
                current_graph.add_edge(decision.node, scapegoat, -1)
        elif decision.action == 'defend':
            current_defenders.add(decision.node)

        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    # Final state (hold)
    for _ in range(5):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/requirements/ring_negative_edge.gif'
    os.makedirs('output/requirements', exist_ok=True)

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=2
    )

    mob_size = len(result.accusers) - 1  # Exclude scapegoat
    total = len(nodes) - 1

    print(f"\n✓ Animation saved: {output_path}")
    print(f"  Mob: {mob_size}/{total} joined ({100*mob_size/total:.0f}%)")
    print(f"  → Negative edge BLOCKED propagation")
    print(f"  → Only nodes on accuser's side of negative edge joined")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser


def generate_ring_all_positive():
    """
    Viz 4.2: Ring with all positive edges - complete propagation.

    6-node ring: All edges positive

    Scapegoat: N0
    Accuser: N3

    Propagation goes both directions around ring
    Result: Everyone joins
    """
    print("\n" + "="*70)
    print("VIZ 4.2: Ring All Positive - Complete Propagation")
    print("="*70)

    nodes = [f'N{i}' for i in range(6)]
    graph = SignedGraph()

    for node in nodes:
        graph.add_node(node)

    # Ring edges - ALL positive
    for i in range(len(nodes)):
        graph.add_edge(nodes[i], nodes[(i+1) % len(nodes)], 1)

    scapegoat = 'N0'
    initial_accuser = 'N3'

    # Ensure connected
    if not graph.has_edge(initial_accuser, scapegoat):
        graph.add_edge(initial_accuser, scapegoat, 1)

    print(f"\nScapegoat: {scapegoat}")
    print(f"Accuser: {initial_accuser}")
    print(f"Structure: 6-node ring with ALL positive edges")
    print(f"Prediction: Complete propagation in both directions")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, initial_accuser)

    # Create circular layout
    positions = vu.circular_layout(nodes, radius=1.5)

    # Generate animation frames
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
            if current_graph.has_edge(decision.node, scapegoat):
                current_graph.flip_edge(decision.node, scapegoat)
            else:
                current_graph.add_edge(decision.node, scapegoat, -1)
        elif decision.action == 'defend':
            current_defenders.add(decision.node)

        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    # Final state (hold)
    for _ in range(5):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/requirements/ring_all_positive.gif'

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=2
    )

    mob_size = len(result.accusers) - 1
    total = len(nodes) - 1

    print(f"\n✓ Animation saved: {output_path}")
    print(f"  Mob: {mob_size}/{total} joined ({100*mob_size/total:.0f}%)")
    print(f"  → Complete unity achieved")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser


def generate_ring_comparison():
    """
    Viz 4.3: Side-by-side comparison.

    Shows the dramatic difference one negative edge makes.
    """
    print("\n" + "="*70)
    print("VIZ 4.3: Negative Edge Comparison")
    print("="*70)

    # Scenario 1: Ring with negative edge
    nodes1 = [f'N{i}' for i in range(6)]
    graph1 = SignedGraph()
    for node in nodes1:
        graph1.add_node(node)
    for i in range(len(nodes1)):
        if i == 2:
            graph1.add_edge(nodes1[i], nodes1[(i+1) % len(nodes1)], -1)
        else:
            graph1.add_edge(nodes1[i], nodes1[(i+1) % len(nodes1)], 1)
    # Ensure connected
    if not graph1.has_edge('N3', 'N0'):
        graph1.add_edge('N3', 'N0', 1)

    sim1 = MimeticContagionSimulator(graph1, verbose=False)
    result1 = sim1.introduce_accusation('N0', 'N3')
    pos1 = vu.circular_layout(nodes1, radius=1.5)

    # Scenario 2: Ring all positive
    nodes2 = [f'N{i}' for i in range(6)]
    graph2 = SignedGraph()
    for node in nodes2:
        graph2.add_node(node)
    for i in range(len(nodes2)):
        graph2.add_edge(nodes2[i], nodes2[(i+1) % len(nodes2)], 1)
    # Ensure accuser and scapegoat are connected
    if not graph2.has_edge('N3', 'N0'):
        graph2.add_edge('N3', 'N0', 1)

    sim2 = MimeticContagionSimulator(graph2, verbose=False)
    result2 = sim2.introduce_accusation('N0', 'N3')
    pos2 = vu.circular_layout(nodes2, radius=1.5)

    # Create comparison
    images_data = [
        (result1.final_state, pos1, set(result1.accusers), set(), 'N0', 'N3'),
        (result2.final_state, pos2, set(result2.accusers), set(), 'N0', 'N3'),
    ]

    mob1 = len(result1.accusers) - 1
    total1 = len(nodes1) - 1
    mob2 = len(result2.accusers) - 1
    total2 = len(nodes2) - 1

    titles = [
        f"Ring with Negative Edge (N2—N3)\nMob: {mob1}/{total1} joined ({100*mob1/total1:.0f}%)\n→ BLOCKED",
        f"Ring All Positive\nMob: {mob2}/{total2} joined ({100*mob2/total2:.0f}%)\n→ COMPLETE UNITY"
    ]

    output_path = 'output/requirements/ring_comparison.png'

    vu.create_comparison_grid(images_data, output_path, titles)

    print(f"\n✓ Comparison saved: {output_path}")
    print(f"\n  With negative edge: {mob1}/{total1} ({100*mob1/total1:.0f}%)")
    print(f"  All positive: {mob2}/{total2} ({100*mob2/total2:.0f}%)")
    print(f"\n  → Key insight: Negative edges block information propagation")


def main():
    """Generate all requirements visualizations."""
    print("\n" + "#"*70)
    print("# GRAPH REQUIREMENTS VISUALIZATIONS")
    print("# Key Insight: Negative Edges Block Propagation")
    print("#"*70)

    # Create output directory
    os.makedirs('output/requirements', exist_ok=True)

    # Generate visualizations
    generate_ring_with_negative()
    generate_ring_all_positive()
    generate_ring_comparison()

    print("\n" + "="*70)
    print("✓ ALL REQUIREMENTS VISUALIZATIONS COMPLETE")
    print("="*70)
    print(f"\nOutput directory: output/requirements/")
    print(f"Generated files:")
    print(f"  - ring_negative_edge.gif (shows blocking)")
    print(f"  - ring_all_positive.gif (shows success)")
    print(f"  - ring_comparison.png (side-by-side)")
    print(f"\n→ Key finding: Negative edges block scapegoating propagation")

    return 0


if __name__ == '__main__':
    sys.exit(main())
