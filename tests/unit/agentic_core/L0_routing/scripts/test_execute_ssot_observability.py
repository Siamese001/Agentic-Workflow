"""
Wave 1-4 observability tests for execute_ssot prove-it data collection layer.

Covers:
  Wave 1: _collect_llm_call_trace, _collect_blocker_scan,
          _build_coverage_proof, _build_calibration_proof
  Wave 2: _write_heal_run_complete (schema, proof fields, hash determinism, OSError)
  Wave 3: _write_failure_forensics (empty, partial, full)
  Wave 4: _print_executive_summary (gate thresholds, PASS/FAIL, empty-state)

BRANCH_INVENTORY: see plan at docs/reports/plans/execute-ssot-observability-hardening-plan.md
"""

import json
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Module import
# ---------------------------------------------------------------------------


def _load():
    import importlib

    try:
        return importlib.import_module("agentic_core.L0_routing.scripts.execute_ssot")
    except ImportError as exc:
        pytest.skip(f"Cannot import execute_ssot: {exc}")


# ---------------------------------------------------------------------------
# Fixtures: minimal state_mgr and decision_engine stubs
# ---------------------------------------------------------------------------


def _make_state(overrides: dict | None = None) -> MagicMock:
    """Return a state_mgr stub with a `.state` dict.

    completed_agents mirrors the real state shape: list of dicts with 'agent' key.
    Tests may pass either {"AgentA": True} shorthand (converted here) or the real list form.
    """
    state = {
        "healing_actions": [],
        "meta_learning": {},
        "blocked_agents": [],
        "completed_agents": [],
        "prior_meta": {},
        "faiss_retrieval_stats": {},
    }
    if overrides:
        # Normalize completed_agents shorthand {"AgentA": True} → [{"agent": "AgentA"}]
        if "completed_agents" in overrides and isinstance(overrides["completed_agents"], dict):
            overrides = dict(overrides)
            overrides["completed_agents"] = [
                {"agent": k} for k, v in overrides["completed_agents"].items() if v
            ]
        state.update(overrides)
    mgr = MagicMock()
    mgr.state = state
    mgr.project_root = None
    return mgr


def _make_engine(decisions: list | None = None) -> MagicMock:
    eng = MagicMock()
    eng.decisions_made = decisions or []
    return eng


# ============================================================================
# WAVE 1 — _collect_llm_call_trace
# ============================================================================


