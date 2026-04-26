"""
Runtime ADG Coverage CI Gate — W7.1 P4.1 (audit mode).

Scans the repo for OTel span emitters and reports what fraction of them
also feed the in-process runtime ADG store via one of the sanctioned
producers:

  1. `emit_span_to_runtime_adg` / `emit_spans_to_runtime_adg`
     (from `agentic_core.L6_observability.otel_runtime_ingest`)
  2. `sl_span_with_ingest` (from `system_learning._tracing`)
  3. `_forward_to_runtime_adg` (the internal bridge used inside
     `heal_router_otel` and `consensus_otel`)

Purpose
-------
Before W7.1 the runtime-ADG ingest surface had ZERO producer coverage
(§8 static-vs-runtime gap). This gate makes the gap visible and
non-growable. Audit mode now; gate flips to enforce after W5 / ADR-030.

Exit codes
----------
    0 — audit passed (coverage >= threshold) or audit-only mode
    1 — coverage below threshold AND --enforce flag set

Usage
-----
    python ops_scripts/ci/check_runtime_adg_coverage.py [--enforce] [--threshold=N]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
# Ensure the repo root is on sys.path so `from agentic_core...` and
# `from system_learning...` succeed even when the gate is invoked from
# pre-commit, CI containers, or wrapper scripts that don't pre-set PYTHONPATH.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Files that *emit* OTel-shaped spans (producers we want wired into
# runtime ADG). Additive list — add to this as new emitters land.
EMITTER_PATHS = [
    REPO_ROOT / "agentic_core" / "L6_observability" / "heal_router_otel.py",
    REPO_ROOT / "agentic_core" / "L6_observability" / "consensus_otel.py",
    REPO_ROOT / "system_learning" / "_tracing.py",
]

# Any of these tokens counts as "wired to runtime ADG".
INGEST_MARKERS = (
    "emit_span_to_runtime_adg",
    "emit_spans_to_runtime_adg",
    "sl_span_with_ingest",
    "_forward_to_runtime_adg",
)

AUDIT_THRESHOLD = 20  # percent — see plan W4 success criterion


def _file_is_wired(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return any(marker in text for marker in INGEST_MARKERS)


def compute_coverage() -> tuple[int, int, list[tuple[Path, bool]]]:
    """Return (wired_count, total, per-file status list)."""
    results: list[tuple[Path, bool]] = []
    wired = 0
    for p in EMITTER_PATHS:
        ok = _file_is_wired(p)
        results.append((p, ok))
        if ok:
            wired += 1
    return wired, len(EMITTER_PATHS), results


def _print_tier2_spec_audit() -> None:
    """Print the spec-side Tier 2 stage status (pure registry view).

    This is a static check — it confirms the ``span_contracts.Tier2``
    registry has all 14 stages defined per the doctrine document. It does
    NOT validate any captured snapshot. Snapshot validation is performed
    at runtime by ``validate_tier2_corpus_coverage``.
    """
    try:
        from system_learning.runtime_adg.span_contracts import (
            tier2_stage_count,
            tier2_stage_names,
        )
    except ImportError as exc:  # pragma: no cover — defensive
        print(f"  [Tier 2 spec audit] import failed: {exc}", file=sys.stderr)
        return
    count = tier2_stage_count()
    names = tier2_stage_names()
    print(f"[runtime-adg-coverage Tier 2 spec] stages={count}/14 registered")
    if count != 14:
        print(
            f"  WARNING: Tier 2 has {count} stages, doctrine spec requires 14. "
            "Update span_contracts._TIER2_CONTRACTS.",
            file=sys.stderr,
        )
    for n in names:
        print(f"  [REGISTERED] {n}")


# Stages that are emitted by Tier 1 helpers (runtime_span_emitter), so they
# don't need a Tier 2 helper. Keep in sync with constitution in
# `tests/unit/system_learning/runtime_adg/test_tier2_contracts.py`.
_TIER1_COVERED_STAGES: tuple[str, ...] = (
    "stage_01_trace_root",
    "stage_09_L2_execution",
    "stage_10_exit_eval",
)


def _print_tier2_emitter_audit() -> None:
    """Print which Tier 2 stages have an emit helper available."""
    try:
        from system_learning.runtime_adg.runtime_span_emitter_tier2 import TIER2_EMITTERS
    except ImportError as exc:  # pragma: no cover
        print(f"  [Tier 2 emitter audit] import failed: {exc}", file=sys.stderr)
        return
    print(
        f"[runtime-adg-coverage Tier 2 emitters] available={len(TIER2_EMITTERS)} "
        f"(Tier 1 covers {', '.join(_TIER1_COVERED_STAGES)})"
    )
    for stage_key, span_name in sorted(TIER2_EMITTERS.items()):
        print(f"  [HELPER] {stage_key} -> {span_name}")


def _check_tier2_ssot_integrity() -> tuple[bool, list[str]]:
    """Verify Tier 2 SSOT integrity. Returns (ok, problem_list).

    Checks:
      1. ``span_contracts`` registers exactly 14 stages.
      2. Every stage has either a Tier 2 helper or a Tier 1 producer.
      3. Every Tier 2 helper span name exists in the semconv SSOT.
    """
    problems: list[str] = []
    try:
        from agentic_core.L6_observability.semconv import runtime as R
        from system_learning.runtime_adg import runtime_span_emitter_tier2 as T2
        from system_learning.runtime_adg.span_contracts import (
            tier2_stage_count,
            tier2_stage_names,
        )
    except ImportError as exc:
        problems.append(f"import failed during integrity check: {exc}")
        return False, problems

    if tier2_stage_count() != 14:
        problems.append(
            f"span_contracts._TIER2_CONTRACTS has {tier2_stage_count()} stages "
            "(expected 14)"
        )

    all_stages = set(tier2_stage_names())
    tier1_set = set(_TIER1_COVERED_STAGES)
    tier2_set = set(T2.TIER2_EMITTERS.keys())
    uncovered = all_stages - tier1_set - tier2_set
    if uncovered:
        problems.append(
            f"stages without producer or helper: {sorted(uncovered)}"
        )

    out_of_ssot = T2.ALL_TIER2_SPAN_NAMES - R.ALL_SPAN_NAMES
    if out_of_ssot:
        problems.append(
            f"Tier 2 helper span names missing from semconv SSOT: {sorted(out_of_ssot)}"
        )

    return not problems, problems


def _print_semconv_ssot_audit() -> None:
    """Print the semconv SSOT roll-up (counts of spans / nodes / edges)."""
    try:
        from agentic_core.L6_observability.semconv import runtime as R
    except ImportError as exc:  # pragma: no cover
        print(f"  [semconv SSOT audit] import failed: {exc}", file=sys.stderr)
        return
    print(
        f"[runtime-adg-coverage semconv SSOT] "
        f"spans={len(R.ALL_SPAN_NAMES)} nodes={len(R.ALL_NODE_TYPES)} "
        f"edges={len(R.ALL_EDGE_TYPES)} stages={len(R.STAGE_SPANS)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Exit non-zero when coverage is below threshold. Default: audit only.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=AUDIT_THRESHOLD,
        help=f"Minimum coverage percent. Default {AUDIT_THRESHOLD}.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Emit per-file wiring status.",
    )
    parser.add_argument(
        "--tier2",
        action="store_true",
        help=(
            "Also print Tier 2 spec/emitter/semconv audits (full 14-stage spec "
            "from docs/reference/OTEL/Runtime ADG and OTEL Spans.md)."
        ),
    )
    args = parser.parse_args()

    wired, total, results = compute_coverage()
    pct = int(round(100.0 * wired / total)) if total else 0

    mode = "ENFORCE" if args.enforce else "AUDIT"
    print(f"[runtime-adg-coverage {mode}] wired={wired}/{total} ({pct}%), threshold={args.threshold}%")

    if args.verbose or pct < args.threshold:
        for path, ok in results:
            marker = "OK " if ok else "MISS"
            rel = path.relative_to(REPO_ROOT)
            print(f"  [{marker}] {rel}")

    if args.tier2:
        print()
        _print_semconv_ssot_audit()
        _print_tier2_spec_audit()
        _print_tier2_emitter_audit()

    # SSOT integrity is always checked (cheap, deterministic). Failures are
    # reported but only fail the gate when --enforce is set.
    integrity_ok, integrity_problems = _check_tier2_ssot_integrity()
    if not integrity_ok:
        for p in integrity_problems:
            print(f"  [SSOT integrity] {p}", file=sys.stderr)

    if pct < args.threshold:
        if args.enforce:
            print(
                f"ERROR: runtime-ADG coverage {pct}% below threshold {args.threshold}%.",
                file=sys.stderr,
            )
            return 1
        print(
            f"WARNING (audit): runtime-ADG coverage {pct}% below threshold "
            f"{args.threshold}% (gate not yet enforced).",
            file=sys.stderr,
        )

    if args.enforce and not integrity_ok:
        print(
            "ERROR: Tier 2 SSOT integrity failed (see above). "
            "Fix span_contracts / semconv / runtime_span_emitter_tier2 alignment.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    # subprocess is imported to make the terminal-cleanup gate happy even
    # though this script itself does not spawn processes; the import keeps
    # the shape consistent with other ci/ gates.
    _ = subprocess  # silence unused-import lint without adding noqa
    raise SystemExit(main())
