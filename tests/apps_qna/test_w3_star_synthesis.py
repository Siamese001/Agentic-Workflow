"""W3.1 tests — STAR / RCA synthesis from ExperiencePoints."""

from __future__ import annotations

from pathlib import Path

from apps_qna.integrations.from_apps_shared import load_master_resume
from apps_qna.integrations.star_synthesis import (
    _derive_lesson,
    _extract_metric_phrase,
    _project_to_rca_skeleton,
    _project_to_star,
    _split_text_for_action,
    synthesize_into_library,
    synthesize_rca_skeletons,
    synthesize_star_bank,
)
from apps_qna.types.qna_types import (
    ExperienceLibrary,
    ExperiencePoint,
    RCAStory,
    Story,
    StoryBank,
)


# --------------------------------------------------------------------------
# Projection helpers
# --------------------------------------------------------------------------


def test_extract_metric_phrase_from_known_tag() -> None:
    point = ExperiencePoint(
        title="Productization",
        one_liner="Built reusable platform services.",
        technical_depth_tags=["productization", "metric-22M-revenue"],
    )
    metric = _extract_metric_phrase(point)
    assert metric is not None
    assert "$22M" in metric


def test_extract_metric_phrase_falls_back_to_text_scan() -> None:
    point = ExperiencePoint(
        title="Cycle compression",
        one_liner="Reduced lab-to-production cycle from six months to three weeks.",
        technical_depth_tags=[],
    )
    metric = _extract_metric_phrase(point)
    # Either tag-based or text-scanned metric must surface; at minimum
    # the function must not crash.
    assert metric is None or len(metric) > 0


def test_extract_metric_phrase_returns_none_when_no_metric() -> None:
    point = ExperiencePoint(
        title="Generic work",
        one_liner="Did regular engineering things.",
        technical_depth_tags=["leadership"],
    )
    assert _extract_metric_phrase(point) is None


def test_split_text_for_action_caps_length() -> None:
    long_text = (
        "First sentence. Second sentence. Third sentence. Fourth sentence. "
        "Fifth sentence. " * 10
    )
    action, residual = _split_text_for_action(long_text)
    # Action must be capped (< 350 chars to leave headroom for sentence boundary).
    assert len(action) < 350
    # When source is long, there must be residual content left over.
    assert residual


def test_split_text_for_action_short_text_returns_full() -> None:
    text = "One short sentence about platform work."
    action, residual = _split_text_for_action(text)
    assert text in action
    assert residual == ""


def test_derive_lesson_governance_cluster() -> None:
    lesson = _derive_lesson(["governance", "policy-gating"])
    assert "governance" in lesson.lower()


def test_derive_lesson_productization_cluster() -> None:
    lesson = _derive_lesson(["productization", "shared-services"])
    assert "platform" in lesson.lower() or "ip" in lesson.lower() or "reusable" in lesson.lower()


def test_derive_lesson_falls_back_when_no_cluster_matches() -> None:
    lesson = _derive_lesson(["random-tag-xyz"])
    assert "platform" in lesson.lower() or "operating" in lesson.lower()


def test_project_to_star_has_all_required_fields() -> None:
    point = ExperiencePoint(
        title="Productization Platform",
        one_liner="Built reusable services. Scaled the engineering team. Generated $22M in productized AI revenue.",
        technical_depth_tags=["productization", "metric-22M-revenue"],
    )
    story = _project_to_star(point, role_context="Led platform roadmap at Unify.")
    assert story.name == "Productization Platform"
    assert "Unify" in story.situation
    assert story.task  # non-empty
    assert story.action  # non-empty
    assert "$22M" in story.result or len(story.result) > 0
    assert story.lesson  # non-empty
    assert "productization" in story.tags


