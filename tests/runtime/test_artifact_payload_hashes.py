"""Tests — Artifact payload content_hash recomputation (RTC-REQ-123).

Plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-hardened-w0-7e3c9a.md``

Coverage
--------

  - hash_payload_file recomputes deterministic SHA-256 over file bytes
  - Tampering with the payload changes the hash
  - Tampering with the manifest's declared hash but NOT the payload is detected
  - recompute_payload_hashes detects missing payload, mismatched hash,
    matched hash, and incomplete manifest entry
  - The verifier script exits 0 on baseline
  - The verifier script exits 2 when an artifact_manifest.json declares a
    payload hash that does not match the actual payload bytes
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.artifact_payload_hasher import (
    hash_payload_file,
    recompute_payload_hashes,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"


class TestHashPayloadFile:
    def test_deterministic_across_calls(self, tmp_path):
        p = tmp_path / "x.bin"
        p.write_bytes(b"hello world\n")
        h1, sz1 = hash_payload_file(p)
        h2, sz2 = hash_payload_file(p)
        assert h1 == h2
        assert sz1 == sz2 == 12
        # Sanity: must equal a manual SHA-256
        manual = hashlib.sha256(b"hello world\n").hexdigest()
        assert h1 == manual

    def test_tamper_changes_hash(self, tmp_path):
        p = tmp_path / "x.bin"
        p.write_bytes(b"hello\n")
        h1, _ = hash_payload_file(p)
        p.write_bytes(b"hello!\n")
        h2, _ = hash_payload_file(p)
        assert h1 != h2

    def test_missing_file_raises(self, tmp_path):
        p = tmp_path / "nope.bin"
        with pytest.raises(FileNotFoundError):
            hash_payload_file(p)


class TestRecomputePayloadHashes:
    def _mk_artifact(self, root: Path, rel: str, content: bytes) -> str:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return hashlib.sha256(content).hexdigest()

    def test_match_path_legal(self, tmp_path):
        h = self._mk_artifact(tmp_path, "a.bin", b"alpha")
        result = recompute_payload_hashes(
            [{"artifact_id": "A", "payload_path": "a.bin", "expected_hash": h}],
            tmp_path,
        )
        assert result.legal is True
        assert result.match_count == 1
        assert result.checks[0].match is True

    def test_mismatch_payload_detected(self, tmp_path):
        h = self._mk_artifact(tmp_path, "a.bin", b"alpha")
        # Manifest claims a different hash than payload
        result = recompute_payload_hashes(
            [{"artifact_id": "A", "payload_path": "a.bin",
              "expected_hash": "0" * 64}],
            tmp_path,
        )
        assert result.legal is False
        assert result.mismatch_count == 1
        assert result.checks[0].match is False
        assert result.checks[0].expected_fail_reason == "PAYLOAD_HASH_MISMATCH"
        assert result.expected_fail_reason == "PAYLOAD_HASH_MISMATCH"

    def test_missing_payload_detected(self, tmp_path):
        result = recompute_payload_hashes(
            [{"artifact_id": "A", "payload_path": "missing.bin",
              "expected_hash": "0" * 64}],
            tmp_path,
        )
        assert result.legal is False
        assert result.missing_count == 1
        assert result.checks[0].payload_exists is False
        assert result.expected_fail_reason == "PAYLOADS_MISSING"

    def test_manifest_with_no_artifacts_fails(self, tmp_path):
        result = recompute_payload_hashes([], tmp_path)
        assert result.legal is False
        assert result.expected_fail_reason == "MANIFEST_HAS_NO_ARTIFACTS"

    def test_manifest_dict_form_works(self, tmp_path):
        h = self._mk_artifact(tmp_path, "a.bin", b"alpha")
        manifest = {"artifacts": [
            {"artifact_id": "A", "payload_path": "a.bin", "expected_hash": h},
        ]}
        result = recompute_payload_hashes(manifest, tmp_path)
        assert result.legal is True

    def test_incomplete_entry_detected(self, tmp_path):
        result = recompute_payload_hashes(
            [{"artifact_id": "A"}],  # missing payload_path
            tmp_path,
        )
        # entry-without-path counts as missing
        assert result.legal is False
        assert result.checks[0].expected_fail_reason == "MANIFEST_ENTRY_INCOMPLETE"


class TestVerifierScriptBaseline:
    def test_script_exits_zero_when_no_artifact_manifest(self):
        result = subprocess.run(
            [sys.executable, "scripts/verify_artifact_payload_hashes.py"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
        )
        assert result.returncode == 0

    def test_report_artifact_emitted(self):
        report_path = ARTIFACTS_DIR / "artifact_payload_hash_report.json"
        assert report_path.exists()
        report = json.loads(report_path.read_text(encoding="utf-8"))
        for k in ("verifier", "rule", "status",
                  "csv_self_hash_check", "multi_payload_manifest_check"):
            assert k in report


class TestVerifierFailsClosedOnTamper:
    def test_artifact_manifest_with_bad_hash_triggers_fail_closed(self, tmp_path):
        """Synthesize an artifact_manifest.json with a deliberately wrong hash
        and confirm the verifier exits 2 with PAYLOAD_HASH_MISMATCH."""
        # Pick a payload known to exist: the canonical CSV
        rel = "docs/reference/contracts/certification/runtime_certification_requirements_100_percent_hardened.csv"
        manifest = {"artifacts": [{
            "artifact_id": "canonical_csv",
            "payload_path": rel,
            "expected_hash": "0" * 64,
        }]}
        manifest_path = ARTIFACTS_DIR / "artifact_manifest.json"
        backup = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else None
        try:
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "scripts/verify_artifact_payload_hashes.py"],
                capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
            )
            assert result.returncode == 2, (
                f"expected exit=2, got {result.returncode}\n{result.stdout}\n{result.stderr}"
            )
            report = json.loads((ARTIFACTS_DIR / "artifact_payload_hash_report.json").read_text(encoding="utf-8"))
            assert report["status"] == "FAIL_CLOSED"
            assert report["expected_fail_reason"] == "PAYLOAD_HASH_MISMATCH"
        finally:
            if backup is None:
                if manifest_path.exists():
                    os.remove(manifest_path)
            else:
                manifest_path.write_text(backup, encoding="utf-8")
            # Re-run verifier to restore clean baseline report
            subprocess.run(
                [sys.executable, "scripts/verify_artifact_payload_hashes.py"],
                capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
            )
