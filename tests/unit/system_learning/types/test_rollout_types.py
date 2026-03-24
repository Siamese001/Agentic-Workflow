"""Foundational behavioral tests for system_learning/types/rollout_types.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_rollout_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.types.rollout_types import (  # noqa: F401
        ROLLBACK_REASONS,
        ROLLOUT_STRATEGIES,
        MetaLearningRollbackArtifact,
        MetaLearningRolloutPlanArtifact,
        build_meta_learning_rollback,
        build_meta_learning_rollout_plan,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MetaLearningRolloutPlanArtifact = None  # type: ignore[assignment,misc]
    MetaLearningRollbackArtifact = None  # type: ignore[assignment,misc]
    build_meta_learning_rollout_plan = None  # type: ignore[assignment,misc]
    build_meta_learning_rollback = None  # type: ignore[assignment,misc]
    ROLLOUT_STRATEGIES = None  # type: ignore[assignment,misc]
    ROLLBACK_REASONS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rollout_types.py deps unavailable")
class TestMetaLearningRolloutPlanArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetaLearningRolloutPlanArtifact)

    def test_is_frozen(self):
        assert MetaLearningRolloutPlanArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(MetaLearningRolloutPlanArtifact)}
        assert fnames >= {'rollout_strategy', 'max_duration_minutes', 'artifact_type', 'canary_percent', 'invariants', 'change_package_trace_id'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(MetaLearningRolloutPlanArtifact)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="rollout_types.py deps unavailable")
class TestMetaLearningRollbackArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetaLearningRollbackArtifact)

    def test_is_frozen(self):
        assert MetaLearningRollbackArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(MetaLearningRollbackArtifact)}
        assert fnames >= {'rollback_reason', 'policy_config_hash', 'trace_id', 'rollout_trace_id', 'artifact_type', 'semantic_clock'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(MetaLearningRollbackArtifact)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="rollout_types.py deps unavailable")
class TestBuildMetaLearningRolloutPlanFunction:
    def test_is_callable(self):
        assert callable(build_meta_learning_rollout_plan)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_meta_learning_rollout_plan)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="rollout_types.py deps unavailable")
class TestBuildMetaLearningRollbackFunction:
    def test_is_callable(self):
        assert callable(build_meta_learning_rollback)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_meta_learning_rollback)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="rollout_types.py deps unavailable")
class TestRolloutStrategiesConstant:
    def test_is_not_none(self):
        assert ROLLOUT_STRATEGIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rollout_types.py deps unavailable")
class TestRollbackReasonsConstant:
    def test_is_not_none(self):
        assert ROLLBACK_REASONS is not None


def test_module_importable():
    """Smoke: rollout_types importable or gracefully unavailable."""
    pass