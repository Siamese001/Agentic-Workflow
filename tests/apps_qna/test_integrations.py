"""Wave 8 tests — apps_qna intake integrations.

Covers:
- from_jd: markdown JD parsing
- from_apps_research: fixture-driven brief + source_register loading
- from_research_brief: text-mode parser (PDF path is exercised end-to-end via
  a tiny MD fixture; pdfplumber/pypdf is not invoked in unit tests)
- from_apps_rg: YAML loader + empty fallback
- from_apps_exec: bullets extracted from a fixture brief
- wizard: non-interactive end-to-end composition
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from apps_qna.integrations.from_apps_exec import load_executive_close_patterns
from apps_qna.integrations.from_apps_research import (
    _claims_from_register,
    load_apps_research,
)
from apps_qna.integrations.from_apps_shared import (
    load_competency_areas,
    load_executive_summary,
    load_master_resume,
)
from apps_qna.integrations.from_apps_rg import (
    empty_library,
    load_experience_yaml,
)
from apps_qna.integrations.from_jd import (
    _extract_keywords,
    load_markdown_jd,
    parse_markdown_jd,
)
from apps_qna.integrations.from_research_brief import (
    parse_research_brief_text,
)
from apps_qna.integrations.wizard import (
    WizardOptions,
    run_wizard,
    write_interview_yaml,
)


# ----------------- from_jd -----------------


def test_parse_markdown_jd_with_h2_sections() -> None:
    text = """Lead paragraph describing the team.

## Mandate

Build governed agentic systems for the decisioning practice.

- Design L0..L6 layering
- Build guardian agents for safe action

## Requirements

- 10+ years engineering experience
- Governed AI exposure
"""
    jd = parse_markdown_jd(text)
    assert len(jd.sections) == 3  # Overview + Mandate + Requirements
    assert jd.sections[0].heading == "Overview"
    assert jd.sections[1].heading == "Mandate"
    assert jd.sections[2].heading == "Requirements"
    # Bullets feed extracted_keywords. The lead noun phrase is taken up to
    # the first comma or period — keywords are hints, not lossless extraction.
    assert "Build guardian agents for safe action" in jd.sections[1].extracted_keywords


def test_parse_markdown_jd_no_h2() -> None:
    jd = parse_markdown_jd("Just a single paragraph of JD text.")
    assert len(jd.sections) == 1
    assert jd.sections[0].heading == "Overview"


def test_load_markdown_jd_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_markdown_jd(tmp_path / "nope.md")


def test_extract_keywords_picks_bullet_leads() -> None:
    body = "- Governed agents over hand-rolled tools, audited end to end.\n- ROI-oriented productization."
    kws = _extract_keywords(body)
    assert kws[0] == "Governed agents over hand-rolled tools"
    assert kws[1] == "ROI-oriented productization"


# ----------------- from_apps_research -----------------


def test_load_apps_research_from_fixture(tmp_path: Path) -> None:
    """Synthesize a tiny research_dir and verify the adapter loads it."""
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    (research_dir / "research_brief_abc12345.md").write_text(
        """# Research Artifact — synthetic

## Executive Summary

This is the company brief paragraph.

## Key Findings

- Finding 1: governance is platform-layer
- Finding 2: determinism is contract-layer

## Strategic Implications

- Trend A: enterprise auditability
- Trend B: governed actions
""",
        encoding="utf-8",
    )
    (research_dir / "source_register_abc12345.json").write_text(
        json.dumps(
            [
                {
                    "claim_type": "direct_evidence",
                    "section_id": "exec",
                    "source_id": "SRC-001",
                    "summary": "Six-layer architecture.",
                    "title": "Architecture",
                    "url": "urn:repo:docs/",
                },
                {
                    "claim_type": "analyst_inference",
                    "section_id": "implications",
                    "source_id": "SRC-002",
                    "summary": "Buyers increasingly require auditability.",
                    "title": "Buyer trends",
                    "url": "",
                },
            ]
        ),
        encoding="utf-8",
    )

    research = load_apps_research(trace_id="abc12345", research_dir=research_dir)
    assert research.company_brief and "company brief paragraph" in research.company_brief
    assert "Finding 1: governance is platform-layer" in research.role_areas_of_focus
    assert "Trend A: enterprise auditability" in research.industry_trends
    assert len(research.source_register) == 2
    assert research.source_register[0].source_id == "SRC-001"
    assert research.source_register[1].claim_type == "analyst_inference"


def test_load_apps_research_picks_latest_when_trace_omitted(tmp_path: Path) -> None:
    research_dir = tmp_path / "r"
    research_dir.mkdir()
    for trace in ("aaaa1111", "bbbb2222"):
        (research_dir / f"research_brief_{trace}.md").write_text(
            f"# {trace}\n\n## Executive Summary\nTrace {trace}\n", encoding="utf-8"
        )
    # Modify mtime so bbbb2222 is newest.
    import os, time
    older = research_dir / "research_brief_aaaa1111.md"
    os.utime(older, (time.time() - 100, time.time() - 100))

    research = load_apps_research(research_dir=research_dir)
    assert research.company_brief and "bbbb2222" in research.company_brief


def test_load_apps_research_missing_dir_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_apps_research(research_dir=tmp_path / "not-there")


def test_claims_from_register_normalizes_unknown_claim_type() -> None:
    rows = [{"summary": "Some claim", "claim_type": "garbage", "source_id": "SRC-1"}]
    claims = _claims_from_register(rows)
    assert claims[0].claim_type == "analyst_inference"


# ----------------- from_research_brief (text-mode) -----------------


def test_parse_research_brief_with_known_sections() -> None:
    text = """# AI Executive Interview Briefing — Test Co

