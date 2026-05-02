"""Unit tests for ``post_cascade_mcp_serialization_audit`` (hardened 2026-05-01).

Under the hardened scope, only **remote MCP servers** require serialization:
notion, tavily, deepwiki, context7, GitKraken. Local stdio MCPs (adg_sqlite,
redis, memory, filesystem, vector_db, pytest_mcp, otel_mcp, task_manager,
playwright) batch freely with each other and with native tools.

Covers:

* Single-call responses — always compliant.
* All-native batches — compliant.
* Local-MCP + native — compliant under hardened scope.
* Two local MCPs in same batch — compliant.
* Remote MCP + native — violation (`remote_mcp_mixed_with_native`).
* Remote MCP + local MCP — violation (`remote_mcp_mixed_with_local_mcp`).
* Two remote MCPs — violation (`multi_remote_mcp_in_single_batch`).
* Remote + local + native — violation (`remote_mcp_mixed_with_local_mcp_and_native`).
* Bypass env var — logs bypass row, no violation records.
* Sunset TTL — post-retirement date short-circuits with no file writes.
* Stdin / payload shape coverage (str, dict, tool_info wrapper).
* Classifier returns 4-class taxonomy: mcp_remote, mcp_local, native, unknown.
"""

from __future__ import annotations

import importlib.util
import json
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


# Canonical examples for each classification
_REMOTE_NOTION = "mcp7_API-post-page"
_REMOTE_TAVILY = "mcp12_tavily_search"
_REMOTE_DEEPWIKI = "mcp3_ask_question"
_REMOTE_CONTEXT7 = "mcp2_resolve-library-id"
_REMOTE_GITKRAKEN = "mcp0_git_status"
_LOCAL_ADG = "mcp1_adg_health"
_LOCAL_REDIS = "mcp10_redis_keys"
_LOCAL_MEMORY = "mcp6_add_observations"


# ---------------------------------------------------------------------------
# Compliant batches (no violations)
# ---------------------------------------------------------------------------


def test_single_call_is_compliant(audit):
    text = _wrap(_invoke("read_file"))
    assert audit.detect_violations(text) == []


def test_all_native_batch_is_compliant(audit):
    text = _wrap(_invoke("read_file") + _invoke("grep_search") + _invoke("run_command"))
    assert audit.detect_violations(text) == []


def test_local_mcp_alone_is_compliant(audit):
    text = _wrap(_invoke(_LOCAL_ADG))
    assert audit.detect_violations(text) == []


def test_local_mcp_with_native_is_compliant(audit):
    """HARDENED 2026-05-01: local MCP batches freely with native tools."""
    text = _wrap(_invoke(_LOCAL_ADG) + _invoke("read_file"))
    assert audit.detect_violations(text) == []


def test_two_local_mcps_in_batch_is_compliant(audit):
    """HARDENED 2026-05-01: multiple local MCPs may batch."""
    text = _wrap(_invoke(_LOCAL_ADG) + _invoke(_LOCAL_REDIS))
    assert audit.detect_violations(text) == []


def test_local_mcp_plus_native_plus_local_mcp_is_compliant(audit):
    text = _wrap(
        _invoke(_LOCAL_ADG)
        + _invoke("read_file")
        + _invoke(_LOCAL_MEMORY)
        + _invoke("edit")
    )
    assert audit.detect_violations(text) == []


def test_remote_mcp_alone_is_compliant(audit):
    text = _wrap(_invoke(_REMOTE_NOTION))
    assert audit.detect_violations(text) == []


# ---------------------------------------------------------------------------
# Violation: remote MCP + sibling
# ---------------------------------------------------------------------------


def test_remote_mcp_mixed_with_native_is_violation(audit):
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke("read_file"))
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    v = violations[0]
    assert v["violation_type"] == "remote_mcp_mixed_with_native"
    assert v["remote_mcp_calls"] == [_REMOTE_NOTION]
    assert v["native_calls"] == ["read_file"]
    assert v["local_mcp_calls"] == []
    assert v["upstream"] == "anthropics/claude-agent-sdk-typescript#41"
    assert v["scope"] == "remote-only-since-2026-05-01"


