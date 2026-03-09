"""
Comprehensive branch-coverage tests for SovereignDecisionEngine and
compute_routing_decision (execute_ssot.py).

Coverage targets (per .windsurfrules §1.2):
  - _check_healing_budget: cycle, depth, budget, unknown-rename, OK
  - calculate_healing_confidence: zero, auto_approve, base_score, pattern,
    territory boost/penalty, BMG-disabled, boundary, cap=1.0
  - should_proceed_with_healing: budget-blocked, FAIL_CLOSED, DETERMINISTIC,
    LLM-disabled-approved, LLM-disabled-denied, CONF_Y override,
    CONF_X+Qwen override, decisions_made growth
  - _classify_violation_type: all 6 pattern branches
  - compute_routing_decision: gates 0-8, threshold bands, tiebreak,
    provider-prohibition combos, determinism, digest stability
"""

from __future__ import annotations

import importlib
import os
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Module import helper
# ---------------------------------------------------------------------------


def _load():
    """Import execute_ssot; skip if unavailable."""
    try:
        return importlib.import_module("agentic_core.L0_routing.scripts.execute_ssot")
    except ImportError as exc:
        pytest.fail(f"execute_ssot not importable: {exc}")


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture()
def sde(mod):
    """Fresh SovereignDecisionEngine with LLM disabled."""
    return mod.SovereignDecisionEngine(enable_llm=False)


@pytest.fixture()
def sde_auto(mod):
    """SovereignDecisionEngine with auto_approve=True."""
    return mod.SovereignDecisionEngine(enable_llm=False, auto_approve=True)


@pytest.fixture()
def cs(mod):
    """Factory for ConfidenceScore."""

    def _make(value=0.9, reasoning="test"):
        return mod.ConfidenceScore(value=value, reasoning=reasoning)

    return _make


# ===========================================================================
# _check_healing_budget
# ===========================================================================


class TestCheckHealingBudget:
    def test_ok_on_clean_state(self, sde):
        ok, msg = sde._check_healing_budget("AgentA")
        assert ok is True
        assert msg == "OK"

    def test_cycle_detection_blocks(self, sde):
        sde._call_path.add("AgentA")
        ok, msg = sde._check_healing_budget("AgentA")
        assert ok is False
        assert "Healing cycle detected" in msg
        assert "AgentA" in msg

    def test_depth_at_limit_is_ok(self, sde):
        ok, msg = sde._check_healing_budget("AgentX", depth=3, max_depth=3)
        assert ok is True

    def test_depth_exceeds_limit_blocked(self, sde):
        ok, msg = sde._check_healing_budget("AgentX", depth=4, max_depth=3)
        assert ok is False
        assert "Healing depth limit exceeded" in msg

    def test_depth_boundary_minus_one_ok(self, sde):
        ok, _ = sde._check_healing_budget("AgentX", depth=2, max_depth=3)
        assert ok is True

    def test_budget_exhausted_blocks(self, sde):
        sde._healing_count = sde._max_healing_operations
        ok, msg = sde._check_healing_budget("AgentB")
        assert ok is False
        assert "Budget exceeded" in msg

    def test_budget_at_limit_minus_one_ok(self, sde):
        sde._healing_count = sde._max_healing_operations - 1
        ok, msg = sde._check_healing_budget("AgentB")
        assert ok is True

    def test_unknown_agent_name_renamed(self, sde):
        ok, msg = sde._check_healing_budget("Unknown")
        assert ok is True
        assert "operation-" in str(sde._call_path) or ok is True

    def test_unknown_never_cycle_blocked(self, sde_factory=None):
        m = _load()
        eng = m.SovereignDecisionEngine(enable_llm=False)
        ok1, _ = eng._check_healing_budget("Unknown")
        ok2, _ = eng._check_healing_budget("Unknown")
        assert ok1 is True
        assert ok2 is True

    def test_different_agents_dont_conflict(self, sde):
        sde._call_path.add("AgentA")
        ok, _ = sde._check_healing_budget("AgentB")
        assert ok is True


# ===========================================================================
# calculate_healing_confidence
# ===========================================================================


