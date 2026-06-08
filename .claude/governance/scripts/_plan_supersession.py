#!/usr/bin/env python3
"""
_plan_supersession.py — shared engine for plan-supersession auto-retire.

A plan declares the plans it replaces via a ``## Supersedes`` markdown table
(and/or a ``supersedes:`` frontmatter list). When such a declaration exists and
the named predecessor is still in a non-terminal Notion status, the predecessor
should be flipped to ``Retired`` with a dated Summary note AND an explanatory
Notion comment linking the successor.

This module is the single source of that behavior. Two callers consume it:

* ``post_agent_plan_supersession_retire.py`` — fail-soft post-agent hook,
  runs opportunistically after each agent response.
* ``ops_scripts/ci/check_plan_supersession_consistency.py`` — CI sweep gate,
  catches cross-session / cross-worktree misses the live hook cannot observe.

Design constraints:
* Fail-soft: every Notion call returns ``None`` on error; nothing raises into a
  hook turn. ``reconcile`` swallows per-item errors and records them.
* Idempotent: a predecessor already in a terminal status is skipped; a
  supersession comment is posted at most once (detected by a stable marker).
* Dry-run by default. ``execute=True`` performs writes.
* Network calls carry ``timeout=30`` (constitutional §0).

Bypass: ``PLAN_SUPERSESSION_RETIRE_BYPASS=1`` (honored by callers, not here).
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
PLAN_DIRS = [REPO_ROOT / "plans", REPO_ROOT / ".claude" / "plans"]
AUDIT_LOG = REPO_ROOT / "artifacts" / "governance" / "plan_supersession_audit.jsonl"

# Stable marker embedded in every auto-posted comment + Summary note so re-runs
# are idempotent and the provenance is greppable.
COMMENT_MARKER = "[supersession-auto-retire]"
SUMMARY_MARKER = "[supersession-auto-retire]"

_SCRIPTS_DIR = Path(__file__).resolve().parent
import sys  # noqa: E402

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    PLANS_DATA_SOURCE_ID,
)

try:
    from _notion_canonical import get_terminal_statuses  # noqa: E402
except ImportError:  # pragma: no cover - defensive fallback
    def get_terminal_statuses() -> set[str]:  # type: ignore[misc]
        return {"Completed", "Retired", "Archived"}


# ---------------------------------------------------------------------------
# Plan-file parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# A markdown H2 named "Supersedes" followed by content up to the next H2 / EOF.
_SUPERSEDES_SECTION_RE = re.compile(
    r"^##\s+Supersedes\s*$(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL
)
# Plan slugs are kebab-case (optionally with a -<6hex> suffix, but not required:
# e.g. apps-lic-redesign-refactor-plan-v2-consolidated has none).
_SLUG_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]{3,}")


def _slug_from_filename(path: Path) -> str:
    return path.stem


def parse_supersedes(text: str) -> list[str]:
    """Extract predecessor slugs from a plan body.

    Reads both the ``supersedes:`` frontmatter list and the ``## Supersedes``
    table. Returns a de-duplicated list of slug tokens (order preserved).
    A section whose only content is "None"/"N/A" yields an empty list.
    """
    found: list[str] = []

    fm = _FRONTMATTER_RE.match(text)
    if fm:
        block = fm.group(1)
        m = re.search(r"^supersedes:\s*(.+)$", block, re.MULTILINE)
        if m:
            raw = m.group(1).strip()
            # supersedes: [a-1abc12, b-2def34]  OR  supersedes: a-1abc12
            raw = raw.strip("[]")
            for tok in re.split(r"[,\s]+", raw):
                tok = tok.strip().strip("'\"")
                if _SLUG_TOKEN_RE.fullmatch(tok):
                    found.append(tok)

    sec = _SUPERSEDES_SECTION_RE.search(text)
    if sec:
        body = sec.group(1)
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            # Skip the header / separator rows.
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not cells:
                continue
            first = cells[0].lower()
            if first in {"predecessor slug", "predecessor", "slug", ""} or set(first) <= {"-", ":"}:
                continue
            # The first cell holds the predecessor slug (optionally as a markdown
            # link). Take the first kebab token — that is the slug / link text.
            matches = _SLUG_TOKEN_RE.findall(cells[0])
            if matches:
                found.append(matches[0])

    # De-dup, preserve order.
    seen: set[str] = set()
    out: list[str] = []
    for s in found:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def iter_plan_files() -> list[Path]:
    out: list[Path] = []
    for d in PLAN_DIRS:
        if d.is_dir():
            out.extend(sorted(d.glob("*.md")))
    return out


def discover_declarations() -> dict[str, list[str]]:
    """Map ``successor_slug -> [predecessor_slug, ...]`` across all plan files."""
    decls: dict[str, list[str]] = {}
    for path in iter_plan_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        preds = parse_supersedes(text)
        if preds:
            decls[_slug_from_filename(path)] = preds
    return decls


# ---------------------------------------------------------------------------
# Notion access (self-contained, fail-soft, timeout=30)
# ---------------------------------------------------------------------------

def load_token() -> str:
    return os.environ.get("NOTION_TOKEN", "").strip()


def _log(record: dict[str, Any]) -> None:
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        record.setdefault("ts", datetime.now(timezone.utc).isoformat())
        with AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def notion_request(
    method: str, path: str, token: str, body: Optional[dict] = None
) -> Optional[dict]:
    url = f"{NOTION_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            parsed: Any = json.loads(resp.read().decode("utf-8"))
            return parsed if isinstance(parsed, dict) else None
    except urllib.error.HTTPError as exc:
        _log(
            {
                "event": "notion_http_error",
                "method": method,
                "path": path,
                "status": exc.code,
                "body": exc.read().decode("utf-8", errors="replace")[:500],
            }
        )
        return None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        _log({"event": "notion_net_error", "method": method, "path": path, "error": str(exc)})
        return None


def find_plan_page(slug: str, token: str) -> Optional[dict]:
    """Look up a Plans-DB row by exact Slug (title). Returns the page dict or None."""
    body = {
        "filter": {"property": "Slug", "title": {"equals": slug}},
        "page_size": 1,
    }
    resp = notion_request("POST", f"/data_sources/{PLANS_DATA_SOURCE_ID}/query", token, body)
    if not resp:
        return None
    results = resp.get("results") or []
    for row in results:
        if isinstance(row, dict):
            return row
    return None


def page_status(page: dict) -> str:
    sel = (page.get("properties", {}).get("Status", {}) or {}).get("select") or {}
    return sel.get("name", "") or ""


def page_summary(page: dict) -> str:
    rt = (page.get("properties", {}).get("Summary", {}) or {}).get("rich_text") or []
    return "".join(t.get("plain_text", "") for t in rt)


def is_terminal(status: str) -> bool:
    return status in get_terminal_statuses()


def has_supersession_comment(page_id: str, token: str) -> bool:
    """True if a prior auto-retire comment (marker) already exists on the page."""
    resp = notion_request("GET", f"/comments?block_id={page_id}&page_size=100", token)
    if not resp:
        return False
    for c in resp.get("results", []) or []:
        for t in (c.get("rich_text") or []):
            if COMMENT_MARKER in (t.get("plain_text") or ""):
                return True
    return False


def build_reason(successor_slug: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (
        f"Retired {today} {SUMMARY_MARKER} — superseded by {successor_slug}, "
        f"which declares this plan in its ## Supersedes table."
    )


def retire_predecessor(
    page_id: str, successor_slug: str, token: str, existing_summary: str
) -> bool:
    """Patch Status->Retired and append a dated Summary note (idempotent append)."""
    reason = build_reason(successor_slug)
    if SUMMARY_MARKER in existing_summary:
        new_summary = existing_summary  # note already present; just ensure status
    else:
        joiner = "\n\n" if existing_summary.strip() else ""
        new_summary = (existing_summary + joiner + reason)[:2000]
    body = {
        "properties": {
            "Status": {"select": {"name": "Retired"}},
            "Summary": {"rich_text": [{"type": "text", "text": {"content": new_summary}}]},
        }
    }
    resp = notion_request("PATCH", f"/pages/{page_id}", token, body)
    return resp is not None


def post_supersession_comment(page_id: str, successor_slug: str, token: str) -> bool:
    reason = build_reason(successor_slug)
    body = {
        "parent": {"page_id": page_id},
        "rich_text": [{"type": "text", "text": {"content": reason}}],
    }
    resp = notion_request("POST", "/comments", token, body)
    return resp is not None


# ---------------------------------------------------------------------------
# Reconcile engine
# ---------------------------------------------------------------------------

@dataclass
class Action:
    successor: str
    predecessor: str
    outcome: str  # retired | commented | skipped_terminal | skipped_not_found | skipped_comment_exists | error | would_retire
    detail: str = ""


@dataclass
class ReconcileResult:
    actions: list[Action] = field(default_factory=list)
    token_present: bool = False

    @property
    def retired(self) -> list[Action]:
        return [a for a in self.actions if a.outcome in {"retired", "would_retire"}]

    @property
    def inconsistencies(self) -> list[Action]:
        """Predecessors that are declared-superseded but still non-terminal."""
        return [a for a in self.actions if a.outcome in {"retired", "would_retire", "error"}]


def reconcile(
    *,
    execute: bool,
    token: Optional[str] = None,
    declarations: Optional[dict[str, list[str]]] = None,
    request_fn: Optional[Callable[..., Optional[dict]]] = None,
) -> ReconcileResult:
    """Core engine. For each declared (successor -> predecessor), retire the
    predecessor if it is non-terminal.

    ``request_fn`` is injectable for tests; defaults to the module ``notion_request``.
    With ``execute=False`` no writes occur — non-terminal predecessors are
    recorded as ``would_retire`` so the sweep gate can flag them.
    """
    global notion_request  # allow test injection via request_fn without monkeypatch
    req = request_fn or notion_request
    tok = token if token is not None else load_token()
    decls = declarations if declarations is not None else discover_declarations()
    result = ReconcileResult(token_present=bool(tok))

    if not tok:
        # Cannot read Notion; record declarations as unverifiable.
        for succ, preds in decls.items():
            for p in preds:
                result.actions.append(Action(succ, p, "error", "NOTION_TOKEN not set"))
        return result

    # Bind the injected request_fn into the module helpers for this call.
    saved = notion_request
    notion_request = req  # type: ignore[assignment]
    try:
        for succ, preds in decls.items():
            for pred in preds:
                page = find_plan_page(pred, tok)
                if page is None:
                    result.actions.append(Action(succ, pred, "skipped_not_found"))
                    continue
                status = page_status(page)
                if is_terminal(status):
                    result.actions.append(
                        Action(succ, pred, "skipped_terminal", f"status={status}")
                    )
                    continue
                page_id = page.get("id", "")
                if not execute:
                    result.actions.append(
                        Action(succ, pred, "would_retire", f"status={status}")
                    )
                    continue
                ok = retire_predecessor(page_id, succ, tok, page_summary(page))
                if not ok:
                    result.actions.append(Action(succ, pred, "error", "patch_failed"))
                    continue
                if has_supersession_comment(page_id, tok):
                    result.actions.append(
                        Action(succ, pred, "retired", "comment_exists")
                    )
                else:
                    posted = post_supersession_comment(page_id, succ, tok)
                    result.actions.append(
                        Action(succ, pred, "retired", "comment_posted" if posted else "comment_failed")
                    )
                _log(
                    {
                        "event": "supersession_retire",
                        "successor": succ,
                        "predecessor": pred,
                        "page_id": page_id,
                        "prior_status": status,
                    }
                )
    finally:
        notion_request = saved  # type: ignore[assignment]

    return result