def test_remote_mcp_mixed_with_local_mcp_is_violation(audit):
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke(_LOCAL_ADG))
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    v = violations[0]
    assert v["violation_type"] == "remote_mcp_mixed_with_local_mcp"
    assert v["remote_mcp_calls"] == [_REMOTE_NOTION]
    assert v["local_mcp_calls"] == [_LOCAL_ADG]
    assert v["native_calls"] == []


def test_remote_mcp_mixed_with_local_and_native_is_violation(audit):
    text = _wrap(
        _invoke(_REMOTE_NOTION) + _invoke(_LOCAL_ADG) + _invoke("read_file")
    )
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    v = violations[0]
    assert v["violation_type"] == "remote_mcp_mixed_with_local_mcp_and_native"


def test_two_remote_mcps_is_multi_remote_violation(audit):
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke(_REMOTE_TAVILY))
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    v = violations[0]
    assert v["violation_type"] == "multi_remote_mcp_in_single_batch"
    assert v["remote_mcp_count"] == 2


def test_remote_mcp_mixed_with_three_natives(audit):
    text = _wrap(
        _invoke(_REMOTE_NOTION)
        + _invoke("read_file")
        + _invoke("grep_search")
        + _invoke("run_command")
    )
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "remote_mcp_mixed_with_native"
    assert len(violations[0]["native_calls"]) == 3


# ---------------------------------------------------------------------------
# Block-by-block independence
# ---------------------------------------------------------------------------


def test_multiple_compliant_blocks_in_one_response(audit):
    text = (
        _wrap(_invoke(_LOCAL_ADG) + _invoke(_LOCAL_REDIS))  # compliant: 2 local MCPs
        + "some prose\n"
        + _wrap(_invoke("read_file") + _invoke("grep_search"))  # compliant: all native
        + "\nmore prose\n"
        + _wrap(_invoke(_REMOTE_NOTION))  # compliant: remote MCP alone
    )
    assert audit.detect_violations(text) == []


def test_mixed_compliant_and_violating_blocks(audit):
    """Each `<function_calls>` block is independently scored."""
    text = (
        _wrap(_invoke(_LOCAL_ADG))  # compliant (alone)
        + _wrap(_invoke(_REMOTE_NOTION) + _invoke("read_file"))  # violation
        + _wrap(_invoke("edit") + _invoke("run_command"))  # compliant (all native)
    )
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "remote_mcp_mixed_with_native"
    assert violations[0]["block_index"] == 1


def test_prose_mention_of_mcp_name_not_a_violation(audit):
    """Mentioning ``mcp1_adg_health`` in markdown must not count as a call."""
    text = (
        "I considered using `mcp1_adg_health` and `mcp7_API-post-page` but opted otherwise.\n\n"
        + _wrap(_invoke("read_file"))
    )
    assert audit.detect_violations(text) == []


def test_unknown_tool_name_does_not_mask_remote_mcp_violation(audit):
    """Unknown-but-not-MCP names count as 'native' siblings for the rule."""
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke("some_future_native_tool"))
    violations = audit.detect_violations(text)
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "remote_mcp_mixed_with_native"


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
        def isatty(self) -> bool:  # noqa: D401 — match sys.stdin API
            return False

        def read(self) -> str:
            return stdin_text

    monkeypatch.setattr(audit.sys, "stdin", _FakeStdin())
    for key, val in (env or {}).items():
        monkeypatch.setenv(key, val)
    return audit.main()


def test_main_writes_violation_to_log(audit, monkeypatch):
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke("read_file"))
    rc = _run_main(audit, {"tool_info": {"response": text}}, monkeypatch)
    assert rc == 0
    assert audit.violations_log.exists()
    lines = audit.violations_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["violation_type"] == "remote_mcp_mixed_with_native"


