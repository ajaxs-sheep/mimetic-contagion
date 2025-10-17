"""
Mimetic Cascade Simulator: Propagate social contagion through a signed graph.
"""

from typing import List, Tuple, Dict, Set
from collections import deque
import random
import math
from .graph import SignedGraph
from .analyzer import find_pressured_nodes, get_node_unbalanced_triangles, calculate_triangle_delta
from .decision import choose_flip, get_decision_context


class CascadeStep:
    """Represents one step in the cascade."""

    def __init__(
        self,
        step_num: int,
        actor: str,
        edge: Tuple[str, str],
        old_sign: int,
        new_sign: int,
        decision_context: Dict,
        new_pressured_nodes: Set[str],
        stuck: bool = False
    ):
        self.step_num = step_num
        self.actor = actor
        self.edge = edge
        self.old_sign = old_sign
        self.new_sign = new_sign
        self.decision_context = decision_context
        self.new_pressured_nodes = new_pressured_nodes
        self.stuck = stuck  # True if actor couldn't act due to no-reversal rule

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "step": self.step_num,
            "actor": self.actor,
            "edge": list(self.edge) if self.edge else None,
            "from_sign": self.old_sign,
            "to_sign": self.new_sign,
            "new_pressured": sorted(list(self.new_pressured_nodes))
        }
        if self.stuck:
            result["stuck"] = True
        return result


class CascadeResult:
    """Results of running a cascade simulation."""

    def __init__(
        self,
        initial_state: SignedGraph,
        perturbation: Tuple[str, str],
        cascade_steps: List[CascadeStep],
        final_state: SignedGraph,
        converged: bool
    ):
        self.initial_state = initial_state
        self.perturbation = perturbation
        self.cascade_steps = cascade_steps
        self.final_state = final_state
        self.converged = converged

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "initial_state": self.initial_state.to_dict(),
            "cascade": [step.to_dict() for step in self.cascade_steps],
            "final_state": self.final_state.to_dict(),
            "converged": self.converged,
            "total_steps": len(self.cascade_steps)
        }

        if self.perturbation is not None:
            result["perturbation"] = {
                "edge": list(self.perturbation),
                "from_sign": self.initial_state.get_edge(*self.perturbation),
                "to_sign": -self.initial_state.get_edge(*self.perturbation)
            }
        else:
            result["perturbation"] = None

        return result


