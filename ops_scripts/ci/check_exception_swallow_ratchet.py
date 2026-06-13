#!/usr/bin/env python3
"""Gate S3 — exception swallow antipattern ratchet (plan wiring-ci / ADR-034).

Counts ADG edges whose ``semantic_type`` is one of the exception-swallow
families (silent / log / broad-except) in production scope.

Tier: **R** (ratchet).

Seed:

    python ops_scripts/ci/check_exception_swallow_ratchet.py --seed
"""

from __future__ import annotations

__adg_consumer_mode__ = "inventory"

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (
    Violation,
    WiringGate,
    cli_exit,
    connect_snapshot,
    latest_snapshot,
)

SWALLOW_SEMANTICS = (
    "antipattern_silent_swallow",
    "antipattern_log_swallow",
    "antipattern_broad_except",
)

PRODUCTION_ROOTS = (
    "agentic_core/",
    "apps_eval/",
    "apps_exec/",
    "apps_lic/",
    "apps_research/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "system_learning/",
    "infrastructure/",
)
EXCLUDE_PREFIXES = (
    "tests/",
    "tools/archive/",
    "tools/bench/",
    "tools/debug/",
    "tools/diag/",
    "archives/",
)


def _scoped(resolved_path: str | None) -> bool:
    if not resolved_path:
        return False
    if not resolved_path.startswith(PRODUCTION_ROOTS):
        return False
    return not any(resolved_path.startswith(p) for p in EXCLUDE_PREFIXES)


class ExceptionSwallowRatchetGate(WiringGate):
    gate_id = "S3_exception_swallow_ratchet"
    tier = "R"
    baseline_filename = "wiring_exception_swallow_ratchet.json"

    def run(self, conn) -> list[Violation]:
        placeholders = ",".join("?" * len(SWALLOW_SEMANTICS))
        rows = conn.execute(
            f"""
            SELECT e.source_file, e.line_no, src.resolved_path, e.semantic_type
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            WHERE e.semantic_type IN ({placeholders})
            """,
            SWALLOW_SEMANTICS,
        ).fetchall()
        violations: list[Violation] = []
        for source_file, line_no, src_path, sem in rows:
            if not _scoped(src_path):
                continue
            loc = f"{source_file or src_path}:{line_no or 0}"
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=loc,
                    rule="exception_swallow_antipattern",
                    detail=f"{sem}; module={src_path}",
                    extra={
                        "source_file": source_file,
                        "line_no": line_no,
                        "module": src_path,
                        "semantic_type": sem,
                    },
                )
            )
        violations.sort(key=lambda v: v.subject)
        return violations


def main() -> int:
    gate = ExceptionSwallowRatchetGate()
    if "--seed" in sys.argv:
        conn = connect_snapshot(latest_snapshot())
        try:
            raw = gate.run(conn)
        finally:
            conn.close()
        gate.seed_baseline(len(raw))
        print(f"[{gate.gate_id}] baseline seeded: count={len(raw)}")
        return 0
    result = gate.execute()
    if result.baseline_count is not None:
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    raise SystemExit(main())
