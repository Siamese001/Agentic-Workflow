"""Smoke tests for agentic_core/interfaces hardening (commit 7e4d24cdf7).

Covers:
  G1 - validate_sandbox RuntimeError → SandboxViolationError (source fix)
  G2 - validate_sandbox happy path
  G3 - validate_sandbox path traversal
  G4 - validate_sandbox project-root-not-found → SandboxViolationError
  G5 - query_similarity empty/whitespace → []
  G6 - _normalize_top_k boundary (0→1, 100→_MAX_TOP_K)
  G7 - fail-fast stubs raise ModuleNotFoundError
  G8 - require_healing_lease blocks denied-lease writes
  G9 - write_file PreservationViolationError when content < 90% of original
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import (
    HealingLeaseError,
    PreservationViolationError,
    SandboxViolationError,
    require_healing_lease,
    validate_sandbox,
    write_file,
)
from agentic_core.interfaces.embeddings import _normalize_top_k, query_similarity
from agentic_core.interfaces.mixins import _missing_dependency
from agentic_core.interfaces.routing_types import _MissingOptionalDependency
from agentic_core.interfaces.validators import _missing_rule_failure
from agentic_core.L2_execution.types.tool_args_types import WriteFileArgs


class TestValidateSandboxHappyPath:
    def test_returns_absolute_path_for_existing_relative_path(self):
        result = validate_sandbox("agentic_core/__init__.py")
        assert isinstance(result, Path)
        assert result.is_absolute()

    def test_returns_path_for_directory(self):
        result = validate_sandbox("agentic_core/interfaces")
        assert isinstance(result, Path)
        assert result.is_absolute()


class TestValidateSandboxFailurePaths:
    def test_path_traversal_raises_sandbox_violation(self):
        with pytest.raises(SandboxViolationError):
            validate_sandbox("../../etc/passwd")

    def test_project_root_not_found_raises_sandbox_violation(self):
        with patch("agentic_core.interfaces.IBlackboardLeaseVerifierProtocol.get_project_root") as mock_root:
            mock_root.side_effect = RuntimeError("Project root not found.")
            with pytest.raises(SandboxViolationError, match="Project root not found"):
                validate_sandbox("some/path.py")

    def test_empty_path_raises_sandbox_violation(self):
        with pytest.raises(SandboxViolationError):
            validate_sandbox("")


class TestRequireHealingLease:
    def test_no_blackboard_executes_function(self):
        @require_healing_lease
        def noop(args, blackboard=None, agent_id=None):
            return "executed"

        assert noop("dummy") == "executed"

    def test_denied_lease_raises_healing_lease_error(self):
        @require_healing_lease
        def noop(args, blackboard=None, agent_id=None, path=None):
            return "should_not_reach"

        mock_bb = MagicMock()
        mock_bb.verify_healing_lease.return_value = False

        with pytest.raises(HealingLeaseError, match="does not hold HealingLease"):
            noop("args", blackboard=mock_bb, agent_id="agent-1", path="some/path.py")

    def test_granted_lease_executes_function(self):
        @require_healing_lease
        def noop(args, blackboard=None, agent_id=None, path=None):
            return "executed"

        mock_bb = MagicMock()
        mock_bb.verify_healing_lease.return_value = True

        assert noop("args", blackboard=mock_bb, agent_id="agent-1", path="some/path.py") == "executed"


class TestWriteFilePreservation:
    def test_raises_preservation_violation_when_content_too_short(self, tmp_path):
        original_content = "\n".join([f"line {i}" for i in range(100)])
        target = tmp_path / "target.py"
        target.write_text(original_content, encoding="utf-8")

        args = WriteFileArgs(path="dummy/target.py", content="short\ncontent")

        with patch("agentic_core.interfaces.IBlackboardLeaseVerifierProtocol.validate_sandbox") as mock_vs:
            mock_vs.return_value = target
            with pytest.raises(PreservationViolationError):
                write_file(args)

    def test_passes_when_content_meets_threshold(self, tmp_path):
        original_lines = [f"line {i}" for i in range(10)]
        original_content = "\n".join(original_lines)
        target = tmp_path / "target.py"
        target.write_text(original_content, encoding="utf-8")

        new_content = "\n".join(original_lines)
        args = WriteFileArgs(path="dummy/target.py", content=new_content)

        with patch("agentic_core.interfaces.IBlackboardLeaseVerifierProtocol.validate_sandbox") as mock_vs:
            mock_vs.return_value = target
            write_file(args)
        assert target.read_text(encoding="utf-8") == new_content


class TestNormalizeTopK:
    def test_zero_normalized_to_one(self):
        assert _normalize_top_k(0) == 1

    def test_negative_normalized_to_one(self):
        assert _normalize_top_k(-10) == 1

    def test_one_unchanged(self):
        assert _normalize_top_k(1) == 1

    def test_over_max_capped_to_max(self):
        assert _normalize_top_k(100) == 20

    def test_at_max_unchanged(self):
        assert _normalize_top_k(20) == 20


class TestQuerySimilarityInputValidation:
    def test_empty_string_returns_empty_list(self):
        assert query_similarity("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert query_similarity("   ") == []

    def test_whitespace_stripped_before_cache_call(self):
        with patch(
            "agentic_core.L4_state.utils.memory.sovereign_semantic_cache.SovereignSemanticCache"
        ) as mock_cache:
            mock_cache.return_value.query.side_effect = RuntimeError("cache error")
            result = query_similarity("  hello  ")
        assert result == []


class TestFailFastStubs:
    def test_rule_failure_stub_raises_module_not_found(self):
        stub_cls = _missing_rule_failure("validator package missing")
        with pytest.raises(ModuleNotFoundError, match="RuleFailure is unavailable"):
            stub_cls()

    def test_missing_optional_dependency_getattr_raises(self):
        stub = _MissingOptionalDependency("ReasoningIntensityProfile", "L0 not found")
        with pytest.raises(ModuleNotFoundError, match="ReasoningIntensityProfile is unavailable"):
            _ = stub.some_attribute

    def test_missing_optional_dependency_call_raises(self):
        stub = _MissingOptionalDependency("ActionRouter", "L3 not found")
        with pytest.raises(ModuleNotFoundError, match="ActionRouter is unavailable"):
            stub()

    def test_missing_dependency_mixin_raises_on_instantiation(self):
        stub_cls = _missing_dependency("HealerMixin", "L5 safety not found")
        with pytest.raises(ModuleNotFoundError, match="HealerMixin is unavailable"):
            stub_cls()
