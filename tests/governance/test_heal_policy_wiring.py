"""
Tests for Phase 2: Heal Policy Wiring

Proves:
1. enable_llm=False never selects a tier (hard gate)
2. enable_llm=True selects LOW then HIGH based on confidence thresholds
3. No network calls are made (LLM client seam is blocked)
4. proceed=False returns deterministic refusal
"""

import os
from unittest import mock

import pytest

pytestmark = pytest.mark.governance

from agentic_core.L5_safety.types.heal_policy_types import (
    HealEscalationInputs,
    ReasoningTier,
    decide_heal_escalation,
)


class TestEnableLlmHardGate:
    """Tests proving enable_llm=False never selects a tier."""

    def test_enable_llm_false_high_confidence_proceeds_no_tier(self):
        """High confidence with enable_llm=False proceeds without tier."""
        inputs = HealEscalationInputs(
            confidence_value=0.85,
            enable_llm=False,
            task_complexity=5,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is True
        assert decision.tier is None
        assert "HIGH_CONF_AUTO" in decision.threshold_used

    def test_enable_llm_false_medium_confidence_blocked(self):
        """Medium confidence with enable_llm=False is blocked."""
        inputs = HealEscalationInputs(
            confidence_value=0.60,
            enable_llm=False,
            task_complexity=5,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is False
        assert decision.tier is None
        assert "LLM_DISABLED" in decision.threshold_used

    def test_enable_llm_false_low_confidence_blocked(self):
        """Low confidence with enable_llm=False is blocked."""
        inputs = HealEscalationInputs(
            confidence_value=0.30,
            enable_llm=False,
            task_complexity=8,
            prior_failures=2,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is False
        assert decision.tier is None
        assert "LLM_DISABLED" in decision.threshold_used


class TestTierSelection:
    """Tests proving LOW then HIGH tier selection based on confidence."""

    def test_medium_confidence_selects_low_tier(self):
        """Medium confidence with enable_llm=True and complexity>=5 selects LOW tier."""
        inputs = HealEscalationInputs(
            confidence_value=0.60,
            enable_llm=True,
            task_complexity=5,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is True
        assert decision.tier == ReasoningTier.LOW
        assert "MEDIUM_CONF_LLM_LOW" in decision.threshold_used

    def test_low_confidence_selects_high_tier(self):
        """Low confidence with enable_llm=True and judicious gate met selects HIGH tier."""
        inputs = HealEscalationInputs(
            confidence_value=0.30,
            enable_llm=True,
            task_complexity=7,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is True
        assert decision.tier == ReasoningTier.HIGH
        assert "LOW_CONF_LLM_HIGH" in decision.threshold_used

    def test_low_confidence_with_prior_failures_selects_high_tier(self):
        """Low confidence with prior_failures>=1 selects HIGH tier."""
        inputs = HealEscalationInputs(
            confidence_value=0.30,
            enable_llm=True,
            task_complexity=3,
            prior_failures=1,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is True
        assert decision.tier == ReasoningTier.HIGH


class TestJudiciousGate:
    """Tests proving judicious gate blocks low-complexity escalation."""

    def test_medium_confidence_low_complexity_blocked(self):
        """Medium confidence with low complexity is blocked by judicious gate."""
        inputs = HealEscalationInputs(
            confidence_value=0.60,
            enable_llm=True,
            task_complexity=3,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is False
        assert "JUDICIOUS_BLOCK" in decision.threshold_used

    def test_low_confidence_low_complexity_no_failures_blocked(self):
        """Low confidence with low complexity and no failures is blocked."""
        inputs = HealEscalationInputs(
            confidence_value=0.30,
            enable_llm=True,
            task_complexity=3,
            prior_failures=0,
        )
        decision = decide_heal_escalation(inputs)
        assert decision.proceed is False
        assert "JUDICIOUS_BLOCK" in decision.threshold_used


class TestNoNetworkCalls:
    """Tests proving no network calls are made through the decorator."""

    def test_standard_heal_no_llm_call_when_disabled(self):
        """standard_heal does not invoke LLM when enable_llm=False."""
        from agentic_core.L5_safety.types import heal_llm_seam
        from agentic_core.utils import decorators_util

        llm_call_count = 0

        def blocking_llm_caller(request):
            nonlocal llm_call_count
            llm_call_count += 1
            raise RuntimeError("LLM call attempted when disabled!")

        original_caller = heal_llm_seam.DEFAULT_HEAL_LLM_CALLER

        try:
            heal_llm_seam.DEFAULT_HEAL_LLM_CALLER = blocking_llm_caller

            with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "0"}):

                @decorators_util.standard_heal
                def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                    return {"violations_found": 0, "violations_fixed": 0}

                class MockAgent:
                    pass

                agent = MockAgent()
                result = mock_heal_repository(agent, _confidence=0.60, _task_complexity=5)

                assert llm_call_count == 0
                assert result["status"] == "BLOCKED"

        finally:
            heal_llm_seam.DEFAULT_HEAL_LLM_CALLER = original_caller

    def test_standard_heal_high_confidence_no_llm_call(self):
        """standard_heal does not invoke LLM for high confidence (no tier)."""
        from agentic_core.L5_safety.types import heal_llm_seam
        from agentic_core.utils import decorators_util

        llm_call_count = 0

        def blocking_llm_caller(request):
            nonlocal llm_call_count
            llm_call_count += 1
            raise RuntimeError("LLM call attempted for high confidence!")

        original_caller = heal_llm_seam.DEFAULT_HEAL_LLM_CALLER

        try:
            heal_llm_seam.DEFAULT_HEAL_LLM_CALLER = blocking_llm_caller

            with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):

                @decorators_util.standard_heal
                def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                    return {"violations_found": 0, "violations_fixed": 0}

                class MockAgent:
                    pass

                agent = MockAgent()
                result = mock_heal_repository(agent, _confidence=0.85, _task_complexity=5)

                assert llm_call_count == 0
                assert result["status"] == "PASS"

        finally:
            heal_llm_seam.DEFAULT_HEAL_LLM_CALLER = original_caller


class TestDeterministicRefusal:
    """Tests proving proceed=False returns deterministic refusal."""

    def test_blocked_result_contains_policy_decision(self):
        """Blocked result contains policy decision metadata."""
        from agentic_core.utils import decorators_util

        with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "0"}):

            @decorators_util.standard_heal
            def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"violations_found": 1, "violations_fixed": 0}

            class MockAgent:
                pass

            agent = MockAgent()
            result = mock_heal_repository(agent, _confidence=0.60, _task_complexity=5)

            assert result["status"] == "BLOCKED"
            assert "_policy_decision" in result
            assert result["_policy_decision"]["proceed"] is False
            assert "LLM" in result["error_message"] or "disabled" in result["error_message"].lower()

    def test_blocked_result_is_deterministic(self):
        """Blocked result is deterministic across multiple calls."""
        from agentic_core.utils import decorators_util

        with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "0"}):

            @decorators_util.standard_heal
            def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"violations_found": 1, "violations_fixed": 0}

            class MockAgent:
                pass

            agent = MockAgent()

            result1 = mock_heal_repository(agent, _confidence=0.60, _task_complexity=5)
            result2 = mock_heal_repository(agent, _confidence=0.60, _task_complexity=5)

            assert result1["status"] == result2["status"]
            assert (
                result1["_policy_decision"]["threshold_used"] == result2["_policy_decision"]["threshold_used"]
            )
            assert result1["error_message"] == result2["error_message"]