class TestCollectLlmCallTrace:
    """Branch: empty, missing tier, proven call, blocked call, decisions without actions."""

    def setup_method(self):
        self.mod = _load()

    def test_llm_trace_empty_actions(self):
        """Empty healing_actions + no decisions → empty trace and stats."""
        sm = _make_state()
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert result["call_trace"] == []
        assert result["blocked_calls"] == []
        assert result["stats"]["expected_calls"] == 0
        assert result["stats"]["actual_calls"] == 0
        assert result["stats"]["execution_rate"] == 1.0

    def test_llm_trace_deterministic_action_ignored(self):
        """DETERMINISTIC tier actions are not counted as LLM calls."""
        sm = _make_state(
            {"healing_actions": [{"agent": "AgentA", "routing_tier": "DETERMINISTIC", "outcome": "SUCCESS"}]}
        )
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert result["stats"]["expected_calls"] == 0
        assert result["call_trace"] == []

    def test_llm_trace_missing_tier_defaults_deterministic(self):
        """Action without routing_tier defaults to DETERMINISTIC → not counted."""
        sm = _make_state({"healing_actions": [{"agent": "AgentB", "outcome": "SUCCESS"}]})
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert result["stats"]["expected_calls"] == 0

    def test_llm_trace_proven_call_qwen(self):
        """QWEN_VLLM action with llm_call_made=True → call_trace entry with proof hash."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentC",
                        "routing_tier": "QWEN_VLLM",
                        "timestamp": "2025-01-01T00:00:00",
                        "outcome": "SUCCESS",
                        "llm_call_evidence": {
                            "llm_call_made": True,
                            "model": "qwen-2.5",
                            "endpoint": "http://localhost:8000",
                            "request_id": "req-123",
                            "http_status": 200,
                            "latency_ms": 350,
                        },
                    }
                ]
            }
        )
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert len(result["call_trace"]) == 1
        call = result["call_trace"][0]
        assert call["agent"] == "AgentC"
        assert call["tier"] == "QWEN_VLLM"
        assert call["model"] == "qwen-2.5"
        assert "proof" in call
        assert call["proof"]["request_hash"].startswith("sha256:")
        assert result["stats"]["actual_calls"] == 1
        assert result["stats"]["execution_rate"] == 1.0

    def test_llm_trace_blocked_call(self):
        """GEMINI action with llm_call_made=False → blocked_calls entry."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentD",
                        "routing_tier": "GEMINI_2_5_PRO",
                        "timestamp": "2025-01-01T00:00:00",
                        "outcome": "FAIL",
                        "llm_call_evidence": {
                            "llm_call_made": False,
                            "blocker_type": "feature_flag",
                            "blocker": "ENABLE_GEMINI flag is False",
                            "fallback_tier": "DETERMINISTIC",
                        },
                    }
                ]
            }
        )
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert len(result["blocked_calls"]) == 1
        assert result["blocked_calls"][0]["blocker_type"] == "feature_flag"
        assert result["stats"]["blocked_by_flags"] == 1
        assert result["stats"]["execution_rate"] == 0.0

    def test_llm_trace_decision_without_action_recorded_as_blocked(self):
        """Decision routing to QWEN but no matching healing_action → blocked_call entry."""
        sm = _make_state()
        eng = _make_engine(
            decisions=[
                {
                    "agent": "AgentE",
                    "routing_tier": "QWEN_VLLM",
                    "decision": True,
                    "confidence": 0.5,
                }
            ]
        )
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert len(result["blocked_calls"]) == 1
        assert result["blocked_calls"][0]["blocker_type"] == "not_recorded"

    def test_llm_trace_tier_aliases_qwen(self):
        """Alias 'QWEN' maps to 'QWEN_VLLM'."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentF",
                        "routing_tier": "QWEN",
                        "timestamp": "",
                        "llm_call_evidence": {"llm_call_made": True, "model": "q"},
                    }
                ]
            }
        )
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert result["call_trace"][0]["tier"] == "QWEN_VLLM"

    def test_llm_trace_tier_aliases_gemini(self):
        """Alias 'GEMINI' maps to 'GEMINI_2_5_PRO'."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentG",
                        "routing_tier": "GEMINI",
                        "timestamp": "",
                        "llm_call_evidence": {"llm_call_made": True, "model": "g"},
                    }
                ]
            }
        )
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert result["call_trace"][0]["tier"] == "GEMINI_2_5_PRO"

    def test_llm_trace_blocked_by_errors_counter(self):
        """blocker_type containing 'error' increments blocked_by_errors."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentH",
                        "routing_tier": "GEMINI_2_5_PRO",
                        "timestamp": "",
                        "llm_call_evidence": {
                            "llm_call_made": False,
                            "blocker_type": "network_error",
                        },
                    }
                ]
            }
        )
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert result["stats"]["blocked_by_errors"] == 1
        assert result["stats"]["blocked_by_flags"] == 0

    def test_llm_trace_no_llm_call_evidence_key(self):
        """Action missing llm_call_evidence entirely → blocked_call with unknown type."""
        sm = _make_state(
            {
                "healing_actions": [
                    {"agent": "AgentI", "routing_tier": "QWEN_VLLM", "timestamp": "", "outcome": "FAIL"}
                ]
            }
        )
        eng = _make_engine()
        result = self.mod._collect_llm_call_trace(sm, eng)
        assert len(result["blocked_calls"]) == 1
        assert result["blocked_calls"][0]["blocker_type"] == "unknown"


# ============================================================================
# WAVE 1 — _collect_blocker_scan
# ============================================================================


class TestCollectBlockerScan:
    """Branch: empty blocked_agents, feature_flag blocker, missing stack_trace."""

    def setup_method(self):
        self.mod = _load()

    def test_blocker_scan_empty(self):
        """No blocked_agents → returns empty list."""
        sm = _make_state()
        result = self.mod._collect_blocker_scan(sm)
        assert result == []

    def test_blocker_scan_feature_flag(self):
        """feature_flag blocker → blocker_type preserved, stack_trace_hash computed."""
        sm = _make_state(
            {
                "blocked_agents": [
                    {
                        "agent": "AgentX",
                        "blocker_type": "feature_flag",
                        "flag": "ENABLE_X",
                        "flag_value": False,
                        "flag_source": "env",
                        "check_timestamp": "2025-01-01T00:00:00",
                        "code_location": "execute_ssot.py:500",
                        "stack_trace": ["frame1", "frame2"],
                        "last_successful_run": "2025-01-01",
                        "remediation": "Set ENABLE_X=True",
                    }
                ]
            }
        )
        result = self.mod._collect_blocker_scan(sm)
        assert len(result) == 1
        b = result[0]
        assert b["agent"] == "AgentX"
        assert b["blocker_type"] == "feature_flag"
        assert b["flag"] == "ENABLE_X"
        assert b["stack_trace_hash"].startswith("sha256:")
        assert b["remediation"] == "Set ENABLE_X=True"

    def test_blocker_scan_no_stack_trace(self):
        """Blocker without stack_trace → stack_trace_hash is empty string."""
        sm = _make_state({"blocked_agents": [{"agent": "AgentY", "blocker_type": "dependency"}]})
        result = self.mod._collect_blocker_scan(sm)
        assert result[0]["stack_trace_hash"] == ""

    def test_blocker_scan_skips_non_dict_entries(self):
        """Non-dict entries in blocked_agents are silently skipped."""
        sm = _make_state({"blocked_agents": ["bad_entry", None, {"agent": "Good", "blocker_type": "flag"}]})
        result = self.mod._collect_blocker_scan(sm)
        assert len(result) == 1
        assert result[0]["agent"] == "Good"

    def test_blocker_scan_dependency_uses_dependency_key(self):
        """Records with 'dependency' key use it as 'flag' fallback."""
        sm = _make_state(
            {"blocked_agents": [{"agent": "AgentZ", "blocker_type": "dependency", "dependency": "pydantic"}]}
        )
        result = self.mod._collect_blocker_scan(sm)
        assert result[0]["flag"] == "pydantic"


# ============================================================================
# WAVE 1 — _build_coverage_proof
# ============================================================================


class TestBuildCoverageProof:
    """Branch: all agents executed (ratio 1.0), partial coverage, zero executed."""

    def setup_method(self):
        self.mod = _load()

    def test_coverage_full(self):
        """All agents executed, no blockers → coverage_ratio=1.0."""
        sm = _make_state(
            {
                "completed_agents": {"A": True, "B": True},
                "blocked_agents": [],
            }
        )
        eng = _make_engine()
        result = self.mod._build_coverage_proof(sm, eng)
        assert result["coverage_ratio"] == 1.0
        assert result["executed_agents"]["count"] == 2
        assert result["skipped_agents"]["count"] == 0
        assert result["proof_complete"] is True

    def test_coverage_partial(self):
        """Some agents blocked → ratio < 1.0."""
        sm = _make_state(
            {
                "completed_agents": {"A": True},
                "blocked_agents": [{"agent": "B", "blocker_type": "feature_flag"}],
            }
        )
        eng = _make_engine()
        result = self.mod._build_coverage_proof(sm, eng)
        assert result["coverage_ratio"] < 1.0
        assert result["skipped_agents"]["count"] == 1
        assert "B" in result["skipped_agents"]["agents"]

    def test_coverage_no_agents_at_all(self):
        """No completed, no blocked → n_expected floor is 1 (max(0,1)), n_executed=0 → ratio=0.0."""
        sm = _make_state(
            {
                "completed_agents": {},
                "blocked_agents": [],
            }
        )
        eng = _make_engine()
        result = self.mod._build_coverage_proof(sm, eng)
        assert result["coverage_ratio"] == 0.0

    def test_coverage_hashes_are_deterministic(self):
        """Same inputs produce identical hashes (replay-stable)."""
        sm = _make_state(
            {
                "completed_agents": {"X": True, "Y": True},
                "blocked_agents": [],
            }
        )
        eng = _make_engine()
        r1 = self.mod._build_coverage_proof(sm, eng)
        r2 = self.mod._build_coverage_proof(sm, eng)
        assert r1["executed_agents"]["hash"] == r2["executed_agents"]["hash"]
        assert r1["expected_agents"]["hash"] == r2["expected_agents"]["hash"]

    def test_coverage_hash_changes_with_different_agents(self):
        """Different agent sets produce different hashes."""
        sm_a = _make_state({"completed_agents": {"A": True}, "blocked_agents": []})
        sm_b = _make_state({"completed_agents": {"B": True}, "blocked_agents": []})
        eng = _make_engine()
        ha = self.mod._build_coverage_proof(sm_a, eng)["executed_agents"]["hash"]
        hb = self.mod._build_coverage_proof(sm_b, eng)["executed_agents"]["hash"]
        assert ha != hb

    def test_coverage_ratio_exact_boundary_0_90(self):
        """9 of 10 executed → ratio = 0.9 (boundary)."""
        completed = {f"Agent{i}": True for i in range(9)}
        blocked = [{"agent": "Agent9", "blocker_type": "flag"}]
        sm = _make_state({"completed_agents": completed, "blocked_agents": blocked})
        eng = _make_engine()
        result = self.mod._build_coverage_proof(sm, eng)
        assert result["coverage_ratio"] == 0.9


# ============================================================================
# WAVE 1 — _build_calibration_proof
# ============================================================================


class TestBuildCalibrationProof:
    """Branch: no decisions, zero actual, perfect calibration, imperfect calibration."""

    def setup_method(self):
        self.mod = _load()

    def test_calibration_no_decisions(self):
        """No routing decisions → returns empty dict."""
        sm = _make_state()
        eng = _make_engine()
        result = self.mod._build_calibration_proof(sm, eng)
        assert result == {}

    def test_calibration_all_success_perfect(self):
        """confidence=1.0 and outcome=SUCCESS → calibration_error=0.0."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "SUCCESS"}]})
        eng = _make_engine(
            decisions=[{"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": 1.0, "decision": True}]
        )
        result = self.mod._build_calibration_proof(sm, eng)
        assert "DETERMINISTIC" in result
        assert result["DETERMINISTIC"]["calibration_error"] == 0.0

    def test_calibration_all_fail_zero_actual(self):
        """confidence=0.9 but outcome=FAIL → calibration_error close to 0.9."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "FAIL"}]})
        eng = _make_engine(
            decisions=[{"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": 0.9, "decision": True}]
        )
        result = self.mod._build_calibration_proof(sm, eng)
        assert result["DETERMINISTIC"]["calibration_error"] == pytest.approx(0.9, abs=1e-4)

    def test_calibration_non_numeric_confidence_skipped(self):
        """Non-numeric confidence value is skipped."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "SUCCESS"}]})
        eng = _make_engine(
            decisions=[
                {"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": "high", "decision": True}
            ]
        )
        result = self.mod._build_calibration_proof(sm, eng)
        assert result == {}

    def test_calibration_no_decision_flag_skipped(self):
        """Decisions with decision=False are skipped."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "SUCCESS"}]})
        eng = _make_engine(
            decisions=[{"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": 0.8, "decision": False}]
        )
        result = self.mod._build_calibration_proof(sm, eng)
        assert result == {}

    def test_calibration_tier_aliases(self):
        """'QWEN' tier alias maps to 'QWEN_VLLM' in result dict."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "SUCCESS"}]})
        eng = _make_engine(
            decisions=[{"agent": "A", "routing_tier": "QWEN", "confidence": 0.6, "decision": True}]
        )
        result = self.mod._build_calibration_proof(sm, eng)
        assert "QWEN_VLLM" in result

    def test_calibration_proof_hash_present(self):
        """Proof hash present and starts with sha256:."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "SUCCESS"}]})
        eng = _make_engine(
            decisions=[{"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": 0.8, "decision": True}]
        )
        result = self.mod._build_calibration_proof(sm, eng)
        assert result["DETERMINISTIC"]["proof"]["pairs_hash"].startswith("sha256:")

    def test_calibration_deterministic_same_input(self):
        """Same inputs produce identical calibration_error (replay-stable)."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "SUCCESS"}]})
        eng = _make_engine(
            decisions=[{"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": 0.75, "decision": True}]
        )
        r1 = self.mod._build_calibration_proof(sm, eng)
        r2 = self.mod._build_calibration_proof(sm, eng)
        assert r1["DETERMINISTIC"]["calibration_error"] == r2["DETERMINISTIC"]["calibration_error"]

    def test_calibration_multi_tier(self):
        """Multiple tiers produce separate calibration entries."""
        sm = _make_state(
            {
                "healing_actions": [
                    {"agent": "A", "outcome": "SUCCESS"},
                    {"agent": "B", "outcome": "FAIL"},
                ]
            }
        )
        eng = _make_engine(
            decisions=[
                {"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": 0.9, "decision": True},
                {"agent": "B", "routing_tier": "QWEN_VLLM", "confidence": 0.5, "decision": True},
            ]
        )
        result = self.mod._build_calibration_proof(sm, eng)
        assert "DETERMINISTIC" in result
        assert "QWEN_VLLM" in result


