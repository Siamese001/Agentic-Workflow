from pathlib import Path

import yaml

from apps_lic.engines.standing_sender_knowledge import (
    DEFAULT_STANDING_SENDER_CORPUS_PATH,
    STATUS_CLAIMS_BLOCKED,
    STATUS_CLAIMS_PASS,
    STATUS_MISSING,
    STATUS_READY,
    STATUS_SELECTION_READY,
    build_c03_sender_proof_packet,
    check_standing_sender_corpus_readiness,
    load_standing_sender_corpus,
    select_sender_proof_points,
    validate_sender_claims_before_l2,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_w1_sender_namespace_and_collection_are_seeded() -> None:
    corpus = load_standing_sender_corpus()

    assert corpus.namespace == "apps_lic_sender_facts"
    assert corpus.collection_name == "apps_lic_sender_facts"
    assert corpus.sender_profile["name"] == "Amit Ayer"
    assert corpus.no_send_policy["auto_send_allowed"] is False
    assert corpus.approved_proof_points


def test_w1_readiness_passes_for_seeded_standing_corpus() -> None:
    readiness = check_standing_sender_corpus_readiness()

    assert readiness.ready is True
    assert readiness.status == STATUS_READY
    assert readiness.error_code == ""
    assert readiness.namespace == "apps_lic_sender_facts"
    assert readiness.collection_name == "apps_lic_sender_facts"
    assert readiness.corpus_hash.startswith("sha256:")


def test_w1_missing_sender_corpus_returns_clear_readiness_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing_standing_sender_knowledge.yaml"

    readiness = check_standing_sender_corpus_readiness(missing_path)

    assert readiness.ready is False
    assert readiness.status == STATUS_MISSING
    assert readiness.error_code == STATUS_MISSING
    assert "Missing standing sender corpus" in readiness.details


def test_c03_selects_only_approved_sender_proof_points() -> None:
    selection = select_sender_proof_points(
        recipient_class="RECRUITER",
        message_type="general_intro",
        max_points=3,
    )

    assert selection.status == STATUS_SELECTION_READY
    assert selection.readiness.ready is True
    assert 1 <= len(selection.selected_proof_points) <= 3
    assert selection.claim_permission_map_hash.startswith("sha256:")
    assert all(point.permission == "allow" for point in selection.selected_proof_points)
    assert "sp_unapproved_placeholder" not in {
        point.proof_id for point in selection.selected_proof_points
    }


def test_c03_selection_carries_graph_links_and_source_lineage() -> None:
    packet = build_c03_sender_proof_packet(
        recipient_class="CEO",
        message_type="trigger_based_insight",
        target_tags=("agentic-platform", "governance"),
    )

    assert packet["status"] == STATUS_SELECTION_READY
    assert packet["proof_ids"]
    assert packet["proof_packet_id"].startswith("sha256:")
    for proof_id in packet["proof_ids"]:
        assert packet["source_lineage"][proof_id]
        assert packet["graph_links"][proof_id]


def test_unapproved_sender_claim_is_blocked_before_l2() -> None:
    result = validate_sender_claims_before_l2(
        ["sp_agentic_platform", "sp_not_in_corpus"],
        recipient_class="RECRUITER",
        message_type="general_intro",
    )

    assert result.status == STATUS_CLAIMS_BLOCKED
    assert result.allowed_claim_ids == ("sp_agentic_platform",)
    assert any(
        item["proof_id"] == "sp_not_in_corpus"
        and item["reason"] == "unapproved_sender_claim"
        for item in result.blocked_claims
    )


def test_blocked_permission_claim_is_blocked_before_l2() -> None:
    result = validate_sender_claims_before_l2(
        ["sp_unapproved_placeholder"],
        recipient_class="RECRUITER",
        message_type="general_intro",
    )

    assert result.status == STATUS_CLAIMS_BLOCKED
    assert result.allowed_claim_ids == ()
    assert result.blocked_claims[0]["reason"] == "claim_permission_not_allow"


def test_scope_disallowed_claim_is_blocked_before_l2() -> None:
    result = validate_sender_claims_before_l2(
        ["sp_platform_commercialization"],
        recipient_class="RECRUITER",
        message_type="general_intro",
    )

    assert result.status == STATUS_CLAIMS_BLOCKED
    assert result.allowed_claim_ids == ()
    assert result.blocked_claims[0]["reason"] == "not_allowed_for_message_scope"


def test_allowed_claims_pass_before_l2() -> None:
    result = validate_sender_claims_before_l2(
        ["sp_agentic_platform"],
        recipient_class="RECRUITER",
        message_type="general_intro",
    )

    assert result.status == STATUS_CLAIMS_PASS
    assert result.allowed_claim_ids == ("sp_agentic_platform",)
    assert result.blocked_claims == ()


def test_w1_corpus_file_contains_required_sections() -> None:
    with DEFAULT_STANDING_SENDER_CORPUS_PATH.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle)

    for key in (
        "sender_profile",
        "approved_sender_proof_points",
        "resume_project_facts",
        "writing_preferences",
        "no_send_policy",
        "claim_permission_map",
        "graph_skill_links",
    ):
        assert document[key]


def test_w1_engine_is_decision_only_no_provider_or_vector_writes() -> None:
    source = (
        REPO_ROOT / "apps_lic" / "engines" / "standing_sender_knowledge.py"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "openai",
        "anthropic",
        "chromadb",
        "SovereignChromaClient",
        "L4_state",
        "sqlite3.connect",
        "write_text(",
    ):
        assert forbidden not in source
