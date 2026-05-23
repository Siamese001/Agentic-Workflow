"""SSOT path constants for governance CI gates (Cursor-primary).

Windsurf mirror paths remain for hooks/MCP constitutional gates only.
Plan files and registration helpers use ``.cursor/`` per governance two-tier closeout.

Artifact logs: primary write ``artifacts/cursor/``; dual-write mirror to
``artifacts/windsurf/`` during namespace transition (W5.D4).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

CURSOR_PLANS_DIR = REPO_ROOT / ".cursor" / "plans"
CURSOR_SCRIPTS_DIR = REPO_ROOT / ".cursor" / "scripts"
CURSOR_SCHEMAS_DIR = REPO_ROOT / ".cursor" / "schemas"
CURSOR_STATE_DIR = REPO_ROOT / ".cursor" / "state"
CURSOR_REFACTOR_DECISIONS_DIR = CURSOR_STATE_DIR / "refactor_decisions"

# Primary alias used by plan drift / registration gates
PLANS_DIR = CURSOR_PLANS_DIR

# Legacy artifact namespace (dual-write target during transition)
WINDSURF_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "windsurf"
CURSOR_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "cursor"


def governance_artifact_log(name: str) -> Path:
    """Primary audit log path under ``artifacts/cursor/``."""
    path = CURSOR_ARTIFACTS_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def append_governance_artifact_jsonl(name: str, record: dict[str, Any]) -> Path:
    """Append one JSON line to cursor SSOT and windsurf mirror."""
    line = json.dumps(record, ensure_ascii=False) + "\n"
    primary = governance_artifact_log(name)
    legacy = WINDSURF_ARTIFACTS_DIR / name
    legacy.parent.mkdir(parents=True, exist_ok=True)
    for path in (primary, legacy):
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line)
    return primary


def read_governance_artifact_jsonl_paths(name: str) -> list[Path]:
    """Return existing log paths (cursor first, then windsurf) for dual-read."""
    out: list[Path] = []
    for base in (CURSOR_ARTIFACTS_DIR, WINDSURF_ARTIFACTS_DIR):
        p = base / name
        if p.is_file():
            out.append(p)
    return out
