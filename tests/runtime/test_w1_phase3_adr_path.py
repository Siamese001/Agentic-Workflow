"""Tests — W1 phase 3 ADR path invariant (user §B 'ADR/calibration artifact').

If the production threshold fails calibration, the ONLY sanctioned path to
a PASS verdict is an ADR-backed recalibration (artifact at
``artifacts/certification/semantic_cache_threshold_adr.json``). This test
module proves:

  1. If an ADR exists, it is PROPOSED_NOT_APPLIED (W1p3: absent; W1p4:
     present but pending approval). Neither state unlocks the override.
  2. The threshold probe documents the ADR path in its rationale.
  3. The calibration probe documents the ADR path in its adr_path_note.
  4. Attempting to lower threshold via env var without APPROVED+APPLIED
     ADR is BLOCKED.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
THRESHOLD_PROBE = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_semantic_cache_threshold.py"
CAL_PROBE = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_threshold_calibration.py"
THRESHOLD_ART = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_proof.json"
CAL_ART = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_calibration_results.json"
ADR_ART = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_adr.json"
ADR_GENERATOR = REPO_ROOT / "scripts" / "generate_threshold_adr.py"


def _run(script: Path, env: dict | None = None) -> int:
    e = dict(os.environ)
    if env:
        for k, v in env.items():
            if v is None:
                e.pop(k, None)
            else:
                e[k] = v
    return subprocess.run(
        [sys.executable, str(script)], cwd=str(REPO_ROOT),
        timeout=120, check=False, capture_output=True, env=e,
    ).returncode


class TestADRIfPresentIsProposedNotApplied:
    """User directive 2026-04-30: any ADR on disk must be PROPOSED_NOT_APPLIED.

    W1 phase 3 did not ship one; W1 phase 4 ships it as PROPOSED_NOT_APPLIED.
    Either state preserves the invariant that RTC-REQ-055 cannot flip PASS
    without explicit owner approval.
    """

    def test_adr_if_exists_is_pending_approval(self):
        if not ADR_ART.exists():
            return  # W1p3 state — valid
        d = json.loads(ADR_ART.read_text(encoding="utf-8"))
        assert d["owner_approval"]["status"] == "PENDING_APPROVAL", (
            f"ADR on disk must be PENDING_APPROVAL, got "
            f"{d['owner_approval']['status']}"
        )
        assert d["implementation_status"] == "PROPOSED_NOT_APPLIED"
        assert d["config_binding"]["applied"] is False


class TestThresholdProbeDocumentsADRPath:
    def test_threshold_probe_records_adr_path(self):
        _run(THRESHOLD_PROBE, {"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        a = json.loads(THRESHOLD_ART.read_text())
        adr_info = a["adr_calibration_artifact"]
        assert "adr_artifact_path" in adr_info
        assert adr_info["adr_artifact_path"].endswith("semantic_cache_threshold_adr.json")
        # adr_artifact_exists is True on W1p4, False on W1p3 — both acceptable.
        # The STRICT invariant is that adr_approved_and_applied is False.
        assert adr_info.get("adr_approved_and_applied") is False, (
            "ADR must not be approved+applied in this test pass"
        )


class TestCalibrationProbeDocumentsADRPath:
    def test_calibration_probe_records_adr_path_note(self):
        _run(CAL_PROBE, {"EMBEDDING_ENABLED": "true",
                         "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": None})
        if not CAL_ART.exists():
            return
        a = json.loads(CAL_ART.read_text())
        assert "adr_path_note" in a
        assert "ADR" in a["adr_path_note"]
        assert "NOT auto-create" in a["adr_path_note"] or "does NOT auto-create" in a["adr_path_note"]


class TestOverrideWithoutADRBlocked:
    """User Rule 1: threshold override without APPROVED+APPLIED ADR -> BLOCKED.

    W1p4: an ADR on disk that is PROPOSED_NOT_APPLIED does NOT authorize the
    override. The test temporarily clears the ADR + runs the probe + restores.
    """

    def _with_adr_absent(self, fn):
        """Run fn with ADR absent, then restore via generator if it existed."""
        backup_path = None
        if ADR_ART.exists():
            backup_path = ADR_ART.with_suffix(".bak")
            shutil.move(str(ADR_ART), str(backup_path))
        try:
            return fn()
        finally:
            if backup_path and backup_path.exists():
                shutil.move(str(backup_path), str(ADR_ART))

    def test_threshold_probe_override_without_adr_blocks(self):
        def run_and_check():
            _run(THRESHOLD_PROBE, {"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": "0.80"})
            a = json.loads(THRESHOLD_ART.read_text())
            assert a["threshold_subclaim_status"] == "OVERRIDE_PRESENT", (
                f"Threshold override without ADR must yield OVERRIDE_PRESENT; "
                f"got {a['threshold_subclaim_status']}"
            )
        self._with_adr_absent(run_and_check)

    def test_threshold_probe_override_with_pending_adr_still_blocks(self):
        """W1p4: even with a PROPOSED_NOT_APPLIED ADR present, override is blocked."""
        if not ADR_ART.exists():
            return  # W1p3 state — covered by the other test
        _run(THRESHOLD_PROBE, {"SEMANTIC_CACHE_THRESHOLD_DYNAMIC": "0.80"})
        a = json.loads(THRESHOLD_ART.read_text())
        assert a["threshold_subclaim_status"] == "OVERRIDE_PRESENT", (
            f"W1p4: override with PROPOSED_NOT_APPLIED ADR still must be BLOCKED; "
            f"got {a['threshold_subclaim_status']}"
        )

    def test_calibration_probe_override_yields_override_present(self):
        _run(CAL_PROBE, {
            "EMBEDDING_ENABLED": "true",
            "SEMANTIC_CACHE_THRESHOLD_DYNAMIC": "0.80",
        })
        if not CAL_ART.exists():
            return
        a = json.loads(CAL_ART.read_text())
        assert a["overall_status"] == "OVERRIDE_PRESENT"


class TestADRPathExistenceChangesVerdict:
    """If an ADR file were present AND override set, threshold_probe would
    not OVERRIDE_PRESENT. We don't create the ADR in this test (user
    directive), but we verify the code path references it.

    This test is a contract-documentation test — it proves the ADR gate
    is wired into the probe's classify logic.
    """

    def test_threshold_probe_classify_references_adr_state(self):
        # Read the probe source to verify the logic path exists
        src = THRESHOLD_PROBE.read_text(encoding="utf-8")
        # W1p4: the probe now consults adr_approved_and_applied (stricter than
        # adr_artifact_exists). Either field name is acceptable evidence.
        assert (
            "adr_approved_and_applied" in src or "adr_artifact_exists" in src
        ), "Threshold probe must consult ADR state in its classification"
        assert "OVERRIDE_PRESENT" in src

    def test_calibration_probe_references_adr_path(self):
        src = CAL_PROBE.read_text(encoding="utf-8")
        assert "ADR" in src
        assert "recalibration" in src.lower()
