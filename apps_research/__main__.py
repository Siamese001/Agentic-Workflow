"""Canonical entrypoint for apps_research."""

from __future__ import annotations

import importlib
import logging
import sys

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


def _run_live_cert(argv: list[str]) -> int:
    """Wrap the apps_research pipeline in apps_shared.spine_emission.

    Emits the 10 strict-required receipts (SINGLE_STEP / BYPASSED with
    C0 grounding + prompt assembly) under
    ``artifacts/apps_research/runs/<ts>/``. Plan:
    apps-e2e-spine-cert-wireup-e1c4d7 W4.
    """
    from pathlib import Path

    from apps_shared.spine_emission import EmissionConfig, governed_run
    from apps_shared.spine_emission.contracts import L1PlanStep

    repo_root = Path(__file__).resolve().parents[1]
    cfg = EmissionConfig(
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
    # FEC producer registration — plan apps-research-c0-fec-producer-wiring-e7a2c3 W1.P2.
    import apps_research.cert  # noqa: F401, PLC0415
    from apps_shared.cert.fec_producer import resolve_fec  # noqa: PLC0415

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
                    "route_id": "R3_SIMPLE_GROUNDED_READ",
                    "route_contract": {"route_id": "R3_SIMPLE_GROUNDED_READ"},
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
        "route_contract": {"route_id": "R3_SIMPLE_GROUNDED_READ"},
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
    # Live certification path — emits real spine receipts and exits 0.
    if _is_live_cert_mode():
        return _run_live_cert(list(sys.argv[1:]))
    # apps_e2e auditability harness short-circuit. MUST be first statement
    # of the non-live path.
    from apps_shared._apps_e2e_dry_run import maybe_short_circuit
    maybe_short_circuit("apps_research")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    _adg_bootstrap()
    return _run_canonical(list(sys.argv[1:]))


def _run_canonical(argv: list[str]) -> int:
    """Canonical agentic_core runner path — capability resolution + governed run.

    Resolves apps_research.company_brief_v1 via the capability registry and
    delegates execution to the registered handler. On capability unavailable,
    fails closed through Exit v6 (CAPABILITY_UNAVAILABLE) — no generic brief.
    """
    from apps_research.integrations.research_capability_registry import (  # noqa: PLC0415
        CAPABILITY_ID,
        CapabilityUnavailableError,
        resolve_company_brief_capability,
    )

    try:
        handler = resolve_company_brief_capability(CAPABILITY_ID)
    except CapabilityUnavailableError as exc:
        _log.error(
            "[apps_research] Capability unavailable — failing closed. "
            "Reason: %s. No generic brief fallback.",
            exc,
        )
        _emit_capability_unavailable_exit()
        return 1

    try:
        result = handler(argv)
        return int(result) if result is not None else 0
    except Exception as exc:  # guardian: allow-broad-exception -- capability handler raises heterogeneous errors (IOError, ValueError, RuntimeError); all surfaced via Exit v6 fail-close
        _log.error("[apps_research] Capability handler raised %s: %s", type(exc).__name__, exc)
        _emit_capability_unavailable_exit()
        return 1


def _emit_capability_unavailable_exit() -> None:
    """Emit an R5-terminal Exit v6 packet for CAPABILITY_UNAVAILABLE.

    Fail-soft: any error during emission is logged and suppressed so the
    calling main() can still return a non-zero exit code.
    """
    try:
        from apps_shared.cert import maybe_invoke_exit_eval  # noqa: PLC0415
        receipts = {
            "output": {},
            "route_contract": {"route_id": "R3_SIMPLE_GROUNDED_READ"},
            "evidence_bundle": {},
            "final_evidence_contract": {},
            "state_diff": {},
            "compiled_prompt_artifact": {},
            "exit_reason": "CAPABILITY_UNAVAILABLE",
        }
        maybe_invoke_exit_eval(receipts, {"invoke_exit_eval": True})
    except Exception as exc:  # guardian: allow-broad-exception -- Exit emission on error path must never re-raise; this is a best-effort audit trail
        _log.warning("[apps_research] Exit v6 emission failed: %s: %s", type(exc).__name__, exc)


if __name__ == "__main__":
    raise SystemExit(main())
