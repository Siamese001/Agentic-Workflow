"""Governed runner adapter for apps_exec.

The full apps_exec product surface is intentionally larger than this adapter.
This module restores the governed substrate entrypoint named by APP_REGISTRY
and by the shared GovernedAppRunner contract tests.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from apps_shared.integrations.governed_app_runner import (
    GovernedAppRunRecord,
    GovernedAppRunner,
    build_app_record,
)


@dataclass(frozen=True)
class GovernedExecE2ERunRecord:
    """Sealed record for one apps_exec governed run."""

    run_id: str
    audience: str
    emphasis_areas: tuple[str, ...]
    query: str
    l1_sub_queries: tuple[str, ...]
    l1_fallback: bool
    l0_intent: str
    l0_target: str
    l0_confidence: float
    l0_fallback: bool
    c0_raw_count: int
    c0_shaped_count: int
    c0_collection: str
    disposition: str
    gate_disposition: str
    grounded: bool
    citation_count: int
    support_coverage: float
    l6_ingested: bool
    error: str
    l2_executed: bool = False
    l1_error: str = ""
    l0_error: str = ""
    c0_error: str = ""
    l2_error: str = ""
    l5_error: str = ""
    l6_error: str = ""
    hitl_error: str = ""
    hitl_action: str = "none"
    hitl_class: str = ""
    hitl_ledger_id: str = ""
    hitl_enabled: bool = False


class GovernedExecRun(GovernedAppRunner):
    """GovernedAppRunner substrate adapter for executive brief assembly."""

    APP_NAME = "apps_exec"
    CAPABILITY_TOKEN = "apps_exec.governed_e2e.v1"
    ROUTING_TARGET = "exec_brief_assembly"
    ROUTING_KEYWORDS = ["executive", "brief", "board", "cto", "svp", "recruiter"]
    HITL_ENABLED = True

    def __init__(self, collection: str = "exec_docs") -> None:
        super().__init__(collection=collection)

    def run_governed_e2e(
        self,
        request: Any,
        *,
        inject_chunks: list[Any] | None = None,
    ) -> GovernedExecE2ERunRecord:
        """Run the shared governed substrate and translate to apps_exec shape."""
        audience = str(getattr(request, "audience", "") or "executive")
        emphasis = tuple(getattr(request, "emphasis_areas", ()) or ())
        query = str(
            getattr(request, "query", "")
            or getattr(request, "topic", "")
            or f"executive brief for {audience}"
        )
        run_id = str(getattr(request, "trace_id", "") or getattr(request, "run_id", "") or uuid.uuid4())
        core: GovernedAppRunRecord = self.run_governed_core(
            query=query,
            run_id=run_id,
            inject_chunks=inject_chunks,
        )
        return build_app_record(
            GovernedExecE2ERunRecord,
            core,
            audience=audience,
            emphasis_areas=emphasis,
        )


__all__ = ["GovernedExecE2ERunRecord", "GovernedExecRun"]

