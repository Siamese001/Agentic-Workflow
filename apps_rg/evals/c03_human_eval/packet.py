"""Deterministic builder for blinded C0.3 human-evaluation packets.

The builder transforms completed run evidence into reviewer-safe payloads. It
does not generate labels, inspect a protected release holdout, execute a judge,
or emit a calibrated probability.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import hmac
import json
import math
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence

from apps_rg.runtime.c0.resume_graph_allocation import (
    DEFAULT_MAX_CANDIDATES_PER_SLOT,
)

from ._io import (
    copy_private_file,
    controlled_path_error,
    digest_matches,
    file_digest,
    ensure_private_directory,
    private_path_error,
    path_has_symlink_component,
    paths_refer_same,
    read_json,
    read_yaml,
    record_with_digest,
    repo_root_from_module,
    stable_digest,
    write_json,
    write_jsonl,
    write_private_text,
)
from ._safety import unsafe_reviewer_keys
from .split_policy import (
    PROOF_SPLIT_POLICY_ID,
    ProofSplitPolicyError,
    allocate_stratified_proof_splits,
    proof_identity_digest,
    proof_split_group_digest,
)
from .source_bundle import SOURCE_FREEZE_RECEIPT_SCHEMA

SOURCE_SCHEMA = "apps_rg.c03_human_eval.source_bundle.v1"
MANIFEST_SCHEMA = "apps_rg.c03_human_eval.packet_manifest.v1"
CLAIM_SCHEMA = "apps_rg.c03_human_eval.claim_item.v1"
RETRIEVAL_SCHEMA = "apps_rg.c03_human_eval.retrieval_query.v1"
W9_SCHEMA = "apps_rg.c03_human_eval.w9_pair.v1"
FULL_UNIVERSE_JUDGING_SCOPE = "FULL_FINITE_UNIVERSE"
RETRIEVAL_SPLIT_POLICY_ID = "secret-hmac-balanced-by-target-profile-v1"
METRIC_BINDING_FIELDS = (
    "metric_outcome_id",
    "normalized_metric_signature",
    "metric_text",
    "metric_value",
    "metric_unit",
)

DEFAULT_TARGET_MANIFEST = Path(__file__).with_name("target_cases.v1.yaml")
CANONICAL_TARGET_MANIFEST_SHA256 = (
    "d36338de05e681dae2001f6e9c975eee4a79ef0963efd8875b1167456e3640d8"
)
RUBRIC_FILES: Mapping[str, str] = {
    "claim": "proof_label_rubric.v1.yaml",
    "retrieval": "retrieval_label_rubric.v1.yaml",
    "w9_pair": "w9_resume_coach_rubric.v1.yaml",
}
PROOF_REVIEWER_ROOT = "reviewer_proof"
RETRIEVAL_REVIEWER_ROOT = "reviewer_retrieval"
W9_REVIEWER_ROOT = "reviewer_w9"
REVIEWER_ROOTS: Mapping[str, str] = {
    "proof": PROOF_REVIEWER_ROOT,
    "retrieval": RETRIEVAL_REVIEWER_ROOT,
    "w9": W9_REVIEWER_ROOT,
}
REVIEWER_FILES = (
    f"{PROOF_REVIEWER_ROOT}/claim_items.jsonl",
    f"{RETRIEVAL_REVIEWER_ROOT}/retrieval_queries.jsonl",
    f"{W9_REVIEWER_ROOT}/w9_blind_pairs.jsonl",
)
_COMMON_REVIEWER_ASSET_NAMES = (
    "reviewer_instructions.v1.md",
    "human_review.v1.schema.json",
    "adjudication.v1.schema.json",
    "seal_records.py",
)
_RUBRIC_NAME_BY_COHORT: Mapping[str, str] = {
    "proof": "proof_label_rubric.v1.yaml",
    "retrieval": "retrieval_label_rubric.v1.yaml",
    "w9": "w9_resume_coach_rubric.v1.yaml",
}


def _cohort_asset_files(cohort: str) -> tuple[str, ...]:
    root = REVIEWER_ROOTS[cohort]
    return tuple(
        f"{root}/{name}"
        for name in (*_COMMON_REVIEWER_ASSET_NAMES, _RUBRIC_NAME_BY_COHORT[cohort])
    )


def _cohort_generated_files(cohort: str) -> tuple[str, str]:
    root = REVIEWER_ROOTS[cohort]
    return (f"{root}/reviewer_manifest.v1.json", f"{root}/SHA256SUMS")


BASE_REVIEWER_ASSET_FILES = (
    *_cohort_asset_files("proof"),
    *_cohort_asset_files("retrieval"),
)
W9_REVIEWER_ASSET_FILES = _cohort_asset_files("w9")
REVIEWER_GENERATED_FILES = (
    *_cohort_generated_files("proof"),
    *_cohort_generated_files("retrieval"),
    *_cohort_generated_files("w9"),
)
INTERNAL_FILES = (
    "sealed_internal/claim_mapping.jsonl",
    "sealed_internal/retrieval_mapping.jsonl",
    "sealed_internal/w9_variant_mapping.jsonl",
)
EXPECTED_CLAIM_ITEMS = 282
EXPECTED_RETRIEVAL_QUERIES = 84
EXPECTED_W9_PAIRS = 6
_BLINDING_NONCE_RE = re.compile(r"^[0-9a-f]{64}$")


def reviewer_distribution_files(*, include_w9: bool) -> tuple[str, ...]:
    """Return the flat allowlist across isolated reviewer distributions."""

    by_cohort = reviewer_distribution_files_by_cohort(include_w9=include_w9)
    return tuple(
        path
        for cohort in ("proof", "retrieval", "w9")
        for path in by_cohort.get(cohort, ())
    )


def sealed_internal_files(*, include_w9: bool) -> tuple[str, ...]:
    """Return the controller-only inventory for the selected evaluation wave."""

    return INTERNAL_FILES if include_w9 else INTERNAL_FILES[:2]


def reviewer_distribution_files_by_cohort(
    *, include_w9: bool
) -> dict[str, tuple[str, ...]]:
    """Return exact, non-overlapping self-contained distribution allowlists."""

    output = {
        "proof": (
            REVIEWER_FILES[0],
            *_cohort_asset_files("proof"),
            *_cohort_generated_files("proof"),
        ),
        "retrieval": (
            REVIEWER_FILES[1],
            *_cohort_asset_files("retrieval"),
            *_cohort_generated_files("retrieval"),
        ),
    }
    if include_w9:
        output["w9"] = (
            REVIEWER_FILES[2],
            *_cohort_asset_files("w9"),
            *_cohort_generated_files("w9"),
        )
    return output


def _reviewer_asset_sources(
    *, cohort: str | None = None, include_w9: bool = False
) -> dict[str, Path]:
    package = Path(__file__).resolve().parent
    cohorts = (cohort,) if cohort is not None else (
        "proof",
        "retrieval",
        *(("w9",) if include_w9 else ()),
    )
    sources: dict[str, Path] = {}
    for cohort_id in cohorts:
        if cohort_id not in REVIEWER_ROOTS:
            raise ValueError(f"unsupported reviewer cohort: {cohort_id}")
        root = REVIEWER_ROOTS[cohort_id]
        sources.update(
            {
                f"{root}/reviewer_instructions.v1.md": package
                / "reviewer_instructions.v1.md",
                f"{root}/human_review.v1.schema.json": package
                / "schemas/human_review.v1.schema.json",
                f"{root}/adjudication.v1.schema.json": package
                / "schemas/adjudication.v1.schema.json",
                f"{root}/seal_records.py": package / "seal_records.py",
                f"{root}/{_RUBRIC_NAME_BY_COHORT[cohort_id]}": package
                / _RUBRIC_NAME_BY_COHORT[cohort_id],
            }
        )
    return sources


class PacketBuildError(ValueError):
    """The proposed packet cannot be frozen without violating its contract."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PacketBuildError(f"{label} must be an object")
    return dict(value)


