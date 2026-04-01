"""
L5 Safety — Retrieval Bridge Module

Provides RetrievalSafetyGate for wiring L5 retrieval guardrails
to the retrieval pipeline across all apps_* packages.
"""

from __future__ import annotations

# L5 Safety components for retrieval
from agentic_core.L5_safety.retrieval.retrieval_safety_gate import RetrievalSafetyGate

__all__ = [
    "RetrievalSafetyGate",
]
