"""Tests for ``normalize_ag5_terminal_input``."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import SourceType
from agentic_core.runtime.exit.exit_review_normalizer import (
    AG5NormalizationError,
    normalize_ag5_terminal_input,
)


def test_normalize_app_binding_compatibility_minimal() -> None:
    raw = {
        "source_type": "APP_BINDING_COMPATIBILITY_PACKAGE",
        "route_contract_ref": "route://native-test",
        "route_id": "R_TEST",
        "replay_key": "replay-native-test",
        "terminal_class": "answer_only",
        "path_class": "neutral",
        "policy_hash": "ph-native",
        "route_contract": {"policy_hash": "ph-native"},
        "output": {"completion_score": 1.0},
        "otel_spans": {"spans": {"trace_root": {"present": True}}},
    }
    pkt = normalize_ag5_terminal_input(raw)
    assert pkt.source_type == SourceType.APP_BINDING_COMPATIBILITY_PACKAGE
    assert pkt.replay_key == "replay-native-test"
    assert pkt.terminal_class == "answer_only"


def test_normalize_rejects_unknown_source_type() -> None:
    with pytest.raises(AG5NormalizationError):
        normalize_ag5_terminal_input(
            {
                "source_type": "NOT_A_REAL_SOURCE",
                "route_id": "x",
                "replay_key": "r",
                "terminal_class": "answer_only",
                "path_class": "neutral",
            },
        )
