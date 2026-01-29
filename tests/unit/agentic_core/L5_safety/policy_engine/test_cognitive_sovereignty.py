"""
File: tests/unit/L5_safety/test_cognitive_sovereignty.py
Path: tests/unit/L5_safety/test_cognitive_sovereignty.py
Rationale:
    Unit-level verification for Cognitive Sovereignty guardians.
    [SSOT] Mirrored path enforcement (tests/unit/L5_safety/) per structure_blueprint.py.
    Ensures ComplexityAnalyzer and CodeDetector correctly identify logic risks.
"""

import pytest

# Sovereignty Guardians from L5_safety
from agentic_core.L5_safety.policy_engine.ComplexityAnalyzerAgent import (
    ComplexityAnalyzerAgent,
    ComplexityConfig,
)
from agentic_core.L5_safety.policy_engine.CodeDetectorAgent import CodeDetectorAgent, DetectorConfig


@pytest.fixture
def complex_mock_file(tmp_path):
    """Generates a Python file exceeding cyclomatic complexity limits."""
    # Create mirrored structure in tmp_path to simulate project root
    mock_root = tmp_path / "mock_project"
    mock_root.mkdir()
    f = mock_root / "complex_logic_agent.py"

    # Logic: 25 branches (McCabe Limit = 10)
    code = "def handle_multi_branch_logic(x):\n"
    for i in range(25):
        code += f"    if x == {i}: print('Branch {i}')\n"

    f.write_text(code, encoding="utf-8")
    return f


@pytest.fixture
def deadlock_mock_file(tmp_path):
    """Generates a file with nested lock patterns for detection."""
    mock_root = tmp_path / "mock_project"
    if not mock_root.exists():
        mock_root.mkdir()
    f = mock_root / "sync_hazard.py"

    code = """import threading
lock1_lock = threading.Lock()
lock2_lock = threading.Lock()
def risky_sync():
    with lock1_lock:
        with lock2_lock:
            pass
"""
    f.write_text(code, encoding="utf-8")
    return f


def test_complexity_analysis_enforcement(complex_mock_file):
    """
    Scenario: ComplexityAnalyzerAgent scans high-branching logic.
    Expectation: Detection of 'CYCLOMATIC' type with 'CRITICAL' severity.
    """
    cfg = ComplexityConfig(max_cyclomatic_complexity=10, project_root=complex_mock_file.parent)
    agent = ComplexityAnalyzerAgent(config=cfg)

    violations = agent.analyze_file(complex_mock_file)

    assert len(violations) >= 1
    assert violations[0].type == "CYCLOMATIC"
    assert violations[0].complexity > 20
    assert violations[0].severity == "CRITICAL"


def test_deadlock_pattern_detection(deadlock_mock_file):
    """
    Scenario: CodeDetectorAgent scans for synchronization hazards.
    Expectation: Detection of 'DEADLOCK' type via nested pattern matching.
    """
    cfg = DetectorConfig(project_root=deadlock_mock_file.parent)
    agent = CodeDetectorAgent(config=cfg)

    detections = agent.detect_all(deadlock_mock_file)

    # Filter for deadlock detections specifically
    deadlock_detections = [d for d in detections if d.detection_type == "DEADLOCK"]
    assert len(deadlock_detections) >= 1
    assert "nested lock" in deadlock_detections[0].message.lower()


def test_complexity_exclusion_rules(tmp_path):
    """
    Scenario: Complexity config set to ignore test directories.
    Expectation: Files within 'tests/' are exempted from audit.
    """
    test_subdir = tmp_path / "tests"
    test_subdir.mkdir()
    f = test_subdir / "test_dummy.py"

    # High complexity inside a test file
    code = "def complex_test_setup():\n" + "".join(["    if True: pass\n" for _ in range(15)])
    f.write_text(code)

    cfg = ComplexityConfig(ignore_tests=True, project_root=tmp_path)
    agent = ComplexityAnalyzerAgent(config=cfg)

    report = agent.analyze_repository(target_path=test_subdir)
    assert len(report["violations"]) == 0