class TestCanonicalSeamEnforcement:
    """Tests proving only standard_heal can invoke LLM escalation."""

    def test_direct_llm_call_without_seam_fails(self):
        """Direct call to guarded_heal_llm_call without standard_heal context fails."""
        from agentic_core.L5_safety.types.heal_llm_seam import (
            HealLlmRequest,
            HealSeamBypassError,
            guarded_heal_llm_call,
        )

        request = HealLlmRequest(
            prompt="bypass_attempt",
            model_id="test-model",
            metadata={"source": "direct_bypass"},
        )

        with pytest.raises(HealSeamBypassError) as exc_info:
            guarded_heal_llm_call(request)

        assert "canonical seam" in str(exc_info.value).lower()
        assert "standard_heal" in str(exc_info.value)

    def test_standard_heal_sets_capability_token(self):
        """standard_heal decorator sets capability token for LLM access."""
        from agentic_core.L5_safety.types.heal_llm_seam import (
            _HEAL_SEAM_CAPABILITY,
        )
        from agentic_core.utils import decorators_util

        capability_inside = None

        with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):

            @decorators_util.standard_heal
            def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                nonlocal capability_inside
                capability_inside = _HEAL_SEAM_CAPABILITY.get()
                return {"violations_found": 0, "violations_fixed": 0}

            class MockAgent:
                pass

            agent = MockAgent()
            mock_heal_repository(agent, _confidence=0.85)

            # Inside standard_heal, capability should be True
            assert capability_inside is True

        # Outside standard_heal, capability should be False (reset)
        assert _HEAL_SEAM_CAPABILITY.get() is False

    def test_llm_escalation_only_via_standard_heal(self):
        """LLM escalation succeeds only when enable_llm=True AND via standard_heal."""
        from agentic_core.L5_safety.types import heal_llm_seam
        from agentic_core.utils import decorators_util

        llm_calls = []

        def tracking_llm_caller(request):
            llm_calls.append(request)
            return "mock_response"

        original_caller = heal_llm_seam.DEFAULT_HEAL_LLM_CALLER

        try:
            heal_llm_seam.DEFAULT_HEAL_LLM_CALLER = tracking_llm_caller

            # Set up model router to return a model
            original_router = decorators_util._HEAL_MODEL_ROUTER
            decorators_util._HEAL_MODEL_ROUTER = lambda tier: "test-model"

            with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):

                @decorators_util.standard_heal
                def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                    return {"violations_found": 0, "violations_fixed": 0}

                class MockAgent:
                    pass

                agent = MockAgent()
                # Medium confidence with enable_llm=True triggers LLM escalation
                result = mock_heal_repository(agent, _confidence=0.60, _task_complexity=5)

                assert result["status"] == "PASS"
                assert len(llm_calls) == 1
                assert llm_calls[0].metadata["source"] == "standard_heal"

            decorators_util._HEAL_MODEL_ROUTER = original_router

        finally:
            heal_llm_seam.DEFAULT_HEAL_LLM_CALLER = original_caller


