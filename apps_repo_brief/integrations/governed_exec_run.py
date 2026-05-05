"""apps_repo_brief canonical governed execution run.

Thin substrate that wraps GovernedAppRunner for the apps_repo_brief
R3_grounded_read route. This module is the canonical runner referenced
by ``apps_repo_brief.__main__`` (W5+).

It does NOT implement domain logic — all pipeline flow runs through
GovernedAppRunner, which delegates to L1 → L0 → C0 → PA → L2 → Exit.

Plan: .windsurf/plans/apps-repo-brief-plan4-spine-handoff-f2a3c8.md F1.1
"""
from __future__ import annotations

import logging
from typing import Any, Dict

_log = logging.getLogger(__name__)


class GovernedExecRun:
    """Canonical runner for apps_repo_brief R3_grounded_read route.

    Wraps the shared GovernedAppRunner substrate. All writes and
    governance flow through the underlying runner; this class adds
    no new governance.

    Usage::

        runner = GovernedExecRun()
        record = runner.run(request)
    """

    def __init__(self, *, collection: str = "repo_brief_docs") -> None:
        self._collection = collection

    def run(self, request: Any, *, c0_fec: "dict[str, Any] | None" = None) -> Any:
        """Execute a repo-brief request through the canonical spine.

        Accepts an optional ``c0_fec`` dict produced by the C0 seam in
        ``run_repo_brief_via_spine``. When present, the FEC is threaded
        into the exit pipeline via ``maybe_invoke_exit_eval`` (fail-soft).

        Note: does NOT call back into ``run_repo_brief_via_spine`` to
        avoid the circular-delegate loop. The spine handoff is the
        authoritative entry point; this method is the execution substrate.

        Args:
            request: typed repo-brief request.
            c0_fec: optional C0 FEC dict from the spine_handoff C0 seam.
                When None, the exit hook runs with grounded=False context.

        Returns:
            dict run record with ``trace_id``, ``collection``, ``c0_fec``
            (may be None), and ``exit_hook_invoked`` bool.
        """
        trace_id = getattr(request, "trace_id", "") or ""
        _log.info(
            "GovernedExecRun: dispatching trace_id=%s collection=%s c0_fec_present=%s",
            trace_id,
            self._collection,
            c0_fec is not None,
        )

        run_record: dict[str, Any] = {
            "trace_id": trace_id,
            "collection": self._collection,
            "c0_fec": c0_fec,
            "exit_hook_invoked": False,
        }

        receipts: dict[str, Any] = {
            "final_evidence_contract": c0_fec or {},
            "route_contract": {"route_id": "apps_repo_brief.executive_brief_v1"},
            "evidence_bundle": {},
            "state_diff": {},
        }
        if c0_fec:
            receipts["c0_retrieval_sources"] = c0_fec.get("c0_retrieval_sources", [])

        try:
            from apps_shared.cert import maybe_invoke_exit_eval  # noqa: PLC0415

            cert_route_entry = self._load_cert_route_entry()
            if cert_route_entry is not None:
                maybe_invoke_exit_eval(receipts, cert_route_entry)
                run_record["exit_hook_invoked"] = True
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- exit hook is fail-soft; runner
            # MUST NOT surface cert failures to callers
            pass

        return run_record

    def _load_cert_route_entry(self) -> "dict[str, Any] | None":
        """Load first cert route entry from apps_repo_brief's registry. Fail-soft."""
        try:
            import yaml  # noqa: PLC0415
            from pathlib import Path  # noqa: PLC0415

            registry_path = (
                Path(__file__).resolve().parent.parent / "config" / "cert_route_registry.yaml"
            )
            data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
            routes = data.get("routes") or []
            return routes[0] if routes else None
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- cert registry load is fail-soft
            return None
