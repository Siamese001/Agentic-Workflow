"""Config/profile tests: targeting branch vs default company-brief branch.

Proves the apps_rg targeting route does NOT require the JSON CompanyBrief
shape or citation anchors, while the default route still produces the
structured JSON brief.
"""

from __future__ import annotations

from apps_research.prompt_assembly.apps_rg_targeting_brief import (
    apps_rg_targeting_brief_enabled,
)


def test_targeting_branch_enabled_by_output_format() -> None:
    assert apps_rg_targeting_brief_enabled(
        jd_context={"output_format": "apps_rg_targeting_brief_v1"}
    )
    assert apps_rg_targeting_brief_enabled(
        jd_context={"synthesis_template": "apps_rg_targeting_brief_synthesis_v1"}
    )


def test_default_branch_is_json_company_brief() -> None:
    # No targeting signal → default JSON CompanyBrief route.
    assert not apps_rg_targeting_brief_enabled(jd_context={})
    assert not apps_rg_targeting_brief_enabled(jd_context=None)
    assert not apps_rg_targeting_brief_enabled(
        jd_context={"company_name": "Acme", "job_title": "SVP"}
    )


def test_env_override_forces_targeting_branch(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RESEARCH_APPS_RG_TARGETING_BRIEF", "1")
    assert apps_rg_targeting_brief_enabled(jd_context={})
    monkeypatch.setenv("APPS_RESEARCH_APPS_RG_TARGETING_BRIEF", "0")
    assert not apps_rg_targeting_brief_enabled(
        jd_context={"output_format": "apps_rg_targeting_brief_v1"}
    )


def test_targeting_contract_has_no_citation_requirement() -> None:
    # The targeting contract validator REJECTS citations/links — the opposite
    # of the default JSON brief which carries citation anchors. This asserts
    # the two routes have distinct, separable contracts.
    from apps_research.types.apps_rg_targeting_brief_contract import (
        validate_targeting_brief_text,
    )

    cited = "=== STRATEGIC MANDATE ===\n- revenue grew (source: 10-K)\n"
    v = validate_targeting_brief_text(cited)
    assert not v.valid
    assert "citation_present" in v.violations
