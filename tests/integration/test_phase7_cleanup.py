"""
Phase 7 Cleanup Verification Tests
Ensures critical duplicates are archived and renamed files exist with shims
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_critical_duplicates_archived():
    """Verify critical duplicate files have been archived."""
    forbidden = [
        "agentic_core/L5_safety/guardrails/CognitiveBatchProcessor.py",
        "agentic_core/L5_safety/guardrails/TieredBatchProcessor.py",
        "agentic_core/L1_cognition/thought_engine/structured_engine.py",
    ]
    for p in forbidden:
        assert not (PROJECT_ROOT / p).exists(), f"Duplicate file still exists: {p}"


def test_renamed_files_exist():
    """Verify renamed files exist at new locations."""
    required = [
        "agentic_core/L1_cognition/thought_engine/supreme_court.py",
        "agentic_core/L1_cognition/thought_engine/execution_types.py",
        "agentic_core/L2_execution/tool_registry/subprocess_executor.py",
        "agentic_core/L4_state/ValidationContext/omni_context.py",
    ]
    for p in required:
        assert (PROJECT_ROOT / p).exists(), f"Renamed file missing: {p}"


def test_shims_exist():
    """Verify backward-compatible shims exist."""
    shims = [
        "agentic_core/L1_cognition/thought_engine/consensus.py",
        "agentic_core/L1_cognition/thought_engine/execution.py",
        "agentic_core/L2_execution/tool_registry/execution.py",
        "agentic_core/L4_state/ValidationContext/context.py",
    ]
    for p in shims:
        shim_path = PROJECT_ROOT / p
        assert shim_path.exists(), f"Shim file missing: {p}"
        content = shim_path.read_text()
        assert "PHASE 7 MIGRATION SHIM" in content, f"Shim missing migration marker: {p}"


def test_nested_maintenance_folder_archived():
    """Verify nested maintenance folder has been archived."""
    nested_folder = PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/maintenance"
    assert not nested_folder.exists(), "Nested maintenance folder still exists"
