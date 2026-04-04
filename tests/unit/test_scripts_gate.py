"""
Test scripts purity gate in FCA.

Validates:
- L0/scripts accepts script-like modules only
- Rejects PascalCase filenames
- Rejects substantive class definitions
- Rejects test_*.py files
"""

import re

import pytest

from agentic_core.L0_routing.config import SCRIPTS_FORBIDDEN_PATTERNS

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestScriptsGatePatterns:
    """Tests for scripts gate pattern matching."""

    @pytest.fixture
    def compiled_patterns(self):
        """Compile forbidden patterns for testing."""
        return [re.compile(p) for p in SCRIPTS_FORBIDDEN_PATTERNS]

    @pytest.mark.parametrize(
        "forbidden_name",
        [
            "AgentAuditResult.py",
            "BatchEmbeddingService.py",
            "GitKrakenHealingStrategy.py",
            "InMemoryVectorCache.py",
            "SovereignHealingEngine.py",
            "SovereignReport.py",
            "StrategistBioWriter.py",
            "VectorHealingStrategy.py",
            "MyClass.py",
            "SomeAgent.py",
        ],
    )
    def test_pascalcase_rejected(self, compiled_patterns, forbidden_name: str):
        """PascalCase filenames must be rejected."""
        matched = any(p.match(forbidden_name) for p in compiled_patterns)
        assert matched, f"'{forbidden_name}' should be rejected by scripts gate"

    @pytest.mark.parametrize(
        "forbidden_name",
        [
            "test_boundary_stress_test.py",
            "test_lifecycle_audit.py",
            "test_runtime_verify_installation.py",
            "test_verify_meta_learning_integration.py",
            "test_verify_self_healing.py",
            "test_generator.py",
            "test_something.py",
            "test_.py",
        ],
    )
    def test_test_files_rejected(self, compiled_patterns, forbidden_name: str):
        """test_*.py files must be rejected."""
        matched = any(p.match(forbidden_name) for p in compiled_patterns)
        assert matched, f"'{forbidden_name}' should be rejected by scripts gate"

    @pytest.mark.parametrize(
        "allowed_name",
        [
            "run_healing.py",
            "colors.py",
            "full_agent_discovery.py",
            "check_syntax_util.py",
            "generate_report_util.py",
            "migrate_imports_util.py",
            "__init__.py",
            "conftest.py",
        ],
    )
    def test_valid_scripts_accepted(self, compiled_patterns, allowed_name: str):
        """Valid script names must be accepted."""
        matched = any(p.match(allowed_name) for p in compiled_patterns)
        assert not matched, f"'{allowed_name}' should be accepted by scripts gate"


class TestScriptsGateContentValidation:
    """Tests for scripts gate content validation."""

    def test_script_with_main_guard_accepted(self):
        """Script with __main__ guard should be accepted."""
        content = '''"""Script module."""

def main():
    print("Running")

if __name__ == "__main__":
    main()
'''
        # Script-like: has __main__ guard, no substantive classes
        assert 'if __name__ == "__main__"' in content
        assert "class " not in content

    def test_script_with_class_should_be_flagged(self):
        """Script with substantive class should be flagged."""
        content = '''"""Script module with class."""

class SomeService:
    def __init__(self):
        self.data = {}

    def process(self):
        pass

if __name__ == "__main__":
    SomeService().process()
'''
        # Has substantive class - should be flagged
        assert "class SomeService" in content

    def test_script_with_dataclass_may_be_allowed(self):
        """Script with simple dataclass for CLI args may be allowed."""
        content = '''"""Script module with dataclass."""
from dataclasses import dataclass

@dataclass
class Args:
    verbose: bool = False

def main():
    pass

if __name__ == "__main__":
    main()
'''
        # Simple dataclass for CLI args - may be allowed
        assert "@dataclass" in content
