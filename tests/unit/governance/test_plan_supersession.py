"""Unit tests for _plan_supersession — parsing + reconcile engine (mocked Notion)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / ".claude" / "governance" / "scripts"


def _load_module():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import _plan_supersession  # noqa: E402  (sys.path primed above)

    return _plan_supersession


mod = _load_module()


# ---------------------------------------------------------------------------
# Fake Notion client
# ---------------------------------------------------------------------------

class FakeNotion:
    def __init__(self, pages: dict[str, dict], comments: dict[str, list] | None = None):
        # pages keyed by slug
        self.pages = pages
        self.comments = comments or {}
        self.calls: list[tuple[str, str, dict | None]] = []

    def __call__(self, method, path, token, body=None):
        self.calls.append((method, path, body))
        if method == "POST" and "/data_sources/" in path and path.endswith("/query"):
            slug = body["filter"]["title"]["equals"]
            pg = self.pages.get(slug)
            return {"results": [pg] if pg else []}
        if method == "PATCH" and path.startswith("/pages/"):
            pid = path.split("/pages/")[1]
            for pg in self.pages.values():
                if pg.get("id") == pid:
                    props = body["properties"]
                    pg["properties"]["Status"] = props["Status"]
                    pg["properties"]["Summary"] = props["Summary"]
            return {"object": "page", "id": pid}
        if method == "GET" and path.startswith("/comments"):
            pid = path.split("block_id=")[1].split("&")[0]
            return {"results": self.comments.get(pid, [])}
        if method == "POST" and path == "/comments":
            pid = body["parent"]["page_id"]
            self.comments.setdefault(pid, []).append({"rich_text": body["rich_text"]})
            return {"object": "comment", "id": "c1"}
        return None


def _page(slug, status, summary="", pid=None):
    return {
        "id": pid or f"pid-{slug}",
        "properties": {
            "Slug": {"title": [{"plain_text": slug}]},
            "Status": {"select": {"name": status}},
            "Summary": {"rich_text": [{"plain_text": summary}] if summary else []},
        },
    }


# ---------------------------------------------------------------------------
# parse_supersedes
# ---------------------------------------------------------------------------

def test_parse_frontmatter_list():
    text = "---\nslug: x\nsupersedes: [foo-1abc12, bar-2def34]\n---\n# body\n"
    assert mod.parse_supersedes(text) == ["foo-1abc12", "bar-2def34"]


def test_parse_supersedes_table():
    text = (
        "# Plan\n\n## Supersedes\n"
        "| Predecessor slug | Reason |\n|---|---|\n"
        "| apps-lic-redesign-37927693 | implemented elsewhere |\n\n"
        "## Next\n"
    )
    assert mod.parse_supersedes(text) == ["apps-lic-redesign-37927693"]


def test_parse_none_section_is_empty():
    text = "# Plan\n\n## Supersedes\n\n_None — net-new plan._\n"
    assert mod.parse_supersedes(text) == []


def test_parse_dedup_across_sources():
    text = "---\nsupersedes: foo-1abc12\n---\n## Supersedes\n| Predecessor slug |\n|---|\n| foo-1abc12 |\n"
    assert mod.parse_supersedes(text) == ["foo-1abc12"]


def test_parse_ignores_fenced_example():
    # A fenced EXAMPLE table naming a real slug must not be treated as a
    # declaration when the actual ## Supersedes section says net-new.
    text = (
        "---\nsupersedes: []\n---\n# Plan\n\n"
        "> Grammar:\n"
        "```markdown\n## Supersedes\n| Predecessor slug | Reason |\n|---|---|\n"
        "| apps-lic-redesign-refactor-plan-v2-consolidated | x |\n```\n\n"
        "## Supersedes\n\n_None — net-new plan._\n"
    )
    assert mod.parse_supersedes(text) == []


def test_parse_real_section_outside_fence_still_found():
    text = (
        "Example:\n```\n## Supersedes\n| ghost-000000 |\n```\n\n"
        "## Supersedes\n| Predecessor slug |\n|---|\n| real-1abc12 |\n"
    )
    assert mod.parse_supersedes(text) == ["real-1abc12"]


# ---------------------------------------------------------------------------
# reconcile
# ---------------------------------------------------------------------------

def test_dry_run_flags_would_retire():
    fake = FakeNotion({"pred-aaaaaa": _page("pred-aaaaaa", "In Progress")})
    res = mod.reconcile(
        execute=False, token="t", declarations={"succ-bbbbbb": ["pred-aaaaaa"]}, request_fn=fake
    )
    assert [a.outcome for a in res.actions] == ["would_retire"]
    # No PATCH in dry-run.
    assert not any(m == "PATCH" for m, _p, _b in fake.calls)


def test_execute_retires_and_comments():
    fake = FakeNotion({"pred-aaaaaa": _page("pred-aaaaaa", "In Progress", "old summary")})
    res = mod.reconcile(
        execute=True, token="t", declarations={"succ-bbbbbb": ["pred-aaaaaa"]}, request_fn=fake
    )
    assert [a.outcome for a in res.actions] == ["retired"]
    pg = fake.pages["pred-aaaaaa"]
    assert pg["properties"]["Status"]["select"]["name"] == "Retired"
    summary = pg["properties"]["Summary"]["rich_text"][0]["text"]["content"]
    assert "old summary" in summary and "succ-bbbbbb" in summary and mod.SUMMARY_MARKER in summary
    # A comment was posted carrying the marker.
    posted = fake.comments["pid-pred-aaaaaa"][0]["rich_text"][0]["text"]["content"]
    assert mod.COMMENT_MARKER in posted


def test_skip_terminal_predecessor():
    fake = FakeNotion({"pred-aaaaaa": _page("pred-aaaaaa", "Retired")})
    res = mod.reconcile(
        execute=True, token="t", declarations={"succ-bbbbbb": ["pred-aaaaaa"]}, request_fn=fake
    )
    assert res.actions[0].outcome == "skipped_terminal"
    assert not any(m == "PATCH" for m, _p, _b in fake.calls)


def test_skip_not_found():
    fake = FakeNotion({})
    res = mod.reconcile(
        execute=True, token="t", declarations={"succ-bbbbbb": ["ghost-999999"]}, request_fn=fake
    )
    assert res.actions[0].outcome == "skipped_not_found"


def test_no_token_records_error():
    res = mod.reconcile(execute=True, token="", declarations={"s-aaaaaa": ["p-bbbbbb"]})
    assert res.token_present is False
    assert res.actions[0].outcome == "error"


def test_comment_idempotent_when_marker_present():
    fake = FakeNotion(
        {"pred-aaaaaa": _page("pred-aaaaaa", "In Progress")},
        comments={"pid-pred-aaaaaa": [{"rich_text": [{"plain_text": mod.COMMENT_MARKER + " prior"}]}]},
    )
    res = mod.reconcile(
        execute=True, token="t", declarations={"succ-bbbbbb": ["pred-aaaaaa"]}, request_fn=fake
    )
    assert res.actions[0].outcome == "retired"
    assert res.actions[0].detail == "comment_exists"
    # Only the pre-existing comment remains; no duplicate POST /comments.
    assert len(fake.comments["pid-pred-aaaaaa"]) == 1
    assert not any(m == "POST" and p == "/comments" for m, p, _b in fake.calls)


def test_retire_preserves_long_summary():
    # Existing Summary well over the 2000-char per-segment cap must survive,
    # with the retire note appended (nothing dropped, nothing overwritten away).
    long_existing = "X" * 2500
    fake = FakeNotion({"pred-aaaaaa": _page("pred-aaaaaa", "In Progress", long_existing)})
    res = mod.reconcile(
        execute=True, token="t", declarations={"succ-bbbbbb": ["pred-aaaaaa"]}, request_fn=fake
    )
    assert res.actions[0].outcome == "retired"
    chunks = fake.pages["pred-aaaaaa"]["properties"]["Summary"]["rich_text"]
    combined = "".join(c["text"]["content"] for c in chunks)
    assert combined.count("X") == 2500  # original content fully preserved
    assert mod.SUMMARY_MARKER in combined and "succ-bbbbbb" in combined
    assert all(len(c["text"]["content"]) <= 2000 for c in chunks)  # within Notion cap


def test_retire_payload_shape():
    fake = FakeNotion({"pred-aaaaaa": _page("pred-aaaaaa", "In Progress")})
    mod.reconcile(
        execute=True, token="t", declarations={"succ-bbbbbb": ["pred-aaaaaa"]}, request_fn=fake
    )
    patch = next(b for m, p, b in fake.calls if m == "PATCH")
    assert patch["properties"]["Status"]["select"]["name"] == "Retired"
    assert "rich_text" in patch["properties"]["Summary"]
