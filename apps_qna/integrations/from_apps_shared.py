"""apps_shared master_resume.json -> ExperienceLibrary adapter.

Reads the canonical structured resume at apps_shared/data/master_resume.json
(or master_resume_svp.json for the SVP-tailored variant) and projects it
onto the ExperienceLibrary that drives apps_qna cards.

Mapping:
    professional_experience[*].bullet_pool[*]  ->  ExperiencePoint
        ExperiencePoint.title                  =  bullet.label OR first 60 chars of text
        ExperiencePoint.one_liner              =  bullet.text
        ExperiencePoint.technical_depth_tags   =  bullet.tags

The adapter does NOT populate StoryBank or RCA bank — those are
scenario-specific (which story will I tell THIS interviewer?) and must be
authored per-interview.

Both flat-string bullet pools (legacy `master_resume.json`) and structured
{label, text, tags} dict bullets (new `master_resume_svp.json`) are accepted.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

from apps_qna.types.qna_types import ExperienceLibrary, ExperiencePoint
from apps_shared.contracts.cross_app import (
    EnvelopeLoadError,
    ExperienceLibraryEnvelope,
)

_DEFAULT_RESUME = Path("apps_shared/data/master_resume.json")
_DEFAULT_SVP = Path("apps_shared/data/master_resume_svp.json")
_DEFAULT_ENVELOPE = Path("apps_shared/data/master_resume.envelope.json")
_DEFAULT_ENVELOPE_SVP = Path("apps_shared/data/master_resume_svp.envelope.json")


def _envelope_for(resume_path: Path) -> Path:
    return resume_path.with_suffix("").with_suffix(".envelope.json") \
        if resume_path.suffix == ".json" \
        else resume_path.with_name(resume_path.stem + ".envelope.json")


def _points_from_envelope(env: ExperienceLibraryEnvelope) -> list[ExperiencePoint]:
    points: list[ExperiencePoint] = []
    for bullet in env.payload.bullets:
        text = bullet.text
        label = bullet.label
        title = label or (text.split(".", 1)[0] or text)[:60]
        points.append(
            ExperiencePoint(
                title=title,
                one_liner=text,
                technical_depth_tags=list(bullet.tags),
            )
        )
    return points


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


def load_master_resume(
    resume_path: Path | None = None,
    *,
    prefer_svp: bool = False,
) -> ExperienceLibrary:
    """Load apps_shared master resume into an ExperienceLibrary.

    Args:
        resume_path: explicit path. If None, picks
            `master_resume_svp.json` when `prefer_svp=True` and it exists,
            otherwise `master_resume.json`.
        prefer_svp: when no explicit path is given, prefer the SVP variant.

    Returns:
        ExperienceLibrary populated with ExperiencePoints from every
        bullet_pool entry in professional_experience. StoryBank and RCA
        bank are returned empty — those are scenario-specific.

    Raises:
        FileNotFoundError: resume file is missing and no fallback.
        ValueError: resume JSON is malformed.
    """
    if resume_path is None:
        resume_path = (
            _DEFAULT_SVP if (prefer_svp and _DEFAULT_SVP.is_file())
            else _DEFAULT_RESUME
        )

    # Prefer envelope path (typed, sealed, freshness-checked).
    envelope_path = _envelope_for(resume_path)
    if envelope_path.is_file():
        try:
            env = ExperienceLibraryEnvelope.load(envelope_path)
            return ExperienceLibrary(points=_points_from_envelope(env))
        except EnvelopeLoadError as exc:
            warnings.warn(
                f"Envelope at {envelope_path} failed to load ({exc}); "
                "falling back to raw JSON parser.",
                DeprecationWarning,
                stacklevel=2,
            )

    if not resume_path.is_file():
        raise FileNotFoundError(f"Master resume not found: {resume_path}")

    warnings.warn(
        f"Envelope missing at {envelope_path}; falling back to raw JSON "
        "parser. Run `python -m apps_shared.outputs.experience_library_emitter` "
        "to produce the envelope.",
        DeprecationWarning,
        stacklevel=2,
    )

    try:
        data = json.loads(resume_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed resume JSON at {resume_path}: {exc}") from exc

    points: list[ExperiencePoint] = []
    for role in data.get("professional_experience", []):
        title = role.get("title", "")
        for bullet in role.get("bullet_pool", []):
            points.append(_bullet_to_point(bullet, title))

    return ExperienceLibrary(points=points)


def load_competency_areas(
    resume_path: Path | None = None,
    *,
    prefer_svp: bool = False,
) -> list[dict]:
    """Load the competency areas list (used to seed cross_exam_depth_anchors)."""
    if resume_path is None:
        resume_path = (
            _DEFAULT_SVP if (prefer_svp and _DEFAULT_SVP.is_file())
            else _DEFAULT_RESUME
        )
    if not resume_path.is_file():
        return []
    data = json.loads(resume_path.read_text(encoding="utf-8"))
    # New schema: engineering_and_platform_competencies (list of {area, skills})
    areas = data.get("engineering_and_platform_competencies")
    if isinstance(areas, list):
        return areas
    # Legacy schema: strategic_and_technical_competencies (list of dicts)
    legacy = data.get("strategic_and_technical_competencies")
    if isinstance(legacy, list):
        return legacy
    return []


def load_executive_summary(
    resume_path: Path | None = None,
    *,
    prefer_svp: bool = False,
) -> str | None:
    """Load the executive summary block, useful for card 13 close patterns."""
    if resume_path is None:
        resume_path = (
            _DEFAULT_SVP if (prefer_svp and _DEFAULT_SVP.is_file())
            else _DEFAULT_RESUME
        )
    if not resume_path.is_file():
        return None
    data = json.loads(resume_path.read_text(encoding="utf-8"))
    summary = data.get("executive_summary")
    return summary if isinstance(summary, str) and summary.strip() else None
