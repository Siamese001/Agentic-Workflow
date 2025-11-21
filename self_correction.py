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

    • Provides:
        - evaluate_all_surfaces(...) → list[CorrectionSignal]
        - aggregate_correction_signals(...) → best CorrectionSignal | None

Responsibilities:
    • Detect when a re-run of part of the pipeline would likely improve quality.
    • NEVER call LLMs or tools.
    • NEVER mutate WorkflowState.
    • Provide deterministic, side-effect-free advice to the L3 workflow graph.

This module is purely META-layer logic:

    - It analyzes L2 outputs (StrategyResult, etc.).
    - It emits structured CorrectionSignal objects.
    - L3 (workflow_graph) decides whether/how to apply corrections.
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
    recommended_action: str

    @property
    def needs_correction(self) -> bool:
        """Return True if this signal indicates that some correction is needed."""
        return self.severity > 0 and self.recommended_action != "none"


# =============================================================================
# Strategy Surface
# =============================================================================


def _evaluate_strategy_surface(strategy: StrategyResult) -> CorrectionSignal:
    """
    Inspect StrategyResult and decide whether the strategy surface needs correction.

    Heuristics (deterministic, non-LLM):

        • If there are zero branches → severe issue → retry strategy.
        • If chosen_branch_id is None or invalid:
             – severity = 3 (severe)
             – recommended_action = "retry_strategy"
        • If chosen branch text is suspiciously short (e.g., < 40 chars):
             – severity = 2 (moderate)
             – recommended_action = "retry_strategy"
        • Otherwise:
             – severity = 0 (no correction)
    """
    # No branches at all → strong signal to retry strategy
    if not strategy.branches:
        return CorrectionSignal(
            surface="strategy",
            severity=3,
            reason="No strategy branches were produced.",
            recommended_action="retry_strategy",
        )

    # chosen_branch_id must correspond to an existing branch
    branch_ids = {b.id for b in strategy.branches}
    if strategy.chosen_branch_id not in branch_ids:
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

    return CorrectionSignal(
        surface="strategy",
        severity=0,
        reason="Strategy surface is acceptable.",
        recommended_action="none",
    )


# =============================================================================
# RAG Surface
# =============================================================================


def _evaluate_rag_surface(rag: RAGResult) -> CorrectionSignal:
    """
    Inspect RAGResult evidence for retrieval/coverage issues.

    Heuristics:

        • If no evidence at all:
             – severity = 3
             – recommended_action = "retry_rag"
        • If evidence exists but is very small (< 3 items) AND none are marked
          as "hybrid" or "resume_experience":
             – severity = 2
             – recommended_action = "retry_rag"
        • Otherwise:
             – severity = 0
    """
    evidence = rag.evidence or []

    if not evidence:
        return CorrectionSignal(
            surface="rag",
            severity=3,
            reason="No retrieval evidence was produced.",
            recommended_action="retry_rag",
        )

    if len(evidence) < 3:
        has_hybrid = any(ev.source == "hybrid_job_resume" for ev in evidence)
        has_resume = any(ev.source == "resume_experience" for ev in evidence)
        if not has_hybrid and not has_resume:
            return CorrectionSignal(
                surface="rag",
                severity=2,
                reason="Too few evidence items and no hybrid/resume coverage.",
                recommended_action="retry_rag",
            )

    return CorrectionSignal(
        surface="rag",
        severity=0,
        reason="RAG surface is acceptable.",
        recommended_action="none",
    )


# =============================================================================
# Drafting Surface
# =============================================================================


def _evaluate_drafting_surface(drafting: DraftingResult) -> CorrectionSignal:
    """
    Inspect DraftingResult section structure.

    Heuristics:

        • If zero sections, or total characters across sections < 400:
             – severity = 3
             – recommended_action = "retry_drafting"
        • If < 3 sections:
             – severity = 2
             – recommended_action = "retry_drafting"
        • Otherwise:
             – severity = 0
    """
    sections = drafting.sections or []
    if not sections:
        return CorrectionSignal(
            surface="drafting",
            severity=3,
            reason="Drafting produced no sections.",
            recommended_action="retry_drafting",
        )

    total_chars = sum(len(s.text or "") for s in sections)
    if total_chars < 400:
        return CorrectionSignal(
            surface="drafting",
            severity=3,
            reason="Drafting output is too short.",
            recommended_action="retry_drafting",
        )

    if len(sections) < 3:
        return CorrectionSignal(
            surface="drafting",
            severity=2,
            reason="Too few sections produced by drafting.",
            recommended_action="retry_drafting",
        )

    return CorrectionSignal(
        surface="drafting",
        severity=0,
        reason="Drafting surface is acceptable.",
        recommended_action="none",
    )


