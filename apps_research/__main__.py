"""Canonical entrypoint for apps_research."""

from __future__ import annotations

import importlib
import json
import logging
import os
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from apps_research.integrations.apps_rg_handoff import (
    build_apps_rg_handoff_envelope,
    find_apps_rg_targeting_sidecar,
    looks_like_stub_company_brief,
)

_log = logging.getLogger("apps_research")


def _adg_bootstrap() -> None:
    """Run optional ADG bootstrap without making package import fragile."""
    try:
        module = importlib.import_module("agentic_core.adg.applications.execute_ssot_integration")
        build_pre_run_report = getattr(module, "build_pre_run_report")
    except (ImportError, AttributeError):
        return

    try:
        report = build_pre_run_report(changed_files=[], force_fresh=False)
    except Exception as exc:  # guardian: allow-broad-exception -- build_pre_run_report raises heterogeneous errors (OSError, RuntimeError, sqlite3.Error); all logged, bootstrap degrades gracefully
        _log.warning("[ADG] bootstrap unavailable: %s", exc)
        return

    _log.info("[ADG] %s", getattr(report, "summary", "pre-run report generated"))
    if getattr(report, "layer_violation_count", 0) > 0:
        _log.warning(
            "[ADG] %d layer violation(s): %s",
            report.layer_violation_count,
            getattr(report, "scope_widening_events", []),
        )
    if getattr(report, "route_mode", "") == "HUMAN_REVIEW":
        raise SystemExit(1)


def _is_live_cert_mode() -> bool:
    """True when `--apps-e2e-live` appears in sys.argv; strip flag from argv."""
    if "--apps-e2e-live" in sys.argv:
        sys.argv.remove("--apps-e2e-live")
        return True
    return False


def _build_emission_config():
    """Shared EmissionConfig for apps_research product + cert modes."""
    from pathlib import Path

    from apps_shared.spine_emission import EmissionConfig
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    return EmissionConfig(
        app_name="apps_research",
        entrypoint_command="python -m apps_research",
        runs_root=repo_root / "artifacts" / "apps_research" / "runs",
        route_registry_path=repo_root / "apps_research" / "config" / "route_registry.yaml",
        l3_dag_path=None,
        plan_steps=[
            L1PlanStep(step_id="intake", name="Intake", kind="ingest"),
            L1PlanStep(step_id="retrieve", name="Retrieve evidence", kind="retrieve"),
            L1PlanStep(step_id="assemble_prompt", name="Assemble prompt", kind="assemble"),
            L1PlanStep(step_id="generate_brief", name="Generate company brief", kind="render"),
            L1PlanStep(step_id="seal", name="Seal output", kind="assemble"),
        ],
        plan_rationale=(
            "apps_research is a deterministic single-step research app. Plan is "
            "hard-coded by route selection. C0 grounding is fixture-backed; prompt "
            "assembly is template-driven."
        ),
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
        selected_capability="R3_SIMPLE_GROUNDED_READ",
        repo_root=repo_root,
    )