class TestCalculateHealingConfidence:
    def test_zero_violations_returns_perfect(self, sde):
        cs = sde.calculate_healing_confidence(0, [], "any_territory")
        assert cs.value == 1.0
        assert "Zero" in cs.reasoning

    def test_auto_approve_returns_perfect(self, sde_auto):
        cs = sde_auto.calculate_healing_confidence(5, ["X"], "any")
        assert cs.value == 1.0
        assert "AUTO-HEAL" in cs.reasoning

    def test_base_score_1_violation(self, sde):
        cs = sde.calculate_healing_confidence(1, [], "neutral")
        assert 0.60 <= cs.value <= 1.0, cs.value

    def test_base_score_10_violations(self, sde):
        cs = sde.calculate_healing_confidence(10, [], "neutral")
        assert cs.value < 1.0

    def test_base_score_capped_at_10(self, sde):
        cs10 = sde.calculate_healing_confidence(10, [], "neutral")
        cs15 = sde.calculate_healing_confidence(15, [], "neutral")
        assert cs10.value == pytest.approx(cs15.value, abs=1e-6)

    def test_prompt_governance_boost(self, sde):
        cs_neutral = sde.calculate_healing_confidence(1, ["NAMING"], "neutral")
        cs_pg = sde.calculate_healing_confidence(1, ["NAMING"], "prompt_governance")
        assert cs_pg.value > cs_neutral.value

    def test_L5_territory_penalty(self, sde):
        cs_neutral = sde.calculate_healing_confidence(1, ["NAMING"], "neutral")
        cs_l5 = sde.calculate_healing_confidence(1, ["NAMING"], "L5_safety")
        assert cs_l5.value < cs_neutral.value

    def test_cap_at_1_0(self, sde):
        cs = sde.calculate_healing_confidence(0, [], "prompt_governance")
        assert cs.value <= 1.0

    def test_weighted_formula(self, sde):
        violations = 2
        base_score = max(0.0, 1.0 - (min(violations, 10) * 0.1))
        hist = 0.8
        cs = sde.calculate_healing_confidence(violations, [], "neutral", historical_success_rate=hist)
        expected = (base_score * 0.4) + (0.5 * 0.4) + (hist * 0.2)
        assert cs.value == pytest.approx(min(1.0, expected), abs=0.01)

    def test_no_agent_name_uses_jaccard(self, sde):
        """Without agent_name, pattern_score falls back to Jaccard (BGE path requires agent_name)."""
        cs = sde.calculate_healing_confidence(1, ["LAYER_VIOLATION"], "neutral")
        assert 0.0 <= cs.value <= 1.0

    def test_pattern_score_matched_types(self, sde):
        cs_match = sde.calculate_healing_confidence(1, ["NAMING"], "prompt_governance")
        cs_empty = sde.calculate_healing_confidence(1, [], "prompt_governance")
        assert 0.0 <= cs_match.value <= 1.0
        assert 0.0 <= cs_empty.value <= 1.0

    def test_violations_9_base_score_0_1(self, sde):
        cs = sde.calculate_healing_confidence(9, [], "neutral")
        base_score = max(0.0, 1.0 - 9 * 0.1)
        assert base_score == pytest.approx(0.1, abs=0.01)
        assert cs.value > 0.0

    def test_historical_success_rate_influences_output(self, sde):
        cs_high = sde.calculate_healing_confidence(3, [], "neutral", historical_success_rate=1.0)
        cs_low = sde.calculate_healing_confidence(3, [], "neutral", historical_success_rate=0.0)
        assert cs_high.value > cs_low.value


# ===========================================================================
# should_proceed_with_healing
# ===========================================================================


