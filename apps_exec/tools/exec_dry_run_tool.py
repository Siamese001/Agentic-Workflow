# guardian: allow-silent_swallower
"""
apps_exec dry-run diagnostic tool.

Usage:
    python -m apps_exec.tools.exec_dry_run_tool

Runs a dry-run executive brief for each AudiencePersona and prints
status + quality score. No files are written. No LLM calls.
"""

from __future__ import annotations

import logging
import sys
from tqdm import tqdm

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
_log = logging.getLogger("apps_exec.tools.exec_dry_run_tool")


def main() -> int:
    from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
    from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

    personas = [p.value for p in AudiencePersona]
    failures = 0

    for persona in tqdm(personas, desc="Processing", unit="item"):
        try:
            req = ExecBriefRequest(
                audience=AudiencePersona(persona),
                source_dirs=["docs/architecture"],
                dry_run=True,
            )
            orch = ExecOrchestrator(dry_run=True)
            result = orch.run(req)
            status = str(result.status)
            score = result.quality_score
            sections = len(result.sections)
            print(f"  [{status:8s}] persona={persona:15s} score={score:.2f} sections={sections}")
            if status not in ("dry_run", "complete"):
                failures += 1
        except (RuntimeError, ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
            _log.error(f"Dry-run failed: {exc}")
            print(f"  [ERROR   ] persona={persona}: {exc}")
            failures += 1

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
