"""ADG-driven tests for L2 execution type modules — fan_in=1.

Covers: l2_phase_spec, replay_envelope_types, tool_args_types.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# l2_phase_spec
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.types.l2_phase_spec import (
    L2ExecutionPlan,
    LEGACY_MIRROR_PLAN,
    PhaseSpec,
)


class TestPhaseSpec:
    def test_creates_with_name_only(self):
        spec = PhaseSpec(name="pre_audit")
        assert spec.name == "pre_audit"

    def test_frozen_dataclass(self):
        spec = PhaseSpec(name="discovery")
        with pytest.raises((AttributeError, TypeError)):
            spec.name = "new_name"  # type: ignore[misc]

    def test_guardian_ids_default_empty(self):
        spec = PhaseSpec(name="healing")
        assert spec.guardian_ids == ()

    def test_healer_ids_default_empty(self):
        spec = PhaseSpec(name="healing")
        assert spec.healer_ids == ()

    def test_approval_required_default_false(self):
        spec = PhaseSpec(name="certification")
        assert spec.approval_required is False

    def test_creates_with_guardian_ids(self):
        spec = PhaseSpec(name="pre_audit", guardian_ids=("g1", "g2"))
        assert "g1" in spec.guardian_ids


class TestL2ExecutionPlan:
    def test_creates_with_phases(self):
        plan = L2ExecutionPlan(
            phases=(PhaseSpec(name="p1"), PhaseSpec(name="p2"))
        )
        assert len(plan.phases) == 2

    def test_frozen(self):
        plan = L2ExecutionPlan(phases=(PhaseSpec(name="p1"),))
        with pytest.raises((AttributeError, TypeError)):
            plan.phases = ()  # type: ignore[misc]


class TestLegacyMirrorPlan:
    def test_is_l2_execution_plan(self):
        assert isinstance(LEGACY_MIRROR_PLAN, L2ExecutionPlan)

    def test_has_phases(self):
        assert len(LEGACY_MIRROR_PLAN.phases) > 0

    def test_first_phase_pre_audit(self):
        assert LEGACY_MIRROR_PLAN.phases[0].name == "pre_audit"

    def test_contains_discovery(self):
        names = [p.name for p in LEGACY_MIRROR_PLAN.phases]
        assert "discovery" in names

    def test_contains_healing(self):
        names = [p.name for p in LEGACY_MIRROR_PLAN.phases]
        assert "healing" in names


# ---------------------------------------------------------------------------
# replay_envelope_types
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.types.replay_envelope_types import ReplayEnvelope


class TestReplayEnvelope:
    def _make_envelope(self, **kwargs):
        defaults = dict(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-4",
            model_version="1.0",
            temperature=0.7,
            allowed_model_policy_version="v1",
            policy_version="v1",
            gateway_version="v1",
            embedder_provider="openai",
            embedder_model="text-embedding-3-small",
            embedder_dim=1536,
            normalization_policy="l2",
            chunking_policy="fixed",
            distance_metric="cosine",
            retrieval_top_k=5,
            retrieval_similarity_cutoff=0.7,
            agent_registry_hash="xyz789",
            deterministic_engine_version="1.0.0",
        )
        defaults.update(kwargs)
        return ReplayEnvelope(**defaults)

    def test_creates_with_required_fields(self):
        env = self._make_envelope()
        assert env.model_id == "gpt-4"

    def test_frozen_dataclass(self):
        env = self._make_envelope()
        with pytest.raises((AttributeError, TypeError)):
            env.model_id = "other"  # type: ignore[misc]

    def test_code_commit_hash_optional(self):
        env = self._make_envelope(code_commit_hash=None)
        assert env.code_commit_hash is None

    def test_code_commit_hash_set(self):
        env = self._make_envelope(code_commit_hash="abc")
        assert env.code_commit_hash == "abc"


# ---------------------------------------------------------------------------
# tool_args_types
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.types.tool_args_types import (
    CreateDirectoryArgs,
    DeleteFileArgs,
    ExecuteCommandArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)


class TestToolArgsTypes:
    def test_read_file_args_valid(self):
        a = ReadFileArgs(path="foo/bar.py")
        assert a.path == "foo/bar.py"

    def test_write_file_args_valid(self):
        a = WriteFileArgs(path="foo/bar.py", content="hello")
        assert a.content == "hello"

    def test_list_files_args_pattern_optional(self):
        a = ListFilesArgs(directory="src/")
        assert a.pattern is None

    def test_list_files_args_with_pattern(self):
        a = ListFilesArgs(directory="src/", pattern="*.py")
        assert a.pattern == "*.py"

    def test_move_file_args(self):
        a = MoveFileArgs(source="old.py", destination="new.py")
        assert a.source == "old.py"

    def test_delete_file_args(self):
        a = DeleteFileArgs(path="old.py")
        assert a.path == "old.py"

    def test_create_directory_args(self):
        a = CreateDirectoryArgs(path="new_dir/")
        assert a.path == "new_dir/"

    def test_execute_command_args_importable(self):
        assert callable(ExecuteCommandArgs)
