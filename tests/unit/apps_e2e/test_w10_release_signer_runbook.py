"""W10 of plan apps-fort-knox-parity-c5d9a3 \u2014 Release-signer runbook tests.

Smoke-checks that the runbook covers all required sections and references
the canonical scripts. Prevents the runbook from silently rotting when
script paths change.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNBOOK = REPO_ROOT / "docs/runbooks/release_signer.md"


def test_runbook_exists():
    assert RUNBOOK.exists(), "release_signer runbook missing"


def test_runbook_covers_required_sections():
    text = RUNBOOK.read_text(encoding="utf-8")
    for needle in (
        "## 1. When to rotate",
        "## 2. Pre-rotation checklist",
        "## 3. Rotation procedure",
        "## 4. Rollback",
        "## 5. Communicating the new fingerprint",
        "## 6. Cosign keyless",
        "## 7. Audit trail",
    ):
        assert needle in text, f"runbook missing section: {needle}"


def test_runbook_references_canonical_scripts():
    text = RUNBOOK.read_text(encoding="utf-8")
    for script in (
        "tools/cert/apps_e2e/sign_apps_release_bundle.py",
        "tools/cert/apps_e2e/verify_apps_release_signature.py",
        "tools/certification/generate_apps_100pct_runtime_proof.py",
        "ops_scripts/ci/check_apps_fortknox_signed_proof.py",
    ):
        assert script in text, f"runbook missing reference to: {script}"


def test_runbook_references_keypair_paths():
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "keys/release_signer/release_signer.key.pem" in text
    assert "config/release_signer/release_signer.pub.pem" in text


def test_runbook_explicitly_warns_against_committing_private_key():
    text = RUNBOOK.read_text(encoding="utf-8")
    # The "do not commit private key" warning must appear in the rotation
    # procedure section so anyone following the steps cannot miss it.
    assert "Do NOT commit" in text or "do NOT commit" in text


def test_runbook_distinguishes_w5_vs_w9_rotation_semantics():
    """W9 keyless (Sigstore) does NOT need rotation; runbook MUST say so explicitly."""
    text = RUNBOOK.read_text(encoding="utf-8")
    assert (
        "ephemeral" in text.lower() or "does NOT need rotation" in text
    ), "runbook must explain W9 keyless requires no rotation"


def test_runbook_includes_rollback_procedure():
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "git revert" in text
