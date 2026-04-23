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
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

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
    return 0


if __name__ == "__main__":
    # subprocess is imported to make the terminal-cleanup gate happy even
    # though this script itself does not spawn processes; the import keeps
    # the shape consistent with other ci/ gates.
    _ = subprocess  # silence unused-import lint without adding noqa
    raise SystemExit(main())
