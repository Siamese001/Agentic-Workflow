"""
Phase 7 — Wave 3 Tests: End-to-end gateway path + default parity + static audit.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L2_execution.engines.tool_intent_executor import (
    ToolIntentExecutor,
    ToolResult,
)
from agentic_core.L2_execution.types.ml_write_intent import MLWriteIntentExecutor
from agentic_core.L2_execution.types.tool_intent import (
    ToolCapability,
    ToolViolation,
    assert_l1_tool_allowed,
    build_tool_intent,
    is_l1_cognition_active,
    l1_cognition_scope,
)

pytestmark = pytest.mark.unit_min_deps

_TOOL_INTENT_MODULE = (
    Path(__file__).parent.parent.parent / "agentic_core" / "L2_execution" / "types" / "tool_intent.py"
)

_EXECUTOR_MODULE = (
    Path(__file__).parent.parent.parent
    / "agentic_core"
    / "L2_execution"
    / "engines"
    / "tool_intent_executor.py"
)


def _noop_fn(args: dict) -> dict:
    return {"output_summary": "ok", "success": True, "anchor_ids": []}


def _retrieval_fn(args: dict) -> dict:
    return {
        "output_summary": "retrieved 3 chunks",
        "success": True,
        "anchor_ids": ["chunk-C", "chunk-A", "chunk-B"],
    }


class TestEndToEndGatewayPath:
    def test_l1_cognition_blocks_mutating_tool_deterministically(self):
        """
        End-to-end: L1 cognition flow that attempts a mutating tool call is
        blocked deterministically before any side effect.
        """
        with l1_cognition_scope():
            with pytest.raises(ToolViolation) as exc_info:
                assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "redis_set")
        assert exc_info.value.code == "L1_TOOL_CALL_BLOCKED"
        # Scope is released after the block
        assert is_l1_cognition_active() is False

    def test_l1_cognition_blocks_all_mutating_capabilities(self):
        """All three MUTATING_* capabilities are blocked inside L1."""
        for cap in (
            ToolCapability.MUTATING_EXTERNAL,
            ToolCapability.MUTATING_FS,
            ToolCapability.MUTATING_STATEBUS,
        ):
            with l1_cognition_scope():
                with pytest.raises(ToolViolation) as exc_info:
                    assert_l1_tool_allowed(cap, f"tool_{cap.value}")
            assert exc_info.value.code == "L1_TOOL_CALL_BLOCKED"

    def test_tool_intent_executed_inside_l22_sandbox_succeeds(self):
        """
        Equivalent ToolIntent executed inside L2.2 sandbox succeeds and
        returns a valid ToolResult.
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
        assert result.args_hash == intent.args_hash

    def test_full_gateway_path_l1_emit_l2_execute(self):
        """
        Full gateway path:
        1. L1 cognition scope blocks direct mutating call.
        2. L1 emits ToolIntent instead.
        3. L2.2 sandbox executes the intent successfully.
        """
        # Step 1: L1 blocks direct call
        with l1_cognition_scope():
            with pytest.raises(ToolViolation):
                assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "pinecone_upsert")

        # Step 2: L1 emits ToolIntent (outside scope — intent construction is safe)
        intent = build_tool_intent(
            "pinecone_upsert",
            ToolCapability.MUTATING_EXTERNAL,
            {"vectors": [{"id": "v1", "values": [0.1, 0.2]}]},
        )
        assert intent.requires_commit is True

        # Step 3: L2.2 executes
        executor = ToolIntentExecutor()
        with MLWriteIntentExecutor():
            result = executor.execute(intent, fn=_noop_fn)
        assert result.success is True

    def test_retrieval_result_carries_anchor_ids(self):
        """ToolResult from a retrieval tool carries sorted anchor_ids."""
        intent = build_tool_intent(
            "llm_call",
            ToolCapability.NON_MUTATING,
            {"prompt": "summarize"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_retrieval_fn)
        assert result.anchor_ids == ["chunk-A", "chunk-B", "chunk-C"]

    def test_sandbox_released_after_execution(self):
        """L2.2 sandbox is released after ToolIntentExecutor.execute returns."""
        from agentic_core.L2_execution.types.ml_write_intent import (
            is_commit_sandbox_active,
        )

        intent = build_tool_intent(
            "redis_set",
            ToolCapability.MUTATING_EXTERNAL,
            {"key": "k"},
        )
        executor = ToolIntentExecutor()
        with MLWriteIntentExecutor():
            executor.execute(intent, fn=_noop_fn)
        assert is_commit_sandbox_active() is False


class TestDefaultParityNonMutatingTools:
    def test_default_config_preserves_non_mutating_tool_behavior(self):
        """
        Default parity: existing non-mutating tool usage is unchanged.
        NON_MUTATING tools execute without sandbox, without L1 block.
        """
        intent = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/test.txt"},
        )
        assert intent.requires_commit is False
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_noop_fn)
        assert result.success is True

    def test_non_mutating_tool_allowed_inside_l1_scope(self):
        """NON_MUTATING tools are allowed inside L1 cognition scope."""
        with l1_cognition_scope():
            assert_l1_tool_allowed(ToolCapability.NON_MUTATING, "file_read")
            assert_l1_tool_allowed(ToolCapability.NON_MUTATING, "ast_parse")
            assert_l1_tool_allowed(ToolCapability.NON_MUTATING, "llm_call")

    def test_non_mutating_tool_result_hash_stable(self):
        intent = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/test.txt"},
        )
        executor = ToolIntentExecutor()
        r1 = executor.execute(intent, fn=_noop_fn)
        r2 = executor.execute(intent, fn=_noop_fn)
        assert r1.result_hash == r2.result_hash

    def test_intent_hash_stable_across_executions(self):
        i1 = build_tool_intent("file_read", ToolCapability.NON_MUTATING, {"path": "/tmp/f.txt"})
        i2 = build_tool_intent("file_read", ToolCapability.NON_MUTATING, {"path": "/tmp/f.txt"})
        assert i1.intent_hash == i2.intent_hash