## Executive Summary

Test Co builds decisioning platforms. The role is VP Decisioning Engineering.

## Company Overview

- Founded 2010
- HQ in NYC

## Role Areas of Focus

- Governed agent platform
- Measurement modernization

## Industry Trends

- Agentic governance is becoming a board-level concern
- Privacy regulations are tightening

## Interviewer Lens: Drew Clements

VP Engineering with deep platform background.

## Glossary

- MMM: Marketing Mix Modeling
- DGS: Distributed Global Services

## Source Register

- [SRC-001] Test Co company brief
- [SRC-002] Recent industry whitepaper
"""
    research = parse_research_brief_text(text)
    assert research.company_brief and "decisioning platforms" in research.company_brief
    assert "Governed agent platform" in research.role_areas_of_focus
    assert any("agentic governance" in t.lower() for t in research.industry_trends)
    assert "Drew Clements" in research.interviewer_lenses
    assert any(g.term == "MMM" for g in research.glossary_entries)
    assert any(c.source_id == "SRC-001" for c in research.source_register)


def test_parse_research_brief_preserves_unmatched_sections() -> None:
    text = """## Random Section

Some content that does not match any heading classifier.
"""
    research = parse_research_brief_text(text)
    # Unmatched content lives in company_brief so nothing is dropped.
    assert research.company_brief
    assert "Random Section" in research.company_brief


# ----------------- from_apps_rg -----------------


def test_load_experience_yaml_minimal(tmp_path: Path) -> None:
    yaml_path = tmp_path / "exp.yaml"
    yaml_path.write_text(
        yaml.safe_dump(
            {
                "points": [
                    {
                        "title": "Shipped governed agent platform",
                        "one_liner": "Led L0..L6 platform build",
                        "technical_depth_tags": ["agentic", "governance"],
                    }
                ],
                "star_bank": {"stories": []},
                "rca_bank": [],
            }
        ),
        encoding="utf-8",
    )
    library = load_experience_yaml(yaml_path)
    assert len(library.points) == 1
    assert library.points[0].title == "Shipped governed agent platform"


def test_empty_library_is_valid() -> None:
    lib = empty_library()
    assert lib.points == []
    assert lib.star_bank.stories == []
    assert lib.rca_bank == []


def test_load_experience_yaml_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_experience_yaml(tmp_path / "nope.yaml")


# ----------------- from_apps_exec -----------------


def test_load_executive_close_patterns(tmp_path: Path) -> None:
    brief = tmp_path / "exec_brief_test.md"
    brief.write_text(
        """# Executive Brief

## Thesis

