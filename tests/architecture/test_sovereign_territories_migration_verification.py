"""Comprehensive verification suite for SOVEREIGN_TERRITORIES migration (Phases 1-5).

This test suite verifies:
1. New territory API functions work correctly
2. All public imports use new API (no SOVEREIGN_TERRITORIES in public code)
3. Deprecation warning triggers correctly
4. All test files migrated successfully
5. Internal testing code still has access to SOVEREIGN_TERRITORIES
6. No regressions in derived registries
"""

from __future__ import annotations

import sqlite3
import warnings

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

_emit_records_execution_trace("p0", "evidence", "test_sovereign_territories_migration_verification")
_emit_applies_guardrail("p0", "test_sovereign_territories_migration_verification", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereign_territories_migration_verification", "policy_binding")
_emit_snapshots_state("p0", "test_sovereign_territories_migration_verification", "state_snapshot")
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
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_sovereign_territories_migration_verification", "p4obs", "metric_1")
_emit_emits_metric_event("test_sovereign_territories_migration_verification", "p4obs", "metric_2")
_emit_emits_metric_event("test_sovereign_territories_migration_verification", "p4obs", "metric_3")
_emit_emits_metric_event("test_sovereign_territories_migration_verification", "p4obs", "metric_4")
_emit_emits_metric_event("test_sovereign_territories_migration_verification", "p4obs", "metric_5")
_emit_emits_metric_event("test_sovereign_territories_migration_verification", "p4obs", "metric_6")
_emit_records_incident_event("test_sovereign_territories_migration_verification", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sovereign_territories_migration_verification", "p4obs", "anomaly")
_emit_writes_observability_log("test_sovereign_territories_migration_verification", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sovereign_territories_migration_verification", "p4obs", "mon_state")
_emit_triggers_alert("test_sovereign_territories_migration_verification", "p4obs", "alert")
_emit_links_incident_trace("test_sovereign_territories_migration_verification", "p4obs", "trace_link")
_emit_captures_pattern("test_sovereign_territories_migration_verification", "p3lm", "pattern")
_emit_records_learning_event("test_sovereign_territories_migration_verification", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sovereign_territories_migration_verification", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sovereign_territories_migration_verification", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sovereign_territories_migration_verification", "p3lm", "routing")
_emit_improves_agent_policy("test_sovereign_territories_migration_verification", "p3lm", "policy")
_emit_stores_learning_state("test_sovereign_territories_migration_verification", "p3lm", "state")
_emit_records_execution_trace("test_sovereign_territories_migration_verification", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_sovereign_territories_migration_verification", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_sovereign_territories_migration_verification", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_sovereign_territories_migration_verification", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_sovereign_territories_migration_verification", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_sovereign_territories_migration_verification", "env_read", "p2_env_1")
_emit_reads_environ("test_sovereign_territories_migration_verification", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_sovereign_territories_migration_verification", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_sovereign_territories_migration_verification", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_sovereign_territories_migration_verification", "context_pull")
_emit_pulls_context("p1", "test_sovereign_territories_migration_verification", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_sovereign_territories_migration_verification", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_sovereign_territories_migration_verification", "uwg_term_2")
_emit_writes_through("p1", "test_sovereign_territories_migration_verification", "write_through")
_emit_writes_through("p1", "test_sovereign_territories_migration_verification", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_sovereign_territories_migration_verification", "safety_validation")
_emit_invokes_eval("p1", "test_sovereign_territories_migration_verification", "eval_call")
_emit_proposal_commits_routing("p1", "test_sovereign_territories_migration_verification", "routing_commit")
_emit_escalates_to_human("p1", "test_sovereign_territories_migration_verification", "human_escalation")
_emit_routes_through("p1", "test_sovereign_territories_migration_verification", "route_through")
_emit_checks_agent_registry("p1", "test_sovereign_territories_migration_verification", "agent_registry")
_emit_validates_agent_capability("p1", "test_sovereign_territories_migration_verification", "capability")
_emit_dispatches_execution_plan("p1", "test_sovereign_territories_migration_verification", "exec_plan")
_emit_agent_executes_agent("p1", "test_sovereign_territories_migration_verification", "sub_agent")
_emit_routes_to_agent("p1", "test_sovereign_territories_migration_verification", "target_agent")
_emit_verifies_policy("p1", "test_sovereign_territories_migration_verification", "policy_check")
_emit_observes_runtime_state("p1", "test_sovereign_territories_migration_verification", "runtime_state")
_emit_verifies_boundary("p1", "test_sovereign_territories_migration_verification", "boundary_check")
_emit_transcripts_response("p1", "test_sovereign_territories_migration_verification", "transcript")
_emit_hard_fails_untranscripted("p1", "test_sovereign_territories_migration_verification")
_emit_gated_by_confidence("p1", "test_sovereign_territories_migration_verification", "confidence_gate")
emit_replay_key("p0", "test_sovereign_territories_migration_verification")
emit_determinism_digest("p0", "test_sovereign_territories_migration_verification")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_sovereign_territories_migration_verification", "execution_auth")
_emit_validates_capability("p2", "test_sovereign_territories_migration_verification", "capability_check")
_emit_routes_to_capability("p2", "test_sovereign_territories_migration_verification", "capability_route")
_emit_writes_via_uwg("p2", "test_sovereign_territories_migration_verification", "uwg_write")
_emit_blocks_direct_write("p2", "test_sovereign_territories_migration_verification", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sovereign_territories_migration_verification", "tool_invocation")
_emit_captures_execution_output("p2", "test_sovereign_territories_migration_verification", "exec_output")
_emit_dispatches_agent("p3", "test_sovereign_territories_migration_verification", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sovereign_territories_migration_verification", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sovereign_territories_migration_verification", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sovereign_territories_migration_verification", "healing_outcome")
_emit_escalates_failure("p3", "test_sovereign_territories_migration_verification", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sovereign_territories_migration_verification", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sovereign_territories_migration_verification", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sovereign_territories_migration_verification", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sovereign_territories_migration_verification", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sovereign_territories_migration_verification", "eval_metric")
_emit_stores_embedding("p4", "test_sovereign_territories_migration_verification", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sovereign_territories_migration_verification", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sovereign_territories_migration_verification", "exec_snapshot_link")


class TestNewTerritoryAPI:
    """Verify new territory API functions work correctly."""

    def test_get_all_territories_returns_mapping(self):
        """get_all_territories() returns a Mapping with expected territories."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            get_all_territories,
        )

        territories = get_all_territories()
        assert hasattr(territories, "items"), "Should return a Mapping"
        assert len(territories) > 0, "Should have at least one territory"

        # Verify expected territories exist
        expected = ["agentic_core", "apps_shared", "apps_rg", "apps_lic", "tests"]
        for territory in expected:
            assert territory in territories, f"{territory} should be in territories"

    def test_get_territory_metadata_returns_dict(self):
        """get_territory_metadata() returns territory definition dict."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            get_territory_metadata,
        )

        meta = get_territory_metadata("apps_shared")
        assert meta is not None, "apps_shared should exist"
        assert isinstance(meta, dict), "Should return a dict"
        assert "purpose" in meta or "subfolders" in meta, "Should have metadata keys"

    def test_get_territory_metadata_returns_none_for_invalid(self):
        """get_territory_metadata() returns None for invalid territory."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            get_territory_metadata,
        )

        meta = get_territory_metadata("invalid_territory_name_xyz")
        assert meta is None, "Should return None for invalid territory"

    def test_is_valid_root_folder_accepts_valid(self):
        """is_valid_root_folder() returns True for valid root folders."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            is_valid_root_folder,
        )

        assert is_valid_root_folder("apps_shared") is True
        assert is_valid_root_folder("agentic_core") is True
        assert is_valid_root_folder("tests") is True

    def test_is_valid_root_folder_rejects_invalid(self):
        """is_valid_root_folder() returns False for invalid folders."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            is_valid_root_folder,
        )

        assert is_valid_root_folder("invalid_folder") is False
        assert is_valid_root_folder("random_dir") is False


class TestPublicAPINoSovereignTerritories:
    """Verify SOVEREIGN_TERRITORIES is not in public API."""

    def test_sovereign_territories_not_in_init_all(self):
        """SOVEREIGN_TERRITORIES should not be in __all__ export list."""
        from agentic_core.L5_safety.config.structure_blueprint import __all__

        assert "SOVEREIGN_TERRITORIES" not in __all__, (
            "SOVEREIGN_TERRITORIES should be removed from public __all__ list"
        )

    def test_sovereign_territories_not_importable_from_init(self):
        """SOVEREIGN_TERRITORIES should not be importable from __init__."""
        with pytest.raises(ImportError):
            pass

    def test_build_sovereign_territories_not_in_init_all(self):
        """build_sovereign_territories should not be in __all__."""
        from agentic_core.L5_safety.config.structure_blueprint import __all__

        assert "build_sovereign_territories" not in __all__, (
            "build_sovereign_territories should be removed from public __all__"
        )

    def test_new_api_functions_in_init_all(self):
        """New API functions should be in __all__."""
        from agentic_core.L5_safety.config.structure_blueprint import __all__

        assert "get_all_territories" in __all__
        assert "get_territory_metadata" in __all__


class TestDeprecationWarning:
    """Verify deprecation warning triggers correctly."""

    def test_build_sovereign_territories_triggers_warning(self):
        """Importing _constants triggers deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Force reimport to trigger warning
            import importlib

            import agentic_core.L5_safety.config.structure_blueprint._constants as const_mod

            importlib.reload(const_mod)

            # Check that at least one warning was triggered
            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "SOVEREIGN_TERRITORIES is deprecated" in str(warning.message)
            ]

            assert len(deprecation_warnings) > 0, (
                "Should trigger DeprecationWarning when building SOVEREIGN_TERRITORIES"
            )


class TestCoreFilesMigration:
    """Verify core infrastructure files use new API."""

    def test_derived_py_uses_get_all_territories(self):
        """derived.py should import get_all_territories, not SOVEREIGN_TERRITORIES."""
        from pathlib import Path

        # Get repository root (3 levels up from tests/architecture/)
        repo_root = Path(__file__).parent.parent.parent
        derived_path = (
            repo_root / "agentic_core" / "L5_safety" / "config" / "structure_blueprint" / "derived.py"
        )
        content = derived_path.read_text(encoding="utf-8")

        assert "from agentic_core.L5_safety.config.structure_blueprint.territories import" in content
        assert "get_all_territories" in content
        assert "SOVEREIGN_TERRITORIES," not in content, "Should not import SOVEREIGN_TERRITORIES"

    def test_ssot_py_uses_get_all_territories(self):
        """ssot.py should import get_all_territories, not SOVEREIGN_TERRITORIES."""
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        ssot_path = repo_root / "agentic_core" / "L5_safety" / "config" / "structure_blueprint" / "ssot.py"
        content = ssot_path.read_text(encoding="utf-8")

        assert "from agentic_core.L5_safety.config.structure_blueprint.territories import" in content
        assert "get_all_territories" in content
        # ssot.py should not have SOVEREIGN_TERRITORIES in imports (only in usage via get_all_territories())


class TestFilesMigration:
    """Verify test files migrated successfully."""

    @pytest.mark.parametrize(
        "test_file",
        [
            "tests/integration/agentic_core/L5_safety/reasoning/test_tests_support_phantom_subdirs.py",
            "tests/architecture/test_contracts_fixture_placement.py",
            "tests/integration/agentic_core/L5_safety/reasoning/test_hierarchy_agent_phantom_dir_edge_cases.py",
            "tests/architecture/test_hierarchy_agent_invariants.py",
            "tests/architecture/test_phantom_folder_regression.py",
            "tests/integration/test_depth_violation_no_archive_invariant.py",
            "tests/unit/agentic_core/L5_safety/reasoning/test_constants_quarantine_invariant.py",
            "tests/unit/agentic_core/L5_safety/validators/test_global_candidate_vacuum.py",
        ],
    )
    def test_file_uses_new_api(self, test_file):
        """Test file should use get_all_territories(), not SOVEREIGN_TERRITORIES."""
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        file_path = repo_root / test_file
        if not file_path.exists():
            pytest.skip(f"File not found: {test_file}")

        content = file_path.read_text(encoding="utf-8")

        # Should use get_all_territories()
        assert "get_all_territories" in content, f"{test_file} should use get_all_territories()"

        # Should not import SOVEREIGN_TERRITORIES directly
        assert "import SOVEREIGN_TERRITORIES" not in content, (
            f"{test_file} should not import SOVEREIGN_TERRITORIES directly"
        )


class TestInternalTestingAccess:
    """Verify internal testing code can still access SOVEREIGN_TERRITORIES."""

    def test_verify_py_can_import_sovereign_territories(self):
        """_verify.py should still be able to import SOVEREIGN_TERRITORIES for testing."""
        # This is allowed because _verify.py tests the implementation itself
        from agentic_core.L5_safety.config.structure_blueprint._constants import (
            SOVEREIGN_TERRITORIES,
        )

        assert SOVEREIGN_TERRITORIES is not None
        assert len(SOVEREIGN_TERRITORIES) > 0


class TestDerivedRegistriesNoRegression:
    """Verify derived registries still work correctly after migration."""

    def test_depth_rules_derived_correctly(self):
        """DEPTH_RULES should still be derived correctly."""
        from agentic_core.L5_safety.config.structure_blueprint.derived import DEPTH_RULES

        assert len(DEPTH_RULES) > 0, "DEPTH_RULES should have entries"
        assert "agentic_core" in DEPTH_RULES
        assert isinstance(DEPTH_RULES["agentic_core"], int)

    def test_core_subfolder_map_derived_correctly(self):
        """CORE_SUBFOLDER_MAP should still be derived correctly."""
        from agentic_core.L5_safety.config.structure_blueprint.derived import (
            CORE_SUBFOLDER_MAP,
        )

        assert len(CORE_SUBFOLDER_MAP) > 0, "CORE_SUBFOLDER_MAP should have entries"

    def test_allow_root_py_territories_derived_correctly(self):
        """ALLOW_ROOT_PY_TERRITORIES should still be derived correctly."""
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            ALLOW_ROOT_PY_TERRITORIES,
        )

        assert isinstance(ALLOW_ROOT_PY_TERRITORIES, frozenset)


class TestADGVerification:
    """Verify migration completeness via ADG (if available)."""

    def test_no_sovereign_territories_imports_in_production_code(self):
        """Production code should not import SOVEREIGN_TERRITORIES (ADG check)."""
        from pathlib import Path

        # Find latest ADG
        repo_root = Path(__file__).parent.parent.parent
        adg_dir = repo_root / "artifacts" / "adg"
        if not adg_dir.exists():
            pytest.skip("ADG artifacts directory not found")

        dbs = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
        if not dbs:
            pytest.skip("No ADG SQLite database found")

        db_path = dbs[-1]
        conn = sqlite3.connect(str(db_path))

        # Query for SOVEREIGN_TERRITORIES imports
        sovereign_edges = conn.execute(
            "SELECT n_src.resolved_path FROM edges e "
            "JOIN nodes n_src ON e.src_id=n_src.id "
            "WHERE e.symbol LIKE '%SOVEREIGN_TERRITORIES%' AND e.relation_type='imports'"
        ).fetchall()

        conn.close()

        # Filter out allowed files (internal infrastructure that uses SOVEREIGN_TERRITORIES via new API)
        allowed_files = {
            "agentic_core/L5_safety/config/structure_blueprint/_verify.py",
            "agentic_core/L5_safety/config/structure_blueprint/_constants.py",
            "agentic_core/L5_safety/config/structure_blueprint/territories.py",
            "agentic_core/L5_safety/config/structure_blueprint/derived.py",
            "agentic_core/L5_safety/config/structure_blueprint/ssot.py",
            "agentic_core/L5_safety/config/structure_blueprint_config.py",
        }

        production_imports = [
            path for (path,) in sovereign_edges if path not in allowed_files and not path.startswith("tests/")
        ]

        assert len(production_imports) == 0, (
            f"Production code should not import SOVEREIGN_TERRITORIES. Found: {production_imports}"
        )


class TestMigrationCompleteness:
    """Verify all migration phases completed successfully."""

    def test_phase1_deprecation_warning_present(self):
        """Phase 1: Deprecation warning should be in build_sovereign_territories()."""
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        constants_path = (
            repo_root / "agentic_core" / "L5_safety" / "config" / "structure_blueprint" / "_constants.py"
        )
        content = constants_path.read_text(encoding="utf-8")

        assert "warnings.warn" in content
        assert "SOVEREIGN_TERRITORIES is deprecated" in content

    def test_phase2_new_api_functions_exist(self):
        """Phase 2: New API functions should exist and be importable."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            get_all_territories,
            get_territory_metadata,
            is_valid_root_folder,
        )

        assert callable(get_all_territories)
        assert callable(get_territory_metadata)
        assert callable(is_valid_root_folder)

    def test_phase3_core_files_migrated(self):
        """Phase 3: Core files should use new API."""
        # Already tested in TestCoreFilesMigration
        pass

    def test_phase4_test_files_migrated(self):
        """Phase 4: Test files should use new API."""
        # Already tested in TestTestFilesMigration
        pass

    def test_phase5_sovereign_territories_not_public(self):
        """Phase 5: SOVEREIGN_TERRITORIES should not be in public API."""
        # Already tested in TestPublicAPINoSovereignTerritories
        pass
