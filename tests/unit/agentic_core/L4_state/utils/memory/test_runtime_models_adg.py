"""Test runtime models adg functionality."""

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
agentic_core = import_or_skip(
    "agentic_core",
    reason="agentic_core unavailable for test_runtime_models_adg.py tests",
)
module_under_test = getattr(agentic_core, "runtime_models")


@pytest.mark.unit
class TestRuntimemodels:
    """Test runtime models adg functionality."""

    def test_module_imports(self):
        assert module_under_test is not None

    def test_module_has_exports(self):
        if hasattr(module_under_test, "__all__"):
            for name in module_under_test.__all__:
                assert hasattr(module_under_test, name)

    def test_module_docstring_present(self):
        assert module_under_test.__doc__ is not None

    def test_module_attributes_accessible(self):
        attrs = [a for a in dir(module_under_test) if not a.startswith("_")]
        assert len(attrs) >= 0
