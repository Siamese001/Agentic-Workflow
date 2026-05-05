"""Exit adapter for apps_eval — maps sealed packets to X3 dispositions.

Implements Exit X1 (checkout), X2 (aggregation), X3 (disposition) for R4_SINGLE_ACTION.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def exit_disposition(
    terminal_class: str,
    x3_code: str,
    reason: str | None = None,
    scorecard_path: Path | None = None,
    scorecard_ref: str | None = None,
    **kwargs: Any,
) -> int:
    """Emit Exit X3 disposition and return shell exit code.

    X3 Codes for apps_eval (R4_SINGLE_ACTION, no HITL):
    - X3A_DENY_REROUTE: hard failure, no usable scorecard
    - X3C_COMMIT_REQUEST_TO_UWG: cache commit (eval doesn't use)
    - X3D_ALLOW_FINISH: success or degraded success
    - X3E_SAFE_ABSTAIN: suite missing, validation failed
    """
    # X1: Checkout (not used in eval — no runtime state)
    # X2: Aggregation (collected during L2 E5 SEAL)

    # X3: Exactly one disposition
    x3_dispositions = {
        "X3A_DENY_REROUTE": _handle_x3a,
        "X3D_ALLOW_FINISH": _handle_x3d,
        "X3E_SAFE_ABSTAIN": _handle_x3e,
    }

    handler = x3_dispositions.get(x3_code, _handle_x3e)
    return handler(terminal_class, reason, scorecard_path, scorecard_ref, **kwargs)


def _handle_x3a(
    terminal_class: str,
    reason: str | None,
    scorecard_path: Path | None,
    scorecard_ref: str | None,
    **kwargs: Any,
) -> int:
    """X3A_DENY_REROUTE — hard failure."""
    logger.error("Exit X3A_DENY_REROUTE: %s", reason or "unknown_failure")
    return 1


def _handle_x3d(
    terminal_class: str,
    reason: str | None,
    scorecard_path: Path | None,
    scorecard_ref: str | None,
    **kwargs: Any,
) -> int:
    """X3D_ALLOW_FINISH — success or degraded success."""
    if scorecard_path:
        logger.info("Exit X3D_ALLOW_FINISH: scorecard at %s", scorecard_path)
    elif scorecard_ref:
        logger.info("Exit X3D_ALLOW_FINISH: cached scorecard %s", scorecard_ref)
    else:
        logger.info("Exit X3D_ALLOW_FINISH")
    return 0


def _handle_x3e(
    terminal_class: str,
    reason: str | None,
    scorecard_path: Path | None,
    scorecard_ref: str | None,
    **kwargs: Any,
) -> int:
    """X3E_SAFE_ABSTAIN — safe failure (suite missing, validation failed)."""
    logger.warning("Exit X3E_SAFE_ABSTAIN: %s", reason or "abstained")
    return 2  # Different from hard failure exit code


def maybe_invoke_exit_hook(final_evidence_contract: dict[str, Any] | None = None) -> None:
    """Optional Exit v6 hook for cert pipeline integration.

    apps_eval runs as a standalone tool; Exit hook is optional for cert bundles.
    """
    # TODO: Implement if needed for certification integration (deferred)
    pass
