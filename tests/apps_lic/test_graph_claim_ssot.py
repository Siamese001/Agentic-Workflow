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

from apps_lic.engines.sender_proof_graph import (
    STATUS_DRAFT_METRICS_GROUNDED,
    STATUS_DRAFT_METRICS_NOT_APPLICABLE,
    STATUS_DRAFT_METRICS_UNGROUNDED,
    STATUS_PROOF_GRAPH_READY,
    SenderProofGraphPacket,
    validate_draft_metrics_against_packet,
)
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


# --- W1: deterministic draft-level metric-grounding gate ---------------------
# The corpus-load gate above grounds the CURATED proof-point claim_text. These
# cover the L2-GENERATED draft: a number the model introduces that the graph does
# not back must be blocked, while benign text and the SSOT-absent path stay safe.


def _proof_point(proof_id: str):
    corpus = load_standing_sender_corpus()
    return next((p for p in corpus.proof_points if p.proof_id == proof_id), None)


def _packet_with(points) -> SenderProofGraphPacket:
    """Minimal packet carrying just selected_proof_points.

    validate_draft_metrics_against_packet only reads selected_proof_points (and
    each point's apps_rg_skill_ids); the rest are inert defaults.
    """
    return SenderProofGraphPacket(
        status=STATUS_PROOF_GRAPH_READY,
        ready=True,
        recipient_class="EXECUTIVE",
        message_type="trigger_based_insight",
        proof_packet_id="sha256:test_packet",
        selected_proof_points=tuple(points),
        permission_decisions=(),
        omitted_claims=(),
        blocked_claims=(),
        proof_to_target_relevance_score={},
        source_lineage={},
        graph_links={},
        claim_permission_map_hash="",
        unsupported_claim_policy="block",
        corpus_hash="",
        source_snapshot_ids=(),
        reason_codes=(),
    )


def test_draft_metric_gate_not_applicable_without_graph_skills() -> None:
    """No graph-linked skills in the packet -> fail-soft NOT_APPLICABLE (never blocks)."""
    result = validate_draft_metrics_against_packet(
        "We delivered $999M and improved throughput 40%.",
        packet=_packet_with(()),
    )
    assert not result.applicable
    assert result.status == STATUS_DRAFT_METRICS_NOT_APPLICABLE
    assert result.grounded  # NA must not block


def test_draft_metric_gate_passes_graph_grounded_metric() -> None:
    """A generated draft whose only metric is graph-approved ($10M) grounds."""
    if not _ssot_available():
        return
    point = _proof_point("sp_platform_commercialization")
    if point is None or not getattr(point, "apps_rg_skill_ids", ()):
        return  # precondition: the point must carry graph-linked skills
    result = validate_draft_metrics_against_packet(
        "I built the GTM motion that delivered $10M in net-new revenue.",
        packet=_packet_with((point,)),
    )
    assert result.applicable
    assert result.status == STATUS_DRAFT_METRICS_GROUNDED
    assert result.grounded


def test_draft_metric_gate_blocks_generator_fabricated_metric() -> None:
    """A generated draft that smuggles an ungrounded number ($22M) is blocked."""
    if not _ssot_available():
        return
    point = _proof_point("sp_platform_commercialization")
    if point is None or not getattr(point, "apps_rg_skill_ids", ()):
        return
    result = validate_draft_metrics_against_packet(
        "I personally generated $22M in IP-led revenue last year.",
        packet=_packet_with((point,)),
    )
    assert result.applicable
    assert result.status == STATUS_DRAFT_METRICS_UNGROUNDED
    assert not result.grounded
    assert result.ungrounded_metric_tokens  # names the offending token(s)
