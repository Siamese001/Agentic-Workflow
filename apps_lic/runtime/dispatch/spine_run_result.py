"""Typed result for canonical apps_lic spine runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


def x3_manifest_fields(x3: Any) -> tuple[str, str, bool]:
    """Extract spine manifest X3 fields from ``X3Disposition`` (single SSOT).

    Priority for ``x3_disposition``:
      1. ``final_output["disposition"]`` (V6 packet value, e.g. X3D)
      2. ``exit_status`` (e.g. success, escalated)
      3. literal ``UNKNOWN``
    """
    final_output = getattr(x3, "final_output", None) or {}
    if isinstance(final_output, Mapping):
        disposition = final_output.get("disposition")
    else:
        disposition = None
    if disposition not in (None, ""):
        x3_disposition = str(disposition)
    else:
        exit_status_fallback = getattr(x3, "exit_status", None) or ""
        x3_disposition = str(exit_status_fallback) if exit_status_fallback else "UNKNOWN"
    exit_status = str(getattr(x3, "exit_status", None) or "unknown")
    outcome_authorized = bool(getattr(x3, "outcome_authorized", False))
    return x3_disposition, exit_status, outcome_authorized


@dataclass(frozen=True)
class SpineRunResult:
    """Result of ``run_canonical_apps_lic_spine``."""

    run_id: str
    request_id: str
    trace_id: str
    route_id: str
    route_family: str
    execution_form: str
    x3_disposition: str
    terminal_r5: bool
    terminal_r5_reason: str
    artifact_dir: Path
    producer_component: str = "apps_lic.runtime.dispatch.canonical_dispatch"
    l3_participated: bool = False
    c0_invoked: bool = False
    pa_invoked: bool = False
    l2_executed: bool = False
    l2_execution_status: str = ""
    exit_status: str = ""
    outcome_authorized: bool = False
    fault: str = ""
    artifacts: tuple[str, ...] = ()

    def to_manifest_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "route_id": self.route_id,
            "route_family": self.route_family,
            "execution_form": self.execution_form,
            "x3_disposition": self.x3_disposition,
            "exit_status": self.exit_status,
            "outcome_authorized": self.outcome_authorized,
            "terminal_r5": self.terminal_r5,
            "terminal_r5_reason": self.terminal_r5_reason,
            "artifact_dir": str(self.artifact_dir),
            "producer_component": self.producer_component,
            "l3_participated": self.l3_participated,
            "c0_invoked": self.c0_invoked,
            "pa_invoked": self.pa_invoked,
            "l2_executed": self.l2_executed,
            "l2_execution_status": self.l2_execution_status,
            "fault": self.fault,
            "artifacts": list(self.artifacts),
        }
