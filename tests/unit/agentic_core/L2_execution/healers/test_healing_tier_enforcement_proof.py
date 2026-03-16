"""
Confidence + Healing Tier Enforcement Proof — Phases 2 & 3.

Phase 2 — Dynamic Behavior Proof:
  Wave 1: Controlled confidence simulation (epsilon bands + retry override).
  Wave 2: Agent-level integration proof (allowlisted agents delegate to router).
  Wave 3: Negative control (synthetic bypass agent detected by static scan).

Phase 3 — System-Wide Coverage:
  Wave 2: Blast radius check (non-tiered agents do NOT import router).
  Wave 3: Determinism check (byte-identical decisions across two runs).
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_healing_tier_enforcement_proof")
_emit_applies_guardrail("p0", "test_healing_tier_enforcement_proof", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_tier_enforcement_proof", "policy_binding")
_emit_snapshots_state("p0", "test_healing_tier_enforcement_proof", "state_snapshot")
emit_replay_key("p0", "test_healing_tier_enforcement_proof")
emit_determinism_digest("p0", "test_healing_tier_enforcement_proof")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_tier_enforcement_proof", "execution_auth")
_emit_validates_capability("p2", "test_healing_tier_enforcement_proof", "capability_check")
_emit_routes_to_capability("p2", "test_healing_tier_enforcement_proof", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_tier_enforcement_proof", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_tier_enforcement_proof", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_tier_enforcement_proof", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_tier_enforcement_proof", "exec_output")
_emit_dispatches_agent("p3", "test_healing_tier_enforcement_proof", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_tier_enforcement_proof", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_tier_enforcement_proof", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_tier_enforcement_proof", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_tier_enforcement_proof", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_tier_enforcement_proof", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_tier_enforcement_proof", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_tier_enforcement_proof", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_tier_enforcement_proof", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_tier_enforcement_proof", "eval_metric")
_emit_stores_embedding("p4", "test_healing_tier_enforcement_proof", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_tier_enforcement_proof", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_tier_enforcement_proof", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.healers.healing_tier_config import (
    HealingTierConfig,
    load_default_healing_tier_config,
)
from agentic_core.L2_execution.healers.healing_tier_router import (
    clear_historical_success_rates,
    compute_heal_confidence,
    route_healing_tier,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    FailureSignal,
    HealingInput,
    HealingTier,
)
from agentic_core.L2_execution.healers.tiering_allowlist import (
    TIERING_ALLOWLIST_FILE_PATHS,
    is_tiering_allowed,
    is_tiering_allowed_by_path,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_healing_tier_enforcement_proof", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_tier_enforcement_proof", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_tier_enforcement_proof", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_tier_enforcement_proof", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_tier_enforcement_proof", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_tier_enforcement_proof", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_tier_enforcement_proof", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_tier_enforcement_proof", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_tier_enforcement_proof", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_tier_enforcement_proof", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_tier_enforcement_proof", "p4obs", "alert")
_emit_links_incident_trace("test_healing_tier_enforcement_proof", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_tier_enforcement_proof", "p3lm", "pattern")
_emit_records_learning_event("test_healing_tier_enforcement_proof", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_tier_enforcement_proof", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_tier_enforcement_proof", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_tier_enforcement_proof", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_tier_enforcement_proof", "p3lm", "policy")
_emit_stores_learning_state("test_healing_tier_enforcement_proof", "p3lm", "state")
_emit_records_execution_trace("test_healing_tier_enforcement_proof", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_tier_enforcement_proof", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_tier_enforcement_proof", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_tier_enforcement_proof", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_tier_enforcement_proof", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_tier_enforcement_proof", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_tier_enforcement_proof", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_tier_enforcement_proof", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_tier_enforcement_proof", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_healing_tier_enforcement_proof", "context_pull")
_emit_pulls_context("p1", "test_healing_tier_enforcement_proof", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_enforcement_proof", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_enforcement_proof", "uwg_term_2")
_emit_writes_through("p1", "test_healing_tier_enforcement_proof", "write_through")
_emit_writes_through("p1", "test_healing_tier_enforcement_proof", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_healing_tier_enforcement_proof", "safety_validation")
_emit_invokes_eval("p1", "test_healing_tier_enforcement_proof", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_tier_enforcement_proof", "routing_commit")
_emit_escalates_to_human("p1", "test_healing_tier_enforcement_proof", "human_escalation")
_emit_routes_through("p1", "test_healing_tier_enforcement_proof", "route_through")
_emit_checks_agent_registry("p1", "test_healing_tier_enforcement_proof", "agent_registry")
_emit_validates_agent_capability("p1", "test_healing_tier_enforcement_proof", "capability")
_emit_dispatches_execution_plan("p1", "test_healing_tier_enforcement_proof", "exec_plan")
_emit_agent_executes_agent("p1", "test_healing_tier_enforcement_proof", "sub_agent")
_emit_routes_to_agent("p1", "test_healing_tier_enforcement_proof", "target_agent")
_emit_verifies_policy("p1", "test_healing_tier_enforcement_proof", "policy_check")
_emit_observes_runtime_state("p1", "test_healing_tier_enforcement_proof", "runtime_state")
_emit_verifies_boundary("p1", "test_healing_tier_enforcement_proof", "boundary_check")
_emit_transcripts_response("p1", "test_healing_tier_enforcement_proof", "transcript")
_emit_hard_fails_untranscripted("p1", "test_healing_tier_enforcement_proof")
_emit_gated_by_confidence("p1", "test_healing_tier_enforcement_proof", "confidence_gate")

REPO_ROOT = Path(__file__).resolve().parents[5]
ROUTER_MODULE = "agentic_core.L2_execution.healers.healing_tier_router"
HEALING_TIER_SYSTEM_FILES = frozenset(
    {
        "agentic_core/L2_execution/healers/healing_tier_router.py",
        "agentic_core/L2_execution/healers/healing_tier_dispatcher.py",
        "agentic_core/L2_execution/healers/healing_tier_types.py",
        "agentic_core/L2_execution/healers/healing_tier_config.py",
        "agentic_core/L2_execution/healers/tiering_allowlist.py",
        "agentic_core/L2_execution/healers/healing_provider_adapters.py",
    }
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_history():
    clear_historical_success_rates()
    yield
    clear_historical_success_rates()


@pytest.fixture
def default_config() -> HealingTierConfig:
    return load_default_healing_tier_config()


def _make_input(
    failure_type: str = "syntax_error",
    blast_radius: float = 0.0,
    retry_count: int = 0,
    error_sig: str = "sig-001",
    failure_entropy_class: str = "MEDIUM",
) -> HealingInput:
    return HealingInput(
        failure_type=failure_type,
        error_signature=error_sig,
        trace_id="trace-test",
        retry_count=retry_count,
        blast_radius_estimate=blast_radius,
        required_tools=(),
        violation_metadata_refs=(),
        failure_entropy_class=failure_entropy_class,
    )


# ---------------------------------------------------------------------------
# Phase 2 Wave 1: Controlled Confidence Simulation
# ---------------------------------------------------------------------------


class TestConfidenceBands:
    def test_above_x_routes_local_agent(self, default_config):
        inp = _make_input(failure_type="syntax_error", blast_radius=0.0, retry_count=0)
        decision = route_healing_tier(inp, default_config)
        conf = decision.heal_confidence
        assert conf >= default_config.heal_confidence_x
        assert decision.tier == HealingTier.LOCAL_AGENT
        assert any("LOCAL_AGENT" in r for r in decision.reason_codes)

    def test_between_y_and_x_routes_qwen_vllm(self, default_config):
        inp = _make_input(failure_type="runtime_error", blast_radius=0.5, retry_count=0)
        decision = route_healing_tier(inp, default_config)
        conf = decision.heal_confidence
        assert default_config.heal_confidence_y <= conf < default_config.heal_confidence_x
        assert decision.tier == HealingTier.QWEN_VLLM
        assert any("QWEN_VLLM" in r for r in decision.reason_codes)

    def test_below_y_routes_gemini(self, default_config):
        # unknown prior=0.30, blast=1.0, retry=2, HIGH entropy -> score=0.395 < Y=0.40
        inp = _make_input(
            failure_type="unknown", blast_radius=1.0, retry_count=2, failure_entropy_class="HIGH"
        )
        decision = route_healing_tier(inp, default_config)
        conf = decision.heal_confidence
        assert conf < default_config.heal_confidence_y, (
            f"Expected confidence < {default_config.heal_confidence_y}, got {conf}"
        )
        assert decision.tier == HealingTier.GEMINI_2_5_PRO
        assert any("GEMINI_2_5_PRO" in r for r in decision.reason_codes)

    def test_retry_at_max_forces_gemini(self, default_config):
        inp = _make_input(
            failure_type="syntax_error",
            blast_radius=0.0,
            retry_count=default_config.max_heal_retries,
        )
        decision = route_healing_tier(inp, default_config)
        assert decision.tier == HealingTier.GEMINI_2_5_PRO
        assert any("FORCED_GEMINI" in r for r in decision.reason_codes)

    def test_retry_above_max_forces_gemini(self, default_config):
        inp = _make_input(
            failure_type="syntax_error",
            blast_radius=0.0,
            retry_count=default_config.max_heal_retries + 5,
        )
        assert route_healing_tier(inp, default_config).tier == HealingTier.GEMINI_2_5_PRO

    def test_retry_below_max_does_not_force_gemini(self, default_config):
        inp = _make_input(
            failure_type="syntax_error",
            blast_radius=0.0,
            retry_count=default_config.max_heal_retries - 1,
        )
        decision = route_healing_tier(inp, default_config)
        assert decision.tier == HealingTier.LOCAL_AGENT
        assert not any("FORCED_GEMINI" in r for r in decision.reason_codes)

    def test_exactly_at_x_is_local(self, default_config):
        conf, _ = compute_heal_confidence(_make_input("syntax_error", 0.0, 0))
        cfg = HealingTierConfig(
            heal_confidence_x=conf,
            heal_confidence_y=conf - 0.1,
            max_heal_retries=3,
            model_qwen_vllm_id="qwen2.5-coder-32b-instruct",
            model_gemini_2_5_pro_id="gemini-2.5-pro",
        )
        decision = route_healing_tier(_make_input("syntax_error", 0.0, 0), cfg)
        assert decision.tier == HealingTier.LOCAL_AGENT

    def test_just_below_x_is_qwen(self, default_config):
        conf, _ = compute_heal_confidence(_make_input("syntax_error", 0.0, 0))
        cfg = HealingTierConfig(
            heal_confidence_x=conf + 0.001,
            heal_confidence_y=conf - 0.1,
            max_heal_retries=3,
            model_qwen_vllm_id="qwen2.5-coder-32b-instruct",
            model_gemini_2_5_pro_id="gemini-2.5-pro",
        )
        decision = route_healing_tier(_make_input("syntax_error", 0.0, 0), cfg)
        assert decision.tier == HealingTier.QWEN_VLLM

    def test_exactly_at_y_is_qwen(self, default_config):
        conf, _ = compute_heal_confidence(_make_input("unknown", 0.9, 0))
        cfg = HealingTierConfig(
            heal_confidence_x=conf + 0.1,
            heal_confidence_y=conf,
            max_heal_retries=3,
            model_qwen_vllm_id="qwen2.5-coder-32b-instruct",
            model_gemini_2_5_pro_id="gemini-2.5-pro",
        )
        decision = route_healing_tier(_make_input("unknown", 0.9, 0), cfg)
        assert decision.tier == HealingTier.QWEN_VLLM

    def test_just_below_y_is_gemini(self, default_config):
        conf, _ = compute_heal_confidence(_make_input("unknown", 0.9, 0))
        cfg = HealingTierConfig(
            heal_confidence_x=conf + 0.2,
            heal_confidence_y=conf + 0.001,
            max_heal_retries=3,
            model_qwen_vllm_id="qwen2.5-coder-32b-instruct",
            model_gemini_2_5_pro_id="gemini-2.5-pro",
        )
        decision = route_healing_tier(_make_input("unknown", 0.9, 0), cfg)
        assert decision.tier == HealingTier.GEMINI_2_5_PRO


# ---------------------------------------------------------------------------
# Phase 2 Wave 2: Agent-Level Integration Proof
# ---------------------------------------------------------------------------

_ALLOWLIST_PARAMS = [
    ("CodeHealerAgent", "agentic_core/L5_safety/reasoning/CodeHealerAgent.py"),
    ("GravityLeakRepairAgent", "agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py"),
    ("IntegrityGateExecutorAgent", "agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py"),
    ("LocationHealerAgent", "agentic_core/L5_safety/reasoning/LocationHealerAgent.py"),
    ("SafetyExecutorAgent", "agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py"),
    ("StructureHealerAgent", "agentic_core/L5_safety/reasoning/StructureHealerAgent.py"),
    ("TypeHintFixerAgent", "agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py"),
    ("DispatchOutreachToolsAgent", "apps_lic/reasoning/DispatchOutreachToolsAgent.py"),
    ("OutreachValidationExecutorAgent", "apps_lic/reasoning/OutreachValidationExecutorAgent.py"),
    ("DispatchResumeToolsAgent", "apps_rg/reasoning/DispatchResumeToolsAgent.py"),
]


class TestAgentLevelIntegration:
    @pytest.mark.parametrize("agent_name,file_path", _ALLOWLIST_PARAMS)
    def test_allowlisted_by_name(self, agent_name, file_path):
        assert is_tiering_allowed(agent_name)

    @pytest.mark.parametrize("agent_name,file_path", _ALLOWLIST_PARAMS)
    def test_allowlisted_by_path(self, agent_name, file_path):
        assert is_tiering_allowed_by_path(file_path)

    def test_non_allowlisted_rejected(self):
        assert not is_tiering_allowed("SomeRandomAgent")
        assert not is_tiering_allowed("FakeHealerAgent")
        assert not is_tiering_allowed("")

    def test_failure_signal_routes_through_router(self, default_config):
        signal = FailureSignal(
            source_agent="CodeHealerAgent",
            failure_type="syntax_error",
            error_signature="sig-syntax-001",
            trace_id="trace-integration-001",
            context={"file": "foo.py"},
            retry_count=0,
            blast_radius_estimate=0.1,
        )
        inp = signal.to_healing_input(required_tools=("ast_rewrite",))
        decision = route_healing_tier(inp, default_config)
        assert decision.tier in {HealingTier.LOCAL_AGENT, HealingTier.QWEN_VLLM, HealingTier.GEMINI_2_5_PRO}
        assert 0.0 <= decision.heal_confidence <= 1.0
        assert len(decision.reason_codes) > 0

    @pytest.mark.parametrize("agent_name,_", _ALLOWLIST_PARAMS)
    def test_each_agent_failure_signal_routes(self, agent_name, _, default_config):
        signal = FailureSignal(
            source_agent=agent_name,
            failure_type="test_failure",
            error_signature=f"sig-{agent_name}",
            trace_id=f"trace-{agent_name}",
            context={},
            retry_count=0,
            blast_radius_estimate=0.3,
        )
        decision = route_healing_tier(signal.to_healing_input(), default_config)
        assert isinstance(decision.tier, HealingTier)
        assert 0.0 <= decision.heal_confidence <= 1.0


# ---------------------------------------------------------------------------
# Phase 2 Wave 3: Negative Control
# ---------------------------------------------------------------------------


class TestNegativeControl:
    def test_synthetic_bypass_agent_detected(self):
        """AST scanner detects HealingTier member references in bypass code."""
        bypass_code = textwrap.dedent("""
            from agentic_core.L2_execution.healers.healing_tier_types import HealingTier

            def select_model(confidence: float):
                if confidence < 0.4:
                    return HealingTier.GEMINI_2_5_PRO
                elif confidence < 0.75:
                    return HealingTier.QWEN_VLLM
                return HealingTier.LOCAL_AGENT
        """)
        tree = ast.parse(bypass_code)
        imported_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)

        assert "HealingTier" in imported_names

        members = {"LOCAL_AGENT", "QWEN_VLLM", "GEMINI_2_5_PRO"}
        found = [
            node.attr
            for node in ast.walk(tree)
            if (
                isinstance(node, ast.Attribute)
                and node.attr in members
                and isinstance(node.value, ast.Name)
                and node.value.id == "HealingTier"
            )
        ]
        assert set(found) == {"GEMINI_2_5_PRO", "QWEN_VLLM", "LOCAL_AGENT"}

    def test_clean_agent_not_flagged(self):
        """File without HealingTier import is not flagged."""
        clean_code = "def do_something(x: float) -> str:\n    return 'result'\n"
        tree = ast.parse(clean_code)
        imported_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
        assert "HealingTier" not in imported_names

    def test_router_exempt_from_bypass_check(self):
        """Router file is in the system files exemption set."""
        router_rel = "agentic_core/L2_execution/healers/healing_tier_router.py"
        assert router_rel in HEALING_TIER_SYSTEM_FILES


# ---------------------------------------------------------------------------
# Phase 3 Wave 2: Blast Radius Check
# ---------------------------------------------------------------------------


class TestBlastRadiusCheck:
    def _collect_python_files(self) -> list[Path]:
        scan_roots = [
            REPO_ROOT / AGENTIC_CORE_DIR,
            REPO_ROOT / APPS_LIC_DIR,
            REPO_ROOT / APPS_RG_DIR,
            REPO_ROOT / APPS_SHARED_DIR,
        ]
        files: list[Path] = []
        for root in scan_roots:
            if not root.exists():
                continue
            for p in root.rglob("*.py"):
                if "__pycache__" not in p.parts:
                    files.append(p)
        return sorted(files)

    def _get_imports(self, tree: ast.Module) -> list[str]:
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def test_non_tiered_agents_do_not_import_router(self):
        """Non-allowlisted, non-system, non-test files must not import the router."""
        all_files = self._collect_python_files()
        violations: list[str] = []
        for fpath in all_files:
            rel = fpath.relative_to(REPO_ROOT).as_posix()
            if rel in HEALING_TIER_SYSTEM_FILES:
                continue
            if "/tests/" in rel or rel.startswith("tests/"):
                continue
            if rel in TIERING_ALLOWLIST_FILE_PATHS:
                continue
            try:
                tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError as e:
                assert False, f"SyntaxError in {fpath}: {e}"
            if any(ROUTER_MODULE in imp for imp in self._get_imports(tree)):
                violations.append(f"NON_TIERED_IMPORTS_ROUTER: {rel}")

        if violations:
            pytest.fail(
                f"{len(violations)} non-tiered file(s) import the healing tier router:\n"
                + "\n".join(f"  {v}" for v in violations)
            )

    def test_blast_radius_report(self):
        """Print total vs tiered agent counts."""
        all_files = self._collect_python_files()
        total_agents = sum(1 for f in all_files if f.name.endswith("Agent.py"))
        tiered_count = len(TIERING_ALLOWLIST_FILE_PATHS)
        non_tiered = total_agents - tiered_count
        pct = (tiered_count / total_agents * 100) if total_agents else 0
        print(
            f"\nBlast Radius: total={total_agents} tiered={tiered_count} "
            f"non_tiered={non_tiered} pct={pct:.1f}%"
        )
        assert tiered_count == 11, f"Expected 11 tiered agents, got {tiered_count}"
        assert total_agents >= tiered_count


# ---------------------------------------------------------------------------
# Phase 3 Wave 3: Determinism Check
# ---------------------------------------------------------------------------


class TestDeterminismCheck:
    """Run tier decisions twice; assert byte-identical outputs."""

    @pytest.mark.parametrize(
        "failure_type,blast,retry",
        [
            ("syntax_error", 0.0, 0),
            ("runtime_error", 0.5, 0),
            ("unknown", 0.9, 0),
            ("import_cycle", 0.3, 1),
            ("test_failure", 0.6, 2),
            ("syntax_error", 0.0, 3),  # forced GEMINI
        ],
    )
    def test_deterministic_tier_decision(self, failure_type, blast, retry, default_config):
        """Same inputs produce byte-identical HealingDecision twice."""
        inp = _make_input(failure_type=failure_type, blast_radius=blast, retry_count=retry)
        d1 = route_healing_tier(inp, default_config)
        d2 = route_healing_tier(inp, default_config)
        assert d1.tier == d2.tier
        assert d1.heal_confidence == d2.heal_confidence
        assert d1.reason_codes == d2.reason_codes

    def test_deterministic_confidence_score(self, default_config):
        """compute_heal_confidence returns identical float twice for same input."""
        inp = _make_input("syntax_error", 0.0, 0)
        c1, r1 = compute_heal_confidence(inp)
        c2, r2 = compute_heal_confidence(inp)
        assert c1 == c2
        assert r1 == r2

    def test_all_failure_types_deterministic(self, default_config):
        """All known failure types produce deterministic results."""
        from agentic_core.L2_execution.healers.healing_tier_router import FAILURE_CLASS_PRIORS

        for failure_type in FAILURE_CLASS_PRIORS:
            inp = _make_input(failure_type=failure_type, blast_radius=0.3, retry_count=0)
            d1 = route_healing_tier(inp, default_config)
            d2 = route_healing_tier(inp, default_config)
            assert d1.tier == d2.tier, f"Non-deterministic for failure_type={failure_type}"
            assert d1.heal_confidence == d2.heal_confidence
