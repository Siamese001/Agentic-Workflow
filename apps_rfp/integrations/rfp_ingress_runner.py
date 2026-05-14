"""Ingress-wired runner factory for ``apps_rfp`` — TOMBSTONED (W2, 2026-05-14).

TOMBSTONE: make_rfp_ingress_runner() is the pre-profile dispatch= factory pattern
eliminated by the one-spine migration (W0 design question 7 / W2.P3).

The caller-supplied dispatch= parameter is the anti-pattern the one-spine law
removes. Post-W2, apps_rfp uses AppRuntimeProfile via profile_builder.py:

    from apps_rfp.runtime.profile_builder import build_app_runtime_contract
    from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
    profile = build_app_runtime_contract()
    runner = AppIngressRunner(profile=profile)
    result = runner.run(payload)

NC-4: grep confirms this factory is NOT called from apps_rfp/__main__.py
or any product path post-migration.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P3
"""

from __future__ import annotations

RFP_REQUIRED_FIELDS: tuple[str, ...] = ("rfp_id", "proposal_type", "deadline")


def make_rfp_ingress_runner(*args, **kwargs):  # type: ignore[no-untyped-def]
    """TOMBSTONED — raises RuntimeError unconditionally.

    Use build_app_runtime_contract() + AppIngressRunner(profile=profile) instead.
    """
    raise RuntimeError(
        "make_rfp_ingress_runner() is TOMBSTONED (W2 one-spine migration, 2026-05-14). "
        "Use: apps_rfp.runtime.profile_builder.build_app_runtime_contract() + "
        "agentic_core.runtime.entry.app_ingress_runner.AppIngressRunner(profile=profile). "
        "The dispatch= factory pattern is forbidden post-migration."
    )


__all__ = ["RFP_REQUIRED_FIELDS", "make_rfp_ingress_runner"]


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_rfp.integrations.rfp_ingress_runner', "module_loaded")
