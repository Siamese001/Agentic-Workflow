"""Last-marker-wins sealing for the mandatory-output bundle."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Collection, Mapping, Sequence
from pathlib import Path

MANDATORY_OUTPUT_COMMIT_MANIFEST = "apps_rg_mandatory_output_commit_manifest.json"
_SCHEMA_VERSION = "apps_rg.mandatory_output_commit_manifest.v1"
PRODUCT_MANDATORY_OUTPUT_PROFILE = "apps_rg.mandatory_outputs.product.v1"
CLOSEOUT_MANDATORY_OUTPUT_PROFILE = "apps_rg.mandatory_outputs.closeout.v1"


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _fsync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_directory_tree(path: Path) -> None:
    directories = [path, *(item for item in path.rglob("*") if item.is_dir())]
    for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        _fsync_dir(directory)


def _normalized_artifact_set(values: Collection[str]) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        rel = Path(str(value))
        if rel.is_absolute() or ".." in rel.parts or not rel.parts:
            raise ValueError(f"invalid mandatory artifact reference: {value}")
        normalized.add(rel.as_posix())
    return normalized


def begin_mandatory_output_transaction(run_root: Path) -> None:
    root = Path(run_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    marker = root / MANDATORY_OUTPUT_COMMIT_MANIFEST
    if marker.exists():
        marker.unlink()
        _fsync_dir(root)


def seal_mandatory_output_bundle(
    run_root: Path,
    files: Mapping[str, bytes],
    *,
    additional_files: Mapping[str, Path] | None = None,
    profile_id: str = "apps_rg.mandatory_outputs.custom.v1",
    required_artifacts: Sequence[str] | None = None,
) -> dict[str, object]:
    """Publish exact output bytes and write the commit manifest last."""

    root = Path(run_root).resolve()
    begin_mandatory_output_transaction(root)
    staging = Path(tempfile.mkdtemp(prefix=".mandatory-output-", dir=root))
    try:
        digests: dict[str, str] = {}
        sizes: dict[str, int] = {}
        for relative, data in sorted(files.items()):
            rel = Path(relative)
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError(f"mandatory output path escapes run root: {relative}")
            path = staging / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            with path.open("rb") as handle:
                os.fsync(handle.fileno())
            digests[rel.as_posix()] = _sha256(data)
            sizes[rel.as_posix()] = len(data)
        _fsync_directory_tree(staging)

        for relative in sorted(files):
            rel = Path(relative)
            destination = root / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging / rel, destination)
            _fsync_dir(destination.parent)

        for name, path in sorted((additional_files or {}).items()):
            resolved = Path(path).resolve()
            if not resolved.is_file() or not (
                resolved == root or root in resolved.parents
            ):
                raise ValueError(f"uncontained mandatory artifact: {name}")
            data = resolved.read_bytes()
            relative = resolved.relative_to(root).as_posix()
            digests[relative] = _sha256(data)
            sizes[relative] = len(data)

        artifact_set = set(digests)
        required_set = (
            _normalized_artifact_set(required_artifacts)
            if required_artifacts is not None
            else artifact_set
        )
        if artifact_set != required_set:
            missing = sorted(required_set - artifact_set)
            extra = sorted(artifact_set - required_set)
            raise ValueError(
                "mandatory artifact set mismatch: "
                f"missing={missing}, extra={extra}"
            )

        manifest = {
            "schema_version": _SCHEMA_VERSION,
            "commit_protocol": "write_fsync_replace_marker_last.v1",
            "profile_id": str(profile_id),
            "required_artifacts": sorted(required_set),
            "artifacts": {
                name: {"sha256": digests[name], "byte_length": sizes[name]}
                for name in sorted(digests)
            },
        }
        seed = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        manifest["bundle_digest"] = _sha256(seed)
        marker_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        marker_tmp = staging / MANDATORY_OUTPUT_COMMIT_MANIFEST
        marker_tmp.write_bytes(marker_bytes)
        with marker_tmp.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(marker_tmp, root / MANDATORY_OUTPUT_COMMIT_MANIFEST)
        _fsync_dir(root)
        return manifest
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def validate_mandatory_output_seal(
    run_root: Path,
    *,
    expected_profile_id: str = "",
    expected_artifacts: Collection[str] | None = None,
) -> tuple[bool, list[str]]:
    root = Path(run_root).resolve()
    marker = root / MANDATORY_OUTPUT_COMMIT_MANIFEST
    try:
        manifest = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return False, ["mandatory_output_commit_manifest_missing_or_malformed"]
    seed = dict(manifest)
    claimed_root = str(seed.pop("bundle_digest", "") or "")
    computed_root = _sha256(
        json.dumps(seed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    errors: list[str] = []
    if manifest.get("schema_version") != _SCHEMA_VERSION:
        errors.append("mandatory_output_commit_manifest_schema_invalid")
    if claimed_root != computed_root:
        errors.append("mandatory_output_bundle_digest_mismatch")
    if expected_profile_id and manifest.get("profile_id") != expected_profile_id:
        errors.append("mandatory_output_profile_mismatch")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        errors.append("mandatory_output_artifact_map_missing")
        return False, errors
    required = manifest.get("required_artifacts")
    if not isinstance(required, list) or not required:
        errors.append("mandatory_output_required_artifact_set_missing")
        required_set: set[str] = set()
    else:
        try:
            required_set = _normalized_artifact_set(required)
        except ValueError:
            errors.append("mandatory_output_required_artifact_set_invalid")
            required_set = set()
    declared_set = {str(item) for item in artifacts}
    if required_set != declared_set:
        errors.append("mandatory_output_declared_artifact_set_mismatch")
    if expected_artifacts is not None:
        try:
            expected_set = _normalized_artifact_set(expected_artifacts)
        except ValueError:
            errors.append("mandatory_output_expected_artifact_set_invalid")
            expected_set = set()
        if expected_set != declared_set:
            errors.append("mandatory_output_expected_artifact_set_mismatch")
    for relative, metadata in sorted(artifacts.items()):
        rel = Path(str(relative))
        path = (root / rel).resolve()
        if rel.is_absolute() or ".." in rel.parts or root not in path.parents or not path.is_file():
            errors.append(f"mandatory_output_artifact_missing_or_uncontained:{relative}")
            continue
        data = path.read_bytes()
        if not isinstance(metadata, dict) or metadata.get("sha256") != _sha256(data):
            errors.append(f"mandatory_output_artifact_digest_mismatch:{relative}")
        if not isinstance(metadata, dict) or metadata.get("byte_length") != len(data):
            errors.append(f"mandatory_output_artifact_length_mismatch:{relative}")
    return not errors, errors


__all__ = [
    "CLOSEOUT_MANDATORY_OUTPUT_PROFILE",
    "MANDATORY_OUTPUT_COMMIT_MANIFEST",
    "PRODUCT_MANDATORY_OUTPUT_PROFILE",
    "begin_mandatory_output_transaction",
    "seal_mandatory_output_bundle",
    "validate_mandatory_output_seal",
]
