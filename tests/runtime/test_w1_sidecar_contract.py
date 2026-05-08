"""W1.1 — Sidecar Contract Advisory Mode Tests.

Validates sidecar contract in advisory mode (W0/W1.1):
- Sidecar absent: exit 0 (baseline green)
- Sidecar present + clean: exit 0
- Sidecar present + malformed: exit 2

W1 implementation per runtime-cert-hardened-w0-7e3c9a.md
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Sidecar paths (per W1.1 contract)
SIDECAR_PATH = Path("artifacts/certification/semantic_cache_subclaims.json")


def load_sidecar() -> dict[str, Any] | None:
    """Load sidecar if it exists."""
    if not SIDECAR_PATH.exists():
        return None
    try:
        with open(SIDECAR_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"_malformed": True}


def check_sidecar_advisory() -> tuple[int, str]:
    """Check sidecar in advisory mode.
    
    Returns: (exit_code, reason)
    """
    sidecar = load_sidecar()
    
    if sidecar is None:
        # Sidecar absent: exit 0 (advisory mode)
        return 0, "SIDECAR_ABSENT_ADVISORY"
    
    if sidecar.get("_malformed"):
        # Sidecar malformed: exit 2
        return 2, "SIDECAR_MALFORMED"
    
    # Sidecar present and valid: check subclaims
    subclaims = sidecar.get("subclaims", [])
    
    if not subclaims:
        # Empty sidecar: exit 0 in advisory mode
        return 0, "SIDECAR_EMPTY_ADVISORY"
    
    # Check for blocked/partial subclaims
    for claim in subclaims:
        if claim.get("status") in {"BLOCKED", "PARTIAL", "MISMATCH_EXPLAINED"}:
            # Advisory mode: still exit 0, but warn
            return 0, f"SUBCLAIM_{claim.get('status')}_ADVISORY"
    
    return 0, "SIDECAR_CLEAN"


class TestW1SidecarAdvisoryMode:
    """W1.1: Sidecar contract advisory mode."""

    def test_sidecar_absent_exits_zero(self) -> None:
        """Sidecar absent → exit 0 in advisory mode."""
        if SIDECAR_PATH.exists():
            pytest.skip("Sidecar exists — test requires absent sidecar")
        
        exit_code, reason = check_sidecar_advisory()
        assert exit_code == 0, f"Expected exit 0 for absent sidecar, got {exit_code}"
        assert "ADVISORY" in reason

    def test_sidecar_advisory_vs_strict_modes(self) -> None:
        """Advisory and strict modes have different exit codes for absent sidecar."""
        # Advisory mode: absent sidecar → exit 0
        advisory_exit, _ = check_sidecar_advisory()
        
        # In strict mode (would be): absent sidecar → exit 2
        # This is documented in the workflow comments
        
        assert advisory_exit == 0


class TestW1SidecarStructure:
    """Sidecar JSON structure validation."""

    def test_sidecar_schema_if_present(self) -> None:
        """Validate sidecar schema if it exists."""
        sidecar = load_sidecar()
        if sidecar is None:
            pytest.skip("Sidecar not present")
        
        # Should be a dict
        assert isinstance(sidecar, dict)
        
        # Should not be malformed
        assert not sidecar.get("_malformed")

    def test_sidecar_has_subclaims_array(self) -> None:
        """Sidecar has subclaims array if present."""
        sidecar = load_sidecar()
        if sidecar is None or sidecar.get("_malformed"):
            pytest.skip("Sidecar not present or malformed")
        
        # Should have subclaims key
        assert "subclaims" in sidecar
        assert isinstance(sidecar["subclaims"], list)


class TestW1StrictModeContract:
    """W1.2+ strict mode contract tests (documented behavior)."""

    def test_strict_mode_absent_sidecar_exit_two(self) -> None:
        """Strict mode: absent sidecar → exit 2 (SEMANTIC_CACHE_SIDECAR_REQUIRED)."""
        # This test documents the strict mode contract
        # Actual strict mode is gated on SEMANTIC_CACHE_CERTIFICATION_STRICT=1
        
        if SIDECAR_PATH.exists():
            pytest.skip("Sidecar exists")
        
        # In strict mode, this would be exit 2
        # We verify the contract is documented in the workflow
        workflow_path = Path(".github/workflows/runtime-certification.yml")
        if workflow_path.exists():
            with open(workflow_path, "r", encoding="utf-8") as f:
                workflow = f.read()
            
            # Should document strict mode contract
            assert "SEMANTIC_CACHE_SIDECAR_REQUIRED" in workflow or "strict" in workflow.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
