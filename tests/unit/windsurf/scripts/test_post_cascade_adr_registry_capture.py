"""Tests for post_cascade_adr_registry_capture.py — auto-post ADRs to Notion.

Coverage:
    * Path detection: forward/back slash, markdown link wrap, dedup, archive
      exclusion, non-numeric variants logged separately.
    * Markdown parsing: header field extraction, status normalization,
      decision-date isolation, layer extraction (numeric, path-prefix,
      L_<NAMESPACE>), title separators (em/en-dash, hyphen, colon),
      Context-section summary fall-through.
    * File guards: missing file, oversized file, unicode-decode failure.
    * Notion payload: required vs optional properties, length truncation,
      multi-select preserves order.
    * Main flow: empty stdin, response budget cap, bypass env, no-token
      pending, dedup vs Notion existing page.
    * No real network or filesystem-write side effects (Notion API stubbed,
      capture log redirected to tmp_path).

Loaded via importlib so the module's REPO_ROOT does not pollute sys.modules.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SCRIPTS = _REPO_ROOT / ".windsurf" / "scripts"


def _load(mod_name: str = "adr_registry_t") -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        mod_name,
        _SCRIPTS / "post_cascade_adr_registry_capture.py",
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def hook(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Loaded hook with capture log redirected and REPO_ROOT pinned to tmp."""
    mod = _load()
    log_path = tmp_path / "adr_registry_capture.jsonl"
    monkeypatch.setattr(mod, "CAPTURE_LOG", log_path)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    # Pre-create the docs/architecture/adr directory to mirror real layout.
    (tmp_path / "docs" / "architecture" / "adr").mkdir(parents=True)
    return mod


# ---------------------------------------------------------------------------
# Path detection
# ---------------------------------------------------------------------------


class TestFindAdrFilenames:
    def test_forward_slash_path(self, hook: ModuleType) -> None:
        numeric, variants = hook._find_adr_filenames("see docs/architecture/adr/ADR-055-foo.md")
        assert numeric == ["ADR-055-foo.md"]
        assert variants == []

    def test_back_slash_path(self, hook: ModuleType) -> None:
        numeric, _ = hook._find_adr_filenames(r"@c:\repo\docs\architecture\adr\ADR-055-foo.md")
        assert numeric == ["ADR-055-foo.md"]

    def test_markdown_link_wrapped(self, hook: ModuleType) -> None:
        numeric, _ = hook._find_adr_filenames("[ADR-055](docs/architecture/adr/ADR-055-foo.md) is the spec.")
        assert numeric == ["ADR-055-foo.md"]

    def test_multiple_unique(self, hook: ModuleType) -> None:
        numeric, _ = hook._find_adr_filenames(
            "Created docs/architecture/adr/ADR-055-a.md "
            "and docs/architecture/adr/ADR-056-b.md "
            "and docs/architecture/adr/ADR-057-c.md"
        )
        assert numeric == ["ADR-055-a.md", "ADR-056-b.md", "ADR-057-c.md"]

    def test_dedup_preserves_first_seen_order(self, hook: ModuleType) -> None:
        text = (
            "First mention docs/architecture/adr/ADR-100-x.md. "
            "Then docs/architecture/adr/ADR-099-y.md. "
            "Then again docs/architecture/adr/ADR-100-x.md."
        )
        numeric, _ = hook._find_adr_filenames(text)
        assert numeric == ["ADR-100-x.md", "ADR-099-y.md"]

    def test_archive_path_excluded(self, hook: ModuleType) -> None:
        numeric, variants = hook._find_adr_filenames(
            "old version at archives/docs/architecture/adr/ADR-001-old.md"
        )
        assert numeric == []
        assert variants == []

    def test_smoke_path_excluded(self, hook: ModuleType) -> None:
        numeric, _ = hook._find_adr_filenames("_smoke_v1_coerce_e9aa09/docs/architecture/adr/ADR-099-fake.md")
        assert numeric == []

    def test_non_numeric_variant_logged_separately(self, hook: ModuleType) -> None:
        numeric, variants = hook._find_adr_filenames(
            "see docs/architecture/adr/ADR-PROMPT-ASSEMBLY-001-rendering.md"
        )
        assert numeric == []
        assert variants == ["ADR-PROMPT-ASSEMBLY-001-rendering.md"]

    def test_numeric_and_variant_coexist(self, hook: ModuleType) -> None:
        numeric, variants = hook._find_adr_filenames(
            "docs/architecture/adr/ADR-055-foo.md docs/architecture/adr/ADR-PROMPT-ASSEMBLY-002-bar.md"
        )
        assert numeric == ["ADR-055-foo.md"]
        assert variants == ["ADR-PROMPT-ASSEMBLY-002-bar.md"]

    def test_no_paths_in_response(self, hook: ModuleType) -> None:
        numeric, variants = hook._find_adr_filenames("Discussion of ADR-055 without a path mention.")
        assert numeric == []
        assert variants == []


