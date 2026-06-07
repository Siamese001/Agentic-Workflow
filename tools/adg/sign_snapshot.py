"""Sign the canonical ADG snapshot with an in-toto SLSA-style attestation (W6).

Plan: ``docs/archive/windsurf/legacy-tree/plans/three-bucket-gap-remediation-069806.md`` (W6).

This is the **supply-chain provenance** stage of the three-bucket ADG
authority pipeline. After the snapshot at
``artifacts/adg/adg_indexed_<ts>.sqlite`` is generated, we:

  1. Compute its SHA-256 digest.
  2. Compute an artifact-content digest covering all three buckets
     (static.edges + registry.edges + v_runtime_proof) — the **certified
     digest** from ``check_adg_certified.py`` triplet completeness.
  3. Build an in-toto v1.0 statement with a SLSA Provenance v1.0
     predicate naming the build step (generate_full_adg.py) and inputs.
  4. Sign the statement with an Ed25519 keypair. The keypair is loaded
     from ``ADG_SIGNING_KEY_PATH`` env var, or auto-generated at
     ``artifacts/adg/keys/ed25519_<fingerprint>.{key,pub}`` (gitignored
     by default — emits a banner if a fresh key is generated).
  5. Emit a ``.intoto.jsonl`` envelope in DSSE-compatible shape so a
     future Sigstore integration can verify against a real OIDC
     identity. Today the verifier checks the local Ed25519 signature;
     tomorrow it will accept Fulcio-issued certificates.

Why local Ed25519 first: SLSA-3 requires non-falsifiable provenance. A
local Ed25519 signature gives auditors the trust foundation. Sigstore
(Fulcio + Rekor) is a strict superset that can be layered later
without breaking the attestation format.

Usage::

    python tools/adg/sign_snapshot.py                   # sign latest snapshot
    python tools/adg/sign_snapshot.py --snapshot path/to/.sqlite
    python tools/adg/sign_snapshot.py --regenerate-key  # force new keypair
    python tools/adg/sign_snapshot.py --verify-only     # verify, do not re-sign

Verification: ``python ops_scripts/ci/check_adg_snapshot_signed.py``

References:
- in-toto v1.0 statement: https://github.com/in-toto/attestation/tree/main/spec/v1
- SLSA Provenance v1.0: https://slsa.dev/spec/v1.0/provenance
- DSSE: https://github.com/secure-systems-lab/dsse
"""

from __future__ import annotations

# This script consumes the canonical snapshot via direct SQLite; it does not
# query ADG materialized views.
__adg_consumer_mode__ = "inventory"

import argparse
import base64
import getpass
import hashlib
import json
import os
import platform
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from tools.adg.shared_modules.path_resolver import connect_adg_snapshot_readonly

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR: Final[Path] = REPO_ROOT / "artifacts" / "adg"
KEYS_DIR: Final[Path] = ARTIFACTS_DIR / "keys"

INTOTO_PREDICATE_TYPE: Final[str] = "https://slsa.dev/provenance/v1"
INTOTO_STATEMENT_TYPE: Final[str] = "https://in-toto.io/Statement/v1"
DSSE_PAYLOAD_TYPE: Final[str] = "application/vnd.in-toto+json"


# ---------------------------------------------------------------------------
# Crypto helpers
# ---------------------------------------------------------------------------


