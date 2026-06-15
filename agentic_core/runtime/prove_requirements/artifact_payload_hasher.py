"""Artifact Payload Hasher — RTC-REQ-123.

Plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-hardened-w0-7e3c9a.md``

The implementation prompt's non-negotiable §11 (and CSV row RTC-REQ-123) is
explicit:

  > Artifact inventory must verify referenced payload content_hash, not only
  > manifest/index hash.

This module recomputes SHA-256 over the **payload bytes** of every artifact
declared in a manifest. Manifest-level hashes are explicitly NOT trusted —
they are an index that the verifier independently re-derives. If a payload
is tampered with but the manifest hash is updated to match, the trick is
caught only when the verifier reads the bytes itself.

Public API
----------

- ``ArtifactPayloadCheck`` — dataclass result for one artifact
- ``hash_payload_file(path)`` — SHA-256 over file bytes
- ``recompute_payload_hashes(manifest, root)`` — apply over a manifest
- ``ManifestPayloadResult`` — bulk result for one manifest
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Iterable, Mapping


SUPPORTED_HASH_ALGORITHMS: Final[frozenset[str]] = frozenset({"sha256"})


def hash_artifact_payload(payload: bytes, algorithm: str = "sha256") -> str:
    """Hash raw artifact payload bytes with a supported algorithm."""
    alg = algorithm.lower().strip()
    if alg not in SUPPORTED_HASH_ALGORITHMS:
        raise ValueError(f"unsupported hash algorithm: {algorithm}")
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    return hashlib.new(alg, payload).hexdigest()


@dataclass(frozen=True)
class ArtifactPayloadCheck:
    """Outcome of recomputing one artifact's payload hash."""

    artifact_id: str
    payload_path: str
    expected_hash: str
    """The hash the manifest claims (NOT trusted; checked AGAINST recomputation)."""
    actual_hash: str
    """SHA-256 over the payload bytes the verifier just read."""
    match: bool
    payload_exists: bool
    payload_size_bytes: int
    expected_fail_reason: str = ""
    actual_fail_reason: str = ""

    def to_row(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "payload_path": self.payload_path,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "match": self.match,
            "payload_exists": self.payload_exists,
            "payload_size_bytes": self.payload_size_bytes,
            "expected_fail_reason": self.expected_fail_reason,
            "actual_fail_reason": self.actual_fail_reason,
        }


@dataclass(frozen=True)
class ManifestPayloadResult:
    """Bulk outcome for one manifest worth of artifacts."""

    manifest_path: str
    checks: tuple[ArtifactPayloadCheck, ...]
    total_count: int
    match_count: int
    mismatch_count: int
    missing_count: int
    legal: bool
    expected_fail_reason: str = ""
    actual_fail_reason: str = ""


def hash_payload_file(path: Path) -> tuple[str, int]:
    """Return (sha256_hex, size_bytes) for a payload file.

    Raises ``FileNotFoundError`` if the file is absent. Streams the file in
    64KB chunks so this is safe for large artifacts.
    """
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"PAYLOAD_NOT_FOUND: {path}")
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def _check_one(
    *,
    artifact_id: str,
    payload_path: Path,
    expected_hash: str | None,
) -> ArtifactPayloadCheck:
    expected = (expected_hash or "").strip().lower()
    if not payload_path.exists() or not payload_path.is_file():
        return ArtifactPayloadCheck(
            artifact_id=artifact_id,
            payload_path=str(payload_path),
            expected_hash=expected,
            actual_hash="",
            match=False,
            payload_exists=False,
            payload_size_bytes=0,
            expected_fail_reason="PAYLOAD_NOT_FOUND",
            actual_fail_reason=f"manifest references {payload_path} but it is missing",
        )
    actual_hex, size = hash_payload_file(payload_path)
    actual_hex = actual_hex.lower()
    if not expected:
        # No expected hash supplied — record actual for the report; not
        # automatically a fail (caller decides). This represents the case
        # where the manifest is being POPULATED for the first time. To
        # make this distinguishable from a real mismatch the match flag
        # is False but expected_fail_reason carries MANIFEST_HASH_NOT_DECLARED.
        return ArtifactPayloadCheck(
            artifact_id=artifact_id,
            payload_path=str(payload_path),
            expected_hash="",
            actual_hash=actual_hex,
            match=False,
            payload_exists=True,
            payload_size_bytes=size,
            expected_fail_reason="MANIFEST_HASH_NOT_DECLARED",
            actual_fail_reason="manifest does not declare an expected_hash for this payload",
        )
    if actual_hex != expected:
        return ArtifactPayloadCheck(
            artifact_id=artifact_id,
            payload_path=str(payload_path),
            expected_hash=expected,
            actual_hash=actual_hex,
            match=False,
            payload_exists=True,
            payload_size_bytes=size,
            expected_fail_reason="PAYLOAD_HASH_MISMATCH",
            actual_fail_reason=(
                f"expected={expected[:12]}... actual={actual_hex[:12]}... "
                f"path={payload_path}"
            ),
        )
    return ArtifactPayloadCheck(
        artifact_id=artifact_id,
        payload_path=str(payload_path),
        expected_hash=expected,
        actual_hash=actual_hex,
        match=True,
        payload_exists=True,
        payload_size_bytes=size,
    )


