"""apps_shared identity resume + apps_rg graph -> ExperienceLibrary adapter.

The base resume at ``apps_shared/data/master_resume.json`` (and the SVP variant
``master_resume_svp.json``) is now IDENTITY-ONLY: it carries no
bullets/context/competencies/executive_summary. The single source of truth for
experience facts/claims/metrics is the apps_rg ``augmented_skills_graph`` (see
``apps_qna/integrations/from_graph.py``, which mirrors the cross-app consumption
pattern in ``apps_lic/integrations/apps_rg_proof_bridge.py``).

Loader contract (graph-first, fixture-compatible):
    * ``load_master_resume`` returns the GRAPH-derived ExperienceLibrary by
      default. An explicit ``resume_path`` that still carries a ``bullet_pool``
      (test fixtures, legacy resumes) is parsed from that file; an explicit
      identity-only path with no bullets degrades to the graph projection.
    * ``load_competency_areas`` / ``load_executive_summary`` return the
      graph-derived projection (the identity resume has no such blocks).

The adapter does NOT populate StoryBank or RCA bank — those are
scenario-specific (which story will I tell THIS interviewer?) and are filled by
``star_synthesis`` from the graph-derived points.

Fail-soft: if the apps_rg graph is unavailable, the loaders degrade to empty
(never crash).
"""

from __future__ import annotations

import json
from pathlib import Path

from apps_qna.integrations.from_graph import (
    competency_areas_from_graph,
    executive_summary_from_graph,
    experience_library_from_graph,
)
from apps_qna.types.qna_types import ExperienceLibrary, ExperiencePoint

_DEFAULT_RESUME = Path("apps_shared/data/master_resume.json")
_DEFAULT_SVP = Path("apps_shared/data/master_resume_svp.json")


def _bullet_to_point(bullet: dict | str, role_title: str) -> ExperiencePoint:
    """Coerce a bullet (dict or legacy string) into an ExperiencePoint."""
    if isinstance(bullet, str):
        text = bullet.strip()
        title = (text.split(".", 1)[0] or text)[:60]
        return ExperiencePoint(
            title=title,
            one_liner=text,
            technical_depth_tags=[],
        )
    # Structured shape
    text = (bullet.get("text") or "").strip()
    label = (bullet.get("label") or "").strip()
    tags = list(bullet.get("tags") or [])
    title = label or (text.split(".", 1)[0] or text)[:60]
    return ExperiencePoint(
        title=title,
        one_liner=text,
        technical_depth_tags=tags,
    )


def _points_from_resume_file(resume_path: Path) -> list[ExperiencePoint]:
    """Parse bullet_pool ExperiencePoints from a resume JSON file.

    Returns ``[]`` when the resume is identity-only (no ``bullet_pool``). Both
    flat-string bullets (legacy) and structured ``{label, text, tags}`` dicts
    are accepted.

    Raises:
        ValueError: resume JSON is malformed.
    """
    try:
        data = json.loads(resume_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed resume JSON at {resume_path}: {exc}") from exc
    points: list[ExperiencePoint] = []
    for role in data.get("professional_experience", []):
        title = role.get("title", "")
        for bullet in role.get("bullet_pool", []):
            points.append(_bullet_to_point(bullet, title))
    return points


def load_master_resume(
    resume_path: Path | None = None,
    *,
    prefer_svp: bool = False,
) -> ExperienceLibrary:
    """Load the candidate's ExperienceLibrary — graph-first.

    Experience facts come from the apps_rg ``augmented_skills_graph`` (the SSOT);
    the base resume is identity-only. The ``resume_path``/``prefer_svp`` args are
    retained for backward compatibility:

      * When an explicit ``resume_path`` is given and that file still carries a
        ``bullet_pool`` (test fixtures / legacy resumes), its bullets are parsed
        from the file. A missing explicit path raises ``FileNotFoundError``.
      * Otherwise (default path, or an identity-only resume with no bullets) the
        library is projected from the apps_rg graph.

    Args:
        resume_path: optional explicit resume path. ``None`` -> graph projection.
        prefer_svp: accepted for signature compatibility; no longer selects a
            fact source (facts come from the graph regardless).

    Returns:
        ExperienceLibrary populated with ExperiencePoints (StoryBank and RCA
        bank empty — those are filled by star_synthesis).

    Raises:
        FileNotFoundError: an explicit ``resume_path`` is missing.
        ValueError: an explicit resume JSON is malformed.
    """
    if resume_path is not None:
        if not resume_path.is_file():
            raise FileNotFoundError(f"Master resume not found: {resume_path}")
        # An explicit resume that still carries bullets (fixtures / legacy)
        # is honored; an identity-only resume degrades to the graph.
        points = _points_from_resume_file(resume_path)
        if points:
            return ExperienceLibrary(points=points)

    # Default + identity-only path: the apps_rg graph is the SSOT.
    return experience_library_from_graph()


def load_competency_areas(
    resume_path: Path | None = None,
    *,
    prefer_svp: bool = False,
) -> list[dict]:
    """Competency areas (used to seed cross_exam_depth_anchors) — graph-first.

    The identity-only resume has no competency block; areas are projected from
    the apps_rg graph (pillar -> comma-joined skill names). An explicit
    ``resume_path`` that still carries a competency block (test fixtures /
    legacy resumes) is honored for backward compatibility.

    Returns ``[]`` when neither a fixture block nor the graph is available.
    """
    if resume_path is not None and resume_path.is_file():
        data = json.loads(resume_path.read_text(encoding="utf-8"))
        # New schema: engineering_and_platform_competencies (list of {area, skills}).
        areas = data.get("engineering_and_platform_competencies")
        if isinstance(areas, list) and areas:
            return areas
        # Legacy schema: strategic_and_technical_competencies (list of dicts).
        legacy = data.get("strategic_and_technical_competencies")
        if isinstance(legacy, list) and legacy:
            return legacy
    return competency_areas_from_graph()


def load_executive_summary(
    resume_path: Path | None = None,
    *,
    prefer_svp: bool = False,
) -> str | None:
    """Executive summary (card 13 close patterns) — graph-first.

    The identity-only resume has no executive_summary block; the summary is a
    short, metric-grounded synthesis from the apps_rg graph. An explicit
    ``resume_path`` that still carries an ``executive_summary`` string (test
    fixtures / legacy resumes) is honored for backward compatibility.

    Returns ``None`` when neither a fixture block nor the graph is available.
    """
    if resume_path is not None and resume_path.is_file():
        data = json.loads(resume_path.read_text(encoding="utf-8"))
        summary = data.get("executive_summary")
        if isinstance(summary, str) and summary.strip():
            return summary
    return executive_summary_from_graph()
