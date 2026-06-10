from __future__ import annotations

from collections import Counter, defaultdict

from scripts.apps_lic.run_post_w7_live_12_archetype_matrix import (
    FULL_E2E_GATE_ROLE,
    FULL_E2E_GATE_SHAPE,
    LIVE_ARCHETYPE_CONTACTS,
    REQUESTED_SLOT_BY_PROFILE,
    _build_summary,
)


def test_main_full_e2e_gate_is_four_per_company_archetype_matrix() -> None:
    assert FULL_E2E_GATE_ROLE == "main_full_e2e_gate"
    assert FULL_E2E_GATE_SHAPE == "4_per_company_12_archetype_matrix"
    assert len(LIVE_ARCHETYPE_CONTACTS) == 12

    counts_by_company: dict[str, Counter[str]] = defaultdict(Counter)
    for contact in LIVE_ARCHETYPE_CONTACTS:
        slot = REQUESTED_SLOT_BY_PROFILE[contact.profile_id]
        counts_by_company[contact.company_key][slot] += 1

    assert set(counts_by_company) == {"aig", "citi", "neo4j"}
    assert all(
        counts == {"Recruiter": 1, "Senior TA": 1, "C-Level": 1, "Executive": 1}
        for counts in counts_by_company.values()
    )


def test_main_full_e2e_summary_contract_names_primary_gate() -> None:
    summary = _build_summary((), generated_at="2026-06-09T00:00:00+00:00")

    assert summary["gate_role"] == "main_full_e2e_gate"
    assert summary["gate_shape"] == "4_per_company_12_archetype_matrix"
    assert (
        summary["acceptance_contract"]
        == "all_12_company_archetype_rows_clear_with_zero_quality_violations"
    )
