#!/usr/bin/env python3
"""
pre_read_gate.py — Cursor pre_read_code hard gate.

Reads JSON payload from stdin. Payload fields:
  tool_info.file_path        — path Cursor Agent is about to read

Behavior (FAIL-CLOSED on explicit violations, FAIL-OPEN on parse errors):
  - Block reads of paths outside the repo root (with narrow exceptions for
    docs/cursor mirror, Cursor home config, user tmp screenshots).
  - Block reads of sensitive filenames (.env, id_rsa, credentials*, etc.)
    and sensitive suffixes (.pem, .key, .kdbx, etc.), with .env.example
    / .env.template / .env.sample whitelisted.
  - Append every block decision to artifacts/governance/secret_scan.jsonl
    for audit and later baseline tuning.

FAIL POLICY: closed for explicit sensitivity hits; open for malformed
payloads (matches pre_write_gate.py conventions).

CONSTITUTIONAL:
  - No PowerShell, no shell=True
  - Specific exceptions (OSError, json.JSONDecodeError, ValueError)
  - UTF-8 explicit on all file I/O
  - Bounded logging (truncate fields to 500 chars per record)

Zero hardcoded paths outside the repo root — REPO_ROOT derived from __file__.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _secret_patterns import is_sensitive_path  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = REPO_ROOT / "artifacts" / "governance"
AUDIT_LOG = AUDIT_DIR / "secret_scan.jsonl"

# Paths outside the repo that are explicitly allowed for read
# (documented Cursor conventions — see docs/cursor/*.md and agent screenshots)
_ALLOWED_OUTSIDE_REPO = (
    # Cursor docs mirror and cache
    "docs/cursor",
    # User screenshot temp paths — documented behavior in Cursor Agent
    "/Temp/TemporaryItems/",
    "\\Temp\\TemporaryItems\\",
    "/var/folders/",
    # Cursor user-home config (read-only probes)
    ".cursor/cursor/",
    "\\.cursor\\cursor\\",
)

# Paths outside the repo that are explicitly forbidden even if matched above
_ALWAYS_FORBIDDEN = (
    "C:/Users",
    "C:\\Users",
)

_MAX_FIELD_LEN = 500


def _append_audit(record: dict) -> None:
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log append: non-fatal, fail-open
        pass


def _truncate(value: str) -> str:
    if not isinstance(value, str):
        return ""
    return value if len(value) <= _MAX_FIELD_LEN else value[:_MAX_FIELD_LEN] + "…"


def _normalize(path: str) -> str:
    if not path:
        return ""
    # Prefer forward slashes for comparison
    return path.replace("\\", "/")


def _is_inside_repo(path: str) -> bool:
    if not path:
        return False
    try:
        abs_path = Path(path).resolve()
        abs_path.relative_to(REPO_ROOT)
        return True
    except (OSError, ValueError):
        return False


def _is_allowed_outside_repo(path: str) -> bool:
    """True if path matches any documented outside-repo allowlist pattern."""
    if not path:
        return False
    norm = _normalize(path)

    # Always-forbidden wins over allowlist (except our own repo root)
    repo_norm = _normalize(str(REPO_ROOT))
    for forbid in _ALWAYS_FORBIDDEN:
        if norm.startswith(_normalize(forbid)) and not norm.startswith(repo_norm):
            return False

    for pattern in _ALLOWED_OUTSIDE_REPO:
        if _normalize(pattern) in norm:
            return True
    return False


def _exit_block(reason: str, detail: dict) -> int:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "action": "pre_read_code",
        "decision": "block",
        "reason": reason,
        **{k: _truncate(str(v)) for k, v in detail.items()},
    }
    _append_audit(record)
    print(f"[pre_read_gate] BLOCKED: {reason} — {detail.get('file_path', '')}", file=sys.stderr)
    return 2


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
    # NOTE: we do NOT log every allowed read (too noisy). Only blocks are logged.
    raw = sys.stdin.read()
    if not raw.strip():
        # No payload — not enough info to decide; fail-open
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return 0

    file_path = tool_info.get("file_path", "")
    if not isinstance(file_path, str):
        return 0

    # Empty path → nothing to check
    if not file_path.strip():
        return 0

    # 1. Sensitivity check FIRST — applies regardless of path location
    sensitivity_reason = is_sensitive_path(file_path)
    if sensitivity_reason:
        return _exit_block(
            reason=sensitivity_reason,
            detail={"file_path": file_path, "category": "sensitive_filename_or_suffix"},
        )

    # 2. Path scoping — must be inside repo OR match allowlist
    if not _is_inside_repo(file_path) and not _is_allowed_outside_repo(file_path):
        return _exit_block(
            reason="read outside repo root + no allowlist match",
            detail={"file_path": file_path, "repo_root": str(REPO_ROOT), "category": "out_of_scope"},
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
