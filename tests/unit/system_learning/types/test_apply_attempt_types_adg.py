"""ADG-driven tests for system_learning/types/apply_attempt_types.py — fan_in=4.

Contract tests for MetaLearningApplyAttemptArtifact and build_apply_attempt.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.interfaces.determinism_types import SemanticClockSnapshot
from system_learning.types.apply_attempt_types import (
    MetaLearningApplyAttemptArtifact,
    build_apply_attempt,
)


def _clock() -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=1)


def _applied(**kw) -> MetaLearningApplyAttemptArtifact:
    return build_apply_attempt(
        change_package_trace_id=kw.get("cp_trace_id", "cp-abc"),
        rollout_trace_id=kw.get("rollout_trace_id", "ro-abc"),
        policy_config_hash=kw.get("policy_hash", None),
        target_component=kw.get("target", "some.module"),
        apply_mode=kw.get("mode", "DRY_RUN"),
        outcome=kw.get("outcome", "APPLIED"),
        reject_reason=kw.get("reject_reason", None),
        details=kw.get("details", {}),
        semantic_clock=_clock(),
    )


class TestMetaLearningApplyAttemptArtifactImport:
    def test_class_importable(self):
        assert callable(MetaLearningApplyAttemptArtifact)

    def test_build_apply_attempt_callable(self):
        assert callable(build_apply_attempt)


class TestBuildApplyAttempt:
    def test_correct_artifact_type(self):
        a = _applied()
        assert a.artifact_type == "META_LEARNING_APPLY_ATTEMPT"

    def test_trace_id_deterministic(self):
        a1 = _applied()
        a2 = _applied()
        assert a1.trace_id == a2.trace_id

    def test_outcome_applied(self):
        a = _applied(outcome="APPLIED")
        assert a.outcome == "APPLIED"

    def test_outcome_rejected(self):
        a = _applied(outcome="REJECTED", reject_reason="POLICY_VIOLATION")
        assert a.outcome == "REJECTED"
        assert a.reject_reason == "POLICY_VIOLATION"

    def test_apply_mode_dry_run(self):
        a = _applied(mode="DRY_RUN")
        assert a.apply_mode == "DRY_RUN"

    def test_apply_mode_apply(self):
        a = _applied(mode="APPLY")
        assert a.apply_mode == "APPLY"

    def test_details_sorted(self):
        a = _applied(details={"z": "last", "a": "first"})
        keys = list(a.details.keys())
        assert keys == sorted(keys)

    def test_frozen_artifact(self):
        a = _applied()
        with pytest.raises(Exception):
            a.outcome = "REJECTED"  # type: ignore[misc]


class TestApplyAttemptSerialization:
    def test_to_dict_has_required_keys(self):
        a = _applied()
        d = a.to_dict()
        for key in ("artifact_type", "outcome", "apply_mode", "trace_id", "semantic_clock"):
            assert key in d, f"Missing key: {key}"

    def test_to_json_valid_json(self):
        import json
        a = _applied()
        parsed = json.loads(a.to_json())
        assert parsed["artifact_type"] == "META_LEARNING_APPLY_ATTEMPT"

    def test_to_json_deterministic(self):
        a1 = _applied()
        a2 = _applied()
        assert a1.to_json() == a2.to_json()


class TestApplyAttemptValidation:
    def test_wrong_artifact_type_raises(self):
        clock = _clock()
        with pytest.raises(ValueError, match="artifact_type"):
            MetaLearningApplyAttemptArtifact(
                artifact_type="WRONG_TYPE",  # type: ignore[arg-type]
                change_package_trace_id="cp",
                rollout_trace_id="ro",
                policy_config_hash=None,
                target_component="mod",
                apply_mode="DRY_RUN",
                outcome="APPLIED",
                reject_reason=None,
                details={},
                semantic_clock=clock,
                trace_id="t",
            )
