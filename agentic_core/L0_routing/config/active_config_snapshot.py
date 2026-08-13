"""Immutable exact-byte active configuration snapshots."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

ACTIVE_CONFIG_SCHEMA_VERSION = "active-config-snapshot/v1"
SNAPSHOT_POINTER_SCHEMA_VERSION = "snapshot-pointer/v1"
REQUIRED_COMPONENT_NAMES = frozenset({"budget", "model", "policy", "routing"})


class ActiveConfigFailureReason(str, Enum):
    ACTIVE_CONFIG_MISSING = "ACTIVE_CONFIG_MISSING"
    ACTIVE_CONFIG_MALFORMED = "ACTIVE_CONFIG_MALFORMED"
    ACTIVE_CONFIG_VERSION_UNSUPPORTED = "ACTIVE_CONFIG_VERSION_UNSUPPORTED"
    ACTIVE_CONFIG_NONCANONICAL = "ACTIVE_CONFIG_NONCANONICAL"
    ACTIVE_CONFIG_DIGEST_MISMATCH = "ACTIVE_CONFIG_DIGEST_MISMATCH"
    ACTIVE_CONFIG_PROFILE_MISMATCH = "ACTIVE_CONFIG_PROFILE_MISMATCH"
    ACTIVE_CONFIG_SOURCE_CHANGED = "ACTIVE_CONFIG_SOURCE_CHANGED"
    ACTIVE_CONFIG_DRIFT_DURING_OPERATION = "ACTIVE_CONFIG_DRIFT_DURING_OPERATION"
    ACTIVE_CONFIG_INCOMPLETE = "ACTIVE_CONFIG_INCOMPLETE"
    ACTIVE_CONFIG_UNKNOWN = "ACTIVE_CONFIG_UNKNOWN"


class ActiveConfigSnapshotError(RuntimeError):
    def __init__(self, reason: ActiveConfigFailureReason, detail: str = "") -> None:
        self.reason = reason
        message = reason.value if not detail else f"{reason.value}: {detail}"
        super().__init__(message)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ActiveConfigComponentV1:
    name: str
    byte_length: int
    sha256: str
    content_base64: str

    def exact_bytes(self) -> bytes:
        try:
            payload = base64.b64decode(self.content_base64, validate=True)
        except (ValueError, TypeError) as exc:
            raise ActiveConfigSnapshotError(
                ActiveConfigFailureReason.ACTIVE_CONFIG_MALFORMED,
                f"component {self.name!r} is not valid base64",
            ) from exc
        if len(payload) != self.byte_length or sha256_bytes(payload) != self.sha256:
            raise ActiveConfigSnapshotError(
                ActiveConfigFailureReason.ACTIVE_CONFIG_DIGEST_MISMATCH,
                f"component {self.name!r} bytes do not match their binding",
            )
        return payload

    def to_payload(self) -> dict[str, Any]:
        return {
            "byte_length": self.byte_length,
            "content_base64": self.content_base64,
            "name": self.name,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class ActiveConfigSnapshotV1:
    snapshot_id: str
    schema_version: str
    selected_profile_id: str
    snapshot_boundary_id: str
    components: tuple[ActiveConfigComponentV1, ...]
    configuration_digest: str
    _bound_hashes: Mapping[str, str] = field(repr=False, compare=False)

    def hashes(self) -> Mapping[str, str]:
        """Return immutable, already-bound digest data without performing reads."""
        return self._bound_hashes


def _component_payloads(components: tuple[ActiveConfigComponentV1, ...]) -> list[dict[str, Any]]:
    return [component.to_payload() for component in components]


def _configuration_core(
    *,
    components: tuple[ActiveConfigComponentV1, ...],
    selected_profile_id: str,
    snapshot_boundary_id: str,
) -> dict[str, Any]:
    return {
        "components": _component_payloads(components),
        "schema_version": ACTIVE_CONFIG_SCHEMA_VERSION,
        "selected_profile_id": selected_profile_id,
        "snapshot_boundary_id": snapshot_boundary_id,
    }


def build_active_config_snapshot(
    component_bytes: Mapping[str, bytes],
    *,
    selected_profile_id: str,
    snapshot_boundary_id: str,
) -> tuple[ActiveConfigSnapshotV1, bytes]:
    if not selected_profile_id or not snapshot_boundary_id:
        raise ActiveConfigSnapshotError(
            ActiveConfigFailureReason.ACTIVE_CONFIG_INCOMPLETE,
            "profile and snapshot boundary are required",
        )
    names = frozenset(component_bytes)
    if names != REQUIRED_COMPONENT_NAMES:
        missing = sorted(REQUIRED_COMPONENT_NAMES - names)
        extra = sorted(names - REQUIRED_COMPONENT_NAMES)
        raise ActiveConfigSnapshotError(
            ActiveConfigFailureReason.ACTIVE_CONFIG_INCOMPLETE,
            f"missing={missing!r} extra={extra!r}",
        )
    components = tuple(
        ActiveConfigComponentV1(
            name=name,
            byte_length=len(component_bytes[name]),
            sha256=sha256_bytes(component_bytes[name]),
            content_base64=base64.b64encode(component_bytes[name]).decode("ascii"),
        )
        for name in sorted(component_bytes)
    )
    core = _configuration_core(
        components=components,
        selected_profile_id=selected_profile_id,
        snapshot_boundary_id=snapshot_boundary_id,
    )
    configuration_digest = sha256_bytes(canonical_json_bytes(core))
    snapshot_id = f"active-config-{configuration_digest[:24]}"
    payload = {
        **core,
        "configuration_digest": configuration_digest,
        "snapshot_id": snapshot_id,
    }
    bound_hashes = MappingProxyType({f"{component.name}_hash": component.sha256 for component in components})
    snapshot = ActiveConfigSnapshotV1(
        snapshot_id=snapshot_id,
        schema_version=ACTIVE_CONFIG_SCHEMA_VERSION,
        selected_profile_id=selected_profile_id,
        snapshot_boundary_id=snapshot_boundary_id,
        components=components,
        configuration_digest=configuration_digest,
        _bound_hashes=bound_hashes,
    )
    return snapshot, canonical_json_bytes(payload)


def _decode_canonical_snapshot(raw: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_MALFORMED) from exc
    if not isinstance(payload, dict):
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_MALFORMED)
    if canonical_json_bytes(payload) != raw:
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_NONCANONICAL)
    return payload


def _snapshot_from_payload(payload: dict[str, Any]) -> ActiveConfigSnapshotV1:
    required = {
        "components",
        "configuration_digest",
        "schema_version",
        "selected_profile_id",
        "snapshot_boundary_id",
        "snapshot_id",
    }
    if set(payload) != required:
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_INCOMPLETE)
    if payload["schema_version"] != ACTIVE_CONFIG_SCHEMA_VERSION:
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_VERSION_UNSUPPORTED)
    if not isinstance(payload["components"], list):
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_MALFORMED)
    try:
        components = tuple(
            ActiveConfigComponentV1(
                name=item["name"],
                byte_length=item["byte_length"],
                sha256=item["sha256"],
                content_base64=item["content_base64"],
            )
            for item in payload["components"]
        )
    except (KeyError, TypeError) as exc:
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_MALFORMED) from exc
    names = {component.name for component in components}
    if names != REQUIRED_COMPONENT_NAMES or len(components) != len(REQUIRED_COMPONENT_NAMES):
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_INCOMPLETE)
    for component in components:
        component.exact_bytes()
    core = _configuration_core(
        components=components,
        selected_profile_id=payload["selected_profile_id"],
        snapshot_boundary_id=payload["snapshot_boundary_id"],
    )
    digest = sha256_bytes(canonical_json_bytes(core))
    if payload["configuration_digest"] != digest:
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_DIGEST_MISMATCH)
    if payload["snapshot_id"] != f"active-config-{digest[:24]}":
        raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_DIGEST_MISMATCH)
    hashes = MappingProxyType({f"{component.name}_hash": component.sha256 for component in components})
    return ActiveConfigSnapshotV1(
        snapshot_id=payload["snapshot_id"],
        schema_version=payload["schema_version"],
        selected_profile_id=payload["selected_profile_id"],
        snapshot_boundary_id=payload["snapshot_boundary_id"],
        components=components,
        configuration_digest=digest,
        _bound_hashes=hashes,
    )


class ActiveConfigSnapshotProviderV1:
    """Read and bind one immutable configuration snapshot from an explicit root."""

    def __init__(
        self,
        *,
        snapshot_root: Path,
        selected_profile_id: str,
        snapshot_boundary_id: str,
    ) -> None:
        self._snapshot_root = Path(snapshot_root)
        self._selected_profile_id = selected_profile_id
        self._snapshot_boundary_id = snapshot_boundary_id
        self._loaded_snapshot: ActiveConfigSnapshotV1 | None = None

    def load(self) -> ActiveConfigSnapshotV1:
        if self._loaded_snapshot is not None:
            return self._loaded_snapshot
        pointer_path = self._snapshot_root / "active.json"
        try:
            pointer_before = pointer_path.read_bytes()
        except FileNotFoundError as exc:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_MISSING) from exc
        pointer = _decode_canonical_snapshot(pointer_before)
        expected_pointer_keys = {"generation_id", "schema_version", "snapshot_digest", "snapshot_path", "state"}
        if set(pointer) != expected_pointer_keys:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_UNKNOWN)
        if pointer["schema_version"] != SNAPSHOT_POINTER_SCHEMA_VERSION:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_VERSION_UNSUPPORTED)
        if pointer["state"] != "ACTIVE":
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_UNKNOWN)
        snapshot_path = (self._snapshot_root / pointer["snapshot_path"]).resolve()
        root = self._snapshot_root.resolve()
        if not snapshot_path.is_relative_to(root):
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_UNKNOWN)
        try:
            raw_snapshot = snapshot_path.read_bytes()
        except FileNotFoundError as exc:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_INCOMPLETE) from exc
        if sha256_bytes(raw_snapshot) != pointer["snapshot_digest"]:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_DIGEST_MISMATCH)
        snapshot = _snapshot_from_payload(_decode_canonical_snapshot(raw_snapshot))
        if pointer["generation_id"] != snapshot.snapshot_id:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_DIGEST_MISMATCH)
        if snapshot.selected_profile_id != self._selected_profile_id:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_PROFILE_MISMATCH)
        if snapshot.snapshot_boundary_id != self._snapshot_boundary_id:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_SOURCE_CHANGED)
        try:
            pointer_after = pointer_path.read_bytes()
        except FileNotFoundError as exc:
            raise ActiveConfigSnapshotError(
                ActiveConfigFailureReason.ACTIVE_CONFIG_DRIFT_DURING_OPERATION
            ) from exc
        if pointer_after != pointer_before:
            raise ActiveConfigSnapshotError(ActiveConfigFailureReason.ACTIVE_CONFIG_DRIFT_DURING_OPERATION)
        self._loaded_snapshot = snapshot
        return snapshot


__all__ = [
    "ACTIVE_CONFIG_SCHEMA_VERSION",
    "ActiveConfigComponentV1",
    "ActiveConfigFailureReason",
    "ActiveConfigSnapshotError",
    "ActiveConfigSnapshotProviderV1",
    "ActiveConfigSnapshotV1",
    "build_active_config_snapshot",
    "canonical_json_bytes",
    "sha256_bytes",
]
