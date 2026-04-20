# guardian: allow-silent_swallower
"""
apps_research dry-run diagnostic tool.

Usage:
    python -m apps_research.tools.research_dry_run_tool

Runs a dry-run research artifact for each ArtifactMode and prints
status + quality score. No files are written. No LLM calls.
"""

from __future__ import annotations

import logging
import sys
from tqdm import tqdm

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
_log = logging.getLogger("apps_research.tools.research_dry_run_tool")

_TOPIC = "Agentic AI platform governance and deterministic execution contracts"


def main() -> int:
    from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
    from apps_research.types.research_types import ArtifactMode, ResearchRequest

    modes = [m.value for m in ArtifactMode]
    failures = 0

    for mode in tqdm(modes, desc="Processing", unit="item"):
        try:
            req = ResearchRequest(
                topic=_TOPIC,
                mode=ArtifactMode(mode),
                dry_run=True,
            )
            orch = ResearchOrchestrator(dry_run=True)
            result = orch.run(req)
            status = result.status.value
            score = result.quality_score
            sections = len(result.sections)
            sources = len(result.source_register)
            print(f"  [{status:8s}] mode={mode:20s} score={score:.2f} sections={sections} sources={sources}")
            if status not in ("dry_run", "complete"):
                failures += 1
        except (RuntimeError, ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
            _log.error(f"Dry-run failed: {exc}")
            print(f"  [ERROR   ] mode={mode}: {exc}")
            failures += 1

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
