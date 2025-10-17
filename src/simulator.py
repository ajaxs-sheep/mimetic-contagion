"""
Mimetic Scapegoating Simulator: Propagate scapegoating contagion through a signed graph.
"""

from typing import List, Tuple, Dict, Set, Optional
import random
from .graph import SignedGraph
from .analyzer import find_unbalanced_triangles


class ContagionDecision:
    """Represents one node's decision during contagion."""

    def __init__(
        self,
        node: str,
        action: Optional[str],
        reason: str,
        edge_flipped: Optional[Tuple[str, str]] = None,
        old_sign: Optional[int] = None,
        new_sign: Optional[int] = None
    ):
        self.node = node
        self.action = action  # "join_accusers", "befriend_accuser", or None
        self.reason = reason
        self.edge_flipped = edge_flipped
        self.old_sign = old_sign
        self.new_sign = new_sign

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "node": self.node,
            "action": self.action,
            "reason": self.reason
        }
        if self.edge_flipped:
            result["edge_flipped"] = list(self.edge_flipped)
            result["from_sign"] = self.old_sign
            result["to_sign"] = self.new_sign
        return result


class ScapegoatResult:
    """Results of scapegoating simulation."""

    def __init__(
        self,
        initial_state: SignedGraph,
        scapegoat: str,
        initial_accuser: str,
        decisions: List[ContagionDecision],
        final_state: SignedGraph,
        accusers: Set[str],
        defenders: Set[str],
        is_balanced: bool,
        is_all_against_one: bool
    ):
        self.initial_state = initial_state
        self.scapegoat = scapegoat
        self.initial_accuser = initial_accuser
        self.decisions = decisions
        self.final_state = final_state
        self.accusers = accusers
        self.defenders = defenders
        self.is_balanced = is_balanced
        self.is_all_against_one = is_all_against_one
        self.contagion_succeeded = len(defenders) == 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "initial_state": self.initial_state.to_dict(),
            "scapegoat": self.scapegoat,
            "initial_accuser": self.initial_accuser,
            "decisions": [d.to_dict() for d in self.decisions],
            "final_state": self.final_state.to_dict(),
            "accusers": sorted(list(self.accusers)),
            "defenders": sorted(list(self.defenders)),
            "is_balanced": self.is_balanced,
            "is_all_against_one": self.is_all_against_one,
            "contagion_succeeded": self.contagion_succeeded
        }


