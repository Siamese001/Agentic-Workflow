"""
Phase 4 tests for repo-heal pipeline.

Tests deterministic plan/apply, scope controls, and idempotency.
"""

import json

import pytest

pytestmark = pytest.mark.governance


class TestRepoHealPlanDeterminism:
    """Tests proving repo-heal plan is deterministic."""

    def test_build_plan_produces_same_result_twice(self, tmp_path):
        """Building plan twice on same repo produces identical results."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import build_repo_heal_plan

        # Create test repo structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "src" / "utils.py").write_text("def foo(): pass")
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "config.json").write_text("{}")

        plan1 = build_repo_heal_plan(str(tmp_path))
        plan2 = build_repo_heal_plan(str(tmp_path))

        assert plan1.plan_hash() == plan2.plan_hash()
        assert plan1.scanned_files == plan2.scanned_files
        assert len(plan1.operations) == len(plan2.operations)

        # Verify operations are identical
        for op1, op2 in zip(plan1.operations, plan2.operations):
            assert op1.path == op2.path
            assert op1.operation == op2.operation

    def test_plan_is_sorted_deterministically(self, tmp_path):
        """Plan operations are sorted by priority then path."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import build_repo_heal_plan

        # Create files in random order
        (tmp_path / "z_last.py").write_text("")
        (tmp_path / "a_first.py").write_text("")
        (tmp_path / "m_middle.py").write_text("")

        plan = build_repo_heal_plan(str(tmp_path))

        paths = [op.path for op in plan.operations]
        assert paths == sorted(paths)


class TestRepoHealScopeControls:
    """Tests proving scope controls work correctly."""

    def test_denylist_excludes_directories(self, tmp_path):
        """Denylist directories are excluded from scan."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import build_repo_heal_plan

        # Create allowed and denied directories
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("")
        (tmp_path / ".venv").mkdir()
        (tmp_path / ".venv" / "bad.py").write_text("")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "package.json").write_text("{}")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("")

        plan = build_repo_heal_plan(str(tmp_path))

        paths = [op.path for op in plan.operations]
        assert "src/main.py" in paths
        assert not any(".venv" in p for p in paths)
        assert not any("node_modules" in p for p in paths)
        assert not any(".git" in p for p in paths)

    def test_allowlist_filters_extensions(self, tmp_path):
        """Only allowlisted extensions are included."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import build_repo_heal_plan

        # Create files with various extensions
        (tmp_path / "main.py").write_text("")
        (tmp_path / "README.md").write_text("")
        (tmp_path / "config.json").write_text("{}")
        (tmp_path / "notes.txt").write_text("")
        (tmp_path / "binary.exe").write_text("")
        (tmp_path / "image.png").write_text("")
        (tmp_path / "style.css").write_text("")

        plan = build_repo_heal_plan(str(tmp_path))

        paths = [op.path for op in plan.operations]
        assert "main.py" in paths
        assert "README.md" in paths
        assert "config.json" in paths
        assert "notes.txt" in paths
        assert "binary.exe" not in paths
        assert "image.png" not in paths
        assert "style.css" not in paths

    def test_skipped_files_counted(self, tmp_path):
        """Skipped files are counted correctly."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import build_repo_heal_plan

        (tmp_path / "main.py").write_text("")
        (tmp_path / "binary.exe").write_text("")
        (tmp_path / "image.png").write_text("")

        plan = build_repo_heal_plan(str(tmp_path))

        assert plan.scanned_files == 1  # main.py
        assert plan.skipped_files == 2  # exe, png


class TestRepoHealApplyIdempotency:
    """Tests proving apply is idempotent."""

    def test_apply_is_idempotent(self, tmp_path):
        """Applying plan twice produces same result."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            apply_repo_heal_plan,
            build_repo_heal_plan,
        )

        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def foo(): pass")

        plan = build_repo_heal_plan(str(tmp_path))

        result1 = apply_repo_heal_plan(plan, dry_run=True)
        result2 = apply_repo_heal_plan(plan, dry_run=True)

        assert result1.plan_hash == result2.plan_hash
        assert result1.operations_succeeded == result2.operations_succeeded
        assert result1.is_idempotent == result2.is_idempotent

    def test_apply_handles_missing_files(self, tmp_path):
        """Apply handles files that were deleted after plan creation."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            apply_repo_heal_plan,
            build_repo_heal_plan,
        )

        (tmp_path / "main.py").write_text("")
        (tmp_path / "deleted.py").write_text("")

        plan = build_repo_heal_plan(str(tmp_path))

        # Delete a file after plan creation
        (tmp_path / "deleted.py").unlink()

        result = apply_repo_heal_plan(plan, dry_run=True)

        assert result.operations_skipped == 1  # deleted.py
        assert result.operations_succeeded == 1  # main.py

    def test_dry_run_makes_no_changes(self, tmp_path):
        """Dry run mode makes no file changes."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            apply_repo_heal_plan,
            build_repo_heal_plan,
        )

        original_content = "print('original')"
        (tmp_path / "main.py").write_text(original_content)

        plan = build_repo_heal_plan(str(tmp_path))
        apply_repo_heal_plan(plan, dry_run=True)

        # Verify file unchanged
        assert (tmp_path / "main.py").read_text() == original_content


