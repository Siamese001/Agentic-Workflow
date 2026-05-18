"""Fail-closed messaging for legacy ``python -m apps_rg.runtime.dispatch.*`` CLIs."""
from __future__ import annotations

import sys

_MSG_PREFIX = "Deprecated runtime interface."


def exit_deprecated_dispatch_cli(*, section: str | None = None) -> int:
    """Print stderr guidance and return exit code 2 (do not execute lane)."""
    if section:
        msg = f"{_MSG_PREFIX} Use: python -m apps_rg --section {section}"
    else:
        msg = f"{_MSG_PREFIX} Use: python -m apps_rg (see --help for supported options)."
    print(msg, file=sys.stderr, flush=True)
    return 2


__all__ = ["exit_deprecated_dispatch_cli"]
