"""
Analyzer: Detect triangles, classify balance, find nodes under pressure.
"""

from typing import List, Set, Tuple, Dict
from itertools import combinations
from .graph import SignedGraph


class Triangle:
    """Represents a triangle in the graph."""

    def __init__(self, nodes: Tuple[str, str, str], edges: Tuple[int, int, int]):
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


def find_pressured_nodes(graph: SignedGraph) -> Set[str]:
    """Find all nodes that are in unbalanced triangles (under pressure)."""
    unbalanced = find_unbalanced_triangles(graph)
    pressured = set()

    for triangle in unbalanced:
        pressured.update(triangle.nodes)

    return pressured


def get_node_triangles(graph: SignedGraph, node: str) -> List[Triangle]:
    """Get all triangles that include a specific node."""
    all_triangles = find_all_triangles(graph)
    return [t for t in all_triangles if node in t.nodes]


def get_node_unbalanced_triangles(graph: SignedGraph, node: str) -> List[Triangle]:
    """Get all unbalanced triangles that include a specific node."""
    all_triangles = get_node_triangles(graph, node)
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


def calculate_triangle_delta(graph: SignedGraph, edge: tuple) -> int:
    """
    Calculate the triangle balance delta for a potential edge flip.

    Returns:
        Positive number = net improvement (more triangles balanced)
        Negative number = net worsening (more triangles unbalanced)
        Zero = no change

    Args:
        graph: The signed graph
        edge: The edge to potentially flip (u, v)

    Returns:
        triangle_delta: (triangles_balanced - triangles_unbalanced) after flip
    """
    # Count unbalanced triangles before flip
    unbalanced_before = len(find_unbalanced_triangles(graph))

    # Simulate the flip
    graph_copy = graph.copy()
    graph_copy.flip_edge(*edge)

    # Count unbalanced triangles after flip
    unbalanced_after = len(find_unbalanced_triangles(graph_copy))

    # Delta: negative change in unbalanced triangles = improvement
    # If we go from 10 unbalanced to 5 unbalanced, delta = -5, which is good
    # Return the inverse so positive = good
    return unbalanced_before - unbalanced_after
