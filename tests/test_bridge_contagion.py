#!/usr/bin/env python3
"""
Test contagion spreading across community boundaries via friendship bridges.

Question: If Community A and B are mostly isolated but have ONE friendship bridge,
does the scapegoating accusation spread from A to B through that bridge?

Energy Analysis: Track the number of edge flips required as contagion spreads
within vs across communities.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
import json


def create_two_communities_with_bridge(
    size_a=6,
    size_b=6,
    p_internal_positive=0.9,  # 10% internal negative
    bridge_node_a='A2',  # Middle node in A
    bridge_node_b='B3',  # Middle node in B
    seed=42
):
    """
    Create two communities with single friendship bridge.

    Communities are mostly cohesive (90% positive internal edges).
    One positive edge connects them (the bridge).
    """
    import random
    random.seed(seed)

    graph = SignedGraph()

    # Create communities
    comm_a = [f'A{i}' for i in range(size_a)]
    comm_b = [f'B{i}' for i in range(size_b)]

    for node in comm_a + comm_b:
        graph.add_node(node)

    # Internal edges for A (mostly positive, some negative)
    for i, n1 in enumerate(comm_a):
        for n2 in comm_a[i+1:]:
            sign = 1 if random.random() < p_internal_positive else -1
            graph.add_edge(n1, n2, sign)

    # Internal edges for B (mostly positive, some negative)
    for i, n1 in enumerate(comm_b):
        for n2 in comm_b[i+1:]:
            sign = 1 if random.random() < p_internal_positive else -1
            graph.add_edge(n1, n2, sign)

    # Add THE BRIDGE (single friendship between communities)
    graph.add_edge(bridge_node_a, bridge_node_b, 1)

    return graph, comm_a, comm_b, bridge_node_a, bridge_node_b


def add_accuser_scapegoat_edge(graph, accuser, scapegoat, sign=1):
    """Add initial edge between accuser and scapegoat if it doesn't exist."""
    if not graph.has_edge(accuser, scapegoat):
        graph.add_edge(accuser, scapegoat, sign)


def track_edge_flips_by_community(initial_graph, final_graph, comm_a, comm_b):
    """
    Track edge flips within A, within B, and across A-B.

    Returns dict with counts and lists of flipped edges.
    """
    flips = {
        'within_A': [],
        'within_B': [],
        'across_AB': [],
        'total': 0
    }

    # Check all possible edges
    all_nodes = list(initial_graph.nodes)

    for i, n1 in enumerate(all_nodes):
        for n2 in all_nodes[i+1:]:
            initial_sign = initial_graph.get_edge(n1, n2)
            final_sign = final_graph.get_edge(n1, n2)

            if initial_sign != final_sign:
                # Edge flipped
                flip_info = {
                    'edge': (n1, n2),
                    'from': initial_sign,
                    'to': final_sign
                }

                # Categorize flip
                n1_in_a = n1 in comm_a
                n1_in_b = n1 in comm_b
                n2_in_a = n2 in comm_a
                n2_in_b = n2 in comm_b

                if n1_in_a and n2_in_a:
                    flips['within_A'].append(flip_info)
                elif n1_in_b and n2_in_b:
                    flips['within_B'].append(flip_info)
                elif (n1_in_a and n2_in_b) or (n1_in_b and n2_in_a):
                    flips['across_AB'].append(flip_info)

    flips['total'] = len(flips['within_A']) + len(flips['within_B']) + len(flips['across_AB'])

    return flips


