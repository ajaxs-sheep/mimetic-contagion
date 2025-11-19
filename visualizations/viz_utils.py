#!/usr/bin/env python3
"""
Shared utilities for creating scapegoating visualizations.

Provides common layout algorithms, color schemes, and animation functions
used across all visualization scripts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
import math
import numpy as np


# ==================== COLOR SCHEMES ====================

NODE_COLORS = {
    'normal': '#95A5A6',        # Gray - uninvolved/defenders
    'accuser': '#FF8C00',       # Orange - initial accuser (DISTINCT)
    'accusers': '#E74C3C',      # Red - mob (nodes who joined)
    'defender': '#95A5A6',      # Gray - defenders
    'scapegoat': '#000000',     # BLACK - the scapegoat (MOST PROMINENT)
    'unreachable': '#D3D3D3',   # Light gray - never heard about it
}

EDGE_COLORS = {
    'positive': '#2ECC71',      # Green - friendship
    'negative': '#E74C3C',      # Red - hostility
    'neutral': '#CCCCCC',       # Light gray - absent
}

COMMUNITY_COLORS = {
    'A': '#4A90E2',  # Blue
    'B': '#2ECC71',  # Green
    'C': '#9B59B6',  # Purple
}


# ==================== LAYOUT ALGORITHMS ====================

def circular_layout(nodes, radius=1.0, center=(0, 0)):
    """
    Arrange nodes in a circle.

    Args:
        nodes: List of node names
        radius: Circle radius
        center: (x, y) center point

    Returns:
        dict: {node: (x, y)}
    """
    positions = {}
    n = len(nodes)

    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        positions[node] = (x, y)

    return positions


def star_layout(hub, periphery, hub_pos=(0, 0), radius=1.0):
    """
    Arrange nodes in star topology (hub at center, periphery in circle).

    Args:
        hub: Hub node name
        periphery: List of peripheral node names
        hub_pos: (x, y) position of hub
        radius: Distance of periphery from hub

    Returns:
        dict: {node: (x, y)}
    """
    positions = {hub: hub_pos}

    n = len(periphery)
    for i, node in enumerate(periphery):
        angle = 2 * math.pi * i / n
        x = hub_pos[0] + radius * math.cos(angle)
        y = hub_pos[1] + radius * math.sin(angle)
        positions[node] = (x, y)

    return positions


def linear_layout(nodes, spacing=1.0, horizontal=True):
    """
    Arrange nodes in a line.

    Args:
        nodes: List of node names
        spacing: Distance between consecutive nodes
        horizontal: If True, arrange horizontally, else vertically

    Returns:
        dict: {node: (x, y)}
    """
    positions = {}

    for i, node in enumerate(nodes):
        if horizontal:
            positions[node] = (i * spacing, 0)
        else:
            positions[node] = (0, i * spacing)

    return positions


def two_community_layout(comm_a, comm_b, separation=2.0, radius=1.0):
    """
    Arrange two communities facing each other (semicircles).

    Args:
        comm_a: List of community A node names
        comm_b: List of community B node names
        separation: Distance between community centers
        radius: Radius of each semicircle

    Returns:
        dict: {node: (x, y)}
    """
    positions = {}

    # Community A: Left semicircle
    center_a_x = -separation / 2
    for i, node in enumerate(comm_a):
        angle = math.pi/6 + (2*math.pi/3) * i / max(len(comm_a)-1, 1)
        x = center_a_x + radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions[node] = (x, y)

    # Community B: Right semicircle
    center_b_x = separation / 2
    for i, node in enumerate(comm_b):
        angle = math.pi - math.pi/6 - (2*math.pi/3) * i / max(len(comm_b)-1, 1)
        x = center_b_x + radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions[node] = (x, y)

    return positions


def force_directed_layout(graph, iterations=50, k=None):
    """
    Simple spring layout with better stability.

    Args:
        graph: SignedGraph instance
        iterations: Number of iterations
        k: Optimal distance between nodes (auto-calculated if None)

    Returns:
        dict: {node: (x, y)}
    """
    nodes = list(graph.nodes)
    n = len(nodes)

    # Initialize positions in a circle to avoid overlaps
    np.random.seed(42)
    positions = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        positions[node] = (math.cos(angle), math.sin(angle))

    # Calculate optimal distance
    if k is None:
        k = 1.0 / math.sqrt(n)

    # Temperature for cooling
    temp = 1.0
    dt = temp / (iterations + 1)

    for iteration in range(iterations):
        # Calculate forces
        forces = {node: np.array([0.0, 0.0]) for node in nodes}

        for i, u in enumerate(nodes):
            for j, v in enumerate(nodes):
                if i >= j:
                    continue

                pos_u = np.array(positions[u])
                pos_v = np.array(positions[v])
                delta = pos_u - pos_v
                dist = np.linalg.norm(delta)

                # Avoid division by zero
                if dist < 0.01:
                    dist = 0.01
                    delta = np.array([np.random.rand() - 0.5, np.random.rand() - 0.5])
                    delta = delta / np.linalg.norm(delta) * 0.01

                # Repulsive force (all pairs)
                repulsive = (k * k / (dist * dist)) * (delta / dist)
                forces[u] += repulsive
                forces[v] -= repulsive

                # Attractive force (only if connected)
                if graph.has_edge(u, v):
                    attractive = (dist * dist / k) * (delta / dist)
                    forces[u] -= attractive * 0.5
                    forces[v] += attractive * 0.5

        # Update positions with damping
        max_displacement = 0
        for node in nodes:
            force = forces[node]
            force_magnitude = np.linalg.norm(force)

            # Limit displacement
            if force_magnitude > 0:
                displacement = min(force_magnitude * temp, 0.1) * (force / force_magnitude)
                positions[node] = tuple(np.array(positions[node]) + displacement)
                max_displacement = max(max_displacement, np.linalg.norm(displacement))

        # Cool down
        temp -= dt

        # Early stopping if converged
        if max_displacement < 0.001:
            break

    # Normalize to fit in reasonable bounds
    x_coords = [pos[0] for pos in positions.values()]
    y_coords = [pos[1] for pos in positions.values()]

    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    # Scale to [-1, 1] range
    if max_x > min_x and max_y > min_y:
        for node in nodes:
            x, y = positions[node]
            x_norm = 2 * (x - min_x) / (max_x - min_x) - 1
            y_norm = 2 * (y - min_y) / (max_y - min_y) - 1
            positions[node] = (x_norm, y_norm)

    return positions


# ==================== DRAWING FUNCTIONS ====================

def draw_graph_state(ax, graph, positions, accusers, defenders, scapegoat,
                     initial_accuser=None, unreachable=None, communities=None,
                     title=None, show_legend=True, show_metrics=False, legend_loc='upper right'):
    """
    Draw graph state with color-coded nodes and edges.

    Args:
        ax: Matplotlib axes
        graph: SignedGraph instance
        positions: dict {node: (x, y)}
        accusers: set of accuser nodes
        defenders: set of defender nodes
        scapegoat: scapegoat node
        initial_accuser: initial accuser (optional, highlighted differently)
        unreachable: set of unreachable nodes (optional)
        communities: dict {community_name: [nodes]} (optional)
        title: Plot title (optional)
        show_legend: Show legend (default True)
        show_metrics: Show metrics overlay (default False)
        legend_loc: Legend location (default 'upper right')
    """
    ax.clear()
    ax.set_aspect('equal')
    ax.axis('off')

    # Set reasonable axis limits to ensure everything is visible
    x_coords = [pos[0] for pos in positions.values()]
    y_coords = [pos[1] for pos in positions.values()]
    margin = 0.5
    ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
    ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)

    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=15)

    # Draw edges
    for u in graph.nodes:
        for v in graph.neighbors(u):
            if u < v:  # Draw each edge only once
                x = [positions[u][0], positions[v][0]]
                y = [positions[u][1], positions[v][1]]

                edge_sign = graph.get_edge(u, v)
                if edge_sign == 1:
                    color = EDGE_COLORS['positive']
                    style = '-'
                    width = 1.5
                elif edge_sign == -1:
                    color = EDGE_COLORS['negative']
                    style = '-'
                    width = 2.0
                else:
                    color = EDGE_COLORS['neutral']
                    style = '--'
                    width = 0.5

                ax.plot(x, y, color=color, linestyle=style, linewidth=width,
                       zorder=1, alpha=0.7)

    # Draw nodes
    for node in graph.nodes:
        x, y = positions[node]

        # Determine node color
        if node == scapegoat:
            color = NODE_COLORS['scapegoat']
            size = 800
        elif unreachable and node in unreachable:
            color = NODE_COLORS['unreachable']
            size = 600
        elif node == initial_accuser:
            color = NODE_COLORS['accuser']
            size = 700
        elif node in accusers:
            color = NODE_COLORS['accusers']
            size = 700
        elif node in defenders:
            color = NODE_COLORS['defender']
            size = 700
        else:
            color = NODE_COLORS['normal']
            size = 600

        # Community border
        if communities:
            for comm_name, comm_nodes in communities.items():
                if node in comm_nodes:
                    edge_color = COMMUNITY_COLORS.get(comm_name, 'black')
                    edge_width = 2
                    break
            else:
                edge_color = 'black'
                edge_width = 1
        else:
            edge_color = 'black'
            edge_width = 1

        ax.scatter([x], [y], s=size, c=[color], edgecolors=edge_color,
                  linewidths=edge_width, zorder=2)

        # Node label
        label_color = 'white' if node == scapegoat or node in accusers or node == initial_accuser else 'black'
        ax.text(x, y, node, fontsize=10, fontweight='bold',
               ha='center', va='center', color=label_color, zorder=3)

        # Role label below node
        if node == scapegoat:
            ax.text(x, y - 0.25, 'SCAPEGOAT', fontsize=7, fontweight='bold',
                   ha='center', va='top', color='black',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8, edgecolor='black'))
        elif node == initial_accuser:
            ax.text(x, y - 0.25, 'ACCUSER', fontsize=7, fontweight='bold',
                   ha='center', va='top', color='darkorange',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='darkorange'))

    # Add legend if requested
    if show_legend:
        create_legend(ax, show_communities=communities is not None, loc=legend_loc)

    # Add metrics if requested
    if show_metrics:
        total_nodes = len(graph.nodes) - 1
        num_accusers = len(accusers) - 1 if scapegoat in accusers else len(accusers)
        num_defenders = len(defenders)
        add_metrics_overlay(ax, num_accusers, num_defenders, total_nodes, scapegoat)


def create_legend(ax, show_communities=False, loc='upper right'):
    """
    Add simple legend to axes.

    Args:
        ax: Matplotlib axes
        show_communities: Whether to show community info
        loc: Legend location (default 'upper right')
    """
    legend_elements = [
        mpatches.Patch(color=NODE_COLORS['scapegoat'], label='Scapegoat'),
        mpatches.Patch(color=NODE_COLORS['accuser'], label='Accuser'),
        mpatches.Patch(color=NODE_COLORS['accusers'], label='Mob (joined)'),
        mpatches.Patch(color=NODE_COLORS['normal'], label='Neutral/Defender'),
        mpatches.Patch(color=EDGE_COLORS['positive'], label='Friendship'),
        mpatches.Patch(color=EDGE_COLORS['negative'], label='Hostility'),
    ]

    # Position legend to avoid covering nodes
    ax.legend(handles=legend_elements, loc=loc, fontsize=8,
             framealpha=0.95, edgecolor='black')


def add_metrics_overlay(ax, accusers, defenders, total_nodes, scapegoat):
    """
    Add text overlay showing unity metrics.

    Args:
        ax: Matplotlib axes
        accusers: Number of accusers (excluding scapegoat)
        defenders: Number of defenders
        total_nodes: Total number of nodes (excluding scapegoat)
        scapegoat: Scapegoat node name
    """
    unity_pct = 100 * accusers / total_nodes if total_nodes > 0 else 0

    text = f"{accusers}/{total_nodes} accusers ({unity_pct:.0f}%)"

    ax.text(0.02, 0.02, text, transform=ax.transAxes,
           fontsize=11, verticalalignment='bottom',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))


# ==================== ANIMATION FUNCTIONS ====================

def animate_contagion(graph_states, positions, decisions, scapegoat,
                     initial_accuser, output_path, fps=2, communities=None):
    """
    Create animated GIF of contagion process.

    Args:
        graph_states: List of (graph, accusers, defenders) tuples for each frame
        positions: dict {node: (x, y)}
        decisions: List of decision objects from simulator
        scapegoat: Scapegoat node name
        initial_accuser: Initial accuser node name
        output_path: Output file path (.gif)
        fps: Frames per second
        communities: Optional dict {community_name: [nodes]}
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    def update(frame_num):
        if frame_num < len(graph_states):
            graph, accusers, defenders = graph_states[frame_num]

            # Determine unreachable nodes (never heard)
            heard = accusers | defenders | {scapegoat}
            unreachable = set(graph.nodes) - heard

            # Title with step number
            if frame_num == 0:
                title = "Initial State"
            elif frame_num == len(graph_states) - 1:
                title = "Final State"
            else:
                title = f"Step {frame_num}"

            draw_graph_state(ax, graph, positions, accusers, defenders,
                           scapegoat, initial_accuser, unreachable,
                           communities, title)

            # Add metrics
            total_nodes = len(graph.nodes) - 1  # Exclude scapegoat
            add_metrics_overlay(ax, len(accusers) - 1, len(defenders),
                              total_nodes, scapegoat)

    # Create animation
    anim = FuncAnimation(fig, update, frames=len(graph_states),
                        interval=1000/fps, repeat=True)

    # Save as GIF
    writer = PillowWriter(fps=fps)
    anim.save(output_path, writer=writer)
    plt.close(fig)

    print(f"Animation saved to: {output_path}")


