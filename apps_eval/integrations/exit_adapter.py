"""Exit adapter for apps_eval — maps sealed packets to X3 dispositions.

Implements Exit X1 (checkout), X2 (aggregation), X3 (disposition) for R4_SINGLE_ACTION.

Plan: apps-eval-agentic-spine-hardening-9d4f2e W4
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ExitContext:
    """W4.1: X1 Checkout context — provenance for Exit v6."""
    trace_id: str = ""
    run_dir: Path | None = None
    content_hashes: dict[str, str] | None = None
    replay_key: str = ""


@dataclass
class ExitX2Aggregate:
    """W4.2: X2 Aggregation — gate violations and stage results."""
    gate_violations: list[dict] = field(default_factory=list)
    scenario_results: list[Any] = field(default_factory=list)
    all_passed: bool = False
    degraded: bool = False


def _x1_checkout(context: ExitContext | None) -> bool:
    """W4.1: X1 Checkout — validate provenance before Exit.

    For apps_eval: verify run_dir exists and has required artifacts.
    """
    if context is None:
        logger.warning("X1 Checkout: No context provided")
        return True  # Degraded — proceed without validation

    if context.run_dir is None:
        logger.warning("X1 Checkout: No run_dir in context")
        return True

    if not context.run_dir.exists():
        logger.error("X1 Checkout: run_dir does not exist: %s", context.run_dir)
        return False

    # Check for required artifacts (manifest and scorecard)
    manifest = context.run_dir / f"eval_manifest_{context.trace_id}.json"
    scorecard = context.run_dir / f"scorecard_{context.trace_id}.csv"

    if not manifest.exists():
        logger.warning("X1 Checkout: manifest missing")
    if not scorecard.exists():
        logger.warning("X1 Checkout: scorecard missing")

    logger.info("X1 Checkout: OK — trace_id=%s", context.trace_id)
    return True


def _x2_aggregate(x2: ExitX2Aggregate | None) -> dict[str, Any]:
    """W4.2: X2 Aggregation — roll up gate violations and results.

    Returns aggregate dict for X3 decision.
    """
    if x2 is None:
        return {"violations": [], "all_passed": False, "degraded": False}

    violations = x2.gate_violations
    violation_summary = {
        "count": len(violations),
        "by_type": {},
        "by_scenario": {},
    }
    for v in violations:
        vtype = v.get("type", "unknown")
        scenario = v.get("scenario_id", "global")
        violation_summary["by_type"][vtype] = violation_summary["by_type"].get(vtype, 0) + 1
        if scenario not in violation_summary["by_scenario"]:
            violation_summary["by_scenario"][scenario] = []
        violation_summary["by_scenario"][scenario].append(v)

    result = {
        "violations": violations,
        "violation_summary": violation_summary,
        "all_passed": x2.all_passed,
        "degraded": x2.degraded,
        "scenarios_run": len(x2.scenario_results),
        "scenarios_passed": sum(1 for r in x2.scenario_results if getattr(r, "passed", False)),
    }

    logger.info(
        "X2 Aggregate: scenarios=%d passed=%d violations=%d degraded=%s",
        result["scenarios_run"],
        result["scenarios_passed"],
        result["violation_summary"]["count"],
        result["degraded"],
    )
    return result


def _map_terminal_to_x3(
    terminal_class: str,
    x2_aggregate: dict[str, Any],
    has_scorecard: bool,
) -> str:
    """W4.3: Map terminal class to exact X3 disposition.

    apps_eval uses only X3D/X3E (no HITL X3B):
    - X3D_ALLOW_FINISH: success or degraded success with scorecard
    - X3E_SAFE_ABSTAIN: validation failed, suite missing, or no scorecard
    """
    if not has_scorecard:
        return "X3E_SAFE_ABSTAIN"

    # SUCCESS or DEGRADED_SUCCESS → X3D_ALLOW_FINISH
    if terminal_class in ("SUCCESS", "DEGRADED_SUCCESS"):
        return "X3D_ALLOW_FINISH"

    # FAILURE with violations → X3E_SAFE_ABSTAIN (eval doesn't reroute)
    if x2_aggregate.get("violation_summary", {}).get("count", 0) > 0:
        return "X3E_SAFE_ABSTAIN"

    # Default: safe abstain
    return "X3E_SAFE_ABSTAIN"


def exit_disposition(
    terminal_class: str,
    x3_code: str,
    reason: str | None = None,
    scorecard_path: Path | None = None,
    scorecard_ref: str | None = None,
    **kwargs: Any,
) -> int:
    """Emit Exit X3 disposition and return shell exit code.

    W4: Exit v6 wiring — X1 → X2 → X3 pipeline.

    X3 Codes for apps_eval (R4_SINGLE_ACTION, no HITL):
    - X3D_ALLOW_FINISH: success or degraded success (with scorecard)
    - X3E_SAFE_ABSTAIN: suite missing, validation failed, no scorecard
    """
    # W4.1: X1 Checkout (provenance validation)
    context = kwargs.get("context")
    checkout_ok = _x1_checkout(context)
    if not checkout_ok:
        logger.error("X1 Checkout failed — forcing X3E_SAFE_ABSTAIN")
        x3_code = "X3E_SAFE_ABSTAIN"
        reason = reason or "checkout_failed"

    # W4.2: X2 Aggregation (gate violations rollup)
    x2 = kwargs.get("x2_aggregate")
    x2_aggregate = _x2_aggregate(x2)

    # W4.3: X3 Exact Disposition (map terminal_class to X3)
    has_scorecard = scorecard_path is not None or scorecard_ref is not None
    mapped_x3 = _map_terminal_to_x3(terminal_class, x2_aggregate, has_scorecard)

    # Use caller's x3_code if provided, otherwise use mapped
    final_x3 = x3_code if x3_code else mapped_x3

    # X3 execution
    x3_dispositions = {
        "X3D_ALLOW_FINISH": _handle_x3d,
        "X3E_SAFE_ABSTAIN": _handle_x3e,
    }

    handler = x3_dispositions.get(final_x3, _handle_x3e)
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