def test_bridge_allows_contagion():
    """
    Test 1: Does single friendship bridge allow contagion to spread from A to B?

    Setup:
    - Community A: 6 members, 90% positive internal
    - Community B: 6 members, 90% positive internal
    - Bridge: A2 ↔ B3 (friends)
    - Scapegoat: B0 (peripheral member of B)
    - Accuser: A0 (member of A)

    Prediction:
    1. A0 accuses B0 (cross-community)
    2. Accusation spreads through A (all of A hears)
    3. A2 (bridge node) hears about B0
    4. A2 tells B3 (via friendship bridge)
    5. B3 hears accusation, turns against B0
    6. Accusation spreads through B (all of B hears)
    7. RESULT: Both communities unified against B0
    """
    print("="*70)
    print("TEST 1: SINGLE FRIENDSHIP BRIDGE ALLOWS CONTAGION")
    print("="*70)

    graph, comm_a, comm_b, bridge_a, bridge_b = create_two_communities_with_bridge(
        size_a=6,
        size_b=6,
        p_internal_positive=0.9,
        bridge_node_a='A2',
        bridge_node_b='B3',
        seed=42
    )

    scapegoat = 'B0'  # Peripheral member of B
    accuser = 'A0'    # Member of A

    print(f"\nSetup:")
    print(f"  Community A: {len(comm_a)} members")
    print(f"  Community B: {len(comm_b)} members")
    print(f"  Bridge: {bridge_a} ↔ {bridge_b} (friendship)")
    print(f"  Scapegoat: {scapegoat} (Community B)")
    print(f"  Accuser: {accuser} (Community A)")

    # Add accuser-scapegoat edge if needed (positive initially, will flip)
    add_accuser_scapegoat_edge(graph, accuser, scapegoat, 1)

    # Initial state
    initial_graph = graph.copy()

    # Count initial edges
    a_internal_pos = sum(1 for i, n1 in enumerate(comm_a)
                         for n2 in comm_a[i+1:]
                         if graph.get_edge(n1, n2) == 1)
    a_internal_neg = sum(1 for i, n1 in enumerate(comm_a)
                         for n2 in comm_a[i+1:]
                         if graph.get_edge(n1, n2) == -1)

    b_internal_pos = sum(1 for i, n1 in enumerate(comm_b)
                         for n2 in comm_b[i+1:]
                         if graph.get_edge(n1, n2) == 1)
    b_internal_neg = sum(1 for i, n1 in enumerate(comm_b)
                         for n2 in comm_b[i+1:]
                         if graph.get_edge(n1, n2) == -1)

    print(f"\nInitial State:")
    print(f"  Community A internal: {a_internal_pos} positive, {a_internal_neg} negative")
    print(f"  Community B internal: {b_internal_pos} positive, {b_internal_neg} negative")
    print(f"  Inter-community: 1 bridge ({bridge_a} ↔ {bridge_b})")

    print(f"\nPrediction:")
    print(f"  1. {accuser} accuses {scapegoat}")
    print(f"  2. Accusation spreads through Community A")
    print(f"  3. {bridge_a} (bridge) hears, turns against {scapegoat}")
    print(f"  4. {bridge_a} tells {bridge_b} via friendship bridge")
    print(f"  5. Accusation spreads through Community B")
    print(f"  6. BOTH communities unified against {scapegoat}")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, accuser)

    # Count who turned against scapegoat
    final_graph = result.final_state
    a_against_sg = sum(1 for a in comm_a if final_graph.get_edge(a, scapegoat) == -1)
    b_against_sg = sum(1 for b in comm_b if b != scapegoat and final_graph.get_edge(b, scapegoat) == -1)

    print(f"\n" + "="*70)
    print("RESULTS")
    print("="*70)

    print(f"\nCommunity A members hostile to {scapegoat}: {a_against_sg}/{len(comm_a)}")
    print(f"Community B members hostile to {scapegoat}: {b_against_sg}/{len(comm_b)-1}")

    # Track edge flips
    flips = track_edge_flips_by_community(initial_graph, final_graph, comm_a, comm_b)

    print(f"\nEdge Flips (Energy Cost):")
    print(f"  Within Community A: {len(flips['within_A'])} flips")
    print(f"  Within Community B: {len(flips['within_B'])} flips")
    print(f"  Across A-B boundary: {len(flips['across_AB'])} flips")
    print(f"  TOTAL: {flips['total']} flips")

    # Check if contagion crossed the bridge
    bridge_crossed = b_against_sg > 0

    if bridge_crossed:
        print(f"\n✓ CONTAGION CROSSED THE BRIDGE")
        print(f"  Single friendship bridge WAS sufficient")
        print(f"  Both communities affected")
    else:
        print(f"\n✗ CONTAGION STOPPED AT BRIDGE")
        print(f"  Single friendship bridge was NOT sufficient")
        print(f"  Only Community A affected")

    # Detailed flip analysis
    print(f"\n" + "="*70)
    print("DETAILED FLIP ANALYSIS")
    print("="*70)

    print(f"\nFlips within Community A:")
    for flip in flips['within_A'][:5]:  # Show first 5
        e = flip['edge']
        print(f"  {e[0]} ↔ {e[1]}: {flip['from']:+d} → {flip['to']:+d}")
    if len(flips['within_A']) > 5:
        print(f"  ... and {len(flips['within_A'])-5} more")

    print(f"\nFlips within Community B:")
    for flip in flips['within_B'][:5]:
        e = flip['edge']
        print(f"  {e[0]} ↔ {e[1]}: {flip['from']:+d} → {flip['to']:+d}")
    if len(flips['within_B']) > 5:
        print(f"  ... and {len(flips['within_B'])-5} more")

    print(f"\nFlips across A-B boundary:")
    for flip in flips['across_AB']:
        e = flip['edge']
        print(f"  {e[0]} ↔ {e[1]}: {flip['from']:+d} → {flip['to']:+d}")

    return {
        'bridge_crossed': bridge_crossed,
        'flips': flips,
        'a_unified': a_against_sg == len(comm_a),
        'b_unified': b_against_sg == len(comm_b) - 1,
        'result': result
    }


