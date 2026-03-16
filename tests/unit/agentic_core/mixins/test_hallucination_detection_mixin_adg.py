"""ADG-driven tests for mixins/hallucination_detection_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hallucination_detection_mixin_adg")
_emit_applies_guardrail("p0", "test_hallucination_detection_mixin_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_hallucination_detection_mixin_adg", "policy_binding")
_emit_snapshots_state("p0", "test_hallucination_detection_mixin_adg", "state_snapshot")
emit_replay_key("p0", "test_hallucination_detection_mixin_adg")
emit_determinism_digest("p0", "test_hallucination_detection_mixin_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.mixins.hallucination_detection_mixin import HallucinationDetectionMixin


class TestHallucinationDetectionMixin:
    def test_importable(self):
        assert callable(HallucinationDetectionMixin)

    def test_hallucination_cache_default_empty(self):
        assert HallucinationDetectionMixin._hallucination_cache == {}

    def test_has_verify_target_exists(self):
        assert hasattr(HallucinationDetectionMixin, "verify_target_exists")

    def test_verify_nonexistent_file_returns_false(self, tmp_path):
        mixin = HallucinationDetectionMixin()
        result = mixin.verify_target_exists(
            file_path=tmp_path / "nonexistent.py",
            target_type="function",
            target_name="foo",
        )
        assert result is False

    def test_verify_existing_function(self, tmp_path):
        src = tmp_path / "module.py"
        src.write_text("def my_func():\n    pass\n", encoding="utf-8")
        mixin = HallucinationDetectionMixin()
        result = mixin.verify_target_exists(
            file_path=src,
            target_type="function",
            target_name="my_func",
        )
        assert result is True
