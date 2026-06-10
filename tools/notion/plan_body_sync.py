"""plan_body_sync.py — markdown → Notion page-body block sync for Plans DB pages.

Closes the gap where `create_plan_in_notion` registered the Plans DB ROW (properties:
Slug, Status, Plan File Path, Summary, AI Summary) but never uploaded the plan markdown
as page CONTENT — every registered plan page rendered empty.

Conversion contract (mirrors the manual backfill of page 37b27693-f55c-818a-88aa-fefd4cb49856,
2026-06-10, 201 blocks from 32KB markdown):

* leading YAML frontmatter        → one ``yaml`` code block
* ``#`` / ``##`` / ``###`` / ``####`` → heading_1 / heading_2 / heading_3 / heading_3
* fenced ``` blocks               → code blocks (language whitelisted, else "plain text")
* consecutive ``|`` table lines   → one ``markdown`` code block (preserves column alignment;
  Notion's native table block needs per-cell construction — fidelity over styling)
* leading ``- `` / ``* ``         → bulleted_list_item
* leading ``> ``                  → quote
* bare ``---``                    → divider
* everything else                 → paragraph (blank lines skipped)

Notion API limits honored: ≤2000 chars per rich_text element (we chunk at 1900),
≤100 children per append call (`MAX_BLOCKS_PER_APPEND`).

Governance note (`.claude/rules/memory-notion-writeback.md`: "row should link, not
repeat"): the disk plan file stays the SSOT. Body upload is therefore OPT-IN —
`create_plan_in_notion(include_body=True)` / `NOTION_PLAN_BODY_SYNC=1` for the
file-driven hook path — and `sync_plan_body(mode="replace")` is idempotent so the
Notion copy mirrors (never forks) the disk content.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none

_NOTION_BASE = "https://api.notion.com/v1"
_NOTION_API_VERSION = "2025-09-03"
_NOTION_TIMEOUT_S = 60

MAX_RICH_TEXT_CHARS = 1900  # Notion hard cap is 2000/element; headroom for safety
MAX_BLOCKS_PER_APPEND = 100  # Notion hard cap per PATCH /blocks/{id}/children

# Notion-accepted language ids we emit; anything else maps to "plain text".
_CODE_LANGUAGES = frozenset(
    {"bash", "shell", "python", "yaml", "json", "markdown", "sql", "plain text"}
)

SYNC_MODES = ("replace", "append", "skip_if_nonempty")


class PlanBodySyncError(Exception):
    """Raised when the Notion body sync cannot proceed (missing token / API error)."""


# ---------------------------------------------------------------------------
# Pure markdown → blocks conversion
# ---------------------------------------------------------------------------


def _rich_text(text: str) -> list[dict[str, Any]]:
    """Rich-text array, split into ≤MAX_RICH_TEXT_CHARS chunks (Notion caps 2000/element)."""
    chunks = [text[i : i + MAX_RICH_TEXT_CHARS] for i in range(0, len(text), MAX_RICH_TEXT_CHARS)] or [""]
    return [{"type": "text", "text": {"content": c}} for c in chunks]


def _code_blocks(text: str, language: str = "markdown") -> list[dict[str, Any]]:
    """Code block(s) for ``text``; bodies are split so no block exceeds rich_text limits."""
    if language not in _CODE_LANGUAGES:
        language = "plain text"
    blocks: list[dict[str, Any]] = []
    step = MAX_RICH_TEXT_CHARS * 40  # stay well under the 100 rich_text elements/block cap
    for i in range(0, max(len(text), 1), step):
        blocks.append(
            {
                "object": "block",
                "type": "code",
                "code": {"rich_text": _rich_text(text[i : i + step]), "language": language},
            }
        )
    return blocks


def markdown_to_notion_blocks(md: str) -> list[dict[str, Any]]:
    """Convert plan markdown to a list of Notion block objects (pure; no I/O)."""
    lines = md.splitlines()
    blocks: list[dict[str, Any]] = []
    i = 0
    n = len(lines)

    # Leading YAML frontmatter → one yaml code block.
    if lines and lines[0].strip() == "---":
        j = 1
        while j < n and lines[j].strip() != "---":
            j += 1
        if j < n:
            blocks += _code_blocks("\n".join(lines[0 : j + 1]), "yaml")
            i = j + 1

    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            lang = s[3:].strip() or "plain text"
            j = i + 1
            buf: list[str] = []
            while j < n and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            blocks += _code_blocks("\n".join(buf), lang)
            i = j + 1
            continue
        if s.startswith("|"):
            j = i
            buf = []
            while j < n and lines[j].strip().startswith("|"):
                buf.append(lines[j])
                j += 1
            blocks += _code_blocks("\n".join(buf), "markdown")
            i = j
            continue
        if s == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue
        for prefix, btype in (("# ", "heading_1"), ("## ", "heading_2"), ("### ", "heading_3")):
            if s.startswith(prefix):
                blocks.append(
                    {"object": "block", "type": btype, btype: {"rich_text": _rich_text(s[len(prefix):])}}
                )
                break
        else:
            if s.startswith("#### "):
                blocks.append(
                    {"object": "block", "type": "heading_3", "heading_3": {"rich_text": _rich_text(s[5:])}}
                )
            elif s.startswith(("- ", "* ")):
                blocks.append(
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {"rich_text": _rich_text(s[2:])},
                    }
                )
            elif s.startswith("> "):
                blocks.append({"object": "block", "type": "quote", "quote": {"rich_text": _rich_text(s[2:])}})
            else:
                blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": _rich_text(line)}})
        i += 1
    return blocks


# ---------------------------------------------------------------------------
# Notion HTTP surface (urllib, same style as plan_creation_helper)
# ---------------------------------------------------------------------------


def _http(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": _NOTION_API_VERSION,
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=_NOTION_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        raise PlanBodySyncError(f"Notion API HTTP {exc.code}: {exc.read().decode('utf-8')[:500]}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise PlanBodySyncError(f"Notion API connection error: {exc}")


def append_children(token: str, page_id: str, blocks: list[dict[str, Any]]) -> int:
    """Append blocks in ≤MAX_BLOCKS_PER_APPEND batches. Returns count appended."""
    appended = 0
    for i in range(0, len(blocks), MAX_BLOCKS_PER_APPEND):
        out = _http(
            "PATCH",
            f"{_NOTION_BASE}/blocks/{page_id}/children",
            token,
            {"children": blocks[i : i + MAX_BLOCKS_PER_APPEND]},
        )
        appended += len(out.get("results", []))
    return appended


def _list_child_block_ids(token: str, page_id: str) -> list[str]:
    ids: list[str] = []
    cursor: str | None = None
    while True:
        url = f"{_NOTION_BASE}/blocks/{page_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        out = _http("GET", url, token)
        ids += [b["id"] for b in out.get("results", []) if b.get("id")]
        if not out.get("has_more"):
            return ids
        cursor = out.get("next_cursor")


def page_body_is_empty(token: str, page_id: str) -> bool:
    out = _http("GET", f"{_NOTION_BASE}/blocks/{page_id}/children?page_size=1", token)
    return not out.get("results")


def clear_page_children(token: str, page_id: str) -> int:
    """Delete all existing child blocks (idempotent replace support). Returns count deleted."""
    ids = _list_child_block_ids(token, page_id)
    for block_id in ids:
        _http("DELETE", f"{_NOTION_BASE}/blocks/{block_id}", token)
    return len(ids)


def sync_plan_body(
    page_id: str,
    markdown: str,
    *,
    token: str | None = None,
    mode: str = "replace",
) -> int:
    """Upload plan markdown as the Notion page body. Returns blocks appended.

    Modes:
    * ``replace``          — clear existing children, then append (idempotent; default)
    * ``append``           — append after any existing children
    * ``skip_if_nonempty`` — no-op (returns 0) when the page already has a body

    Raises PlanBodySyncError on missing token/page_id, unknown mode, or API failure.
    Callers on fail-soft paths (hooks, registration) must wrap this.
    """
    if mode not in SYNC_MODES:
        raise PlanBodySyncError(f"unknown sync mode '{mode}' (expected one of {SYNC_MODES})")
    if not page_id:
        raise PlanBodySyncError("page_id required")
    resolved = token or get_notion_bearer_token_or_none()
    if not resolved:
        raise PlanBodySyncError("NOTION_TOKEN unavailable")

    if mode == "skip_if_nonempty" and not page_body_is_empty(resolved, page_id):
        return 0
    if mode == "replace":
        clear_page_children(resolved, page_id)

    blocks = markdown_to_notion_blocks(markdown)
    if not blocks:
        return 0
    appended = append_children(resolved, page_id, blocks)
    print(
        f"[plan-body-sync] page_id={page_id} mode={mode} blocks={appended}",
        file=sys.stderr,
    )
    return appended


__all__ = [
    "MAX_BLOCKS_PER_APPEND",
    "MAX_RICH_TEXT_CHARS",
    "PlanBodySyncError",
    "SYNC_MODES",
    "append_children",
    "clear_page_children",
    "markdown_to_notion_blocks",
    "page_body_is_empty",
    "sync_plan_body",
]
