#!/usr/bin/env python3
"""
Analyze performance results and generate comprehensive report.
"""

import json
import os
import sys
from collections import defaultdict
from typing import List, Dict, Any
import math


def load_results(results_dir: str) -> Dict[str, List[Dict]]:
    """Load all test results from JSON files."""
    results = {}

    result_files = {
        'large_sparse': 'large_sparse_results.json',
        'complete_graphs': 'complete_graph_results.json',
        'pathological': 'pathological_structures_results.json',
        'density': 'density_variation_results.json',
        'positivity': 'positivity_variation_results.json'
    }

    for key, filename in result_files.items():
        filepath = os.path.join(results_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Handle both list of metrics objects and list of dicts
                if isinstance(data, list) and len(data) > 0:
                    # If first element is PerformanceMetrics object, it's already converted
                    results[key] = data
                else:
                    results[key] = []
        else:
            print(f"Warning: {filepath} not found")
            results[key] = []

    return results


def analyze_scaling_complexity(results: List[Dict]) -> Dict[str, Any]:
    """
    Analyze time complexity from empirical data.
    Use log-log regression to estimate O() notation.
    """
    if len(results) < 2:
        return {'error': 'Insufficient data points'}

    # Extract (nodes, time) pairs
    data_points = [(r['graph']['num_nodes'], r['timing']['simulation_time']) for r in results]
    data_points.sort()

    # Log-log regression: log(T) = a * log(N) + b
    # If a ≈ 1: O(N), a ≈ 2: O(N²), a ≈ 3: O(N³)
    n_values = [p[0] for p in data_points]
    t_values = [p[1] for p in data_points]

    # Avoid log(0)
    if any(t <= 0 for t in t_values) or any(n <= 0 for n in n_values):
        return {'error': 'Invalid data (non-positive values)'}

    # Simple log-log regression
    log_n = [math.log(n) for n in n_values]
    log_t = [math.log(t) for t in t_values]

    n_count = len(log_n)
    sum_log_n = sum(log_n)
    sum_log_t = sum(log_t)
    sum_log_n_sq = sum(x * x for x in log_n)
    sum_log_n_log_t = sum(log_n[i] * log_t[i] for i in range(n_count))

    # Slope a = (n * sum(xy) - sum(x) * sum(y)) / (n * sum(x²) - sum(x)²)
    denominator = n_count * sum_log_n_sq - sum_log_n ** 2
    if abs(denominator) < 1e-10:
        return {'error': 'Cannot compute regression (singular matrix)'}

    slope = (n_count * sum_log_n_log_t - sum_log_n * sum_log_t) / denominator
    intercept = (sum_log_t - slope * sum_log_n) / n_count

    # Estimate complexity class
    if slope < 1.2:
        complexity_class = "O(N) or O(N log N)"
    elif slope < 1.7:
        complexity_class = "O(N^1.5)"
    elif slope < 2.5:
        complexity_class = "O(N²)"
    elif slope < 3.5:
        complexity_class = "O(N³)"
    else:
        complexity_class = f"O(N^{slope:.1f})"

    return {
        'data_points': data_points,
        'log_log_slope': round(slope, 3),
        'log_log_intercept': round(intercept, 3),
        'estimated_complexity': complexity_class,
        'r_squared': calculate_r_squared(log_n, log_t, slope, intercept)
    }


def calculate_r_squared(x_values, y_values, slope, intercept):
    """Calculate R² (coefficient of determination) for linear fit."""
    n = len(y_values)
    y_mean = sum(y_values) / n

    # Predicted values
    y_pred = [slope * x + intercept for x in x_values]

    # Total sum of squares
    ss_tot = sum((y - y_mean) ** 2 for y in y_values)

    # Residual sum of squares
    ss_res = sum((y_values[i] - y_pred[i]) ** 2 for i in range(n))

    if ss_tot == 0:
        return 0.0

    r_squared = 1 - (ss_res / ss_tot)
    return round(r_squared, 4)


def analyze_best_worst_cases(all_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """
    Identify best and worst case scenarios.
    """
    all_metrics = []

    for category, results in all_results.items():
        for r in results:
            metric = {
                'category': category,
                'nodes': r['graph']['num_nodes'],
                'edges': r['graph']['num_edges'],
                'avg_degree': r['graph']['avg_degree'],
                'simulation_time': r['timing']['simulation_time'],
                'decisions': r['decisions']['total'],
                'decisions_per_node': r['decisions']['decisions_per_node'],
                'bfs_depth': r['bfs']['depth'],
                'memory_mb': r['memory']['peak_memory_mb']
            }

            # Add category-specific info
            if 'structure_type' in r:
                metric['structure'] = r['structure_type']
            if 'density_config' in r:
                metric['density'] = r['density_config']
            if 'p_positive' in r:
                metric['positivity'] = r['p_positive']

            all_metrics.append(metric)

    if not all_metrics:
        return {'error': 'No metrics available'}

    # Find extremes
    best_time = min(all_metrics, key=lambda x: x['simulation_time'])
    worst_time = max(all_metrics, key=lambda x: x['simulation_time'])
    best_decisions = min(all_metrics, key=lambda x: x['decisions_per_node'])
    worst_decisions = max(all_metrics, key=lambda x: x['decisions_per_node'])
    best_memory = min(all_metrics, key=lambda x: x['memory_mb'])
    worst_memory = max(all_metrics, key=lambda x: x['memory_mb'])

    return {
        'best_case_time': {
            'category': best_time['category'],
            'nodes': best_time['nodes'],
            'time': round(best_time['simulation_time'], 4),
            'structure': best_time.get('structure', 'N/A')
        },
        'worst_case_time': {
            'category': worst_time['category'],
            'nodes': worst_time['nodes'],
            'time': round(worst_time['simulation_time'], 4),
            'structure': worst_time.get('structure', 'N/A')
        },
        'best_case_decisions': {
            'category': best_decisions['category'],
            'decisions_per_node': round(best_decisions['decisions_per_node'], 2),
            'structure': best_decisions.get('structure', 'N/A')
        },
        'worst_case_decisions': {
            'category': worst_decisions['category'],
            'decisions_per_node': round(worst_decisions['decisions_per_node'], 2),
            'structure': worst_decisions.get('structure', 'N/A')
        },
        'best_case_memory': {
            'category': best_memory['category'],
            'memory_mb': round(best_memory['memory_mb'], 2)
        },
        'worst_case_memory': {
            'category': worst_memory['category'],
            'memory_mb': round(worst_memory['memory_mb'], 2)
        }
    }


def analyze_rule_firing_patterns(all_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """
    Analyze which rules fire most frequently across different scenarios.
    """
    rule_stats = defaultdict(lambda: {'total': 0, 'rule1': 0, 'rule2': 0, 'rule3': 0, 'count': 0})

    for category, results in all_results.items():
        for r in results:
            decisions = r['decisions']
            rule_stats[category]['total'] += decisions['total']
            rule_stats[category]['rule1'] += decisions['rule1_forced_choice']
            rule_stats[category]['rule2'] += decisions['rule2_befriend_enemy']
            rule_stats[category]['rule3'] += decisions['rule3_hear_accusation']
            rule_stats[category]['count'] += 1

    # Calculate percentages
    summary = {}
    for category, stats in rule_stats.items():
        if stats['total'] > 0:
            summary[category] = {
                'avg_decisions': round(stats['total'] / stats['count'], 1),
                'rule1_pct': round(100 * stats['rule1'] / stats['total'], 1),
                'rule2_pct': round(100 * stats['rule2'] / stats['total'], 1),
                'rule3_pct': round(100 * stats['rule3'] / stats['total'], 1)
            }

    return summary


def generate_performance_table(results: List[Dict], title: str) -> str:
    """Generate a formatted performance table."""
    if not results:
        return f"\n{title}\nNo data available.\n"

    output = [f"\n{'='*80}"]
    output.append(f"{title}")
    output.append('='*80)

    # Headers
    headers = ['Nodes', 'Edges', 'Avg Deg', 'Sim Time', 'Decisions', 'D/N', 'Depth', 'Memory', 'Unity']
    output.append(f"{'  '.join([h.ljust(8) for h in headers])}")
    output.append('-'*80)

    # Data rows
    for r in results:
        row = [
            str(r['graph']['num_nodes']).ljust(8),
            str(r['graph']['num_edges']).ljust(8),
            f"{r['graph']['avg_degree']:.1f}".ljust(8),
            f"{r['timing']['simulation_time']:.3f}s".ljust(8),
            str(r['decisions']['total']).ljust(8),
            f"{r['decisions']['decisions_per_node']:.1f}".ljust(8),
            str(r['bfs']['depth']).ljust(8),
            f"{r['memory']['peak_memory_mb']:.1f}MB".ljust(8),
            ('✓' if r['outcomes']['unity_achieved'] else '✗').ljust(8)
        ]
        output.append('  '.join(row))

    return '\n'.join(output)


def generate_report(results_dir: str, output_file: str):
    """Generate comprehensive performance analysis report."""
    print("Loading results...")
    all_results = load_results(results_dir)

    report = []
    report.append("="*80)
    report.append("SCAPEGOATING CONTAGION SIMULATOR")
    report.append("Comprehensive Performance Analysis Report")
    report.append("="*80)

    # Summary statistics
    total_tests = sum(len(r) for r in all_results.values())
    report.append(f"\nTotal Tests Run: {total_tests}")
    report.append(f"Test Categories: {len([k for k, v in all_results.items() if v])}")

    # Performance tables
    if all_results['large_sparse']:
        report.append(generate_performance_table(
            all_results['large_sparse'],
            "LARGE SPARSE GRAPHS (Realistic Social Networks)"
        ))

    if all_results['complete_graphs']:
        report.append(generate_performance_table(
            all_results['complete_graphs'],
            "COMPLETE GRAPHS (Worst-Case O(V³) Complexity)"
        ))

    if all_results['pathological']:
        report.append(generate_performance_table(
            all_results['pathological'],
            "PATHOLOGICAL STRUCTURES"
        ))

    # Scaling complexity analysis
    report.append("\n" + "="*80)
    report.append("COMPLEXITY ANALYSIS")
    report.append("="*80)

    if all_results['large_sparse']:
        print("Analyzing sparse graph scaling...")
        sparse_complexity = analyze_scaling_complexity(all_results['large_sparse'])
        if 'error' not in sparse_complexity:
            report.append("\nSparse Graphs:")
            report.append(f"  Log-log slope: {sparse_complexity['log_log_slope']}")
            report.append(f"  Estimated complexity: {sparse_complexity['estimated_complexity']}")
            report.append(f"  R² (goodness of fit): {sparse_complexity['r_squared']}")
            report.append(f"  Data points: {sparse_complexity['data_points']}")
        else:
            report.append(f"\nSparse Graphs: {sparse_complexity['error']}")

    if all_results['complete_graphs']:
        print("Analyzing complete graph scaling...")
        complete_complexity = analyze_scaling_complexity(all_results['complete_graphs'])
        if 'error' not in complete_complexity:
            report.append("\nComplete Graphs:")
            report.append(f"  Log-log slope: {complete_complexity['log_log_slope']}")
            report.append(f"  Estimated complexity: {complete_complexity['estimated_complexity']}")
            report.append(f"  R² (goodness of fit): {complete_complexity['r_squared']}")
            report.append(f"  Data points: {complete_complexity['data_points']}")
        else:
            report.append(f"\nComplete Graphs: {complete_complexity['error']}")

    # Best/worst case analysis
    print("Analyzing best/worst cases...")
    best_worst = analyze_best_worst_cases(all_results)
    if 'error' not in best_worst:
        report.append("\n" + "="*80)
        report.append("BEST/WORST CASE ANALYSIS")
        report.append("="*80)

        report.append("\nBest Case (Fastest Time):")
        report.append(f"  Category: {best_worst['best_case_time']['category']}")
        report.append(f"  Nodes: {best_worst['best_case_time']['nodes']}")
        report.append(f"  Time: {best_worst['best_case_time']['time']}s")
        report.append(f"  Structure: {best_worst['best_case_time']['structure']}")

        report.append("\nWorst Case (Slowest Time):")
        report.append(f"  Category: {best_worst['worst_case_time']['category']}")
        report.append(f"  Nodes: {best_worst['worst_case_time']['nodes']}")
        report.append(f"  Time: {best_worst['worst_case_time']['time']}s")
        report.append(f"  Structure: {best_worst['worst_case_time']['structure']}")

        report.append("\nMost Efficient (Fewest Decisions/Node):")
        report.append(f"  Category: {best_worst['best_case_decisions']['category']}")
        report.append(f"  Decisions per node: {best_worst['best_case_decisions']['decisions_per_node']}")

        report.append("\nLeast Efficient (Most Decisions/Node):")
        report.append(f"  Category: {best_worst['worst_case_decisions']['category']}")
        report.append(f"  Decisions per node: {best_worst['worst_case_decisions']['decisions_per_node']}")

    # Rule firing patterns
    print("Analyzing rule firing patterns...")
    rule_patterns = analyze_rule_firing_patterns(all_results)
    if rule_patterns:
        report.append("\n" + "="*80)
        report.append("RULE FIRING PATTERNS")
        report.append("="*80)

        for category, stats in rule_patterns.items():
            report.append(f"\n{category.upper()}:")
            report.append(f"  Avg decisions: {stats['avg_decisions']}")
            report.append(f"  Rule 1 (Forced choice): {stats['rule1_pct']}%")
            report.append(f"  Rule 2 (Befriend enemy): {stats['rule2_pct']}%")
            report.append(f"  Rule 3 (Hear accusation): {stats['rule3_pct']}%")

    # Recommendations
    report.append("\n" + "="*80)
    report.append("OPTIMIZATION RECOMMENDATIONS")
    report.append("="*80)

    report.append("\n1. ADJACENCY LIST CACHING")
    report.append("   Current: O(E) neighbor lookup via edge iteration")
    report.append("   Optimized: O(1) with cached adjacency dictionary")
    report.append("   Expected speedup: 5-10x for large graphs")
    report.append("   Implementation: Add self._adjacency cache in SignedGraph")

    report.append("\n2. TRIANGLE ENUMERATION OPTIMIZATION")
    report.append("   Current: O(V³) brute force in find_all_triangles()")
    report.append("   Optimized: O(V × degree²) neighbor-based enumeration")
    report.append("   Expected speedup: 100x for sparse graphs")
    report.append("   Implementation: Use neighbor lists instead of triple loop")

    report.append("\n3. INCREMENTAL BALANCE TRACKING")
    report.append("   Current: Recompute all triangles after simulation")
    report.append("   Optimized: Track balance changes during edge flips")
    report.append("   Expected speedup: Constant factor improvement")

    report.append("\n4. OPTIONAL NUMPY/SCIPY BACKEND")
    report.append("   For very large graphs (10k+ nodes)")
    report.append("   Use scipy.sparse for adjacency matrix")
    report.append("   Vectorized operations with numpy")
    report.append("   Expected speedup: 2-5x for large dense graphs")

    # Save report
    report_text = '\n'.join(report)
    with open(output_file, 'w') as f:
        f.write(report_text)

    print(f"\n✓ Report saved to: {output_file}")
    print("\n" + "="*80)
    print("REPORT PREVIEW")
    print("="*80)
    print(report_text)

    return report_text


def main():
    results_dir = "output/stress_tests"
    output_file = "output/stress_tests/performance_analysis_report.txt"

    if not os.path.exists(results_dir):
        print(f"Error: Results directory not found: {results_dir}")
        print("Please run stress_tests.py first.")
        return 1

    generate_report(results_dir, output_file)
    return 0


if __name__ == '__main__':
    sys.exit(main())
