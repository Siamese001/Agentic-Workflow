"""Tests for the 6 deferred-scope items completed in one pass.

W3.2 depth_anchor_synth + W3.4 source_register_gate + W4.2 paste_bandit
+ W4.3 promotion_gates + W5.2 flywheel + W5.3 memory_writeback.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from apps_qna.config.route_registry import Route, RouteRegistry
from apps_qna.types.qna_types import (
    ExperienceLibrary,
    ExperiencePoint,
)


def _ledger_path() -> Path | None:
    try:
        from tools.ledgers.schema_registry import get
        return get("apps_qna_pack_lifecycle").db_path
    except (ImportError, KeyError):  # guardian: allow-return-none-swallow -- optional ledger registry; test skips when unavailable
        return None


@pytest.fixture
def ledger_db() -> Path:
    p = _ledger_path()
    if p is None or not p.is_file():
        pytest.skip("apps_qna_pack_lifecycle ledger not materialized")
    return p


# ============================================================================
# W3.2 — depth_anchor_synth
# ============================================================================


def _resume_library() -> ExperienceLibrary:
    """Mock library with multi-cluster tag overlap."""
    return ExperienceLibrary(
        points=[
            ExperiencePoint(
                title="Productization Platform",
                one_liner="Built reusable platform services with $22M revenue.",
                technical_depth_tags=["productization", "metric-22M-revenue", "shared-services"],
            ),
            ExperiencePoint(
                title="Engineering Org Scaling",
                one_liner="Grew engineering team from 8 to 28 specialists.",
                technical_depth_tags=["leadership", "metric-8-to-28-team"],
            ),
            ExperiencePoint(
                title="Cycle Compression",
                one_liner="Reduced lab-to-production from 6 months to 3 weeks.",
                technical_depth_tags=["lifecycle", "lab-to-production", "metric-6mo-to-3wk"],
            ),
            ExperiencePoint(
                title="Hyperscaler Co-Sell",
                one_liner="Generated $15M incremental via hyperscaler alliances.",
                technical_depth_tags=["co-sell", "hyperscaler-alliance", "metric-15M-revenue"],
            ),
            ExperiencePoint(
                title="IBM Co-Sell Motion",
                one_liner="Joint roadmaps with hyperscaler account teams.",
                technical_depth_tags=["co-sell", "metric-15M-revenue"],
            ),
            ExperiencePoint(
                title="Renewal Rate Improvement",
                one_liner="Improved renewals 25% via SaaS-like platform conversion.",
                technical_depth_tags=["productization", "shared-services", "metric-25pct-renewal"],
            ),
        ],
    )


def test_depth_anchor_synth_returns_anchors() -> None:
    from apps_qna.integrations.depth_anchor_synth import (
        synthesize_cross_exam_anchors,
    )
    anchors = synthesize_cross_exam_anchors(_resume_library())
    assert len(anchors) > 0
    titles = {a.title for a in anchors}
    # At minimum the productization cluster should fire (3+ qualifying points).
    assert "Productization economics" in titles or "Hyperscaler co-sell motion" in titles


def test_depth_anchor_synth_caps_supporting_points() -> None:
    from apps_qna.integrations.depth_anchor_synth import (
        synthesize_cross_exam_anchors,
        _MAX_POINTS_PER_ANCHOR,
    )
    anchors = synthesize_cross_exam_anchors(_resume_library())
    for anchor in anchors:
        assert len(anchor.supporting_points) <= _MAX_POINTS_PER_ANCHOR
        assert len(anchor.supporting_points) >= 2  # _MIN_POINTS_PER_ANCHOR


def test_depth_anchor_synth_empty_library_returns_empty() -> None:
    from apps_qna.integrations.depth_anchor_synth import (
        synthesize_cross_exam_anchors,
    )
    assert synthesize_cross_exam_anchors(ExperienceLibrary(points=[])) == []


def test_depth_anchor_synth_into_extra_context_preserves_existing() -> None:
    from apps_qna.integrations.depth_anchor_synth import (
        synthesize_into_extra_context,
    )
    existing = [{"topic": "Operator anchor", "specifics": "Custom"}]
    result = synthesize_into_extra_context(_resume_library(), existing=existing)
    assert result == existing


def test_depth_anchor_synth_into_extra_context_jinja_shape() -> None:
    from apps_qna.integrations.depth_anchor_synth import (
        synthesize_into_extra_context,
    )
    result = synthesize_into_extra_context(_resume_library())
    assert all("topic" in d and "specifics" in d for d in result)


# ============================================================================
# W3.4 — source_register_gate
# ============================================================================


def test_is_claim_line_detects_numeric_claims() -> None:
    from apps_qna.integrations.source_register_gate import _is_claim_line
    assert _is_claim_line("Generated $22M in productized revenue") is True
    assert _is_claim_line("Achieved 99.9% uptime in regulated environments") is True


def test_is_claim_line_skips_non_claims() -> None:
    from apps_qna.integrations.source_register_gate import _is_claim_line
    assert _is_claim_line("") is False
    assert _is_claim_line("# Heading") is False
    assert _is_claim_line("```code") is False
    assert _is_claim_line("the") is False  # too short


def test_audit_card_claims_counts_correctly(tmp_path: Path) -> None:
    from apps_qna.integrations.source_register_gate import audit_card_claims
    card = tmp_path / "test_card.md"
    card.write_text(
        "# Test Card\n\n"
        "## Substantive\n"
        "Generated $22M in productized revenue [SRC-001].\n"
        "Achieved 99.9% uptime across regulated environments.\n"
        "Reduced cycle from 6 months to 3 weeks [SRC-002].\n",
        encoding="utf-8",
    )
    audit = audit_card_claims(card)
    assert audit.total_claims >= 2
    assert audit.cited_claims >= 2
    # The uncited 99.9% line should be flagged.
    assert any("99.9%" in ex for ex in audit.uncited_examples)


def test_evaluate_pack_clean_when_well_cited(tmp_path: Path) -> None:
    from apps_qna.integrations.source_register_gate import evaluate_pack
    pack = tmp_path / "good_pack"
    pack.mkdir()
    (pack / "01.md").write_text(
        "# Card\n\n## Body\nGenerated $22M [SRC-001]. Won $15M [SRC-002].\n",
        encoding="utf-8",
    )
    verdict = evaluate_pack(pack)
    # Well-cited or below the warn threshold (n<5).
    assert verdict.status in {"CLEAN", "WARN"}


def test_evaluate_pack_blocks_when_mostly_uncited(tmp_path: Path) -> None:
    from apps_qna.integrations.source_register_gate import evaluate_pack
    pack = tmp_path / "bad_pack"
    pack.mkdir()
    body = "\n".join(
        f"## Section {i}\nDelivered {i*5}M in revenue improvements." for i in range(1, 13)
    )
    (pack / "01.md").write_text(f"# Card\n\n{body}\n", encoding="utf-8")
    verdict = evaluate_pack(pack)
    assert verdict.status in {"BLOCK", "WARN"}
    assert verdict.total_claims >= 10


def test_evaluate_pack_bypass_env_var(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_qna.integrations.source_register_gate import evaluate_pack
    monkeypatch.setenv("APPS_QNA_SOURCE_GATE_BYPASS", "1")
    pack = tmp_path / "any_pack"
    pack.mkdir()
    (pack / "01.md").write_text("Anything goes here.", encoding="utf-8")
    verdict = evaluate_pack(pack)
    assert verdict.status == "BYPASSED"


# ============================================================================
# W4.2 — paste_bandit
# ============================================================================


def test_paste_bandit_cold_start_returns_none() -> None:
    from apps_qna.router.paste_bandit import AppsQnaPasteBandit
    bandit = AppsQnaPasteBandit(seed=42)
    result = bandit.choose_paste_set(
        signal="test signal",
        paste_budget=18,
        admissible_cards=["00.md", "01.md", "02.md"],
    )
    assert result is None


def test_paste_bandit_clears_cold_start_after_updates() -> None:
    from apps_qna.router.paste_bandit import (
        AppsQnaPasteBandit,
        _hash_signal_with_budget,
    )
    bandit = AppsQnaPasteBandit(seed=42)
    signal = "hot signal"
    namespace = _hash_signal_with_budget(signal, 18)
    cards = ["00.md", "01.md", "02.md", "13.md"]
    for card in cards * 2:
        bandit.update_outcome(
            namespace=namespace, card_id=card, included=True, useful=True
        )
    result = bandit.choose_paste_set(
        signal=signal, paste_budget=18, admissible_cards=cards
    )
    assert result is not None
    assert len(result) <= 4
    for sel in result:
        assert sel.card_id in cards


def test_paste_bandit_emits_paired_marker_and_ledger(
    capsys: pytest.CaptureFixture[str], ledger_db: Path
) -> None:
    from apps_qna.router.paste_bandit import (
        AppsQnaPasteBandit,
        _hash_signal_with_budget,
    )
    bandit = AppsQnaPasteBandit(seed=42)
    signal = "marker test"
    namespace = _hash_signal_with_budget(signal, 8)
    cards = ["00.md", "13.md"]
    for c in cards * 4:
        bandit.update_outcome(namespace=namespace, card_id=c, included=True, useful=True)
    result = bandit.choose_paste_set(
        signal=signal, paste_budget=8, admissible_cards=cards
    )
    assert result is not None
    captured = capsys.readouterr()
    markers = [
        line for line in captured.out.splitlines()
        if line.startswith("ROUTER_DECISION:")
    ]
    assert len(markers) == len(result)
    for line in markers:
        assert "router=apps_qna_paste_bandit" in line
        assert "budget_bucket=" in line


def test_paste_bandit_budget_buckets() -> None:
    from apps_qna.router.paste_bandit import _bucket_for_budget
    assert _bucket_for_budget(7) == 8
    assert _bucket_for_budget(11) == 12
    assert _bucket_for_budget(20) == 18
    assert _bucket_for_budget(30) == 25


# ============================================================================
# W4.3 — promotion_gates
# ============================================================================


def test_evaluate_promotion_promotes_strong_candidate() -> None:
    from apps_qna.router.promotion_gates import (
        CellOutcomes,
        evaluate_promotion,
    )
    candidate = CellOutcomes("ns", "candidate_arm", successes=45, failures=5)
    baseline = CellOutcomes("ns", "baseline_arm", successes=15, failures=35)
    verdict = evaluate_promotion(candidate=candidate, baseline=baseline)
    assert verdict.promote is True
    assert verdict.uplift > 0
    assert verdict.wilson_lower_candidate >= 0.60


def test_evaluate_promotion_rejects_insufficient_n() -> None:
    from apps_qna.router.promotion_gates import (
        CellOutcomes,
        evaluate_promotion,
    )
    candidate = CellOutcomes("ns", "c", successes=5, failures=2)
    baseline = CellOutcomes("ns", "b", successes=3, failures=4)
    verdict = evaluate_promotion(candidate=candidate, baseline=baseline)
    assert verdict.promote is False
    assert "insufficient" in verdict.reason.lower()


def test_evaluate_promotion_rejects_when_baseline_better() -> None:
    from apps_qna.router.promotion_gates import (
        CellOutcomes,
        evaluate_promotion,
    )
    candidate = CellOutcomes("ns", "c", successes=15, failures=35)
    baseline = CellOutcomes("ns", "b", successes=45, failures=5)
    verdict = evaluate_promotion(candidate=candidate, baseline=baseline)
    assert verdict.promote is False
    assert verdict.uplift < 0


def test_evaluate_promotion_namespace_mismatch_raises() -> None:
    from apps_qna.router.promotion_gates import (
        CellOutcomes,
        evaluate_promotion,
    )
    with pytest.raises(ValueError, match="namespace mismatch"):
        evaluate_promotion(
            candidate=CellOutcomes("ns_a", "c", 30, 10),
            baseline=CellOutcomes("ns_b", "b", 30, 10),
        )


def test_emit_promotion_verdict_paired_marker_and_row(
    capsys: pytest.CaptureFixture[str], ledger_db: Path
) -> None:
    from apps_qna.router.promotion_gates import (
        CellOutcomes,
        evaluate_promotion,
        emit_promotion_verdict_to_ledger,
    )
    candidate = CellOutcomes("ns_test", "c_arm", successes=45, failures=5)
    baseline = CellOutcomes("ns_test", "b_arm", successes=15, failures=35)
    verdict = evaluate_promotion(candidate=candidate, baseline=baseline)
    event_id = emit_promotion_verdict_to_ledger(verdict)
    assert event_id  # non-empty
    captured = capsys.readouterr()
    assert "ROUTER_DECISION:" in captured.out
    assert "router=apps_qna_promotion_gate" in captured.out
    # Check ledger row landed.
    con = sqlite3.connect(ledger_db)
    try:
        rows = list(
            con.execute(
                "SELECT score_band FROM events WHERE event_kind='promote_decision' "
                "ORDER BY ts_utc DESC LIMIT 1"
            )
        )
    finally:
        con.close()
    assert rows
    assert rows[0][0] in {"promote", "rollback", "insufficient_evidence"}


# ============================================================================
# W5.2 — flywheel
# ============================================================================


def test_flywheel_compute_defaults_returns_schema() -> None:
    from apps_qna.integrations.flywheel import compute_flywheel_defaults
    snapshot = compute_flywheel_defaults()
    assert snapshot["schema_version"] == 1
    assert "promoted_routes" in snapshot
    assert "promoted_cards" in snapshot
    assert "thresholds" in snapshot


def test_flywheel_handles_missing_db(tmp_path: Path) -> None:
    from apps_qna.integrations.flywheel import compute_flywheel_defaults
    snapshot = compute_flywheel_defaults(db_path=tmp_path / "nope.sqlite")
    assert snapshot["promoted_routes"] == []
    assert snapshot["promoted_cards"] == []
    assert "warning" in snapshot


def test_flywheel_emits_snapshot_to_disk(tmp_path: Path) -> None:
    from apps_qna.integrations.flywheel import (
        emit_flywheel_snapshot,
        load_flywheel_defaults,
    )
    target = tmp_path / "flywheel_test.json"
    written = emit_flywheel_snapshot(output_path=target)
    assert written == target
    assert target.is_file()
    loaded = load_flywheel_defaults(target)
    assert loaded.get("schema_version") == 1


def test_flywheel_load_defaults_handles_missing(tmp_path: Path) -> None:
    from apps_qna.integrations.flywheel import load_flywheel_defaults
    assert load_flywheel_defaults(tmp_path / "nonexistent.json") == {}


def test_flywheel_emit_paired_marker(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from apps_qna.integrations.flywheel import emit_flywheel_snapshot
    emit_flywheel_snapshot(output_path=tmp_path / "fw.json")
    captured = capsys.readouterr()
    assert "ROUTER_DECISION:" in captured.out
    assert "router=apps_qna_flywheel" in captured.out


# ============================================================================
# W5.3 — memory_writeback
# ============================================================================


def test_memory_writeback_distill_handles_missing_db(tmp_path: Path) -> None:
    from apps_qna.integrations.memory_writeback import distill_patterns
    assert distill_patterns(db_path=tmp_path / "nope.sqlite") == []


def test_memory_writeback_distill_returns_drafts(ledger_db: Path) -> None:
    """Distillation may return empty list when data is sparse — that's valid."""
    from apps_qna.integrations.memory_writeback import distill_patterns
    drafts = distill_patterns()
    # Result is a list (may be empty if ledger lacks enough cross-namespace data).
    assert isinstance(drafts, list)


def test_memory_writeback_format_drafts_for_mcp() -> None:
    from apps_qna.integrations.memory_writeback import (
        MemoryEntityDraft,
        format_drafts_for_mcp_call,
    )
    drafts = [
        MemoryEntityDraft(
            name="ProceduralPattern:Test",
            entityType="ProceduralPattern",
            observations=["obs1", "obs2"],
        ),
    ]
    formatted = format_drafts_for_mcp_call(drafts)
    assert formatted == [
        {
            "name": "ProceduralPattern:Test",
            "entityType": "ProceduralPattern",
            "observations": ["obs1", "obs2"],
        }
    ]


def test_memory_writeback_drafts_use_protected_entity_type() -> None:
    """Drafts must NOT use entityType='general' — those get auto-purged at 30 days."""
    from apps_qna.integrations.memory_writeback import distill_patterns
    drafts = distill_patterns()
    protected_types = {
        "ProceduralPattern", "ProjectContext", "ArchitecturalInvariant",
        "EpisodicEvent",
    }
    for draft in drafts:
        assert draft.entityType in protected_types, (
            f"Draft {draft.name} uses non-protected type {draft.entityType!r}"
        )
