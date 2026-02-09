#!/usr/bin/env python3
"""Active Set Fingerprint Stability Tests.

Asserts that the ACTIVE set fingerprint is:
  1. Deterministic under repeated invocations.
  2. Stable under deterministic ordering (sorted agent_ids → sha256).
  3. Changes if agent_ids change.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ops_scripts.ci.active_set_helper import _compute_fingerprint, get_active_set


class TestFingerprintDeterminism:
    """Fingerprint must be stable across repeated calls."""

    def test_two_calls_same_fingerprint(self) -> None:
        r1 = get_active_set(PROJECT_ROOT)
        r2 = get_active_set(PROJECT_ROOT)
        assert r1.fingerprint == r2.fingerprint
        assert r1.count == r2.count
        assert r1.agent_ids == r2.agent_ids

    def test_fingerprint_matches_manual_sha256(self) -> None:
        result = get_active_set(PROJECT_ROOT)
        payload = "\n".join(result.agent_ids).encode("utf-8")
        expected = hashlib.sha256(payload).hexdigest()
        assert result.fingerprint == expected

    def test_fingerprint_changes_on_different_ids(self) -> None:
        fp_a = _compute_fingerprint(("Alpha", "Bravo"))
        fp_b = _compute_fingerprint(("Alpha", "Charlie"))
        assert fp_a != fp_b

    def test_fingerprint_order_sensitive(self) -> None:
        fp_a = _compute_fingerprint(("Alpha", "Bravo"))
        fp_b = _compute_fingerprint(("Bravo", "Alpha"))
        assert fp_a != fp_b

    def test_active_set_count_positive(self) -> None:
        result = get_active_set(PROJECT_ROOT)
        assert result.count > 0
        assert len(result.agent_ids) == result.count
