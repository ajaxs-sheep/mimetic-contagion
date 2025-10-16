"""
SignedGraph: A graph with positive (+1) and negative (-1) edges.
"""

from typing import Dict, Set, Tuple, List
from collections import defaultdict


class SignedGraph:
    """Graph with signed edges representing friend/enemy relationships."""

    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[Tuple[str, str], int] = {}  # {(u, v): +1 or -1}

    def add_node(self, node: str):
        """Add a node to the graph."""
        self.nodes.add(node)

    def add_edge(self, u: str, v: str, sign: int):
        """Add or update an edge between two nodes."""
        if sign not in [-1, 1]:
            raise ValueError(f"Edge sign must be +1 or -1, got {sign}")

        # Ensure nodes exist
        self.add_node(u)
        self.add_node(v)

        # Store edge in canonical order (alphabetical)
        edge = self._canonical_edge(u, v)
        self.edges[edge] = sign

    def flip_edge(self, u: str, v: str):
        """Flip the sign of an edge."""
        edge = self._canonical_edge(u, v)
        if edge not in self.edges:
            raise ValueError(f"Edge {edge} does not exist")
        self.edges[edge] *= -1

    def get_edge(self, u: str, v: str) -> int:
        """Get the sign of an edge between two nodes."""
        edge = self._canonical_edge(u, v)
        return self.edges.get(edge, 0)  # 0 means no edge

    def has_edge(self, u: str, v: str) -> bool:
        """Check if an edge exists."""
        edge = self._canonical_edge(u, v)
        return edge in self.edges

    def neighbors(self, node: str) -> List[str]:
        """Get all nodes connected to this node."""
        neighbors = []
        for (u, v) in self.edges.keys():
            if u == node:
                neighbors.append(v)
            elif v == node:
                neighbors.append(u)
        return neighbors

    def get_all_edges(self) -> List[Tuple[str, str, int]]:
        """Get all edges as (u, v, sign) tuples."""
        return [(u, v, sign) for (u, v), sign in self.edges.items()]

    def _canonical_edge(self, u: str, v: str) -> Tuple[str, str]:
        """Return edge in canonical order (alphabetical)."""
        return tuple(sorted([u, v]))

    def copy(self):
        """Create a deep copy of the graph."""
        new_graph = SignedGraph()
        new_graph.nodes = self.nodes.copy()
        new_graph.edges = self.edges.copy()
        return new_graph

    def to_dict(self) -> dict:
        """Serialize graph to dictionary."""
        return {
            "nodes": sorted(list(self.nodes)),
            "edges": [
                {"nodes": [u, v], "sign": sign}
                for (u, v), sign in self.edges.items()
            ]
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize graph from dictionary."""
        graph = cls()
        for node in data.get("nodes", []):
            graph.add_node(node)
        for edge in data.get("edges", []):
            u, v = edge["nodes"]
            sign = edge["sign"]
            graph.add_edge(u, v, sign)
        return graph

    @classmethod
    def create_complete_positive(cls, nodes: List[str]):
        """Create a fully connected graph with all positive edges."""
        graph = cls()
        for node in nodes:
            graph.add_node(node)

        # Connect all pairs
        for i, u in enumerate(nodes):
            for v in nodes[i+1:]:
                graph.add_edge(u, v, 1)

        return graph