def _require_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise PacketBuildError(f"{label} is required")
    return text


def metric_applicable(binding: Mapping[str, Any]) -> bool:
    """Return whether a sealed binding carries any metric-bearing authority."""

    return any(
        value is not None and str(value).strip() != ""
        for field in METRIC_BINDING_FIELDS
        for value in (binding.get(field),)
    )


def _validated_blinding_nonce(value: str) -> str:
    nonce = str(value or "").strip()
    if not _BLINDING_NONCE_RE.fullmatch(nonce):
        raise PacketBuildError(
            "blinding_nonce must be an explicit lowercase 64-hex secret (256 bits)"
        )
    return nonce


def blinding_nonce_commitment(blinding_nonce: str) -> str:
    """Return the publishable one-way commitment to a validated secret nonce."""

    nonce = _validated_blinding_nonce(blinding_nonce)
    return hashlib.sha256(
        b"apps_rg.c03_human_eval.blinding_nonce_commitment.v1\x00"
        + bytes.fromhex(nonce)
    ).hexdigest()


def _blind_digest(
    *, blinding_nonce: str, purpose: str, payload: Mapping[str, Any]
) -> str:
    """Return a domain-separated HMAC for reviewer-visible pseudonyms/order."""

    nonce = _validated_blinding_nonce(blinding_nonce)
    message = (
        "apps_rg.c03_human_eval.blind.v1\x00"
        + purpose
        + "\x00"
        + stable_digest(payload)
    ).encode("utf-8")
    return hmac.new(bytes.fromhex(nonce), message, hashlib.sha256).hexdigest()


def _opaque_reviewer_id(
    *, blinding_nonce: str, cohort: str, source_parts: Sequence[str]
) -> str:
    """Create a deterministic lane-domain-separated reviewer identifier.

    The source linkage remains only in sealed mappings.  Cohort isolation is the
    actual blinding boundary; the opaque identifier additionally prevents an
    accidental join on case or claim-unit keys across reviewer distributions.
    """

    prefix = {
        "proof": "proof-item-",
        "retrieval": "retrieval-item-",
        "w9": "w9-item-",
    }.get(cohort)
    if prefix is None:
        raise PacketBuildError(f"unsupported reviewer cohort: {cohort}")
    return prefix + _blind_digest(
        blinding_nonce=blinding_nonce,
        purpose=f"reviewer-item:{cohort}",
        payload={"source_parts": list(source_parts)},
    )[:24]


def frontier_contract_error(
    candidates: Sequence[Mapping[str, Any]],
    *,
    candidate_universe_size: Any,
    frontier_k: Any,
    frontier_exhausted: Any,
) -> str | None:
    """Return an error unless every allocator-bounded candidate is conserved."""

    if frontier_k != 10:
        return "frontier_k must equal the frozen retrieval K of 10"
    if (
        not isinstance(candidate_universe_size, int)
        or isinstance(candidate_universe_size, bool)
        or candidate_universe_size <= 0
    ):
        return "candidate_universe_size must be a positive integer"
    expected_exhausted = candidate_universe_size <= frontier_k
    if not isinstance(frontier_exhausted, bool) or frontier_exhausted != expected_exhausted:
        return "frontier_exhausted must exactly reflect candidate_universe_size <= frontier_k"
    if len(candidates) != candidate_universe_size:
        return "candidate rows must conserve the complete bounded finite universe"
    ranks = [row.get("rank") for row in candidates]
    if any(
        not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0
        for rank in ranks
    ):
        return "candidate frontier ranks must be explicit positive integers"
    if len(set(ranks)) != len(ranks):
        return "candidate frontier ranks must be unique"
    if set(ranks) != set(range(1, candidate_universe_size + 1)):
        return "candidate ranks must exactly cover the bounded finite universe"
    selected = [row for row in candidates if row.get("selected") is True]
    if len(selected) != 1:
        return "candidate frontier must identify exactly one globally selected row"
    return None


def frontier_metadata_contract_error(metadata: Mapping[str, Any]) -> str | None:
    """Validate allocator provenance and complete finite-universe judging."""

    raw_count = metadata.get("raw_eligible_candidate_count")
    budget = metadata.get("allocator_candidate_budget")
    truncated = metadata.get("allocator_budget_truncated")
    universe_size = metadata.get("candidate_universe_size")
    if (
        not isinstance(raw_count, int)
        or isinstance(raw_count, bool)
        or raw_count <= 0
    ):
        return "raw_eligible_candidate_count must be a positive integer"
    if budget != DEFAULT_MAX_CANDIDATES_PER_SLOT:
        return (
            "allocator_candidate_budget must equal the frozen allocator budget "
            f"{DEFAULT_MAX_CANDIDATES_PER_SLOT}"
        )
    if not isinstance(truncated, bool) or truncated != (raw_count > budget):
        return "allocator_budget_truncated must exactly reflect raw count > budget"
    if universe_size != min(raw_count, budget):
        return "candidate_universe_size must equal min(raw eligible count, allocator budget)"
    if metadata.get("candidate_judging_scope") != FULL_UNIVERSE_JUDGING_SCOPE:
        return (
            "candidate_judging_scope must require the complete bounded finite universe"
        )
    if metadata.get("judged_candidate_count") != universe_size:
        return "judged_candidate_count must equal candidate_universe_size"
    return None


def _target_manifest(path: Path, repo_root: Path) -> dict[str, Any]:
    payload = _require_mapping(read_yaml(path), "target manifest")
    if payload.get("schema_version") != "apps_rg.c03_human_eval.target_cases.v1":
        raise PacketBuildError("unsupported target manifest schema")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 6:
        raise PacketBuildError("target manifest must declare exactly six cases")
    case_ids: set[str] = set()
    target_profiles: Counter[str] = Counter()
    for raw in cases:
        case = _require_mapping(raw, "target case")
        case_id = _require_text(case.get("case_id"), "target case_id")
        if case_id in case_ids:
            raise PacketBuildError(f"duplicate target case_id {case_id}")
        case_ids.add(case_id)
        if "retrieval_split" in case:
            raise PacketBuildError(
                f"{case_id}: public target manifest must not expose retrieval_split"
            )
        target_profiles[
            _require_text(case.get("target_profile_id"), f"{case_id} target_profile_id")
        ] += 1
        for kind in ("jd", "brief"):
            relative = Path(
                _require_text(
                    case.get(f"{kind}_path"), f"{case_id} {kind}_path"
                )
            )
            if relative.is_absolute():
                raise PacketBuildError(f"{case_id}: {kind}_path must be repository-relative")
            unresolved_source = repo_root / relative
            if path_has_symlink_component(unresolved_source):
                raise PacketBuildError(f"{case_id}: frozen {kind} source must not use symlinks")
            source = unresolved_source.resolve()
            try:
                source.relative_to(repo_root)
            except ValueError as exc:
                raise PacketBuildError(
                    f"{case_id}: frozen {kind} source escapes repo_root"
                ) from exc
            expected = _require_text(case.get(f"{kind}_sha256"), f"{case_id} {kind}_sha256")
            if not source.is_file():
                raise PacketBuildError(f"{case_id}: missing frozen {kind} source {source}")
            if file_digest(source) != expected:
                raise PacketBuildError(f"{case_id}: frozen {kind} digest mismatch")
    if len(target_profiles) != 3 or set(target_profiles.values()) != {2}:
        raise PacketBuildError(
            "target manifest must contain exactly two cases for each of three profiles"
        )
    return payload


