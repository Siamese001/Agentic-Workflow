"""Behavioral tests for interfaces hardening: sandbox, healing lease, preservation, embeddings."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.mark.unit
class TestGetProjectRoot:
    def test_returns_path_with_known_marker(self):
        from pathlib import Path

        from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import get_project_root

        root = get_project_root()
        assert isinstance(root, Path)
        assert (root / ".git").exists() or (root / "agentic_core").exists()


@pytest.mark.unit
class TestValidateSandbox:
    def test_valid_relative_path_returns_resolved(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "workdir").mkdir()
        result = mod.validate_sandbox("workdir")
        assert result == (tmp_path / "workdir").resolve()

    def test_path_traversal_raises_sandbox_violation(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import SandboxViolationError

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(SandboxViolationError):
            mod.validate_sandbox("../outside")

    def test_excluded_dir_raises_sandbox_violation(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import SandboxViolationError

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        (tmp_path / ".git").mkdir()
        with pytest.raises(SandboxViolationError, match="excluded directories"):
            mod.validate_sandbox(".git")

    def test_empty_path_raises_sandbox_violation(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import SandboxViolationError

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(SandboxViolationError, match="Empty path"):
            mod.validate_sandbox("")


@pytest.mark.unit
class TestRequireHealingLease:
    def test_no_blackboard_passes_through(self):
        from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import require_healing_lease

        @require_healing_lease
        def target(**kwargs):
            return "ok"

        assert target() == "ok"

    def test_denied_lease_raises_healing_lease_error(self):
        from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import (
            HealingLeaseError,
            require_healing_lease,
        )

        @require_healing_lease
        def target(**kwargs):
            return "ok"

        blackboard = MagicMock()
        blackboard.verify_healing_lease.return_value = False
        with pytest.raises(HealingLeaseError):
            target(blackboard=blackboard, agent_id="agent_x", path="some/file.txt")

    def test_granted_lease_passes_through(self):
        from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import require_healing_lease

        @require_healing_lease
        def target(**kwargs):
            return "passed"

        blackboard = MagicMock()
        blackboard.verify_healing_lease.return_value = True
        assert target(blackboard=blackboard, agent_id="agent_x", path="some/file.txt") == "passed"


@pytest.mark.unit
class TestWriteFilePreservation:
    def test_preservation_violation_raises(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import PreservationViolationError
        from agentic_core.L2_execution.types.tool_args_types import WriteFileArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "file.txt").write_text("\n".join(["line"] * 20), encoding="utf-8")
        args = WriteFileArgs(path="file.txt", content="short")
        with pytest.raises(PreservationViolationError):
            mod.write_file(args)

    def test_override_preservation_bypasses_check(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import WriteFileArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "file.txt").write_text("\n".join(["line"] * 20), encoding="utf-8")
        args = WriteFileArgs(path="file.txt", content="short")
        mod.write_file(args, override_preservation=True)
        assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "short"

    def test_new_file_write_succeeds(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import WriteFileArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        args = WriteFileArgs(
            path="newfile.txt",
            content="""Behavioral tests for fail-fast proxy pattern in phase-hardened interface shim files.""",
        )
        mod.write_file(args)
        assert (tmp_path / "newfile.txt").read_text(
            encoding="utf-8"
        ) == """Behavioral tests for fail-fast proxy pattern in phase-hardened interface shim files."""

    def test_write_file_atomic_leaves_no_tmp_file(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import WriteFileArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        args = WriteFileArgs(path="atomic.txt", content="atomic content")
        mod.write_file(args)
        assert list(tmp_path.glob("*.tmp")) == []
        assert (tmp_path / "atomic.txt").read_text(encoding="utf-8") == "atomic content"


@pytest.mark.unit
class TestMixinsFailFast:
    # --- happy path ---

    def test_mixins_exports_healer_and_metalearning(self):
        from agentic_core.interfaces import mixins

        assert hasattr(mixins, "HealerMixin")
        assert hasattr(mixins, "MetaLearningMixin")

    # --- failure path ---

    def test_missing_dependency_raises_module_not_found_on_call(self):
        from agentic_core.interfaces.mixins import _missing_dependency

        stub_cls = _missing_dependency("HealerMixin", "test.module not found")
        with pytest.raises(ModuleNotFoundError, match="HealerMixin"):
            stub_cls()

    # --- edge case ---

    def test_missing_dependency_error_message_includes_reason(self):
        from agentic_core.interfaces.mixins import _missing_dependency

        stub_cls = _missing_dependency("HealerMixin", "reason: L5 missing")
        with pytest.raises(ModuleNotFoundError, match="reason: L5 missing"):
            stub_cls()


@pytest.mark.unit
class TestOrchestrationProxy:
    # --- happy path ---

    def test_missing_optional_dependency_call_raises(self):
        from agentic_core.interfaces.orchestration import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("ActionRouter", "module not importable")
        with pytest.raises(ModuleNotFoundError, match="ActionRouter"):
            proxy()

    # --- failure path ---

    def test_missing_optional_dependency_getattr_raises(self):
        from agentic_core.interfaces.orchestration import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("ActionRouter", "module not importable")
        with pytest.raises(ModuleNotFoundError, match="ActionRouter"):
            _ = proxy.route

    # --- edge case ---

    def test_missing_optional_dependency_message_includes_reason(self):
        from agentic_core.interfaces.orchestration import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("ActionRouter", "L3 not installed")
        with pytest.raises(ModuleNotFoundError, match="L3 not installed"):
            proxy()


@pytest.mark.unit
class TestValidatorsFailFast:
    # --- happy path ---

    def test_validators_exports_rule_failure(self):
        from agentic_core.interfaces import validators

        assert hasattr(validators, "RuleFailure")

    # --- failure path ---

    def test_missing_rule_failure_raises_on_instantiation(self):
        from agentic_core.interfaces.validators import _missing_rule_failure

        stub_cls = _missing_rule_failure("validators package missing")
        with pytest.raises(ModuleNotFoundError, match="RuleFailure"):
            stub_cls()

    # --- edge case ---

    def test_missing_rule_failure_message_includes_reason(self):
        from agentic_core.interfaces.validators import _missing_rule_failure

        stub_cls = _missing_rule_failure("L5_safety not found")
        with pytest.raises(ModuleNotFoundError, match="L5_safety not found"):
            stub_cls()


@pytest.mark.unit
class TestSafetyProxy:
    def test_missing_optional_dependency_call_raises_safety(self):
        from agentic_core.interfaces.safety import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("UnifiedCSTHealer", "L5 missing")
        with pytest.raises(ModuleNotFoundError, match="UnifiedCSTHealer"):
            proxy()

    def test_missing_optional_dependency_getattr_raises_safety(self):
        from agentic_core.interfaces.safety import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("UnifiedCSTHealer", "L5 missing")
        with pytest.raises(ModuleNotFoundError, match="UnifiedCSTHealer"):
            _ = proxy.heal


@pytest.mark.unit
class TestRoutingTypesProxy:
    def test_missing_optional_dependency_call_raises_routing(self):
        from agentic_core.interfaces.routing_types import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("ReasoningIntensityProfile", "L0 missing")
        with pytest.raises(ModuleNotFoundError, match="ReasoningIntensityProfile"):
            proxy()

    def test_missing_optional_dependency_getattr_raises_routing(self):
        from agentic_core.interfaces.routing_types import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("ReasoningIntensityProfile", "L0 missing")
        with pytest.raises(ModuleNotFoundError, match="ReasoningIntensityProfile"):
            _ = proxy.intensity


@pytest.mark.unit
class TestNormalizeTopK:
    def test_in_range_unchanged(self):
        from agentic_core.interfaces.embeddings import _normalize_top_k

        assert _normalize_top_k(5) == 5

    def test_zero_clamped_to_one(self):
        from agentic_core.interfaces.embeddings import _normalize_top_k

        assert _normalize_top_k(0) == 1

    def test_above_max_clamped(self):
        from agentic_core.interfaces.embeddings import _MAX_TOP_K, _normalize_top_k

        assert _normalize_top_k(_MAX_TOP_K + 100) == _MAX_TOP_K


@pytest.mark.unit
class TestQuerySimilarityGuards:
    def test_empty_query_returns_empty(self):
        from agentic_core.interfaces.embeddings import query_similarity

        assert query_similarity("") == []

    def test_whitespace_only_returns_empty(self):
        from agentic_core.interfaces.embeddings import query_similarity

        assert query_similarity("   \t\n") == []

    def test_valid_query_returns_list_type(self):
        from agentic_core.interfaces.embeddings import query_similarity

        result = query_similarity("some query term")
        assert isinstance(result, list)


@pytest.mark.unit
class TestEmbeddingsShimAttributeError:
    def test_attribute_error_from_cache_returns_empty(self, monkeypatch):
        import sys
        from unittest.mock import MagicMock

        from agentic_core.interfaces import embeddings_shim

        bad_cache = MagicMock()
        bad_cache.query.side_effect = AttributeError("cache broken")
        mock_mod = MagicMock()
        mock_mod.SovereignSemanticCache = MagicMock(return_value=bad_cache)
        monkeypatch.setitem(
            sys.modules,
            "agentic_core.L4_state.utils.memory.sovereign_semantic_cache",
            mock_mod,
        )
        result = embeddings_shim.query_similarity("test query")
        assert result == []


@pytest.mark.unit
class TestAdversarialValidatorNullAgent:
    def test_validate_null_agent_returns_agent_unavailable(self):
        from agentic_core.interfaces.IValidatorProtocol import AdversarialValidator

        v = AdversarialValidator()
        v._initialized = True
        v._agent = None
        result = v.validate("content", {})
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["threat_assessment"]["status"] == "agent_unavailable"

    def test_boundary_validator_null_agent_returns_valid(self):
        from agentic_core.interfaces.IValidatorProtocol import BoundaryValidator

        v = BoundaryValidator()
        v._initialized = True
        v._agent = None
        result = v.validate("content", {})
        assert result["valid"] is True
        assert result["errors"] == []
        assert "recommendations" in result


@pytest.mark.unit
class TestListFiles:
    def test_lists_files_in_directory(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import ListFilesArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "a.py").write_text("x", encoding="utf-8")
        (tmp_path / "subdir" / "b.py").write_text("y", encoding="utf-8")
        result = mod.list_files(ListFilesArgs(directory="subdir"))
        assert len(result) == 2
        assert all(f.endswith(".py") for f in result)

    def test_missing_directory_raises_file_not_found(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import ListFilesArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(FileNotFoundError):
            mod.list_files(ListFilesArgs(directory="no_such_dir"))

    def test_path_is_file_raises_not_a_directory(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import ListFilesArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "afile.txt").write_text("x", encoding="utf-8")
        with pytest.raises(NotADirectoryError):
            mod.list_files(ListFilesArgs(directory="afile.txt"))


@pytest.mark.unit
class TestReadFile:
    def test_read_existing_file_returns_content(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import ReadFileArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "hello.txt").write_text("hello world", encoding="utf-8")
        result = mod.read_file(ReadFileArgs(path="hello.txt"))
        assert result == "hello world"

    def test_read_missing_file_raises_file_not_found(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import ReadFileArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(FileNotFoundError):
            mod.read_file(ReadFileArgs(path="missing.txt"))

    def test_read_directory_raises_value_error(self, tmp_path, monkeypatch):
        import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as mod
        from agentic_core.L2_execution.types.tool_args_types import ReadFileArgs

        monkeypatch.setattr(mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "adir").mkdir()
        with pytest.raises(ValueError, match="Not a file"):
            mod.read_file(ReadFileArgs(path="adir"))
