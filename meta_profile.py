# FILE: 10_10/meta_profile.py
"""
Meta-Learning Profile (v10_10)
==============================

Responsibilities:
    • Capture historical signals about workflow behavior.
    • Provide a snapshot (read-only) to L1 and L2 for:
         - Complexity estimation
         - RoutingPolicy model selection bias
    • Allow deterministic updates from L3/L4 after each run.

Non-responsibilities:
    • No LLM calls.
    • No safety decisions.
    • No state mutation outside of structured update().
    • No orchestration (L3 does that).
    • No caching or runtime behavior.

This module enables pillars:
    • P6: Reasoning Models (meta-aware policies)
    • P11: Cost & Optimization
    • P10: Observability (exposed metrics)
    • P5: Capability Maturity (self-improvement loop)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from models import QAResult, SafetyResult
from self_correction import CorrectionSignal
from observability import record_event


# =============================================================================
# Meta Profile Snapshot (Read-only for L1/L2)
# =============================================================================

@dataclass(frozen=True)
class MetaProfileSnapshot:
    """
    Immutable snapshot accessible to L1/L2.

    Fields influence:
        • complexity classification
        • routing provider selection (openai vs anthropic)
        • branch depth (ToT)
    """

    # Historical signal rates:
    qa_failure_rate_last_10: float = 0.0
    correction_rate_last_10: float = 0.0

    # Provider preference hints:
    prefers_anthropic: bool = False
    prefers_openai: bool = True

    # Optional counters:
    total_runs: int = 0
    total_corrections: int = 0
    total_qa_failures: int = 0
    total_safety_failures: int = 0


# =============================================================================
# Meta-Profile Updater (Write Path)
# =============================================================================

@dataclass
class MetaProfileUpdater:
    """
    A simple deterministic updater for generating a fresh MetaProfileSnapshot
    after each DAG execution.

    This updater is called by L4 or L3 external logic (not within L3 itself).
    """

    # Internal rolling logs for last 10 runs:
    last_10_correction_flags: List[int] = field(default_factory=list)
    last_10_qa_flags: List[int] = field(default_factory=list)

    # Persistent counters:
    total_runs: int = 0
    total_corrections: int = 0
    total_qa_failures: int = 0
    total_safety_failures: int = 0

    # Provider preference:
    prefers_anthropic: bool = False
    prefers_openai: bool = True

    # ----------------------------------------------------------------------
    # Update Entry Point
    # ----------------------------------------------------------------------

    def update(
        self,
        qa: QAResult,
        safety: SafetyResult,
        corrections: List[CorrectionSignal],
    ) -> MetaProfileSnapshot:
        """
        Update meta-learning profile using outputs of a single DAG execution.
        """

        self.total_runs += 1

        # --- QA Failures ---------------------------------------------------
        qa_failed = any(not chk.passed for chk in (qa.checks or []))
        if qa_failed:
            self.total_qa_failures += 1
            self.last_10_qa_flags.append(1)
        else:
            self.last_10_qa_flags.append(0)

        # Maintain rolling window size
        self.last_10_qa_flags = self.last_10_qa_flags[-10:]


        # --- Correction Signals --------------------------------------------
        correction_fired = any(sig.severity >= 1 for sig in (corrections or []))
        if correction_fired:
            self.total_corrections += 1
            self.last_10_correction_flags.append(1)
        else:
            self.last_10_correction_flags.append(0)

        self.last_10_correction_flags = self.last_10_correction_flags[-10:]


        # --- Safety Failures ------------------------------------------------
        safety_violation = any(f.blocking for f in (safety.findings or []))
        if safety_violation:
            self.total_safety_failures += 1


        # --- Compute Rolling Rates -----------------------------------------
        qa_fail_rate = (
            sum(self.last_10_qa_flags) / len(self.last_10_qa_flags)
            if self.last_10_qa_flags else 0.0
        )
        correction_rate = (
            sum(self.last_10_correction_flags) / len(self.last_10_correction_flags)
            if self.last_10_correction_flags else 0.0
        )


        # --- Update Provider Preferences -----------------------------------
        # If QA repeatedly fails, prefer Anthropic for semantic depth.
        if qa_fail_rate > 0.4:
            self.prefers_anthropic = True
            self.prefers_openai = False

        # If correction rate stays low, prefer OpenAI for speed/economy.
        if correction_rate < 0.1 and self.total_runs > 3:
            self.prefers_openai = True
            self.prefers_anthropic = False


        # Emit observability event
        record_event(
            "meta_profile_updated",
            {
                "total_runs": self.total_runs,
                "qa_failure_rate_last_10": qa_fail_rate,
                "correction_rate_last_10": correction_rate,
                "prefers_openai": self.prefers_openai,
                "prefers_anthropic": self.prefers_anthropic,
            },
        )

        # Produce immutable snapshot
        return MetaProfileSnapshot(
            qa_failure_rate_last_10=qa_fail_rate,
            correction_rate_last_10=correction_rate,
            prefers_anthropic=self.prefers_anthropic,
            prefers_openai=self.prefers_openai,
            total_runs=self.total_runs,
            total_corrections=self.total_corrections,
            total_qa_failures=self.total_qa_failures,
            total_safety_failures=self.total_safety_failures,
        )


# =============================================================================
# Optional: Initialize an empty meta-profile
# =============================================================================

def new_meta_profile() -> MetaProfileSnapshot:
    """
    Convenience constructor for a default, empty meta-profile snapshot.
    """
    return MetaProfileSnapshot()