def _secret_retrieval_split_assignments(
    *,
    target_cases: Sequence[Mapping[str, Any]],
    blinding_nonce: str,
) -> tuple[dict[str, str], str]:
    """Assign one secret calibration/holdout case per target profile."""

    by_profile: dict[str, list[str]] = {}
    for case in target_cases:
        profile = _require_text(case.get("target_profile_id"), "target_profile_id")
        case_id = _require_text(case.get("case_id"), "case_id")
        by_profile.setdefault(profile, []).append(case_id)
    assignments: dict[str, str] = {}
    for profile, case_ids in sorted(by_profile.items()):
        if len(case_ids) != 2:
            raise PacketBuildError(
                f"{profile}: secret retrieval split requires exactly two cases"
            )
        ordered = sorted(
            case_ids,
            key=lambda case_id: _blind_digest(
                blinding_nonce=blinding_nonce,
                purpose="retrieval-split-case-order",
                payload={"target_profile_id": profile, "case_id": case_id},
            ),
        )
        assignments[ordered[0]] = "calibration"
        assignments[ordered[1]] = "release_holdout"
    commitment = _blind_digest(
        blinding_nonce=blinding_nonce,
        purpose="retrieval-split-assignment-commitment",
        payload={
            "policy_id": RETRIEVAL_SPLIT_POLICY_ID,
            "assignments": sorted(assignments.items()),
        },
    )
    return assignments, commitment


def _source_bundle(value: Mapping[str, Any], target_case_ids: set[str]) -> dict[str, Any]:
    payload = dict(value)
    if payload.get("schema_version") != SOURCE_SCHEMA:
        raise PacketBuildError(f"source bundle schema must be {SOURCE_SCHEMA}")
    source_commit = str(payload.get("source_commit_sha") or "")
    if len(source_commit) != 40 or any(char not in "0123456789abcdef" for char in source_commit):
        raise PacketBuildError("source_commit_sha must be a lowercase 40-character hex SHA")
    for field in ("graph_digest", "policy_digest"):
        digest = str(payload.get(field) or "")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise PacketBuildError(f"{field} must be a lowercase SHA-256 digest")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 6:
        raise PacketBuildError("source bundle must contain exactly six cases")
    observed = {_require_text(_require_mapping(row, "source case").get("case_id"), "source case_id") for row in cases}
    if observed != target_case_ids:
        raise PacketBuildError("source bundle case IDs must exactly match the frozen target manifest")
    return payload


