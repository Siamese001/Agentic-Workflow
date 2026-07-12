"""Atomic, role-separated activation pointers for ADG SQLite snapshots."""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping


SnapshotRole = Literal["certified", "repair", "candidate"]
SNAPSHOT_POINTER_SCHEMA_VERSION = "adg-snapshot-pointer/v1"
POINTER_FILENAMES: dict[SnapshotRole, str] = {
    "certified": "adg_snapshot_certified.json",
    "repair": "adg_snapshot_repair.json",
    "candidate": "adg_snapshot_candidate.json",
}
_SNAPSHOT_RE = re.compile(r"^adg_indexed_(\d{8}_\d{4})\.sqlite$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SnapshotPointerError(RuntimeError):
    """A snapshot activation pointer is absent, malformed, or inconsistent."""


@dataclass(frozen=True)
class SnapshotPointer:
    role: SnapshotRole
    path: Path
    snapshot_id: str
    snapshot_sha256: str
    snapshot_size_bytes: int
    certification_status: str
    artifact_status: str
    pointer_path: Path
    published_at_utc: str
    source_artifacts: dict[str, dict[str, Any]]
    digest_verified: bool


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_role_status(role: SnapshotRole, certification_status: str, artifact_status: str) -> None:
    if role == "certified":
        if certification_status != "clean" or artifact_status != "certified":
            raise SnapshotPointerError(
                "certified pointer requires certification_status='clean' and "
                "artifact_status='certified'"
            )
        return
    if role == "repair":
        if certification_status not in {"failed", "diagnostic_only"} or artifact_status != "repair_ready":
            raise SnapshotPointerError(
                "repair pointer requires failed/diagnostic_only certification and "
                "artifact_status='repair_ready'"
            )
        return
    if artifact_status != "candidate":
        raise SnapshotPointerError("candidate pointer requires artifact_status='candidate'")


def _safe_artifact_path(adg_dir: Path, relative_path: str, *, direct_child: bool = False) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        raise SnapshotPointerError("artifact path is missing")
    raw = Path(relative_path)
    if raw.is_absolute():
        raise SnapshotPointerError(f"pointer artifact path must be relative: {relative_path!r}")
    base = adg_dir.resolve()
    candidate = (base / raw).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise SnapshotPointerError(f"pointer artifact escapes ADG directory: {relative_path!r}") from exc
    if direct_child and candidate.parent != base:
        raise SnapshotPointerError("snapshot must be a direct child of ADG directory")
    return candidate


def _artifact_ref(adg_dir: Path, path: Path, *, known_sha256: str | None = None) -> dict[str, Any]:
    base = adg_dir.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(base)
    except ValueError as exc:
        raise SnapshotPointerError(f"source artifact is outside ADG directory: {resolved}") from exc
    if not resolved.is_file():
        raise SnapshotPointerError(f"source artifact does not exist: {resolved}")
    sha = known_sha256 or _sha256(resolved)
    if not _SHA256_RE.fullmatch(sha):
        raise SnapshotPointerError(f"invalid SHA-256 for {relative.as_posix()}")
    return {
        "path": relative.as_posix(),
        "sha256": sha,
        "size_bytes": resolved.stat().st_size,
    }


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        if os.name != "nt":
            directory_fd = os.open(str(path.parent), os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def publish_snapshot_pointer(
    *,
    adg_dir: Path,
    role: SnapshotRole,
    snapshot_path: Path,
    certification_status: str,
    artifact_status: str,
    snapshot_sha256: str | None = None,
    source_artifacts: Mapping[str, Path] | None = None,
) -> Path:
    """Atomically publish one role pointer after validating all referenced files."""
    _validate_role_status(role, certification_status, artifact_status)
    adg_dir = adg_dir.resolve()
    snapshot_path = snapshot_path.resolve()
    if snapshot_path.parent != adg_dir:
        raise SnapshotPointerError("snapshot must be a direct child of ADG directory")
    match = _SNAPSHOT_RE.fullmatch(snapshot_path.name)
    if match is None:
        raise SnapshotPointerError(f"invalid timestamped snapshot filename: {snapshot_path.name}")
    if not snapshot_path.is_file():
        raise SnapshotPointerError(f"snapshot does not exist: {snapshot_path}")
    sha = snapshot_sha256 or _sha256(snapshot_path)
    if not _SHA256_RE.fullmatch(sha):
        raise SnapshotPointerError("snapshot_sha256 must be 64 lowercase hex characters")
    refs = {
        label: _artifact_ref(adg_dir, path)
        for label, path in sorted((source_artifacts or {}).items())
    }
    payload = {
        "schema_version": SNAPSHOT_POINTER_SCHEMA_VERSION,
        "role": role,
        "snapshot_id": match.group(1),
        "snapshot_filename": snapshot_path.name,
        "snapshot_sha256": sha,
        "snapshot_size_bytes": snapshot_path.stat().st_size,
        "certification_status": certification_status,
        "artifact_status": artifact_status,
        "published_at_utc": _utcnow_iso(),
        "source_artifacts": refs,
    }
    pointer_path = adg_dir / POINTER_FILENAMES[role]
    _atomic_write_json(pointer_path, payload)
    return pointer_path


def _validate_artifact_ref(adg_dir: Path, label: str, value: Any) -> None:
    if not isinstance(value, dict):
        raise SnapshotPointerError(f"source_artifacts.{label} must be an object")
    path = _safe_artifact_path(adg_dir, value.get("path"))
    if not path.is_file():
        raise SnapshotPointerError(f"source artifact missing: {path}")
    expected_size = value.get("size_bytes")
    if not isinstance(expected_size, int) or expected_size < 0 or path.stat().st_size != expected_size:
        raise SnapshotPointerError(f"source artifact size mismatch: {path}")
    expected_sha = value.get("sha256")
    if not isinstance(expected_sha, str) or not _SHA256_RE.fullmatch(expected_sha):
        raise SnapshotPointerError(f"invalid source artifact SHA-256: {path}")
    if _sha256(path) != expected_sha:
        raise SnapshotPointerError(f"source artifact SHA-256 mismatch: {path}")


def load_snapshot_pointer(
    adg_dir: Path,
    role: SnapshotRole,
    *,
    verify_digest: bool,
) -> SnapshotPointer:
    """Load and validate a role pointer; never falls back to another role."""
    adg_dir = adg_dir.resolve()
    pointer_path = adg_dir / POINTER_FILENAMES[role]
    if not pointer_path.is_file():
        raise SnapshotPointerError(f"{role} snapshot pointer is missing: {pointer_path}")
    try:
        payload = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SnapshotPointerError(f"{role} snapshot pointer is unreadable: {exc}") from exc
    if not isinstance(payload, dict):
        raise SnapshotPointerError("snapshot pointer root must be an object")
    if payload.get("schema_version") != SNAPSHOT_POINTER_SCHEMA_VERSION:
        raise SnapshotPointerError(f"unsupported snapshot pointer schema: {payload.get('schema_version')!r}")
    if payload.get("role") != role:
        raise SnapshotPointerError(f"snapshot pointer role mismatch: {payload.get('role')!r}")
    certification_status = payload.get("certification_status")
    artifact_status = payload.get("artifact_status")
    if not isinstance(certification_status, str) or not isinstance(artifact_status, str):
        raise SnapshotPointerError("snapshot pointer status fields are missing")
    _validate_role_status(role, certification_status, artifact_status)
    filename = payload.get("snapshot_filename")
    snapshot_path = _safe_artifact_path(adg_dir, filename, direct_child=True)
    match = _SNAPSHOT_RE.fullmatch(snapshot_path.name)
    if match is None or payload.get("snapshot_id") != match.group(1):
        raise SnapshotPointerError("snapshot id/filename mismatch")
    if not snapshot_path.is_file():
        raise SnapshotPointerError(f"snapshot is missing: {snapshot_path}")
    expected_size = payload.get("snapshot_size_bytes")
    if not isinstance(expected_size, int) or expected_size < 0 or snapshot_path.stat().st_size != expected_size:
        raise SnapshotPointerError("snapshot size mismatch")
    expected_sha = payload.get("snapshot_sha256")
    if not isinstance(expected_sha, str) or not _SHA256_RE.fullmatch(expected_sha):
        raise SnapshotPointerError("snapshot SHA-256 is malformed")
    if verify_digest and _sha256(snapshot_path) != expected_sha:
        raise SnapshotPointerError("snapshot SHA-256 mismatch")
    source_refs = payload.get("source_artifacts", {})
    if not isinstance(source_refs, dict):
        raise SnapshotPointerError("source_artifacts must be an object")
    for label, value in source_refs.items():
        _validate_artifact_ref(adg_dir, str(label), value)
    return SnapshotPointer(
        role=role,
        path=snapshot_path,
        snapshot_id=match.group(1),
        snapshot_sha256=expected_sha,
        snapshot_size_bytes=expected_size,
        certification_status=certification_status,
        artifact_status=artifact_status,
        pointer_path=pointer_path,
        published_at_utc=str(payload.get("published_at_utc") or ""),
        source_artifacts=source_refs,
        digest_verified=verify_digest,
    )


def protected_snapshot_run_ids(adg_dir: Path) -> frozenset[str]:
    """Return run IDs that retention must never archive."""
    try:
        pointer = load_snapshot_pointer(adg_dir, "certified", verify_digest=False)
    except SnapshotPointerError:
        return frozenset()
    return frozenset((pointer.snapshot_id,))
