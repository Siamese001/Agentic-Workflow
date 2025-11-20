# FILE: 10_10/self_correction.py
"""
Self-Correction Surfaces (v10_10)
=================================

v10_10 refactor of the v10_9 self_correction module.

This version:

    • NO longer operates on raw state dicts.
    • NO longer uses SelfCorrectionSurface enums or SafetyIssue types.
    • Operates directly on typed L2 results:
        - StrategyResult
        - RAGResult
        - DraftingResult
        - QAResult
        - SafetyResult
    • Produces simple, typed CorrectionSignal objects.
    • Provides:
        - evaluate_all_surfaces(...) → list[CorrectionSignal]
        - aggregate_correction_signals(...) → best CorrectionSignal | None

Responsibilities:
    • Detect when a retry/replan is advisable.
    • Provide severity + recommended_action hints to L3.
    • Remain PURE decision logic (no I/O, no LLM, no state mutation).

Non-Responsibilities:
    • No orchestration (L3 handles retries).
    • No LLM/tool execution (L2).
    • No safety decisions (L5).
    • No state patching (L4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from models import (
    StrategyResult,
    RAGResult,
    DraftingResult,
    QAResult,
    SafetyResult,
)
from observability import record_event


# =============================================================================
# Correction Signal
# =============================================================================

@dataclass
class CorrectionSignal:
    """
    Correction signal emitted by a surface evaluator.

    Fields:
        surface           – logical domain ("strategy", "rag", "drafting", "qa", "safety").
        severity          – 0..3 (0 = none; 1 = mild; 2 = moderate; 3 = severe).
        reason            – short human-readable explanation.
        recommended_action – coarse-grained hint for L3 or meta-layer:
                             "retry_strategy", "retry_rag", "retry_drafting",
                             "retry_qa", "retry_safety", "none".
    """

    surface: str
    severity: int
    reason: str
    recommended_action: str = "none"

    @property
    def needs_correction(self) -> bool:
        return self.severity >= 1


# =============================================================================
# Strategy Surface
# =============================================================================

def _evaluate_strategy_surface(strategy: StrategyResult) -> CorrectionSignal:
    """
    Strategy surface: check if chosen branch is valid and substantive.
    """
    if not strategy.branches:
        return CorrectionSignal(
            surface="strategy",
            severity=3,
            reason="No strategy branches generated.",
            recommended_action="retry_strategy",
        )

    if strategy.chosen_branch_id not in [b.id for b in strategy.branches]:
        return CorrectionSignal(
            surface="strategy",
            severity=3,
            reason="Chosen strategy branch ID is invalid.",
            recommended_action="retry_strategy",
        )

    chosen_text = strategy.get_chosen_branch_text().strip()
    if len(chosen_text) < 40:
        return CorrectionSignal(
            surface="strategy",
            severity=2,
            reason="Chosen strategy branch is too short or uninformative.",
            recommended_action="retry_strategy",
        )

    return CorrectionSignal(surface="strategy", severity=0, reason="OK")


# =============================================================================
# RAG Surface
# =============================================================================

def _evaluate_rag_surface(rag: RAGResult) -> CorrectionSignal:
    """
    RAG surface: check if retrieval was insufficient.
    """
    if not rag.evidence:
        return CorrectionSignal(
            surface="rag",
            severity=2,
            reason="No RAG evidence retrieved.",
            recommended_action="retry_rag",
        )

    low_scores = [ev for ev in rag.evidence if ev.score < 0.01]
    if len(low_scores) == len(rag.evidence):
        return CorrectionSignal(
            surface="rag",
            severity=2,
            reason="All RAG evidence scores are extremely low.",
            recommended_action="retry_rag",
        )

    return CorrectionSignal(surface="rag", severity=0, reason="OK")


# =============================================================================
# Drafting Surface
# =============================================================================

def _evaluate_drafting_surface(drafting: DraftingResult) -> CorrectionSignal:
    """
    Drafting surface: check if draft has sections and content.
    """
    if not drafting.sections:
        return CorrectionSignal(
            surface="drafting",
            severity=3,
            reason="Drafting produced zero sections.",
            recommended_action="retry_drafting",
        )

    blank = [s for s in drafting.sections if not s.text.strip()]
    if blank:
        return CorrectionSignal(
            surface="drafting",
            severity=2,
            reason=f"{len(blank)} drafting sections are blank.",
            recommended_action="retry_drafting",
        )

    return CorrectionSignal(surface="drafting", severity=0, reason="OK")


# =============================================================================
# QA Surface
# =============================================================================

def _evaluate_qa_surface(qa: QAResult) -> CorrectionSignal:
    """
    QA surface: check for failed QA checks.
    """
    failed = [chk for chk in qa.checks if not chk.passed]

    if len(failed) >= 3:
        return CorrectionSignal(
            surface="qa",
            severity=3,
            reason=f"{len(failed)} QA checks failed.",
            recommended_action="retry_qa",
        )

    if 1 <= len(failed) <= 2:
        return CorrectionSignal(
            surface="qa",
            severity=2,
            reason=f"{len(failed)} QA checks failed.",
            recommended_action="retry_drafting",
        )

    return CorrectionSignal(surface="qa", severity=0, reason="OK")


# =============================================================================
# Safety Surface
# =============================================================================

def _evaluate_safety_surface(safety: SafetyResult) -> CorrectionSignal:
    """
    Safety surface: detect blocking safety findings.
    """
    blocking = [f for f in safety.findings if f.blocking]

    if blocking:
        return CorrectionSignal(
            surface="safety",
            severity=3,
            reason="Blocking safety findings present.",
            recommended_action="retry_safety",
        )

    return CorrectionSignal(surface="safety", severity=0, reason="OK")


# =============================================================================
# Public API: Evaluate All Surfaces
# =============================================================================

def evaluate_all_surfaces(
    strategy: StrategyResult,
    rag: RAGResult,
    drafting: DraftingResult,
    qa: QAResult,
    safety: SafetyResult,
) -> List[CorrectionSignal]:
    """
    Evaluate all correction surfaces and return a list of CorrectionSignal objects.
    """
    signals = [
        _evaluate_strategy_surface(strategy),
        _evaluate_rag_surface(rag),
        _evaluate_drafting_surface(drafting),
        _evaluate_qa_surface(qa),
        _evaluate_safety_surface(safety),
    ]

    for sig in signals:
        record_event(
            "self_correction_surface_evaluated",
            {
                "surface": sig.surface,
                "severity": sig.severity,
                "recommended_action": sig.recommended_action,
            },
        )

    return signals


def aggregate_correction_signals(signals: List[CorrectionSignal]) -> Optional[CorrectionSignal]:
    """
    Aggregate signals into a single "best" CorrectionSignal.

    Strategy:
        • Select highest severity.
        • If multiple share the highest severity, pick the first
          in canonical order (strategy → rag → drafting → qa → safety).
    """
    if not signals:
        return None

    # Filter to those that need correction
    needing = [s for s in signals if s.needs_correction]
    if not needing:
        return None

    # Severity priority
    best = max(needing, key=lambda s: s.severity)
    return best
