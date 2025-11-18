#!/usr/bin/env python3
"""
Generate visualizations for performance analysis.
Creates plots without requiring matplotlib (using ASCII art if needed).
"""

import json
import os
import sys
import math


def load_results(results_dir: str):
    """Load results from JSON files."""
    results = {}
    files = {
        'large_sparse': 'large_sparse_results.json',
        'complete': 'complete_graph_results.json',
        'pathological': 'pathological_structures_results.json',
        'density': 'density_variation_results.json',
        'positivity': 'positivity_variation_results.json'
    }

    for key, filename in files.items():
        path = os.path.join(results_dir, filename)
        if os.path.exists(path):
            with open(path) as f:
                results[key] = json.load(f)
        else:
            results[key] = []

    return results


def ascii_bar_chart(data, labels, title, width=60):
    """Generate ASCII bar chart."""
    if not data:
        return f"{title}\nNo data available.\n"

    max_val = max(data)
    if max_val == 0:
        max_val = 1

    output = [f"\n{title}", "=" * width]

    for i, (label, value) in enumerate(zip(labels, data)):
        bar_length = int((value / max_val) * (width - 25))
        bar = '█' * bar_length
        output.append(f"{label[:15]:15} {bar} {value:.2f}")

    return '\n'.join(output)


def ascii_scatter_plot(x_data, y_data, title, x_label, y_label, log_scale=False):
    """Generate ASCII scatter plot."""
    if not x_data or not y_data:
        return f"{title}\nNo data available.\n"

    width = 70
    height = 20

    # Transform data if log scale
    if log_scale:
        x_plot = [math.log10(x) if x > 0 else 0 for x in x_data]
        y_plot = [math.log10(y) if y > 0 else 0 for y in y_data]
        x_label = f"log10({x_label})"
        y_label = f"log10({y_label})"
    else:
        x_plot = x_data
        y_plot = y_data

    x_min, x_max = min(x_plot), max(x_plot)
    y_min, y_max = min(y_plot), max(y_plot)

    # Avoid division by zero
    if x_max == x_min:
        x_max = x_min + 1
    if y_max == y_min:
        y_max = y_min + 1

    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Plot points
    for x, y in zip(x_plot, y_plot):
        col = int((x - x_min) / (x_max - x_min) * (width - 1))
        row = height - 1 - int((y - y_min) / (y_max - y_min) * (height - 1))
        if 0 <= row < height and 0 <= col < width:
            grid[row][col] = '●'

    # Build output
    output = [f"\n{title}", "=" * width]
    output.append(f"{y_label} (vertical) vs {x_label} (horizontal)")
    output.append("")

    # Y-axis and grid
    for i, row in enumerate(grid):
        y_val = y_max - (i / height) * (y_max - y_min)
        row_str = ''.join(row)
        if i % 5 == 0:
            output.append(f"{y_val:6.2f} |{row_str}|")
        else:
            output.append(f"       |{row_str}|")

    # X-axis
    output.append("       " + "-" * (width + 2))
    x_axis_labels = f"       {x_min:.2f}" + " " * (width - 15) + f"{x_max:.2f}"
    output.append(x_axis_labels)

    return '\n'.join(output)


