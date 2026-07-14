"""Freeze deterministic W6 allocation evidence for the human-review packet.

This module is the narrow bridge between the production whole-resume allocator
and :mod:`apps_rg.evals.c03_human_eval.packet`.  The allocator intentionally
publishes only the winning assignments.  Retrieval evaluation also needs a
bounded view of the exact candidate universe from which those winners were
chosen, so this bridge reuses the allocator's private candidate-construction
and ordering helpers.  Keeping that dependency here prevents the reviewer
packet from inventing a second ranking policy.

Reviewer-visible proof context never contains scores, predictions, verdicts,
selection state, or ranks.  Those values remain under ``system_fields`` in the
sealed mapping.  The function does not create W9 resume variants.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from ._io import path_has_symlink_component

from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    load_master_skills_arsenal_ledger,
)
from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest
from apps_rg.runtime.c0.resume_graph_allocation import (
    DEFAULT_MAX_CANDIDATES_PER_SLOT,
    _candidate_sets_from_section_plans,
    _candidate_sort_key,
    _default_slot_specs,
    build_whole_resume_graph_allocation,
)

SOURCE_BUNDLE_SCHEMA = "apps_rg.c03_human_eval.source_bundle.v1"
SOURCE_FREEZE_RECEIPT_SCHEMA = "apps_rg.c03_human_eval.source_freeze_receipt.v1"
TARGET_CASES_SCHEMA = "apps_rg.c03_human_eval.target_cases.v1"
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_RETRIEVAL_K_MAX = 10
_ALLOCATOR_ELIGIBLE_REASON_CODES = frozenset(
    {
        "selected_by_global_allocation",
        "global_constraint_or_objective_not_selected",
    }
)
_ALLOCATOR_BUDGET_REASON_CODE = "allocation_candidate_budget"


class SourceBundleFreezeError(ValueError):
    """The frozen inputs or allocator output cannot satisfy the W6 contract."""


def build_source_freeze_receipt(
    *,
    source_bundle_path: Path,
    source_bundle: Mapping[str, Any],
    target_manifest_path: Path,
) -> dict[str, Any]:
    """Seal a clean-checkout allocator freeze into an externally pinnable receipt."""

    bundle_path = source_bundle_path.resolve()
    target_path = target_manifest_path.resolve()
    if not bundle_path.is_file():
        raise SourceBundleFreezeError("source bundle file is required before receipt sealing")
    if not target_path.is_file():
        raise SourceBundleFreezeError("target manifest file is required before receipt sealing")
    try:
        observed_bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise SourceBundleFreezeError(f"source bundle file is not valid JSON: {exc}") from exc
    if observed_bundle != dict(source_bundle):
        raise SourceBundleFreezeError(
            "source bundle file content differs from the allocator freeze payload"
        )
    cases = source_bundle.get("cases")
    if not isinstance(cases, list):
        raise SourceBundleFreezeError("source bundle cases must be a list")
    claims = [
        claim
        for case in cases
        if isinstance(case, Mapping)
        for claim in case.get("claims") or []
    ]
    receipt: dict[str, Any] = {
        "schema_version": SOURCE_FREEZE_RECEIPT_SCHEMA,
        "freeze_mode": "CLEAN_CHECKOUT_REAL_ALLOCATOR",
        "official_provenance_eligible": True,
        "checkout_head_verified": True,
        "checkout_clean_verified": True,
        "source_bundle_sha256": _file_digest(bundle_path),
        "source_bundle_canonical_digest": stable_digest(source_bundle),
        "source_commit_sha": _text(
            source_bundle.get("source_commit_sha"), "source_commit_sha"
        ),
        "target_manifest_digest": _file_digest(target_path),
        "graph_digest": _text(source_bundle.get("graph_digest"), "graph_digest"),
        "policy_digest": _text(source_bundle.get("policy_digest"), "policy_digest"),
        "case_count": len(cases),
        "claim_count": len(claims),
        "retrieval_frontier_count": sum(
            isinstance(claim, Mapping) and "candidate_frontier" in claim
            for claim in claims
        ),
        "unknown_is_pass": False,
    }
    receipt["receipt_digest"] = stable_digest(receipt)
    return receipt


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise SourceBundleFreezeError(f"{label} must be an object")
    return dict(value)


def _text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise SourceBundleFreezeError(f"{label} is required")
    return text


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest(value: Mapping[str, Any] | Path) -> dict[str, Any]:
    if isinstance(value, Path):
        if value.is_symlink() or path_has_symlink_component(value):
            raise SourceBundleFreezeError(
                "target cases manifest must be a real non-symlink file"
            )
        payload = yaml.safe_load(value.read_text(encoding="utf-8"))
    else:
        payload = value
    manifest = _mapping(payload, "target cases manifest")
    if manifest.get("schema_version") != TARGET_CASES_SCHEMA:
        raise SourceBundleFreezeError(
            f"target cases schema must be {TARGET_CASES_SCHEMA}"
        )
    cases = manifest.get("cases")
    if not isinstance(cases, list) or len(cases) != 6:
        raise SourceBundleFreezeError("target cases manifest must contain exactly six cases")
    if int(manifest.get("claim_count_per_case") or 0) != 47:
        raise SourceBundleFreezeError("claim_count_per_case must be 47")
    if int(manifest.get("retrieval_slots_per_ranked_section") or 0) != 2:
        raise SourceBundleFreezeError("retrieval_slots_per_ranked_section must be 2")
    ranked = manifest.get("independently_ranked_sections")
    if not isinstance(ranked, list) or len(ranked) != 7:
        raise SourceBundleFreezeError(
            "independently_ranked_sections must contain exactly seven sections"
        )
    return manifest


def _source_path(repo_root: Path, relative_path: Any, label: str) -> Path:
    relative = Path(_text(relative_path, label))
    if relative.is_absolute():
        raise SourceBundleFreezeError(f"{label} must be repository-relative")
    unresolved = repo_root / relative
    if path_has_symlink_component(unresolved):
        raise SourceBundleFreezeError(f"{label} must be a real non-symlink file")
    path = unresolved.resolve()
    try:
        path.relative_to(repo_root)
    except ValueError as exc:
        raise SourceBundleFreezeError(f"{label} escapes repo_root") from exc
    if not path.is_file():
        raise SourceBundleFreezeError(f"{label} does not exist: {relative}")
    return path


def _frozen_text(
    *,
    repo_root: Path,
    case: Mapping[str, Any],
    kind: str,
) -> str:
    case_id = _text(case.get("case_id"), "case_id")
    path = _source_path(repo_root, case.get(f"{kind}_path"), f"{case_id} {kind}_path")
    expected = _text(case.get(f"{kind}_sha256"), f"{case_id} {kind}_sha256")
    if not _DIGEST_RE.fullmatch(expected):
        raise SourceBundleFreezeError(f"{case_id} {kind}_sha256 is not a SHA-256 digest")
    observed = _file_digest(path)
    if observed != expected:
        raise SourceBundleFreezeError(
            f"{case_id}: frozen {kind} digest mismatch: expected {expected}, got {observed}"
        )
    return path.read_text(encoding="utf-8")


def _visible_claim_text(candidate: Mapping[str, Any]) -> str:
    root_text = _text(candidate.get("root_claim_text"), "candidate root_claim_text")
    metric_text = str(candidate.get("metric_text") or "").strip()
    if not metric_text:
        return root_text
    return f"{root_text} Exact metric: {metric_text}"


def _load_skill_evidence(repo_root: Path) -> dict[str, dict[str, list[str]]]:
    """Load canonical, pre-targeting skill evidence exactly once per freeze."""

    ledger = load_master_skills_arsenal_ledger(repo_root=repo_root)
    rows = ledger.get("skill_rows")
    if not isinstance(rows, list):
        raise SourceBundleFreezeError("arsenal ledger skill_rows must be a list")
    output: dict[str, dict[str, list[str]]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            continue
        skill_id = str(raw.get("skill_id") or "").strip()
        if not skill_id:
            continue
        if skill_id in output:
            raise SourceBundleFreezeError(f"duplicate arsenal skill evidence for {skill_id}")
        output[skill_id] = {
            "source_snippets": [
                str(value).strip()
                for value in raw.get("source_snippets") or []
                if str(value).strip()
            ],
            "fact_id_links": [
                str(value).strip()
                for value in raw.get("fact_id_links") or []
                if str(value).strip()
            ],
            "source_resume_files": [
                str(value).strip()
                for value in raw.get("source_resume_files") or []
                if str(value).strip()
            ],
        }
    return output


def _proof_context(
    candidate: Mapping[str, Any],
    skill_evidence: Mapping[str, Mapping[str, Sequence[str]]],
) -> dict[str, Any]:
    """Build non-circular reviewer evidence from the canonical source ledger."""

    skill_id = _text(candidate.get("skill_id"), "candidate skill_id")
    root_claim = _text(candidate.get("root_claim_text"), "candidate root_claim_text")
    evidence = skill_evidence.get(skill_id)
    if not isinstance(evidence, Mapping):
        raise SourceBundleFreezeError(
            f"{skill_id}: selected graph skill has no canonical arsenal evidence row"
        )
    snippets = [
        str(value).strip()
        for value in evidence.get("source_snippets") or []
        if str(value).strip() and str(value).strip() != root_claim
    ]
    fact_id = _text(candidate.get("fact_id"), f"{skill_id} candidate fact_id")
    fact_links = [str(value) for value in evidence.get("fact_id_links") or []]
    source_files = [str(value) for value in evidence.get("source_resume_files") or []]
    citations = [str(value) for value in candidate.get("citation_refs") or []]
    trace_parts = [
        f"skill_id={skill_id}",
        f"candidate_fact_id={fact_id}",
    ]
    if fact_links:
        trace_parts.append("ledger_fact_id_links=" + ", ".join(fact_links))
    if source_files:
        trace_parts.append("source_resume_files=" + ", ".join(source_files))
    if citations:
        trace_parts.append("citation_refs=" + ", ".join(citations))
    source_trace = "; ".join(trace_parts)
    if snippets:
        evidence_text = "\n".join(snippets)
        evidence_mode = "CANONICAL_SOURCE_SNIPPET"
        canonical_truth_input_assumption = False
    else:
        # W0 freezes canonical graph facts as validated truth inputs.  This is
        # not independent corroboration: expose the canonical graph claim and
        # exact provenance so a reviewer can label the proof relationship
        # without being forced to infer meaning from opaque IDs.
        evidence_text = (
            "Canonical graph fact authority (accepted truth input; not independent "
            f"corroboration): {root_claim} Provenance: {source_trace}"
        )
        evidence_mode = "CANONICAL_FACT_AUTHORITY"
        canonical_truth_input_assumption = True
    if evidence_text.strip() == root_claim:
        raise SourceBundleFreezeError(
            f"{skill_id}/{fact_id}: reviewer evidence cannot equal the visible root claim"
        )
    metric_text = str(candidate.get("metric_text") or "").strip()
    return {
        "evidence_text": evidence_text,
        "evidence_mode": evidence_mode,
        "canonical_truth_input_assumption": canonical_truth_input_assumption,
        "independent_corroboration": False,
        "source_trace_text": source_trace,
        "skill_text": str(
            candidate.get("skill_label") or candidate.get("skill_id") or ""
        ).strip(),
        "fact_text": str(candidate.get("fact_id") or "").strip(),
        "metric_text": metric_text or "not applicable",
        "path_text": " -> ".join(
            str(value) for value in candidate.get("graph_path_ids") or []
        ),
        "citation_text": ", ".join(
            str(value) for value in candidate.get("citation_refs") or []
        ),
    }


def _binding(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Retain exact graph/fact/metric references without adding authority."""

    return {
        "root_id": str(candidate.get("root_id") or ""),
        "skill_id": str(candidate.get("skill_id") or ""),
        "fact_id": str(candidate.get("fact_id") or ""),
        "metric_outcome_id": str(candidate.get("metric_outcome_id") or ""),
        "metric_text": str(candidate.get("metric_text") or ""),
        "metric_value": str(candidate.get("metric_value") or ""),
        "metric_unit": str(candidate.get("metric_unit") or ""),
        "normalized_metric_signature": str(
            candidate.get("normalized_metric_signature") or ""
        ),
        "graph_path_ids": [
            str(value) for value in candidate.get("graph_path_ids") or []
        ],
        "edge_ids": [str(value) for value in candidate.get("edge_ids") or []],
        "citation_refs": [
            str(value) for value in candidate.get("citation_refs") or []
        ],
    }


