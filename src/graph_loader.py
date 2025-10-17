#!/usr/bin/env python3
"""
Graph file loader supporting multiple formats.
"""

import json
import csv
from typing import Dict, List, Tuple, Set
from .graph import SignedGraph


class GraphLoader:
    """Load signed graphs from various file formats."""

    @staticmethod
    def load_from_file(filepath: str) -> SignedGraph:
        """
        Load graph from file, auto-detecting format from extension.

        Supported formats:
        - .json: JSON format with nodes and edges
        - .csv: CSV edge list (source,target,sign)
        - .txt/.edges: Space or tab-separated edge list

        Returns:
            SignedGraph instance
        """
        if filepath.endswith('.json'):
            return GraphLoader._load_json(filepath)
        elif filepath.endswith('.csv'):
            return GraphLoader._load_csv(filepath)
        elif filepath.endswith('.txt') or filepath.endswith('.edges'):
            return GraphLoader._load_txt(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")

    @staticmethod
    def _load_json(filepath: str) -> SignedGraph:
        """
        Load from JSON format:
        {
          "nodes": ["A", "B", "C"],
          "edges": [
            {"source": "A", "target": "B", "sign": 1},
            {"source": "A", "target": "C", "sign": -1}
          ]
        }
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        if 'nodes' not in data or 'edges' not in data:
            raise ValueError("JSON must contain 'nodes' and 'edges' keys")

        graph = SignedGraph()

        # Add nodes
        for node in data['nodes']:
            graph.add_node(str(node))

        # Add edges
        for edge in data['edges']:
            source = str(edge['source'])
            target = str(edge['target'])
            sign = edge['sign']

            if sign not in [1, -1, '+', '-']:
                raise ValueError(f"Invalid sign '{sign}'. Must be 1, -1, '+', or '-'")

            sign_val = 1 if sign in [1, '+'] else -1
            graph.add_edge(source, target, sign_val)

        return graph

    @staticmethod
    def _load_csv(filepath: str) -> SignedGraph:
        """
        Load from CSV edge list format:
        source,target,sign
        A,B,1
        A,C,-1

        Sign can be: 1/-1 or +/- or positive/negative or friend/enemy
        """
        graph = SignedGraph()
        nodes_seen: Set[str] = set()

        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)

            if not all(k in reader.fieldnames for k in ['source', 'target', 'sign']):
                raise ValueError("CSV must have 'source', 'target', 'sign' columns")

            for row in reader:
                source = row['source'].strip()
                target = row['target'].strip()
                sign_str = row['sign'].strip().lower()

                # Parse sign
                if sign_str in ['1', '+', 'positive', 'friend']:
                    sign = 1
                elif sign_str in ['-1', '-', 'negative', 'enemy']:
                    sign = -1
                else:
                    raise ValueError(f"Invalid sign '{sign_str}' for edge {source}-{target}")

                # Add nodes if not seen
                if source not in nodes_seen:
                    graph.add_node(source)
                    nodes_seen.add(source)
                if target not in nodes_seen:
                    graph.add_node(target)
                    nodes_seen.add(target)

                graph.add_edge(source, target, sign)

        return graph

    @staticmethod
    def _load_txt(filepath: str) -> SignedGraph:
        """
        Load from text edge list format (space or tab-separated):
        A B +
        A C -
        A D 1
        B C -1

        Sign can be: +/- or 1/-1
        """
        graph = SignedGraph()
        nodes_seen: Set[str] = set()

        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Split by whitespace
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError(f"Line {line_num}: Expected 3 columns, got {len(parts)}")

                source, target, sign_str = parts
                sign_str = sign_str.strip()

                # Parse sign
                if sign_str in ['+', '1']:
                    sign = 1
                elif sign_str in ['-', '-1']:
                    sign = -1
                else:
                    raise ValueError(f"Line {line_num}: Invalid sign '{sign_str}'")

                # Add nodes if not seen
                if source not in nodes_seen:
                    graph.add_node(source)
                    nodes_seen.add(source)
                if target not in nodes_seen:
                    graph.add_node(target)
                    nodes_seen.add(target)

                graph.add_edge(source, target, sign)

        return graph

    @staticmethod
    def save_to_file(graph: SignedGraph, filepath: str, format: str = 'json'):
        """
        Save graph to file.

        Args:
            graph: SignedGraph to save
            filepath: Output file path
            format: 'json', 'csv', or 'txt'
        """
        if format == 'json':
            GraphLoader._save_json(graph, filepath)
        elif format == 'csv':
            GraphLoader._save_csv(graph, filepath)
        elif format == 'txt':
            GraphLoader._save_txt(graph, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _save_json(graph: SignedGraph, filepath: str):
        """Save graph as JSON."""
        data = {
            'nodes': sorted(graph.nodes),
            'edges': []
        }

        for (u, v), sign in sorted(graph.edges.items()):
            data['edges'].append({
                'source': u,
                'target': v,
                'sign': sign
            })

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _save_csv(graph: SignedGraph, filepath: str):
        """Save graph as CSV."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['source', 'target', 'sign'])

            for (u, v), sign in sorted(graph.edges.items()):
                writer.writerow([u, v, sign])

    @staticmethod
    def _save_txt(graph: SignedGraph, filepath: str):
        """Save graph as text edge list."""
        with open(filepath, 'w') as f:
            for (u, v), sign in sorted(graph.edges.items()):
                sign_str = '+' if sign == 1 else '-'
                f.write(f"{u} {v} {sign_str}\n")
