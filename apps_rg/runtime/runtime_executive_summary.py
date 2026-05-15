"""apps_rg runtime executive summary — per-run summary dataclass."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

__all__ = ["RuntimeExecutiveSummary"]


@dataclass
class RuntimeExecutiveSummary:
    """Top-level summary of a single apps_rg run.

    Tracks identity, timing, section results, writeback status, and
    L6 observability handoff markers.
    """

    run_id: str = ""
    trace_id: str = ""
    target_company: str = ""
    target_role: str = ""
    target_level: str = ""
    generation_mode: str = ""
    start_timestamp: str = ""
    end_timestamp: str = ""
    total_duration_ms: int = 0
    sections: list[str] = field(default_factory=list)

    # Writeback accounting
    inert_writeback_candidates: int = 0
    uwg_committed_writes: int = 0
    pending_writeback_count: int = 0
    durable_commit_occurred: bool = False

    # Exit gate verdicts
    g21_verdict: str = ""
    g22_verdict: str = ""
    g23_verdict: str = ""
    g24_verdict: str = ""
    overall_exit_verdict: str = ""

    # Observability
    runtime_exhaust_bundle_emitted: bool = False
    l6_shadow_handoff_emitted: bool = False
    otel_span_count: int = 0

    # Provenance
    compilation_hash: str = ""
    evidence_digest: str = ""
    seal_digest: str = ""
    l5_certification_ref: str = ""

    # Metadata
    extras: dict[str, Any] = field(default_factory=dict)