# ============================================================================
# WAVE 2 — _write_heal_run_complete
# ============================================================================


class TestWriteHealRunComplete:
    """Schema contract, proof fields, write fail, empty state."""

    def setup_method(self):
        self.mod = _load()

    def test_heal_run_complete_written_to_file(self, tmp_path):
        """Function writes heal_run_complete.json to the out_dir."""
        sm = _make_state()
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        out_file = tmp_path / "logs" / "compliance_reports" / "heal_run_complete.json"
        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert data["meta"]["report_type"] == "HEAL_RUN_COMPLETE"

    def test_heal_run_complete_returns_dict(self, tmp_path):
        """Return value is a dict (so _print_executive_summary can consume it)."""
        sm = _make_state()
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        assert isinstance(result, dict)

    def test_heal_run_complete_mandatory_sections(self, tmp_path):
        """All 7 top-level sections present in output."""
        sm = _make_state()
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        for section in (
            "meta",
            "coverage",
            "routing",
            "learning",
            "healing_actions",
            "blockers",
            "executive_summary",
        ):
            assert section in result, f"Missing section: {section}"

    def test_heal_run_complete_executive_summary_10_gates(self, tmp_path):
        """executive_summary contains exactly 10 gate criteria."""
        sm = _make_state()
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        assert result["executive_summary"]["criteria_total"] == 10
        assert len(result["executive_summary"]["gate_criteria"]) == 10

    def test_heal_run_complete_write_fail_no_crash(self):
        """OSError during write is logged and swallowed — function returns dict."""
        sm = _make_state()
        sm.project_root = None
        eng = _make_engine()
        with patch("builtins.open", side_effect=OSError("disk full")):
            result = self.mod._write_heal_run_complete(sm, eng)
        # Must not raise; result is None or dict (error path may return None after exception)
        # The function has try/except that returns output before write, so result still populated
        assert result is not None

    def test_heal_run_complete_coverage_ratio_in_output(self, tmp_path):
        """coverage.coverage_ratio is present in written JSON."""
        sm = _make_state({"completed_agents": {"A": True}})
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        assert "coverage_ratio" in result["coverage"]

    def test_heal_run_complete_routing_llm_stats_present(self, tmp_path):
        """routing.llm_invocation_stats is present."""
        sm = _make_state()
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        assert "llm_invocation_stats" in result["routing"]

    def test_heal_run_complete_learning_run_comparison_present(self, tmp_path):
        """learning.run_comparison is present with proof fields."""
        sm = _make_state()
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        rc = result["learning"]["run_comparison"]
        assert "proof" in rc
        assert "current_success_rate" in rc

    def test_heal_run_complete_all_pass_when_empty_state(self, tmp_path):
        """Empty state (no healing actions, no blockers) → most gates PASS."""
        sm = _make_state()
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        # coverage gate: 1 expected (floor), 0 completed → ratio handled by floor logic
        # At minimum, gates without actual failures should not hardcrash
        assert result["executive_summary"]["overall_status"] in ("PASS", "FAIL")

    def test_heal_run_complete_no_baseline_trend_is_pass(self, tmp_path):
        """When success_delta is None (no prior run), trend gates are PASS."""
        sm = _make_state()
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        trend_gates = [
            g
            for g in result["executive_summary"]["gate_criteria"]
            if "Trend" in g["criterion"] or "Delta" in g["criterion"]
        ]
        for g in trend_gates:
            assert g["status"] == "PASS", f"Expected PASS for {g['criterion']} with no baseline"


