"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  CLASSIFICATION KERNEL CONTRACT TESTS — Golden Set                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  These tests lock the 19-priority queue behavior of the classification     ║
║  kernel. Any change to classification logic must pass ALL golden cases.    ║
║                                                                            ║
║  SSOT: agentic_core/core/classification_kernel.py                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pathlib import Path

import pytest

from agentic_core.core.classification_kernel import (
    FileType,
    classify_file_standalone,
    is_agent_file,
    is_agent_or_orchestrator,
)

# ============================================================================
# PROJECT ROOT — resolved once for all tests
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# ============================================================================
# GOLDEN SET — parametrized file paths and their expected FileType
# ============================================================================
#
# Each entry is (relative_path, expected_FileType).
# These files MUST exist in the repo. If a file is renamed or deleted,
# update this golden set immediately.

GOLDEN_SET: list[tuple[str, FileType]] = [
    # --- PRIORITY 0: IGNORE (critical infrastructure) ---
    ("agentic_core/core/__init__.py", "IGNORE"),
    ("tests/conftest.py", "IGNORE"),  # conftest is critical ignore, not TEST
    # --- PRIORITY 1: CLASS (base_agents/ directory) ---
    ("agentic_core/base_agents/SovereignBaseAgent.py", "CLASS"),
    # --- PRIORITY 5: UTILITY (no classes, no __main__) ---
    ("agentic_core/core/classification_kernel.py", "UTILITY"),
    # --- PRIORITY 6: EXCEPTION ---
    ("agentic_core/L2_execution/types/mcp_error_types.py", "EXCEPTION"),
    # --- PRIORITY 7: MIXIN ---
    ("agentic_core/mixins/healer_mixin.py", "MIXIN"),
    ("agentic_core/mixins/circuit_breaker_mixin.py", "MIXIN"),
    # --- PRIORITY 8: PROTOCOL ---
    ("agentic_core/interfaces/IHealerProtocol.py", "PROTOCOL"),
    ("agentic_core/interfaces/IOrchestratorProtocol.py", "PROTOCOL"),
    # --- PRIORITY 9: ORCHESTRATOR ---
    ("agentic_core/knowledge/engine/rag_orchestrator.py", "ORCHESTRATOR"),
    # --- PRIORITY 10: AGENT ---
    ("agentic_core/L5_safety/reasoning/FileClassificationAgent.py", "AGENT"),
    ("agentic_core/L5_safety/reasoning/LocationHealerAgent.py", "AGENT"),
    ("agentic_core/L5_safety/reasoning/HierarchyAgent.py", "AGENT"),
    ("apps_lic/engines/CampaignBalanceAgent.py", "AGENT"),
    # --- PRIORITY 11: STRATEGY ---
    ("agentic_core/L0_maintenance/enforcement/audit_healing_strategy.py", "STRATEGY"),
    # --- PRIORITY 12: ADAPTER ---
    ("agentic_core/L4_state/utils/local_disk_adapter.py", "ADAPTER"),
    # --- PRIORITY 14: CONFIG ---
    ("agentic_core/L5_safety/config/structure_blueprint_config.py", "CONFIG"),
    # --- PRIORITY 15: VALIDATOR ---
    ("agentic_core/L1_cognition/validators/consensus_validator.py", "VALIDATOR"),
    # --- PRIORITY 16: FACTORY ---
    ("agentic_core/runtime/enforcement/envelope_factory.py", "FACTORY"),
    # --- PRIORITY 4: SCRIPT ---
    ("agentic_core/L0_maintenance/scripts/add_agent_suffix_plan_util.py", "SCRIPT"),
]


# ============================================================================
# CONTRACT: classify_file_standalone returns expected FileType
# ============================================================================


@pytest.mark.parametrize(
    "rel_path, expected_type",
    GOLDEN_SET,
    ids=[entry[0].split("/")[-1] for entry in GOLDEN_SET],
)
def test_golden_set_classification(rel_path: str, expected_type: FileType) -> None:
    """Each golden file MUST be classified to its expected FileType."""
    abs_path = PROJECT_ROOT / rel_path
    assert abs_path.exists(), f"Golden file missing from repo: {rel_path}"

    result = classify_file_standalone(abs_path)
    assert result == expected_type, (
        f"Classification mismatch for {rel_path}:\n"
        f"  Expected: {expected_type}\n"
        f"  Got:      {result}\n"
        f"  If this change is intentional, update the GOLDEN_SET in this file."
    )


# ============================================================================
# CONTRACT: is_agent_file agrees with classify_file_standalone
# ============================================================================


@pytest.mark.parametrize(
    "rel_path, expected_type",
    GOLDEN_SET,
    ids=[f"is_agent_{entry[0].split('/')[-1]}" for entry in GOLDEN_SET],
)
def test_is_agent_file_consistency(rel_path: str, expected_type: FileType) -> None:
    """is_agent_file must return True iff classify_file_standalone returns AGENT."""
    abs_path = PROJECT_ROOT / rel_path
    if not abs_path.exists():
        pytest.skip(f"File not found: {rel_path}")

    result = is_agent_file(abs_path)
    expected = expected_type == "AGENT"
    assert result == expected, (
        f"is_agent_file({rel_path}) returned {result}, but classify_file_standalone returned {expected_type}"
    )


