"""Tests — W1 phase 3 threshold-calibration probe."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE_CAL = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_threshold_calibration.py"
PROBE_OP = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_bge_m3_operational.py"
ARTIFACT = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_calibration_results.json"
OP_ARTIFACT = REPO_ROOT / "artifacts" / "certification" / "bge_m3_operational_proof.json"


def _run(script: Path, env_override: dict | None = None) -> int:
    env = dict(os.environ)
    if env_override:
        for k, v in env_override.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
    return subprocess.run(
        [sys.executable, str(script)], cwd=str(REPO_ROOT),
        timeout=180, check=False, capture_output=True, env=env,
    ).returncode


def _read() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _bge_m3_deps_available() -> bool:
    import importlib.util
    for dep in ("FlagEmbedding", "sentence_transformers", "torch"):
        if importlib.util.find_spec(dep) is None:
            return False
    return True


def _ensure_bge_operational():
    """Run the operational probe with EMBEDDING_ENABLED=true. Returns status."""
    _run(PROBE_OP, {"EMBEDDING_ENABLED": "true"})
    if not OP_ARTIFACT.exists():
        return "ABSENT"
    return json.loads(OP_ARTIFACT.read_text())["status"]


class TestProbeExits:
    def test_probe_runs_when_bge_m3_operational(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        if _ensure_bge_operational() != "OPERATIONAL":
            pytest.skip("BGE-M3 not operational locally")
        assert _run(PROBE_CAL, {"EMBEDDING_ENABLED": "true"}) == 0

    def test_probe_infrastructure_gap_when_bge_m3_absent(self):
        # Simulate bge_m3 operational evidence missing by removing artifact
        if OP_ARTIFACT.exists():
            OP_ARTIFACT.unlink()
        _run(PROBE_CAL, {"EMBEDDING_ENABLED": "true"})
        a = _read()
        assert a["overall_status"] == "INFRASTRUCTURE_GAP"
        assert a["bge_m3_operational_check"]["ok"] is False


class TestAntiCheatRule1NoOverride:
    def test_override_present_yields_override_status(self):
        # Even with everything else ok, override must block
        _run(PROBE_CAL, {
            "EMBEDDING_ENABLED": "true",
            "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": "0.80",
        })
        a = _read()
        assert a["overall_status"] == "OVERRIDE_PRESENT"
        assert a["override_active"] is True

    def test_no_override_does_not_lower_threshold(self):
        _run(PROBE_CAL, {
            "EMBEDDING_ENABLED": "true",
            "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None,
        })
        a = _read()
        assert a["override_active"] is False
        if a["production_threshold_default"] is not None:
            assert a["production_threshold_default"] == 0.95
            assert a["threshold_actual"] == 0.95


class TestAntiCheatFlags:
    def test_anti_cheat_rules_recorded(self):
        _run(PROBE_CAL, {"EMBEDDING_ENABLED": "true",
                         "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        a = _read()
        f = a["anti_cheat_rules_honored"]
        assert f["rule_1_no_silent_threshold_lowering"] is True
        assert f["rule_2_no_silent_fallback_pass"] is True
        assert f["probe_did_not_modify_threshold_env"] is True
        assert f["probe_did_not_create_adr"] is True
        assert f["probe_did_not_write_sidecar"] is True
        assert f["reference_contract_negatives_not_measured_for_similarity"] is True

    def test_no_final_acceptance_status_field(self):
        _run(PROBE_CAL, {"EMBEDDING_ENABLED": "true"})
        a = _read()
        assert "final_acceptance_status" not in a


class TestCalibrationResultsShape:
    def test_results_include_required_aggregate_fields(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        if _ensure_bge_operational() != "OPERATIONAL":
            pytest.skip("BGE-M3 not operational locally")
        _run(PROBE_CAL, {"EMBEDDING_ENABLED": "true",
                         "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        a = _read()
        if a["overall_status"] in ("INFRASTRUCTURE_GAP", "DATASET_MISSING"):
            pytest.skip(f"calibration did not run: {a['overall_status']}")
        agg = a["aggregate"]
        for key in ("total_positives", "total_negatives",
                    "positive_pass_count", "negative_miss_count",
                    "false_positive_count", "false_negative_count"):
            assert key in agg

    def test_per_pair_records_similarity(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        if _ensure_bge_operational() != "OPERATIONAL":
            pytest.skip("BGE-M3 not operational locally")
        _run(PROBE_CAL, {"EMBEDDING_ENABLED": "true",
                         "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        a = _read()
        if not a["per_pair_results"]:
            pytest.skip("no per-pair results")
        for r in a["per_pair_results"]:
            assert "similarity_score" in r
            assert 0.0 <= r["similarity_score"] <= 1.0
            assert "passed_at_threshold" in r
            assert "agreement" in r
            assert r["agreement"] in ("HIT", "MISS", "FALSE_POSITIVE", "FALSE_NEGATIVE")


class TestCalibrationGapPath:
    def test_calibration_gap_rationale_names_rule_1(self):
        """If calibration fails, rationale must invoke Rule 1 (no silent lowering)."""
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        if _ensure_bge_operational() != "OPERATIONAL":
            pytest.skip("BGE-M3 not operational locally")
        _run(PROBE_CAL, {"EMBEDDING_ENABLED": "true",
                         "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        a = _read()
        if a["overall_status"] == "CALIBRATION_GAP":
            assert "Rule 1" in a["rationale"] or "silently lower" in a["rationale"]

    def test_adr_path_documented_not_auto_created(self):
        if not _bge_m3_deps_available():
            pytest.skip("BGE-M3 deps not available")
        adr = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_adr.json"
        mtime_before = adr.stat().st_mtime if adr.exists() else None
        _run(PROBE_CAL, {"EMBEDDING_ENABLED": "true"})
        a = _read()
        assert "ADR" in a["adr_path_note"]
        # Probe MUST NOT create or modify the ADR
        if mtime_before is None:
            assert not adr.exists(), "Probe must not auto-create the ADR artifact"
        else:
            assert adr.exists()
            assert adr.stat().st_mtime == mtime_before, (
                "Probe must not modify a pre-existing ADR"
            )
