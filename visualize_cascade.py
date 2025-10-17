#!/usr/bin/env python3
"""
Visualize mimetic cascade as 2D circular layout animation.
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


def circular_layout(num_nodes):
    """Generate circular layout positions for nodes."""
    positions = {}
    radius = 1.0
    for i in range(num_nodes):
        angle = 2 * math.pi * i / num_nodes
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions[i] = (x, y)
    return positions


def load_cascade_json(filepath):
    """Load cascade data from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def create_frame(ax, nodes, edges, positions, step_info, highlight_edge=None):
    """
    Draw a single frame of the cascade.

    Args:
        ax: Matplotlib axis
        nodes: List of node names
        edges: Dict of {(u,v): sign}
        positions: Dict of {node: (x, y)}
        step_info: Dict with step metadata
        highlight_edge: Edge tuple to highlight (if any)
    """
    ax.clear()
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect('equal')
    ax.axis('off')

    # Node name to index mapping
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # Draw edges
    for (u, v), sign in edges.items():
        if u not in node_to_idx or v not in node_to_idx:
            continue

        u_idx = node_to_idx[u]
        v_idx = node_to_idx[v]
        x1, y1 = positions[u_idx]
        x2, y2 = positions[v_idx]

        # Edge color and style
        color = 'green' if sign == 1 else 'red'
        linewidth = 1.5
        alpha = 0.4

        # Highlight the edge that just flipped
        if highlight_edge and ((u, v) == highlight_edge or (v, u) == highlight_edge):
            linewidth = 4
            alpha = 1.0
            color = 'gold' if sign == 1 else 'orange'

        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth,
                alpha=alpha, zorder=1)

    # Draw nodes
    for i, node in enumerate(nodes):
        x, y = positions[i]
        ax.scatter(x, y, s=300, c='white', edgecolors='black',
                  linewidths=2, zorder=2)
        ax.text(x, y, node, ha='center', va='center', fontsize=8,
               fontweight='bold', zorder=3)

    # Add title and info
    step_num = step_info.get('step', 0)
    actor = step_info.get('actor', '')
    edge_flip = step_info.get('edge_flip', '')
    pressured = step_info.get('pressured', 0)
    converged = step_info.get('converged', False)

    if step_num == 'Initial':
        title = "Initial State (Perfect Harmony)"
    elif step_num == 'PERTURB':
        title = f"PERTURBATION: {edge_flip} becomes hostile"
    elif converged:
        title = f"✓ CONVERGED (Step {step_num})"
    else:
        title = f"Step {step_num}: {actor} flips {edge_flip}"

    ax.text(0, 1.15, title, ha='center', va='center',
           fontsize=14, fontweight='bold')

    # Stats
    pos_edges = sum(1 for s in edges.values() if s == 1)
    neg_edges = sum(1 for s in edges.values() if s == -1)
    stats = f"Positive: {pos_edges} | Negative: {neg_edges}"
    if pressured > 0:
        stats += f" | Pressured: {pressured}"

    ax.text(0, -1.15, stats, ha='center', va='center',
           fontsize=10, style='italic', color='gray')

    # Legend
    green_patch = mpatches.Patch(color='green', label='Friendship (+)')
    red_patch = mpatches.Patch(color='red', label='Enmity (-)')
    ax.legend(handles=[green_patch, red_patch], loc='upper right',
             fontsize=8, framealpha=0.9)