def test_energy_cost_by_scapegoat_position():
    """
    Test 2: Energy cost depends on scapegoat's position in B.

    Compare:
    - Peripheral scapegoat (B0): Few edges to flip in B
    - Hub scapegoat (B_central): Many edges to flip in B

    Hypothesis: Hub scapegoat requires MORE edge flips (higher energy).
    """
    print("\n" + "="*70)
    print("TEST 2: ENERGY COST BY SCAPEGOAT POSITION")
    print("="*70)

    results = {}

    for scapegoat_type, scapegoat in [('Peripheral', 'B0'), ('Hub', 'B2')]:
        print(f"\n--- Scapegoat: {scapegoat} ({scapegoat_type}) ---")

        graph, comm_a, comm_b, bridge_a, bridge_b = create_two_communities_with_bridge(
            size_a=6,
            size_b=6,
            p_internal_positive=0.9,
            bridge_node_a='A2',
            bridge_node_b='B3',
            seed=42
        )

        accuser = 'A0'

        # Add accuser-scapegoat edge
        add_accuser_scapegoat_edge(graph, accuser, scapegoat, 1)

        # Initial state
        initial_graph = graph.copy()

        # Run simulation
        simulator = MimeticContagionSimulator(graph, verbose=False)
        result = simulator.introduce_accusation(scapegoat, accuser)
        final_graph = result.final_state

        # Track flips
        flips = track_edge_flips_by_community(initial_graph, final_graph, comm_a, comm_b)

        # Count unified
        a_against_sg = sum(1 for a in comm_a if final_graph.get_edge(a, scapegoat) == -1)
        b_against_sg = sum(1 for b in comm_b if b != scapegoat and final_graph.get_edge(b, scapegoat) == -1)

        print(f"  Community A hostile to {scapegoat}: {a_against_sg}/{len(comm_a)}")
        print(f"  Community B hostile to {scapegoat}: {b_against_sg}/{len(comm_b)-1}")
        print(f"  Edge flips in A: {len(flips['within_A'])}")
        print(f"  Edge flips in B: {len(flips['within_B'])}")
        print(f"  Edge flips across AB: {len(flips['across_AB'])}")
        print(f"  TOTAL flips: {flips['total']}")

        results[scapegoat_type] = {
            'scapegoat': scapegoat,
            'flips_A': len(flips['within_A']),
            'flips_B': len(flips['within_B']),
            'flips_AB': len(flips['across_AB']),
            'total_flips': flips['total'],
            'a_unified': a_against_sg,
            'b_unified': b_against_sg
        }

    print(f"\n" + "="*70)
    print("ENERGY COMPARISON")
    print("="*70)

    print(f"\nPeripheral Scapegoat (B0):")
    print(f"  Total flips: {results['Peripheral']['total_flips']}")
    print(f"  In Community B: {results['Peripheral']['flips_B']}")

    print(f"\nHub Scapegoat (B2):")
    print(f"  Total flips: {results['Hub']['total_flips']}")
    print(f"  In Community B: {results['Hub']['flips_B']}")

    energy_diff = results['Hub']['total_flips'] - results['Peripheral']['total_flips']

    if energy_diff > 0:
        print(f"\n✓ Hub requires MORE energy: +{energy_diff} flips")
        print(f"  Hub scapegoat has more connections to flip")
    elif energy_diff < 0:
        print(f"\n✗ Hub requires LESS energy: {energy_diff} flips")
    else:
        print(f"\n= Same energy cost")

    return results


