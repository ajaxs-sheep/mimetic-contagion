#!/usr/bin/env python3
"""
Visualize scapegoating contagion as 2D circular layout animation.
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


def create_frame(ax, nodes, edges, positions, step_info, highlight_edge=None,
                scapegoat=None, accusers=None, defenders=None):
    """
    Draw a single frame of the scapegoating contagion.

    Args:
        ax: Matplotlib axis
        nodes: List of node names
        edges: Dict of {(u,v): sign}
        positions: Dict of {node: (x, y)}
        step_info: Dict with step metadata
        highlight_edge: Edge tuple to highlight (if any)
        scapegoat: Name of scapegoat node
        accusers: Set of accuser nodes
        defenders: Set of defender nodes
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

    # Draw nodes with role-based colors
    for i, node in enumerate(nodes):
        x, y = positions[i]

        # Determine node color based on role
        node_color = 'white'
        edge_color = 'black'
        edge_width = 2

        if scapegoat and node == scapegoat:
            node_color = 'lightcoral'  # Scapegoat in red
            edge_color = 'darkred'
            edge_width = 3
        elif accusers and node in accusers:
            node_color = 'lightblue'  # Accusers in blue
            edge_color = 'darkblue'
            edge_width = 2
        elif defenders and node in defenders:
            node_color = 'lightgreen'  # Defenders in green
            edge_color = 'darkgreen'
            edge_width = 3

        ax.scatter(x, y, s=400, c=node_color, edgecolors=edge_color,
                  linewidths=edge_width, zorder=2)
        ax.text(x, y, node, ha='center', va='center', fontsize=9,
               fontweight='bold', zorder=3)

    # Add title and info
    step_type = step_info.get('step_type', 'step')
    actor = step_info.get('actor', '')
    action_desc = step_info.get('action_desc', '')

    if step_type == 'initial':
        title = "Initial State"
    elif step_type == 'accusation':
        title = f"ACCUSATION: {actor} accuses {scapegoat}"
    elif step_type == 'contagion':
        title = f"{actor}: {action_desc}"
    elif step_type == 'cleanup':
        title = f"COMMUNITY UNITY: {actor} {action_desc}"
    elif step_type == 'final':
        converged = step_info.get('converged', False)
        if converged:
            title = "✓ ORDER THROUGH VIOLENCE (complete unity)"
        else:
            title = "⚠ CONTAGION FAILED (defenders remain)"
    else:
        title = "Scapegoating Contagion"

    ax.text(0, 1.15, title, ha='center', va='center',
           fontsize=14, fontweight='bold')

    # Stats
    pos_edges = sum(1 for s in edges.values() if s == 1)
    neg_edges = sum(1 for s in edges.values() if s == -1)
    stats = f"Positive: {pos_edges} | Negative: {neg_edges}"

    if accusers:
        stats += f" | Accusers: {len(accusers)}"
    if defenders:
        stats += f" | Defenders: {len(defenders)}"

    ax.text(0, -1.15, stats, ha='center', va='center',
           fontsize=10, style='italic', color='gray')

    # Legend
    patches = [
        mpatches.Patch(color='green', label='Friendship (+)'),
        mpatches.Patch(color='red', label='Enmity (-)'),
    ]
    if scapegoat:
        patches.append(mpatches.Patch(color='lightcoral', label='Scapegoat'))
    if accusers:
        patches.append(mpatches.Patch(color='lightblue', label='Accuser'))
    if defenders and len(defenders) > 0:
        patches.append(mpatches.Patch(color='lightgreen', label='Defender'))

    ax.legend(handles=patches, loc='upper right',
             fontsize=8, framealpha=0.9)


