"""Verifier — W0 closure check #3: forbidden-language audit.

Plan: ``.cursor/plans/runtime-cert-hardened-w0-7e3c9a.md``

W0 is the verifier foundation only. It MUST NOT use language that overclaims:

  - "runtime certified"
  - "100% complete"
  - "100% runtime certified"
  - "semantic cache certified"
  - "OTEL certified" / "OTel certified"
  - "replay certified"
  - "fully certified"
  - "production certified"

Any W0 artifact (JSON or Markdown under ``artifacts/certification/``) that
contains one of these phrases triggers exit 2. This stops the verifier
foundation from leaking into runtime-tier language before the actual
runtime evidence has been gathered (W1+).

W0 may use:

  - "verifier foundation PASS"
  - "source-of-truth verifier PASS"
  - "acceptance legality verifier PASS"
  - "schema validation PASS"
  - "PASS" / "FAIL_CLOSED" status fields

Output: ``artifacts/certification/w0_language_discipline_report.json``

Exit codes: 0 PASS, 2 FAIL_CLOSED, 3 HARNESS_ERROR.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
LANGUAGE_REPORT = ARTIFACTS_DIR / "w0_language_discipline_report.json"

# Forbidden phrases (regex, case-insensitive). The patterns are deliberately
# strict — substring matches catch most overclaim variants.
FORBIDDEN_PATTERNS = (
    (r"runtime\s+certified", "RUNTIME_CERTIFIED_OVERCLAIM"),
    (r"100\s*%\s*complete", "PCT_COMPLETE_OVERCLAIM"),
    (r"100\s*%\s*runtime", "PCT_RUNTIME_OVERCLAIM"),
    (r"100\s*%\s*certified", "PCT_CERTIFIED_OVERCLAIM"),
    (r"semantic\s+cache\s+certified", "SEMANTIC_CACHE_CERTIFIED_OVERCLAIM"),
    (r"\botel\s+certified", "OTEL_CERTIFIED_OVERCLAIM"),
    (r"replay\s+certified", "REPLAY_CERTIFIED_OVERCLAIM"),
    (r"fully\s+certified", "FULLY_CERTIFIED_OVERCLAIM"),
    (r"production\s+certified", "PRODUCTION_CERTIFIED_OVERCLAIM"),
)

# Files to scan: ALL JSON and MD under artifacts/certification/, EXCEPT this
# report itself (the report mentions the forbidden patterns intentionally as
# the audit subject and would otherwise self-trigger).
SCAN_GLOBS = ("*.json", "*.md")
SELF_REPORT_NAME = "w0_language_discipline_report.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def _scan_text(text: str) -> list[dict]:
    """Return list of forbidden-phrase hits in the given text."""
    hits = []
    for pattern, code in FORBIDDEN_PATTERNS:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            # Capture a small surrounding context (40 chars) for diagnostics
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 20)
            hits.append({
                "code": code,
                "match": m.group(0),
                "context": text[start:end].replace("\n", " "),
                "char_offset": m.start(),
            })
    return hits


def _iter_files() -> list[Path]:
    if not ARTIFACTS_DIR.exists():
        return []
    files: list[Path] = []
    for pat in SCAN_GLOBS:
        files.extend(ARTIFACTS_DIR.glob(pat))
    return sorted(p for p in files if p.name != SELF_REPORT_NAME)


def main() -> int:
    files = _iter_files()
    print(f"[verify_w0_language] scanning {len(files)} W0 artifact(s)...")

    findings: list[dict] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append({
                "file": str(f.relative_to(REPO_ROOT)),
                "kind": "READ_ERROR",
                "detail": str(exc),
            })
            continue
        hits = _scan_text(text)
        if hits:
            findings.append({
                "file": str(f.relative_to(REPO_ROOT)),
                "kind": "FORBIDDEN_LANGUAGE",
                "hits": hits,
            })

    legal = len(findings) == 0
    report = {
        "verifier": "verify_w0_language_discipline",
        "executed_at_utc": _now(),
        "rule": "W0_CLOSURE_LANGUAGE_DISCIPLINE",
        "status": "PASS" if legal else "FAIL_CLOSED",
        "expected_fail_reason": "" if legal else "FORBIDDEN_LANGUAGE_IN_W0_ARTIFACT",
        "actual_fail_reason": (
            "" if legal else f"{len(findings)} W0 artifact(s) contain forbidden runtime-certification language"
        ),
        "files_scanned": [str(f.relative_to(REPO_ROOT)) for f in files],
        "files_scanned_count": len(files),
        "findings": findings,
        "forbidden_pattern_count": len(FORBIDDEN_PATTERNS),
        "allowed_w0_phrases": [
            "verifier foundation PASS",
            "source-of-truth verifier PASS",
            "acceptance legality verifier PASS",
            "schema validation PASS",
            "PASS",
            "FAIL_CLOSED",
        ],
    }
    _write_json(LANGUAGE_REPORT, report)
    print(f"[verify_w0_language] {report['status']}: findings={len(findings)}")
    print(f"[verify_w0_language] wrote: {LANGUAGE_REPORT.relative_to(REPO_ROOT)}")
    return 0 if legal else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[verify_w0_language] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
