"""DEPRECATED: Legacy LIC implementation.
This file is preserved only for archival/reference.
All runtime LIC behavior now uses the atomic engine under l1/l2/l3/l4/l5.
Do NOT import from this module in new code."""

"""
LICState (L4 Layer)
Holds execution history and intermediate outputs.
"""

class LICState:
    """Stub state container."""

    def __init__(self):
        self.k_node_outputs = {}
        self.violations = []

    def record_output(self, k_node, output):
        """Record K-node output (stub)."""
        pass

    def record_violation(self, violation):
        """Record safety violation (stub)."""
        pass
