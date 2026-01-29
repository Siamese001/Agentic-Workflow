import pytest
from unittest.mock import patch
from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent


# Mock Logger to avoid clutter
@pytest.fixture(autouse=True)
def mock_logger():
    with patch("agentic_core.L5_safety.validators.SystemArchitectAgent.Logger") as mock:
        yield mock


# Mock security validation to allow testing in temp directories
@pytest.fixture(autouse=True)
def mock_security_validation():
    with patch(
        "agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent._security_hardening_validation"
    ) as mock:
        mock.return_value = None
        yield mock


def test_dependency_graph_core_isolation(tmp_path):
    """Test 1: Verify Core scan completely ignores 'apps_*' noise (Performance Check)."""
    # Setup Core Territory
    core_dir = tmp_path / "agentic_core" / "prompt_governance"
    core_dir.mkdir(parents=True)
    (core_dir / "main.py").write_text("import agentic_core.prompt_governance.utils")
    (core_dir / "utils.py").write_text("x = 1")

    # Setup Apps Noise (should be IGNORED)
    apps_dir = tmp_path / "apps_lic"
    apps_dir.mkdir()
    (apps_dir / "noise.py").write_text("import sys")

    agent = SystemArchitectAgent(project_root=tmp_path)

    # Execution: Target a core module
    report = agent.validate_core_architecture("agentic_core/prompt_governance")

    # Verification
    assert report["valid"] is True
    # files_scanned must be exactly 2 (main.py, utils.py), ignoring noise.py
    assert report["files_scanned"] == 2
    print("Test Case 1: 100% pass - Core Isolation Verified")


def test_circular_dependency_detection_scoped(tmp_path):
    """Test 2: Verify circular dependency detection works within the targeted scope."""
    core_dir = tmp_path / "agentic_core" / "circular"
    core_dir.mkdir(parents=True)

    # Create cycle: a -> b -> a
    (core_dir / "a.py").write_text("import agentic_core.circular.b")
    (core_dir / "b.py").write_text("import agentic_core.circular.a")

    agent = SystemArchitectAgent(project_root=tmp_path)
    report = agent.validate_core_architecture("agentic_core/circular")

    assert report["valid"] is False
    assert len(report["circular_dependencies"]) > 0
    assert (
        "agentic_core.circular.a -> agentic_core.circular.b -> agentic_core.circular.a"
        in report["circular_dependencies"][0]
    )
    print("Test Case 2: 100% pass - Cycle Detection Verified")


def test_app_targeting_isolation(tmp_path):
    """Test 3: Verify targeting an App strictly ignores 'agentic_core' (Inverse Isolation)."""
    # Setup App Territory
    app_dir = tmp_path / "apps_rg"
    app_dir.mkdir()
    (app_dir / "app_main.py").write_text("x = 1")

    # Setup Core Noise (should be IGNORED when targeting app)
    core_dir = tmp_path / "agentic_core" / "noise"
    core_dir.mkdir(parents=True)
    (core_dir / "core_noise.py").write_text("y = 2")

    agent = SystemArchitectAgent(project_root=tmp_path)

    # Execution: Target the App explicitly
    report = agent.validate_core_architecture("apps_rg")

    # Verification
    assert report["valid"] is True
    # files_scanned should be 1 (app_main.py), ignoring core_noise.py
    assert report["files_scanned"] == 1
    print("Test Case 3: 100% pass - App Targeting Verified")


def test_resilience_invalid_target(tmp_path):
    """Test 4: Verify graceful failure on non-existent targets."""
    agent = SystemArchitectAgent(project_root=tmp_path)

    # Execution: Target ghost folder
    report = agent.validate_core_architecture("agentic_core/ghost_folder")

    # Verification
    assert report["valid"] is False
    assert "Target not found" in report["error"]
    print("Test Case 4: 100% pass - Resilience Verified")
