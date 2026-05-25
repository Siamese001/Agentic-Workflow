"""W3 tests for ADG FIX → Notion backlog sync (plan adg-action-dispatch-c9e4a2)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.notion.adg_fix_backlog_sync import (
    SKIP_MSG,
    build_backlog_page_payload,
    sync_fix_rows,
)
from tools.reports.adg_action_queue import extract_notion_fix_rows, notion_fix_idempotency_key


def _queue_doc() -> dict:
    return {
        "snapshot_ts": "20260525_130122",
        "actions": [
            {
                "rank": 1,
                "verdict_cluster": "FIX",
                "gate_id": "10_infra_wiring",
                "source_digest": "a" * 64,
                "signal": "block",
                "sort_band": "P0",
                "ordering_reason": "fix_block",
                "violation_count": 2,
            },
            {
                "rank": 2,
                "verdict_cluster": "P0_WAVE",
                "gate_id": None,
                "source_id": "apps_shared/foo.py",
                "source_digest": "b" * 64,
                "signal": "wave",
                "sort_band": "P0",
                "ordering_reason": "p0",
                "violation_count": 1,
            },
        ],
    }


def test_idempotency_key_fallback_digest() -> None:
    assert notion_fix_idempotency_key("G1", "snap", "digest") == "G1+snap"
    assert notion_fix_idempotency_key("G1", "", "digest") == "G1+digest"


def test_track_never_in_notion_payload() -> None:
    rows = extract_notion_fix_rows(_queue_doc())
    assert len(rows) == 1
    assert rows[0]["gate_id"] == "10_infra_wiring"
    assert all("TRACK" not in r["gate_id"] for r in rows)


def test_skip_when_token_missing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    q = tmp_path / "q.json"
    q.write_text(json.dumps(_queue_doc()), encoding="utf-8")
    with patch("tools.notion.adg_fix_backlog_sync.get_notion_bearer_token", return_value=""):
        from tools.notion import adg_fix_backlog_sync

        code = adg_fix_backlog_sync.main(["--queue", str(q), "--dry-run"])
    assert code == 0
    assert SKIP_MSG in capsys.readouterr().err


def test_dry_run_payload_shape() -> None:
    rows = extract_notion_fix_rows(_queue_doc())
    payload = build_backlog_page_payload(rows[0])
    assert payload["parent"]["database_id"]
    props = payload["properties"]
    assert "ADG FIX: 10_infra_wiring" in props["Phase Title"]["title"][0]["text"]["content"]
    assert props["Phase ID"]["rich_text"][0]["text"]["content"] == rows[0]["idempotency_key"]
    assert props["Wave ID"]["rich_text"][0]["text"]["content"] == "ADG-FIX"


def test_apply_api_failure_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = extract_notion_fix_rows(_queue_doc())

    def _boom(*_a: object, **_k: object) -> dict:
        raise OSError("network down")

    monkeypatch.setattr(
        "tools.notion.adg_fix_backlog_sync._notion_post_page",
        _boom,
    )
    monkeypatch.setattr(
        "tools.notion.adg_fix_backlog_sync._row_exists",
        lambda *_a, **_k: False,
    )
    monkeypatch.setattr(
        "tools.notion.adg_fix_backlog_sync._resolve_plan_page_id",
        lambda *_a, **_k: None,
    )
    summary = sync_fix_rows(rows, apply=True, token="test-token")
    assert summary["errors"]


def test_main_apply_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    q = tmp_path / "q.json"
    q.write_text(json.dumps(_queue_doc()), encoding="utf-8")
    monkeypatch.setattr(
        "tools.notion.adg_fix_backlog_sync.get_notion_bearer_token",
        lambda: "tok",
    )
    monkeypatch.setattr(
        "tools.notion.adg_fix_backlog_sync.sync_fix_rows",
        lambda *_a, **_k: {"errors": [{"gate_id": "x", "error": "fail"}]},
    )
    from tools.notion import adg_fix_backlog_sync

    assert adg_fix_backlog_sync.main(["--queue", str(q), "--apply"]) == 1
