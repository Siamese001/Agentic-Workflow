"""Canonical entrypoint for apps_rg — pure transport shim.

Usage:
    python -m apps_rg --target-company <company> --target-role <role>

Delegates immediately to ``agentic_core.runtime.entrypoints
.integrated_r4_deterministic_pipeline_run`` with ``app_name="apps_rg"``.

apps_rg MUST NOT:
  - resolve L2 recipe
  - construct or pass l2_callable
  - run HOPs, narrative pass, DOCX export
  - call models or build prompts
  - commit cache or write L4
  - call Exit or emit X3

All domain execution is owned by agentic_core via registered L2 step
adapters in ``apps_rg.l2_recipe.steps``.

If the agentic_core runner is unavailable, apps_rg **fails closed** (exit 1).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from apps_rg.cache.r1a_adapter import check_r1a_cache, compute_r1a_key, stamp_r1a_cache
from apps_rg.utils.intent_builder import build_intent_from_request

try:
    from opentelemetry import trace as _otel_trace

    _tracer = _otel_trace.get_tracer("apps_rg.cache")
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False
    _tracer = None  # type: ignore[assignment]


def _span(name: str):
    """Context manager: OTEL span when available, else no-op."""
    if _OTEL_AVAILABLE and _tracer is not None:
        return _tracer.start_as_current_span(name)
    import contextlib
    return contextlib.nullcontext()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("apps_rg")


# ---------------------------------------------------------------------------
# Fail-closed import of the R4 deterministic pipeline runner
# ---------------------------------------------------------------------------
try:
    from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
        run_integrated_r4_deterministic_pipeline,
        R4IntegratedRunResult,
    )

    _RUNNER_AVAILABLE = True
except ImportError as _import_err:
    _RUNNER_AVAILABLE = False
    _RUNNER_IMPORT_ERROR = _import_err


# ---------------------------------------------------------------------------
# Helpers — transport-level only, no domain logic
# ---------------------------------------------------------------------------


def _get_current_policy_hash() -> str:
    return os.environ.get("APPS_RG_POLICY_HASH", "policy_v1")


def _get_current_blueprint_hash() -> str:
    return os.environ.get("APPS_RG_BLUEPRINT_HASH", "blueprint_v1")


def _hash_file_content(path: Path) -> str:
    """SHA-256 of file content, first 32 hex chars."""
    if not path.exists():
        return "none"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:32]


_DEFAULT_JD_PATH = "apps_rg/scripts/job_description.json"
_DEFAULT_BRIEF_PATH = "apps_rg/scripts/company_research.json"
_DEFAULT_CANDIDATE_PATH = "apps_rg/scripts/candidate_profile.yaml"


def _build_raw_request(args) -> dict[str, Any]:
    """Build the raw_request envelope from parsed CLI args.

    This dict is the contract surface between apps_rg and the R4 pipeline.
    It contains only transport-level data — no executable code.
    """
    jd_arg: str = getattr(args, "jd", "") or ""
    jd_path = Path(jd_arg or _DEFAULT_JD_PATH)

    brief_arg: str = getattr(args, "manual_brief", "") or ""
    brief_path = Path(brief_arg if brief_arg and Path(brief_arg).exists() else _DEFAULT_BRIEF_PATH)

    candidate_path = (
        Path(args.candidate) if getattr(args, "candidate", None) else Path(_DEFAULT_CANDIDATE_PATH)
    )

    jd_payload: dict[str, Any] = {}
    if jd_path.exists():
        try:
            jd_payload = json.loads(jd_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    raw = {
        "transport": "api",
        "method": "POST",
        "jd_path_resolved": str(jd_path),
        "content_type": "application/json",
        "source_channel": "apps_rg_cli",
        "declared_schema": "apps_rg_jd_v1",
        "body_text": json.dumps(jd_payload) if jd_payload else "{}",
        "tenant_id": getattr(args, "tenant_id", "default"),
        "user_id": "u-apps_rg",
        "target_company": args.target_company or "",
        "target_role": args.target_role or "",
        "jd_payload": jd_payload,  # DS-R7: must be dict; consumed by L1_cognition
        "jd_hash": _hash_file_content(jd_path),
        "brief_hash": _hash_file_content(brief_path),
        "resume_hash": _hash_file_content(candidate_path),
        "policy_hash": _get_current_policy_hash(),
        "blueprint_hash": _get_current_blueprint_hash(),
        "manual_brief": str(brief_path),
        "research_via": getattr(args, "research_via", None),
        "auto_research_internal": getattr(args, "auto_research_internal", False),
        "auto_research_tavily": getattr(args, "auto_research_tavily", False),
    }
    assert isinstance(raw["jd_payload"], dict), (
        f"apps_rg: jd_payload must be a dict, got {type(raw['jd_payload']).__name__}"
    )
    return raw


# ---------------------------------------------------------------------------
# Core pipeline logic — extracted for testability
# ---------------------------------------------------------------------------


def _run_with_args(
    args: Any,
    runs_dir: Path | None = None,
    artifact_dir_override: Path | None = None,
) -> None:
    """Execute the full L0-wired pipeline given parsed CLI args.

    Extracted from ``main()`` so tests can inject args directly without
    going through argparse or subprocess.  Calls ``sys.exit`` on all paths.

    Parameters
    ----------
    args:
        Namespace-like object with target_company, target_role, candidate,
        jd, manual_brief, target_level, tenant_id, etc.
    runs_dir:
        Override the directory scanned for R1A cache entries.
        Defaults to ``artifacts/apps_rg/runs``.
    artifact_dir_override:
        Override the per-run artifact directory (used by tests to pre-seed
        ``generated_resume.json`` for R1B store testing).
    """
    raw_request = _build_raw_request(args)
    _runs_dir = runs_dir if runs_dir is not None else Path("artifacts/apps_rg/runs")
    artifact_dir = (
        artifact_dir_override
        if artifact_dir_override is not None
        else _runs_dir / f"r4_{raw_request['resume_hash'][:8]}"
    )

    # ── Single source of truth: resolve all paths from raw_request (not args) ──
    # _build_raw_request may have prompted interactively; args.* is NOT updated.
    jd_path = Path(raw_request.get("jd_path_resolved") or getattr(args, "jd", "") or "apps_rg/scripts/job_description.json")
    brief_path = Path(raw_request["manual_brief"])
    candidate_path = (
        Path(args.candidate) if getattr(args, "candidate", None)
        else Path("apps_rg/scripts/candidate_profile.yaml")
    )

    # ── L0 prerequisite gate: briefing validation before R4 ──
    try:
        from agentic_core.L0_routing.gates.apps_rg_prerequisite_gate import check_apps_rg_prerequisites
        _prereq = check_apps_rg_prerequisites(
            target_company=raw_request["target_company"],
            target_role=raw_request["target_role"],
            policy_hash=raw_request["policy_hash"],
            blueprint_hash=raw_request["blueprint_hash"],
            trace_id=raw_request.get("tenant_id", "default"),
            briefing_path=brief_path,
        )
        if _prereq is not None:
            from agentic_core.L0_routing.types.routing_artifact_types import L0Route
            _sel = _prereq.get("selected_route")
            if _sel == L0Route.R5:
                _log.error(
                    "[apps_rg] L0 prerequisite gate: briefing incompatible — %s. "
                    "Check briefing file at %s.",
                    _prereq.get("reason_codes"),
                    brief_path,
                )
                sys.exit(1)
            if _sel == L0Route.R3R4_MANAGED:
                _log.warning(
                    "[apps_rg] L0 prerequisite gate: briefing MISSING or STALE for '%s'. "
                    "Run apps_research first to generate a fresh briefing, "
                    "then re-run apps_rg with --manual-brief <path>.",
                    raw_request["target_company"],
                )
                sys.exit(1)
    except ImportError:
        _log.debug("[apps_rg] L0 prerequisite gate unavailable (fail-open)")
    except Exception as _gate_err:
        _log.warning("[apps_rg] L0 prerequisite gate failed (fail-soft): %s", _gate_err)

    # ── W1 / GAP-1: R1A exact-cache pre-flight ──
    r1a_key = compute_r1a_key(
        source_resume_hash=raw_request["resume_hash"],
        target_company=raw_request["target_company"],
        target_role=raw_request["target_role"],
        jd_hash=raw_request["jd_hash"],
        briefing_hash=raw_request["brief_hash"],
        policy_hash=raw_request["policy_hash"],
        blueprint_hash=raw_request["blueprint_hash"],
    )
    with _span("apps_rg.cache.r1a.check") as r1a_span:
        cached_run_dir = check_r1a_cache(
            r1a_key,
            runs_dir=_runs_dir,
            policy_hash=raw_request["policy_hash"],
            blueprint_hash=raw_request["blueprint_hash"],
        )
        if _OTEL_AVAILABLE and r1a_span is not None:
            r1a_span.set_attribute("cache.layer", "r1a")
            r1a_span.set_attribute("cache.result", "hit" if cached_run_dir else "miss")
            r1a_span.set_attribute("cache.key_prefix", r1a_key[:16])
    if cached_run_dir is not None:
        _log.info("[apps_rg] R1A exact cache hit — returning cached run at %s", cached_run_dir)
        sys.exit(0)

    # ── W2 / GAP-2: R1B semantic-cache pre-flight (gated by env flag) ──
    if os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0") == "1":
        try:
            from apps_rg.cache.r1b_adapter import check_r1b_for_apps_rg

            with _span("apps_rg.cache.r1b.check") as r1b_span:
                r1b_hit = check_r1b_for_apps_rg(
                    candidate_profile_path=str(candidate_path),
                    target_company=args.target_company,
                    target_role=args.target_role,
                    policy_hash=raw_request["policy_hash"],
                    blueprint_hash=raw_request["blueprint_hash"],
                    jd_path=jd_path,
                    briefing_path=brief_path,
                    tenant_id=raw_request.get("tenant_id", "default"),
                )
                if _OTEL_AVAILABLE and r1b_span is not None:
                    r1b_span.set_attribute("cache.layer", "r1b")
                    r1b_span.set_attribute("cache.result", "hit" if r1b_hit else "miss")
                    if r1b_hit is not None:
                        _sim = r1b_hit.get("_cache_similarity_score")
                        if _sim is not None:
                            r1b_span.set_attribute("cache.similarity_score", _sim)
            if r1b_hit is not None:
                _log.info("[apps_rg] R1B semantic cache hit — returning cached result")
                sys.exit(0)
        except Exception as _r1b_err:  # guardian: allow-broad-exception -- R1B recall is fail-soft; a miss is always safe
            _log.warning("[apps_rg] R1B recall failed (fail-soft): %s", _r1b_err)

    # ── Delegate to agentic_core R4 pipeline (core resolves L2 recipe) ──
    result: R4IntegratedRunResult = run_integrated_r4_deterministic_pipeline(
        app_name="apps_rg",
        raw_request=raw_request,
        artifact_dir=artifact_dir,
        policy_hash=raw_request["policy_hash"],
        blueprint_hash=raw_request["blueprint_hash"],
    )

    _log.info(
        "[apps_rg] R4 pipeline complete: run_id=%s x3=%s terminal_r5=%s fault=%s",
        result.run_id,
        result.x3_disposition,
        result.terminal_r5,
        result.fault or "(none)",
    )

    # ── W4 / GAP-4: R1A post-run stamp (only on clean execution) ──
    if not result.fault and not result.terminal_r5:
        try:
            with _span("apps_rg.cache.r1a.stamp") as r1a_stamp_span:
                stamp_r1a_cache(
                    r1a_key,
                    str(artifact_dir),
                    policy_hash=raw_request["policy_hash"],
                    blueprint_hash=raw_request["blueprint_hash"],
                )
                if _OTEL_AVAILABLE and r1a_stamp_span is not None:
                    r1a_stamp_span.set_attribute("cache.layer", "r1a")
                    r1a_stamp_span.set_attribute("cache.operation", "stamp")
            _log.debug("[apps_rg] R1A cache stamped for key=%s", r1a_key[:16])
        except Exception as _stamp_err:  # guardian: allow-broad-exception -- cache stamp is fail-soft; run already succeeded
            _log.warning("[apps_rg] R1A stamp failed (fail-soft): %s", _stamp_err)

    # ── W4 / GAP-5: R1B post-run store (only on clean execution, gated by env flag) ──
    if not result.fault and not result.terminal_r5 and os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0") == "1":
        try:
            from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter

            intent = build_intent_from_request(
                candidate_profile_path=candidate_path,
                target_company=args.target_company,
                target_role=args.target_role,
                target_level=getattr(args, "target_level", None),
                policy_hash=raw_request["policy_hash"],
                blueprint_hash=raw_request["blueprint_hash"],
                jd_path=jd_path,
                briefing_path=brief_path,
                tenant_id=raw_request.get("tenant_id", "default"),
                request_id=result.run_id,
            )
            generated_resume_path = artifact_dir / "generated_resume.json"
            output_chunks: list[dict] = []
            if generated_resume_path.exists():
                try:
                    resume_data = json.loads(generated_resume_path.read_text(encoding="utf-8"))
                    output_chunks = resume_data if isinstance(resume_data, list) else [resume_data]
                except (json.JSONDecodeError, OSError):
                    pass
            if output_chunks:
                adapter = AppsRgR1BCacheAdapter(
                    tenant_id=raw_request.get("tenant_id", "default")
                )
                with _span("apps_rg.cache.r1b.store") as r1b_store_span:
                    adapter.store_intent_and_output(
                        intent=intent,
                        output_chunks=output_chunks,
                        run_context={
                            "run_id": result.run_id,
                            "exit_disposition": result.x3_disposition,
                            "uwg_commit_receipt": result.run_id,
                            "policy_hash": raw_request["policy_hash"],
                            "blueprint_hash": raw_request["blueprint_hash"],
                        },
                    )
                    if _OTEL_AVAILABLE and r1b_store_span is not None:
                        r1b_store_span.set_attribute("cache.layer", "r1b")
                        r1b_store_span.set_attribute("cache.operation", "store")
                        r1b_store_span.set_attribute("cache.chunks_stored", len(output_chunks))
                _log.debug("[apps_rg] R1B semantic cache stored %d chunks", len(output_chunks))
        except Exception as _store_err:  # guardian: allow-broad-exception -- R1B store is fail-soft; run already succeeded
            _log.warning("[apps_rg] R1B store failed (fail-soft): %s", _store_err)

    if result.fault:
        _log.error("[apps_rg] Pipeline fault: %s", result.fault)
        sys.exit(1)

    sys.exit(0)


# ---------------------------------------------------------------------------
# Main entrypoint — pure shim
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse transport args → delegate to agentic_core R4 pipeline."""

    # ── Fail-closed guard ──
    if not _RUNNER_AVAILABLE:
        print(
            f"FATAL: agentic_core runner unavailable — apps_rg fails closed.\n"
            f"  ImportError: {_RUNNER_IMPORT_ERROR}",
            file=sys.stderr,
        )
        sys.exit(1)

    import argparse

    parser = argparse.ArgumentParser(prog="apps_rg", add_help=True)
    parser.add_argument("--target-company", default=None, help="Target company")
    parser.add_argument("--target-role", default=None, help="Target role title")
    parser.add_argument("--research-via", default=None, choices=["apps_research"])
    parser.add_argument("--auto-research-internal", action="store_true")
    parser.add_argument("--auto-research-tavily", action="store_true")
    parser.add_argument("--manual-brief", default="apps_rg/scripts/company_research.json")
    parser.add_argument("--candidate", default=None, help="Candidate profile path")
    parser.add_argument("--target-level", default=None)
    parser.add_argument("--jd", default=None, help="Job description JSON path")
    args, _unknown = parser.parse_known_args()

    # ── Resolve company/role from script defaults when not supplied on CLI ──
    if not args.target_company:
        try:
            _brief = json.loads(Path(_DEFAULT_BRIEF_PATH).read_text(encoding="utf-8"))
            args.target_company = _brief.get("company", "") or ""
        except (OSError, json.JSONDecodeError):
            pass
    if not args.target_role:
        try:
            _jd = json.loads(Path(_DEFAULT_JD_PATH).read_text(encoding="utf-8"))
            args.target_role = (
                _jd.get("role_title") or _jd.get("title") or _jd.get("job_title") or ""
            )
        except (OSError, json.JSONDecodeError):
            pass

    if not args.target_company:
        parser.error("--target-company is required (and could not be read from apps_rg/scripts/company_research.json)")
    if not args.target_role:
        parser.error("--target-role is required (and could not be read from apps_rg/scripts/job_description.json)")

    _run_with_args(args)


if __name__ == "__main__":
    main()