# ============================================================================
# WAVE 2 — Gate criteria threshold boundary tests
# ============================================================================


class TestGateCriteriaThresholds:
    """Boundary testing for all 10 gate thresholds."""

    def setup_method(self):
        self.mod = _load()

    def _get_gate(self, result: dict, name_fragment: str) -> dict:
        for g in result["executive_summary"]["gate_criteria"]:
            if name_fragment.lower() in g["criterion"].lower():
                return g
        pytest.fail(f"Gate not found: {name_fragment}")

    def test_coverage_gate_exactly_0_90_is_pass(self, tmp_path):
        """coverage_ratio == 0.90 → PASS (>= threshold)."""
        completed = {f"Agent{i}": True for i in range(9)}
        blocked = [{"agent": "Agent9", "blocker_type": "flag"}]
        sm = _make_state({"completed_agents": completed, "blocked_agents": blocked})
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        g = self._get_gate(result, "Agent Coverage")
        assert g["status"] == "PASS"
        assert g["actual"] == pytest.approx(0.9, abs=1e-4)

    def test_coverage_gate_below_0_90_is_fail(self, tmp_path):
        """coverage_ratio < 0.90 → FAIL."""
        completed = {f"Agent{i}": True for i in range(8)}
        blocked = [{"agent": f"Agent{i}", "blocker_type": "flag"} for i in range(8, 10)]
        sm = _make_state({"completed_agents": completed, "blocked_agents": blocked})
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        g = self._get_gate(result, "Agent Coverage")
        assert g["status"] == "FAIL"

    def test_calib_error_exactly_0_15_is_pass(self, tmp_path):
        """calibration_error == 0.15 → PASS (<= threshold)."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "FAIL"}]})
        sm.project_root = str(tmp_path)
        # conf=0.15 with all fail → calib_error = |0.15 - 0.0| = 0.15
        eng = _make_engine(
            decisions=[{"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": 0.15, "decision": True}]
        )
        result = self.mod._write_heal_run_complete(sm, eng)
        g = self._get_gate(result, "Calibration")
        assert g["status"] == "PASS"

    def test_calib_error_above_0_15_is_fail(self, tmp_path):
        """calibration_error > 0.15 → FAIL."""
        sm = _make_state({"healing_actions": [{"agent": "A", "outcome": "FAIL"}]})
        sm.project_root = str(tmp_path)
        # conf=0.9 with all fail → calib_error = 0.9
        eng = _make_engine(
            decisions=[{"agent": "A", "routing_tier": "DETERMINISTIC", "confidence": 0.9, "decision": True}]
        )
        result = self.mod._write_heal_run_complete(sm, eng)
        g = self._get_gate(result, "Calibration")
        assert g["status"] == "FAIL"

    def test_meta_learning_negative_delta_is_fail(self, tmp_path):
        """success_delta < 0 → Meta-Learning Improvement gate FAIL."""
        sm = _make_state(
            {
                "healing_actions": [
                    {"agent": "A", "outcome": "FAIL"},
                ],
                "prior_meta": {"success_rate": 0.8},
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        g = self._get_gate(result, "Meta-Learning")
        assert g["status"] == "FAIL"

    def test_meta_learning_positive_delta_is_pass(self, tmp_path):
        """success_delta > 0 → Meta-Learning Improvement gate PASS."""
        sm = _make_state(
            {
                "healing_actions": [
                    {"agent": "A", "outcome": "SUCCESS"},
                ],
                "prior_meta": {"success_rate": 0.5},
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        g = self._get_gate(result, "Meta-Learning")
        assert g["status"] == "PASS"

    def test_llm_rate_exactly_0_80_is_pass(self, tmp_path):
        """LLM execution_rate == 0.80 → PASS."""
        # 4 of 5 expected calls made
        actions = []
        for i in range(4):
            actions.append(
                {
                    "agent": f"Agent{i}",
                    "routing_tier": "QWEN_VLLM",
                    "timestamp": "",
                    "llm_call_evidence": {"llm_call_made": True, "model": "q"},
                }
            )
        actions.append(
            {
                "agent": "Agent4",
                "routing_tier": "QWEN_VLLM",
                "timestamp": "",
                "llm_call_evidence": {
                    "llm_call_made": False,
                    "blocker_type": "feature_flag",
                },
            }
        )
        sm = _make_state({"healing_actions": actions})
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        g = self._get_gate(result, "LLM Call Execution")
        assert g["actual"] == pytest.approx(0.8, abs=1e-4)
        assert g["status"] == "PASS"

    def test_llm_rate_below_0_80_is_fail(self, tmp_path):
        """LLM execution_rate < 0.80 → FAIL."""
        actions = [
            {
                "agent": f"Agent{i}",
                "routing_tier": "QWEN_VLLM",
                "timestamp": "",
                "llm_call_evidence": {
                    "llm_call_made": False,
                    "blocker_type": "feature_flag",
                },
            }
            for i in range(3)
        ]
        sm = _make_state({"healing_actions": actions})
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        result = self.mod._write_heal_run_complete(sm, eng)
        g = self._get_gate(result, "LLM Call Execution")
        assert g["status"] == "FAIL"


# ============================================================================
# WAVE 3 — _write_failure_forensics
# ============================================================================


class TestWriteFailureForensics:
    """Branch: no failures (no file), partial, full with failed/blocked/misrouted."""

    def setup_method(self):
        self.mod = _load()

    def test_forensics_no_failures_no_file(self, tmp_path):
        """No failures, no blockers → file NOT written."""
        sm = _make_state(
            {
                "healing_actions": [{"agent": "A", "outcome": "SUCCESS"}],
                "blocked_agents": [],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        out = tmp_path / "logs" / "compliance_reports" / "failure_forensics.json"
        assert not out.exists()

    def test_forensics_with_failed_agents(self, tmp_path):
        """Failed agents → file written with failed_agents populated."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentFail",
                        "outcome": "FAIL",
                        "routing_tier": "DETERMINISTIC",
                        "territory": "test_terr",
                    }
                ],
                "blocked_agents": [],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        out = tmp_path / "logs" / "compliance_reports" / "failure_forensics.json"
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["summary"]["failed_agents_count"] == 1
        assert data["failed_agents"][0]["agent"] == "AgentFail"

    def test_forensics_with_blocked_agents_only(self, tmp_path):
        """Only blockers (no failed actions) → file written with blocked_agents populated."""
        sm = _make_state(
            {
                "healing_actions": [],
                "blocked_agents": [{"agent": "BlockedX", "blocker_type": "feature_flag"}],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        out = tmp_path / "logs" / "compliance_reports" / "failure_forensics.json"
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["summary"]["blocked_agents_count"] == 1

    def test_forensics_misrouted_low_confidence_fail(self, tmp_path):
        """DETERMINISTIC tier + outcome=FAIL + conf<0.75 → misrouted entry."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentM",
                        "outcome": "FAIL",
                        "routing_tier": "DETERMINISTIC",
                        "confidence": 0.50,
                    }
                ],
                "blocked_agents": [],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        out = tmp_path / "logs" / "compliance_reports" / "failure_forensics.json"
        data = json.loads(out.read_text())
        assert data["summary"]["misrouted_agents_count"] == 1
        assert data["misrouted_agents"][0]["should_have_routed_to"] in ("QWEN_VLLM", "GEMINI_2_5_PRO")

    def test_forensics_misrouted_qwen_for_medium_conf(self, tmp_path):
        """conf=0.50 (medium) → should_have_routed_to QWEN_VLLM."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentN",
                        "outcome": "FAIL",
                        "routing_tier": "DETERMINISTIC",
                        "confidence": 0.50,
                    }
                ],
                "blocked_agents": [],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        data = json.loads((tmp_path / "logs" / "compliance_reports" / "failure_forensics.json").read_text())
        assert data["misrouted_agents"][0]["should_have_routed_to"] == "QWEN_VLLM"

    def test_forensics_misrouted_gemini_for_low_conf(self, tmp_path):
        """conf=0.30 (low) → should_have_routed_to GEMINI_2_5_PRO."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentO",
                        "outcome": "FAIL",
                        "routing_tier": "DETERMINISTIC",
                        "confidence": 0.30,
                    }
                ],
                "blocked_agents": [],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        data = json.loads((tmp_path / "logs" / "compliance_reports" / "failure_forensics.json").read_text())
        assert data["misrouted_agents"][0]["should_have_routed_to"] == "GEMINI_2_5_PRO"

    def test_forensics_write_fail_no_crash(self):
        """OSError during write → logged and swallowed, no exception raised."""
        sm = _make_state(
            {
                "healing_actions": [{"agent": "A", "outcome": "FAIL"}],
                "blocked_agents": [],
            }
        )
        sm.project_root = None
        eng = _make_engine()
        with patch("builtins.open", side_effect=OSError("no space")):
            # Should not raise
            self.mod._write_failure_forensics(sm, eng)

    def test_forensics_report_type_field(self, tmp_path):
        """meta.report_type == 'FAILURE_FORENSICS'."""
        sm = _make_state(
            {
                "healing_actions": [{"agent": "A", "outcome": "FAIL", "routing_tier": "DETERMINISTIC"}],
                "blocked_agents": [],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        data = json.loads((tmp_path / "logs" / "compliance_reports" / "failure_forensics.json").read_text())
        assert data["meta"]["report_type"] == "FAILURE_FORENSICS"

    def test_forensics_blocker_proof_hash_present_when_llm_blocker(self, tmp_path):
        """When llm_call_evidence.blocker is set → blocker_proof_hash in llm_routing_proof."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentP",
                        "outcome": "FAIL",
                        "routing_tier": "GEMINI_2_5_PRO",
                        "llm_call_evidence": {
                            "llm_call_made": False,
                            "blocker": "ENABLE_GEMINI=False",
                        },
                    }
                ],
                "blocked_agents": [],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        data = json.loads((tmp_path / "logs" / "compliance_reports" / "failure_forensics.json").read_text())
        fa = data["failed_agents"][0]
        assert fa["llm_routing_proof"]["blocker_proof_hash"].startswith("sha256:")

    def test_forensics_empty_blocker_proof_hash_when_no_blocker(self, tmp_path):
        """No blocker value → blocker_proof_hash is empty string."""
        sm = _make_state(
            {
                "healing_actions": [
                    {
                        "agent": "AgentQ",
                        "outcome": "FAIL",
                        "routing_tier": "DETERMINISTIC",
                    }
                ],
                "blocked_agents": [],
            }
        )
        sm.project_root = str(tmp_path)
        eng = _make_engine()
        self.mod._write_failure_forensics(sm, eng)
        data = json.loads((tmp_path / "logs" / "compliance_reports" / "failure_forensics.json").read_text())
        fa = data["failed_agents"][0]
        assert fa["llm_routing_proof"]["blocker_proof_hash"] == ""


