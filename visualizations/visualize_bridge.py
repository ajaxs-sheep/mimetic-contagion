#!/usr/bin/env python3
"""
Generate bridge dynamics visualizations.

Demonstrates why bridge nodes make terrible scapegoats - they fragment the network.

Creates:
1. Simple 3-node chain - bridge blocks information
2. Two communities with bridge - network fragmentation
3. Comparison: bridge vs non-bridge scapegoat
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
import viz_utils as vu


def generate_3node_chain():
    """
    Viz 3.1: Simple 3-node chain A -- B -- C.

    When B (bridge) is scapegoated, C becomes unreachable.
    Information barrier demonstrated.
    """
    print("\n" + "="*70)
    print("VIZ 3.1: 3-Node Chain - Bridge Blocks Information")
    print("="*70)

    # Create chain
    nodes = ['A', 'B', 'C']
    graph = vu.create_chain_graph(nodes)

    scapegoat = 'B'
    initial_accuser = 'A'

    print(f"\nScapegoat: {scapegoat} (bridge connecting A and C)")
    print(f"Accuser: {initial_accuser}")
    print(f"Structure: Linear chain A—B—C")
    print(f"\nPrediction: C will never hear (information blocked)")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, initial_accuser)

    # Create linear layout
    positions = vu.linear_layout(nodes, spacing=2.0, horizontal=True)

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
            current_graph.add_edge(decision.node, scapegoat, -1)
        elif decision.action == 'defend':
            current_defenders.add(decision.node)

        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    # Final state (hold)
    for _ in range(5):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/bridge/3node_chain.gif'
    os.makedirs('output/bridge', exist_ok=True)

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=2
    )

    print(f"\n✓ Animation saved: {output_path}")
    print(f"  Accusers: {len(result.accusers)-1}/{len(nodes)-1}")
    print(f"  C unreachable: {'Yes' if 'C' not in result.accusers else 'No'}")
    print(f"  → Bridge scapegoating creates information barrier")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser


def generate_two_communities_bridge():
    """
    Viz 3.2: Two 3-node communities connected by single bridge.

    Communities: ABC and DEF, bridge C↔D
    When C is scapegoated, DEF never hears.
    """
    print("\n" + "="*70)
    print("VIZ 3.2: Two Communities Bridge - Network Fragmentation")
    print("="*70)

    # Create two communities
    comm_a = ['A', 'B', 'C']
    comm_b = ['D', 'E', 'F']
    nodes = comm_a + comm_b

    graph = SignedGraph()
    for node in nodes:
        graph.add_node(node)

    # Community A (complete)
    graph.add_edge('A', 'B', 1)
    graph.add_edge('A', 'C', 1)
    graph.add_edge('B', 'C', 1)

    # Community B (complete)
    graph.add_edge('D', 'E', 1)
    graph.add_edge('D', 'F', 1)
    graph.add_edge('E', 'F', 1)

    # Bridge
    graph.add_edge('C', 'D', 1)

    scapegoat = 'C'
    initial_accuser = 'A'

    communities = {'A': comm_a, 'B': comm_b}

    print(f"\nScapegoat: {scapegoat} (bridge node)")
    print(f"Accuser: {initial_accuser} (in community A)")
    print(f"Structure: Two 3-node communities, single bridge C↔D")
    print(f"\nPrediction: Community B (DEF) will never hear")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, initial_accuser)

    # Create clear bridge layout
    # Community A (left triangle): A at top, B at bottom, C at right (bridge endpoint)
    # Community B (right triangle): D at left (bridge endpoint), E at top, F at bottom
    positions = {
        'A': (-2.5, 0.5),
        'B': (-2.5, -0.5),
        'C': (-1.0, 0.0),  # Bridge node on right side of comm A
        'D': (1.0, 0.0),   # Bridge node on left side of comm B
        'E': (2.5, 0.5),
        'F': (2.5, -0.5),
    }

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
            current_graph.add_edge(decision.node, scapegoat, -1)
        elif decision.action == 'defend':
            current_defenders.add(decision.node)

        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    # Final state (hold)
    for _ in range(5):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/bridge/two_communities.gif'

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=2,
        communities=communities
    )

    print(f"\n✓ Animation saved: {output_path}")

    a_accusers = [n for n in comm_a if n in result.accusers and n != scapegoat]
    b_accusers = [n for n in comm_b if n in result.accusers]

    print(f"  Community A accusers: {len(a_accusers)}/{len(comm_a)-1}")
    print(f"  Community B accusers: {len(b_accusers)}/{len(comm_b)} (should be 0)")
    print(f"  → Network fragmented, global unity FAILED")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser, communities


def generate_bridge_comparison():
    """
    Viz 3.3: Comparison - bridge vs non-bridge scapegoat.

    Same two-community structure, different scapegoat:
    - Left: C (bridge) as scapegoat → fragmentation
    - Right: B (non-bridge) as scapegoat → success
    """
    print("\n" + "="*70)
    print("VIZ 3.3: Bridge vs Non-Bridge Scapegoat Comparison")
    print("="*70)

    # Create two communities (same structure)
    comm_a = ['A', 'B', 'C']
    comm_b = ['D', 'E', 'F']

    # Scenario 1: Bridge as scapegoat
    graph1 = SignedGraph()
    for node in comm_a + comm_b:
        graph1.add_node(node)

    graph1.add_edge('A', 'B', 1)
    graph1.add_edge('A', 'C', 1)
    graph1.add_edge('B', 'C', 1)
    graph1.add_edge('D', 'E', 1)
    graph1.add_edge('D', 'F', 1)
    graph1.add_edge('E', 'F', 1)
    graph1.add_edge('C', 'D', 1)

    result1 = MimeticContagionSimulator(graph1, verbose=False).introduce_accusation('C', 'A')

    # Scenario 2: Non-bridge as scapegoat
    graph2 = SignedGraph()
    for node in comm_a + comm_b:
        graph2.add_node(node)

    graph2.add_edge('A', 'B', 1)
    graph2.add_edge('A', 'C', 1)
    graph2.add_edge('B', 'C', 1)
    graph2.add_edge('D', 'E', 1)
    graph2.add_edge('D', 'F', 1)
    graph2.add_edge('E', 'F', 1)
    graph2.add_edge('C', 'D', 1)

    result2 = MimeticContagionSimulator(graph2, verbose=False).introduce_accusation('B', 'A')

    # Clear bridge layout - same as two_communities visualization
    positions = {
        'A': (-2.5, 0.5),
        'B': (-2.5, -0.5),
        'C': (-1.0, 0.0),  # Bridge node on right side of comm A
        'D': (1.0, 0.0),   # Bridge node on left side of comm B
        'E': (2.5, 0.5),
        'F': (2.5, -0.5),
    }

    images_data = [
        (result1.final_state, positions, set(result1.accusers), set(), 'C', 'A'),
        (result2.final_state, positions, set(result2.accusers), set(), 'B', 'A'),
    ]

    acc1 = len(result1.accusers) - 1
    total1 = len(graph1.nodes) - 1
    acc2 = len(result2.accusers) - 1
    total2 = len(graph2.nodes) - 1

    titles = [
        f"Bridge as Scapegoat (C)\nAccusers: {acc1}/{total1} ({100*acc1/total1:.0f}%)\n→ FRAGMENTATION",
        f"Non-Bridge as Scapegoat (B)\nAccusers: {acc2}/{total2} ({100*acc2/total2:.0f}%)\n→ GLOBAL UNITY"
    ]

    output_path = 'output/bridge/comparison.png'

    vu.create_comparison_grid(images_data, output_path, titles)

    print(f"\n✓ Comparison saved: {output_path}")
    print(f"\n  Bridge scapegoat: {acc1}/{total1} unity ({100*acc1/total1:.0f}%)")
    print(f"  Non-bridge scapegoat: {acc2}/{total2} unity ({100*acc2/total2:.0f}%)")
    print(f"  → Non-bridge is {acc2/acc1:.1f}x more effective")


def main():
    """Generate all bridge dynamics visualizations."""
    print("\n" + "#"*70)
    print("# BRIDGE DYNAMICS VISUALIZATIONS")
    print("#"*70)

    # Create output directory
    os.makedirs('output/bridge', exist_ok=True)

    # Generate visualizations
    generate_3node_chain()
    generate_two_communities_bridge()
    generate_bridge_comparison()

    print("\n" + "="*70)
    print("✓ ALL BRIDGE VISUALIZATIONS COMPLETE")
    print("="*70)
    print(f"\nOutput directory: output/bridge/")
    print(f"Generated files:")
    print(f"  - 3node_chain.gif (information barrier)")
    print(f"  - two_communities.gif (network fragmentation)")
    print(f"  - comparison.png (bridge vs non-bridge)")
    print(f"\n→ Bridge nodes make terrible scapegoats: they fragment networks")

    return 0


if __name__ == '__main__':
    sys.exit(main())
