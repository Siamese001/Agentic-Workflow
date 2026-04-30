"""Interactive intake wizard — composes a typed Interview YAML from real inputs.

Usage:
    python -m apps_qna init --output-yaml reports/qna/<slug>/interview.yaml

The wizard prompts for:
    - Interview slug
    - Company name (+ optional division/practice/anchors)
    - Role title, level, primary mandate
    - One or more interviewers (name, title, team, lens, hot buttons)
    - JD path (markdown) — parsed via from_jd
    - Research source — one of:
        (a) PDF / markdown brief path -> from_research_brief
        (b) apps_research trace id   -> from_apps_research
        (c) skip
    - Experience source — one of:
        (a) YAML path                -> from_apps_rg.load_experience_yaml
        (b) skip (empty library; user fills in later)

It composes a dict matching the Interview schema, dumps it as YAML, and
optionally invokes the build immediately.

The wizard never calls an LLM. PDF parsing is heuristic; the operator is
strongly recommended to review the produced YAML before building.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from apps_qna.integrations.from_apps_exec import load_executive_close_patterns
from apps_qna.integrations.from_apps_research import load_apps_research
from apps_qna.integrations.from_apps_rg import (
    empty_library,
    load_experience_yaml,
)
from apps_qna.integrations.from_apps_shared import load_master_resume
from apps_qna.integrations.from_jd import load_markdown_jd
from apps_qna.integrations.from_research_brief import load_research_brief
from apps_qna.types.qna_types import (
    BuildMetadata,
    Company,
    Interview,
    Interviewer,
    JobDescription,
    ResearchInputs,
    Role,
)

_log = logging.getLogger(__name__)


@dataclass
class WizardOptions:
    """Non-interactive overrides for the wizard (used by tests + automation)."""

    slug: str | None = None
    company_name: str | None = None
    role_title: str | None = None
    role_level: str = "director"
    role_mandate: str | None = None
    interviewer_names: list[str] = field(default_factory=list)
    jd_path: Path | None = None
    research_pdf: Path | None = None
    research_trace_id: str | None = None
    research_dir: Path | None = None
    experience_yaml: Path | None = None
    master_resume_json: Path | None = None
    use_master_resume: bool = True  # default to apps_shared/data/master_resume*.json
    prefer_svp_resume: bool = False  # if True and SVP variant exists, use it
    exec_brief: Path | None = None
    output_yaml: Path | None = None
    non_interactive: bool = False  # if True, fail rather than prompt


def _prompt(question: str, default: str = "") -> str:
    """Prompt with optional default. Returns stripped string."""
    suffix = f" [{default}]" if default else ""
    response = input(f"{question}{suffix}: ").strip()
    return response or default


def _resolve_interviewers(
    options: WizardOptions,
    interactive: bool,
) -> list[Interviewer]:
    """Build Interviewer list from CLI flags or interactive prompts."""
    if options.interviewer_names:
        return [
            Interviewer(name=name, title="TBD")
            for name in options.interviewer_names
        ]
    if not interactive:
        raise ValueError("No interviewer_names provided and non-interactive mode set")
    interviewers: list[Interviewer] = []
    print("\nEnter interviewer(s). Empty name finishes the list.")
    while True:
        name = _prompt("  Interviewer name (empty to finish)")
        if not name:
            break
        title = _prompt("  Title", default="TBD")
        team = _prompt("  Team (optional)")
        lens = _prompt("  Lens / one-line angle (optional)")
        interviewers.append(
            Interviewer(name=name, title=title, team=team, lens=lens)
        )
    if not interviewers:
        raise ValueError("At least one interviewer is required")
    return interviewers


def _resolve_research(
    options: WizardOptions,
    interactive: bool,
) -> ResearchInputs:
    """Pick research source: PDF/MD, apps_research trace, or empty."""
    if options.research_pdf is not None:
        return load_research_brief(options.research_pdf)
    if options.research_trace_id is not None:
        return load_apps_research(
            trace_id=options.research_trace_id,
            research_dir=options.research_dir,
        )
    if not interactive:
        return ResearchInputs()
    print("\nResearch source:")
    print("  1) Path to PDF or markdown briefing")
    print("  2) apps_research trace id (looks under reports/research/)")
    print("  3) Skip — start with an empty research scaffold")
    choice = _prompt("Choose 1/2/3", default="3")
    if choice == "1":
        path = Path(_prompt("  Briefing path"))
        return load_research_brief(path)
    if choice == "2":
        trace = _prompt("  Trace id (8-hex)")
        return load_apps_research(trace_id=trace or None)
    return ResearchInputs()


def _resolve_jd(
    options: WizardOptions,
    interactive: bool,
) -> JobDescription:
    if options.jd_path is not None:
        return load_markdown_jd(options.jd_path)
    if not interactive:
        return JobDescription()
    raw = _prompt("\nJD markdown path (empty to skip)")
    if not raw:
        return JobDescription()
    return load_markdown_jd(Path(raw))


def _resolve_experience(options: WizardOptions, interactive: bool):
    """Source order:
        1. --experience-yaml (per-interview YAML, full StoryBank/RCA included)
        2. --master-resume-json (or default apps_shared/data/master_resume*.json
           when use_master_resume=True) — provides ExperiencePoints only
        3. interactive prompt
        4. empty library
    """
    if options.experience_yaml is not None:
        return load_experience_yaml(options.experience_yaml)
    if options.master_resume_json is not None:
        return load_master_resume(options.master_resume_json)
    if options.use_master_resume:
        try:
            return load_master_resume(prefer_svp=options.prefer_svp_resume)
        except FileNotFoundError as exc:
            _log.warning("Master resume not found: %s — falling back", exc)
    if not interactive:
        return empty_library()
    raw = _prompt(
        "\nExperience source — YAML path, "
        "or 'master' for apps_shared/data/master_resume.json, "
        "or empty for empty library"
    )
    if not raw:
        return empty_library()
    if raw.lower() == "master":
        return load_master_resume()
    return load_experience_yaml(Path(raw))


def _resolve_executive_close_patterns(
    options: WizardOptions,
    interactive: bool,
) -> list[str]:
    if options.exec_brief is not None:
        try:
            return load_executive_close_patterns(brief_path=options.exec_brief)
        except FileNotFoundError as exc:
            _log.warning("Skipping executive brief: %s", exc)
            return []
    if not interactive:
        return []
    raw = _prompt("\nExecutive brief path (empty to skip)")
    if not raw:
        return []
    try:
        return load_executive_close_patterns(brief_path=Path(raw))
    except FileNotFoundError as exc:
        _log.warning("Skipping executive brief: %s", exc)
        return []


def _company_from(options: WizardOptions, interactive: bool) -> Company:
    name = options.company_name
    if name is None:
        if not interactive:
            raise ValueError("company_name is required in non-interactive mode")
        name = _prompt("\nCompany name")
        if not name:
            raise ValueError("Company name is required")
    return Company(name=name)


def _role_from(options: WizardOptions, interactive: bool) -> Role:
    title = options.role_title
    mandate = options.role_mandate
    if title is None:
        if not interactive:
            raise ValueError("role_title is required in non-interactive mode")
        title = _prompt("Role title")
    if mandate is None:
        mandate = _prompt(
            "Role primary mandate (one sentence)",
            default="TBD — fill in before building.",
        ) if interactive else "TBD — fill in before building."
    return Role(
        title=title or "TBD",
        level=options.role_level,
        primary_mandate=mandate,
    )


def _slug_from(options: WizardOptions, interactive: bool, company: Company) -> str:
    if options.slug:
        return options.slug
    default = company.name.lower().replace(" ", "-").replace("/", "-")
    if not interactive:
        return default
    return _prompt("Interview slug", default=default)


def run_wizard(
    options: WizardOptions | None = None,
    *,
    interactive: bool = True,
) -> tuple[Interview, dict[str, Any]]:
    """Compose a typed Interview from interactive prompts and/or options.

    Returns:
        (interview, extra_context) — extra_context is the dict of optional
        per-template content blocks.
    """
    options = options or WizardOptions()
    if options.non_interactive:
        interactive = False

    company = _company_from(options, interactive)
    role = _role_from(options, interactive)
    interviewers = _resolve_interviewers(options, interactive)
    jd = _resolve_jd(options, interactive)
    research = _resolve_research(options, interactive)
    experience = _resolve_experience(options, interactive)
    exec_close = _resolve_executive_close_patterns(options, interactive)
    slug = _slug_from(options, interactive, company)
    output_yaml = options.output_yaml or Path(f"reports/qna/{slug}/interview.yaml")

    build_meta = BuildMetadata(
        interview_slug=slug,
        built_at=datetime.now(timezone.utc),
        builder_version="0.1.0",
        template_set_version="v2",
        output_dir=output_yaml.parent,
    )

    interview = Interview(
        slug=slug,
        company=company,
        role=role,
        interviewers=interviewers,
        jd=jd,
        experience=experience,
        research=research,
        build_metadata=build_meta,
    )

    # Extra context: empty content blocks the templates iterate over. The
    # operator can populate these in the YAML before building.
    extra_context: dict[str, Any] = {
        "candidate_first_name": "Candidate",
        "architecture_content_blocks": [],
        "governance_content_blocks": [],
        "data_platform_content_blocks": [],
        "measurement_content_blocks": [],
        "semantic_grounding_content_blocks": [],
        "ds_to_platform_content_blocks": [],
        "global_engineering_content_blocks": [],
        "productization_content_blocks": [],
        "executive_fit_close_patterns": exec_close,
        "cross_exam_depth_anchors": [],
        "questions_for_lead": [],
        "questions_for_panel": [],
        "plan_days_1_30": [],
        "plan_days_31_60": [],
        "plan_days_61_90": [],
    }

    return interview, extra_context


def write_interview_yaml(
    interview: Interview,
    extra_context: dict[str, Any],
    path: Path,
) -> None:
    """Dump an Interview + extra_context to a YAML file the builder can load."""
    payload = interview.model_dump(mode="json")
    payload["extra_context"] = extra_context
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
