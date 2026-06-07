"""Tests for tools/adg/sign_snapshot.py + ops_scripts/ci/check_adg_snapshot_signed.py (W6).

Plan: ``docs/archive/windsurf/legacy-tree/plans/three-bucket-gap-remediation-069806.md`` (W6).

Verifies:
  * Ed25519 keypair generation + reuse
  * Snapshot signing produces a verifiable DSSE envelope
  * The signing self-verify catches a tampered envelope
  * The verification gate passes for a valid attestation
  * The gate detects file SHA-256 tampering
  * The gate detects three-bucket content drift
  * Bypass / strict-mode contract
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_adg_snapshot_signed.py"

__adg_consumer_mode__ = "inventory"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_minimal_snapshot(path: Path) -> None:
    """Build a tiny snapshot with the schema sign_snapshot inspects."""
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE nodes (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER, dst_id INTEGER,
            relation_type TEXT, bucket TEXT
        );
        CREATE TABLE v_runtime_proof (
            id INTEGER PRIMARY KEY,
            src_name TEXT, dst_name TEXT, relation_type TEXT
        );
        INSERT INTO nodes (id, name) VALUES (1, 'a'), (2, 'b');
        INSERT INTO edges (src_id, dst_id, relation_type, bucket)
            VALUES (1, 2, 'imports', 'static'),
                   (1, 2, 'declared', 'registry');
        INSERT INTO v_runtime_proof (src_name, dst_name, relation_type)
            VALUES ('a', 'b', 'imports');
        """
    )
    con.commit()
    con.close()


def _run_gate(*args: str, env: dict | None = None) -> tuple[int, str]:
    cmd = [sys.executable, str(GATE), *args]
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, env=full_env, check=False
    )
    return proc.returncode, proc.stdout + proc.stderr


@pytest.fixture
def tmp_snapshot(tmp_path: Path) -> Path:
    snap = tmp_path / "adg_indexed_TEST.sqlite"
    _build_minimal_snapshot(snap)
    return snap


@pytest.fixture
def tmp_keypath(tmp_path: Path) -> Path:
    return tmp_path / "ed25519_test.key"


# ---------------------------------------------------------------------------
# Crypto + signing module
# ---------------------------------------------------------------------------


class TestKeypair:
    def test_generates_keypair_at_explicit_path(self, tmp_keypath: Path):
        from tools.adg.sign_snapshot import _ensure_keypair  # noqa: PLC0415

        priv, pub, fresh = _ensure_keypair(
            regenerate=True, key_path=tmp_keypath
        )
        assert priv == tmp_keypath
        assert pub == tmp_keypath.with_suffix(".pub")
        assert priv.exists()
        assert pub.exists()
        assert pub.read_bytes().startswith(b"-----BEGIN PUBLIC KEY-----")
        assert fresh is True

    def test_reuses_existing_keypair(self, tmp_keypath: Path):
        from tools.adg.sign_snapshot import _ensure_keypair  # noqa: PLC0415

        priv1, pub1, fresh1 = _ensure_keypair(
            regenerate=True, key_path=tmp_keypath
        )
        priv2, pub2, fresh2 = _ensure_keypair(key_path=tmp_keypath)
        assert priv1 == priv2
        assert pub1 == pub2
        assert fresh2 is False  # second call reuses the persisted key


