#!/usr/bin/env python3
"""
Visualize escalation cycle between two communities.

Creates animated GIF showing:
- Phase 1: Community A accuses member of B
- Phase 2: Community B retaliates against A
- Final: Mutual polarization
"""

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np


def two_community_layout(comm_a, comm_b, separation=2.0):
    """
    Generate layout with two communities facing each other.

    Community A: Left semicircle
    Community B: Right semicircle
    """
    positions = {}

    # Community A: Left semicircle (centered at x=-separation/2)
    center_a_x = -separation / 2
    radius = 1.0

    for i, node in enumerate(comm_a):
        # Angles from 30° to 150° (upper left arc)
        angle = math.pi/6 + (2*math.pi/3) * i / max(len(comm_a)-1, 1)
        x = center_a_x + radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions[node] = (x, y)

    # Community B: Right semicircle (centered at x=+separation/2)
    center_b_x = separation / 2

    for i, node in enumerate(comm_b):
        # Angles from 30° to 150° (upper right arc, mirrored)
        angle = math.pi - (math.pi/6 + (2*math.pi/3) * i / max(len(comm_b)-1, 1))
        x = center_b_x + radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions[node] = (x, y)

    return positions


def load_escalation_data(filepath):
    """Load escalation cycle data from JSON."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def dict_to_graph_edges(graph_dict):
    """Convert graph dict to edge dict."""
    edges = {}
    for edge_data in graph_dict['edges']:
        # Handle both formats: 'nodes' array or 'source'/'target'
        if 'nodes' in edge_data:
            u, v = edge_data['nodes']
        else:
            u = edge_data['source']
            v = edge_data['target']

        sign = edge_data['sign']
        edges[(u, v)] = sign
        edges[(v, u)] = sign  # Undirected
    return edges


def create_frame(ax, positions, edges, phase_info, communities):
    """
    Draw a single frame of the escalation.

    Args:
        ax: Matplotlib axis
        positions: Dict of {node: (x, y)}
        edges: Dict of {(u,v): sign}
        phase_info: Dict with phase metadata
        communities: Dict of {'A': [...], 'B': [...]}
    """
    ax.clear()
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.set_aspect('equal')
    ax.axis('off')

    phase_name = phase_info.get('phase', 'Initial')
    title = phase_info.get('title', 'Escalation Cycle')
    highlight_nodes = phase_info.get('highlight_nodes', [])
    highlight_edge = phase_info.get('highlight_edge', None)

    # Draw title
    ax.text(0, 2.3, title, ha='center', va='top', fontsize=14, fontweight='bold')
    ax.text(0, 2.1, phase_name, ha='center', va='top', fontsize=10, style='italic')

    # Draw edges first (so they're behind nodes)
    for (u, v), sign in edges.items():
        if u not in positions or v not in positions:
            continue
        if u > v:  # Only draw each edge once
            continue

        x1, y1 = positions[u]
        x2, y2 = positions[v]

        # Edge color and style
        if sign == 1:
            color = 'green'
            alpha = 0.3
            linewidth = 1.0
        elif sign == -1:
            color = 'red'
            alpha = 0.5
            linewidth = 1.5
        else:
            continue  # Don't draw 0 edges

        # Highlight specific edge
        if highlight_edge and ((u, v) == highlight_edge or (v, u) == highlight_edge):
            if sign == -1:
                color = 'darkred'
                alpha = 1.0
                linewidth = 3.0
            else:
                color = 'darkgreen'
                alpha = 1.0
                linewidth = 3.0

        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth,
                alpha=alpha, zorder=1)

    # Draw nodes
    for node, (x, y) in positions.items():
        # Determine node color
        if node in communities['A']:
            base_color = 'lightblue'
            edge_color = 'darkblue'
        else:
            base_color = 'lightgreen'
            edge_color = 'darkgreen'

        # Highlight special roles
        node_size = 500
        edge_width = 2

        if node in highlight_nodes:
            if 'scapegoat' in phase_info and node == phase_info['scapegoat']:
                base_color = 'red'
                edge_color = 'darkred'
                edge_width = 4
                node_size = 700
            elif 'accuser' in phase_info and node == phase_info['accuser']:
                base_color = 'orange'
                edge_color = 'darkorange'
                edge_width = 4
                node_size = 700

        ax.scatter(x, y, s=node_size, c=base_color, edgecolors=edge_color,
                   linewidths=edge_width, zorder=2)

        # Node label
        ax.text(x, y, node, ha='center', va='center', fontsize=10,
                fontweight='bold', zorder=3)

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='lightblue', edgecolor='darkblue', label='Community A'),
        mpatches.Patch(facecolor='lightgreen', edgecolor='darkgreen', label='Community B'),
        mpatches.Patch(facecolor='red', edgecolor='darkred', label='Scapegoat'),
        mpatches.Patch(facecolor='orange', edgecolor='darkorange', label='Accuser'),
        plt.Line2D([0], [0], color='green', linewidth=2, label='Friendship'),
        plt.Line2D([0], [0], color='red', linewidth=2, label='Hostility'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8)


def generate_animation_frames(data):
    """
    Generate frames for escalation animation.

    Returns list of frame specs.
    """
    frames = []

    communities = data['initial']['communities']
    comm_a = communities['A']
    comm_b = communities['B']

    # Generate positions (same for all frames)
    positions = two_community_layout(comm_a, comm_b)

    # Frame 1-3: Initial state
    initial_edges = dict_to_graph_edges(data['initial']['graph'])

    for i in range(3):
        frames.append({
            'positions': positions,
            'edges': initial_edges,
            'phase_info': {
                'phase': 'Initial State',
                'title': 'Two Communities with Bridge',
                'highlight_nodes': [],
                'highlight_edge': None
            },
            'communities': communities
        })

    # Frame 4-6: Phase 1 - A0 accuses B0
    phase1_accuser = data['phase1']['accuser']
    phase1_scapegoat = data['phase1']['scapegoat']

    for i in range(3):
        frames.append({
            'positions': positions,
            'edges': initial_edges,
            'phase_info': {
                'phase': 'Phase 1: Initial Accusation',
                'title': f'{phase1_accuser} (A) accuses {phase1_scapegoat} (B)',
                'highlight_nodes': [phase1_accuser, phase1_scapegoat],
                'highlight_edge': (phase1_accuser, phase1_scapegoat),
                'scapegoat': phase1_scapegoat,
                'accuser': phase1_accuser
            },
            'communities': communities
        })

    # Frame 7-9: Phase 1 result - A unified, B defends
    phase1_edges = dict_to_graph_edges(data['phase1']['graph'])

    for i in range(3):
        frames.append({
            'positions': positions,
            'edges': phase1_edges,
            'phase_info': {
                'phase': 'Phase 1: Result',
                'title': 'Community A unified against B0, Community B defends',
                'highlight_nodes': [phase1_scapegoat],
                'highlight_edge': None,
                'scapegoat': phase1_scapegoat
            },
            'communities': communities
        })

    # Frame 10-12: Phase 2 - B1 retaliates against A1
    phase2_retaliator = data['phase2']['retaliator']
    phase2_scapegoat = data['phase2']['scapegoat']

    for i in range(3):
        frames.append({
            'positions': positions,
            'edges': phase1_edges,
            'phase_info': {
                'phase': 'Phase 2: Retaliation',
                'title': f'{phase2_retaliator} (B) retaliates against {phase2_scapegoat} (A)',
                'highlight_nodes': [phase2_retaliator, phase2_scapegoat],
                'highlight_edge': (phase2_retaliator, phase2_scapegoat),
                'scapegoat': phase2_scapegoat,
                'accuser': phase2_retaliator
            },
            'communities': communities
        })

    # Frame 13-15: Phase 2 result - B unified, A defends
    phase2_edges = dict_to_graph_edges(data['phase2']['graph'])

    for i in range(3):
        frames.append({
            'positions': positions,
            'edges': phase2_edges,
            'phase_info': {
                'phase': 'Phase 2: Result',
                'title': 'Community B unified against A1, Community A defends',
                'highlight_nodes': [phase2_scapegoat],
                'highlight_edge': None,
                'scapegoat': phase2_scapegoat
            },
            'communities': communities
        })

    # Frame 16-20: Final state - Mutual polarization
    for i in range(5):
        frames.append({
            'positions': positions,
            'edges': phase2_edges,
            'phase_info': {
                'phase': 'Final State',
                'title': 'MUTUAL POLARIZATION: A vs B',
                'highlight_nodes': [],
                'highlight_edge': None
            },
            'communities': communities
        })

    return frames


def animate_escalation(data_file, output_file, fps=2):
    """
    Create animated GIF of escalation cycle.

    Args:
        data_file: Path to escalation_cycle_data.json
        output_file: Path for output GIF
        fps: Frames per second
    """
    print(f"Loading data from {data_file}...")
    data = load_escalation_data(data_file)

    print("Generating animation frames...")
    frames = generate_animation_frames(data)

    print(f"Creating animation with {len(frames)} frames...")

    fig, ax = plt.subplots(figsize=(12, 8))

    def update_frame(frame_idx):
        frame = frames[frame_idx]
        create_frame(
            ax,
            frame['positions'],
            frame['edges'],
            frame['phase_info'],
            frame['communities']
        )

    anim = FuncAnimation(
        fig,
        update_frame,
        frames=len(frames),
        interval=1000/fps,
        repeat=True
    )

    print(f"Saving animation to {output_file}...")
    writer = PillowWriter(fps=fps)
    anim.save(output_file, writer=writer)

    print(f"✓ Animation saved!")
    plt.close()


def create_static_comparison(data_file, output_file):
    """
    Create static comparison showing initial, phase1, phase2, final.
    """
    print(f"Loading data from {data_file}...")
    data = load_escalation_data(data_file)

    communities = data['initial']['communities']
    positions = two_community_layout(communities['A'], communities['B'])

    # Create 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    # Frame 1: Initial
    create_frame(
        axes[0],
        positions,
        dict_to_graph_edges(data['initial']['graph']),
        {
            'phase': 'Initial State',
            'title': 'Two Communities with Bridge',
            'highlight_nodes': [],
            'highlight_edge': None
        },
        communities
    )

    # Frame 2: Phase 1
    create_frame(
        axes[1],
        positions,
        dict_to_graph_edges(data['phase1']['graph']),
        {
            'phase': 'Phase 1 Result',
            'title': f"A accuses {data['phase1']['scapegoat']}, B defends",
            'highlight_nodes': [data['phase1']['scapegoat']],
            'highlight_edge': None,
            'scapegoat': data['phase1']['scapegoat']
        },
        communities
    )

    # Frame 3: Phase 2
    create_frame(
        axes[2],
        positions,
        dict_to_graph_edges(data['phase2']['graph']),
        {
            'phase': 'Phase 2 Result',
            'title': f"B retaliates against {data['phase2']['scapegoat']}, A defends",
            'highlight_nodes': [data['phase2']['scapegoat']],
            'highlight_edge': None,
            'scapegoat': data['phase2']['scapegoat']
        },
        communities
    )

    # Frame 4: Final
    final_title = "Mutual Polarization: A vs B"
    if data['final']['mutual_polarization']:
        final_title += " ✓"

    create_frame(
        axes[3],
        positions,
        dict_to_graph_edges(data['phase2']['graph']),
        {
            'phase': 'Final State',
            'title': final_title,
            'highlight_nodes': [],
            'highlight_edge': None
        },
        communities
    )

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Static comparison saved to {output_file}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Visualize escalation cycle')
    parser.add_argument('data_file', help='Path to escalation_cycle_data.json')
    parser.add_argument('-o', '--output', default='output/escalation/escalation_animation.gif',
                        help='Output file path')
    parser.add_argument('--static', action='store_true',
                        help='Create static comparison instead of animation')
    parser.add_argument('--fps', type=float, default=2.0,
                        help='Frames per second (default: 2)')

    args = parser.parse_args()

    if args.static:
        output_file = args.output.replace('.gif', '_comparison.png')
        create_static_comparison(args.data_file, output_file)
    else:
        animate_escalation(args.data_file, args.output, fps=args.fps)


if __name__ == '__main__':
    main()
