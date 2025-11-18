#!/usr/bin/env python3
"""
Test escalatory cycle between two communities with loyalty.

Models the classic feud pattern:
1. Community A accuses member of Community B
2. Community B defends their member (loyalty, no defection)
3. Community B retaliates by accusing member of Community A
4. Community A defends their member (loyalty)
5. Result: Mutual polarization (A vs B)

This is the Montagues vs Capulets / Hatfields vs McCoys pattern.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graph import SignedGraph
from src.simulator_with_loyalty import LoyaltySimulator
import json


def create_two_communities_complete(size_a=6, size_b=6, bridge_count=1, seed=42):
    """
    Create two fully cohesive communities with bridges.

    Both communities are complete positive graphs (everyone friends).
    Bridges connect random members across communities.
    """
    import random
    random.seed(seed)

    graph = SignedGraph()

    comm_a = [f'A{i}' for i in range(size_a)]
    comm_b = [f'B{i}' for i in range(size_b)]

    for node in comm_a + comm_b:
        graph.add_node(node)

    # Community A: complete positive
    for i, n1 in enumerate(comm_a):
        for n2 in comm_a[i+1:]:
            graph.add_edge(n1, n2, 1)

    # Community B: complete positive
    for i, n1 in enumerate(comm_b):
        for n2 in comm_b[i+1:]:
            graph.add_edge(n1, n2, 1)

    # Bridges
    bridges = []
    for _ in range(bridge_count):
        a_node = random.choice(comm_a)
        b_node = random.choice(comm_b)
        if not graph.has_edge(a_node, b_node):
            graph.add_edge(a_node, b_node, 1)
            bridges.append((a_node, b_node))

    communities = {'A': comm_a, 'B': comm_b}

    return graph, communities, bridges


def run_escalation_cycle(size_a=6, size_b=6, bridge_count=1, seed=42):
    """
    Run complete escalation cycle.

    Phase 1: A0 accuses B0
    - A unifies against B0
    - B defends B0 (loyalty)

    Phase 2: B detects attack, retaliates
    - B1 accuses A1
    - B unifies against A1
    - A defends A1 (loyalty)

    Result: Mutual polarization
    """
    print("="*70)
    print("ESCALATION CYCLE: TWO COMMUNITIES WITH LOYALTY")
    print("="*70)

    # Create initial graph
    graph, communities, bridges = create_two_communities_complete(
        size_a, size_b, bridge_count, seed
    )

    print(f"\nInitial Setup:")
    print(f"  Community A: {communities['A']}")
    print(f"  Community B: {communities['B']}")
    print(f"  Bridges: {bridges}")

    # Count initial edges
    initial_edges = {
        'A_internal': sum(1 for i, n1 in enumerate(communities['A'])
                          for n2 in communities['A'][i+1:]
                          if graph.get_edge(n1, n2) == 1),
        'B_internal': sum(1 for i, n1 in enumerate(communities['B'])
                          for n2 in communities['B'][i+1:]
                          if graph.get_edge(n1, n2) == 1),
        'AB_cross': len(bridges)
    }

    print(f"\n  Initial edges:")
    print(f"    A internal: {initial_edges['A_internal']} (all positive)")
    print(f"    B internal: {initial_edges['B_internal']} (all positive)")
    print(f"    A-B cross: {initial_edges['AB_cross']} (bridges)")

    # ==================== PHASE 1: A accuses B ====================
    print(f"\n" + "="*70)
    print("PHASE 1: Community A accuses member of Community B")
    print("="*70)

    scapegoat_b = 'B0'  # Community B member
    accuser_a = 'A0'    # Community A member

    # Ensure they know each other
    if not graph.has_edge(accuser_a, scapegoat_b):
        graph.add_edge(accuser_a, scapegoat_b, 1)

    print(f"\n{accuser_a} (Community A) accuses {scapegoat_b} (Community B)")

    # Save phase 1 initial state
    phase1_initial = graph.copy()

    # Run phase 1 with loyalty
    simulator1 = LoyaltySimulator(graph, communities, verbose=False)
    result1 = simulator1.introduce_accusation(scapegoat_b, accuser_a)

    # Analyze phase 1 results
    a_accusers = [n for n in communities['A'] if n in result1.accusers]
    b_defenders = [n for n in communities['B'] if n != scapegoat_b and n not in result1.accusers]
    b_defectors = [n for n in communities['B'] if n != scapegoat_b and n in result1.accusers]

    print(f"\nPhase 1 Results:")
    print(f"  Community A accusers: {a_accusers} ({len(a_accusers)}/{len(communities['A'])})")
    print(f"  Community B defenders: {b_defenders} ({len(b_defenders)}/{len(communities['B'])-1})")
    print(f"  Community B defectors: {b_defectors} ({len(b_defectors)}/{len(communities['B'])-1})")

    if b_defenders:
        print(f"\n  ✓ LOYALTY CONFIRMED: Community B defended {scapegoat_b}")
    else:
        print(f"\n  ✗ NO LOYALTY: Community B defected")

    phase1_graph = result1.final_state

    # ==================== PHASE 2: B retaliates ====================
    print(f"\n" + "="*70)
    print("PHASE 2: Community B retaliates")
    print("="*70)

    # B learns about the attack through bridge
    # B chooses to retaliate by scapegoating an A member

    scapegoat_a = 'A1'  # Community A member (different from accuser)
    retaliator_b = 'B1'  # Community B member (different from original scapegoat)

    # Ensure they know each other
    if not phase1_graph.has_edge(retaliator_b, scapegoat_a):
        phase1_graph.add_edge(retaliator_b, scapegoat_a, 1)

    print(f"\n{retaliator_b} (Community B) retaliates against {scapegoat_a} (Community A)")
    print(f"  Motivation: Defending {scapegoat_b}, punishing Community A")

    # Run phase 2 with loyalty
    simulator2 = LoyaltySimulator(phase1_graph, communities, verbose=False)
    result2 = simulator2.introduce_accusation(scapegoat_a, retaliator_b)

    # Analyze phase 2 results
    b_accusers = [n for n in communities['B'] if n in result2.accusers]
    a_defenders = [n for n in communities['A'] if n != scapegoat_a and n not in result2.accusers]
    a_defectors = [n for n in communities['A'] if n != scapegoat_a and n in result2.accusers]

    print(f"\nPhase 2 Results:")
    print(f"  Community B accusers: {b_accusers} ({len(b_accusers)}/{len(communities['B'])})")
    print(f"  Community A defenders: {a_defenders} ({len(a_defenders)}/{len(communities['A'])-1})")
    print(f"  Community A defectors: {a_defectors} ({len(a_defectors)}/{len(communities['A'])-1})")

    if a_defenders:
        print(f"\n  ✓ LOYALTY CONFIRMED: Community A defended {scapegoat_a}")
    else:
        print(f"\n  ✗ NO LOYALTY: Community A defected")

    phase2_graph = result2.final_state

    # ==================== FINAL ANALYSIS ====================
    print(f"\n" + "="*70)
    print("FINAL STATE: MUTUAL POLARIZATION")
    print("="*70)

    # Compute inter-community hostility
    a_hostile_to_b = sum(
        1 for a in communities['A'] for b in communities['B']
        if phase2_graph.get_edge(a, b) == -1
    )

    b_hostile_to_a = sum(
        1 for b in communities['B'] for a in communities['A']
        if phase2_graph.get_edge(b, a) == -1
    )

    max_possible = len(communities['A']) * len(communities['B'])

    print(f"\nInter-community hostility:")
    print(f"  A hostile to B: {a_hostile_to_b}/{max_possible} edges ({100*a_hostile_to_b/max_possible:.1f}%)")
    print(f"  B hostile to A: {b_hostile_to_a}/{max_possible} edges ({100*b_hostile_to_a/max_possible:.1f}%)")

    # Check if bridges survived
    bridges_intact = sum(
        1 for (a, b) in bridges
        if phase2_graph.has_edge(a, b) and phase2_graph.get_edge(a, b) == 1
    )

    bridges_broken = len(bridges) - bridges_intact

    print(f"\nBridge status:")
    print(f"  Intact: {bridges_intact}/{len(bridges)}")
    print(f"  Broken: {bridges_broken}/{len(bridges)}")

    # Check internal unity
    a_internal_pos = sum(1 for i, n1 in enumerate(communities['A'])
                         for n2 in communities['A'][i+1:]
                         if phase2_graph.get_edge(n1, n2) == 1)
    b_internal_pos = sum(1 for i, n1 in enumerate(communities['B'])
                         for n2 in communities['B'][i+1:]
                         if phase2_graph.get_edge(n1, n2) == 1)

    print(f"\nInternal cohesion:")
    print(f"  Community A: {a_internal_pos}/{initial_edges['A_internal']} positive edges")
    print(f"  Community B: {b_internal_pos}/{initial_edges['B_internal']} positive edges")

    # Interpret results
    print(f"\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

    mutual_polarization = (a_hostile_to_b > 0 and b_hostile_to_a > 0)

    if mutual_polarization:
        print(f"\n✓ MUTUAL POLARIZATION ACHIEVED")
        print(f"  - Both communities hostile to each other")
        print(f"  - Escalatory cycle complete")
        print(f"  - Classic feud pattern (Montagues vs Capulets)")
    else:
        print(f"\n✗ NO MUTUAL POLARIZATION")
        print(f"  - One or both communities not hostile")

    if b_defenders and a_defenders:
        print(f"\n✓ LOYALTY PREVENTED TOTAL SCAPEGOATING")
        print(f"  - Community B defended {scapegoat_b}")
        print(f"  - Community A defended {scapegoat_a}")
        print(f"  - No defection occurred")
        print(f"  - Result: A vs B (not all vs one)")
    else:
        print(f"\n✗ DEFECTION OCCURRED")
        print(f"  - One or both communities failed to defend members")

    # Return complete data
    return {
        'initial': {
            'graph': phase1_initial.to_dict(),
            'communities': communities,
            'bridges': bridges
        },
        'phase1': {
            'accuser': accuser_a,
            'scapegoat': scapegoat_b,
            'a_accusers': a_accusers,
            'b_defenders': b_defenders,
            'b_defectors': b_defectors,
            'result': result1,
            'graph': phase1_graph.to_dict()
        },
        'phase2': {
            'retaliator': retaliator_b,
            'scapegoat': scapegoat_a,
            'b_accusers': b_accusers,
            'a_defenders': a_defenders,
            'a_defectors': a_defectors,
            'result': result2,
            'graph': phase2_graph.to_dict()
        },
        'final': {
            'a_hostile_to_b': a_hostile_to_b,
            'b_hostile_to_a': b_hostile_to_a,
            'bridges_intact': bridges_intact,
            'bridges_broken': bridges_broken,
            'a_internal_cohesion': a_internal_pos,
            'b_internal_cohesion': b_internal_pos,
            'mutual_polarization': mutual_polarization
        }
    }


def main():
    """Run escalation cycle test."""

    # Make output directory
    os.makedirs('output/escalation', exist_ok=True)

    # Run test
    data = run_escalation_cycle(size_a=6, size_b=6, bridge_count=1, seed=42)

    # Save data
    output_file = 'output/escalation/escalation_cycle_data.json'

    # Convert ScapegoatResult objects to dicts
    output_data = {
        'initial': data['initial'],
        'phase1': {
            'accuser': data['phase1']['accuser'],
            'scapegoat': data['phase1']['scapegoat'],
            'a_accusers': data['phase1']['a_accusers'],
            'b_defenders': data['phase1']['b_defenders'],
            'b_defectors': data['phase1']['b_defectors'],
            'graph': data['phase1']['graph'],
            'decisions': [d.to_dict() for d in data['phase1']['result'].decisions]
        },
        'phase2': {
            'retaliator': data['phase2']['retaliator'],
            'scapegoat': data['phase2']['scapegoat'],
            'b_accusers': data['phase2']['b_accusers'],
            'a_defenders': data['phase2']['a_defenders'],
            'a_defectors': data['phase2']['a_defectors'],
            'graph': data['phase2']['graph'],
            'decisions': [d.to_dict() for d in data['phase2']['result'].decisions]
        },
        'final': data['final']
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n\nData saved to: {output_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