def recompute_payload_hashes(
    manifest: Mapping[str, Any] | Iterable[Mapping[str, Any]],
    root: Path,
    *,
    manifest_path: Path | None = None,
) -> ManifestPayloadResult:
    """Recompute payload hashes for every artifact entry in a manifest.

    The manifest can be either:

      - a dict with key ``artifacts`` whose value is a list of artifact entries
      - a flat list of artifact entries

    Each artifact entry MUST have at minimum:
      - ``artifact_id`` (or ``id``) — string identifier
      - ``payload_path`` (or ``path``) — repo-relative path to the payload file
      - ``expected_hash`` (or ``content_hash``, ``sha256``) — manifest's
        claimed SHA-256 (not trusted, checked AGAINST actual)

    Returns ``ManifestPayloadResult`` containing per-artifact checks AND
    aggregate counts. ``legal=True`` iff every check matched AND every
    payload existed.
    """
    if isinstance(manifest, Mapping):
        entries = list(manifest.get("artifacts") or [])
    else:
        entries = list(manifest)  # iterable of entries

    checks: list[ArtifactPayloadCheck] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        aid = (entry.get("artifact_id") or entry.get("id") or "").strip()
        rel_path = (
            entry.get("payload_path")
            or entry.get("path")
            or ""
        )
        expected = (
            entry.get("expected_hash")
            or entry.get("content_hash")
            or entry.get("sha256")
            or ""
        )
        if not aid or not rel_path:
            checks.append(ArtifactPayloadCheck(
                artifact_id=aid or "(unknown)",
                payload_path=str(rel_path),
                expected_hash=str(expected),
                actual_hash="",
                match=False,
                payload_exists=False,
                payload_size_bytes=0,
                expected_fail_reason="MANIFEST_ENTRY_INCOMPLETE",
                actual_fail_reason="entry missing artifact_id or payload_path",
            ))
            continue
        payload_path = (root / rel_path).resolve()
        checks.append(_check_one(
            artifact_id=aid, payload_path=payload_path, expected_hash=str(expected),
        ))

    total = len(checks)
    matches = sum(1 for c in checks if c.match)
    mismatches = sum(1 for c in checks if not c.match and c.payload_exists and c.expected_hash)
    missing = sum(1 for c in checks if not c.payload_exists)
    legal = total > 0 and matches == total

    expected_fail = ""
    actual_fail = ""
    if total == 0:
        legal = False
        expected_fail = "MANIFEST_HAS_NO_ARTIFACTS"
        actual_fail = "manifest contained zero artifact entries"
    elif missing > 0:
        legal = False
        expected_fail = "PAYLOADS_MISSING"
        actual_fail = f"{missing} of {total} artifact payloads are missing"
    elif mismatches > 0:
        legal = False
        expected_fail = "PAYLOAD_HASH_MISMATCH"
        actual_fail = f"{mismatches} of {total} artifact payload hashes do not match manifest"

    return ManifestPayloadResult(
        manifest_path=str(manifest_path) if manifest_path else "",
        checks=tuple(checks),
        total_count=total,
        match_count=matches,
        mismatch_count=mismatches,
        missing_count=missing,
        legal=legal,
        expected_fail_reason=expected_fail,
        actual_fail_reason=actual_fail,
    )


def load_manifest_json(path: Path) -> dict[str, Any]:
    """Read a JSON manifest fail-closed."""
    if not path.exists():
        raise FileNotFoundError(f"MANIFEST_NOT_FOUND: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


__all__ = [
    "ArtifactPayloadCheck",
    "ManifestPayloadResult",
    "SUPPORTED_HASH_ALGORITHMS",
    "hash_artifact_payload",
    "hash_payload_file",
    "recompute_payload_hashes",
    "load_manifest_json",
]