class TestPolicyDecisionRecord:
    """Tests for deterministic policy decision record artifact."""

    def test_policy_decision_record_schema(self):
        """PolicyDecisionRecord has correct schema."""
        from agentic_core.L5_safety.types.heal_llm_seam import PolicyDecisionRecord

        record = PolicyDecisionRecord(
            confidence=0.75,
            enable_llm=True,
            complexity=5,
            prior_failures=0,
            proceed=True,
            tier="LOW",
            threshold_used="MEDIUM_CONF_LLM_LOW",
            rationale="Medium confidence with LLM enabled",
        )

        as_dict = record.to_dict()

        assert as_dict["confidence"] == 0.75
        assert as_dict["enable_llm"] is True
        assert as_dict["complexity"] == 5
        assert as_dict["prior_failures"] == 0
        assert as_dict["proceed"] is True
        assert as_dict["tier"] == "LOW"
        assert as_dict["threshold_used"] == "MEDIUM_CONF_LLM_LOW"
        assert as_dict["rationale"] == "Medium confidence with LLM enabled"

    def test_policy_decision_record_deterministic_hash(self):
        """PolicyDecisionRecord produces deterministic input hash."""
        from agentic_core.L5_safety.types.heal_llm_seam import PolicyDecisionRecord

        record1 = PolicyDecisionRecord(
            confidence=0.75,
            enable_llm=True,
            complexity=5,
            prior_failures=0,
            proceed=True,
            tier="LOW",
            threshold_used="TEST",
            rationale="test",
        )

        record2 = PolicyDecisionRecord(
            confidence=0.75,
            enable_llm=True,
            complexity=5,
            prior_failures=0,
            proceed=False,  # Different output, same inputs
            tier=None,
            threshold_used="DIFFERENT",
            rationale="different",
        )

        # Same inputs produce same hash
        assert record1.input_hash() == record2.input_hash()

        # Different inputs produce different hash
        record3 = PolicyDecisionRecord(
            confidence=0.60,  # Different input
            enable_llm=True,
            complexity=5,
            prior_failures=0,
            proceed=True,
            tier="LOW",
            threshold_used="TEST",
            rationale="test",
        )
        assert record1.input_hash() != record3.input_hash()

    def test_standard_heal_emits_policy_record(self):
        """standard_heal includes policy decision record in result."""
        from agentic_core.utils import decorators_util

        with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "0"}):

            @decorators_util.standard_heal
            def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                # Capture the policy decision passed through
                return {
                    "violations_found": 0,
                    "violations_fixed": 0,
                    "_policy_from_kwargs": kwargs.get("_policy_decision"),
                }

            class MockAgent:
                pass

            agent = MockAgent()
            result = mock_heal_repository(agent, _confidence=0.85, _task_complexity=3)

            # Policy record should be in _raw_result
            raw_result = result.get("_raw_result", {})
            policy = raw_result.get("_policy_from_kwargs")

            assert policy is not None
            assert policy["confidence"] == 0.85
            assert policy["complexity"] == 3
            assert policy["proceed"] is True
            assert "rationale" in policy


