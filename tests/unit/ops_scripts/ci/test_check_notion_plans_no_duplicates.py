"""
Unit tests for ops_scripts/ci/check_notion_plans_no_duplicates.py.

Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2d).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_notion_plans_no_duplicates.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_notion_plans_no_duplicates", MODULE_PATH
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_notion_plans_no_duplicates"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


def _write_cache(tmp_path: Path, plans: dict) -> Path:
    cache = tmp_path / "plan_registration_cache.json"
    cache.write_text(json.dumps({
        "fetched_at": "2026-05-10T12:00:00Z",
        "fetched_at_epoch": 1.0,
        "plans": plans,
    }), encoding="utf-8")
    return cache


def test_load_cache_clean_returns_singletons(mod, tmp_path, monkeypatch):
    cache = _write_cache(tmp_path, {
        "plan-a-aaaaaa": {"page_id": "p1", "status": "Completed"},
        "plan-b-bbbbbb": {"page_id": "p2", "status": "In Progress"},
    })
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    snapshot = mod.load_cache_snapshot()
    assert snapshot is not None
    assert all(len(rows) == 1 for rows in snapshot.values())


def test_load_cache_missing_returns_none(mod, tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", tmp_path / "absent.json")
    assert mod.load_cache_snapshot() is None


def test_load_cache_malformed_returns_none(mod, tmp_path, monkeypatch):
    cache = tmp_path / "bad.json"
    cache.write_text("not json", encoding="utf-8")
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    assert mod.load_cache_snapshot() is None


def test_main_clean_cache_exits_zero(mod, tmp_path, monkeypatch, capsys):
    cache = _write_cache(tmp_path, {
        "plan-a-aaaaaa": {"page_id": "p1", "status": "Completed"},
    })
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    rc = mod.main([])
    assert rc == 0
    assert "OK" in capsys.readouterr().out


def test_main_missing_cache_exits_two(mod, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mod, "CACHE_PATH", tmp_path / "absent.json")
    rc = mod.main([])
    assert rc == 2
    err = capsys.readouterr().err
    assert "cache missing" in err


def test_main_bypass_env_passes(mod, monkeypatch, capsys):
    monkeypatch.setenv("NOTION_PLANS_DUP_BYPASS", "1")
    rc = mod.main([])
    assert rc == 0
    assert "BYPASS" in capsys.readouterr().out.upper()


def test_main_with_synthetic_duplicates_via_live_mock(mod, monkeypatch, capsys):
    """Force --live with mocked fetcher to verify duplicate-fail path."""
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setattr(
        mod, "fetch_live_plans",
        lambda token: {
            "twin-plan-aaaaaa": [
                {"id": "p1", "status": "In Progress"},
                {"id": "p2", "status": "Not Started"},
            ],
            "lonely-plan-bbbbbb": [{"id": "p3", "status": "Completed"}],
        },
    )
    rc = mod.main(["--live"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "twin-plan-aaaaaa" in out
    assert "p1" in out
    assert "p2" in out


def test_main_json_output(mod, monkeypatch, capsys):
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setattr(
        mod, "fetch_live_plans",
        lambda token: {"twin-aaaaaa": [{"id": "p1"}, {"id": "p2"}]},
    )
    rc = mod.main(["--live", "--json"])
    assert rc == 1
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert payload["duplicate_count"] == 1
    assert payload["duplicates"][0]["slug"] == "twin-aaaaaa"


def test_main_live_no_token_exits_two(mod, monkeypatch, capsys):
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    rc = mod.main(["--live"])
    assert rc == 2
    assert "requires NOTION_TOKEN" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Gap-filling tests
# ---------------------------------------------------------------------------

def test_load_cache_empty_plans_returns_empty_dict(mod, tmp_path, monkeypatch):
    """Cache with zero plans is valid — no duplicates found."""
    cache = _write_cache(tmp_path, {})
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    snapshot = mod.load_cache_snapshot()
    assert snapshot == {}


def test_main_empty_plans_cache_exits_zero(mod, tmp_path, monkeypatch, capsys):
    """Empty plans dict → OK, exits 0."""
    cache = _write_cache(tmp_path, {})
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    rc = mod.main([])
    assert rc == 0
    assert "OK" in capsys.readouterr().out


def test_main_json_output_clean_cache(mod, tmp_path, monkeypatch, capsys):
    """--json with no duplicates emits zero duplicate_count."""
    cache = _write_cache(tmp_path, {
        "solo-plan-aaaaaa": {"page_id": "p1", "status": "In Progress"},
    })
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    rc = mod.main(["--json"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["duplicate_count"] == 0
    assert payload["duplicates"] == []


def test_main_live_no_duplicates_exits_zero(mod, monkeypatch, capsys):
    """--live with all singletons → exits 0."""
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setattr(
        mod, "fetch_live_plans",
        lambda token: {
            "plan-a-aaaaaa": [{"id": "p1", "status": "In Progress"}],
            "plan-b-bbbbbb": [{"id": "p2", "status": "Completed"}],
        },
    )
    rc = mod.main(["--live"])
    assert rc == 0
    assert "OK" in capsys.readouterr().out


def test_main_live_empty_fetch_exits_zero(mod, monkeypatch, capsys):
    """--live returning empty dict → exits 0, no error."""
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setattr(mod, "fetch_live_plans", lambda token: {})
    rc = mod.main(["--live"])
    assert rc == 0


def test_main_live_json_output_multiple_duplicates(mod, monkeypatch, capsys):
    """--live --json with two duplicate slugs → duplicate_count == 2."""
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setattr(
        mod, "fetch_live_plans",
        lambda token: {
            "dup-a-aaaaaa": [{"id": "p1"}, {"id": "p2"}],
            "dup-b-bbbbbb": [{"id": "p3"}, {"id": "p4"}, {"id": "p5"}],
        },
    )
    rc = mod.main(["--live", "--json"])
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["duplicate_count"] == 2
    slugs = [d["slug"] for d in payload["duplicates"]]
    assert "dup-a-aaaaaa" in slugs
    assert "dup-b-bbbbbb" in slugs


def test_load_cache_missing_plans_key_returns_none(mod, tmp_path, monkeypatch):
    """Cache JSON without a 'plans' key is considered malformed."""
    cache = tmp_path / "bad.json"
    cache.write_text(json.dumps({"fetched_at": "2026-05-10T00:00:00Z"}), encoding="utf-8")
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    # Should either return None or an empty dict — must not raise.
    result = mod.load_cache_snapshot()
    assert result is None or result == {}


# ---------------------------------------------------------------------------
# W2 Pagination — cursor exhaustion
# ---------------------------------------------------------------------------

def _make_page(slug: str, page_id: str, status: str = "In Progress") -> dict:
    """Build a minimal Notion page response dict."""
    return {
        "id": page_id,
        "in_trash": False,
        "archived": False,
        "properties": {
            "Slug": {"title": [{"plain_text": slug}]},
            "Status": {"select": {"name": status}},
        },
    }


class TestFetchLivePlansPagination:
    """fetch_live_plans must exhaust all cursor pages (W2 — D-4 deferred scope)."""

    def test_single_page_no_cursor(self, mod, monkeypatch):
        """Single page with has_more=False — one API call, correct result."""
        pages = [
            _make_page("plan-a-aaaaaa", "id-a"),
            _make_page("plan-b-bbbbbb", "id-b"),
        ]
        response_data = {"results": pages, "has_more": False}

        call_count = 0

        def fake_urlopen(req, timeout=None):
            nonlocal call_count
            call_count += 1
            body = json.dumps(response_data).encode("utf-8")

            class Resp:
                def read(self):
                    return body
                def __enter__(self):
                    return self
                def __exit__(self, *_):
                    pass

            return Resp()

        import urllib.request as urq
        monkeypatch.setattr(urq, "urlopen", fake_urlopen)

        result = mod.fetch_live_plans("fake-token")

        assert call_count == 1
        assert set(result.keys()) == {"plan-a-aaaaaa", "plan-b-bbbbbb"}

    def test_three_page_cursor_exhaustion(self, mod, monkeypatch):
        """Three pages of results — all slugs collected via cursor pagination."""
        pages = [
            [_make_page(f"plan-{i}-aaaaaa", f"id-{i}") for i in range(1, 4)],
            [_make_page(f"plan-{i}-aaaaaa", f"id-{i}") for i in range(4, 7)],
            [_make_page(f"plan-{i}-aaaaaa", f"id-{i}") for i in range(7, 10)],
        ]
        responses = [
            {"results": pages[0], "has_more": True,  "next_cursor": "cursor-1"},
            {"results": pages[1], "has_more": True,  "next_cursor": "cursor-2"},
            {"results": pages[2], "has_more": False},
        ]

        call_count = 0
        sent_cursors: list[str | None] = []

        def fake_urlopen(req, timeout=None):
            nonlocal call_count
            body_bytes = req.data or b"{}"
            sent_body = json.loads(body_bytes)
            sent_cursors.append(sent_body.get("start_cursor"))
            resp_data = json.dumps(responses[call_count]).encode("utf-8")
            call_count += 1

            class Resp:
                def read(self):
                    return resp_data
                def __enter__(self):
                    return self
                def __exit__(self, *_):
                    pass

            return Resp()

        import urllib.request as urq
        monkeypatch.setattr(urq, "urlopen", fake_urlopen)

        result = mod.fetch_live_plans("fake-token")

        assert call_count == 3
        assert len(result) == 9
        assert sent_cursors[0] is None        # first call: no cursor
        assert sent_cursors[1] == "cursor-1"  # second call uses page-1 cursor
        assert sent_cursors[2] == "cursor-2"  # third call uses page-2 cursor

    def test_trashed_pages_excluded(self, mod, monkeypatch):
        """Pages with in_trash=True or archived=True must be skipped."""
        pages = [
            _make_page("live-plan-aaaaaa", "id-live"),
            {**_make_page("trashed-plan-bbbbbb", "id-trash"), "in_trash": True},
            {**_make_page("archived-plan-cccccc", "id-arch"), "archived": True},
        ]
        response_data = {"results": pages, "has_more": False}

        def fake_urlopen(req, timeout=None):
            class Resp:
                def read(self):
                    return json.dumps(response_data).encode("utf-8")
                def __enter__(self):
                    return self
                def __exit__(self, *_):
                    pass
            return Resp()

        import urllib.request as urq
        monkeypatch.setattr(urq, "urlopen", fake_urlopen)

        result = mod.fetch_live_plans("fake-token")

        assert "live-plan-aaaaaa" in result
        assert "trashed-plan-bbbbbb" not in result
        assert "archived-plan-cccccc" not in result
