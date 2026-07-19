"""Read-only runtime contract for offline-derived ingestion snapshots."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.active_config_snapshot import canonical_json_bytes, sha256_bytes

INGESTION_SNAPSHOT_SCHEMA_VERSION = "ingestion-snapshot/v1"
INGESTION_BUILDER_VERSION = "ingestion-snapshot-packager/v1"
SNAPSHOT_POINTER_SCHEMA_VERSION = "snapshot-pointer/v1"


class IngestionSnapshotFailureReason(str, Enum):
    SNAPSHOT_MISSING = "SNAPSHOT_MISSING"
    SNAPSHOT_STALE = "SNAPSHOT_STALE"
    SNAPSHOT_MALFORMED = "SNAPSHOT_MALFORMED"
    INPUT_DIGEST_MISMATCH = "INPUT_DIGEST_MISMATCH"
    CONFIG_DIGEST_MISMATCH = "CONFIG_DIGEST_MISMATCH"
    SCHEMA_VERSION_MISMATCH = "SCHEMA_VERSION_MISMATCH"
    BUILDER_VERSION_MISMATCH = "BUILDER_VERSION_MISMATCH"
    SNAPSHOT_VALIDATION_FAILED = "SNAPSHOT_VALIDATION_FAILED"
    SNAPSHOT_PUBLICATION_INCOMPLETE = "SNAPSHOT_PUBLICATION_INCOMPLETE"
    REBUILD_REQUIRED = "REBUILD_REQUIRED"
    REBUILD_NOT_AUTHORIZED = "REBUILD_NOT_AUTHORIZED"


class IngestionSnapshotError(RuntimeError):
    def __init__(self, reason: IngestionSnapshotFailureReason, detail: str = "") -> None:
        self.reason = reason
        message = reason.value if not detail else f"{reason.value}: {detail}"
        super().__init__(message)


@dataclass(frozen=True)
class IngestionLoadRequestV1:
    snapshot_root: Path
    expected_input_digest: str
    expected_configuration_digest: str
    expected_input_schema_version: str
    expected_snapshot_schema_version: str = INGESTION_SNAPSHOT_SCHEMA_VERSION
    expected_builder_version: str = INGESTION_BUILDER_VERSION
    expected_generation_id: str | None = None


@dataclass(frozen=True)
class IngestionSnapshotV1:
    generation_id: str
    schema_version: str
    builder_version: str
    input_schema_version: str
    input_digest: str
    active_configuration_digest: str
    payload_digest: str
    canonical_payload_bytes: bytes
    payload: dict[str, Any]


def validate_canonical_ingestion_payload(payload_bytes: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(payload_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_MALFORMED) from exc
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != payload_bytes:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_VALIDATION_FAILED)
    chunks = payload.get("chunks")
    if not isinstance(chunks, list):
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_VALIDATION_FAILED)
    for chunk in chunks:
        if not isinstance(chunk, dict) or not isinstance(chunk.get("text"), str) or not chunk["text"]:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_VALIDATION_FAILED)
        if "metadata" in chunk and not isinstance(chunk["metadata"], dict):
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_VALIDATION_FAILED)
    return payload


def build_ingestion_snapshot(
    payload_bytes: bytes,
    *,
    input_schema_version: str,
    active_configuration_digest: str,
) -> tuple[IngestionSnapshotV1, bytes]:
    payload = validate_canonical_ingestion_payload(payload_bytes)
    if not input_schema_version or len(active_configuration_digest) != 64:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_VALIDATION_FAILED)
    input_digest = sha256_bytes(payload_bytes)
    core = {
        "active_configuration_digest": active_configuration_digest,
        "artifact_classification": "OFFLINE_DERIVED_ARTIFACT",
        "builder_version": INGESTION_BUILDER_VERSION,
        "input_digest": input_digest,
        "input_schema_version": input_schema_version,
        "payload_base64": base64.b64encode(payload_bytes).decode("ascii"),
        "payload_byte_length": len(payload_bytes),
        "payload_digest": input_digest,
        "schema_version": INGESTION_SNAPSHOT_SCHEMA_VERSION,
    }
    generation_digest = sha256_bytes(canonical_json_bytes(core))
    generation_id = f"ingestion-{generation_digest[:24]}"
    raw_snapshot = canonical_json_bytes({**core, "generation_id": generation_id})
    return (
        IngestionSnapshotV1(
            generation_id=generation_id,
            schema_version=INGESTION_SNAPSHOT_SCHEMA_VERSION,
            builder_version=INGESTION_BUILDER_VERSION,
            input_schema_version=input_schema_version,
            input_digest=input_digest,
            active_configuration_digest=active_configuration_digest,
            payload_digest=input_digest,
            canonical_payload_bytes=payload_bytes,
            payload=payload,
        ),
        raw_snapshot,
    )


def _decode_canonical_json(raw: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_MALFORMED) from exc
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != raw:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_MALFORMED)
    return payload


def _snapshot_from_payload(payload: dict[str, Any]) -> IngestionSnapshotV1:
    required = {
        "active_configuration_digest",
        "artifact_classification",
        "builder_version",
        "generation_id",
        "input_digest",
        "input_schema_version",
        "payload_base64",
        "payload_byte_length",
        "payload_digest",
        "schema_version",
    }
    if set(payload) != required or payload.get("artifact_classification") != "OFFLINE_DERIVED_ARTIFACT":
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_MALFORMED)
    try:
        payload_bytes = base64.b64decode(payload["payload_base64"], validate=True)
    except (ValueError, TypeError) as exc:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_MALFORMED) from exc
    if len(payload_bytes) != payload["payload_byte_length"]:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_VALIDATION_FAILED)
    digest = sha256_bytes(payload_bytes)
    if digest != payload["payload_digest"] or digest != payload["input_digest"]:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.INPUT_DIGEST_MISMATCH)
    decoded_payload = validate_canonical_ingestion_payload(payload_bytes)
    core = {key: value for key, value in payload.items() if key != "generation_id"}
    expected_generation = f"ingestion-{sha256_bytes(canonical_json_bytes(core))[:24]}"
    if payload["generation_id"] != expected_generation:
        raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_VALIDATION_FAILED)
    return IngestionSnapshotV1(
        generation_id=payload["generation_id"],
        schema_version=payload["schema_version"],
        builder_version=payload["builder_version"],
        input_schema_version=payload["input_schema_version"],
        input_digest=payload["input_digest"],
        active_configuration_digest=payload["active_configuration_digest"],
        payload_digest=payload["payload_digest"],
        canonical_payload_bytes=payload_bytes,
        payload=decoded_payload,
    )


class IngestionSnapshotLoaderV1:
    """Load an immutable snapshot without creating, repairing, or publishing state."""

    def load(self, request: IngestionLoadRequestV1) -> IngestionSnapshotV1:
        root = Path(request.snapshot_root)
        pointer_path = root / "active.json"
        try:
            pointer_before = pointer_path.read_bytes()
        except FileNotFoundError as exc:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_MISSING) from exc
        pointer = _decode_canonical_json(pointer_before)
        required_pointer = {"generation_id", "schema_version", "snapshot_digest", "snapshot_path", "state"}
        if set(pointer) != required_pointer or pointer.get("schema_version") != SNAPSHOT_POINTER_SCHEMA_VERSION:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_MALFORMED)
        if pointer.get("state") != "ACTIVE":
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_STALE)
        if request.expected_generation_id and pointer["generation_id"] != request.expected_generation_id:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_STALE)
        snapshot_path = (root / pointer["snapshot_path"]).resolve()
        if not snapshot_path.is_relative_to(root.resolve()):
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_MALFORMED)
        try:
            raw_snapshot = snapshot_path.read_bytes()
        except FileNotFoundError as exc:
            raise IngestionSnapshotError(
                IngestionSnapshotFailureReason.SNAPSHOT_PUBLICATION_INCOMPLETE
            ) from exc
        if sha256_bytes(raw_snapshot) != pointer["snapshot_digest"]:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_PUBLICATION_INCOMPLETE)
        snapshot = _snapshot_from_payload(_decode_canonical_json(raw_snapshot))
        if pointer["generation_id"] != snapshot.generation_id:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_PUBLICATION_INCOMPLETE)
        if snapshot.schema_version != request.expected_snapshot_schema_version:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SCHEMA_VERSION_MISMATCH)
        if snapshot.builder_version != request.expected_builder_version:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.BUILDER_VERSION_MISMATCH)
        if snapshot.input_schema_version != request.expected_input_schema_version:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SCHEMA_VERSION_MISMATCH)
        if snapshot.input_digest != request.expected_input_digest:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.INPUT_DIGEST_MISMATCH)
        if snapshot.active_configuration_digest != request.expected_configuration_digest:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.CONFIG_DIGEST_MISMATCH)
        try:
            pointer_after = pointer_path.read_bytes()
        except FileNotFoundError as exc:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_STALE) from exc
        if pointer_after != pointer_before:
            raise IngestionSnapshotError(IngestionSnapshotFailureReason.SNAPSHOT_STALE)
        return snapshot


__all__ = [
    "INGESTION_BUILDER_VERSION",
    "INGESTION_SNAPSHOT_SCHEMA_VERSION",
    "IngestionLoadRequestV1",
    "IngestionSnapshotError",
    "IngestionSnapshotFailureReason",
    "IngestionSnapshotLoaderV1",
    "IngestionSnapshotV1",
    "build_ingestion_snapshot",
    "validate_canonical_ingestion_payload",
]
