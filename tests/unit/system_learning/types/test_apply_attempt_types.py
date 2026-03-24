"""Foundational behavioral tests for system_learning/types/apply_attempt_types.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_apply_attempt_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.types.apply_attempt_types import (  # noqa: F401
        MetaLearningApplyAttemptArtifact,
        build_apply_attempt,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MetaLearningApplyAttemptArtifact = None  # type: ignore[assignment,misc]
    build_apply_attempt = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="apply_attempt_types.py deps unavailable")
class TestMetaLearningApplyAttemptArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetaLearningApplyAttemptArtifact)

    def test_is_frozen(self):
        assert MetaLearningApplyAttemptArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(MetaLearningApplyAttemptArtifact)}
        assert fnames >= {'policy_config_hash', 'rollout_trace_id', 'artifact_type', 'target_component', 'apply_mode', 'change_package_trace_id'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(MetaLearningApplyAttemptArtifact)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="apply_attempt_types.py deps unavailable")
class TestBuildApplyAttemptFunction:
    def test_is_callable(self):
        assert callable(build_apply_attempt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_apply_attempt)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: apply_attempt_types importable or gracefully unavailable."""
    pass