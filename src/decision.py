"""
Decision logic: How nodes decide which edge to flip when under pressure.
"""

from typing import Tuple, Optional, List, Dict, Set
import random
from .graph import SignedGraph
from .analyzer import (
    get_node_unbalanced_triangles,
    compute_social_score,
    Triangle
)


class FlipOption:
    """Represents a possible edge flip and its context."""

    def __init__(
        self,
        actor: str,
        target: str,
        current_sign: int,
        target_score: int,
        triangle_type: str,
        triangle: Triangle
    ):
        self.actor = actor
        self.target = target
        self.current_sign = current_sign
        self.target_score = target_score
        self.triangle_type = triangle_type
        self.triangle = triangle

    def __repr__(self):
        action = "Break with" if self.current_sign == 1 else "Ally with"
        return f"{action} {self.target} (score={self.target_score})"


def get_flip_options(graph: SignedGraph, actor: str, actor_flipped_edges: Set[Tuple[str, Tuple[str, str]]] = None) -> List[FlipOption]:
    """
    Get all possible edge flips for a node under pressure.

    Args:
        graph: The signed graph
        actor: The node making the decision
        actor_flipped_edges: Set of (actor, edge) tuples tracking who has acted on which edges

    Returns:
        List of FlipOption objects
    """
    if actor_flipped_edges is None:
        actor_flipped_edges = set()

    options = []
    unbalanced_triangles = get_node_unbalanced_triangles(graph, actor)

    # Track which edges we've already considered
    considered_edges = set()

    for triangle in unbalanced_triangles:
        # Get the other two nodes in this triangle
        other_nodes = [n for n in triangle.nodes if n != actor]

        for target in other_nodes:
            edge = tuple(sorted([actor, target]))
            if edge in considered_edges:
                continue
            considered_edges.add(edge)

            # Skip edges where THIS ACTOR has already acted (no reversals for this actor)
            if (actor, edge) in actor_flipped_edges:
                continue

            current_sign = graph.get_edge(actor, target)
            target_score = compute_social_score(graph, target)

            option = FlipOption(
                actor=actor,
                target=target,
                current_sign=current_sign,
                target_score=target_score,
                triangle_type=triangle.get_type(),
                triangle=triangle
            )
            options.append(option)

    return options


def choose_flip(graph: SignedGraph, actor: str, actor_flipped_edges: Set[Tuple[str, Tuple[str, str]]] = None) -> Optional[Tuple[str, str]]:
    """
    Decide which edge to flip based on mimetic logic.

    Rules:
    - For ++- triangles: Break with the person with LOWEST score (easiest to hate)
    - For --- triangles: Ally with the person with HIGHEST score (easiest to love)
    - No reversals: Each actor can only flip an edge once

    Args:
        graph: The signed graph
        actor: The node making the decision
        actor_flipped_edges: Set of (actor, edge) tuples tracking who has acted on which edges

    Returns:
        (actor, target) tuple for the edge to flip, or None if no valid options
    """
    options = get_flip_options(graph, actor, actor_flipped_edges)

    if not options:
        return None

    # Separate options by type
    breaking_options = [opt for opt in options if opt.current_sign == 1]  # ++- case
    allying_options = [opt for opt in options if opt.current_sign == -1]  # --- case

    chosen_option = None

    # Priority: Try to break friendships first (++- triangles)
    if breaking_options:
        # Choose person with lowest score (easiest to hate)
        min_score = min(opt.target_score for opt in breaking_options)
        candidates = [opt for opt in breaking_options if opt.target_score == min_score]
        chosen_option = random.choice(candidates)

    # If no breaking options, try to form alliances (--- triangles)
    elif allying_options:
        # Choose person with highest score (easiest to love)
        max_score = max(opt.target_score for opt in allying_options)
        candidates = [opt for opt in allying_options if opt.target_score == max_score]
        chosen_option = random.choice(candidates)

    if chosen_option:
        return (actor, chosen_option.target)

    return None


def get_decision_context(graph: SignedGraph, actor: str) -> Dict:
    """
    Get full decision context for a node (for human-readable output).

    Returns:
        Dictionary with:
        - unbalanced_triangles: List of triangles causing pressure
        - options: List of possible flips
        - scores: Dict of target -> score
        - chosen: The chosen flip option
    """
    unbalanced = get_node_unbalanced_triangles(graph, actor)
    options = get_flip_options(graph, actor)

    # Compute scores for all relevant nodes
    relevant_nodes = set()
    for opt in options:
        relevant_nodes.add(opt.target)

    scores = {node: compute_social_score(graph, node) for node in relevant_nodes}

    # Get the chosen flip
    chosen_edge = choose_flip(graph, actor)

    # Find the chosen option
    chosen_option = None
    if chosen_edge:
        target = chosen_edge[1] if chosen_edge[0] == actor else chosen_edge[0]
        chosen_option = next((opt for opt in options if opt.target == target), None)

    return {
        "unbalanced_triangles": unbalanced,
        "options": options,
        "scores": scores,
        "chosen": chosen_option,
        "chosen_edge": chosen_edge
    }
