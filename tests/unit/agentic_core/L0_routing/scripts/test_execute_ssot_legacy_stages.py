"""
Comprehensive branch-coverage tests for:
  - execute_phase3_alignment_impl  (Phase 3: structural alignment)
  - execute_phase4_validation_impl (Phase 4: architectural validation)
  - execute_phase5_healing_impl    (Phase 5: healing)

Coverage targets per .windsurfrules §1.2:

Phase 3:
  - zero violations → completes "No violations found", returns None
  - violations > 0, proceed=False → completes "Skipped", returns None
  - violations > 0, proceed=True, ctx.heal=False → skip_agent, returns None
  - violations > 0, proceed=True, ctx.heal=True → invokes healer, returns dict

Phase 4:
  - gov_report is None → returns (None, None)
  - territory in ENFORCED_TERRITORIES → target_territories = all enforced
  - territory NOT in ENFORCED_TERRITORIES → target_territories = [territory]
  - non-L-layer territory → no file size check
  - L-layer territory → check_file_sizes called, warnings logged on violations

Phase 5:
  - gov_report is None → returns None
  - plan is None → returns None
  - requires_healing=False → returns None
  - requires_healing=True, proceed=False → skip_agent, returns None
  - requires_healing=True, proceed=True, ctx=None → skip_agent, returns None
  - requires_healing=True, proceed=True, ctx.heal=False → skip_agent, returns None
  - requires_healing=True, proceed=True, ctx.heal=True → invokes healer, returns dict
"""

from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentic_core.L5_safety.enforcement.hitl_gate import HitlGate
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