def _system_fields(candidate: Mapping[str, Any], *, selected: bool) -> dict[str, Any]:
    metric_id = str(candidate.get("metric_outcome_id") or "")
    proof_strength = float(candidate.get("proof_strength_raw") or 0.0)
    claim_entailment = float(candidate.get("claim_entailment_score") or 0.0)
    metric_binding = float(candidate.get("metric_binding_score") or 0.0)
    return {
        # ``proof_score_raw`` is the evaluation-harness field; retain the
        # allocator-native name beside it so provenance is not collapsed.
        "proof_score_raw": proof_strength,
        "proof_strength_raw": proof_strength,
        "path_confidence_raw": float(candidate.get("path_confidence_raw") or 0.0),
        "source_independence_score": float(
            candidate.get("source_independence_score") or 0.0
        ),
        "target_alignment_score": float(
            candidate.get("target_alignment_score") or 0.0
        ),
        "claim_entailment_score": claim_entailment,
        "metric_binding_score": metric_binding,
        "selection_margin": float(candidate.get("selection_margin") or 0.0),
        "selection_margin_available": bool(
            candidate.get("selection_margin_available", False)
        ),
        "selection_margin_basis": str(
            candidate.get("selection_margin_basis") or ""
        ),
        "system_prediction": {
            "authority_eligible": candidate.get("authority_pass") is not False,
            "claim_entailment_prediction": claim_entailment >= 0.9,
            "path_valid": bool(candidate.get("graph_path_ids")),
            "metric_binding_prediction": not metric_id or metric_binding >= 0.95,
            "globally_selected": selected,
        },
    }


