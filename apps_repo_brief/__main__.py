"""Canonical entrypoint for apps_repo_brief.

W5 P5.6: apps_exec archived. The W1-W4 delegation shim is retired.
Invoke via: python -m apps_repo_brief [args...]

The canonical runner lives in apps_repo_brief.integrations.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P5.6
DS-1: FEC producer wired; exit hook wired.
"""
from __future__ import annotations

import sys


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


def main() -> None:
    """apps_repo_brief canonical entry point (W5+)."""
    from apps_repo_brief.integrations.governed_exec_run import GovernedExecRun  # noqa: F401

    print(
        "[apps_repo_brief] Canonical runner — use GovernedExecRun directly.",
        file=sys.stderr,
    )
    _fec = _build_fec()
    _maybe_run_exit_hook(_fec)


if __name__ == "__main__":
    main()