class MimeticCascadeSimulator:
    """Simulates mimetic contagion in signed social graphs."""

    def __init__(self, graph: SignedGraph, max_steps: int = 1000, rationality: float = 0.5, verbose: bool = False):
        """
        Args:
            graph: The initial signed graph
            max_steps: Maximum number of cascade steps before stopping
            rationality: Decision rationality (0.0=myopic, 1.0=globally optimal, 0.5=balanced)
            verbose: If True, print progress updates to stderr
        """
        self.initial_graph = graph.copy()
        self.graph = graph.copy()
        self.max_steps = max_steps
        self.rationality = rationality
        self.verbose = verbose

    def introduce_perturbation(self, edge: Tuple[str, str]) -> CascadeResult:
        """
        Introduce a perturbation (flip one edge) and propagate the cascade.

        Args:
            edge: (node1, node2) edge to flip

        Returns:
            CascadeResult with full simulation history
        """
        # Store initial state
        initial_state = self.initial_graph.copy()

        # Track actor-edge pairs (each actor can only flip an edge once)
        self.actor_flipped_edges = set()

        # Flip the edge (perturbation)
        canonical_edge = tuple(sorted(edge))
        self.graph.flip_edge(*edge)

        # Perturbation is bidirectionally locked - NEITHER actor can touch this edge
        self.actor_flipped_edges.add((edge[0], canonical_edge))
        self.actor_flipped_edges.add((edge[1], canonical_edge))

        # Run the cascade
        cascade_steps = self._propagate_cascade()

        # Check if converged
        converged = len(cascade_steps) < self.max_steps

        return CascadeResult(
            initial_state=initial_state,
            perturbation=edge,
            cascade_steps=cascade_steps,
            final_state=self.graph.copy(),
            converged=converged
        )

    def run_from_current_state(self) -> CascadeResult:
        """
        Run cascade from current graph state without any perturbation.

        Useful for testing if randomly initialized graphs converge naturally.

        Returns:
            CascadeResult with full simulation history
        """
        # Store initial state
        initial_state = self.initial_graph.copy()

        # Track actor-edge pairs (each actor can only flip an edge once)
        self.actor_flipped_edges = set()

        # No perturbation - just run from current state
        # Run the cascade
        cascade_steps = self._propagate_cascade()

        # Check if converged
        converged = len(cascade_steps) < self.max_steps

        return CascadeResult(
            initial_state=initial_state,
            perturbation=None,  # No perturbation
            cascade_steps=cascade_steps,
            final_state=self.graph.copy(),
            converged=converged
        )

    def _propagate_cascade(self) -> List[CascadeStep]:
        """
        Propagate the cascade until stability or max steps.

        Uses round-based selection with rationality parameter:
        - Each round: find all pressured actors
        - For each, determine their preferred move
        - Calculate triangle delta for each move
        - Select move based on rationality (1.0=best, 0.0=random, 0.5=weighted)

        Returns:
            List of CascadeStep objects
        """
        import sys
        import time

        cascade_steps = []
        step_num = 0
        start_time = time.time()
        last_progress_time = start_time

        if self.verbose:
            t0 = time.time()
            initial_pressured = len(find_pressured_nodes(self.graph))
            t_init = time.time() - t0
            print(f"Starting cascade... {initial_pressured} initially pressured nodes (took {t_init:.3f}s to find)", file=sys.stderr)

        while step_num < self.max_steps:
            step_start = time.time()

            # Find all currently pressured nodes
            t0 = time.time()
            pressured_nodes = find_pressured_nodes(self.graph)
            t_find_pressured = time.time() - t0

            if not pressured_nodes:
                # No more pressured nodes, stable!
                if self.verbose:
                    print(f"✓ Converged at step {step_num}!", file=sys.stderr)
                break

            # Collect all possible moves for this round
            t0 = time.time()
            possible_moves = []  # List of (actor, edge, triangle_delta)

            for actor in pressured_nodes:
                # Get this actor's preferred move
                edge_to_flip = choose_flip(self.graph, actor, self.actor_flipped_edges)

                if edge_to_flip is None:
                    # Actor is stuck
                    possible_moves.append((actor, None, -1000))  # Large negative penalty
                else:
                    # Calculate triangle delta for this move
                    triangle_delta = calculate_triangle_delta(self.graph, edge_to_flip)
                    possible_moves.append((actor, edge_to_flip, triangle_delta))
            t_compute_moves = time.time() - t0

            if not possible_moves:
                # All stuck, stop
                if self.verbose:
                    print(f"✗ All actors stuck at step {step_num}", file=sys.stderr)
                break

            # Select move based on rationality parameter
            t0 = time.time()
            selected_actor, selected_edge, selected_delta = self._select_move(possible_moves)
            t_select = time.time() - t0

            # Get decision context for output
            t0 = time.time()
            decision_context = get_decision_context(self.graph, selected_actor)
            t_context = time.time() - t0

            if selected_edge is None:
                # Selected actor is stuck
                step = CascadeStep(
                    step_num=step_num + 1,
                    actor=selected_actor,
                    edge=None,
                    old_sign=0,
                    new_sign=0,
                    decision_context=decision_context,
                    new_pressured_nodes=set(),
                    stuck=True
                )
                cascade_steps.append(step)
                step_num += 1

                step_time = time.time() - step_start
                if self.verbose:
                    print(f"  Step {step_num}: {selected_actor} STUCK | total: {step_time:.3f}s", file=sys.stderr)
                continue

            # Execute the selected flip
            t0 = time.time()
            old_sign = self.graph.get_edge(*selected_edge)
            self.graph.flip_edge(*selected_edge)
            new_sign = self.graph.get_edge(*selected_edge)

            # Mark that this actor has acted on this edge (no reversals for this actor)
            canonical_edge = tuple(sorted(selected_edge))
            self.actor_flipped_edges.add((selected_actor, canonical_edge))

            # Find new pressured nodes created by this flip
            pressured_after = find_pressured_nodes(self.graph)
            new_pressured = pressured_after - pressured_nodes
            t_execute = time.time() - t0

            # Record this step
            step = CascadeStep(
                step_num=step_num + 1,
                actor=selected_actor,
                edge=selected_edge,
                old_sign=old_sign,
                new_sign=new_sign,
                decision_context=decision_context,
                new_pressured_nodes=new_pressured
            )
            cascade_steps.append(step)

            step_num += 1

            # Verbose output every step
            step_time = time.time() - step_start
            if self.verbose:
                u, v = selected_edge
                sign_str = "+" if new_sign == 1 else "-"
                print(f"  Step {step_num}: {selected_actor} flips {u}↔{v} → {sign_str} | "
                      f"find: {t_find_pressured:.3f}s, moves: {t_compute_moves:.3f}s, "
                      f"select: {t_select:.3f}s, exec: {t_execute:.3f}s | "
                      f"total: {step_time:.3f}s", file=sys.stderr)

        return cascade_steps

    def _select_move(self, possible_moves: List[Tuple[str, Tuple[str, str], int]]) -> Tuple[str, Tuple[str, str], int]:
        """
        Select a move from possible moves based on rationality parameter.

        Args:
            possible_moves: List of (actor, edge, triangle_delta) tuples

        Returns:
            Selected (actor, edge, triangle_delta) tuple
        """
        if self.rationality == 1.0:
            # Fully rational: always pick best triangle delta
            return max(possible_moves, key=lambda x: x[2])

        elif self.rationality == 0.0:
            # Fully myopic: random choice
            return random.choice(possible_moves)

        else:
            # Probabilistic: weight by triangle delta with temperature
            # Higher rationality = more weight on good moves
            temperature = 1.0 / (self.rationality + 0.01)  # Avoid division by zero

            # Calculate weights using softmax
            deltas = [m[2] for m in possible_moves]
            max_delta = max(deltas)

            # Shift deltas to avoid overflow
            exp_deltas = [math.exp((d - max_delta) / temperature) for d in deltas]
            total = sum(exp_deltas)
            probabilities = [e / total for e in exp_deltas]

            # Sample based on probabilities
            r = random.random()
            cumulative = 0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if r < cumulative:
                    return possible_moves[i]

            # Fallback (shouldn't reach here)
            return possible_moves[-1]
