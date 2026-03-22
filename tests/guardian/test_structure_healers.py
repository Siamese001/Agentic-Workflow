"""
Contract Tests: Wave 6 Healers (classification, hierarchy, architecture).

Tests:
1. Dry-run mode returns SKIPPED with planned actions
2. Apply mode for territory_compliance moves files
3. Apply mode for missing_structure creates directories
4. Human-review-only healers always return SKIPPED
5. HealCheckResult schema validity
6. Healer registry contains all expected entries
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L1_COGNITION_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_structure_healers")
_emit_applies_guardrail("p0", "test_structure_healers", "p0_governance")
_emit_reads_policy_state("p0", "test_structure_healers", "policy_binding")
_emit_snapshots_state("p0", "test_structure_healers", "state_snapshot")
emit_replay_key("p0", "test_structure_healers")
emit_determinism_digest("p0", "test_structure_healers")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_structure_healers", "execution_auth")
_emit_validates_capability("p2", "test_structure_healers", "capability_check")
_emit_routes_to_capability("p2", "test_structure_healers", "capability_route")
_emit_writes_via_uwg("p2", "test_structure_healers", "uwg_write")
_emit_blocks_direct_write("p2", "test_structure_healers", "direct_write_block")
_emit_records_tool_invocation("p2", "test_structure_healers", "tool_invocation")
_emit_captures_execution_output("p2", "test_structure_healers", "exec_output")
_emit_dispatches_agent("p3", "test_structure_healers", "agent_dispatch")
_emit_coordinates_agents("p3", "test_structure_healers", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_structure_healers", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_structure_healers", "healing_outcome")
_emit_escalates_failure("p3", "test_structure_healers", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_structure_healers", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_structure_healers", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_structure_healers", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_structure_healers", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_structure_healers", "eval_metric")
_emit_stores_embedding("p4", "test_structure_healers", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_structure_healers", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_structure_healers", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L2_execution.healers.architecture_governance_healer import (
    heal_import_compliance,
    heal_layer_gravity,
)
from agentic_core.L2_execution.healers.classification_compliance_healer import (
    heal_naming_compliance,
    heal_territory_compliance,
)
from agentic_core.L2_execution.healers.hierarchy_compliance_healer import (
    heal_missing_structure,
    heal_subfolder_compliance,
)
from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
from agentic_core.L2_execution.types.healer_registry_types import HEALER_REGISTRY
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_structure_healers", "p4obs", "metric_1")
_emit_emits_metric_event("test_structure_healers", "p4obs", "metric_2")
_emit_emits_metric_event("test_structure_healers", "p4obs", "metric_3")
_emit_emits_metric_event("test_structure_healers", "p4obs", "metric_4")
_emit_emits_metric_event("test_structure_healers", "p4obs", "metric_5")
_emit_emits_metric_event("test_structure_healers", "p4obs", "metric_6")
_emit_records_incident_event("test_structure_healers", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_structure_healers", "p4obs", "anomaly")
_emit_writes_observability_log("test_structure_healers", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_structure_healers", "p4obs", "mon_state")
_emit_triggers_alert("test_structure_healers", "p4obs", "alert")
_emit_links_incident_trace("test_structure_healers", "p4obs", "trace_link")
_emit_captures_pattern("test_structure_healers", "p3lm", "pattern")
_emit_records_learning_event("test_structure_healers", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_structure_healers", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_structure_healers", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_structure_healers", "p3lm", "routing")
_emit_improves_agent_policy("test_structure_healers", "p3lm", "policy")
_emit_stores_learning_state("test_structure_healers", "p3lm", "state")
_emit_records_execution_trace("test_structure_healers", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_structure_healers", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_structure_healers", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_structure_healers", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_structure_healers", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_structure_healers", "env_read", "p2_env_1")
_emit_reads_environ("test_structure_healers", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_structure_healers", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_structure_healers", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_structure_healers", "context_pull")
_emit_pulls_context("p1", "test_structure_healers", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_structure_healers", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_structure_healers", "uwg_term_secondary")
_emit_writes_through("p1", "test_structure_healers", "write_through")
_emit_writes_through("p1", "test_structure_healers", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_structure_healers", "safety_validation")
_emit_invokes_eval("p1", "test_structure_healers", "eval_call")
_emit_proposal_commits_routing("p1", "test_structure_healers", "routing_commit")
_emit_escalates_to_human("p1", "test_structure_healers", "human_escalation")
_emit_routes_through("p1", "test_structure_healers", "route_through")
_emit_checks_agent_registry("p1", "test_structure_healers", "agent_registry")
_emit_validates_agent_capability("p1", "test_structure_healers", "capability")
_emit_dispatches_execution_plan("p1", "test_structure_healers", "exec_plan")
_emit_agent_executes_agent("p1", "test_structure_healers", "sub_agent")
_emit_routes_to_agent("p1", "test_structure_healers", "target_agent")
_emit_verifies_policy("p1", "test_structure_healers", "policy_check")
_emit_observes_runtime_state("p1", "test_structure_healers", "runtime_state")
_emit_verifies_boundary("p1", "test_structure_healers", "boundary_check")
_emit_transcripts_response("p1", "test_structure_healers", "transcript")
_emit_hard_fails_untranscripted("p1", "test_structure_healers")
_emit_gated_by_confidence("p1", "test_structure_healers", "confidence_gate")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures: synthetic check dicts (mimic guardian aggregate evidence)
# ---------------------------------------------------------------------------


@pytest.fixture()
def naming_check() -> dict:
    return {
        "check_id": "naming_compliance",
        "status": "FAIL",
        "evidence": {
            "violation_count": 2,
            "violations": [
                {"path": "agentic_core/L1_cognition/config/foo_config_types.py"},
                {"path": "agentic_core/L2_execution/utils/bar_util_mixin.py"},
            ],
        },
    }


@pytest.fixture()
def territory_check() -> dict:
    return {
        "check_id": "territory_compliance",
        "status": "FAIL",
        "evidence": {
            "violation_count": 1,
            "violations": [
                {
                    "path": "agentic_core/L1_cognition/config/SomeAgent.py",
                    "classified_as": "AGENT",
                    "expected_folder": "reasoning",
                    "actual_folder": "config",
                },
            ],
        },
    }


@pytest.fixture()
def missing_structure_check() -> dict:
    return {
        "check_id": "missing_structure",
        "status": "FAIL",
        "evidence": {
            "violation_count": 2,
            "violations": [
                {"level": "L2", "path": "agentic_core/L7_future"},
                {"level": "L3", "path": "agentic_core/L5_safety/new_subfolder", "parent_layer": "L5_safety"},
            ],
        },
    }


@pytest.fixture()
def subfolder_check() -> dict:
    return {
        "check_id": "subfolder_compliance",
        "status": "FAIL",
        "evidence": {
            "violation_count": 1,
            "violations": [
                {"path": "agentic_core/L5_safety/rogue", "parent_layer": "L5_safety", "folder_name": "rogue"},
            ],
        },
    }


@pytest.fixture()
def import_check() -> dict:
    return {
        "check_id": "import_compliance",
        "status": "FAIL",
        "evidence": {
            "violation_count": 1,
            "violations": [
                {
                    "path": "agentic_core/L0_routing/scripts/bad.py",
                    "source_layer": "L0",
                    "target_layer": "L5",
                    "import_line": "from agentic_core.L5_safety.reasoning import ...",
                    "line_number": 3,
                },
            ],
        },
    }


@pytest.fixture()
def gravity_check() -> dict:
    return {
        "check_id": "layer_gravity",
        "status": "FAIL",
        "evidence": {
            "violation_count": 1,
            "violations": [
                {
                    "path": "agentic_core/L0_routing/reasoning/WrongAgent.py",
                    "agent_name": "WrongAgent",
                    "actual_layer": "L0",
                    "assigned_layer": "L3",
                },
            ],
        },
    }


# ---------------------------------------------------------------------------
# 1. Healer registry completeness
# ---------------------------------------------------------------------------


class TestHealerRegistry:
    """Verify all Wave 6 healers are registered."""

    EXPECTED_IDS = {
        "naming_compliance",
        "territory_compliance",
        "missing_structure",
        "subfolder_compliance",
        "import_compliance",
        "layer_gravity",
    }

    def test_all_healers_registered(self) -> None:
        for cid in self.EXPECTED_IDS:
            assert cid in HEALER_REGISTRY, f"{cid} not in HEALER_REGISTRY"

    def test_registry_values_are_callable(self) -> None:
        for cid in self.EXPECTED_IDS:
            assert callable(HEALER_REGISTRY[cid])


# ---------------------------------------------------------------------------
# 2. Classification compliance healers
# ---------------------------------------------------------------------------


class TestNamingComplianceHealer:
    """Naming healer is always dry-run only."""

    def test_dry_run_returns_skipped(self, naming_check: dict) -> None:
        result = heal_naming_compliance(naming_check)
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 2

    def test_apply_still_skipped(self, naming_check: dict, tmp_path: Path) -> None:
        result = heal_naming_compliance(naming_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.SKIPPED

    def test_planned_actions_sorted(self, naming_check: dict) -> None:
        result = heal_naming_compliance(naming_check)
        assert list(result.changes_made) == sorted(result.changes_made)


class TestTerritoryComplianceHealer:
    """Territory healer supports dry-run and apply."""

    def test_dry_run_returns_skipped(self, territory_check: dict) -> None:
        result = heal_territory_compliance(territory_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 1
        assert "would_move" in result.changes_made[0]

    def test_apply_moves_file(self, territory_check: dict, tmp_path: Path) -> None:
        # Create source file
        src = tmp_path / L1_COGNITION_DIR / "config" / "SomeAgent.py"
        src.parent.mkdir(parents=True)
        src.write_text("class SomeAgent: pass\n", encoding="utf-8")

        result = heal_territory_compliance(territory_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.HEALED
        assert len(result.changes_made) == 1

        # Verify file moved
        target = tmp_path / L1_COGNITION_DIR / "reasoning" / "SomeAgent.py"
        assert target.is_file()
        assert not src.exists()

    def test_apply_without_repo_root_fails(self, territory_check: dict) -> None:
        result = heal_territory_compliance(territory_check, apply=True)
        assert result.status == HealStatus.FAILED


# ---------------------------------------------------------------------------
# 3. Hierarchy compliance healers
# ---------------------------------------------------------------------------


class TestMissingStructureHealer:
    """Missing structure healer supports dry-run and apply."""

    def test_dry_run_returns_skipped(self, missing_structure_check: dict) -> None:
        result = heal_missing_structure(missing_structure_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 2

    def test_apply_creates_directories(self, missing_structure_check: dict, tmp_path: Path) -> None:
        result = heal_missing_structure(missing_structure_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.HEALED
        assert len(result.changes_made) == 2

        assert (tmp_path / AGENTIC_CORE_DIR / "L7_future").is_dir()
        assert (tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "new_subfolder").is_dir()

    def test_apply_without_repo_root_fails(self, missing_structure_check: dict) -> None:
        result = heal_missing_structure(missing_structure_check, apply=True)
        assert result.status == HealStatus.FAILED

    def test_planned_actions_sorted(self, missing_structure_check: dict) -> None:
        result = heal_missing_structure(missing_structure_check)
        assert list(result.changes_made) == sorted(result.changes_made)


class TestSubfolderComplianceHealer:
    """Subfolder healer is always dry-run only."""

    def test_dry_run_returns_skipped(self, subfolder_check: dict) -> None:
        result = heal_subfolder_compliance(subfolder_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 1

    def test_apply_still_skipped(self, subfolder_check: dict, tmp_path: Path) -> None:
        result = heal_subfolder_compliance(subfolder_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.SKIPPED


# ---------------------------------------------------------------------------
# 4. Architecture governance healers (dry-run only)
# ---------------------------------------------------------------------------


class TestImportComplianceHealer:
    """Import compliance healer is always dry-run only."""

    def test_dry_run_returns_skipped(self, import_check: dict) -> None:
        result = heal_import_compliance(import_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 1
        assert "would_fix_import" in result.changes_made[0]

    def test_apply_still_skipped(self, import_check: dict, tmp_path: Path) -> None:
        result = heal_import_compliance(import_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.SKIPPED


class TestLayerGravityHealer:
    """Layer gravity healer is always dry-run only."""

    def test_dry_run_returns_skipped(self, gravity_check: dict) -> None:
        result = heal_layer_gravity(gravity_check)
        assert result.status == HealStatus.SKIPPED
        assert len(result.changes_made) == 1
        assert "would_relocate_agent" in result.changes_made[0]

    def test_apply_still_skipped(self, gravity_check: dict, tmp_path: Path) -> None:
        result = heal_layer_gravity(gravity_check, repo_root=tmp_path, apply=True)
        assert result.status == HealStatus.SKIPPED


# ---------------------------------------------------------------------------
# 5. Schema validity (all healers return valid HealCheckResult)
# ---------------------------------------------------------------------------


class TestSchemaValidity:
    """Verify all healers produce valid HealCheckResult objects."""

    ALL_HEALER_FIXTURES = [
        "naming_check",
        "territory_check",
        "missing_structure_check",
        "subfolder_check",
        "import_check",
        "gravity_check",
    ]

    @pytest.mark.parametrize(
        "check_id",
        [
            "naming_compliance",
            "territory_compliance",
            "missing_structure",
            "subfolder_compliance",
            "import_compliance",
            "layer_gravity",
        ],
    )
    def test_healer_returns_valid_result(self, check_id: str) -> None:
        check = {"check_id": check_id, "status": "PASS", "evidence": {"violations": []}}
        healer_fn = HEALER_REGISTRY[check_id]
        result = healer_fn(check)
        assert isinstance(result, HealCheckResult)
        assert result.check_id == check_id
        assert isinstance(result.status, HealStatus)
        assert isinstance(result.changes_made, tuple)