# ============================================================================
# CONTRACT: is_agent_or_orchestrator agrees with classify_file_standalone
# ============================================================================


@pytest.mark.parametrize(
    "rel_path, expected_type",
    GOLDEN_SET,
    ids=[f"is_agent_orch_{entry[0].split('/')[-1]}" for entry in GOLDEN_SET],
)
def test_is_agent_or_orchestrator_consistency(
    rel_path: str,
    expected_type: FileType,
) -> None:
    """is_agent_or_orchestrator must return True iff AGENT or ORCHESTRATOR."""
    abs_path = PROJECT_ROOT / rel_path
    if not abs_path.exists():
        pytest.skip(f"File not found: {rel_path}")

    result = is_agent_or_orchestrator(abs_path)
    expected = expected_type in ("AGENT", "ORCHESTRATOR")
    assert result == expected, (
        f"is_agent_or_orchestrator({rel_path}) returned {result}, "
        f"but classify_file_standalone returned {expected_type}"
    )


# ============================================================================
# CONTRACT: AGENT files must NOT be classified as MIXIN, PROTOCOL, or STRATEGY
# ============================================================================


class TestPriorityInvariants:
    """Verify that priority ordering invariants hold across the golden set."""

    def test_no_agent_is_mixin(self) -> None:
        """No file classified as AGENT should have 'Mixin' in its primary class name."""
        for rel_path, expected_type in GOLDEN_SET:
            if expected_type == "AGENT":
                assert "Mixin" not in rel_path, f"{rel_path} is classified as AGENT but has 'Mixin' in path"

    def test_ignore_files_are_infrastructure(self) -> None:
        """IGNORE files should only be __init__.py, conftest.py, etc."""
        infra_names = {"__init__.py", "conftest.py", "__main__.py", "setup.py", "tool_registry.py"}
        for rel_path, expected_type in GOLDEN_SET:
            if expected_type == "IGNORE":
                filename = Path(rel_path).name
                assert filename in infra_names, f"{rel_path} is IGNORE but not in critical infrastructure set"

    def test_mixin_before_agent(self) -> None:
        """MIXIN priority (7) is higher than AGENT priority (10).
        A file with 'Mixin' in its class name must be MIXIN, not AGENT."""
        for rel_path, expected_type in GOLDEN_SET:
            if "mixin" in Path(rel_path).stem.lower():
                assert expected_type in ("MIXIN", "IGNORE"), (
                    f"{rel_path} has 'mixin' in stem but classified as {expected_type}"
                )


# ============================================================================
# CONTRACT: Kernel function signatures are stable
# ============================================================================


class TestKernelAPI:
    """Verify the kernel's public API surface is stable."""

    def test_classify_file_standalone_exists(self) -> None:
        """classify_file_standalone must be importable."""
        assert callable(classify_file_standalone)

    def test_is_agent_file_exists(self) -> None:
        """is_agent_file must be importable."""
        assert callable(is_agent_file)

    def test_is_agent_or_orchestrator_exists(self) -> None:
        """is_agent_or_orchestrator must be importable."""
        assert callable(is_agent_or_orchestrator)

    def test_filetype_has_all_expected_values(self) -> None:
        """FileType Literal must contain all 20 expected classification values."""
        import typing

        args = typing.get_args(FileType)
        expected = {
            "AGENT",
            "CLASS",
            "MIXIN",
            "UTILITY",
            "PROTOCOL",
            "ENGINE",
            "STUB",
            "TEST",
            "SCRIPT",
            "TYPES",
            "GATEWAY",
            "ORCHESTRATOR",
            "VALIDATOR",
            "FACTORY",
            "CONFIG",
            "ADAPTER",
            "STRATEGY",
            "EXCEPTION",
            "SERVICE",
            "IGNORE",
        }
        assert set(args) == expected, (
            f"FileType mismatch.\n  Missing: {expected - set(args)}\n  Extra:   {set(args) - expected}"
        )


# ============================================================================
# CONTRACT: Agent count regression guard
# ============================================================================


class TestAgentCountRegression:
    """Guard against agent count drift."""

    EXPECTED_MIN = 170  # Allow some tolerance below 190
    EXPECTED_MAX = 220  # Allow some tolerance above 190

    def test_agent_count_in_range(self) -> None:
        """Total agent count must stay within expected bounds."""
        import os

        scan_dirs = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]
        exclude = {
            "__pycache__",
            ".git",
            "node_modules",
            ".backup",
            "archives",
            ".healing_backups",
            "tests",
            ".venv",
        }
        agent_count = 0
        for sd in scan_dirs:
            d = PROJECT_ROOT / sd
            if not d.exists():
                continue
            for dirpath, dirnames, filenames in os.walk(d):
                dirnames[:] = [dn for dn in dirnames if dn not in exclude]
                for fn in filenames:
                    if fn.endswith(".py") and fn != "__init__.py":
                        fp = Path(dirpath) / fn
                        if is_agent_file(fp):
                            agent_count += 1

        assert self.EXPECTED_MIN <= agent_count <= self.EXPECTED_MAX, (
            f"Agent count {agent_count} outside expected range "
            f"[{self.EXPECTED_MIN}, {self.EXPECTED_MAX}]. "
            f"If intentional, update the bounds in this test."
        )
