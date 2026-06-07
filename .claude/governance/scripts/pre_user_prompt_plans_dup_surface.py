#!/usr/bin/env python3
"""pre_user_prompt_plans_dup_surface.py — surface unacknowledged Plans-DB
duplicate violations at the start of each Cursor Agent prompt.

When ``post_agent_plans_dup_audit.py`` detected a duplicate Plans-DB POST
in the previous response and logged it to
``artifacts/governance/notion_plans_dup_violations.jsonl``, this hook reads the
last entry and surfaces a PLANS_DUP_SURFACE line so the operator is informed
before acting on the next prompt.

The hook is purely advisory — it never exits non-zero.  Violations are
one-shot: once surfaced here, the log entry is not repeated.

DS-3 of notion-plans-db-hygiene-deferred-scope-d4f7c1.

Bypass: ``NOTION_PLANS_DUP_SURFACE_BYPASS=1``.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "governance" / "notion_plans_dup_violations.jsonl"
)
SURFACED_LOG = (
    REPO_ROOT / "artifacts" / "governance" / "notion_plans_dup_surfaced.jsonl"
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_violations() -> list[dict]:
    if not VIOLATIONS_LOG.exists():
        return []
    try:
        lines = VIOLATIONS_LOG.read_text(encoding="utf-8").splitlines()
        out = []
        for line in lines:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return out
    except OSError:
        return []


def _load_surfaced() -> set[str]:
    """Return set of already-surfaced violation fingerprints (timestamp+slug)."""
    if not SURFACED_LOG.exists():
        return set()
    try:
        lines = SURFACED_LOG.read_text(encoding="utf-8").splitlines()
        keys: set[str] = set()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                fp = rec.get("fingerprint", "")
                if fp:
                    keys.add(fp)
            except json.JSONDecodeError:
                pass
        return keys
    except OSError:
        return set()


def _append_surfaced(record: dict) -> None:
    try:
        SURFACED_LOG.parent.mkdir(parents=True, exist_ok=True)
        with SURFACED_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _fingerprint(v: dict) -> str:
    return f"{v.get('timestamp', '')}|{v.get('slug', '')}|{v.get('invoke_index', '')}"


def main() -> int:
    if os.environ.get("NOTION_PLANS_DUP_SURFACE_BYPASS") == "1":
        return 0

    violations = _load_violations()
    if not violations:
        return 0

    already_surfaced = _load_surfaced()

    new_violations = [
        v for v in violations
        if v.get("severity") == "error"
        and _fingerprint(v) not in already_surfaced
    ]

    if not new_violations:
        return 0

    for v in new_violations:
        slug = v.get("slug", "?")
        existing_page_id = v.get("existing_page_id", "?")
        ts = v.get("timestamp", "?")
        print(
            f"PLANS_DUP_SURFACE: slug={slug!r} existing_page_id={existing_page_id!r} "
            f"ts={ts} — a duplicate Plans-DB POST was detected in the previous "
            f"response. Use register_plan_idempotent() to avoid creating phantom rows. "
            f"Run tools/notion/triage_plans_duplicates.py --live to clean up."
        )
        fp = _fingerprint(v)
        _append_surfaced({
            "fingerprint": fp,
            "surfaced_at": _now_iso(),
            "slug": slug,
        })

    return 0


if __name__ == "__main__":
    sys.exit(main())