def test_main_ignores_compliant_response(audit, monkeypatch):
    text = _wrap(_invoke(_LOCAL_ADG) + _invoke("read_file"))  # compliant under hardened scope
    rc = _run_main(audit, text, monkeypatch)
    assert rc == 0
    assert not audit.violations_log.exists()


def test_main_extracts_raw_string_payload(audit, monkeypatch):
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke("grep_search"))
    rc = _run_main(audit, text, monkeypatch)
    assert rc == 0
    assert audit.violations_log.exists()


def test_bypass_env_logs_bypass_row_only(audit, monkeypatch):
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke("read_file"))
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
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke("read_file"))  # would otherwise violate
    rc = _run_main(audit, {"tool_info": {"response": text}}, monkeypatch)
    assert rc == 0
    assert not audit.violations_log.exists()


def test_sunset_ttl_future_retirement_still_audits(audit, monkeypatch):
    audit.ttl_config.parent.mkdir(parents=True, exist_ok=True)
    audit.ttl_config.write_text(
        json.dumps({"retired_after": "2099-12-31T00:00:00Z"}),
        encoding="utf-8",
    )
    text = _wrap(_invoke(_REMOTE_NOTION) + _invoke("read_file"))
    rc = _run_main(audit, {"tool_info": {"response": text}}, monkeypatch)
    assert rc == 0
    assert audit.violations_log.exists()


# ---------------------------------------------------------------------------
# _classify — 4-class taxonomy
# ---------------------------------------------------------------------------


def test_classify_helper_remote_mcps(audit):
    """Notion, tavily, deepwiki, context7, GitKraken classify as mcp_remote."""
    assert audit._classify("mcp7_API-post-page") == "mcp_remote"
    assert audit._classify("mcp7_API-query-data-source") == "mcp_remote"
    assert audit._classify("mcp12_tavily_search") == "mcp_remote"
    assert audit._classify("mcp12_tavily-extract") == "mcp_remote"
    assert audit._classify("mcp3_ask_question") == "mcp_remote"
    assert audit._classify("mcp3_read_wiki_contents") == "mcp_remote"
    assert audit._classify("mcp2_resolve-library-id") == "mcp_remote"
    assert audit._classify("mcp2_query-docs") == "mcp_remote"
    assert audit._classify("mcp0_git_status") == "mcp_remote"
    assert audit._classify("mcp0_pull_request_create") == "mcp_remote"
    assert audit._classify("mcp0_issues_get_detail") == "mcp_remote"
    assert audit._classify("mcp0_repository_get_file_content") == "mcp_remote"
    assert audit._classify("mcp0_gitlens_launchpad") == "mcp_remote"
    assert audit._classify("mcp0_gitkraken_workspace_list") == "mcp_remote"


def test_classify_helper_local_mcps(audit):
    """ADG, redis, memory, vector_db, pytest, otel, task_manager classify as mcp_local."""
    assert audit._classify("mcp1_adg_health") == "mcp_local"
    assert audit._classify("mcp1_adg_edge_fanin") == "mcp_local"
    assert audit._classify("mcp10_redis_keys") == "mcp_local"
    assert audit._classify("mcp10_redis_health") == "mcp_local"
    assert audit._classify("mcp6_add_observations") == "mcp_local"
    assert audit._classify("mcp6_create_entities") == "mcp_local"
    assert audit._classify("mcp13_query_collection") == "mcp_local"
    assert audit._classify("mcp9_run_tests") == "mcp_local"
    assert audit._classify("mcp8_otel_anomalies") == "mcp_local"
    assert audit._classify("mcp11_create_task") == "mcp_local"
    # Server-index agnostic: any future numeric prefix
    assert audit._classify("mcp42_some_local_tool") == "mcp_local"


def test_classify_helper_native_and_unknown(audit):
    assert audit._classify("read_file") == "native"
    assert audit._classify("grep_search") == "native"
    assert audit._classify("edit") == "native"
    assert audit._classify("run_command") == "native"
    assert audit._classify("totally_made_up_tool") == "unknown"
