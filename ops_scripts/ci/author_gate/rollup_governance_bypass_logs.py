#!/usr/bin/env python3
"""
rollup_governance_bypass_logs.py — W4.2 aggregate CI/hook bypass JSONL files.

Scans (rglob) under selected artifact roots for files matching *bypass*.jsonl,
counts lines, optionally buckets coarse JSON `reason` / `msg` fields.

Writes:
  artifacts/cursor/governance_bypass_rollup_latest.json

Exit 0 always (operator visibility). BYPASS: ROLLUP_GOVERNANCE_BYPASS_LOGS_BYPASS=1.

Scans only:
  artifacts/cursor/
  artifacts/cursor/
  artifacts/ci/
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_ROOTS = (
    REPO_ROOT / "artifacts" / "windsurf",
    REPO_ROOT / "artifacts" / "cursor",
    REPO_ROOT / "artifacts" / "ci",
)
OUT_JSON = REPO_ROOT / "artifacts" / "windsurf" / "governance_bypass_rollup_latest.json"
MAX_LINE_BYTES = 65536


def _scan_file(path: Path) -> dict[str, Any]:
    line_count = 0
    reasons: Counter[str] = Counter()
    parse_errors = 0
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {"path": str(path), "lines": 0, "error": "read_failed", "reasons": {}}
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        line_count += 1
        if len(raw) > MAX_LINE_BYTES:
            reasons["line_too_long"] += 1
            continue
        try:
            obj = json.loads(raw)
            key = str(
                obj.get("reason") or obj.get("msg") or obj.get("message") or "unspecified"
            )[:120]
            reasons[key] += 1
        except json.JSONDecodeError:
            parse_errors += 1
            reasons["unparseable_line"] += 1
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "lines": line_count,
        "parse_errors": parse_errors,
        "mtime_utc": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(
            timespec="seconds"
        ),
        "top_reasons": dict(reasons.most_common(12)),
    }


def main() -> int:
    if os.environ.get("ROLLUP_GOVERNANCE_BYPASS_LOGS_BYPASS", "").strip() == "1":
        print("[bypass_rollup] BYPASS — ROLLUP_GOVERNANCE_BYPASS_LOGS_BYPASS=1", file=sys.stderr)
        return 0

    files: list[Path] = []
    for root in ARTIFACT_ROOTS:
        if not root.exists():
            continue
        try:
            for p in root.rglob("*bypass*.jsonl"):
                if p.is_file():
                    files.append(p)
        except OSError:
            continue

    files = sorted(set(files))
    per_file = [_scan_file(p) for p in files]
    total_lines = sum(int(x.get("lines") or 0) for x in per_file)

    payload = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files_scanned": len(per_file),
        "total_bypass_lines": total_lines,
        "by_file": per_file,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(
        f"[bypass_rollup] files={len(per_file)} total_lines={total_lines} -> {OUT_JSON}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
