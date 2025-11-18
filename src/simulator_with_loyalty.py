"""
Mimetic Scapegoating Simulator with Community Loyalty.

Extends the base simulator to model community loyalty:
- Members defend their own community against external accusations
- Prevents defection when attacked by outsiders
- Enables escalatory dynamics between communities
"""

from typing import List, Tuple, Dict, Set, Optional
from .simulator import MimeticContagionSimulator, ScapegoatResult, ContagionDecision
from .graph import SignedGraph


class LoyaltySimulator(MimeticContagionSimulator):
    """
    Simulator with community loyalty rules.

    Key difference from base simulator:
    - Nodes will defend community members when accused by outsiders
    - Cross-community attacks trigger loyalty, not defection
    """

    def __init__(
        self,
        graph: SignedGraph,
        communities: Dict[str, List[str]],
        verbose: bool = False
    ):
        """
        Args:
            graph: The initial signed graph
            communities: Dict mapping community names to member lists
                         e.g., {'A': ['A0', 'A1', ...], 'B': ['B0', 'B1', ...]}
            verbose: If True, print progress updates to stderr
        """
        super().__init__(graph, verbose)
        self.communities = communities

        # Build reverse lookup: node -> community name
        self.node_to_community = {}
        for comm_name, members in communities.items():
            for node in members:
                self.node_to_community[node] = comm_name

    def get_community(self, node: str) -> Optional[str]:
        """Get the community name for a node."""
        return self.node_to_community.get(node)

    def is_cross_community_attack(
        self,
        node: str,
        scapegoat: str,
        initial_accuser: str
    ) -> bool:
        """
        Check if this is a cross-community attack.

        Returns True if:
        - Node and scapegoat are in same community
        - Initial accuser is from different community
        - This represents external attack on community member
        """
        node_comm = self.get_community(node)
        sg_comm = self.get_community(scapegoat)
        acc_comm = self.get_community(initial_accuser)

        # If any are unknown, not a cross-community attack
        if node_comm is None or sg_comm is None or acc_comm is None:
            return False

        # Cross-community if: node and scapegoat same community, accuser different
        return (node_comm == sg_comm) and (acc_comm != sg_comm)

    def should_defend_community_member(
        self,
        node: str,
        scapegoat: str,
        initial_accuser: str
    ) -> bool:
        """
        Check if node should defend scapegoat based on community loyalty.

        Loyalty triggers when:
        1. Node and scapegoat are in same community
        2. Accusation came from different community (external attack)
        3. Node has positive edge to scapegoat (they're friends)

        Returns:
            True if node should defend (refuse to turn against scapegoat)
            False if normal rules apply
        """
        # Must be cross-community attack
        if not self.is_cross_community_attack(node, scapegoat, initial_accuser):
            return False

        # Only defend if node is friend of scapegoat
        # (enemies within community can still turn against them)
        if self.graph.has_edge(node, scapegoat):
            edge_sign = self.graph.get_edge(node, scapegoat)
            if edge_sign == 1:
                return True  # Defend friend from external attack

        return False

    def _propagate_scapegoat_contagion(
        self,
        scapegoat: str,
        accusers: Set[str]
    ) -> List[ContagionDecision]:
        """
        Propagate scapegoating contagion with community loyalty.

        Modified from base class to check loyalty before applying forced choice.
        """
        import sys
        from collections import deque

        decisions = []

        # Get initial accuser for loyalty checks
        initial_accuser = list(accusers)[0]

        # BFS traversal
        accuser_has_friends = any(
            self.graph.get_edge(initial_accuser, neighbor) == 1
            for neighbor in self.graph.neighbors(initial_accuser)
            if neighbor != scapegoat
        )

        if not accuser_has_friends and self.verbose:
            print(f"⚠ WARNING: {initial_accuser} has no friends!", file=sys.stderr)

        visited = {scapegoat}
        queue = deque([initial_accuser])
        visited.add(initial_accuser)

        if self.verbose:
            print(f"Processing nodes with LOYALTY rules...", file=sys.stderr)

        while queue:
            current = queue.popleft()

            # Check loyalty BEFORE applying contagion rules
            if self.should_defend_community_member(current, scapegoat, initial_accuser):
                # LOYALTY: Defend community member
                reason = (
                    f"Community loyalty: defending {scapegoat} "
                    f"against external attack from {self.get_community(initial_accuser)}"
                )

                decision = ContagionDecision(
                    node=current,
                    action="defend",
                    reason=reason
                )
                decisions.append(decision)

                if self.verbose:
                    print(f"  {current}: DEFENDING {scapegoat} (loyalty)", file=sys.stderr)

                # Continue BFS through this node's friends (they can also defend)
                for neighbor in self.graph.neighbors(current):
                    if neighbor not in visited and self.graph.get_edge(current, neighbor) == 1:
                        visited.add(neighbor)
                        queue.append(neighbor)

                continue  # Skip normal contagion rules

            # Normal contagion rules (no loyalty override)
            from .decision import apply_contagion_rule

            actions_list = apply_contagion_rule(
                self.graph, current, scapegoat, accusers
            )

            for action, reason, target_node in actions_list:
                if action == "join_accusers":
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

                elif action == "hear_accusation":
                    self.graph.add_edge(current, scapegoat, -1)

                    decision = ContagionDecision(
                        node=current,
                        action=action,
                        reason=reason,
                        edge_flipped=(current, scapegoat),
                        old_sign=0,
                        new_sign=-1
                    )
                    decisions.append(decision)
                    accusers.add(current)

                    if self.verbose:
                        print(f"  {current}: {reason}", file=sys.stderr)

                elif action == "befriend_other":
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

                else:
                    decision = ContagionDecision(
                        node=current,
                        action=None,
                        reason=reason
                    )
                    decisions.append(decision)

                    if self.verbose:
                        print(f"  {current}: {reason}", file=sys.stderr)

            # Add friends to queue
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited and self.graph.get_edge(current, neighbor) == 1:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # Process unreachable nodes
        for node in self.graph.nodes:
            if node not in visited:
                from .decision import apply_contagion_rule
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

        # Cleanup pass (resolve --- triangles within accusers)
        cleanup_decisions = self._resolve_community_conflicts(scapegoat)
        if cleanup_decisions:
            decisions.extend(cleanup_decisions)
            if self.verbose:
                print(f"\nCommunity unity pass: {len(cleanup_decisions)} edges flipped", file=sys.stderr)

        return decisions
