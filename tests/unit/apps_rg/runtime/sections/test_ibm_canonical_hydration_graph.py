"""IBM canonical hydration when graph-skills authority emits fact_* claim ids."""
from __future__ import annotations

from apps_rg.runtime.sections.ibm_canonical_hydration import (
    align_ibm_narrative_claim_ledger_to_bul_ibm,
    bind_missing_ibm_narrative_theme_citations,
    decompose_ibm_narrative_claim_ledger_by_clause,
    should_hydrate_ibm_bullets_from_canonical,
)
from apps_rg.runtime.validators.ibm_narrative_x2 import (
    check_ibm_narrative_claim_ledger_clause_decomposition,
    ibm_narrative_material_fact_ids_for_sentence,
)

# Live failing run postW4_20260610_1716 (e2e_aig_verify, ibm_narrative_20260610_213740):
# the only X2 fail keeping ibm_narrative from X3_ALLOW was
# x2_ibm_narrative_claim_ledger_clause_decomposition with
# reason=loose_source_fact_id_union — ledger row 0 cited 3 roots [001, 002, 004].
LIVE_POSTW4_CLAUSE_1 = (
    "At IBM led enterprise-scale cloud modernization, data governance, lineage and "
    "observability programs for regulated financial institutions"
)
LIVE_POSTW4_CLAUSE_2 = (
    "establishing platform discipline, alliance execution and governed delivery culture "
    "that anchored analytics and risk infrastructure across complex financial services "
    "engagements"
)
LIVE_POSTW4_NARRATIVE = f"{LIVE_POSTW4_CLAUSE_1}, {LIVE_POSTW4_CLAUSE_2}."
LIVE_POSTW4_FAILING_LEDGER = [
    {
        "claim_text": LIVE_POSTW4_CLAUSE_1,
        "source_fact_ids": ["bul_ibm_001", "bul_ibm_002", "bul_ibm_004"],
    },
    {
        "claim_text": LIVE_POSTW4_CLAUSE_2,
        "source_fact_ids": ["bul_ibm_001", "bul_ibm_005"],
    },
]
ALL_IBM_POOL = {"bul_ibm_001", "bul_ibm_002", "bul_ibm_003", "bul_ibm_004", "bul_ibm_005"}


def test_gate_still_rejects_live_postw4_three_root_row() -> None:
    """Gate unchanged: the live failing shape (3-root row 0) must keep failing."""
    ok, detail = check_ibm_narrative_claim_ledger_clause_decomposition(
        LIVE_POSTW4_NARRATIVE,
        [dict(r) for r in LIVE_POSTW4_FAILING_LEDGER],
    )
    assert ok is False
    assert detail["reason"] == "loose_source_fact_id_union"
    assert detail["violations"][0]["roots"] == ["bul_ibm_001", "bul_ibm_002", "bul_ibm_004"]


def test_decompose_live_postw4_shape_covers_all_themes_max_two_grounded_roots() -> None:
    """Coverage-aware decomposition: live narrative yields 2 rows, each <=2 grounded roots,

    with the row union covering every detected theme (001/002/004/005) — the
    assignment the naive themes[:2] + append-to-row-0 chain could not produce.
    """
    parsed = {
        "narrative_sentence": LIVE_POSTW4_NARRATIVE,
        "claim_ledger": [dict(r) for r in LIVE_POSTW4_FAILING_LEDGER],
    }
    decompose_ibm_narrative_claim_ledger_by_clause(
        parsed,
        narrative_sentence=LIVE_POSTW4_NARRATIVE,
        allowed_fact_ids=set(ALL_IBM_POOL),
    )
    ledger = parsed["claim_ledger"]
    assert len(ledger) == 2
    union: set[str] = set()
    for row in ledger:
        roots = {str(s) for s in row["source_fact_ids"] if str(s).startswith("bul_ibm_")}
        assert 1 <= len(roots) <= 2
        # Theme-grounded attribution: every root cited by a row is a theme its own
        # claim_text expresses (no fabricated or padded roots).
        assert roots <= ibm_narrative_material_fact_ids_for_sentence(str(row["claim_text"]))
        union |= roots
    assert union == {"bul_ibm_001", "bul_ibm_002", "bul_ibm_004", "bul_ibm_005"}