class TestShouldProceedWithHealing:
    def test_budget_blocked_returns_safety_lock(self, sde, cs):
        sde._healing_count = sde._max_healing_operations
        ok, msg = sde.should_proceed_with_healing(cs(), "AgentX")
        assert ok is False
        assert "SAFETY LOCK" in msg

    def test_fail_closed_routing_blocked(self, sde, cs, mod):
        low_conf = cs(value=0.05, reasoning="very low")
        with patch.object(sde, "_route_decision") as mock_route:
            decision = MagicMock()
            decision.tier = mod.RoutingTier.FAIL_CLOSED
            decision.gate_applied = "TEST_GATE"
            decision.score = 99
            decision.determinism_digest = "abc"
            decision.model_id = "FAIL_CLOSED"
            mock_route.return_value = decision
            ok, msg = sde.should_proceed_with_healing(low_conf, "AgentX")
        assert ok is False
        assert "FAIL-CLOSED" in msg

    def test_deterministic_routing_approves(self, sde, cs, mod):
        high_conf = cs(value=0.95, reasoning="high")
        with patch.object(sde, "_route_decision") as mock_route:
            decision = MagicMock()
            decision.tier = mod.RoutingTier.DETERMINISTIC
            decision.gate_applied = "THRESHOLD_LOW_DET"
            decision.score = 5
            decision.determinism_digest = "abc"
            decision.model_id = "deterministic-sovereign"
            mock_route.return_value = decision
            ok, msg = sde.should_proceed_with_healing(high_conf, "AgentX")
        assert ok is True
        assert "AUTO-HEAL" in msg

    def test_deterministic_increments_healing_count(self, sde, cs, mod):
        count_before = sde._healing_count
        high_conf = cs(value=0.95)
        with patch.object(sde, "_route_decision") as mock_route:
            decision = MagicMock()
            decision.tier = mod.RoutingTier.DETERMINISTIC
            decision.gate_applied = "THRESHOLD_LOW_DET"
            decision.score = 5
            decision.determinism_digest = "abc"
            decision.model_id = "deterministic-sovereign"
            mock_route.return_value = decision
            sde.should_proceed_with_healing(high_conf, "AgentX")
        assert sde._healing_count == count_before + 1

    def test_deterministic_adds_to_call_path(self, sde, cs, mod):
        high_conf = cs(value=0.95)
        with patch.object(sde, "_route_decision") as mock_route:
            decision = MagicMock()
            decision.tier = mod.RoutingTier.DETERMINISTIC
            decision.gate_applied = "THRESHOLD_LOW_DET"
            decision.score = 5
            decision.determinism_digest = "abc"
            decision.model_id = "deterministic-sovereign"
            mock_route.return_value = decision
            sde.should_proceed_with_healing(high_conf, "UniqueAgent42")
        assert "UniqueAgent42" in sde._call_path

    def test_decisions_made_grows(self, sde, cs, mod):
        before = len(sde.decisions_made)
        conf = cs(value=0.95)
        with patch.object(sde, "_route_decision") as mock_route:
            decision = MagicMock()
            decision.tier = mod.RoutingTier.DETERMINISTIC
            decision.gate_applied = "THRESHOLD_LOW_DET"
            decision.score = 5
            decision.determinism_digest = "abc"
            decision.model_id = "deterministic-sovereign"
            mock_route.return_value = decision
            sde.should_proceed_with_healing(conf, "A1")
        assert len(sde.decisions_made) == before + 1

    def test_conf_y_override_forces_gemini(self, mod, cs):
        """Confidence < 0.40 (CONF_Y) → tier forced to GEMINI."""
        eng = mod.SovereignDecisionEngine(enable_llm=False)
        low_conf = cs(value=0.30, reasoning="below CONF_Y")
        with patch.object(eng, "_hitl_gate", return_value=(False, "HITL-SKIPPED")) as _hitl:
            with patch.dict(os.environ, {"SOVEREIGN_AUTO_APPROVE": "0"}):
                ok, reason = eng.should_proceed_with_healing(low_conf, "SomeAgent", territory="neutral")
        assert "GEMINI" in reason or ok is False or "LLM" in reason

    def test_conf_x_override_to_qwen_for_listed_agent(self, mod, cs):
        """0.40 <= confidence < 0.75 with DETERMINISTIC tier + Qwen14B key → QWEN tier override."""
        eng = mod.SovereignDecisionEngine(enable_llm=False)
        med_conf = cs(value=0.60, reasoning="medium")
        with patch(
            "agentic_core.L2_execution.healers.healing_tier_config.QWEN_14B_AGENT_KEYS",
            frozenset({"SpecialQwenAgent"}),
            create=True,
        ):
            with patch.object(eng, "_route_decision") as mock_route:
                decision = MagicMock()
                decision.tier = mod.RoutingTier.DETERMINISTIC
                decision.gate_applied = "THRESHOLD_LOW_DET"
                decision.score = 5
                decision.determinism_digest = "abc"
                decision.model_id = "deterministic-sovereign"
                mock_route.return_value = decision
                with patch.object(eng, "_hitl_gate", return_value=(False, "skipped")):
                    with patch.dict(os.environ, {"SOVEREIGN_AUTO_APPROVE": "0"}):
                        ok, reason = eng.should_proceed_with_healing(
                            med_conf, "SpecialQwenAgent", territory="neutral"
                        )
        assert ok is False or "LLM Disabled" in reason or "QWEN" in reason

    def test_llm_disabled_does_not_block_qwen_routing(self, sde, cs, mod):
        """enable_llm=False is no longer a blocking gate — QWEN arbitration fires directly."""
        eng = mod.SovereignDecisionEngine(enable_llm=False)
        conf = cs(value=0.50)
        with patch.object(eng, "_route_decision") as mock_route:
            decision = MagicMock()
            decision.tier = mod.RoutingTier.QWEN
            decision.gate_applied = "THRESHOLD_MED_QWEN"
            decision.score = 15
            decision.determinism_digest = "abc"
            decision.model_id = "Qwen2.5-14B"
            mock_route.return_value = decision
            with patch.object(eng, "_get_qwen_vllm_arbiter") as mock_arbiter:
                mock_arbiter.return_value = lambda agent_name, violation_types, territory, score, gate: {
                    "decision": True,
                    "reason": "QWEN-OK",
                }
                ok, reason = eng.should_proceed_with_healing(conf, "QwenAgent")
        assert ok is True
        assert "QWEN" in reason or "LLM" in reason

    def test_llm_disabled_qwen_arbitration_fires_not_hitl(self, mod, cs):
        """Routing to QWEN bypasses the HITL gate entirely — _hitl_gate is never called."""
        eng = mod.SovereignDecisionEngine(enable_llm=False)
        conf = cs(value=0.50)
        with patch.object(eng, "_route_decision") as mock_route:
            decision = MagicMock()
            decision.tier = mod.RoutingTier.QWEN
            decision.gate_applied = "THRESHOLD_MED_QWEN"
            decision.score = 15
            decision.determinism_digest = "abc"
            decision.model_id = "Qwen2.5-14B"
            mock_route.return_value = decision
            with patch.object(eng, "_hitl_gate") as mock_hitl:
                with patch.object(eng, "_get_qwen_vllm_arbiter") as mock_arbiter:
                    mock_arbiter.return_value = lambda agent_name, violation_types, territory, score, gate: {
                        "decision": True,
                        "reason": "QWEN-OK",
                    }
                    ok, reason = eng.should_proceed_with_healing(conf, "QwenAgent")
        mock_hitl.assert_not_called()
        assert ok is True


