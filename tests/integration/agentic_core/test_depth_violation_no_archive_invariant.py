"""
Wave 0A Invariant: LocationHealerAgent must never archive files under sovereign roots
for depth violations (DEEP VIOLATION or SHALLOW VIOLATION).

Root cause this guards against: The archive fallback in _apply_healing_strategy()
was firing for depth violations that slipped through the strategy map or produced
no-op moves, causing 1,031 unintended file deletions in run11.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Check if required modules are available
try:
    from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
    )
    from agentic_core.L5_safety.config.structure_blueprint import get_all_territories

    # MW-9 (2026-04-24): Class body relocated to utils module.
    from agentic_core.L5_safety.utils.location_healer_util import LocationHealerAgent
    from agentic_core.L5_safety.utils.location_constants_util import HEALING_STRATEGY_MAP
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        _emit_applies_guardrail,
        _emit_reads_policy_state,
        _emit_records_execution_trace,
        _emit_snapshots_state,
    )

    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


# Under --import-mode=importlib pytest collects this as package tests/agentic_core,
# so bare 'from agentic_core...' resolves into tests/ not the project root.
_PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

SOVEREIGN_ROOTS = [APPS_LIC_DIR, APPS_RG_DIR, AGENTIC_CORE_DIR, APPS_SHARED_DIR]

DEPTH_VIOLATION_MESSAGES = [
    "DEEP VIOLATION: file is too deep",
    "SHALLOW VIOLATION: file is too shallow",
    "DEEP VIOLATION at apps_lic/engines/FooAgent.py",
    "SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py",
]


@pytest.fixture
def healer(tmp_path):
    """Minimal LocationHealerAgent configured against tmp_path as project root."""
    agent = LocationHealerAgent.__new__(LocationHealerAgent)
    agent.project_root = tmp_path
    agent._autonomous_mode = False
    return agent, tmp_path


@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
@pytest.mark.parametrize("violation_msg", DEPTH_VIOLATION_MESSAGES)
@pytest.mark.parametrize("sovereign_root", SOVEREIGN_ROOTS)
def test_depth_violation_never_archived(healer, sovereign_root, violation_msg):
    """
    Invariant: _apply_healing_strategy must never return ARCHIVED for any
    DEEP VIOLATION or SHALLOW VIOLATION message under a sovereign root.
    """
    agent, tmp_path = healer

    # Create a fake file under the sovereign root
    sovereign_dir = tmp_path / sovereign_root / "engines"
    sovereign_dir.mkdir(parents=True, exist_ok=True)
    fake_file = sovereign_dir / "TestAgent.py"
    fake_file.write_text("class TestAgent: pass\n")

    archives_root = tmp_path / ".healing_backups"
    archives_root.mkdir(parents=True, exist_ok=True)

    affected_paths: list[Path] = []
    import_touched_paths: list[Path] = []

    result = agent._apply_healing_strategy(
        file_path=fake_file,
        msg=violation_msg,
        archives_root=archives_root,
        dry_run=False,
        affected_paths=affected_paths,
        import_touched_paths=import_touched_paths,
    )

    action = result.get("action_taken", "")
    assert "ARCHIVED" not in action.upper(), (
        f"INVARIANT VIOLATED: {sovereign_root} file was ARCHIVED for depth violation.\n"
        f"  File: {fake_file}\n"
        f"  Violation: {violation_msg}\n"
        f"  Result: {result}"
    )

    # Confirm the file was not actually moved to archives
    assert fake_file.exists(), (
        f"INVARIANT VIOLATED: {sovereign_root} file was physically moved/deleted "
        f"for depth violation: {violation_msg}"
    )


@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
def test_identity_path_guard_returns_skipped(healer):
    """
    Bug 3 guard: when _heal_depth_violation computes target_path == file_path
    (depth already correct), it must return SKIPPED, not fall to archive.
    """
    agent, tmp_path = healer

    apps_dir = tmp_path / APPS_LIC_DIR / "engines"
    apps_dir.mkdir(parents=True, exist_ok=True)
    fake_file = apps_dir / "FooAgent.py"
    fake_file.write_text("class FooAgent: pass\n")

    affected_paths: list[Path] = []
    import_touched_paths: list[Path] = []

    # Patch SOVEREIGN_REGISTRY to return depth=2 (matching the file's actual depth=2)
    mock_registry = {APPS_LIC_DIR: {"depth": 2, "subfolders": ["engines", "reasoning"]}}
    with patch(
        "agentic_core.L5_safety.utils.location_healer_util.SOVEREIGN_REGISTRY",
        mock_registry,
    ):
        result = agent._heal_depth_violation(
            file_path=fake_file,
            msg="DEEP VIOLATION: file is too deep",
            dry_run=False,
            affected_paths=affected_paths,
            import_touched_paths=import_touched_paths,
        )

    action = result.get("action_taken", "")
    assert "SKIPPED" in action.upper() or "depth already correct" in action.lower(), (
        f"Identity-path guard failed — expected SKIPPED, got: {result}"
    )
    assert fake_file.exists(), "File was moved despite identity-path guard"


@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
def test_shallow_violation_in_strategy_map():
    """Bug 2 guard: SHALLOW VIOLATION must be in HEALING_STRATEGY_MAP."""
    assert "SHALLOW VIOLATION" in HEALING_STRATEGY_MAP, (
        "SHALLOW VIOLATION missing from HEALING_STRATEGY_MAP — shallow files will fall to archive fallback"
    )


@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
def test_pascal_in_non_agent_folder_in_strategy_map():
    """Bug 5 guard: PASCAL_IN_NON_AGENT_FOLDER must be in HEALING_STRATEGY_MAP."""
    assert "PASCAL_IN_NON_AGENT_FOLDER" in HEALING_STRATEGY_MAP, (
        "PASCAL_IN_NON_AGENT_FOLDER missing from HEALING_STRATEGY_MAP — "
        "PascalCase agent files in engines/ will be archived instead of moved to reasoning/"
    )


@pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
def test_apps_rg_apps_lic_depth_is_two():
    """Bug 1 guard: apps_rg and apps_lic must have depth=2 in get_all_territories()."""
    for territory in (APPS_RG_DIR, APPS_LIC_DIR):
        depth = get_all_territories().get(territory, {}).get("depth")
        assert depth == 2, (
            f"SSOT depth split: {territory} has depth={depth} in get_all_territories(), "
            f"expected 2. This causes DEEP VIOLATION false positives and archive fallback."
        )
