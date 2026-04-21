"""Runtime HITL ledger audit chain — append-only, hash-linked, optionally signed.

Per plan runtime-hitl-exit-control-c4e7b3 W7 P7.1 and ADR-023 §5 (Integrity):

- Every lifecycle event (``created``, ``approved``, ``denied``, ``timeout``) is
  appended to ``hitl_audit_chain`` as an immutable row.
- Each row carries ``prev_hash`` (= hash of the prior row in insertion order)
  and ``entry_hash`` (= SHA-256 of the row payload including ``prev_hash``).
- When a signing key is configured, each ``entry_hash`` is also ed25519-signed
  and the signature is stored in the row.
- Verification walks the chain in order: recomputes every ``entry_hash``,
  asserts the linkage, and — if a public key is provided — validates every
  signature. Failures produce a deterministic :class:`IntegrityReport`.

This module MUST remain pure-stdlib + optional ``cryptography`` — no heavy
crypto stack required for unsigned operation.

Design invariants
-----------------

- The audit chain is append-only. There is no ``UPDATE`` surface.
- The chain is **global-ordered** (not per-run). This lets reviewers verify
  the entire ledger with one walk.
- A broken chain NEVER raises during append — it only surfaces at verify time.
  This is intentional: a runtime crash during append would otherwise wedge the
  whole system.
- Signing is strictly optional. Unsigned chains still prove linkage integrity
  (tamper-evident), just not authenticity.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence, TypeVar

_log = logging.getLogger(__name__)

_T = TypeVar("_T")

try:  # Optional progress bar — §16 compliance for long verify() walks
    from tqdm import tqdm as _tqdm  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover — tqdm is an optional dep

    def _tqdm(it: Iterable[_T], **_kw: Any) -> Iterable[_T]:  # type: ignore[no-redef]
        return it


# ---------------------------------------------------------------------------
# Event taxonomy
# ---------------------------------------------------------------------------


class AuditEventType(str, Enum):
    """Stable taxonomy of HITL lifecycle events."""

    CREATED = "created"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"


# ---------------------------------------------------------------------------
# Signing key Protocol
# ---------------------------------------------------------------------------


class SigningKey(Protocol):
    """Produce an ed25519-style signature over a payload.

    Real implementations wrap a ``cryptography.hazmat.primitives.asymmetric.
    ed25519.Ed25519PrivateKey``. Test doubles sign deterministically.
    """

    def sign(self, payload: bytes) -> bytes: ...  # pragma: no cover — Protocol stub

    @property
    def public_key_bytes(self) -> bytes: ...  # pragma: no cover — Protocol stub


class VerifyingKey(Protocol):
    """Validate a signature produced by a :class:`SigningKey`."""

    def verify(self, signature: bytes, payload: bytes) -> bool: ...  # pragma: no cover — Protocol stub


# ---------------------------------------------------------------------------
# Schema + dataclasses
# ---------------------------------------------------------------------------


_SCHEMA = """
CREATE TABLE IF NOT EXISTS hitl_audit_chain (
    audit_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    ledger_id    TEXT NOT NULL,
    run_id       TEXT NOT NULL,
    event_type   TEXT NOT NULL,
    event_ts     REAL NOT NULL,
    payload_json TEXT NOT NULL,
    prev_hash    TEXT NOT NULL,
    entry_hash   TEXT NOT NULL,
    signature    TEXT,
    public_key   TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_ledger ON hitl_audit_chain(ledger_id);
CREATE INDEX IF NOT EXISTS idx_audit_run ON hitl_audit_chain(run_id);
"""


@dataclass(frozen=True)
class AuditEvent:
    """One immutable audit-chain row."""

    audit_id: int
    ledger_id: str
    run_id: str
    event_type: AuditEventType
    event_ts: float
    payload: Mapping[str, Any]
    prev_hash: str
    entry_hash: str
    signature: str = ""
    public_key: str = ""


@dataclass(frozen=True)
class IntegrityViolation:
    """Single chain violation produced by :meth:`AuditChain.verify`."""

    audit_id: int
    reason: str
    detail: str = ""


@dataclass(frozen=True)
class IntegrityReport:
    """Deterministic chain verification result.

    ``ok=True`` only when every row verified: hash linkage + (when a public key
    was supplied) signature.
    """

    ok: bool
    total_events: int
    verified_events: int
    violations: Sequence[IntegrityViolation]
    signed_events: int = 0
    verified_signatures: int = 0
    notes: Mapping[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def compute_entry_hash(
    *,
    ledger_id: str,
    run_id: str,
    event_type: str,
    event_ts: float,
    payload: Mapping[str, Any],
    prev_hash: str,
) -> str:
    """Deterministic SHA-256 over the canonical event payload.

    The hash pre-image is ``json.dumps(..., sort_keys=True)`` over a fixed
    field set; this is the ONLY function allowed to define the hash pre-image
    — any change here is a ledger-format migration.
    """
    canonical = {
        "ledger_id": ledger_id,
        "run_id": run_id,
        "event_type": event_type,
        "event_ts": event_ts,
        "payload": _canonical_payload(payload),
        "prev_hash": prev_hash,
    }
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(blob).hexdigest()


def _canonical_payload(payload: Mapping[str, Any]) -> Any:
    """Convert to JSON-safe values; refuse non-serializable inputs loudly."""
    return json.loads(json.dumps(payload, sort_keys=True, separators=(",", ":")))


# ---------------------------------------------------------------------------
# AuditChain
# ---------------------------------------------------------------------------


class AuditChain:
    """SQLite-backed append-only audit chain.

    Usage::

        chain = AuditChain(path="artifacts/runtime/hitl_audit.db",
                           signing_key=load_signing_key())
        chain.append(ledger_id="abc", run_id="r1",
                     event_type=AuditEventType.CREATED,
                     payload={"hitl_class": "financial"})
        report = chain.verify(verifying_key=load_verifying_key())
        assert report.ok
    """

    def __init__(
        self,
        path: Path | str,
        *,
        signing_key: SigningKey | None = None,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._signing_key = signing_key
        self._now = now or time.time
        self._conn = sqlite3.connect(str(self._path), isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)

    # -- lifecycle -------------------------------------------------------

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "AuditChain":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()

    # -- public API ------------------------------------------------------

    def append(
        self,
        *,
        ledger_id: str,
        run_id: str,
        event_type: AuditEventType,
        payload: Mapping[str, Any] | None = None,
        event_ts: float | None = None,
    ) -> AuditEvent:
        """Append one event. Computes prev_hash + entry_hash + optional signature.

        Raises ``ValueError`` if ``payload`` is not JSON-serializable — audit
        rows MUST be deterministically re-hashable.
        """
        try:
            canonical = _canonical_payload(payload or {})
        except (TypeError, ValueError) as exc:
            raise ValueError(f"audit payload not JSON-serializable: {exc}") from exc

        ts = float(event_ts) if event_ts is not None else float(self._now())
        prev_hash = self._latest_hash()
        entry_hash = compute_entry_hash(
            ledger_id=ledger_id,
            run_id=run_id,
            event_type=event_type.value,
            event_ts=ts,
            payload=canonical,
            prev_hash=prev_hash,
        )
        signature_hex = ""
        public_key_hex = ""
        if self._signing_key is not None:
            sig = self._signing_key.sign(entry_hash.encode("ascii"))
            signature_hex = sig.hex()
            public_key_hex = self._signing_key.public_key_bytes.hex()

        cursor = self._conn.execute(
            """INSERT INTO hitl_audit_chain (
                ledger_id, run_id, event_type, event_ts, payload_json,
                prev_hash, entry_hash, signature, public_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ledger_id,
                run_id,
                event_type.value,
                ts,
                json.dumps(canonical, sort_keys=True, separators=(",", ":")),
                prev_hash,
                entry_hash,
                signature_hex or None,
                public_key_hex or None,
            ),
        )
        audit_id = int(cursor.lastrowid or 0)
        return AuditEvent(
            audit_id=audit_id,
            ledger_id=ledger_id,
            run_id=run_id,
            event_type=event_type,
            event_ts=ts,
            payload=canonical,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            signature=signature_hex,
            public_key=public_key_hex,
        )

    def list_events(
        self,
        *,
        ledger_id: str | None = None,
        run_id: str | None = None,
    ) -> list[AuditEvent]:
        query = "SELECT * FROM hitl_audit_chain"
        args: list[Any] = []
        where: list[str] = []
        if ledger_id is not None:
            where.append("ledger_id = ?")
            args.append(ledger_id)
        if run_id is not None:
            where.append("run_id = ?")
            args.append(run_id)
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY audit_id ASC"
        rows = self._conn.execute(query, args).fetchall()
        return [_row_to_event(r) for r in rows]

    def verify(
        self,
        *,
        verifying_key: VerifyingKey | None = None,
    ) -> IntegrityReport:
        """Walk the whole chain and validate linkage + (optional) signatures."""
        rows = self._conn.execute("SELECT * FROM hitl_audit_chain ORDER BY audit_id ASC").fetchall()
        violations: list[IntegrityViolation] = []
        prev_hash = ""
        verified = 0
        signed = 0
        sig_verified = 0
        # §16: progress bar for audit-chain walks (may be thousands of rows)
        for row in _tqdm(rows, desc="Verify audit chain", unit="row", disable=len(rows) < 50):
            event = _row_to_event(row)
            row_ok = True

            if event.prev_hash != prev_hash:
                violations.append(
                    IntegrityViolation(
                        audit_id=event.audit_id,
                        reason="prev_hash_mismatch",
                        detail=f"expected={prev_hash!r} got={event.prev_hash!r}",
                    )
                )
                row_ok = False

            recomputed = compute_entry_hash(
                ledger_id=event.ledger_id,
                run_id=event.run_id,
                event_type=event.event_type.value,
                event_ts=event.event_ts,
                payload=event.payload,
                prev_hash=event.prev_hash,
            )
            if recomputed != event.entry_hash:
                violations.append(
                    IntegrityViolation(
                        audit_id=event.audit_id,
                        reason="entry_hash_mismatch",
                        detail=f"recomputed={recomputed} stored={event.entry_hash}",
                    )
                )
                row_ok = False

            if event.signature:
                signed += 1
                if verifying_key is not None:
                    try:
                        valid = verifying_key.verify(
                            bytes.fromhex(event.signature),
                            event.entry_hash.encode("ascii"),
                        )
                    except (ValueError, TypeError) as exc:
                        valid = False
                        violations.append(
                            IntegrityViolation(
                                audit_id=event.audit_id,
                                reason="signature_error",
                                detail=str(exc),
                            )
                        )
                    if valid:
                        sig_verified += 1
                    else:
                        violations.append(
                            IntegrityViolation(
                                audit_id=event.audit_id,
                                reason="signature_invalid",
                            )
                        )
                        row_ok = False

            if row_ok:
                verified += 1
            prev_hash = event.entry_hash

        notes: dict[str, str] = {}
        if verifying_key is None and signed > 0:
            notes["signature_check"] = f"{signed} signed row(s) present but no verifying_key supplied"
        return IntegrityReport(
            ok=not violations,
            total_events=len(rows),
            verified_events=verified,
            violations=tuple(violations),
            signed_events=signed,
            verified_signatures=sig_verified,
            notes=notes,
        )

    # -- internals -------------------------------------------------------

    def _latest_hash(self) -> str:
        row = self._conn.execute(
            "SELECT entry_hash FROM hitl_audit_chain ORDER BY audit_id DESC LIMIT 1"
        ).fetchone()
        return row["entry_hash"] if row else ""


