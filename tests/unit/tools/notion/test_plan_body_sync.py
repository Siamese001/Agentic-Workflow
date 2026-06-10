"""Unit tests for tools/notion/plan_body_sync.py and the include_body seam in
tools/notion/plan_creation_helper.py.

Covers: markdown→Notion block conversion fidelity, rich_text chunking limits,
≤100-block append batching, sync modes (replace / append / skip_if_nonempty),
fail-closed token handling, and the opt-in (default-off) body upload during
plan registration.
"""
from __future__ import annotations

import json
import urllib.request

import pytest

from tools.notion import plan_body_sync as pbs
from tools.notion import plan_creation_helper as pch

# ---------------------------------------------------------------------------
# markdown_to_notion_blocks — pure conversion
# ---------------------------------------------------------------------------


class TestMarkdownToNotionBlocks:
    def test_frontmatter_becomes_yaml_code_block(self):
        md = "---\nplan_id: x-abc123\nplan_format: v2\n---\n\n# Title\n"
        blocks = pbs.markdown_to_notion_blocks(md)
        assert blocks[0]["type"] == "code"
        assert blocks[0]["code"]["language"] == "yaml"
        assert "plan_id: x-abc123" in blocks[0]["code"]["rich_text"][0]["text"]["content"]
        assert blocks[1]["type"] == "heading_1"

    def test_heading_levels(self):
        md = "# One\n## Two\n### Three\n#### Four\n"
        types = [b["type"] for b in pbs.markdown_to_notion_blocks(md)]
        assert types == ["heading_1", "heading_2", "heading_3", "heading_3"]

    def test_bullet_quote_divider_paragraph(self):
        md = "- item\n> quoted\n---\nplain line\n"
        blocks = pbs.markdown_to_notion_blocks(md)
        types = [b["type"] for b in blocks]
        assert types == ["bulleted_list_item", "quote", "divider", "paragraph"]
        assert blocks[0]["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "item"
        assert blocks[1]["quote"]["rich_text"][0]["text"]["content"] == "quoted"

    def test_consecutive_table_lines_become_one_markdown_code_block(self):
        md = "| a | b |\n|---|---|\n| 1 | 2 |\nafter\n"
        blocks = pbs.markdown_to_notion_blocks(md)
        assert blocks[0]["type"] == "code"
        assert blocks[0]["code"]["language"] == "markdown"
        body = blocks[0]["code"]["rich_text"][0]["text"]["content"]
        assert body.count("\n") == 2  # three table lines in one block
        assert blocks[1]["type"] == "paragraph"

    def test_fenced_code_language_whitelist(self):
        md = "```bash\necho hi\n```\n```weirdlang\nx\n```\n"
        blocks = pbs.markdown_to_notion_blocks(md)
        assert blocks[0]["code"]["language"] == "bash"
        assert blocks[1]["code"]["language"] == "plain text"

    def test_long_text_chunked_under_2000(self):
        md = "x" * 5000
        blocks = pbs.markdown_to_notion_blocks(md)
        assert len(blocks) == 1
        chunks = blocks[0]["paragraph"]["rich_text"]
        assert all(len(c["text"]["content"]) <= pbs.MAX_RICH_TEXT_CHARS for c in chunks)
        assert sum(len(c["text"]["content"]) for c in chunks) == 5000

    def test_blank_lines_skipped(self):
        assert pbs.markdown_to_notion_blocks("\n\n  \n") == []


# ---------------------------------------------------------------------------
# append_children — batching against a mocked Notion API
# ---------------------------------------------------------------------------


class _FakeResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


class TestAppendChildren:
    def test_batches_of_at_most_100(self, monkeypatch):
        calls: list[dict] = []

        def fake_urlopen(req, timeout=None):
            body = json.loads(req.data.decode("utf-8"))
            calls.append({"method": req.method, "url": req.full_url, "n": len(body["children"])})
            return _FakeResp({"results": [{}] * len(body["children"])})

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        blocks = [{"object": "block", "type": "divider", "divider": {}}] * 201
        appended = pbs.append_children("tok", "page-1", blocks)
        assert appended == 201
        assert [c["n"] for c in calls] == [100, 100, 1]
        assert all(c["method"] == "PATCH" and "page-1" in c["url"] for c in calls)


# ---------------------------------------------------------------------------
# sync_plan_body — modes and fail-closed guards
# ---------------------------------------------------------------------------


class TestSyncPlanBody:
    def test_missing_token_raises(self, monkeypatch):
        monkeypatch.setattr(pbs, "get_notion_bearer_token_or_none", lambda: None)
        with pytest.raises(pbs.PlanBodySyncError, match="NOTION_TOKEN"):
            pbs.sync_plan_body("page-1", "# x")

    def test_missing_page_id_raises(self):
        with pytest.raises(pbs.PlanBodySyncError, match="page_id"):
            pbs.sync_plan_body("", "# x", token="tok")

    def test_unknown_mode_raises(self):
        with pytest.raises(pbs.PlanBodySyncError, match="unknown sync mode"):
            pbs.sync_plan_body("page-1", "# x", token="tok", mode="upsert")

    def test_replace_clears_then_appends(self, monkeypatch):
        order: list[str] = []
        monkeypatch.setattr(pbs, "clear_page_children", lambda t, p: order.append("clear") or 2)
        monkeypatch.setattr(pbs, "append_children", lambda t, p, b: order.append("append") or len(b))
        appended = pbs.sync_plan_body("page-1", "# Title\nbody\n", token="tok", mode="replace")
        assert order == ["clear", "append"]
        assert appended == 2  # heading + paragraph

    def test_skip_if_nonempty_noop_when_body_exists(self, monkeypatch):
        monkeypatch.setattr(pbs, "page_body_is_empty", lambda t, p: False)
        monkeypatch.setattr(
            pbs, "append_children", lambda t, p, b: pytest.fail("must not append")
        )
        assert pbs.sync_plan_body("page-1", "# x", token="tok", mode="skip_if_nonempty") == 0

    def test_append_mode_does_not_clear(self, monkeypatch):
        monkeypatch.setattr(
            pbs, "clear_page_children", lambda t, p: pytest.fail("must not clear")
        )
        monkeypatch.setattr(pbs, "append_children", lambda t, p, b: len(b))
        assert pbs.sync_plan_body("page-1", "# x", token="tok", mode="append") == 1

    def test_empty_markdown_returns_zero(self, monkeypatch):
        monkeypatch.setattr(pbs, "clear_page_children", lambda t, p: 0)
        monkeypatch.setattr(
            pbs, "append_children", lambda t, p, b: pytest.fail("must not append")
        )
        assert pbs.sync_plan_body("page-1", "\n\n", token="tok", mode="replace") == 0


# ---------------------------------------------------------------------------
# create_plan_in_notion — include_body seam (default off, opt-in, fail-soft)
# ---------------------------------------------------------------------------


@pytest.fixture()
def _creation_env(monkeypatch):
    """Mock the Notion creation API + summary derivation for helper tests."""
    monkeypatch.setattr(pch, "_call_notion_api", lambda payload: {"id": "page-xyz"})
    monkeypatch.setattr(pch, "build_plan_notion_summary", lambda c: "derived summary")
    monkeypatch.setattr(pch, "build_plan_notion_ai_summary", lambda c: "derived ai summary")


class TestCreatePlanIncludeBody:
    PLAN_MD = "---\nplan_id: t-abc123\n---\n# T\nbody\n"

    def test_default_does_not_upload_body(self, monkeypatch, _creation_env):
        monkeypatch.setattr(
            pbs, "sync_plan_body", lambda *a, **k: pytest.fail("body sync must not run by default")
        )
        result = pch.create_plan_in_notion(
            slug="t-abc123", summary="s", ai_summary="a", plan_content=self.PLAN_MD
        )
        assert result.ok
        assert result.body_blocks_appended == 0

    def test_include_body_uploads_with_replace_mode(self, monkeypatch, _creation_env):
        seen: dict = {}

        def fake_sync(page_id, markdown, *, token=None, mode=None):
            seen.update(page_id=page_id, markdown=markdown, mode=mode)
            return 7

        monkeypatch.setattr(pbs, "sync_plan_body", fake_sync)
        result = pch.create_plan_in_notion(
            slug="t-abc123",
            summary="s",
            ai_summary="a",
            plan_content=self.PLAN_MD,
            include_body=True,
        )
        assert result.ok
        assert result.body_blocks_appended == 7
        assert seen["page_id"] == "page-xyz"
        assert seen["mode"] == "replace"
        assert seen["markdown"] == self.PLAN_MD

    def test_include_body_without_content_is_noop(self, monkeypatch, _creation_env):
        monkeypatch.setattr(
            pbs, "sync_plan_body", lambda *a, **k: pytest.fail("no plan_content → no body sync")
        )
        result = pch.create_plan_in_notion(
            slug="t-abc123", summary="s", ai_summary="a", include_body=True
        )
        assert result.ok
        assert result.body_blocks_appended == 0

    def test_body_sync_failure_is_fail_soft(self, monkeypatch, _creation_env):
        def boom(*a, **k):
            raise pbs.PlanBodySyncError("api down")

        monkeypatch.setattr(pbs, "sync_plan_body", boom)
        result = pch.create_plan_in_notion(
            slug="t-abc123",
            summary="s",
            ai_summary="a",
            plan_content=self.PLAN_MD,
            include_body=True,
        )
        assert result.ok  # registration must survive body-sync failure
        assert result.body_blocks_appended == 0
