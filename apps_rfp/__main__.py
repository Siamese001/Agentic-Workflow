"""Canonical entrypoint for apps_rfp.

Usage:
    python -m apps_rfp

ADG bootstrap fires before any agent dispatch.
"""

from __future__ import annotations

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("apps_rfp")


def _adg_bootstrap() -> None:
    try:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report

        report = build_pre_run_report(changed_files=[], force_fresh=False)
        _log.info("[ADG] %s", report.summary)
        if report.layer_violation_count > 0:
            _log.warning(
                "[ADG] %d layer violation(s): %s", report.layer_violation_count, report.scope_widening_events
            )
        if report.route_mode == "HUMAN_REVIEW":
            _log.error("[ADG] route_mode=HUMAN_REVIEW — manual review required")
            sys.exit(1)
    # guardian: allow-silent-swallow
    except Exception as exc:
        _log.warning("[ADG] bootstrap unavailable: %s", exc)


def main() -> None:
    _adg_bootstrap()
    from apps_rfp.scripts.run_rfp import main as _run

    sys.exit(_run())


if __name__ == "__main__":
    main()