def test_decompose_then_binder_passes_clause_decomposition_gate_live_shape() -> None:
    """Full deterministic chain on the live failing shape now passes the gate;

    the binder finds nothing missing (coverage already complete) and is a no-op.
    """
    parsed = {
        "narrative_sentence": LIVE_POSTW4_NARRATIVE,
        "claim_ledger": [dict(r) for r in LIVE_POSTW4_FAILING_LEDGER],
    }
    decompose_ibm_narrative_claim_ledger_by_clause(
        parsed,
        narrative_sentence=LIVE_POSTW4_NARRATIVE,
        allowed_fact_ids=set(ALL_IBM_POOL),
    )
    bound = bind_missing_ibm_narrative_theme_citations(
        parsed, allowed_fact_ids=set(ALL_IBM_POOL)
    )
    assert bound == []
    ok, detail = check_ibm_narrative_claim_ledger_clause_decomposition(
        LIVE_POSTW4_NARRATIVE, parsed["claim_ledger"]
    )
    assert ok is True, detail
    # Theme coverage holds too: union covers every detected sentence theme.
    cited = {
        str(s)
        for row in parsed["claim_ledger"]
        for s in row["source_fact_ids"]
    }
    assert ibm_narrative_material_fact_ids_for_sentence(LIVE_POSTW4_NARRATIVE) <= cited


def test_binder_places_missing_theme_on_grounded_row_with_capacity() -> None:
    parsed = {
        "narrative_sentence": LIVE_POSTW4_NARRATIVE,
        "claim_ledger": [
            {"claim_text": LIVE_POSTW4_CLAUSE_1, "source_fact_ids": ["bul_ibm_002"]},
            {
                "claim_text": LIVE_POSTW4_CLAUSE_2,
                "source_fact_ids": ["bul_ibm_001", "bul_ibm_005"],
            },
        ],
    }
    bound = bind_missing_ibm_narrative_theme_citations(
        parsed, allowed_fact_ids=set(ALL_IBM_POOL)
    )
    # bul_ibm_004 (lineage/observability) is grounded in clause 1 which has capacity.
    assert bound == ["bul_ibm_004"]
    assert parsed["claim_ledger"][0]["source_fact_ids"] == ["bul_ibm_002", "bul_ibm_004"]
    ok, detail = check_ibm_narrative_claim_ledger_clause_decomposition(
        LIVE_POSTW4_NARRATIVE, parsed["claim_ledger"]
    )
    assert ok is True, detail
    ops = [e.get("operation") for e in parsed["change_log"] if isinstance(e, dict)]
    assert "bind_detected_theme_citations" in ops


def test_binder_fail_open_when_grounded_rows_are_full() -> None:
    """No grounded row with capacity: theme stays uncited; never a third root on a row."""
    ledger = [
        {
            "claim_text": LIVE_POSTW4_CLAUSE_1,
            "source_fact_ids": ["bul_ibm_001", "bul_ibm_002"],
        },
        {
            "claim_text": LIVE_POSTW4_CLAUSE_2,
            "source_fact_ids": ["bul_ibm_001", "bul_ibm_005"],
        },
    ]
    parsed = {
        "narrative_sentence": LIVE_POSTW4_NARRATIVE,
        "claim_ledger": [dict(r) for r in ledger],
    }
    bound = bind_missing_ibm_narrative_theme_citations(
        parsed, allowed_fact_ids=set(ALL_IBM_POOL)
    )
    assert bound == []
    assert parsed["claim_ledger"] == ledger
    ok, _detail = check_ibm_narrative_claim_ledger_clause_decomposition(
        LIVE_POSTW4_NARRATIVE, parsed["claim_ledger"]
    )
    assert ok is True  # clause gate holds; theme-coverage gate fails honestly elsewhere


