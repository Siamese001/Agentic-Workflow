"""Tests — W1 phase 2 R1B production-threshold probe."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_semantic_cache_threshold.py"
ARTIFACT = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_proof.json"


def _run(env_override: dict | None = None) -> int:
    env = dict(os.environ)
    if env_override:
        for k, v in env_override.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
    return subprocess.run(
        [sys.executable, str(PROBE)], cwd=str(REPO_ROOT),
        timeout=30, check=False, capture_output=True, env=env,
    ).returncode


def _read_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class TestProbeEmitsValidArtifact:
    def test_probe_exits_zero(self):
        # Clear any override envs so we get the default CALIBRATION_GAP path
        assert _run({
            "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None,
            "SEMANTIC_CACHE_THRESHOLD_STATIC": None,
            "SEMANTIC_CACHE_HYBRID_THRESHOLD": None,
        }) == 0

    def test_artifact_records_ssot_defaults(self):
        _run({"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None,
              "SEMANTIC_CACHE_THRESHOLD_STATIC": None,
              "SEMANTIC_CACHE_HYBRID_THRESHOLD": None})
        a = _read_artifact()
        # Defaults from SSOT
        assert a["production_threshold_defaults"]["static"] == 1.0
        assert a["production_threshold_defaults"]["dynamic"] == 0.95


class TestAntiCheatRule1NoSilentLowering:
    def test_no_override_run_yields_calibration_gap(self):
        """Baseline W1p2 behavior: absent any calibration evidence and any
        override, threshold probe emits CALIBRATION_GAP honestly.

        W1p3 note: if a prior run wrote calibration_results.json with
        overall_status=PASS or CALIBRATION_GAP, the probe consumes that
        authoritatively. This test isolates the W1p2 baseline by removing
        calibration artifacts first.
        """
        cal_art = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_calibration_results.json"
        if cal_art.exists():
            cal_art.unlink()
        rc = _run({
            "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None,
            "SEMANTIC_CACHE_THRESHOLD_STATIC": None,
            "SEMANTIC_CACHE_HYBRID_THRESHOLD": None,
        })
        assert rc == 0
        a = _read_artifact()
        assert a["threshold_subclaim_status"] == "CALIBRATION_GAP"
        assert a["override_active"] is False

    def test_override_without_adr_yields_override_present(self):
        rc = _run({"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": "0.80"})
        assert rc == 0
        a = _read_artifact()
        # With override and no APPROVED+APPLIED ADR -> OVERRIDE_PRESENT (BLOCKED path).
        # W1p4: a PROPOSED_NOT_APPLIED ADR on disk does NOT authorize override —
        # only APPROVED+APPLIED ADRs do. The probe must still report OVERRIDE_PRESENT.
        assert a["threshold_subclaim_status"] == "OVERRIDE_PRESENT"
        assert a["override_active"] is True
        assert a["adr_calibration_artifact"]["adr_approved_and_applied"] is False

    def test_anti_cheat_flags_recorded(self):
        _run({"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        a = _read_artifact()
        assert a["anti_cheat_rules_honored"]["rule_1_no_silent_threshold_lowering"] is True
        assert a["anti_cheat_rules_honored"]["probe_did_not_modify_threshold_env"] is True
        assert a["anti_cheat_rules_honored"]["probe_did_not_create_adr"] is True
        assert a["anti_cheat_rules_honored"]["probe_did_not_write_sidecar"] is True

    def test_no_final_acceptance_status_field(self):
        _run({"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        a = _read_artifact()
        assert "final_acceptance_status" not in a
        assert "actual_proof_depth" not in a


class TestADRPathDocumentedButNotActivated:
    def test_adr_artifact_path_is_documented(self):
        _run({"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        a = _read_artifact()
        assert a["adr_calibration_artifact"]["adr_artifact_path"].endswith(
            "semantic_cache_threshold_adr.json"
        )

    def test_adr_artifact_not_created_by_probe(self):
        """Per user 2026-04-30: probe must not create an ADR.

        W1p3 assertion: no ADR on disk at all.
        W1p4 assertion: the probe ITSELF does not create the ADR — if one
        exists, a separate generator script (ops_scripts/ci/generate_threshold_adr.py)
        created it. We verify the probe is not the generator by running the
        probe and checking it does NOT change the ADR file when run.
        """
        adr_path = REPO_ROOT / "artifacts/certification/semantic_cache_threshold_adr.json"
        adr_mtime_before = adr_path.stat().st_mtime if adr_path.exists() else None

        _run({"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})

        if adr_mtime_before is None:
            # W1p3 state: probe did not create one
            assert not adr_path.exists(), (
                f"Probe must not auto-create the ADR artifact at {adr_path}"
            )
        else:
            # W1p4 state: ADR exists; probe must not have touched it
            assert adr_path.exists()
            adr_mtime_after = adr_path.stat().st_mtime
            assert adr_mtime_after == adr_mtime_before, (
                f"Probe must not modify pre-existing ADR; mtime changed "
                f"{adr_mtime_before} -> {adr_mtime_after}"
            )
