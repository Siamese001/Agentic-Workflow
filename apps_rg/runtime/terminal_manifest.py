"""Final Apps RG manifest and non-self-referential pipeline close receipt."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from apps_rg.runtime.e2e_stage_ledger import (
    E2E_STAGE_LEDGER_FILENAME,
    E2E_STAGE_LEDGER_SEAL_FILENAME,
    E2E_STAGE_LEDGER_SEAL_SCHEMA_VERSION,
    E2E_STAGE_LEDGER_V2_SCHEMA_VERSION,
    verify_e2e_stage_ledger,
)
from apps_rg.runtime.terminal_state import TerminalStateError, TerminalStateMachine

TERMINAL_MANIFEST_FILENAME = "apps_rg_e2e_terminal_manifest.json"
TERMINAL_MANIFEST_SCHEMA_VERSION = "apps_rg.e2e_terminal_manifest.v1"
PIPELINE_COMPLETION_RECEIPT_FILENAME = "apps_rg_pipeline_completion_receipt.json"
PIPELINE_COMPLETION_RECEIPT_SCHEMA_VERSION = (
    "apps_rg.pipeline_completion_receipt.v1"
)

_X3_CODES = frozenset(
    {
        "X3A_DENY_REROUTE",
        "X3B_ESCALATE_HITL",
        "X3C_COMMIT_REQUEST_TO_UWG",
        "X3D_ALLOW_FINISH",
        "X3E_SAFE_ABSTAIN",
    }
)
_PROMOTION_STATUSES = frozenset(
    {"PROMOTED", "REJECTED", "NO_CHANGE", "DEFERRED", "NOT_RUN"}
)


@dataclass(frozen=True, slots=True)
class TerminalManifestVerification:
    valid: bool
    errors: tuple[str, ...]
    manifest: dict[str, Any]
    pipeline_completion_receipt: dict[str, Any]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return _sha256_bytes(_canonical_json_bytes(value))


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _resolve_contained_file(root: Path, ref: str | Path) -> Path:
    base = Path(root).resolve()
    raw = Path(ref)
    target = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise TerminalStateError(f"terminal artifact escapes run directory: {ref}") from exc
    if not target.is_file():
        raise TerminalStateError(f"terminal artifact is missing: {ref}")
    return target


def _binding(root: Path, ref: str | Path, *, artifact_id: str = "") -> dict[str, Any]:
    target = _resolve_contained_file(root, ref)
    raw = target.read_bytes()
    binding = {
        "artifact_ref": target.relative_to(Path(root).resolve()).as_posix(),
        "sha256": _sha256_bytes(raw),
        "byte_length": len(raw),
    }
    if artifact_id:
        binding["artifact_id"] = artifact_id
    return binding


def _write_exclusive(path: Path, payload: Mapping[str, Any]) -> None:
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n")
    except FileExistsError as exc:
        raise TerminalStateError(f"terminal artifact already exists: {path.name}") from exc


def _manifest_digest_payload(manifest: Mapping[str, Any]) -> dict[str, Any]:
    body = json.loads(json.dumps(dict(manifest)))
    seal = body.get("manifest_seal")
    if isinstance(seal, dict):
        seal.pop("manifest_sha256", None)
    return body


def seal_terminal_manifest(
    *,
    artifact_dir: Path,
    identity: Mapping[str, Any],
    x3_code: str,
    x3_receipt_ref: str | Path,
    terminal_state: TerminalStateMachine,
    promotion_status: str,
    promotion_receipt_ref: str | Path,
    mandatory_output_refs: Mapping[str, str | Path]
    | Sequence[tuple[str, str | Path]],
    stage_ledger_ref: str | Path = E2E_STAGE_LEDGER_FILENAME,
    stage_ledger_seal_ref: str | Path = E2E_STAGE_LEDGER_SEAL_FILENAME,
    clock: Callable[[], str] = _utc_now,
) -> tuple[Path, Path]:
    """Seal the manifest, then close the pipeline with an exact-byte receipt."""

    root = Path(artifact_dir).resolve()
    code = str(x3_code or "").strip().upper()
    if code not in _X3_CODES:
        raise TerminalStateError(f"terminal manifest requires a canonical X3 code: {code!r}")
    promotion = str(promotion_status or "").strip().upper()
    if promotion not in _PROMOTION_STATUSES:
        raise TerminalStateError(f"unknown promotion terminal status: {promotion!r}")
    product, pipeline = terminal_state.manifest_blocks()
    if code != "X3D_ALLOW_FINISH" and product["authorized"]:
        raise TerminalStateError("only exact X3D_ALLOW_FINISH may authorize a product")
    if pipeline["complete"] and not product["authorized"]:
        raise TerminalStateError("pipeline completion requires product authorization")
    expected_repair = bool(product["authorized"] and not pipeline["complete"])
    if pipeline["observability_repair_required"] is not expected_repair:
        raise TerminalStateError("terminal repair state contradicts authorization boundary")

    x3 = _binding(root, x3_receipt_ref)
    try:
        x3_payload = json.loads(
            (root / x3["artifact_ref"]).read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise TerminalStateError("X3 authority receipt is not valid JSON") from exc
    if not isinstance(x3_payload, dict):
        raise TerminalStateError("X3 authority receipt must be a JSON object")
    receipt_x3_code = str(
        x3_payload.get("x3_code")
        or x3_payload.get("code")
        or x3_payload.get("disposition")
        or ""
    ).upper()
    if receipt_x3_code != code:
        raise TerminalStateError(
            "terminal X3 code does not match authoritative receipt bytes"
        )
    promotion_binding = _binding(root, promotion_receipt_ref)
    decision_binding = _binding(root, product["decision_receipt_ref"])
    if decision_binding["sha256"] != product["decision_receipt_sha256"]:
        raise TerminalStateError("product decision receipt changed after authorization close")

    ledger_path = _resolve_contained_file(root, stage_ledger_ref)
    ledger_seal_path = _resolve_contained_file(root, stage_ledger_seal_ref)
    ledger_report = verify_e2e_stage_ledger(ledger_path)
    if not ledger_report.valid or not ledger_report.sealed:
        raise TerminalStateError(
            "terminal manifest requires a valid externally sealed v2 stage ledger"
        )
    ledger_payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    if ledger_payload.get("schema_version") != E2E_STAGE_LEDGER_V2_SCHEMA_VERSION:
        raise TerminalStateError("terminal manifest rejects non-product legacy ledgers")
    seal_payload = json.loads(ledger_seal_path.read_text(encoding="utf-8"))
    if not isinstance(seal_payload, dict) or seal_payload.get(
        "schema_version"
    ) != E2E_STAGE_LEDGER_SEAL_SCHEMA_VERSION:
        raise TerminalStateError("stage ledger seal receipt schema is invalid")
    ledger_bytes = ledger_path.read_bytes()
    if seal_payload.get("ledger_sha256") != _sha256_bytes(ledger_bytes):
        raise TerminalStateError("stage ledger seal does not bind exact ledger bytes")
    identity_sha256 = _digest(dict(identity))
    if seal_payload.get("identity_sha256") != identity_sha256:
        raise TerminalStateError("stage ledger seal identity does not match manifest")
    sealed_state = seal_payload.get("terminal_state")
    if not isinstance(sealed_state, dict) or bool(
        sealed_state.get("product_authorized")
    ) != bool(product["authorized"]):
        raise TerminalStateError("stage ledger and manifest authorization states differ")

    output_items = (
        mandatory_output_refs.items()
        if isinstance(mandatory_output_refs, Mapping)
        else mandatory_output_refs
    )
    mandatory = [
        _binding(root, ref, artifact_id=str(artifact_id))
        for artifact_id, ref in output_items
    ]
    if not mandatory:
        raise TerminalStateError("terminal manifest requires mandatory outputs")
    sealed_at = clock()
    manifest = {
        "schema_version": TERMINAL_MANIFEST_SCHEMA_VERSION,
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "identity": dict(identity),
        "x3_disposition": {
            "code": code,
            "receipt_ref": x3["artifact_ref"],
            "receipt_sha256": x3["sha256"],
        },
        "product_authorization": product,
        "pipeline_completion": pipeline,
        "promotion_terminal": {
            "status": promotion,
            "authority_plane": "future_run_only",
            "receipt_ref": promotion_binding["artifact_ref"],
            "receipt_sha256": promotion_binding["sha256"],
        },
        "mandatory_outputs": mandatory,
        "stage_ledger": {
            "schema_version": E2E_STAGE_LEDGER_V2_SCHEMA_VERSION,
            "ledger_ref": ledger_path.relative_to(root).as_posix(),
            "ledger_sha256": _sha256_bytes(ledger_bytes),
            "ledger_byte_length": len(ledger_bytes),
            "seal_receipt_ref": ledger_seal_path.relative_to(root).as_posix(),
            "seal_receipt_sha256": _sha256_bytes(ledger_seal_path.read_bytes()),
            "sealed_at_utc": str(seal_payload.get("sealed_at_utc") or ""),
        },
        "manifest_seal": {
            "canonicalization": (
                "rfc8785_without_manifest_seal.manifest_sha256"
            ),
            "sealed_at_utc": sealed_at,
            "sealed_after_stage_ledger": True,
        },
    }
    manifest["manifest_seal"]["manifest_sha256"] = _digest(
        _manifest_digest_payload(manifest)
    )
    manifest_path = root / TERMINAL_MANIFEST_FILENAME
    completion_path = root / PIPELINE_COMPLETION_RECEIPT_FILENAME
    if completion_path.exists():
        raise TerminalStateError(
            f"terminal artifact already exists: {completion_path.name}"
        )
    terminal_state.seal()
    _write_exclusive(manifest_path, manifest)
    manifest_bytes = manifest_path.read_bytes()
    completion = {
        "schema_version": PIPELINE_COMPLETION_RECEIPT_SCHEMA_VERSION,
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "identity_sha256": identity_sha256,
        "terminal_manifest_ref": manifest_path.name,
        "terminal_manifest_sha256": _sha256_bytes(manifest_bytes),
        "terminal_manifest_byte_length": len(manifest_bytes),
        "product_authorized": bool(product["authorized"]),
        "pipeline_complete": bool(pipeline["complete"]),
        "observability_repair_required": bool(
            pipeline["observability_repair_required"]
        ),
        "closed_at_utc": clock(),
    }
    _write_exclusive(completion_path, completion)
    return manifest_path, completion_path


def verify_terminal_manifest(path: Path) -> TerminalManifestVerification:
    manifest_path = Path(path).resolve()
    root = manifest_path.parent
    errors: list[str] = []
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        return TerminalManifestVerification(
            False,
            (f"manifest_unreadable:{type(exc).__name__}",),
            {},
            {},
        )
    if not isinstance(manifest, dict):
        return TerminalManifestVerification(False, ("manifest_not_object",), {}, {})
    if manifest.get("schema_version") != TERMINAL_MANIFEST_SCHEMA_VERSION:
        errors.append("manifest_schema_mismatch")
    identity = manifest.get("identity")
    identity = identity if isinstance(identity, dict) else {}
    seal = manifest.get("manifest_seal")
    seal = seal if isinstance(seal, dict) else {}
    expected_manifest_digest = _digest(_manifest_digest_payload(manifest))
    if seal.get("manifest_sha256") != expected_manifest_digest:
        errors.append("manifest_seal_digest_mismatch")
    product = manifest.get("product_authorization")
    product = product if isinstance(product, dict) else {}
    pipeline = manifest.get("pipeline_completion")
    pipeline = pipeline if isinstance(pipeline, dict) else {}
    authorized = product.get("authorized") is True
    complete = pipeline.get("complete") is True
    repair = pipeline.get("observability_repair_required") is True
    if complete and not authorized:
        errors.append("pipeline_complete_without_product_authorization")
    if repair != (authorized and not complete):
        errors.append("observability_repair_semantics_mismatch")
    if product.get("immutable") is not True:
        errors.append("product_authorization_not_immutable")

    binding_specs: list[tuple[str, Mapping[str, Any]]] = []
    x3 = manifest.get("x3_disposition")
    if isinstance(x3, dict):
        binding_specs.append(("x3", x3))
    promotion = manifest.get("promotion_terminal")
    if isinstance(promotion, dict):
        binding_specs.append(("promotion", promotion))
    if product:
        binding_specs.append(
            (
                "product_decision",
                {
                    "artifact_ref": product.get("decision_receipt_ref"),
                    "sha256": product.get("decision_receipt_sha256"),
                },
            )
        )
    for index, binding in enumerate(manifest.get("mandatory_outputs") or []):
        if isinstance(binding, dict):
            binding_specs.append((f"mandatory:{index}", binding))
    ledger = manifest.get("stage_ledger")
    ledger = ledger if isinstance(ledger, dict) else {}
    binding_specs.append(
        (
            "ledger",
            {
                "artifact_ref": ledger.get("ledger_ref"),
                "sha256": ledger.get("ledger_sha256"),
                "byte_length": ledger.get("ledger_byte_length"),
            },
        )
    )
    binding_specs.append(
        (
            "ledger_seal",
            {
                "artifact_ref": ledger.get("seal_receipt_ref"),
                "sha256": ledger.get("seal_receipt_sha256"),
            },
        )
    )
    for label, binding in binding_specs:
        ref = str(binding.get("artifact_ref") or binding.get("receipt_ref") or "")
        try:
            target = _resolve_contained_file(root, ref)
            raw = target.read_bytes()
        except TerminalStateError:
            errors.append(f"bound_artifact_unreadable:{label}")
            continue
        expected_sha = binding.get("sha256") or binding.get("receipt_sha256")
        if expected_sha != _sha256_bytes(raw):
            errors.append(f"bound_artifact_digest_mismatch:{label}")
        if "byte_length" in binding and binding.get("byte_length") != len(raw):
            errors.append(f"bound_artifact_length_mismatch:{label}")

    completion_path = root / PIPELINE_COMPLETION_RECEIPT_FILENAME
    try:
        completion = json.loads(completion_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        completion = {}
        errors.append(f"pipeline_completion_receipt_unreadable:{type(exc).__name__}")
    if not isinstance(completion, dict):
        completion = {}
        errors.append("pipeline_completion_receipt_not_object")
    if completion.get("schema_version") != PIPELINE_COMPLETION_RECEIPT_SCHEMA_VERSION:
        errors.append("pipeline_completion_schema_mismatch")
    if completion.get("terminal_manifest_sha256") != _sha256_bytes(manifest_bytes):
        errors.append("pipeline_completion_manifest_digest_mismatch")
    if completion.get("terminal_manifest_byte_length") != len(manifest_bytes):
        errors.append("pipeline_completion_manifest_length_mismatch")
    if completion.get("identity_sha256") != _digest(identity):
        errors.append("pipeline_completion_identity_mismatch")
    for field, expected in (
        ("product_authorized", authorized),
        ("pipeline_complete", complete),
        ("observability_repair_required", repair),
    ):
        if completion.get(field) is not expected:
            errors.append(f"pipeline_completion_state_mismatch:{field}")
    return TerminalManifestVerification(
        valid=not errors,
        errors=tuple(errors),
        manifest=manifest,
        pipeline_completion_receipt=completion,
    )


__all__ = [
    "PIPELINE_COMPLETION_RECEIPT_FILENAME",
    "PIPELINE_COMPLETION_RECEIPT_SCHEMA_VERSION",
    "TERMINAL_MANIFEST_FILENAME",
    "TERMINAL_MANIFEST_SCHEMA_VERSION",
    "TerminalManifestVerification",
    "seal_terminal_manifest",
    "verify_terminal_manifest",
]
