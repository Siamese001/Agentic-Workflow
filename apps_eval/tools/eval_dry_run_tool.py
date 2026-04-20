# guardian: allow-silent_swallower
"""
apps_eval dry-run diagnostic tool.

Usage:
    python -m apps_eval.tools.eval_dry_run_tool

Runs a dry-run evaluation with all configured suites and prints
status + scores. No files are written. No LLM calls.
"""

from __future__ import annotations

import logging
import sys

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
_log = logging.getLogger("apps_eval.tools.eval_dry_run_tool")


def main() -> int:
    from apps_eval.config.agent_spec_config import load_eval_specs
    from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator
    from apps_eval.types.eval_types import EvalRequest

    specs = load_eval_specs()
    suite_ids = list(specs.benchmark_suites.keys())

    try:
        req = EvalRequest(suite_ids=suite_ids, dry_run=True)
        orch = EvalOrchestrator(dry_run=True)
        result = orch.run(req)
        status = result.status.value
        score = result.overall_score
        suites = len(result.suite_results)
        violations = len(result.gate_violations)
        print(f"  [{status:8s}] suites={suites} overall_score={score:.2f} gate_violations={violations}")
        for row in result.scorecard:
            print(f"    {row.dimension_id:20s} score={row.score:.2f} weight={row.weight:.1f} [{row.verdict}]")
        return 0 if status in ("dry_run", "complete") else 1
    except (RuntimeError, ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
        _log.error(f"Dry-run failed: {exc}")
        print(f"  [ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