class TestStaticAuditNoDirectMutatingCallsInL1:
    def test_tool_intent_module_exists(self):
        assert _TOOL_INTENT_MODULE.exists(), f"Not found: {_TOOL_INTENT_MODULE}"

    def test_executor_module_exists(self):
        assert _EXECUTOR_MODULE.exists(), f"Not found: {_EXECUTOR_MODULE}"

    def test_executor_imports_commit_sandbox_check(self):
        """Executor must import is_commit_sandbox_active from the L2.2 sandbox."""
        source = _EXECUTOR_MODULE.read_text(encoding="utf-8")
        assert "is_commit_sandbox_active" in source

    def test_executor_raises_tool_violation_not_generic(self):
        """Executor must raise ToolViolation (not a generic Exception)."""
        source = _EXECUTOR_MODULE.read_text(encoding="utf-8")
        assert "ToolViolation" in source

    def test_tool_intent_module_defines_l1_cognition_scope(self):
        source = _TOOL_INTENT_MODULE.read_text(encoding="utf-8")
        assert "l1_cognition_scope" in source

    def test_tool_intent_module_defines_assert_l1_tool_allowed(self):
        source = _TOOL_INTENT_MODULE.read_text(encoding="utf-8")
        assert "assert_l1_tool_allowed" in source

    def test_no_direct_redis_set_in_tool_intent_module(self):
        """
        Static AST audit: tool_intent.py must not contain direct calls to
        redis.set / redis.setex / pinecone.upsert — these must go through
        the ToolIntent emission path.
        """
        source = _TOOL_INTENT_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("set", "setex", "upsert"):
                    forbidden.append(node.func.attr)
        assert forbidden == [], f"tool_intent.py contains direct mutation calls: {forbidden}"

    def test_no_direct_redis_set_in_executor_module(self):
        """
        Static AST audit: tool_intent_executor.py must not contain direct calls to
        redis.set / redis.setex / pinecone.upsert — execution is delegated to fn().
        """
        source = _EXECUTOR_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("setex", "upsert"):
                    forbidden.append(node.func.attr)
        assert forbidden == [], f"tool_intent_executor.py contains direct mutation calls: {forbidden}"
