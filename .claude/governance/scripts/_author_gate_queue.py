#!/usr/bin/env python3
"""
_author_gate_queue.py — Author-Gate pending-packet queue helper (SSOT pure logic).

Shared by:
  - post_cursor_agent_ag_queue_drain_audit.py (post-hook audit)
  - pre_user_prompt_ag_queue_surface.py (pre-hook proactive surface)
  - post_cursor_agent_ag_queue_seed_capture.py (AG_QUEUE_SEED marker capture)
  - ops_scripts/ci/check_ag_queue_drain_freshness.py (weekly drift gate)

State file: .cursor/state/author_gate_queue/<plan-slug>.jsonl (append-only)

Each row shape::

    {
      "id": "W2.P4",
      "title": "apps_underwriting_ai draft->active",
      "depends_on": [],
      "status": "pending" | "answered",
      "recommended_option": "option-a",
      "score": 0.87,
      "gap": 0.15,
      "enqueued_at": "2026-05-03T10:00:00Z",
      "answered_at": null | "2026-05-03T11:00:00Z",
      "chosen": null | "option-a"
    }

Pure: no subprocess, no env reads, no logging side effects. Specific
exceptions only. All writes append-only; reads tolerate malformed rows
by skipping (corruption recovery). Constitutional tie-in: §35 (new).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / ".cursor" / "state" / "author_gate_queue"


def _state_path(plan_slug: str) -> Path:
    """Return the JSONL state file for ``plan_slug``."""
    # Defense-in-depth: refuse path traversal or separator characters.
    if "/" in plan_slug or "\\" in plan_slug or ".." in plan_slug:
        raise ValueError(f"invalid plan_slug: {plan_slug!r}")
    if not plan_slug:
        raise ValueError("plan_slug is empty")
    return STATE_DIR / f"{plan_slug}.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_all(plan_slug: str) -> list[dict[str, Any]]:
    """Read all rows, skipping malformed lines. Missing file → empty list."""
    path = _state_path(plan_slug)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    # Corrupt line — skip but do not fail
                    continue
                if isinstance(row, dict) and "id" in row:
                    rows.append(row)
    except OSError:
        return []
    return rows


def _write_all(plan_slug: str, rows: list[dict[str, Any]]) -> None:
    """Rewrite state file atomically from a full row list."""
    path = _state_path(plan_slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    tmp.replace(path)


def enqueue(plan_slug: str, packet: dict[str, Any]) -> None:
    """
    Idempotently enqueue a packet. Row identity = ``packet["id"]``.
    If a row with the same id already exists, this is a no-op.
    Required fields: id, title. Optional: depends_on, recommended_option,
    score, gap.
    """
    if "id" not in packet or not packet["id"]:
        raise ValueError("packet.id is required")
    if "title" not in packet or not packet["title"]:
        raise ValueError("packet.title is required")

    rows = _read_all(plan_slug)
    existing_ids = {r["id"] for r in rows}
    if packet["id"] in existing_ids:
        return

    row: dict[str, Any] = {
        "id": str(packet["id"]),
        "title": str(packet["title"]),
        "depends_on": list(packet.get("depends_on") or []),
        "status": "pending",
        "recommended_option": packet.get("recommended_option"),
        "score": packet.get("score"),
        "gap": packet.get("gap"),
        "enqueued_at": _now_iso(),
        "answered_at": None,
        "chosen": None,
    }
    rows.append(row)
    _write_all(plan_slug, rows)


def next_packet(plan_slug: str) -> dict[str, Any] | None:
    """
    Return the head-of-queue pending packet respecting depends_on topology.
    A packet is eligible iff all its depends_on IDs are ``answered`` (or
    absent from the queue entirely — treat missing deps as satisfied so a
    partially-seeded queue still drains).
    Ties broken by enqueue order (file order), then score descending.
    Returns None when queue is empty or no eligible packet exists.
    """
    rows = _read_all(plan_slug)
    if not rows:
        return None
    answered_ids = {r["id"] for r in rows if r.get("status") == "answered"}
    all_ids = {r["id"] for r in rows}

    eligible: list[dict[str, Any]] = []
    for r in rows:
        if r.get("status") != "pending":
            continue
        deps = r.get("depends_on") or []
        unmet = [d for d in deps if d in all_ids and d not in answered_ids]
        if unmet:
            continue
        eligible.append(r)

    if not eligible:
        return None
    # Stable order preserves enqueue sequence; secondary: score desc.
    eligible.sort(key=lambda r: (-(r.get("score") or 0.0),))
    return eligible[0]


def mark_answered(plan_slug: str, packet_id: str, chosen_option: str) -> None:
    """Mark a packet as answered and record the chosen option. No-op if not found."""
    rows = _read_all(plan_slug)
    changed = False
    for r in rows:
        if r["id"] == packet_id and r.get("status") == "pending":
            r["status"] = "answered"
            r["answered_at"] = _now_iso()
            r["chosen"] = str(chosen_option)
            changed = True
            break
    if changed:
        _write_all(plan_slug, rows)


def pending_count(plan_slug: str) -> int:
    """Return the number of pending packets for a plan."""
    rows = _read_all(plan_slug)
    return sum(1 for r in rows if r.get("status") == "pending")


def list_plans_with_pending() -> list[str]:
    """Return sorted list of plan slugs that have ≥1 pending packet."""
    if not STATE_DIR.exists():
        return []
    out: list[str] = []
    try:
        for p in STATE_DIR.iterdir():
            if p.suffix != ".jsonl":
                continue
            slug = p.stem
            try:
                if pending_count(slug) > 0:
                    out.append(slug)
            except (OSError, ValueError):
                continue
    except OSError:
        return []
    return sorted(out)