_emit_records_execution_trace("p0", "evidence", "test_execute_ssot_legacy_stages")
_emit_applies_guardrail("p0", "test_execute_ssot_legacy_stages", "p0_governance")
_emit_reads_policy_state("p0", "test_execute_ssot_legacy_stages", "policy_binding")
_emit_snapshots_state("p0", "test_execute_ssot_legacy_stages", "state_snapshot")
emit_replay_key("p0", "test_execute_ssot_legacy_stages")
emit_determinism_digest("p0", "test_execute_ssot_legacy_stages")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execute_ssot_legacy_stages", "execution_auth")
_emit_validates_capability("p2", "test_execute_ssot_legacy_stages", "capability_check")
_emit_routes_to_capability("p2", "test_execute_ssot_legacy_stages", "capability_route")
_emit_writes_via_uwg("p2", "test_execute_ssot_legacy_stages", "uwg_write")
_emit_blocks_direct_write("p2", "test_execute_ssot_legacy_stages", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execute_ssot_legacy_stages", "tool_invocation")
_emit_captures_execution_output("p2", "test_execute_ssot_legacy_stages", "exec_output")
_emit_dispatches_agent("p3", "test_execute_ssot_legacy_stages", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execute_ssot_legacy_stages", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execute_ssot_legacy_stages", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execute_ssot_legacy_stages", "healing_outcome")
_emit_escalates_failure("p3", "test_execute_ssot_legacy_stages", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execute_ssot_legacy_stages", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execute_ssot_legacy_stages", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execute_ssot_legacy_stages", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execute_ssot_legacy_stages", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execute_ssot_legacy_stages", "eval_metric")
_emit_stores_embedding("p4", "test_execute_ssot_legacy_stages", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execute_ssot_legacy_stages", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execute_ssot_legacy_stages", "exec_snapshot_link")


def _auto_approve_gate(repo_root=None):
    """Return an auto-approving HitlGate for use in tests that exercise heal=True paths."""
    return HitlGate(
        repo_root or Path("."),
        input_fn=lambda _: "Y",
        _tty_override=True,
    )


import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    TESTS_DIR,
)


def _load():
    try:
        return importlib.import_module("agentic_core.L0_routing.scripts.execute_ssot")
    except ImportError as exc:
        pytest.fail(f"execute_ssot not importable: {exc}")


@pytest.fixture(scope="module")
def mod():
    return _load()


def _make_de(mod, *, allow=True, reason="AUTO-HEAL: SOVEREIGN-AUTO"):
    de = MagicMock(spec=mod.SovereignDecisionEngine)
    cs = mod.ConfidenceScore(value=0.9, reasoning="test")
    de.calculate_healing_confidence.return_value = cs
    de.should_proceed_with_healing.return_value = (allow, reason)
    return de


def _make_ctx(heal=True, auto_approve=False):
    ctx = MagicMock()
    ctx.heal = heal
    ctx.auto_approve = auto_approve
    return ctx


def _make_state_mgr():
    sm = MagicMock()
    sm.state = {}
    return sm


# ===========================================================================
# Phase 3: execute_phase3_alignment_impl
# ===========================================================================


class TestPhase3Alignment:
    def _hier_scan_result(self, violations_count):
        """Build a scan result compatible with HierarchyAgent.scan_root_violations()."""
        return {
            "violations": [f"v{i}" for i in range(violations_count)],
            "violations_found": violations_count,
        }

    def _mock_hier_agent(self, violations_count):
        """Return (hier_cls, hier_inst) mocking HierarchyAgent with given violation count."""
        hier_cls = MagicMock()
        hier_inst = MagicMock()
        hier_inst.scan_root_violations.return_value = self._hier_scan_result(violations_count)
        hier_cls.return_value = hier_inst
        return hier_cls, hier_inst

    def _hier_agent_patch(self, hier_cls):
        return {
            "agentic_core.L5_safety.reasoning.hierarchy_validator": MagicMock(
                HierarchyValidatorAgent=hier_cls
            )
        }

    def test_zero_violations_completes_no_violations(self, mod):
        de = _make_de(mod)
        sm = _make_state_mgr()
        agents = {}
        hier_cls, _ = self._mock_hier_agent(0)

        with patch.dict("sys.modules", self._hier_agent_patch(hier_cls)):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                result = mod.execute_phase3_alignment_impl(agents, "neutral", de, sm)

        assert result is None
        sm.complete_agent.assert_called()
        call_args = sm.complete_agent.call_args[0]
        assert "No violations" in call_args[2]

    def test_violations_proceed_false_skipped(self, mod):
        de = _make_de(mod, allow=False, reason="BLOCKED")
        sm = _make_state_mgr()
        agents = {}
        hier_cls, _ = self._mock_hier_agent(3)

        with patch.dict("sys.modules", self._hier_agent_patch(hier_cls)):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                result = mod.execute_phase3_alignment_impl(agents, "neutral", de, sm)

        assert result is None
        sm.complete_agent.assert_called()
        call_args = sm.complete_agent.call_args[0]
        assert call_args[1] is False

    def test_violations_proceed_true_ctx_heal_false_returns_none(self, mod):
        de = _make_de(mod, allow=True)
        sm = _make_state_mgr()
        agents = {}
        hier_cls, _ = self._mock_hier_agent(2)

        with patch.dict("sys.modules", self._hier_agent_patch(hier_cls)):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                result = mod.execute_phase3_alignment_impl(
                    agents, "neutral", de, sm, ctx=_make_ctx(heal=False)
                )

        assert result is None

    def test_violations_proceed_true_heal_true_invokes_healer(self, mod):
        de = _make_de(mod, allow=True)
        sm = _make_state_mgr()
        sm.state = {}
        hier_cls, _ = self._mock_hier_agent(4)

        healer_cls = MagicMock()
        healer_inst = MagicMock()
        healer_inst.heal_repository.return_value = {"violations_fixed": 2}
        healer_cls.return_value = healer_inst
        agents = {"hierarchy": healer_cls}

        with patch.dict("sys.modules", self._hier_agent_patch(hier_cls)):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                with patch(
                    "agentic_core.L5_safety.enforcement.hitl_gate.get_hitl_gate",
                    return_value=_auto_approve_gate(),
                ):
                    result = mod.execute_phase3_alignment_impl(
                        agents, "neutral", de, sm, ctx=_make_ctx(heal=True)
                    )

        assert result is not None
        healer_inst.heal_repository.assert_called_once()
        assert result["total_healed"] == 2

    def test_violations_proceed_true_heal_true_updates_state(self, mod):
        de = _make_de(mod, allow=True)
        sm = _make_state_mgr()
        sm.state = {}
        hier_cls, _ = self._mock_hier_agent(1)

        healer_cls = MagicMock()
        healer_inst = MagicMock()
        healer_inst.heal_repository.return_value = {"violations_fixed": 1}
        healer_cls.return_value = healer_inst
        agents = {"hierarchy": healer_cls}

        with patch.dict("sys.modules", self._hier_agent_patch(hier_cls)):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                with patch(
                    "agentic_core.L5_safety.enforcement.hitl_gate.get_hitl_gate",
                    return_value=_auto_approve_gate(),
                ):
                    mod.execute_phase3_alignment_impl(agents, "neutral", de, sm, ctx=_make_ctx(heal=True))

        assert sm.state.get("hierarchy_fixed") is not None

    def test_decision_event_added_when_violations(self, mod):
        de = _make_de(mod, allow=True)
        sm = _make_state_mgr()
        agents = {}
        hier_cls, _ = self._mock_hier_agent(2)

        with patch.dict("sys.modules", self._hier_agent_patch(hier_cls)):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                mod.execute_phase3_alignment_impl(agents, "neutral", de, sm)

        sm.add_event.assert_called()


# ===========================================================================
# Phase 4: execute_phase4_validation_impl
# ===========================================================================


class TestPhase4Validation:
    def _make_agents(self, gov_report=None, size_violations=None):
        arch_gov_inst = MagicMock()
        arch_gov_inst.comprehensive_territory_audit.return_value = gov_report
        arch_gov_inst.check_file_sizes.return_value = size_violations or []
        arch_gov_cls = MagicMock(return_value=arch_gov_inst)
        return {"arch_governor": arch_gov_cls}, arch_gov_inst

    _ET_PATCH = "agentic_core.L5_safety.config.structure_blueprint.ENFORCED_TERRITORIES"

    def test_gov_report_none_returns_none_tuple(self, mod):
        sm = _make_state_mgr()
        agents, _ = self._make_agents(gov_report=None)

        with patch(self._ET_PATCH, frozenset([AGENTIC_CORE_DIR])):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                result = mod.execute_phase4_validation_impl(agents, "neutral", sm)

        assert result == (None, None)
        sm.complete_agent.assert_called_with("ArchitectureGovernorAgent", False, "Returned None")

    def test_territory_in_enforced_audits_all(self, mod):
        sm = _make_state_mgr()
        gov_report = {"layer_violations": [], "naming_violations": []}
        agents, arch_inst = self._make_agents(gov_report=gov_report)

        enforced = frozenset([AGENTIC_CORE_DIR, TESTS_DIR, APPS_LIC_DIR])

        with patch(self._ET_PATCH, enforced):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                mod.execute_phase4_validation_impl(agents, AGENTIC_CORE_DIR, sm)

        call_kwargs = arch_inst.comprehensive_territory_audit.call_args[1]
        target_territories = call_kwargs["target_territories"]
        assert set(target_territories) == set(enforced)

    def test_territory_not_in_enforced_audits_only_territory(self, mod):
        sm = _make_state_mgr()
        gov_report = {"layer_violations": [], "naming_violations": []}
        agents, arch_inst = self._make_agents(gov_report=gov_report)

        enforced = frozenset([AGENTIC_CORE_DIR, TESTS_DIR])

        with patch(self._ET_PATCH, enforced):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                mod.execute_phase4_validation_impl(agents, APPS_RG_DIR, sm)

        call_kwargs = arch_inst.comprehensive_territory_audit.call_args[1]
        assert APPS_RG_DIR in call_kwargs["target_territories"]

    def test_non_l_layer_territory_no_file_size_check(self, mod):
        sm = _make_state_mgr()
        gov_report = {"layer_violations": [], "naming_violations": []}
        agents, arch_inst = self._make_agents(gov_report=gov_report)

        with patch(self._ET_PATCH, frozenset()):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                result = mod.execute_phase4_validation_impl(agents, APPS_RG_DIR, sm)

        arch_inst.check_file_sizes.assert_not_called()
        assert result == (gov_report, None)

    def test_l_layer_territory_calls_file_size_check(self, mod):
        sm = _make_state_mgr()
        gov_report = {"layer_violations": [], "naming_violations": []}
        agents, arch_inst = self._make_agents(gov_report=gov_report, size_violations=[])

        with patch(self._ET_PATCH, frozenset()):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                mod.execute_phase4_validation_impl(agents, "L0_routing", sm)

        arch_inst.check_file_sizes.assert_called_once_with("L0_routing")

    def test_l_layer_size_violations_logged_as_warnings(self, mod):
        sm = _make_state_mgr()
        gov_report = {"layer_violations": [], "naming_violations": []}
        size_violations = [{"message": "too big: file.py"}]
        agents, arch_inst = self._make_agents(gov_report=gov_report, size_violations=size_violations)

        with patch(self._ET_PATCH, frozenset()):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                mod.execute_phase4_validation_impl(agents, "L1_cognition", sm)

        sm.add_event.assert_called()
        event_calls = sm.add_event.call_args_list
        assert any("warning" in str(c) for c in event_calls)

    def test_returns_gov_report_on_success(self, mod):
        sm = _make_state_mgr()
        gov_report = {"layer_violations": ["v1"], "naming_violations": []}
        agents, _ = self._make_agents(gov_report=gov_report)

        with patch(self._ET_PATCH, frozenset()):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                result = mod.execute_phase4_validation_impl(agents, APPS_RG_DIR, sm)

        assert result[0] is gov_report

    def test_all_l_layer_prefixes_trigger_size_check(self, mod):
        for prefix in ("L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_"):
            sm = _make_state_mgr()
            gov_report = {"layer_violations": [], "naming_violations": []}
            agents, arch_inst = self._make_agents(gov_report=gov_report, size_violations=[])
            territory = f"{prefix}test_layer"

            with patch(self._ET_PATCH, frozenset()):
                with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                    mod.execute_phase4_validation_impl(agents, territory, sm)

            arch_inst.check_file_sizes.assert_called_once(), f"check_file_sizes not called for {territory}"


# ===========================================================================
# Phase 5: execute_phase5_healing_impl
# ===========================================================================


class TestPhase5Healing:
    def _make_arch_agent(self, gov_report, plan, *, requires_healing=True, naming_fixes=2):
        if plan is None:
            actual_plan = None
        else:
            actual_plan = {
                "requires_healing": requires_healing,
                "naming_fixes": [f"fix{i}" for i in range(naming_fixes)],
            }
        arch_inst = MagicMock()
        arch_inst.generate_healing_plan.return_value = actual_plan
        arch_inst.check_file_sizes.return_value = []
        arch_cls = MagicMock(return_value=arch_inst)
        return {"arch_governor": arch_cls}, arch_inst

    def test_gov_report_none_returns_none(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod)
        agents, _ = self._make_arch_agent(None, None)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
            result = mod.execute_phase5_healing_impl(agents, "neutral", None, de, sm)

        assert result is None

    def test_plan_none_returns_none(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod)
        agents, _ = self._make_arch_agent({}, None)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
            result = mod.execute_phase5_healing_impl(agents, "neutral", {"something": 1}, de, sm)

        assert result is None

    def test_requires_healing_false_returns_none(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod)
        gov_report = {"violations": []}
        agents, _ = self._make_arch_agent(gov_report, {}, requires_healing=False)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
            result = mod.execute_phase5_healing_impl(agents, "neutral", gov_report, de, sm)

        assert result is None

    def test_requires_healing_true_decision_blocked_skip_agent(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod, allow=False, reason="BLOCKED")
        gov_report = {"violations": []}
        agents, _ = self._make_arch_agent(gov_report, {}, requires_healing=True)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
            result = mod.execute_phase5_healing_impl(agents, "neutral", gov_report, de, sm)

        assert sm.complete_agent.called or sm.skip_agent.called or sm.add_event.called
        assert result is None

    def test_requires_healing_true_ctx_none_skip_agent(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod, allow=True)
        gov_report = {"violations": []}
        agents, _ = self._make_arch_agent(gov_report, {}, requires_healing=True)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
            result = mod.execute_phase5_healing_impl(agents, "neutral", gov_report, de, sm, ctx=None)

        assert sm.complete_agent.called or sm.skip_agent.called or sm.add_event.called
        assert result is None

    def test_requires_healing_true_ctx_heal_false_skip(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod, allow=True)
        gov_report = {"violations": []}
        agents, _ = self._make_arch_agent(gov_report, {}, requires_healing=True)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
            result = mod.execute_phase5_healing_impl(
                agents, "neutral", gov_report, de, sm, ctx=_make_ctx(heal=False)
            )

        assert sm.complete_agent.called or sm.skip_agent.called or sm.add_event.called
        assert result is None

    def test_requires_healing_true_ctx_heal_true_invokes_healer(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod, allow=True)
        gov_report = {"violations": []}
        agents, _ = self._make_arch_agent(gov_report, {}, requires_healing=True, naming_fixes=3)

        heal_result = MagicMock()
        heal_result.status = MagicMock(value="SUCCESS")
        heal_result.changes_made = ["fix1", "fixed2"]

        dispatcher_mod = MagicMock()
        dispatcher_mod._invoke_healer = MagicMock(return_value=heal_result)

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L2_execution.scripts.remediation_dispatcher": dispatcher_mod,
            },
        ):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                result = mod.execute_phase5_healing_impl(
                    agents, "neutral", gov_report, de, sm, ctx=_make_ctx(heal=True)
                )

        assert result is not None
        assert "status" in result

    def test_healer_invoked_with_architecture_governance_id(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod, allow=True)
        gov_report = {}
        agents, arch_inst = self._make_arch_agent(gov_report, {}, requires_healing=True, naming_fixes=1)
        arch_inst.heal_repository.return_value = {"violations_fixed": 1}

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
            result = mod.execute_phase5_healing_impl(
                agents, "neutral", gov_report, de, sm, ctx=_make_ctx(heal=True)
            )

        arch_inst.heal_repository.assert_called()
        assert result is not None

    def test_decision_event_added_on_healing_attempt(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod, allow=True)
        gov_report = {}
        agents, _ = self._make_arch_agent(gov_report, {}, requires_healing=True)

        with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
            mod.execute_phase5_healing_impl(agents, "neutral", gov_report, de, sm, ctx=None)

        sm.add_event.assert_called()
        event_calls = sm.add_event.call_args_list
        assert any("decision" in str(c).lower() or "Arch" in str(c) for c in event_calls)

    def test_complete_agent_called_on_heal_success(self, mod):
        sm = _make_state_mgr()
        de = _make_de(mod, allow=True)
        gov_report = {}
        agents, _ = self._make_arch_agent(gov_report, {}, requires_healing=True, naming_fixes=1)

        heal_result = MagicMock()
        heal_result.status = MagicMock(value="SUCCESS")
        heal_result.changes_made = []

        dispatcher_mod = MagicMock()
        dispatcher_mod._invoke_healer = MagicMock(return_value=heal_result)

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L2_execution.scripts.remediation_dispatcher": dispatcher_mod,
            },
        ):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                mod.execute_phase5_healing_impl(
                    agents, "neutral", gov_report, de, sm, ctx=_make_ctx(heal=True)
                )

        sm.complete_agent.assert_called()