def _import_ed25519():
    """Return cryptography's ed25519 module, raising a clear error if absent."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (  # noqa: PLC0415
            Ed25519PrivateKey,
            Ed25519PublicKey,
        )
        from cryptography.hazmat.primitives.serialization import (  # noqa: PLC0415
            Encoding,
            NoEncryption,
            PrivateFormat,
            PublicFormat,
            load_pem_private_key,
            load_pem_public_key,
        )
    except ImportError as exc:
        raise RuntimeError(
            "cryptography is required for ADG snapshot signing. "
            "Install via: pip install cryptography>=42"
        ) from exc
    return {
        "Ed25519PrivateKey": Ed25519PrivateKey,
        "Ed25519PublicKey": Ed25519PublicKey,
        "Encoding": Encoding,
        "NoEncryption": NoEncryption,
        "PrivateFormat": PrivateFormat,
        "PublicFormat": PublicFormat,
        "load_pem_private_key": load_pem_private_key,
        "load_pem_public_key": load_pem_public_key,
    }


def _key_fingerprint(public_pem: bytes) -> str:
    """Short fingerprint for naming the keypair files."""
    return hashlib.sha256(public_pem).hexdigest()[:16]


def _ensure_keypair(
    *, regenerate: bool = False, key_path: Path | None = None
) -> tuple[Path, Path, bool]:
    """Load or generate an Ed25519 keypair.

    Returns ``(private_key_path, public_key_path, was_freshly_generated)``.
    Honors ``ADG_SIGNING_KEY_PATH`` env var; otherwise uses the default
    location under ``artifacts/adg/keys/``.
    """
    crypto = _import_ed25519()

    explicit_priv = key_path or (
        Path(os.environ["ADG_SIGNING_KEY_PATH"])
        if os.environ.get("ADG_SIGNING_KEY_PATH")
        else None
    )

    if explicit_priv and explicit_priv.exists() and not regenerate:
        priv_path = explicit_priv
        pub_path = explicit_priv.with_suffix(".pub")
        if not pub_path.exists():
            # Re-derive public from private if missing.
            priv_obj = crypto["load_pem_private_key"](
                priv_path.read_bytes(), password=None
            )
            pub_pem = priv_obj.public_key().public_bytes(
                crypto["Encoding"].PEM, crypto["PublicFormat"].SubjectPublicKeyInfo
            )
            pub_path.write_bytes(pub_pem)
        return priv_path, pub_path, False

    # Look for any existing keypair in the default dir before generating.
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    if not regenerate:
        existing = sorted(KEYS_DIR.glob("ed25519_*.key"))
        if existing:
            priv_path = existing[-1]
            pub_path = priv_path.with_suffix(".pub")
            if pub_path.exists():
                return priv_path, pub_path, False

    # Generate a new keypair.
    priv = crypto["Ed25519PrivateKey"].generate()
    priv_pem = priv.private_bytes(
        crypto["Encoding"].PEM,
        crypto["PrivateFormat"].PKCS8,
        crypto["NoEncryption"](),
    )
    pub_pem = priv.public_key().public_bytes(
        crypto["Encoding"].PEM, crypto["PublicFormat"].SubjectPublicKeyInfo
    )
    fingerprint = _key_fingerprint(pub_pem)
    # If an explicit key_path was supplied, honor it (lets tests/CI pin to a
    # tmp location and avoid racing with parallel sign() invocations against
    # the shared default KEYS_DIR).
    if explicit_priv is not None:
        priv_path = explicit_priv
        pub_path = explicit_priv.with_suffix(".pub")
        priv_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        priv_path = KEYS_DIR / f"ed25519_{fingerprint}.key"
        pub_path = KEYS_DIR / f"ed25519_{fingerprint}.pub"
    priv_path.write_bytes(priv_pem)
    pub_path.write_bytes(pub_pem)
    # Tighten permissions on the private key (best-effort on Windows).
    try:
        priv_path.chmod(0o600)
    except OSError:
        pass
    return priv_path, pub_path, True


# ---------------------------------------------------------------------------
# Snapshot inspection
# ---------------------------------------------------------------------------


def _has_nodes_table(p: Path) -> bool:
    """Skip stub/sentinel snapshots that lack the `nodes` base table."""
    try:
        with connect_adg_snapshot_readonly(p) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
            ).fetchone()
            return row is not None
    except Exception:
        return False


def _latest_snapshot() -> Path | None:
    """Newest snapshot with a `nodes` base table; skip stubs / sentinels.

    Must agree with ops_scripts/ci/check_adg_snapshot_signed.py:_latest_snapshot
    so the signed envelope lands on the same file the check gate verifies.
    """
    snaps = sorted(ARTIFACTS_DIR.glob("adg_indexed_*.sqlite"), reverse=True)
    if not snaps:
        return None
    for s in snaps:
        if _has_nodes_table(s):
            return s
    return snaps[0]


def _safe_relative(p: Path) -> str:
    """Render ``p`` as a relative path under REPO_ROOT, or fall back to its
    absolute string form when ``p`` is outside the repository tree (e.g.,
    a pytest tmp_path fixture). Avoids the ValueError raised by
    ``Path.relative_to`` for outside-of-tree paths.
    """
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _content_digest(snapshot: Path) -> dict[str, Any]:
    """Compute a deterministic content digest covering all three buckets.

    This is the same idea as the triplet completeness check in
    ``check_adg_certified.py``: we want a single hash that, if any bucket
    drifts, the hash changes. The digest is constructed from a sorted
    canonical projection of (static_edges_count, registry_edges_count,
    v_runtime_proof_count, total_nodes_count).
    """
    con = connect_adg_snapshot_readonly(snapshot)
    try:
        # Edge counts by bucket.
        try:
            static_n = con.execute(
                "SELECT COUNT(*) FROM edges WHERE bucket='static'"
            ).fetchone()[0]
        except sqlite3.OperationalError:
            static_n = 0
        try:
            registry_n = con.execute(
                "SELECT COUNT(*) FROM edges WHERE bucket='registry'"
            ).fetchone()[0]
        except sqlite3.OperationalError:
            registry_n = 0
        # Runtime proof view.
        try:
            runtime_n = con.execute(
                "SELECT COUNT(*) FROM v_runtime_proof"
            ).fetchone()[0]
        except sqlite3.OperationalError:
            runtime_n = 0
        try:
            nodes_n = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        except sqlite3.OperationalError:
            nodes_n = 0
    finally:
        con.close()

    canonical = json.dumps(
        {
            "static_edges": static_n,
            "registry_edges": registry_n,
            "runtime_proof_edges": runtime_n,
            "nodes": nodes_n,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "canonical": canonical,
        "sha256": digest,
        "static_edges": static_n,
        "registry_edges": registry_n,
        "runtime_proof_edges": runtime_n,
        "nodes": nodes_n,
    }


# ---------------------------------------------------------------------------
# in-toto statement + DSSE envelope
# ---------------------------------------------------------------------------


def _build_intoto_statement(snapshot: Path) -> dict[str, Any]:
    # Content digest first so any snapshot inspection completes before the
    # whole-file SHA is pinned (defense-in-depth if a reader ever opened RW).
    content = _content_digest(snapshot)
    file_sha = _file_sha256(snapshot)

    statement = {
        "_type": INTOTO_STATEMENT_TYPE,
        "subject": [
            {
                "name": snapshot.name,
                "digest": {
                    "sha256": file_sha,
                    "adg_three_bucket_content_sha256": content["sha256"],
                },
            }
        ],
        "predicateType": INTOTO_PREDICATE_TYPE,
        "predicate": {
            "buildDefinition": {
                "buildType": "https://agentic-workflow.local/adg-three-bucket/v1",
                "externalParameters": {
                    "snapshot_filename": snapshot.name,
                },
                "internalParameters": {
                    "static_edges": content["static_edges"],
                    "registry_edges": content["registry_edges"],
                    "runtime_proof_edges": content["runtime_proof_edges"],
                    "nodes": content["nodes"],
                },
                "resolvedDependencies": [
                    {
                        "uri": "git+https://internal/agentic-workflow.git",
                        "name": "agentic-workflow",
                    }
                ],
            },
            "runDetails": {
                "builder": {
                    "id": "https://agentic-workflow.local/builder/generate_full_adg",
                    "version": {
                        "tools/generate/generate_full_adg.py": "v1",
                    },
                },
                "metadata": {
                    "invocationId": hashlib.sha256(
                        f"{snapshot.name}:{file_sha[:16]}".encode()
                    ).hexdigest()[:16],
                    "startedOn": datetime.now(timezone.utc).isoformat(),
                    "finishedOn": datetime.now(timezone.utc).isoformat(),
                    "host": platform.node(),
                    "os": platform.system(),
                    "user": getpass.getuser(),
                },
            },
        },
    }
    return statement


def _dsse_sign(statement: dict[str, Any], priv_path: Path) -> dict[str, Any]:
    crypto = _import_ed25519()
    priv = crypto["load_pem_private_key"](priv_path.read_bytes(), password=None)
    payload_bytes = json.dumps(statement, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    payload_b64 = base64.standard_b64encode(payload_bytes).decode("ascii")
    # DSSE pre-authentication encoding (PAE).
    pae = (
        f"DSSEv1 {len(DSSE_PAYLOAD_TYPE)} {DSSE_PAYLOAD_TYPE} "
        f"{len(payload_bytes)} "
    ).encode("utf-8") + payload_bytes
    signature = priv.sign(pae)
    sig_b64 = base64.standard_b64encode(signature).decode("ascii")
    return {
        "payloadType": DSSE_PAYLOAD_TYPE,
        "payload": payload_b64,
        "signatures": [
            {
                "keyid": _key_fingerprint(
                    priv.public_key().public_bytes(
                        crypto["Encoding"].PEM,
                        crypto["PublicFormat"].SubjectPublicKeyInfo,
                    )
                ),
                "sig": sig_b64,
            }
        ],
    }


def _dsse_verify(envelope: dict[str, Any], pub_path: Path) -> tuple[bool, str]:
    """Verify a DSSE envelope against a public key. Returns (ok, reason)."""
    try:
        crypto = _import_ed25519()
        from cryptography.exceptions import InvalidSignature  # noqa: PLC0415
    except RuntimeError as exc:
        return False, f"crypto import failed: {exc}"
    try:
        pub = crypto["load_pem_public_key"](pub_path.read_bytes())
    except (OSError, ValueError) as exc:
        return False, f"cannot load public key: {exc}"

    try:
        payload_bytes = base64.standard_b64decode(envelope["payload"])
        sig_b64 = envelope["signatures"][0]["sig"]
        signature = base64.standard_b64decode(sig_b64)
    except (KeyError, IndexError, ValueError) as exc:
        return False, f"malformed envelope: {exc}"

    pae = (
        f"DSSEv1 {len(envelope['payloadType'])} {envelope['payloadType']} "
        f"{len(payload_bytes)} "
    ).encode("utf-8") + payload_bytes

    try:
        pub.verify(signature, pae)
    except InvalidSignature:
        return False, "signature verification failed"
    except (ValueError, TypeError) as exc:
        return False, f"verification error: {exc}"
    return True, "ok"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


@dataclass
class SignStats:
    snapshot: str = ""
    snapshot_sha256: str = ""
    content_digest_sha256: str = ""
    envelope_path: str = ""
    public_key_path: str = ""
    private_key_path: str = ""
    fresh_key_generated: bool = False
    verified: bool = False
    fields: dict[str, Any] = field(default_factory=dict)


def sign_snapshot(
    *,
    snapshot: Path | None = None,
    regenerate_key: bool = False,
    verify_only: bool = False,
    key_path: Path | None = None,
) -> SignStats:
    snap = snapshot if snapshot is not None and snapshot.exists() else _latest_snapshot()
    if snap is None or not snap.exists():
        raise FileNotFoundError("no ADG snapshot under artifacts/adg/")

    content = _content_digest(snap)
    stats = SignStats(
        snapshot=_safe_relative(snap),
        snapshot_sha256=_file_sha256(snap),
    )
    stats.content_digest_sha256 = content["sha256"]
    stats.fields = {
        k: v for k, v in content.items() if k not in {"canonical", "sha256"}
    }

    envelope_path = snap.with_suffix(".sqlite.intoto.jsonl")
    stats.envelope_path = _safe_relative(envelope_path)

    priv_path, pub_path, fresh = _ensure_keypair(
        regenerate=regenerate_key, key_path=key_path
    )
    stats.private_key_path = _safe_relative(priv_path)
    stats.public_key_path = _safe_relative(pub_path)
    stats.fresh_key_generated = fresh

    if verify_only:
        if not envelope_path.exists():
            raise FileNotFoundError(f"no envelope to verify at {envelope_path}")
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        ok, reason = _dsse_verify(envelope, pub_path)
        stats.verified = ok
        if not ok:
            raise ValueError(f"verification failed: {reason}")
        return stats

    statement = _build_intoto_statement(snap)
    envelope = _dsse_sign(statement, priv_path)
    envelope_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8"
    )

    # Always self-verify after signing.
    ok, reason = _dsse_verify(envelope, pub_path)
    stats.verified = ok
    if not ok:
        raise RuntimeError(f"self-verify after sign failed: {reason}")

    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--regenerate-key", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--key-path", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        stats = sign_snapshot(
            snapshot=args.snapshot,
            regenerate_key=args.regenerate_key,
            verify_only=args.verify_only,
            key_path=args.key_path,
        )
    except FileNotFoundError as exc:
        print(f"[sign_snapshot] FAIL: {exc}")
        return 1
    except RuntimeError as exc:
        print(f"[sign_snapshot] FAIL: {exc}")
        return 1

    print(f"[sign_snapshot] snapshot          = {stats.snapshot}")
    print(f"[sign_snapshot] sha256            = {stats.snapshot_sha256[:16]}...")
    print(f"[sign_snapshot] content_digest    = {stats.content_digest_sha256[:16]}...")
    print(f"[sign_snapshot] envelope          = {stats.envelope_path}")
    print(f"[sign_snapshot] public_key        = {stats.public_key_path}")
    print(f"[sign_snapshot] verified          = {stats.verified}")
    if stats.fresh_key_generated:
        print(
            "[sign_snapshot] [BANNER] fresh keypair generated. ADD "
            f"`{Path(stats.private_key_path).parent}/*.key` TO `.gitignore` "
            "if not already excluded."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
