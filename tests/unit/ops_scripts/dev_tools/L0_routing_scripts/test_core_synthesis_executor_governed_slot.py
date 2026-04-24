"""Tests for ``CoreSynthesisExecutor.build_governed_slot`` (RH6B.3).

Plan: ``prompt-reception-followups-a7b3c4.md`` phase W6b RH6B.3. The
executor's report text now routes through
``synthesis_bridge.wrap_synthesis_output`` to emit a governed ``C0``
``AuthoritySlot`` instead of bypassing the prompt-assembly pipeline
with raw prose.
"""

from __future__ import annotations

import importlib
from unittest.mock import patch


def _load_executor_class():
    """Dynamic import keeps this test resilient to path moves."""
    module = importlib.import_module(
        "ops_scripts.dev_tools.L0_routing_scripts.core_synthesis_executor"
    )
    return module.CoreSynthesisExecutor


def test_build_governed_slot_returns_c0_info_authority_with_provenance() -> None:
    """RH6B.3: non-empty report → ``C0`` slot, INFO authority, provenance
    producer = the executor's fully-qualified module path."""
    CoreSynthesisExecutor = _load_executor_class()
    # Skip heavy __init__ side-effects (filesystem scans, lifecycle traces);
    # build_governed_slot is a pure, self-contained method.
    executor = CoreSynthesisExecutor.__new__(CoreSynthesisExecutor)

    slot = executor.build_governed_slot("Executive summary: synthesis completed cleanly.")

    assert slot is not None
    assert slot.slot_code == "C0"
    # INFO is the canonical C0 authority level (see compiled_artifact.AuthorityLevel).
    from agentic_core.L2_execution.reasoning.compiled_artifact import AuthorityLevel
    assert slot.authority_level == AuthorityLevel.INFO
    assert (
        slot.metadata["synthesis_producer"]
        == "ops_scripts.dev_tools.L0_routing_scripts.core_synthesis_executor"
    )
    assert slot.metadata["synthesis_kind"] == "plan"
    assert slot.metadata["synthesis_truncated"] is False


def test_build_governed_slot_forwards_trace_ids() -> None:
    """RH6B.3: ``trace_ids`` kwarg propagates into
    ``SynthesisProvenance.source_trace_ids`` so replay tooling can
    cross-link the governed slot to its upstream traces."""
    CoreSynthesisExecutor = _load_executor_class()
    executor = CoreSynthesisExecutor.__new__(CoreSynthesisExecutor)

    slot = executor.build_governed_slot(
        "Some report body.",
        trace_ids=("trace-a", "trace-b"),
    )
    assert slot is not None
    assert slot.metadata["synthesis_source_trace_ids"] == ["trace-a", "trace-b"]


def test_build_governed_slot_rejects_empty_text() -> None:
    """RH6B.3: empty text → None (not an error). ``None`` is the
    documented sentinel for downstream skip-and-continue."""
    CoreSynthesisExecutor = _load_executor_class()
    executor = CoreSynthesisExecutor.__new__(CoreSynthesisExecutor)

    assert executor.build_governed_slot("") is None
    assert executor.build_governed_slot("   \n\t   ") is None


def test_build_governed_slot_surfaces_bridge_rejection_as_none(capsys) -> None:
    """RH6B.3: downstream ``SynthesisBridgeError`` (e.g. from future
    stricter validation) is caught and surfaced as ``None`` + a warning
    line so the CLI report-write path never aborts."""
    CoreSynthesisExecutor = _load_executor_class()
    executor = CoreSynthesisExecutor.__new__(CoreSynthesisExecutor)

    target = (
        "ops_scripts.dev_tools.L0_routing_scripts."
        "core_synthesis_executor.wrap_synthesis_output"
    )
    from agentic_core.L2_execution.enforcement.synthesis_bridge import (
        SynthesisBridgeError,
    )

    with patch(target, side_effect=SynthesisBridgeError("simulated failure")):
        slot = executor.build_governed_slot("non-empty report")

    assert slot is None
    captured = capsys.readouterr()
    assert "synthesis_bridge rejected" in captured.out


def test_build_governed_slot_marks_truncation_on_large_report() -> None:
    """RH6B.3: reports larger than the default 16 KiB budget are
    truncated and the metadata records the original byte count."""
    CoreSynthesisExecutor = _load_executor_class()
    executor = CoreSynthesisExecutor.__new__(CoreSynthesisExecutor)

    # 20 KiB of content — exceeds the 16 KiB default budget.
    big_report = "A" * (20 * 1024)
    slot = executor.build_governed_slot(big_report)

    assert slot is not None
    assert slot.metadata["synthesis_truncated"] is True
    assert slot.metadata["synthesis_original_bytes"] == 20 * 1024
    assert slot.metadata["synthesis_max_bytes"] == 16 * 1024
    # Truncation marker preserved.
    assert "[TRUNCATED]" in slot.content
