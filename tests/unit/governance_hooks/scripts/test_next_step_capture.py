"""Unit tests for :mod:`.claude.governance.scripts.post_agent_next_step_capture`."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
HOOK_PATH = REPO_ROOT / ".claude" / "governance" / "scripts" / "post_agent_next_step_capture.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("post_agent_next_step_capture", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Make the scripts dir importable for the hook's sibling imports.
    scripts_dir = str(HOOK_PATH.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HOOK = _load_module()


def _marker(**overrides) -> dict[str, str]:
    base = {
        "plan": "NEW:next-step-unit",
        "title": "Add nightly CI drift check",
        "priority": "P3",
        "est_tokens": "8000",
        "reason": "Catch orphans earlier than weekly cadence",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def test_parse_marker_extracts_all_fields() -> None:
    body = (
        "plan=NEW:ci-hardening title=Run fleet nightly priority=P3 "
        "est_tokens=8000 reason=Catch orphans earlier"
    )
    fields = HOOK._parse_marker(body)  # noqa: SLF001
    assert fields["plan"] == "NEW:ci-hardening"
    assert fields["title"] == "Run fleet nightly"
    assert fields["priority"] == "P3"
    assert fields["est_tokens"] == "8000"
    assert fields["reason"] == "Catch orphans earlier"


def test_parse_title_with_spaces_is_preserved() -> None:
    body = "plan=NEW:x title=Multi word title with spaces priority=P4 est_tokens=5000 reason=because"
    fields = HOOK._parse_marker(body)  # noqa: SLF001
    assert fields["title"] == "Multi word title with spaces"
    assert fields["reason"] == "because"


def test_parse_reason_last_greedy() -> None:
    body = "plan=abc title=t priority=P4 est_tokens=100 reason=long reason with spaces and ending"
    fields = HOOK._parse_marker(body)  # noqa: SLF001
    assert fields["reason"] == "long reason with spaces and ending"


def test_parse_optional_fields() -> None:
    body = "plan=NEW:x title=t priority=P2 est_tokens=1 reason=r wave=W5 phase=P5.1 depends_on=other-plan"
    fields = HOOK._parse_marker(body)  # noqa: SLF001
    assert fields["wave"] == "W5"
    assert fields["phase"] == "P5.1"
    assert fields["depends_on"] == "other-plan"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_validate_accepts_valid_marker() -> None:
    assert HOOK._validate_marker(_marker()) == []  # noqa: SLF001


def test_validate_rejects_missing_required() -> None:
    fields = _marker()
    del fields["priority"]
    errors = HOOK._validate_marker(fields)  # noqa: SLF001
    assert errors == ["priority"]


def test_validate_rejects_bad_priority() -> None:
    errors = HOOK._validate_marker(_marker(priority="P1"))  # noqa: SLF001
    assert errors and "priority must be one of" in errors[0]


def test_validate_rejects_non_int_tokens() -> None:
    errors = HOOK._validate_marker(_marker(est_tokens="not-a-number"))  # noqa: SLF001
    assert errors and "est_tokens" in errors[0]


def test_validate_rejects_tbd_title() -> None:
    errors = HOOK._validate_marker(_marker(title="TBD"))  # noqa: SLF001
    assert errors == ["title must be non-empty and not 'TBD'"]


def test_validate_rejects_empty_title() -> None:
    errors = HOOK._validate_marker(_marker(title=""))  # noqa: SLF001
    assert errors == ["title must be non-empty and not 'TBD'"]


# ---------------------------------------------------------------------------
# Phase ID defaulting
# ---------------------------------------------------------------------------


def test_default_phase_id_is_stable() -> None:
    a = HOOK._default_phase_id("my-slug", "my title")  # noqa: SLF001
    b = HOOK._default_phase_id("my-slug", "my title")  # noqa: SLF001
    assert a == b
    assert a.startswith("NEXT-")


def test_default_phase_id_varies_by_inputs() -> None:
    a = HOOK._default_phase_id("slug-a", "title")  # noqa: SLF001
    b = HOOK._default_phase_id("slug-b", "title")  # noqa: SLF001
    assert a != b


# ---------------------------------------------------------------------------
# Process marker (no network, no token)
# ---------------------------------------------------------------------------


def test_process_marker_without_token_returns_pending(tmp_path, monkeypatch) -> None:
    # Redirect capture log + REPO_ROOT so scaffold writes into tmp_path.
    monkeypatch.setenv("NOTION_TOKEN", "")
    monkeypatch.setattr(HOOK, "CAPTURE_LOG", tmp_path / "capture.jsonl")
    monkeypatch.setattr(HOOK, "REPO_ROOT", tmp_path)

    record = HOOK._process_marker(_marker(), token=None)  # noqa: SLF001
    assert record["kind"] == "pending_no_token"
    # Scaffolder should still have created the plan file.
    plans_dir = tmp_path / "plans"
    assert plans_dir.exists()
    created = list(plans_dir.glob("next-step-unit-*.md"))
    assert len(created) == 1
    assert record["plan_filename"] == created[0].name


def test_process_marker_malformed(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(HOOK, "REPO_ROOT", tmp_path)
    record = HOOK._process_marker(_marker(priority="CRITICAL"), token=None)  # noqa: SLF001
    assert record["kind"] == "malformed_marker"
    assert any("priority" in e for e in record["errors"])


def test_process_marker_populates_defaults(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(HOOK, "CAPTURE_LOG", tmp_path / "capture.jsonl")
    monkeypatch.setattr(HOOK, "REPO_ROOT", tmp_path)
    record = HOOK._process_marker(_marker(), token=None)  # noqa: SLF001
    marker = record["marker"]
    assert marker["wave"] == HOOK.DEFAULT_WAVE
    assert marker["phase"].startswith("NEXT-")
    assert marker["priority"] == "P3"


# ---------------------------------------------------------------------------
# Notion payload shape
# ---------------------------------------------------------------------------


def test_build_payload_uses_mece_v2_shape() -> None:
    fields = _marker(priority="P2")
    fields = {**fields, "wave": "W-NEXT", "phase": "NEXT-abc12345"}
    payload = HOOK._build_notion_payload(fields, "next-step-unit-123456.md")  # noqa: SLF001
    props = payload["properties"]
    title_chunks = props["Phase Title"]["title"]
    assert title_chunks[0]["text"]["content"] == "Add nightly CI drift check"
    assert "Sub-Wave" not in props
    assert props["P-Band"]["select"]["name"] == "P2"
    assert props["Impact Score"]["number"] == 0.0
    assert props["Plan File"]["rich_text"][0]["text"]["content"] == "next-step-unit-123456.md"
    assert props["Status"]["select"]["name"] == "Todo"
