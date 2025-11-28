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
