"""Deterministic, identity-grouped proof split policy for W6 evidence."""

from __future__ import annotations

import unicodedata
from collections import defaultdict
from typing import Any, Mapping, Sequence

from ._io import stable_digest

PROOF_IDENTITY_POLICY_ID = "c03-proof-claim-binding-sha256-v1"
PROOF_SPLIT_GROUP_POLICY_ID = "c03-proof-binding-group-sha256-v1"
PROOF_SPLIT_POLICY_ID = "c03-proof-binding-group-stratified-sha256-v2"
PROOF_SPLITS = ("calibration", "holdout")
MAX_STRATIFIED_SALT = 100_000


class ProofSplitPolicyError(ValueError):
    """A claim binding cannot form the frozen canonical proof identity."""


def normalize_claim_text(value: Any) -> str:
    """Normalize Unicode, case, and whitespace without discarding claim content."""

    normalized = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = " ".join(normalized.split())
    if not text:
        raise ProofSplitPolicyError("visible claim text is required for proof identity")
    return text


def _required_binding_text(binding: Mapping[str, Any], field: str) -> str:
    value = str(binding.get(field) or "").strip()
    if not value:
        raise ProofSplitPolicyError(f"binding.{field} is required for proof identity")
    return value


def canonical_proof_identity(
    visible_claim_text: Any,
    binding: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the frozen claim+skill/fact/metric/path identity payload."""

    if not isinstance(binding, Mapping):
        raise ProofSplitPolicyError("binding must be an object for proof identity")
    path_ids = binding.get("graph_path_ids")
    if (
        not isinstance(path_ids, list)
        or not path_ids
        or any(not str(value or "").strip() for value in path_ids)
    ):
        raise ProofSplitPolicyError(
            "binding.graph_path_ids must be a nonempty path for proof identity"
        )
    return {
        "policy_id": PROOF_IDENTITY_POLICY_ID,
        "normalized_claim": normalize_claim_text(visible_claim_text),
        "binding": {
            "skill_id": _required_binding_text(binding, "skill_id"),
            "fact_id": _required_binding_text(binding, "fact_id"),
            "metric": {
                field: str(binding.get(field) or "").strip()
                for field in (
                    "metric_outcome_id",
                    "normalized_metric_signature",
                    "metric_text",
                    "metric_value",
                    "metric_unit",
                )
            },
            "graph_path_ids": [str(value).strip() for value in path_ids],
        },
    }


def proof_identity_digest(visible_claim_text: Any, binding: Mapping[str, Any]) -> str:
    """Hash claim+binding identity for entailment dedupe, not split grouping."""

    return stable_digest(canonical_proof_identity(visible_claim_text, binding))


def canonical_proof_split_group(binding: Mapping[str, Any]) -> dict[str, Any]:
    """Return the immutable binding-only grouping payload for proof splits."""

    if not isinstance(binding, Mapping):
        raise ProofSplitPolicyError("binding must be an object for proof split group")
    path_ids = binding.get("graph_path_ids")
    if (
        not isinstance(path_ids, list)
        or not path_ids
        or any(not str(value or "").strip() for value in path_ids)
    ):
        raise ProofSplitPolicyError(
            "binding.graph_path_ids must be a nonempty ordered path for proof split group"
        )
    return {
        "policy_id": PROOF_SPLIT_GROUP_POLICY_ID,
        "binding": {
            "skill_id": _required_binding_text(binding, "skill_id"),
            "fact_id": _required_binding_text(binding, "fact_id"),
            "metric": {
                field: str(binding.get(field) or "").strip()
                for field in (
                    "metric_outcome_id",
                    "normalized_metric_signature",
                    "metric_text",
                    "metric_value",
                    "metric_unit",
                )
            },
            "graph_path_ids": [str(value).strip() for value in path_ids],
        },
    }


def proof_split_group_digest(binding: Mapping[str, Any]) -> str:
    return stable_digest(canonical_proof_split_group(binding))


def proof_split_for_digest(group_digest: str, *, salt: int) -> str:
    """Assign a binding group with the packet's frozen deterministic salt."""

    digest = str(group_digest or "")
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ProofSplitPolicyError("proof split group digest must be lowercase SHA-256")
    if not isinstance(salt, int) or isinstance(salt, bool) or salt < 0:
        raise ProofSplitPolicyError("proof split salt must be a nonnegative integer")
    assignment_digest = stable_digest(
        {
            "policy_id": PROOF_SPLIT_POLICY_ID,
            "salt": salt,
            "proof_split_group_digest": digest,
        }
    )
    return PROOF_SPLITS[int(assignment_digest, 16) & 1]


def proof_identity_and_split(
    visible_claim_text: Any,
    binding: Mapping[str, Any],
    *,
    salt: int,
) -> tuple[str, str]:
    """Return the canonical identity digest and its deterministic proof split."""

    identity_digest = proof_identity_digest(visible_claim_text, binding)
    group_digest = proof_split_group_digest(binding)
    return identity_digest, proof_split_for_digest(group_digest, salt=salt)


def allocate_stratified_proof_splits(
    rows: Sequence[Mapping[str, Any]],
    *,
    minimum_split_count: int,
) -> tuple[int, dict[str, str]]:
    """Find the first salted identity assignment covering every profile/section.

    Each distinct proof identity is assigned once. The salt search is bounded,
    deterministic, and accepts only assignments where every observed
    ``(target_profile_id, section_id)`` stratum appears in both proof splits.
    """

    groups: set[str] = set()
    strata: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        group = str(row.get("proof_split_group_digest") or "")
        if len(group) != 64 or any(char not in "0123456789abcdef" for char in group):
            raise ProofSplitPolicyError("row proof_split_group_digest must be lowercase SHA-256")
        profile = str(row.get("target_profile_id") or "").strip()
        section = str(row.get("section_id") or "").strip()
        if not profile or not section:
            raise ProofSplitPolicyError(
                "target_profile_id and section_id are required for stratified proof split"
            )
        groups.add(group)
        strata[(profile, section)].add(group)
    impossible = sorted(stratum for stratum, values in strata.items() if len(values) < 2)
    if impossible:
        raise ProofSplitPolicyError(
            "proof split cannot cover both sides for single-identity strata: "
            + ", ".join(f"{profile}/{section}" for profile, section in impossible)
        )
    if len(groups) < 2 * minimum_split_count:
        raise ProofSplitPolicyError(
            f"{len(groups)} unique proof split groups cannot satisfy "
            f"{minimum_split_count} per split"
        )
    for salt in range(MAX_STRATIFIED_SALT + 1):
        assignments = {
            group: proof_split_for_digest(group, salt=salt)
            for group in sorted(groups)
        }
        counts = {
            split: sum(assigned == split for assigned in assignments.values())
            for split in PROOF_SPLITS
        }
        if any(counts[split] < minimum_split_count for split in PROOF_SPLITS):
            continue
        if any(
            {assignments[group] for group in stratum_identities}
            != set(PROOF_SPLITS)
            for stratum_identities in strata.values()
        ):
            continue
        return salt, assignments
    raise ProofSplitPolicyError(
        f"no valid stratified proof split found through salt {MAX_STRATIFIED_SALT}"
    )


__all__ = [
    "PROOF_SPLIT_POLICY_ID",
    "PROOF_IDENTITY_POLICY_ID",
    "PROOF_SPLIT_GROUP_POLICY_ID",
    "PROOF_SPLITS",
    "MAX_STRATIFIED_SALT",
    "ProofSplitPolicyError",
    "allocate_stratified_proof_splits",
    "canonical_proof_identity",
    "canonical_proof_split_group",
    "normalize_claim_text",
    "proof_identity_and_split",
    "proof_identity_digest",
    "proof_split_for_digest",
    "proof_split_group_digest",
]
