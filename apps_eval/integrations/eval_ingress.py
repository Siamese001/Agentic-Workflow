"""Evaluation ingress runner — L1→L0→L2→Exit pipeline.

Implements the R4_SINGLE_ACTION deterministic execution path for apps_eval.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps_eval.engines.base_eval_engine import EvalResult
    from apps_eval.contracts.local_eval_evidence import LocalEvalEvidenceContract

logger = logging.getLogger(__name__)


def run_eval_from_cli(
    suites_str: str,
    scenario_filter: str = "",
    baseline_mode: bool = False,
    out_dir: str = "artifacts/apps_eval/runs",
    deterministic_only: bool = False,
    cache_strategy: str = "exact",
) -> int:
    """Run evaluation from CLI args.

    L1: Plan → L0: Route → L2: Execute → Exit: Disposition
    """
    from apps_eval.engines.eval_prep import EvalPrepStage
    from apps_eval.engines.eval_valid import EvalValidStage
    from apps_eval.engines.scenario_runner import ScenarioRunner
    from apps_eval.engines.eval_seal import EvalSealStage
    from apps_eval.integrations.exit_adapter import exit_disposition

    suite_ids = [s.strip() for s in suites_str.split(",") if s.strip()]
    if not suite_ids:
        logger.error("No suites specified")
        return exit_disposition(
            terminal_class="FAILURE",
            x3_code="X3E_SAFE_ABSTAIN",
            reason="no_suites",
        )

    # L1 + L2 E1: PREP
    prep = EvalPrepStage(
        suite_ids=suite_ids,
        scenario_filter=scenario_filter,
        baseline_mode=baseline_mode,
        out_dir=out_dir,
        deterministic_only=deterministic_only,
        cache_strategy=cache_strategy,
    )
    prep_result = prep.run()
    if not prep_result.ok:
        return exit_disposition(
            terminal_class="FAILURE",
            x3_code="X3E_SAFE_ABSTAIN",
            reason=prep_result.failure_reason or "prep_failed",
        )

    # L0: Route decision (R1A exact cache, R1B semantic cache, R4_SINGLE_ACTION)
    route_result = _check_cache_or_route(prep_result)
    if route_result.cache_hit:
        # X3D_ALLOW_FINISH with cached scorecard
        return exit_disposition(
            terminal_class="SUCCESS",
            x3_code="X3D_ALLOW_FINISH",
            scorecard_ref=route_result.scorecard_ref,
        )

    # L2 E2: VALID
    valid = EvalValidStage(prep_result)
    valid_result = valid.run()
    if not valid_result.ok:
        return exit_disposition(
            terminal_class="FAILURE",
            x3_code="X3E_SAFE_ABSTAIN",
            reason=valid_result.failure_reason or "validation_failed",
        )

    # L2 E3: EXEC (scenario loop)
    runner = ScenarioRunner(valid_result)
    exec_result = runner.run()

    # L2 E4: HEAL (inline during scenario loop)
    # L2 E5: SEAL
    sealer = EvalSealStage(exec_result)
    seal_result = sealer.run()

    # Resolve FEC (Local Evidence Contract) at exit boundary
    fec = resolve_fec(
        suite_ids=suite_ids,
        prep_result=prep_result,
        valid_result=valid_result,
        seal_result=seal_result,
    )

    # Exit: X3 disposition based on execution results
    if seal_result.all_scenarios_passed:
        return exit_disposition(
            terminal_class="SUCCESS",
            x3_code="X3D_ALLOW_FINISH",
            scorecard_path=seal_result.scorecard_path,
            fec=fec,
        )
    elif seal_result.degraded:
        return exit_disposition(
            terminal_class="DEGRADED_SUCCESS",
            x3_code="X3D_ALLOW_FINISH",
            scorecard_path=seal_result.scorecard_path,
            fec=fec,
        )
    else:
        return exit_disposition(
            terminal_class="FAILURE",
            x3_code="X3A_DENY_REROUTE",
            scorecard_path=seal_result.scorecard_path,
            fec=fec,
        )


def resolve_fec(
    suite_ids: list[str],
    prep_result,
    valid_result,
    seal_result,
) -> "LocalEvalEvidenceContract | None":
    """Resolve Final Evidence Contract at evaluation exit.

    W2.4: FEC integration wiring — produces LocalEvalEvidenceContract
    from L2 sealed artifacts for Exit v6 handoff.
    """
    from apps_eval.cert.fec_producer import produce_fec
    from apps_eval.contracts.local_eval_evidence import LocalEvalEvidenceContract

    # Build run_context for FEC producer
    run_context = {
        "route_id": "apps_eval.evaluation_v1",
        "suite_ids": suite_ids,
        "baseline_mode": prep_result.baseline_mode if prep_result else False,
        "deterministic_only": valid_result.deterministic_only if valid_result else False,
        "all_passed": seal_result.all_scenarios_passed if seal_result else False,
        "degraded": seal_result.degraded if seal_result else False,
    }

    fec_dict = produce_fec(run_context)
    return LocalEvalEvidenceContract.from_fec_dict(fec_dict)


def _check_cache_or_route(prep_result) -> "RouteResult":
    """L0 routing: check R1A exact, R1B semantic, default to R4_SINGLE_ACTION."""
    # TODO: Implement cache lookup (deferred to W3)
    return RouteResult(cache_hit=False, scorecard_ref=None)


class RouteResult:
    def __init__(self, cache_hit: bool, scorecard_ref: str | None):
        self.cache_hit = cache_hit
        self.scorecard_ref = scorecard_ref
