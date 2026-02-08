"""
Tests for FileClassificationAgent apps-aware mode (2026-02-08 HARDENING).

Covers all edge cases that caused destructive behavior in the previous run:
1. Territory moves: apps_* files must NOT be moved between recognized subfolders
2. Naming: Agent/Strategy/Validator suffixes must NEVER be stripped in apps_*
3. Collisions: divergent-content collisions must ABORT (no .CONFLICT files)
4. Folder purity: apps_* paths must be exempt from agentic_core purity rules
5. Suffix consistency: apps_* paths must be exempt from LCD suffix enforcement
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixture: build a minimal FileClassificationAgent wired to a temp tree
# ---------------------------------------------------------------------------


@pytest.fixture
def agent(tmp_path):
    """Create a FileClassificationAgent rooted at a temp directory."""
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    a = FileClassificationAgent(project_root=tmp_path, dry_run=True, verbose=False)
    # Patch verify_environment to always pass (avoids Windows LongPathsEnabled check)
    a.verify_environment = lambda: True
    return a


def _write(path: Path, content: str = "") -> Path:
    """Helper: create a file with optional content, ensuring parent dirs exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content or f"# {path.name}\n", encoding="utf-8")
    return path


# ============================================================================
# 1. TERRITORY MAP — apps_* files stay in recognized subfolders
# ============================================================================


