"""Tests — W1 phase 2 R1B negative controls NEG-5/6/7."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_semantic_cache_negatives.py"
ARTIFACT = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_negative_controls.json"


def _run() -> int:
    return subprocess.run(
        [sys.executable, str(PROBE)], cwd=str(REPO_ROOT),
        timeout=30, check=False, capture_output=True,
    ).returncode


def _read() -> dict:
    _run()
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class TestProbeRuns:
    def test_probe_exits_zero(self):
        assert _run() == 0


class TestNeg5ExpiredFreshness:
    def test_neg5_passes(self):
        a = _read()
        neg5 = a["negatives"]["NEG-5_expired_freshness"]
        assert neg5["passes"] is True
        assert neg5["status"] == "PASS"

    def test_neg5_expected_vs_actual_match(self):
        a = _read()
        neg5 = a["negatives"]["NEG-5_expired_freshness"]
        assert neg5["expected_fail_reason"] == neg5["actual_fail_reason"]
        assert neg5["expected_fail_reason"] == "EXPIRED_ENTRY_MUST_NOT_REUSE"

    def test_neg5_uses_deterministic_clock_fixture(self):
        a = _read()
        neg5 = a["negatives"]["NEG-5_expired_freshness"]
        assert neg5["fixture"]["deterministic_clock_fixture"] is True

    def test_neg5_expired_classified_cold(self):
        a = _read()
        neg5 = a["negatives"]["NEG-5_expired_freshness"]
        assert neg5["fixture"]["expired_class_observed"] == "cold"


class TestNeg6MissingEmbeddingRef:
    def test_neg6_passes(self):
        a = _read()
        neg6 = a["negatives"]["NEG-6_missing_embedding_ref"]
        assert neg6["passes"] is True
        assert neg6["status"] == "PASS"

    def test_neg6_expected_vs_actual_match(self):
        a = _read()
        neg6 = a["negatives"]["NEG-6_missing_embedding_ref"]
        assert neg6["expected_fail_reason"] == neg6["actual_fail_reason"]
        assert neg6["expected_fail_reason"] == "MISSING_EMBEDDING_REF_MUST_BLOCK"

    def test_neg6_embedding_id_required(self):
        a = _read()
        neg6 = a["negatives"]["NEG-6_missing_embedding_ref"]
        assert neg6["fixture"]["embedding_model_id_has_no_default"] is True


class TestNeg7UnsafeReuseClass:
    def test_neg7_passes(self):
        a = _read()
        neg7 = a["negatives"]["NEG-7_unsafe_reuse_class"]
        assert neg7["passes"] is True
        assert neg7["status"] == "PASS"

    def test_neg7_expected_vs_actual_match(self):
        a = _read()
        neg7 = a["negatives"]["NEG-7_unsafe_reuse_class"]
        assert neg7["expected_fail_reason"] == neg7["actual_fail_reason"]
        assert neg7["expected_fail_reason"] == "UNSAFE_REUSE_CLASS_MUST_BLOCK"

    def test_neg7_unsafe_code_rejected_at_construction(self):
        a = _read()
        neg7 = a["negatives"]["NEG-7_unsafe_reuse_class"]
        assert neg7["fixture"]["rejection_observed"] is True
        assert neg7["fixture"]["rejection_error"] is not None


class TestOverall:
    def test_all_three_negatives_pass(self):
        a = _read()
        assert a["overall_status"] == "PASS"
        assert a["all_pass"] is True

    def test_anti_cheat_flags(self):
        a = _read()
        flags = a["anti_cheat_rules_honored"]
        assert flags["expected_vs_actual_fail_reason_compared"] is True
        assert flags["deterministic_fixtures_only"] is True
        assert flags["no_live_embedding_or_cache"] is True
        assert flags["probe_did_not_write_sidecar"] is True

    def test_no_final_acceptance_status_field(self):
        a = _read()
        assert "final_acceptance_status" not in a
