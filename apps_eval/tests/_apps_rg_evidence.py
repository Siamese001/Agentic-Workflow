from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _payload_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _signature(secret: str, body: dict[str, Any]) -> str:
    return "hmac-sha256:" + hmac.new(
        secret.encode("utf-8"),
        _canonical_bytes(body),
        hashlib.sha256,
    ).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> bytes:
    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def emit_verified_current_run_evidence(
    root: Path,
    monkeypatch: Any,
    *,
    output_ref: str = "outputs/generated_resume.json",
    parent_run_id: str = "parent-1",
    child_run_id: str = "child-1",
    section_attempt_id: str = "attempt-1",
    runtime_exhaust_bundle_id: str = "exhaust-1",
) -> dict[str, str]:
    """Emit the minimum authentic signed/byte-bound current-run evidence chain."""

    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    secret = "apps-eval-test-route-secret"
    key_id = "apps-eval-test-key"
    monkeypatch.setenv("APPS_RG_ROUTE_HMAC_SECRET", secret)
    monkeypatch.setenv("APPS_RG_ROUTE_HMAC_KEY_ID", key_id)
    digest = "sha256:" + "a" * 64
    identity = {
        "producer_app_id": "apps_research",
        "consumer_app_id": "apps_rg",
        "parent_run_id": parent_run_id,
        "child_run_id": child_run_id,
        "request_id": "request-1",
        "trace_root": "trace-1",
        "tenant_id": "tenant-1",
        "target_company": "ExampleCo",
        "target_role": "SVP Engineering",
        "jd_sha256": digest,
        "brief_sha256": digest,
        "policy_hash": digest,
        "blueprint_hash": digest,
        "schema_version": "apps_research_rg_run_identity.v1",
    }
    continuation_body = {
        "schema_version": "apps_rg.e2e_preflight.v1",
        "gate_id": "APPS_RG_ROUTE_SIGNING_PREFLIGHT",
        "e2e_run_id": root.name,
        "artifact_dir": str(root),
        "artifact_dir_sha256": _payload_digest(str(root)),
        "identity": identity,
        "identity_sha256": _payload_digest(identity),
        "identity_profile": "apps_research_rg_run_identity.v1",
        "product_entry_eligible": True,
        "issued_at_utc": "2026-01-01T00:00:00+00:00",
        "expires_at_utc": "2026-01-01T00:05:00+00:00",
        "continuation_ttl_seconds": 300,
        "continuation_nonce": "test-continuation-nonce",
        "continuation_scope": "APPS_RG_PRODUCT_ENTRY_ONCE",
        "signature_algorithm": "HMAC-SHA256",
        "status": "PASS",
        "route_signing_key_id": key_id,
    }
    continuation = {
        **continuation_body,
        "continuation_payload_digest": _payload_digest(continuation_body),
        "continuation_signature": _signature(secret, continuation_body),
    }
    continuation_raw = _write_json(
        root / "e2e_preflight_continuation_receipt.json",
        continuation,
    )
    consumption_body = {
        "schema_version": "apps_rg.e2e_preflight_consumption.v1",
        "e2e_run_id": root.name,
        "consumer_id": "apps_rg.product_entry",
        "continuation_ref": "e2e_preflight_continuation_receipt.json",
        "continuation_sha256": _bytes_digest(continuation_raw),
        "continuation_payload_digest": continuation["continuation_payload_digest"],
        "consumed_at_utc": "2026-01-01T00:01:00+00:00",
    }
    consumption = {
        **consumption_body,
        "consumption_signature": _signature(secret, consumption_body),
    }
    consumption_raw = _write_json(
        root / "e2e_preflight_continuation_consumption_receipt.json",
        consumption,
    )
    product_entry = {
        "schema_version": "apps_rg.e2e_preflight_product_entry.v1",
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "status": "PASS",
        "identity": identity,
        "identity_sha256": _payload_digest(identity),
        "signed_continuation": {
            "artifact_ref": "e2e_preflight_continuation_receipt.json",
            "sha256": _bytes_digest(continuation_raw),
            "byte_length": len(continuation_raw),
            "payload_digest": continuation["continuation_payload_digest"],
            "route_signing_key_id": key_id,
        },
        "consume_once_receipt": {
            "artifact_ref": "e2e_preflight_continuation_consumption_receipt.json",
            "sha256": _bytes_digest(consumption_raw),
            "byte_length": len(consumption_raw),
            "consumer_id": "apps_rg.product_entry",
        },
        "created_at_utc": "2026-01-01T00:01:01+00:00",
    }
    _write_json(root / "e2e_preflight_product_entry_receipt.json", product_entry)

    decision_raw = _write_json(
        root / "uwg_commit_receipt.json",
        {"schema_version": "test.uwg_commit.v1", "status": "COMMITTED"},
    )
    output_path = (root / output_ref).resolve()
    output_raw = output_path.read_bytes()
    product_authorization = {
        "schema_version": "apps_rg.product_authorization_receipt.v1",
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "identity": identity,
        "identity_sha256": _payload_digest(identity),
        "authorized": True,
        "status": "AUTHORIZED",
        "boundary": "UWG_COMMIT_CLOSED",
        "immutable": True,
        "decision_receipt": {
            "artifact_ref": "uwg_commit_receipt.json",
            "sha256": _bytes_digest(decision_raw),
            "byte_length": len(decision_raw),
        },
        "output_artifact": {
            "artifact_ref": output_ref,
            "sha256": _bytes_digest(output_raw),
            "byte_length": len(output_raw),
        },
        "closed_at_utc": "2026-01-01T00:02:00+00:00",
    }
    _write_json(
        root / "apps_rg_product_authorization_receipt.json",
        product_authorization,
    )
    _write_json(
        root / "r4_run_manifest.json",
        {
            "identity": {
                **identity,
                "section_attempt_id": section_attempt_id,
            }
        },
    )
    _write_json(
        root / "runtime_exhaust_bundle.json",
        {
            "identity": identity,
            "runtime_exhaust_bundle_id": runtime_exhaust_bundle_id,
        },
    )
    if not (root / "x3_disposition_receipt.json").is_file():
        _write_json(
            root / "x3_disposition_receipt.json",
            {"x3_code": "X3D_ALLOW_FINISH"},
        )
    return identity


__all__ = ["emit_verified_current_run_evidence"]
