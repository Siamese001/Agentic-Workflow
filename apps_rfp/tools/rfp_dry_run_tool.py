# guardian: allow-silent_swallower
"""
apps_rfp dry-run diagnostic tool.

Usage:
    python -m apps_rfp.tools.rfp_dry_run_tool

Runs a dry-run proposal for each configured industry and prints
status + quality score. No files are written. No LLM calls.
"""

from __future__ import annotations

import logging
import sys
from tqdm import tqdm

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
_log = logging.getLogger("apps_rfp.tools.rfp_dry_run_tool")

_INDUSTRIES = ["financial_services", "healthcare", "technology", "government"]
_BRIEF = "We need to modernize our AI platform to improve governance and reduce manual workflows."


def main() -> int:
    from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator
    from apps_rfp.types.rfp_types import ArchitecturePosture, RfpRequest

    failures = 0
    for industry in tqdm(_INDUSTRIES, desc="Processing", unit="item"):
        try:
            req = RfpRequest(
                problem_statement=_BRIEF,
                industry=industry,
                architecture_posture=ArchitecturePosture.CLOUD_FIRST,
                dry_run=True,
            )
            orch = RfpOrchestrator(dry_run=True)
            result = orch.run(req)
            status = str(result.status)
            score = result.quality_score
            sections = len(result.sections)
            print(f"  [{status:8s}] industry={industry:20s} score={score:.2f} sections={sections}")
            if status not in ("dry_run", "complete"):
                failures += 1
        except (RuntimeError, ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
            _log.error(f"Dry-run failed: {exc}")
            print(f"  [ERROR   ] industry={industry}: {exc}")
            failures += 1

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
