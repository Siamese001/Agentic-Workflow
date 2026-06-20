#!/usr/bin/env python3
"""CI gate: check_pipeline_skips.py — ADG pipeline skip-ledger enforcement.

Plan adg-pipeline-e2e-5287a1 W4b. Symmetric to `check_snapshot_has_mvs.py` but
for the non-blocking intelligence-layer artifacts (P4/P5/P6/P6b/P7).

Background
----------
W4a converted the 5 `print("[ADG] P* skipped: {e}")` sites in
`tools/generate/generate_full_adg.py` to emit a JSONL ledger entry via
`_record_pipeline_skip()`. Each ledger entry is:

    {"ts": "...", "layer": "P6", "name": "graph-projection",
     "exc_type": "ImportError", "exc_message": "No module named 'networkx'"}

This gate inspects the most-recent `adg_pipeline_skips_<ts>.jsonl` under
`artifacts/adg/` and fails when any skip is present beyond the allow-list.

Allow-list
----------
A skip is accepted (non-failing) when:
  - `exc_type == "ImportError"` AND the allow-list env flag
    `ADG_PIPELINE_SKIP_ACCEPT_IMPORT_ERROR` is "1" (default on)

All other skip types fail the gate — they represent latent defects in
optional pipeline stages that must be surfaced.

Run modes
---------
    $ python ops_scripts/ci/check_pipeline_skips.py
        Check the most-recent adg_pipeline_skips_*.jsonl.

    $ python ops_scripts/ci/check_pipeline_skips.py path/to/ledger.jsonl
        Check a specific ledger file.

    Env flags:
        ADG_PIPELINE_SKIPS_WARN=1                   — warn instead of fail
        ADG_PIPELINE_SKIP_ACCEPT_IMPORT_ERROR=0     — disable ImportError allow

Exit codes
----------
    0 — ledger absent or only contains allow-listed entries
    1 — non-allow-listed skip present (or warn-mode self-fail)
    2 — runner error (ledger unreadable)

References
----------
    - Constitutional §22 (graph-layer evidence)
    - .codex/plans/adg-pipeline-e2e-5287a1.md (W4)
    - tools/generate/generate_full_adg.py::_record_pipeline_skip
"""

from __future__ import annotations

import glob
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = ROOT / "artifacts" / "adg"
LOG_DIR = ROOT / "artifacts" / "governance"
LOG_FILE = LOG_DIR / "pipeline_skip_violations.jsonl"

ACCEPT_IMPORT_ERROR = os.environ.get(
    "ADG_PIPELINE_SKIP_ACCEPT_IMPORT_ERROR",
    "1",
).strip().lower() in ("1", "true", "yes")
WARN_MODE = os.environ.get(
    "ADG_PIPELINE_SKIPS_WARN",
    "",
).strip().lower() in ("1", "true", "yes")


def _resolve_ledger(argv_path: str | None) -> Path | None:
    """Return the ledger file to inspect, or None if no ledger exists yet."""
    if argv_path:
        p = Path(argv_path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"ledger not found: {p}")
        return p
    pattern = str(ADG_DIR / "adg_pipeline_skips_*.jsonl")
    candidates = sorted(glob.glob(pattern), key=os.path.getmtime)
    return Path(candidates[-1]) if candidates else None


def _load_entries(ledger: Path) -> list[dict]:
    entries: list[dict] = []
    with ledger.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                entries.append({"_parse_error": str(exc), "_raw": line[:200]})
    return entries


def _log_violation(ledger: Path | None, failing: list[dict], allowed: list[dict]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    rec = {
        "ledger": ledger.name if ledger else None,
        "ledger_path": str(ledger) if ledger else None,
        "failing_count": len(failing),
        "allowed_count": len(allowed),
        "failing": failing,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def _classify(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return (failing, allowed)."""
    failing: list[dict] = []
    allowed: list[dict] = []
    for entry in entries:
        if "_parse_error" in entry:
            failing.append(entry)
            continue
        exc_type = entry.get("exc_type", "")
        if exc_type == "ImportError" and ACCEPT_IMPORT_ERROR:
            allowed.append(entry)
        else:
            failing.append(entry)
    return failing, allowed


def main(argv: list[str]) -> int:
    try:
        ledger = _resolve_ledger(argv[1] if len(argv) > 1 else None)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 2
    except (OSError, ValueError) as exc:
        print(f"[ERROR] ledger resolve failed: {exc}")
        return 2

    header = "=" * 72
    print(header)
    print("ADG PIPELINE SKIP LEDGER — Constitutional §22 (non-blocking stages)")
    print(header)

    if ledger is None:
        print("ledger: <none> (no pipeline-skip ledger present yet)")
        print(header)
        print("[PASS] no skips recorded")
        return 0

    try:
        entries = _load_entries(ledger)
    except OSError as exc:
        print(f"[ERROR] could not read {ledger.name}: {exc}")
        return 2

    failing, allowed = _classify(entries)
    print(f"ledger  : {ledger.name}")
    print(f"entries : {len(entries)}  (allowed={len(allowed)}  failing={len(failing)})")
    print(f"accept-import-error: {ACCEPT_IMPORT_ERROR}")
    print(header)

    for entry in allowed:
        print(
            f"[ALLOW] {entry.get('layer', '?')}/{entry.get('name', '?')}  "
            f"{entry.get('exc_type', '?')}: {entry.get('exc_message', '')[:80]}",
        )
    for entry in failing:
        if "_parse_error" in entry:
            print(f"[FAIL] malformed line: {entry['_parse_error']}")
            continue
        print(
            f"[FAIL] {entry.get('layer', '?')}/{entry.get('name', '?')}  "
            f"{entry.get('exc_type', '?')}: {entry.get('exc_message', '')[:80]}",
        )

    if not failing:
        print("\n[PASS] all skips allow-listed")
        return 0

    _log_violation(ledger, failing, allowed)
    print(
        "\nREMEDIATION:\n"
        "  1. For each failing skip, inspect the pipeline stage and fix the\n"
        "     underlying defect (schema drift, missing dependency, helper bug).\n"
        "  2. If a skip is genuinely optional (e.g., a new optional dep), update\n"
        "     ADG_PIPELINE_SKIP_ACCEPT_IMPORT_ERROR handling or add a narrower\n"
        "     allow-list entry.\n"
        "  3. Regenerate ADG: `python tools/generate_full_adg.py`\n",
    )
    print(f"Log: {LOG_FILE.relative_to(ROOT)}")

    if WARN_MODE:
        print("[WARN] ADG_PIPELINE_SKIPS_WARN=1 — exiting 0 (soft mode)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