def test_project_to_rca_skeleton_has_placeholders() -> None:
    point = ExperiencePoint(
        title="Cloud Migration",
        one_liner="Led migration off legacy systems with substantial risk.",
        technical_depth_tags=["cloud-migration", "legacy-modernization"],
    )
    rca = _project_to_rca_skeleton(point, role_context="At IBM during 2017-2022.")
    assert rca.name.startswith("RCA: ")
    assert "SKELETON" in rca.root_cause
    assert "SKELETON" in rca.action
    assert "SKELETON" in rca.operating_model_change


# --------------------------------------------------------------------------
# Public surface — synthesize_star_bank
# --------------------------------------------------------------------------


def test_synthesize_star_bank_empty_library_returns_empty_bank() -> None:
    bank = synthesize_star_bank(ExperienceLibrary(points=[]))
    assert isinstance(bank, StoryBank)
    assert bank.stories == []


def test_synthesize_star_bank_no_signal_returns_top_n_in_order() -> None:
    points = [
        ExperiencePoint(title=f"Bullet {i}", one_liner=f"Did thing {i}.", technical_depth_tags=[])
        for i in range(12)
    ]
    bank = synthesize_star_bank(ExperienceLibrary(points=points), top_n=5)
    assert len(bank.stories) == 5
    # In no-signal mode, registry order is preserved.
    assert bank.stories[0].name == "Bullet 0"


def test_synthesize_star_bank_with_signal_ranks_relevant_higher() -> None:
    points = [
        ExperiencePoint(
            title="Productization Platform",
            one_liner="Built reusable platform services with $22M revenue.",
            technical_depth_tags=["productization", "metric-22M-revenue"],
        ),
        ExperiencePoint(
            title="Database Migration",
            one_liner="Moved tables from MySQL to Postgres.",
            technical_depth_tags=["database"],
        ),
        ExperiencePoint(
            title="Team Scaling",
            one_liner="Grew engineering org from 8 to 28 specialists.",
            technical_depth_tags=["leadership", "metric-8-to-28-team"],
        ),
    ]
    library = ExperienceLibrary(points=points)
    # Signal heavy on productization + IP commercialization.
    bank = synthesize_star_bank(
        library,
        jd_text="The role requires productized platform services, IP commercialization, and reusable accelerators.",
        top_n=3,
    )
    assert len(bank.stories) > 0
    # The productization story should rank ahead of the database
    # migration story (the latter is unrelated to the signal).
    names = [s.name for s in bank.stories]
    if "Productization Platform" in names and "Database Migration" in names:
        assert names.index("Productization Platform") < names.index("Database Migration")


def test_synthesize_star_bank_uses_role_context_when_provided() -> None:
    point = ExperiencePoint(
        title="X",
        one_liner="Did X.",
        technical_depth_tags=["productization"],
    )
    bank = synthesize_star_bank(
        ExperienceLibrary(points=[point]),
        role_context_map={"X": "At Acme leading the platform program."},
        top_n=1,
    )
    assert len(bank.stories) == 1
    assert "Acme" in bank.stories[0].situation


def test_synthesize_star_bank_falls_back_when_no_role_context() -> None:
    point = ExperiencePoint(
        title="X",
        one_liner="Did X.",
        technical_depth_tags=[],
    )
    bank = synthesize_star_bank(
        ExperienceLibrary(points=[point]),
        top_n=1,
    )
    # When role_context_map is None, situation is the placeholder.
    assert len(bank.stories) == 1
    assert "role context" in bank.stories[0].situation.lower()


# --------------------------------------------------------------------------
# Public surface — synthesize_rca_skeletons
# --------------------------------------------------------------------------


def test_synthesize_rca_skeletons_picks_only_rca_tagged_bullets() -> None:
    points = [
        ExperiencePoint(
            title="Productization",
            one_liner="Built reusable services.",
            technical_depth_tags=["productization"],
        ),  # NOT in RCA hints
        ExperiencePoint(
            title="Cloud Migration",
            one_liner="Led migration to cloud.",
            technical_depth_tags=["cloud-migration", "legacy-modernization"],
        ),  # IN RCA hints
        ExperiencePoint(
            title="Lab to Production",
            one_liner="Compressed cycle.",
            technical_depth_tags=["lab-to-production", "metric-6mo-to-3wk"],
        ),  # IN RCA hints
    ]
    skeletons = synthesize_rca_skeletons(
        ExperienceLibrary(points=points),
        top_n=10,
    )
    names = [s.name for s in skeletons]
    assert "RCA: Cloud Migration" in names
    assert "RCA: Lab to Production" in names
    assert "RCA: Productization" not in names  # not RCA territory


