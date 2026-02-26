"""Invariant tests for sovereignty hardening.

Tests:
- C0: C0ContextRetriever seed pack hash verification
- MODIFY_DIFF: HumanDecisionArtifact enforces L5 re-clear
- Unregistered agent: SovereignLLMGateway rejects unknown agents
- Tier choke: DETERMINISTIC agents cannot call LLM gateway
- Proposal only: MetaLearningPipeline in proposal_only mode does not commit
"""

import hashlib
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentic_core.agents.types.agent_execution_profile import ExecutionMode
from agentic_core.L0_routing.seams.c0_context_retriever import (
    C0ContextArtifact,
    C0ContextRetriever,
    ContentHash,
)
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    SovereignLLMGateway,
    SovereigntyViolation,
)
from agentic_core.L2_execution.types.gateway_types import GenerationRequest
from agentic_core.L5_safety.enforcement.human_review_queue import HumanReviewQueue
from agentic_core.L5_safety.types.human_decision_artifact import HumanDecisionArtifact


class TestC0Invariant:
    """C0: seed pack hash must match computed SHA256."""

    @pytest.mark.asyncio
    async def test_seed_pack_hash_mismatch_raises(self):
        retriever = C0ContextRetriever()
        # Mock load with tampered seed pack
        artifact = MagicMock(spec=C0ContextArtifact)
        artifact.seed_pack = "tampered content"
        artifact.seed_pack_hash = "deadbeef"
        artifact.supporting_content_hashes = []

        # Patch the load method on the class, not instance
        import agentic_core.L0_routing.seams.c0_context_retriever as c0_module

        c0_module.C0ContextArtifact.load = AsyncMock(return_value=artifact)

        with pytest.raises(RuntimeError, match="hash mismatch"):
            await retriever.retrieve("any prompt")

    @pytest.mark.asyncio
    async def test_valid_seed_pack_returns_context(self):
        retriever = C0ContextRetriever()
        # Mock valid artifact
        seed = "valid content"
        expected_hash = hashlib.sha256(seed.encode()).hexdigest()
        artifact = MagicMock(spec=C0ContextArtifact)
        artifact.seed_pack = seed
        artifact.seed_pack_hash = expected_hash
        artifact.supporting_content_hashes = [
            ContentHash(content_hash="abc123", score=0.9),
            ContentHash(content_hash="def456", score=0.6),
        ]

        # Patch the load method on the class
        import agentic_core.L0_routing.seams.c0_context_retriever as c0_module

        c0_module.C0ContextArtifact.load = AsyncMock(return_value=artifact)

        result = await retriever.retrieve("any prompt")
        assert "abc123" in result
        assert "def456" in result


class TestModifyDiffInvariant:
    """MODIFY_DIFF: HumanDecisionArtifact enforces L5 re-clear."""

    def test_modify_diff_sets_l5_reclear_required(self):
        artifact = HumanDecisionArtifact(
            trace_id="t1",
            policy_hash="p1",
            reviewer_id="r1",
            action="MODIFY_DIFF",
            original_plan_hash="oph1",
            structured_patch_schema={"ops": []},
        )
        assert artifact.l5_reclear_required

    def test_other_actions_do_not_require_l5_reclear(self):
        for action in ("APPROVE", "REJECT"):
            artifact = HumanDecisionArtifact(
                trace_id="t1",
                policy_hash="p1",
                reviewer_id="r1",
                action=action,
                original_plan_hash="oph1",
                structured_patch_schema={},
            )
            assert not artifact.l5_reclear_required

    def test_human_review_queue_modify_diff_returns_artifact(self):
        queue = HumanReviewQueue()
        # Submit a dummy request
        from agentic_core.L5_safety.enforcement.human_review_queue import ContextBundle, ProposedDiff

        diff = ProposedDiff(
            file_path="/tmp/file.py",
            original_content="old",
            proposed_content="new",
            change_summary="test",
        )
        bundle = ContextBundle(
            detection_signal={},
            proposed_diff=diff,
            ai_rationale="test",
            simulated_outcome=MagicMock(),
            risk_assessment={},
        )
        request = queue.submit_for_review(bundle)

        artifact = queue.modify_diff(
            request_id=request.request_id,
            reviewer_id="reviewer",
            structured_patch_schema={"ops": []},
            original_plan_hash="oph1",
            secret=b"secret",
        )
        assert artifact.action == "MODIFY_DIFF"
        assert artifact.l5_reclear_required