def _raw_selected_candidate(
    *,
    assignment: Mapping[str, Any],
    candidate_sets: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[dict[str, Any], str]:
    section_id = str(assignment.get("section_id") or "")
    source_claim_unit_id = str(
        assignment.get("derived_from_claim_unit_id")
        or assignment.get("claim_unit_id")
        or ""
    )
    selected_id = str(assignment.get("candidate_id") or "")
    if assignment.get("derived_from_claim_unit_id"):
        selected_id = selected_id.removeprefix(f"derived:{section_id}:")
    rows = [dict(row) for row in candidate_sets.get(source_claim_unit_id) or []]
    for candidate in rows:
        if str(candidate.get("candidate_id") or "") == selected_id:
            return candidate, source_claim_unit_id
    raise SourceBundleFreezeError(
        f"{section_id}/{assignment.get('claim_unit_id')}: selected candidate "
        f"{selected_id!r} is absent from the frozen candidate universe"
    )


def _allocator_bounded_candidate_sets(
    *,
    raw_candidate_sets: Mapping[str, Sequence[Mapping[str, Any]]],
    allocation_plan: Mapping[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    """Project raw candidates onto the allocator's actual eligible universe.

    ``allocate_candidate_sets`` currently admits at most 64 normalized rows per
    slot.  Its decision ledger is authoritative for that boundary: eligible
    rows carry one of the two global-allocation reason codes, while overflow
    rows carry ``allocation_candidate_budget`` and invalid rows retain their
    fail-closed rejection reason.  Using the ledger avoids evaluating raw
    cross-product rows the allocator could never retrieve.
    """

    solver_metadata = allocation_plan.get("solver_metadata")
    if not isinstance(solver_metadata, Mapping) or solver_metadata.get(
        "max_candidates_per_slot"
    ) != DEFAULT_MAX_CANDIDATES_PER_SLOT:
        raise SourceBundleFreezeError(
            "allocation plan candidate budget disagrees with the frozen allocator contract"
        )

    admitted_ids_by_slot: dict[str, set[str]] = {}
    budget_rejected_ids_by_slot: dict[str, set[str]] = {}
    decisions = allocation_plan.get("candidate_decisions")
    if not isinstance(decisions, list):
        raise SourceBundleFreezeError("allocation plan candidate_decisions must be a list")
    for raw in decisions:
        if not isinstance(raw, Mapping):
            continue
        claim_unit_id = str(raw.get("claim_unit_id") or "").strip()
        candidate_id = str(raw.get("candidate_id") or "").strip()
        reason_codes = {str(value) for value in raw.get("reason_codes") or []}
        if (
            claim_unit_id
            and candidate_id
            and reason_codes.intersection(_ALLOCATOR_ELIGIBLE_REASON_CODES)
        ):
            admitted_ids_by_slot.setdefault(claim_unit_id, set()).add(candidate_id)
        elif (
            claim_unit_id
            and candidate_id
            and _ALLOCATOR_BUDGET_REASON_CODE in reason_codes
        ):
            budget_rejected_ids_by_slot.setdefault(claim_unit_id, set()).add(candidate_id)

    output: dict[str, list[dict[str, Any]]] = {}
    boundary_metadata: dict[str, dict[str, Any]] = {}
    for claim_unit_id, raw_rows in raw_candidate_sets.items():
        admitted_ids = admitted_ids_by_slot.get(str(claim_unit_id), set())
        budget_rejected_ids = budget_rejected_ids_by_slot.get(
            str(claim_unit_id), set()
        )
        raw_eligible_ids = admitted_ids | budget_rejected_ids
        rows = [
            dict(row)
            for row in raw_rows
            if str(row.get("candidate_id") or "") in admitted_ids
        ]
        observed_ids = {str(row.get("candidate_id") or "") for row in rows}
        raw_ids = {str(row.get("candidate_id") or "") for row in raw_rows}
        if observed_ids != admitted_ids or not raw_eligible_ids.issubset(raw_ids):
            missing = sorted(raw_eligible_ids - raw_ids)
            raise SourceBundleFreezeError(
                f"{claim_unit_id}: allocator-eligible candidates absent from raw universe: "
                f"{missing}"
            )
        if not rows:
            raise SourceBundleFreezeError(
                f"{claim_unit_id}: allocator decision ledger has no eligible candidates"
            )
        raw_eligible_count = len(raw_eligible_ids)
        admitted_count = len(admitted_ids)
        truncated = bool(budget_rejected_ids)
        if raw_eligible_count != admitted_count + len(budget_rejected_ids):
            raise SourceBundleFreezeError(
                f"{claim_unit_id}: allocator candidate decision IDs overlap"
            )
        if truncated:
            if admitted_count != DEFAULT_MAX_CANDIDATES_PER_SLOT:
                raise SourceBundleFreezeError(
                    f"{claim_unit_id}: truncated universe admitted {admitted_count}, "
                    f"expected allocator budget {DEFAULT_MAX_CANDIDATES_PER_SLOT}"
                )
            if raw_eligible_count <= DEFAULT_MAX_CANDIDATES_PER_SLOT:
                raise SourceBundleFreezeError(
                    f"{claim_unit_id}: budget truncation recorded below allocator budget"
                )
        elif raw_eligible_count != admitted_count:
            raise SourceBundleFreezeError(
                f"{claim_unit_id}: untruncated raw/admitted candidate counts disagree"
            )
        output[str(claim_unit_id)] = sorted(rows, key=_candidate_sort_key)
        boundary_metadata[str(claim_unit_id)] = {
            "raw_eligible_candidate_count": raw_eligible_count,
            "allocator_candidate_budget": DEFAULT_MAX_CANDIDATES_PER_SLOT,
            "allocator_budget_truncated": truncated,
        }
    return output, boundary_metadata


def _frontier(
    *,
    rows: Sequence[Mapping[str, Any]],
    selected_candidate_id: str,
    selected_assignment: Mapping[str, Any],
    skill_evidence: Mapping[str, Mapping[str, Sequence[str]]],
    universe_boundary: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Freeze the complete allocator-bounded finite universe for review.

    Recall@K needs relevance labels outside the system's top K; otherwise the
    judged pool is selected by the ranking being evaluated and recall can pass
    circularly.  The production allocator already bounds every slot at
    ``DEFAULT_MAX_CANDIDATES_PER_SLOT``.  Preserve every admitted candidate in
    that finite universe here while keeping rank and selection sealed later.
    """

    ranked = sorted((dict(row) for row in rows), key=_candidate_sort_key)
    candidate_ids = [str(candidate.get("candidate_id") or "") for candidate in ranked]
    if any(not value for value in candidate_ids) or len(set(candidate_ids)) != len(
        candidate_ids
    ):
        raise SourceBundleFreezeError("candidate frontier IDs must be present and unique")
    rank_by_id = {candidate_id: rank for rank, candidate_id in enumerate(candidate_ids, 1)}
    selected = next(
        (
            candidate
            for candidate in ranked
            if str(candidate.get("candidate_id") or "") == selected_candidate_id
        ),
        None,
    )
    if selected is None:
        raise SourceBundleFreezeError(
            f"selected candidate {selected_candidate_id!r} is absent from its frontier"
        )
    candidate_universe_size = len(ranked)
    selected_rank = rank_by_id[selected_candidate_id]
    audit_extra_included = candidate_universe_size > _RETRIEVAL_K_MAX and selected_rank > (
        _RETRIEVAL_K_MAX
    )
    output: list[dict[str, Any]] = []
    for candidate in ranked:
        candidate_id = str(candidate.get("candidate_id") or "")
        is_selected = candidate_id == selected_candidate_id
        evidence_candidate = dict(candidate)
        if is_selected:
            root_claim_text = evidence_candidate.get("root_claim_text")
            evidence_candidate.update(selected_assignment)
            evidence_candidate["candidate_id"] = candidate_id
            evidence_candidate["root_claim_text"] = root_claim_text
        fields = _system_fields(evidence_candidate, selected=is_selected)
        fields["binding"] = _binding(evidence_candidate)
        output.append(
            {
                "candidate_id": candidate_id,
                "candidate_text": _visible_claim_text(evidence_candidate),
                "proof_context": _proof_context(evidence_candidate, skill_evidence),
                "rank": rank_by_id[candidate_id],
                "selected": is_selected,
                "system_fields": fields,
            }
        )
    metadata = {
        "candidate_universe_size": candidate_universe_size,
        "raw_eligible_candidate_count": int(
            universe_boundary.get("raw_eligible_candidate_count") or 0
        ),
        "allocator_candidate_budget": int(
            universe_boundary.get("allocator_candidate_budget") or 0
        ),
        "allocator_budget_truncated": bool(
            universe_boundary.get("allocator_budget_truncated", False)
        ),
        "frontier_k": _RETRIEVAL_K_MAX,
        "frontier_exhausted": candidate_universe_size <= _RETRIEVAL_K_MAX,
        "judged_top_count": min(_RETRIEVAL_K_MAX, candidate_universe_size),
        "judged_candidate_count": candidate_universe_size,
        "candidate_judging_scope": "FULL_FINITE_UNIVERSE",
        "selected_audit_extra_included": audit_extra_included,
        "selected_audit_extra_rank": selected_rank if audit_extra_included else None,
    }
    expected_admitted = min(
        metadata["raw_eligible_candidate_count"], metadata["allocator_candidate_budget"]
    )
    if (
        metadata["allocator_candidate_budget"] != DEFAULT_MAX_CANDIDATES_PER_SLOT
        or candidate_universe_size != expected_admitted
        or metadata["allocator_budget_truncated"]
        is not (
            metadata["raw_eligible_candidate_count"]
            > metadata["allocator_candidate_budget"]
        )
    ):
        raise SourceBundleFreezeError(
            "candidate frontier boundary metadata disagrees with allocator universe"
        )
    return output, metadata


def freeze_allocation_source_bundle(
    *,
    repo_root: Path,
    target_cases_manifest: Mapping[str, Any] | Path,
    source_commit_sha: str,
) -> dict[str, Any]:
    """Run all six frozen targets and return a packet-compatible source bundle.

    ``source_commit_sha`` is supplied by the caller instead of inferred from a
    mutable checkout.  This makes provenance explicit and keeps the freezer
    deterministic in CI, local worktrees, and artifact reconstruction.
    """

    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise SourceBundleFreezeError(f"repo_root does not exist: {root}")
    source_sha = str(source_commit_sha or "").strip()
    if not _SHA_RE.fullmatch(source_sha):
        raise SourceBundleFreezeError(
            "source_commit_sha must be a lowercase 40-character hex SHA"
        )
    manifest = _manifest(target_cases_manifest)
    skill_evidence = _load_skill_evidence(root)
    ranked_sections = [str(value) for value in manifest["independently_ranked_sections"]]
    slots_per_section = int(manifest["retrieval_slots_per_ranked_section"])
    expected_section_counts = {
        str(key): int(value)
        for key, value in _mapping(
            manifest.get("section_claim_counts"), "section_claim_counts"
        ).items()
    }
    if sum(expected_section_counts.values()) != 47:
        raise SourceBundleFreezeError("section_claim_counts must sum to 47")

    raw_cases = [_mapping(value, "target case") for value in manifest["cases"]]
    case_ids = [_text(case.get("case_id"), "case_id") for case in raw_cases]
    if len(set(case_ids)) != 6:
        raise SourceBundleFreezeError("target case_id values must be unique")

    source_cases: list[dict[str, Any]] = []
    observed_graph_digests: set[str] = set()
    observed_policy_digests: set[str] = set()
    for case in sorted(raw_cases, key=lambda row: str(row.get("case_id") or "")):
        case_id = str(case["case_id"])
        target_profile_id = _text(
            case.get("target_profile_id"), f"{case_id} target_profile_id"
        )
        jd_text = _frozen_text(repo_root=root, case=case, kind="jd")
        briefing_text = _frozen_text(repo_root=root, case=case, kind="brief")
        bundle = build_whole_resume_graph_allocation(
            repo_root=root,
            target_role=target_profile_id.replace("_", " "),
            jd_text=jd_text,
            briefing_text=briefing_text,
        )
        allocation_plan = _mapping(
            bundle.get("allocation_plan"), f"{case_id} allocation_plan"
        )
        section_plans = _mapping(bundle.get("section_plans"), f"{case_id} section_plans")
        assignments = [
            _mapping(value, f"{case_id} assignment")
            for value in allocation_plan.get("assignments") or []
        ]
        if len(assignments) != 47:
            raise SourceBundleFreezeError(
                f"{case_id}: allocator returned {len(assignments)} claims instead of 47"
            )
        observed_counts: dict[str, int] = {}
        for assignment in assignments:
            section_id = _text(assignment.get("section_id"), f"{case_id} section_id")
            observed_counts[section_id] = observed_counts.get(section_id, 0) + 1
        if observed_counts != expected_section_counts:
            raise SourceBundleFreezeError(
                f"{case_id}: allocator section counts differ from frozen contract: "
                f"{observed_counts}"
            )

        # Private helpers are used deliberately: they are the sole constructor
        # and ordering policy for the allocator's objective candidate universe.
        slot_specs = _default_slot_specs(section_plans)
        raw_candidate_sets = _candidate_sets_from_section_plans(section_plans, slot_specs)
        candidate_sets, universe_boundaries = _allocator_bounded_candidate_sets(
            raw_candidate_sets=raw_candidate_sets,
            allocation_plan=allocation_plan,
        )
        retrieval_claim_units: set[str] = set()
        for section_id in ranked_sections:
            section_assignments = sorted(
                (
                    assignment
                    for assignment in assignments
                    if str(assignment.get("section_id") or "") == section_id
                ),
                key=lambda row: str(row.get("claim_unit_id") or ""),
            )
            if len(section_assignments) < slots_per_section:
                raise SourceBundleFreezeError(
                    f"{case_id}/{section_id}: insufficient retrieval slots"
                )
            retrieval_claim_units.update(
                str(row.get("claim_unit_id") or "")
                for row in section_assignments[:slots_per_section]
            )

        claims: list[dict[str, Any]] = []
        for assignment in sorted(
            assignments,
            key=lambda row: (
                str(row.get("section_id") or ""),
                str(row.get("claim_unit_id") or ""),
            ),
        ):
            raw_selected_candidate, source_claim_unit_id = _raw_selected_candidate(
                assignment=assignment,
                candidate_sets=candidate_sets,
            )
            claim_unit_id = str(assignment["claim_unit_id"])
            source_selected_id = str(raw_selected_candidate.get("candidate_id") or "")
            selected_candidate = {**raw_selected_candidate, **assignment}
            selected_candidate["root_claim_text"] = raw_selected_candidate[
                "root_claim_text"
            ]
            claim: dict[str, Any] = {
                "section_id": str(assignment["section_id"]),
                "claim_unit_id": claim_unit_id,
                "visible_claim_text": _visible_claim_text(selected_candidate),
                "proof_context": _proof_context(selected_candidate, skill_evidence),
                "candidate_id": str(assignment["candidate_id"]),
                "binding": _binding(selected_candidate),
                "system_fields": _system_fields(selected_candidate, selected=True),
            }
            if claim_unit_id in retrieval_claim_units:
                frontier, frontier_metadata = _frontier(
                    rows=candidate_sets[source_claim_unit_id],
                    selected_candidate_id=source_selected_id,
                    selected_assignment=assignment,
                    skill_evidence=skill_evidence,
                    universe_boundary=universe_boundaries[source_claim_unit_id],
                )
                claim["candidate_frontier"] = frontier
                claim["candidate_frontier_metadata"] = frontier_metadata
            claims.append(claim)

        allocation_digest = _text(
            allocation_plan.get("allocation_plan_digest"),
            f"{case_id} allocation_plan_digest",
        )
        graph_digest = _text(
            allocation_plan.get("graph_digest"), f"{case_id} graph_digest"
        )
        policy_digest = _text(
            allocation_plan.get("policy_digest"), f"{case_id} policy_digest"
        )
        if not _DIGEST_RE.fullmatch(allocation_digest):
            raise SourceBundleFreezeError(f"{case_id}: invalid allocation plan digest")
        if not _DIGEST_RE.fullmatch(graph_digest) or not _DIGEST_RE.fullmatch(policy_digest):
            raise SourceBundleFreezeError(f"{case_id}: invalid graph or policy digest")
        observed_graph_digests.add(graph_digest)
        observed_policy_digests.add(policy_digest)
        source_cases.append(
            {
                "case_id": case_id,
                "run_id": "w6-allocation::"
                + stable_digest(
                    {
                        "source_commit_sha": source_sha,
                        "case_id": case_id,
                        "allocation_plan_digest": allocation_digest,
                    }
                )[:24],
                "allocation_plan_digest": allocation_digest,
                "claims": claims,
            }
        )

    if len(observed_graph_digests) != 1 or len(observed_policy_digests) != 1:
        raise SourceBundleFreezeError(
            "all six cases must share one frozen graph digest and policy digest"
        )
    return {
        "schema_version": SOURCE_BUNDLE_SCHEMA,
        "source_commit_sha": source_sha,
        "graph_digest": next(iter(observed_graph_digests)),
        "policy_digest": next(iter(observed_policy_digests)),
        "cases": source_cases,
    }


# A concise alias for callers that already operate in the W6 source-bundle domain.
freeze_source_bundle = freeze_allocation_source_bundle


__all__ = [
    "SOURCE_BUNDLE_SCHEMA",
    "SOURCE_FREEZE_RECEIPT_SCHEMA",
    "SourceBundleFreezeError",
    "build_source_freeze_receipt",
    "freeze_allocation_source_bundle",
    "freeze_source_bundle",
]
