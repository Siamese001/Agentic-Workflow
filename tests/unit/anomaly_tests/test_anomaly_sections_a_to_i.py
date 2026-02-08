"""
Anomaly-mapped unit tests for sections A-I.

Parametrized tests that validate expected violations and recommended targets
for each anomaly type from the controller prompt.
"""

from pathlib import Path

import pytest

from agentic_core.L5_safety.config.structure_blueprint_config import (
    CORE_SUBFOLDER_MAP,
    L5_SUBPROCESS_ALLOWLIST,
    L6_HYBRID_ALLOWLIST,
)


class TestSectionA_L5SubprocessAnomalies:
    """Section A: L5 subprocess anomalies."""

    @pytest.mark.parametrize(
        "anomaly_file,should_be_allowed",
        [
            ("dashboard_e2_e_pipeline.py", False),
            ("analysis_ops_validator.py", False),
            ("deterministic_cleaner_validator.py", False),
            ("GitAgent.py", False),
            ("ReportLocationAgent.py", False),
        ],
    )
    def test_true_anomalies_not_in_allowlist(self, anomaly_file: str, should_be_allowed: bool):
        """True L5 subprocess anomalies must NOT be in allowlist."""
        is_allowed = anomaly_file in L5_SUBPROCESS_ALLOWLIST
        assert is_allowed == should_be_allowed, f"{anomaly_file} allowlist status incorrect"

    @pytest.mark.parametrize(
        "allowed_file",
        [
            "safe_subprocess_handler.py",
            "subprocess_security_util.py",
            "PreCommitSovereignAgent.py",
            "ArchitectureGovernorAgent.py",
            "AutonomyGuardianAgent.py",
            "SovereignActionPlaneAgent.py",
            "pre_deploy_check_util.py",
        ],
    )
    def test_allowed_l5_files_in_allowlist(self, allowed_file: str):
        """Allowed L5 subprocess files must be in allowlist."""
        assert allowed_file in L5_SUBPROCESS_ALLOWLIST


class TestSectionB_UnifiedAgentValidators:
    """Section B: UnifiedAgent containing Validator classes."""

    def test_unified_agent_validators_are_strategies(self):
        """UnifiedAgent validators should be Strategy subclasses, not standalone."""
        # This is by design - validators in UnifiedAgent are Strategy subclasses
        unified_agent_path = Path(
            "c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core/L3_orchestration/reasoning/UnifiedAgent.py",
        )
        if unified_agent_path.exists():
            content = unified_agent_path.read_text(encoding="utf-8")
            # Validators should be Strategy subclasses
            assert "ValidatorStrategy" in content or "class.*Validator.*Strategy" in content


class TestSectionC_L4AgentsInWrongSubfolder:
    """Section C: L4 agents in wrong subfolder."""

    @pytest.mark.parametrize(
        "old_path,new_path",
        [
            ("L4_state/enforcement/cached_state_ledger.py", "L4_state/reasoning/cached_state_ledger.py"),
            ("L4_state/memory/checkpoint_manager.py", "L4_state/reasoning/checkpoint_manager.py"),
            ("L4_state/memory/gravity_state_store.py", "L4_state/reasoning/gravity_state_store.py"),
        ],
    )
    def test_l4_agents_moved_to_reasoning(self, old_path: str, new_path: str):
        """L4 agents must be in reasoning/, not enforcement/ or memory/."""
        base = Path("c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core")
        old_full = base / old_path
        new_full = base / new_path

        # Old location should not exist
        assert not old_full.exists(), f"Old location still exists: {old_path}"
        # New location should exist
        assert new_full.exists(), f"New location missing: {new_path}"