class TestUnregisteredAgentInvariant:
    """Unregistered agent: SovereignLLMGateway rejects unknown agents."""

    @pytest.mark.asyncio
    async def test_unknown_agent_raises_sovereignty_violation(self):
        gateway = SovereignLLMGateway()
        request = GenerationRequest(
            agent_id="nonexistent_agent",
            provider="openai",
            model="gpt-4",
            prompt="test",
        )
        with pytest.raises(SovereigntyViolation, match="not found in registry"):
            await gateway.route_generation(request)

    @pytest.mark.asyncio
    async def test_deterministic_agent_cannot_call_gateway(self):
        gateway = SovereignLLMGateway()
        # Mock registry to return a DETERMINISTIC profile
        from agentic_core.agents.agent_registry import get_profile

        mock_profile = MagicMock()
        mock_profile.execution_mode = ExecutionMode.DETERMINISTIC
        get_profile.return_value = mock_profile

        request = GenerationRequest(
            agent_id="deterministic_agent",
            provider="openai",
            model="gpt-4",
            prompt="test",
        )
        with pytest.raises(SovereigntyViolation, match="DETERMINISTIC and cannot call"):
            await gateway.route_generation(request)


class TestTierChokeInvariant:
    """Tier choke: DETERMINISTIC agents cannot use LLM_API models."""

    @pytest.mark.asyncio
    async def test_llm_api_agent_blocked_on_unallowed_model(self):
        gateway = SovereignLLMGateway()
        # Mock registry to return LLM_API profile with restricted models
        from agentic_core.agents.agent_registry import get_profile

        mock_profile = MagicMock()
        mock_profile.execution_mode = ExecutionMode.LLM_API
        mock_profile.allowed_models = ["gpt-3.5-turbo"]
        mock_profile.allowed_providers = ["openai"]
        get_profile.return_value = mock_profile

        request = GenerationRequest(
            agent_id="llm_api_agent",
            provider="openai",
            model="gpt-4",  # Not in allowed_models
            prompt="test",
        )
        with pytest.raises(SovereigntyViolation, match="not allowed to use model"):
            await gateway.route_generation(request)


class TestProposalOnlyInvariant:
    """Proposal only: MetaLearningPipeline in proposal_only mode does not commit."""

    @pytest.mark.asyncio
    async def test_proposal_only_mode_does_not_commit(self):
        from system_learning.pipelines.meta_learning_pipeline import (
            PipelineConfig,
            PipelineDependencies,
            run_pipeline,
        )

        cfg = PipelineConfig(
            window_start_utc=0,
            window_end_utc=1000,
            oscillation_policy=MagicMock(),
            cooldown_policy=MagicMock(),
            sample_policy=MagicMock(),
            shadow_thresholds=MagicMock(),
            enabled_proposers=(),
            proposal_only=True,  # Critical flag
        )
        deps = PipelineDependencies(
            audit_store=MagicMock(),
            telemetry_store=MagicMock(),
            config_provider=MagicMock(),
            baseline_metrics_provider=MagicMock(),
            version_store=None,  # None in proposal_only
            activator=None,  # None in proposal_only
            approval_gate=None,  # None in proposal_only
        )

        # Mock all provider methods to avoid real calls
        deps.audit_store.read_audit_slice.return_value = b"{}"
        deps.telemetry_store.read_events.return_value = ()
        deps.config_provider.get_current_configs.return_value = {}
        deps.baseline_metrics_provider.production_metrics.return_value = MagicMock()
        deps.baseline_metrics_provider.shadow_metrics.return_value = MagicMock()

        # Should not raise; should complete without committing
        result = await run_pipeline(cfg, deps)
        assert result is not None  # Pipeline returns a result object
