"""Pure-shim entrypoint for apps_repo_brief (W1 transition).

This module is intentionally minimal — a pure argument-parsing shim that
delegates to the canonical apps_exec runner during the W1-W4 transition
window. No engine instantiation, no direct provider calls, no business logic.

Usage:
    python -m apps_repo_brief [args...]

Delegation chain:
    __main__ → apps_exec.__main__.main()  (W1-W4 shim)
    __main__ → apps_repo_brief runner (W5+, once canonical runner exists)

Entrypoint purity:
    This file MUST remain a pure shim. Any implementation logic belongs in:
    - apps_repo_brief/integrations/ (W2+)
    - apps_repo_brief/engines/ (W3+)
    The ONLY permitted non-trivial code here is argument parsing and a
    single call to a canonical runner function.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P1.10
"""
from __future__ import annotations

import sys


def main() -> None:
    """Delegate to apps_exec entrypoint during W1-W4 shim window.

    W5: Replace this with the canonical apps_repo_brief runner call once
    the zero-hard-refs gate passes and apps_exec is fully retired.
    """
    try:
        import apps_exec.__main__ as _exec_main

        _exec_main.main()
    except ImportError as exc:
        print(
            f"[apps_repo_brief] ERROR: apps_exec not available: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