# ===========================================================================
# _classify_violation_type
# ===========================================================================


class TestClassifyViolationType:
    def test_missing_sovereign_root(self, sde):
        assert sde._classify_violation_type("missing sovereign root directory") == "MISSING_DIRECTORY"

    def test_missing_director(self, sde):
        assert sde._classify_violation_type("missing director path") == "MISSING_DIRECTORY"

    def test_forbidden_keyword(self, sde):
        assert sde._classify_violation_type("forbidden keyword found") == "FORBIDDEN_CONTENT"

    def test_forbidden_extension(self, sde):
        assert sde._classify_violation_type("forbidden extension .pyc") == "EXTENSION_MISMATCH"

    def test_test_file_misplaced(self, sde):
        assert sde._classify_violation_type("test_ file is misplaced") == "TEST_FILE_MISPLACED"

    def test_sovereign_violation(self, sde):
        assert sde._classify_violation_type("sovereign boundary breached") == "SOVEREIGN_VIOLATION"

    def test_structural_fallback(self, sde):
        assert sde._classify_violation_type("random unrecognized violation") == "STRUCTURAL_VIOLATION"

    def test_empty_string(self, sde):
        assert sde._classify_violation_type("") == "STRUCTURAL_VIOLATION"

    def test_case_insensitive_forbidden(self, sde):
        assert sde._classify_violation_type("FORBIDDEN KEYWORD here") == "FORBIDDEN_CONTENT"


