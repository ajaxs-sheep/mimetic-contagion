"""
Output formatters for scapegoating results.
"""

import json
from .simulator import ScapegoatResult
from .analyzer import compute_all_scores


def format_json(result: ScapegoatResult) -> str:
    """Format scapegoating result as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def format_human_readable(result: ScapegoatResult) -> str:
    """Format scapegoating result as human-readable narrative."""
    lines = []

    # Header
    lines.append("=" * 70)
    lines.append("SCAPEGOATING CONTAGION SIMULATION")
    lines.append("=" * 70)

    # Initial state
    lines.append("\n=== INITIAL STATE ===")
    lines.append(f"Nodes: {len(result.initial_state.nodes)}")
    lines.append(f"Edges: {len(result.initial_state.edges)}")

    pos_edges = sum(1 for _, _, s in result.initial_state.get_all_edges() if s == 1)
    neg_edges = sum(1 for _, _, s in result.initial_state.get_all_edges() if s == -1)
    lines.append(f"  Positive: {pos_edges}")
    lines.append(f"  Negative: {neg_edges}")

    # Initial accusation
    lines.append("\n=== INITIAL ACCUSATION ===")
    lines.append(f"Scapegoat: {result.scapegoat}")
    lines.append(f"Initial Accuser: {result.initial_accuser}")

    old_sign = result.initial_state.get_edge(result.initial_accuser, result.scapegoat)
    new_sign = -1  # Always flipped to negative
    lines.append(f"  Edge {result.initial_accuser}↔{result.scapegoat}: {_sign_str(old_sign)} → {_sign_str(new_sign)}")

    # Contagion decisions
    lines.append(f"\n=== CONTAGION (single pass through {len(result.decisions)} nodes) ===")

    if result.decisions:
        for decision in result.decisions:
            lines.append(f"\n{decision.node}:")
            lines.append(f"  {decision.reason}")

            if decision.action:
                u, v = decision.edge_flipped
                lines.append(f"  Action: {u}↔{v}: {_sign_str(decision.old_sign)} → {_sign_str(decision.new_sign)}")

                if decision.action == "join_accusers":
                    lines.append(f"  → {decision.node} joins accusers")
                elif decision.action == "hear_accusation":
                    lines.append(f"  → {decision.node} hears accusation, forms negative opinion")
                elif decision.action == "befriend_other":
                    lines.append(f"  → {decision.node} resolves --- triangle")
            else:
                lines.append(f"  → No action taken")
    else:
        lines.append("No nodes to process (all nodes already accusers or scapegoat)")

    # Final analysis
    lines.append("\n" + "=" * 70)
    lines.append("=== FINAL ANALYSIS ===")

    lines.append(f"\nAccusers ({len(result.accusers)}): {sorted(list(result.accusers))}")

    if result.defenders:
        lines.append(f"Defenders ({len(result.defenders)}): {sorted(list(result.defenders))}")
        lines.append("\n⚠ CONTAGION FAILED")
        lines.append("Some nodes remain defenders of the scapegoat.")
        lines.append("This represents a stronghold preventing full scapegoating.")
    else:
        lines.append(f"Defenders: None")
        lines.append("\n✓ CONTAGION SUCCEEDED")
        lines.append("All nodes (except scapegoat) became accusers or united against scapegoat.")

    # Structural checks
    lines.append(f"\nStructural Balance: {'YES' if result.is_balanced else 'NO'}")
    if not result.is_balanced:
        lines.append("  (Some unbalanced triangles remain)")

    lines.append(f"All-Against-One: {'YES' if result.is_all_against_one else 'NO'}")
    if result.is_all_against_one:
        lines.append(f"  ({result.scapegoat} is completely isolated)")

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
        marker = ""
        if node == result.scapegoat:
            marker = " (scapegoat)"
        elif node in result.defenders:
            marker = " (defender)"
        elif node == result.initial_accuser:
            marker = " (initial accuser)"
        lines.append(f"  {node}: {score:+d}{marker}")

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)


def _sign_str(sign: int) -> str:
    """Convert sign to string."""
    if sign == 0:
        return "∅"  # No edge
    return "+" if sign == 1 else "-"


def format_simple_chain(result: ScapegoatResult) -> str:
    """Format scapegoating as simple event chain."""
    lines = []

    # Initial accusation
    old_sign = result.initial_state.get_edge(result.initial_accuser, result.scapegoat)
    new_sign = -1
    lines.append(f"ACCUSATION: {result.initial_accuser} accuses {result.scapegoat}")
    lines.append(f"  {result.initial_accuser}↔{result.scapegoat}: {_sign_str(old_sign)} → {_sign_str(new_sign)}")

    # Each decision
    lines.append(f"\nCONTAGION:")
    for i, decision in enumerate(result.decisions, 1):
        if decision.action:
            u, v = decision.edge_flipped
            if decision.action == "join_accusers":
                action_desc = "joins accusers"
            elif decision.action == "hear_accusation":
                action_desc = "hears accusation"
            elif decision.action == "befriend_other":
                action_desc = "resolves --- triangle"
            else:
                action_desc = "takes action"

            lines.append(
                f"  {i}. {decision.node} {action_desc}: "
                f"{u}↔{v} {_sign_str(decision.old_sign)}→{_sign_str(decision.new_sign)}"
            )
        else:
            lines.append(f"  {i}. {decision.node}: no action ({decision.reason})")

    # Summary
    lines.append(f"\nRESULT:")
    lines.append(f"  Accusers: {len(result.accusers)}")
    lines.append(f"  Defenders: {len(result.defenders)}")
    lines.append(f"  Contagion succeeded: {result.contagion_succeeded}")
    lines.append(f"  Is balanced: {result.is_balanced}")
    lines.append(f"  Is all-against-one: {result.is_all_against_one}")

    return "\n".join(lines)