def test_binder_never_binds_to_ungrounded_row() -> None:
    """A row with capacity whose claim_text does not express the theme is skipped."""
    parsed = {
        "narrative_sentence": LIVE_POSTW4_NARRATIVE,
        "claim_ledger": [
            # Clause 2 text does not contain lineage/observability triggers.
            {"claim_text": LIVE_POSTW4_CLAUSE_2, "source_fact_ids": ["bul_ibm_005"]},
        ],
    }
    bound = bind_missing_ibm_narrative_theme_citations(
        parsed, allowed_fact_ids={"bul_ibm_004", "bul_ibm_005"}
    )
    assert "bul_ibm_004" not in bound
    assert parsed["claim_ledger"][0]["source_fact_ids"] == ["bul_ibm_005"]


def test_should_hydrate_graph_pool_when_ledger_lacks_bul_ibm() -> None:
    parsed = {
        "bullets": [
            {
                "bullet_id": "bul_ibm_001",
                "bullet_text": "Wrong metrics only 20%.",
                "source_fact_ids": ["fact_partnerships_gtm_002"],
            }
        ],
        "claim_ledger": [
            {
                "claim_text": "Wrong metrics only 20%.",
                "source_fact_ids": ["fact_partnerships_gtm_002"],
            }
        ],
    }
    runtime_payload = {
        "proof_pool_metadata": {"claim_evidence_source_type": "augmented_skills_graph"},
        "selected_fact_plan": {"facts": [{"fact_id": "fact_partnerships_gtm_002"}]},
    }
    assert should_hydrate_ibm_bullets_from_canonical(runtime_payload, parsed) is False


def test_align_narrative_ledger_replaces_fact_ids_with_bul_ibm() -> None:
    sentence = (
        "At IBM, led enterprise-scale cloud, data, lineage and observability initiatives "
        "for regulated financial services."
    )
    parsed = {
        "narrative_sentence": sentence,
        "claim_ledger": [
            {
                "claim_text": sentence.rstrip("."),
                "source_fact_ids": ["fact_consulting_001", "fact_governance_003"],
            }
        ],
    }
    themes = ibm_narrative_material_fact_ids_for_sentence(sentence)
    align_ibm_narrative_claim_ledger_to_bul_ibm(
        parsed,
        narrative_sentence=sentence,
        allowed_fact_ids={"bul_ibm_001", "bul_ibm_004", "fact_consulting_001"},
    )
    src = parsed["claim_ledger"][0]["source_fact_ids"]
    assert all(str(s).startswith("bul_ibm_") for s in src)
    assert themes.issubset(set(src)) or src


def test_decompose_overflow_row_covers_third_theme_in_one_clause() -> None:
    """Live flap 4x (attempt4/postRungs 2026-06-11): a clause grounding 3 themes was
    structurally uncoverable with one row per clause (max 2 bul_ibm roots per row, theme
    citable only by a row whose own clause expresses it). The decomposer now emits an
    overflow row (same clause text, <=2 roots) so the union covers every grounded theme;
    the clause-decomposition gate (roots-per-row cap) and theme-coverage gate both pass.
    """
    from apps_rg.runtime.validators.ibm_narrative_x2 import (
        check_ibm_narrative_claim_ledger_clause_decomposition,
    )

    sentence = (
        "At IBM, led enterprise-scale cloud modernization, data lineage and observability "
        "programs for regulated financial services institutions, establishing governed "
        "delivery discipline and hyperscaler alliance execution that expanded platform "
        "reach across complex enterprise portfolios."
    )
    allowed = {f"bul_ibm_00{i}" for i in range(1, 6)}
    parsed = {"narrative_sentence": sentence, "claim_ledger": [], "change_log": []}
    decompose_ibm_narrative_claim_ledger_by_clause(
        parsed, narrative_sentence=sentence, allowed_fact_ids=allowed
    )
    rows = parsed["claim_ledger"]
    themes = ibm_narrative_material_fact_ids_for_sentence(sentence)
    union = {fid for r in rows for fid in r.get("source_fact_ids", [])}
    assert themes <= union, f"uncovered: {sorted(themes - union)}"
    assert all(len(r.get("source_fact_ids", [])) <= 2 for r in rows)
    ok, detail = check_ibm_narrative_claim_ledger_clause_decomposition(sentence, rows)
    assert ok, detail