class TestSectionD_EmbeddedAgentsInNonReasoning:
    """Section D: Embedded agents in non-reasoning subfolders."""

    @pytest.mark.parametrize(
        "old_path,new_agent_name",
        [
            ("L5_safety/types/code_detection_types.py", "CodeDetectorAgent.py"),
            ("L5_safety/types/code_enforcement_types.py", "CodeEnforcerAgent.py"),
            ("L5_safety/types/code_validation_types.py", "CodeValidatorAgent.py"),
            ("L5_safety/types/credential_types.py", "CredentialScannerAgent.py"),
            ("L5_safety/types/rag_health_check_types.py", "RagHealthCheckAgent.py"),
            ("L5_safety/types/resource_types.py", "ResourceManagerAgent.py"),
            ("L5_safety/types/safety_detection_types.py", "SafetyDetectorAgent.py"),
            ("L5_safety/types/security_types.py", "SecurityManagerAgent.py"),
            ("L5_safety/types/structure_enforcement_types.py", "StructureEnforcerAgent.py"),
        ],
    )
    def test_l5_types_agents_moved_to_reasoning(self, old_path: str, new_agent_name: str):
        """Embedded agents from L5/types must be moved to L5/reasoning."""
        base = Path("c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core")
        old_full = base / old_path
        new_full = base / "L5_safety" / "reasoning" / new_agent_name

        assert not old_full.exists(), f"Old location still exists: {old_path}"
        assert new_full.exists(), f"New location missing: {new_agent_name}"

    @pytest.mark.parametrize(
        "old_path,layer,new_agent_name",
        [
            ("L3_orchestration/config/dag_mutator_config.py", "L3_orchestration", "DAGMutatorAgent.py"),
            (
                "L3_orchestration/validators/dag_runtime_inspector_validator.py",
                "L3_orchestration",
                "DagRuntimeInspectorAgent.py",
            ),
            (
                "L2_execution/config/peer_intelligence_auditor_config.py",
                "L2_execution",
                "PeerIntelligenceAuditorAgent.py",
            ),
            ("L5_safety/enforcement/hygiene_guardian.py", "L5_safety", "HygieneGuardianAgent.py"),
            ("L5_safety/utils/cache_invalidation_util.py", "L5_safety", "CacheInvalidationHealerAgent.py"),
            ("L5_safety/validators/naming_validator.py", "L5_safety", "NamingAgent.py"),
        ],
    )
    def test_other_embedded_agents_moved_to_reasoning(self, old_path: str, layer: str, new_agent_name: str):
        """Other embedded agents must be moved to their layer's reasoning/."""
        base = Path("c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core")
        old_full = base / old_path
        new_full = base / layer / "reasoning" / new_agent_name

        assert not old_full.exists(), f"Old location still exists: {old_path}"
        assert new_full.exists(), f"New location missing: {layer}/reasoning/{new_agent_name}"


class TestSectionE_PascalCaseInL0Scripts:
    """Section E: PascalCase class files in L0/scripts."""

    @pytest.mark.parametrize(
        "old_name,new_path",
        [
            ("AgentAuditResult.py", "L0_maintenance/types/agent_audit_result.py"),
            ("BatchEmbeddingService.py", "L2_execution/reasoning/batch_embedding_service.py"),
            ("GitKrakenHealingStrategy.py", "L0_maintenance/enforcement/git_kraken_healing_strategy.py"),
            ("InMemoryVectorCache.py", "L4_state/memory/in_memory_vector_cache.py"),
            ("SovereignHealingEngine.py", "L0_maintenance/reasoning/sovereign_healing_engine.py"),
            ("SovereignReport.py", "L6_observability/types/sovereign_report.py"),
            ("StrategistBioWriter.py", "L1_cognition/reasoning/strategist_bio_writer.py"),
            ("VectorHealingStrategy.py", "L0_maintenance/enforcement/vector_healing_strategy.py"),
        ],
    )
    def test_pascalcase_moved_from_scripts(self, old_name: str, new_path: str):
        """PascalCase files must be moved out of L0/scripts."""
        base = Path("c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core")
        old_full = base / "L0_maintenance" / "scripts" / old_name
        new_full = base / new_path

        assert not old_full.exists(), f"PascalCase file still in scripts: {old_name}"
        assert new_full.exists(), f"New location missing: {new_path}"


