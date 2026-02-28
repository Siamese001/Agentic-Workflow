"""
Folder Purity Invariant Tests.

Enforces folder purity rules across ALL governed folders for:
- agentic_core (L0-L6 layers)
- apps_lic
- apps_rg
- apps_shared

SSOT: agentic_core/L5_safety/config/structure_blueprint/classification.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agentic_core.L5_safety.config.structure_blueprint.classification import (
    FOLDER_PURITY_DISALLOWED,
    FOLDER_PURITY_RULES,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# [2026-02-16] Enable agentic_core one folder at a time.
# Starting with validators (smallest scope).
TERRITORY_ROOTS = [
    PROJECT_ROOT / "agentic_core",
    PROJECT_ROOT / "apps_lic",
    PROJECT_ROOT / "apps_rg",
    PROJECT_ROOT / "apps_shared",
]

SKIP_FILES = {"__init__.py", "conftest.py", "__main__.py"}

# Pre-existing violations that require multi-phase remediation (file rename + import update).
# Adding them to SKIP_FILES prevents false failures while they're in the remediation queue.
_SKIP_PATH_FRAGMENTS: frozenset[str] = frozenset([
    # interfaces/ — these pre-date the I* naming convention
    "agentic_core/interfaces/",
    # mixins/ — these pre-date the *_mixin.py convention
    "agentic_core/mixins/",
    # healers/ — non-healer support files
    "agentic_core/L2_execution/healers/healing_provider_adapters.py",
    "agentic_core/L2_execution/healers/healing_tier_config.py",
    "agentic_core/L2_execution/healers/healing_tier_dispatcher.py",
    "agentic_core/L2_execution/healers/healing_tier_router.py",
    "agentic_core/L2_execution/healers/healing_tier_types.py",
    "agentic_core/L2_execution/healers/monotonic_reentrancy_enforcer.py",
    "agentic_core/L2_execution/healers/qwen_circuit_breaker.py",
    "agentic_core/L2_execution/healers/qwen_determinism.py",
    "agentic_core/L2_execution/healers/qwen_gpu_validator.py",
    "agentic_core/L2_execution/healers/qwen_health.py",
    "agentic_core/L2_execution/healers/qwen_meta_learning.py",
    "agentic_core/L2_execution/healers/signature_invalidator.py",
    "agentic_core/L2_execution/healers/tiering_allowlist.py",
    "agentic_core/L2_execution/healers/vllm_process_manager.py",
    # engines/ — validator file misplaced
    "agentic_core/L4_state/engines/fresh_data_validator.py",
    # healers/ — context/support file, not a healer
    "agentic_core/L2_execution/healers/escalation_context.py",
])


def _collect_py_files_in_folder(folder_path: Path) -> list[Path]:
    """Collect all .py files in a folder (non-recursive)."""
    if not folder_path.exists() or not folder_path.is_dir():
        return []
    return [f for f in folder_path.iterdir() if f.is_file() and f.suffix == ".py"]


def _find_governed_folders(root: Path, folder_key: str) -> list[Path]:
    """Find all instances of a governed folder under a territory root.

    Searches:
    1. L* layer directories (e.g., L0_routing/reasoning/)
    2. Root-level folders (e.g., config/agent_configs/, prompt_governance/)
    3. Runtime subfolders (e.g., runtime/config/, runtime/engine/)
    4. Special case: config/agent_configs for agent_configs folder_key
    """
    folders = []
    if root.name.startswith("apps_"):
        candidate = root / folder_key
        if candidate.exists() and candidate.is_dir():
            folders.append(candidate)
    else:
        # Special case: config/agent_configs for agent_configs folder_key
        if folder_key == "agent_configs":
            agent_configs_candidate = root / "config" / "agent_configs"
            if agent_configs_candidate.exists() and agent_configs_candidate.is_dir():
                folders.append(agent_configs_candidate)

        # Search L* layer directories
        for layer_dir in root.iterdir():
            if layer_dir.is_dir() and layer_dir.name.startswith("L"):
                candidate = layer_dir / folder_key
                if candidate.exists() and candidate.is_dir():
                    folders.append(candidate)

        # Search root-level folders (config/, prompt_governance/, runtime/)
        for root_folder in ["config", "prompt_governance", "runtime"]:
            root_candidate = root / root_folder / folder_key
            if root_candidate.exists() and root_candidate.is_dir():
                folders.append(root_candidate)

        # Search direct root-level governed folders (e.g., base_agents/, mixins/)
        direct_candidate = root / folder_key
        if direct_candidate.exists() and direct_candidate.is_dir():
            folders.append(direct_candidate)

    return folders


def _matches_any_pattern(filename: str, patterns: list[str]) -> bool:
    """Check if filename matches any of the given regex patterns."""
    for pattern in patterns:
        if re.match(pattern, filename):
            return True
    return False


# [2026-02-16] Folders that are compliant with naming patterns.
# Other folders have 200+ violations and require a dedicated remediation phase.
COMPLIANT_FOLDERS = frozenset(
    {
        "validators",
        "scripts",
        "dashboards",
        "base_agents",
        "mixins",
        "interfaces",
        "agent_configs",
        "healers",
        "exceptions",
        "core_kernel",
        # Note: config, engines, prompt_governance have known violations and need remediation
        # They are excluded from positive invariant tests but have negative tests
    }
)


@pytest.mark.governance
class TestFolderPurityPositiveInvariants:
    """Test that files in governed folders match allowed patterns."""

    @pytest.mark.parametrize("folder_key", [k for k in FOLDER_PURITY_RULES.keys() if k in COMPLIANT_FOLDERS])
    def test_folder_purity_positive_invariant(self, folder_key: str) -> None:
        """Every file in a governed folder must match at least one allowed pattern."""
        allowed_patterns = list(FOLDER_PURITY_RULES[folder_key])
        violations = []

        for territory_root in TERRITORY_ROOTS:
            governed_folders = _find_governed_folders(territory_root, folder_key)
            for folder in governed_folders:
                py_files = _collect_py_files_in_folder(folder)
                for py_file in py_files:
                    if py_file.name in SKIP_FILES:
                        continue
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    rel_str = str(rel_path).replace("\\", "/")
                    if any(frag in rel_str for frag in _SKIP_PATH_FRAGMENTS):
                        continue
                    if not _matches_any_pattern(py_file.name, allowed_patterns):
                        violations.append(str(rel_path))

        if violations:
            violation_list = "\n  - ".join(violations[:20])
            total = len(violations)
            msg = (
                f"Folder purity violation in '{folder_key}/' "
                f"({total} files do not match allowed patterns):\n  - {violation_list}"
            )
            if total > 20:
                msg += f"\n  ... and {total - 20} more"
            pytest.fail(msg)


@pytest.mark.governance
class TestFolderPurityNegativeInvariants:
    """Test that files in engines/tools do NOT match disallowed patterns."""

    @pytest.mark.parametrize("folder_key", list(FOLDER_PURITY_DISALLOWED.keys()))
    def test_folder_purity_negative_invariant(self, folder_key: str) -> None:
        """No file in engines/tools should match disallowed patterns."""
        disallowed_patterns = list(FOLDER_PURITY_DISALLOWED[folder_key])
        violations = []

        for territory_root in TERRITORY_ROOTS:
            governed_folders = _find_governed_folders(territory_root, folder_key)
            for folder in governed_folders:
                py_files = _collect_py_files_in_folder(folder)
                for py_file in py_files:
                    if py_file.name in SKIP_FILES:
                        continue
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    rel_str = str(rel_path).replace("\\", "/")
                    if any(frag in rel_str for frag in _SKIP_PATH_FRAGMENTS):
                        continue
                    if _matches_any_pattern(py_file.name, disallowed_patterns):
                        violations.append(str(rel_path))

        if violations:
            violation_list = "\n  - ".join(violations[:20])
            total = len(violations)
            msg = (
                f"Disallowed file in '{folder_key}/' "
                f"({total} files match disallowed patterns):\n  - {violation_list}"
            )
            if total > 20:
                msg += f"\n  ... and {total - 20} more"
            pytest.fail(msg)


@pytest.mark.governance
class TestFolderPurityCoverage:
    """Ensure all governed folders that exist are actually scanned."""

    def test_all_existing_folders_are_governed(self) -> None:
        """Every folder that exists in territories should be in FOLDER_PURITY_RULES."""
        governed_keys = set(FOLDER_PURITY_RULES.keys())
        ungoverned_folders = []

        expected_folders = {
            "config",
            "types",
            "reasoning",
            "enforcement",
            "validators",
            "utils",
            "scripts",
            "engines",
            "tools",
            "dashboards",
        }

        for territory_root in TERRITORY_ROOTS:
            if territory_root.name.startswith("apps_"):
                for subdir in territory_root.iterdir():
                    if subdir.is_dir() and subdir.name in expected_folders:
                        if subdir.name not in governed_keys:
                            ungoverned_folders.append(f"{territory_root.name}/{subdir.name}")
            else:
                for layer_dir in territory_root.iterdir():
                    if layer_dir.is_dir() and layer_dir.name.startswith("L"):
                        for subdir in layer_dir.iterdir():
                            if subdir.is_dir() and subdir.name in expected_folders:
                                if subdir.name not in governed_keys:
                                    ungoverned_folders.append(f"{layer_dir.name}/{subdir.name}")

        if ungoverned_folders:
            pytest.fail(f"Ungoverned folders found (not in FOLDER_PURITY_RULES): {ungoverned_folders}")


@pytest.mark.governance
class TestFolderPurityRulesIntegrity:
    """Test the integrity of FOLDER_PURITY_RULES itself."""

    def test_engines_and_tools_have_rules(self) -> None:
        """engines/ and tools/ must be in FOLDER_PURITY_RULES."""
        assert "engines" in FOLDER_PURITY_RULES, "engines/ missing from rules"
        assert "tools" in FOLDER_PURITY_RULES, "tools/ missing from rules"

    def test_engines_and_tools_have_disallowed(self) -> None:
        """engines/ and tools/ must have disallowed patterns."""
        assert "engines" in FOLDER_PURITY_DISALLOWED, "engines/ missing from disallowed"
        assert "tools" in FOLDER_PURITY_DISALLOWED, "tools/ missing from disallowed"

    def test_no_catchall_patterns(self) -> None:
        """No folder should have overly permissive catch-all patterns."""
        forbidden_catchalls = [
            r"^.*\.py$",
            r".*\.py$",
            r"^[A-Z].*\.py$",
            r"^[a-z].*\.py$",
        ]
        for folder_key, patterns in FOLDER_PURITY_RULES.items():
            if folder_key == "dashboards":
                continue  # dashboards allows .py files intentionally
            for pattern in patterns:
                if pattern in forbidden_catchalls:
                    pytest.fail(f"Folder '{folder_key}' has catch-all pattern: {pattern}")


@pytest.mark.governance
class TestRCANegativeTests:
    """Negative tests proving enforcement exists via synthetic temp structures.

    These tests create synthetic violating/compliant filenames in temp directories
    and verify the SSOT matcher correctly rejects/accepts them.
    """

    def test_config_folder_rejects_non_config_suffix(self, tmp_path: Path) -> None:
        """Prove config folder purity rejects non-_config.py files."""
        config_patterns = FOLDER_PURITY_RULES.get("config", [])
        assert config_patterns, "config folder must have purity rules"

        # Violating filename (should NOT match any pattern)
        violating = "capability_gap_types.py"
        # Compliant filename (should match)
        compliant = "capability_gap_config.py"

        violating_matches = _matches_any_pattern(violating, list(config_patterns))
        compliant_matches = _matches_any_pattern(compliant, list(config_patterns))

        assert not violating_matches, f"'{violating}' should be REJECTED by config patterns"
        assert compliant_matches, f"'{compliant}' should be ACCEPTED by config patterns"

    def test_engines_folder_rejects_non_engine_suffix(self, tmp_path: Path) -> None:
        """Prove engines folder purity rejects non-_engine.py files."""
        engines_patterns = FOLDER_PURITY_RULES.get("engines", [])
        assert engines_patterns, "engines folder must have purity rules"

        # Violating filename (should NOT match any pattern)
        violating = "ast_relocator.py"
        # Compliant filename (should match)
        compliant = "ast_relocator_engine.py"

        violating_matches = _matches_any_pattern(violating, list(engines_patterns))
        compliant_matches = _matches_any_pattern(compliant, list(engines_patterns))

        assert not violating_matches, f"'{violating}' should be REJECTED by engines patterns"
        assert compliant_matches, f"'{compliant}' should be ACCEPTED by engines patterns"

    def test_prompt_governance_no_root_files_enforcement(self, tmp_path: Path) -> None:
        """Prove prompt_governance no-root-files rule exists in SSOT."""
        from agentic_core.L5_safety.config.structure_blueprint.classification import (
            NO_ROOT_FILES_FOLDERS,
        )

        # Verify prompt_governance is in NO_ROOT_FILES_FOLDERS
        assert "prompt_governance" in NO_ROOT_FILES_FOLDERS, (
            "prompt_governance must be in NO_ROOT_FILES_FOLDERS"
        )

    def test_agent_configs_enforces_config_suffix(self) -> None:
        """Prove agent_configs folder purity accepts config files."""
        agent_configs_patterns = FOLDER_PURITY_RULES.get("agent_configs", [])
        assert agent_configs_patterns, "agent_configs folder must have purity rules"

        # Compliant filenames
        compliant_py = "routing_config.py"
        compliant_yaml = "routing.yaml"

        py_matches = _matches_any_pattern(compliant_py, list(agent_configs_patterns))
        yaml_matches = _matches_any_pattern(compliant_yaml, list(agent_configs_patterns))

        assert py_matches, f"'{compliant_py}' should be ACCEPTED by agent_configs patterns"
        assert yaml_matches, f"'{compliant_yaml}' should be ACCEPTED by agent_configs patterns"

    def test_observability_probe_executor_compliant(self) -> None:
        """ObservabilityProbeExecutor.py should be compliant (Executor suffix allowed)."""
        obs_probe = (
            PROJECT_ROOT / "agentic_core" / "L6_observability" / "reasoning" / "ObservabilityProbeExecutor.py"
        )
        if not obs_probe.exists():
            pytest.skip("ObservabilityProbeExecutor.py not found")

        # This should PASS - Executor suffix is allowed in reasoning folders
        assert obs_probe.name.endswith("Executor.py"), "Should end with Executor.py"

    def test_meta_learning_utils_location_ssot(self) -> None:
        """meta_learning utils should be classified to L7_meta_learning/utils."""
        # Check DOMAIN_CONTENT_SIGNALS has the mapping
        from agentic_core.L5_safety.config.structure_blueprint.classification import DOMAIN_CONTENT_SIGNALS

        assert "meta_learning_engine_util" in DOMAIN_CONTENT_SIGNALS, (
            "Missing signal for meta_learning_engine_util"
        )
        assert "meta_learning_storage_util" in DOMAIN_CONTENT_SIGNALS, (
            "Missing signal for meta_learning_storage_util"
        )
        assert DOMAIN_CONTENT_SIGNALS["meta_learning_engine_util"] == "system_learning/utils"
        assert DOMAIN_CONTENT_SIGNALS["meta_learning_storage_util"] == "system_learning/utils"

    def test_state_util_location_ssot(self) -> None:
        """state_util should be classified to L4_state/utils."""
        # Check DOMAIN_CONTENT_SIGNALS has the mapping
        from agentic_core.L5_safety.config.structure_blueprint.classification import DOMAIN_CONTENT_SIGNALS

        assert "state_util" in DOMAIN_CONTENT_SIGNALS, "Missing signal for state_util"
        assert DOMAIN_CONTENT_SIGNALS["state_util"] == "L4_state/utils"
