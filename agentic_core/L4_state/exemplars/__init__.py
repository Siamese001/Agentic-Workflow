"""Exemplar bank \u2014 W4 RH4.

Module-level SSOT for the E0 (exemplars) slot introduced in W3.

Public surface:
    ExemplarRecord \u2014 immutable dataclass representing one few-shot example.
    ExemplarBank   \u2014 in-memory store keyed by task_class. Pluggable retriever.
    select_top_k  \u2014 static keyword-matching retrieval (embedding-based in W7).
"""

from __future__ import annotations

from agentic_core.L4_state.exemplars.bank import ExemplarBank, ExemplarRecord
from agentic_core.L4_state.exemplars.retriever import select_top_k

__all__ = ["ExemplarBank", "ExemplarRecord", "select_top_k"]