def create_comparison_grid(images_data, output_path, titles=None):
    """
    Create side-by-side comparison grid of scenarios.

    Args:
        images_data: List of (graph, positions, accusers, defenders, scapegoat, initial_accuser) tuples
        output_path: Output file path (.png)
        titles: List of titles for each subplot (optional)
    """
    n = len(images_data)

    # Determine grid dimensions
    if n <= 2:
        rows, cols = 1, n
    elif n <= 4:
        rows, cols = 2, 2
    elif n <= 6:
        rows, cols = 2, 3
    else:
        rows = math.ceil(math.sqrt(n))
        cols = math.ceil(n / rows)

    fig, axes = plt.subplots(rows, cols, figsize=(7*cols, 6*rows))

    # Flatten axes array for easy iteration
    if n == 1:
        axes = [axes]
    elif rows == 1 or cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()

    for idx, (graph, positions, accusers, defenders, scapegoat, initial_accuser) in enumerate(images_data):
        ax = axes[idx]

        # Determine unreachable
        heard = accusers | defenders | {scapegoat}
        unreachable = set(graph.nodes) - heard

        title = titles[idx] if titles and idx < len(titles) else f"Scenario {idx+1}"

        draw_graph_state(ax, graph, positions, accusers, defenders,
                        scapegoat, initial_accuser, unreachable, None, title,
                        show_legend=False, show_metrics=False)

    # Hide unused subplots
    for idx in range(n, len(axes)):
        axes[idx].axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"Comparison grid saved to: {output_path}")