# ---------------------------------------------------------------------------
# Header field parsing
# ---------------------------------------------------------------------------


class TestParseHeaderField:
    def test_simple_field(self, hook: ModuleType) -> None:
        text = "**Status**: Proposed\n**Date**: 2026-04-24"
        assert hook._parse_header_field(text, "Status") == "Proposed"
        assert hook._parse_header_field(text, "Date") == "2026-04-24"

    def test_label_case_insensitive(self, hook: ModuleType) -> None:
        text = "**status**: Accepted"
        assert hook._parse_header_field(text, "Status") == "Accepted"

    def test_missing_field(self, hook: ModuleType) -> None:
        assert hook._parse_header_field("no fields here", "Status") == ""

    def test_value_strips_inline_emphasis(self, hook: ModuleType) -> None:
        text = "**Status**: *Proposed*"
        assert hook._parse_header_field(text, "Status") == "Proposed"


class TestNormalizeStatus:
    def test_canonical(self, hook: ModuleType) -> None:
        assert hook._normalize_status("Proposed") == "Proposed"
        assert hook._normalize_status("Accepted") == "Accepted"

    def test_with_parenthetical(self, hook: ModuleType) -> None:
        assert hook._normalize_status("Proposed (rescoped 2026-04-23; amended 2026-04-24)") == "Proposed"

    def test_unknown_falls_back(self, hook: ModuleType) -> None:
        assert hook._normalize_status("Bizarre") == hook.DEFAULT_STATUS

    def test_draft_coerced_to_proposed(self, hook: ModuleType) -> None:
        assert hook._normalize_status("Draft") == "Proposed"
        assert hook._normalize_status("WIP") == "Proposed"

    def test_empty_returns_default(self, hook: ModuleType) -> None:
        assert hook._normalize_status("") == hook.DEFAULT_STATUS

    def test_lowercase_normalized(self, hook: ModuleType) -> None:
        assert hook._normalize_status("accepted") == "Accepted"


class TestParseDecisionDate:
    def test_iso_date(self, hook: ModuleType) -> None:
        assert hook._parse_decision_date("2026-04-24") == "2026-04-24"

    def test_with_amendment_text(self, hook: ModuleType) -> None:
        assert hook._parse_decision_date("2026-04-23 (amended 2026-04-24)") == "2026-04-23"

    def test_no_date(self, hook: ModuleType) -> None:
        assert hook._parse_decision_date("never") == ""

    def test_empty(self, hook: ModuleType) -> None:
        assert hook._parse_decision_date("") == ""


class TestParseImpactLayers:
    def test_bare_numeric_tokens(self, hook: ModuleType) -> None:
        assert hook._parse_impact_layers("L1, L4") == ["L1", "L4"]

    def test_path_prefix_numeric(self, hook: ModuleType) -> None:
        raw = (
            "agentic_core/L4_state/utils/client/chroma_client.py, "
            "agentic_core/embeddings/bge_runtime.py, "
            "agentic_core/L1_cognition/reasoning/multi_query_fusion.py"
        )
        assert hook._parse_impact_layers(raw) == ["L4", "L1"]

    def test_namespace_layer_l_shared(self, hook: ModuleType) -> None:
        assert hook._parse_impact_layers("apps_shared L_SHARED") == ["L_SHARED"]

    def test_namespace_layer_l_tools_l_app(self, hook: ModuleType) -> None:
        assert hook._parse_impact_layers("L_TOOLS and L_APP") == ["L_TOOLS", "L_APP"]

    def test_unknown_namespace_token_rejected(self, hook: ModuleType) -> None:
        # L_NONEXISTENT is not in ALLOWED_LAYERS.
        assert hook._parse_impact_layers("L_NONEXISTENT") == []

    def test_l7_rejected(self, hook: ModuleType) -> None:
        # Numeric pattern is L0-L6; L7 must not match.
        assert hook._parse_impact_layers("L7 something") == []

    def test_dedup_first_seen_wins(self, hook: ModuleType) -> None:
        assert hook._parse_impact_layers("L1 L4 L1 L4 L1") == ["L1", "L4"]

    def test_empty(self, hook: ModuleType) -> None:
        assert hook._parse_impact_layers("") == []

    def test_mixed_numeric_and_namespace(self, hook: ModuleType) -> None:
        assert hook._parse_impact_layers("agentic_core/L1_cognition/, L_SHARED") == ["L1", "L_SHARED"]


