"""Graph is the SSOT for sender claims + metrics (no apps_lic-only numbers).

`given graph skills and metrics are now SSOT` — the standing sender corpus must
not author its own claim language or metrics. Every approved proof point that is
linked to apps_rg skills derives its `claim_text` from the graph, and every metric
token in that claim must trace to a linked skill's graph snippet. This gate fails
if any proof point smuggles in an apps_lic-only number (the historical failure was
`sp_platform_commercialization` asserting a "20% gross margin" that exists nowhere
in the graph).
"""

from __future__ import annotations

from apps_lic.engines.standing_sender_knowledge import load_standing_sender_corpus
from apps_lic.integrations.apps_rg_proof_bridge import (
    claim_metrics_are_graph_grounded,
    graph_claim_assets,
    load_apps_rg_proof_index,
    metric_tokens,
)


def _ssot_available() -> bool:
    index = load_apps_rg_proof_index()
    return bool(index.available and index.skills_by_id)


def test_every_graph_linked_claim_is_metric_grounded() -> None:
    """No proof point may carry a metric the graph does not back."""
    if not _ssot_available():  # shared apps_rg graph absent in this env
        return
    corpus = load_standing_sender_corpus()
    offenders: list[tuple[str, tuple[str, ...]]] = []
    for point in corpus.proof_points:
        if not point.apps_rg_skill_ids:
            continue
        grounded, ungrounded = claim_metrics_are_graph_grounded(
            point.claim_text, point.apps_rg_skill_ids
        )
        if not grounded:
            offenders.append((point.proof_id, ungrounded))
    assert not offenders, f"apps_lic-only metrics not in the graph SSOT: {offenders}"


def test_curated_metric_is_graph_phrase_not_yaml_authored() -> None:
    """Every metric a curated claim carries must be an approved graph metric phrase."""
    if not _ssot_available():
        return
    corpus = load_standing_sender_corpus()
    for point in corpus.proof_points:
        if not point.apps_rg_skill_ids:
            continue
        claim_metrics = metric_tokens(point.claim_text)
        if not claim_metrics:
            continue  # metric-free curated prose is trivially grounded
        approved = " ".join(graph_claim_assets(point.apps_rg_skill_ids)["approved_metric_phrases"]).lower()
        for token in claim_metrics:
            assert token in approved, (point.proof_id, token, point.claim_text)


def test_dropped_metrics_are_actually_absent() -> None:
    """Regression: the apps_lic-authored '$22M' / '20%' must not reappear."""
    if not _ssot_available():
        return
    corpus = load_standing_sender_corpus()
    commercialization = next(
        (p for p in corpus.proof_points if p.proof_id == "sp_platform_commercialization"),
        None,
    )
    assert commercialization is not None
    # Both fabricated metrics dropped; the graph-grounded $10M survives.
    assert "20%" not in commercialization.claim_text
    assert "$22M" not in commercialization.claim_text
    grounded, ungrounded = claim_metrics_are_graph_grounded(
        commercialization.claim_text, commercialization.apps_rg_skill_ids
    )
    assert grounded, ungrounded
    assert metric_tokens(commercialization.claim_text), "claim should still carry the $10M metric"


def test_ungrounded_metric_blocks_corpus_load() -> None:
    """The load-time gate fail-closes on an ungrounded curated metric."""
    if not _ssot_available():
        return
    from apps_lic.engines.standing_sender_knowledge import (
        _assert_claim_metrics_graph_grounded,
    )

    # '$22M' is not grounded for the GTM/revops skills — must raise.
    import pytest

    with pytest.raises(ValueError):
        _assert_claim_metrics_graph_grounded(
            "sp_platform_commercialization",
            "Generated $22M in IP-led revenue.",
            ("skill_partner_gtm_enablement", "skill_revops_multi_channel_gtm_alignment"),
        )
