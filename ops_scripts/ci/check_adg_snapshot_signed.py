"""G-ADG-SNAPSHOT-SIGNED — verify the in-toto attestation on the latest ADG
snapshot (W6 of plan three-bucket-gap-remediation-069806).

This gate ensures every published ADG snapshot has a valid SLSA-style
in-toto v1.0 attestation signed with an Ed25519 keypair (DSSE envelope
shape — Sigstore-compatible). It guards against:

  * snapshot tampering (file SHA-256 in attestation must match disk)
  * three-bucket drift (content digest in attestation must match the
    static + registry + runtime counts in the snapshot)
  * unsigned promotions (envelope must verify against the trusted
    public key)

Verification failure modes:

  * envelope file missing
  * Ed25519 signature invalid
  * file SHA-256 mismatch
  * three-bucket content digest mismatch

Modes
-----
* ``advisory`` (env ``ADG_SIGNATURE_GATE_STRICT=0``): violations logged
  to stdout + report file; exit 0.
* ``strict`` (default): exit 1 on any verification failure.

Bypass: ``ADG_SIGNATURE_BYPASS=1`` — short-circuits to exit 0.
"""

from __future__ import annotations

# This gate consumes the snapshot via direct SQLite + on-disk envelope; it
# does not query ADG materialized views.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR: Final[Path] = REPO_ROOT / "artifacts" / "adg"
KEYS_DIR: Final[Path] = ARTIFACTS_DIR / "keys"
GATE_REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "adg_snapshot_signed_gate_report.json"
)


@dataclass
class GateResult:
    gate: str = "G-ADG-SNAPSHOT-SIGNED"
    tier: str = "B"
    timestamp: str = ""
    snapshot: str = ""
    envelope_path: str = ""
    public_key_path: str = ""
    verified: bool = False
    file_sha256_match: bool = False
    content_digest_match: bool = False
    strict_mode: bool = True
    violations: list[str] = field(default_factory=list)
    status: str = "ok"


def _has_nodes_table(p: Path) -> bool:
    """Skip stub/sentinel snapshots that lack the `nodes` base table."""
    try:
        import sqlite3 as _sq
        with _sq.connect(str(p)) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
            ).fetchone()
            return row is not None
    except Exception:
        return False


def _latest_snapshot() -> Path | None:
    """Return the newest snapshot with a `nodes` base table; skip stubs.

    Sorting by name (`adg_indexed_99999999_9999.sqlite` is a sentinel future
    date) AND skipping snapshots without `nodes` ensures the gate operates
    on a real signable artifact rather than a placeholder.
    """
    snaps = sorted(ARTIFACTS_DIR.glob("adg_indexed_*.sqlite"), reverse=True)
    if not snaps:
        return None
    for s in snaps:
        if _has_nodes_table(s):
            return s
    return snaps[0]


def _find_public_key() -> Path | None:
    if not KEYS_DIR.exists():
        return None
    pubs = sorted(KEYS_DIR.glob("ed25519_*.pub"))
    return pubs[-1] if pubs else None


