"""Lossless persistence for the canonical Apps RG ``ValidatedRequest``."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

CANONICAL_APPS_RG_VALIDATED_REQUEST_FILENAME = "apps_rg_u0_validated_request.json"
_SCHEMA_VERSION = "apps_rg.validated_request_contract.v1"


class ValidatedRequestContractError(ValueError):
    """The persisted U0 contract is absent, malformed, or digest-inconsistent."""


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    if is_dataclass(value):
        return _jsonable(asdict(value))
    raise ValidatedRequestContractError(
        f"ValidatedRequest contains a non-serializable value: {type(value).__name__}"
    )


def _artifact_hash(document: Mapping[str, Any]) -> str:
    body = {key: value for key, value in document.items() if key != "artifact_hash"}
    raw = json.dumps(
        body,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def build_validated_request_contract(
    validated_request: ValidatedRequest,
    *,
    consumer_stage: str,
) -> dict[str, Any]:
    """Build a digest-bound envelope without changing the U0 contract."""
    payload = _jsonable(validated_request)
    if not isinstance(payload, dict):
        raise ValidatedRequestContractError("ValidatedRequest payload must serialize to an object")
    receipt = payload.get("authority_validation_receipt")
    if not isinstance(receipt, dict):
        raise ValidatedRequestContractError(
            "ValidatedRequest authority_validation_receipt must serialize to an object"
        )
    document: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "contract_type": "ValidatedRequest",
        "contract_version": "apps_rg_spine_front_contracts_v1",
        "producer_stage": "U0",
        "consumer_stage": str(consumer_stage or "L1"),
        "request_id": str(validated_request.request_id or ""),
        "run_id": str(validated_request.run_id or ""),
        "trace_id": str(validated_request.trace_id or ""),
        "trace_root": str(validated_request.trace_root or validated_request.trace_id or ""),
        "tenant_id": str(validated_request.tenant_id or ""),
        "payload_digest": str(validated_request.payload_digest or ""),
        "authority_contract_id": str(receipt.get("authority_contract_id") or ""),
        "authority_receipt_digest": str(receipt.get("authority_receipt_digest") or ""),
        "validation_status": (
            "PASS" if receipt.get("validation_passed") is True else "FAIL"
        ),
        "payload": payload,
    }
    document["artifact_hash"] = _artifact_hash(document)
    return document


def write_validated_request_contract(
    path: Path,
    validated_request: ValidatedRequest,
    *,
    consumer_stage: str,
) -> Path:
    document = build_validated_request_contract(
        validated_request,
        consumer_stage=consumer_stage,
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _dataclass_kwargs(cls: type, body: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {item.name for item in fields(cls)}
    return {key: value for key, value in body.items() if key in allowed}


def _tuple_values(body: dict[str, Any], *names: str) -> None:
    for name in names:
        value = body.get(name)
        if isinstance(value, list):
            body[name] = tuple(value)


def _deserialize_validated_request(payload: Mapping[str, Any]) -> ValidatedRequest:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.runtime.contracts.posture import RuntimePosture
    from agentic_core.runtime.u0.reflection_receipt import AppsRgU0ReflectionReceipt
    from apps_rg.runtime.bindings.u0_binding import AppsRgU0AuthorityReceipt

    body = dict(payload)
    receipt_raw = body.get("authority_validation_receipt")
    if not isinstance(receipt_raw, Mapping):
        raise ValidatedRequestContractError(
            "authority_validation_receipt is missing or malformed"
        )
    receipt_body = dict(receipt_raw)
    _tuple_values(receipt_body, "forbidden_fields_checked")
    try:
        body["authority_validation_receipt"] = AppsRgU0AuthorityReceipt(
            **_dataclass_kwargs(AppsRgU0AuthorityReceipt, receipt_body)
        )
    except (TypeError, ValueError) as exc:
        raise ValidatedRequestContractError(
            f"authority_validation_receipt is malformed: {exc}"
        ) from exc

    posture_raw = body.get("posture")
    if isinstance(posture_raw, Mapping):
        body["posture"] = RuntimePosture(
            **_dataclass_kwargs(RuntimePosture, posture_raw)
        )

    reflection_raw = body.get("reflection_receipt")
    if isinstance(reflection_raw, Mapping):
        reflection_body = dict(reflection_raw)
        _tuple_values(
            reflection_body,
            "deferred_reasons",
            "silently_dropped",
            "unknown_mappings",
        )
        if isinstance(reflection_body.get("deferred_reasons"), tuple):
            reflection_body["deferred_reasons"] = tuple(
                tuple(item) if isinstance(item, list) else item
                for item in reflection_body["deferred_reasons"]
            )
        body["reflection_receipt"] = AppsRgU0ReflectionReceipt(
            **_dataclass_kwargs(AppsRgU0ReflectionReceipt, reflection_body)
        )

    _tuple_values(
        body,
        "otel_span_refs",
        "audit_refs",
        "gate_verdict_refs",
        "snapshot_refs",
    )
    try:
        return ValidatedRequest(**_dataclass_kwargs(ValidatedRequest, body))
    except (TypeError, ValueError) as exc:
        raise ValidatedRequestContractError(
            f"ValidatedRequest payload is malformed: {exc}"
        ) from exc


def load_validated_request_contract(path: Path) -> ValidatedRequest:
    path = Path(path)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidatedRequestContractError(
            f"cannot read ValidatedRequest contract {path}: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise ValidatedRequestContractError("ValidatedRequest contract must be a JSON object")
    observed_hash = str(document.get("artifact_hash") or "")
    if not observed_hash or observed_hash != _artifact_hash(document):
        raise ValidatedRequestContractError("ValidatedRequest artifact_hash mismatch")
    payload = document.get("payload")
    if not isinstance(payload, Mapping):
        raise ValidatedRequestContractError("ValidatedRequest contract payload is missing")
    request = _deserialize_validated_request(payload)
    receipt = request.authority_validation_receipt
    bindings = {
        "request_id": request.request_id,
        "run_id": request.run_id,
        "trace_id": request.trace_id,
        "trace_root": request.trace_root or request.trace_id,
        "tenant_id": request.tenant_id,
        "payload_digest": request.payload_digest,
        "authority_contract_id": receipt.authority_contract_id,
        "authority_receipt_digest": receipt.authority_receipt_digest,
    }
    mismatches = tuple(
        key
        for key, value in bindings.items()
        if str(document.get(key) or "") != str(value or "")
    )
    if mismatches:
        raise ValidatedRequestContractError(
            f"ValidatedRequest envelope binding mismatch: {mismatches}"
        )
    return request


__all__ = [
    "CANONICAL_APPS_RG_VALIDATED_REQUEST_FILENAME",
    "ValidatedRequestContractError",
    "build_validated_request_contract",
    "load_validated_request_contract",
    "write_validated_request_contract",
]