- Governed agents reduce client-trust risk by 60%
- ROI accrues in quarter 2 via planner adoption
- [SRC-001] Citation that should be filtered
""",
        encoding="utf-8",
    )
    patterns = load_executive_close_patterns(brief_path=brief)
    assert any("Governed agents" in p for p in patterns)
    assert any("ROI accrues" in p for p in patterns)
    # Citation lines starting with "[SRC..." must be filtered out.
    assert not any(p.startswith("[SRC") for p in patterns)


# ----------------- from_apps_shared (master resume) -----------------


def _write_resume_fixture(path: Path, *, structured: bool) -> None:
    """Write a minimal resume JSON in either legacy or SVP shape."""
    if structured:
        bullet = {
            "label": "Platform Architecture",
            "text": "Designed an agentic AI platform combining routing and governance.",
            "tags": ["agentic-platform", "governance"],
        }
    else:
        bullet = (
            "Designed an agentic AI platform combining routing and governance."
        )
    payload = {
        "schema_version": "test",
        "owner": {"name": "Test Person"},
        "professional_experience": [
            {
                "company": "Test Co",
                "title": "Lead Architect",
                "bullet_pool": [bullet],
            }
        ],
        "executive_summary": "Engineering executive with platform experience.",
        "engineering_and_platform_competencies": [
            {"area": "Agentic AI Platforms", "skills": "Multi-agent orchestration"},
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_master_resume_structured_svp_shape(tmp_path: Path) -> None:
    fixture = tmp_path / "master_resume_svp.json"
    _write_resume_fixture(fixture, structured=True)
    library = load_master_resume(fixture)
    assert len(library.points) == 1
    point = library.points[0]
    assert point.title == "Platform Architecture"
    assert "agentic-platform" in point.technical_depth_tags


def test_load_master_resume_legacy_string_bullets(tmp_path: Path) -> None:
    fixture = tmp_path / "master_resume.json"
    _write_resume_fixture(fixture, structured=False)
    library = load_master_resume(fixture)
    assert len(library.points) == 1
    # Legacy string-bullet fallback synthesizes a title from the lead clause
    assert "Designed an agentic AI platform" in library.points[0].title
    assert library.points[0].technical_depth_tags == []


def test_load_master_resume_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_master_resume(tmp_path / "nope.json")


def test_load_competency_areas_svp(tmp_path: Path) -> None:
    fixture = tmp_path / "r.json"
    _write_resume_fixture(fixture, structured=True)
    areas = load_competency_areas(fixture)
    assert len(areas) == 1
    assert areas[0]["area"] == "Agentic AI Platforms"


def test_load_executive_summary(tmp_path: Path) -> None:
    fixture = tmp_path / "r.json"
    _write_resume_fixture(fixture, structured=True)
    summary = load_executive_summary(fixture)
    assert summary and "platform experience" in summary


def test_load_master_resume_real_svp_fixture_in_repo() -> None:
    """The committed master_resume_svp.json is IDENTITY-ONLY → no experience facts.

    Standing rule: the base resume carries no claims/bullets/metrics; experience
    facts come from the apps_rg graph. So loading it yields an empty library.
    TODO(apps_qna→graph): repoint load_master_resume at the graph-derived
    ExperienceLibrary (tracked as a follow-up) — then this asserts >0 again.
    """
    library = load_master_resume(Path("apps_shared/data/master_resume_svp.json"))
    assert library.points == []  # identity-only resume has no bullet_pool


def test_load_master_resume_real_legacy_fixture_in_repo() -> None:
    """The identity-only master_resume.json must load cleanly with no fact points."""
    path = Path("apps_shared/data/master_resume.json")
    if not path.is_file():
        pytest.skip("master_resume.json absent")
    library = load_master_resume(path)
    # Identity-only: no bullet_pool → no experience points (facts come from graph).
    assert library.points == []


# ----------------- wizard end-to-end -----------------


def test_wizard_non_interactive_minimal(tmp_path: Path) -> None:
    """Wizard composes a valid Interview from CLI flags only — no prompts.

    Use --no-master-resume so we get an empty library (deterministic).
    """
    out_yaml = tmp_path / "interview.yaml"
    options = WizardOptions(
        slug="test-co",
        company_name="Test Co",
        role_title="VP Decisioning",
        role_mandate="Build governed agent platform.",
        interviewer_names=["Jane Doe", "John Smith"],
        use_master_resume=False,
        non_interactive=True,
        output_yaml=out_yaml,
    )
    interview, extra = run_wizard(options, interactive=False)
    assert interview.slug == "test-co"
    assert interview.company.name == "Test Co"
    assert len(interview.interviewers) == 2
    assert interview.research is not None  # default empty ResearchInputs
    assert interview.experience.points == []  # empty library (opt-out)
    write_interview_yaml(interview, extra, out_yaml)
    assert out_yaml.is_file()
    loaded = yaml.safe_load(out_yaml.read_text(encoding="utf-8"))
    assert loaded["slug"] == "test-co"
    assert loaded["extra_context"]["candidate_first_name"] == "Candidate"


def test_wizard_with_jd_and_research(tmp_path: Path) -> None:
    """Full pipeline: JD + apps_research adapter -> Interview YAML buildable."""
    # Synthesize a JD
    jd_path = tmp_path / "jd.md"
    jd_path.write_text(
        """## Mandate

