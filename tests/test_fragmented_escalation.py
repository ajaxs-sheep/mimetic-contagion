#!/usr/bin/env python3
"""
Test escalation with FRAGMENTED communities.

Starting condition: Both A and B have internal conflicts (enemies within)
Process: Escalation cycle with loyalty
Result: Both communities achieve internal unity while becoming hostile to each other

This demonstrates how external conflict unifies internally divided communities.
Classic political pattern: "Nothing unites a people like a common enemy"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graph import SignedGraph
from src.simulator_with_loyalty import LoyaltySimulator
import json


def create_fragmented_communities(size_a=6, size_b=6, bridge_count=1,
                                   p_positive_a=0.7, p_positive_b=0.7, seed=42):
    """
    Create two FRAGMENTED communities with internal conflicts.

    Args:
        size_a, size_b: Community sizes
        bridge_count: Number of cross-community bridges
        p_positive_a, p_positive_b: Probability of positive internal edges
                                     (lower = more internal conflict)
        seed: Random seed
    """
    import random
    random.seed(seed)

    graph = SignedGraph()

    comm_a = [f'A{i}' for i in range(size_a)]
    comm_b = [f'B{i}' for i in range(size_b)]

    for node in comm_a + comm_b:
        graph.add_node(node)

    # Community A: FRAGMENTED (mix of friends and enemies)
    for i, n1 in enumerate(comm_a):
        for n2 in comm_a[i+1:]:
            sign = 1 if random.random() < p_positive_a else -1
            graph.add_edge(n1, n2, sign)

    # Community B: FRAGMENTED (mix of friends and enemies)
    for i, n1 in enumerate(comm_b):
        for n2 in comm_b[i+1:]:
            sign = 1 if random.random() < p_positive_b else -1
            graph.add_edge(n1, n2, sign)

    # Bridges (always positive initially)
    bridges = []
    for _ in range(bridge_count):
        a_node = random.choice(comm_a)
        b_node = random.choice(comm_b)
        if not graph.has_edge(a_node, b_node):
            graph.add_edge(a_node, b_node, 1)
            bridges.append((a_node, b_node))

    communities = {'A': comm_a, 'B': comm_b}

    return graph, communities, bridges


def count_internal_cohesion(graph, community):
    """Count internal positive vs negative edges in community."""
    positive = 0
    negative = 0

    for i, n1 in enumerate(community):
        for n2 in community[i+1:]:
            sign = graph.get_edge(n1, n2)
            if sign == 1:
                positive += 1
            elif sign == -1:
                negative += 1

    total = positive + negative
    return {
        'positive': positive,
        'negative': negative,
        'total': total,
        'percent_positive': 100 * positive / total if total > 0 else 0
    }


def run_fragmented_escalation(size_a=6, size_b=6, bridge_count=1,
                               p_positive_a=0.7, p_positive_b=0.7, seed=42):
    """
    Run escalation cycle with fragmented communities.

    Shows how external conflict unifies internally divided groups.
    """
    print("="*70)
    print("FRAGMENTED ESCALATION: EXTERNAL ENEMIES UNIFY DIVIDED COMMUNITIES")
    print("="*70)

    # Create fragmented initial graph
    graph, communities, bridges = create_fragmented_communities(
        size_a, size_b, bridge_count, p_positive_a, p_positive_b, seed
    )

    print(f"\nInitial Setup:")
    print(f"  Community A: {communities['A']}")
    print(f"  Community B: {communities['B']}")
    print(f"  Bridges: {bridges}")

    # Analyze initial fragmentation
    initial_a_cohesion = count_internal_cohesion(graph, communities['A'])
    initial_b_cohesion = count_internal_cohesion(graph, communities['B'])

    print(f"\n  Community A internal state (FRAGMENTED):")
    print(f"    Positive: {initial_a_cohesion['positive']}/{initial_a_cohesion['total']} " +
          f"({initial_a_cohesion['percent_positive']:.1f}%)")
    print(f"    Negative: {initial_a_cohesion['negative']}/{initial_a_cohesion['total']} " +
          f"({100 - initial_a_cohesion['percent_positive']:.1f}%)")
    print(f"    → Internal enemies exist")

    print(f"\n  Community B internal state (FRAGMENTED):")
    print(f"    Positive: {initial_b_cohesion['positive']}/{initial_b_cohesion['total']} " +
          f"({initial_b_cohesion['percent_positive']:.1f}%)")
    print(f"    Negative: {initial_b_cohesion['negative']}/{initial_b_cohesion['total']} " +
          f"({100 - initial_b_cohesion['percent_positive']:.1f}%)")
    print(f"    → Internal enemies exist")

    # ==================== PHASE 1: A accuses B ====================
    print(f"\n" + "="*70)
    print("PHASE 1: Community A accuses member of Community B")
    print("="*70)

    scapegoat_b = 'B0'
    accuser_a = 'A0'

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

    print(f"\nPhase 1 Results:")
    print(f"  Community A accusers: {len(a_accusers)}/{len(communities['A'])}")
    print(f"  Community B defenders: {len(b_defenders)}/{len(communities['B'])-1}")

    # Check if A unified internally
    phase1_a_cohesion = count_internal_cohesion(result1.final_state, communities['A'])

    print(f"\n  Community A internal cohesion AFTER Phase 1:")
    print(f"    Positive: {phase1_a_cohesion['positive']}/{phase1_a_cohesion['total']} " +
          f"({phase1_a_cohesion['percent_positive']:.1f}%)")
    print(f"    Negative: {phase1_a_cohesion['negative']}/{phase1_a_cohesion['total']} " +
          f"({100 - phase1_a_cohesion['percent_positive']:.1f}%)")

    if phase1_a_cohesion['negative'] < initial_a_cohesion['negative']:
        print(f"    ✓ Internal enemies reconciled ({initial_a_cohesion['negative']} → {phase1_a_cohesion['negative']})")
        print(f"    → Scapegoating unified Community A")
    else:
        print(f"    = No change in internal cohesion")

    phase1_graph = result1.final_state

    # ==================== PHASE 2: B retaliates ====================
    print(f"\n" + "="*70)
    print("PHASE 2: Community B retaliates")
    print("="*70)

    scapegoat_a = 'A1'
    retaliator_b = 'B1'

    if not phase1_graph.has_edge(retaliator_b, scapegoat_a):
        phase1_graph.add_edge(retaliator_b, scapegoat_a, 1)

    print(f"\n{retaliator_b} (Community B) retaliates against {scapegoat_a} (Community A)")

    # Run phase 2 with loyalty
    simulator2 = LoyaltySimulator(phase1_graph, communities, verbose=False)
    result2 = simulator2.introduce_accusation(scapegoat_a, retaliator_b)

    # Analyze phase 2 results
    b_accusers = [n for n in communities['B'] if n in result2.accusers]
    a_defenders = [n for n in communities['A'] if n != scapegoat_a and n not in result2.accusers]

    print(f"\nPhase 2 Results:")
    print(f"  Community B accusers: {len(b_accusers)}/{len(communities['B'])}")
    print(f"  Community A defenders: {len(a_defenders)}/{len(communities['A'])-1}")

    # Check if B unified internally
    phase2_b_cohesion = count_internal_cohesion(result2.final_state, communities['B'])
    phase2_a_cohesion = count_internal_cohesion(result2.final_state, communities['A'])

    print(f"\n  Community B internal cohesion AFTER Phase 2:")
    print(f"    Positive: {phase2_b_cohesion['positive']}/{phase2_b_cohesion['total']} " +
          f"({phase2_b_cohesion['percent_positive']:.1f}%)")
    print(f"    Negative: {phase2_b_cohesion['negative']}/{phase2_b_cohesion['total']} " +
          f"({100 - phase2_b_cohesion['percent_positive']:.1f}%)")

    if phase2_b_cohesion['negative'] < initial_b_cohesion['negative']:
        print(f"    ✓ Internal enemies reconciled ({initial_b_cohesion['negative']} → {phase2_b_cohesion['negative']})")
        print(f"    → Scapegoating unified Community B")
    else:
        print(f"    = No change in internal cohesion")

    phase2_graph = result2.final_state

    # ==================== FINAL ANALYSIS ====================
    print(f"\n" + "="*70)
    print("FINAL STATE: INTERNAL UNITY + EXTERNAL POLARIZATION")
    print("="*70)

    # Inter-community hostility
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

    # Internal cohesion comparison
    print(f"\n" + "="*70)
    print("INTERNAL COHESION: BEFORE vs AFTER")
    print("="*70)

    print(f"\nCommunity A:")
    print(f"  BEFORE: {initial_a_cohesion['positive']}/{initial_a_cohesion['total']} positive " +
          f"({initial_a_cohesion['percent_positive']:.1f}%), " +
          f"{initial_a_cohesion['negative']} enemies")
    print(f"  AFTER:  {phase2_a_cohesion['positive']}/{phase2_a_cohesion['total']} positive " +
          f"({phase2_a_cohesion['percent_positive']:.1f}%), " +
          f"{phase2_a_cohesion['negative']} enemies")

    a_improvement = phase2_a_cohesion['percent_positive'] - initial_a_cohesion['percent_positive']
    if a_improvement > 0:
        print(f"  → Improved by {a_improvement:.1f}% ({initial_a_cohesion['negative'] - phase2_a_cohesion['negative']} enemies reconciled)")

    print(f"\nCommunity B:")
    print(f"  BEFORE: {initial_b_cohesion['positive']}/{initial_b_cohesion['total']} positive " +
          f"({initial_b_cohesion['percent_positive']:.1f}%), " +
          f"{initial_b_cohesion['negative']} enemies")
    print(f"  AFTER:  {phase2_b_cohesion['positive']}/{phase2_b_cohesion['total']} positive " +
          f"({phase2_b_cohesion['percent_positive']:.1f}%), " +
          f"{phase2_b_cohesion['negative']} enemies")

    b_improvement = phase2_b_cohesion['percent_positive'] - initial_b_cohesion['percent_positive']
    if b_improvement > 0:
        print(f"  → Improved by {b_improvement:.1f}% ({initial_b_cohesion['negative'] - phase2_b_cohesion['negative']} enemies reconciled)")

    # Interpretation
    print(f"\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

    both_unified_internally = (
        phase2_a_cohesion['negative'] < initial_a_cohesion['negative'] and
        phase2_b_cohesion['negative'] < initial_b_cohesion['negative']
    )

    mutual_polarization = (a_hostile_to_b > 0 and b_hostile_to_a > 0)

    if both_unified_internally:
        print(f"\n✓ INTERNAL UNIFICATION ACHIEVED")
        print(f"  - Community A reconciled internal enemies (Rule 2: enemy's enemy)")
        print(f"  - Community B reconciled internal enemies")
        print(f"  - Shared external enemy unified each community")
        print(f"  - Classic pattern: 'Nothing unites like a common enemy'")
    else:
        print(f"\n○ PARTIAL INTERNAL UNIFICATION")

    if mutual_polarization:
        print(f"\n✓ MUTUAL POLARIZATION ACHIEVED")
        print(f"  - Both communities hostile to each other")
        print(f"  - Symmetric conflict (A vs B)")
    else:
        print(f"\n○ PARTIAL POLARIZATION")

    if both_unified_internally and mutual_polarization:
        print(f"\n✓✓ COMPLETE TRANSFORMATION:")
        print(f"  BEFORE: Two fragmented communities (internal conflicts)")
        print(f"  AFTER:  Two unified communities (external conflict)")
        print(f"")
        print(f"  Key insight: External conflict resolved internal conflicts")
        print(f"  Political reality: Leaders use external enemies to unify divided populations")

    # Return data
    return {
        'initial': {
            'graph': phase1_initial.to_dict(),
            'communities': communities,
            'bridges': bridges,
            'a_cohesion': initial_a_cohesion,
            'b_cohesion': initial_b_cohesion
        },
        'phase1': {
            'accuser': accuser_a,
            'scapegoat': scapegoat_b,
            'a_accusers': a_accusers,
            'b_defenders': b_defenders,
            'graph': phase1_graph.to_dict(),
            'a_cohesion': phase1_a_cohesion,
            'decisions': [d.to_dict() for d in result1.decisions]
        },
        'phase2': {
            'retaliator': retaliator_b,
            'scapegoat': scapegoat_a,
            'b_accusers': b_accusers,
            'a_defenders': a_defenders,
            'graph': phase2_graph.to_dict(),
            'b_cohesion': phase2_b_cohesion,
            'a_cohesion': phase2_a_cohesion,
            'decisions': [d.to_dict() for d in result2.decisions]
        },
        'final': {
            'a_hostile_to_b': a_hostile_to_b,
            'b_hostile_to_a': b_hostile_to_a,
            'a_cohesion': phase2_a_cohesion,
            'b_cohesion': phase2_b_cohesion,
            'a_improvement': a_improvement,
            'b_improvement': b_improvement,
            'both_unified': both_unified_internally,
            'mutual_polarization': mutual_polarization
        }
    }


def main():
    """Run fragmented escalation test."""

    # Make output directory
    os.makedirs('output/escalation', exist_ok=True)

    # Run test with 70% positive (30% internal conflict)
    print("\n### Test with 70% internal positivity (moderate fragmentation) ###\n")
    data = run_fragmented_escalation(
        size_a=6,
        size_b=6,
        bridge_count=1,
        p_positive_a=0.7,
        p_positive_b=0.7,
        seed=42
    )

    # Save data
    output_file = 'output/escalation/fragmented_escalation_data.json'

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n\nData saved to: {output_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
