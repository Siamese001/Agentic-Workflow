"""
Guardian test: Discovery script hash authority is singular and correct.

Invariants enforced:
  1. Exactly ONE canonical hash constant for forensic_discovery_prep.py
     exported from structure_blueprint (no KNOWN_GOOD_HASHES or secondary dict).
  2. The canonical value equals the SHA-256 of the on-disk script.
  3. Default discovery output conforms to v5.4 strict schema.
  4. --legacy-schema flag produces the legacy key structure.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
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


def _run_discovery(project_root: Path, *extra_args: str) -> dict:
    """Run forensic_discovery_prep.py and return parsed JSON output."""
    script = project_root / FORENSIC_DISCOVERY_SCRIPT
    result = subprocess.run(
        [sys.executable, str(script), *extra_args],
        capture_output=True,
        text=True,
        cwd=str(project_root),
        env={**__import__("os").environ, "PYTHONPATH": str(project_root)},
        timeout=120,
    )
    assert result.returncode == 0, (
        f"FAIL: discovery script exited {result.returncode}\nstderr: {result.stderr}"
    )
    return json.loads(result.stdout)


class TestDiscoveryV54Schema:
    """Ensure default discovery output conforms to v5.4 strict schema."""

    def test_v54_top_level_keys(self, project_root: Path) -> None:
        """Default output must have top-level keys: meta, ssot_validation, agents."""
        data = _run_discovery(project_root)
        required = {"meta", "ssot_validation", "agents"}
        assert required.issubset(data.keys()), (
            f"FAIL: Missing top-level keys. Required: {required}. Got: {set(data.keys())}"
        )

    def test_v54_meta_keys(self, project_root: Path) -> None:
        """meta must contain timestamp, root_path, git_hash."""
        data = _run_discovery(project_root)
        meta = data["meta"]
        for key in ("timestamp", "root_path", "git_hash"):
            assert key in meta, f"FAIL: meta missing required key '{key}'"

    def test_v54_ssot_validation_keys(self, project_root: Path) -> None:
        """ssot_validation must contain blueprint_hash and status."""
        data = _run_discovery(project_root)
        sv = data["ssot_validation"]
        assert "blueprint_hash" in sv, "FAIL: ssot_validation missing 'blueprint_hash'"
        assert "status" in sv, "FAIL: ssot_validation missing 'status'"

    def test_v54_ssot_validation_match(self, project_root: Path) -> None:
        """ssot_validation.status must be MATCH when hash is correct."""
        data = _run_discovery(project_root)
        assert data["ssot_validation"]["status"] == "MATCH", (
            f"FAIL: ssot_validation.status is '{data['ssot_validation']['status']}', expected 'MATCH'"
        )

    def test_v54_agent_keys(self, project_root: Path) -> None:
        """Each agent must have all v5.4 required keys including mixins."""
        data = _run_discovery(project_root)
        agents = data["agents"]
        assert len(agents) > 0, "FAIL: agents list is empty"
        required = {
            "identity",
            "layer",
            "status",
            "file_path",
            "class_name",
            "mro_chain",
            "mixins",
            "detected_methods",
            "integrity_hash",
        }
        for i, agent in enumerate(agents[:5]):
            missing = required - set(agent.keys())
            assert not missing, f"FAIL: agents[{i}] missing keys: {missing}"

    def test_v54_mixins_is_list(self, project_root: Path) -> None:
        """agents[*].mixins must be a list."""
        data = _run_discovery(project_root)
        for i, agent in enumerate(data["agents"][:5]):
            assert isinstance(agent["mixins"], list), (
                f"FAIL: agents[{i}].mixins is {type(agent['mixins']).__name__}, expected list"
            )


class TestDiscoveryLegacySchema:
    """Ensure --legacy-schema produces the prior key structure."""

    def test_legacy_top_level_keys(self, project_root: Path) -> None:
        """--legacy-schema must produce audit_meta and environment_under_test."""
        data = _run_discovery(project_root, "--legacy-schema")
        required = {"audit_meta", "environment_under_test"}
        assert required.issubset(data.keys()), (
            f"FAIL: Legacy output missing keys. Required: {required}. Got: {set(data.keys())}"
        )

    def test_legacy_no_v54_keys(self, project_root: Path) -> None:
        """--legacy-schema must NOT produce v5.4-only keys at top level."""
        data = _run_discovery(project_root, "--legacy-schema")
        for key in ("meta", "ssot_validation", "agents"):
            assert key not in data, f"FAIL: Legacy output unexpectedly contains v5.4 key '{key}'"
