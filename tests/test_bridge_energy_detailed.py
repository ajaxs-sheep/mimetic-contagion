#!/usr/bin/env python3
"""
Detailed energy analysis of bridge contagion with realistic communities.

Tests fragmented communities (internal conflicts, partial connectivity)
and tracks edge CREATIONS vs FLIPS separately to understand true energy costs.

Key questions:
1. How much energy is creating new edges vs flipping existing ones?
2. Does internal fragmentation increase total energy cost?
3. Are there cascading flips WITHIN communities (not just to scapegoat)?
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
import random


def create_realistic_communities_with_bridge(
    size_a=8,
    size_b=8,
    p_connected_a=0.4,      # 40% of possible edges exist in A
    p_connected_b=0.4,      # 40% of possible edges exist in B
    p_positive_a=0.7,       # 70% of existing edges in A are positive
    p_positive_b=0.7,       # 70% of existing edges in B are positive
    bridge_count=1,         # Number of bridges
    min_degree=2,           # Ensure connectivity (at least 2 positive edges per node)
    seed=42
):
    """
    Create realistic fragmented communities with bridge.

    - Partial connectivity (not complete graphs)
    - Mix of positive and negative edges (internal conflicts)
    - Guaranteed connected via positive edges (min_degree)
    - Single bridge between communities
    """
    random.seed(seed)
    graph = SignedGraph()

    comm_a = [f'A{i}' for i in range(size_a)]
    comm_b = [f'B{i}' for i in range(size_b)]

    for node in comm_a + comm_b:
        graph.add_node(node)

    def add_community_edges(community, p_connected, p_positive):
        """Add edges within a community with partial connectivity."""
        # First pass: random edges
        for i, n1 in enumerate(community):
            for n2 in community[i+1:]:
                if random.random() < p_connected:
                    sign = 1 if random.random() < p_positive else -1
                    graph.add_edge(n1, n2, sign)

        # Second pass: ensure min_degree positive edges for connectivity
        for node in community:
            positive_neighbors = [n for n in community
                                  if n != node and graph.get_edge(node, n) == 1]

            while len(positive_neighbors) < min_degree:
                # Add a positive edge to a random other node
                candidates = [n for n in community
                              if n != node and graph.get_edge(node, n) == 0]
                if not candidates:
                    break  # Can't add more

                new_friend = random.choice(candidates)
                graph.add_edge(node, new_friend, 1)
                positive_neighbors.append(new_friend)

    # Create communities
    add_community_edges(comm_a, p_connected_a, p_positive_a)
    add_community_edges(comm_b, p_connected_b, p_positive_b)

    # Add bridges
    bridges = []
    for _ in range(bridge_count):
        a_node = random.choice(comm_a)
        b_node = random.choice(comm_b)

        if not graph.has_edge(a_node, b_node):
            graph.add_edge(a_node, b_node, 1)
            bridges.append((a_node, b_node))

    return graph, comm_a, comm_b, bridges


def analyze_energy_detailed(initial_graph, final_graph, comm_a, comm_b, scapegoat):
    """
    Detailed energy analysis: track creations vs flips, within vs across communities.

    Returns dict with:
    - creations: edges that went from 0 to +/-1
    - flips: edges that changed sign (+1 to -1 or vice versa)
    - strengthening: edges that went from -1 to +1 (enemy to friend)
    - weakening: edges that went from +1 to -1 (friend to enemy)
    """
    energy = {
        'total_changes': 0,
        'within_A': {'creations': [], 'flips': [], 'total': 0},
        'within_B': {'creations': [], 'flips': [], 'total': 0},
        'across_AB': {'creations': [], 'flips': [], 'total': 0},
        'to_scapegoat': {'creations': [], 'flips': [], 'total': 0},
        'internal_cascade': {'creations': [], 'flips': [], 'total': 0}
    }

    all_nodes = list(initial_graph.nodes)

    for i, n1 in enumerate(all_nodes):
        for n2 in all_nodes[i+1:]:
            initial_sign = initial_graph.get_edge(n1, n2)
            final_sign = final_graph.get_edge(n1, n2)

            if initial_sign == final_sign:
                continue  # No change

            # Categorize change
            change_info = {
                'edge': (n1, n2),
                'from': initial_sign,
                'to': final_sign,
                'type': None
            }

            # Creation or flip?
            if initial_sign == 0:
                change_info['type'] = 'creation'
            else:
                change_info['type'] = 'flip'

            # Location categorization
            n1_in_a = n1 in comm_a
            n1_in_b = n1 in comm_b
            n2_in_a = n2 in comm_a
            n2_in_b = n2 in comm_b

            involves_scapegoat = (n1 == scapegoat or n2 == scapegoat)

            # Categorize by location
            if involves_scapegoat:
                # Edge to/from scapegoat
                energy['to_scapegoat'][change_info['type'] + 's'].append(change_info)
                energy['to_scapegoat']['total'] += 1
            elif n1_in_a and n2_in_a:
                # Within A (internal cascade)
                energy['within_A'][change_info['type'] + 's'].append(change_info)
                energy['within_A']['total'] += 1
                energy['internal_cascade'][change_info['type'] + 's'].append(change_info)
                energy['internal_cascade']['total'] += 1
            elif n1_in_b and n2_in_b:
                # Within B (internal cascade)
                energy['within_B'][change_info['type'] + 's'].append(change_info)
                energy['within_B']['total'] += 1
                energy['internal_cascade'][change_info['type'] + 's'].append(change_info)
                energy['internal_cascade']['total'] += 1
            elif (n1_in_a and n2_in_b) or (n1_in_b and n2_in_a):
                # Across boundary (not involving scapegoat directly)
                energy['across_AB'][change_info['type'] + 's'].append(change_info)
                energy['across_AB']['total'] += 1

    energy['total_changes'] = sum(cat['total'] for cat in
                                   [energy['within_A'], energy['within_B'],
                                    energy['across_AB'], energy['to_scapegoat']])

    return energy


def count_graph_stats(graph, comm_a, comm_b):
    """Count edges and nodes for statistics."""
    stats = {
        'nodes': len(graph.nodes),
        'edges': {'total': 0, 'positive': 0, 'negative': 0},
        'A_internal': {'total': 0, 'positive': 0, 'negative': 0},
        'B_internal': {'total': 0, 'positive': 0, 'negative': 0},
        'AB_cross': {'total': 0, 'positive': 0, 'negative': 0}
    }

    all_nodes = list(graph.nodes)
    for i, n1 in enumerate(all_nodes):
        for n2 in all_nodes[i+1:]:
            sign = graph.get_edge(n1, n2)
            if sign == 0:
                continue

            stats['edges']['total'] += 1
            if sign == 1:
                stats['edges']['positive'] += 1
            else:
                stats['edges']['negative'] += 1

            # Categorize by location
            n1_in_a = n1 in comm_a
            n2_in_a = n2 in comm_a
            n1_in_b = n1 in comm_b
            n2_in_b = n2 in comm_b

            if n1_in_a and n2_in_a:
                stats['A_internal']['total'] += 1
                if sign == 1:
                    stats['A_internal']['positive'] += 1
                else:
                    stats['A_internal']['negative'] += 1
            elif n1_in_b and n2_in_b:
                stats['B_internal']['total'] += 1
                if sign == 1:
                    stats['B_internal']['positive'] += 1
                else:
                    stats['B_internal']['negative'] += 1
            elif (n1_in_a and n2_in_b) or (n1_in_b and n2_in_a):
                stats['AB_cross']['total'] += 1
                if sign == 1:
                    stats['AB_cross']['positive'] += 1
                else:
                    stats['AB_cross']['negative'] += 1

    return stats


def test_realistic_bridge_contagion():
    """
    Test bridge contagion with realistic fragmented communities.

    Key features:
    - Partial connectivity (not everyone knows everyone)
    - Internal conflicts (negative edges within communities)
    - Track creations vs flips separately
    - Identify internal cascades (friendships forming within communities)
    """
    print("="*70)
    print("REALISTIC BRIDGE CONTAGION: DETAILED ENERGY ANALYSIS")
    print("="*70)

    graph, comm_a, comm_b, bridges = create_realistic_communities_with_bridge(
        size_a=8,
        size_b=8,
        p_connected_a=0.4,      # Sparse (40% connectivity)
        p_connected_b=0.4,
        p_positive_a=0.7,       # 70% positive, 30% negative (internal conflicts)
        p_positive_b=0.7,
        bridge_count=1,
        min_degree=2,
        seed=42
    )

    scapegoat = 'B0'  # Member of Community B
    accuser = 'A0'    # Member of Community A

    # Ensure accuser-scapegoat edge exists
    if not graph.has_edge(accuser, scapegoat):
        graph.add_edge(accuser, scapegoat, 1)

    print(f"\nSetup:")
    print(f"  Community A: {len(comm_a)} members (fragmented)")
    print(f"  Community B: {len(comm_b)} members (fragmented)")
    print(f"  Bridges: {len(bridges)} friendship(s) - {bridges}")
    print(f"  Scapegoat: {scapegoat} (Community B)")
    print(f"  Accuser: {accuser} (Community A)")

    # Initial stats
    initial_stats = count_graph_stats(graph, comm_a, comm_b)

    print(f"\nInitial Graph Structure:")
    print(f"  Total nodes: {initial_stats['nodes']}")
    print(f"  Total edges: {initial_stats['edges']['total']} " +
          f"({initial_stats['edges']['positive']} positive, " +
          f"{initial_stats['edges']['negative']} negative)")

    print(f"\n  Community A internal:")
    print(f"    Edges: {initial_stats['A_internal']['total']} " +
          f"({initial_stats['A_internal']['positive']}+, " +
          f"{initial_stats['A_internal']['negative']}-)")
    pct_pos_a = 100 * initial_stats['A_internal']['positive'] / initial_stats['A_internal']['total'] if initial_stats['A_internal']['total'] > 0 else 0
    print(f"    Positivity: {pct_pos_a:.1f}% (internal conflicts exist)")

    print(f"\n  Community B internal:")
    print(f"    Edges: {initial_stats['B_internal']['total']} " +
          f"({initial_stats['B_internal']['positive']}+, " +
          f"{initial_stats['B_internal']['negative']}-)")
    pct_pos_b = 100 * initial_stats['B_internal']['positive'] / initial_stats['B_internal']['total'] if initial_stats['B_internal']['total'] > 0 else 0
    print(f"    Positivity: {pct_pos_b:.1f}% (internal conflicts exist)")

    print(f"\n  Cross-community:")
    print(f"    Edges: {initial_stats['AB_cross']['total']} " +
          f"({initial_stats['AB_cross']['positive']}+, " +
          f"{initial_stats['AB_cross']['negative']}-)")

    # Check scapegoat's initial position
    sg_friends_in_b = [n for n in comm_b if n != scapegoat and graph.get_edge(scapegoat, n) == 1]
    sg_enemies_in_b = [n for n in comm_b if n != scapegoat and graph.get_edge(scapegoat, n) == -1]
    sg_unknown_in_b = [n for n in comm_b if n != scapegoat and graph.get_edge(scapegoat, n) == 0]

    print(f"\n  Scapegoat {scapegoat} initial position in Community B:")
    print(f"    Friends: {len(sg_friends_in_b)} {sg_friends_in_b}")
    print(f"    Enemies: {len(sg_enemies_in_b)} {sg_enemies_in_b}")
    print(f"    Unknown: {len(sg_unknown_in_b)} {sg_unknown_in_b}")

    # Save initial state
    initial_graph = graph.copy()

    # Run simulation
    print(f"\n" + "="*70)
    print("RUNNING SIMULATION")
    print("="*70)

    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, accuser)

    # Analyze energy
    energy = analyze_energy_detailed(initial_graph, result.final_state, comm_a, comm_b, scapegoat)

    # Final stats
    final_stats = count_graph_stats(result.final_state, comm_a, comm_b)

    # Results
    print(f"\n" + "="*70)
    print("RESULTS")
    print("="*70)

    # Unification
    a_accusers = [n for n in comm_a if n in result.accusers]
    b_accusers = [n for n in comm_b if n in result.accusers]

    print(f"\nUnification:")
    print(f"  Community A: {len(a_accusers)}/{len(comm_a)} unified against {scapegoat}")
    print(f"  Community B: {len(b_accusers)}/{len(comm_b)-1} unified against {scapegoat}")
    print(f"  Bridge crossed: {len(b_accusers) > 0}")

    # Energy breakdown
    print(f"\n" + "="*70)
    print("DETAILED ENERGY ANALYSIS")
    print("="*70)

    print(f"\nTotal edge changes: {energy['total_changes']}")

    print(f"\n1. EDGES TO/FROM SCAPEGOAT ({energy['to_scapegoat']['total']} changes):")
    print(f"   Creations: {len(energy['to_scapegoat']['creations'])} (new hostility)")
    print(f"   Flips:     {len(energy['to_scapegoat']['flips'])} (broken friendships)")

    if energy['to_scapegoat']['creations']:
        print(f"\n   Created edges to scapegoat:")
        for change in energy['to_scapegoat']['creations'][:5]:
            print(f"     {change['edge'][0]} ↔ {change['edge'][1]}: ∅ → {change['to']:+d}")
        if len(energy['to_scapegoat']['creations']) > 5:
            print(f"     ... and {len(energy['to_scapegoat']['creations'])-5} more")

    if energy['to_scapegoat']['flips']:
        print(f"\n   Flipped edges to scapegoat:")
        for change in energy['to_scapegoat']['flips'][:5]:
            print(f"     {change['edge'][0]} ↔ {change['edge'][1]}: {change['from']:+d} → {change['to']:+d}")
        if len(energy['to_scapegoat']['flips']) > 5:
            print(f"     ... and {len(energy['to_scapegoat']['flips'])-5} more")

    print(f"\n2. WITHIN COMMUNITY A ({energy['within_A']['total']} changes):")
    print(f"   Creations: {len(energy['within_A']['creations'])} (new friendships)")
    print(f"   Flips:     {len(energy['within_A']['flips'])} (changed relationships)")

    if energy['within_A']['total'] > 0:
        print(f"\n   Internal cascade in A:")
        for change in (energy['within_A']['creations'] + energy['within_A']['flips'])[:3]:
            print(f"     {change['edge'][0]} ↔ {change['edge'][1]}: " +
                  f"{'∅' if change['from'] == 0 else change['from']:+d} → {change['to']:+d} ({change['type']})")

    print(f"\n3. WITHIN COMMUNITY B ({energy['within_B']['total']} changes):")
    print(f"   Creations: {len(energy['within_B']['creations'])} (new friendships)")
    print(f"   Flips:     {len(energy['within_B']['flips'])} (changed relationships)")

    if energy['within_B']['total'] > 0:
        print(f"\n   Internal cascade in B:")
        for change in (energy['within_B']['creations'] + energy['within_B']['flips'])[:3]:
            print(f"     {change['edge'][0]} ↔ {change['edge'][1]}: " +
                  f"{'∅' if change['from'] == 0 else change['from']:+d} → {change['to']:+d} ({change['type']})")

    print(f"\n4. ACROSS COMMUNITIES (not scapegoat) ({energy['across_AB']['total']} changes):")
    print(f"   Creations: {len(energy['across_AB']['creations'])}")
    print(f"   Flips:     {len(energy['across_AB']['flips'])}")

    print(f"\n5. INTERNAL CASCADE TOTAL ({energy['internal_cascade']['total']} changes):")
    print(f"   (Changes within A or B, excluding scapegoat edges)")
    print(f"   Creations: {len(energy['internal_cascade']['creations'])}")
    print(f"   Flips:     {len(energy['internal_cascade']['flips'])}")

    # Energy ratio analysis
    print(f"\n" + "="*70)
    print("ENERGY COST BREAKDOWN")
    print("="*70)

    total_creations = sum(len(energy[cat]['creations']) for cat in
                          ['to_scapegoat', 'within_A', 'within_B', 'across_AB'])
    total_flips = sum(len(energy[cat]['flips']) for cat in
                      ['to_scapegoat', 'within_A', 'within_B', 'across_AB'])

    print(f"\nGlobal breakdown:")
    print(f"  Total creations: {total_creations} (new edges)")
    print(f"  Total flips:     {total_flips} (existing edges changed)")
    print(f"  Ratio:           {total_creations}:{total_flips}")

    if total_creations > 0 or total_flips > 0:
        pct_creations = 100 * total_creations / (total_creations + total_flips)
        pct_flips = 100 * total_flips / (total_creations + total_flips)
        print(f"  Percentages:     {pct_creations:.1f}% creations, {pct_flips:.1f}% flips")

    # Energy by location
    print(f"\nBy location:")
    print(f"  To scapegoat:    {len(energy['to_scapegoat']['creations'])} creations, " +
          f"{len(energy['to_scapegoat']['flips'])} flips")
    print(f"  Within A:        {len(energy['within_A']['creations'])} creations, " +
          f"{len(energy['within_A']['flips'])} flips")
    print(f"  Within B:        {len(energy['within_B']['creations'])} creations, " +
          f"{len(energy['within_B']['flips'])} flips")
    print(f"  Across A-B:      {len(energy['across_AB']['creations'])} creations, " +
          f"{len(energy['across_AB']['flips'])} flips")

    # Interpretation
    print(f"\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

    print(f"\n1. CREATION vs FLIP ENERGY:")
    if total_flips > total_creations:
        print(f"   Most energy went into FLIPPING existing edges ({total_flips}/{total_creations+total_flips})")
        print(f"   → Breaking existing relationships is the 'expensive' operation")
    elif total_creations > total_flips:
        print(f"   Most energy went into CREATING new edges ({total_creations}/{total_creations+total_flips})")
        print(f"   → Forming new hostilities/friendships dominates")
    else:
        print(f"   Equal energy in creations and flips")

    print(f"\n2. SCAPEGOAT-SPECIFIC ENERGY:")
    sg_creations = len(energy['to_scapegoat']['creations'])
    sg_flips = len(energy['to_scapegoat']['flips'])
    print(f"   {sg_creations} new hostile edges to scapegoat (didn't know them before)")
    print(f"   {sg_flips} flipped edges to scapegoat (were friends, now enemies)")

    if sg_flips > 0:
        print(f"   → Scapegoat lost {sg_flips} friendships")
        print(f"   → This represents REAL social cost (breaking bonds)")

    print(f"\n3. INTERNAL CASCADE:")
    internal_total = energy['internal_cascade']['total']
    if internal_total > 0:
        print(f"   {internal_total} changes within communities (excluding scapegoat)")
        print(f"   → Scapegoating triggered internal relationship changes")
        print(f"   → Communities are restructuring around the conflict")
    else:
        print(f"   No internal cascade detected")
        print(f"   → Communities only changed relationships with scapegoat")

    print(f"\n4. CROSS-COMMUNITY DYNAMICS:")
    if energy['across_AB']['total'] > 0:
        print(f"   {energy['across_AB']['total']} changes in A-B relationships (not scapegoat)")
        print(f"   → Communities are polarizing beyond just the scapegoat")
    else:
        print(f"   No changes in A-B relationships (except via scapegoat)")
        print(f"   → Conflict is focused solely on scapegoat")

    return {
        'energy': energy,
        'result': result,
        'initial_stats': initial_stats,
        'final_stats': final_stats,
        'total_creations': total_creations,
        'total_flips': total_flips
    }


def main():
    """Run detailed energy analysis."""
    result = test_realistic_bridge_contagion()

    print(f"\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    energy = result['energy']

    print(f"\nKey Findings:")
    print(f"  1. Bridge contagion: {'SUCCESS' if len([n for n in result['result'].accusers if n.startswith('B')]) > 0 else 'FAILED'}")
    print(f"  2. Total edge changes: {result['energy']['total_changes']}")
    print(f"  3. Creations vs Flips: {result['total_creations']}:{result['total_flips']}")
    print(f"  4. Internal cascade: {result['energy']['internal_cascade']['total']} changes within communities")

    print(f"\nEnergy interpretation:")
    if result['total_flips'] > 0:
        print(f"  - {result['total_flips']} existing relationships destroyed (high cost)")
    if result['total_creations'] > 0:
        print(f"  - {result['total_creations']} new edges created (medium cost)")
    if energy['internal_cascade']['total'] > 0:
        print(f"  - {energy['internal_cascade']['total']} internal restructuring (secondary effects)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