def _mapping_source_file_digest(value: Mapping[str, Any]) -> str:
    """Match ``write_json`` bytes for explicit test-only in-memory fixtures."""

    encoded = (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _source_freeze_receipt(
    *,
    value: Mapping[str, Any] | Path,
    expected_receipt_digest: str,
    source_bundle_input: Mapping[str, Any] | Path,
    source_bundle: Mapping[str, Any],
    target_manifest_path: Path,
    allow_test_only_provenance: bool,
) -> tuple[dict[str, Any], bool]:
    """Verify an externally pinned clean-freeze receipt and all source bindings."""

    expected = str(expected_receipt_digest or "").strip()
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        raise PacketBuildError(
            "trusted_source_freeze_receipt_digest must be a lowercase SHA-256 digest"
        )
    raw = read_json(value) if isinstance(value, Path) else value
    receipt = _require_mapping(raw, "source freeze receipt")
    expected_keys = {
        "schema_version",
        "freeze_mode",
        "official_provenance_eligible",
        "checkout_head_verified",
        "checkout_clean_verified",
        "source_bundle_sha256",
        "source_bundle_canonical_digest",
        "source_commit_sha",
        "target_manifest_digest",
        "graph_digest",
        "policy_digest",
        "case_count",
        "claim_count",
        "retrieval_frontier_count",
        "unknown_is_pass",
        "receipt_digest",
    }
    if set(receipt) != expected_keys:
        raise PacketBuildError("source freeze receipt fields differ from the frozen contract")
    if receipt.get("schema_version") != SOURCE_FREEZE_RECEIPT_SCHEMA:
        raise PacketBuildError("unsupported source freeze receipt schema")
    if not digest_matches(receipt, "receipt_digest"):
        raise PacketBuildError("source freeze receipt digest is invalid")
    if receipt.get("receipt_digest") != expected:
        raise PacketBuildError("source freeze receipt differs from the trusted expected digest")
    if isinstance(source_bundle_input, Path):
        observed_source_sha = file_digest(source_bundle_input.resolve())
    else:
        if not allow_test_only_provenance:
            raise PacketBuildError(
                "official packet build requires source_bundle to be a frozen JSON file"
            )
        observed_source_sha = _mapping_source_file_digest(source_bundle)
    binding_expectations = {
        "source_bundle_sha256": observed_source_sha,
        "source_bundle_canonical_digest": stable_digest(source_bundle),
        "source_commit_sha": str(source_bundle.get("source_commit_sha") or ""),
        "target_manifest_digest": file_digest(target_manifest_path),
        "graph_digest": str(source_bundle.get("graph_digest") or ""),
        "policy_digest": str(source_bundle.get("policy_digest") or ""),
        "case_count": len(source_bundle.get("cases") or []),
        "claim_count": sum(
            len(case.get("claims") or [])
            for case in source_bundle.get("cases") or []
            if isinstance(case, Mapping)
        ),
        "retrieval_frontier_count": sum(
            "candidate_frontier" in claim
            for case in source_bundle.get("cases") or []
            if isinstance(case, Mapping)
            for claim in case.get("claims") or []
            if isinstance(claim, Mapping)
        ),
    }
    for field, field_expected in binding_expectations.items():
        if receipt.get(field) != field_expected:
            raise PacketBuildError(f"source freeze receipt {field} binding mismatch")
    if receipt.get("unknown_is_pass") is not False:
        raise PacketBuildError("source freeze receipt must make UNKNOWN non-passing")
    official_pass = bool(
        isinstance(source_bundle_input, Path)
        and isinstance(value, Path)
        and receipt.get("freeze_mode") == "CLEAN_CHECKOUT_REAL_ALLOCATOR"
        and receipt.get("official_provenance_eligible") is True
        and receipt.get("checkout_head_verified") is True
        and receipt.get("checkout_clean_verified") is True
    )
    if not official_pass and not allow_test_only_provenance:
        raise PacketBuildError(
            "official packet build requires a clean-checkout real-allocator freeze receipt file"
        )
    return receipt, official_pass


def _target_context(case: Mapping[str, Any], repo_root: Path) -> dict[str, Any]:
    jd_path = repo_root / str(case["jd_path"])
    brief_path = repo_root / str(case["brief_path"])
    return {
        "target_profile_id": str(case["target_profile_id"]),
        "jd_text": jd_path.read_text(encoding="utf-8"),
        "jd_digest": str(case["jd_sha256"]),
        "brief_text": brief_path.read_text(encoding="utf-8"),
        "brief_digest": str(case["brief_sha256"]),
    }


def _claim_item(
    *,
    blinding_nonce: str,
    case: Mapping[str, Any],
    source_case: Mapping[str, Any],
    claim: Mapping[str, Any],
    target_context: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    case_id = str(case["case_id"])
    section_id = _require_text(claim.get("section_id"), f"{case_id} claim section_id")
    claim_unit_id = _require_text(claim.get("claim_unit_id"), f"{case_id} claim_unit_id")
    item_id = _opaque_reviewer_id(
        blinding_nonce=blinding_nonce,
        cohort="proof",
        source_parts=(case_id, claim_unit_id),
    )
    narrative = section_id in {
        "unify_narrative",
        "ibm_narrative",
        "insurtech_narrative",
        "ey_narrative",
    }
    binding = _require_mapping(claim.get("binding"), f"{case_id}/{claim_unit_id} binding")
    path_ids = binding.get("graph_path_ids")
    if (
        not isinstance(path_ids, list)
        or not path_ids
        or any(not str(value or "").strip() for value in path_ids)
        or len({str(value) for value in path_ids}) != len(path_ids)
    ):
        raise PacketBuildError(
            f"{case_id}/{claim_unit_id}: binding.graph_path_ids must be a nonempty unique list"
        )
    system_fields = dict(claim.get("system_fields") or {})
    proof_score_fields = [
        field
        for field in ("proof_score_raw", "proof_strength_raw")
        if field in system_fields
    ]
    if not proof_score_fields:
        raise PacketBuildError(
            f"{case_id}/{claim_unit_id}: system_fields requires proof_score_raw or proof_strength_raw"
        )
    for field in (*proof_score_fields, "selection_margin"):
        value = system_fields.get(field)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise PacketBuildError(
                f"{case_id}/{claim_unit_id}: system_fields.{field} must be finite numeric evidence"
            )
    if (
        len(proof_score_fields) == 2
        and float(system_fields["proof_score_raw"])
        != float(system_fields["proof_strength_raw"])
    ):
        raise PacketBuildError(
            f"{case_id}/{claim_unit_id}: conflicting proof_score_raw and proof_strength_raw"
        )
    visible_claim_text = _require_text(
        claim.get("visible_claim_text"), f"{case_id}/{claim_unit_id} visible_claim_text"
    )
    try:
        identity_digest = proof_identity_digest(
            visible_claim_text,
            binding,
        )
        split_group_digest = proof_split_group_digest(binding)
    except ProofSplitPolicyError as exc:
        raise PacketBuildError(f"{case_id}/{claim_unit_id}: {exc}") from exc
    item = {
        "schema_version": CLAIM_SCHEMA,
        "item_id": item_id,
        "target_profile_id": str(case["target_profile_id"]),
        "section_id": section_id,
        "representation_mode": "DERIVED_ALTERNATIVE" if narrative else "CANONICAL_VISIBLE",
        "target_context": dict(target_context),
        "visible_claim_text": visible_claim_text,
        "proof_context": _require_mapping(
            claim.get("proof_context"), f"{case_id}/{claim_unit_id} proof_context"
        ),
        "rubric_id": "c03_claim_proof_v1",
    }
    item = record_with_digest(item, "content_digest")
    unsafe = unsafe_reviewer_keys(item)
    if unsafe:
        raise PacketBuildError(
            f"{case_id}/{claim_unit_id}: reviewer claim payload exposes forbidden keys {unsafe}"
        )
    internal = {
        "schema_version": "apps_rg.c03_human_eval.claim_mapping.v1",
        "item_id": item_id,
        "content_digest": item["content_digest"],
        "case_id": case_id,
        "retrieval_split": str(case["retrieval_split"]),
        "retrieval_split_assignment_commitment": str(
            case["retrieval_split_assignment_commitment"]
        ),
        "proof_identity_digest": identity_digest,
        "proof_split_group_digest": split_group_digest,
        "target_profile_id": str(case["target_profile_id"]),
        "run_id": _require_text(source_case.get("run_id"), f"{case_id} run_id"),
        "allocation_plan_digest": _require_text(
            source_case.get("allocation_plan_digest"), f"{case_id} allocation_plan_digest"
        ),
        "section_id": section_id,
        "claim_unit_id": claim_unit_id,
        "candidate_id": _require_text(
            claim.get("candidate_id"), f"{case_id}/{claim_unit_id} candidate_id"
        ),
        "binding": binding,
        "metric_applicable": metric_applicable(binding),
        "system_fields": system_fields,
    }
    return item, record_with_digest(internal, "record_digest")


def _retrieval_query(
    *,
    blinding_nonce: str,
    case: Mapping[str, Any],
    claim: Mapping[str, Any],
    target_context: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    case_id = str(case["case_id"])
    section_id = str(claim["section_id"])
    claim_unit_id = str(claim["claim_unit_id"])
    query_id = _opaque_reviewer_id(
        blinding_nonce=blinding_nonce,
        cohort="retrieval",
        source_parts=(case_id, claim_unit_id),
    )
    frontier = claim.get("candidate_frontier")
    if not isinstance(frontier, list) or not frontier:
        raise PacketBuildError(f"{case_id}/{claim_unit_id}: complete candidate_frontier is required")
    reviewer_candidates: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []
    seen_candidates: set[str] = set()
    for ordinal, raw in enumerate(frontier, 1):
        candidate = _require_mapping(raw, f"{query_id} candidate")
        candidate_id = _require_text(candidate.get("candidate_id"), f"{query_id} candidate_id")
        if candidate_id in seen_candidates:
            raise PacketBuildError(f"{query_id}: duplicate candidate_id {candidate_id}")
        seen_candidates.add(candidate_id)
        blind_id = "candidate-" + _blind_digest(
            blinding_nonce=blinding_nonce,
            purpose="retrieval-candidate-id",
            payload={"query_id": query_id, "candidate_id": candidate_id},
        )[:20]
        reviewer_candidates.append(
            {
                "candidate_blind_id": blind_id,
                "candidate_text": _require_text(
                    candidate.get("candidate_text"), f"{query_id}/{candidate_id} candidate_text"
                ),
                "proof_context": _require_mapping(
                    candidate.get("proof_context"), f"{query_id}/{candidate_id} proof_context"
                ),
            }
        )
        rank = candidate.get("rank")
        if not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0:
            raise PacketBuildError(
                f"{query_id}/{candidate_id}: rank must be an explicit positive integer"
            )
        candidate_system_fields = dict(candidate.get("system_fields") or {})
        candidate_binding = _require_mapping(
            candidate_system_fields.get("binding"),
            f"{query_id}/{candidate_id} sealed binding",
        )
        mappings.append(
            {
                "candidate_blind_id": blind_id,
                "candidate_id": candidate_id,
                "original_ordinal": ordinal,
                "rank": rank,
                "selected": bool(candidate.get("selected", False)),
                "metric_applicable": metric_applicable(candidate_binding),
                "system_fields": candidate_system_fields,
            }
        )
    frontier_metadata = _require_mapping(
        claim.get("candidate_frontier_metadata"),
        f"{query_id} candidate_frontier_metadata",
    )
    expected_metadata_keys = {
        "raw_eligible_candidate_count",
        "allocator_candidate_budget",
        "allocator_budget_truncated",
        "candidate_universe_size",
        "frontier_k",
        "frontier_exhausted",
        "judged_top_count",
        "judged_candidate_count",
        "candidate_judging_scope",
        "selected_audit_extra_included",
        "selected_audit_extra_rank",
    }
    if set(frontier_metadata) != expected_metadata_keys:
        raise PacketBuildError(
            f"{query_id}: candidate_frontier_metadata keys must be "
            f"{sorted(expected_metadata_keys)}"
        )
    boundary_error = frontier_metadata_contract_error(frontier_metadata)
    if boundary_error:
        raise PacketBuildError(f"{query_id}: {boundary_error}")
    candidate_universe_size = frontier_metadata.get("candidate_universe_size")
    frontier_k = frontier_metadata.get("frontier_k")
    frontier_exhausted = frontier_metadata.get("frontier_exhausted")
    frontier_error = frontier_contract_error(
        mappings,
        candidate_universe_size=candidate_universe_size,
        frontier_k=frontier_k,
        frontier_exhausted=frontier_exhausted,
    )
    if frontier_error:
        raise PacketBuildError(f"{query_id}: {frontier_error}")
    judged_top_count = min(int(frontier_k), int(candidate_universe_size))
    selected_audit_extra = next(
        (
            {
                "candidate_id": str(row["candidate_id"]),
                "rank": int(row["rank"]),
            }
            for row in mappings
            if row["selected"] is True and int(row["rank"]) > int(frontier_k)
        ),
        None,
    )
    if frontier_metadata.get("judged_top_count") != judged_top_count:
        raise PacketBuildError(f"{query_id}: judged_top_count mismatch")
    if frontier_metadata.get("selected_audit_extra_included") is not bool(
        selected_audit_extra
    ):
        raise PacketBuildError(f"{query_id}: selected_audit_extra_included mismatch")
    expected_extra_rank = (
        selected_audit_extra["rank"] if selected_audit_extra is not None else None
    )
    if frontier_metadata.get("selected_audit_extra_rank") != expected_extra_rank:
        raise PacketBuildError(f"{query_id}: selected_audit_extra_rank mismatch")
    reviewer_candidates.sort(
        key=lambda row: _blind_digest(
            blinding_nonce=blinding_nonce,
            purpose="retrieval-candidate-order",
            payload={
                "query_id": query_id,
                "candidate_blind_id": row["candidate_blind_id"],
            },
        )
    )
    query = {
        "schema_version": RETRIEVAL_SCHEMA,
        "query_id": query_id,
        "target_profile_id": str(case["target_profile_id"]),
        "section_id": section_id,
        "target_context": dict(target_context),
        "retrieval_target": (
            "Independently assess which candidate provides the strongest eligible, "
            f"factually grounded evidence for the {section_id.replace('_', ' ')} "
            "resume section under the supplied target context."
        ),
        "candidates": reviewer_candidates,
        "candidate_count": len(reviewer_candidates),
        "candidate_judging_scope": FULL_UNIVERSE_JUDGING_SCOPE,
        "rubric_id": "c03_retrieval_relevance_v1",
    }
    query = record_with_digest(query, "content_digest")
    unsafe = unsafe_reviewer_keys(query)
    if unsafe:
        raise PacketBuildError(f"{query_id}: reviewer retrieval payload exposes forbidden keys {unsafe}")
    mapping = {
        "schema_version": "apps_rg.c03_human_eval.retrieval_mapping.v1",
        "query_id": query_id,
        "content_digest": query["content_digest"],
        "case_id": case_id,
        "retrieval_split": str(case["retrieval_split"]),
        "retrieval_split_assignment_commitment": str(
            case["retrieval_split_assignment_commitment"]
        ),
        "section_id": section_id,
        "claim_unit_id": claim_unit_id,
        "candidate_frontier_metadata": frontier_metadata,
        "selected_audit_extra": selected_audit_extra,
        "candidate_conservation_count": len(mappings),
        "candidate_judging_scope": FULL_UNIVERSE_JUDGING_SCOPE,
        "candidates": sorted(mappings, key=lambda row: (row["rank"], row["candidate_id"])),
    }
    return query, record_with_digest(mapping, "record_digest")


def _w9_pair(
    *,
    blinding_nonce: str,
    case: Mapping[str, Any],
    source_case: Mapping[str, Any],
    target_context: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    baseline = str(source_case.get("baseline_resume_text") or "").strip()
    hardened = str(source_case.get("hardened_resume_text") or "").strip()
    if not baseline and not hardened:
        return None
    if not baseline or not hardened:
        raise PacketBuildError(f"{case['case_id']}: W9 requires both resume variants")
    case_id = str(case["case_id"])
    pair_id = _opaque_reviewer_id(
        blinding_nonce=blinding_nonce,
        cohort="w9",
        source_parts=(case_id,),
    )
    orientation_digest = _blind_digest(
        blinding_nonce=blinding_nonce,
        purpose="w9-variant-orientation",
        payload={"pair_id": pair_id},
    )
    hardened_is_a = int(orientation_digest[-1], 16) % 2 == 0
    resume_a, resume_b = (hardened, baseline) if hardened_is_a else (baseline, hardened)
    pair = {
        "schema_version": W9_SCHEMA,
        "pair_id": pair_id,
        "target_profile_id": str(case["target_profile_id"]),
        "target_context": dict(target_context),
        "resume_a": resume_a,
        "resume_b": resume_b,
        "rubric_id": "c03_w9_blind_resume_coach_v1",
    }
    pair = record_with_digest(pair, "content_digest")
    unsafe = unsafe_reviewer_keys(pair)
    if unsafe:
        raise PacketBuildError(f"{pair_id}: reviewer W9 payload exposes forbidden keys {unsafe}")
    mapping = {
        "schema_version": "apps_rg.c03_human_eval.w9_variant_mapping.v1",
        "pair_id": pair_id,
        "content_digest": pair["content_digest"],
        "case_id": case_id,
        "retrieval_split": str(case["retrieval_split"]),
        "retrieval_split_assignment_commitment": str(
            case["retrieval_split_assignment_commitment"]
        ),
        "variant_a": "hardened" if hardened_is_a else "baseline",
        "variant_b": "baseline" if hardened_is_a else "hardened",
        "baseline_digest": stable_digest({"resume_text": baseline}),
        "hardened_digest": stable_digest({"resume_text": hardened}),
    }
    return pair, record_with_digest(mapping, "record_digest")


def _coverage(
    claims: Sequence[Mapping[str, Any]],
    claim_mappings: Sequence[Mapping[str, Any]],
    queries: Sequence[Mapping[str, Any]],
    query_mappings: Sequence[Mapping[str, Any]],
    pairs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    claim_proof_split = Counter(str(row["proof_split"]) for row in claim_mappings)
    claim_retrieval_split = Counter(
        str(row["retrieval_split"]) for row in claim_mappings
    )
    query_retrieval_split = Counter(
        str(row["retrieval_split"]) for row in query_mappings
    )
    proof_identity_count_by_split = {
        split: len(
            {
                str(row["proof_identity_digest"])
                for row in claim_mappings
                if row["proof_split"] == split
            }
        )
        for split in ("calibration", "holdout")
    }
    return {
        "target_case_count": len({str(row["case_id"]) for row in claim_mappings}),
        "target_profile_count": len({str(row["target_profile_id"]) for row in claims}),
        "claim_count": len(claims),
        "claim_count_by_proof_split": dict(sorted(claim_proof_split.items())),
        "proof_identity_count_by_proof_split": proof_identity_count_by_split,
        "claim_count_by_retrieval_split": dict(
            sorted(claim_retrieval_split.items())
        ),
        "claim_count_by_section": dict(sorted(Counter(str(row["section_id"]) for row in claims).items())),
        "claim_count_by_profile": dict(
            sorted(Counter(str(row["target_profile_id"]) for row in claims).items())
        ),
        "retrieval_query_count": len(queries),
        "retrieval_query_count_by_retrieval_split": dict(
            sorted(query_retrieval_split.items())
        ),
        "retrieval_query_count_by_section": dict(
            sorted(Counter(str(row["section_id"]) for row in queries).items())
        ),
        "w9_pair_count": len(pairs),
    }


def build_packet(
    *,
    source_bundle: Mapping[str, Any] | Path,
    source_freeze_receipt: Mapping[str, Any] | Path,
    trusted_source_freeze_receipt_digest: str,
    out_dir: Path,
    blinding_nonce: str,
    target_manifest_path: Path = DEFAULT_TARGET_MANIFEST,
    repo_root: Path | None = None,
    require_w9: bool = False,
    allow_test_only_provenance: bool = False,
) -> dict[str, Any]:
    """Build a deterministic reviewer-safe packet and return its manifest."""

    root = (repo_root or repo_root_from_module()).resolve()
    target_path = target_manifest_path.resolve()
    if not allow_test_only_provenance:
        if root != repo_root_from_module().resolve():
            raise PacketBuildError(
                "official packet build requires the canonical repository root"
            )
        if target_manifest_path.is_symlink() or target_path != DEFAULT_TARGET_MANIFEST.resolve():
            raise PacketBuildError(
                "official packet build requires the canonical committed target manifest path"
            )
        if file_digest(target_path) != CANONICAL_TARGET_MANIFEST_SHA256:
            raise PacketBuildError(
                "canonical target manifest digest differs from the frozen official contract"
            )
        output_error = controlled_path_error(out_dir, repo_root=root)
        if output_error:
            raise PacketBuildError(f"official packet output {output_error}")
        for label, sensitive_path in (
            ("source bundle", source_bundle),
            ("source freeze receipt", source_freeze_receipt),
        ):
            if isinstance(sensitive_path, Path) and paths_refer_same(
                out_dir, sensitive_path
            ):
                raise PacketBuildError(f"official packet output aliases {label}")
    target = _target_manifest(target_path, root)
    if not allow_test_only_provenance:
        for label, sensitive_path in (
            ("source bundle", source_bundle),
            ("source freeze receipt", source_freeze_receipt),
        ):
            if isinstance(sensitive_path, Path):
                mode_error = private_path_error(sensitive_path, directory=False)
                if mode_error:
                    raise PacketBuildError(f"official {label} {mode_error}")
                location_error = controlled_path_error(sensitive_path, repo_root=root)
                if location_error:
                    raise PacketBuildError(f"official {label} {location_error}")
    raw_source = read_json(source_bundle) if isinstance(source_bundle, Path) else dict(source_bundle)
    target_cases = [_require_mapping(row, "target case") for row in target["cases"]]
    target_by_id = {str(row["case_id"]): row for row in target_cases}
    source = _source_bundle(raw_source, set(target_by_id))
    freeze_receipt, official_provenance_pass = _source_freeze_receipt(
        value=source_freeze_receipt,
        expected_receipt_digest=trusted_source_freeze_receipt_digest,
        source_bundle_input=source_bundle,
        source_bundle=source,
        target_manifest_path=target_path,
        allow_test_only_provenance=allow_test_only_provenance,
    )
    nonce = _validated_blinding_nonce(blinding_nonce)
    nonce_commitment = blinding_nonce_commitment(nonce)
    retrieval_split_assignments, retrieval_split_commitment = (
        _secret_retrieval_split_assignments(
            target_cases=target_cases,
            blinding_nonce=nonce,
        )
    )
    target_cases = [
        {
            **case,
            "retrieval_split": retrieval_split_assignments[str(case["case_id"])],
            "retrieval_split_assignment_commitment": retrieval_split_commitment,
        }
        for case in target_cases
    ]
    packet_id = "c03-human-eval::" + stable_digest(
        {
            "target_manifest": file_digest(target_path),
            "source_bundle": stable_digest(source),
            "source_freeze_receipt_digest": freeze_receipt["receipt_digest"],
            "packet_contract": "isolated-reviewer-cohorts-v2",
            "blinding_nonce_commitment": nonce_commitment,
            "retrieval_split_assignment_commitment": retrieval_split_commitment,
        }
    )[:24]
    source_by_id = {
        str(_require_mapping(row, "source case")["case_id"]): _require_mapping(row, "source case")
        for row in source["cases"]
    }
    expected_section_counts = {
        str(key): int(value) for key, value in dict(target["section_claim_counts"]).items()
    }
    ranked_sections = tuple(str(value) for value in target["independently_ranked_sections"])
    slots_per_section = int(target["retrieval_slots_per_ranked_section"])

    claim_items: list[dict[str, Any]] = []
    claim_mappings: list[dict[str, Any]] = []
    retrieval_queries: list[dict[str, Any]] = []
    retrieval_mappings: list[dict[str, Any]] = []
    w9_pairs: list[dict[str, Any]] = []
    w9_mappings: list[dict[str, Any]] = []

    for case in sorted(target_cases, key=lambda row: str(row["case_id"])):
        case_id = str(case["case_id"])
        source_case = source_by_id[case_id]
        claims_raw = source_case.get("claims")
        if not isinstance(claims_raw, list):
            raise PacketBuildError(f"{case_id}: claims must be a list")
        claims = [_require_mapping(row, f"{case_id} claim") for row in claims_raw]
        observed_counts = Counter(_require_text(row.get("section_id"), f"{case_id} section_id") for row in claims)
        if dict(observed_counts) != expected_section_counts:
            raise PacketBuildError(
                f"{case_id}: section claim counts differ from frozen contract: {dict(observed_counts)}"
            )
        claim_units = [str(row.get("claim_unit_id") or "") for row in claims]
        if len(set(claim_units)) != len(claim_units) or any(not value for value in claim_units):
            raise PacketBuildError(f"{case_id}: claim_unit_id values must be present and unique")
        context = _target_context(case, root)
        by_section: dict[str, list[dict[str, Any]]] = {}
        for claim in sorted(claims, key=lambda row: (str(row["section_id"]), str(row["claim_unit_id"]))):
            item, mapping = _claim_item(
                blinding_nonce=nonce,
                case=case,
                source_case=source_case,
                claim=claim,
                target_context=context,
            )
            claim_items.append(item)
            claim_mappings.append(mapping)
            by_section.setdefault(str(claim["section_id"]), []).append(claim)
        for section_id in ranked_sections:
            selected = sorted(by_section[section_id], key=lambda row: str(row["claim_unit_id"]))[
                :slots_per_section
            ]
            if len(selected) != slots_per_section:
                raise PacketBuildError(f"{case_id}/{section_id}: insufficient frozen retrieval slots")
            for claim in selected:
                query, mapping = _retrieval_query(
                    blinding_nonce=nonce,
                    case=case,
                    claim=claim,
                    target_context=context,
                )
                retrieval_queries.append(query)
                retrieval_mappings.append(mapping)
        if require_w9:
            w9 = _w9_pair(
                blinding_nonce=nonce,
                case=case,
                source_case=source_case,
                target_context=context,
            )
            if w9 is not None:
                pair, mapping = w9
                w9_pairs.append(pair)
                w9_mappings.append(mapping)

    try:
        proof_split_salt, proof_assignments = allocate_stratified_proof_splits(
            claim_mappings,
            minimum_split_count=20,
        )
    except ProofSplitPolicyError as exc:
        raise PacketBuildError(f"unable to allocate proof split: {exc}") from exc
    claim_mappings = [
        record_with_digest(
            {
                **{
                    key: value
                    for key, value in mapping.items()
                    if key != "record_digest"
                },
                "proof_split": proof_assignments[
                    str(mapping["proof_split_group_digest"])
                ],
                "proof_split_policy_id": PROOF_SPLIT_POLICY_ID,
                "proof_split_policy_salt": proof_split_salt,
            },
            "record_digest",
        )
        for mapping in claim_mappings
    ]

    if w9_pairs and len(w9_pairs) != len(target_cases):
        raise PacketBuildError("W9 pair inputs must be present for either all six cases or none")
    if require_w9 and len(w9_pairs) != 6:
        raise PacketBuildError("--require-w9 requires six complete blind comparison pairs")

    output_alias = Path(out_dir)
    if output_alias.is_symlink():
        raise PacketBuildError("packet output must not be a symlink alias")
    output = output_alias.resolve()
    if not allow_test_only_provenance:
        output_error = controlled_path_error(output_alias, repo_root=root)
        if output_error:
            raise PacketBuildError(f"official packet output {output_error}")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty packet directory: {output}")
    ensure_private_directory(output)
    include_w9_distribution = require_w9
    distribution_files = reviewer_distribution_files_by_cohort(
        include_w9=include_w9_distribution
    )
    reviewer_path_cohort = {
        path: cohort
        for cohort, cohort_paths in distribution_files.items()
        for path in cohort_paths
    }
    rows_by_path: dict[str, Sequence[Mapping[str, Any]]] = {
        REVIEWER_FILES[0]: claim_items,
        REVIEWER_FILES[1]: retrieval_queries,
        INTERNAL_FILES[0]: claim_mappings,
        INTERNAL_FILES[1]: retrieval_mappings,
    }
    if include_w9_distribution:
        rows_by_path[REVIEWER_FILES[2]] = w9_pairs
        rows_by_path[INTERNAL_FILES[2]] = w9_mappings
    files: list[dict[str, Any]] = []
    for relative_path, rows in rows_by_path.items():
        path = output / relative_path
        row_count = write_jsonl(path, rows)
        cohort = reviewer_path_cohort.get(relative_path)
        files.append(
            {
                "path": relative_path,
                "sha256": file_digest(path),
                "row_count": row_count,
                "format": "jsonl",
                "distribution": (
                    f"reviewer_{cohort}" if cohort is not None else "sealed_internal"
                ),
            }
        )
    reviewer_assets = _reviewer_asset_sources(include_w9=include_w9_distribution)
    for relative_path, source_path in sorted(reviewer_assets.items()):
        destination = output / relative_path
        copy_private_file(source_path, destination)
        cohort = reviewer_path_cohort[relative_path]
        files.append(
            {
                "path": relative_path,
                "sha256": file_digest(destination),
                "byte_count": destination.stat().st_size,
                "format": destination.suffix.removeprefix("."),
                "distribution": f"reviewer_{cohort}",
            }
        )
    reviewer_distributions: dict[str, dict[str, Any]] = {}
    item_type_by_cohort = {
        "proof": "claim",
        "retrieval": "retrieval",
        "w9": "w9_pair",
    }
    for cohort, root_name in REVIEWER_ROOTS.items():
        if cohort not in distribution_files:
            continue
        cohort_distribution = f"reviewer_{cohort}"
        cohort_content_rows = sorted(
            (
                {
                    key: value
                    for key, value in row.items()
                    if key in {"path", "sha256", "row_count", "byte_count", "format"}
                }
                for row in files
                if row["distribution"] == cohort_distribution
            ),
            key=lambda row: str(row["path"]),
        )
        manifest_relative, checksum_relative = _cohort_generated_files(cohort)
        cohort_manifest = record_with_digest(
            {
                "schema_version": "apps_rg.c03_human_eval.reviewer_manifest.v1",
                "packet_id": packet_id,
                "reviewer_cohort": cohort,
                "item_type": item_type_by_cohort[cohort],
                "files": [
                    {
                        **row,
                        "path": str(row["path"]).removeprefix(root_name + "/"),
                    }
                    for row in cohort_content_rows
                ],
                "checksum_file": "SHA256SUMS",
                "sealed_internal_paths_included": False,
                "other_reviewer_cohort_paths_included": False,
                "reviewer_blinding_required": True,
                "cross_cohort_distribution_forbidden": True,
            },
            "manifest_digest",
        )
        cohort_manifest_path = output / manifest_relative
        write_json(cohort_manifest_path, cohort_manifest)
        cohort_manifest_file = {
            "path": manifest_relative,
            "sha256": file_digest(cohort_manifest_path),
            "byte_count": cohort_manifest_path.stat().st_size,
            "format": "json",
            "distribution": cohort_distribution,
        }
        files.append(cohort_manifest_file)
        checksum_rows = [
            (
                str(row["sha256"]),
                str(row["path"]).removeprefix(root_name + "/"),
            )
            for row in [*cohort_content_rows, cohort_manifest_file]
        ]
        checksum_path = output / checksum_relative
        write_private_text(
            checksum_path,
            "".join(
                f"{digest}  {path}\n"
                for digest, path in sorted(checksum_rows, key=lambda row: row[1])
            ),
        )
        checksum_file = {
            "path": checksum_relative,
            "sha256": file_digest(checksum_path),
            "byte_count": checksum_path.stat().st_size,
            "format": "sha256",
            "distribution": cohort_distribution,
        }
        files.append(checksum_file)
        reviewer_distributions[cohort] = {
            "root": root_name,
            "item_type": item_type_by_cohort[cohort],
            "manifest_path": manifest_relative,
            "manifest_digest": cohort_manifest["manifest_digest"],
            "checksum_path": checksum_relative,
            "files": list(distribution_files[cohort]),
            "cross_cohort_distribution_forbidden": True,
            "separate_reviewer_cohort_required": True,
        }

    active_rubric_files = {
        key: filename
        for key, filename in RUBRIC_FILES.items()
        if key != "w9_pair" or include_w9_distribution
    }
    rubric_digests = {
        key: file_digest(Path(__file__).with_name(filename))
        for key, filename in active_rubric_files.items()
    }
    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA,
        "packet_id": packet_id,
        "dataset_id": str(target["dataset_id"]),
        "dataset_version": str(target["dataset_version"]),
        "target_manifest_digest": file_digest(target_path),
        "source_bundle_digest": stable_digest(source),
        "source_freeze_receipt": freeze_receipt,
        "source_freeze_receipt_digest": freeze_receipt["receipt_digest"],
        "source_provenance_status": (
            "OFFICIAL_PASS" if official_provenance_pass else "TEST_ONLY_UNTRUSTED"
        ),
        "official_source_provenance_pass": official_provenance_pass,
        "retrieval_candidate_judging_scope": FULL_UNIVERSE_JUDGING_SCOPE,
        "retrieval_split_policy_id": RETRIEVAL_SPLIT_POLICY_ID,
        "retrieval_split_assignment_commitment": retrieval_split_commitment,
        "source_commit_sha": str(source["source_commit_sha"]),
        "blinding_nonce_commitment": nonce_commitment,
        "graph_digest": str(source.get("graph_digest") or ""),
        "policy_digest": str(source.get("policy_digest") or ""),
        "proof_split_policy_id": PROOF_SPLIT_POLICY_ID,
        "proof_split_policy_salt": proof_split_salt,
        "rubric_digests": rubric_digests,
        "coverage": _coverage(
            claim_items, claim_mappings, retrieval_queries, retrieval_mappings, w9_pairs
        ),
        "reviewer_files": list(
            reviewer_distribution_files(include_w9=include_w9_distribution)
        ),
        "reviewer_distributions": reviewer_distributions,
        "sealed_internal_files": list(
            sealed_internal_files(include_w9=include_w9_distribution)
        ),
        "files": sorted(files, key=lambda row: row["path"]),
        "w9_ready": len(w9_pairs) == 6,
        "blinding_policy": {
            "reviewer_payloads_exclude_system_scores": True,
            "reviewer_payloads_exclude_system_verdicts": True,
            "reviewer_payloads_exclude_other_labels": True,
            "retrieval_rank_hidden": True,
            "proof_and_retrieval_distributions_isolated": True,
            "proof_and_retrieval_reviewer_cohorts_must_be_disjoint": True,
            "reviewer_item_ids_are_lane_opaque": True,
            "reviewer_payloads_exclude_case_and_claim_unit_keys": True,
            "retrieval_target_is_selected_output_independent": True,
            "retrieval_split_is_secret_hmac_assigned": True,
            "reviewer_payloads_exclude_split_assignments": True,
            "w9_variant_identity_hidden": True,
            "sealed_internal_distribution_forbidden": True,
            "full_packet_reviewer_distribution_forbidden": True,
            "source_bundle_reviewer_distribution_forbidden": True,
        },
    }
    manifest = record_with_digest(manifest, "manifest_digest")
    manifest_path = output / "packet_manifest.json"
    write_json(manifest_path, manifest)
    checksum_rows = [
        (file_digest(output / row["path"]), row["path"]) for row in manifest["files"]
    ] + [(file_digest(manifest_path), "packet_manifest.json")]
    write_private_text(
        output / "SHA256SUMS",
        "".join(f"{digest}  {path}\n" for digest, path in sorted(checksum_rows, key=lambda row: row[1])),
    )
    return manifest


def assess_source_bundle_readiness(
    *,
    source_bundle: Mapping[str, Any] | Path,
    source_freeze_receipt: Mapping[str, Any] | Path,
    trusted_source_freeze_receipt_digest: str,
    blinding_nonce: str,
    target_manifest_path: Path = DEFAULT_TARGET_MANIFEST,
    repo_root: Path | None = None,
    require_w9: bool = False,
    allow_test_only_provenance: bool = False,
) -> dict[str, Any]:
    """Exercise the full builder in a temporary directory without publishing a packet."""

    result: dict[str, Any] = {
        "schema_version": "apps_rg.c03_human_eval.source_readiness.v1",
        "status": "FAIL",
        "packet_build_ready": False,
        "official_provenance_pass": False,
        "require_w9": require_w9,
        "expected_counts": {
            "claim_items": EXPECTED_CLAIM_ITEMS,
            "retrieval_queries": EXPECTED_RETRIEVAL_QUERIES,
            "w9_pairs": EXPECTED_W9_PAIRS,
        },
        "observed_counts": {},
        "errors": [],
    }
    try:
        with TemporaryDirectory(prefix="apps-rg-c03-human-eval-") as temp:
            packet_dir = Path(temp) / "packet"
            manifest = build_packet(
                source_bundle=source_bundle,
                source_freeze_receipt=source_freeze_receipt,
                trusted_source_freeze_receipt_digest=(
                    trusted_source_freeze_receipt_digest
                ),
                out_dir=packet_dir,
                blinding_nonce=blinding_nonce,
                target_manifest_path=target_manifest_path,
                repo_root=repo_root,
                require_w9=require_w9,
                allow_test_only_provenance=allow_test_only_provenance,
            )
            from .validation import validate_prelabel_packet

            validation = validate_prelabel_packet(
                packet_dir,
                require_w9=require_w9,
                trusted_source_freeze_receipt_digest=(
                    trusted_source_freeze_receipt_digest
                ),
                allow_test_only_provenance=allow_test_only_provenance,
            )
            coverage = dict(manifest.get("coverage") or {})
            result["observed_counts"] = {
                "claim_items": int(coverage.get("claim_count") or 0),
                "retrieval_queries": int(coverage.get("retrieval_query_count") or 0),
                "w9_pairs": int(coverage.get("w9_pair_count") or 0),
            }
            result["packet_id"] = manifest.get("packet_id")
            result["source_bundle_digest"] = manifest.get("source_bundle_digest")
            result["source_freeze_receipt_digest"] = manifest.get(
                "source_freeze_receipt_digest"
            )
            result["official_provenance_pass"] = manifest.get(
                "official_source_provenance_pass"
            ) is True
            result["prelabel_validation"] = validation
            if not validation["pass"]:
                result["errors"] = [
                    f"prelabel: {message}" for message in validation["errors"]
                ]
                return result
            result["status"] = (
                "PASS"
                if result["official_provenance_pass"]
                else "PASS_TEST_ONLY"
            )
            result["packet_build_ready"] = True
    except (OSError, ValueError, TypeError) as exc:
        result["errors"] = [str(exc)]
    return result


__all__ = [
    "DEFAULT_TARGET_MANIFEST",
    "EXPECTED_CLAIM_ITEMS",
    "EXPECTED_RETRIEVAL_QUERIES",
    "EXPECTED_W9_PAIRS",
    "FULL_UNIVERSE_JUDGING_SCOPE",
    "INTERNAL_FILES",
    "PacketBuildError",
    "PROOF_REVIEWER_ROOT",
    "REVIEWER_FILES",
    "REVIEWER_ROOTS",
    "RETRIEVAL_REVIEWER_ROOT",
    "BASE_REVIEWER_ASSET_FILES",
    "W9_REVIEWER_ROOT",
    "W9_REVIEWER_ASSET_FILES",
    "REVIEWER_GENERATED_FILES",
    "assess_source_bundle_readiness",
    "blinding_nonce_commitment",
    "build_packet",
    "frontier_contract_error",
    "frontier_metadata_contract_error",
    "metric_applicable",
    "reviewer_distribution_files",
    "reviewer_distribution_files_by_cohort",
]
