"""Test AppsLicEnginesInitAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAppsLicEnginesInitAdg:
    """Test AppsLicEnginesInitAdg functionality."""

    def test_apps_lic_engines_init_adg_imports(self):
        """Test apps_lic_engines_init_adg module imports."""
        from apps_lic.engines import control_plane

        assert control_plane is not None

    def test_apps_lic_engines_init_adg_class(self):
        """Test ControlPlane class exists in engines."""
        from apps_lic.engines.control_plane import ControlPlane

        assert ControlPlane is not None

    def test_apps_lic_engines_init_adg_callable(self):
        """Test PolicyDecision is callable."""
        from apps_lic.engines.control_plane import PolicyDecision

        assert callable(PolicyDecision)


@pytest.mark.unit
class TestControlPlaneBehavior:
    """G1: behavioral coverage for phase-added control_plane hardening."""

    def _make_cp(self):
        from apps_lic.engines.control_plane import ControlPlane

        return ControlPlane(policy={})

    def test_evaluate_input_ssn_pattern_blocked(self):
        """G1 happy→block: SSN pattern triggers BLOCK + is_safe=False."""
        from apps_lic.engines.control_plane import PolicyAction

        cp = self._make_cp()
        result = cp.evaluate_input("My SSN is 123-45-6789")
        assert result.action == PolicyAction.BLOCK
        assert result.is_safe is False
        assert len(result.errors) > 0

    def test_evaluate_input_clean_content_allowed(self):
        """G1 happy: clean content passes through as ALLOW."""
        from apps_lic.engines.control_plane import PolicyAction

        cp = self._make_cp()
        result = cp.evaluate_input("Please write a professional outreach email.")
        assert result.action == PolicyAction.ALLOW
        assert result.is_safe is True

    def test_evaluate_input_non_string_raises_typeerror(self):
        """G1 failure: non-string content raises TypeError (phase isinstance guard)."""
        cp = self._make_cp()
        with pytest.raises(TypeError, match="content must be a string"):
            cp.evaluate_input(42)  # type: ignore[arg-type]

    def test_evaluate_input_context_keys_sorted_in_metadata(self):
        """G1 edge: PII block metadata contains sorted context_keys."""
        cp = self._make_cp()
        result = cp.evaluate_input(
            "social security number present",
            context={"z_key": 1, "a_key": 2, "m_key": 3},
        )
        keys = result.metadata.get("context_keys", [])
        assert keys == sorted(keys)

    def test_evaluate_input_gmail_address_blocked(self):
        """G1 edge: Gmail address pattern triggers BLOCK."""
        from apps_lic.engines.control_plane import PolicyAction

        cp = self._make_cp()
        result = cp.evaluate_input("Contact user@gmail.com for details")
        assert result.action == PolicyAction.BLOCK

    def test_evaluate_output_non_string_raises_typeerror(self):
        """G4: evaluate_output phase isinstance guard raises TypeError for non-string."""
        cp = self._make_cp()
        with pytest.raises(TypeError, match="content must be a string"):
            cp.evaluate_output(42)  # type: ignore[arg-type]
