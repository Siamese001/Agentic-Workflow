"""Fail-closed validation for prelabel and completed human-review packets."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from ._io import (
    digest_matches,
    file_digest,
    private_path_error,
    read_json,
    read_jsonl,
    record_with_digest,
    stable_digest,
)
from ._safety import unsafe_reviewer_keys
from .packet import (
    EXPECTED_CLAIM_ITEMS,
    EXPECTED_RETRIEVAL_QUERIES,
    EXPECTED_W9_PAIRS,
    FULL_UNIVERSE_JUDGING_SCOPE,
    INTERNAL_FILES,
    MANIFEST_SCHEMA,
    REVIEWER_FILES,
    REVIEWER_ROOTS,
    RETRIEVAL_SPLIT_POLICY_ID,
    _reviewer_asset_sources,
    frontier_contract_error,
    frontier_metadata_contract_error,
    metric_applicable,
    reviewer_distribution_files,
    reviewer_distribution_files_by_cohort,
    sealed_internal_files,
)
from .split_policy import (
    PROOF_SPLIT_POLICY_ID,
    ProofSplitPolicyError,
    proof_identity_and_split,
    proof_split_group_digest,
)
from .source_bundle import SOURCE_FREEZE_RECEIPT_SCHEMA

EXPECTED_CLAIM_RETRIEVAL_SPLITS = {"calibration": 141, "release_holdout": 141}
EXPECTED_QUERY_RETRIEVAL_SPLITS = {"calibration": 42, "release_holdout": 42}
MINIMUM_PROOF_SPLIT_COUNT = 20
EXPECTED_SECTION_COUNTS = {
    "competencies": 48,
    "unify_bullets": 36,
    "ibm_bullets": 30,
    "insurtech_bullets": 18,
    "ey_bullets": 18,
    "unify_narrative": 36,
    "ibm_narrative": 30,
    "insurtech_narrative": 18,
    "ey_narrative": 18,
    "executive_summary": 18,
    "headline": 12,
}
EXPECTED_QUERY_SECTION_COUNTS = {
    "competencies": 12,
    "unify_bullets": 12,
    "ibm_bullets": 12,
    "insurtech_bullets": 12,
    "ey_bullets": 12,
    "executive_summary": 12,
    "headline": 12,
}
EXPECTED_PROFILE_COUNTS = {
    "ai_partnerships_gtm": 94,
    "svp_agentic_engineering_platform": 94,
    "insurance_it_strategy_modernization": 94,
}
NON_HUMAN_TOKENS = {
    "agent",
    "ai",
    "assistant",
    "auto",
    "automated",
    "automation",
    "bot",
    "cascade",
    "claude",
    "codex",
    "gpt",
    "judge",
    "llm",
    "machine",
    "model",
    "openai",
    "pipeline",
    "robot",
    "synthetic",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
W9_QUALIFICATION_PREFIX = "resume-coach://"
HUMAN_REVIEW_AUTHORITY_SCHEMA = (
    "apps_rg.c03_human_eval.human_review_authority_receipt.v1"
)


def _result(schema: str) -> dict[str, Any]:
    return {"schema_version": schema, "status": "FAIL", "pass": False, "errors": [], "checks": {}}


def _error(report: dict[str, Any], message: str) -> None:
    report["errors"].append(message)


def _check_private_path(
    path: Path,
    *,
    directory: bool,
    label: str,
    report: dict[str, Any],
) -> bool:
    mode_error = private_path_error(path, directory=directory)
    if mode_error:
        _error(report, f"{label} {mode_error}")
        return False
    return True


def _safe_load_jsonl(path: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        return read_jsonl(path)
    except (OSError, ValueError, TypeError) as exc:
        _error(report, f"{path}: {exc}")
        return []


def _index_rows(
    rows: Sequence[Mapping[str, Any]], id_key: str, digest_key: str, label: str, report: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_id = str(row.get(id_key) or "")
        if not row_id:
            _error(report, f"{label}: missing {id_key}")
            continue
        if row_id in index:
            _error(report, f"{label}: duplicate {id_key} {row_id}")
        if not digest_matches(row, digest_key):
            _error(report, f"{label}/{row_id}: invalid {digest_key}")
        index[row_id] = dict(row)
    return index


def human_review_authority_receipt_file_sha256(
    receipt: Mapping[str, Any],
) -> str:
    """Match owner-only ``write_json`` bytes for explicit test-only receipts."""

    encoded = (
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _utc_timestamp(value: Any, label: str, report: dict[str, Any]) -> datetime | None:
    text = str(value or "").strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        _error(report, f"{label} must be an ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        _error(report, f"{label} must include a timezone")
        return None
    return parsed.astimezone(timezone.utc)


def _human_review_authority(
    *,
    value: Mapping[str, Any] | Path | None,
    trusted_file_sha256: str | None,
    manifest: Mapping[str, Any],
    prelabel_manifest_sha256: str,
    allow_test_only_provenance: bool,
    report: dict[str, Any],
) -> tuple[
    dict[tuple[str, str], dict[str, Any]], datetime | None, str, bool, bool
]:
    """Validate an out-of-band roster/assignment authority receipt."""

    expected_sha = str(trusted_file_sha256 or "").strip()
    if not HEX64.fullmatch(expected_sha):
        _error(report, "trusted human-review authority receipt file SHA-256 is required")
    if isinstance(value, Path):
        mode_error = private_path_error(value, directory=False)
        if mode_error:
            _error(report, f"human-review authority receipt {mode_error}")
            raw = {}
            observed_file_sha = ""
        else:
            try:
                raw = read_json(value)
                observed_file_sha = file_digest(value)
            except (OSError, ValueError, TypeError) as exc:
                _error(report, f"invalid human-review authority receipt: {exc}")
                raw = {}
                observed_file_sha = ""
    elif isinstance(value, Mapping):
        raw = dict(value)
        observed_file_sha = human_review_authority_receipt_file_sha256(raw)
        if not allow_test_only_provenance:
            _error(
                report,
                "official completed validation requires a human-review authority receipt file",
            )
    else:
        raw = {}
        observed_file_sha = ""
        _error(report, "human-review authority receipt is required")
    if observed_file_sha != expected_sha:
        _error(report, "human-review authority receipt differs from trusted file SHA-256")
    receipt = dict(raw) if isinstance(raw, Mapping) else {}
    expected_keys = {
        "schema_version",
        "authority_mode",
        "official_authority_eligible",
        "packet_id",
        "packet_manifest_digest",
        "prelabel_packet_manifest_sha256",
        "source_freeze_receipt_digest",
        "cohort_manifest_digests",
        "issuer_ref",
        "approval_ref",
        "issued_at",
        "authorized_participants",
        "unknown_is_pass",
        "receipt_digest",
    }
    if set(receipt) != expected_keys:
        _error(report, "human-review authority receipt fields differ from the frozen contract")
    if receipt.get("schema_version") != HUMAN_REVIEW_AUTHORITY_SCHEMA:
        _error(report, "unsupported human-review authority receipt schema")
    if not digest_matches(receipt, "receipt_digest"):
        _error(report, "human-review authority receipt digest mismatch")
    bindings = {
        "packet_id": manifest.get("packet_id"),
        "packet_manifest_digest": manifest.get("manifest_digest"),
        "prelabel_packet_manifest_sha256": prelabel_manifest_sha256,
        "source_freeze_receipt_digest": manifest.get("source_freeze_receipt_digest"),
        "cohort_manifest_digests": {
            cohort: distribution.get("manifest_digest")
            for cohort, distribution in (manifest.get("reviewer_distributions") or {}).items()
            if isinstance(distribution, Mapping)
        },
    }
    for field, expected in bindings.items():
        if receipt.get(field) != expected:
            _error(report, f"human-review authority receipt {field} binding mismatch")
    if receipt.get("unknown_is_pass") is not False:
        _error(report, "human-review authority receipt must make UNKNOWN non-passing")
    if not str(receipt.get("issuer_ref") or "").startswith("authority-issuer://"):
        _error(report, "human-review authority issuer_ref must use authority-issuer://")
    if not str(receipt.get("approval_ref") or "").startswith("approval://"):
        _error(report, "human-review authority approval_ref must use approval://")
    issued_at = _utc_timestamp(receipt.get("issued_at"), "authority issued_at", report)
    official_authority = bool(
        isinstance(value, Path)
        and receipt.get("authority_mode") == "TRUSTED_HUMAN_ROSTER_APPROVAL"
        and receipt.get("official_authority_eligible") is True
    )
    if not official_authority and not allow_test_only_provenance:
        _error(report, "human-review authority receipt is not eligible for official PASS")
    participants = receipt.get("authorized_participants")
    if not isinstance(participants, list) or not participants:
        _error(report, "human-review authority receipt requires authorized participants")
        participants = []
    roster: dict[tuple[str, str], dict[str, Any]] = {}
    identities_seen: dict[str, str] = {}
    for index, raw_participant in enumerate(participants):
        if not isinstance(raw_participant, Mapping):
            _error(report, f"authority participant[{index}] must be an object")
            continue
        expected_participant_keys = {
            "cohort",
            "identity_ref",
            "identity_hash",
            "roles",
            "qualification_ref",
        }
        if set(raw_participant) != expected_participant_keys:
            _error(report, f"authority participant[{index}] fields differ from contract")
        cohort = str(raw_participant.get("cohort") or "")
        identity_ref = str(raw_participant.get("identity_ref") or "")
        identity_hash = str(raw_participant.get("identity_hash") or "")
        roles = raw_participant.get("roles")
        if cohort not in {"proof", "retrieval", "w9"}:
            _error(report, f"authority participant[{index}] has invalid cohort")
        if not identity_ref.startswith("human-reviewer://"):
            _error(report, f"authority participant[{index}] has invalid identity_ref")
        expected_identity_hash = hashlib.sha256(identity_ref.encode("utf-8")).hexdigest()
        if identity_hash != expected_identity_hash:
            _error(report, f"authority participant[{index}] identity hash mismatch")
        if (
            not isinstance(roles, list)
            or not roles
            or not set(roles).issubset({"primary", "adjudicator"})
        ):
            _error(report, f"authority participant[{index}] roles are invalid")
        prior_cohort = identities_seen.setdefault(identity_hash, cohort)
        if prior_cohort != cohort:
            _error(report, "one authorized identity cannot span reviewer cohorts")
        key = (cohort, identity_hash)
        if key in roster:
            _error(report, f"duplicate authority participant {cohort}/{identity_hash}")
        roster[key] = dict(raw_participant)
    receipt_trusted = bool(
        HEX64.fullmatch(expected_sha)
        and observed_file_sha == expected_sha
        and digest_matches(receipt, "receipt_digest")
        and all(receipt.get(field) == expected for field, expected in bindings.items())
        and receipt.get("unknown_is_pass") is False
    )
    return roster, issued_at, observed_file_sha, official_authority, receipt_trusted


def validate_prelabel_packet(
    packet_dir: Path,
    *,
    require_w9: bool = False,
    trusted_source_freeze_receipt_digest: str | None = None,
    allow_test_only_provenance: bool = False,
) -> dict[str, Any]:
    """Validate exact coverage, hashes, conservation, and reviewer blinding."""

    report = _result("apps_rg.c03_human_eval.prelabel_validation.v1")
    packet_alias = Path(packet_dir)
    packet_alias_valid = not packet_alias.is_symlink()
    if not packet_alias_valid:
        _error(report, "packet root must not be a symlink alias")
    root = packet_alias.resolve()
    controller_permissions_pass = _check_private_path(
        root,
        directory=True,
        label="packet root",
        report=report,
    ) and packet_alias_valid
    manifest_path = root / "packet_manifest.json"
    if not manifest_path.is_file():
        _error(report, "packet_manifest.json is missing")
        return report
    controller_permissions_pass = _check_private_path(
        manifest_path,
        directory=False,
        label="packet manifest",
        report=report,
    ) and controller_permissions_pass
    try:
        manifest = read_json(manifest_path)
    except (OSError, ValueError, TypeError) as exc:
        _error(report, f"invalid packet manifest: {exc}")
        return report
    if not isinstance(manifest, Mapping) or manifest.get("schema_version") != MANIFEST_SCHEMA:
        _error(report, "unsupported packet manifest schema")
        return report
    if not digest_matches(manifest, "manifest_digest"):
        _error(report, "packet manifest digest mismatch")
    for digest_field in ("graph_digest", "policy_digest"):
        if not HEX64.fullmatch(str(manifest.get(digest_field) or "")):
            _error(report, f"manifest {digest_field} must be a nonempty SHA-256 digest")
    blinding_nonce_commitment_valid = bool(
        HEX64.fullmatch(str(manifest.get("blinding_nonce_commitment") or ""))
    )
    if not blinding_nonce_commitment_valid:
        _error(report, "manifest blinding_nonce_commitment must be a SHA-256 digest")
    if "blinding_nonce" in manifest:
        _error(report, "packet manifest must not expose the secret blinding_nonce")
    trusted_receipt_digest = str(
        trusted_source_freeze_receipt_digest or ""
    ).strip()
    if not HEX64.fullmatch(trusted_receipt_digest):
        _error(
            report,
            "trusted source freeze receipt digest is required for official validation",
        )
    freeze_receipt = manifest.get("source_freeze_receipt")
    official_provenance_pass = False
    source_freeze_receipt_trusted = False
    if not isinstance(freeze_receipt, Mapping):
        _error(report, "packet manifest source_freeze_receipt must be an object")
        freeze_receipt = {}
    else:
        if freeze_receipt.get("schema_version") != SOURCE_FREEZE_RECEIPT_SCHEMA:
            _error(report, "unsupported packet source freeze receipt schema")
        if not digest_matches(freeze_receipt, "receipt_digest"):
            _error(report, "packet source freeze receipt digest mismatch")
        observed_receipt_digest = str(freeze_receipt.get("receipt_digest") or "")
        if observed_receipt_digest != trusted_receipt_digest:
            _error(report, "packet source freeze receipt differs from trusted digest")
        if manifest.get("source_freeze_receipt_digest") != observed_receipt_digest:
            _error(report, "packet manifest source freeze receipt binding mismatch")
        receipt_bindings = {
            "source_bundle_canonical_digest": manifest.get("source_bundle_digest"),
            "source_commit_sha": manifest.get("source_commit_sha"),
            "target_manifest_digest": manifest.get("target_manifest_digest"),
            "graph_digest": manifest.get("graph_digest"),
            "policy_digest": manifest.get("policy_digest"),
        }
        receipt_bindings_pass = True
        for field, expected_value in receipt_bindings.items():
            if freeze_receipt.get(field) != expected_value:
                receipt_bindings_pass = False
                _error(report, f"packet source freeze receipt {field} binding mismatch")
        if freeze_receipt.get("unknown_is_pass") is not False:
            _error(report, "packet source freeze receipt must make UNKNOWN non-passing")
        receipt_official = bool(
            freeze_receipt.get("freeze_mode")
            == "CLEAN_CHECKOUT_REAL_ALLOCATOR"
            and freeze_receipt.get("official_provenance_eligible") is True
            and freeze_receipt.get("checkout_head_verified") is True
            and freeze_receipt.get("checkout_clean_verified") is True
        )
        manifest_official = bool(
            manifest.get("source_provenance_status") == "OFFICIAL_PASS"
            and manifest.get("official_source_provenance_pass") is True
        )
        source_freeze_receipt_trusted = bool(
            digest_matches(freeze_receipt, "receipt_digest")
            and observed_receipt_digest == trusted_receipt_digest
            and manifest.get("source_freeze_receipt_digest")
            == observed_receipt_digest
            and receipt_bindings_pass
            and freeze_receipt.get("unknown_is_pass") is False
        )
        official_provenance_pass = receipt_official and manifest_official
        if not official_provenance_pass:
            if not allow_test_only_provenance:
                _error(
                    report,
                    "packet source provenance is test-only and cannot receive official PASS",
                )
            elif not (
                manifest.get("source_provenance_status") == "TEST_ONLY_UNTRUSTED"
                and manifest.get("official_source_provenance_pass") is False
            ):
                _error(report, "invalid test-only source provenance receipt")
    if manifest.get("proof_split_policy_id") != PROOF_SPLIT_POLICY_ID:
        _error(report, "manifest proof split policy differs from the frozen contract")
    retrieval_split_commitment = str(
        manifest.get("retrieval_split_assignment_commitment") or ""
    )
    secret_retrieval_split_binding = bool(
        manifest.get("retrieval_split_policy_id") == RETRIEVAL_SPLIT_POLICY_ID
        and HEX64.fullmatch(retrieval_split_commitment)
    )
    if not secret_retrieval_split_binding:
        _error(report, "manifest secret retrieval split policy/commitment is invalid")
    full_finite_universe_judging = bool(
        manifest.get("retrieval_candidate_judging_scope")
        == FULL_UNIVERSE_JUDGING_SCOPE
    )
    if not full_finite_universe_judging:
        _error(
            report,
            "manifest must bind retrieval judging to the full finite universe",
        )
    proof_split_salt = manifest.get("proof_split_policy_salt")
    if (
        not isinstance(proof_split_salt, int)
        or isinstance(proof_split_salt, bool)
        or proof_split_salt < 0
    ):
        _error(report, "manifest proof_split_policy_salt must be a nonnegative integer")
        proof_split_salt = 0
    include_w9_assets = require_w9
    if manifest.get("w9_ready") is not include_w9_assets:
        _error(
            report,
            "packet W9 readiness must exactly match the explicitly selected evaluation wave",
        )
    expected_distributions = reviewer_distribution_files_by_cohort(
        include_w9=include_w9_assets
    )
    expected_reviewer_files = reviewer_distribution_files(
        include_w9=include_w9_assets
    )
    if tuple(manifest.get("reviewer_files") or ()) != expected_reviewer_files:
        _error(report, "reviewer file allowlist differs from frozen contract")
    expected_internal_files = sealed_internal_files(include_w9=include_w9_assets)
    if tuple(manifest.get("sealed_internal_files") or ()) != expected_internal_files:
        _error(report, "sealed internal file list differs from frozen contract")
    controller_permissions_pass = _check_private_path(
        root / "sealed_internal",
        directory=True,
        label="sealed internal root",
        report=report,
    ) and controller_permissions_pass
    file_rows = manifest.get("files")
    if not isinstance(file_rows, list):
        _error(report, "manifest files must be a list")
        file_rows = []
    observed_manifest_paths: set[str] = set()
    manifest_file_index: dict[str, Mapping[str, Any]] = {}
    for raw in file_rows:
        if not isinstance(raw, Mapping):
            _error(report, "manifest file row must be an object")
            continue
        relative = str(raw.get("path") or "")
        if relative in observed_manifest_paths:
            _error(report, f"duplicate manifest file path: {relative}")
        observed_manifest_paths.add(relative)
        manifest_file_index[relative] = raw
        unresolved_path = root / relative
        controller_permissions_pass = _check_private_path(
            unresolved_path,
            directory=False,
            label=f"packet file {relative}",
            report=report,
        ) and controller_permissions_pass
        path = unresolved_path.resolve()
        try:
            path.relative_to(root)
        except ValueError:
            _error(report, f"manifest file escapes packet root: {relative}")
            continue
        if not path.is_file():
            _error(report, f"manifest file missing: {relative}")
            continue
        if file_digest(path) != str(raw.get("sha256") or ""):
            _error(report, f"manifest file digest mismatch: {relative}")
        reviewer_cohort = next(
            (
                cohort
                for cohort, paths in expected_distributions.items()
                if relative in paths
            ),
            None,
        )
        expected_distribution = (
            f"reviewer_{reviewer_cohort}"
            if reviewer_cohort is not None
            else "sealed_internal"
        )
        if raw.get("distribution") != expected_distribution:
            _error(report, f"manifest distribution mismatch: {relative}")
        file_format = str(raw.get("format") or "")
        if file_format == "jsonl":
            rows = _safe_load_jsonl(path, report)
            if len(rows) != int(raw.get("row_count") or 0):
                _error(report, f"manifest row count mismatch: {relative}")
        elif int(raw.get("byte_count") or -1) != path.stat().st_size:
            _error(report, f"manifest byte count mismatch: {relative}")
    expected_manifest_paths = set(expected_reviewer_files) | set(
        expected_internal_files
    )
    if observed_manifest_paths != expected_manifest_paths:
        _error(report, "manifest file inventory differs from reviewer/internal allowlists")
    expected_asset_sources = _reviewer_asset_sources(include_w9=include_w9_assets)
    for relative, source in expected_asset_sources.items():
        packet_asset = root / relative
        if packet_asset.is_file() and file_digest(packet_asset) != file_digest(source):
            _error(report, f"reviewer support asset differs from frozen source: {relative}")
    declared_distributions = manifest.get("reviewer_distributions")
    if not isinstance(declared_distributions, Mapping):
        _error(report, "reviewer_distributions must be a cohort mapping")
        declared_distributions = {}
    if set(declared_distributions) != set(expected_distributions):
        _error(report, "reviewer distribution cohorts differ from frozen contract")
    item_type_by_cohort = {
        "proof": "claim",
        "retrieval": "retrieval",
        "w9": "w9_pair",
    }
    reviewer_distribution_checks: dict[str, bool] = {}
    for cohort, cohort_files in expected_distributions.items():
        reviewer_root_name = REVIEWER_ROOTS[cohort]
        reviewer_root_path = root / reviewer_root_name
        filesystem_boundary_valid = True
        if reviewer_root_path.is_symlink() or not reviewer_root_path.is_dir():
            _error(report, f"{cohort}: reviewer root must be a real directory")
            filesystem_boundary_valid = False
        else:
            if not _check_private_path(
                reviewer_root_path,
                directory=True,
                label=f"{cohort} reviewer root",
                report=report,
            ):
                filesystem_boundary_valid = False
                controller_permissions_pass = False
            expected_local_names = {
                path.removeprefix(reviewer_root_name + "/")
                for path in cohort_files
            }
            entries = list(reviewer_root_path.iterdir())
            observed_local_names = {entry.name for entry in entries}
            if observed_local_names != expected_local_names:
                _error(
                    report,
                    f"{cohort}: reviewer root filesystem inventory differs from allowlist",
                )
                filesystem_boundary_valid = False
            for entry in entries:
                if entry.is_symlink() or not entry.is_file():
                    _error(
                        report,
                        f"{cohort}: reviewer root permits regular files only: {entry.name}",
                    )
                    filesystem_boundary_valid = False
                elif not _check_private_path(
                    entry,
                    directory=False,
                    label=f"{cohort} reviewer file {entry.name}",
                    report=report,
                ):
                    filesystem_boundary_valid = False
                    controller_permissions_pass = False
        reviewer_root = reviewer_root_path.resolve()
        manifest_relative = f"{reviewer_root_name}/reviewer_manifest.v1.json"
        checksum_relative = f"{reviewer_root_name}/SHA256SUMS"
        reviewer_manifest_path = root / manifest_relative
        reviewer_manifest: Mapping[str, Any] = {}
        if not reviewer_manifest_path.is_file():
            _error(report, f"{cohort}: reviewer manifest is missing")
        else:
            try:
                raw_reviewer_manifest = read_json(reviewer_manifest_path)
                if not isinstance(raw_reviewer_manifest, Mapping):
                    raise TypeError("reviewer manifest must be an object")
                reviewer_manifest = raw_reviewer_manifest
            except (OSError, ValueError, TypeError) as exc:
                _error(report, f"{cohort}: invalid reviewer manifest: {exc}")
        cohort_valid = bool(reviewer_manifest) and filesystem_boundary_valid
        if reviewer_manifest:
            if reviewer_manifest.get("schema_version") != (
                "apps_rg.c03_human_eval.reviewer_manifest.v1"
            ):
                _error(report, f"{cohort}: unsupported reviewer manifest schema")
                cohort_valid = False
            if reviewer_manifest.get("packet_id") != manifest.get("packet_id"):
                _error(report, f"{cohort}: reviewer manifest packet_id mismatch")
                cohort_valid = False
            if reviewer_manifest.get("reviewer_cohort") != cohort:
                _error(report, f"{cohort}: reviewer manifest cohort mismatch")
                cohort_valid = False
            if reviewer_manifest.get("item_type") != item_type_by_cohort[cohort]:
                _error(report, f"{cohort}: reviewer manifest item_type mismatch")
                cohort_valid = False
            if not digest_matches(reviewer_manifest, "manifest_digest"):
                _error(report, f"{cohort}: reviewer manifest digest mismatch")
                cohort_valid = False
            for flag in (
                "sealed_internal_paths_included",
                "other_reviewer_cohort_paths_included",
            ):
                if reviewer_manifest.get(flag) is not False:
                    _error(report, f"{cohort}: reviewer manifest must set {flag}=false")
                    cohort_valid = False
            if reviewer_manifest.get("cross_cohort_distribution_forbidden") is not True:
                _error(report, f"{cohort}: cross-cohort distribution must be forbidden")
                cohort_valid = False
            reviewer_rows = reviewer_manifest.get("files")
            if not isinstance(reviewer_rows, list):
                _error(report, f"{cohort}: reviewer manifest files must be a list")
                reviewer_rows = []
                cohort_valid = False
            generated = {manifest_relative, checksum_relative}
            expected_content_paths = {
                path.removeprefix(reviewer_root_name + "/")
                for path in cohort_files
                if path not in generated
            }
            observed_content_paths = {
                str(row.get("path") or "")
                for row in reviewer_rows
                if isinstance(row, Mapping)
            }
            if observed_content_paths != expected_content_paths:
                _error(
                    report,
                    f"{cohort}: reviewer-safe manifest inventory differs from frozen allowlist",
                )
                cohort_valid = False
            for row in reviewer_rows:
                if not isinstance(row, Mapping):
                    _error(report, f"{cohort}: reviewer manifest row must be an object")
                    cohort_valid = False
                    continue
                safe_relative = str(row.get("path") or "")
                safe_path = (reviewer_root / safe_relative).resolve()
                try:
                    safe_path.relative_to(reviewer_root)
                except ValueError:
                    _error(report, f"{cohort}: unsafe reviewer manifest path: {safe_relative}")
                    cohort_valid = False
                    continue
                if Path(safe_relative).is_absolute() or "/" in safe_relative:
                    _error(report, f"{cohort}: reviewer manifest path must remain cohort-local")
                    cohort_valid = False
                    continue
                root_relative = f"{reviewer_root_name}/{safe_relative}"
                root_row = manifest_file_index.get(root_relative) or {}
                if row.get("sha256") != root_row.get("sha256"):
                    _error(report, f"{cohort}: reviewer/root manifest digest mismatch")
                    cohort_valid = False
            declared = declared_distributions.get(cohort)
            if not isinstance(declared, Mapping):
                _error(report, f"{cohort}: top-level reviewer distribution receipt missing")
                cohort_valid = False
            else:
                expected_declaration = {
                    "root": reviewer_root_name,
                    "item_type": item_type_by_cohort[cohort],
                    "manifest_path": manifest_relative,
                    "manifest_digest": reviewer_manifest.get("manifest_digest"),
                    "checksum_path": checksum_relative,
                    "files": list(cohort_files),
                    "cross_cohort_distribution_forbidden": True,
                    "separate_reviewer_cohort_required": True,
                }
                if dict(declared) != expected_declaration:
                    _error(report, f"{cohort}: top-level reviewer distribution receipt mismatch")
                    cohort_valid = False

        reviewer_checksum_path = root / checksum_relative
        if not reviewer_checksum_path.is_file():
            _error(report, f"{cohort}: reviewer SHA256SUMS is missing")
            cohort_valid = False
        else:
            checksum_inputs = [
                row
                for path, row in manifest_file_index.items()
                if path.startswith(reviewer_root_name + "/")
                and path != checksum_relative
            ]
            expected_checksum_text = "".join(
                f"{row['sha256']}  {str(row['path']).removeprefix(reviewer_root_name + '/')}\n"
                for row in sorted(checksum_inputs, key=lambda value: str(value["path"]))
            )
            if reviewer_checksum_path.read_text(encoding="utf-8") != expected_checksum_text:
                _error(report, f"{cohort}: reviewer SHA256SUMS differs from frozen inventory")
                cohort_valid = False
        reviewer_distribution_checks[cohort] = cohort_valid

    top_checksum_path = root / "SHA256SUMS"
    top_checksum_valid = top_checksum_path.is_file()
    if not top_checksum_valid:
        _error(report, "top-level SHA256SUMS is missing")
    else:
        controller_permissions_pass = _check_private_path(
            top_checksum_path,
            directory=False,
            label="top-level SHA256SUMS",
            report=report,
        ) and controller_permissions_pass
        expected_top_checksum = "".join(
            f"{digest}  {path}\n"
            for digest, path in sorted(
                [
                    (str(row.get("sha256") or ""), str(row.get("path") or ""))
                    for row in file_rows
                    if isinstance(row, Mapping)
                ]
                + [(file_digest(manifest_path), "packet_manifest.json")],
                key=lambda row: row[1],
            )
        )
        if top_checksum_path.read_text(encoding="utf-8") != expected_top_checksum:
            _error(report, "top-level SHA256SUMS differs from packet manifest inventory")
            top_checksum_valid = False

    claims = _safe_load_jsonl(root / REVIEWER_FILES[0], report)
    queries = _safe_load_jsonl(root / REVIEWER_FILES[1], report)
    pairs = (
        _safe_load_jsonl(root / REVIEWER_FILES[2], report)
        if include_w9_assets
        else []
    )
    claim_map = _safe_load_jsonl(root / INTERNAL_FILES[0], report)
    query_map = _safe_load_jsonl(root / INTERNAL_FILES[1], report)
    w9_map = (
        _safe_load_jsonl(root / INTERNAL_FILES[2], report)
        if include_w9_assets
        else []
    )

    claim_index = _index_rows(claims, "item_id", "content_digest", "claim", report)
    query_index = _index_rows(queries, "query_id", "content_digest", "query", report)
    pair_index = _index_rows(pairs, "pair_id", "content_digest", "w9_pair", report)
    claim_mapping_index = _index_rows(claim_map, "item_id", "record_digest", "claim_mapping", report)
    query_mapping_index = _index_rows(query_map, "query_id", "record_digest", "query_mapping", report)
    pair_mapping_index = _index_rows(w9_map, "pair_id", "record_digest", "w9_mapping", report)

    for mapping_label, mappings in (
        ("claim", claim_map),
        ("retrieval", query_map),
        ("W9", w9_map),
    ):
        for index, mapping in enumerate(mappings):
            if mapping.get("retrieval_split_assignment_commitment") != (
                retrieval_split_commitment
            ):
                _error(
                    report,
                    f"{mapping_label} mapping[{index}]: secret retrieval split commitment mismatch",
                )
                secret_retrieval_split_binding = False

    if len(claims) != EXPECTED_CLAIM_ITEMS:
        _error(report, f"expected {EXPECTED_CLAIM_ITEMS} claim items, observed {len(claims)}")
    if len(queries) != EXPECTED_RETRIEVAL_QUERIES:
        _error(report, f"expected {EXPECTED_RETRIEVAL_QUERIES} retrieval queries, observed {len(queries)}")
    expected_w9 = EXPECTED_W9_PAIRS if require_w9 else 0
    if len(pairs) != expected_w9:
        _error(report, f"expected {expected_w9} W9 pairs, observed {len(pairs)}")
    if set(claim_index) != set(claim_mapping_index):
        _error(report, "claim reviewer/internal identity conservation failed")
    if set(query_index) != set(query_mapping_index):
        _error(report, "retrieval reviewer/internal identity conservation failed")
    if set(pair_index) != set(pair_mapping_index):
        _error(report, "W9 reviewer/internal identity conservation failed")
    for row_id, row in claim_index.items():
        mapping = claim_mapping_index.get(row_id) or {}
        if row.get("content_digest") != mapping.get("content_digest"):
            _error(report, f"{row_id}: claim content digest binding mismatch")
        binding = mapping.get("binding")
        if not isinstance(binding, Mapping):
            _error(report, f"{row_id}: sealed claim binding must be an object")
        elif mapping.get("metric_applicable") is not metric_applicable(binding):
            _error(report, f"{row_id}: claim metric applicability binding mismatch")
    for row_id, row in query_index.items():
        mapping = query_mapping_index.get(row_id) or {}
        if row.get("content_digest") != mapping.get("content_digest"):
            _error(report, f"{row_id}: retrieval content digest binding mismatch")
        blind_ids = [str(candidate.get("candidate_blind_id") or "") for candidate in row.get("candidates") or []]
        internal_ids = [
            str(candidate.get("candidate_blind_id") or "") for candidate in mapping.get("candidates") or []
        ]
        if len(blind_ids) != len(set(blind_ids)) or set(blind_ids) != set(internal_ids):
            _error(report, f"{row_id}: retrieval candidate conservation failed")
        if len(blind_ids) != int(mapping.get("candidate_conservation_count") or -1):
            _error(report, f"{row_id}: retrieval candidate count receipt mismatch")
        for candidate in mapping.get("candidates") or []:
            candidate_binding = (candidate.get("system_fields") or {}).get("binding")
            candidate_id = str(candidate.get("candidate_blind_id") or "<missing>")
            if not isinstance(candidate_binding, Mapping):
                _error(report, f"{row_id}/{candidate_id}: sealed candidate binding must be an object")
            elif candidate.get("metric_applicable") is not metric_applicable(
                candidate_binding
            ):
                _error(
                    report,
                    f"{row_id}/{candidate_id}: candidate metric applicability binding mismatch",
                )
        if row.get("candidate_count") != len(blind_ids):
            _error(report, f"{row_id}: reviewer candidate_count mismatch")
            full_finite_universe_judging = False
        if row.get("candidate_judging_scope") != FULL_UNIVERSE_JUDGING_SCOPE:
            _error(report, f"{row_id}: reviewer judging scope is not full finite universe")
            full_finite_universe_judging = False
        if mapping.get("candidate_judging_scope") != FULL_UNIVERSE_JUDGING_SCOPE:
            _error(report, f"{row_id}: sealed judging scope is not full finite universe")
            full_finite_universe_judging = False
        frontier_metadata = mapping.get("candidate_frontier_metadata")
        if not isinstance(frontier_metadata, Mapping):
            frontier_metadata = {}
            _error(report, f"{row_id}: candidate_frontier_metadata must be an object")
        metadata_error = frontier_metadata_contract_error(frontier_metadata)
        if metadata_error:
            _error(report, f"{row_id}: {metadata_error}")
            full_finite_universe_judging = False
        frontier_error = frontier_contract_error(
            mapping.get("candidates") or [],
            candidate_universe_size=frontier_metadata.get("candidate_universe_size"),
            frontier_k=frontier_metadata.get("frontier_k"),
            frontier_exhausted=frontier_metadata.get("frontier_exhausted"),
        )
        if frontier_error:
            _error(report, f"{row_id}: {frontier_error}")
            full_finite_universe_judging = False
        if (
            isinstance(frontier_metadata.get("candidate_universe_size"), int)
            and not isinstance(frontier_metadata.get("candidate_universe_size"), bool)
            and len(blind_ids) != frontier_metadata.get("candidate_universe_size")
        ):
            _error(report, f"{row_id}: reviewer candidates do not conserve the finite universe")
            full_finite_universe_judging = False
        frontier_k = frontier_metadata.get("frontier_k")
        universe_size = frontier_metadata.get("candidate_universe_size")
        if (
            isinstance(frontier_k, int)
            and not isinstance(frontier_k, bool)
            and isinstance(universe_size, int)
            and not isinstance(universe_size, bool)
        ):
            expected_judged_top = min(frontier_k, universe_size)
            if frontier_metadata.get("judged_top_count") != expected_judged_top:
                _error(report, f"{row_id}: judged_top_count mismatch")
            selected_extras = [
                candidate
                for candidate in mapping.get("candidates") or []
                if candidate.get("selected") is True
                and isinstance(candidate.get("rank"), int)
                and not isinstance(candidate.get("rank"), bool)
                and candidate["rank"] > frontier_k
            ]
            expected_extra = (
                {
                    "candidate_id": str(selected_extras[0].get("candidate_id") or ""),
                    "rank": int(selected_extras[0]["rank"]),
                }
                if len(selected_extras) == 1
                else None
            )
            if mapping.get("selected_audit_extra") != expected_extra:
                _error(report, f"{row_id}: selected_audit_extra mismatch")
            if frontier_metadata.get("selected_audit_extra_included") is not bool(
                expected_extra
            ):
                _error(report, f"{row_id}: selected_audit_extra_included mismatch")
            expected_extra_rank = expected_extra["rank"] if expected_extra else None
            if frontier_metadata.get("selected_audit_extra_rank") != expected_extra_rank:
                _error(report, f"{row_id}: selected_audit_extra_rank mismatch")
    for row_id, row in pair_index.items():
        mapping = pair_mapping_index.get(row_id) or {}
        if row.get("content_digest") != mapping.get("content_digest"):
            _error(report, f"{row_id}: W9 content digest binding mismatch")
        if set((mapping.get("variant_a"), mapping.get("variant_b"))) != {"baseline", "hardened"}:
            _error(report, f"{row_id}: invalid sealed W9 variant mapping")

    for label, rows in (("claim", claims), ("retrieval", queries), ("w9_pair", pairs)):
        for index, row in enumerate(rows):
            unsafe = unsafe_reviewer_keys(row)
            if unsafe:
                _error(report, f"{label}[{index}]: reviewer payload exposes forbidden keys {unsafe}")

    claim_sections = Counter(str(row.get("section_id") or "") for row in claims)
    claim_profiles = Counter(str(row.get("target_profile_id") or "") for row in claims)
    claim_proof_splits = Counter(str(row.get("proof_split") or "") for row in claim_map)
    claim_retrieval_splits = Counter(
        str(row.get("retrieval_split") or "") for row in claim_map
    )
    proof_group_counts = {
        split: len(
            {
                str(row.get("proof_split_group_digest") or "")
                for row in claim_map
                if row.get("proof_split") == split
            }
        )
        for split in ("calibration", "holdout")
    }
    query_sections = Counter(str(row.get("section_id") or "") for row in queries)
    query_retrieval_splits = Counter(
        str(row.get("retrieval_split") or "") for row in query_map
    )
    if dict(claim_sections) != EXPECTED_SECTION_COUNTS:
        _error(report, f"claim section coverage mismatch: {dict(claim_sections)}")
    if dict(claim_profiles) != EXPECTED_PROFILE_COUNTS:
        _error(report, f"claim profile coverage mismatch: {dict(claim_profiles)}")
    if dict(claim_retrieval_splits) != EXPECTED_CLAIM_RETRIEVAL_SPLITS:
        _error(
            report,
            f"claim retrieval-split coverage mismatch: {dict(claim_retrieval_splits)}",
        )
    if set(claim_proof_splits) != {"calibration", "holdout"} or any(
        proof_group_counts[split] < MINIMUM_PROOF_SPLIT_COUNT
        for split in ("calibration", "holdout")
    ):
        _error(
            report,
            "proof-split coverage must contain at least "
            f"{MINIMUM_PROOF_SPLIT_COUNT} unique proof binding groups in calibration and "
            f"holdout: {proof_group_counts}",
        )
    if dict(query_sections) != EXPECTED_QUERY_SECTION_COUNTS:
        _error(report, f"retrieval section coverage mismatch: {dict(query_sections)}")
    if dict(query_retrieval_splits) != EXPECTED_QUERY_RETRIEVAL_SPLITS:
        _error(
            report,
            f"retrieval query split coverage mismatch: {dict(query_retrieval_splits)}",
        )
    retrieval_split_cases: dict[str, set[str]] = defaultdict(set)
    for row in claim_map:
        retrieval_split_cases[str(row.get("retrieval_split") or "")].add(
            str(row.get("case_id") or "")
        )
    if retrieval_split_cases["calibration"] & retrieval_split_cases["release_holdout"]:
        _error(report, "target cases overlap calibration and release-holdout splits")
    retrieval_split_jd_digests: dict[str, set[str]] = defaultdict(set)
    retrieval_split_brief_digests: dict[str, set[str]] = defaultdict(set)
    proof_identity_splits: dict[str, set[str]] = defaultdict(set)
    proof_group_splits: dict[str, set[str]] = defaultdict(set)
    proof_identity_retrieval_splits: dict[str, set[str]] = defaultdict(set)
    proof_group_retrieval_splits: dict[str, set[str]] = defaultdict(set)
    proof_split_deterministic = True
    for mapping in claim_map:
        retrieval_split = str(mapping.get("retrieval_split") or "")
        reviewer_item = claim_index.get(str(mapping.get("item_id") or "")) or {}
        context = reviewer_item.get("target_context")
        if isinstance(context, Mapping):
            retrieval_split_jd_digests[retrieval_split].add(
                str(context.get("jd_digest") or "")
            )
            retrieval_split_brief_digests[retrieval_split].add(
                str(context.get("brief_digest") or "")
            )
        try:
            identity_digest, expected_proof_split = proof_identity_and_split(
                reviewer_item.get("visible_claim_text"),
                mapping.get("binding") or {},
                salt=proof_split_salt,
            )
        except ProofSplitPolicyError as exc:
            proof_split_deterministic = False
            _error(report, f"{mapping.get('item_id')}: invalid proof identity: {exc}")
            continue
        observed_identity = str(mapping.get("proof_identity_digest") or "")
        observed_group = str(mapping.get("proof_split_group_digest") or "")
        expected_group = proof_split_group_digest(mapping.get("binding") or {})
        observed_proof_split = str(mapping.get("proof_split") or "")
        if observed_identity != identity_digest:
            proof_split_deterministic = False
            _error(report, f"{mapping.get('item_id')}: proof identity digest mismatch")
        if observed_group != expected_group:
            proof_split_deterministic = False
            _error(report, f"{mapping.get('item_id')}: proof split group digest mismatch")
        if observed_proof_split != expected_proof_split:
            proof_split_deterministic = False
            _error(report, f"{mapping.get('item_id')}: deterministic proof split mismatch")
        if mapping.get("proof_split_policy_id") != PROOF_SPLIT_POLICY_ID:
            proof_split_deterministic = False
            _error(report, f"{mapping.get('item_id')}: proof split policy mismatch")
        if mapping.get("proof_split_policy_salt") != proof_split_salt:
            proof_split_deterministic = False
            _error(report, f"{mapping.get('item_id')}: proof split salt mismatch")
        proof_identity_splits[identity_digest].add(observed_proof_split)
        proof_group_splits[expected_group].add(observed_proof_split)
        proof_identity_retrieval_splits[identity_digest].add(retrieval_split)
        proof_group_retrieval_splits[expected_group].add(retrieval_split)

    target_case_overlap = (
        retrieval_split_cases["calibration"]
        & retrieval_split_cases["release_holdout"]
    )
    target_input_overlap = (
        retrieval_split_jd_digests["calibration"]
        & retrieval_split_jd_digests["release_holdout"]
    ) | (
        retrieval_split_brief_digests["calibration"]
        & retrieval_split_brief_digests["release_holdout"]
    )
    if target_input_overlap:
        _error(
            report,
            "calibration/release-holdout retrieval target input leakage: "
            f"{len(target_input_overlap)} overlapping digests",
        )
    proof_identity_overlap = {
        identity: splits
        for identity, splits in proof_identity_splits.items()
        if len(splits) != 1
    }
    if proof_identity_overlap:
        _error(
            report,
            f"proof identities cross proof calibration/holdout: {len(proof_identity_overlap)}",
        )
    proof_group_overlap = {
        group: splits
        for group, splits in proof_group_splits.items()
        if len(splits) != 1
    }
    if proof_group_overlap:
        _error(
            report,
            "proof binding groups cross proof calibration/holdout: "
            f"{len(proof_group_overlap)}",
        )
    proof_identity_retrieval_overlap_count = sum(
        len(splits) > 1 for splits in proof_identity_retrieval_splits.values()
    )
    proof_group_retrieval_overlap_count = sum(
        len(splits) > 1 for splits in proof_group_retrieval_splits.values()
    )
    proof_split_profiles: dict[str, set[str]] = defaultdict(set)
    proof_split_sections: dict[str, set[str]] = defaultdict(set)
    proof_split_strata: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for mapping in claim_map:
        proof_split = str(mapping.get("proof_split") or "")
        profile = str(mapping.get("target_profile_id") or "")
        section = str(mapping.get("section_id") or "")
        proof_split_profiles[proof_split].add(profile)
        proof_split_sections[proof_split].add(section)
        proof_split_strata[proof_split].add((profile, section))
    expected_profiles = set(EXPECTED_PROFILE_COUNTS)
    expected_sections = set(EXPECTED_SECTION_COUNTS)
    expected_strata = {
        (profile, section)
        for profile in expected_profiles
        for section in expected_sections
    }
    proof_strata_complete = all(
        proof_split_profiles[split] == expected_profiles
        and proof_split_sections[split] == expected_sections
        and proof_split_strata[split] == expected_strata
        for split in ("calibration", "holdout")
    )
    if not proof_strata_complete:
        _error(report, "each proof split must cover every target profile and section stratum")
    retrieval_split_profiles: dict[str, set[str]] = defaultdict(set)
    retrieval_split_sections: dict[str, set[str]] = defaultdict(set)
    for mapping in query_map:
        retrieval_split = str(mapping.get("retrieval_split") or "")
        reviewer_query = query_index.get(str(mapping.get("query_id") or "")) or {}
        retrieval_split_profiles[retrieval_split].add(
            str(reviewer_query.get("target_profile_id") or "")
        )
        retrieval_split_sections[retrieval_split].add(
            str(reviewer_query.get("section_id") or "")
        )
    expected_retrieval_sections = set(EXPECTED_QUERY_SECTION_COUNTS)
    retrieval_strata_complete = all(
        retrieval_split_profiles[split] == expected_profiles
        and retrieval_split_sections[split] == expected_retrieval_sections
        for split in ("calibration", "release_holdout")
    )
    if not retrieval_strata_complete:
        _error(
            report,
            "each retrieval split must cover every target profile and ranked section",
        )
    retrieval_mapping_by_claim = {
        (str(row.get("case_id") or ""), str(row.get("claim_unit_id") or "")): row
        for row in query_map
    }
    for mapping in claim_map:
        query_mapping = retrieval_mapping_by_claim.get(
            (str(mapping.get("case_id") or ""), str(mapping.get("claim_unit_id") or ""))
        )
        if query_mapping is not None and query_mapping.get("retrieval_split") != mapping.get(
            "retrieval_split"
        ):
            _error(
                report,
                f"{mapping.get('item_id')}: claim/query retrieval_split mismatch",
            )

    leakage_pass = bool(
        not target_case_overlap
        and not target_input_overlap
        and not proof_identity_overlap
        and not proof_group_overlap
        and proof_split_deterministic
        and proof_strata_complete
        and retrieval_strata_complete
        and blinding_nonce_commitment_valid
        and all(reviewer_distribution_checks.values())
        and set(reviewer_distribution_checks) == set(expected_distributions)
        and top_checksum_valid
        and controller_permissions_pass
        and secret_retrieval_split_binding
    )

    report["checks"] = {
        "claim_items": len(claims),
        "retrieval_queries": len(queries),
        "w9_pairs": len(pairs),
        "claim_proof_split_counts": dict(sorted(claim_proof_splits.items())),
        "proof_split_group_counts": proof_group_counts,
        "proof_split_policy_salt": proof_split_salt,
        "claim_retrieval_split_counts": dict(sorted(claim_retrieval_splits.items())),
        "retrieval_query_split_counts": dict(sorted(query_retrieval_splits.items())),
        "reviewer_payloads_blinded": not any(
            unsafe_reviewer_keys(row) for row in [*claims, *queries, *pairs]
        ),
        "blinding_nonce_commitment_valid": blinding_nonce_commitment_valid,
        "secret_blinding_nonce_not_distributed": "blinding_nonce" not in manifest,
        "source_freeze_receipt_trusted": source_freeze_receipt_trusted,
        "official_source_provenance_pass": official_provenance_pass,
        "full_finite_universe_judging": full_finite_universe_judging,
        "secret_retrieval_split_binding": secret_retrieval_split_binding,
        "reviewer_distribution_isolation": dict(sorted(reviewer_distribution_checks.items())),
        "top_level_checksum_valid": top_checksum_valid,
        "controller_permissions_pass": controller_permissions_pass,
        "identity_conservation": (
            set(claim_index) == set(claim_mapping_index)
            and set(query_index) == set(query_mapping_index)
            and set(pair_index) == set(pair_mapping_index)
        ),
        "target_case_retrieval_split_disjoint": not bool(target_case_overlap),
        "target_input_retrieval_split_disjoint": not bool(target_input_overlap),
        "proof_identity_split_disjoint": not bool(proof_identity_overlap),
        "proof_split_group_disjoint": not bool(proof_group_overlap),
        "proof_split_deterministic": proof_split_deterministic,
        "proof_split_strata_complete": proof_strata_complete,
        "proof_split_profiles": {
            split: sorted(proof_split_profiles[split])
            for split in ("calibration", "holdout")
        },
        "proof_split_sections": {
            split: sorted(proof_split_sections[split])
            for split in ("calibration", "holdout")
        },
        "retrieval_split_strata_complete": retrieval_strata_complete,
        "retrieval_split_profiles": {
            split: sorted(retrieval_split_profiles[split])
            for split in ("calibration", "release_holdout")
        },
        "retrieval_split_sections": {
            split: sorted(retrieval_split_sections[split])
            for split in ("calibration", "release_holdout")
        },
        "proof_identity_retrieval_overlap_count": proof_identity_retrieval_overlap_count,
        "proof_split_group_retrieval_overlap_count": (
            proof_group_retrieval_overlap_count
        ),
        "leakage_checks_pass": leakage_pass,
    }
    report["pass"] = not report["errors"]
    report["official_pass"] = report["pass"] and official_provenance_pass
    report["status"] = (
        "PASS"
        if report["official_pass"]
        else "PASS_TEST_ONLY"
        if report["pass"]
        else "FAIL"
    )
    return report


def _identity_tokens(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", value.casefold()) if token}


def _validate_human_identity(
    row: Mapping[str, Any],
    label: str,
    report: dict[str, Any],
    *,
    qualification_prefix: str | None = None,
) -> None:
    if row.get("reviewer_type") != "human":
        _error(report, f"{label}: reviewer_type must be human")
    identity_hash = str(row.get("reviewer_id_hash") or "")
    if not HEX64.fullmatch(identity_hash):
        _error(report, f"{label}: reviewer_id_hash must be lowercase SHA-256")
    identity_ref = str(row.get("reviewer_identity_ref") or "")
    if not identity_ref.startswith("human-reviewer://"):
        _error(report, f"{label}: reviewer_identity_ref must use human-reviewer://")
    elif identity_hash != hashlib.sha256(identity_ref.encode("utf-8")).hexdigest():
        _error(
            report,
            f"{label}: reviewer_id_hash must bind reviewer_identity_ref with SHA-256",
        )
    identity_words = _identity_tokens(identity_ref + " " + str(row.get("qualification_ref") or ""))
    rejected = sorted(identity_words & NON_HUMAN_TOKENS)
    if rejected:
        _error(report, f"{label}: non-human reviewer identity tokens rejected: {rejected}")
    if row.get("human_attestation") is not True:
        _error(report, f"{label}: human_attestation must be true")
    if row.get("independent_review") is not True:
        _error(report, f"{label}: independent_review must be true")
    qualification_ref = str(row.get("qualification_ref") or "").strip()
    if not qualification_ref:
        _error(report, f"{label}: qualification_ref is required")
    elif qualification_prefix is not None and not qualification_ref.startswith(
        qualification_prefix
    ):
        _error(
            report,
            f"{label}: W9 qualification_ref must use {qualification_prefix}",
        )


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str, report: dict[str, Any]) -> None:
    if set(value) != expected:
        _error(report, f"{label}: label keys must be {sorted(expected)}")


def _integer(value: Any, low: int, high: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def _validate_claim_labels(
    labels: Any,
    label: str,
    report: dict[str, Any],
    *,
    expected_metric_applicable: bool,
) -> None:
    if not isinstance(labels, Mapping):
        _error(report, f"{label}: claim labels must be an object")
        return
    expected = {
        "authority_eligible",
        "claim_entailment_grade",
        "path_accuracy",
        "metric_binding",
        "target_relevance_grade",
        "overall_proof_valid",
    }
    _exact_keys(labels, expected, label, report)
    if labels.get("authority_eligible") not in {"PASS", "FAIL"}:
        _error(report, f"{label}: authority_eligible UNKNOWN/non-final is nonpass")
    if not _integer(labels.get("claim_entailment_grade"), 0, 3):
        _error(report, f"{label}: claim_entailment_grade must be 0..3")
    if not isinstance(labels.get("path_accuracy"), bool):
        _error(report, f"{label}: path_accuracy UNKNOWN/non-boolean is nonpass")
    if labels.get("metric_binding") not in {"EXACT", "INEXACT", "NOT_APPLICABLE"}:
        _error(report, f"{label}: metric_binding UNKNOWN/non-final is nonpass")
    elif expected_metric_applicable and labels.get("metric_binding") not in {
        "EXACT",
        "INEXACT",
    }:
        _error(report, f"{label}: metric-bearing claim cannot be NOT_APPLICABLE")
    elif not expected_metric_applicable and labels.get("metric_binding") != "NOT_APPLICABLE":
        _error(report, f"{label}: nonmetric claim must be NOT_APPLICABLE")
    if not _integer(labels.get("target_relevance_grade"), 0, 3):
        _error(report, f"{label}: target_relevance_grade must be 0..3")
    if not isinstance(labels.get("overall_proof_valid"), bool):
        _error(report, f"{label}: overall_proof_valid UNKNOWN/non-boolean is nonpass")
    authority = labels.get("authority_eligible")
    entailment = labels.get("claim_entailment_grade")
    path_accuracy = labels.get("path_accuracy")
    metric_binding = labels.get("metric_binding")
    overall = labels.get("overall_proof_valid")
    dimensions_are_final = (
        authority in {"PASS", "FAIL"}
        and _integer(entailment, 0, 3)
        and isinstance(path_accuracy, bool)
        and metric_binding in {"EXACT", "INEXACT", "NOT_APPLICABLE"}
        and isinstance(overall, bool)
    )
    if dimensions_are_final:
        expected_overall = (
            authority == "PASS"
            and entailment >= 2
            and path_accuracy is True
            and metric_binding in {"EXACT", "NOT_APPLICABLE"}
        )
        if overall is not expected_overall:
            _error(
                report,
                f"{label}: overall_proof_valid disagrees with the frozen proof rubric",
            )


def _validate_retrieval_labels(
    labels: Any,
    label: str,
    expected_candidates: set[str],
    expected_metric_applicability: Mapping[str, bool],
    report: dict[str, Any],
) -> None:
    if not isinstance(labels, Mapping) or set(labels) != {"candidates"}:
        _error(report, f"{label}: retrieval labels require only candidates")
        return
    candidates = labels.get("candidates")
    if not isinstance(candidates, list):
        _error(report, f"{label}: candidates must be a list")
        return
    observed: set[str] = set()
    for index, raw in enumerate(candidates):
        if not isinstance(raw, Mapping):
            _error(report, f"{label}/candidate[{index}]: must be an object")
            continue
        _exact_keys(
            raw,
            {"candidate_blind_id", "relevance_grade", "path_valid", "metric_binding"},
            f"{label}/candidate[{index}]",
            report,
        )
        blind_id = str(raw.get("candidate_blind_id") or "")
        if blind_id in observed:
            _error(report, f"{label}: duplicate candidate_blind_id {blind_id}")
        observed.add(blind_id)
        if not _integer(raw.get("relevance_grade"), 0, 3):
            _error(report, f"{label}/{blind_id}: relevance_grade must be 0..3")
        if not isinstance(raw.get("path_valid"), bool):
            _error(report, f"{label}/{blind_id}: path_valid UNKNOWN/non-boolean is nonpass")
        if raw.get("metric_binding") not in {"EXACT", "INEXACT", "NOT_APPLICABLE"}:
            _error(report, f"{label}/{blind_id}: metric_binding UNKNOWN/non-final is nonpass")
        elif expected_metric_applicability.get(blind_id) is True and raw.get(
            "metric_binding"
        ) not in {"EXACT", "INEXACT"}:
            _error(
                report,
                f"{label}/{blind_id}: metric-bearing candidate cannot be NOT_APPLICABLE",
            )
        elif expected_metric_applicability.get(blind_id) is False and raw.get(
            "metric_binding"
        ) != "NOT_APPLICABLE":
            _error(
                report,
                f"{label}/{blind_id}: nonmetric candidate must be NOT_APPLICABLE",
            )
        relevance = raw.get("relevance_grade")
        if (
            _integer(relevance, 0, 3)
            and relevance != 0
            and (
                raw.get("path_valid") is False
                or raw.get("metric_binding") == "INEXACT"
            )
        ):
            _error(
                report,
                f"{label}/{blind_id}: invalid path or inexact metric requires relevance_grade 0",
            )
    if observed != expected_candidates:
        _error(report, f"{label}: candidate labels do not conserve the blinded frontier")


W9_DIMENSIONS = {
    "target_relevance",
    "claim_naturalness",
    "executive_readability",
    "ats_keyword_coverage",
    "authenticity_factuality",
    "concision",
    "hiring_manager_usefulness",
}


def _validate_w9_labels(labels: Any, label: str, report: dict[str, Any]) -> None:
    if not isinstance(labels, Mapping):
        _error(report, f"{label}: W9 labels must be an object")
        return
    _exact_keys(labels, {"resume_a", "resume_b", "preference"}, label, report)
    for variant in ("resume_a", "resume_b"):
        dimensions = labels.get(variant)
        if not isinstance(dimensions, Mapping):
            _error(report, f"{label}/{variant}: dimensions must be an object")
            continue
        _exact_keys(dimensions, W9_DIMENSIONS, f"{label}/{variant}", report)
        for dimension, value in dimensions.items():
            if not _integer(value, 1, 5):
                _error(report, f"{label}/{variant}/{dimension}: score must be 1..5")
    if labels.get("preference") not in {"A", "B", "TIE"}:
        _error(report, f"{label}: preference UNKNOWN/non-final is nonpass")


def _validate_labels(
    item_type: str,
    labels: Any,
    label: str,
    candidate_ids: set[str],
    metric_applicability: bool | Mapping[str, bool] | None,
    report: dict[str, Any],
) -> None:
    if item_type == "claim":
        if not isinstance(metric_applicability, bool):
            _error(report, f"{label}: sealed claim metric applicability is missing")
            return
        _validate_claim_labels(
            labels,
            label,
            report,
            expected_metric_applicable=metric_applicability,
        )
    elif item_type == "retrieval":
        if not isinstance(metric_applicability, Mapping):
            _error(report, f"{label}: sealed candidate metric applicability is missing")
            return
        _validate_retrieval_labels(
            labels,
            label,
            candidate_ids,
            metric_applicability,
            report,
        )
    elif item_type == "w9_pair":
        _validate_w9_labels(labels, label, report)
    else:
        _error(report, f"{label}: unsupported item_type {item_type}")


def _validate_participant_cohorts(
    participants: Sequence[Mapping[str, Any]],
    report: dict[str, Any],
) -> dict[str, bool]:
    """Enforce one identity binding and isolated proof/retrieval/W9 humans."""

    identity_refs_by_hash: dict[str, set[str]] = defaultdict(set)
    identity_hashes_by_ref: dict[str, set[str]] = defaultdict(set)
    hashes_by_item_type: dict[str, set[str]] = defaultdict(set)
    refs_by_item_type: dict[str, set[str]] = defaultdict(set)
    for row in participants:
        item_type = str(row.get("item_type") or "")
        identity_hash = str(row.get("reviewer_id_hash") or "")
        identity_ref = str(row.get("reviewer_identity_ref") or "")
        if identity_hash and identity_ref:
            identity_refs_by_hash[identity_hash].add(identity_ref)
            identity_hashes_by_ref[identity_ref].add(identity_hash)
            hashes_by_item_type[item_type].add(identity_hash)
            refs_by_item_type[item_type].add(identity_ref)

    hash_ref_binding_valid = True
    for identity_hash, identity_refs in sorted(identity_refs_by_hash.items()):
        if len(identity_refs) != 1:
            hash_ref_binding_valid = False
            _error(
                report,
                "reviewer identity hash is bound to multiple reviewer_identity_ref values: "
                f"{identity_hash}",
            )
    for identity_ref, identity_hashes in sorted(identity_hashes_by_ref.items()):
        if len(identity_hashes) != 1:
            hash_ref_binding_valid = False
            _error(
                report,
                "reviewer_identity_ref is bound to multiple reviewer identity hashes: "
                f"{identity_ref}",
            )

    item_type_labels = {
        "claim": "proof",
        "retrieval": "retrieval",
        "w9_pair": "W9",
    }
    participant_cohorts_disjoint = True
    item_types = tuple(item_type_labels)
    for left_index, left in enumerate(item_types):
        for right in item_types[left_index + 1 :]:
            overlapping_hashes = sorted(hashes_by_item_type[left] & hashes_by_item_type[right])
            overlapping_refs = sorted(refs_by_item_type[left] & refs_by_item_type[right])
            if overlapping_hashes:
                participant_cohorts_disjoint = False
                _error(
                    report,
                    f"{item_type_labels[left]} and {item_type_labels[right]} "
                    "reviewer/adjudicator participant hash cohorts must be disjoint: "
                    + ", ".join(overlapping_hashes),
                )
            if overlapping_refs:
                participant_cohorts_disjoint = False
                _error(
                    report,
                    f"{item_type_labels[left]} and {item_type_labels[right]} "
                    "reviewer/adjudicator participant identity-ref cohorts must be disjoint: "
                    + ", ".join(overlapping_refs),
                )
    return {
        "participant_cohorts_pairwise_disjoint": participant_cohorts_disjoint,
        "reviewer_identity_hash_ref_binding_one_to_one": hash_ref_binding_valid,
    }


def validate_completed_packet(
    packet_dir: Path,
    labels_dir: Path,
    *,
    require_w9: bool = False,
    trusted_source_freeze_receipt_digest: str | None = None,
    trusted_prelabel_packet_manifest_sha256: str | None = None,
    human_review_authority_receipt: Mapping[str, Any] | Path | None = None,
    trusted_human_review_authority_receipt_sha256: str | None = None,
    allow_test_only_provenance: bool = False,
) -> dict[str, Any]:
    """Validate two independent human reviews and adjudication for every item."""

    report = _result("apps_rg.c03_human_eval.completed_validation.v1")
    prelabel = validate_prelabel_packet(
        packet_dir,
        require_w9=require_w9,
        trusted_source_freeze_receipt_digest=trusted_source_freeze_receipt_digest,
        allow_test_only_provenance=allow_test_only_provenance,
    )
    report["prelabel_validation"] = prelabel
    if not prelabel["pass"]:
        _error(report, "prelabel packet validation failed")
        report["errors"].extend(f"prelabel: {value}" for value in prelabel["errors"])
        return report
    root = packet_dir.resolve()
    observed_prelabel_manifest_sha256 = file_digest(root / "packet_manifest.json")
    trusted_prelabel_sha256 = str(
        trusted_prelabel_packet_manifest_sha256 or ""
    ).strip()
    prelabel_manifest_pin_trusted = bool(
        HEX64.fullmatch(trusted_prelabel_sha256)
        and trusted_prelabel_sha256 == observed_prelabel_manifest_sha256
    )
    if not HEX64.fullmatch(trusted_prelabel_sha256):
        _error(
            report,
            "trusted prelabel packet manifest SHA-256 is required for completed validation",
        )
    elif trusted_prelabel_sha256 != observed_prelabel_manifest_sha256:
        _error(
            report,
            "current packet manifest differs from the trusted prelabel SHA-256 pin",
        )
    if not prelabel_manifest_pin_trusted:
        report["checks"] = {
            "prelabel_manifest_pin_trusted": False,
            "observed_prelabel_packet_manifest_sha256": (
                observed_prelabel_manifest_sha256
            ),
        }
        return report
    manifest = read_json(root / "packet_manifest.json")
    (
        authority_roster,
        authority_issued_at,
        authority_receipt_file_sha256,
        official_human_authority,
        authority_receipt_trusted,
    ) = _human_review_authority(
        value=human_review_authority_receipt,
        trusted_file_sha256=trusted_human_review_authority_receipt_sha256,
        manifest=manifest,
        prelabel_manifest_sha256=trusted_prelabel_sha256,
        allow_test_only_provenance=allow_test_only_provenance,
        report=report,
    )
    claims = read_jsonl(root / REVIEWER_FILES[0])
    queries = read_jsonl(root / REVIEWER_FILES[1])
    pairs = read_jsonl(root / REVIEWER_FILES[2]) if require_w9 else []
    claim_metric_applicability = {
        ("claim", str(row["item_id"])): bool(row["metric_applicable"])
        for row in read_jsonl(root / INTERNAL_FILES[0])
    }
    retrieval_metric_applicability = {
        ("retrieval", str(row["query_id"])): {
            str(candidate["candidate_blind_id"]): bool(
                candidate["metric_applicable"]
            )
            for candidate in row["candidates"]
        }
        for row in read_jsonl(root / INTERNAL_FILES[1])
    }
    metric_applicability_by_item: dict[
        tuple[str, str], bool | Mapping[str, bool] | None
    ] = {
        **claim_metric_applicability,
        **retrieval_metric_applicability,
    }
    labels_alias = Path(labels_dir)
    labels_alias_valid = not labels_alias.is_symlink()
    if not labels_alias_valid:
        _error(report, "completed labels root must not be a symlink alias")
    labels_root = labels_alias.resolve()
    labels_permissions_pass = _check_private_path(
        labels_root,
        directory=True,
        label="completed labels root",
        report=report,
    ) and labels_alias_valid
    expected_label_names = {
        "claim_reviews.jsonl",
        "retrieval_reviews.jsonl",
        "adjudications.jsonl",
    }
    if pairs:
        expected_label_names.add("w9_reviews.jsonl")
    if labels_root.is_dir():
        observed_label_entries = list(labels_root.iterdir())
        if {entry.name for entry in observed_label_entries} != expected_label_names:
            _error(report, "completed labels filesystem inventory differs from allowlist")
            labels_permissions_pass = False
        for entry in observed_label_entries:
            if not _check_private_path(
                entry,
                directory=False,
                label=f"completed label file {entry.name}",
                report=report,
            ):
                labels_permissions_pass = False
    if not labels_permissions_pass:
        report["checks"] = {"labels_permissions_pass": False}
        return report
    item_index: dict[tuple[str, str], dict[str, Any]] = {}
    for item_type, id_key, rows in (
        ("claim", "item_id", claims),
        ("retrieval", "query_id", queries),
        ("w9_pair", "pair_id", pairs),
    ):
        for row in rows:
            item_index[(item_type, str(row[id_key]))] = row
    rubric_digests = dict(manifest.get("rubric_digests") or {})

    review_paths = {
        "claim": labels_root / "claim_reviews.jsonl",
        "retrieval": labels_root / "retrieval_reviews.jsonl",
        "w9_pair": labels_root / "w9_reviews.jsonl",
    }
    reviews: list[dict[str, Any]] = []
    for item_type, path in review_paths.items():
        expected = any(key[0] == item_type for key in item_index)
        if not path.is_file():
            if expected:
                _error(report, f"missing completed review file {path.name}")
            continue
        rows = _safe_load_jsonl(path, report)
        for row in rows:
            if row.get("item_type") != item_type:
                _error(report, f"{path.name}: item_type mismatch")
            reviews.append(row)
    reviews_by_item: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    review_by_id: dict[str, dict[str, Any]] = {}
    for row in reviews:
        review_id = str(row.get("review_id") or "")
        key = (str(row.get("item_type") or ""), str(row.get("item_id") or ""))
        label = f"review/{review_id or '<missing>'}"
        if not review_id or review_id in review_by_id:
            _error(report, f"{label}: review_id missing or duplicate")
        review_by_id[review_id] = row
        if not digest_matches(row, "record_digest"):
            _error(report, f"{label}: record_digest mismatch")
        item = item_index.get(key)
        if item is None:
            _error(report, f"{label}: unknown item {key}")
            continue
        if row.get("blinded_payload_digest") != item.get("content_digest"):
            _error(report, f"{label}: blinded payload digest mismatch")
        expected_rubric = rubric_digests.get(key[0])
        if row.get("rubric_digest") != expected_rubric:
            _error(report, f"{label}: rubric digest mismatch")
        _validate_human_identity(
            row,
            label,
            report,
            qualification_prefix=W9_QUALIFICATION_PREFIX if key[0] == "w9_pair" else None,
        )
        cohort = {"claim": "proof", "retrieval": "retrieval", "w9_pair": "w9"}.get(
            key[0], ""
        )
        authorization = authority_roster.get(
            (cohort, str(row.get("reviewer_id_hash") or ""))
        )
        if (
            authorization is None
            or "primary" not in (authorization.get("roles") or [])
            or authorization.get("identity_ref") != row.get("reviewer_identity_ref")
            or authorization.get("qualification_ref") != row.get("qualification_ref")
        ):
            _error(report, f"{label}: reviewer is not authorized for this cohort/role")
        labeled_at = _utc_timestamp(row.get("labeled_at"), f"{label}/labeled_at", report)
        if (
            authority_issued_at is not None
            and labeled_at is not None
            and labeled_at <= authority_issued_at
        ):
            _error(report, f"{label}: authority receipt must predate human labels")
        candidate_ids = {
            str(candidate.get("candidate_blind_id") or "")
            for candidate in item.get("candidates") or []
        }
        _validate_labels(
            key[0],
            row.get("labels"),
            label,
            candidate_ids,
            metric_applicability_by_item.get(key),
            report,
        )
        reviews_by_item[key].append(row)

    for key, item in item_index.items():
        rows = reviews_by_item.get(key, [])
        if len(rows) != 2:
            _error(report, f"{key}: exactly two primary human reviews required; observed {len(rows)}")
            continue
        identities = {str(row.get("reviewer_id_hash") or "") for row in rows}
        if len(identities) != 2:
            _error(report, f"{key}: primary reviewers must have distinct identities")
        identity_refs = {str(row.get("reviewer_identity_ref") or "") for row in rows}
        if len(identity_refs) != 2:
            _error(report, f"{key}: primary reviewers must have distinct identity refs")
        if len({str(row.get("label_batch_id") or "") for row in rows}) != 2:
            _error(report, f"{key}: independent reviews require distinct label_batch_id values")

    adjudication_path = labels_root / "adjudications.jsonl"
    adjudications = (
        _safe_load_jsonl(adjudication_path, report) if adjudication_path.is_file() else []
    )
    if not adjudication_path.is_file():
        _error(report, "missing adjudications.jsonl")
    adjudication_by_item: dict[tuple[str, str], dict[str, Any]] = {}
    human_adjudicator_participants: list[dict[str, Any]] = []
    for row in adjudications:
        key = (str(row.get("item_type") or ""), str(row.get("item_id") or ""))
        adjudication_id = str(row.get("adjudication_id") or "")
        label = f"adjudication/{adjudication_id or '<missing>'}"
        if key in adjudication_by_item:
            _error(report, f"{label}: duplicate adjudication for {key}")
        adjudication_by_item[key] = row
        if not digest_matches(row, "record_digest"):
            _error(report, f"{label}: record_digest mismatch")
        if key not in item_index:
            _error(report, f"{label}: unknown item {key}")
            continue
        primary = reviews_by_item.get(key, [])
        refs = [str(value) for value in row.get("review_refs") or []]
        digests = [str(value) for value in row.get("review_digests") or []]
        if len(refs) != 2 or len(set(refs)) != 2:
            _error(report, f"{label}: exactly two unique review_refs required")
        if set(refs) != {str(value.get("review_id") or "") for value in primary}:
            _error(report, f"{label}: review_refs do not bind the two primary reviews")
        if set(digests) != {str(value.get("record_digest") or "") for value in primary}:
            _error(report, f"{label}: review_digests do not bind the two primary reviews")
        adjudicated_at = _utc_timestamp(
            row.get("adjudicated_at"), f"{label}/adjudicated_at", report
        )
        if (
            authority_issued_at is not None
            and adjudicated_at is not None
            and adjudicated_at <= authority_issued_at
        ):
            _error(report, f"{label}: authority receipt must predate adjudication")
        status = row.get("status")
        if status not in {"CONSENSUS_ACCEPTED", "ADJUDICATED"}:
            _error(report, f"{label}: invalid adjudication status")
        item = item_index[key]
        candidate_ids = {
            str(candidate.get("candidate_blind_id") or "")
            for candidate in item.get("candidates") or []
        }
        _validate_labels(
            key[0],
            row.get("final_labels"),
            label,
            candidate_ids,
            metric_applicability_by_item.get(key),
            report,
        )
        if status == "CONSENSUS_ACCEPTED" and len(primary) == 2:
            label_digests = {stable_digest(value.get("labels")) for value in primary}
            if len(label_digests) != 1 or stable_digest(row.get("final_labels")) not in label_digests:
                _error(report, f"{label}: consensus receipt labels do not exactly agree")
            if row.get("adjudicator_type") != "deterministic_consensus":
                _error(report, f"{label}: consensus receipt must identify deterministic_consensus")
        if status == "ADJUDICATED":
            adjudicator = {
                "item_type": key[0],
                "reviewer_type": row.get("adjudicator_type"),
                "reviewer_id_hash": row.get("adjudicator_id_hash"),
                "reviewer_identity_ref": row.get("adjudicator_identity_ref"),
                "qualification_ref": row.get("qualification_ref"),
                "human_attestation": row.get("human_attestation"),
                "independent_review": True,
            }
            _validate_human_identity(
                adjudicator,
                label + "/adjudicator",
                report,
                qualification_prefix=(
                    W9_QUALIFICATION_PREFIX if key[0] == "w9_pair" else None
                ),
            )
            cohort = {
                "claim": "proof",
                "retrieval": "retrieval",
                "w9_pair": "w9",
            }.get(key[0], "")
            authorization = authority_roster.get(
                (cohort, str(row.get("adjudicator_id_hash") or ""))
            )
            if (
                authorization is None
                or "adjudicator" not in (authorization.get("roles") or [])
                or authorization.get("identity_ref")
                != row.get("adjudicator_identity_ref")
                or authorization.get("qualification_ref")
                != row.get("qualification_ref")
            ):
                _error(report, f"{label}: adjudicator is not authorized for this cohort/role")
            human_adjudicator_participants.append(adjudicator)
            primary_hashes = {str(value.get("reviewer_id_hash") or "") for value in primary}
            if str(row.get("adjudicator_id_hash") or "") in primary_hashes:
                _error(report, f"{label}: adjudicator must be independent from primary reviewers")
            primary_identity_refs = {
                str(value.get("reviewer_identity_ref") or "") for value in primary
            }
            if str(row.get("adjudicator_identity_ref") or "") in primary_identity_refs:
                _error(
                    report,
                    f"{label}: adjudicator identity ref must be independent from primary reviewers",
                )

    missing_adjudications = sorted(set(item_index) - set(adjudication_by_item))
    if missing_adjudications:
        _error(report, f"missing adjudication receipts for {len(missing_adjudications)} items")
    extra_adjudications = sorted(set(adjudication_by_item) - set(item_index))
    if extra_adjudications:
        _error(report, f"adjudications reference {len(extra_adjudications)} unknown items")

    participant_contract = _validate_participant_cohorts(
        [*reviews, *human_adjudicator_participants],
        report,
    )

    report["checks"] = {
        "expected_item_count": len(item_index),
        "review_count": len(reviews),
        "adjudication_count": len(adjudications),
        "two_human_reviews_per_item": all(
            len(reviews_by_item.get(key, [])) == 2 for key in item_index
        ),
        "adjudication_per_item": set(adjudication_by_item) == set(item_index),
        "labels_permissions_pass": labels_permissions_pass,
        "prelabel_manifest_pin_trusted": prelabel_manifest_pin_trusted,
        "observed_prelabel_packet_manifest_sha256": (
            observed_prelabel_manifest_sha256
        ),
        "human_review_authority_receipt_trusted": authority_receipt_trusted,
        "human_review_authority_receipt_file_sha256": (
            authority_receipt_file_sha256
        ),
        "official_human_review_authority": official_human_authority,
        **participant_contract,
        "unknown_is_pass": False,
    }
    report["pass"] = not report["errors"]
    report["official_pass"] = bool(
        report["pass"]
        and prelabel.get("official_pass") is True
        and official_human_authority
    )
    report["status"] = (
        "PASS"
        if report["official_pass"]
        else "PASS_TEST_ONLY"
        if report["pass"]
        else "FAIL"
    )
    return report


def build_prelabel_packet_receipt(
    packet_dir: Path,
    *,
    trusted_source_freeze_receipt_digest: str,
    require_w9: bool = False,
    allow_test_only_provenance: bool = False,
) -> dict[str, Any]:
    """Create the out-of-band receipt pinned before any reviewer distribution."""

    validation = validate_prelabel_packet(
        packet_dir,
        require_w9=require_w9,
        trusted_source_freeze_receipt_digest=trusted_source_freeze_receipt_digest,
        allow_test_only_provenance=allow_test_only_provenance,
    )
    if not validation["pass"]:
        raise ValueError(
            "prelabel packet cannot be sealed: " + "; ".join(validation["errors"][:10])
        )
    root = Path(packet_dir).resolve()
    manifest_path = root / "packet_manifest.json"
    manifest = read_json(manifest_path)
    return record_with_digest(
        {
            "schema_version": "apps_rg.c03_human_eval.prelabel_packet_receipt.v1",
            "status": "PASS" if validation.get("official_pass") else "PASS_TEST_ONLY",
            "official_pass": validation.get("official_pass") is True,
            "unknown_is_pass": False,
            "packet_id": str(manifest["packet_id"]),
            "packet_manifest_sha256": file_digest(manifest_path),
            "packet_manifest_digest": str(manifest["manifest_digest"]),
            "source_freeze_receipt_digest": str(
                manifest["source_freeze_receipt_digest"]
            ),
            "proof_split_policy_id": str(manifest["proof_split_policy_id"]),
            "proof_split_policy_salt": int(manifest["proof_split_policy_salt"]),
            "retrieval_split_policy_id": str(manifest["retrieval_split_policy_id"]),
            "retrieval_split_assignment_commitment": str(
                manifest["retrieval_split_assignment_commitment"]
            ),
            "prelabel_validation_digest": stable_digest(validation),
        },
        "receipt_digest",
    )


__all__ = [
    "build_prelabel_packet_receipt",
    "human_review_authority_receipt_file_sha256",
    "validate_completed_packet",
    "validate_prelabel_packet",
]
