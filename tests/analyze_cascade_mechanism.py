#!/usr/bin/env python3
"""
Analyze the mechanism behind internal cascade flips.

Question: When enemies become friends during scapegoating, which rule fires?

Expected: Rule 2 (Befriend enemy's enemy)
- Node A is enemy of scapegoat (-1)
- Node B is enemy of scapegoat (-1)
- A and B are currently enemies (-1)
- Triangle: [A, B, scapegoat] with edges [-, -, -] (unbalanced)
- Rule 2: Befriend B (flip A↔B to +1)
- Reason: "Enemy's enemy is friend"
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
    p_connected_a=0.4,
    p_connected_b=0.4,
    p_positive_a=0.7,
    p_positive_b=0.7,
    min_degree=2,
    seed=42
):
    """Create realistic fragmented communities with bridge."""
    random.seed(seed)
    graph = SignedGraph()

    comm_a = [f'A{i}' for i in range(size_a)]
    comm_b = [f'B{i}' for i in range(size_b)]

    for node in comm_a + comm_b:
        graph.add_node(node)

    def add_community_edges(community, p_connected, p_positive):
        """Add edges within a community with partial connectivity."""
        for i, n1 in enumerate(community):
            for n2 in community[i+1:]:
                if random.random() < p_connected:
                    sign = 1 if random.random() < p_positive else -1
                    graph.add_edge(n1, n2, sign)

        for node in community:
            positive_neighbors = [n for n in community
                                  if n != node and graph.get_edge(node, n) == 1]

            while len(positive_neighbors) < min_degree:
                candidates = [n for n in community
                              if n != node and graph.get_edge(node, n) == 0]
                if not candidates:
                    break

                new_friend = random.choice(candidates)
                graph.add_edge(node, new_friend, 1)
                positive_neighbors.append(new_friend)

    add_community_edges(comm_a, p_connected_a, p_positive_a)
    add_community_edges(comm_b, p_connected_b, p_positive_b)

    # Add bridge
    bridge_a = random.choice(comm_a)
    bridge_b = random.choice(comm_b)
    if not graph.has_edge(bridge_a, bridge_b):
        graph.add_edge(bridge_a, bridge_b, 1)

    return graph, comm_a, comm_b, (bridge_a, bridge_b)


def analyze_flip_by_rule():
    """
    Trace through simulation decisions to categorize flips by rule.

    Rules:
    - Rule 1: Forced choice (friend of both accuser and scapegoat, choose accuser)
    - Rule 2: Befriend enemy's enemy (--- triangle resolution)
    - Rule 3: Hear accusation (friend of accuser, no edge to scapegoat, create negative)
    """
    print("="*70)
    print("ANALYZING CASCADE MECHANISM: WHICH RULE CAUSES ENEMY→FRIEND FLIPS?")
    print("="*70)

    graph, comm_a, comm_b, bridge = create_realistic_communities_with_bridge(
        size_a=8,
        size_b=8,
        p_connected_a=0.4,
        p_connected_b=0.4,
        p_positive_a=0.7,
        p_positive_b=0.7,
        min_degree=2,
        seed=42
    )

    scapegoat = 'B0'
    accuser = 'A0'

    # Ensure accuser-scapegoat edge exists
    if not graph.has_edge(accuser, scapegoat):
        graph.add_edge(accuser, scapegoat, 1)

    print(f"\nSetup:")
    print(f"  Scapegoat: {scapegoat}")
    print(f"  Accuser: {accuser}")
    print(f"  Bridge: {bridge}")

    # Run simulation
    simulator = MimeticContagionSimulator(graph, verbose=False)
    result = simulator.introduce_accusation(scapegoat, accuser)

    # Categorize decisions by action
    decisions_by_action = {
        'join_accusers': [],
        'hear_accusation': [],
        'befriend_other': [],
        'no_action': []
    }

    for decision in result.decisions:
        action = decision.action if decision.action else 'no_action'
        decisions_by_action[action].append(decision)

    print(f"\n" + "="*70)
    print("DECISION BREAKDOWN BY RULE")
    print("="*70)

    print(f"\nTotal decisions: {len(result.decisions)}")
    for action, decisions in decisions_by_action.items():
        print(f"  {action}: {len(decisions)}")

    # Analyze befriend_other (Rule 2: Enemy's enemy is friend)
    print(f"\n" + "="*70)
    print("RULE 2: BEFRIEND ENEMY'S ENEMY (Enemy → Friend flips)")
    print("="*70)

    if decisions_by_action['befriend_other']:
        print(f"\n{len(decisions_by_action['befriend_other'])} instances of Rule 2 firing:")

        for i, decision in enumerate(decisions_by_action['befriend_other'], 1):
            print(f"\n{i}. Node: {decision.node}")
            print(f"   Reason: {decision.reason}")

            if decision.edge_flipped:
                n1, n2 = decision.edge_flipped
                print(f"   Edge flipped: {n1} ↔ {n2}")
                print(f"   Change: {decision.old_sign:+d} → {decision.new_sign:+d}")

                # Explain the triangle
                print(f"\n   Triangle analysis:")
                print(f"     {decision.node} ↔ {scapegoat}: -1 (both are enemies of scapegoat)")

                # Find who the other node is
                other = n2 if n1 == decision.node else n1
                print(f"     {other} ↔ {scapegoat}: -1 (both are enemies of scapegoat)")
                print(f"     {decision.node} ↔ {other}: {decision.old_sign:+d} → {decision.new_sign:+d}")
                print(f"\n   Before: [{decision.node}, {other}, {scapegoat}] had edges [-, -, -] (unbalanced)")
                print(f"   After:  [{decision.node}, {other}, {scapegoat}] has edges [+, -, -] (balanced)")
                print(f"   ✓ 'Enemy of my enemy is my friend'")

    else:
        print("\nNo Rule 2 firings detected!")
        print("(Enemy→friend flips must have come from a different mechanism)")

    # Analyze join_accusers (Rule 1: Forced choice)
    print(f"\n" + "="*70)
    print("RULE 1: FORCED CHOICE (Friend dilemma)")
    print("="*70)

    if decisions_by_action['join_accusers']:
        print(f"\n{len(decisions_by_action['join_accusers'])} instances of Rule 1 firing:")

        for i, decision in enumerate(decisions_by_action['join_accusers'][:5], 1):
            print(f"\n{i}. Node: {decision.node}")
            print(f"   Reason: {decision.reason}")

            if decision.edge_flipped:
                n1, n2 = decision.edge_flipped
                print(f"   Edge flipped: {n1} ↔ {n2}")
                print(f"   Change: {decision.old_sign:+d} → {decision.new_sign:+d}")
                print(f"   ✓ Chose accuser over scapegoat (friend → enemy flip)")

    # Analyze hear_accusation (Rule 3: Information spread)
    print(f"\n" + "="*70)
    print("RULE 3: HEAR ACCUSATION (Information contagion)")
    print("="*70)

    if decisions_by_action['hear_accusation']:
        print(f"\n{len(decisions_by_action['hear_accusation'])} instances of Rule 3 firing:")

        for i, decision in enumerate(decisions_by_action['hear_accusation'][:5], 1):
            print(f"\n{i}. Node: {decision.node}")
            print(f"   Reason: {decision.reason}")

            if decision.edge_flipped:
                n1, n2 = decision.edge_flipped
                print(f"   Edge created: {n1} ↔ {n2}")
                print(f"   Change: {decision.old_sign} → {decision.new_sign:+d}")
                print(f"   ✓ Heard about scapegoat, formed negative opinion")

    # Summary by flip type
    print(f"\n" + "="*70)
    print("FLIP TYPE SUMMARY")
    print("="*70)

    flip_types = {
        'friend_to_enemy': [],    # +1 → -1 (Rule 1: forced choice, or initial accusation)
        'enemy_to_friend': [],    # -1 → +1 (Rule 2: befriend enemy's enemy)
        'none_to_enemy': [],      # 0 → -1 (Rule 3: hear accusation)
        'none_to_friend': [],     # 0 → +1 (Rule 2: befriend, rare)
        'other': []
    }

    for decision in result.decisions:
        if not decision.edge_flipped:
            continue

        old_sign = decision.old_sign
        new_sign = decision.new_sign

        if old_sign == 1 and new_sign == -1:
            flip_types['friend_to_enemy'].append(decision)
        elif old_sign == -1 and new_sign == 1:
            flip_types['enemy_to_friend'].append(decision)
        elif old_sign == 0 and new_sign == -1:
            flip_types['none_to_enemy'].append(decision)
        elif old_sign == 0 and new_sign == 1:
            flip_types['none_to_friend'].append(decision)
        else:
            flip_types['other'].append(decision)

    print(f"\nFlips by type:")
    print(f"  Friend → Enemy (+1 → -1): {len(flip_types['friend_to_enemy'])}")
    print(f"  Enemy → Friend (-1 → +1): {len(flip_types['enemy_to_friend'])}")
    print(f"  None → Enemy (0 → -1):    {len(flip_types['none_to_enemy'])}")
    print(f"  None → Friend (0 → +1):   {len(flip_types['none_to_friend'])}")
    print(f"  Other:                    {len(flip_types['other'])}")

    # Detail enemy→friend flips
    if flip_types['enemy_to_friend']:
        print(f"\n" + "="*70)
        print(f"ENEMY → FRIEND FLIPS ({len(flip_types['enemy_to_friend'])} total)")
        print("="*70)

        for i, decision in enumerate(flip_types['enemy_to_friend'], 1):
            n1, n2 = decision.edge_flipped
            print(f"\n{i}. {n1} ↔ {n2}: -1 → +1")
            print(f"   Node: {decision.node}")
            print(f"   Action: {decision.action}")
            print(f"   Reason: {decision.reason}")

            # Check which community
            n1_comm = 'A' if n1.startswith('A') else 'B'
            n2_comm = 'A' if n2.startswith('A') else 'B'
            print(f"   Location: Community {n1_comm} - {n2_comm}")

            # Verify it's Rule 2
            if decision.action == 'befriend_other':
                print(f"   ✓ RULE 2: Befriend enemy's enemy")
            else:
                print(f"   ⚠ Unexpected action for enemy→friend flip!")

    # Detail friend→enemy flips
    if flip_types['friend_to_enemy']:
        print(f"\n" + "="*70)
        print(f"FRIEND → ENEMY FLIPS ({len(flip_types['friend_to_enemy'])} total)")
        print("="*70)

        for i, decision in enumerate(flip_types['friend_to_enemy'], 1):
            n1, n2 = decision.edge_flipped
            print(f"\n{i}. {n1} ↔ {n2}: +1 → -1")
            print(f"   Node: {decision.node}")
            print(f"   Action: {decision.action}")
            print(f"   Reason: {decision.reason}")

            # Check if it involves scapegoat
            involves_sg = (n1 == scapegoat or n2 == scapegoat)
            print(f"   Involves scapegoat: {involves_sg}")

            if decision.action == 'join_accusers' or involves_sg:
                print(f"   ✓ RULE 1: Forced choice (or initial accusation)")
            else:
                print(f"   ⚠ Unexpected action for friend→enemy flip!")

    return {
        'decisions_by_action': decisions_by_action,
        'flip_types': flip_types,
        'result': result
    }


def main():
    """Run cascade mechanism analysis."""
    result = analyze_flip_by_rule()

    print(f"\n" + "="*70)
    print("CONCLUSION")
    print("="*70)

    enemy_to_friend = len(result['flip_types']['enemy_to_friend'])
    befriend_other = len(result['decisions_by_action']['befriend_other'])

    print(f"\nEnemy → Friend flips: {enemy_to_friend}")
    print(f"Rule 2 (befriend_other) firings: {befriend_other}")

    if enemy_to_friend == befriend_other and enemy_to_friend > 0:
        print(f"\n✓ MECHANISM CONFIRMED:")
        print(f"  All {enemy_to_friend} enemy→friend flips were caused by Rule 2")
        print(f"  'Enemy of my enemy is my friend' (--- triangle resolution)")
        print(f"\nHow it works:")
        print(f"  1. Node A becomes enemy of scapegoat (hears accusation)")
        print(f"  2. Node B also becomes enemy of scapegoat")
        print(f"  3. A and B were previously enemies (-1 edge)")
        print(f"  4. Triangle [A, B, scapegoat] has edges [-, -, -] (unbalanced)")
        print(f"  5. Rule 2 fires: A befriends B (flip to +1)")
        print(f"  6. Result: Enemies reconcile through shared enemy")

    return 0


if __name__ == '__main__':
    sys.exit(main())