# ==================== GRAPH GENERATION HELPERS ====================

def create_complete_graph_nodes(node_names):
    """
    Create complete graph (all positive edges) from node names.

    Args:
        node_names: List of node names

    Returns:
        SignedGraph with all positive edges
    """
    from src.graph import SignedGraph

    graph = SignedGraph()

    for node in node_names:
        graph.add_node(node)

    for i, u in enumerate(node_names):
        for v in node_names[i+1:]:
            graph.add_edge(u, v, 1)

    return graph


def create_star_graph(hub_name, peripheral_names):
    """
    Create star graph (hub connected to all peripherals).

    Args:
        hub_name: Hub node name
        peripheral_names: List of peripheral node names

    Returns:
        SignedGraph with star topology
    """
    from src.graph import SignedGraph

    graph = SignedGraph()

    graph.add_node(hub_name)
    for node in peripheral_names:
        graph.add_node(node)
        graph.add_edge(hub_name, node, 1)

    return graph


def create_chain_graph(node_names):
    """
    Create chain graph (linear).

    Args:
        node_names: List of node names (in chain order)

    Returns:
        SignedGraph with chain topology
    """
    from src.graph import SignedGraph

    graph = SignedGraph()

    for node in node_names:
        graph.add_node(node)

    for i in range(len(node_names) - 1):
        graph.add_edge(node_names[i], node_names[i+1], 1)

    return graph
