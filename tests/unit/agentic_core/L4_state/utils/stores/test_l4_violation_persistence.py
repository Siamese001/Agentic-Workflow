"""Test l4 violation persistence functionality."""

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
agentic_core = import_or_skip(
    "agentic_core",
    reason="agentic_core unavailable for test_l4_violation_persistence.py tests",
)
module_under_test = getattr(agentic_core, "l4_violation_persistence")


@pytest.mark.unit
class TestL4ViolationPersistence:
    """Test l4 violation persistence functionality."""

    def test_module_imports(self):
        assert module_under_test is not None

    def test_module_class(self):
        exported_class = getattr(agentic_core, "L4ViolationPersistence")
        assert exported_class is not None

    def test_module_callable(self):
        validator = getattr(agentic_core, "validate_l4_violation_persistence")
        assert callable(validator)
