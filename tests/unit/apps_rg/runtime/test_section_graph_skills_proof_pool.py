from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime import section_graph_skills_proof_pool as proof_pool
from apps_rg.runtime.sections.graph_evidence_contract import SECTION_KEYS


@pytest.mark.parametrize("section_id", SECTION_KEYS)
def test_assert_graph_skills_section_accepts_every_declared_section(section_id: str) -> None:
    proof_pool.assert_graph_skills_section(section_id)


def test_assert_graph_skills_section_rejects_unknown_section() -> None:
    with pytest.raises(ValueError, match="not a graph-skills authority section"):
        proof_pool.assert_graph_skills_section("not_a_section")


def test_company_hint_plan_filters_high_confidence_matches_and_sanitizes_private_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = {
        "candidate_facts": [
            {
                "candidate_fact_id": "fact_ibm_001",
                "company": "IBM",
                "confidence": "HIGH",
                "claim_text": "IBM hybrid-cloud GTM operating model.",
                "claim_eligible_medium": True,
                "metric_values": ["20%"],
                "source_trace_archive_relpaths": ["archive/ibm.json"],
            },
            {
                "candidate_fact_id": "fact_ibm_002",
                "company_lane": "ibm",
                "confidence": "LOW",
                "claim_text": "Low confidence IBM row must not be selected.",
            },
            {
                "candidate_fact_id": "fact_unify_001",
                "company": "Unify",
                "confidence": "HIGH",
                "claim_text": "Wrong company row must not be selected.",
            },
            "not a row",
        ]
    }

    def _stamp_with_private_key(plan: dict) -> tuple[dict, list[str], set[str]]:
        stamped = {**plan, "_private_debug": "drop-me"}
        ordered = list(stamped["required_fact_ids"])
        return stamped, ordered, set(ordered)

    monkeypatch.setattr(
        "apps_rg.runtime.proof_pool_resolver._stamp_unify_canonical_bullet_ids",
        _stamp_with_private_key,
    )

    result = proof_pool._graph_substrate_company_hint_plan(
        ledger,
        section_id="ibm_narrative",
        hints=("ibm",),
        limit=3,
    )

    assert result is not None
    plan, ordered, allowed = result
    assert "_private_debug" not in plan
    assert plan["selection_method"] == "augmented_skills_graph_ibm_narrative_company_hint"
    assert plan["required_fact_ids"] == ["fact_ibm_001"]
    assert ordered == ["fact_ibm_001"]
    assert allowed == {"fact_ibm_001"}
    assert [f["fact_id"] for f in plan["facts"]] == ["fact_ibm_001"]
    assert plan["facts"][0]["claim_text"] == "IBM hybrid-cloud GTM operating model."


def test_company_hint_plan_rejects_unify_bullets() -> None:
    with pytest.raises(ValueError, match="company_hint allocation is forbidden for unify_bullets"):
        proof_pool._graph_substrate_company_hint_plan(
            {"candidate_facts": []},
            section_id="unify_bullets",
            hints=("unify",),
            limit=6,
        )


def test_role_episode_bundle_plan_fails_closed_for_missing_and_malformed_bundle(
    tmp_path: Path,
) -> None:
    assert (
        proof_pool._role_episode_bundle_plan(
            section_id="ey_bullets",
            repo_root=tmp_path,
            limit=1,
        )
        is None
    )

    bundle_dir = tmp_path / "apps_rg" / "fact_inventory"
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "ey_role_episode_bundles.json").write_text("{not-json", encoding="utf-8")

    assert (
        proof_pool._role_episode_bundle_plan(
            section_id="ey_bullets",
            repo_root=tmp_path,
            limit=1,
        )
        is None
    )


def test_allocate_section_rejects_competencies_before_graph_resolution() -> None:
    with pytest.raises(
        ValueError,
        match="competencies uses track-weighted graph expansion, not role slice allocation",
    ):
        proof_pool.allocate_section_facts_from_graph_substrate(
            ledger={},
            taxonomy={},
            section_id="competencies",
            target_company="AIG",
            target_role="VP",
            jd_text="Lead AI transformation.",
            briefing_text="AIG briefing.",
            ledger_path=Path("ledger.json"),
            taxonomy_path=Path("taxonomy.json"),
        )


def test_allocate_section_uses_role_episode_bundle_before_graph_selector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    def _bundle_plan(*, section_id: str, repo_root: Path, limit: int):
        calls.append({"section_id": section_id, "repo_root": repo_root, "limit": limit})
        plan = {
            "section_id": section_id,
            "selection_method": "augmented_skills_graph_ey_bullets_role_episode_bundle",
            "facts": [{"fact_id": "reb_ey_test", "claim_text": "EY role episode."}],
            "required_fact_ids": ["reb_ey_test"],
            "role_episode_bundle_fallback": True,
        }
        return plan, ["reb_ey_test"], {"reb_ey_test"}

    monkeypatch.setattr(proof_pool, "_role_episode_bundle_plan", _bundle_plan)

    plan, ordered, allowed = proof_pool.allocate_section_facts_from_graph_substrate(
        ledger={},
        taxonomy={},
        section_id="ey_bullets",
        target_company="AIG",
        target_role="VP",
        jd_text="Lead AI transformation.",
        briefing_text="AIG briefing.",
        ledger_path=Path("ledger.json"),
        taxonomy_path=Path("taxonomy.json"),
    )

    assert calls == [
        {
            "section_id": "ey_bullets",
            "repo_root": Path(proof_pool.__file__).resolve().parents[2],
            "limit": 5,
        }
    ]
    assert plan["role_episode_bundle_fallback"] is True
    assert plan["required_fact_ids"] == ["reb_ey_test"]
    assert ordered == ["reb_ey_test"]
    assert allowed == {"reb_ey_test"}
