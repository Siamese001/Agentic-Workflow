"""Validate canonical apps_research Exit proof before apps_rg U0 accepts a brief."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.exit.exit_disposition import X3D_ALLOW_FINISH


def _sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _sha256_json(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class CanonicalAppsResearchExitValidation:
    observed: bool
    valid: bool
    reason: str
    envelope_path: str = ""
    exit_disposition_path: str = ""
    brief_sha256: str = ""
    jd_sha256: str = ""
    exit_disposition_receipt_digest: str = ""
    x3_code: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_rg.canonical_apps_research_exit_validation.v1",
            "observed": self.observed,
            "valid": self.valid,
            "reason": self.reason,
            "envelope_path": self.envelope_path,
            "exit_disposition_path": self.exit_disposition_path,
            "brief_sha256": self.brief_sha256,
            "jd_sha256": self.jd_sha256,
            "exit_disposition_receipt_digest": self.exit_disposition_receipt_digest,
            "x3_code": self.x3_code,
        }


def _read_text_ref(ref: str) -> tuple[str, Path | None]:
    raw = str(ref or "").strip()
    path = Path(raw)
    if path.is_file():
        return path.read_text(encoding="utf-8").strip(), path.resolve()
    return raw, None


def _envelope_path_for_brief(brief_path: Path | None) -> Path | None:
    if brief_path is None:
        return None
    candidates = (
        brief_path.parent / "apps_research_briefing_envelope.json",
        brief_path.with_suffix(brief_path.suffix + ".apps_research_envelope.json"),
        brief_path.with_suffix(".envelope.json"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def _receipt_digest(receipt: Mapping[str, Any]) -> str:
    seed = dict(receipt)
    seed["deterministic_digest"] = ""
    return _sha256_json(seed)


def validate_canonical_apps_research_exit(
    *,
    brief_ref: str,
    jd_ref: str = "",
    require_observed: bool = True,
) -> CanonicalAppsResearchExitValidation:
    """Fail closed unless the producer bundle is Exit-authorized and digest-bound."""

    failures: list[str] = []
    try:
        brief_text, brief_path = _read_text_ref(brief_ref)
    except OSError as exc:
        return CanonicalAppsResearchExitValidation(
            observed=False,
            valid=False,
            reason=f"brief_unreadable:{type(exc).__name__}",
        )
    envelope_path = _envelope_path_for_brief(brief_path)
    if envelope_path is None:
        return CanonicalAppsResearchExitValidation(
            observed=False,
            valid=not require_observed,
            reason=(
                "missing_apps_research_envelope"
                if require_observed
                else "no_apps_research_envelope_present"
            ),
            brief_sha256=_sha256_text(brief_text) if brief_text else "",
        )

    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CanonicalAppsResearchExitValidation(
            observed=True,
            valid=False,
            reason=f"unreadable_envelope:{type(exc).__name__}",
            envelope_path=str(envelope_path),
        )
    if not isinstance(envelope, dict):
        envelope = {}
        failures.append("envelope_not_object")

    if envelope.get("schema_version") != "apps_research.apps_rg_briefing_envelope.v1":
        failures.append("unsupported_envelope_schema")
    if envelope.get("producer_app") != "apps_research":
        failures.append("producer_app_mismatch")
    if envelope.get("consumer_app") != "apps_rg":
        failures.append("consumer_app_mismatch")
    if envelope.get("canonical_exit_authorized") is not True:
        failures.append("canonical_exit_not_authorized")
    if envelope.get("x3_code") != X3D_ALLOW_FINISH:
        failures.append("envelope_x3_not_allow_finish")
    if bool(envelope.get("dry_run")):
        failures.append("dry_run_envelope")
    if bool(envelope.get("stub_detected")):
        failures.append("stub_detected")
    if bool(envelope.get("is_stale")):
        failures.append("stale_envelope")

    brief_sha = _sha256_text(brief_text) if brief_text else ""
    expected_brief_sha = str(envelope.get("brief_sha256") or "").strip()
    if not brief_sha:
        failures.append("empty_brief")
    if not expected_brief_sha:
        failures.append("missing_brief_sha256")
    elif brief_sha != expected_brief_sha:
        failures.append("brief_sha256_mismatch")

    jd_sha = ""
    if jd_ref:
        try:
            jd_text, _jd_path = _read_text_ref(jd_ref)
        except OSError as exc:
            jd_text = ""
            failures.append(f"jd_unreadable:{type(exc).__name__}")
        jd_sha = _sha256_text(jd_text) if jd_text else ""
        expected_jd_sha = str(envelope.get("jd_sha256") or "").strip()
        if not expected_jd_sha:
            failures.append("missing_jd_sha256")
        elif jd_sha != expected_jd_sha:
            failures.append("jd_sha256_mismatch")

    run_id = str(envelope.get("run_id") or "").strip()
    if not run_id:
        failures.append("missing_run_id")

    receipt = envelope.get("apps_research_exit_disposition_receipt")
    receipt = dict(receipt) if isinstance(receipt, Mapping) else {}
    receipt_digest = str(receipt.get("deterministic_digest") or "").strip()
    envelope_receipt_digest = str(
        envelope.get("exit_disposition_receipt_digest") or ""
    ).strip()
    if not receipt:
        failures.append("missing_canonical_exit_receipt")
    else:
        if receipt.get("x3_code") != X3D_ALLOW_FINISH:
            failures.append("canonical_exit_x3_not_allow_finish")
        if receipt.get("required_gates_passed") is not True:
            failures.append("canonical_exit_required_gates_not_passed")
        for field in ("hard_fail_count", "unknown_count", "missing_gate_count"):
            try:
                if int(receipt.get(field) or 0) != 0:
                    failures.append(f"canonical_exit_{field}_nonzero")
            except (TypeError, ValueError):
                failures.append(f"canonical_exit_{field}_invalid")
        if str(receipt.get("run_id") or "") != run_id:
            failures.append("canonical_exit_run_id_mismatch")
        if str(receipt.get("output_artifact_digest") or "") != expected_brief_sha:
            failures.append("canonical_exit_output_digest_mismatch")
        if not receipt_digest:
            failures.append("missing_canonical_exit_receipt_digest")
        elif _receipt_digest(receipt) != receipt_digest:
            failures.append("canonical_exit_receipt_digest_mismatch")
        if receipt_digest != envelope_receipt_digest:
            failures.append("envelope_exit_receipt_digest_mismatch")

    mesh = envelope.get("apps_research_gate_mesh_result")
    mesh = dict(mesh) if isinstance(mesh, Mapping) else {}
    mesh_digest = str(mesh.get("deterministic_digest") or "").strip()
    if not mesh:
        failures.append("missing_gate_mesh_result")
    else:
        if mesh_digest != str(envelope.get("gate_mesh_result_digest") or ""):
            failures.append("envelope_gate_mesh_digest_mismatch")
        if receipt and mesh_digest != str(receipt.get("gate_mesh_result_ref") or ""):
            failures.append("exit_receipt_gate_mesh_digest_mismatch")
        if bool(mesh.get("hard_fail_present")):
            failures.append("gate_mesh_hard_fail_present")
        if bool(mesh.get("unknown_material_present")):
            failures.append("gate_mesh_unknown_present")
        if list(mesh.get("missing_gate_ids") or []):
            failures.append("gate_mesh_missing_required_gates")
        required = set(str(v) for v in (mesh.get("required_gate_ids") or []))
        pass_ids = {
            str(row.get("gate_id") or "")
            for row in (mesh.get("verdicts") or [])
            if isinstance(row, Mapping) and row.get("result") == "PASS"
        }
        if not required or not required.issubset(pass_ids):
            failures.append("gate_mesh_required_gates_not_all_pass")

    exhaust = envelope.get("apps_research_runtime_exhaust_bundle")
    exhaust = dict(exhaust) if isinstance(exhaust, Mapping) else {}
    if not exhaust:
        failures.append("missing_runtime_exhaust_bundle")
    else:
        if exhaust.get("created_after_exit") is not True:
            failures.append("runtime_exhaust_not_after_exit")
        if str(exhaust.get("exit_disposition_ref") or "") != receipt_digest:
            failures.append("runtime_exhaust_exit_receipt_mismatch")
        if str(exhaust.get("gate_mesh_result_ref") or "") != mesh_digest:
            failures.append("runtime_exhaust_gate_mesh_mismatch")

    sealed_ref = str(envelope.get("sealed_workflow_package_ref") or "").strip()
    if not sealed_ref:
        failures.append("missing_sealed_workflow_package_ref")
    if str(envelope.get("sealed_workflow_package_digest") or "") != expected_brief_sha:
        failures.append("sealed_workflow_digest_mismatch")
    if receipt and str(receipt.get("sealed_workflow_package_ref") or "") != sealed_ref:
        failures.append("exit_receipt_sealed_package_mismatch")

    exit_path_raw = str(envelope.get("exit_disposition_receipt_path") or "").strip()
    exit_path = Path(exit_path_raw) if exit_path_raw else None
    if exit_path is None or not exit_path.is_file():
        failures.append("missing_persisted_exit_disposition_receipt")
    else:
        try:
            persisted_receipt = json.loads(exit_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            persisted_receipt = {}
            failures.append("unreadable_persisted_exit_disposition_receipt")
        if persisted_receipt != receipt:
            failures.append("persisted_exit_receipt_mismatch")

    return CanonicalAppsResearchExitValidation(
        observed=True,
        valid=not failures,
        reason="ok" if not failures else ";".join(failures),
        envelope_path=str(envelope_path),
        exit_disposition_path=(
            str(exit_path.resolve()) if exit_path and exit_path.is_file() else ""
        ),
        brief_sha256=brief_sha,
        jd_sha256=jd_sha,
        exit_disposition_receipt_digest=receipt_digest,
        x3_code=str(receipt.get("x3_code") or ""),
    )


__all__ = [
    "CanonicalAppsResearchExitValidation",
    "validate_canonical_apps_research_exit",
]
