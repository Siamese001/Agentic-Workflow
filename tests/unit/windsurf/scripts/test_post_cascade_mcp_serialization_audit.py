"""Unit tests for ``post_cascade_mcp_serialization_audit``.

Covers:

* Single-call responses — always compliant.
* All-native batches — compliant (not our concern).
* MCP + native in the same ``<function_calls>`` block — violation.
* Two MCP calls in the same block — violation (different type).
* Multiple independent compliant blocks in one response — no violations.
* Bypass env var — logs bypass row, no violation records.
* Sunset TTL — post-retirement date short-circuits with no file writes.
* Stdin / payload shape coverage (str, dict, tool_info wrapper).
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[4]
    / ".windsurf"
    / "scripts"
    / "post_cascade_mcp_serialization_audit.py"
)


def _load_module():
    """Load the hook module by absolute path so tests don't depend on sys.path."""

    spec = importlib.util.spec_from_file_location(
        "post_cascade_mcp_serialization_audit", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="audit")
def _audit(tmp_path, monkeypatch):
    """Load the module with violations_log redirected into tmp_path."""

    module = _load_module()
    monkeypatch.setattr(module, "violations_log", tmp_path / "mcp_serialization.jsonl")
    monkeypatch.setattr(module, "ttl_config", tmp_path / "mcp_serialization_ttl.json")
    monkeypatch.delenv("MCP_SERIAL_BYPASS", raising=False)
    return module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _wrap(block_body: str) -> str:
    return f"<function_calls>{block_body}</function_calls>"


def _invoke(name: str) -> str:
    return f'<invoke name="{name}"><parameter name="x">1</parameter></invoke>'


# ---------------------------------------------------------------------------
# detect_violations — pure-function tests
# ---------------------------------------------------------------------------


def test_single_call_is_compliant(audit):
    text = _wrap(_invoke("read_file"))
    assert audit.detect_violations(text) == []


def test_all_native_batch_is_compliant(audit):
    text = _wrap(_invoke("read_file") + _invoke("grep_search") + _invoke("run_command"))
    assert audit.detect_violations(text) == []


def test_mcp_mixed_with_native_is_violation(audit):
    text = _wrap(_invoke("mcp1_adg_health") + _invoke("read_file"))
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    v = violations[0]
    assert v["violation_type"] == "mcp_mixed_with_native"
    assert v["mcp_calls"] == ["mcp1_adg_health"]
    assert v["non_mcp_calls"] == ["read_file"]
    assert v["upstream"] == "anthropics/claude-agent-sdk-typescript#41"


def test_two_mcp_calls_is_multi_mcp_violation(audit):
    text = _wrap(_invoke("mcp1_adg_health") + _invoke("mcp9_redis_health"))
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "multi_mcp_in_single_batch"
    assert violations[0]["mcp_count"] == 2


def test_mcp_mixed_with_three_natives(audit):
    text = _wrap(
        _invoke("mcp6_API-query-data-source")
        + _invoke("read_file")
        + _invoke("grep_search")
        + _invoke("run_command")
    )
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "mcp_mixed_with_native"
    assert len(violations[0]["non_mcp_calls"]) == 3


def test_multiple_compliant_blocks_in_one_response(audit):
    text = (
        _wrap(_invoke("mcp1_adg_health"))
        + "some prose\n"
        + _wrap(_invoke("read_file") + _invoke("grep_search"))
        + "\nmore prose\n"
        + _wrap(_invoke("mcp9_redis_health"))
    )
    assert audit.detect_violations(text) == []


def test_mixed_compliant_and_violating_blocks(audit):
    """Each `<function_calls>` block is independently scored."""

    text = (
        _wrap(_invoke("mcp1_adg_health"))  # compliant (alone)
        + _wrap(_invoke("mcp1_adg_status") + _invoke("read_file"))  # violation
        + _wrap(_invoke("edit") + _invoke("run_command"))  # compliant (all native)
    )
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "mcp_mixed_with_native"
    assert violations[0]["block_index"] == 1


def test_prose_mention_of_mcp_name_not_a_violation(audit):
    """Mentioning ``mcp1_adg_health`` in markdown must not count as a call."""

    text = (
        "I considered using `mcp1_adg_health` but opted for a direct SQLite read.\n\n"
        + _wrap(_invoke("read_file"))
    )
    assert audit.detect_violations(text) == []