class TestParseTitle:
    def test_em_dash_separator(self, hook: ModuleType) -> None:
        text = "# ADR-055 \u2014 Embedding Model Enforcement\n\nbody"
        assert hook._parse_title(text, "fb") == "Embedding Model Enforcement"

    def test_en_dash_separator(self, hook: ModuleType) -> None:
        text = "# ADR-055 \u2013 Embedding Model Enforcement\n"
        assert hook._parse_title(text, "fb") == "Embedding Model Enforcement"

    def test_hyphen_separator(self, hook: ModuleType) -> None:
        text = "# ADR-055 - Embedding Model Enforcement\n"
        assert hook._parse_title(text, "fb") == "Embedding Model Enforcement"

    def test_colon_separator(self, hook: ModuleType) -> None:
        text = "# ADR-055: Embedding Model Enforcement\n"
        assert hook._parse_title(text, "fb") == "Embedding Model Enforcement"

    def test_no_separator(self, hook: ModuleType) -> None:
        text = "# ADR-055 Embedding Model Enforcement\n"
        # No recognized separator — return raw H1 line as-is.
        assert hook._parse_title(text, "fb") == "ADR-055 Embedding Model Enforcement"

    def test_no_h1(self, hook: ModuleType) -> None:
        assert hook._parse_title("body without heading", "ADR-055") == "ADR-055"

    def test_h1_with_only_id(self, hook: ModuleType) -> None:
        # Edge: title is just the ID with no body — fall back to the line.
        text = "# ADR-055\n"
        assert hook._parse_title(text, "fb") == "ADR-055"


class TestParseSummary:
    def test_context_section_first_paragraph(self, hook: ModuleType) -> None:
        text = (
            "# ADR-055\n\n---\n\n## Context\n\n"
            "First paragraph of context.\n\nSecond paragraph.\n\n## Decision\n"
        )
        out = hook._parse_summary(text)
        assert out.startswith("First paragraph of context")
        assert "Second paragraph" not in out

    def test_no_context_section_fallback(self, hook: ModuleType) -> None:
        text = "# ADR-055\n\n---\n\nFirst body paragraph here.\n\nSecond.\n"
        out = hook._parse_summary(text)
        assert "First body paragraph" in out

    def test_strips_inline_code(self, hook: ModuleType) -> None:
        text = "## Context\n\nThe `foo()` function is broken.\n"
        assert "`" not in hook._parse_summary(text)

    def test_truncates_to_1800(self, hook: ModuleType) -> None:
        body = "x " * 5000
        text = f"## Context\n\n{body}\n"
        assert len(hook._parse_summary(text)) <= 1800


class TestFlattenMd:
    def test_strips_bold_italic_code(self, hook: ModuleType) -> None:
        out = hook._flatten_md("**bold** *italic* `code` __also__ _also2_")
        assert out == "bold italic code also also2"

    def test_collapses_whitespace(self, hook: ModuleType) -> None:
        out = hook._flatten_md("a  b\n\tc\n\nd")
        assert out == "a b c d"


# ---------------------------------------------------------------------------
# File parsing
# ---------------------------------------------------------------------------


