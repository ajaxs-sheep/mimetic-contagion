"""
Output formatters for cascade results.
"""

import json
from .simulator import CascadeResult, CascadeStep
from .analyzer import compute_all_scores


def format_json(result: CascadeResult) -> str:
    """Format cascade result as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def format_human_readable(result: CascadeResult) -> str:
    """Format cascade result as human-readable narrative."""
    lines = []

    # Header
    lines.append("=" * 70)
    lines.append("MIMETIC CASCADE SIMULATION")
    lines.append("=" * 70)

    # Initial state
    lines.append("\n=== INITIAL STATE ===")
    lines.append(f"Nodes: {len(result.initial_state.nodes)}")
    lines.append(f"Edges: {len(result.initial_state.edges)}")

    pos_edges = sum(1 for _, _, s in result.initial_state.get_all_edges() if s == 1)
    neg_edges = sum(1 for _, _, s in result.initial_state.get_all_edges() if s == -1)
    lines.append(f"  Positive: {pos_edges}")
    lines.append(f"  Negative: {neg_edges}")

    # Perturbation
    if result.perturbation:
        lines.append("\n=== PERTURBATION ===")
        u, v = result.perturbation
        old_sign = result.initial_state.get_edge(u, v)
        new_sign = -old_sign
        sign_str = "+" if new_sign == 1 else "-"

        if new_sign == -1:
            lines.append(f"{u} accuses {v}")
        else:
            lines.append(f"{u} reconciles with {v}")

        lines.append(f"  Edge {u}↔{v}: {_sign_str(old_sign)} → {_sign_str(new_sign)}")
    else:
        lines.append("\n=== NO PERTURBATION ===")
        lines.append("Running cascade from initial state imbalances")

    # Cascade steps
    if result.cascade_steps:
        lines.append(f"\n=== CASCADE ({len(result.cascade_steps)} steps) ===")

        for step in result.cascade_steps:
            lines.append(f"\n--- STEP {step.step_num} ---")

            # Handle stuck actors (can't act due to no-reversal rule)
            if step.stuck:
                lines.append(f"{step.actor.upper()} under pressure but STUCK\n")
                ctx = step.decision_context
                triangles = ctx["unbalanced_triangles"]

                if triangles:
                    lines.append(f"  Unbalanced triangles: {len(triangles)}")
                    for tri in triangles:
                        nodes_str = ", ".join(tri.nodes)
                        lines.append(f"    • ({nodes_str}) [{tri.get_type()}]")

                lines.append(f"\n  {step.actor} cannot act - all options would reverse a previous decision.")
                lines.append(f"  (No take-backs allowed)")
                continue

            lines.append(f"{step.actor.upper()} under pressure\n")

            # Show unbalanced triangles
            ctx = step.decision_context
            triangles = ctx["unbalanced_triangles"]

            if triangles:
                lines.append(f"  Unbalanced triangles: {len(triangles)}")
                for tri in triangles:
                    nodes_str = ", ".join(tri.nodes)
                    lines.append(f"    • ({nodes_str}) [{tri.get_type()}]")

            # Show options
            lines.append(f"\n  {step.actor} must choose a side in this conflict.")

            options = ctx["options"]
            if options:
                # Group by action type
                breaking = [opt for opt in options if opt.current_sign == 1]
                allying = [opt for opt in options if opt.current_sign == -1]

                if breaking:
                    lines.append("\n  Options to resolve (++- → break friendship with lowest score):")
                    for opt in breaking:
                        score = opt.target_score
                        lines.append(f"    • Break with {opt.target}: score = {score}")

                if allying:
                    lines.append("\n  Options to resolve (--- → ally with highest score):")
                    for opt in allying:
                        score = opt.target_score
                        lines.append(f"    • Ally with {opt.target}: score = {score}")

            # Show decision
            chosen = ctx["chosen"]
            if chosen:
                lines.append("")

                # Determine if it's a tie
                all_scores = [opt.target_score for opt in options
                             if opt.current_sign == chosen.current_sign]
                is_tie = all_scores.count(chosen.target_score) > 1

                if is_tie:
                    lines.append(f"  Decision: TIE → random choice")

                if chosen.current_sign == 1:
                    lines.append(f"  → Easier to hate: {chosen.target}")
                    action = f"{step.actor}→{chosen.target}: + → -"
                else:
                    lines.append(f"  → Easier to love: {chosen.target}")
                    action = f"{step.actor}→{chosen.target}: - → +"

                lines.append(f"  Action: {action}")

            # Show new pressured nodes
            if step.new_pressured_nodes:
                new_list = ", ".join(sorted(step.new_pressured_nodes))
                lines.append(f"\n  New pressured nodes: [{new_list}]")
            else:
                lines.append(f"\n  No new pressured nodes.")

    else:
        lines.append("\n=== CASCADE ===")
        lines.append("No cascade occurred (already stable after perturbation)")

    # Final state
    lines.append("\n" + "=" * 70)
    lines.append("=== FINAL STATE ===")

    if result.converged:
        lines.append("Status: CONVERGED (stable)")
    else:
        lines.append(f"Status: MAX STEPS REACHED ({len(result.cascade_steps)} steps)")

    if result.perturbation:
        lines.append(f"Total flips: {len(result.cascade_steps) + 1} (including perturbation)")
    else:
        lines.append(f"Total flips: {len(result.cascade_steps)}")

    # Show final edge counts
    pos_edges = sum(1 for _, _, s in result.final_state.get_all_edges() if s == 1)
    neg_edges = sum(1 for _, _, s in result.final_state.get_all_edges() if s == -1)
    lines.append(f"\nFinal edges:")
    lines.append(f"  Positive: {pos_edges}")
    lines.append(f"  Negative: {neg_edges}")

    # Show final social scores
    lines.append(f"\nFinal social scores (friends - enemies):")
    scores = compute_all_scores(result.final_state)
    for node in sorted(scores.keys()):
        score = scores[node]
        lines.append(f"  {node}: {score:+d}")

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)


def _sign_str(sign: int) -> str:
    """Convert sign to string."""
    return "+" if sign == 1 else "-"


def format_simple_chain(result: CascadeResult) -> str:
    """Format cascade as simple event chain."""
    lines = []

    # Perturbation
    if result.perturbation:
        u, v = result.perturbation
        old_sign = result.initial_state.get_edge(u, v)
        new_sign = -old_sign
        lines.append(f"PERTURB: {u}↔{v} {_sign_str(old_sign)}→{_sign_str(new_sign)}")
    else:
        lines.append("NO PERTURBATION - running from initial state")

    # Each step
    for step in result.cascade_steps:
        if step.stuck:
            lines.append(f"STEP {step.step_num}: {step.actor} STUCK (no take-backs)")
        else:
            u, v = step.edge
            lines.append(
                f"STEP {step.step_num}: {step.actor} flips {u}↔{v} "
                f"{_sign_str(step.old_sign)}→{_sign_str(step.new_sign)}"
            )

    return "\n".join(lines)