def test_unknown_tool_name_does_not_mask_mcp_violation(audit):
    """Unknown-but-not-MCP names are classified as 'non-mcp' for the purpose
    of this rule (anything that isn't mcp*_ counts as a sibling)."""

    text = _wrap(_invoke("mcp1_adg_health") + _invoke("some_future_native_tool"))
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "mcp_mixed_with_native"


def test_empty_response_returns_empty(audit):
    assert audit.detect_violations("") == []


def test_response_without_function_calls_blocks(audit):
    assert audit.detect_violations("# Just prose, no tool calls.") == []


# ---------------------------------------------------------------------------
# main() — stdin payload + side-effect tests
# ---------------------------------------------------------------------------


def _run_main(audit, payload, monkeypatch, env: dict | None = None) -> int:
    """Invoke main() with payload fed through stdin."""

    stdin_text = payload if isinstance(payload, str) else json.dumps(payload)

    class _FakeStdin:
        def read(self) -> str:
            return stdin_text

    monkeypatch.setattr(audit.sys, "stdin", _FakeStdin())
    for key, val in (env or {}).items():
        monkeypatch.setenv(key, val)
    return audit.main()


def test_main_writes_violation_to_log(audit, monkeypatch):
    text = _wrap(_invoke("mcp1_adg_health") + _invoke("read_file"))
    rc = _run_main(audit, {"tool_info": {"response": text}}, monkeypatch)
    assert rc == 0
    assert audit.violations_log.exists()
    lines = audit.violations_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["violation_type"] == "mcp_mixed_with_native"


def test_main_ignores_compliant_response(audit, monkeypatch):
    text = _wrap(_invoke("mcp1_adg_health"))
    rc = _run_main(audit, text, monkeypatch)
    assert rc == 0
    assert not audit.violations_log.exists()


def test_main_extracts_raw_string_payload(audit, monkeypatch):
    text = _wrap(_invoke("mcp1_adg_health") + _invoke("grep_search"))
    rc = _run_main(audit, text, monkeypatch)
    assert rc == 0
    assert audit.violations_log.exists()


def test_bypass_env_logs_bypass_row_only(audit, monkeypatch):
    text = _wrap(_invoke("mcp1_adg_health") + _invoke("read_file"))
    rc = _run_main(
        audit,
        {"tool_info": {"response": text}},
        monkeypatch,
        env={"MCP_SERIAL_BYPASS": "1"},
    )
    assert rc == 0
    assert audit.violations_log.exists()
    lines = audit.violations_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["violation_type"] == "bypass"


def test_main_never_raises_on_malformed_payload(audit, monkeypatch):
    # Not valid JSON and not a useful string either — should still exit 0.
    rc = _run_main(audit, "{not json", monkeypatch)
    assert rc == 0


def test_sunset_ttl_past_retirement_short_circuits(audit, monkeypatch):
    audit.ttl_config.parent.mkdir(parents=True, exist_ok=True)
    audit.ttl_config.write_text(
        json.dumps(
            {
                "retired_after": "2000-01-01T00:00:00Z",
                "issue_url": "https://example/test",
                "verified_by": "test-suite",
            }
        ),
        encoding="utf-8",
    )
    text = _wrap(_invoke("mcp1_adg_health") + _invoke("read_file"))
    rc = _run_main(audit, {"tool_info": {"response": text}}, monkeypatch)
    assert rc == 0
    # Past-retirement: no violation written even though the pattern is violating.
    assert not audit.violations_log.exists()


def test_sunset_ttl_future_retirement_still_audits(audit, monkeypatch):
    audit.ttl_config.parent.mkdir(parents=True, exist_ok=True)
    audit.ttl_config.write_text(
        json.dumps({"retired_after": "2099-12-31T00:00:00Z"}),
        encoding="utf-8",
    )
    text = _wrap(_invoke("mcp1_adg_health") + _invoke("read_file"))
    rc = _run_main(audit, {"tool_info": {"response": text}}, monkeypatch)
    assert rc == 0
    assert audit.violations_log.exists()


def test_classify_helper(audit):
    assert audit._classify("mcp1_adg_health") == "mcp"
    assert audit._classify("mcp42_some_future_server_tool") == "mcp"
    # Notion-style hyphenated MCP tools must classify as MCP too.
    assert audit._classify("mcp6_API-query-data-source") == "mcp"
    assert audit._classify("mcp6_API-post-page") == "mcp"
    assert audit._classify("read_file") == "native"
    assert audit._classify("grep_search") == "native"
    assert audit._classify("totally_made_up_tool") == "unknown"
