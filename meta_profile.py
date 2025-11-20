# FILE: 10_10/meta_profile.py
"""
Meta Profile & Adaptive Biases (v10_10) — META LAYER ONLY
=========================================================

Refactored from v10_9 meta_profile.py to align with the v10_10 architecture.

This module defines the *meta-layer* profile for the agentic system. It is
NOT part of L1–L5, but provides SOFT BIASES and historical signals that
L1, L2, routing, and self-correction may consult:

    • Model routing preferences (e.g., prefer fast vs robust).
    • Planning preferences (e.g., conservative vs exploratory).
    • QA-related hints (recent failures, extra passes).
    • Safety-related hints (heightened caution, HIL bias).
    • Rolling failure rates for QA and corrections.
    • Provider preference hints (prefer OpenAI vs Anthropic).

Strict layer constraints (Agentic Guardrails):
    • NO L1 planning (no PlanObject creation).
    • NO L2 execution (no tool/LLM calls).
    • NO L3 DAG/orchestration logic.
    • NO L4 state mutation (no StateAdapter usage).
    • NO L5 safety/policy decisions.

It is safe to consider this a v10_10 “L6 META” component.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from models import QAResult, SafetyResult
from self_correction import CorrectionSignal


# ============================================================================
# 1. META PROFILE DATA CLASSES (BIAS STRUCTURES)
# ============================================================================


@dataclass
class RoutingBias:
    """
    Routing-level preferences for L2/L5.

    Fields:
        prefer_fast:             prefer cheaper/faster models
        prefer_robust_retrieval: bias toward more robust RAG settings
        prefer_long_context:     bias toward long-context models
    """
    prefer_fast: bool = False
    prefer_robust_retrieval: bool = False
    prefer_long_context: bool = False


@dataclass
class PlanningBias:
    """
    Planning (L1 reasoning) preferences.

    Fields:
        conservative:           reduce branching / depth
        exploratory:            allow more branches / alternatives
        deterministic_recovery: bias toward structured recovery plans
    """
    conservative: bool = False
    exploratory: bool = False
    deterministic_recovery: bool = False


@dataclass
class QaBias:
    """
    QA-related preferences and signals.

    Fields:
        recent_failures:    QA has recently failed often
        require_extra_pass: bias toward extra QA passes
    """
    recent_failures: bool = False
    require_extra_pass: bool = False


@dataclass
class SafetyBias:
    """
    Safety-related preferences.

    Fields:
        heightened_caution:     bias toward stricter safety paths
        human_review_important: HIL review is frequently beneficial
    """
    heightened_caution: bool = False
    human_review_important: bool = False


@dataclass
class MetaUpdate:
    """
    Single meta-update record used in history.

    Fields:
        source:    "spans" | "self_correction" | "run_summary" | ...
        payload:   arbitrary context information
        deltas:    snapshot of bias fields that changed
    """
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    deltas: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# 2. META PROFILE (INTERNAL STATE) + SNAPSHOT (L1/L2 VIEW)
# ============================================================================

@dataclass
class MetaProfile:
    """
    Global meta-configuration for adaptive behavior (INTERNAL STATE).

    Fields:
        • routing_bias       – knobs influencing model routing.
        • planning_bias      – knobs influencing L1 planners.
        • qa_bias            – knobs based on QA outcomes.
        • safety_bias        – knobs based on safety outcomes.
        • history            – recent meta-updates (for inspection/tests).
        • last_10_qa_flags   – rolling QA failures (0/1).
        • last_10_corr_flags – rolling correction fires (0/1).
        • total_runs         – number of DAG runs observed.
        • total_corrections  – total runs with corrections.
        • total_qa_failures  – total runs with QA failures.
        • total_safety_failures – total runs with blocking safety findings.

    This object is mutable and should not be exposed to L1/L2 directly.
    """

    routing_bias: RoutingBias = field(default_factory=RoutingBias)
    planning_bias: PlanningBias = field(default_factory=PlanningBias)
    qa_bias: QaBias = field(default_factory=QaBias)
    safety_bias: SafetyBias = field(default_factory=SafetyBias)
    history: List[MetaUpdate] = field(default_factory=list)

    last_10_qa_flags: List[int] = field(default_factory=list)
    last_10_corr_flags: List[int] = field(default_factory=list)
    total_runs: int = 0
    total_corrections: int = 0
    total_qa_failures: int = 0
    total_safety_failures: int = 0

    def snapshot_dict(self) -> Dict[str, Any]:
        """
        Full snapshot as a dict (used for logging, debugging).
        """
        return {
            "routing_bias": asdict(self.routing_bias),
            "planning_bias": asdict(self.planning_bias),
            "qa_bias": asdict(self.qa_bias),
            "safety_bias": asdict(self.safety_bias),
            "history": [
                {
                    "source": h.source,
                    "payload": dict(h.payload),
                    "deltas": dict(h.deltas),
                }
                for h in self.history[-10:]
            ],
            "last_10_qa_flags": list(self.last_10_qa_flags),
            "last_10_corr_flags": list(self.last_10_corr_flags),
            "total_runs": self.total_runs,
            "total_corrections": self.total_corrections,
            "total_qa_failures": self.total_qa_failures,
            "total_safety_failures": self.total_safety_failures,
        }

    def _record_update(self, source: str, payload: Dict[str, Any], deltas: Dict[str, Any]) -> None:
        """
        Internal helper to append a MetaUpdate to history.
        """
        if not deltas:
            return
        self.history.append(
            MetaUpdate(
                source=source,
                payload=dict(payload),
                deltas=dict(deltas),
            )
        )


@dataclass(frozen=True)
class MetaProfileSnapshot:
    """
    Immutable, read-only snapshot consumed by L1/L2/L2 routing.

    This is the ONLY shape that core layers should depend on.

    Fields:
        qa_failure_rate_last_10
        correction_rate_last_10
        prefers_anthropic
        prefers_openai
        total_runs
        total_corrections
        total_qa_failures
        total_safety_failures
    """

    qa_failure_rate_last_10: float = 0.0
    correction_rate_last_10: float = 0.0
    prefers_anthropic: bool = False
    prefers_openai: bool = True
    total_runs: int = 0
    total_corrections: int = 0
    total_qa_failures: int = 0
    total_safety_failures: int = 0


# ============================================================================
# 3. META PROFILE UPDATER
# ============================================================================

@dataclass
class MetaProfileUpdater:
    """
    Updater responsible for mutating MetaProfile and producing snapshots.

    It encapsulates the v10_9 heuristics:
        • update_from_spans
        • update_from_self_correction
        • update_from_run_summary

    But returns a MetaProfileSnapshot for consumption by 10_10 components.
    """

    profile: MetaProfile = field(default_factory=MetaProfile)

    # ------------------------- SPAN-BASED UPDATE -----------------------------

    def update_from_spans(self, spans: List[Dict[str, Any]]) -> None:
        """
        Update routing_bias from a list of span dicts:

            {"name": "planning"|"execution", "duration_ms": float}

        Heuristics (restored v10_9 semantics):
            • If planning consistently slower than execution → prefer_fast = True.
            • Else → prefer_fast = False.
        """
        if not spans:
            return

        planning = next((s for s in spans if s.get("name") == "planning"), None)
        execution = next((s for s in spans if s.get("name") == "execution"), None)

        p_ms = float(planning.get("duration_ms", 0.0)) if planning else 0.0
        e_ms = float(execution.get("duration_ms", 0.0)) if execution else 0.0

        payload = {"planning_ms": p_ms, "execution_ms": e_ms}
        deltas: Dict[str, Any] = {}

        prefer_fast_before = self.profile.routing_bias.prefer_fast

        if p_ms > e_ms * 1.1 and p_ms > 0.0:
            self.profile.routing_bias.prefer_fast = True
        else:
            self.profile.routing_bias.prefer_fast = False

        if self.profile.routing_bias.prefer_fast != prefer_fast_before:
            deltas["routing_bias.prefer_fast"] = self.profile.routing_bias.prefer_fast

        self.profile._record_update(source="spans", payload=payload, deltas=deltas)

    # -------------------- SELF-CORRECTION-BASED UPDATE ----------------------

    def update_from_self_correction(self, block: Dict[str, Any]) -> None:
        """
        Update biases from a self_correction block.

        Heuristics:
            • surface == "qa_recheck":
                  planning_bias.conservative = True
                  qa_bias.recent_failures = True
            • surface == "strategy_replan":
                  planning_bias.exploratory = True
            • surface == "hil_escalation":
                  safety_bias.human_review_important = True
            • surface == "rag_retry":
                  routing_bias.prefer_robust_retrieval = True
            • surface == "checkpoint_recovery":
                  planning_bias.deterministic_recovery = True
        """
        if not block:
            return

        needed = bool(block.get("needed", False))
        surface = str(block.get("surface") or "")

        if not needed or not surface:
            return

        payload = {
            "surface": surface,
            "rationale": block.get("rationale", ""),
            "metadata": block.get("metadata", {}),
        }
        deltas: Dict[str, Any] = {}

        if surface == "qa_recheck":
            if not self.profile.planning_bias.conservative:
                self.profile.planning_bias.conservative = True
                deltas["planning_bias.conservative"] = True
            if not self.profile.qa_bias.recent_failures:
                self.profile.qa_bias.recent_failures = True
                deltas["qa_bias.recent_failures"] = True

        elif surface == "strategy_replan":
            if not self.profile.planning_bias.exploratory:
                self.profile.planning_bias.exploratory = True
                deltas["planning_bias.exploratory"] = True

        elif surface == "hil_escalation":
            if not self.profile.safety_bias.human_review_important:
                self.profile.safety_bias.human_review_important = True
                deltas["safety_bias.human_review_important"] = True

        elif surface == "rag_retry":
            if not self.profile.routing_bias.prefer_robust_retrieval:
                self.profile.routing_bias.prefer_robust_retrieval = True
                deltas["routing_bias.prefer_robust_retrieval"] = True

        elif surface == "checkpoint_recovery":
            if not self.profile.planning_bias.deterministic_recovery:
                self.profile.planning_bias.deterministic_recovery = True
                deltas["planning_bias.deterministic_recovery"] = True

        self.profile._record_update(source="self_correction", payload=payload, deltas=deltas)

    # ---------------------- RUN-SUMMARY-BASED UPDATE -----------------------

    def update_from_run_summary(self, run_summary: Dict[str, Any]) -> None:
        """
        Update biases from a run_summary with shape:

            {
              "workflow_id": str,
              "phases": [...],
              "timings": {...},
              "counts": {...},
              "issues": {
                "qa": [...],
                "safety": [...],
                "hil": [...],
                ...
              },
            }

        Heuristics:
            • QA issues       → conservative planning, qa.recent_failures = True.
            • Safety issues   → safety.heightened_caution = True.
            • HIL issues      → safety.human_review_important = True.
        """
        if not run_summary:
            return

        issues = run_summary.get("issues") or {}
        qa_issues = issues.get("qa") or []
        safety_issues = issues.get("safety") or []
        hil_issues = issues.get("hil") or []

        payload = {
            "qa_issue_count": len(qa_issues),
            "safety_issue_count": len(safety_issues),
            "hil_issue_count": len(hil_issues),
        }
        deltas: Dict[str, Any] = {}

        if qa_issues:
            if not self.profile.planning_bias.conservative:
                self.profile.planning_bias.conservative = True
                deltas["planning_bias.conservative"] = True
            if not self.profile.qa_bias.recent_failures:
                self.profile.qa_bias.recent_failures = True
                deltas["qa_bias.recent_failures"] = True

        if safety_issues:
            if not self.profile.safety_bias.heightened_caution:
                self.profile.safety_bias.heightened_caution = True
                deltas["safety_bias.heightened_caution"] = True

        if hil_issues:
            if not self.profile.safety_bias.human_review_important:
                self.profile.safety_bias.human_review_important = True
                deltas["safety_bias.human_review_important"] = True

        self.profile._record_update(source="run_summary", payload=payload, deltas=deltas)

    # ------------------ DIRECT UPDATE FROM DAG RESULTS ----------------------

    def update_from_dag_outputs(
        self,
        qa: QAResult,
        safety: SafetyResult,
        corrections: List[CorrectionSignal],
    ) -> None:
        """
        v10_10-native meta update after a DAG run, fed with L2/L3 outputs.

        This keeps rolling QA/correction/safety stats up to date.
        """

        self.profile.total_runs += 1

        # QA failures
        qa_failed = any(not chk.passed for chk in (qa.checks or []))
        if qa_failed:
            self.profile.total_qa_failures += 1
            self.profile.last_10_qa_flags.append(1)
        else:
            self.profile.last_10_qa_flags.append(0)

        self.profile.last_10_qa_flags = self.profile.last_10_qa_flags[-10:]

        # Correction signals
        correction_fired = any(sig.severity >= 1 for sig in (corrections or []))
        if correction_fired:
            self.profile.total_corrections += 1
            self.profile.last_10_corr_flags.append(1)
        else:
            self.profile.last_10_corr_flags.append(0)

        self.profile.last_10_corr_flags = self.profile.last_10_corr_flags[-10:]

        # Safety failures
        safety_violation = any(f.blocking for f in (safety.findings or []))
        if safety_violation:
            self.profile.total_safety_failures += 1

    # --------------------------- SNAPSHOT -----------------------------------

    def snapshot(self) -> MetaProfileSnapshot:
        """
        Construct an immutable MetaProfileSnapshot for L1/L2/L2 routing.
        """
        qa_fail_rate = (
            sum(self.profile.last_10_qa_flags) / len(self.profile.last_10_qa_flags)
            if self.profile.last_10_qa_flags else 0.0
        )
        corr_rate = (
            sum(self.profile.last_10_corr_flags) / len(self.profile.last_10_corr_flags)
            if self.profile.last_10_corr_flags else 0.0
        )

        # Provider preference heuristics:
        prefers_anthropic = False
        prefers_openai = True

        if qa_fail_rate > 0.4:
            prefers_anthropic = True
            prefers_openai = False
        elif corr_rate < 0.1 and self.profile.total_runs > 3:
            prefers_openai = True
            prefers_anthropic = False

        return MetaProfileSnapshot(
            qa_failure_rate_last_10=qa_fail_rate,
            correction_rate_last_10=corr_rate,
            prefers_anthropic=prefers_anthropic,
            prefers_openai=prefers_openai,
            total_runs=self.profile.total_runs,
            total_corrections=self.profile.total_corrections,
            total_qa_failures=self.profile.total_qa_failures,
            total_safety_failures=self.profile.total_safety_failures,
        )


# ============================================================================
# 4. GLOBAL META-PROFILE STORE (META-LAYER ONLY)
# ============================================================================

# A single global meta-profile store, as in v10_9, but its shape is now
# strictly controlled and only exposed to L1/L2 via MetaProfileSnapshot.
_META_UPDATER = MetaProfileUpdater()


# ---------------------------- WRITE PATHS -----------------------------------

def update_from_spans(spans: List[Dict[str, Any]]) -> None:
    _META_UPDATER.update_from_spans(spans)


def update_from_self_correction(block: Dict[str, Any]) -> None:
    _META_UPDATER.update_from_self_correction(block)


def update_from_run_summary(run_summary: Dict[str, Any]) -> None:
    _META_UPDATER.update_from_run_summary(run_summary)


def update_from_dag_outputs(
    qa: QAResult,
    safety: SafetyResult,
    corrections: List[CorrectionSignal],
) -> None:
    _META_UPDATER.update_from_dag_outputs(qa, safety, corrections)


# ---------------------------- READ PATHS ------------------------------------

def get_meta_profile_snapshot() -> MetaProfileSnapshot:
    """
    Primary accessor used by L1/L2/L2 routing (v10_10-native).
    """
    return _META_UPDATER.snapshot()


# The following accessors preserve v10_9 semantics for any remaining calls.
# They can be deprecated over time once all callers move to the snapshot.

def get_routing_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.routing_bias)


def get_planning_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.planning_bias)


def get_qa_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.qa_bias)


def get_safety_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.safety_bias)
