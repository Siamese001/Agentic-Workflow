"""Canonical fresh E2E preflight with mandatory failure closeout."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.e2e_baseline import validate_pinned_baseline
from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger

E2E_PREFLIGHT_RECEIPT_FILENAME = "e2e_preflight_receipt.json"
E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME = (
    "e2e_preflight_continuation_receipt.json"
)
E2E_PREFLIGHT_CONTINUATION_CONSUMPTION_FILENAME = (
    "e2e_preflight_continuation_consumption_receipt.json"
)
E2E_PREFLIGHT_PRODUCT_ENTRY_RECEIPT_FILENAME = (
    "e2e_preflight_product_entry_receipt.json"
)
E2E_PREFLIGHT_SCHEMA_VERSION = "apps_rg.e2e_preflight.v1"
ROUTE_SIGNING_PREFLIGHT_GATE_ID = "APPS_RG_ROUTE_SIGNING_PREFLIGHT"
DEFAULT_CONTINUATION_TTL_SECONDS = 300

_CANONICAL_IDENTITY_FIELDS = frozenset(
    {
        "producer_app_id",
        "consumer_app_id",
        "parent_run_id",
        "child_run_id",
        "request_id",
        "trace_root",
        "tenant_id",
        "target_company",
        "target_role",
        "jd_sha256",
        "brief_sha256",
        "policy_hash",
        "blueprint_hash",
        "schema_version",
    }
)


@dataclass(frozen=True, slots=True)
class FreshE2EPreflightOutcome:
    passed: bool
    exit_code: int
    receipt: dict[str, Any]
    result: dict[str, Any]
    bootstrap_receipt: dict[str, Any] | None


@dataclass(frozen=True, slots=True)
class PreflightContinuationValidation:
    valid: bool
    errors: tuple[str, ...]
    receipt: dict[str, Any]
    consumption_receipt: dict[str, Any] | None = None


class PreflightContinuationError(RuntimeError):
    """Raised when a product entrypoint receives an invalid continuation."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _payload_digest(value: Any) -> str:
    return _sha256_bytes(_canonical_json_bytes(value))


def _signature(secret: str, body: Mapping[str, Any]) -> str:
    digest = hmac.new(
        str(secret).encode("utf-8"),
        _canonical_json_bytes(dict(body)),
        hashlib.sha256,
    ).hexdigest()
    return "hmac-sha256:" + digest


def _parse_utc(value: Any) -> datetime:
    text = str(value or "").strip()
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def _canonical_identity_valid(identity: Mapping[str, Any]) -> bool:
    if not _CANONICAL_IDENTITY_FIELDS.issubset(identity):
        return False
    if any(
        not str(identity.get(field) or "").strip()
        for field in _CANONICAL_IDENTITY_FIELDS
    ):
        return False
    if identity.get("schema_version") != "apps_research_rg_run_identity.v1":
        return False
    if identity.get("consumer_app_id") != "apps_rg":
        return False
    for field in ("jd_sha256", "brief_sha256", "policy_hash", "blueprint_hash"):
        digest = str(identity.get(field) or "")
        if len(digest) != 71 or not digest.startswith("sha256:"):
            return False
        if any(char not in "0123456789abcdef" for char in digest[7:]):
            return False
    return True