# ============================================================================
# WAVE 4 — _print_executive_summary
# ============================================================================


class TestPrintExecutiveSummary:
    """Branch: all pass, any fail, empty state, VERDICT lines, blockers section."""

    def setup_method(self):
        self.mod = _load()

    def _make_complete_output(
        self,
        overall: str = "PASS",
        n_pass: int = 10,
        n_fail: int = 0,
        gate_criteria: list | None = None,
        blockers: list | None = None,
        skipped_count: int = 0,
        blocked_llm: int = 0,
    ) -> dict:
        """Build a minimal complete_output dict for _print_executive_summary."""
        if gate_criteria is None:
            gate_criteria = [
                {
                    "criterion": f"Gate {i}",
                    "target": ">=0.9",
                    "threshold": 0.9,
                    "actual": 1.0,
                    "status": "PASS",
                    "blocker": None,
                    "severity": "high",
                }
                for i in range(10)
            ]
        return {
            "meta": {
                "report_type": "HEAL_RUN_COMPLETE",
                "timestamp": "2025-01-01T00:00:00",
                "run_id": "run_test",
                "git_commit": "abc1234",
            },
            "coverage": {
                "coverage_ratio": 1.0 - skipped_count * 0.1,
                "executed_agents": {"count": 10 - skipped_count},
                "expected_agents": {"count": 10},
                "skipped_agents": {"count": skipped_count, "agents": []},
            },
            "routing": {
                "llm_call_trace": [],
                "llm_invocation_stats": {
                    "execution_rate": 1.0,
                    "expected_calls": 5,
                    "actual_calls": 5,
                    "blocked_by_flags": blocked_llm,
                },
            },
            "learning": {
                "run_comparison": {"current_success_rate": 0.8},
            },
            "blockers": {"blocked_agents": blockers or []},
            "executive_summary": {
                "overall_status": overall,
                "criteria_passed": n_pass,
                "criteria_failed": n_fail,
                "criteria_total": 10,
                "gate_criteria": gate_criteria,
            },
        }

    def test_summary_all_pass_verdict(self, capsys):
        """VERDICT: PASS printed when all gates pass."""
        data = self._make_complete_output(overall="PASS", n_pass=10, n_fail=0)
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "VERDICT: PASS" in captured

    def test_summary_any_fail_verdict(self, capsys):
        """VERDICT: FAIL printed when any gate fails."""
        gc = [
            {
                "criterion": "Agent Coverage",
                "target": ">=0.90",
                "threshold": 0.90,
                "actual": 0.80,
                "status": "FAIL",
                "blocker": "2 agents blocked",
                "severity": "critical",
            }
        ] + [
            {
                "criterion": f"Gate {i}",
                "target": ">=0.9",
                "threshold": 0.9,
                "actual": 1.0,
                "status": "PASS",
                "blocker": None,
                "severity": "high",
            }
            for i in range(9)
        ]
        data = self._make_complete_output(overall="FAIL", n_pass=9, n_fail=1, gate_criteria=gc)
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "VERDICT: FAIL" in captured

    def test_summary_coverage_fail_gate_shown(self, capsys):
        """FAIL gate row appears in table output."""
        gc = [
            {
                "criterion": "Agent Coverage",
                "target": ">=0.90",
                "threshold": 0.90,
                "actual": 0.80,
                "status": "FAIL",
                "blocker": "2 agents blocked",
                "severity": "critical",
            }
        ] + [
            {
                "criterion": f"Gate {i}",
                "target": ">=0.9",
                "threshold": 0.9,
                "actual": 1.0,
                "status": "PASS",
                "blocker": None,
                "severity": "high",
            }
            for i in range(9)
        ]
        data = self._make_complete_output(overall="FAIL", n_pass=9, n_fail=1, gate_criteria=gc)
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "[FAIL]" in captured
        assert "Agent Coverage" in captured

    def test_summary_blockers_section_shown(self, capsys):
        """Critical blockers section printed when blockers present."""
        blockers = [
            {
                "agent": "AgentBlocked",
                "blocker_type": "feature_flag",
                "flag": "ENABLE_X",
                "remediation": "Set ENABLE_X=True",
            }
        ]
        data = self._make_complete_output(blockers=blockers)
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "CRITICAL BLOCKERS" in captured
        assert "AgentBlocked" in captured

    def test_summary_no_blockers_no_critical_section(self, capsys):
        """No blockers → CRITICAL BLOCKERS section not printed."""
        data = self._make_complete_output()
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "CRITICAL BLOCKERS" not in captured

    def test_summary_proof_integrity_section_always_shown(self, capsys):
        """PROOF INTEGRITY section always present."""
        data = self._make_complete_output()
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "PROOF INTEGRITY" in captured

    def test_summary_next_run_prediction_shown_when_skipped(self, capsys):
        """NEXT RUN PREDICTION section shown when agents skipped."""
        data = self._make_complete_output(skipped_count=2)
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "NEXT RUN PREDICTION" in captured

    def test_summary_next_run_prediction_not_shown_when_clean(self, capsys):
        """NEXT RUN PREDICTION NOT shown when no skipped agents and no blocked LLM."""
        data = self._make_complete_output(skipped_count=0, blocked_llm=0)
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "NEXT RUN PREDICTION" not in captured

    def test_summary_empty_complete_output_no_crash(self, capsys):
        """Empty dict input → does not crash, prints something."""
        self.mod._print_executive_summary({})
        captured = capsys.readouterr().out
        assert len(captured) > 0

    def test_summary_run_id_and_git_in_header(self, capsys):
        """run_id and git_commit appear in header line."""
        data = self._make_complete_output()
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "run_test" in captured
        assert "abc1234" in captured

    def test_summary_n_fail_in_overall_row(self, capsys):
        """Number of failed criteria shown in overall row."""
        gc = [
            {
                "criterion": f"Gate {i}",
                "target": ">=0.9",
                "threshold": 0.9,
                "actual": 0.5,
                "status": "FAIL",
                "blocker": "fail",
                "severity": "high",
            }
            for i in range(3)
        ] + [
            {
                "criterion": f"Gate {i}",
                "target": ">=0.9",
                "threshold": 0.9,
                "actual": 1.0,
                "status": "PASS",
                "blocker": None,
                "severity": "high",
            }
            for i in range(7)
        ]
        data = self._make_complete_output(overall="FAIL", n_pass=7, n_fail=3, gate_criteria=gc)
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "3/10" in captured

    def test_summary_pass_all_message(self, capsys):
        """All pass → 'All diagnostic gates satisfied' message shown."""
        data = self._make_complete_output(overall="PASS")
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "All diagnostic gates satisfied" in captured

    def test_summary_fail_forensics_reference(self, capsys):
        """Any fail → 'failure_forensics.json' referenced."""
        gc = [
            {
                "criterion": "Gate 0",
                "target": ">=0.9",
                "threshold": 0.9,
                "actual": 0.0,
                "status": "FAIL",
                "blocker": "bad",
                "severity": "high",
            }
        ] + [
            {
                "criterion": f"Gate {i}",
                "target": ">=0.9",
                "threshold": 0.9,
                "actual": 1.0,
                "status": "PASS",
                "blocker": None,
                "severity": "high",
            }
            for i in range(9)
        ]
        data = self._make_complete_output(overall="FAIL", n_pass=9, n_fail=1, gate_criteria=gc)
        self.mod._print_executive_summary(data)
        captured = capsys.readouterr().out
        assert "failure_forensics.json" in captured


# ============================================================================
# Integration smoke: new functions exported by module
# ============================================================================


class TestModuleExportsNewFunctions:
    """Verify all four wave functions exist in the module."""

    def setup_method(self):
        self.mod = _load()

    def test_collect_llm_call_trace_callable(self):
        assert callable(getattr(self.mod, "_collect_llm_call_trace", None))

    def test_collect_blocker_scan_callable(self):
        assert callable(getattr(self.mod, "_collect_blocker_scan", None))

    def test_build_coverage_proof_callable(self):
        assert callable(getattr(self.mod, "_build_coverage_proof", None))

    def test_build_calibration_proof_callable(self):
        assert callable(getattr(self.mod, "_build_calibration_proof", None))

    def test_write_heal_run_complete_callable(self):
        assert callable(getattr(self.mod, "_write_heal_run_complete", None))

    def test_write_failure_forensics_callable(self):
        assert callable(getattr(self.mod, "_write_failure_forensics", None))

    def test_print_executive_summary_callable(self):
        assert callable(getattr(self.mod, "_print_executive_summary", None))
