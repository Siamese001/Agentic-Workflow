"""Contracts and canonical hashing for the apps_rg governed L2 authority path."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any, Mapping


class L2AuthorityError(ValueError):
    """Fail-closed L2 authority validation error with a stable reason code."""

    def __init__(self, code: str, reason: str, *, field_name: str = "") -> None:
        self.code = str(code)
        self.reason = str(reason)
        self.field_name = str(field_name)
        super().__init__(f"{self.code}: {self.reason}")


@dataclass(frozen=True, slots=True)
class AuthorityGateReceipt:
    gate_id: str
    status: str
    decisive_reason_code: str
    checked_fields: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status != "PASS":
            raise ValueError("AuthorityGateReceipt may only represent an explicit PASS")

    @property
    def ref(self) -> str:
        return f"{self.gate_id}:PASS:{self.decisive_reason_code}"


@dataclass(frozen=True, slots=True)
class SignedAppsRgL2ExecutionPacket:
    schema_version: str
    request_id: str
    run_id: str
    app_id: str
    trace_id: str
    tenant_id: str
    route_id: str
    workflow_id: str
    node_id: str
    step_id: str
    execution_lane: str
    capability_scope_digest: str
    sandbox_envelope_digest: str
    sandbox_required: bool
    egress_policy_ref: str
    policy_hash: str
    blueprint_hash: str
    prompt_hash: str
    replay_key: str
    attempt_number: int
    attempt_seed: str
    snapshot_manifest: str
    idempotency_key: str
    registry_digest_set: tuple[str, ...]
    compiled_prompt_artifact_ref: str
    final_evidence_contract_ref: str
    canonical_provider: str
    target_model: str
    allowed_tools: tuple[str, ...]
    allowed_models: tuple[str, ...]
    allowed_networks: tuple[str, ...]
    allowed_file_roots: tuple[str, ...]
    side_effect_class: str
    budget: Mapping[str, Any]
    signature_chain: tuple[str, ...]
    signature_chain_digest: str
    packet_signature_algorithm: str = "HMAC-SHA256"
    packet_signing_key_ref: str = "APPS_RG_ROUTE_HMAC_SECRET"
    packet_signature: str = ""
    packet_digest: str = ""

    def unsigned_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("packet_signature", None)
        payload.pop("packet_digest", None)
        return payload

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FrozenExecutionRoom:
    schema_version: str
    packet_digest: str
    route_id: str
    workflow_id: str
    node_id: str
    step_id: str
    execution_lane: str
    capability_scope_digest: str
    sandbox_envelope_digest: str
    sandbox_required: bool
    egress_policy_ref: str
    policy_hash: str
    blueprint_hash: str
    prompt_hash: str
    replay_key: str
    attempt_seed: str
    snapshot_manifest: str
    idempotency_key: str
    registry_digest_set: tuple[str, ...]
    provider_lane: str
    model_id: str
    filesystem_view: tuple[str, ...]
    network_rules: tuple[str, ...]
    secrets_scope: str
    locale: str
    budget: Mapping[str, Any]
    no_direct_l4_path: bool = True
    proposed_diff_only: bool = True
    persistence_disabled: bool = True
    room_digest: str = ""

    def unsigned_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("room_digest", None)
        return payload


@dataclass(frozen=True, slots=True)
class ReceiptBundleResult:
    sealed: Any
    bundle: Mapping[str, Any]


def _string(value: Any) -> str:
    return str(value or "").strip()


def _tuple_strings(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()) if str(item).strip())


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _require(condition: bool, code: str, reason: str, field_name: str = "") -> None:
    if not condition:
        raise L2AuthorityError(code, reason, field_name=field_name)


__all__ = [
    "AuthorityGateReceipt",
    "FrozenExecutionRoom",
    "L2AuthorityError",
    "ReceiptBundleResult",
    "SignedAppsRgL2ExecutionPacket",
    "_jsonable",
    "_require",
    "_string",
    "_tuple_strings",
    "canonical_json_bytes",
    "sha256_hex",
]