Build governed agentic systems for the decisioning practice.

## Requirements

- 10+ years engineering experience
""",
        encoding="utf-8",
    )
    # Synthesize an apps_research dir
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    (research_dir / "research_brief_xyz98765.md").write_text(
        "# Brief\n\n## Executive Summary\n\nTest Co is a decisioning company.\n",
        encoding="utf-8",
    )
    (research_dir / "source_register_xyz98765.json").write_text(
        "[]", encoding="utf-8"
    )

    options = WizardOptions(
        slug="end-to-end",
        company_name="Test Co",
        role_title="VP Decisioning",
        role_mandate="Build agent platform.",
        interviewer_names=["Jane Doe"],
        jd_path=jd_path,
        research_trace_id="xyz98765",
        research_dir=research_dir,
        non_interactive=True,
        output_yaml=tmp_path / "out.yaml",
    )
    interview, extra = run_wizard(options, interactive=False)
    assert len(interview.jd.sections) == 2
    assert interview.research and "Test Co is a decisioning" in (
        interview.research.company_brief or ""
    )


def test_wizard_uses_master_resume_by_default(tmp_path: Path) -> None:
    """When no --experience flag is given, the wizard auto-loads the master resume."""
    options = WizardOptions(
        slug="auto-resume",
        company_name="Test Co",
        role_title="VP X",
        role_mandate="x",
        interviewer_names=["P"],
        # use_master_resume defaults to True — should auto-load apps_shared/data/master_resume.json
        non_interactive=True,
        output_yaml=tmp_path / "out.yaml",
    )
    interview, _ = run_wizard(options, interactive=False)
    # The committed master resume is IDENTITY-ONLY (no bullet_pool) → no experience
    # facts (those come from the apps_rg graph). Wizard still auto-loads without error.
    # TODO(apps_qna→graph): repoint to the graph-derived ExperienceLibrary.
    assert interview.experience.points == []


def test_wizard_master_resume_explicit_path(tmp_path: Path) -> None:
    """An explicit --master-resume path overrides the default search."""
    fixture = tmp_path / "custom_resume.json"
    _write_resume_fixture(fixture, structured=True)
    options = WizardOptions(
        slug="custom-resume",
        company_name="Test Co",
        role_title="VP X",
        role_mandate="x",
        interviewer_names=["P"],
        master_resume_json=fixture,
        non_interactive=True,
        output_yaml=tmp_path / "out.yaml",
    )
    interview, _ = run_wizard(options, interactive=False)
    assert len(interview.experience.points) == 1
    assert interview.experience.points[0].title == "Platform Architecture"


def test_wizard_non_interactive_requires_company() -> None:
    options = WizardOptions(non_interactive=True)
    with pytest.raises(ValueError, match="company_name"):
        run_wizard(options, interactive=False)


def test_wizard_non_interactive_requires_interviewer() -> None:
    options = WizardOptions(
        company_name="Test", role_title="VP", role_mandate="x", non_interactive=True
    )
    with pytest.raises(ValueError, match="interviewer"):
        run_wizard(options, interactive=False)


def test_wizard_built_yaml_is_buildable_end_to_end(tmp_path: Path) -> None:
    """The composed YAML must round-trip through the actual builder."""
    from apps_qna.builder.card_pack_builder import CardPackBuilder
    from apps_qna.config.build_config import QnaBuildConfig
    from apps_qna.types.qna_types import Interview

    out_yaml = tmp_path / "interview.yaml"
    options = WizardOptions(
        slug="round-trip",
        company_name="Round Trip Co",
        role_title="VP X",
        role_mandate="Mandate.",
        interviewer_names=["Test Person"],
        non_interactive=True,
        output_yaml=out_yaml,
    )
    interview, extra = run_wizard(options, interactive=False)
    write_interview_yaml(interview, extra, out_yaml)

    # Re-load the YAML and run the actual builder.
    loaded = yaml.safe_load(out_yaml.read_text(encoding="utf-8"))
    extra_loaded = loaded.pop("extra_context", {})
    output_dir = tmp_path / "pack"
    loaded["build_metadata"]["output_dir"] = str(output_dir)
    interview2 = Interview.model_validate(loaded)
    builder = CardPackBuilder(config=QnaBuildConfig(force=True))
    manifest = builder.build(interview2, output_dir, extra_loaded)
    assert len(manifest.cards) == 22
    assert manifest.routes_covered  # all 9 routes still covered
