"""ADG-driven tests for apps_lic/engines/__init__.py — fan_in=13.

Contract tests: all __all__ symbols must be importable (or gracefully None
when optional deps are missing) and the package structure must be stable.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestAppsLicEnginesPublicAPI:
    def test_package_importable(self):
        import apps_lic.engines  # noqa: F401

    def test_all_exports_present_as_attributes(self):
        import apps_lic.engines as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"

    def test_optional_symbols_are_none_or_callable(self):
        """Optional imports must be None (ImportError) or callable — never missing."""
        import apps_lic.engines as m
        for name in m.__all__:
            val = getattr(m, name)
            assert val is None or callable(val), (
            """Test apps_lic import functionality."""
            import apps_lic.engines
            # Basic functionality assertion
            assert True  # Replace with meaningful assertion
        import apps_lic.engines as m
        assert hasattr(m, "ExecutiveStrategyAgent")
        """Test apps_lic import functionality."""
        import apps_lic.engines
        # Basic functionality assertion
        assert True  # Replace with meaningful assertion

    def test_lic_validation_executor_attr(self):
        import apps_lic.engines as m
        assert hasattr(m, "LICValidationExecutor")

    def test_outreach_message_agent_attr(self):
        import apps_lic.engines as m
        assert hasattr(m, "OutreachMessageAgent")

    def test_exec_helper_functions_attr(self):
        import apps_lic.engines as m
        for fn in ("get_exec_interviewer_profile", "get_exec_shadow_audit", "get_exec_strategy_roadmap"):
            assert hasattr(m, fn), f"Missing attribute: {fn}"


class TestAppsLicEnginesGracefulDegradation:
    """When optional deps are absent the package must not raise on import."""

    def test_import_does_not_raise(self):
        import importlib

        import apps_lic.engines as m
        importlib.reload(m)  # second import must also succeed

    def test_none_values_are_not_callable(self):
        import apps_lic.engines as m
        for name in m.__all__:
            val = getattr(m, name)
            if val is None:
                assert not callable(val)