class TestParseAdrFile:
    def _write_adr(self, root: Path, name: str, body: str) -> Path:
        path = root / "docs" / "architecture" / "adr" / name
        path.write_text(body, encoding="utf-8")
        return path

    def test_well_formed_adr(self, hook: ModuleType, tmp_path: Path) -> None:
        body = (
            "# ADR-055 \u2014 Embedding Model Enforcement\n\n"
            "**Status**: Proposed\n"
            "**Date**: 2026-04-24\n"
            "**Deciders**: Maintainers\n"
            "**Impact Layers**: L4, L_SHARED\n\n"
            "---\n\n"
            "## Context\n\nThe repo embeds without enforcement.\n"
        )
        path = self._write_adr(tmp_path, "ADR-055-foo.md", body)
        result = hook._parse_adr_file(path)
        assert result is not None
        assert result["adr_id"] == "ADR-055"
        assert result["title"] == "Embedding Model Enforcement"
        assert result["status"] == "Proposed"
        assert result["decision_date"] == "2026-04-24"
        assert result["impact_layers"] == ["L4", "L_SHARED"]
        assert result["deciders"] == "Maintainers"
        assert result["summary"].startswith("The repo embeds")

    def test_missing_file(self, hook: ModuleType, tmp_path: Path) -> None:
        result = hook._parse_adr_file(tmp_path / "nope.md")
        assert result is None

    def test_oversized_file_rejected(self, hook: ModuleType, tmp_path: Path) -> None:
        body = "# ADR-055\n" + "x" * (hook.MAX_ADR_FILE_BYTES + 1)
        path = self._write_adr(tmp_path, "ADR-055-huge.md", body)
        assert hook._parse_adr_file(path) is None

    def test_no_adr_id_returns_none(self, hook: ModuleType, tmp_path: Path) -> None:
        body = "# Generic Doc\n\nNo ADR id anywhere."
        path = self._write_adr(tmp_path, "ADR-XYZ-fake.md", body)
        # Filename has no \\d+ either, ID extraction fails.
        assert hook._parse_adr_file(path) is None

    def test_id_padding(self, hook: ModuleType, tmp_path: Path) -> None:
        body = "# ADR-7 \u2014 Tiny Id\n\n**Status**: Proposed\n"
        path = self._write_adr(tmp_path, "ADR-7-tiny.md", body)
        result = hook._parse_adr_file(path)
        assert result is not None
        assert result["adr_id"] == "ADR-007"

    def test_minimal_body_uses_defaults(self, hook: ModuleType, tmp_path: Path) -> None:
        body = "# ADR-099 \u2014 Bare Bones\n\nNo header lines.\n"
        path = self._write_adr(tmp_path, "ADR-099-bare.md", body)
        result = hook._parse_adr_file(path)
        assert result is not None
        assert result["status"] == hook.DEFAULT_STATUS
        assert result["decision_date"] == ""
        assert result["impact_layers"] == []
        assert result["deciders"] == "Agentic-Workflow maintainers"


# ---------------------------------------------------------------------------
# Notion payload shape
# ---------------------------------------------------------------------------


class TestBuildNotionPayload:
    def _adr(self, **overrides: Any) -> dict[str, Any]:
        base = {
            "adr_id": "ADR-055",
            "filename": "ADR-055-foo.md",
            "title": "Embedding Model Enforcement",
            "status": "Proposed",
            "decision_date": "2026-04-24",
            "deciders": "Maintainers",
            "impact_layers": ["L4", "L_SHARED"],
            "summary": "Brief description.",
        }
        base.update(overrides)
        return base

    def test_all_required_fields(self, hook: ModuleType) -> None:
        payload = hook._build_notion_payload(self._adr())
        props = payload["properties"]
        assert props["ADR Title"]["title"][0]["text"]["content"] == "Embedding Model Enforcement"
        assert props["ADR ID"]["rich_text"][0]["text"]["content"] == "ADR-055"
        assert props["Status"]["select"]["name"] == "Proposed"
        assert props["Filename"]["rich_text"][0]["text"]["content"] == "ADR-055-foo.md"
        assert props["Deciders"]["rich_text"][0]["text"]["content"] == "Maintainers"
        assert payload["parent"]["database_id"] == hook.ADR_REGISTRY_DB_ID

    def test_optional_date_omitted_when_blank(self, hook: ModuleType) -> None:
        payload = hook._build_notion_payload(self._adr(decision_date=""))
        assert "Decision Date" not in payload["properties"]

    def test_optional_layers_omitted_when_empty(self, hook: ModuleType) -> None:
        payload = hook._build_notion_payload(self._adr(impact_layers=[]))
        assert "Impact Layers" not in payload["properties"]

    def test_optional_summary_omitted_when_blank(self, hook: ModuleType) -> None:
        payload = hook._build_notion_payload(self._adr(summary=""))
        assert "Summary" not in payload["properties"]

    def test_layers_preserve_order(self, hook: ModuleType) -> None:
        payload = hook._build_notion_payload(self._adr(impact_layers=["L_SHARED", "L1", "L4"]))
        names = [m["name"] for m in payload["properties"]["Impact Layers"]["multi_select"]]
        assert names == ["L_SHARED", "L1", "L4"]

    def test_title_truncated_to_200(self, hook: ModuleType) -> None:
        payload = hook._build_notion_payload(self._adr(title="x" * 500))
        content = payload["properties"]["ADR Title"]["title"][0]["text"]["content"]
        assert len(content) == 200


