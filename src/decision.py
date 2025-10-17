"""
Decision logic: How nodes respond to scapegoating accusations.
"""

from typing import Tuple, Optional, Set
from .graph import SignedGraph


def has_accuser_friend(graph: SignedGraph, node: str, accusers: Set[str]) -> bool:
    """Check if node has any friends who are accusers."""
    for accuser in accusers:
        if graph.has_edge(node, accuser) and graph.get_edge(node, accuser) == 1:
            return True
    return False


def has_accuser_enemy(graph: SignedGraph, node: str, accusers: Set[str]) -> bool:
    """Check if node has any enemies who are accusers."""
    for accuser in accusers:
        if graph.has_edge(node, accuser) and graph.get_edge(node, accuser) == -1:
            return True
    return False


def find_unbalanced_triangles_with_scapegoat(graph: SignedGraph, node: str, scapegoat: str):
    """Find all --- triangles involving this node and the scapegoat."""
    from .analyzer import Triangle

    unbalanced = []

    # Check all potential third nodes
    for third_node in graph.nodes:
        if third_node == node or third_node == scapegoat:
            continue

        # Check if triangle exists (all three edges present)
        if not (graph.has_edge(node, scapegoat) and
                graph.has_edge(node, third_node) and
                graph.has_edge(scapegoat, third_node)):
            continue

        # Get edge signs
        node_scapegoat = graph.get_edge(node, scapegoat)
        node_third = graph.get_edge(node, third_node)
        scapegoat_third = graph.get_edge(scapegoat, third_node)

        # Check if it's a --- triangle (all negative)
        if node_scapegoat == -1 and node_third == -1 and scapegoat_third == -1:
            triangle = Triangle(
                nodes=(node, scapegoat, third_node),
                edges=(node_scapegoat, scapegoat_third, node_third)
            )
            unbalanced.append((triangle, third_node))

    return unbalanced


def apply_contagion_rule(
    graph: SignedGraph,
    node: str,
    scapegoat: str,
    accusers: Set[str]
):
    """
    Apply scapegoating contagion rules to a node.

    Rules:
    1. Friend of accuser + Friend of scapegoat → Flip against scapegoat (join accusers)
    2. Enemy of scapegoat → In --- triangle: befriend the third person
    3. Friend of accuser + NO edge to scapegoat → Hear about them, create negative edge (join accusers)

    Args:
        graph: The signed graph
        node: The node to evaluate
        scapegoat: The scapegoat
        accusers: Set of current accusers

    Returns:
        List of (action, reason, target_node) tuples - one for each triangle to resolve
    """
    actions = []

    # Check if node has edge to scapegoat
    if not graph.has_edge(node, scapegoat):
        # Rule 3: If friend of accuser, HEAR about scapegoat and create negative edge
        if has_accuser_friend(graph, node, accusers):
            triggering_accuser = next(
                (a for a in accusers if graph.has_edge(node, a) and graph.get_edge(node, a) == 1),
                None
            )
            reason = f"Heard from {triggering_accuser} about {scapegoat}"
            return [("hear_accusation", reason, scapegoat)]
        else:
            return [(None, "No connection to scapegoat or accusers", None)]

    node_scapegoat_relation = graph.get_edge(node, scapegoat)

    # Rule 1: Friend of accuser + Friend of scapegoat → Flip against scapegoat
    if has_accuser_friend(graph, node, accusers) and node_scapegoat_relation == 1:
        # Find triggering accuser (first friend who is accuser)
        triggering_accuser = next(
            (a for a in accusers if graph.has_edge(node, a) and graph.get_edge(node, a) == 1),
            None
        )
        reason = f"Friend of {triggering_accuser}, chose them over {scapegoat}"
        return [("join_accusers", reason, scapegoat)]

    # Rule 2: Enemy of scapegoat → Find all --- triangles and resolve them
    if node_scapegoat_relation == -1:
        # Find all --- triangles involving this node and scapegoat
        unbalanced_triangles = find_unbalanced_triangles_with_scapegoat(graph, node, scapegoat)

        if unbalanced_triangles:
            for triangle, third_node in unbalanced_triangles:
                # Befriend the third person to resolve this --- triangle
                reason = f"In --- triangle ({node}, {scapegoat}, {third_node}), befriend {third_node}"
                actions.append(("befriend_other", reason, third_node))
            return actions
        else:
            # Enemy of scapegoat but no --- triangles
            return [(None, f"Already enemy of {scapegoat} (no --- triangles)", None)]

    # Friend of scapegoat but no accuser friends (defender)
    return [(None, f"Defender of {scapegoat} (no accuser friends)", None)]
