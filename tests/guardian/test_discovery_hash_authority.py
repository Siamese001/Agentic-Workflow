"""
Guardian test: Discovery script hash authority is singular and correct.

Invariants enforced:
  1. Exactly ONE canonical hash constant for forensic_discovery_prep.py
     exported from structure_blueprint (no KNOWN_GOOD_HASHES or secondary dict).
  2. The canonical value equals the SHA-256 of the on-disk script.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    FORENSIC_DISCOVERY_INTEGRITY_HASH,
    FORENSIC_DISCOVERY_SCRIPT,
)


def _project_root() -> Path:
    """Walk up from this file to find the project root (contains pyproject.toml)."""
    p = Path(__file__).resolve()
    for parent in (p, *p.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Cannot locate project root (no pyproject.toml found)")


@pytest.fixture(scope="module")
def project_root() -> Path:
    return _project_root()


class TestDiscoveryHashAuthority:
    """Ensure a single, correct discovery-script hash authority in the SSOT."""

    def test_no_known_good_hashes_in_ssot(self) -> None:
        """KNOWN_GOOD_HASHES must NOT exist in ssot.py (dual-source-of-truth prevention)."""
        import agentic_core.L5_safety.config.structure_blueprint.ssot as ssot_mod

        assert not hasattr(ssot_mod, "KNOWN_GOOD_HASHES"), (
            "FAIL: ssot.py still exports KNOWN_GOOD_HASHES. "
            "Only FORENSIC_DISCOVERY_INTEGRITY_HASH is the canonical authority."
        )

    def test_no_known_good_hashes_in_package(self) -> None:
        """KNOWN_GOOD_HASHES must NOT be re-exported from the blueprint package."""
        import agentic_core.L5_safety.config.structure_blueprint as bp

        assert not hasattr(bp, "KNOWN_GOOD_HASHES"), (
            "FAIL: structure_blueprint package still exports KNOWN_GOOD_HASHES."
        )

    def test_canonical_hash_matches_on_disk_script(self, project_root: Path) -> None:
        """FORENSIC_DISCOVERY_INTEGRITY_HASH must equal SHA-256 of the on-disk script."""
        script_path = project_root / FORENSIC_DISCOVERY_SCRIPT
        assert script_path.exists(), f"FAIL: Discovery script not found at {script_path}"
        computed = hashlib.sha256(script_path.read_bytes()).hexdigest()
        assert computed == FORENSIC_DISCOVERY_INTEGRITY_HASH, (
            f"FAIL: Hash mismatch.\n"
            f"  Computed:  {computed}\n"
            f"  SSOT:      {FORENSIC_DISCOVERY_INTEGRITY_HASH}\n"
            f"  Script:    {script_path}\n"
            f"Update FORENSIC_DISCOVERY_INTEGRITY_HASH in ssot.py after any "
            f"change to {FORENSIC_DISCOVERY_SCRIPT}."
        )

    def test_canonical_hash_is_valid_sha256(self) -> None:
        """FORENSIC_DISCOVERY_INTEGRITY_HASH must be a valid 64-char lowercase hex string."""
        h = FORENSIC_DISCOVERY_INTEGRITY_HASH
        assert isinstance(h, str), f"FAIL: hash is {type(h).__name__}, expected str"
        assert len(h) == 64, f"FAIL: hash length is {len(h)}, expected 64"
        assert all(c in "0123456789abcdef" for c in h), f"FAIL: hash contains non-hex characters: {h}"

    def test_forensic_discovery_script_path_is_canonical(self) -> None:
        """FORENSIC_DISCOVERY_SCRIPT must use forward slashes and no '..' segments."""
        assert "\\" not in FORENSIC_DISCOVERY_SCRIPT, (
            f"FAIL: backslash in FORENSIC_DISCOVERY_SCRIPT: {FORENSIC_DISCOVERY_SCRIPT}"
        )
        assert ".." not in FORENSIC_DISCOVERY_SCRIPT, (
            f"FAIL: '..' in FORENSIC_DISCOVERY_SCRIPT: {FORENSIC_DISCOVERY_SCRIPT}"
        )
        assert not FORENSIC_DISCOVERY_SCRIPT.startswith("/"), (
            f"FAIL: absolute path in FORENSIC_DISCOVERY_SCRIPT: {FORENSIC_DISCOVERY_SCRIPT}"
        )
