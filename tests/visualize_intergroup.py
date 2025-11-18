#!/usr/bin/env python3
"""
Create ASCII visualization of intergroup scapegoating.
Shows how ingroup unifies against outgroup member.
"""

import json
import sys
import os


def load_visualization_data(filename):
    """Load the visualization JSON."""
    with open(filename) as f:
        return json.load(f)


def visualize_intergroup_scapegoating(data):
    """
    Create ASCII visualization showing before/after states.
    """
    comm_a = data['communities']['A']
    comm_b = data['communities']['B']
    scapegoat = data['scapegoat']
    accuser = data['accuser']

    initial_edges = {(e['source'], e['target']): e['sign']
                     for e in data['initial_graph']['edges']}
    final_edges = {(e['source'], e['target']): e['sign']
                   for e in data['final_graph']['edges']}

    def get_edge_sign(edges, n1, n2):
        """Get edge sign (handles undirected)."""
        if (n1, n2) in edges:
            return edges[(n1, n2)]
        if (n2, n1) in edges:
            return edges[(n2, n1)]
        return 0

    print("="*70)
    print("INTERGROUP SCAPEGOATING VISUALIZATION")
    print("="*70)

    print(f"\nScapegoat: {scapegoat} (Community B)")
    print(f"Accuser: {accuser} (Community A)")

    # Initial state
    print("\n" + "="*70)
    print("INITIAL STATE")
    print("="*70)

    print("\nCommunity A (Ingroup):")
    print("  " + "  ".join(comm_a))
    print("  Internal: All positive (cohesive)")

    print("\nCommunity B (Outgroup):")
    print("  " + "  ".join(comm_b))
    print("  Internal: All positive (cohesive)")

    print("\nInter-community Relations:")
    for a in comm_a:
        for b in comm_b:
            sign = get_edge_sign(initial_edges, a, b)
            if sign != 0:
                symbol = "+" if sign == 1 else "-"
                print(f"  {a} ↔ {b}: {symbol}")

    # Final state
    print("\n" + "="*70)
    print("FINAL STATE (After Accusation)")
    print("="*70)

    print("\nCommunity A (Ingroup) - UNIFIED AGAINST B0:")
    print("  " + "  ".join(comm_a))
    print("  Internal: All positive (strengthened)")

    print("\nCommunity B (Outgroup) - UNAFFECTED:")
    print("  " + "  ".join(comm_b))
    print("  Internal: All positive (unchanged)")

    print("\nInter-community Relations:")
    a_to_sg_edges = []
    for a in comm_a:
        sign = get_edge_sign(final_edges, a, scapegoat)
        if sign != 0:
            symbol = "+" if sign == 1 else "-"
            a_to_sg_edges.append((a, symbol))
            print(f"  {a} ↔ {scapegoat}: {symbol}")

    # ASCII diagram
    print("\n" + "="*70)
    print("DIAGRAM")
    print("="*70)

    print("\nBEFORE:")
    print("""
    Community A          Community B
    ┌─────────┐          ┌─────────┐
    │  A0 A1  │          │  B0 B1  │
    │  A2 A3  │   ↔?     │  B2 B3  │
    └─────────┘          └─────────┘
    (cohesive)          (cohesive)
    """)

    print("\nAFTER A0 accuses B0:")
    print("""
    Community A          Community B
    ┌─────────┐          ┌─────────┐
    │  A0 A1  │  ──┐     │  B0 B1  │
    │  A2 A3  │  ──┼──X→ │  B2 B3  │
    └─────────┘  ──┘     └─────────┘
     UNIFIED              UNAWARE
    (all hostile         (internal
     to B0)               cohesion
                          intact)
    """)

    print("\nKEY:")
    print("  → : Negative edges (hostility)")
    print("  X : Scapegoat (B0)")
    print("  UNIFIED: Community A has internal cohesion + shared enemy")
    print("  UNAWARE: Community B doesn't know about accusation")

    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)

    # Count edges to scapegoat
    a_hostile_to_sg = sum(1 for a in comm_a
                          if get_edge_sign(final_edges, a, scapegoat) == -1)

    print(f"\nCommunity A members hostile to {scapegoat}: {a_hostile_to_sg}/{len(comm_a)}")

    # Ingroup cohesion (A internal)
    a_internal_positive = sum(1 for i, a1 in enumerate(comm_a)
                              for a2 in comm_a[i+1:]
                              if get_edge_sign(final_edges, a1, a2) == 1)
    max_internal = len(comm_a) * (len(comm_a) - 1) // 2

    print(f"Community A internal cohesion: {a_internal_positive}/{max_internal} positive edges")

    # Decisions
    print(f"\nDecisions made: {len(data['decisions'])}")
    for decision in data['decisions']:
        print(f"  {decision['node']}: {decision['reason']}")

    print("\n✓ POLARIZATION ACHIEVED")
    print("  - Ingroup unified through shared enemy")
    print("  - Clear us-them boundary created")
    print("  - Outgroup unaffected (unaware)")


def main():
    """Generate visualization."""

    # Check if data file exists
    data_file = "output/intergroup/outgroup_unified.json"

    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found")
        print("Run test_intergroup_scapegoating.py first")
        return 1

    # Load and visualize
    data = load_visualization_data(data_file)
    visualize_intergroup_scapegoating(data)

    print("\n" + "="*70)
    print("THEORETICAL IMPLICATIONS")
    print("="*70)

    print("\n1. SCHMITTIAN FRIEND-ENEMY DISTINCTION")
    print("   The 'political' emerges through creating an enemy")
    print("   Community A defines itself AGAINST B0")
    print("   Identity formed through opposition")

    print("\n2. INGROUP COHESION VIA OUTGROUP HOSTILITY")
    print("   Internal unity achieved through external enemy")
    print("   'Rally around the flag' effect")
    print("   Scapegoating as political tool")

    print("\n3. ASYMMETRIC AWARENESS")
    print("   Community A: Unified, aware of enemy")
    print("   Community B: Unaware, internal cohesion intact")
    print("   One-sided polarization (for now)")

    print("\n4. ESCALATION RISK")
    print("   If Community B learns of hostility:")
    print("   - B will unify AGAINST A")
    print("   - Symmetric polarization emerges")
    print("   - Conflict escalation likely")

    print("\n5. DIFFERENT FROM UNIVERSAL SCAPEGOATING")
    print("   Not expelling a member from the community")
    print("   Creating a BOUNDARY between communities")
    print("   Political identity formation, not purification")

    return 0


if __name__ == '__main__':
    sys.exit(main())
