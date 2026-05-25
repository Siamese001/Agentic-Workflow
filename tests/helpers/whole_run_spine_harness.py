"""Test-only whole-run spine harness — R1A/R1B preflight + single-action spine.

Replaces the retired ``apps_rg.__main__.run_whole_run_spine_harness`` shim. Production entry remains
``python -m apps_rg`` → ``dispatch_apps_rg_run``.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from apps_rg.cache.r1a_adapter import compute_r1a_key, stamp_r1a_cache
from apps_rg.cache.whole_run_entrypoint_preflight import (
    ENTRYPOINT_TEST_WHOLE_RUN_HARNESS,
    maybe_ingest_r1b_post_exit,
    run_whole_run_cache_preflight,
)
from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4
from apps_rg.runtime.run_bundle_index import emit_integrated_run_bundle_index
from apps_rg.runtime.runtime_proof_layout import find_repo_root


def run_whole_run_spine_harness(
    args: Any,
    *,
    runs_dir: Path,
    artifact_dir_override: Path | None = None,
) -> None:
    """Exercise cache preflight + spine for unit tests (not a CLI entrypoint)."""
    from apps_rg.enforcement.cli_prerequisite_gate import check_apps_rg_cli_prerequisites

    check_apps_rg_cli_prerequisites(
        target_company=str(getattr(args, "target_company", "") or ""),
        target_role=str(getattr(args, "target_role", "") or ""),
        policy_hash=os.environ.get("APPS_RG_POLICY_HASH", ""),
        blueprint_hash=os.environ.get("APPS_RG_BLUEPRINT_HASH", ""),
        trace_id=str(getattr(args, "tenant_id", "") or "default_cli"),
        manual_brief_path=str(getattr(args, "manual_brief", "") or ""),
    )

    raw_request = build_raw_request_for_r4(
        target_company=str(getattr(args, "target_company", "") or ""),
        target_role=str(getattr(args, "target_role", "") or ""),
        target_level=str(getattr(args, "target_level", "") or ""),
        jd=str(getattr(args, "jd", "") or ""),
        manual_brief=str(getattr(args, "manual_brief", "") or ""),
        resume_path=str(getattr(args, "resume", "") or ""),
        generation_mode=str(getattr(args, "generation_mode", None) or "strategic_tailor"),
    )

    env_policy = os.environ.get("APPS_RG_POLICY_HASH")
    env_bp = os.environ.get("APPS_RG_BLUEPRINT_HASH")

    preflight = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_TEST_WHOLE_RUN_HARNESS,
        raw_request=raw_request,
        target_company=str(getattr(args, "target_company", "") or ""),
        target_role=str(getattr(args, "target_role", "") or ""),
        artifact_dir=artifact_dir_override,
        runs_dir=runs_dir,
        policy_hash=env_policy,
        blueprint_hash=env_bp,
    )
    from apps_rg.cache.cache_preflight_evidence import (
        build_cache_preflight_evidence,
        write_cache_miss_receipt,
        write_whole_run_cache_preflight_artifact,
    )

    evidence = build_cache_preflight_evidence(preflight, artifact_dir=artifact_dir_override)
    if artifact_dir_override is not None:
        write_whole_run_cache_preflight_artifact(Path(artifact_dir_override), preflight, evidence)

    if not preflight.generation_required:
        raise SystemExit(0)

    artifact_root = (
        artifact_dir_override
        if artifact_dir_override is not None
        else (runs_dir / "_r4_artifact_scratch")
    )
    if artifact_dir_override is None:
        artifact_root.mkdir(parents=True, exist_ok=True)

    if artifact_dir_override is not None:
        write_cache_miss_receipt(Path(artifact_root), preflight, evidence)

    from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
        run_integrated_single_action_spine,
    )

    outcome = run_integrated_single_action_spine(
        raw_request=raw_request,
        app_name="apps_rg",
        artifact_dir=artifact_root,
        route_family="R4_SINGLE_ACTION",
        cache_preflight_evidence=evidence,
    )

    rid = str(getattr(outcome, "run_id", "") or "").strip()
    try:
        emit_integrated_run_bundle_index(
            find_repo_root(),
            Path(outcome.artifact_dir),
            run_id=rid or None,
            correlation_id=rid or None,
        )
    except ValueError:
        from apps_rg.runtime.product_output_policy import is_apps_rg_test_harness

        if not is_apps_rg_test_harness():
            raise

    fault_txt = str(getattr(outcome, "fault", "") or "").strip()
    if fault_txt:
        raise SystemExit(1)
    if bool(getattr(outcome, "terminal_r5", False)):
        raise SystemExit(0)

    resume_hash = str(raw_request.get("resume_hash") or "")
    r1a_key = compute_r1a_key(
        source_resume_hash=resume_hash,
        target_company=str(getattr(args, "target_company", "") or ""),
        target_role=str(getattr(args, "target_role", "") or ""),
    )
    stamp_r1a_cache(
        r1a_key,
        Path(outcome.artifact_dir),
        policy_hash=env_policy,
        blueprint_hash=env_bp,
    )

    try:
        maybe_ingest_r1b_post_exit(
            raw_request=dict(raw_request),
            artifact_dir=Path(outcome.artifact_dir),
            runs_dir=runs_dir,
        )
    except (OSError, TypeError, ValueError):
        pass

    raise SystemExit(0)


__all__ = ["run_whole_run_spine_harness"]
