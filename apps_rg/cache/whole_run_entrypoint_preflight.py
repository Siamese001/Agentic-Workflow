"""W9b — SSOT whole-run cache preflight (R1A → R1B) for all canonical entrypoints."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_rg.cache.r1a_adapter import check_r1a_cache, compute_r1a_key, stamp_r1a_cache
from apps_rg.cache.r1b_post_exit_ingest import ingest_post_exit_after_run
from apps_rg.cache.r1b_store import default_store_root
from apps_rg.cache.r1b_whole_run_preflight import (
    PREFLIGHT_ORDER,
    WholeRunR1BPreflightResult,
    execute_whole_run_r1b_preflight,
    write_r1b_preflight_receipt,
)

ENTRYPOINT_TEST_WHOLE_RUN_HARNESS = "tests.helpers.whole_run_spine_harness.run_whole_run_spine_harness"
ENTRYPOINT_CANONICAL_DISPATCH = "apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives"
ENTRYPOINT_DISPATCH_APPS_RG_RUN = "agentic_core.runtime.entry.apps_rg_dispatch.dispatch_apps_rg_run"
ENTRYPOINT_ENVELOPE_DISPATCH = "apps_rg.runtime.dispatch.apps_rg_dispatch.apps_rg_dispatch"


def _semantic_cache_r1b_enabled() -> bool:
    from apps_rg.runtime.embedding_settings import semantic_cache_r1b_eligible

    return semantic_cache_r1b_eligible()


def resolve_r1b_store_root(*, artifact_dir: Path | str | None = None) -> Path:
    """R1B SSOT store (not per-run scratch); optional override via env."""
    env = os.environ.get("APPS_RG_R1B_CACHE_ROOT", "").strip()
    if env:
        p = Path(env)
        return p if p.is_absolute() else (Path.cwd() / p).resolve()
    return default_store_root()


def resolve_preflight_receipt_dir(
    *,
    artifact_dir: Path | str | None,
    runs_dir: Path | str | None,
) -> Path:
    if artifact_dir and str(artifact_dir).strip():
        return Path(artifact_dir)
    if runs_dir and str(runs_dir).strip():
        return Path(runs_dir)
    return default_store_root().parent / "preflight_receipts"


@dataclass
class WholeRunCachePreflightOutcome:
    entrypoint: str
    preflight_order: tuple[str, ...] = PREFLIGHT_ORDER
    r1a_hit: bool = False
    r1a_artifact_dir: str = ""
    r1b_result: WholeRunR1BPreflightResult | None = None
    generation_required: bool = True
    c0_fact_vectors_consulted: bool = False
    section_lane: bool = False

    @property
    def r1b_hit(self) -> bool:
        return bool(self.r1b_result and self.r1b_result.r1b_hit)

    @property
    def outcome(self) -> str:
        if self.r1a_hit:
            return "r1a_hit"
        if self.r1b_hit:
            return "r1b_hit"
        if self.r1b_result and self.r1b_result.outcome == "r1b_inadmissible_only":
            return "r1b_inadmissible_only"
        return "fallthrough_generation"

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "preflight_order": list(self.preflight_order),
            "outcome": self.outcome,
            "r1a_hit": self.r1a_hit,
            "r1a_artifact_dir": self.r1a_artifact_dir,
            "r1b_hit": self.r1b_hit,
            "r1b_preflight": self.r1b_result.to_dict() if self.r1b_result else None,
            "generation_required": self.generation_required,
            "c0_fact_vectors_consulted": self.c0_fact_vectors_consulted,
            "section_lane_skipped_preflight": self.section_lane,
        }


def run_whole_run_cache_preflight(
    *,
    entrypoint: str,
    raw_request: dict[str, Any],
    target_company: str,
    target_role: str,
    artifact_dir: Path | str | None = None,
    runs_dir: Path | str | None = None,
    policy_hash: str | None = None,
    blueprint_hash: str | None = None,
    section: str = "",
) -> WholeRunCachePreflightOutcome:
    """R1A exact → R1B semantic (ROLE_TARGET_RUN) → generation on miss/inadmissible."""
    if str(section).strip():
        return WholeRunCachePreflightOutcome(
            entrypoint=entrypoint,
            generation_required=True,
            section_lane=True,
        )

    resume_hash = str(raw_request.get("resume_hash") or "")
    r1a_key = compute_r1a_key(
        source_resume_hash=resume_hash,
        target_company=target_company,
        target_role=target_role,
    )
    r1a_dir = check_r1a_cache(
        r1a_key,
        runs_dir=runs_dir or resolve_preflight_receipt_dir(artifact_dir=artifact_dir, runs_dir=runs_dir),
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
    )
    if r1a_dir:
        return WholeRunCachePreflightOutcome(
            entrypoint=entrypoint,
            r1a_hit=True,
            r1a_artifact_dir=r1a_dir,
            generation_required=False,
        )

    r1b_result: WholeRunR1BPreflightResult | None = None
    if _semantic_cache_r1b_enabled():
        store_root = resolve_r1b_store_root(artifact_dir=artifact_dir)
        r1b_result = execute_whole_run_r1b_preflight(
            raw_request=raw_request,
            runs_dir=str(store_root),
            prompt_profile_hash=str(policy_hash or ""),
            gate_profile_hash=str(blueprint_hash or ""),
        )
        receipt_dir = resolve_preflight_receipt_dir(artifact_dir=artifact_dir, runs_dir=runs_dir)
        if r1b_result.r1b_hit:
            write_r1b_preflight_receipt(
                receipt_dir / "r1b_whole_run_preflight_hit.json",
                r1b_result,
            )
            return WholeRunCachePreflightOutcome(
                entrypoint=entrypoint,
                r1b_result=r1b_result,
                generation_required=False,
            )

    return WholeRunCachePreflightOutcome(
        entrypoint=entrypoint,
        r1b_result=r1b_result,
        generation_required=True,
    )


def build_cache_hit_dispatch_result(
    preflight: WholeRunCachePreflightOutcome,
) -> dict[str, Any]:
    """Production-shaped short-circuit result (Exit review, no generation pipeline)."""
    base: dict[str, Any] = {
        "exit_status": "success",
        "execution_status": "completed",
        "outcome_authorized": True,
        "fault": "",
        "terminal_r5": True,
        "generation_skipped": True,
        "preflight_order": list(PREFLIGHT_ORDER),
        "cache_preflight": preflight.outcome,
        "c0_fact_vectors_consulted": False,
        "exit_bypassed": False,
        "l7_how_trace_emitted": False,
        "whole_run_cache_preflight": preflight.to_dict(),
    }
    if preflight.r1a_hit:
        base["artifact_dir"] = preflight.r1a_artifact_dir
        base["x3_disposition"] = "X3_ALLOW"
        base["run_id"] = "r1a_cache_hit"
        return base
    if preflight.r1b_hit and preflight.r1b_result:
        tp = preflight.r1b_result.terminal_packet or {}
        base["artifact_dir"] = str(
            resolve_preflight_receipt_dir(artifact_dir=None, runs_dir=None)
        )
        base["x3_disposition"] = str(tp.get("x3_disposition") or "X3_ALLOW")
        base["run_id"] = str(tp.get("run_id") or tp.get("source_run_id") or "")
        base["r1b_terminal_packet"] = tp
        base["r1b_child_chunk_inspection"] = preflight.r1b_result.child_chunk_inspection
        return base
    return base


def maybe_ingest_r1b_post_exit(
    *,
    raw_request: dict[str, Any],
    artifact_dir: Path,
    runs_dir: Path | str | None = None,
) -> str | None:
    """Post-run R1B ingest (W8); only after Exit artifacts exist."""
    if not _semantic_cache_r1b_enabled():
        return None
    store_root = resolve_r1b_store_root(artifact_dir=artifact_dir)
    return ingest_post_exit_after_run(
        artifact_dir=artifact_dir,
        raw_request=raw_request,
        runs_dir=store_root,
    )


def build_entrypoint_audit_matrix() -> list[dict[str, Any]]:
    """Static audit of canonical whole-run entrypoints (code-derived)."""
    return [
        {
            "entrypoint": ENTRYPOINT_DISPATCH_APPS_RG_RUN,
            "delegates_to": ENTRYPOINT_CANONICAL_DISPATCH,
            "uses_r1a": True,
            "uses_r1b": True,
            "order": list(PREFLIGHT_ORDER),
            "hit_behavior": "return build_cache_hit_dispatch_result without pipeline",
            "miss_behavior": "run_integrated_single_action_spine",
            "exit_handoff": "terminal_packet + exit_review_required on R1B hit",
            "section_scope": "out of scope — section lanes bypass preflight",
            "status": "wired_w9b",
        },
        {
            "entrypoint": ENTRYPOINT_CANONICAL_DISPATCH,
            "delegates_to": "run_integrated_single_action_spine",
            "uses_r1a": True,
            "uses_r1b": True,
            "order": list(PREFLIGHT_ORDER),
            "hit_behavior": "early return cache hit dict",
            "miss_behavior": "normal generation",
            "exit_handoff": "no bypass — R1B hit requires exit_review_required",
            "section_scope": "section=* branches skip whole-run preflight",
            "status": "wired_w9b",
        },
        {
            "entrypoint": ENTRYPOINT_ENVELOPE_DISPATCH,
            "delegates_to": ENTRYPOINT_DISPATCH_APPS_RG_RUN,
            "uses_r1a": True,
            "uses_r1b": True,
            "order": list(PREFLIGHT_ORDER),
            "hit_behavior": "via dispatch_apps_rg_run",
            "miss_behavior": "via dispatch_apps_rg_run",
            "exit_handoff": "inherited",
            "section_scope": "N/A",
            "status": "wired_w9b",
        },
        {
            "entrypoint": ENTRYPOINT_TEST_WHOLE_RUN_HARNESS,
            "delegates_to": "run_integrated_single_action_spine (tests/helpers only)",
            "uses_r1a": True,
            "uses_r1b": True,
            "order": list(PREFLIGHT_ORDER),
            "hit_behavior": "SystemExit(0)",
            "miss_behavior": "pipeline + post_exit ingest",
            "exit_handoff": "receipt r1b_whole_run_preflight_hit.json",
            "section_scope": "N/A",
            "status": "test_harness_only",
        },
        {
            "entrypoint": "apps_rg.runtime.internal.lane_batch",
            "uses_r1a": False,
            "uses_r1b": False,
            "order": ["NORMAL_GENERATION"],
            "hit_behavior": "N/A",
            "miss_behavior": "offline modular lanes",
            "exit_handoff": "N/A",
            "section_scope": "explicitly out of scope",
            "status": "out_of_scope",
        },
    ]


__all__ = [
    "ENTRYPOINT_CANONICAL_DISPATCH",
    "ENTRYPOINT_TEST_WHOLE_RUN_HARNESS",
    "ENTRYPOINT_DISPATCH_APPS_RG_RUN",
    "ENTRYPOINT_ENVELOPE_DISPATCH",
    "WholeRunCachePreflightOutcome",
    "build_cache_hit_dispatch_result",
    "build_entrypoint_audit_matrix",
    "maybe_ingest_r1b_post_exit",
    "resolve_r1b_store_root",
    "run_whole_run_cache_preflight",
]
