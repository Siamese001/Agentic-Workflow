"""Fort Knox v2 — Independent Bundle Verifier tests.

Confirms that scripts/verify_final_requirement_signoff_bundle.py:
  - PASSes on a clean bundle
  - FAILs on each tamper scenario
  - Emits the verification sidecar artifact
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPILER = REPO_ROOT / "scripts" / "compile_requirement_signoff.py"
BUNDLE_VERIFIER = REPO_ROOT / "scripts" / "verify_final_requirement_signoff_bundle.py"
EXPORTER_XLSX = REPO_ROOT / "scripts" / "export_signoff_to_xlsx.py"
EXPORTER_MD = REPO_ROOT / "scripts" / "export_signoff_to_markdown.py"

OUTPUT_DIR = REPO_ROOT / "artifacts" / "certification"
REPORT_PATH = OUTPUT_DIR / "final_requirement_signoff_report.json"
MERKLE_PATH = OUTPUT_DIR / "final_requirement_signoff_report.merkle.json"
SIG_PATH = OUTPUT_DIR / "final_requirement_signoff_report.signature.json"
SHA256_PATH = OUTPUT_DIR / "final_requirement_signoff_report.sha256"
VERIFY_OUT = OUTPUT_DIR / "final_requirement_signoff_bundle_verification.json"


def _run(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable] + cmd, cwd=REPO_ROOT,
                          capture_output=True, text=True, timeout=timeout)


@pytest.fixture(scope="module", autouse=True)
def build_bundle():
    """Build the full bundle once before any test in this module."""
    r = _run([str(COMPILER)])
    assert r.returncode == 0, f"compile failed: {r.stderr}"
    r = _run([str(EXPORTER_XLSX)])
    assert r.returncode == 0, f"xlsx export failed: {r.stderr}"
    r = _run([str(EXPORTER_MD)])
    assert r.returncode == 0, f"md export failed: {r.stderr}"
    r = _run([str(BUNDLE_VERIFIER)])
    assert r.returncode == 0, f"initial bundle verification failed: {r.stderr}\n{r.stdout}"


@pytest.fixture
def bundle_backup(tmp_path):
    """Backup all bundle files, yield, then restore them."""
    saved: list[tuple[Path, Path]] = []
    for p in (REPORT_PATH, MERKLE_PATH, SIG_PATH, SHA256_PATH):
        if p.exists():
            bk = tmp_path / p.name
            shutil.copy2(p, bk)
            saved.append((p, bk))
    yield
    for orig, bk in saved:
        shutil.copy2(bk, orig)


def _verify() -> dict:
    _run([str(BUNDLE_VERIFIER)])
    return json.loads(VERIFY_OUT.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Clean-bundle tests
# ---------------------------------------------------------------------------

def test_clean_bundle_passes():
    res = _verify()
    assert res["bundle_verification_status"] == "PASS", f"failures: {res['failures'][:5]}"
    assert res["checks_run"] > 0
    assert res["failures"] == []


def test_verifier_emits_structured_output():
    res = _verify()
    assert "bundle_verification_status" in res
    assert "checks_run" in res
    assert "failures" in res
    assert "report_sha256" in res


def test_verifier_detects_report_sha_drift(bundle_backup):
    """Modify report content after compilation — sha sidecar must be seen as drift."""
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    # Tamper by adding a comment field — changes hash
    data["__tampered__"] = "hi"
    REPORT_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    res = _verify()
    assert res["bundle_verification_status"] == "FAIL"
    assert any("sha256" in f.lower() for f in res["failures"])


def test_verifier_detects_manual_signoff_greenwash(bundle_backup):
    """Flip one BLOCKED/NOT_VERIFIED row to SIGNED_OFF without updating controls."""
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    target = next((r for r in data["rows"] if r["computed_status"] != "SIGNED_OFF"), None)
    if target is None:
        pytest.skip("no open rows to greenwash")
    target["computed_status"] = "SIGNED_OFF"
    target["blocking_gap"] = None
    REPORT_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    res = _verify()
    assert res["bundle_verification_status"] == "FAIL"


def test_verifier_detects_missing_row(bundle_backup):
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    data["rows"].pop(0)
    REPORT_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    res = _verify()
    assert res["bundle_verification_status"] == "FAIL"


def test_verifier_detects_tampered_merkle_root(bundle_backup):
    merkle = json.loads(MERKLE_PATH.read_text(encoding="utf-8"))
    merkle["root"] = "0" * 64
    MERKLE_PATH.write_text(json.dumps(merkle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    res = _verify()
    assert res["bundle_verification_status"] == "FAIL"
    assert any("merkle" in f.lower() for f in res["failures"])
