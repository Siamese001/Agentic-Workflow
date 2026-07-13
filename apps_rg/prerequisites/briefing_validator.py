"""apps_rg prerequisite gate — historical and apps_research handoff validators."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

__all__ = [
    "BriefingValidationResult",
    "BriefingCheck",
    "AppsResearchHandoffValidation",
    "HistoricalBriefingValidator",
    "find_legacy_apps_research_envelope_for_briefing",
    "find_apps_research_handoff_v2_for_briefing",
    "validate_apps_research_handoff",
    "check_briefing_prerequisite",
]

_REQUIRES_RESEARCH_STATUSES = frozenset({
    "missing",
    "stale",
    "incomplete",
    "scope_mismatch",
})
_CANONICAL_X3_ALLOW = "X3D_ALLOW_FINISH"


class BriefingValidationResult(str, Enum):
    """Possible outcomes of briefing prerequisite validation."""

    VALID = "valid"
    MISSING = "missing"
    STALE = "stale"
    POLICY_MISMATCH = "policy_mismatch"
    BLUEPRINT_MISMATCH = "blueprint_mismatch"
    SCOPE_MISMATCH = "scope_mismatch"
    INCOMPLETE = "incomplete"


@dataclass
class BriefingCheck:
    """Result of a briefing prerequisite check."""

    result: BriefingValidationResult
    briefing: dict[str, Any] | None
    reason: str = ""
    freshness_hours: float | None = None

    @property
    def is_valid(self) -> bool:
        return self.result == BriefingValidationResult.VALID

    @property
    def requires_apps_research(self) -> bool:
        return self.result.value in _REQUIRES_RESEARCH_STATUSES


@dataclass(frozen=True)
class AppsResearchHandoffValidation:
    """Validation result for an apps_research-produced apps_rg briefing."""

    observed: bool
    valid: bool
    reason: str
    envelope_path: str = ""
    envelope: dict[str, Any] | None = None
    receipt: dict[str, Any] | None = None

    def to_receipt(self) -> dict[str, Any]:
        if self.receipt is not None:
            return dict(self.receipt)
        return {
            "schema_version": "apps_rg.apps_research_handoff_validation_receipt.v2",
            "observed": self.observed,
            "valid": self.valid,
            "reason": self.reason,
            "envelope_path": self.envelope_path,
        }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_text_ref(ref: str) -> tuple[str, str]:
    path = Path(str(ref or "").strip())
    try:
        is_file = path.is_file()
    except OSError:
        # Long inline inputs (for example a complete JSON JD) are text, not
        # filesystem paths.  Some platforms raise ENAMETOOLONG while probing.
        is_file = False
    if is_file:
        return path.read_text(encoding="utf-8").strip(), str(path.resolve())
    return str(ref or "").strip(), "inline:text"


def find_legacy_apps_research_envelope_for_briefing(
    brief_ref: str,
) -> Path | None:
    """Detect a retired v1 sidecar so callers can reject it explicitly."""
    ref = str(brief_ref or "").strip()
    if not ref or ref.startswith(("http://", "https://")):
        return None
    path = Path(ref)
    if not path.is_file():
        return None
    candidates = (
        path.parent / "apps_research_briefing_envelope.json",
        path.with_suffix(path.suffix + ".apps_research_envelope.json"),
        path.with_suffix(".envelope.json"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def find_apps_research_handoff_v2_for_briefing(brief_ref: str) -> Path | None:
    """Locate only an adjacent, physically committed v2 producer manifest."""
    ref = str(brief_ref or "").strip()
    if not ref or ref.startswith(("http://", "https://")):
        return None
    brief_path = Path(ref)
    if not brief_path.is_file():
        return None
    direct = brief_path.parent / "apps_research_apps_rg_handoff_v2.json"
    if direct.is_file():
        return direct.resolve()
    return None


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _canonical_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        + "\n"
    ).encode("utf-8")


def _path_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def _normalized_input_bytes(ref: str) -> bytes:
    raw = str(ref or "")
    path = Path(raw.strip())
    try:
        is_file = path.is_file()
    except OSError:
        # Treat unprobeable values as inline input.  In particular, a long
        # canonical JSON JD can exceed the host filesystem's name limit.
        is_file = False
    if is_file:
        raw = path.read_text(encoding="utf-8", errors="strict")
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n").strip()
    return (normalized + "\n").encode("utf-8")


def _persist_consumer_receipt(
    root: Path, receipt: Mapping[str, Any]
) -> dict[str, Any]:
    destination = root / "apps_research_handoff_validation_receipt.json"
    if destination.is_file():
        try:
            existing = json.loads(destination.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = None
        if isinstance(existing, dict):
            existing_comparable = dict(existing)
            incoming_comparable = dict(receipt)
            existing_comparable.pop("validated_at_utc", None)
            incoming_comparable.pop("validated_at_utc", None)
            if existing_comparable == incoming_comparable:
                return existing
    temporary = root / f".{destination.name}.tmp-{uuid.uuid4().hex}"
    payload = (
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        descriptor = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if temporary.exists():
            temporary.unlink(missing_ok=True)
    return dict(receipt)


_V2_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "handoff_id",
        "authority_contract_id",
        "identity",
        "producer",
        "raw_input",
        "normalized_input",
        "mandatory_gate_receipts",
        "exit_authorization",
        "artifact_manifest",
        "commit_protocol",
        "created_at_utc",
    }
)
_V2_IDENTITY_KEYS = frozenset(
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
_SHORT_TO_LONG_GATES = {
    "G5": "G5_ANSWER_PRESENT",
    "G6": "G6_ANSWER_RELEVANT",
    "G7": "G7_FACTUAL_CLAIMS_HAVE_EVIDENCE",
    "G21": "G21_OUTPUT_SCHEMA",
    "G24": "G24_REPLAY_ELIGIBLE",
    "G26": "G26_EXIT_ELIGIBILITY",
}


def _exact_keys(value: Any, expected: set[str] | frozenset[str]) -> bool:
    return isinstance(value, Mapping) and set(value) == set(expected)


def _as_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _valid_sha256(value: Any) -> bool:
    raw = str(value or "")
    if len(raw) != 71 or not raw.startswith("sha256:"):
        return False
    return all(char in "0123456789abcdef" for char in raw[7:])


def _validate_v2_handoff(
    *,
    manifest_path: Path,
    brief_ref: str,
    jd_ref: str,
    now: datetime | None,
    expected_target_company: str,
    expected_target_role: str,
    expected_parent_run_id: str,
    expected_request_id: str,
    expected_trace_root: str,
    expected_tenant_id: str,
) -> AppsResearchHandoffValidation:
    """Recompute the committed v2 bundle from bytes and fail closed on drift."""
    failures: list[str] = []
    artifact_validations: list[dict[str, Any]] = []
    root = manifest_path.parent.resolve()
    try:
        manifest_bytes = manifest_path.read_bytes()
    except OSError as exc:
        return AppsResearchHandoffValidation(
            observed=True,
            valid=False,
            reason=f"unreadable_v2_manifest:{type(exc).__name__}",
            envelope_path=str(manifest_path),
        )
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        return AppsResearchHandoffValidation(
            observed=True,
            valid=False,
            reason=f"unreadable_v2_manifest:{type(exc).__name__}",
            envelope_path=str(manifest_path),
        )
    if not isinstance(manifest, dict):
        manifest = {}
        failures.append("v2_manifest_not_object")
    if set(manifest) != _V2_TOP_LEVEL_KEYS:
        failures.append("v2_schema_top_level_keys_mismatch")
    if manifest.get("schema_version") != "apps_research.apps_rg_handoff.v2":
        failures.append("unsupported_v2_handoff_schema")
    if manifest.get("authority_contract_id") != "apps_research_rg_e2e_authority":
        failures.append("authority_contract_id_mismatch")

    identity_raw = manifest.get("identity")
    identity = _as_mapping(identity_raw)
    if set(identity) != _V2_IDENTITY_KEYS:
        failures.append("identity_schema_keys_mismatch")
    expected_identity_literals = {
        "producer_app_id": "apps_research",
        "consumer_app_id": "apps_rg",
        "schema_version": "apps_research_rg_run_identity.v1",
    }
    for key, expected in expected_identity_literals.items():
        if identity.get(key) != expected:
            failures.append(f"identity_{key}_mismatch")
    for key in _V2_IDENTITY_KEYS:
        if not str(identity.get(key) or "").strip():
            failures.append(f"identity_missing_{key}")
    for key in ("jd_sha256", "brief_sha256", "policy_hash", "blueprint_hash"):
        if not _valid_sha256(identity.get(key)):
            failures.append(f"identity_{key}_format_invalid")

    commit_raw = manifest.get("commit_protocol")
    commit = _as_mapping(commit_raw)
    if not _exact_keys(
        commit,
        {
            "protocol",
            "temporary_bundle_ref",
            "committed_bundle_ref",
            "commit_marker_ref",
            "commit_marker_sha256",
            "consumer_validation_receipt_name",
        },
    ):
        failures.append("commit_protocol_schema_keys_mismatch")
    if commit.get("protocol") != "write_fsync_atomic_rename_marker.v1":
        failures.append("commit_protocol_mismatch")
    if commit.get("consumer_validation_receipt_name") != (
        "apps_research_handoff_validation_receipt.json"
    ):
        failures.append("consumer_validation_receipt_name_mismatch")
    committed_ref = Path(str(commit.get("committed_bundle_ref") or ""))
    if not committed_ref.is_absolute() or committed_ref.resolve() != root:
        failures.append("committed_bundle_ref_mismatch")
    marker_ref = Path(str(commit.get("commit_marker_ref") or ""))
    if not marker_ref.is_absolute() or marker_ref.resolve() != root / "bundle_commit_manifest.json":
        failures.append("commit_marker_ref_mismatch")
    temporary_ref = Path(str(commit.get("temporary_bundle_ref") or ""))
    if (
        not temporary_ref.is_absolute()
        or temporary_ref.parent.resolve() != root.parent
        or not temporary_ref.name.startswith(f".{root.name}.staging-")
    ):
        failures.append("temporary_bundle_ref_mismatch")
    elif temporary_ref.exists():
        failures.append("temporary_bundle_still_present")
    marker_bytes = b""
    marker: dict[str, Any] = {}
    if not marker_ref.is_file() or not _path_within(marker_ref, root):
        failures.append("missing_commit_marker")
    else:
        try:
            marker_bytes = marker_ref.read_bytes()
        except OSError:
            marker_bytes = b""
            failures.append("unreadable_commit_marker")
        try:
            loaded_marker = json.loads(marker_bytes)
            marker = dict(loaded_marker) if isinstance(loaded_marker, Mapping) else {}
        except json.JSONDecodeError:
            failures.append("unreadable_commit_marker")
        if _sha256_bytes(marker_bytes) != str(commit.get("commit_marker_sha256") or ""):
            failures.append("commit_marker_sha256_mismatch")
        if marker.get("status") != "COMMITTED":
            failures.append("commit_marker_status_mismatch")
        if marker.get("handoff_id") != manifest.get("handoff_id"):
            failures.append("commit_marker_handoff_id_mismatch")
        if marker.get("authority_contract_id") != manifest.get("authority_contract_id"):
            failures.append("commit_marker_authority_contract_mismatch")
        if marker.get("created_at_utc") != manifest.get("created_at_utc"):
            failures.append("commit_marker_created_at_mismatch")
        if set(marker) != {
            "schema_version",
            "authority_contract_id",
            "handoff_id",
            "artifact_manifest_sha256",
            "artifact_count",
            "status",
            "created_at_utc",
        }:
            failures.append("commit_marker_schema_keys_mismatch")

    artifact_manifest_raw = manifest.get("artifact_manifest")
    artifact_manifest = _as_mapping(artifact_manifest_raw)
    if not _exact_keys(
        artifact_manifest, {"artifacts", "artifact_count", "manifest_sha256"}
    ):
        failures.append("artifact_manifest_schema_keys_mismatch")
    rows_raw = artifact_manifest.get("artifacts")
    rows = list(rows_raw) if isinstance(rows_raw, list) else []
    if _int_or_none(artifact_manifest.get("artifact_count")) != len(rows):
        failures.append("artifact_count_mismatch")
    manifest_root_digest = _sha256_bytes(_canonical_json_bytes(rows))
    if manifest_root_digest != str(artifact_manifest.get("manifest_sha256") or ""):
        failures.append("artifact_manifest_sha256_mismatch")
    if marker.get("artifact_manifest_sha256") != manifest_root_digest:
        failures.append("commit_marker_artifact_manifest_mismatch")
    if _int_or_none(marker.get("artifact_count")) != len(rows):
        failures.append("commit_marker_artifact_count_mismatch")

    artifact_bytes_by_name: dict[str, bytes] = {}
    artifact_digest_by_ref: dict[str, str] = {}
    artifact_ids_seen: set[str] = set()
    artifact_refs_seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            failures.append("artifact_manifest_row_not_object")
            continue
        if set(row) != {
            "artifact_id",
            "artifact_ref",
            "sha256",
            "byte_length",
            "media_type",
            "required",
        }:
            failures.append("artifact_manifest_row_schema_keys_mismatch")
        ref = Path(str(row.get("artifact_ref") or ""))
        expected_sha = str(row.get("sha256") or "")
        artifact_id = str(row.get("artifact_id") or "")
        resolved_ref = str(ref.resolve())
        if artifact_id in artifact_ids_seen or resolved_ref in artifact_refs_seen:
            failures.append("artifact_manifest_duplicate_identity")
        artifact_ids_seen.add(artifact_id)
        artifact_refs_seen.add(resolved_ref)
        if row.get("required") is not True:
            failures.append(f"artifact_not_required:{ref.name}")
        if not _valid_sha256(expected_sha):
            failures.append(f"artifact_sha256_format_invalid:{ref.name}")
        actual = b""
        status = "BLOCKED"
        if (
            not ref.is_absolute()
            or ref != ref.resolve()
            or ref.is_symlink()
            or not _path_within(ref, root)
        ):
            failures.append(f"artifact_ref_outside_committed_bundle:{ref}")
        elif not ref.is_file():
            failures.append(f"artifact_missing:{ref.name}")
        else:
            try:
                actual = ref.read_bytes()
            except OSError:
                actual = b""
                failures.append(f"artifact_unreadable:{ref.name}")
            actual_sha = _sha256_bytes(actual)
            if len(actual) != _int_or_none(row.get("byte_length")):
                failures.append(f"artifact_byte_length_mismatch:{ref.name}")
            elif actual_sha != expected_sha:
                failures.append(f"artifact_sha256_mismatch:{ref.name}")
            else:
                status = "PASS"
            artifact_bytes_by_name[ref.name] = actual
            artifact_digest_by_ref[resolved_ref] = actual_sha
        artifact_validations.append(
            {
                "artifact_ref": str(ref),
                "expected_sha256": expected_sha,
                "actual_sha256": _sha256_bytes(actual),
                "byte_length": len(actual),
                "status": status,
            }
        )

    required_names = {
        "briefing.md",
        "job_description.raw.txt",
        "job_description.normalized.txt",
        "apps_research_u0_receipt.json",
        "apps_research_gate_mesh_result.json",
        "sealed_workflow_package.json",
        "exit_review_packet.json",
        "exit_disposition_receipt.json",
        "runtime_exhaust_bundle.json",
        "company_brief.json",
        "run_metadata.json",
    }
    if set(artifact_bytes_by_name) != required_names:
        failures.append("artifact_manifest_required_set_mismatch")

    try:
        supplied_brief_bytes = Path(brief_ref).read_bytes()
    except OSError:
        supplied_brief_bytes = b""
        failures.append("brief_unreadable")
    if _sha256_bytes(supplied_brief_bytes) != str(identity.get("brief_sha256") or ""):
        failures.append("brief_sha256_mismatch")
    if _sha256_bytes(artifact_bytes_by_name.get("briefing.md", b"")) != str(
        identity.get("brief_sha256") or ""
    ):
        failures.append("committed_brief_sha256_mismatch")
    if jd_ref:
        try:
            supplied_jd_bytes = _normalized_input_bytes(jd_ref)
        except (OSError, UnicodeError):
            supplied_jd_bytes = b""
            failures.append("jd_unreadable")
        if _sha256_bytes(supplied_jd_bytes) != str(identity.get("jd_sha256") or ""):
            failures.append("jd_sha256_mismatch")

    raw_input = _as_mapping(manifest.get("raw_input"))
    normalized_input = _as_mapping(manifest.get("normalized_input"))
    if not _exact_keys(raw_input, {"artifact_ref", "sha256", "byte_length"}):
        failures.append("raw_input_schema_keys_mismatch")
    if not _exact_keys(
        normalized_input,
        {
            "artifact_ref",
            "sha256",
            "byte_length",
            "normalization_profile_hash",
            "raw_input_sha256",
        },
    ):
        failures.append("normalized_input_schema_keys_mismatch")
    for label, section in (("raw_input", raw_input), ("normalized_input", normalized_input)):
        ref = Path(str(section.get("artifact_ref") or ""))
        actual_digest = artifact_digest_by_ref.get(str(ref.resolve()), "")
        if actual_digest != str(section.get("sha256") or ""):
            failures.append(f"{label}_sha256_mismatch")
    if normalized_input.get("raw_input_sha256") != raw_input.get("sha256"):
        failures.append("normalized_raw_input_lineage_mismatch")
    if normalized_input.get("sha256") != identity.get("jd_sha256"):
        failures.append("identity_normalized_jd_mismatch")
    expected_normalization_profile = _sha256_bytes(
        b"apps_research.apps_rg.jd_normalization.v1"
    )
    if normalized_input.get("normalization_profile_hash") != expected_normalization_profile:
        failures.append("normalization_profile_hash_mismatch")
    if _int_or_none(raw_input.get("byte_length")) != len(
        artifact_bytes_by_name.get("job_description.raw.txt", b"")
    ):
        failures.append("raw_input_byte_length_mismatch")
    if _int_or_none(normalized_input.get("byte_length")) != len(
        artifact_bytes_by_name.get("job_description.normalized.txt", b"")
    ):
        failures.append("normalized_input_byte_length_mismatch")

    gate_receipts_raw = manifest.get("mandatory_gate_receipts")
    gate_receipts = _as_mapping(gate_receipts_raw)
    if set(gate_receipts) != set(_SHORT_TO_LONG_GATES):
        failures.append("mandatory_gate_receipt_set_mismatch")
    for gate_id, row_raw in gate_receipts.items():
        row = _as_mapping(row_raw)
        if not _exact_keys(
            row, {"gate_id", "status", "receipt_ref", "receipt_sha256", "schema_version"}
        ):
            failures.append(f"mandatory_gate_receipt_schema_keys_mismatch:{gate_id}")
        ref = Path(str(row.get("receipt_ref") or ""))
        if row.get("gate_id") != gate_id or row.get("status") != "PASS":
            failures.append(f"mandatory_gate_receipt_invalid:{gate_id}")
        if artifact_digest_by_ref.get(str(ref.resolve()), "") != row.get("receipt_sha256"):
            failures.append(f"mandatory_gate_receipt_sha256_mismatch:{gate_id}")
    try:
        gate_mesh = json.loads(artifact_bytes_by_name.get("apps_research_gate_mesh_result.json", b"{}"))
    except json.JSONDecodeError:
        gate_mesh = {}
        failures.append("gate_mesh_unreadable")
    verdicts = gate_mesh.get("verdicts") if isinstance(gate_mesh, Mapping) else []
    pass_ids = {
        str(row.get("gate_id") or "")
        for row in (verdicts or [])
        if isinstance(row, Mapping) and row.get("result") == "PASS"
    }
    required_long_gates = set(_SHORT_TO_LONG_GATES.values())
    if pass_ids != required_long_gates:
        failures.append("gate_mesh_exact_pass_set_mismatch")
    if set(gate_mesh.get("required_gate_ids") or []) != required_long_gates:
        failures.append("gate_mesh_required_set_mismatch")
    if gate_mesh.get("hard_fail_present") or gate_mesh.get("unknown_material_present"):
        failures.append("gate_mesh_not_clean")
    if list(gate_mesh.get("missing_gate_ids") or []):
        failures.append("gate_mesh_missing_gates")
    for field, expected in (
        ("run_id", identity.get("child_run_id")),
        ("request_id", identity.get("request_id")),
        ("trace_root", identity.get("trace_root")),
    ):
        if str(gate_mesh.get(field) or "") != str(expected or ""):
            failures.append(f"gate_mesh_{field}_identity_mismatch")
    for verdict in verdicts or []:
        if not isinstance(verdict, Mapping):
            failures.append("gate_mesh_verdict_not_object")
            continue
        for field, expected in (
            ("run_id", identity.get("child_run_id")),
            ("request_id", identity.get("request_id")),
            ("trace_root", identity.get("trace_root")),
        ):
            if str(verdict.get(field) or "") != str(expected or ""):
                failures.append(f"gate_verdict_{field}_identity_mismatch")

    exit_auth = _as_mapping(manifest.get("exit_authorization"))
    if not _exact_keys(
        exit_auth,
        {"x3_code", "receipt_ref", "receipt_sha256", "output_artifact_sha256"},
    ):
        failures.append("exit_authorization_schema_keys_mismatch")
    if exit_auth.get("x3_code") != _CANONICAL_X3_ALLOW:
        failures.append("exit_authorization_not_x3d")
    exit_ref = Path(str(exit_auth.get("receipt_ref") or ""))
    if artifact_digest_by_ref.get(str(exit_ref.resolve()), "") != exit_auth.get("receipt_sha256"):
        failures.append("exit_authorization_receipt_sha256_mismatch")
    if exit_auth.get("output_artifact_sha256") != identity.get("brief_sha256"):
        failures.append("exit_authorization_output_sha256_mismatch")
    try:
        exit_receipt = json.loads(
            artifact_bytes_by_name.get("exit_disposition_receipt.json", b"{}")
        )
    except json.JSONDecodeError:
        exit_receipt = {}
        failures.append("exit_receipt_unreadable")
    if exit_receipt.get("x3_code") != _CANONICAL_X3_ALLOW:
        failures.append("persisted_exit_receipt_not_x3d")
    if exit_receipt.get("required_gates_passed") is not True:
        failures.append("persisted_exit_required_gates_not_passed")
    for field in ("hard_fail_count", "unknown_count", "missing_gate_count"):
        if _int_or_none(exit_receipt.get(field)) != 0:
            failures.append(f"persisted_exit_{field}_nonzero")
    for field, expected in (
        ("run_id", identity.get("child_run_id")),
        ("request_id", identity.get("request_id")),
        ("trace_root", identity.get("trace_root")),
    ):
        if str(exit_receipt.get(field) or "") != str(expected or ""):
            failures.append(f"persisted_exit_{field}_identity_mismatch")
    exit_seed = dict(exit_receipt)
    exit_digest = str(exit_seed.get("deterministic_digest") or "")
    exit_seed["deterministic_digest"] = ""
    if _sha256_json(exit_seed) != exit_digest:
        failures.append("persisted_exit_deterministic_digest_mismatch")

    def load_committed_json(name: str) -> dict[str, Any]:
        try:
            loaded = json.loads(artifact_bytes_by_name.get(name, b"{}"))
        except json.JSONDecodeError:
            failures.append(f"committed_json_unreadable:{name}")
            return {}
        if not isinstance(loaded, Mapping):
            failures.append(f"committed_json_not_object:{name}")
            return {}
        return dict(loaded)

    sealed = load_committed_json("sealed_workflow_package.json")
    review = load_committed_json("exit_review_packet.json")
    exhaust = load_committed_json("runtime_exhaust_bundle.json")
    if str(sealed.get("run_id") or "") != str(identity.get("child_run_id") or ""):
        failures.append("sealed_workflow_run_id_identity_mismatch")
    if str(sealed.get("trace_root") or "") != str(identity.get("trace_root") or ""):
        failures.append("sealed_workflow_trace_root_identity_mismatch")
    if sealed.get("terminal_class") != "success":
        failures.append("sealed_workflow_terminal_class_not_success")
    if exit_receipt.get("sealed_workflow_package_ref") != sealed.get("package_id"):
        failures.append("exit_sealed_workflow_ref_mismatch")
    if exit_receipt.get("output_artifact_digest") != sealed.get("merged_content_digest"):
        failures.append("exit_sealed_output_digest_mismatch")
    if exit_receipt.get("gate_mesh_result_ref") != gate_mesh.get("deterministic_digest"):
        failures.append("exit_gate_mesh_ref_mismatch")

    for field, expected in (
        ("run_id", identity.get("child_run_id")),
        ("request_id", identity.get("request_id")),
        ("trace_root", identity.get("trace_root")),
    ):
        if str(review.get(field) or "") != str(expected or ""):
            failures.append(f"exit_review_{field}_identity_mismatch")
    x1 = _as_mapping(review.get("x1_checkout_result"))
    x2 = _as_mapping(review.get("x2_aggregation_result"))
    if x1.get("overall_pass") is not True or list(x1.get("blockers") or []):
        failures.append("exit_review_x1_not_pass")
    x2_gate_verdicts = _as_mapping(x2.get("gate_verdicts"))
    if set(x2_gate_verdicts.get("PASS") or []) != required_long_gates:
        failures.append("exit_review_x2_exact_pass_set_mismatch")
    if any(x2_gate_verdicts.get(key) for key in ("FAIL", "UNKNOWN", "WARN")):
        failures.append("exit_review_x2_nonpass_material")

    if str(exhaust.get("run_id") or "") != str(identity.get("child_run_id") or ""):
        failures.append("runtime_exhaust_run_id_identity_mismatch")
    if str(exhaust.get("trace_root") or "") != str(identity.get("trace_root") or ""):
        failures.append("runtime_exhaust_trace_root_identity_mismatch")
    if exhaust.get("created_after_exit") is not True:
        failures.append("runtime_exhaust_not_after_exit")
    if exhaust.get("exit_disposition_ref") != exit_digest:
        failures.append("runtime_exhaust_exit_ref_mismatch")
    if exhaust.get("gate_mesh_result_ref") != gate_mesh.get("deterministic_digest"):
        failures.append("runtime_exhaust_gate_mesh_ref_mismatch")
    if exhaust.get("sealed_result_ref") != sealed.get("package_id"):
        failures.append("runtime_exhaust_sealed_ref_mismatch")

    try:
        u0_receipt = json.loads(
            artifact_bytes_by_name.get("apps_research_u0_receipt.json", b"{}")
        )
    except json.JSONDecodeError:
        u0_receipt = {}
        failures.append("u0_receipt_unreadable")
    if u0_receipt.get("status") != "PASS":
        failures.append("apps_research_u0_not_pass")
    if u0_receipt.get("authority_contract_id") != "apps_research_rg_e2e_authority":
        failures.append("apps_research_u0_authority_contract_mismatch")
    for receipt_field, identity_field in (
        ("request_id", "request_id"),
        ("parent_run_id", "parent_run_id"),
        ("child_run_id", "child_run_id"),
        ("trace_root", "trace_root"),
        ("tenant_id", "tenant_id"),
    ):
        if str(u0_receipt.get(receipt_field) or "") != str(
            identity.get(identity_field) or ""
        ):
            failures.append(f"apps_research_u0_{receipt_field}_identity_mismatch")

    repo_root = Path(__file__).resolve().parents[2]
    policy_path = repo_root / "config/certification/apps_research_rg_e2e_authority_contract.v1.json"
    blueprint_path = repo_root / "apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.json"
    expected_policy = _sha256_bytes(policy_path.read_bytes())
    expected_blueprint = _sha256_bytes(blueprint_path.read_bytes())
    if identity.get("policy_hash") != expected_policy:
        failures.append("policy_hash_mismatch")
    if identity.get("blueprint_hash") != expected_blueprint:
        failures.append("blueprint_hash_mismatch")

    expected_fields = {
        "target_company": expected_target_company,
        "target_role": expected_target_role,
        "parent_run_id": expected_parent_run_id,
        "request_id": expected_request_id,
        "trace_root": expected_trace_root,
        "tenant_id": expected_tenant_id,
    }
    for key, expected in expected_fields.items():
        if expected and str(identity.get(key) or "") != str(expected):
            failures.append(f"identity_{key}_context_mismatch")

    observed_now = now or datetime.now(timezone.utc)
    created_at = _parse_timestamp(manifest.get("created_at_utc"))
    if created_at is None:
        failures.append("missing_created_at_utc")
    elif created_at > observed_now + timedelta(minutes=5):
        failures.append("handoff_created_in_future")
    elif observed_now - created_at > timedelta(days=7):
        failures.append("stale_handoff")

    producer = _as_mapping(manifest.get("producer"))
    if not _exact_keys(
        producer, {"producer_app_id", "producer_run_id", "attestation_sha256"}
    ):
        failures.append("producer_schema_keys_mismatch")
    attestation_seed = {
        "identity": identity,
        "u0_receipt_sha256": _sha256_bytes(
            artifact_bytes_by_name.get("apps_research_u0_receipt.json", b"")
        ),
        "exit_receipt_sha256": _sha256_bytes(
            artifact_bytes_by_name.get("exit_disposition_receipt.json", b"")
        ),
    }
    expected_attestation = _sha256_bytes(_canonical_json_bytes(attestation_seed))
    if producer.get("producer_app_id") != "apps_research":
        failures.append("producer_app_id_mismatch")
    if producer.get("producer_run_id") != identity.get("child_run_id"):
        failures.append("producer_run_id_mismatch")
    if producer.get("attestation_sha256") != expected_attestation:
        failures.append("producer_attestation_sha256_mismatch")

    receipt = {
        "schema_version": "apps_rg.apps_research_handoff_validation_receipt.v2",
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "identity": identity,
        "identity_sha256": _sha256_bytes(_canonical_json_bytes(identity)),
        "raw_input_sha256": str(raw_input.get("sha256") or ""),
        "normalized_input_sha256": str(normalized_input.get("sha256") or ""),
        "bundle_manifest_sha256": _sha256_bytes(manifest_bytes),
        "commit_marker_sha256": _sha256_bytes(marker_bytes),
        "artifact_validations": artifact_validations,
        "status": "BLOCKED" if failures else "PASS",
        "failure_reasons": sorted(set(failures)),
        "validated_at_utc": observed_now.isoformat(),
    }
    try:
        receipt = _persist_consumer_receipt(root, receipt)
    except OSError as exc:
        failures.append(f"consumer_receipt_persist_failed:{type(exc).__name__}")
        receipt["status"] = "BLOCKED"
        receipt["failure_reasons"] = sorted(set(failures))

    return AppsResearchHandoffValidation(
        observed=True,
        valid=not failures,
        reason="ok" if not failures else ";".join(sorted(set(failures))),
        envelope_path=str(manifest_path),
        envelope=manifest,
        receipt=receipt,
    )


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def validate_apps_research_handoff(
    *,
    brief_ref: str,
    jd_ref: str = "",
    now: datetime | None = None,
    require_observed: bool = False,
    require_x1_x3_authorization: bool = False,
    require_canonical_exit: bool = False,
    expected_target_company: str = "",
    expected_target_role: str = "",
    expected_parent_run_id: str = "",
    expected_request_id: str = "",
    expected_trace_root: str = "",
    expected_tenant_id: str = "",
) -> AppsResearchHandoffValidation:
    """Fail-closed validator for apps_research handoff envelopes.

    Ordinary user-authored ``--manual-brief`` files remain supported when
    ``require_observed`` is false. Once an apps_research envelope is present it
    becomes authoritative for freshness, digest coherence, and—when present or
    required—the canonical GateMesh/Exit authorization chain.
    """
    handoff_v2_path = find_apps_research_handoff_v2_for_briefing(brief_ref)
    if handoff_v2_path is not None:
        return _validate_v2_handoff(
            manifest_path=handoff_v2_path,
            brief_ref=brief_ref,
            jd_ref=jd_ref,
            now=now,
            expected_target_company=expected_target_company,
            expected_target_role=expected_target_role,
            expected_parent_run_id=expected_parent_run_id,
            expected_request_id=expected_request_id,
            expected_trace_root=expected_trace_root,
            expected_tenant_id=expected_tenant_id,
        )

    envelope_path = find_legacy_apps_research_envelope_for_briefing(brief_ref)
    if envelope_path is None:
        valid = not require_observed
        return AppsResearchHandoffValidation(
            observed=False,
            valid=valid,
            reason=(
                "missing_apps_research_handoff_v2"
                if require_observed
                else "no_apps_research_handoff_present"
            ),
        )
    return AppsResearchHandoffValidation(
        observed=True,
        valid=False,
        reason="legacy_only_handoff_rejected",
        envelope_path=str(envelope_path),
        receipt={
            "schema_version": "apps_rg.apps_research_handoff_validation_receipt.v2",
            "observed": True,
            "valid": False,
            "reason": "legacy_only_handoff_rejected",
            "envelope_path": str(envelope_path),
        },
    )



class HistoricalBriefingValidator:
    """Validates that a company research briefing meets prerequisite policy."""

    DEFAULT_MAX_FRESHNESS_HOURS: float = 168.0
    DEFAULT_REQUIRED_SECTIONS: frozenset[str] = frozenset({
        "company_overview",
        "role_context",
    })

    def __init__(
        self,
        *,
        max_freshness_hours: float = DEFAULT_MAX_FRESHNESS_HOURS,
        required_sections: frozenset[str] | None = None,
        policy_hash: str = "",
    ) -> None:
        self.max_freshness_hours = max_freshness_hours
        self.required_sections = required_sections or self.DEFAULT_REQUIRED_SECTIONS
        self.policy_hash = policy_hash

    def validate(
        self,
        briefing: dict[str, Any] | None,
        *,
        target_company: str = "",
        target_role: str = "",
    ) -> BriefingCheck:
        """Validate a briefing dict and return a BriefingCheck."""
        if briefing is None:
            return BriefingCheck(
                result=BriefingValidationResult.MISSING,
                briefing=None,
                reason="No briefing provided",
            )

        if self.policy_hash:
            bp_hash = briefing.get("policy_hash", "")
            if bp_hash and bp_hash != self.policy_hash:
                return BriefingCheck(
                    result=BriefingValidationResult.POLICY_MISMATCH,
                    briefing=briefing,
                    reason=(
                        f"Policy hash mismatch: expected {self.policy_hash!r}, "
                        f"got {bp_hash!r}"
                    ),
                )

        if target_company:
            brief_company = briefing.get("company", "") or briefing.get(
                "target_company", ""
            )
            if brief_company and brief_company.lower() != target_company.lower():
                return BriefingCheck(
                    result=BriefingValidationResult.BLUEPRINT_MISMATCH,
                    briefing=briefing,
                    reason=(
                        f"Briefing company {brief_company!r} "
                        f"!= target {target_company!r}"
                    ),
                )

        import datetime

        generated_at = briefing.get("generated_at") or briefing.get("created_at")
        freshness_hours: float | None = None
        if generated_at:
            try:
                if isinstance(generated_at, str):
                    ts = datetime.datetime.fromisoformat(
                        generated_at.replace("Z", "+00:00")
                    )
                else:
                    ts = generated_at
                now = datetime.datetime.now(datetime.timezone.utc)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=datetime.timezone.utc)
                age_hours = (now - ts).total_seconds() / 3600
                freshness_hours = age_hours
                if age_hours > self.max_freshness_hours:
                    return BriefingCheck(
                        result=BriefingValidationResult.STALE,
                        briefing=briefing,
                        reason=(
                            f"Briefing is {age_hours:.1f}h old "
                            f"(limit: {self.max_freshness_hours}h)"
                        ),
                        freshness_hours=age_hours,
                    )
            except Exception:
                pass

        missing = self.required_sections - set(briefing.keys())
        if missing:
            return BriefingCheck(
                result=BriefingValidationResult.INCOMPLETE,
                briefing=briefing,
                reason=f"Missing required sections: {sorted(missing)}",
                freshness_hours=freshness_hours,
            )

        return BriefingCheck(
            result=BriefingValidationResult.VALID,
            briefing=briefing,
            reason="Briefing is valid",
            freshness_hours=freshness_hours,
        )


def check_briefing_prerequisite(
    briefing: dict[str, Any] | None,
    *,
    target_company: str = "",
    target_role: str = "",
    max_freshness_hours: float = HistoricalBriefingValidator.DEFAULT_MAX_FRESHNESS_HOURS,
) -> BriefingCheck:
    """Convenience wrapper — validates a briefing with default policy."""
    validator = HistoricalBriefingValidator(
        max_freshness_hours=max_freshness_hours
    )
    return validator.validate(
        briefing,
        target_company=target_company,
        target_role=target_role,
    )
