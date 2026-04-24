"""W4 unit tests for the L2 best-practices gap plan (b7c4e2).

Covers:
- ToolSearchIndex: register, search ranking, k cap, stable tie-break (G6)
- ProgrammaticToolRunner: sub-context summarization + intermediate
  suppression + error wrapping (G7)
- KillSwitchRegistry: trip / is_tripped / idempotency / raise_if_tripped
  / untrip / default registry module-level API (G12)
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement.kill_switch import (
    KillSwitchRegistry,
    KillSwitchTripped,
    default_registry,
    is_tripped,
    trip,
    untrip,
)
from agentic_core.L2_execution.reasoning.programmatic_tool_runner import (
    ProgrammaticToolRunner,
    SubContextToolError,
    ToolStep,
)
from agentic_core.L2_execution.reasoning.tool_search import (
    ToolSearchEntry,
    ToolSearchIndex,
)


# ---------------------------------------------------------------------------
# ToolSearchIndex (G6)
# ---------------------------------------------------------------------------


class TestToolSearchIndex:
    def test_register_and_size(self) -> None:
        idx = ToolSearchIndex()
        idx.register(ToolSearchEntry("tool.a", "alpha reads records"))
        idx.register(ToolSearchEntry("tool.b", "beta writes records"))
        assert idx.size() == 2
        assert idx.has("tool.a")
        assert idx.has("tool.b")

    def test_search_ranks_by_term_overlap(self) -> None:
        idx = ToolSearchIndex()
        idx.register(ToolSearchEntry("orders.submit", "submit customer order"))
        idx.register(ToolSearchEntry("orders.cancel", "cancel customer order"))
        idx.register(ToolSearchEntry("cache.get", "read cached value"))
        hits = idx.search("submit customer order", k=3)
        assert hits[0].tool_name == "orders.submit"
        names = [h.tool_name for h in hits]
        assert "cache.get" not in names  # zero overlap

    def test_k_cap(self) -> None:
        idx = ToolSearchIndex()
        for i in range(25):
            idx.register(ToolSearchEntry(f"tool.{i}", f"sample description {i} common"))
        hits = idx.search("common", k=10)
        assert len(hits) == 10

    def test_k_must_be_positive(self) -> None:
        idx = ToolSearchIndex()
        idx.register(ToolSearchEntry("t", "x"))
        with pytest.raises(ValueError):
            idx.search("x", k=0)

    def test_empty_query_returns_empty(self) -> None:
        idx = ToolSearchIndex()
        idx.register(ToolSearchEntry("t", "x"))
        assert idx.search("", k=5) == []

    def test_reregister_updates_doc_freq(self) -> None:
        idx = ToolSearchIndex()
        idx.register(ToolSearchEntry("t", "alpha beta gamma"))
        idx.register(ToolSearchEntry("t", "delta epsilon"))
        hits = idx.search("alpha", k=5)
        assert hits == []  # old description replaced
        hits = idx.search("delta", k=5)
        assert len(hits) == 1

    def test_tie_break_stable(self) -> None:
        idx = ToolSearchIndex()
        idx.register(ToolSearchEntry("t.one", "shared term"))
        idx.register(ToolSearchEntry("t.two", "shared term"))
        hits = idx.search("shared term", k=2)
        # Insertion order resolves ties
        assert [h.tool_name for h in hits] == ["t.one", "t.two"]


# ---------------------------------------------------------------------------
# ProgrammaticToolRunner (G7)
# ---------------------------------------------------------------------------


def _stub_executor(tool_name: str, args: dict):
    if tool_name == "search":
        return list(range(100))  # large intermediate
    if tool_name == "filter":
        return [x for x in args["input"] if x % 2 == 0]
    if tool_name == "fail":
        raise RuntimeError("boom")
    return {"echo": args}


class TestProgrammaticToolRunner:
    def test_chain_hides_intermediates_by_default(self) -> None:
        runner = ProgrammaticToolRunner(tool_executor=_stub_executor)
        outputs_seen: list = []

        def _filter_transform(raw):
            # Use the raw result as input for a compose-style chain.
            outputs_seen.append(raw)
            return [x for x in raw if x % 2 == 0]

        result = runner.run(
            steps=[
                ToolStep("search", {"q": "x"}, transform=_filter_transform),
            ],
            summarize=lambda outs: {"count": len(outs[-1])},
        )
        assert result.summary == {"count": 50}
        assert result.intermediates == []  # suppressed by default
        assert result.intermediates_count == 1
        assert result.step_names == ["search"]

    def test_keep_intermediates(self) -> None:
        runner = ProgrammaticToolRunner(tool_executor=_stub_executor)
        result = runner.run(
            steps=[ToolStep("echo", {"k": 1})],
            summarize=lambda outs: outs[-1],
            keep_intermediates=True,
        )
        assert result.intermediates == [{"echo": {"k": 1}}]

    def test_discard_intermediates(self) -> None:
        runner = ProgrammaticToolRunner(tool_executor=_stub_executor)
        result = runner.run(
            steps=[ToolStep("echo", {"k": 1})],
            summarize=lambda outs: "ok",
            keep_intermediates=True,
        )
        assert len(result.intermediates) == 1
        result.discard_intermediates()
        assert result.intermediates == []

    def test_error_wrapped(self) -> None:
        runner = ProgrammaticToolRunner(tool_executor=_stub_executor)
        with pytest.raises(SubContextToolError) as exc:
            runner.run(
                steps=[ToolStep("fail", {})],
                summarize=lambda outs: outs,
            )
        assert exc.value.step_index == 0
        assert exc.value.tool_name == "fail"
        assert isinstance(exc.value.cause, RuntimeError)


# ---------------------------------------------------------------------------
# KillSwitch (G12)
# ---------------------------------------------------------------------------


class TestKillSwitch:
    def setup_method(self) -> None:
        default_registry().clear()

    def teardown_method(self) -> None:
        default_registry().clear()

    def test_trip_and_is_tripped(self) -> None:
        assert is_tripped("L-1") is False
        rec = trip(lineage_id="L-1", reason="user cancelled")
        assert rec.lineage_id == "L-1"
        assert is_tripped("L-1") is True

    def test_trip_is_idempotent(self) -> None:
        rec1 = trip(lineage_id="L-2", reason="first")
        rec2 = trip(lineage_id="L-2", reason="second")
        assert rec1 is rec2
        assert rec1.reason == "first"

    def test_raise_if_tripped(self) -> None:
        reg = KillSwitchRegistry()
        reg.trip(lineage_id="L-3", reason="policy block")
        with pytest.raises(KillSwitchTripped) as exc:
            reg.raise_if_tripped("L-3")
        assert exc.value.record.reason == "policy block"

    def test_raise_if_tripped_no_op_when_clean(self) -> None:
        reg = KillSwitchRegistry()
        reg.raise_if_tripped("L-never")  # no raise

    def test_untrip(self) -> None:
        trip(lineage_id="L-4", reason="transient")
        assert untrip("L-4") is True
        assert is_tripped("L-4") is False
        assert untrip("L-4") is False  # idempotent clear

    def test_invalid_inputs(self) -> None:
        with pytest.raises(ValueError):
            trip(lineage_id="", reason="r")
        with pytest.raises(ValueError):
            trip(lineage_id="L", reason="")

    def test_record_to_dict(self) -> None:
        rec = trip(
            lineage_id="L-5",
            reason="manual",
            tripped_by="operator",
            metadata={"ticket": "INC-1"},
        )
        d = rec.to_dict()
        assert d["lineage_id"] == "L-5"
        assert d["tripped_by"] == "operator"
        assert d["metadata"] == {"ticket": "INC-1"}

    def test_snapshot_is_copy(self) -> None:
        reg = KillSwitchRegistry()
        reg.trip(lineage_id="L-6", reason="x")
        snap = reg.snapshot()
        reg.clear()
        # snap retains
        assert "L-6" in snap
        assert reg.is_tripped("L-6") is False
