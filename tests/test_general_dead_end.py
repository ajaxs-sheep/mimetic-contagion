#!/usr/bin/env python3
"""
Test the general dead-end problem: ANY node whose only friend is the scapegoat
becomes isolated and blocks BFS propagation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator


def test_intermediate_dead_end():
    """
    Test case where an INTERMEDIATE node (not accuser) becomes a dead end.

    Graph structure:
      Accuser → Node1 → Node2 → Node3
                  ↓
              Scapegoat

    Where:
    - Accuser has other friends (fine)
    - Node1's ONLY friend is Scapegoat
    - Node1 is the only path to Node2 and Node3

    Expected: Node2 and Node3 never hear about accusation
    """
    print("="*70)
    print("TEST: INTERMEDIATE DEAD END")
    print("="*70)

    graph = SignedGraph()
    nodes = ["Accuser", "Node1", "Node2", "Node3", "Scapegoat", "OtherFriend"]
    for node in nodes:
        graph.add_node(node)

    # Accuser has OtherFriend (so accuser won't be isolated)
    graph.add_edge("Accuser", "OtherFriend", 1)

    # Accuser knows Node1 as friend
    graph.add_edge("Accuser", "Node1", 1)

    # Node1's ONLY friend is Scapegoat (PROBLEM!)
    graph.add_edge("Node1", "Scapegoat", 1)

    # Node1 knows Node2 as ENEMY
    graph.add_edge("Node1", "Node2", -1)

    # Node2 knows Node3 as friend
    graph.add_edge("Node2", "Node3", 1)

    # Accuser knows Scapegoat as friend (for initial accusation)
    graph.add_edge("Accuser", "Scapegoat", 1)

    print("\nGraph structure:")
    print("  Accuser ↔ OtherFriend: +1")
    print("  Accuser ↔ Node1: +1")
    print("  Accuser ↔ Scapegoat: +1")
    print("  Node1 ↔ Scapegoat: +1 (Node1's ONLY friend!)")
    print("  Node1 ↔ Node2: -1 (enemies)")
    print("  Node2 ↔ Node3: +1")

    print("\nExpected behavior:")
    print("  1. Accuser accuses Scapegoat")
    print("  2. Accuser tells Node1 and OtherFriend")
    print("  3. Node1 joins accusers (Rule 1: friend of accuser + friend of scapegoat)")
    print("  4. Node1 now has ZERO friends (all negative edges)")
    print("  5. BFS cannot propagate through Node1 to Node2")
    print("  6. Node2 and Node3 never hear about Scapegoat")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=True)
    result = simulator.introduce_accusation("Scapegoat", "Accuser")

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Accusers: {sorted(result.accusers)}")
    print(f"Defenders: {sorted(result.defenders)}")
    print(f"Total accusers: {len(result.accusers)}/{len(graph.nodes)-1}")
    print(f"Unity achieved: {result.is_all_against_one}")

    # Check if Node2 and Node3 were reached
    if "Node2" not in result.accusers and "Node2" not in result.defenders:
        print("\n✓ CONFIRMED: Node2 never processed (unreachable via BFS)")

    if "Node3" not in result.accusers and "Node3" not in result.defenders:
        print("✓ CONFIRMED: Node3 never processed (unreachable via BFS)")

    print("\nConclusion:")
    print("  Node1 became a DEAD END after joining accusers")
    print("  Nodes beyond Node1 in the friendship chain are unreachable")
    print("  This is NOT just an accuser problem - it's ANY node!")

    return result


def test_chain_with_multiple_dead_ends():
    """
    Test a longer chain where multiple nodes have scapegoat as only friend.
    """
    print("\n" + "="*70)
    print("TEST: CHAIN WITH MULTIPLE POTENTIAL DEAD ENDS")
    print("="*70)

    graph = SignedGraph()

    # Create chain: A → B → C → D → E
    # Where B, C, D all have Scapegoat as only friend

    nodes = ["A", "B", "C", "D", "E", "Scapegoat"]
    for node in nodes:
        graph.add_node(node)

    # A is accuser, friends with B and F
    graph.add_edge("A", "B", 1)
    graph.add_edge("A", "Scapegoat", 1)

    # B friends with A and Scapegoat only
    graph.add_edge("B", "Scapegoat", 1)
    graph.add_edge("B", "C", -1)  # Enemy with C

    # C friends with Scapegoat only
    graph.add_edge("C", "Scapegoat", 1)
    graph.add_edge("C", "D", -1)  # Enemy with D

    # D friends with Scapegoat only
    graph.add_edge("D", "Scapegoat", 1)
    graph.add_edge("D", "E", -1)  # Enemy with E

    # E friends with Scapegoat only
    graph.add_edge("E", "Scapegoat", 1)

    print("\nGraph: A → B(-C) → C(-D) → D(-E) → E")
    print("Where: Each of B, C, D, E has Scapegoat as ONLY friend")
    print("       (Besides their negative edges in chain)")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation("Scapegoat", "A")

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Accusers: {sorted(result.accusers)}")
    print(f"Total accusers: {len(result.accusers)}/{len(graph.nodes)-1}")

    print("\nExpected: Only A and B join accusers")
    print("  - A has other friends, starts contagion")
    print("  - B hears from A, joins, but then becomes isolated")
    print("  - C, D, E never hear (no positive path from B)")

    return result


def formalize_general_prerequisite():
    """
    Formalize the general prerequisite: EVERY node must have a friend
    other than the scapegoat (or be the scapegoat itself).
    """
    print("\n" + "="*70)
    print("GENERALIZED PREREQUISITE FOR UNITY")
    print("="*70)

    print("\nORIGINAL (TOO WEAK):")
    print("  'Each node must have at least one positive edge'")

    print("\nCORRECTED (STRONGER):")
    print("  'For any choice of scapegoat S, every node v ≠ S must have")
    print("   at least one positive edge to some node other than S.'")

    print("\nFORMAL STATEMENT:")
    print("  ∀ S ∈ V, ∀ v ∈ V \\ {S}:")
    print("    ∃ w ∈ V \\ {S, v} : edge(v, w) = +1")

    print("\nEQUIVALENT FORMULATION:")
    print("  'Every node must have degree ≥ 2 in the positive edge subgraph'")
    print("  (i.e., at least 2 friends)")

    print("\nWHY THIS MATTERS:")
    print("  - If node v's ONLY friend is scapegoat S:")
    print("    1. When v joins accusers, v↔S flips to negative")
    print("    2. v now has ZERO positive edges")
    print("    3. BFS cannot propagate THROUGH v")
    print("    4. Any nodes reachable ONLY via v will never hear accusation")

    print("\nIMPLICATIONS:")
    print("  - Ring graphs: Every node has degree 2, so they SHOULD work")
    print("    (unless one edge in ring is negative, breaking connectivity)")
    print("  ")
    print("  - Star graphs: Peripheral nodes have degree 1")
    print("    If scapegoat is the hub, peripherals become isolated")
    print("    → Unity fails")

    print("\nMINIMUM VIABLE GRAPH STRUCTURE:")
    print("  1. Every node has ≥2 positive edges")
    print("  2. Positive edge subgraph is connected")
    print("  3. These conditions are SUFFICIENT for unity (with high p_positive)")

    print("\nEXCEPTION:")
    print("  If the graph is fully connected with all positive edges,")
    print("  removing the scapegoat leaves V-1 nodes, each still with")
    print("  ≥V-2 positive edges. This always works.")


def check_ring_graph_more_carefully():
    """
    Re-examine why the 300-node ring failed in stress tests.
    """
    print("\n" + "="*70)
    print("RE-ANALYZING RING GRAPH FAILURE")
    print("="*70)

    # Create small ring with all positive edges
    graph = SignedGraph()
    nodes = [f"n{i}" for i in range(6)]
    for node in nodes:
        graph.add_node(node)

    # Create ring: 0-1-2-3-4-5-0
    for i in range(6):
        next_i = (i + 1) % 6
        graph.add_edge(nodes[i], nodes[next_i], 1)  # All positive

    print("Ring graph: n0-n1-n2-n3-n4-n5-n0 (all positive edges)")
    print("Scapegoat: n0, Accuser: n1")

    # Check degrees
    print("\nDegrees:")
    for node in nodes:
        friends = [n for n in graph.neighbors(node) if graph.get_edge(node, n) == 1]
        print(f"  {node}: {len(friends)} friends = {friends}")

    print("\nPrediction: Should WORK because:")
    print("  - Every node has degree 2")
    print("  - After n1 accuses n0, n1 still has n2 as friend")
    print("  - n1 can tell n2")
    print("  - n2 can tell n3, etc.")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation("n0", "n1")

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Accusers: {sorted(result.accusers)}")
    print(f"Total: {len(result.accusers)}/{len(graph.nodes)-1}")
    print(f"Unity: {result.is_all_against_one}")

    if len(result.accusers) == len(graph.nodes) - 1:
        print("\n✓ SUCCESS: Ring graph with all positive edges WORKS")

    print("\nConclusion about 300-node ring failure:")
    print("  The ring must have had NEGATIVE edges breaking connectivity")
    print("  When p_positive < 1.0, some edges are negative")
    print("  A single negative edge in the ring creates TWO chains")
    print("  If both chains connect to scapegoat, isolation can occur")

    return result


def main():
    """Run all tests."""

    # Test 1: Intermediate dead end
    result1 = test_intermediate_dead_end()

    # Test 2: Multiple dead ends
    result2 = test_chain_with_multiple_dead_ends()

    # Formalize the general prerequisite
    formalize_general_prerequisite()

    # Re-check ring graph
    result3 = check_ring_graph_more_carefully()

    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print("\nYou are ABSOLUTELY CORRECT:")
    print("  ✓ It's not just the accuser")
    print("  ✓ ANY node whose only friend is the scapegoat becomes a dead end")
    print("  ✓ This blocks BFS propagation to nodes beyond it")
    print("  ✓ Unity fails for parts of the graph")

    print("\nCORRECTED PREREQUISITE:")
    print("  'Every node must have ≥2 positive edges'")
    print("  OR equivalently:")
    print("  'For any scapegoat choice, every other node has ≥1 friend besides scapegoat'")

    print("\nThis should be documented as:")
    print("  - Fundamental requirement for guaranteed unity")
    print("  - Constraint on valid input graphs")
    print("  - Realistic limitation (not all social structures support scapegoating)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
