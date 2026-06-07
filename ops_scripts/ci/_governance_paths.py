"""SSOT path constants for governance CI gates.

Plan files, registration helpers, state, and artifact logs use Cursor-native
locations. Deprecated Windsurf compatibility copies are not write targets.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

CURSOR_PLANS_DIR = REPO_ROOT / ".claude" / "plans"
CURSOR_SCRIPTS_DIR = REPO_ROOT / ".claude" / "governance/scripts"
CURSOR_SCHEMAS_DIR = REPO_ROOT / ".claude" / "schemas"
CURSOR_STATE_DIR = REPO_ROOT / ".claude" / "state"
CURSOR_REFACTOR_DECISIONS_DIR = CURSOR_STATE_DIR / "refactor_decisions"

# Primary alias used by plan drift / registration gates
PLANS_DIR = CURSOR_PLANS_DIR

CURSOR_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "cursor"


def governance_artifact_log(name: str) -> Path:
    """Primary audit log path under ``artifacts/cursor/``."""
    path = CURSOR_ARTIFACTS_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def append_governance_artifact_jsonl(name: str, record: dict[str, Any]) -> Path:
    """Append one JSON line to the Cursor governance artifact log."""
    line = json.dumps(record, ensure_ascii=False) + "\n"
    primary = governance_artifact_log(name)
    with primary.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return primary


def read_governance_artifact_jsonl_paths(name: str) -> list[Path]:
    """Return existing Cursor governance artifact log paths."""
    p = CURSOR_ARTIFACTS_DIR / name
    return [p] if p.is_file() else []
