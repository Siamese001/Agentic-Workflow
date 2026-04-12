"""E2E Test Harness for FileClassificationAgent - Wave 1 Baseline"""

import pytest

# Check if FileClassificationAgent is available
try:
    from agentic_core.L5_safety.core_kernel.classification_kernel import FileType

    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        ClassificationResult,
        FileClassificationAgent,
        FileClassificationHealerAgent,
    )

    FCA_AVAILABLE = True
except ImportError:
    FCA_AVAILABLE = False


import sys
from pathlib import Path
from typing import Any

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parents[7]))


@pytest.fixture(scope="session")
def agent():
    """Session-scoped FileClassificationAgent fixture."""
    if not FCA_AVAILABLE:
        pytest.skip("FileClassificationAgent not available")
    return FileClassificationAgent()


@pytest.fixture(scope="session")
def healer_agent():
    """Session-scoped FileClassificationHealerAgent fixture."""
    if not FCA_AVAILABLE:
        pytest.skip("FileClassificationAgent not available")
    return FileClassificationHealerAgent()


@pytest.fixture
def repo_root():
    """Return repository root path."""
    return Path(__file__).parents[6]


@pytest.fixture
def expected_agent_files(repo_root):
    """Return list of expected AGENT files in reasoning/."""
    reasoning_dir = repo_root / "agentic_core" / "L5_safety" / "reasoning"
    if not reasoning_dir.exists():
        return []
    return list(reasoning_dir.glob("*Agent.py"))


@pytest.fixture
def expected_script_dirs(repo_root):
    """Return directories where SCRIPT files should be located."""
    return [
        repo_root / "ops_scripts",
        repo_root / "tools",
    ]


class ClassificationReporter:
    """Helper class to generate baseline classification reports."""

    def __init__(self, agent):
        self.agent = agent
        self.results: list[dict[str, Any]] = []

    def classify_directory(self, directory: Path, recursive: bool = True) -> None:
        """Classify all Python files in a directory."""
        pattern = "**/*.py" if recursive else "*.py"
        for file_path in directory.glob(pattern):
            try:
                result = self.agent.classify_file(file_path)
                self.results.append(
                    {
                        "file": str(file_path.relative_to(directory)),
                        "classification": result,
                        "compliant_name": self.agent.get_compliant_name(file_path, result),
                    }
                )
            except Exception as e:
                self.results.append(
                    {
                        "file": str(file_path.relative_to(directory)),
                        "classification": "ERROR",
                        "error": str(e),
                    }
                )

    def generate_report(self) -> dict[str, Any]:
        """Generate summary statistics."""
        stats = {}
        for r in self.results:
            cls = r["classification"]
            stats[cls] = stats.get(cls, 0) + 1
        return {
            "total_files": len(self.results),
            "classifications": stats,
            "details": self.results,
        }


@pytest.fixture
def reporter(agent):
    """Return a ClassificationReporter instance."""
    return ClassificationReporter(agent)


# Test configuration constants
TEST_CONFIG = {
    "performance_target_ms": 5,  # 5ms per file target
    "coverage_target": 0.95,  # 95% test coverage target
    "change_threshold": 0.05,  # 5% classification change threshold
}


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "agent: AGENT classification tests")
    config.addinivalue_line("markers", "script: SCRIPT classification tests")
    config.addinivalue_line("markers", "boundary: Boundary case tests")
    config.addinivalue_line("markers", "performance: Performance benchmark tests")
    config.addinivalue_line("markers", "spec: Spec compliance tests")
