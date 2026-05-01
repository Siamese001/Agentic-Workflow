"""W1 Phase 5 — Semantic Cache Safety Veto Modules.

This package provides layered safety vetoes for semantic cache reuse:
- veto_protocol: Core Protocol class that all veto stages implement
- llm_judge_veto: Option C primary veto (LLM-as-judge)
- lexical_intent_veto: Option A pre-veto (deterministic lexical rules)
"""

from __future__ import annotations

from .veto_protocol import VetoStage, VetoResult, VetoStatus

__all__ = ["VetoStage", "VetoResult", "VetoStatus"]
