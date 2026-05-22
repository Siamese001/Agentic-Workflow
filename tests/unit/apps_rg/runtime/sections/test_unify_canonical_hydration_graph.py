"""Unify canonical hydration when graph-skills authority drifts metrics."""
from __future__ import annotations

from apps_rg.runtime.sections.unify_canonical_hydration import (
    should_hydrate_unify_bullets_from_canonical,
    unify_core_metrics_missing,
)


def test_should_hydrate_when_metrics_missing() -> None:
    parsed = {
        "bullets": [
            {
                "bullet_id": "bul_unify_006",
                "bullet_text": "Led platform without locked metrics.",
                "rewrite_intensity": "MODERATE",
                "source_fact_ids": ["fact_platform_001"],
            }
        ],
    }
    runtime_payload = {
        "proof_pool_metadata": {"claim_evidence_source_type": "augmented_skills_graph"},
        "selected_fact_plan": {"facts": [{"fact_id": "fact_platform_001"}]},
    }
    assert unify_core_metrics_missing(parsed) is True
    assert should_hydrate_unify_bullets_from_canonical(runtime_payload, parsed) is False