def test_phase_transition_at_boundary():
    """
    Test 3: Does energy cost spike when contagion crosses A-B boundary?

    Track cumulative edge flips over time (BFS steps).
    Hypothesis: Sharp increase when contagion enters Community B.
    """
    print("\n" + "="*70)
    print("TEST 3: PHASE TRANSITION AT COMMUNITY BOUNDARY")
    print("="*70)

    graph, comm_a, comm_b, bridge_a, bridge_b = create_two_communities_with_bridge(
        size_a=6,
        size_b=6,
        p_internal_positive=0.9,
        bridge_node_a='A2',
        bridge_node_b='B3',
        seed=42
    )

    scapegoat = 'B0'
    accuser = 'A0'

    print(f"\nScapegoat: {scapegoat} (Community B)")
    print(f"Accuser: {accuser} (Community A)")
    print(f"Bridge: {bridge_a} ↔ {bridge_b}")

    # Add accuser-scapegoat edge
    add_accuser_scapegoat_edge(graph, accuser, scapegoat, 1)

    # Run simulation and track step-by-step flips
    initial_graph = graph.copy()
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, accuser)

    # Reconstruct flip timeline from decisions
    print(f"\n" + "="*70)
    print("FLIP TIMELINE")
    print("="*70)

    cumulative_flips = 0
    flips_in_a = 0
    flips_in_b = 0
    flips_across = 0

    for i, decision in enumerate(result.decisions):
        node = decision.node
        action = decision.action

        if action in ['join_accusers', 'hear_accusation']:
            # Node turned against scapegoat
            edge = decision.edge_flipped
            if edge:
                n1, n2 = edge

                # Categorize flip
                n1_in_a = n1 in comm_a
                n1_in_b = n1 in comm_b
                n2_in_a = n2 in comm_a
                n2_in_b = n2 in comm_b

                if (n1_in_a and n2_in_b) or (n1_in_b and n2_in_a):
                    flips_across += 1
                    category = "ACROSS"
                elif n1_in_a and n2_in_a:
                    flips_in_a += 1
                    category = "within A"
                elif n1_in_b and n2_in_b:
                    flips_in_b += 1
                    category = "within B"

                cumulative_flips += 1

                node_community = "A" if node in comm_a else "B"

                print(f"Step {i+1}: {node} (Community {node_community}) - {category}")
                print(f"  Cumulative flips: {cumulative_flips} (A:{flips_in_a}, B:{flips_in_b}, AB:{flips_across})")

                # Check if this is the bridge crossing
                if node == bridge_b or (node in comm_b and flips_in_b == 1):
                    print(f"  >>> CONTAGION ENTERED COMMUNITY B <<<")

    print(f"\n" + "="*70)
    print("PHASE ANALYSIS")
    print("="*70)

    print(f"\nPhase 1 (Within Community A): {flips_in_a} flips")
    print(f"Phase 2 (Across boundary): {flips_across} flips")
    print(f"Phase 3 (Within Community B): {flips_in_b} flips")

    if flips_in_b > 0:
        ratio = flips_in_b / flips_in_a if flips_in_a > 0 else float('inf')
        print(f"\nEnergy ratio (B/A): {ratio:.2f}")

        if ratio > 1.5:
            print(f"✓ PHASE TRANSITION DETECTED")
            print(f"  Community B required {ratio:.1f}x more flips per member")
        else:
            print(f"= Similar energy cost in both communities")


def main():
    """Run all bridge contagion tests."""

    print("="*70)
    print("BRIDGE CONTAGION AND ENERGY ANALYSIS")
    print("="*70)
    print("\nQuestion: Does single friendship bridge allow contagion to spread?")
    print("Analysis: Track 'energy cost' (edge flips) within vs across communities")
    print()

    # Test 1: Does bridge allow contagion?
    result1 = test_bridge_allows_contagion()

    # Test 2: Energy cost by scapegoat position
    result2 = test_energy_cost_by_scapegoat_position()

    # Test 3: Phase transition at boundary
    test_phase_transition_at_boundary()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"\n1. SINGLE BRIDGE SUFFICIENCY:")
    if result1['bridge_crossed']:
        print(f"   ✓ Single friendship bridge IS sufficient")
        print(f"   Contagion spreads from A to B via bridge")
    else:
        print(f"   ✗ Single friendship bridge NOT sufficient")
        print(f"   Contagion contained within A")

    print(f"\n2. ENERGY COST:")
    print(f"   Total flips: {result1['flips']['total']}")
    print(f"   Within A: {len(result1['flips']['within_A'])}")
    print(f"   Within B: {len(result1['flips']['within_B'])}")
    print(f"   Across boundary: {len(result1['flips']['across_AB'])}")

    print(f"\n3. POSITION MATTERS:")
    if result2:
        hub_energy = result2['Hub']['total_flips']
        periph_energy = result2['Peripheral']['total_flips']
        print(f"   Hub scapegoat: {hub_energy} flips")
        print(f"   Peripheral scapegoat: {periph_energy} flips")
        if hub_energy > periph_energy:
            print(f"   ✓ Hub requires more energy (+{hub_energy - periph_energy})")

    return 0


if __name__ == '__main__':
    sys.exit(main())
