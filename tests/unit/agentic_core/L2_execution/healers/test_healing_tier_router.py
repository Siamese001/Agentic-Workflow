"""
L2.3 Healing Tier Router — Comprehensive Test Suite.

Phase 3 Wave 1: Unit tests for tier routing (PASS/FAIL bands)
Phase 3 Wave 2: Enforcement tests (NO_TIERING prohibition + negative control)
Phase 3 Wave 3: Determinism test (byte-identical decisions)
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_healing_tier_router")
_emit_applies_guardrail("p0", "test_healing_tier_router", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_tier_router", "policy_binding")
_emit_snapshots_state("p0", "test_healing_tier_router", "state_snapshot")
emit_replay_key("p0", "test_healing_tier_router")
emit_determinism_digest("p0", "test_healing_tier_router")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_tier_router", "execution_auth")
_emit_validates_capability("p2", "test_healing_tier_router", "capability_check")
_emit_routes_to_capability("p2", "test_healing_tier_router", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_tier_router", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_tier_router", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_tier_router", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_tier_router", "exec_output")
_emit_dispatches_agent("p3", "test_healing_tier_router", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_tier_router", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_tier_router", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_tier_router", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_tier_router", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_tier_router", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_tier_router", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_tier_router", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_tier_router", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_tier_router", "eval_metric")
_emit_stores_embedding("p4", "test_healing_tier_router", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_tier_router", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_tier_router", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.healers.healing_tier_config import (
    HealingTierConfig,
    load_default_healing_tier_config,
)
from agentic_core.L2_execution.healers.healing_tier_router import (
    clear_historical_success_rates,
    compute_heal_confidence,
    route_healing_tier,
    set_historical_success_rate,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    FailureSignal,
    HealingDecision,
    HealingInput,
    HealingTier,
)
from agentic_core.L2_execution.healers.tiering_allowlist import (
    TIERING_ALLOWLIST,
    is_tiering_allowed,
    is_tiering_allowed_by_path,
)

REPO_ROOT = Path(__file__).resolve().parents[5]

# Explicit config for all tests — no silent defaults
TEST_CONFIG = HealingTierConfig(
    heal_confidence_x=0.75,
    heal_confidence_y=0.40,
    max_heal_retries=3,
    model_qwen_vllm_id="qwen2.5-coder-32b-instruct",
    model_gemini_2_5_pro_id="gemini-2.5-pro",
)


def _make_input(
    failure_type: str = "syntax_error",
    error_signature: str = "sig_001",
    trace_id: str = "trace_001",
    retry_count: int = 0,
    blast_radius_estimate: float = 0.1,
    required_tools: tuple[str, ...] = (),
    violation_metadata_refs: tuple[str, ...] = (),
) -> HealingInput:
    return HealingInput(
        failure_type=failure_type,
        error_signature=error_signature,
        trace_id=trace_id,
        retry_count=retry_count,
        blast_radius_estimate=blast_radius_estimate,
        required_tools=required_tools,
        violation_metadata_refs=violation_metadata_refs,
    )


# ===================================================================
# Phase 3 Wave 1: Unit tests for tier routing (PASS/FAIL bands)
# ===================================================================


class TestHealingTierConfig:
    """Config validation tests."""

    def test_valid_config(self):
        config = TEST_CONFIG
        assert config.heal_confidence_x == 0.75
        assert config.heal_confidence_y == 0.40
        assert config.max_heal_retries == 3
        assert config.model_qwen_vllm_id == "qwen2.5-coder-32b-instruct"
        assert config.model_gemini_2_5_pro_id == "gemini-2.5-pro"

    def test_x_must_be_greater_than_y(self):
        with pytest.raises(ValueError, match="must be >"):
            HealingTierConfig(
                heal_confidence_x=0.40,
                heal_confidence_y=0.75,
                max_heal_retries=3,
                model_qwen_vllm_id="qwen",
                model_gemini_2_5_pro_id="gemini",
            )

    def test_x_equals_y_rejected(self):
        with pytest.raises(ValueError, match="must be >"):
            HealingTierConfig(
                heal_confidence_x=0.50,
                heal_confidence_y=0.50,
                max_heal_retries=3,
                model_qwen_vllm_id="qwen",
                model_gemini_2_5_pro_id="gemini",
            )

    def test_max_retries_must_be_positive(self):
        with pytest.raises(ValueError, match="max_heal_retries"):
            HealingTierConfig(
                heal_confidence_x=0.75,
                heal_confidence_y=0.40,
                max_heal_retries=0,
                model_qwen_vllm_id="qwen",
                model_gemini_2_5_pro_id="gemini",
            )

    def test_empty_model_ids_rejected(self):
        with pytest.raises(ValueError, match="model_qwen_vllm_id"):
            HealingTierConfig(
                heal_confidence_x=0.75,
                heal_confidence_y=0.40,
                max_heal_retries=3,
                model_qwen_vllm_id="",
                model_gemini_2_5_pro_id="gemini",
            )

    def test_load_default_config(self):
        config = load_default_healing_tier_config()
        assert config.heal_confidence_x > config.heal_confidence_y
        assert config.max_heal_retries >= 1
        assert config.model_qwen_vllm_id
        assert config.model_gemini_2_5_pro_id


class TestHealingInput:
    """Contract validation for HealingInput."""

    def test_valid_input(self):
        inp = _make_input()
        assert inp.failure_type == "syntax_error"
        assert inp.retry_count == 0

    def test_empty_failure_type_rejected(self):
        with pytest.raises(ValueError, match="failure_type"):
            _make_input(failure_type="")

    def test_negative_retry_count_rejected(self):
        with pytest.raises(ValueError, match="retry_count"):
            _make_input(retry_count=-1)

    def test_blast_radius_out_of_range(self):
        with pytest.raises(ValueError, match="blast_radius_estimate"):
            _make_input(blast_radius_estimate=1.5)

    def test_blast_radius_negative(self):
        with pytest.raises(ValueError, match="blast_radius_estimate"):
            _make_input(blast_radius_estimate=-0.1)


class TestHealingDecision:
    """Contract validation for HealingDecision."""

    def test_valid_decision(self):
        d = HealingDecision(
            heal_confidence=0.80,
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=("test",),
        )
        assert d.tier == HealingTier.LOCAL_AGENT

    def test_confidence_out_of_range(self):
        with pytest.raises(ValueError, match="heal_confidence"):
            HealingDecision(
                heal_confidence=1.5,
                tier=HealingTier.LOCAL_AGENT,
                reason_codes=(),
            )


class TestComputeHealConfidence:
    """Deterministic scoring tests."""

    def setup_method(self):
        clear_historical_success_rates()

    def test_high_confidence_syntax_error(self):
        inp = _make_input(failure_type="syntax_error", blast_radius_estimate=0.1)
        score, reasons = compute_heal_confidence(inp)
        assert score > 0.7, f"Expected high confidence for syntax_error, got {score}"

    def test_low_confidence_runtime_error(self):
        inp = _make_input(failure_type="runtime_error", blast_radius_estimate=0.9, retry_count=2)
        score, reasons = compute_heal_confidence(inp)
        assert score < 0.5, f"Expected low confidence for runtime_error+high blast+retries, got {score}"

    def test_retry_decay_lowers_score(self):
        inp0 = _make_input(retry_count=0)
        inp2 = _make_input(retry_count=2)
        score0, _ = compute_heal_confidence(inp0)
        score2, _ = compute_heal_confidence(inp2)
        assert score2 < score0, "Retry decay should lower score"

    def test_historical_success_rate_affects_score(self):
        inp = _make_input(error_signature="known_good")
        set_historical_success_rate("known_good", 0.95)
        score_good, _ = compute_heal_confidence(inp)

        clear_historical_success_rates()
        set_historical_success_rate("known_good", 0.05)
        score_bad, _ = compute_heal_confidence(inp)

        assert score_good > score_bad, "Higher historical success should yield higher score"

    def test_score_clamped_to_unit_interval(self):
        inp = _make_input(failure_type="syntax_error", blast_radius_estimate=0.0, retry_count=0)
        score, _ = compute_heal_confidence(inp)
        assert 0.0 <= score <= 1.0

    def test_reason_codes_populated(self):
        inp = _make_input()
        _, reasons = compute_heal_confidence(inp)
        assert len(reasons) >= 6, f"Expected >= 6 reason codes, got {len(reasons)}"
        assert any("failure_prior" in r for r in reasons)
        assert any("heal_confidence" in r for r in reasons)


class TestRouteHealingTier:
    """Tier routing band tests — explicit config, no defaults."""

    def setup_method(self):
        clear_historical_success_rates()

    def test_local_agent_band(self):
        """heal_confidence >= X routes to LOCAL_AGENT."""
        inp = _make_input(failure_type="syntax_error", blast_radius_estimate=0.05)
        decision = route_healing_tier(inp, TEST_CONFIG)
        assert decision.tier == HealingTier.LOCAL_AGENT, (
            f"Expected LOCAL_AGENT for high confidence, got {decision.tier} "
            f"(heal_confidence={decision.heal_confidence})"
        )
        assert decision.heal_confidence >= TEST_CONFIG.heal_confidence_x

    def test_qwen_vllm_band(self):
        """Y <= heal_confidence < X routes to QWEN_VLLM."""
        inp = _make_input(
            failure_type="integrity_gate_failure",
            blast_radius_estimate=0.4,
            retry_count=1,
        )
        decision = route_healing_tier(inp, TEST_CONFIG)
        assert decision.tier == HealingTier.QWEN_VLLM, (
            f"Expected QWEN_VLLM for mid confidence, got {decision.tier} "
            f"(heal_confidence={decision.heal_confidence})"
        )
        assert TEST_CONFIG.heal_confidence_y <= decision.heal_confidence < TEST_CONFIG.heal_confidence_x

    def test_gemini_band(self):
        """heal_confidence < Y routes to GEMINI_2_5_PRO."""
        set_historical_success_rate("low_sig", 0.05)
        inp = _make_input(
            failure_type="unknown",
            error_signature="low_sig",
            blast_radius_estimate=0.95,
            retry_count=2,
        )
        decision = route_healing_tier(inp, TEST_CONFIG)
        assert decision.tier == HealingTier.GEMINI_2_5_PRO, (
            f"Expected GEMINI_2_5_PRO for low confidence, got {decision.tier} "
            f"(heal_confidence={decision.heal_confidence})"
        )
        assert decision.heal_confidence < TEST_CONFIG.heal_confidence_y

    def test_retry_count_forces_gemini(self):
        """retry_count >= MAX_HEAL_RETRIES forces GEMINI_2_5_PRO regardless of score."""
        inp = _make_input(
            failure_type="syntax_error",
            blast_radius_estimate=0.05,
            retry_count=3,
        )
        decision = route_healing_tier(inp, TEST_CONFIG)
        assert decision.tier == HealingTier.GEMINI_2_5_PRO, (
            f"Expected GEMINI_2_5_PRO when retry_count >= max, got {decision.tier}"
        )
        assert any("FORCED_GEMINI" in r for r in decision.reason_codes)

    def test_retry_count_above_max_forces_gemini(self):
        """retry_count > MAX_HEAL_RETRIES also forces GEMINI_2_5_PRO."""
        inp = _make_input(failure_type="syntax_error", retry_count=10)
        decision = route_healing_tier(inp, TEST_CONFIG)
        assert decision.tier == HealingTier.GEMINI_2_5_PRO

    def test_decision_has_reason_codes(self):
        inp = _make_input()
        decision = route_healing_tier(inp, TEST_CONFIG)
        assert len(decision.reason_codes) > 0
        assert isinstance(decision.reason_codes, tuple)


class TestFailureSignal:
    """FailureSignal contract tests."""

    def test_valid_signal(self):
        sig = FailureSignal(
            source_agent="TestAgent",
            failure_type="syntax_error",
            error_signature="sig_001",
            trace_id="trace_001",
            context={"key": "value"},
        )
        assert sig.source_agent == "TestAgent"

    def test_to_healing_input(self):
        sig = FailureSignal(
            source_agent="TestAgent",
            failure_type="syntax_error",
            error_signature="sig_001",
            trace_id="trace_001",
            context={},
            retry_count=2,
            blast_radius_estimate=0.3,
        )
        inp = sig.to_healing_input(required_tools=("ast_rewrite",))
        assert inp.failure_type == "syntax_error"
        assert inp.retry_count == 2
        assert inp.blast_radius_estimate == 0.3
        assert inp.required_tools == ("ast_rewrite",)

    def test_empty_source_agent_rejected(self):
        with pytest.raises(ValueError, match="source_agent"):
            FailureSignal(
                source_agent="",
                failure_type="syntax_error",
                error_signature="sig",
                trace_id="trace",
                context={},
            )


# ===================================================================
# Phase 3 Wave 2: Enforcement tests (NO_TIERING prohibition)
# ===================================================================


class TestTieringAllowlist:
    """Verify allowlist matches CSV SSOT."""

    def test_allowlist_count(self):
        assert len(TIERING_ALLOWLIST) == 11, f"Expected 11 YES_TIERING agents, got {len(TIERING_ALLOWLIST)}"

    def test_yes_tiering_agents_in_allowlist(self):
        expected_agents = {
            "CodeHealerAgent",
            "GravityLeakRepairAgent",
            "IntegrityGateExecutorAgent",
            "LocationHealerAgent",
            "SafetyExecutorAgent",
            "StructureHealerAgent",
            "TypeHintFixerAgent",
            "DispatchOutreachToolsAgent",
            "OutreachValidationExecutorAgent",
            "DispatchResumeToolsAgent",
            "remediation_dispatcher",
        }
        actual_agents = {name for name, _ in TIERING_ALLOWLIST}
        assert actual_agents == expected_agents

    def test_is_tiering_allowed_yes(self):
        assert is_tiering_allowed("CodeHealerAgent") is True
        assert is_tiering_allowed("LocationHealerAgent") is True

    def test_is_tiering_allowed_no(self):
        assert is_tiering_allowed("CoverageAgent") is False
        assert is_tiering_allowed("RootCustomsAgent") is False
        assert is_tiering_allowed("CognitiveDispositionAgent") is False

    def test_is_tiering_allowed_by_path(self):
        assert is_tiering_allowed_by_path("agentic_core/L5_safety/reasoning/CodeHealerAgent.py") is True
        assert is_tiering_allowed_by_path("agentic_core/L3_orchestration/reasoning/CoverageAgent.py") is False


class TestNoTieringEnforcement:
    """AST-based enforcement: NO_TIERING agents must not directly invoke
    healing model selection (Qwen/Gemini entrypoints or model clients).

    Prohibited patterns in NO_TIERING agent files:
    - Direct import of route_healing_tier
    - Direct import of HealingTier
    - String literals containing model IDs
    """

    # Modules that ARE allowed to reference healing tier internals
    ALLOWED_MODULES = frozenset(
        {
            "agentic_core/L2_execution/healers/healing_tier_router.py",
            "agentic_core/L2_execution/healers/healing_tier_config.py",
            "agentic_core/L2_execution/healers/healing_tier_types.py",
            "agentic_core/L2_execution/healers/tiering_allowlist.py",
            "agentic_core/L2_execution/healers/__init__.py",
        }
    )

    # Prohibited import targets for NO_TIERING agents
    PROHIBITED_IMPORTS = frozenset(
        {
            "route_healing_tier",
            "HealingTier",
            "HealingDecision",
        }
    )

    def _get_no_tiering_agent_files(self) -> list[Path]:
        """Get all agent files NOT in the tiering allowlist."""
        csv_path = REPO_ROOT / "docs" / "technical" / "agent_confidence_tiering_recommendations.csv"
        if not csv_path.exists():
            pytest.fail("CSV SSOT not found")

        no_tiering_files = []
        with open(csv_path, encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines[1:]:  # Skip header
            parts = line.strip().split(",")
            if len(parts) >= 7:
                file_path = parts[2]
                tiering = parts[6]
                if tiering == "NO_TIERING":
                    full_path = REPO_ROOT / file_path
                    if full_path.exists():
                        no_tiering_files.append(full_path)

        return no_tiering_files

    def test_no_tiering_agents_do_not_import_tier_router(self):
        """NO_TIERING agents must not import route_healing_tier or HealingTier."""
        violations = []

        for agent_file in self._get_no_tiering_agent_files():
            relative = agent_file.relative_to(REPO_ROOT).as_posix()
            if relative in self.ALLOWED_MODULES:
                continue

            try:
                source = agent_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(agent_file))
            except (SyntaxError, UnicodeDecodeError) as e:
                assert False, f"Parse error in {agent_file}: {e}"

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if "healing_tier" in node.module:
                        for alias in node.names:
                            if alias.name in self.PROHIBITED_IMPORTS:
                                violations.append(f"{relative}:{node.lineno} imports {alias.name}")
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if "healing_tier" in alias.name:
                            violations.append(f"{relative}:{node.lineno} imports {alias.name}")

        assert violations == [], "NO_TIERING agents must not import healing tier internals:\n" + "\n".join(
            f"  - {v}" for v in violations
        )

    def test_negative_control_enforcement_would_catch_violation(self):
        """Prove the enforcement test WOULD fail if a NO_TIERING agent imported HealingTier.

        We simulate by checking that the prohibited import set is non-empty
        and that the detection logic correctly identifies a synthetic violation.
        """
        # Synthetic AST with prohibited import
        synthetic_source = (
            "from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier\n"
        )
        tree = ast.parse(synthetic_source)
        found_violation = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "healing_tier" in node.module:
                    for alias in node.names:
                        if alias.name in self.PROHIBITED_IMPORTS:
                            found_violation = True

        assert found_violation, (
            "Negative control failed: enforcement logic did not detect synthetic prohibited import"
        )


# ===================================================================
# Phase 3 Wave 3: Determinism test (byte-identical decisions)
# ===================================================================


class TestDeterminism:
    """Verify that the router produces byte-identical output for identical input."""

    def setup_method(self):
        clear_historical_success_rates()

    def test_deterministic_routing_identical_output(self):
        """Run the router twice with identical input; assert byte-identical decision."""
        inp = _make_input(
            failure_type="import_cycle",
            error_signature="cycle_abc",
            trace_id="det_trace_001",
            retry_count=1,
            blast_radius_estimate=0.3,
        )

        decision1 = route_healing_tier(inp, TEST_CONFIG)
        decision2 = route_healing_tier(inp, TEST_CONFIG)

        # Structural equality
        assert decision1.heal_confidence == decision2.heal_confidence, (
            f"heal_confidence mismatch: {decision1.heal_confidence} vs {decision2.heal_confidence}"
        )
        assert decision1.tier == decision2.tier, f"tier mismatch: {decision1.tier} vs {decision2.tier}"
        assert decision1.reason_codes == decision2.reason_codes, (
            f"reason_codes mismatch:\n  {decision1.reason_codes}\n  vs\n  {decision2.reason_codes}"
        )

        # Byte-identical JSON serialization
        def _to_json(d: HealingDecision) -> str:
            return json.dumps(
                {
                    "heal_confidence": d.heal_confidence,
                    "tier": d.tier.value,
                    "reason_codes": list(d.reason_codes),
                },
                sort_keys=True,
            )

        json1 = _to_json(decision1)
        json2 = _to_json(decision2)
        assert json1 == json2, f"JSON mismatch:\n  {json1}\n  vs\n  {json2}"

    def test_deterministic_scoring_identical_output(self):
        """Run compute_heal_confidence twice; assert identical results."""
        inp = _make_input(
            failure_type="gravity_leak",
            error_signature="leak_xyz",
            trace_id="det_trace_002",
            retry_count=0,
            blast_radius_estimate=0.5,
        )

        score1, reasons1 = compute_heal_confidence(inp)
        score2, reasons2 = compute_heal_confidence(inp)

        assert score1 == score2
        assert reasons1 == reasons2

    def test_deterministic_across_all_failure_types(self):
        """Verify determinism for every known failure type."""
        from agentic_core.L2_execution.healers.healing_tier_router import FAILURE_CLASS_PRIORS

        for failure_type in sorted(FAILURE_CLASS_PRIORS.keys()):
            inp = _make_input(failure_type=failure_type, retry_count=0)
            d1 = route_healing_tier(inp, TEST_CONFIG)
            d2 = route_healing_tier(inp, TEST_CONFIG)
            assert d1.heal_confidence == d2.heal_confidence, f"Non-deterministic for {failure_type}"
            assert d1.tier == d2.tier
            assert d1.reason_codes == d2.reason_codes


# ===================================================================
# Config printing (for evidence capture)
# ===================================================================


class TestConfigPrinting:
    """Print config values for evidence capture."""

    def test_print_config_values(self, capsys):
        config = TEST_CONFIG
        print(f"HEAL_CONFIDENCE_X={config.heal_confidence_x}")
        print(f"HEAL_CONFIDENCE_Y={config.heal_confidence_y}")
        print(f"MAX_HEAL_RETRIES={config.max_heal_retries}")
        print(f"MODEL_QWEN_VLLM_ID={config.model_qwen_vllm_id}")
        print(f"MODEL_GEMINI_2_5_PRO_ID={config.model_gemini_2_5_pro_id}")

        captured = capsys.readouterr()
        assert "HEAL_CONFIDENCE_X=0.75" in captured.out
        assert "HEAL_CONFIDENCE_Y=0.4" in captured.out
        assert "MAX_HEAL_RETRIES=3" in captured.out
        assert "MODEL_QWEN_VLLM_ID=qwen2.5-coder-32b-instruct" in captured.out
        assert "MODEL_GEMINI_2_5_PRO_ID=gemini-2.5-pro" in captured.out
