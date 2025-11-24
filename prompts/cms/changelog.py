from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from prompts.cms.schemas import PromptSchema


_BASE_DIR = Path(__file__).resolve().parent
_CHANGELOG_DIR = _BASE_DIR / "changelog"
_CHANGELOG_DIR.mkdir(parents=True, exist_ok=True)


def _changelog_path(prompt_id: str) -> Path:
    return _CHANGELOG_DIR / f"{prompt_id}.jsonl"


def record_change(prompt_id: str, version: str, user: str, diff: Dict[str, Any]) -> None:
    """Append a change record for a prompt/version.

    Stored as JSON Lines for easy ingestion.
    """

    entry = {
        "prompt_id": prompt_id,
        "version": version,
        "user": user,
        "diff": diff,
        "ts": datetime.utcnow().isoformat() + "Z",
    }
    path = _changelog_path(prompt_id)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def get_history(prompt_id: str) -> List[Dict[str, Any]]:
    path = _changelog_path(prompt_id)
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
    return entries


def record_prompt_change(prompt: PromptSchema, user: str, comment: str) -> None:
    diff: Dict[str, Any] = {
        "comment": comment,
        "schema": prompt.model_dump(),
    }
    record_change(prompt.id, prompt.version, user, diff)


def get_prompt_history(prompt_id: str) -> List[Dict[str, Any]]:
    return get_history(prompt_id)



