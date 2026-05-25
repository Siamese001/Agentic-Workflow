"""W1: Authority separation invariant tests (NEG-1 started)."""
from __future__ import annotations

from apps_rg.runtime.graph_selection_rationale import reject_jd_only_skill_admission


def test_neg1_graph_skill_with_fact_links_admitted() -> None:
    row = reject_jd_only_skill_admission(
        skill_id="skill_platform_engineering",
        jd_text="IT strategy and AI platforms",
        fact_id_links=["fact_engineering_platform_001"],
    )
    assert row["admitted"] is True


def test_neg1_jd_only_id_pattern_rejected_even_with_links() -> None:
    row = reject_jd_only_skill_admission(
        skill_id="jd_keyword_skill",
        jd_text="IT strategy",
        fact_id_links=["fact_x"],
    )
    assert row["admitted"] is False
