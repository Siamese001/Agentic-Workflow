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
from typing import Any

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

    def run(self, request: Any) -> Any:
        """Execute a repo-brief request through the canonical spine.

        Delegates to ``apps_repo_brief.integrations.spine_handoff``
        ``run_repo_brief_via_spine`` so the handoff seam is explicit.
        """
        from apps_repo_brief.integrations.spine_handoff import (
            run_repo_brief_via_spine,
        )

        trace_id = getattr(request, "trace_id", "") or ""
        _log.info(
            "GovernedExecRun: dispatching trace_id=%s collection=%s",
            trace_id,
            self._collection,
        )
        return run_repo_brief_via_spine(request)