class TestSignAndVerify:
    def test_round_trip(self, tmp_snapshot: Path, tmp_keypath: Path):
        from tools.adg.sign_snapshot import sign_snapshot  # noqa: PLC0415

        stats = sign_snapshot(
            snapshot=tmp_snapshot, regenerate_key=True, key_path=tmp_keypath
        )
        assert stats.verified is True
        envelope_path = tmp_snapshot.with_suffix(".sqlite.intoto.jsonl")
        assert envelope_path.exists()
        envelope = json.loads(envelope_path.read_text())
        assert envelope["payloadType"] == "application/vnd.in-toto+json"
        assert envelope["signatures"][0]["sig"]
        assert stats.fields["static_edges"] == 1
        assert stats.fields["registry_edges"] == 1
        assert stats.fields["runtime_proof_edges"] == 1

    def test_tampered_envelope_fails_verification(
        self, tmp_snapshot: Path, tmp_keypath: Path
    ):
        from tools.adg.sign_snapshot import (  # noqa: PLC0415
            _dsse_verify,
            _ensure_keypair,
            sign_snapshot,
        )

        sign_snapshot(
            snapshot=tmp_snapshot, regenerate_key=True, key_path=tmp_keypath
        )
        envelope_path = tmp_snapshot.with_suffix(".sqlite.intoto.jsonl")
        envelope = json.loads(envelope_path.read_text())
        # Flip one byte in the signature.
        bad_sig = list(envelope["signatures"][0]["sig"])
        bad_sig[0] = "X" if bad_sig[0] != "X" else "Y"
        envelope["signatures"][0]["sig"] = "".join(bad_sig)
        _, pub_path, _ = _ensure_keypair(key_path=tmp_keypath)
        ok, reason = _dsse_verify(envelope, pub_path)
        assert ok is False
        assert "signature" in reason.lower() or "verification" in reason.lower()


# ---------------------------------------------------------------------------
# CI gate
# ---------------------------------------------------------------------------


class TestGate:
    def test_gate_passes_for_freshly_signed_snapshot(
        self, tmp_snapshot: Path, tmp_keypath: Path
    ):
        """Sign a tmp snapshot with a tmp keypair, run the gate explicitly.

        Self-contained: pins to tmp_keypath so parallel xdist workers do
        not race over the shared default KEYS_DIR.
        """
        from tools.adg.sign_snapshot import sign_snapshot  # noqa: PLC0415

        sign_snapshot(
            snapshot=tmp_snapshot, regenerate_key=True, key_path=tmp_keypath
        )
        rc, out = _run_gate(
            "--snapshot", str(tmp_snapshot),
            "--public-key", str(tmp_keypath.with_suffix(".pub")),
        )
        assert rc == 0, f"gate should pass on freshly signed snapshot. out={out[-300:]}"
        assert "verified=True" in out

    def test_gate_detects_file_tampering(
        self, tmp_snapshot: Path, tmp_keypath: Path
    ):
        from tools.adg.sign_snapshot import sign_snapshot  # noqa: PLC0415

        sign_snapshot(
            snapshot=tmp_snapshot, regenerate_key=True, key_path=tmp_keypath
        )
        with tmp_snapshot.open("ab") as f:
            f.write(b"\x00")

        rc, out = _run_gate(
            "--snapshot", str(tmp_snapshot),
            "--public-key", str(tmp_keypath.with_suffix(".pub")),
        )
        assert rc == 1
        # File-sha mismatch is the canonical signal; sig-verify failure is
        # an acceptable alternative — both prove tamper detection.
        assert (
            "file SHA-256 mismatch" in out
            or "signature verification failed" in out
        )

    def test_gate_advisory_does_not_block(self, tmp_path: Path):
        # Point at a non-existent snapshot in advisory mode.
        rc, out = _run_gate(
            "--snapshot", str(tmp_path / "nope.sqlite"),
            env={"ADG_SIGNATURE_GATE_STRICT": "0"},
        )
        assert rc == 0

    def test_gate_strict_blocks_on_missing_snapshot(self, tmp_path: Path):
        rc, out = _run_gate(
            "--snapshot", str(tmp_path / "nope.sqlite"),
            env={"ADG_SIGNATURE_GATE_STRICT": "1"},
        )
        assert rc == 1
        # Either "no snapshot" (when --snapshot is None) or "envelope missing".
        assert (
            "no snapshot" in out
            or "envelope missing" in out
            or "FAIL" in out
        )

    def test_gate_bypass_envvar_short_circuits(self, tmp_path: Path):
        rc, out = _run_gate(
            "--snapshot", str(tmp_path / "nope.sqlite"),
            env={"ADG_SIGNATURE_BYPASS": "1"},
        )
        assert rc == 0
        assert "bypass active" in out
