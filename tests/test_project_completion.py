"""
tests/test_project_completion.py
"""

from pathlib import Path


class TestProjectCompletion:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    The final check before closing the project.
    """

    def test_zero_legacy_debt(self):
        """Verify no legacy folders exist."""
        assert not Path("apps_shared/legacy").exists()
        assert not Path("apps_lic/legacy").exists()
        assert not Path("apps_rg/legacy").exists()

    def test_certificate_is_green(self):
        """Verify the certificate is 100% clean."""
        cert = Path("SOVEREIGN_SYSTEM_CERTIFICATE.md")
        content = cert.read_text()
        assert "**Status:** CERTIFIED PRODUCTION READY" in content
        assert "[FAIL]" not in content
        assert "ERROR" not in content