# =============================================================================
# QA Surface
# =============================================================================


def _evaluate_qa_surface(qa: QAResult) -> CorrectionSignal:
    """
    Inspect QAResult for severity of findings.

    Heuristics:

        • If there are ≥ 3 high-severity findings:
             – severity = 3
             – recommended_action = "retry_qa"
        • If there are ≥ 5 total findings (any severity):
             – severity = 2
             – recommended_action = "retry_qa"
        • Otherwise:
             – severity = 0
    """
    checks = qa.checks or []
    if not checks:
        # No QA checks present does not automatically mean retry;
        # treat it as "no signal".
        return CorrectionSignal(
            surface="qa",
            severity=0,
            reason="No QA checks present; treating as neutral.",
            recommended_action="none",
        )

    high_severity = [chk for chk in checks if getattr(chk, "severity", "").lower() == "high"]
    if len(high_severity) >= 3:
        return CorrectionSignal(
            surface="qa",
            severity=3,
            reason="Three or more high-severity QA findings detected.",
            recommended_action="retry_qa",
        )

    if len(checks) >= 5:
        return CorrectionSignal(
            surface="qa",
            severity=2,
            reason="Many QA findings detected; consider retry.",
            recommended_action="retry_qa",
        )

    return CorrectionSignal(
        surface="qa",
        severity=0,
        reason="QA surface is acceptable.",
        recommended_action="none",
    )


# =============================================================================
# Safety Surface
# =============================================================================


def _evaluate_safety_surface(safety: SafetyResult) -> CorrectionSignal:
    """
    Inspect SafetyResult for policy violations.

    Heuristics:

        • Any "high" severity finding:
             – severity = 3
             – recommended_action = "retry_safety"
        • ≥ 3 total findings of any severity:
             – severity = 2
             – recommended_action = "retry_safety"
        • Otherwise:
             – severity = 0
    """
    findings = safety.findings or []
    if not findings:
        return CorrectionSignal(
            surface="safety",
            severity=0,
            reason="No safety findings present.",
            recommended_action="none",
        )

    high = [f for f in findings if getattr(f, "severity", "").lower() == "high"]
    if high:
        return CorrectionSignal(
            surface="safety",
            severity=3,
            reason="High-severity safety findings present.",
            recommended_action="retry_safety",
        )

    if len(findings) >= 3:
        return CorrectionSignal(
            surface="safety",
            severity=2,
            reason="Multiple safety findings present.",
            recommended_action="retry_safety",
        )

    return CorrectionSignal(
        surface="safety",
        severity=0,
        reason="Safety surface is acceptable.",
        recommended_action="none",
    )


# =============================================================================
# Public API
# =============================================================================


def evaluate_all_surfaces(
    *,
    strategy: StrategyResult,
    rag: RAGResult,
    drafting: DraftingResult,
    qa: QAResult,
    safety: SafetyResult,
) -> List[CorrectionSignal]:
    """
    Evaluate all L2 surfaces and return a list of CorrectionSignal.

    The list will contain one signal per surface:
        ["strategy", "rag", "drafting", "qa", "safety"]

    Each signal may have severity 0..3 and a recommended_action.
    """
    signals: List[CorrectionSignal] = []

    signals.append(_evaluate_strategy_surface(strategy))
    signals.append(_evaluate_rag_surface(rag))
    signals.append(_evaluate_drafting_surface(drafting))
    signals.append(_evaluate_qa_surface(qa))
    signals.append(_evaluate_safety_surface(safety))

    return signals


def aggregate_correction_signals(
    signals: List[CorrectionSignal],
) -> Optional[CorrectionSignal]:
    """
    Aggregate a list of CorrectionSignal into a single best signal.

    Rules:

        • Ignore all signals where needs_correction is False.
        • If none need correction, return None.
        • Otherwise, pick the signal with highest severity.
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