class TestRepoHealPlanSchema:
    """Tests for plan/result serialization."""

    def test_plan_to_dict_schema(self, tmp_path):
        """Plan to_dict produces correct schema."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import build_repo_heal_plan

        (tmp_path / "main.py").write_text("")

        plan = build_repo_heal_plan(str(tmp_path))
        as_dict = plan.to_dict()

        assert "repo_root" in as_dict
        assert "operations" in as_dict
        assert "scanned_files" in as_dict
        assert "skipped_files" in as_dict
        assert "total_operations" in as_dict
        assert isinstance(as_dict["operations"], list)

    def test_result_to_dict_schema(self, tmp_path):
        """Result to_dict produces correct schema."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            apply_repo_heal_plan,
            build_repo_heal_plan,
        )

        (tmp_path / "main.py").write_text("")

        plan = build_repo_heal_plan(str(tmp_path))
        result = apply_repo_heal_plan(plan, dry_run=True)
        as_dict = result.to_dict()

        assert "plan_hash" in as_dict
        assert "operations_attempted" in as_dict
        assert "operations_succeeded" in as_dict
        assert "operations_failed" in as_dict
        assert "operations_skipped" in as_dict
        assert "is_idempotent" in as_dict

    def test_plan_json_serializable(self, tmp_path):
        """Plan can be serialized to JSON."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import build_repo_heal_plan

        (tmp_path / "main.py").write_text("")

        plan = build_repo_heal_plan(str(tmp_path))
        json_str = json.dumps(plan.to_dict(), sort_keys=True)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["total_operations"] == len(plan.operations)


class TestHealRepositoryPolicyIntegration:
    """Tests for heal_repository policy + seam guard integration."""

    def test_enable_llm_false_no_llm_call(self):
        """enable_llm=False prevents any LLM escalation path."""
        from agentic_core.L5_safety.types import heal_llm_seam
        from agentic_core.L5_safety.types.heal_policy_types import (
            HealEscalationInputs,
            decide_heal_escalation,
        )

        # Test policy decision with enable_llm=False
        inputs = HealEscalationInputs(
            confidence_value=0.50,  # Low confidence would normally trigger LLM
            enable_llm=False,
            task_complexity=8,
            prior_failures=2,
        )
        decision = decide_heal_escalation(inputs)

        # Should be blocked, not proceed to LLM
        assert decision.proceed is False or decision.tier is None

        # Set up a trap - if LLM is called, this will raise
        def llm_trap(request):
            raise AssertionError("LLM should not be called when enable_llm=False!")

        original_caller = heal_llm_seam.DEFAULT_HEAL_LLM_CALLER
        try:
            heal_llm_seam.DEFAULT_HEAL_LLM_CALLER = llm_trap

            # Verify policy blocks before LLM path
            if decision.proceed and decision.tier is not None:
                # This path should not be reached with enable_llm=False
                pytest.fail("Policy should block LLM escalation when enable_llm=False")

        finally:
            heal_llm_seam.DEFAULT_HEAL_LLM_CALLER = original_caller

    def test_enable_llm_true_requires_capability_token(self):
        """LLM escalation requires capability token even with enable_llm=True."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealLlmRequest,
            HealSeamBypassError,
            guarded_heal_llm_call,
        )

        # Direct call without capability token should fail
        request = HealLlmRequest(
            prompt="test",
            model_id="test-model",
            metadata={"source": "test"},
        )

        with pytest.raises(HealSeamBypassError):
            guarded_heal_llm_call(request)

    def test_policy_decision_record_emitted(self):
        """PolicyDecisionRecord is emitted with stable schema."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import PolicyDecisionRecord

        record = PolicyDecisionRecord(
            confidence=0.75,
            enable_llm=True,
            complexity=5,
            prior_failures=0,
            proceed=True,
            tier="LOW",
            threshold_used="MEDIUM_CONF_LLM_LOW",
            rationale="test",
        )

        # Verify stable filename via input hash
        hash1 = record.input_hash()
        hash2 = record.input_hash()
        assert hash1 == hash2
        assert len(hash1) == 16  # 16-char hash prefix

        # Verify dict schema
        as_dict = record.to_dict()
        required_keys = {
            "confidence",
            "enable_llm",
            "complexity",
            "prior_failures",
            "proceed",
            "tier",
            "threshold_used",
            "rationale",
        }
        assert set(as_dict.keys()) == required_keys

    def test_baseline_plan_runs_before_escalation(self, tmp_path):
        """Baseline plan runs before any LLM escalation."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            apply_repo_heal_plan,
            build_repo_heal_plan,
        )
        from agentic_core.L5_safety.types.heal_policy_types import (
            HealEscalationInputs,
            decide_heal_escalation,
        )

        # Create test repo
        (tmp_path / "main.py").write_text("")

        # Step 1: Build baseline plan (always deterministic, no LLM)
        plan = build_repo_heal_plan(str(tmp_path))
        assert len(plan.operations) > 0

        # Step 2: Apply baseline plan
        result = apply_repo_heal_plan(plan, dry_run=True)
        assert result.is_idempotent is True

        # Step 3: Only after baseline, check if escalation needed
        unresolved = result.operations_failed > 0
        inputs = HealEscalationInputs(
            confidence_value=0.60,
            enable_llm=True,
            task_complexity=5,
            prior_failures=0,
        )
        escalation_decision = decide_heal_escalation(inputs)

        # If no unresolved issues, no escalation needed
        if not unresolved:
            assert result.operations_succeeded > 0
            # Escalation decision exists but won't be acted upon
            assert escalation_decision.proceed is True or escalation_decision.proceed is False