def _safe_rel(p: Path) -> str:
    """Path.relative_to(REPO_ROOT) but fall back to absolute when outside."""
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--public-key", type=Path, default=None)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Force strict mode (override ADG_SIGNATURE_GATE_STRICT env var)",
    )
    args = parser.parse_args(argv)

    if os.environ.get("ADG_SIGNATURE_BYPASS") == "1":
        print("[adg_snapshot_signed] bypass active (ADG_SIGNATURE_BYPASS=1)")
        return 0

    # Strict-by-default per W4-style policy.
    _env = os.environ.get("ADG_SIGNATURE_GATE_STRICT", "1")
    strict = args.strict or _env == "1"

    snapshot = args.snapshot or _latest_snapshot()
    result = GateResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
        strict_mode=strict,
    )

    if snapshot is None or not snapshot.exists():
        result.violations.append("no ADG snapshot found under artifacts/adg/")
        result.status = "no_snapshot"
        _write_report(result)
        print("[adg_snapshot_signed] FAIL: no snapshot found")
        return 1 if strict else 0

    result.snapshot = _safe_rel(snapshot)
    envelope_path = snapshot.with_suffix(".sqlite.intoto.jsonl")
    result.envelope_path = _safe_rel(envelope_path)

    if not envelope_path.exists():
        result.violations.append(
            f"envelope missing at {_safe_rel(envelope_path)}; "
            "run: python tools/adg/sign_snapshot.py"
        )
        result.status = "envelope_missing"
        _write_report(result)
        _print_summary(result)
        return 1 if strict else 0

    pub_path = args.public_key or _find_public_key()
    if pub_path is None or not pub_path.exists():
        result.violations.append(
            "no Ed25519 public key found under artifacts/adg/keys/; "
            "run: python tools/adg/sign_snapshot.py to generate"
        )
        result.status = "no_public_key"
        _write_report(result)
        _print_summary(result)
        return 1 if strict else 0
    result.public_key_path = _safe_rel(pub_path)

    # Delegate signature verification + content checks to the signing module.
    sys.path.insert(0, str(REPO_ROOT))
    from tools.adg.sign_snapshot import (  # noqa: PLC0415
        _content_digest,
        _dsse_verify,
        _file_sha256,
    )

    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result.violations.append(f"cannot parse envelope: {exc}")
        result.status = "envelope_unparseable"
        _write_report(result)
        _print_summary(result)
        return 1 if strict else 0

    ok, reason = _dsse_verify(envelope, pub_path)
    result.verified = ok
    if not ok:
        result.violations.append(f"signature verification failed: {reason}")

    # Content checks — extract subject from the in-toto statement embedded
    # in the envelope payload.
    try:
        import base64  # noqa: PLC0415

        payload_bytes = base64.standard_b64decode(envelope["payload"])
        statement = json.loads(payload_bytes)
        subject = statement["subject"][0]
        attested_file_sha = subject["digest"]["sha256"]
        attested_content_sha = subject["digest"]["adg_three_bucket_content_sha256"]
    except (KeyError, ValueError, IndexError) as exc:
        result.violations.append(f"cannot read attestation subject: {exc}")
        result.status = "subject_unparseable"
        _write_report(result)
        _print_summary(result)
        return 1 if strict else 0

    actual_file_sha = _file_sha256(snapshot)
    actual_content = _content_digest(snapshot)

    result.file_sha256_match = attested_file_sha == actual_file_sha
    result.content_digest_match = attested_content_sha == actual_content["sha256"]

    if not result.file_sha256_match:
        result.violations.append(
            f"snapshot file SHA-256 mismatch: attested="
            f"{attested_file_sha[:16]}... actual={actual_file_sha[:16]}... "
            "(snapshot may have been modified after signing)"
        )
    if not result.content_digest_match:
        result.violations.append(
            f"three-bucket content digest mismatch: attested="
            f"{attested_content_sha[:16]}... actual="
            f"{actual_content['sha256'][:16]}... "
            "(static/registry/runtime counts diverged from attestation)"
        )

    if result.violations:
        result.status = "violations"
    _write_report(result)
    _print_summary(result)

    if result.violations and strict:
        return 1
    return 0


def _print_summary(result: GateResult) -> None:
    print(
        f"[adg_snapshot_signed] verified={result.verified} "
        f"file_sha_match={result.file_sha256_match} "
        f"content_digest_match={result.content_digest_match} "
        f"violations={len(result.violations)} strict={result.strict_mode}"
    )
    for v in result.violations:
        print(f"  - {v}")
    print(f"[adg_snapshot_signed] report: {GATE_REPORT_PATH.relative_to(REPO_ROOT)}")


def _write_report(result: GateResult) -> None:
    GATE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_REPORT_PATH.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