# ---------------------------------------------------------------------------
# Process flow
# ---------------------------------------------------------------------------


class TestProcessFilename:
    def _write_adr(self, root: Path, name: str = "ADR-055-foo.md") -> Path:
        path = root / "docs" / "architecture" / "adr" / name
        path.write_text(
            "# ADR-055 \u2014 Test ADR\n\n**Status**: Proposed\n"
            "**Date**: 2026-04-24\n\n## Context\n\nTest body.\n",
            encoding="utf-8",
        )
        return path

    def test_file_missing(self, hook: ModuleType) -> None:
        record = hook._process_filename("ADR-999-missing.md", token="t")
        assert record["kind"] == "file_missing"

    def test_no_token_pending(self, hook: ModuleType, tmp_path: Path) -> None:
        self._write_adr(tmp_path)
        record = hook._process_filename("ADR-055-foo.md", token=None)
        assert record["kind"] == "pending_no_token"
        assert record["adr"]["adr_id"] == "ADR-055"

    def test_local_recent_duplicate_skipped(
        self, hook: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._write_adr(tmp_path)
        monkeypatch.setattr(hook, "_recent_local_duplicate", lambda _id: True)
        record = hook._process_filename("ADR-055-foo.md", token="t")
        assert record["kind"] == "skipped_recent_duplicate"

    def test_notion_duplicate_skipped(
        self, hook: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._write_adr(tmp_path)
        monkeypatch.setattr(hook, "_recent_local_duplicate", lambda _id: False)
        monkeypatch.setattr(hook, "_notion_existing_page", lambda _id, _t: "existing-page")
        record = hook._process_filename("ADR-055-foo.md", token="t")
        assert record["kind"] == "skipped_notion_duplicate"
        assert record["notion_page_id"] == "existing-page"

    def test_post_success(self, hook: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self._write_adr(tmp_path)
        monkeypatch.setattr(hook, "_recent_local_duplicate", lambda _id: False)
        monkeypatch.setattr(hook, "_notion_existing_page", lambda _id, _t: None)
        monkeypatch.setattr(
            hook,
            "_notion_post",
            lambda _p, _t: {"id": "new-page-id", "url": "https://notion/new-page"},
        )
        record = hook._process_filename("ADR-055-foo.md", token="t")
        assert record["kind"] == "auto_posted"
        assert record["notion_page_id"] == "new-page-id"

    def test_post_http_error(self, hook: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import urllib.error

        self._write_adr(tmp_path)
        monkeypatch.setattr(hook, "_recent_local_duplicate", lambda _id: False)
        monkeypatch.setattr(hook, "_notion_existing_page", lambda _id, _t: None)

        def _raise(*_a: Any, **_kw: Any) -> None:
            raise urllib.error.HTTPError("u", 409, "Conflict", {}, None)  # type: ignore[arg-type]

        monkeypatch.setattr(hook, "_notion_post", _raise)
        record = hook._process_filename("ADR-055-foo.md", token="t")
        assert record["kind"] == "post_http_error"
        assert record["status"] == 409

    def test_post_transport_error_recorded(
        self, hook: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import urllib.error

        self._write_adr(tmp_path)
        monkeypatch.setattr(hook, "_recent_local_duplicate", lambda _id: False)
        monkeypatch.setattr(hook, "_notion_existing_page", lambda _id, _t: None)

        def _raise(*_a: Any, **_kw: Any) -> None:
            raise urllib.error.URLError("dns")

        monkeypatch.setattr(hook, "_notion_post", _raise)
        record = hook._process_filename("ADR-055-foo.md", token="t")
        assert record["kind"] == "post_transport_error"


class TestRecentLocalDuplicate:
    def test_no_log_returns_false(self, hook: ModuleType) -> None:
        assert hook._recent_local_duplicate("ADR-055") is False

    def test_recent_auto_posted_match_true(self, hook: ModuleType, tmp_path: Path) -> None:
        log = hook.CAPTURE_LOG
        rec = {
            "timestamp": hook._utc_now_iso(),
            "kind": "auto_posted",
            "adr": {"adr_id": "ADR-055"},
        }
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        assert hook._recent_local_duplicate("ADR-055") is True

    def test_old_record_ignored(self, hook: ModuleType) -> None:
        from datetime import datetime, timedelta, timezone

        log = hook.CAPTURE_LOG
        old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        rec = {"timestamp": old_ts, "kind": "auto_posted", "adr": {"adr_id": "ADR-055"}}
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        assert hook._recent_local_duplicate("ADR-055") is False

    def test_other_kinds_ignored(self, hook: ModuleType) -> None:
        log = hook.CAPTURE_LOG
        rec = {
            "timestamp": hook._utc_now_iso(),
            "kind": "post_http_error",
            "adr": {"adr_id": "ADR-055"},
        }
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        assert hook._recent_local_duplicate("ADR-055") is False


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


class TestMain:
    def test_bypass_env(self, hook: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ADR_REGISTRY_CAPTURE_BYPASS", "1")
        # No stdin redirect needed; bypass returns before stdin read.
        assert hook.main() == 0
        assert hook.CAPTURE_LOG.exists()
        records = [json.loads(line) for line in hook.CAPTURE_LOG.read_text(encoding="utf-8").splitlines()]
        assert records[-1]["kind"] == "bypass"

    def test_no_adr_paths_in_response_exits_zero(
        self, hook: ModuleType, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from io import StringIO

        monkeypatch.setattr(sys, "stdin", StringIO("a response without any adr paths"))
        assert hook.main() == 0
        # No log entries when response has no paths.
        assert not hook.CAPTURE_LOG.exists() or hook.CAPTURE_LOG.read_text(encoding="utf-8") == ""

    def test_response_size_capped(
        self, hook: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        # Place a real ADR file so the auto-post path can run.
        adr = tmp_path / "docs" / "architecture" / "adr" / "ADR-055-foo.md"
        adr.write_text("# ADR-055 \u2014 T\n**Status**: Proposed\n", encoding="utf-8")

        # Construct a response: ADR mention at the head, then garbage to push
        # the total over the budget. The cap should preserve head detection.
        head = "Created docs/architecture/adr/ADR-055-foo.md\n"
        garbage = "x" * (hook.MAX_RESPONSE_BYTES + 1024)
        from io import StringIO

        monkeypatch.setattr(sys, "stdin", StringIO(head + garbage))
        # Stub Notion calls so we don't make a real request.
        monkeypatch.setattr(hook, "_notion_token", lambda: None)
        rc = hook.main()
        assert rc == 0
        # Head ADR was detected and recorded.
        records = [json.loads(line) for line in hook.CAPTURE_LOG.read_text(encoding="utf-8").splitlines()]
        ids_seen = {r.get("adr", {}).get("adr_id") for r in records if "adr" in r}
        assert "ADR-055" in ids_seen

    def test_unsupported_variant_logged_and_main_skips(
        self, hook: ModuleType, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from io import StringIO

        text = "Created docs/architecture/adr/ADR-PROMPT-ASSEMBLY-001-x.md"
        monkeypatch.setattr(sys, "stdin", StringIO(text))
        rc = hook.main()
        assert rc == 0
        records = [json.loads(line) for line in hook.CAPTURE_LOG.read_text(encoding="utf-8").splitlines()]
        assert any(r.get("kind") == "unsupported_naming" for r in records)