def visualize_cascade(json_path, output_path=None, fps=2, show_all_steps=False,
                     key_steps_only=False):
    """
    Create visualization of cascade.

    Args:
        json_path: Path to JSON cascade file
        output_path: Output file path (.gif or .mp4)
        fps: Frames per second for animation
        show_all_steps: If True, show every single step
        key_steps_only: If True, only show initial, key moments, and final
    """
    # Load data
    print(f"Loading cascade from {json_path}...", file=sys.stderr)
    data = load_cascade_json(json_path)

    # Extract info
    initial_state = data['initial_state']
    cascade_steps = data['cascade']
    final_state = data['final_state']
    converged = data['converged']

    nodes = sorted(initial_state['nodes'])
    num_nodes = len(nodes)

    print(f"  Nodes: {num_nodes}", file=sys.stderr)
    print(f"  Steps: {len(cascade_steps)}", file=sys.stderr)
    print(f"  Converged: {converged}", file=sys.stderr)

    # Create circular layout
    positions = circular_layout(num_nodes)

    # Prepare frames data
    frames_data = []

    # Initial state (before perturbation)
    initial_edges = {}
    for edge_data in initial_state['edges']:
        u, v = edge_data['nodes']
        sign = edge_data['sign']
        initial_edges[(u, v)] = sign

    frames_data.append({
        'edges': initial_edges.copy(),
        'step_info': {
            'step': 'Initial',
            'actor': '',
            'edge_flip': '',
            'pressured': 0,
            'converged': False
        },
        'highlight_edge': None
    })

    # Perturbation step (if present)
    current_edges = initial_edges.copy()

    perturbation = data.get('perturbation')
    if perturbation:
        perturb_edge = tuple(perturbation['edge'])
        from_sign = perturbation['from_sign']
        to_sign = perturbation['to_sign']

        # Apply perturbation
        current_edges[perturb_edge] = to_sign

        frames_data.append({
            'edges': current_edges.copy(),
            'step_info': {
                'step': 'PERTURB',
                'actor': 'Initial',
                'edge_flip': f"{perturb_edge[0]}↔{perturb_edge[1]}",
                'pressured': 0,
                'converged': False
            },
            'highlight_edge': perturb_edge
        })

    # Add each cascade step

    for i, step in enumerate(cascade_steps):
        step_num = step['step']
        actor = step['actor']

        if step.get('stuck'):
            # Skip stuck steps in visualization
            continue

        edge = tuple(step['edge']) if step['edge'] else None
        to_sign = step['to_sign']

        if edge:
            # Update edges
            current_edges[edge] = to_sign
            edge_str = f"{edge[0]}↔{edge[1]}"
        else:
            edge_str = "STUCK"

        # Decide if we should include this frame
        include = True
        if key_steps_only:
            # Only include first 5, then every 10th, then last 5
            total = len(cascade_steps)
            if not (i < 5 or i > total - 5 or i % 10 == 0):
                include = False
        elif not show_all_steps:
            # Show every 5th step for medium-length cascades
            if len(cascade_steps) > 50 and i % 5 != 0 and i != len(cascade_steps) - 1:
                include = False

        if include:
            frames_data.append({
                'edges': current_edges.copy(),
                'step_info': {
                    'step': step_num,
                    'actor': actor,
                    'edge_flip': edge_str,
                    'pressured': len(step.get('new_pressured', [])),
                    'converged': False
                },
                'highlight_edge': edge
            })

    # Final state
    frames_data.append({
        'edges': current_edges.copy(),
        'step_info': {
            'step': len(cascade_steps),
            'actor': '',
            'edge_flip': '',
            'pressured': 0,
            'converged': converged
        },
        'highlight_edge': None
    })

    print(f"  Frames: {len(frames_data)}", file=sys.stderr)

    # Create animation
    fig, ax = plt.subplots(figsize=(10, 10))

    def update(frame_idx):
        frame = frames_data[frame_idx]
        create_frame(ax, nodes, frame['edges'], positions,
                    frame['step_info'], frame['highlight_edge'])
        return ax,

    anim = FuncAnimation(fig, update, frames=len(frames_data),
                        interval=1000/fps, blit=False, repeat=True)

    # Save or show
    if output_path:
        print(f"Saving animation to {output_path}...", file=sys.stderr)
        if output_path.endswith('.gif'):
            writer = PillowWriter(fps=fps)
            anim.save(output_path, writer=writer)
        elif output_path.endswith('.mp4'):
            anim.save(output_path, fps=fps, extra_args=['-vcodec', 'libx264'])
        print(f"✓ Saved to {output_path}", file=sys.stderr)
    else:
        print("Showing animation... (close window to exit)", file=sys.stderr)
        plt.show()

    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize mimetic cascade as 2D circular layout animation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create GIF animation (2 fps, smart frame selection)
  python visualize_cascade.py output/harmony_20_n0-n1_seed42_json.json -o cascade.gif

  # Show every single step (slower, more frames)
  python visualize_cascade.py output/harmony_20_n0-n1_seed42_json.json -o cascade.gif --all-steps

  # Show only key moments (faster, fewer frames)
  python visualize_cascade.py output/harmony_20_n0-n1_seed42_json.json -o cascade.gif --key-steps

  # Faster playback (4 fps)
  python visualize_cascade.py output/harmony_20_n0-n1_seed42_json.json -o cascade.gif --fps 4

  # Just display without saving
  python visualize_cascade.py output/harmony_20_n0-n1_seed42_json.json
        """
    )

    parser.add_argument(
        'json_file',
        help='Path to JSON cascade file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file path (.gif). If not provided, displays interactively.'
    )

    parser.add_argument(
        '--fps',
        type=float,
        default=2,
        help='Frames per second (default: 2)'
    )

    parser.add_argument(
        '--all-steps',
        action='store_true',
        help='Show every single step (many frames)'
    )

    parser.add_argument(
        '--key-steps',
        action='store_true',
        help='Show only key moments (fewer frames)'
    )

    args = parser.parse_args()

    # Validate input file
    if not Path(args.json_file).exists():
        print(f"Error: File not found: {args.json_file}", file=sys.stderr)
        sys.exit(1)

    # Validate output format
    if args.output and not args.output.endswith('.gif'):
        print("Error: Output must be .gif format", file=sys.stderr)
        sys.exit(1)

    visualize_cascade(
        args.json_file,
        args.output,
        args.fps,
        args.all_steps,
        args.key_steps
    )


if __name__ == '__main__':
    main()
