#!/usr/bin/env python3
"""
Generate scapegoating effort analysis visualizations.

Compares the "effort" required to scapegoat:
1. Peripheral node (outsider, dreg of society) - few connections
2. Central node (king, billionaire, nexus) - highly connected

Key insight: Despite different dynamics, total effort may be similar.
Central requires many flips, peripheral requires many new edge formations.

Creates:
1. Peripheral scenario animation
2. Central scenario animation
3. Side-by-side comparison
4. Effort analysis bar chart
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
import viz_utils as vu
import random
import matplotlib.pyplot as plt
import numpy as np


def create_base_graph(num_nodes=25, avg_degree=4, seed=42):
    """
    Create sparse, fragmented base graph for both scenarios.

    - Some nodes well-connected (local hubs)
    - Some nodes peripheral (1-2 connections)
    - Overall sparse connectivity

    Returns:
        SignedGraph with realistic community structure
    """
    random.seed(seed)
    nodes = [f'N{i}' for i in range(num_nodes)]

    graph = SignedGraph()
    for node in nodes:
        graph.add_node(node)

    # Create ring for basic connectivity
    for i in range(len(nodes)):
        graph.add_edge(nodes[i], nodes[(i+1) % len(nodes)], 1)

    # Add random edges to reach target average degree
    # Each node starts with 2 (from ring), need to add more
    target_edges = int(num_nodes * avg_degree / 2)  # Undirected edges
    current_edges = num_nodes  # Ring edges

    while current_edges < target_edges:
        i = random.randint(0, num_nodes - 1)
        j = random.randint(0, num_nodes - 1)

        if i != j and not graph.has_edge(nodes[i], nodes[j]):
            graph.add_edge(nodes[i], nodes[j], 1)
            current_edges += 1

    return graph


def analyze_scapegoating_cost(graph, scapegoat, initial_accuser):
    """
    Run simulation and analyze the "effort" required.

    Tracks:
    - edge_flips: Existing + edges that became - (changing opinion about friend)
    - edge_creations: New - edges (forming opinion about stranger)
    - befriend_actions: New + edges (resolving conflicts)

    Returns:
        dict with metrics
    """
    # Track initial edges to scapegoat
    initial_connections = set()
    for node in graph.nodes:
        if graph.has_edge(node, scapegoat):
            initial_connections.add(node)

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, initial_accuser)

    # Analyze decisions
    edge_flips = 0
    edge_creations = 0
    befriend_actions = 0

    for decision in result.decisions:
        if decision.action == 'join_accusers':
            # Node was already connected to scapegoat, flipped edge
            edge_flips += 1
        elif decision.action == 'hear_accusation':
            # Node was NOT connected to scapegoat, created new negative edge
            edge_creations += 1
        elif decision.action == 'befriend_other':
            # Resolved --- triangle by befriending
            befriend_actions += 1

    # Simple "effort" - just sum of conversions needed
    total_effort = edge_flips + edge_creations

    return {
        'edge_flips': edge_flips,
        'edge_creations': edge_creations,
        'befriend_actions': befriend_actions,
        'total_effort': total_effort,
        'mob_size': len(result.accusers),
        'total_nodes': len(graph.nodes) - 1,  # Exclude scapegoat
        'success': result.contagion_succeeded,
        'result': result,
    }


def generate_peripheral_scenario():
    """
    Scenario 1: Scapegoating a peripheral node (outsider).

    - Pick node with low degree (1-3 connections)
    - On edge of network
    - Not well-known
    """
    print("\n" + "="*70)
    print("SCENARIO 1: Peripheral Scapegoat (Outsider/Dreg)")
    print("="*70)

    # Create base graph (same 23 nodes as central scenario)
    graph = create_base_graph(num_nodes=23, avg_degree=4, seed=42)

    # Add one peripheral node with minimal connections (degree 1-2)
    peripheral = 'PERIPHERAL'
    graph.add_node(peripheral)

    # Connect peripheral to just 1-2 random nodes (outsider, barely known)
    base_nodes = [n for n in graph.nodes if n != peripheral]
    num_connections = 2  # Very low connectivity
    connected_nodes = random.sample(base_nodes, num_connections)

    for node in connected_nodes:
        graph.add_edge(peripheral, node, 1)

    scapegoat = peripheral

    # Accuser: someone connected to scapegoat
    neighbors = list(graph.neighbors(scapegoat))
    initial_accuser = random.choice(neighbors)

    scapegoat_degree = len(list(graph.neighbors(scapegoat)))

    print(f"\nScapegoat: {scapegoat} (degree: {scapegoat_degree})")
    print(f"Accuser: {initial_accuser}")
    print(f"Structure: Sparse graph, 23 base nodes + peripheral outsider")
    print(f"Peripheral connected to: {num_connections}/{len(base_nodes)} nodes")
    print(f"Prediction: Few flips, many new edges created")

    # Analyze
    metrics = analyze_scapegoating_cost(graph, scapegoat, initial_accuser)

    # Create layout
    positions = vu.force_directed_layout(graph, iterations=100)

    # Generate animation frames
    result = metrics['result']
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
        elif decision.action == 'befriend_other':
            # Befriend action
            if hasattr(decision, 'target_node'):
                current_graph.flip_edge(decision.node, decision.target_node)

        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    # Hold final state
    for _ in range(5):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/effort/peripheral_scapegoat.gif'
    os.makedirs('output/effort', exist_ok=True)

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=1.5
    )

    print(f"\n✓ Animation saved: {output_path}")
    print(f"\n  ANALYSIS:")
    print(f"  Edge flips (+ → -): {metrics['edge_flips']}")
    print(f"  Edge creations (new -): {metrics['edge_creations']}")
    print(f"  Befriend actions (new +): {metrics['befriend_actions']}")
    print(f"  Total conversions: {metrics['total_effort']}")
    print(f"  Mob size: {metrics['mob_size']}/{metrics['total_nodes']} ({100*metrics['mob_size']/metrics['total_nodes']:.0f}%)")
    print(f"  Success: {metrics['success']}")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser, metrics


def generate_central_scenario():
    """
    Scenario 2: Scapegoating a central node (king/billionaire).

    - Highly connected node (everyone knows them)
    - Create 'KING' node connected to ALL base nodes
    - Maximum degree
    """
    print("\n" + "="*70)
    print("SCENARIO 2: Central Scapegoat (King/Billionaire)")
    print("="*70)

    # Create base graph (same seed for fairness)
    graph = create_base_graph(num_nodes=23, avg_degree=4, seed=42)  # 23 + KING = 24

    # Add KING node connected to ALL nodes (everyone knows the king)
    king = 'KING'
    graph.add_node(king)

    base_nodes = [n for n in graph.nodes if n != king]

    # Connect king to ALL base nodes (100% connectivity)
    for node in base_nodes:
        graph.add_edge(king, node, 1)

    scapegoat = king

    # Accuser: random person who knows the king
    neighbors = list(graph.neighbors(king))
    initial_accuser = random.choice(neighbors)

    king_degree = len(list(graph.neighbors(king)))

    print(f"\nScapegoat: {scapegoat} (degree: {king_degree})")
    print(f"Accuser: {initial_accuser}")
    print(f"Structure: Sparse graph + highly connected king")
    print(f"King connected to: ALL {len(base_nodes)} base nodes (100%)")
    print(f"Prediction: All flips, zero new edges created")

    # Analyze
    metrics = analyze_scapegoating_cost(graph, scapegoat, initial_accuser)

    # Create layout - put king in center
    positions = vu.force_directed_layout(graph, iterations=100)

    # Generate animation frames
    result = metrics['result']
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
        elif decision.action == 'befriend_other':
            if hasattr(decision, 'target_node'):
                current_graph.flip_edge(decision.node, decision.target_node)

        graph_states.append((current_graph.copy(), current_accusers.copy(), current_defenders.copy()))

    # Hold final state
    for _ in range(5):
        graph_states.append((result.final_state, set(result.accusers), current_defenders))

    # Create animation
    output_path = 'output/effort/central_scapegoat.gif'

    vu.animate_contagion(
        graph_states=graph_states,
        positions=positions,
        decisions=result.decisions,
        scapegoat=scapegoat,
        initial_accuser=initial_accuser,
        output_path=output_path,
        fps=1.5
    )

    print(f"\n✓ Animation saved: {output_path}")
    print(f"\n  ANALYSIS:")
    print(f"  Edge flips (+ → -): {metrics['edge_flips']}")
    print(f"  Edge creations (new -): {metrics['edge_creations']}")
    print(f"  Befriend actions (new +): {metrics['befriend_actions']}")
    print(f"  Total conversions: {metrics['total_effort']}")
    print(f"  Mob size: {metrics['mob_size']}/{metrics['total_nodes']} ({100*metrics['mob_size']/metrics['total_nodes']:.0f}%)")
    print(f"  Success: {metrics['success']}")

    return result.final_state, positions, set(result.accusers), current_defenders, scapegoat, initial_accuser, metrics


def generate_effort_comparison_chart(peripheral_metrics, central_metrics):
    """
    Create bar chart comparing effort metrics between scenarios.
    """
    print("\n" + "="*70)
    print("EFFORT COMPARISON CHART")
    print("="*70)

    fig, ax = plt.subplots(figsize=(12, 8))

    metrics = ['Edge Flips\n(+ → -)', 'Edge Creations\n(new -)',
               'Befriend Actions\n(new +)', '"Effort"\n(flips + creates)']

    peripheral_values = [
        peripheral_metrics['edge_flips'],
        peripheral_metrics['edge_creations'],
        peripheral_metrics['befriend_actions'],
        peripheral_metrics['total_effort']
    ]

    central_values = [
        central_metrics['edge_flips'],
        central_metrics['edge_creations'],
        central_metrics['befriend_actions'],
        central_metrics['total_effort']
    ]

    x = np.arange(len(metrics))
    width = 0.35

    bars1 = ax.bar(x - width/2, peripheral_values, width, label='Peripheral (Outsider)',
                   color='#3498db', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, central_values, width, label='Central (King)',
                   color='#e74c3c', edgecolor='black', linewidth=1.5)

    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title('Scapegoating Comparison: Peripheral vs Central Target',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add insight text box
    insight_text = "Key Insight:\n"
    insight_text += f"• Peripheral: {peripheral_metrics['edge_flips']} flips, {peripheral_metrics['edge_creations']} creations\n"
    insight_text += f"• Central: {central_metrics['edge_flips']} flips, {central_metrics['edge_creations']} creations\n"
    insight_text += f"• Total: {peripheral_metrics['total_effort']} vs {central_metrics['total_effort']}\n"
    insight_text += f"\n→ Similar totals, opposite dynamics:\n"
    insight_text += f"  Peripheral = many strangers learn about outsider\n"
    insight_text += f"  Central = everyone flips opinion of king"

    ax.text(0.98, 0.97, insight_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9, edgecolor='black', linewidth=2))

    plt.tight_layout()
    output_path = 'output/effort/effort_analysis.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✓ Chart saved: {output_path}")


def generate_comparison_grid(peripheral_data, central_data):
    """
    Side-by-side comparison of final states.
    """
    print("\n" + "="*70)
    print("SIDE-BY-SIDE COMPARISON")
    print("="*70)

    graph_p, pos_p, acc_p, def_p, scape_p, init_p, metrics_p = peripheral_data
    graph_c, pos_c, acc_c, def_c, scape_c, init_c, metrics_c = central_data

    images_data = [
        (graph_p, pos_p, acc_p, def_p, scape_p, init_p),
        (graph_c, pos_c, acc_c, def_c, scape_c, init_c),
    ]

    titles = [
        f"Peripheral Scapegoat\n{metrics_p['mob_size']}/{metrics_p['total_nodes']} joined\n" +
        f"Flips: {metrics_p['edge_flips']}, Creates: {metrics_p['edge_creations']}, Effort: {metrics_p['total_effort']:.1f}",

        f"Central Scapegoat (King)\n{metrics_c['mob_size']}/{metrics_c['total_nodes']} joined\n" +
        f"Flips: {metrics_c['edge_flips']}, Creates: {metrics_c['edge_creations']}, Effort: {metrics_c['total_effort']:.1f}"
    ]

    output_path = 'output/effort/comparison.png'

    vu.create_comparison_grid(images_data, output_path, titles)

    print(f"✓ Comparison saved: {output_path}")


def main():
    """Generate all effort analysis visualizations."""
    print("\n" + "#"*70)
    print("# SCAPEGOATING EFFORT ANALYSIS")
    print("# Comparing Peripheral vs Central Targets")
    print("#"*70)

    os.makedirs('output/effort', exist_ok=True)

    # Generate scenarios
    peripheral_data = generate_peripheral_scenario()
    central_data = generate_central_scenario()

    # Extract metrics
    peripheral_metrics = peripheral_data[6]
    central_metrics = central_data[6]

    # Generate comparisons
    generate_effort_comparison_chart(peripheral_metrics, central_metrics)
    generate_comparison_grid(peripheral_data, central_data)

    print("\n" + "="*70)
    print("✓ ALL EFFORT ANALYSIS VISUALIZATIONS COMPLETE")
    print("="*70)
    print(f"\nOutput directory: output/effort/")
    print(f"Generated files:")
    print(f"  - peripheral_scapegoat.gif (outsider animation)")
    print(f"  - central_scapegoat.gif (king animation)")
    print(f"  - comparison.png (side-by-side final states)")
    print(f"  - effort_analysis.png (bar chart)")

    print(f"\n" + "="*70)
    print("KEY FINDINGS:")
    print("="*70)
    print(f"Peripheral (Outsider):")
    print(f"  - Flips: {peripheral_metrics['edge_flips']}, Creations: {peripheral_metrics['edge_creations']}")
    print(f"  - Total conversions: {peripheral_metrics['total_effort']}")
    print(f"  - Mob: {peripheral_metrics['mob_size']}/{peripheral_metrics['total_nodes']}")

    print(f"\nCentral (King):")
    print(f"  - Flips: {central_metrics['edge_flips']}, Creations: {central_metrics['edge_creations']}")
    print(f"  - Total conversions: {central_metrics['total_effort']}")
    print(f"  - Mob: {central_metrics['mob_size']}/{central_metrics['total_nodes']}")

    print(f"\n→ Nearly identical totals ({peripheral_metrics['total_effort']} vs {central_metrics['total_effort']}), opposite dynamics")

    return 0


if __name__ == '__main__':
    sys.exit(main())