def generate_visualizations(results_dir: str, output_file: str):
    """Generate all visualizations."""
    print("Loading results...")
    results = load_results(results_dir)

    output = []
    output.append("="*70)
    output.append("PERFORMANCE VISUALIZATION REPORT")
    output.append("Scapegoating Contagion Simulator")
    output.append("="*70)

    # 1. Sparse graph scaling (log-log plot)
    if results['large_sparse']:
        nodes = [r['graph']['num_nodes'] for r in results['large_sparse']]
        times = [r['timing']['simulation_time'] for r in results['large_sparse']]

        plot = ascii_scatter_plot(
            nodes, times,
            "SPARSE GRAPH SCALING (Log-Log)",
            "Nodes", "Time (seconds)",
            log_scale=True
        )
        output.append(plot)

        # Also linear scale
        plot2 = ascii_scatter_plot(
            nodes, times,
            "SPARSE GRAPH SCALING (Linear)",
            "Nodes", "Time (seconds)",
            log_scale=False
        )
        output.append(plot2)

    # 2. Complete graph scaling
    if results['complete']:
        nodes = [r['graph']['num_nodes'] for r in results['complete']]
        times = [r['timing']['simulation_time'] for r in results['complete']]

        plot = ascii_scatter_plot(
            nodes, times,
            "COMPLETE GRAPH SCALING (Log-Log)",
            "Nodes", "Time (seconds)",
            log_scale=True
        )
        output.append(plot)

    # 3. Decision counts across structures
    if results['pathological']:
        structures = [r.get('structure_type', 'unknown') for r in results['pathological']]
        decisions_per_node = [r['decisions']['decisions_per_node'] for r in results['pathological']]

        chart = ascii_bar_chart(
            decisions_per_node,
            structures,
            "DECISIONS PER NODE (Pathological Structures)"
        )
        output.append(chart)

    # 4. Density impact
    if results['density']:
        densities = [r.get('density_config', 'unknown') for r in results['density']]
        times = [r['timing']['simulation_time'] for r in results['density']]

        chart = ascii_bar_chart(
            times,
            densities,
            "SIMULATION TIME BY DENSITY (1000 nodes)"
        )
        output.append(chart)

    # 5. Positivity impact
    if results['positivity']:
        positivity = [r.get('p_positive', 0) for r in results['positivity']]
        decisions = [r['decisions']['total'] for r in results['positivity']]

        plot = ascii_scatter_plot(
            positivity, decisions,
            "DECISIONS vs EDGE POSITIVITY (1000 nodes)",
            "p_positive", "Total Decisions",
            log_scale=False
        )
        output.append(plot)

    # 6. Rule firing distribution
    if results['large_sparse']:
        avg_r1 = sum(r['decisions']['rule1_forced_choice'] for r in results['large_sparse']) / len(results['large_sparse'])
        avg_r2 = sum(r['decisions']['rule2_befriend_enemy'] for r in results['large_sparse']) / len(results['large_sparse'])
        avg_r3 = sum(r['decisions']['rule3_hear_accusation'] for r in results['large_sparse']) / len(results['large_sparse'])

        chart = ascii_bar_chart(
            [avg_r1, avg_r2, avg_r3],
            ["Rule 1 (Choice)", "Rule 2 (Befriend)", "Rule 3 (Hear)"],
            "AVERAGE RULE FIRING COUNTS (Sparse Graphs)"
        )
        output.append(chart)

    # 7. Memory usage
    if results['large_sparse']:
        nodes = [r['graph']['num_nodes'] for r in results['large_sparse']]
        memory = [r['memory']['peak_memory_mb'] for r in results['large_sparse']]

        plot = ascii_scatter_plot(
            nodes, memory,
            "MEMORY USAGE SCALING",
            "Nodes", "Memory (MB)",
            log_scale=False
        )
        output.append(plot)

    # 8. BFS depth distribution
    if results['large_sparse']:
        nodes = [r['graph']['num_nodes'] for r in results['large_sparse']]
        depths = [r['bfs']['depth'] for r in results['large_sparse']]

        plot = ascii_scatter_plot(
            nodes, depths,
            "BFS DEPTH SCALING",
            "Nodes", "Max BFS Depth",
            log_scale=False
        )
        output.append(plot)

    # Save visualizations
    viz_text = '\n'.join(output)
    with open(output_file, 'w') as f:
        f.write(viz_text)

    print(f"\n✓ Visualizations saved to: {output_file}")
    print("\n" + viz_text)

    return viz_text


def main():
    results_dir = "output/stress_tests"
    output_file = "output/stress_tests/visualizations.txt"

    if not os.path.exists(results_dir):
        print(f"Error: {results_dir} not found")
        return 1

    generate_visualizations(results_dir, output_file)
    return 0


if __name__ == '__main__':
    sys.exit(main())
