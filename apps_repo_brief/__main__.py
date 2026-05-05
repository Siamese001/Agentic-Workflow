"""Canonical entrypoint for apps_repo_brief.

W5 P5.6: apps_exec archived. The W1-W4 delegation shim is retired.
Invoke via: python -m apps_repo_brief [args...]

The canonical runner lives in apps_repo_brief.integrations.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P5.6
"""
from __future__ import annotations

import sys


def main() -> None:
    """apps_repo_brief canonical entry point (W5+)."""
    from apps_repo_brief.integrations.governed_exec_run import GovernedExecRun  # noqa: F401

    print(
        "[apps_repo_brief] Canonical runner — use GovernedExecRun directly.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
