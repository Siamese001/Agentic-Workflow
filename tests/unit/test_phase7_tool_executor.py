"""
Phase 7 — Wave 2 Tests: ToolIntentExecutor (L2.2 sandbox-only) + ToolResult.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.engines.tool_intent_executor import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    ToolIntentExecutor,
    ToolResult,
)
from agentic_core.L2_execution.types.ml_write_intent_types import MLWriteIntentExecutor
from agentic_core.L2_execution.types.tool_intent_types import (
    ToolCapability,
    ToolViolation,
    build_tool_intent,
)

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"


def _noop_fn(args: dict) -> dict:
    return {"output_summary": "ok", "success": True, "anchor_ids": []}


def _retrieval_fn(args: dict) -> dict:
    return {
        "output_summary": "retrieved 2 chunks",
        "success": True,
        "anchor_ids": ["chunk-B", "chunk-A"],
    }


def _failing_fn(args: dict) -> dict:
    return {"output_summary": "error: timeout", "success": False, "anchor_ids": []}


class TestToolIntentExecBlockedOutsideSandbox:
    def test_tool_intent_exec_blocked_outside_sandbox(self):
        """
        Core Wave 2 guarantee: mutating ToolIntent executed outside sandbox raises
        ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX").
        """
        intent = build_tool_intent(
            "redis_set",
            ToolCapability.MUTATING_EXTERNAL,
            {"key": "k", "value": "v"},
        )
        executor = ToolIntentExecutor()
        with pytest.raises(ToolViolation) as exc_info:
            executor.execute(intent, fn=_noop_fn)
        assert exc_info.value.code == "TOOL_WRITE_OUTSIDE_SANDBOX"

    def test_mutating_fs_blocked_outside_sandbox(self):
        intent = build_tool_intent(
            "file_write",
            ToolCapability.MUTATING_FS,
            {"path": "/tmp/out.txt", "content": "data"},
        )
        executor = ToolIntentExecutor()
        with pytest.raises(ToolViolation) as exc_info:
            executor.execute(intent, fn=_noop_fn)
        assert "TOOL_WRITE_OUTSIDE_SANDBOX" in str(exc_info.value)

    def test_mutating_statebus_blocked_outside_sandbox(self):
        intent = build_tool_intent(
            "event_emit",
            ToolCapability.MUTATING_STATEBUS,
            {"event": "done"},
        )
        executor = ToolIntentExecutor()
        with pytest.raises(ToolViolation) as exc_info:
            executor.execute(intent, fn=_noop_fn)
        assert exc_info.value.code == "TOOL_WRITE_OUTSIDE_SANDBOX"

    def test_violation_detail_contains_tool_name(self):
        intent = build_tool_intent(
            "pinecone_upsert",
            ToolCapability.MUTATING_EXTERNAL,
            {"vectors": []},
        )
        executor = ToolIntentExecutor()
        try:
            executor.execute(intent, fn=_noop_fn)
            pytest.fail("Expected ToolViolation")
        except ToolViolation as exc:  # guardian: allow-silent-swallower
            assert "pinecone_upsert" in exc.detail


class TestToolIntentExecAllowedInsideSandbox:
    def test_tool_intent_exec_allowed_inside_sandbox(self):
        """
        Core Wave 2 guarantee: mutating ToolIntent executed inside sandbox succeeds.
        """
        intent = build_tool_intent(
            "redis_set",
            ToolCapability.MUTATING_EXTERNAL,
            {"key": "k", "value": "v"},
        )
        executor = ToolIntentExecutor()
        with MLWriteIntentExecutor():
            result = executor.execute(intent, fn=_noop_fn)
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.tool_name == "redis_set"

    def test_non_mutating_allowed_outside_sandbox(self):
        """NON_MUTATING tools (requires_commit=False) may execute anywhere."""
        intent = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/f.txt"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_noop_fn)
        assert result.success is True

    def test_mutating_fs_allowed_inside_sandbox(self):
        intent = build_tool_intent(
            "file_write",
            ToolCapability.MUTATING_FS,
            {"path": "/tmp/out.txt", "content": "data"},
        )
        executor = ToolIntentExecutor()
        with MLWriteIntentExecutor():
            result = executor.execute(intent, fn=_noop_fn)
        assert result.success is True

    def test_result_args_hash_matches_intent(self):
        intent = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/f.txt"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_noop_fn)
        assert result.args_hash == intent.args_hash

    def test_result_tool_name_matches_intent(self):
        intent = build_tool_intent(
            "ast_parse",
            ToolCapability.NON_MUTATING,
            {"code": "x = 1"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_noop_fn)
        assert result.tool_name == "ast_parse"

    def test_result_anchor_ids_sorted(self):
        intent = build_tool_intent(
            "llm_call",
            ToolCapability.NON_MUTATING,
            {"prompt": "hello"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_retrieval_fn)
        assert result.anchor_ids == sorted(result.anchor_ids)

    def test_failing_fn_produces_success_false(self):
        intent = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/missing.txt"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_failing_fn)
        assert result.success is False
        assert "error" in result.output_summary


class TestToolResultHashStable:
    def _make_result(self, **overrides) -> ToolResult:
        defaults: dict = {
            "schema_version": 1,
            "tool_name": "file_read",
            "args_hash": "a" * 64,
            "success": True,
            "output_summary": "ok",
            "anchor_ids": [],
        }
        defaults.update(overrides)
        return ToolResult(**defaults)

    def test_tool_result_hash_stable(self):
        """Same inputs produce the same result_hash."""
        r1 = self._make_result()
        r2 = self._make_result()
        assert r1.result_hash == r2.result_hash
        assert len(r1.result_hash) == 64

    def test_hash_changes_with_tool_name(self):
        r1 = self._make_result(tool_name="file_read")
        r2 = self._make_result(tool_name="ast_parse")
        assert r1.result_hash != r2.result_hash

    def test_hash_changes_with_success(self):
        r1 = self._make_result(success=True)
        r2 = self._make_result(success=False)
        assert r1.result_hash != r2.result_hash

    def test_hash_changes_with_output_summary(self):
        r1 = self._make_result(output_summary="ok")
        r2 = self._make_result(output_summary="error")
        assert r1.result_hash != r2.result_hash

    def test_hash_changes_with_anchor_ids(self):
        r1 = self._make_result(anchor_ids=[])
        r2 = self._make_result(anchor_ids=["chunk-A"])
        assert r1.result_hash != r2.result_hash

    def test_result_hash_excluded_from_canonical_bytes(self):
        r = self._make_result()
        assert b"result_hash" not in r.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        r1 = self._make_result()
        r2 = self._make_result()
        assert r1.canonical_bytes() == r2.canonical_bytes()

    def test_anchor_ids_sorted_in_canonical_bytes(self):
        r1 = self._make_result(anchor_ids=["chunk-Z", "chunk-A"])
        r2 = self._make_result(anchor_ids=["chunk-A", "chunk-Z"])
        assert r1.result_hash == r2.result_hash

    def test_to_dict_contains_all_fields(self):
        r = self._make_result()
        d = r.to_dict()
        for key in (
            "schema_version",
            "tool_name",
            "args_hash",
            "success",
            "output_summary",
            "anchor_ids",
            "result_hash",
        ):
            assert key in d


class TestToolResultValidation:
    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            ToolResult(
                schema_version=99,
                tool_name="file_read",
                args_hash="a" * 64,
                success=True,
                output_summary="ok",
                anchor_ids=[],
            )

    def test_empty_tool_name_raises(self):
        with pytest.raises(ValueError, match="tool_name"):
            ToolResult(
                schema_version=1,
                tool_name="",
                args_hash="a" * 64,
                success=True,
                output_summary="ok",
                anchor_ids=[],
            )

    def test_empty_args_hash_raises(self):
        with pytest.raises(ValueError, match="args_hash"):
            ToolResult(
                schema_version=1,
                tool_name="file_read",
                args_hash="",
                success=True,
                output_summary="ok",
                anchor_ids=[],
            )

    def test_non_list_anchor_ids_raises(self):
        with pytest.raises(TypeError, match="anchor_ids"):
            ToolResult(
                schema_version=1,
                tool_name="file_read",
                args_hash="a" * 64,
                success=True,
                output_summary="ok",
                anchor_ids="not-a-list",  # type: ignore[arg-type]
            )