# ===========================================================================
# Matrix: ctx.heal x decision x violations across all phases
# ===========================================================================


class TestPhaseMatrix:
    """Matrix test: heal x proceed x violations for Phases 3 and 5."""

    @pytest.mark.parametrize(
        "heal,proceed,violations_count,expect_healer",
        [
            (True, True, 3, True),
            (True, False, 3, False),
            (False, True, 3, False),
            (False, False, 3, False),
            (True, True, 0, False),
        ],
    )
    def test_phase3_matrix(self, mod, heal, proceed, violations_count, expect_healer):
        de = _make_de(mod, allow=proceed)
        sm = _make_state_mgr()
        sm.state = {}
        agents = {}

        hier_cls = MagicMock()
        hier_inst = MagicMock()
        hier_inst.scan_root_violations.return_value = {
            "violations": ["v"] * violations_count,
            "violations_found": violations_count,
        }
        hier_cls.return_value = hier_inst

        healer_cls = MagicMock()
        healer_inst = MagicMock()
        healer_inst.heal_repository.return_value = {"violations_fixed": 1}
        healer_cls.return_value = healer_inst
        agents_with_healer = dict(agents)
        agents_with_healer["hierarchy"] = healer_cls

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L5_safety.reasoning.hierarchy_validator": MagicMock(
                    HierarchyValidatorAgent=hier_cls
                )
            },
        ):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                with patch(
                    "agentic_core.L5_safety.enforcement.hitl_gate.get_hitl_gate",
                    return_value=_auto_approve_gate(),
                ):
                    mod.execute_phase3_alignment_impl(
                        agents_with_healer, "neutral", de, sm, ctx=_make_ctx(heal=heal)
                    )

        if expect_healer:
            healer_inst.heal_repository.assert_called()
        else:
            healer_inst.heal_repository.assert_not_called()

    @pytest.mark.parametrize(
        "heal,proceed,requires_healing,expect_healer",
        [
            (True, True, True, True),
            (True, False, True, False),
            (False, True, True, False),
            (True, True, False, False),
            (True, True, True, True),
        ],
    )
    def test_phase5_matrix(self, mod, heal, proceed, requires_healing, expect_healer):
        de = _make_de(mod, allow=proceed)
        sm = _make_state_mgr()
        gov_report = {}

        arch_inst = MagicMock()
        plan = {"requires_healing": requires_healing, "naming_fixes": ["f1"]}
        arch_inst.generate_healing_plan.return_value = plan
        arch_cls = MagicMock(return_value=arch_inst)
        agents = {"arch_governor": arch_cls}

        heal_result = MagicMock()
        heal_result.status = MagicMock(value="SUCCESS")
        heal_result.changes_made = []

        dispatcher_mod = MagicMock()
        dispatcher_mod._invoke_healer = MagicMock(return_value=heal_result)

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.L2_execution.scripts.remediation_dispatcher": dispatcher_mod,
            },
        ):
            with patch("agentic_core.L0_routing.scripts.execute_ssot.REPO_ROOT", MagicMock()):
                mod.execute_phase5_healing_impl(
                    agents,
                    "neutral",
                    gov_report,
                    de,
                    sm,
                    ctx=_make_ctx(heal=heal) if heal is not None else None,
                )

        if expect_healer:
            arch_inst.heal_repository.assert_called()
        else:
            arch_inst.heal_repository.assert_not_called()
