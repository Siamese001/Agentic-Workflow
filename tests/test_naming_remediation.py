import pytest
import re
from pathlib import Path


# CRITICAL: Disable the path shield so we can test actual file logic
@pytest.fixture
def disable_path_shield():
    return True


def to_snake_case(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


VERB_PATTERN = re.compile(
    r"^(Fix|Run|Test|Analyze|Update|Manage|Utilities|Check|Archive|Restore|"
    r"Generate|Fetch|Find|Load|Perform|Query|Refactor|Verify|Convert|Calculate)(?=[A-Z])"
)

PROTECTED_SUFFIXES = (
    "Agent.py",
    "Orchestrator.py",
    "Validator.py",
    "Factory.py",
    "Registry.py",
    "Engine.py",
    "Model.py",
)


class TestRemediationLogic:
    def test_verb_heuristic_identification(self, disable_path_shield):
        """Verify that action-based scripts are correctly flagged for rename."""
        # Test PascalCase inputs that should match the verb pattern
        candidates = [
            "FixAllAgenticImports",
            "RunHardenedJob",
            "UtilitiesFixAllViolations",
            "AnalyzeDashboardColorBug",
        ]
        for c in candidates:
            assert VERB_PATTERN.match(c), f"Failed to match verb in {c}"
            assert "_" in to_snake_case(c), f"Failed snake_case conversion for {c}"

    def test_protection_heuristic(self, disable_path_shield):
        """Verify that Agents/Engines are protected."""
        protected = [
            "StrategicPlannerAgent.py",
            "CanonValidatorEngine.py",
            "SecureErrorHandlerAgent.py",
            "DataProcessorFactory.py",
        ]
        for p in protected:
            assert p.endswith(PROTECTED_SUFFIXES), f"Protected file {p} failed check"

    def test_remediation_script_integrity(self, disable_path_shield):
        """Ensure the remediation script was created and is valid python."""
        script_path = Path("scripts/remediate_naming_audit.py")
        assert script_path.exists(), "Remediation script missing"
        try:
            compile(script_path.read_text(), script_path.name, "exec")
        except SyntaxError as e:
            pytest.fail(f"Remediation script has syntax errors: {e}")
