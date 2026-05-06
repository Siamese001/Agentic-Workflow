"""Canonical entrypoint for apps_repo_brief.

W5 P5.6: apps_exec archived. The W1-W4 delegation shim is retired.
Invoke via: python -m apps_repo_brief [args...]

The canonical runner lives in apps_repo_brief.integrations.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P5.6
DS-1: FEC producer wired; exit hook wired.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _build_fec() -> dict:
    """Resolve apps_repo_brief FEC via the shared registry. Fail-soft."""
    try:
        import apps_repo_brief.cert  # noqa: F401, PLC0415 — side-effect register
        from apps_shared.cert.fec_producer import resolve_fec  # noqa: PLC0415

        return resolve_fec(
            "apps_repo_brief",
            {
                "route_id": "apps_repo_brief.executive_brief_v1",
                "route_contract": {"route_id": "apps_repo_brief.executive_brief_v1"},
                "template_ids": ["repo_brief_v1"],
            },
        )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- FEC resolution is fail-soft; cert failures
        # MUST NOT break the main execution path
        return {}


def _load_cert_route_entry() -> dict | None:
    """Return the first route entry from apps_repo_brief's cert_route_registry.yaml.

    Fail-soft: any parse or IO error returns None, which makes
    ``maybe_invoke_exit_eval`` a no-op. Never raises.
    """
    try:
        import yaml  # noqa: PLC0415
        from pathlib import Path  # noqa: PLC0415

        registry_path = (
            Path(__file__).resolve().parent / "config" / "cert_route_registry.yaml"
        )
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
        routes = data.get("routes") or []
        return routes[0] if routes else None
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- cert route registry is fail-soft
        return None


def _maybe_run_exit_hook(fec: dict) -> None:
    """Invoke the v6 Exit pipeline via the fail-soft helper.

    Reads apps_repo_brief/config/cert_route_registry.yaml for the
    ``invoke_exit_eval`` flag; calls
    :func:`apps_shared.cert.maybe_invoke_exit_eval` fail-soft.
    """
    cert_route_entry = _load_cert_route_entry()
    if cert_route_entry is None:
        return
    try:
        from apps_shared.cert import maybe_invoke_exit_eval  # noqa: PLC0415
    except ImportError:
        return
    receipts = {
        "final_evidence_contract": fec,
        "route_contract": {"route_id": "apps_repo_brief.executive_brief_v1"},
        "evidence_bundle": {},
        "state_diff": {},
    }
    try:
        maybe_invoke_exit_eval(receipts, cert_route_entry)
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- cert hook MUST NOT break the
        # main execution path; Exit failures are additional evidence only
        pass


def _create_minimal_request(args: argparse.Namespace):
    """Create minimal request object for spine handoff."""
    class MinimalRequest:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    return MinimalRequest(
        audience=args.audience,
        emphasis_areas=args.emphasis_areas.split(",") if args.emphasis_areas else [],
        trace_id=args.trace_id,
        brief_type=args.brief_type,
        c0_required=not args.skip_c0,
        depth_profile=args.depth_profile,
    )


def _ensure_route_registry(path: Path) -> None:
    """Create minimal route registry for governed_run compatibility."""
    import yaml  # noqa: PLC0415
    path.parent.mkdir(parents=True, exist_ok=True)
    registry = {
        "routes": [
            {
                "route_id": "apps_repo_brief.executive_brief_v1",
                "route_family": "R3_GROUNDED_READ",
                "enabled": True,
                "execution_form": "SINGLE_STEP",
                "expects_c0_grounding": True,
                "expects_prompt_assembly": False,
            }
        ]
    }
    path.write_text(yaml.dump(registry), encoding="utf-8")


def main() -> None:
    """apps_repo_brief canonical entry point (W5+)."""
    parser = argparse.ArgumentParser(description="apps_repo_brief — R3_grounded_read route")
    parser.add_argument("--audience", default="general", help="Target audience for brief")
    parser.add_argument("--emphasis-areas", default="", help="Comma-separated emphasis areas")
    parser.add_argument("--trace-id", default="", help="Trace ID for request")
    parser.add_argument("--brief-type", default="executive", help="Brief type")
    parser.add_argument("--skip-c0", action="store_true", help="Skip C0 grounding")
    parser.add_argument("--depth-profile", default="REPO_BRIEF_STANDARD", help="Depth profile")
    args = parser.parse_args()

    from apps_shared.spine_emission import EmissionConfig, governed_run
    from apps_repo_brief.integrations.spine_handoff import run_repo_brief_via_spine

    # Build EmissionConfig for apps_repo_brief
    out_dir = Path("artifacts/apps_repo_brief/runs")
    registry_path = Path(__file__).resolve().parent / "config" / "route_registry.yaml"
    if not registry_path.exists():
        _ensure_route_registry(registry_path)

    cfg = EmissionConfig(
        app_name="apps_repo_brief",
        entrypoint_command=f"python -m apps_repo_brief --audience {args.audience}",
        runs_root=out_dir,
        route_registry_path=registry_path,
        l3_dag_path=None,
        plan_steps=[],
        plan_rationale=f"Repo brief for audience: {args.audience}",
        expects_c0_grounding=not args.skip_c0,
        expects_prompt_assembly=False,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
    )

    request = _create_minimal_request(args)

    with governed_run(cfg, cli_args=sys.argv[1:]) as gr:
        with gr.span("L2_execute"):
            result = run_repo_brief_via_spine(request)
        gr.set_subprocess_exit_code(0 if result else 1)

    # Post-run cert hook (outside governed_run context)
    _fec = _build_fec()
    _maybe_run_exit_hook(_fec)


if __name__ == "__main__":
    main()
