#!/usr/bin/env python3
"""Gate E1 — trace-stub module detector (plan W2.4).

Catches modules that are *trace theater* — modules whose outgoing import
surface is ≥80% lifecycle-trace symbols, with little or no real logic.
These modules satisfy naive trace-presence checks while the pipeline they
claim to implement has no actual wiring.

Canonical anti-example caught on first run:
    agentic_core/L1_cognition/utils/c0_context_retriever.py
    (73/78 = 0.94 trace-symbol ratio; no retrieval logic)

Tier: R (ratchet).

The initial snapshot of this repo contains ~1,250 modules above threshold —
most reflect a pervasive trace-ritual pattern rather than pure theater.
Using a ratchet locks today's count as the ceiling; any new module that
crosses threshold above baseline fails CI. Periodic ratchet-downs drive
genuine cleanup without blocking the first PR.

Seed:
    python ops_scripts/ci/check_trace_stub_modules.py --seed

Rules:
    TRACE_MARKERS = {"lifecycle_trace_contract._emit_", "lifecycle_trace_contract.emit_"}
    - Candidate modules: entity_type='module' in production roots (same
      allowlist as A1 orphan gate) excluding the trace contract itself.
    - Compute trace_ratio = trace_import_count / total_import_count on
      outgoing 'imports' edges whose `symbol` starts with any TRACE_MARKER.
    - Count when: total_import_count >= MIN_IMPORTS AND trace_ratio >= TRACE_RATIO_THRESHOLD.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
    connect_snapshot,
    latest_snapshot,
)

PRODUCTION_ROOTS = (
    "agentic_core/",
    "apps_eval/",
    "apps_exec/",
    "apps_lic/",
    "apps_research/",
    "apps_rfp/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "system_learning/",
    "infrastructure/",
)
EXCLUDE_PATHS = (
    # The trace contract producer is expected to define _emit_* — do not flag it.
    "agentic_core/runtime/contracts/lifecycle_trace_contract.py",
)
TRACE_MARKER_PREFIXES = (
    "agentic_core.runtime.contracts.lifecycle_trace_contract._emit_",
    "agentic_core.runtime.contracts.lifecycle_trace_contract.emit_",
)
MIN_IMPORTS = 10
TRACE_RATIO_THRESHOLD = 0.80


class TraceStubModuleGate(WiringGate):
    gate_id = "E1_trace_stub_module"
    tier = "R"
    baseline_filename = "wiring_trace_stub_ratchet.json"

    def run(self, conn) -> list[Violation]:
        rows = conn.execute(
            """
            SELECT e.source_file, e.symbol
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            WHERE e.relation_type = 'imports'
              AND e.source_file IS NOT NULL
              AND e.source_file != ''
            """
        ).fetchall()

        per_module: dict[str, dict[str, int]] = {}
        for src_file, symbol in rows:
            if not src_file.startswith(PRODUCTION_ROOTS):
                continue
            if src_file in EXCLUDE_PATHS:
                continue
            bucket = per_module.setdefault(src_file, {"total": 0, "trace": 0})
            bucket["total"] += 1
            if symbol and symbol.startswith(TRACE_MARKER_PREFIXES):
                bucket["trace"] += 1

        violations: list[Violation] = []
        for path, counts in per_module.items():
            total = counts["total"]
            trace = counts["trace"]
            if total < MIN_IMPORTS or trace == 0:
                continue
            ratio = trace / total
            if ratio < TRACE_RATIO_THRESHOLD:
                continue
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=path,
                    rule="trace_theater_stub",
                    detail=(
                        f"{trace}/{total} imports target trace contract symbols "
                        f"(ratio={ratio:.2f} ≥ {TRACE_RATIO_THRESHOLD}); "
                        "module is trace theater, not real logic"
                    ),
                    extra={
                        "trace_imports": trace,
                        "total_imports": total,
                        "trace_ratio": round(ratio, 3),
                    },
                )
            )
        return violations


def main() -> int:
    gate = TraceStubModuleGate()
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
    sys.exit(main())
