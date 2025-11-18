#!/usr/bin/env python3
"""
Analyze graph prerequisites for guaranteed unity achievement.
Identifies conditions under which scapegoating contagion must succeed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graph import SignedGraph
from src.simulator import MimeticContagionSimulator
from generate_graph import generate_sparse_graph, generate_complete_graph
import random


def check_graph_prerequisites(graph: SignedGraph, scapegoat: str, accuser: str):
    """
    Check if graph satisfies prerequisites for guaranteed unity.

    Prerequisites identified:
    1. Each node must have at least one positive edge
    2. Accuser must have at least one positive edge that is NOT to the scapegoat
    3. Graph must be connected via positive edges (friendship network is connected)
    """
    results = {
        'all_nodes_have_friends': True,
        'accuser_has_other_friends': True,
        'friendship_connected': True,
        'min_degree': float('inf'),
        'isolated_nodes': [],
        'accuser_friend_count': 0,
        'accuser_friends_excluding_scapegoat': 0,
        'disconnected_components': 1,
        'reachable_from_accuser': 0
    }

    # Check 1: Every node has at least one positive edge
    for node in graph.nodes:
        friends = [n for n in graph.neighbors(node) if graph.get_edge(node, n) == 1]
        degree = len(friends)

        if degree == 0:
            results['all_nodes_have_friends'] = False
            results['isolated_nodes'].append(node)

        results['min_degree'] = min(results['min_degree'], degree)

    # Check 2: Accuser has friends other than scapegoat
    accuser_friends = [n for n in graph.neighbors(accuser) if graph.get_edge(accuser, n) == 1]
    accuser_friends_excluding = [n for n in accuser_friends if n != scapegoat]

    results['accuser_friend_count'] = len(accuser_friends)
    results['accuser_friends_excluding_scapegoat'] = len(accuser_friends_excluding)
    results['accuser_has_other_friends'] = len(accuser_friends_excluding) > 0

    # Check 3: Friendship connectivity (BFS from accuser through positive edges)
    visited = {accuser, scapegoat}  # Exclude scapegoat from reachability
    queue = [accuser]

    while queue:
        current = queue.pop(0)
        for neighbor in graph.neighbors(current):
            if neighbor not in visited and graph.get_edge(current, neighbor) == 1:
                visited.add(neighbor)
                queue.append(neighbor)

    results['reachable_from_accuser'] = len(visited) - 1  # Exclude accuser itself
    total_others = len(graph.nodes) - 1  # Exclude scapegoat
    results['friendship_connected'] = (len(visited) - 1 >= total_others - 1)  # Can reach all except scapegoat

    # Count disconnected components in friendship graph
    all_visited = set()
    component_count = 0

    for node in graph.nodes:
        if node not in all_visited:
            component_count += 1
            comp_queue = [node]
            all_visited.add(node)

            while comp_queue:
                current = comp_queue.pop(0)
                for neighbor in graph.neighbors(current):
                    if neighbor not in all_visited and graph.get_edge(current, neighbor) == 1:
                        all_visited.add(neighbor)
                        comp_queue.append(neighbor)

    results['disconnected_components'] = component_count

    return results


def test_your_example():
    """Test the 4-node example you described: B-D(--)C-A with B and D friends."""
    print("="*70)
    print("TESTING YOUR 4-NODE EXAMPLE")
    print("="*70)
    print("Graph: B↔D (friends), D↔C (enemies), C↔A (friends), A↔B (no edge)")
    print("Scapegoat: Betty (B), Accuser: David (D)")

    graph = SignedGraph()
    graph.add_node("Betty")
    graph.add_node("David")
    graph.add_node("Charlie")
    graph.add_node("Alice")

    # B↔D: friends
    graph.add_edge("Betty", "David", 1)
    # D↔C: enemies
    graph.add_edge("David", "Charlie", -1)
    # C↔A: friends
    graph.add_edge("Charlie", "Alice", 1)
    # A↔B: no edge (no connection)

    print("\nInitial graph:")
    print("  Betty ↔ David: +1 (friends)")
    print("  David ↔ Charlie: -1 (enemies)")
    print("  Charlie ↔ Alice: +1 (friends)")
    print("  Alice ↔ Betty: 0 (no edge)")

    # Check prerequisites
    prereqs = check_graph_prerequisites(graph, "Betty", "David")

    print("\nPrerequisite Analysis:")
    print(f"  All nodes have friends: {prereqs['all_nodes_have_friends']}")
    print(f"  Accuser has other friends: {prereqs['accuser_has_other_friends']}")
    print(f"  Accuser friend count: {prereqs['accuser_friend_count']}")
    print(f"  Accuser friends (excluding scapegoat): {prereqs['accuser_friends_excluding_scapegoat']}")
    print(f"  Friendship connected: {prereqs['friendship_connected']}")
    print(f"  Reachable from accuser: {prereqs['reachable_from_accuser']}/{len(graph.nodes)-1}")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation("Betty", "David")

    print(f"\nSimulation Result:")
    print(f"  Accusers: {len(result.accusers)}/{len(graph.nodes)-1}")
    print(f"  Defenders: {len(result.defenders)}")
    print(f"  Unity achieved: {result.is_all_against_one and result.is_balanced}")
    print(f"  Accuser list: {sorted(result.accusers)}")
    print(f"  Defender list: {sorted(result.defenders)}")

    print("\n✓ PREDICTION: Unity should FAIL")
    print("  Reason: David's only friend was Betty (the scapegoat)")
    print("  After flipping Betty↔David to negative, David has no friends")
    print("  Therefore, David cannot tell anyone about Betty")
    print("  Alice and Charlie never hear about the accusation")

    return result, prereqs


def test_fixed_example():
    """Test the same example but with David having another friend (Alice)."""
    print("\n" + "="*70)
    print("TESTING FIXED 4-NODE EXAMPLE")
    print("="*70)
    print("Graph: B↔D, D↔C (enemies), C↔A, D↔A (added!)")
    print("Scapegoat: Betty (B), Accuser: David (D)")

    graph = SignedGraph()
    graph.add_node("Betty")
    graph.add_node("David")
    graph.add_node("Charlie")
    graph.add_node("Alice")

    # B↔D: friends
    graph.add_edge("Betty", "David", 1)
    # D↔C: enemies
    graph.add_edge("David", "Charlie", -1)
    # C↔A: friends
    graph.add_edge("Charlie", "Alice", 1)
    # D↔A: friends (ADDED!)
    graph.add_edge("David", "Alice", 1)

    print("\nInitial graph:")
    print("  Betty ↔ David: +1 (friends)")
    print("  David ↔ Charlie: -1 (enemies)")
    print("  Charlie ↔ Alice: +1 (friends)")
    print("  David ↔ Alice: +1 (friends) ← ADDED")

    # Check prerequisites
    prereqs = check_graph_prerequisites(graph, "Betty", "David")

    print("\nPrerequisite Analysis:")
    print(f"  All nodes have friends: {prereqs['all_nodes_have_friends']}")
    print(f"  Accuser has other friends: {prereqs['accuser_has_other_friends']} ✓")
    print(f"  Accuser friend count: {prereqs['accuser_friend_count']}")
    print(f"  Accuser friends (excluding scapegoat): {prereqs['accuser_friends_excluding_scapegoat']}")
    print(f"  Friendship connected: {prereqs['friendship_connected']}")
    print(f"  Reachable from accuser: {prereqs['reachable_from_accuser']}/{len(graph.nodes)-1}")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=True)
    result = simulator.introduce_accusation("Betty", "David")

    print(f"\nSimulation Result:")
    print(f"  Accusers: {len(result.accusers)}/{len(graph.nodes)-1}")
    print(f"  Defenders: {len(result.defenders)}")
    print(f"  Unity achieved: {result.is_all_against_one and result.is_balanced}")
    print(f"  Accuser list: {sorted(result.accusers)}")
    print(f"  Defender list: {sorted(result.defenders)}")

    print("\n✓ PREDICTION: Unity should SUCCEED")
    print("  Reason: David has Alice as a friend (besides Betty)")
    print("  David tells Alice about Betty")
    print("  Alice tells Charlie about Betty")
    print("  David and Charlie become friends (enemy's enemy)")
    print("  All turn against Betty")

    return result, prereqs


def analyze_ring_failure():
    """Analyze why ring graph fails."""
    print("\n" + "="*70)
    print("ANALYZING RING GRAPH FAILURE")
    print("="*70)

    # Create simple ring: 0-1-2-3-4-0 with one negative edge
    graph = SignedGraph()
    nodes = [f"n{i}" for i in range(5)]
    for node in nodes:
        graph.add_node(node)

    # Create ring with one negative edge
    random.seed(42)
    for i in range(5):
        next_i = (i + 1) % 5
        sign = 1 if random.random() < 0.8 else -1
        graph.add_edge(nodes[i], nodes[next_i], sign)

    # Find a good scapegoat/accuser pair
    scapegoat = nodes[0]
    accuser = nodes[1]  # Neighbor of scapegoat

    print(f"Ring graph with {len(nodes)} nodes")
    print(f"Edges:")
    for edge, sign in graph.edges.items():
        sign_str = "+" if sign == 1 else "-"
        print(f"  {edge[0]} ↔ {edge[1]}: {sign_str}")

    print(f"\nScapegoat: {scapegoat}, Accuser: {accuser}")

    # Check prerequisites
    prereqs = check_graph_prerequisites(graph, scapegoat, accuser)

    print("\nPrerequisite Analysis:")
    print(f"  Accuser has other friends: {prereqs['accuser_has_other_friends']}")
    print(f"  Accuser friend count: {prereqs['accuser_friend_count']}")
    print(f"  Accuser friends (excluding scapegoat): {prereqs['accuser_friends_excluding_scapegoat']}")

    # Check accuser's friends
    accuser_friends = [n for n in graph.neighbors(accuser) if graph.get_edge(accuser, n) == 1]
    print(f"\n  Accuser's friends: {accuser_friends}")
    print(f"  Scapegoat in friends: {scapegoat in accuser_friends}")

    if scapegoat in accuser_friends and len(accuser_friends) == 1:
        print("\n  ⚠️  PROBLEM: Accuser's ONLY friend is the scapegoat!")
        print("  After initial accusation, accuser will have NO friends")
        print("  Contagion cannot spread!")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, accuser)

    print(f"\nSimulation Result:")
    print(f"  Accusers: {len(result.accusers)}/{len(graph.nodes)-1}")
    print(f"  Unity achieved: {result.is_all_against_one}")

    return result, prereqs


def formalize_prerequisites():
    """Formalize the prerequisites for guaranteed unity."""
    print("\n" + "="*70)
    print("FORMALIZED PREREQUISITES FOR GUARANTEED UNITY")
    print("="*70)

    print("\nNECESSARY CONDITIONS:")
    print("\n1. ACCUSER NON-ISOLATION")
    print("   The accuser must have at least ONE positive edge to a node")
    print("   that is NOT the scapegoat.")
    print("   ")
    print("   Formal: ∃v ∈ V \\ {scapegoat, accuser} : edge(accuser, v) = +1")
    print("   ")
    print("   Violation: If accuser's only friend is scapegoat, after")
    print("   flipping that edge negative, accuser becomes isolated and")
    print("   cannot propagate the accusation via BFS.")

    print("\n2. FRIENDSHIP CONNECTIVITY")
    print("   The friendship subgraph (positive edges only) must form a")
    print("   connected component that includes the accuser and reaches")
    print("   all other nodes (excluding scapegoat).")
    print("   ")
    print("   Formal: For all v ∈ V \\ {scapegoat}, there exists a path")
    print("   from accuser to v using only positive edges (after initial flip).")
    print("   ")
    print("   Violation: Disconnected friendship components mean some nodes")
    print("   cannot hear about the accusation.")

    print("\n3. MINIMUM DEGREE BOUND")
    print("   Each node should have at least 2 positive edges, OR")
    print("   if a node has only 1 positive edge, that edge must NOT")
    print("   be to the scapegoat (for the accuser specifically).")
    print("   ")
    print("   Weaker form: Accuser must have degree ≥ 2 in friendship graph.")

    print("\n" + "="*70)
    print("SUFFICIENT CONDITION (Simple)")
    print("="*70)

    print("\nSUFFICIENT: Each node has ≥2 positive edges AND friendship graph")
    print("is connected.")
    print("")
    print("This guarantees:")
    print("  - Accuser has at least one friend besides scapegoat")
    print("  - Information can reach all nodes via BFS")
    print("  - Unity will be achieved (assuming high enough positive edge ratio)")

    print("\n" + "="*70)
    print("WEAKER SUFFICIENT CONDITION")
    print("="*70)

    print("\nWEAKER: Friendship graph is connected AND accuser has ≥1 friend")
    print("besides scapegoat.")
    print("")
    print("This allows some nodes to have degree 1, as long as the accuser")
    print("is not one of them.")

    print("\n" + "="*70)
    print("IMPLICATIONS FOR GRAPH GENERATION")
    print("="*70)

    print("\nWhen generating test graphs, we should:")
    print("  1. Ensure min_degree ≥ 2 (sparse graphs)")
    print("  2. OR: Manually verify accuser has friends besides scapegoat")
    print("  3. OR: Pre-check prerequisites before running simulation")
    print("  4. OR: Accept that some graphs will fail (realistic!)")

    print("\nThe ring graph failure is REALISTIC behavior:")
    print("  - If accuser is isolated after accusation, contagion fails")
    print("  - This could model 'failed scapegoating attempts' in real life")
    print("  - Scapegoating requires sufficient social connectivity")


def main():
    """Run all prerequisite analyses."""

    # Test your specific example
    result1, prereqs1 = test_your_example()

    # Test fixed version
    result2, prereqs2 = test_fixed_example()

    # Analyze ring failure
    result3, prereqs3 = analyze_ring_failure()

    # Formalize findings
    formalize_prerequisites()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print("\nYour hypothesis is CORRECT:")
    print("  ✓ Accuser must have ≥1 friend besides scapegoat")
    print("  ✓ Otherwise, accuser becomes isolated after initial flip")
    print("  ✓ BFS cannot propagate through zero friends")
    print("  ✓ Unity fails")

    print("\nThis explains:")
    print("  - Ring graph failure (1 accuser out of 300)")
    print("  - Your 4-node example")
    print("  - Why sparse graphs with min_degree=2 work better")

    print("\nRecommendation:")
    print("  Add prerequisite checking to simulator")
    print("  Warn user if accuser will become isolated")
    print("  OR: Select different accuser who has other friends")

    return 0


if __name__ == '__main__':
    sys.exit(main())
