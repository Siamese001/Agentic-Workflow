"""DEPRECATED: Legacy LIC implementation.
This file is preserved only for archival/reference.
All runtime LIC behavior now uses the atomic engine under l1/l2/l3/l4/l5.
Do NOT import from this module in new code."""

"""
K1ResearchExecutor (L2 Execution Layer)

STRICT L2 RULES:
    • Execution ONLY.
    • NO planning (L1).
    • NO orchestration (L3).
    • NO safety (L5).
    • NO state definitions (L4).
    • NO implemention of retrieval or RAG.
    • NO prompt building, NO generation logic.

This file defines ONLY the scaffolding for multi-hop research execution.
"""

class K1ResearchExecutor:
    """
    Executes multi-hop research according to retrieval_plan defined in L1.
    NO LOGIC — scaffolding only.
    """

    def __init__(self):
        """Initialize research executor. NO logic."""
        pass

    def execute(self, plan, state):
        """
        Execute research pipeline.

        Args:
            plan: LICPlan containing retrieval_plan
            state: LICState for logging outputs
        """
        pass

    def run_single_hop(self, query):
        """Stub for a single retrieval hop. NO logic."""
        pass

    def aggregate_results(self, hop_outputs):
        """Stub combining multi-hop outputs. NO logic."""
        pass

    def finalize_research(self, aggregated):
        """Stub for final research output."""
        pass
