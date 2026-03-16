#!/usr/bin/env python3
"""
Test Silent Skip CI Guardrail

Scans test files for over-broad import guards that silently skip ALL tests
when any non-import error occurs during module setup.

Anti-pattern (DANGEROUS):
    try:
        from some.module import Foo, NONEXISTENT_CONSTANT
        _AVAILABLE = True
    except Exception:          # catches NameError, AttributeError, SyntaxError…
        _AVAILABLE = False     # ALL tests in this file permanently silently skip

Required pattern (SAFE):
    except ImportError:        # only catches genuine missing modules
        _AVAILABLE = False

RCA: This pattern caused 1569 test files to silently drop all coverage whenever
a real bug existed in the imported module, hiding defects indefinitely.
Two layers of existing scanning excluded test files:
  1. SilentDegradationDetector — explicitly whitelists test_*.py
  2. AntiPatternScanner.DEFAULT_EXCLUDES — contains **/test_*
This script fills that gap.

Usage:
    python ops_scripts/ci/check_test_silent_skips.py [dir_or_file ...]
    python ops_scripts/ci/check_test_silent_skips.py --json

Exit codes:
    0 — No violations
    1 — Violations found (build fails)
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "check_test_silent_skips")
_emit_applies_guardrail("p0", "check_test_silent_skips", "p0_governance")
_emit_reads_policy_state("p0", "check_test_silent_skips", "policy_binding")
_emit_snapshots_state("p0", "check_test_silent_skips", "state_snapshot")
emit_replay_key("p0", "check_test_silent_skips")
emit_determinism_digest("p0", "check_test_silent_skips")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))  # guardian: allow-global-mutation -- CI bootstrap

from agentic_core.L5_safety.validators.test_skip_detector_validator import (
    TestSilentSkipDetector,
)

DEFAULT_SCAN_DIRS = ["tests"]
DEFAULT_EXCLUDES = {"__pycache__", ".pyc"}


def _collect_test_files(roots: list[str]) -> list[Path]:
    """Collect all test_*.py and *_test.py files under the given roots."""
    files: list[Path] = []
    for root in roots:
        p = Path(root)
        if p.is_file() and p.suffix == ".py":
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*.py"):
                if "__pycache__" in f.parts:
                    continue
                if f.name.startswith("test_") or f.name.endswith("_test.py"):
                    files.append(f)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="check_test_silent_skips",
        description="Scan test files for over-broad import guards (except Exception: _AVAILABLE=False)",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        default=DEFAULT_SCAN_DIRS,
        help="Directories or files to scan (default: tests/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit results as JSON",
    )
    parser.add_argument(
        "--max-violations",
        type=int,
        default=None,
        metavar="N",
        help="Exit 0 if violation count <= N (ratchet mode)",
    )
    args = parser.parse_args()

    detector = TestSilentSkipDetector()
    test_files = _collect_test_files(args.paths)

    if not test_files:
        print(f"[check_test_silent_skips] No test files found under: {args.paths}")
        return 0

    all_violations = []
    for f in test_files:
        result = detector.scan_file(f)
        for v in result.violations:
            if not v.whitelisted:
                all_violations.append(v)

    if args.json_output:
        payload = {
            "total_files_scanned": len(test_files),
            "total_violations": len(all_violations),
            "violations": [v.to_dict() for v in all_violations],
        }
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(
            f"[check_test_silent_skips] Scanned {len(test_files)} test file(s) — "
            f"{len(all_violations)} violation(s)"
        )
        for v in all_violations:
            rel = Path(v.file_path).relative_to(_REPO_ROOT) if Path(v.file_path).is_absolute() else v.file_path
            flag = v.metadata.get("flag", "?")
            caught = v.metadata.get("caught", "?")
            print(f"  {rel}:{v.line_number}  [{caught}]  {flag}=False")
            print(f"    → {v.message[:100]}")

    if args.max_violations is not None:
        return 0 if len(all_violations) <= args.max_violations else 1

    return 1 if all_violations else 0


if __name__ == "__main__":
    sys.exit(main())
