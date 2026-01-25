import pytest
from pathlib import Path


class TestSovereignFinal:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    """

    def test_certificate_existence(self):
        """Verify the certificate was generated and shows passing status."""
        cert = Path("SOVEREIGN_SYSTEM_CERTIFICATE.md")
        assert cert.exists()
        content = cert.read_text()
        assert "**Status:** CERTIFIED PRODUCTION READY" in content
        assert "[FAIL]" not in content, "System still contains failing agents!"

    def test_legacy_cleanup(self):
        """Verify dead code is gone."""
        legacy = Path("apps_shared/legacy")
        assert not legacy.exists(), "Legacy folder still exists!"

    def test_simulation_run(self):
        """Verify the simulation script runs without error."""
        import scripts.simulate_sovereign_workflow as sim

        try:
            sim.run_simulation()
        except SystemExit as e:
            # SystemExit(0) is success, SystemExit(1) is failure
            if e.code != 0:
                pytest.fail("Simulation exited with error code")
        except Exception as e:
            pytest.fail(f"Simulation failed with exception: {e}")