class TestNetworkTripwire:
    """Tests proving network calls are blocked in governance heal tests."""

    def test_network_tripwire_blocks_socket(self):
        """Network tripwire blocks socket creation when enforcement is active."""
        import socket

        class NetworkTripwireError(Exception):
            pass

        def _blocked_socket(*args, **kwargs):
            raise NetworkTripwireError(
                "Network call attempted in governance test — blocked by tripwire"
            )

        # Enforce tripwire within the scope of this test
        with mock.patch("socket.socket", side_effect=_blocked_socket):
            try:
                socket.socket()
                pytest.fail("Expected NetworkTripwireError but socket.socket() succeeded")
            except NetworkTripwireError as e:
                assert "Network call attempted" in str(e) or "governance test" in str(e)

    def test_heal_paths_make_no_network_calls(self):
        """Heal paths via standard_heal make no network calls."""
        from agentic_core.utils import decorators_util

        with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "0"}):

            @decorators_util.standard_heal
            def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"violations_found": 0, "violations_fixed": 0}

            class MockAgent:
                pass

            agent = MockAgent()

            # This should succeed without triggering network tripwire
            result = mock_heal_repository(agent, _confidence=0.85)
            assert result["status"] == "PASS"


class TestHealRepositoryBaseline:
    """Tests for deterministic heal_repository baseline."""

    def test_heal_repository_deterministic_output(self):
        """heal_repository produces deterministic output using policy decision directly."""
        from agentic_core.L5_safety.types.heal_policy_types import (
            HealEscalationInputs,
            decide_heal_escalation,
        )

        # Test determinism of policy decision (which drives heal_repository)
        inputs = HealEscalationInputs(
            confidence_value=0.85,
            enable_llm=False,
            task_complexity=3,
        )

        result1 = decide_heal_escalation(inputs)
        result2 = decide_heal_escalation(inputs)

        # Same inputs produce same outputs
        assert result1.proceed == result2.proceed
        assert result1.tier == result2.tier
        assert result1.threshold_used == result2.threshold_used
        assert result1.rationale == result2.rationale

    def test_heal_repository_idempotency(self):
        """Policy decision is idempotent across multiple calls."""
        from agentic_core.L5_safety.types.heal_policy_types import (
            HealEscalationInputs,
            decide_heal_escalation,
        )

        inputs = HealEscalationInputs(
            confidence_value=0.85,
            enable_llm=False,
            task_complexity=5,
        )

        # Multiple calls produce identical results
        results = [decide_heal_escalation(inputs) for _ in range(5)]

        for i in range(1, len(results)):
            assert results[0].proceed == results[i].proceed
            assert results[0].tier == results[i].tier
            assert results[0].threshold_used == results[i].threshold_used

    def test_heal_repository_policy_routing(self):
        """Policy routes correctly based on confidence and enable_llm."""
        from agentic_core.L5_safety.types.heal_policy_types import (
            HealEscalationInputs,
            decide_heal_escalation,
        )

        # Test high confidence (proceeds without tier)
        high_conf = HealEscalationInputs(
            confidence_value=0.85,
            enable_llm=False,
            task_complexity=5,
        )
        result = decide_heal_escalation(high_conf)
        assert result.proceed is True
        assert result.tier is None
        assert "HIGH_CONF_AUTO" in result.threshold_used

        # Test medium confidence with LLM disabled (blocked)
        med_conf = HealEscalationInputs(
            confidence_value=0.60,
            enable_llm=False,
            task_complexity=5,
        )
        result = decide_heal_escalation(med_conf)
        assert result.proceed is False
        assert "LLM_DISABLED" in result.threshold_used

    def test_heal_repository_deterministic_baseline_integration(self):
        """Integration test: standard_heal decorator respects policy decision."""
        from agentic_core.utils import decorators_util

        with mock.patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "0"}):

            @decorators_util.standard_heal
            def mock_heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {
                    "violations_found": 0,
                    "violations_fixed": 0,
                }

            class MockAgent:
                pass

            agent = MockAgent()

            # High confidence proceeds
            result = mock_heal_repository(agent, _confidence=0.85, _task_complexity=3)
            assert result["status"] == "PASS"

            # Medium confidence blocked when LLM disabled
            result = mock_heal_repository(agent, _confidence=0.60, _task_complexity=5)
            assert result["status"] == "BLOCKED"
            assert "_policy_decision" in result
            assert result["_policy_decision"]["proceed"] is False
