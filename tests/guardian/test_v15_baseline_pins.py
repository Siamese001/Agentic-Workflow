"""
V15 Baseline Pin Tests — Freeze Guard.

Asserts that the discovery hash remains pinned and that P1/P2 suites
exist and are importable. Any drift from the pinned values means the
baseline has been violated.
"""

from __future__ import annotations

import hashlib
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]

DISCOVERY_OUTPUT_SHA256 = "f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4"


class TestV15BaselinePins:
    """Baseline integrity pins for V15 audit closure."""

    def test_discovery_output_sha256_pinned(self):
        """Discovery output must match the pinned SHA-256."""
        discovery_path = PROJECT_ROOT / "artifacts" / "forensic_discovery_output.json"
        assert discovery_path.exists(), f"Missing: {discovery_path}"
        actual = hashlib.sha256(discovery_path.read_bytes()).hexdigest()
        assert actual == DISCOVERY_OUTPUT_SHA256, (
            f"Discovery hash drift: expected {DISCOVERY_OUTPUT_SHA256}, got {actual}"
        )

    def test_p1_suite_exists_and_collects(self):
        """P1 compliance suite must exist and contain test classes."""
        p1_path = PROJECT_ROOT / "tests" / "guardian" / "test_v15_p1_compliance.py"
        assert p1_path.exists(), f"Missing P1 suite: {p1_path}"
        source = p1_path.read_text(encoding="utf-8")
        assert "class TestP1" in source, "P1 suite has no TestP1* classes"

    def test_p2_suite_exists_and_collects(self):
        """P2 compliance suite must exist and contain test classes."""
        p2_path = PROJECT_ROOT / "tests" / "guardian" / "test_v15_p2_compliance.py"
        assert p2_path.exists(), f"Missing P2 suite: {p2_path}"
        source = p2_path.read_text(encoding="utf-8")
        assert "class TestP2" in source, "P2 suite has no TestP2* classes"
