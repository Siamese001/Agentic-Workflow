"""Canonical entrypoint for apps_lic.

Usage:
    python -m apps_lic

ADG bootstrap fires before any agent dispatch. Gracefully degrades if ADG
is unavailable — never blocks execution on ADG failure.
"""

from __future__ import annotations

import logging
import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "__main__")
_emit_applies_guardrail("p0", "__main__", "p0_governance")
_emit_reads_policy_state("p0", "__main__", "policy_binding")
_emit_snapshots_state("p0", "__main__", "state_snapshot")
emit_replay_key("p0", "__main__")
emit_determinism_digest("p0", "__main__")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("apps_lic")


def _adg_bootstrap() -> None:
    try:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report

        report = build_pre_run_report(changed_files=[], force_fresh=False)
        _log.info("[ADG] %s", report.summary)
        if report.layer_violation_count > 0:
            _log.warning(
                "[ADG] %d layer violation(s) detected: %s",
                report.layer_violation_count,
                report.scope_widening_events,
            )
        if report.route_mode == "HUMAN_REVIEW":
            _log.error("[ADG] route_mode=HUMAN_REVIEW — manual review required before dispatch")
            sys.exit(1)
    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-silent-swallower
        _log.warning("[ADG] bootstrap unavailable: %s", exc)


def main() -> None:
    _adg_bootstrap()
    import asyncio

    from apps_lic.tools.run_workflow_lic import main as _run

    asyncio.run(_run())


if __name__ == "__main__":
    main()