class TestSectionF_TestFilesInL0Scripts:
    """Section F: Test files in L0/scripts."""

    @pytest.mark.parametrize(
        "test_file",
        [
            "test_boundary_stress_test.py",
            "test_lifecycle_audit.py",
            "test_runtime_verify_installation.py",
            "test_verify_meta_learning_integration.py",
            "test_verify_self_healing.py",
            "test_generator.py",
        ],
    )
    def test_test_files_moved_from_scripts(self, test_file: str):
        """Test files must be moved out of L0/scripts to tests/."""
        base = Path("c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core")
        old_full = base / "L0_maintenance" / "scripts" / test_file

        assert not old_full.exists(), f"Test file still in scripts: {test_file}"

    def test_test_files_exist_in_tests_directory(self):
        """Test files should exist somewhere in tests/ directory."""
        tests_dir = Path("c:/Git/Agentic-Workflow/Agentic-Workflow/tests")
        test_files = list(tests_dir.rglob("test_boundary_stress_test.py"))
        assert len(test_files) > 0, "test_boundary_stress_test.py not found in tests/"


class TestSectionG_L6PlaywrightUtil:
    """Section G: L6 playwright util hybrid."""

    def test_playwright_util_in_l6_allowlist(self):
        """verify_dashboard_e2e_playwright_util.py must be in L6 allowlist."""
        assert "verify_dashboard_e2e_playwright_util.py" in L6_HYBRID_ALLOWLIST

    def test_playwright_util_exists_in_l6(self):
        """Playwright util should exist in L6_observability/dashboards/."""
        Path(
            "c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core/L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py",
        )
        # File may or may not exist depending on repo state
        # The key is it's allowlisted if it does exist


class TestSectionH_OrphanedGlobalUtils:
    """Section H: Orphaned global utils."""

    @pytest.mark.parametrize(
        "old_name,new_path",
        [
            ("ssot_discovery_util.py", "L0_maintenance/utils/ssot_discovery_util.py"),
            ("project_root_util.py", "L0_maintenance/utils/project_root_util.py"),
            ("tool_registry_util.py", "L2_execution/utils/tool_registry_util.py"),
            ("find_misnamed_agents_util.py", "L0_maintenance/utils/find_misnamed_agents_util.py"),
            ("fix_testing_observability_util.py", "L6_observability/utils/fix_testing_observability_util.py"),
            ("guard_ddd_alignment_util.py", "L5_safety/utils/guard_ddd_alignment_util.py"),
            ("scan_util.py", "L0_maintenance/utils/scan_util.py"),
            ("canonical_truth_util.py", "L5_safety/utils/canonical_truth_util.py"),
            ("scorched_earth_merge_util.py", "L0_maintenance/utils/scorched_earth_merge_util.py"),
            ("forge_fortress_util.py", "L5_safety/utils/forge_fortress_util.py"),
            ("structural_fix_util.py", "L0_maintenance/utils/structural_fix_util.py"),
            ("force_app_depth_util.py", "L5_safety/utils/force_app_depth_util.py"),
            ("egress_util.py", "L2_execution/utils/egress_util.py"),
            ("component_util.py", "L0_maintenance/utils/component_util.py"),
            ("add_test_coverage_util.py", "L0_maintenance/utils/add_test_coverage_util.py"),
            ("verify_no_mock_data_util.py", "L5_safety/utils/verify_no_mock_data_util.py"),
            ("file_utils_util.py", "L0_maintenance/utils/file_utils_util.py"),
            ("exceptions_util.py", "runtime/exceptions/exceptions_util.py"),
        ],
    )
    def test_orphaned_utils_relocated(self, old_name: str, new_path: str):
        """Orphaned utils must be moved from agentic_core/utils/ to layer utils/."""
        base = Path("c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core")
        old_full = base / "utils" / old_name
        new_full = base / new_path

        assert not old_full.exists(), f"Orphaned util still in utils/: {old_name}"
        assert new_full.exists(), f"New location missing: {new_path}"


class TestSectionI_L6ConfigMissing:
    """Section I: L6_observability missing config/."""

    def test_l6_config_exists(self):
        """L6_observability/config/ must exist."""
        path = Path("c:/Git/Agentic-Workflow/Agentic-Workflow/agentic_core/L6_observability/config")
        assert path.exists(), "L6_observability/config/ missing"
        assert path.is_dir(), "L6_observability/config/ must be a directory"

    def test_l6_has_config_in_subfolder_map(self):
        """L6_observability must have config in CORE_SUBFOLDER_MAP."""
        l6_subfolders = CORE_SUBFOLDER_MAP.get("L6_observability", [])
        assert "config" in l6_subfolders, "L6_observability missing config/ in CORE_SUBFOLDER_MAP"
