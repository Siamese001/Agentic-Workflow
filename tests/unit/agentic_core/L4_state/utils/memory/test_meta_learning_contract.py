"""Test meta learning contract functionality."""

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
agentic_core = import_or_skip(
    "agentic_core",
    reason="agentic_core unavailable for test_meta_learning_contract.py tests",
)
module_under_test = getattr(agentic_core, "meta_learning_contract")


@pytest.mark.unit
class TestMetaLearningContract:
    """Test meta learning contract functionality."""

    def test_module_imports(self):
        assert module_under_test is not None

    def test_module_class(self):
        exported_class = getattr(agentic_core, "MetaLearningContract")
        assert exported_class is not None

    def test_module_callable(self):
        validator = getattr(agentic_core, "validate_meta_learning_contract")
        assert callable(validator)