def _write_receipt(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _write_legacy_non_product_projection(
    *,
    path: Path,
    authoritative_path: Path,
    receipt: Mapping[str, Any],
) -> None:
    projection = dict(receipt)
    projection["compatibility_projection"] = {
        "classification": "NON_PRODUCT_ONLY",
        "authoritative_receipt_ref": authoritative_path.name,
        "authoritative_receipt_sha256": _sha256_bytes(authoritative_path.read_bytes()),
    }
    _write_receipt(path, projection)


def _continuation_body(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in receipt.items()
        if key not in {"continuation_payload_digest", "continuation_signature"}
    }


def validate_preflight_continuation(
    *,
    receipt_path: Path,
    secret: str,
    expected_e2e_run_id: str,
    expected_key_id: str = "",
    expected_identity: Mapping[str, Any] | None = None,
    consumer_id: str = "",
    consume: bool = False,
    require_product_identity: bool = True,
    now_utc: datetime | None = None,
) -> PreflightContinuationValidation:
    """Validate and optionally consume a signed fresh-preflight continuation.

    Consumption is represented by an exclusively-created sidecar receipt.  The
    signed continuation is immutable, so replay protection never rewrites the
    authority bytes it validates.
    """

    path = Path(receipt_path).resolve()
    errors: list[str] = []
    try:
        raw_bytes = path.read_bytes()
        payload = json.loads(raw_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        return PreflightContinuationValidation(
            False,
            (f"continuation_unreadable:{type(exc).__name__}",),
            {},
        )
    if not isinstance(payload, dict):
        return PreflightContinuationValidation(False, ("continuation_not_object",), {})
    body = _continuation_body(payload)
    if str(payload.get("schema_version") or "") != E2E_PREFLIGHT_SCHEMA_VERSION:
        errors.append("continuation_schema_mismatch")
    if str(payload.get("status") or "").upper() != "PASS":
        errors.append("continuation_preflight_not_passed")
    if str(payload.get("e2e_run_id") or "") != str(expected_e2e_run_id or ""):
        errors.append("continuation_run_id_mismatch")
    key_id = str(payload.get("route_signing_key_id") or "")
    if expected_key_id and key_id != expected_key_id:
        errors.append("continuation_key_id_mismatch")
    expected_digest = _payload_digest(body)
    if not hmac.compare_digest(
        str(payload.get("continuation_payload_digest") or ""),
        expected_digest,
    ):
        errors.append("continuation_payload_digest_mismatch")
    expected_signature = _signature(secret, body) if secret else ""
    if not secret or not hmac.compare_digest(
        str(payload.get("continuation_signature") or ""),
        expected_signature,
    ):
        errors.append("continuation_signature_invalid")
    artifact_dir = str(payload.get("artifact_dir") or "")
    if artifact_dir != str(path.parent):
        errors.append("continuation_artifact_dir_mismatch")
    if str(payload.get("artifact_dir_sha256") or "") != _payload_digest(artifact_dir):
        errors.append("continuation_artifact_dir_digest_mismatch")
    identity = payload.get("identity")
    identity = identity if isinstance(identity, dict) else {}
    if str(payload.get("identity_sha256") or "") != _payload_digest(identity):
        errors.append("continuation_identity_digest_mismatch")
    if expected_identity is not None and identity != dict(expected_identity):
        errors.append("continuation_identity_mismatch")
    canonical_identity = _canonical_identity_valid(identity)
    if require_product_identity and not (
        canonical_identity and payload.get("product_entry_eligible") is True
    ):
        errors.append("continuation_not_product_eligible")
    current = (now_utc or _now_utc()).astimezone(timezone.utc)
    try:
        issued = _parse_utc(payload.get("issued_at_utc"))
        expires = _parse_utc(payload.get("expires_at_utc"))
        if expires <= issued:
            errors.append("continuation_expiry_window_invalid")
        if current < issued:
            errors.append("continuation_not_yet_valid")
        if current >= expires:
            errors.append("continuation_expired")
    except (TypeError, ValueError):
        errors.append("continuation_timestamp_invalid")
    if not str(payload.get("continuation_nonce") or "").strip():
        errors.append("continuation_nonce_missing")

    consumption_path = path.parent / E2E_PREFLIGHT_CONTINUATION_CONSUMPTION_FILENAME
    if consumption_path.exists():
        errors.append("continuation_already_consumed")
    consumption: dict[str, Any] | None = None
    if consume and not errors:
        if not str(consumer_id or "").strip():
            errors.append("continuation_consumer_id_missing")
        else:
            consumed_at = current.isoformat()
            consumption_body = {
                "schema_version": "apps_rg.e2e_preflight_consumption.v1",
                "e2e_run_id": str(expected_e2e_run_id),
                "consumer_id": str(consumer_id),
                "continuation_ref": path.name,
                "continuation_sha256": _sha256_bytes(raw_bytes),
                "continuation_payload_digest": str(
                    payload.get("continuation_payload_digest") or ""
                ),
                "consumed_at_utc": consumed_at,
            }
            consumption = {
                **consumption_body,
                "consumption_signature": _signature(secret, consumption_body),
            }
            try:
                with consumption_path.open("x", encoding="utf-8") as handle:
                    handle.write(json.dumps(consumption, indent=2, sort_keys=True) + "\n")
            except FileExistsError:
                errors.append("continuation_already_consumed")
                consumption = None
    return PreflightContinuationValidation(
        valid=not errors,
        errors=tuple(errors),
        receipt=payload,
        consumption_receipt=consumption,
    )


def require_valid_preflight_continuation(**kwargs: Any) -> dict[str, Any]:
    """Return a valid continuation or raise a fail-closed typed error."""

    result = validate_preflight_continuation(**kwargs)
    if not result.valid:
        raise PreflightContinuationError("; ".join(result.errors))
    return result.receipt


def bind_preflight_to_product_identity(
    *,
    validation: PreflightContinuationValidation,
    receipt_path: Path,
    secret: str,
    identity: Mapping[str, Any],
    consumer_id: str,
    clock: Callable[[], datetime] = _now_utc,
) -> Path:
    """Bind an already-consumed signed continuation to producer identity.

    The producer child identity does not exist when fresh preflight executes.
    Once the producer bundle closes, this receipt reopens the signed
    continuation and its consume-once sidecar, verifies both byte bindings,
    and adds the exact canonical identity without rewriting either source.
    """

    if not validation.valid:
        raise PreflightContinuationError("preflight continuation was not valid")
    canonical_identity = dict(identity)
    if not _canonical_identity_valid(canonical_identity):
        raise PreflightContinuationError("canonical product identity is incomplete")
    path = Path(receipt_path).resolve()
    try:
        continuation_bytes = path.read_bytes()
        continuation = json.loads(continuation_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        raise PreflightContinuationError(
            f"continuation_unreadable:{type(exc).__name__}"
        ) from exc
    if not isinstance(continuation, dict) or continuation != validation.receipt:
        raise PreflightContinuationError("continuation bytes changed after validation")
    continuation_body = _continuation_body(continuation)
    if (
        continuation.get("status") != "PASS"
        or continuation.get("continuation_payload_digest")
        != _payload_digest(continuation_body)
        or not secret
        or continuation.get("continuation_signature")
        != _signature(secret, continuation_body)
    ):
        raise PreflightContinuationError("continuation signature revalidation failed")

    consumption_path = path.parent / E2E_PREFLIGHT_CONTINUATION_CONSUMPTION_FILENAME
    try:
        consumption_bytes = consumption_path.read_bytes()
        consumption = json.loads(consumption_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        raise PreflightContinuationError(
            f"continuation_consumption_unreadable:{type(exc).__name__}"
        ) from exc
    if not isinstance(consumption, dict):
        raise PreflightContinuationError("continuation consumption is not an object")
    consumption_body = {
        key: value
        for key, value in consumption.items()
        if key != "consumption_signature"
    }
    if (
        consumption.get("consumer_id") != consumer_id
        or consumption.get("continuation_ref") != path.name
        or consumption.get("continuation_sha256")
        != _sha256_bytes(continuation_bytes)
        or consumption.get("continuation_payload_digest")
        != continuation.get("continuation_payload_digest")
        or consumption.get("consumption_signature")
        != _signature(secret, consumption_body)
    ):
        raise PreflightContinuationError("continuation consumption binding is invalid")

    product_entry = {
        "schema_version": "apps_rg.e2e_preflight_product_entry.v1",
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "status": "PASS",
        "identity": canonical_identity,
        "identity_sha256": _payload_digest(canonical_identity),
        "signed_continuation": {
            "artifact_ref": path.name,
            "sha256": _sha256_bytes(continuation_bytes),
            "byte_length": len(continuation_bytes),
            "payload_digest": continuation["continuation_payload_digest"],
            "route_signing_key_id": continuation.get("route_signing_key_id"),
        },
        "consume_once_receipt": {
            "artifact_ref": consumption_path.name,
            "sha256": _sha256_bytes(consumption_bytes),
            "byte_length": len(consumption_bytes),
            "consumer_id": consumer_id,
        },
        "created_at_utc": clock().astimezone(timezone.utc).isoformat(),
    }
    target = path.parent / E2E_PREFLIGHT_PRODUCT_ENTRY_RECEIPT_FILENAME
    if target.exists():
        raise PreflightContinuationError("product entry receipt already exists")
    _write_receipt(target, product_entry)
    return target


def _redact_error(exc: BaseException, environ: Mapping[str, str]) -> str:
    text = str(exc).strip() or type(exc).__name__
    for key, raw_value in environ.items():
        key_upper = str(key).upper()
        value = str(raw_value or "")
        if (
            value
            and len(value) >= 8
            and any(marker in key_upper for marker in ("KEY", "TOKEN", "SECRET", "PASSWORD"))
        ):
            text = text.replace(value, "[REDACTED]")
    return text[:1000]


def run_fresh_e2e_preflight(
    *,
    artifact_dir: Path,
    e2e_run_id: str,
    repo_root: Path,
    baseline_ref: Path,
    environ: Mapping[str, str] | None = None,
    runtime_check: Callable[[], Any] | None = None,
    bootstrap: Callable[[], Any] | None = None,
    run_identity: Mapping[str, Any] | None = None,
    continuation_ttl_seconds: int = DEFAULT_CONTINUATION_TTL_SECONDS,
    clock: Callable[[], datetime] = _now_utc,
    nonce_factory: Callable[[], str] | None = None,
) -> FreshE2EPreflightOutcome:
    """Run all non-retriable checks before research and close out failures in-run."""
    root = Path(artifact_dir).resolve()
    repo = Path(repo_root).resolve()
    env = environ if environ is not None else os.environ
    ledger = E2EStageLedger.create(artifact_dir=root, e2e_run_id=e2e_run_id)
    secret_present = bool(str(env.get("APPS_RG_ROUTE_HMAC_SECRET") or "").strip())
    key_id = str(env.get("APPS_RG_ROUTE_HMAC_KEY_ID") or "").strip()
    missing = []
    if not secret_present:
        missing.append("APPS_RG_ROUTE_HMAC_SECRET")
    if not key_id:
        missing.append("APPS_RG_ROUTE_HMAC_KEY_ID")
    baseline: dict[str, str] = {}
    failure_code = ""
    failure_detail = ""
    if missing:
        failure_code = "APPS_RG_ROUTE_SIGNING_CONFIGURATION_REQUIRED"
        failure_detail = "Required route-signing environment variables were absent at process ingestion."
    else:
        try:
            baseline = validate_pinned_baseline(repo, Path(baseline_ref))
        except RuntimeError as exc:
            failure_code = "PINNED_BASELINE_PREFLIGHT_FAILED"
            failure_detail = _redact_error(exc, env)
    if not failure_code and runtime_check is not None:
        try:
            runtime_check()
        except Exception as exc:  # Guardian: converted to typed preflight receipt and mandatory RCA.
            failure_code = "PRODUCTION_RUNTIME_PREFLIGHT_FAILED"
            failure_detail = _redact_error(exc, env)
    bootstrap_receipt: dict[str, Any] | None = None
    if not failure_code and bootstrap is not None:
        try:
            raw_bootstrap = bootstrap()
            bootstrap_receipt = raw_bootstrap if isinstance(raw_bootstrap, dict) else {}
            if (
                str(bootstrap_receipt.get("status") or "PASS").upper() != "PASS"
                or int(bootstrap_receipt.get("exit_code") or 0) != 0
            ):
                failure_code = "FACT_VECTOR_BOOTSTRAP_PREFLIGHT_FAILED"
                failure_detail = "Fresh E2E fact-vector bootstrap did not return a passing receipt."
        except Exception as exc:  # Guardian: converted to typed preflight receipt and mandatory RCA.
            failure_code = "FACT_VECTOR_BOOTSTRAP_PREFLIGHT_FAILED"
            failure_detail = _redact_error(exc, env)

    if continuation_ttl_seconds < 1 or continuation_ttl_seconds > 3600:
        raise ValueError("continuation_ttl_seconds must be between 1 and 3600")
    issued_at = clock().astimezone(timezone.utc)
    identity = dict(run_identity or {"e2e_run_id": e2e_run_id})
    canonical_identity = _canonical_identity_valid(identity)
    receipt_body = {
        "schema_version": E2E_PREFLIGHT_SCHEMA_VERSION,
        "gate_id": ROUTE_SIGNING_PREFLIGHT_GATE_ID,
        "e2e_run_id": e2e_run_id,
        "artifact_dir": str(root),
        "artifact_dir_sha256": _payload_digest(str(root)),
        "identity": identity,
        "identity_sha256": _payload_digest(identity),
        "identity_profile": (
            "apps_research_rg_run_identity.v1"
            if canonical_identity
            else "legacy_e2e_run_only.v1"
        ),
        "product_entry_eligible": bool(canonical_identity and not failure_code),
        "issued_at_utc": issued_at.isoformat(),
        "expires_at_utc": (
            issued_at + timedelta(seconds=continuation_ttl_seconds)
        ).isoformat(),
        "continuation_ttl_seconds": continuation_ttl_seconds,
        "continuation_nonce": (nonce_factory or (lambda: secrets.token_urlsafe(32)))(),
        "continuation_scope": "APPS_RG_PRODUCT_ENTRY_ONCE",
        "signature_algorithm": "HMAC-SHA256",
        "status": "BLOCKED" if failure_code else "PASS",
        "failure_code": failure_code,
        "failure_detail": failure_detail,
        "route_signing_secret_present": secret_present,
        "route_signing_key_id_present": bool(key_id),
        "route_signing_key_id": key_id,
        "missing_environment_variables": missing,
        "baseline_ref": str(Path(baseline_ref).resolve()),
        "baseline": baseline,
        "retry_policy": "NON_RETRIABLE_CONFIGURATION" if failure_code else "NOT_APPLICABLE",
        "research_attempt_count": 0,
        "generation_attempt_count": 0,
        "judge_attempt_count": 0,
        "research_artifact_dir": "NOT_REACHED:PREFLIGHT",
        "research_briefing_path": "NOT_REACHED:PREFLIGHT",
        "research_company_brief_path": "NOT_REACHED:PREFLIGHT",
        "research_handoff_v2_path": "NOT_REACHED:PREFLIGHT",
        "apps_eval_record_ref": "NOT_REACHED:PREFLIGHT",
        "l6_shadow_bridge_ref": "NOT_REACHED:PREFLIGHT",
        "l7_audit_status": "NOT_REACHED:PREFLIGHT",
        "bootstrap_receipt": bootstrap_receipt or {},
        "created_at_utc": issued_at.isoformat(),
    }
    receipt = {
        **receipt_body,
        "continuation_payload_digest": _payload_digest(receipt_body),
        "continuation_signature": (
            _signature(str(env.get("APPS_RG_ROUTE_HMAC_SECRET") or ""), receipt_body)
            if secret_present
            else ""
        ),
    }
    receipt_path = root / E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME
    _write_receipt(receipt_path, receipt)
    _write_legacy_non_product_projection(
        path=root / E2E_PREFLIGHT_RECEIPT_FILENAME,
        authoritative_path=receipt_path,
        receipt=receipt,
    )
    if not failure_code:
        ledger.record_from_receipt(
            stage_id="PREFLIGHT",
            receipt_ref=receipt_path,
            reason_code="ALL_NON_RETRIABLE_PREFLIGHT_CHECKS_PASSED",
            output_refs={
                "preflight_receipt": E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME
            },
        )
        return FreshE2EPreflightOutcome(True, 0, receipt, {}, bootstrap_receipt)

    ledger.record_from_receipt(
        stage_id="PREFLIGHT",
        receipt_ref=receipt_path,
        reason_code=failure_code,
        output_refs={
            "preflight_receipt": E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME
        },
    )
    operational_failure = {
        "stage_id": "PREFLIGHT",
        "gate_id": ROUTE_SIGNING_PREFLIGHT_GATE_ID,
        "failure_code": failure_code,
        "failure_detail": failure_detail,
        "missing_environment_variables": missing,
        "preflight_receipt": str(receipt_path),
        "baseline_ref": str(Path(baseline_ref).resolve()),
        "retry_policy": receipt["retry_policy"],
        "research_attempt_count": 0,
        "generation_attempt_count": 0,
        "judge_attempt_count": 0,
        "research_artifact_dir": "NOT_REACHED:PREFLIGHT",
        "research_briefing_path": "NOT_REACHED:PREFLIGHT",
        "research_company_brief_path": "NOT_REACHED:PREFLIGHT",
        "research_handoff_v2_path": "NOT_REACHED:PREFLIGHT",
        "apps_eval_record_ref": "NOT_REACHED:PREFLIGHT",
        "l6_shadow_bridge_ref": "NOT_REACHED:PREFLIGHT",
        "l7_audit_status": "NOT_REACHED:PREFLIGHT",
    }
    result = {
        "exit_status": "error",
        "execution_status": "failed",
        "outcome_authorized": False,
        "x3_disposition": "PRE_RUN:PREFLIGHT",
        "completion_status": "BLOCKED",
        "completion_fault": failure_code,
        "fault": failure_code,
        "artifact_dir": str(root),
        "run_id": e2e_run_id,
        "operational_failure": operational_failure,
        "research_artifact_dir": "NOT_REACHED:PREFLIGHT",
        "research_briefing_path": "NOT_REACHED:PREFLIGHT",
        "research_company_brief_path": "NOT_REACHED:PREFLIGHT",
        "research_handoff_v2_path": "NOT_REACHED:PREFLIGHT",
        "apps_eval_record_ref": "NOT_REACHED:PREFLIGHT",
        "l6_shadow_bridge_ref": "NOT_REACHED:PREFLIGHT",
        "l7_audit_status": "NOT_REACHED:PREFLIGHT",
    }
    from apps_rg.runtime.mandatory_run_outputs import emit_mandatory_run_outputs

    emitted = emit_mandatory_run_outputs(root, repo_root=repo, result=result)
    gate = emitted.get("mandatory_output_gate") or {}
    result.update(
        {
            "mandatory_run_output_json": str(emitted.get("json_path") or ""),
            "mandatory_run_output_md": str(emitted.get("markdown_path") or ""),
            "bcg_executive_output_md": str(emitted.get("bcg_markdown_path") or ""),
            "mandatory_output_hard_stop": gate,
        }
    )
    closeout_pass = gate.get("pass") is True
    ledger.record(
        stage_id="CLOSEOUT",
        status="PASS" if closeout_pass else "FAIL",
        reason_code=(
            "FAILED_RUN_REPORTED"
            if closeout_pass
            else str(gate.get("failure_reason") or "MANDATORY_OUTPUT_CLOSEOUT_FAILED")
        ),
        output_refs={"mandatory_run_output_json": str(emitted.get("json_path") or "")},
    )
    return FreshE2EPreflightOutcome(False, 2, receipt, result, bootstrap_receipt)


__all__ = [
    "DEFAULT_CONTINUATION_TTL_SECONDS",
    "E2E_PREFLIGHT_CONTINUATION_CONSUMPTION_FILENAME",
    "E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME",
    "E2E_PREFLIGHT_PRODUCT_ENTRY_RECEIPT_FILENAME",
    "E2E_PREFLIGHT_RECEIPT_FILENAME",
    "FreshE2EPreflightOutcome",
    "PreflightContinuationError",
    "PreflightContinuationValidation",
    "ROUTE_SIGNING_PREFLIGHT_GATE_ID",
    "bind_preflight_to_product_identity",
    "require_valid_preflight_continuation",
    "run_fresh_e2e_preflight",
    "validate_preflight_continuation",
]