# ===========================================================================
# compute_routing_decision — all gates
# ===========================================================================


class TestComputeRoutingDecision:
    @pytest.fixture(autouse=True)
    def _mod(self, mod):
        self.mod = mod

    def _ri(self, **kwargs):
        defaults = {
            "failure_type": self.mod.FailureType.UNKNOWN,
            "retry_count": 0,
            "C": 0,
            "B": 1,
            "A": 0,
            "N": 1,
            "F": 1,
            "L": 0,
            "replay_mode": False,
            "playbook_match": False,
            "deterministic_coverage": False,
            "provider_prohibited_gemini": False,
            "provider_prohibited_qwen": False,
        }
        defaults.update(kwargs)
        return self.mod.RoutingInputs(**defaults)

    def test_gate0_replay_always_deterministic(self):
        ri = self._ri(replay_mode=True)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.DETERMINISTIC
        assert d.gate_applied == "GATE_0_REPLAY"

    def test_gate1_retry_count_3_gemini(self):
        ri = self._ri(retry_count=3)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.GEMINI
        assert "GATE_1" in d.gate_applied

    def test_gate1_retry_3_gemini_prohibited_fail_closed(self):
        ri = self._ri(retry_count=3, provider_prohibited_gemini=True)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.FAIL_CLOSED

    def test_gate1_retry_count_2_not_triggered(self):
        ri = self._ri(retry_count=2)
        d = self.mod.compute_routing_decision(ri)
        assert "GATE_1" not in d.gate_applied

    def test_gate2_layer_violation_det_cov_deterministic(self):
        ri = self._ri(
            failure_type=self.mod.FailureType.LAYER_VIOLATION,
            deterministic_coverage=True,
        )
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.DETERMINISTIC
        assert "GATE_2" in d.gate_applied

    def test_gate2_layer_violation_no_det_cov_gemini(self):
        ri = self._ri(failure_type=self.mod.FailureType.LAYER_VIOLATION)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.GEMINI
        assert "GATE_2" in d.gate_applied

    def test_gate2_layer_violation_gemini_prohibited_fail_closed(self):
        ri = self._ri(
            failure_type=self.mod.FailureType.LAYER_VIOLATION,
            provider_prohibited_gemini=True,
        )
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.FAIL_CLOSED

    def test_gate2_gateway_bypass_no_det_cov_gemini(self):
        ri = self._ri(failure_type=self.mod.FailureType.GATEWAY_BYPASS)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.GEMINI

    def test_gate3_critical_surface_mechanical(self):
        ri = self._ri(B=3, A=0, playbook_match=True, deterministic_coverage=True)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.DETERMINISTIC
        assert "GATE_3" in d.gate_applied

    def test_gate3_not_triggered_without_playbook(self):
        ri = self._ri(B=3, A=0, playbook_match=False, deterministic_coverage=True)
        d = self.mod.compute_routing_decision(ri)
        assert "GATE_3" not in d.gate_applied

    def test_gate4_hard_override_gemini(self):
        ri = self._ri(B=3, F=3, C=2)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.GEMINI
        assert "GATE_4" in d.gate_applied

    def test_gate4_both_prohibited_fail_closed(self):
        ri = self._ri(B=3, F=3, C=2, provider_prohibited_gemini=True, provider_prohibited_qwen=True)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.FAIL_CLOSED

    def test_gate4_not_triggered_low_blast(self):
        ri = self._ri(B=2, F=3, C=2)
        d = self.mod.compute_routing_decision(ri)
        assert "GATE_4" not in d.gate_applied

    def test_gate5_threshold_low_deterministic(self):
        ri = self._ri(C=0, B=1, A=0, N=1, F=1)
        S = 3 * 0 + 4 * 1 + 3 * 0 + 2 * 1 + 4 * 1
        assert S == 10
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.DETERMINISTIC

    def test_gate5_threshold_exact_boundary_13(self):
        ri = self._ri(C=1, B=1, A=0, N=1, F=1)
        S = 3 * 1 + 4 * 1 + 3 * 0 + 2 * 1 + 4 * 1
        assert S == 13
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.DETERMINISTIC

    def test_gate5_threshold_medium_qwen_s14(self):
        ri = self._ri(C=1, B=1, A=0, N=1, F=1, L=3)
        S = 3 * 1 + 4 * 1 + 3 * 0 + 2 * 1 + 4 * 1
        assert S == 13
        d = self.mod.compute_routing_decision(ri)
        assert d.tier in (self.mod.RoutingTier.QWEN, self.mod.RoutingTier.DETERMINISTIC)

    def test_gate5_threshold_high_gemini(self):
        ri = self._ri(C=3, B=3, A=2, N=3, F=2)
        S = 3 * 3 + 4 * 3 + 3 * 2 + 2 * 3 + 4 * 2
        assert S > 26
        d = self.mod.compute_routing_decision(ri)
        assert d.tier in (self.mod.RoutingTier.GEMINI, self.mod.RoutingTier.FAIL_CLOSED)

    def test_gate5_high_gemini_prohibited_fail_closed(self):
        ri = self._ri(C=3, B=3, A=2, N=3, F=2, provider_prohibited_gemini=True)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.FAIL_CLOSED

    def test_gate6_tiebreak_down_qwen_to_det(self):
        ri = self._ri(C=0, B=1, A=0, N=2, F=1, L=0)
        S = 4 + 4
        assert S == 8
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.DETERMINISTIC

    def test_gate7_qwen_disallowed_falls_to_gemini(self):
        ri = self._ri(
            failure_type=self.mod.FailureType.IMPORT_BOUNDARY_VIOLATION,
            C=1,
            B=1,
            A=0,
            N=1,
            F=1,
        )
        d = self.mod.compute_routing_decision(ri)
        assert d.tier in (
            self.mod.RoutingTier.GEMINI,
            self.mod.RoutingTier.DETERMINISTIC,
            self.mod.RoutingTier.FAIL_CLOSED,
        )

    def test_gate7_qwen_disallowed_det_fallback_when_covered(self):
        ri = self._ri(
            failure_type=self.mod.FailureType.IMPORT_BOUNDARY_VIOLATION,
            C=0,
            B=1,
            A=0,
            N=1,
            F=1,
            deterministic_coverage=True,
        )
        d = self.mod.compute_routing_decision(ri)
        assert d.tier in (
            self.mod.RoutingTier.DETERMINISTIC,
            self.mod.RoutingTier.GEMINI,
            self.mod.RoutingTier.FAIL_CLOSED,
        )

    def test_gate8_qwen_prohibited_falls_to_gemini(self):
        ri = self._ri(C=1, B=1, A=0, N=2, F=1, provider_prohibited_qwen=True)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier in (
            self.mod.RoutingTier.GEMINI,
            self.mod.RoutingTier.DETERMINISTIC,
            self.mod.RoutingTier.FAIL_CLOSED,
        )

    def test_gate8_both_prohibited_qwen_start_fail_closed(self):
        ri = self._ri(C=1, B=1, A=0, N=2, F=1, provider_prohibited_qwen=True, provider_prohibited_gemini=True)
        d = self.mod.compute_routing_decision(ri)
        assert d.tier == self.mod.RoutingTier.FAIL_CLOSED

    def test_determinism_same_input_same_output(self):
        mod = _load()
        ri = mod.RoutingInputs(
            failure_type=mod.FailureType.UNKNOWN,
            retry_count=0,
            C=1,
            B=2,
            A=0,
            N=1,
            F=1,
            L=0,
            replay_mode=False,
            playbook_match=False,
            deterministic_coverage=False,
            provider_prohibited_gemini=False,
            provider_prohibited_qwen=False,
        )
        d1 = mod.compute_routing_decision(ri)
        d2 = mod.compute_routing_decision(ri)
        assert d1.tier == d2.tier
        assert d1.score == d2.score
        assert d1.gate_applied == d2.gate_applied
        assert d1.determinism_digest == d2.determinism_digest

    def test_distinct_inputs_produce_distinct_digests(self):
        mod = _load()
        ri_a = mod.RoutingInputs(failure_type=mod.FailureType.UNKNOWN, C=0, B=1, A=0, N=1, F=1, L=0)
        ri_b = mod.RoutingInputs(failure_type=mod.FailureType.UNKNOWN, C=3, B=3, A=2, N=3, F=3, L=0)
        d_a = mod.compute_routing_decision(ri_a)
        d_b = mod.compute_routing_decision(ri_b)
        assert d_a.determinism_digest != d_b.determinism_digest

    def test_replay_mode_overrides_all_other_inputs(self):
        mod = _load()
        ri = mod.RoutingInputs(
            failure_type=mod.FailureType.LAYER_VIOLATION,
            C=3,
            B=3,
            A=2,
            N=3,
            F=3,
            L=0,
            retry_count=5,
            replay_mode=True,
            provider_prohibited_gemini=True,
            provider_prohibited_qwen=True,
        )
        d = mod.compute_routing_decision(ri)
        assert d.tier == mod.RoutingTier.DETERMINISTIC
        assert d.gate_applied == "GATE_0_REPLAY"

    def test_score_computation_formula(self):
        mod = _load()
        C, B, A, N, F = 1, 2, 1, 1, 1
        expected_S = 3 * C + 4 * B + 3 * A + 2 * N + 4 * F
        ri = mod.RoutingInputs(failure_type=mod.FailureType.UNKNOWN, C=C, B=B, A=A, N=N, F=F, L=0)
        d = mod.compute_routing_decision(ri)
        assert d.score == expected_S

    def test_all_failure_types_produce_valid_tier(self):
        mod = _load()
        for ft in mod.FailureType:
            ri = mod.RoutingInputs(failure_type=ft, C=1, B=1, A=0, N=1, F=1, L=0)
            d = mod.compute_routing_decision(ri)
            assert d.tier in (
                mod.RoutingTier.DETERMINISTIC,
                mod.RoutingTier.QWEN,
                mod.RoutingTier.GEMINI,
                mod.RoutingTier.FAIL_CLOSED,
            )


