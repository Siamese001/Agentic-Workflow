"""Artifact diet policy for apps_rg runtime proof manifests (Wave 11).

The diet is intentionally non-destructive: section lanes may still write verbose
diagnostics for local debugging, while manifests expose a compact proof-oriented
link set for downstream packaging.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ArtifactDietRow:
    filename: str
    diet_class: str
    compact_link: bool
    reason: str


PROOF_CORE_ARTIFACTS: frozenset[str] = frozenset(
    {
        "run_manifest.json",
        "l2_output.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "section_input_usage_ledger.json",
        "canonical_claim_ledger_v2.json",
        "text_claim_coverage.json",
        "selected_fact_plan.json",
        "runtime_exhaust_bundle.json",
        "section_runtime_proof_bundle.json",
        "artifact_inventory.json",
        "stage_sequence.json",
    }
)

PROOF_OPTIONAL_ARTIFACTS: frozenset[str] = frozenset(
    {
        "compiled_prompt_artifact.json",
        "provider_request.json",
        "x1d_llm_judge_outputs.json",
        "l6_shadow_eval_package.json",
        "l6_shadow_learning.json",
        "l6_future_run_proposals.json",
        "real_l2_generation_result.json",
        "c0_metrics.json",
    }
)

DIAGNOSTIC_HEAVY_ARTIFACTS: frozenset[str] = frozenset(
    {
        "compiled_prompt.txt",
        "command_output.txt",
        "provider_response.json",
        "parsed_output.json",
        "prompt_selection_trace.json",
    }
)


def classify_artifact(filename: str) -> ArtifactDietRow:
    """Classify a runtime proof artifact by compact-manifest eligibility."""
    name = str(filename or "").strip().replace("\\", "/")
    base = name.rsplit("/", 1)[-1]
    if name in PROOF_CORE_ARTIFACTS or base in PROOF_CORE_ARTIFACTS:
        return ArtifactDietRow(
            filename=filename,
            diet_class="proof_core",
            compact_link=True,
            reason="required_or_canonical_proof_surface",
        )
    if name in PROOF_OPTIONAL_ARTIFACTS or base in PROOF_OPTIONAL_ARTIFACTS:
        return ArtifactDietRow(
            filename=filename,
            diet_class="proof_optional",
            compact_link=True,
            reason="compact_proof_or_shadow_receipt",
        )
    if name in DIAGNOSTIC_HEAVY_ARTIFACTS or base in DIAGNOSTIC_HEAVY_ARTIFACTS:
        return ArtifactDietRow(
            filename=filename,
            diet_class="diagnostic_heavy",
            compact_link=False,
            reason="verbose_debug_surface_retained_on_disk_not_published_compact",
        )
    return ArtifactDietRow(
        filename=filename,
        diet_class="diagnostic_other",
        compact_link=False,
        reason="unclassified_artifact_retained_on_disk_not_published_compact",
    )


def compact_artifact_links(artifact_links: Mapping[str, str]) -> dict[str, str]:
    """Return proof-oriented artifact links for compact manifest consumers."""
    return {
        name: ref
        for name, ref in artifact_links.items()
        if classify_artifact(name).compact_link
    }


def build_artifact_diet_receipt(artifact_links: Mapping[str, str]) -> dict[str, object]:
    """Summarize the compact-vs-diagnostic split for a run manifest."""
    classes: dict[str, list[str]] = {}
    for name in sorted(artifact_links):
        row = classify_artifact(name)
        classes.setdefault(row.diet_class, []).append(name)
    compact = compact_artifact_links(artifact_links)
    diagnostic_count = sum(
        len(v)
        for k, v in classes.items()
        if k.startswith("diagnostic")
    )
    return {
        "schema_version": "apps_rg_artifact_diet_v1",
        "mode": "manifest_compact_non_destructive",
        "legacy_artifact_links_preserved": True,
        "compact_link_count": len(compact),
        "legacy_link_count": len(artifact_links),
        "diagnostic_retained_on_disk_count": diagnostic_count,
        "classes": classes,
    }


__all__ = [
    "ArtifactDietRow",
    "DIAGNOSTIC_HEAVY_ARTIFACTS",
    "PROOF_CORE_ARTIFACTS",
    "PROOF_OPTIONAL_ARTIFACTS",
    "build_artifact_diet_receipt",
    "classify_artifact",
    "compact_artifact_links",
]
