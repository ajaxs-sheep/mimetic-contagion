"""
Analyzer: Detect triangles, classify balance, compute social scores.
"""

from typing import List, Dict
from itertools import combinations
from .graph import SignedGraph


class Triangle:
    """Represents a triangle in the graph."""

    def __init__(self, nodes: tuple, edges: tuple):
        """
        Args:
            nodes: (a, b, c) tuple of node names
            edges: (ab_sign, bc_sign, ac_sign) tuple of edge signs
        """
        self.nodes = nodes
        self.edges = edges

    def is_balanced(self) -> bool:
        """Check if triangle is balanced (even number of negative edges)."""
        num_negative = sum(1 for sign in self.edges if sign == -1)
        return num_negative % 2 == 0

    def is_unbalanced(self) -> bool:
        """Check if triangle is unbalanced (odd number of negative edges)."""
        return not self.is_balanced()

    def get_type(self) -> str:
        """Get triangle type: '+++', '++-', '---', or '+--'."""
        signs = ''.join('+' if s == 1 else '-' for s in self.edges)
        return signs

    def __repr__(self):
        return f"Triangle({self.nodes}, {self.get_type()})"


def find_all_triangles(graph: SignedGraph) -> List[Triangle]:
    """Find all triangles in the graph."""
    triangles = []

    # Check all combinations of 3 nodes
    for a, b, c in combinations(sorted(graph.nodes), 3):
        # Check if all three edges exist
        if graph.has_edge(a, b) and graph.has_edge(b, c) and graph.has_edge(a, c):
            ab_sign = graph.get_edge(a, b)
            bc_sign = graph.get_edge(b, c)
            ac_sign = graph.get_edge(a, c)

            triangle = Triangle(
                nodes=(a, b, c),
                edges=(ab_sign, bc_sign, ac_sign)
            )
            triangles.append(triangle)

    return triangles


def find_unbalanced_triangles(graph: SignedGraph) -> List[Triangle]:
    """Find all unbalanced triangles in the graph."""
    all_triangles = find_all_triangles(graph)
    return [t for t in all_triangles if t.is_unbalanced()]


def compute_social_score(graph: SignedGraph, node: str) -> int:
    """
    Compute a node's social score: (number of friends) - (number of enemies).

    Args:
        graph: The signed graph
        node: The node to score

    Returns:
        Integer score (positive = more friends, negative = more enemies)
    """
    neighbors = graph.neighbors(node)
    friends = sum(1 for n in neighbors if graph.get_edge(node, n) == 1)
    enemies = sum(1 for n in neighbors if graph.get_edge(node, n) == -1)

    return friends - enemies


def compute_all_scores(graph: SignedGraph) -> Dict[str, int]:
    """Compute social scores for all nodes."""
    return {node: compute_social_score(graph, node) for node in graph.nodes}