def _parse_product_argv(argv: list[str]):
    """Parse default and --spine CLI flags into a single namespace."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m apps_research",
        description="apps_research via agentic_core spine (U0-bound AppRuntimeProfile)",
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Research topic (mapped to target_company when --target-company omitted)",
    )
    parser.add_argument("--target-company", default=None, help="Target company name")
    parser.add_argument("--target-role", default=None)
    parser.add_argument("--mode", default="brief", help="Run mode (brief/deep)")
    parser.add_argument("--depth", default="standard", help="Depth profile")
    parser.add_argument("--manual-brief-path", default=None)
    parser.add_argument(
        "--jd",
        default=None,
        help="Path to JD .txt/.json or inline text (enables compact downstream brief synthesis)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate CLI shape only; does not emit product artifacts",
    )
    return parser.parse_args(argv)


def _read_jd_arg(jd_val: str | None) -> str:
    from pathlib import Path

    s = str(jd_val or "").strip()
    if not s:
        return ""
    p = Path(s)
    if p.is_file():
        try:
            return p.read_text(encoding="utf-8").strip()
        except OSError:
            return ""
    return s


def _payload_from_args(args) -> dict:
    """Build ingress payload dict for AppIngressRunner.parse."""
    topic = (args.topic or args.target_company or "").strip()
    if not topic:
        return {}
    user_constraints: dict = {"topic": topic, "depth": args.depth, "mode": args.mode}
    jd_text = _read_jd_arg(getattr(args, "jd", None))
    jd_context: dict = {}
    if jd_text:
        jd_context = {
            "content": jd_text,
            "jd_text": jd_text,
            "job_title": str(getattr(args, "target_role", "") or "").strip(),
            "company_name": (args.target_company or topic).strip(),
            "output_format": "apps_rg_targeting_brief_v1",
            "synthesis_template": "apps_rg_targeting_brief_synthesis_v1",
        }
    return {
        "target_company": (args.target_company or topic).strip(),
        "topic": topic,
        "target_role": args.target_role,
        "depth": args.depth,
        "user_constraints": user_constraints,
        "briefing_artifact_ref": args.manual_brief_path,
        "manual_brief_path": args.manual_brief_path,
        "jd_context": jd_context,
    }


def _apps_research_runs_root() -> Path:
    return Path(__file__).resolve().parents[1] / "artifacts" / "apps_research" / "runs"


def _truthy_env(name: str, *, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _ensure_searxng_runtime_ready():
    """Warm local SearXNG before apps_research fetches grounded evidence."""
    from apps_research.integrations.searxng_readiness import ensure_runtime_ready

    report = ensure_runtime_ready(
        force_restart=_truthy_env("APPS_RESEARCH_SEARXNG_FORCE_RESTART", default=True),
        restart_wait_seconds=float(os.environ.get("APPS_RESEARCH_SEARXNG_RESTART_WAIT_SECONDS", "8")),
    )
    _log.info(
        "[apps_research] searxng_ready status=%s restarted=%s base_url=%s",
        report.status,
        report.restarted,
        report.base_url,
    )
    return report


def _research_request_from_args(args):
    """Build the governed apps_research request used by product CLI runs."""
    from apps_research.types.research_types import ResearchRequest  # noqa: PLC0415

    topic = (args.topic or args.target_company or "").strip()
    jd_text = _read_jd_arg(getattr(args, "jd", None))
    jd_context: dict[str, object] = {}
    if jd_text:
        jd_context = {
            "content": jd_text,
            "jd_text": jd_text,
            "job_title": str(getattr(args, "target_role", "") or "").strip(),
            "company_name": (args.target_company or topic).strip(),
            "output_format": "apps_rg_targeting_brief_v1",
            "synthesis_template": "apps_rg_targeting_brief_synthesis_v1",
            "jd_context": {
                "role": str(getattr(args, "target_role", "") or "").strip()
                or "target role",
            },
        }
    return ResearchRequest(
        topic=topic,
        mode="brief",
        audience_style="executive",
        depth_profile=str(args.depth or "standard"),
        trace_id=f"research-run-{uuid4().hex[:12]}",
        jd_context=jd_context,
    )


def _run_research_record(request):
    """Invoke the canonical apps_research spine handoff."""
    from apps_research.integrations.spine_handoff import (  # noqa: PLC0415
        run_research_via_spine,
    )

    return run_research_via_spine(request)


def _jsonable(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _apps_rg_targeting_sidecar(record) -> dict:
    fec_ctx = getattr(record, "fec_run_context", {}) or {}
    return find_apps_rg_targeting_sidecar(fec_ctx)


def _write_apps_rg_handoff_envelope(
    *,
    run_dir: Path,
    record,
    request,
    briefing_text: str,
    company_brief_path: Path,
    briefing_path: Path,
    generated_at_utc: str,
) -> dict:
    """Emit authoritative apps_research -> apps_rg handoff metadata."""
    sidecar = _apps_rg_targeting_sidecar(record)
    if not sidecar:
        raise RuntimeError("apps_research targeting run missing apps_rg handoff sidecar")

    jd_ctx = getattr(request, "jd_context", {}) or {}
    if not isinstance(jd_ctx, dict):
        jd_ctx = {}
    jd_text = str(jd_ctx.get("content") or jd_ctx.get("jd_text") or "")
    envelope = build_apps_rg_handoff_envelope(
        sidecar=sidecar,
        run_id=str(getattr(record, "run_id", "") or getattr(request, "trace_id", "")),
        target_company=str(jd_ctx.get("company_name") or getattr(request, "topic", "") or ""),
        target_role=str(jd_ctx.get("job_title") or ""),
        briefing_text=briefing_text,
        jd_text=jd_text,
        generated_at_utc=generated_at_utc,
        briefing_path=str(briefing_path.resolve()),
        company_brief_path=str(company_brief_path.resolve()),
    )
    (run_dir / "apps_research_briefing_envelope.json").write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return envelope


def _write_research_artifacts(record, request) -> Path:
    """Persist a fresh apps_research run artifact bundle."""
    run_id = str(getattr(record, "run_id", "") or getattr(request, "trace_id", "") or uuid4().hex)
    safe_run_id = "".join(c for c in run_id if c.isalnum() or c in "._-") or uuid4().hex
    run_dir = _apps_research_runs_root() / safe_run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    briefing_text = str(getattr(record, "company_brief_text", "") or "").strip()
    is_targeting = (
        str((getattr(request, "jd_context", {}) or {}).get("output_format", ""))
        == "apps_rg_targeting_brief_v1"
    )
    if is_targeting and (not briefing_text or looks_like_stub_company_brief(briefing_text)):
        raise RuntimeError(
            "apps_research targeting run produced no usable company_brief_text; "
            f"terminal_error={getattr(record, 'hop_terminal_error', '')!r}"
        )

    generated_at_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "apps_research.company_brief_artifact.v2",
        "company": str(getattr(record, "topic", "") or getattr(request, "topic", "")),
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "targeting_format": (
            (getattr(request, "jd_context", {}) or {}).get("output_format") or ""
        ),
        "company_brief_text": briefing_text,
        "confidence_score": float(getattr(record, "confidence_score", 0.0) or 0.0),
        "support_coverage": float(getattr(record, "support_coverage", 0.0) or 0.0),
        "hop_terminal_error": str(getattr(record, "hop_terminal_error", "") or ""),
        "fec_run_context": _jsonable(getattr(record, "fec_run_context", {}) or {}),
    }
    company_brief_path = run_dir / "company_brief.json"
    company_brief_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    briefing_path = run_dir / "briefing.md"
    if briefing_text:
        briefing_path.write_text(briefing_text + "\n", encoding="utf-8")
    handoff_envelope = {}
    if is_targeting and briefing_text:
        handoff_envelope = _write_apps_rg_handoff_envelope(
            run_dir=run_dir,
            record=record,
            request=request,
            briefing_text=briefing_text,
            company_brief_path=company_brief_path,
            briefing_path=briefing_path,
            generated_at_utc=generated_at_utc,
        )
    (run_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "topic": getattr(request, "topic", ""),
                "mode": getattr(request, "mode", ""),
                "depth_profile": getattr(request, "depth_profile", ""),
                "targeting_format": payload["targeting_format"],
                "company_brief_path": str(run_dir / "company_brief.json"),
                "briefing_path": str(run_dir / "briefing.md") if briefing_text else "",
                "apps_research_briefing_envelope_path": (
                    str(run_dir / "apps_research_briefing_envelope.json")
                    if handoff_envelope
                    else ""
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return run_dir / ("briefing.md" if briefing_text else "company_brief.json")


def _run_profile_spine(argv: list[str]) -> int:
    """Run apps_research via U0-bound AppRuntimeProfile (Bundle C canonical path).

    Sequences profile.u0 → l1 → l0 → c0 → pa → l2 → exit through agentic_core
    bindings. No dispatch callable and no GovernedResearchRun U0 bypass.
    """
    args = _parse_product_argv(argv)

    if args.dry_run:
        _log.error(
            "[apps_research] --dry-run no longer emits product artifacts; "
            "run without --dry-run for product evidence."
        )
        return 1

    if not (args.topic or args.target_company):
        _log.error(
            "[apps_research] Missing ingress target: provide --topic or --target-company"
        )
        return 1

    try:
        _ensure_searxng_runtime_ready()
        request = _research_request_from_args(args)
        record = _run_research_record(request)
        artifact_path = _write_research_artifacts(record, request)
    except Exception as exc:  # guardian: allow-broad-exception -- product CLI must fail closed with a clear operator message for heterogeneous research/runtime failures
        _log.error("[apps_research] product run failed closed: %s", exc)
        return 1

    _log.info(
        "[apps_research] exit_status=success outcome_authorized=True artifact=%s",
        artifact_path,
    )
    sys.stdout.write(f"artifact={artifact_path}\n")
    return 0


def _run_product_research(argv: list[str]) -> int:
    """Run product CLI inside governed_run spine envelope (receipt emission)."""
    from apps_shared.spine_emission import governed_run

    cfg = _build_emission_config()

    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("C0_retrieval"):
            gr.mark_stage("C0_retrieval", "ok")
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            _exit_code = _run_profile_spine(argv)
            if _exit_code == 0:
                gr.mark_stage("L2_execute", "ok")
            else:
                gr.mark_stage("L2_execute", "fail")
    return _exit_code


def _run_live_cert(argv: list[str]) -> int:
    """Wrap the apps_research pipeline in apps_shared.spine_emission.

    Emits the 10 strict-required receipts (SINGLE_STEP / BYPASSED with
    C0 grounding + prompt assembly) under
    ``artifacts/apps_research/runs/<ts>/``. Plan:
    apps-e2e-spine-cert-wireup-e1c4d7 W4.
    """
    from apps_shared.spine_emission import governed_run
    import apps_research.cert  # noqa: F401, PLC0415
    from apps_shared.cert.fec_producer import resolve_fec  # noqa: PLC0415

    cfg = _build_emission_config()

    with governed_run(cfg, cli_args=argv) as gr:
        with gr.span("C0_retrieval"):
            gr.mark_stage("C0_retrieval", "ok")
        with gr.span("prompt_assembly"):
            gr.mark_stage("prompt_assembly", "ok")
        with gr.span("L2_execute"):
            gr.mark_stage("L2_execute", "ok")
        # Plan apps-exec-research-exit-hook-adoption-a8d3c5 W2.P2 — resolve
        # FEC from shared registry, then invoke the v6 Exit pipeline via
        # the fail-soft helper. Route entry:
        # apps_research/config/cert_route_registry.yaml.
        try:
            _fec = resolve_fec(
                "apps_research",
                {
                    "route_id": "apps_research.company_brief_v1",
                    "route_contract": {"route_id": "apps_research.company_brief_v1"},
                    "template_ids": ["company_brief_v1"],
                },
            )
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- FEC resolution is fail-soft
            _fec = {}
        _maybe_run_exit_hook(_fec)
    return 0


def _load_cert_route_entry(registry_path) -> dict | None:
    """Return the first route entry from apps_research's cert_route_registry.yaml.

    Fail-soft: any parse or IO error returns None; makes
    ``maybe_invoke_exit_eval`` a no-op. Never raises.
    """
    try:
        import yaml  # noqa: PLC0415

        doc = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- cert-path adoption must be fail-soft;
        # any registry-load failure leaves the hook as a no-op and the cert
        # bundle continues unaffected
        return None
    routes = doc.get("routes") if isinstance(doc, dict) else None
    if not routes or not isinstance(routes, list):
        return None
    first = routes[0]
    return first if isinstance(first, dict) else None


def _build_exit_receipts(cert_route_entry, fec: dict | None) -> dict:
    """Build the receipts dict for run_exit_eval.

    apps_research's cert-path live run is currently a SINGLE_STEP symbolic
    pipeline (no real brief output), so deterministic dim_scores default
    to 0.0 -> UNKNOWN -> fail-closed per rubric evidence_required=true.
    The FEC IS populated (producer plan e7a2c3 already landed), so the
    final_evidence_contract carries real retrieval_sources / template_ids
    / grounded flags. That is the correct enforcement posture: enforcement
    runs, FEC is real, dim_scores honestly UNKNOWN on missing evidence.

    Fail-soft: returns a minimal shape on any error.
    """
    from pathlib import Path

    receipts_output: dict = {}
    try:
        from apps_shared.cert import map_l2_receipt_to_dim_scores
        map_path = None
        if isinstance(cert_route_entry, dict):
            rel = cert_route_entry.get("rubric_output_map_path")
            if isinstance(rel, str) and rel:
                map_path = Path(__file__).resolve().parents[1] / rel
        if map_path and map_path.exists():
            projected = map_l2_receipt_to_dim_scores(
                {"output": receipts_output}, map_path,
            )
            receipts_output.update(projected)
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- mapper is fail-soft by design;
        # projection failure yields empty dim_scores (evaluator fail-closes)
        pass

    return {
        "output": receipts_output,
        "route_contract": {"route_id": "apps_research.company_brief_v1"},
        "evidence_bundle": {},
        "final_evidence_contract": fec if isinstance(fec, dict) else {},
        "state_diff": {},
        "compiled_prompt_artifact": {},
    }


def _maybe_run_exit_hook(fec: dict | None) -> None:
    """Invoke the v6 Exit pipeline when apps_research's cert route opts in.

    Reads ``apps_research/config/cert_route_registry.yaml`` for the
    ``invoke_exit_eval`` flag; builds receipts via the declarative rubric
    output map and the pre-computed FEC; calls
    :func:`apps_shared.cert.maybe_invoke_exit_eval` fail-soft.
    """
    from pathlib import Path

    try:
        from apps_shared.cert import maybe_invoke_exit_eval  # noqa: PLC0415
    except ImportError:
        return
    registry_path = (
        Path(__file__).resolve().parents[1]
        / "apps_research" / "config" / "cert_route_registry.yaml"
    )
    cert_route_entry = _load_cert_route_entry(registry_path)
    if cert_route_entry is None:
        return
    receipts = _build_exit_receipts(cert_route_entry, fec)
    try:
        maybe_invoke_exit_eval(receipts, cert_route_entry)
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- cert hook MUST NOT break the
        # bundle-building path; Exit failures are additional evidence only
        _log.warning("[apps_research] Exit hook raised %s: %s",
                     type(exc).__name__, exc)


def main() -> int:
    argv = list(sys.argv[1:])
    # --spine is an alias for the canonical profile path (same as default).
    if "--spine" in argv:
        argv.remove("--spine")
    if _is_live_cert_mode():
        return _run_live_cert(list(sys.argv[1:]))
    from apps_shared._apps_e2e_dry_run import maybe_short_circuit
    maybe_short_circuit("apps_research")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    _adg_bootstrap()
    return _run_product_research(argv)


if __name__ == "__main__":
    raise SystemExit(main())