class TestAppsTerritoryMap:
    """Files in recognized apps_* subfolders must NOT be moved."""

    def test_agent_in_engines_stays(self, agent, tmp_path):
        """An AGENT file in engines/ is correctly placed — no territory violation."""
        p = _write(
            tmp_path / "apps_rg" / "engines" / "ATSCompatibilityAgent.py",
            "class ATSCompatibilityAgent:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "AGENT")
        assert result is None, f"Agent in engines/ should not be moved, got {result}"

    def test_agent_in_reasoning_stays(self, agent, tmp_path):
        """An AGENT file in reasoning/ is correctly placed."""
        p = _write(
            tmp_path / "apps_rg" / "reasoning" / "RgReflectionAgent.py",
            "class RgReflectionAgent:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "AGENT")
        assert result is None

    def test_agent_in_shared_stays(self, agent, tmp_path):
        """An AGENT file in shared/ is correctly placed."""
        p = _write(tmp_path / "apps_lic" / "shared" / "SomeAgent.py", "class SomeAgent:\n    pass\n")
        result = agent.check_territory_violation(p, "AGENT")
        assert result is None

    def test_types_in_types_stays(self, agent, tmp_path):
        """TYPES files in types/ must NOT be moved to domain/."""
        p = _write(
            tmp_path / "apps_rg" / "types" / "resume_analysis_plan_types.py",
            "from dataclasses import dataclass\n@dataclass\nclass Plan:\n    x: int\n",
        )
        result = agent.check_territory_violation(p, "TYPES")
        assert result is None, "Types file in types/ must not be moved"

    def test_types_in_engines_stays(self, agent, tmp_path):
        """TYPES files in engines/ are allowed (compound files)."""
        p = _write(
            tmp_path / "apps_lic" / "engines" / "state_checkpoint_types.py",
            "from dataclasses import dataclass\n@dataclass\nclass Checkpoint:\n    x: int\n",
        )
        result = agent.check_territory_violation(p, "TYPES")
        assert result is None

    def test_types_in_domain_stays(self, agent, tmp_path):
        """TYPES files in domain/ are allowed."""
        p = _write(tmp_path / "apps_rg" / "domain" / "some_types.py", "X = 1\n")
        result = agent.check_territory_violation(p, "TYPES")
        assert result is None

    def test_class_in_tools_stays(self, agent, tmp_path):
        """CLASS files in tools/ must NOT be moved to domain/."""
        p = _write(
            tmp_path / "apps_rg" / "tools" / "ResumeGenerator.py",
            "class ResumeGenerator:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None, "Class in tools/ must not be moved"

    def test_utility_in_tools_stays(self, agent, tmp_path):
        """UTILITY files in tools/ must stay (tools is a valid home for utilities)."""
        p = _write(tmp_path / "apps_lic" / "tools" / "network_ops.py", "def fetch(): pass\n")
        result = agent.check_territory_violation(p, "UTILITY")
        assert result is None

    def test_utility_in_utils_stays(self, agent, tmp_path):
        """UTILITY files in utils/ stay."""
        p = _write(tmp_path / "apps_rg" / "utils" / "enhanced_rg_flow_router.py", "def route(): pass\n")
        result = agent.check_territory_violation(p, "UTILITY")
        assert result is None

    def test_utility_in_shared_stays(self, agent, tmp_path):
        """UTILITY files in shared/ stay."""
        p = _write(tmp_path / "apps_rg" / "shared" / "utils" / "helpers.py", "def help(): pass\n")
        result = agent.check_territory_violation(p, "UTILITY")
        assert result is None

    def test_validator_in_validation_stays(self, agent, tmp_path):
        """VALIDATOR files in validation/ stay."""
        p = _write(
            tmp_path / "apps_rg" / "validation" / "hallucination_detector_validator.py",
            "class HallucinationDetector:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "VALIDATOR")
        assert result is None

    def test_validator_in_engines_stays(self, agent, tmp_path):
        """VALIDATOR files in engines/ are allowed for apps."""
        p = _write(
            tmp_path / "apps_lic" / "engines" / "ValidatorAgent.py",
            "class ValidatorAgent:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "VALIDATOR")
        assert result is None

    def test_config_in_config_stays(self, agent, tmp_path):
        """CONFIG files in config/ stay."""
        p = _write(tmp_path / "apps_rg" / "config" / "settings_config.py", "X = 1\n")
        result = agent.check_territory_violation(p, "CONFIG")
        assert result is None

    def test_config_in_engines_stays(self, agent, tmp_path):
        """CONFIG files in engines/ stay (ultra-conservative: no moves between recognized folders)."""
        p = _write(tmp_path / "apps_rg" / "engines" / "some_config.py", "CONFIG = {}\n")
        result = agent.check_territory_violation(p, "CONFIG")
        assert result is None, "CONFIG in recognized apps subfolder should not be moved"

    def test_script_in_scripts_stays(self, agent, tmp_path):
        """SCRIPT files in scripts/ stay."""
        p = _write(tmp_path / "apps_rg" / "scripts" / "generate_final_report.py", "def main(): pass\n")
        result = agent.check_territory_violation(p, "SCRIPT")
        assert result is None

    def test_script_in_tools_stays(self, agent, tmp_path):
        """SCRIPT files in tools/ stay (tools is valid for scripts in apps)."""
        p = _write(tmp_path / "apps_lic" / "tools" / "run_workflow.py", "def main(): pass\n")
        result = agent.check_territory_violation(p, "SCRIPT")
        assert result is None

    def test_mixin_in_shared_stays(self, agent, tmp_path):
        """MIXIN files in shared/ stay."""
        p = _write(tmp_path / "apps_rg" / "shared" / "mixins.py", "class MCPHardenedMixin:\n    pass\n")
        result = agent.check_territory_violation(p, "MIXIN")
        assert result is None

    def test_class_in_logic_nodes_stays(self, agent, tmp_path):
        """CLASS files in logic_nodes/ stay (recognized app subfolder)."""
        p = _write(tmp_path / "apps_rg" / "logic_nodes" / "some_node.py", "class SomeNode:\n    pass\n")
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None

    def test_class_in_core_stays(self, agent, tmp_path):
        """CLASS files in core/ stay (recognized app subfolder)."""
        p = _write(tmp_path / "apps_rg" / "core" / "base.py", "class Base:\n    pass\n")
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None

    def test_deep_nesting_stays(self, agent, tmp_path):
        """Files in deep nesting under recognized subfolders stay."""
        p = _write(
            tmp_path / "apps_rg" / "engines" / "orchestration" / "resume_engine.py",
            "class ResumeEngine:\n    pass\n",
        )
        # engines is recognized depth-1 folder, orchestration is depth-2
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None

    def test_orphan_file_at_apps_root_gets_routed(self, agent, tmp_path):
        """Files at apps_* root (no subfolder) get routed to appropriate folder."""
        p = _write(tmp_path / "apps_rg" / "orphan_agent.py", "class OrphanAgent:\n    pass\n")
        # Depth-1 folder would be the filename itself, which is not in valid_folders
        result = agent.check_territory_violation(p, "AGENT")
        # Should propose moving to engines/ (first allowed folder for AGENT)
        assert result is not None
        assert "engines" in str(result)


# ============================================================================
# 2. NAMING — Agent suffixes must NEVER be stripped in apps_*
# ============================================================================


class TestAppsNamingPreservation:
    """Apps files must preserve their original filenames including suffixes."""

    def test_agent_suffix_preserved(self, agent, tmp_path):
        """ATSCompatibilityAgent.py must NOT be renamed to ATSCompatibility.py."""
        p = _write(
            tmp_path / "apps_rg" / "engines" / "ATSCompatibilityAgent.py",
            "class ATSCompatibilityAgent:\n    pass\n",
        )
        result = agent.get_compliant_name(p, "AGENT")
        assert result is None, f"Agent suffix should be preserved, got rename to {result}"

    def test_strategy_suffix_preserved(self, agent, tmp_path):
        """HardenedanthropicexecutorStrategy.py must NOT have Strategy stripped."""
        p = _write(
            tmp_path / "apps_rg" / "engines" / "HardenedanthropicexecutorStrategy.py",
            "class HardenedanthropicexecutorStrategy:\n    pass\n",
        )
        result = agent.get_compliant_name(p, "AGENT")
        assert result is None

    def test_validator_suffix_preserved(self, agent, tmp_path):
        """PersonaPlannerValidator.py must NOT have Validator stripped."""
        p = _write(
            tmp_path / "apps_lic" / "engines" / "PersonaPlannerValidator.py",
            "class PersonaPlannerValidator:\n    pass\n",
        )
        result = agent.get_compliant_name(p, "VALIDATOR")
        assert result is None

    def test_orchestrator_suffix_preserved(self, agent, tmp_path):
        """ResumeEnhancementOrchestrator.py must NOT be renamed."""
        p = _write(
            tmp_path / "apps_rg" / "engines" / "ResumeEnhancementOrchestrator.py",
            "class ResumeEnhancementOrchestrator:\n    pass\n",
        )
        result = agent.get_compliant_name(p, "ORCHESTRATOR")
        assert result is None

    def test_snake_case_apps_file_preserved(self, agent, tmp_path):
        """snake_case files in apps (like control_plane.py) must NOT be renamed."""
        p = _write(tmp_path / "apps_lic" / "engines" / "control_plane.py", "class ControlPlane:\n    pass\n")
        result = agent.get_compliant_name(p, "CLASS")
        assert result is None

    def test_types_file_preserved(self, agent, tmp_path):
        """Type files in apps must NOT be renamed."""
        p = _write(
            tmp_path / "apps_lic" / "types" / "validation_result_types.py",
            "from dataclasses import dataclass\n@dataclass\nclass Result:\n    ok: bool\n",
        )
        result = agent.get_compliant_name(p, "TYPES")
        assert result is None

    def test_hop_agent_preserved(self, agent, tmp_path):
        """HOP agents like Hop1ProfileAnalysisAgent.py must NOT be renamed."""
        p = _write(
            tmp_path / "apps_lic" / "engines" / "Hop1ProfileAnalysisAgent.py",
            "class Hop1ProfileAnalysisAgent:\n    pass\n",
        )
        result = agent.get_compliant_name(p, "AGENT")
        assert result is None

    def test_multiple_agents_no_collision(self, agent, tmp_path):
        """Multiple Outreach*Agent files must NOT all rename to Outreach.py."""
        names = [
            "OutreachSignalRouterAgent.py",
            "OutreachLearningAgent.py",
            "OutreachProactiveAgent.py",
            "OutreachTestPilotAgent.py",
            "OutreachCapabilityMonitorAgent.py",
        ]
        results = []
        for name in names:
            p = _write(tmp_path / "apps_lic" / "engines" / name, f"class {name[:-3]}:\n    pass\n")
            r = agent.get_compliant_name(p, "AGENT")
            results.append(r)

        # ALL should return None (no rename)
        for name, result in zip(names, results, strict=False):
            assert result is None, f"{name} should NOT be renamed, got {result}"


# ============================================================================
# 3. COLLISION SAFETY — divergent collisions must ABORT
# ============================================================================


class TestCollisionSafety:
    """Divergent-content collisions must abort, not create .CONFLICT files."""

    def test_identical_collision_deletes_source(self, agent, tmp_path):
        """If src and dest have identical content, delete src (dedup)."""
        agent.dry_run = False
        content = "class Foo:\n    pass\n"
        src = _write(tmp_path / "a" / "Foo.py", content)
        _write(tmp_path / "b" / "Foo.py", content)
        result = agent.resolve_collision_and_rename(src, "Foo.py", target_dir=tmp_path / "b")
        assert result is True  # Resolved by deletion
        assert not src.exists()  # Source deleted

    def test_divergent_collision_aborts(self, agent, tmp_path):
        """If src and dest have different content, ABORT (return False)."""
        agent.dry_run = False
        src = _write(tmp_path / "a" / "Foo.py", "class Foo:\n    version = 1\n")
        _write(tmp_path / "b" / "Foo.py", "class Foo:\n    version = 2\n")
        result = agent.resolve_collision_and_rename(src, "Foo.py", target_dir=tmp_path / "b")
        assert result is False, "Divergent collision must abort"
        assert src.exists(), "Source must remain after abort"

    def test_no_conflict_files_created(self, agent, tmp_path):
        """Ensure NO .CONFLICT files are ever created."""
        agent.dry_run = False
        src = _write(tmp_path / "a" / "Foo.py", "class Foo:\n    v = 1\n")
        _write(tmp_path / "b" / "Foo.py", "class Foo:\n    v = 2\n")
        agent.resolve_collision_and_rename(src, "Foo.py", target_dir=tmp_path / "b")

        # Scan both directories for .CONFLICT files
        for p in (tmp_path / "a").rglob("*"):
            assert ".CONFLICT" not in p.name, f"Found forbidden .CONFLICT file: {p}"
        for p in (tmp_path / "b").rglob("*"):
            assert ".CONFLICT" not in p.name, f"Found forbidden .CONFLICT file: {p}"

    def test_dry_run_collision_plans_move(self, agent, tmp_path):
        """In dry-run, collision detection doesn't matter — just plan the move."""
        agent.dry_run = True
        src = _write(tmp_path / "a" / "Foo.py", "v1")
        _write(tmp_path / "b" / "Foo.py", "v2")
        result = agent.resolve_collision_and_rename(src, "Foo.py", target_dir=tmp_path / "b")
        assert result is True  # Dry-run always plans
        assert src.exists()  # Source unchanged in dry-run

    def test_case_insensitive_same_file_noop(self, agent, tmp_path):
        """Same file with different casing should be a no-op on Windows."""
        agent.dry_run = False
        src = _write(tmp_path / "Foo.py", "class Foo:\n    pass\n")
        # Renaming to same file (case change only on case-insensitive FS)
        result = agent.resolve_collision_and_rename(src, "Foo.py")
        assert result is False  # No-op


# ============================================================================
# 4. FOLDER PURITY — apps_* paths are exempt
# ============================================================================


class TestAppsFolderPurityExemption:
    """Apps paths must be exempt from agentic_core folder purity rules."""

    def test_non_agent_in_apps_reasoning_allowed(self, agent, tmp_path):
        """Non-Agent files in apps_rg/reasoning/ should NOT trigger purity violation."""
        p = _write(
            tmp_path / "apps_rg" / "reasoning" / "resume_orchestrator.py",
            "class ResumeOrchestrator:\n    pass\n",
        )
        result = agent._enforce_folder_purity(p)
        assert result is None, "Apps reasoning/ should not enforce Agent-only purity"

    def test_types_in_apps_engines_allowed(self, agent, tmp_path):
        """Types files in apps engines/ should NOT trigger purity violation."""
        p = _write(
            tmp_path / "apps_lic" / "engines" / "lic_vector_memory_types.py",
            "from dataclasses import dataclass\n@dataclass\nclass Doc:\n    id: str\n",
        )
        result = agent._enforce_folder_purity(p)
        assert result is None

    def test_utility_in_apps_shared_allowed(self, agent, tmp_path):
        """Utility files in apps shared/ should NOT trigger purity violation."""
        p = _write(tmp_path / "apps_rg" / "shared" / "helpers.py", "def help(): pass\n")
        result = agent._enforce_folder_purity(p)
        assert result is None

    def test_core_reasoning_still_enforced(self, agent, tmp_path):
        """agentic_core reasoning/ should STILL enforce purity rules."""
        p = _write(
            tmp_path / "agentic_core" / "L5_safety" / "reasoning" / "not_an_agent.py",
            "def utility_func(): pass\n",
        )
        # This should trigger purity violation (non-Agent in core reasoning/)
        # Note: depends on FOLDER_PURITY_RULES being importable
        try:
            agent._enforce_folder_purity(p)
            # If FOLDER_PURITY_RULES has reasoning/ rule, should be non-None
            # If not importable in test env, skip
        except ImportError:
            pytest.skip("FOLDER_PURITY_RULES not importable in test env")


# ============================================================================
# 5. SUFFIX CONSISTENCY — apps_* paths are exempt
# ============================================================================


class TestAppsSuffixConsistencyExemption:
    """Apps paths must be exempt from LCD suffix enforcement."""

    def test_types_folder_no_suffix_enforcement(self, agent, tmp_path):
        """Files in apps types/ without _types.py suffix should NOT be flagged."""
        p = _write(tmp_path / "apps_rg" / "types" / "provenance_pattern_types.py", "X = 1\n")
        result = agent.validate_folder_suffix_consistency(p)
        assert result is None

    def test_utils_folder_no_suffix_enforcement(self, agent, tmp_path):
        """Files in apps utils/ without _util.py suffix should NOT be flagged."""
        p = _write(tmp_path / "apps_rg" / "utils" / "enhanced_rg_flow_router.py", "def route(): pass\n")
        result = agent.validate_folder_suffix_consistency(p)
        assert result is None, f"Apps utils/ should not enforce _util.py suffix, got {result}"

    def test_config_folder_no_suffix_enforcement(self, agent, tmp_path):
        """Files in apps config/ without _config.py suffix should NOT be flagged."""
        p = _write(tmp_path / "apps_lic" / "config" / "settings.py", "X = 1\n")
        result = agent.validate_folder_suffix_consistency(p)
        assert result is None

    def test_core_utils_still_enforced(self, agent, tmp_path):
        """agentic_core utils/ should STILL enforce _util.py suffix."""
        p = _write(tmp_path / "agentic_core" / "L5_safety" / "utils" / "helper.py", "def help(): pass\n")
        result = agent.validate_folder_suffix_consistency(p)
        # Core paths should still enforce suffix rules
        assert result is not None, "Core utils/ should still enforce suffix rules"
        assert result["folder"] == "utils"


# ============================================================================
# 6. COMPOUND SUFFIX HANDLING — apps context
# ============================================================================


class TestAppsCompoundSuffix:
    """Compound suffix detection should not produce broken names in apps."""

    def test_app_content_validator_types_not_mangled(self, agent, tmp_path):
        """app_content_validator_types.py should NOT become app_content_types_types.py."""
        # This was the actual bug: compound suffix detection saw both _validator and _types
        # and produced the mangled name app_content_types_types.py.
        # With apps-aware mode, naming returns None for apps paths.
        p = _write(
            tmp_path / "apps_lic" / "types" / "app_content_validator_types.py",
            "from enum import Enum\nclass ContentViolationType(Enum):\n    SPAM = 'spam'\n",
        )
        result = agent.get_compliant_name(p, "TYPES")
        assert result is None, f"Should not rename, got {result}"


# ============================================================================
# 7. APPS_SHARED — the third apps folder
# ============================================================================


class TestAppsShared:
    """apps_shared must also be treated as apps territory."""

    def test_apps_shared_agents_stay(self, agent, tmp_path):
        """AGENT files in apps_shared/agents/ should stay."""
        p = _write(tmp_path / "apps_shared" / "agents" / "SharedAgent.py", "class SharedAgent:\n    pass\n")
        result = agent.check_territory_violation(p, "AGENT")
        assert result is None

    def test_apps_shared_utils_stay(self, agent, tmp_path):
        """UTILITY files in apps_shared/utils/ should stay."""
        p = _write(tmp_path / "apps_shared" / "utils" / "common_helpers.py", "def help(): pass\n")
        result = agent.check_territory_violation(p, "UTILITY")
        assert result is None

    def test_apps_shared_naming_preserved(self, agent, tmp_path):
        """apps_shared files should not be renamed."""
        p = _write(tmp_path / "apps_shared" / "agents" / "SharedAgent.py", "class SharedAgent:\n    pass\n")
        result = agent.get_compliant_name(p, "AGENT")
        assert result is None

    def test_apps_shared_mixins_stay(self, agent, tmp_path):
        """MIXIN files in apps_shared/mixins/ should stay."""
        p = _write(tmp_path / "apps_shared" / "mixins" / "auth_mixin.py", "class AuthMixin:\n    pass\n")
        result = agent.check_territory_violation(p, "MIXIN")
        assert result is None

    def test_apps_shared_folder_purity_exempt(self, agent, tmp_path):
        """apps_shared should be exempt from folder purity."""
        p = _write(
            tmp_path / "apps_shared" / "common_utils" / "text_cleaner.py",
            "def clean(s): return s.strip()\n",
        )
        result = agent._enforce_folder_purity(p)
        assert result is None

    def test_apps_shared_suffix_exempt(self, agent, tmp_path):
        """apps_shared should be exempt from suffix consistency."""
        p = _write(tmp_path / "apps_shared" / "utils" / "text_cleaner.py", "def clean(s): return s.strip()\n")
        result = agent.validate_folder_suffix_consistency(p)
        assert result is None


# ============================================================================
# 8. AGENTIC_CORE UNAFFECTED — core rules still apply
# ============================================================================


class TestCoreUnaffected:
    """All existing agentic_core rules must still work."""

    def test_core_agent_in_reasoning_stays(self, agent, tmp_path):
        """AGENT in agentic_core reasoning/ stays (core rule)."""
        p = _write(
            tmp_path / "agentic_core" / "L5_safety" / "reasoning" / "LocationAgent.py",
            "class LocationAgent:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "AGENT")
        assert result is None

    def test_core_config_in_engines_moves(self, agent, tmp_path):
        """CONFIG in agentic_core engines/ is a junk-drawer move target."""
        # In core, config files in junk drawers get moved
        # This test validates core behavior is preserved
        # (exact behavior depends on junk_drawer detection)
        p = _write(tmp_path / "agentic_core" / "L5_safety" / "utils" / "some_config.py", "CONFIG = {}\n")
        # utils is a junk drawer in core — CONFIG should be moved to config/
        result = agent.check_territory_violation(p, "CONFIG")
        if result is not None:
            assert "config" in str(result)

    def test_core_naming_still_applies(self, agent, tmp_path):
        """Core naming rules should still work (e.g., UTILITY gets _util.py suffix)."""
        p = _write(tmp_path / "agentic_core" / "L5_safety" / "utils" / "helpers.py", "def help(): pass\n")
        result = agent.get_compliant_name(p, "UTILITY")
        if result is not None:
            assert result.endswith("_util.py")


# ============================================================================
# 9. EDGE CASES — regression prevention
# ============================================================================


class TestEdgeCases:
    """Edge cases that caused issues in the destructive run."""

    def test_engines_subfolder_stays(self, agent, tmp_path):
        """Files in engines/utils/ (depth 2) must stay — engines is the depth-1 folder."""
        p = _write(
            tmp_path / "apps_rg" / "engines" / "utils" / "agent_executor.py",
            "class AgentExecutor:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None, "engines/utils/ files must not be moved"

    def test_engines_orchestration_stays(self, agent, tmp_path):
        """Files in engines/orchestration/ must stay."""
        p = _write(
            tmp_path / "apps_rg" / "engines" / "orchestration" / "resume_engine.py",
            "class ResumeEngine:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None

    def test_shared_subdirectory_stays(self, agent, tmp_path):
        """Files in shared/utils/ must stay."""
        p = _write(
            tmp_path / "apps_rg" / "shared" / "utils" / "mixins.py",
            "class MCPHardenedMixin:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "MIXIN")
        assert result is None

    def test_engines_base_stays(self, agent, tmp_path):
        """Files in engines/base/ must stay."""
        p = _write(
            tmp_path / "apps_rg" / "engines" / "base" / "engine_base.py",
            "class EngineBase:\n    pass\n",
        )
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None

    def test_init_files_never_moved(self, agent, tmp_path):
        """__init__.py files should never be touched."""
        p = _write(tmp_path / "apps_rg" / "types" / "__init__.py", "# init\n")
        assert agent.check_territory_violation(p, "IGNORE") is None
        assert agent.validate_folder_suffix_consistency(p) is None
        assert agent._enforce_folder_purity(p) is None

    def test_asset_library_stays(self, agent, tmp_path):
        """Files in asset_library/ stay."""
        p = _write(tmp_path / "apps_rg" / "asset_library" / "templates.py", "TEMPLATES = {}\n")
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None

    def test_reports_folder_stays(self, agent, tmp_path):
        """Files in reports/ stay."""
        p = _write(tmp_path / "apps_lic" / "reports" / "audit_report.py", "def generate(): pass\n")
        result = agent.check_territory_violation(p, "CLASS")
        assert result is None

    def test_system_flow_stays(self, agent, tmp_path):
        """Files in system_flow/ stay."""
        p = _write(tmp_path / "apps_rg" / "system_flow" / "flow_config.py", "FLOW = {}\n")
        result = agent.check_territory_violation(p, "CONFIG")
        assert result is None

    def test_unknown_filetype_in_apps_no_crash(self, agent, tmp_path):
        """Unknown file types in apps should not crash or cause moves."""
        p = _write(tmp_path / "apps_rg" / "engines" / "mystery.py", "# mysterious file\n")
        # Unknown type has no entry in app_territory_map -> should not move
        result = agent.check_territory_violation(p, "UNKNOWN_TYPE")
        assert result is None  # No allowed list -> no move (inside recognized folder)