def _row_to_event(row: sqlite3.Row) -> AuditEvent:
    payload = json.loads(row["payload_json"]) if row["payload_json"] else {}
    return AuditEvent(
        audit_id=int(row["audit_id"]),
        ledger_id=row["ledger_id"],
        run_id=row["run_id"],
        event_type=AuditEventType(row["event_type"]),
        event_ts=float(row["event_ts"]),
        payload=payload,
        prev_hash=row["prev_hash"] or "",
        entry_hash=row["entry_hash"] or "",
        signature=row["signature"] or "",
        public_key=row["public_key"] or "",
    )


# ---------------------------------------------------------------------------
# Ed25519 helpers (optional dep — cryptography)
# ---------------------------------------------------------------------------


class Ed25519SigningKey:
    """Adapter over cryptography's Ed25519PrivateKey. Lazy-imported."""

    def __init__(self, private_bytes: bytes) -> None:
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519  # noqa: PLC0415
            from cryptography.hazmat.primitives import serialization  # noqa: PLC0415
        except ImportError as exc:  # pragma: no cover — optional dep
            raise RuntimeError(
                "cryptography package is required for ed25519 signing; "
                "install with `pip install cryptography`"
            ) from exc
        self._ed25519 = ed25519
        self._serialization = serialization
        self._private = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
        self._public = self._private.public_key()

    def sign(self, payload: bytes) -> bytes:
        return bytes(self._private.sign(payload))

    @property
    def public_key_bytes(self) -> bytes:
        return bytes(
            self._public.public_bytes(
                encoding=self._serialization.Encoding.Raw,
                format=self._serialization.PublicFormat.Raw,
            )
        )


class Ed25519VerifyingKey:
    """Adapter over cryptography's Ed25519PublicKey. Lazy-imported."""

    def __init__(self, public_bytes: bytes) -> None:
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519  # noqa: PLC0415
            from cryptography.exceptions import InvalidSignature  # noqa: PLC0415
        except ImportError as exc:  # pragma: no cover — optional dep
            raise RuntimeError("cryptography package is required for ed25519 verification") from exc
        self._ed25519 = ed25519
        self._InvalidSignature = InvalidSignature
        self._public = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)

    def verify(self, signature: bytes, payload: bytes) -> bool:
        try:
            self._public.verify(signature, payload)
            return True
        except self._InvalidSignature:
            return False


__all__ = [
    "AuditChain",
    "AuditEvent",
    "AuditEventType",
    "Ed25519SigningKey",
    "Ed25519VerifyingKey",
    "IntegrityReport",
    "IntegrityViolation",
    "SigningKey",
    "VerifyingKey",
    "compute_entry_hash",
]
