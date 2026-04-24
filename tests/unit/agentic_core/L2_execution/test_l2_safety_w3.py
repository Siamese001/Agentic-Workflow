"""W3 unit tests for the L2 best-practices gap plan (b7c4e2).

Covers:
- Thought-signature determinism + trace-id binding (G4)
- Tool Use Examples registration with 1..5 bound (G5)
- Execution markers default-safe lookup + parallel / idempotent / retry (G10)
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.l2_tool_enrichment import (
    DEFAULT_EXECUTION_MARKERS,
    ExecutionMarkers,
    ThoughtSignature,
    ToolUseExample,
    clear_all_registries,
    get_execution_markers,
    get_thought_signature,
    get_tool_examples,
    make_thought_signature,
    register_execution_markers,
    register_thought_signature,
    register_tool_examples,
)


class TestThoughtSignatures:
    def setup_method(self) -> None:
        clear_all_registries()

    def test_deterministic_for_same_inputs(self) -> None:
        a = make_thought_signature(
            reasoning_payload="hello", trace_id="t-1", turn_index=0
        )
        b = make_thought_signature(
            reasoning_payload="hello", trace_id="t-1", turn_index=0
        )
        assert a.signature == b.signature
        assert len(a.signature) == 32

    def test_differs_on_trace(self) -> None:
        a = make_thought_signature(reasoning_payload="x", trace_id="t-1")
        b = make_thought_signature(reasoning_payload="x", trace_id="t-2")
        assert a.signature != b.signature

    def test_differs_on_turn(self) -> None:
        a = make_thought_signature(reasoning_payload="x", trace_id="t", turn_index=0)
        b = make_thought_signature(reasoning_payload="x", trace_id="t", turn_index=1)
        assert a.signature != b.signature

    def test_register_and_lookup(self) -> None:
        sig = make_thought_signature(reasoning_payload="x", trace_id="t")
        register_thought_signature("tool.foo", sig)
        assert get_thought_signature("tool.foo") is sig
        assert get_thought_signature("tool.missing") is None

    def test_register_rejects_empty_tool_name(self) -> None:
        sig = make_thought_signature(reasoning_payload="x", trace_id="t")
        with pytest.raises(ValueError):
            register_thought_signature("", sig)

    def test_make_rejects_empty_trace(self) -> None:
        with pytest.raises(ValueError):
            make_thought_signature(reasoning_payload="x", trace_id="")

    def test_to_dict_shape(self) -> None:
        sig = make_thought_signature(
            reasoning_payload="x", trace_id="t-1", model_hint="gemini-3"
        )
        d = sig.to_dict()
        assert d["trace_id"] == "t-1"
        assert d["model_hint"] == "gemini-3"
        assert len(d["signature"]) == 32


class TestToolUseExamples:
    def setup_method(self) -> None:
        clear_all_registries()

    def test_register_one_example(self) -> None:
        ex = ToolUseExample(description="basic", args={"x": 1})
        register_tool_examples("tool.foo", [ex])
        got = get_tool_examples("tool.foo")
        assert len(got) == 1
        assert got[0] is ex

    def test_default_empty_tuple(self) -> None:
        assert get_tool_examples("tool.missing") == ()

    def test_register_five_examples_ok(self) -> None:
        exs = [ToolUseExample(description=f"e{i}", args={"i": i}) for i in range(5)]
        register_tool_examples("tool.foo", exs)
        assert len(get_tool_examples("tool.foo")) == 5

    def test_register_zero_rejected(self) -> None:
        with pytest.raises(ValueError):
            register_tool_examples("tool.foo", [])

    def test_register_six_rejected(self) -> None:
        exs = [ToolUseExample(description=f"e{i}", args={}) for i in range(6)]
        with pytest.raises(ValueError):
            register_tool_examples("tool.foo", exs)

    def test_register_rejects_empty_tool_name(self) -> None:
        ex = ToolUseExample(description="x", args={})
        with pytest.raises(ValueError):
            register_tool_examples("", [ex])

    def test_to_dict_shape(self) -> None:
        ex = ToolUseExample(
            description="send order",
            args={"sku": "A1", "qty": 2},
            expected_shape={"order_id": "str"},
            notes="covers partial spec",
        )
        d = ex.to_dict()
        assert d["args"] == {"sku": "A1", "qty": 2}
        assert d["expected_shape"] == {"order_id": "str"}


class TestExecutionMarkers:
    def setup_method(self) -> None:
        clear_all_registries()

    def test_default_is_safest(self) -> None:
        m = get_execution_markers("tool.unknown")
        assert m is DEFAULT_EXECUTION_MARKERS
        assert m.parallel_safe is False
        assert m.idempotent is False
        assert m.max_retries == 0

    def test_register_and_lookup(self) -> None:
        register_execution_markers(
            ExecutionMarkers(
                tool_name="cache.get",
                parallel_safe=True,
                idempotent=True,
                max_retries=2,
                retry_backoff_ms=100,
                rationale="pure read, no side effects",
            )
        )
        m = get_execution_markers("cache.get")
        assert m.parallel_safe is True
        assert m.idempotent is True
        assert m.max_retries == 2

    def test_invalid_inputs(self) -> None:
        with pytest.raises(ValueError):
            register_execution_markers(ExecutionMarkers(tool_name=""))
        with pytest.raises(ValueError):
            register_execution_markers(
                ExecutionMarkers(tool_name="t", max_retries=-1)
            )
        with pytest.raises(ValueError):
            register_execution_markers(
                ExecutionMarkers(tool_name="t", retry_backoff_ms=-5)
            )

    def test_to_dict_shape(self) -> None:
        m = ExecutionMarkers(
            tool_name="orders.submit",
            parallel_safe=False,
            idempotent=True,
            max_retries=3,
            retry_backoff_ms=250,
            rationale="ok to retry with same idempotency key",
        )
        d = m.to_dict()
        assert d["idempotent"] is True
        assert d["max_retries"] == 3