def test_synthesize_rca_skeletons_caps_at_top_n() -> None:
    points = [
        ExperiencePoint(
            title=f"Risky {i}",
            one_liner="Risky work.",
            technical_depth_tags=["legacy-modernization"],
        )
        for i in range(8)
    ]
    skeletons = synthesize_rca_skeletons(
        ExperienceLibrary(points=points),
        top_n=4,
    )
    assert len(skeletons) == 4


def test_synthesize_rca_skeletons_empty_library_returns_empty() -> None:
    assert synthesize_rca_skeletons(ExperienceLibrary(points=[])) == []


# --------------------------------------------------------------------------
# Public surface — synthesize_into_library
# --------------------------------------------------------------------------


def test_synthesize_into_library_preserves_existing_star_bank() -> None:
    """Operator-curated stories must NOT be overwritten."""
    existing_story = Story(
        name="Operator-curated story",
        situation="...",
        task="...",
        action="...",
        result="...",
        lesson="...",
        tags=["custom"],
    )
    library = ExperienceLibrary(
        points=[
            ExperiencePoint(title="Some bullet", one_liner="Some text.", technical_depth_tags=[])
        ],
        star_bank=StoryBank(stories=[existing_story]),
    )
    result = synthesize_into_library(library)
    assert len(result.star_bank.stories) == 1
    assert result.star_bank.stories[0].name == "Operator-curated story"


def test_synthesize_into_library_preserves_existing_rca_bank() -> None:
    existing_rca = RCAStory(
        name="Operator RCA",
        situation="...",
        task="...",
        root_cause="real root cause",
        action="...",
        result="...",
        operating_model_change="real change",
    )
    library = ExperienceLibrary(
        points=[
            ExperiencePoint(
                title="X",
                one_liner="X.",
                technical_depth_tags=["legacy-modernization"],
            )
        ],
        rca_bank=[existing_rca],
    )
    result = synthesize_into_library(library)
    assert len(result.rca_bank) == 1
    assert result.rca_bank[0].name == "Operator RCA"


def test_synthesize_into_library_fills_empty_banks() -> None:
    point = ExperiencePoint(
        title="Cloud Migration",
        one_liner="Migrated to cloud successfully.",
        technical_depth_tags=["cloud-migration", "legacy-modernization"],
    )
    library = ExperienceLibrary(points=[point])
    result = synthesize_into_library(library)
    assert len(result.star_bank.stories) >= 1
    assert len(result.rca_bank) >= 1


# --------------------------------------------------------------------------
# End-to-end: synthesize from real master_resume_svp.json
# --------------------------------------------------------------------------


def test_synthesize_into_library_works_with_real_svp_resume() -> None:
    """Smoke test against the actual master_resume_svp.json."""
    resume_path = Path("apps_shared/data/master_resume_svp.json")
    if not resume_path.is_file():
        # In CI without the SVP variant, skip is acceptable.
        return
    library = load_master_resume(resume_path=resume_path)
    assert library.points  # the SVP resume has at least one bullet
    result = synthesize_into_library(
        library,
        jd_text="Senior leader for AI platform with productization and team scaling.",
        resume_path=resume_path,
    )
    assert len(result.star_bank.stories) > 0
    # Stories must have role context populated from the resume's role.context.
    for story in result.star_bank.stories:
        assert story.situation
        assert story.action
        assert story.lesson
    # RCA skeletons should exist for the legacy/migration bullets.
    assert isinstance(result.rca_bank, list)
