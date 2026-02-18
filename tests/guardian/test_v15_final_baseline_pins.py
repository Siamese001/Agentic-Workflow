"""
V15 Final Baseline Pins — Post-P6 Completion.

Asserts that:
  - Discovery SHA-256 equals pinned value
  - All test_v15_* suites exist
  - P4 trace_id regex is enforced
  - P5 signing enclave / trust root available
  - P6 meta-invariants runner exists
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

PINNED_DISCOVERY_HASH = "7727c2d167460004aa615cbce76abe687b3008aa553beb54a937d39bcf2cbcd8"

V15_TEST_SUITES = [
    "test_v15_p1_compliance.py",
    "test_v15_p2_compliance.py",
    "test_v15_p3_compliance.py",
    "test_v15_p4_compliance.py",
    "test_v15_p5_compliance.py",
    "test_v15_p6_compliance.py",
    "test_v15_baseline_pins.py",
    "test_v15_integration_wiring.py",
]


class TestV15FinalDiscoveryPin:
    """Discovery artifact hash must match pinned value."""

    def test_discovery_hash_pinned(self):
        discovery_path = Path("artifacts/forensic_discovery_output.json")
        assert discovery_path.exists(), "Discovery output missing"
        actual = hashlib.sha256(discovery_path.read_bytes()).hexdigest()
        assert actual == PINNED_DISCOVERY_HASH, f"Discovery hash drift: {actual} != {PINNED_DISCOVERY_HASH}"


class TestV15FinalSuitePresence:
    """All V15 test suites must exist in tests/guardian/."""

    @pytest.mark.parametrize("suite_file", V15_TEST_SUITES)
    def test_suite_exists(self, suite_file: str):
        path = Path("tests/guardian") / suite_file
        assert path.exists(), f"Missing V15 suite: {path}"

    @pytest.mark.parametrize("suite_file", V15_TEST_SUITES)
    def test_suite_contains_test_classes(self, suite_file: str):
        path = Path("tests/guardian") / suite_file
        content = path.read_text(encoding="utf-8")
        assert "class Test" in content, f"{suite_file} has no test classes"


class TestV15FinalP4TraceID:
    """P4 trace_id regex enforcement is available."""

    def test_trace_id_pattern_importable(self):
        from agentic_core.L0_routing.types.traceability_types import (
            TRACE_ID_PATTERN,
            validate_trace_id,
        )

        assert TRACE_ID_PATTERN is not None
        assert validate_trace_id("CC3AL1-0A1B2C3D") == "CC3AL1-0A1B2C3D"

    def test_trace_id_rejects_invalid(self):
        from agentic_core.L0_routing.types.traceability_types import (
            validate_trace_id,
        )

        with pytest.raises(ValueError):
            validate_trace_id("invalid-trace-id")


class TestV15FinalP5SigningEnclave:
    """P5 signing enclave and trust root are available."""

    def test_enclave_importable(self):
        from agentic_core.L0_routing.types.crypto_trust_types import (
            DeterministicTestEnclave,
            KeyRecord,
            KeyStatus,
            TrustRoot,
        )

        key = KeyRecord(
            key_id="pin-test",
            public_key=b"test-key-32-bytes-of-material!!",
            created_tick=0,
            status=KeyStatus.ACTIVE,
        )
        root = TrustRoot(keys=(key,))
        enclave = DeterministicTestEnclave(root)
        sig = enclave.sign(b"test", "pin-test")
        assert enclave.verify(b"test", sig, "pin-test") is True

    def test_revoked_key_rejected(self):
        from agentic_core.L0_routing.types.crypto_trust_types import (
            DeterministicTestEnclave,
            KeyRecord,
            KeyStatus,
            TrustRoot,
        )

        key = KeyRecord(
            key_id="revoked",
            public_key=b"key-material-for-revoked-test!",
            created_tick=0,
            status=KeyStatus.REVOKED,
        )
        root = TrustRoot(keys=(key,))
        enclave = DeterministicTestEnclave(root)
        with pytest.raises(PermissionError):
            enclave.sign(b"test", "revoked")


class TestV15FinalP6MetaGovernor:
    """P6 meta-invariants runner exists and is functional."""

    def test_meta_runner_importable(self):
        from agentic_core.L0_routing.enforcement.boundary_contracts import (
            fail_closed_on_violation,
            run_meta_invariants,
        )

        report = run_meta_invariants(
            trace_id="pin-t1",
            run_id="pin-run",
            semantic_clock_tick=0,
            discovery_hash=PINNED_DISCOVERY_HASH,
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version="1.3.0",
            expected_schema_version="1.3.0",
            expected_artifacts=frozenset({"A"}),
            actual_artifacts=frozenset({"A"}),
        )
        assert report.pass_fail is True
        assert fail_closed_on_violation(report) is True

    def test_meta_runner_detects_drift(self):
        from agentic_core.L0_routing.enforcement.boundary_contracts import (
            MetaInvariantError,
            fail_closed_on_violation,
            run_meta_invariants,
        )

        report = run_meta_invariants(
            trace_id="pin-t2",
            run_id="pin-run-2",
            semantic_clock_tick=0,
            discovery_hash="drifted",
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version="1.3.0",
            expected_schema_version="1.3.0",
            expected_artifacts=frozenset({"A"}),
            actual_artifacts=frozenset({"A"}),
        )
        assert report.pass_fail is False
        with pytest.raises(MetaInvariantError):
            fail_closed_on_violation(report)