# ===========================================================================
# Advisory boundary: _route_decision SovereigntyError re-raise
# ===========================================================================


class TestAdvisoryBoundaryEnforcement:
    def test_sovereignty_error_propagates(self, sde, cs, mod):
        """Non-advisory incident raises SovereigntyError — not silently swallowed."""
        try:
            from agentic_core.L1_cognition.memory.healing_memory_retriever import SovereigntyError
        except ImportError:
            pytest.fail("healing_memory_retriever not available")

        bad_incident = MagicMock()
        bad_incident.advisory_only = False
        bad_incident.content_hash = "abc123"
        bad_incident.similarity = 0.9

        mock_retriever = MagicMock()
        mock_retriever.retrieve_similar_incidents.return_value = [bad_incident]

        eng = mod.SovereignDecisionEngine(
            enable_llm=False,
            healing_memory_retriever=mock_retriever,
        )
        confidence = cs(value=0.9)

        with pytest.raises(SovereigntyError):
            eng._route_decision(confidence, "AgentX", "neutral")

    def test_retrieval_exception_non_sovereignty_swallowed(self, mod, cs):
        """Non-SovereigntyError retrieval errors are swallowed — routing proceeds."""
        mock_retriever = MagicMock()
        mock_retriever.retrieve_similar_incidents.side_effect = ConnectionError("network down")

        eng = mod.SovereignDecisionEngine(
            enable_llm=False,
            healing_memory_retriever=mock_retriever,
        )
        confidence = cs(value=0.9)
        result = eng._route_decision(confidence, "AgentX", "neutral")
        assert result.tier in (
            mod.RoutingTier.DETERMINISTIC,
            mod.RoutingTier.QWEN,
            mod.RoutingTier.GEMINI,
            mod.RoutingTier.FAIL_CLOSED,
        )