def visualize_cascade(json_path, output_path=None, fps=2, pause_on_final=True):
    """
    Create visualization of scapegoating contagion.

    Args:
        json_path: Path to JSON cascade file
        output_path: Output file path (.gif or .mp4)
        fps: Frames per second for animation
        pause_on_final: If True, hold final frame for 3 seconds
    """
    # Load data
    print(f"Loading scapegoating contagion from {json_path}...", file=sys.stderr)
    data = load_cascade_json(json_path)

    # Extract info
    initial_state = data['initial_state']
    scapegoat = data['scapegoat']
    initial_accuser = data['initial_accuser']
    decisions = data['decisions']
    final_state = data['final_state']
    final_accusers = set(data['accusers'])
    final_defenders = set(data['defenders'])
    contagion_succeeded = data['contagion_succeeded']

    nodes = sorted(initial_state['nodes'])
    num_nodes = len(nodes)

    print(f"  Nodes: {num_nodes}", file=sys.stderr)
    print(f"  Scapegoat: {scapegoat}", file=sys.stderr)
    print(f"  Initial Accuser: {initial_accuser}", file=sys.stderr)
    print(f"  Decisions: {len(decisions)}", file=sys.stderr)
    print(f"  Contagion succeeded: {contagion_succeeded}", file=sys.stderr)

    # Create circular layout
    positions = circular_layout(num_nodes)

    # Prepare frames data
    frames_data = []

    # Initial state
    initial_edges = {}
    for edge_data in initial_state['edges']:
        u, v = edge_data['nodes']
        sign = edge_data['sign']
        initial_edges[(u, v)] = sign

    frames_data.append({
        'edges': initial_edges.copy(),
        'step_info': {
            'step_type': 'initial',
            'actor': '',
            'action_desc': ''
        },
        'highlight_edge': None,
        'scapegoat': None,
        'accusers': set(),
        'defenders': set()
    })

    # Accusation step
    current_edges = initial_edges.copy()
    accusers = {initial_accuser}

    # Find and flip accusation edge if needed
    accuser_scapegoat_edge = None
    for (u, v) in current_edges:
        if (u == initial_accuser and v == scapegoat) or (v == initial_accuser and u == scapegoat):
            accuser_scapegoat_edge = (u, v)
            if current_edges[accuser_scapegoat_edge] == 1:
                current_edges[accuser_scapegoat_edge] = -1
            break

    frames_data.append({
        'edges': current_edges.copy(),
        'step_info': {
            'step_type': 'accusation',
            'actor': initial_accuser,
            'action_desc': f'accuses {scapegoat}'
        },
        'highlight_edge': accuser_scapegoat_edge,
        'scapegoat': scapegoat,
        'accusers': accusers.copy(),
        'defenders': set()
    })

    # Add each contagion decision
    for decision in decisions:
        node = decision['node']
        action = decision['action']
        reason = decision['reason']

        if action:
            edge_flipped = tuple(decision['edge_flipped'])
            from_sign = decision['from_sign']
            to_sign = decision['to_sign']

            # Update edges
            current_edges[edge_flipped] = to_sign

            # Determine step type and description
            is_cleanup = 'Community unity' in reason
            step_type = 'cleanup' if is_cleanup else 'contagion'

            # Update accusers if joining
            if action == 'join_accusers':
                accusers.add(node)
                action_desc = f"joins accusers (chose against {scapegoat})"
            elif action == 'hear_accusation':
                accusers.add(node)
                action_desc = f"hears about {scapegoat}, forms negative opinion"
            elif action == 'befriend_other':
                if is_cleanup:
                    action_desc = f"befriends enemy (community unity)"
                else:
                    action_desc = f"resolves --- triangle"
            else:
                action_desc = reason

            frames_data.append({
                'edges': current_edges.copy(),
                'step_info': {
                    'step_type': step_type,
                    'actor': node,
                    'action_desc': action_desc
                },
                'highlight_edge': edge_flipped,
                'scapegoat': scapegoat,
                'accusers': accusers.copy(),
                'defenders': set()
            })
        else:
            # No action (defender or neutral)
            frames_data.append({
                'edges': current_edges.copy(),
                'step_info': {
                    'step_type': 'contagion',
                    'actor': node,
                    'action_desc': reason
                },
                'highlight_edge': None,
                'scapegoat': scapegoat,
                'accusers': accusers.copy(),
                'defenders': {node} if 'Defender' in reason else set()
            })

    # Final state (hold for emphasis)
    final_step_info = {
        'step_type': 'final',
        'actor': '',
        'action_desc': '',
        'converged': contagion_succeeded
    }

    # Add final frame (repeat 3x for pause effect if requested)
    repeat_count = int(fps * 3) if pause_on_final else 1
    for _ in range(repeat_count):
        frames_data.append({
            'edges': current_edges.copy(),
            'step_info': final_step_info,
            'highlight_edge': None,
            'scapegoat': scapegoat,
            'accusers': final_accusers,
            'defenders': final_defenders
        })

    print(f"  Frames: {len(frames_data)}", file=sys.stderr)

    # Create animation
    fig, ax = plt.subplots(figsize=(10, 10))

    def update(frame_idx):
        frame = frames_data[frame_idx]
        create_frame(ax, nodes, frame['edges'], positions,
                    frame['step_info'], frame['highlight_edge'],
                    frame['scapegoat'], frame['accusers'], frame['defenders'])
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
        description="Visualize scapegoating contagion as 2D circular layout animation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create GIF animation of scapegoating contagion
  python visualize_cascade.py /tmp/Alice-Betty-Charlie-David_Betty-scapegoat_Alice-accuser_seed42_json.json -o contagion.gif

  # Faster playback (4 fps)
  python visualize_cascade.py cascade.json -o contagion.gif --fps 4

  # Just display without saving
  python visualize_cascade.py cascade.json

  # No pause on final frame
  python visualize_cascade.py cascade.json -o contagion.gif --no-pause
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
        '--no-pause',
        action='store_true',
        help='Do not pause on final frame'
    )

    args = parser.parse_args()

    # Validate input file
    if not Path(args.json_file).exists():
        print(f"Error: File not found: {args.json_file}", file=sys.stderr)
        sys.exit(1)

    # Validate output format
    if args.output and not (args.output.endswith('.gif') or args.output.endswith('.mp4')):
        print("Error: Output must be .gif or .mp4 format", file=sys.stderr)
        sys.exit(1)

    visualize_cascade(
        args.json_file,
        args.output,
        args.fps,
        pause_on_final=not args.no_pause
    )


if __name__ == '__main__':
    main()
