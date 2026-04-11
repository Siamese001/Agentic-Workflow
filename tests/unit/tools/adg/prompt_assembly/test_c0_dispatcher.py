"""Tests for tools.adg.prompt_assembly.c0_dispatcher.assemble_from_c0_contract().

Verifies:
- Returns None on abstain path (translate_contract returns None bundle).
- Returns PromptEnvelope on valid path.
- Default intent selects executive_summary packet type.
- Path/graph intent keywords select graph_path_explanation packet type.
- replay_extras forwarded verbatim to _assemble().
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (
    C0EvidenceContract,
    CitedSpan,
)
from tools.adg.prompt_assembly.c0_dispatcher import (
    _GRAPH_INTENT_KEYWORDS,
    _maybe_write_packet,
    assemble_from_c0_contract,
)
from tools.adg.prompt_assembly.contracts import (
    EvidenceBundle,
    PromptAssemblyStatus,
    PromptEnvelope,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_cited_span(n: int = 0) -> CitedSpan:
    return CitedSpan(
        span_id=f"chunk-{n}",
        source_ref=f"doc-{n}",
        text_snippet=f"snippet text {n}",
        relevance_score=0.85,
        chunk_hash=f"hash{n:08x}",
    )


def _make_valid_contract(n_spans: int = 2) -> C0EvidenceContract:
    spans = tuple(_make_cited_span(i) for i in range(n_spans))
    return C0EvidenceContract.build(
        retrieval_id="ret-001",
        request_id="req-001",
        coverage_score=0.80,
        cited_spans=spans,
    )


def _make_abstain_contract() -> C0EvidenceContract:
    return C0EvidenceContract.build(
        retrieval_id="ret-abstain",
        request_id="req-abstain",
        coverage_score=0.05,
        cited_spans=(),
    )


def _make_bundle(coverage: float = 0.80) -> EvidenceBundle:
    return EvidenceBundle(items=[], coverage_score=coverage)


def _make_fake_envelope() -> PromptEnvelope:
    env = MagicMock(spec=PromptEnvelope)
    env.assembly_status = MagicMock()
    env.assembly_status.ok = True
    return env


# ---------------------------------------------------------------------------
# Abstain short-circuit
# ---------------------------------------------------------------------------


def test_dispatcher_returns_none_when_translate_contract_yields_none_bundle():
    contract = _make_valid_contract()
    with patch(
        "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
        return_value=(None, {}),
    ):
        result = assemble_from_c0_contract(contract, "do the task")
    assert result is None


def test_dispatcher_returns_none_for_explicit_abstain_contract():
    """Abstain contract (abstain_hint=True) → bridge returns None bundle."""
    contract = _make_abstain_contract()
    with patch(
        "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
        return_value=(None, {"abstain_reason": "low_coverage"}),
    ):
        result = assemble_from_c0_contract(contract, "task")
    assert result is None


# ---------------------------------------------------------------------------
# Valid path — returns PromptEnvelope
# ---------------------------------------------------------------------------


def test_dispatcher_returns_prompt_envelope_on_valid_path():
    bundle = _make_bundle()
    fake_envelope = _make_fake_envelope()
    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, {}),
        ),
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            return_value=fake_envelope,
        ),
    ):
        result = assemble_from_c0_contract(_make_valid_contract(), "task block")
    assert result is fake_envelope


# ---------------------------------------------------------------------------
# Packet type selection
# ---------------------------------------------------------------------------


def test_dispatcher_default_packet_type_is_executive_summary():
    bundle = _make_bundle()
    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, {}),
        ) as mock_translate,
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            return_value=_make_fake_envelope(),
        ),
    ):
        assemble_from_c0_contract(_make_valid_contract(), "task", intent_hint="")
    _, packet_type_arg = mock_translate.call_args[0]
    assert packet_type_arg == "executive_summary"


def test_dispatcher_no_hint_defaults_to_executive_summary():
    bundle = _make_bundle()
    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, {}),
        ) as mock_translate,
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            return_value=_make_fake_envelope(),
        ),
    ):
        assemble_from_c0_contract(_make_valid_contract(), "task")
    _, packet_type_arg = mock_translate.call_args[0]
    assert packet_type_arg == "executive_summary"


@pytest.mark.parametrize(
    "hint",
    [
        "shortest path between two nodes",
        "graph traversal algorithm",
        "route from A to B",
        "find the node",
        "count hops in network",
        "edge between components",
    ],
)
def test_dispatcher_graph_keywords_select_graph_path_explanation(hint: str):
    bundle = _make_bundle()
    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, {}),
        ) as mock_translate,
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            return_value=_make_fake_envelope(),
        ),
    ):
        assemble_from_c0_contract(_make_valid_contract(), "task", intent_hint=hint)
    _, packet_type_arg = mock_translate.call_args[0]
    assert packet_type_arg == "graph_path_explanation", f"Expected graph_path_explanation for hint={hint!r}"


def test_dispatcher_non_graph_hint_stays_executive_summary():
    bundle = _make_bundle()
    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, {}),
        ) as mock_translate,
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            return_value=_make_fake_envelope(),
        ),
    ):
        assemble_from_c0_contract(_make_valid_contract(), "task", intent_hint="summarize the findings")
    _, packet_type_arg = mock_translate.call_args[0]
    assert packet_type_arg == "executive_summary"


def test_graph_intent_keywords_constant_contains_expected_words():
    expected = {"path", "graph", "route", "hop", "hops", "edge", "node"}
    assert expected.issubset(_GRAPH_INTENT_KEYWORDS)


# ---------------------------------------------------------------------------
# replay_extras forwarding
# ---------------------------------------------------------------------------


def test_dispatcher_replay_extras_forwarded_to_assemble():
    bundle = _make_bundle()
    replay = {
        "evidence_hmac": "hmac-value-abc",
        "retrieval_id": "ret-001",
        "coverage_score": 0.80,
    }
    captured: dict[str, Any] = {}

    def _capture_assemble(_template, _must, _opt, _task, replay_extras=None, pre_shaped_bundle=None):
        captured["replay_extras"] = replay_extras
        captured["pre_shaped_bundle"] = pre_shaped_bundle
        return _make_fake_envelope()

    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, replay),
        ),
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            side_effect=_capture_assemble,
        ),
    ):
        assemble_from_c0_contract(_make_valid_contract(), "do the task")

    assert captured["replay_extras"] == replay


def test_dispatcher_pre_shaped_bundle_forwarded_to_assemble():
    bundle = _make_bundle(coverage=0.75)
    captured: dict[str, Any] = {}

    def _capture_assemble(_template, _must, _opt, _task, pre_shaped_bundle=None, **_kw):
        captured["pre_shaped_bundle"] = pre_shaped_bundle
        return _make_fake_envelope()

    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, {}),
        ),
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            side_effect=_capture_assemble,
        ),
    ):
        assemble_from_c0_contract(_make_valid_contract(), "task")

    assert captured["pre_shaped_bundle"] is bundle


def test_dispatcher_empty_lists_passed_to_assemble_must_and_opt():
    """Dispatcher always passes empty must_items and opt_items to _assemble."""
    bundle = _make_bundle()
    captured: dict[str, Any] = {}

    def _capture_assemble(_template, must, opt, _task, **_kw):
        captured["must"] = must
        captured["opt"] = opt
        return _make_fake_envelope()

    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, {}),
        ),
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            side_effect=_capture_assemble,
        ),
    ):
        assemble_from_c0_contract(_make_valid_contract(), "task")

    assert captured["must"] == []
    assert captured["opt"] == []


def test_dispatcher_task_block_forwarded_verbatim():
    bundle = _make_bundle()
    captured: dict[str, Any] = {}
    expected_task = "Analyse the incident timeline and provide root cause."

    def _capture_assemble(_template, _must, _opt, task, **_kw):
        captured["task_block"] = task
        return _make_fake_envelope()

    with (
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher.translate_contract",
            return_value=(bundle, {}),
        ),
        patch(
            "tools.adg.prompt_assembly.c0_dispatcher._assemble",
            side_effect=_capture_assemble,
        ),
    ):
        assemble_from_c0_contract(_make_valid_contract(), expected_task)

    assert captured["task_block"] == expected_task


# ---------------------------------------------------------------------------
# _maybe_write_packet — write guard tests
# ---------------------------------------------------------------------------


def _make_envelope_for_write(
    result: str = "pass",
    replay: dict | None = None,
    with_status: bool = True,
) -> PromptEnvelope:
    """Build a minimal PromptEnvelope with controlled assembly_result."""
    status = (
        PromptAssemblyStatus(
            packet_type="executive_summary",
            assembly_result=result,  # type: ignore[arg-type]
            replay_metadata=replay or {},
        )
        if with_status
        else None
    )
    return PromptEnvelope(
        packet_type="executive_summary",
        assembly_status=status,
        replay_metadata=replay or {},
    )


def test_write_guard_pass_creates_file(tmp_path):
    envelope = _make_envelope_for_write(result="pass")
    written = _maybe_write_packet(envelope, tmp_path)
    assert written is not None
    assert written.exists()
    assert written.suffix == ".json"


def test_write_guard_partial_creates_file(tmp_path):
    envelope = _make_envelope_for_write(result="partial")
    written = _maybe_write_packet(envelope, tmp_path)
    assert written is not None
    assert written.exists()


def test_write_guard_fail_does_not_write(tmp_path):
    envelope = _make_envelope_for_write(result="fail")
    written = _maybe_write_packet(envelope, tmp_path)
    assert written is None
    assert list(tmp_path.iterdir()) == []


def test_write_guard_none_output_dir_does_not_write():
    envelope = _make_envelope_for_write(result="pass")
    written = _maybe_write_packet(envelope, None)
    assert written is None


def test_write_guard_none_assembly_status_does_not_write(tmp_path):
    envelope = _make_envelope_for_write(result="pass", with_status=False)
    written = _maybe_write_packet(envelope, tmp_path)
    assert written is None
    assert list(tmp_path.iterdir()) == []


def test_write_guard_replay_metadata_preserved_in_written_json(tmp_path):
    import json

    replay = {"evidence_hmac": "hmac-abc123", "retrieval_id": "ret-007", "coverage_score": 0.91}
    envelope = _make_envelope_for_write(result="pass", replay=replay)
    written = _maybe_write_packet(envelope, tmp_path)
    assert written is not None
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["replay_metadata"] == replay


def test_write_guard_filename_includes_packet_type_and_id(tmp_path):
    envelope = _make_envelope_for_write(result="pass")
    written = _maybe_write_packet(envelope, tmp_path)
    assert written is not None
    assert f"packet_{envelope.packet_type}" in written.name
    assert envelope.packet_id in written.name


def test_write_guard_creates_output_dir_if_missing(tmp_path):
    nested = tmp_path / "deep" / "nested"
    envelope = _make_envelope_for_write(result="pass")
    written = _maybe_write_packet(envelope, nested)
    assert written is not None
    assert nested.exists()
    assert written.exists()