class MimeticContagionSimulator:
    """Simulates scapegoating contagion in signed social graphs."""

    def __init__(self, graph: SignedGraph, verbose: bool = False):
        """
        Args:
            graph: The initial signed graph
            verbose: If True, print progress updates to stderr
        """
        self.initial_graph = graph.copy()
        self.graph = graph.copy()
        self.verbose = verbose

    def introduce_accusation(self, scapegoat: str, accuser: str) -> ScapegoatResult:
        """
        Introduce an accusation and propagate scapegoating contagion.

        Args:
            scapegoat: The node to be scapegoated
            accuser: The initial accuser

        Returns:
            ScapegoatResult with full simulation results
        """
        import sys

        if self.verbose:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"SCAPEGOATING CONTAGION", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)
            print(f"Scapegoat: {scapegoat}", file=sys.stderr)
            print(f"Initial Accuser: {accuser}", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)

        # Store initial state
        initial_state = self.initial_graph.copy()

        # Flip accuser↔scapegoat to negative (the initial accusation)
        old_sign = self.graph.get_edge(accuser, scapegoat)
        if old_sign != -1:
            self.graph.flip_edge(accuser, scapegoat)

        # Initialize accusers set with initial accuser
        accusers = {accuser}

        # IMPORTANT: Add any pre-existing enemies to accusers set BEFORE contagion
        # This ensures that when friends check "do I have accuser friends?", pre-existing
        # enemies count as accusers (they're already against the scapegoat)
        for node in self.graph.nodes:
            if node == scapegoat:
                continue
            if self.graph.has_edge(node, scapegoat) and \
               self.graph.get_edge(node, scapegoat) == -1:
                accusers.add(node)

        # Propagate contagion (SINGLE PASS)
        decisions = self._propagate_scapegoat_contagion(scapegoat, accusers)

        # Check final state
        is_balanced = len(find_unbalanced_triangles(self.graph)) == 0
        is_all_against_one = self._check_all_against_one(scapegoat)

        # Find defenders (anyone who's still friend of scapegoat)
        defenders = set()
        for node in self.graph.nodes:
            if node == scapegoat:
                continue
            if self.graph.has_edge(node, scapegoat) and \
               self.graph.get_edge(node, scapegoat) == 1:
                defenders.add(node)

        if self.verbose:
            print(f"\nFinal state:", file=sys.stderr)
            print(f"  Accusers: {sorted(list(accusers))}", file=sys.stderr)
            print(f"  Defenders: {sorted(list(defenders))}", file=sys.stderr)
            print(f"  Balanced: {is_balanced}", file=sys.stderr)
            print(f"  All-against-one: {is_all_against_one}", file=sys.stderr)
            print(f"  Contagion succeeded: {len(defenders) == 0}\n", file=sys.stderr)

        return ScapegoatResult(
            initial_state=initial_state,
            scapegoat=scapegoat,
            initial_accuser=accuser,
            decisions=decisions,
            final_state=self.graph.copy(),
            accusers=accusers,
            defenders=defenders,
            is_balanced=is_balanced,
            is_all_against_one=is_all_against_one
        )

    def _propagate_scapegoat_contagion(self, scapegoat: str, accusers: Set[str]) -> List[ContagionDecision]:
        """
        Propagate scapegoating contagion through the network (BFS ORDER).

        Rules:
        1. Friend of accuser + Friend of scapegoat → Flip against scapegoat
        2. Enemy of scapegoat → Resolve all --- triangles by befriending third parties
        3. Friend of accuser + No edge to scapegoat → Hear about scapegoat, create negative edge

        Process nodes in BFS order starting from initial accuser to simulate
        information spreading through social network.

        Args:
            scapegoat: The scapegoat node
            accusers: Set of accusers (modified in place)

        Returns:
            List of ContagionDecision objects
        """
        import sys
        from collections import deque

        decisions = []

        # BFS traversal starting from initial accuser
        # This ensures information spreads through social network realistically
        initial_accuser = list(accusers)[0]  # Should only be one at this point

        # Edge case check: Does the accuser have any friends?
        # If the accuser has only enemies, they can't credibly spread accusations
        # (they're already isolated/scapegoated themselves)
        accuser_has_friends = any(
            self.graph.get_edge(initial_accuser, neighbor) == 1
            for neighbor in self.graph.neighbors(initial_accuser)
            if neighbor != scapegoat
        )

        if not accuser_has_friends and self.verbose:
            print(f"⚠ WARNING: {initial_accuser} has no friends (only enemies)!", file=sys.stderr)
            print(f"  → Accusation cannot spread through friendship network", file=sys.stderr)
            print(f"  → {initial_accuser} is likely already isolated/scapegoated\n", file=sys.stderr)

        visited = {scapegoat}  # Don't process scapegoat
        queue = deque([initial_accuser])
        visited.add(initial_accuser)

        if self.verbose:
            print(f"Processing nodes in BFS order from {initial_accuser}...", file=sys.stderr)

        # Process nodes AS WE DISCOVER THEM in BFS
        # This ensures accusation spreads correctly: when you discover a friend, they hear about it
        while queue:
            current = queue.popleft()

            # Import here to avoid circular dependency
            from .decision import apply_contagion_rule

            # Process THIS node now (before discovering its neighbors)
            actions_list = apply_contagion_rule(
                self.graph, current, scapegoat, accusers
            )

            for action, reason, target_node in actions_list:
                if action == "join_accusers":
                    # Rule 1: Flip against scapegoat
                    old_sign = self.graph.get_edge(current, scapegoat)
                    self.graph.flip_edge(current, scapegoat)
                    new_sign = self.graph.get_edge(current, scapegoat)

                    decision = ContagionDecision(
                        node=current,
                        action=action,
                        reason=reason,
                        edge_flipped=(current, scapegoat),
                        old_sign=old_sign,
                        new_sign=new_sign
                    )
                    decisions.append(decision)
                    accusers.add(current)

                    if self.verbose:
                        print(f"  {current}: {reason}", file=sys.stderr)
                        print(f"    → {current}↔{scapegoat}: {'+' if old_sign == 1 else '-'} → {'+' if new_sign == 1 else '-'}", file=sys.stderr)

                elif action == "hear_accusation":
                    # Rule 3: Hear about scapegoat, create negative edge
                    self.graph.add_edge(current, scapegoat, -1)

                    decision = ContagionDecision(
                        node=current,
                        action=action,
                        reason=reason,
                        edge_flipped=(current, scapegoat),
                        old_sign=0,  # No edge before
                        new_sign=-1
                    )
                    decisions.append(decision)
                    accusers.add(current)

                    if self.verbose:
                        print(f"  {current}: {reason}", file=sys.stderr)
                        print(f"    → {current}↔{scapegoat}: (no edge) → -", file=sys.stderr)

                elif action == "befriend_other":
                    # Rule 2: Befriend third party to resolve --- triangle
                    old_sign = self.graph.get_edge(current, target_node)
                    self.graph.flip_edge(current, target_node)
                    new_sign = self.graph.get_edge(current, target_node)

                    decision = ContagionDecision(
                        node=current,
                        action=action,
                        reason=reason,
                        edge_flipped=(current, target_node),
                        old_sign=old_sign,
                        new_sign=new_sign
                    )
                    decisions.append(decision)

                    if self.verbose:
                        print(f"  {current}: {reason}", file=sys.stderr)
                        print(f"    → {current}↔{target_node}: {'+' if old_sign == 1 else '-'} → {'+' if new_sign == 1 else '-'}", file=sys.stderr)

                else:
                    # No action taken (defender or neutral)
                    decision = ContagionDecision(
                        node=current,
                        action=None,
                        reason=reason
                    )
                    decisions.append(decision)

                    if self.verbose:
                        print(f"  {current}: {reason}", file=sys.stderr)

            # AFTER processing current node, add its friends to queue
            # This way, friends can hear from current if it became an accuser
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited and self.graph.get_edge(current, neighbor) == 1:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # Add any remaining nodes not reached by BFS (disconnected friendship components)
        for node in self.graph.nodes:
            if node not in visited:
                # Process unreachable nodes
                actions_list = apply_contagion_rule(
                    self.graph, node, scapegoat, accusers
                )
                for action, reason, target_node in actions_list:
                    if action:
                        decision = ContagionDecision(
                            node=node,
                            action=action,
                            reason=reason
                        )
                        decisions.append(decision)
                        if self.verbose:
                            print(f"  {node}: {reason}", file=sys.stderr)

        if self.verbose:
            print(f"\nContagion complete. {len([d for d in decisions if d.action])} actions taken.", file=sys.stderr)

        # CLEANUP PASS: Resolve ALL remaining --- triangles with scapegoat
        # This ensures complete community unity (all positive edges between non-scapegoat nodes)
        cleanup_decisions = self._resolve_community_conflicts(scapegoat)
        if cleanup_decisions:
            decisions.extend(cleanup_decisions)
            if self.verbose:
                print(f"\nCommunity unity pass: {len(cleanup_decisions)} edges flipped to positive", file=sys.stderr)

        return decisions

    def _resolve_community_conflicts(self, scapegoat: str) -> List[ContagionDecision]:
        """
        Cleanup pass: Resolve ALL remaining --- triangles involving scapegoat.

        After all nodes become enemies of scapegoat, any two nodes that are enemies
        of each other form a --- triangle with the scapegoat. Rule 2 should resolve
        these to create complete community unity (all positive edges).

        This pass ensures Girardian scapegoating: the community unites against the victim.

        Args:
            scapegoat: The scapegoat node

        Returns:
            List of ContagionDecision objects for community unification
        """
        import sys
        from .decision import find_unbalanced_triangles_with_scapegoat

        decisions = []

        # Check each node for --- triangles with scapegoat
        for node in self.graph.nodes:
            if node == scapegoat:
                continue

            # Only process nodes that are enemies of scapegoat
            if not self.graph.has_edge(node, scapegoat) or \
               self.graph.get_edge(node, scapegoat) != -1:
                continue

            # Find all --- triangles involving this node and scapegoat
            unbalanced_triangles = find_unbalanced_triangles_with_scapegoat(
                self.graph, node, scapegoat
            )

            for triangle, third_node in unbalanced_triangles:
                # Befriend the third person to resolve --- triangle
                old_sign = self.graph.get_edge(node, third_node)
                self.graph.flip_edge(node, third_node)
                new_sign = self.graph.get_edge(node, third_node)

                reason = f"Community unity: resolve --- triangle ({node}, {scapegoat}, {third_node})"

                decision = ContagionDecision(
                    node=node,
                    action="befriend_other",
                    reason=reason,
                    edge_flipped=(node, third_node),
                    old_sign=old_sign,
                    new_sign=new_sign
                )
                decisions.append(decision)

                if self.verbose:
                    print(f"  {node} befriends {third_node} (unity against {scapegoat})", file=sys.stderr)
                    print(f"    → {node}↔{third_node}: - → +", file=sys.stderr)

        return decisions

    def _check_all_against_one(self, scapegoat: str) -> bool:
        """Check if all nodes (except scapegoat) are enemies of scapegoat."""
        for node in self.graph.nodes:
            if node == scapegoat:
                continue
            if not self.graph.has_edge(node, scapegoat):
                return False
            if self.graph.get_edge(node, scapegoat) != -1:
                return False
        return True
