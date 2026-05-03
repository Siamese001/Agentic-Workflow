"""apps_qna CLI — build mode + lint mode.

Usage:
    python -m apps_qna --interview drew-clements --company dentsu \\
        --role "VP Decisioning Engineering" --jd path/to/jd.md \\
        --interviewers path/to/interviewers.yaml \\
        --experience path/to/experience.yaml \\
        --output reports/qna/drew-clements

    python -m apps_qna lint reports/qna/drew-clements

Exit codes:
    0 = success
    1 = lint failure / invariant violation
    2 = input error (missing file, bad YAML, schema mismatch)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from apps_qna.builder.card_pack_builder import BuilderError, CardPackBuilder
from apps_qna.config.build_config import QnaBuildConfig
from apps_qna.types.qna_types import (
    BuildMetadata,
    Company,
    ExperienceLibrary,
    ExperiencePoint,
    Interview,
    Interviewer,
    JDSection,
    JobDescription,
    RCAStory,
    ResearchClaim,
    ResearchInputs,
    Role,
    Story,
    StoryBank,
)

_log = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.subcommand == "lint":
        return _run_lint(args)
    if args.subcommand == "self-eval":
        return _run_self_eval(args)
    if args.subcommand == "route":
        return _run_route(args)
    if args.subcommand == "init":
        return _run_init(args)
    if args.subcommand == "feedback":
        return _run_feedback(args)
    return _run_build(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apps_qna",
        description="Build interview-prep card packs for ChatGPT 5.5-Thinking.",
    )
    sub = parser.add_subparsers(dest="subcommand")

    # Default: build (also explicit `build` subcommand)
    for name in (None, "build"):
        if name is None:
            target = parser
        else:
            target = sub.add_parser(name, help="Build a card pack")
        _add_build_args(target)

    lint_parser = sub.add_parser("lint", help="Lint an existing card pack")
    lint_parser.add_argument(
        "pack_dir",
        type=Path,
        help="Directory containing an emitted card pack",
    )

    route_parser = sub.add_parser(
        "route",
        help="Score a question against the route registry (semantic router)",
    )
    route_parser.add_argument(
        "question",
        help="The question to route (quote it on the shell)",
    )
    route_parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top candidates to print (default: 3)",
    )

    init_parser = sub.add_parser(
        "init",
        help="Interactive intake wizard — compose Interview YAML from real inputs",
    )
    init_parser.add_argument("--slug", help="Interview slug (default: derived from company)")
    init_parser.add_argument("--company", dest="company_name", help="Company name")
    init_parser.add_argument("--role", dest="role_title", help="Role title")
    init_parser.add_argument("--role-level", default="director", help="Role level (default: director)")
    init_parser.add_argument("--role-mandate", help="Role primary mandate (one sentence)")
    init_parser.add_argument(
        "--interviewer", action="append", default=[],
        help="Interviewer name(s); repeat for panel mode",
    )
    init_parser.add_argument("--jd", type=Path, dest="jd_path", help="Markdown JD path")
    init_parser.add_argument(
        "--research-pdf", type=Path, dest="research_pdf",
        help="PDF or markdown research-briefing path",
    )
    init_parser.add_argument(
        "--research-trace", dest="research_trace_id",
        help="apps_research trace id (8-hex); reads reports/research/",
    )
    init_parser.add_argument(
        "--experience", type=Path, dest="experience_yaml",
        help="Per-interview experience YAML path (apps_rg-format) — "
        "highest precedence; if omitted, master resume is used by default",
    )
    init_parser.add_argument(
        "--master-resume", type=Path, dest="master_resume_json",
        help="Path to master_resume*.json (default: "
        "apps_shared/data/master_resume.json or master_resume_svp.json)",
    )
    init_parser.add_argument(
        "--no-master-resume", action="store_true",
        help="Disable the default master-resume fallback (start with empty "
        "library if no --experience flag is given)",
    )
    init_parser.add_argument(
        "--svp-resume", action="store_true",
        help="Prefer apps_shared/data/master_resume_svp.json over the legacy "
        "master_resume.json when both exist",
    )
    init_parser.add_argument(
        "--exec-brief", type=Path, dest="exec_brief",
        help="Executive brief markdown path",
    )
    init_parser.add_argument(
        "--output-yaml", type=Path,
        help="Where to write the composed Interview YAML (default: "
        "reports/qna/<slug>/interview.yaml)",
    )
    init_parser.add_argument(
        "--non-interactive", action="store_true",
        help="Fail rather than prompt — useful for scripted runs",
    )
    init_parser.add_argument(
        "--build", action="store_true",
        help="Run the full build immediately after writing the YAML",
    )

    feedback_parser = sub.add_parser(
        "feedback",
        help="Record post-rehearsal outcomes into the W4.1 bandit (Wave 5.1)",
    )
    feedback_parser.add_argument(
        "--slug",
        required=True,
        help="Interview slug (e.g. searce-applied-ai)",
    )
    feedback_parser.add_argument(
        "--outcomes",
        type=Path,
        required=True,
        help="Path to a JSON file containing the operator's rehearsal outcomes",
    )

    self_eval_parser = sub.add_parser(
        "self-eval",
        help="Diff two card packs and emit a delta report (Wave 5)",
    )
    self_eval_parser.add_argument(
        "--pack",
        type=Path,
        required=True,
        help="Current card pack directory",
    )
    self_eval_parser.add_argument(
        "--previous",
        type=Path,
        required=False,
        help="Previous card pack directory (optional; "
        "if absent, only summary stats for current are shown)",
    )

    return parser


def _add_build_args(target: argparse.ArgumentParser) -> None:
    target.add_argument("--interview", required=False, help="Interview slug")
    target.add_argument(
        "--config",
        type=Path,
        help="YAML file containing the full Interview model (alternative to flags)",
    )
    target.add_argument("--company", help="Company name")
    target.add_argument("--role", help="Role title")
    target.add_argument(
        "--jd",
        type=Path,
        help="Path to JD markdown file",
    )
    target.add_argument(
        "--interviewers",
        type=Path,
        help="YAML file with list of Interviewer entries",
    )
    target.add_argument(
        "--experience",
        type=Path,
        help="YAML file with ExperienceLibrary",
    )
    target.add_argument(
        "--research-from",
        type=Path,
        dest="research_from",
        help="Path to apps_research brief markdown (optional)",
    )
    target.add_argument(
        "--extra-context",
        type=Path,
        dest="extra_context",
        help="YAML file with specialist-card content blocks",
    )
    target.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: reports/qna/<interview-slug>)",
    )
    target.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing non-empty output directory",
    )
    target.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan and exit without writing",
    )


def _run_build(args: argparse.Namespace) -> int:
    try:
        interview, extra_context = _assemble_interview(args)
    except FileNotFoundError as exc:
        _log.error("Input not found: %s", exc)
        return 2
    except (ValueError, KeyError, yaml.YAMLError) as exc:
        _log.error("Input error: %s", exc)
        return 2

    output_dir = args.output or Path("reports/qna") / interview.slug

    if args.dry_run:
        _print_dry_run(interview, output_dir)
        return 0

    config = QnaBuildConfig(
        force=bool(args.force),
        multi_interviewer_mode=(
            "panel" if len(interview.interviewers) > 1 else "single"
        ),
    )
    # Route through the spine_handoff wrapper. The wrapper constructs
    # the canonical ``ValidatedRequest`` envelope, emits the
    # ``validated_request_emit`` ledger event, and delegates to the
    # existing CardPackBuilder.build() unchanged. This makes apps_qna
    # an APP_OVERLAY_STATIC_EVIDENCE per the spine_manifest.yaml's
    # build_time_compiler route declaration.
    from apps_qna.integrations.spine_handoff import build_pack_via_spine

    try:
        manifest = build_pack_via_spine(
            interview,
            output_dir,
            extra_context=extra_context,
            config=config,
        )
    except BuilderError as exc:
        _log.error("Build failed: %s", exc)
        return 1
    except FileExistsError as exc:
        _log.error("%s", exc)
        return 1

    _log.info(
        "Wrote %d cards to %s; manifest at %s/pack_manifest.json",
        len(manifest.cards),
        output_dir,
        output_dir,
    )
    return 0


def _assemble_interview(
    args: argparse.Namespace,
) -> tuple[Interview, dict[str, Any]]:
    """Build an Interview model from CLI args + YAML config files."""
    extra_context: dict[str, Any] = {}

    if args.config and args.config.is_file():
        with args.config.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if "extra_context" in data:
            extra_context = data.pop("extra_context") or {}
        data.setdefault(
            "build_metadata",
            {
                "interview_slug": data.get("slug", args.interview or "unknown"),
                "built_at": datetime.now(timezone.utc),
                "builder_version": "0.1.0",
                "template_set_version": "v1",
                "output_dir": str(args.output or "reports/qna"),
            },
        )
        interview = Interview.model_validate(data)
    else:
        # Build from individual flags
        if not args.interview:
            raise ValueError("--interview is required when --config is not used")
        if not args.company:
            raise ValueError("--company is required when --config is not used")
        if not args.role:
            raise ValueError("--role is required when --config is not used")
        if not args.interviewers:
            raise ValueError("--interviewers is required when --config is not used")

        interviewers = _load_interviewers(args.interviewers)
        jd = _load_jd(args.jd) if args.jd else JobDescription()
        experience = (
            _load_experience(args.experience)
            if args.experience
            else ExperienceLibrary()
        )
        research = (
            _load_research(args.research_from) if args.research_from else None
        )
        company = Company(name=args.company, anchors=[], avoid_phrases=[], overlay_facts=[])
        role = Role(title=args.role, level="VP", primary_mandate="", success_criteria=[])
        build_metadata = BuildMetadata(
            interview_slug=args.interview,
            built_at=datetime.now(timezone.utc),
            builder_version="0.1.0",
            template_set_version="v1",
            output_dir=args.output or Path("reports/qna") / args.interview,
        )
        interview = Interview(
            slug=args.interview,
            company=company,
            role=role,
            interviewers=interviewers,
            jd=jd,
            experience=experience,
            research=research,
            build_metadata=build_metadata,
        )

    if args.extra_context and args.extra_context.is_file():
        with args.extra_context.open("r", encoding="utf-8") as fh:
            extra_context.update(yaml.safe_load(fh) or {})

    return interview, extra_context


def _load_interviewers(path: Path) -> list[Interviewer]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    raw = data.get("interviewers", data) if isinstance(data, dict) else data
    return [Interviewer.model_validate(item) for item in raw]


def _load_jd(path: Path) -> JobDescription:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    # Naive section parse: any `## ` heading starts a section.
    sections: list[JDSection] = []
    current_heading = "Job Description"
    current_body: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_body:
                sections.append(
                    JDSection(
                        heading=current_heading,
                        body="\n".join(current_body).strip(),
                        extracted_keywords=[],
                    )
                )
            current_heading = line[3:].strip()
            current_body = []
        else:
            current_body.append(line)
    if current_body:
        sections.append(
            JDSection(
                heading=current_heading,
                body="\n".join(current_body).strip(),
                extracted_keywords=[],
            )
        )
    return JobDescription(raw_path=path, sections=sections)


def _load_experience(path: Path) -> ExperienceLibrary:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    points = [ExperiencePoint.model_validate(p) for p in data.get("points", [])]
    stories = [Story.model_validate(s) for s in data.get("stories", [])]
    rca = [RCAStory.model_validate(r) for r in data.get("rca", [])]
    return ExperienceLibrary(
        points=points,
        star_bank=StoryBank(stories=stories),
        rca_bank=rca,
    )


def _load_research(path: Path) -> ResearchInputs:
    if not path.is_file():
        raise FileNotFoundError(path)
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return ResearchInputs.model_validate(data)
    # Fallback: markdown brief — wrap as company_brief
    text = path.read_text(encoding="utf-8")
    return ResearchInputs(company_brief=text)


def _print_dry_run(interview: Interview, output_dir: Path) -> None:
    """Print the planned build, including the multi-tier paste manifest preview."""
    from apps_qna.builder.card_pack_builder import (
        _CARD_SPECS,
        _CHATGPT_PROJECT_FILE_CAP,
    )
    from apps_qna.config.route_registry import load_route_registry

    print(f"Interview slug    : {interview.slug}")
    print(f"Company           : {interview.company.name}")
    print(f"Role              : {interview.role.title}")
    print(f"Interviewers      : {[i.name for i in interview.interviewers]}")
    print(f"JD sections       : {len(interview.jd.sections)}")
    print(f"Experience points : {len(interview.experience.points)}")
    print(f"STAR stories      : {len(interview.experience.star_bank.stories)}")
    print(f"RCA stories       : {len(interview.experience.rca_bank)}")
    print(f"Output directory  : {output_dir}")
    print()

    panel = len(interview.interviewers) > 1
    likely = (
        list(interview.research.likely_questions)
        if interview.research and interview.research.likely_questions
        else []
    )
    relevant_routes = (
        {lq.route_id for lq in likely} if likely else None  # None = all
    )

    # Build per-card plan with tier + paste decision.
    registry = load_route_registry()
    relevant_skills: set[str] = set()
    if relevant_routes is None:
        for r in registry.routes:
            relevant_skills.add(r.primary_card)
            relevant_skills.update(r.optional_specialists)
    else:
        for r in registry.routes:
            if r.id in relevant_routes:
                relevant_skills.add(r.primary_card)
                relevant_skills.update(r.optional_specialists)

    print("Card plan (tier | paste? | filename):")
    pasted_count = 0
    archived_count = 0
    for spec in _CARD_SPECS:
        filename, _, panelize, _, _, _, load_strategy = spec
        if panelize and panel:
            for idx, iv in enumerate(interview.interviewers):
                suf = chr(ord("A") + idx)
                panel_filename = filename.replace("03_", f"03{suf}_").replace(
                    "_LENS.md",
                    f"_LENS_{iv.name.upper().replace(' ', '_')}.md",
                )
                paste = "PASTE" if load_strategy != "post_rehearsal" else "archive"
                print(f"  {load_strategy:<14} | {paste:<7} | {panel_filename}")
                if paste == "PASTE":
                    pasted_count += 1
                else:
                    archived_count += 1
            continue
        if load_strategy == "post_rehearsal":
            print(f"  {load_strategy:<14} | archive | {filename}")
            archived_count += 1
        elif load_strategy == "always_on":
            print(f"  {load_strategy:<14} | PASTE   | {filename}")
            pasted_count += 1
        else:
            # primary / specialist — gated by relevant_skills
            if filename in relevant_skills:
                print(f"  {load_strategy:<14} | PASTE   | {filename}")
                pasted_count += 1
            else:
                print(f"  {load_strategy:<14} | skip    | {filename}  (route not in likely_questions)")

    print()
    total_rendered = pasted_count + archived_count + (
        sum(
            1
            for s in _CARD_SPECS
            if s[6] not in {"always_on", "post_rehearsal"} and s[0] not in relevant_skills
        )
        if relevant_routes is not None
        else 0
    )
    # Recompute properly for accuracy.
    rendered = sum(1 for s in _CARD_SPECS) + (
        len(interview.interviewers) - 1 if panel else 0
    )
    print(f"Summary:")
    print(f"  Rendered to disk : {rendered}")
    print(f"  Pasted (ChatGPT) : {pasted_count}")
    print(f"  Archived only    : {archived_count} (post_rehearsal cards stay on disk)")
    if pasted_count > _CHATGPT_PROJECT_FILE_CAP:
        print(
            f"  ⚠ WARNING        : paste count ({pasted_count}) exceeds ChatGPT "
            f"{_CHATGPT_PROJECT_FILE_CAP}-file cap. "
            "Declare interview.research.likely_questions to scope down."
        )
    else:
        print(
            f"  Cap status       : {pasted_count}/{_CHATGPT_PROJECT_FILE_CAP} "
            f"ChatGPT files (under cap)"
        )
    if relevant_routes is None:
        print(
            "  Likely-questions : NOT declared → conservative default "
            "(all skill cards pasted)"
        )
    else:
        print(f"  Likely-questions : declared for routes {sorted(relevant_routes)}")


def _run_lint(args: argparse.Namespace) -> int:
    from apps_qna.router.pack_loader import load_pack
    from apps_qna.validators import run_all_validators

    pack_dir: Path = args.pack_dir
    if not pack_dir.is_dir():
        _log.error("Pack directory not found: %s", pack_dir)
        return 2

    try:
        pack = load_pack(pack_dir)
    except FileNotFoundError as exc:
        _log.error("%s", exc)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        _log.error("Could not read pack: %s", exc)
        return 1

    result = run_all_validators(pack)
    if result.ok:
        _log.info(
            "Lint OK — pack %s passes all 6 invariants (%d cards, %d routes covered).",
            pack_dir,
            len(pack.cards),
            len(pack.manifest.get("routes_covered") or []),
        )
        return 0

    _log.error("Lint FAILED — %d violation(s):", len(result.errors))
    for err in result.errors:
        prefix = f"[{err.code}]"
        if err.where:
            prefix += f" {err.where}:"
        _log.error("  %s %s", prefix, err.message)
    return 1


def _run_init(args: argparse.Namespace) -> int:
    """Interactive intake wizard. Composes Interview YAML; optionally builds."""
    from apps_qna.integrations.wizard import (
        WizardOptions,
        run_wizard,
        write_interview_yaml,
    )

    options = WizardOptions(
        slug=args.slug,
        company_name=args.company_name,
        role_title=args.role_title,
        role_level=args.role_level,
        role_mandate=args.role_mandate,
        interviewer_names=args.interviewer,
        jd_path=args.jd_path,
        research_pdf=args.research_pdf,
        research_trace_id=args.research_trace_id,
        experience_yaml=args.experience_yaml,
        master_resume_json=args.master_resume_json,
        use_master_resume=not args.no_master_resume,
        prefer_svp_resume=args.svp_resume,
        exec_brief=args.exec_brief,
        output_yaml=args.output_yaml,
        non_interactive=args.non_interactive,
    )
    try:
        interview, extra_context = run_wizard(options)
    except (FileNotFoundError, ValueError) as exc:
        _log.error("Intake failed: %s", exc)
        return 2

    output_yaml = options.output_yaml or Path(
        f"reports/qna/{interview.slug}/interview.yaml"
    )
    write_interview_yaml(interview, extra_context, output_yaml)
    _log.info("Wrote Interview YAML to %s", output_yaml)
    print(f"\n✓ Interview YAML written: {output_yaml}")
    print(f"  Slug:         {interview.slug}")
    print(f"  Company:      {interview.company.name}")
    print(f"  Role:         {interview.role.title}")
    print(f"  Interviewers: {[i.name for i in interview.interviewers]}")
    print(f"  JD sections:  {len(interview.jd.sections)}")
    if interview.research:
        print(
            f"  Research:     "
            f"company_brief={'set' if interview.research.company_brief else 'empty'}, "
            f"trends={len(interview.research.industry_trends)}, "
            f"sources={len(interview.research.source_register)}"
        )
    print(f"  Experience:   "
          f"points={len(interview.experience.points)}, "
          f"stars={len(interview.experience.star_bank.stories)}, "
          f"rcas={len(interview.experience.rca_bank)}")
    print()
    print("Review the YAML, fill in any TBD fields, then build with:")
    print(f"  python -m apps_qna --config {output_yaml} --output reports/qna/{interview.slug}")

    if args.build:
        # Re-load through the normal build path so the intake artifact is the
        # single source of truth.
        build_args = argparse.Namespace(
            interview=interview.slug,
            config=output_yaml,
            company=None, role=None, jd=None, interviewers=None,
            experience=None, research_from=None, output=None,
            multi_interviewer_mode="auto", line_ending="lf",
            force=True, dry_run=False,
        )
        _log.info("Running build immediately…")
        return _run_build(build_args)
    return 0


def _run_feedback(args: argparse.Namespace) -> int:
    """Record post-rehearsal outcomes into the W4.1 bandit + ledger.

    Loads ``args.outcomes`` JSON, instantiates an
    :class:`AppsQnaRouteBandit`, replays accumulated outcomes from the
    apps_qna_pack_lifecycle ledger to restore posterior state, persists
    the new outcomes (ledger row + bandit update), and prints a
    one-line summary.
    """
    from apps_qna.config.route_registry import load_route_registry
    from apps_qna.integrations.learning_adapter import (
        load_session_from_json,
        record_rehearsal_outcomes,
        replay_outcomes_into_bandit,
    )
    from apps_qna.router.route_bandit import AppsQnaRouteBandit

    try:
        session = load_session_from_json(args.slug, args.outcomes)
    except (FileNotFoundError, ValueError) as exc:
        _log.error("Failed to load outcomes file: %s", exc)
        return 2

    registry = load_route_registry()
    bandit = AppsQnaRouteBandit(registry)

    replayed = replay_outcomes_into_bandit(bandit, namespace=session.namespace)
    persisted = record_rehearsal_outcomes(session, bandit=bandit)

    total_obs = bandit.total_observations(session.namespace)
    _log.info(
        "feedback recorded — slug=%s namespace=%s replayed=%d persisted=%d "
        "total_observations=%d (cold-start %s)",
        session.slug,
        session.namespace,
        replayed,
        persisted,
        total_obs,
        "cleared" if total_obs >= 5 else "active",
    )
    return 0 if persisted > 0 else 1


def _run_route(args: argparse.Namespace) -> int:
    """Score `args.question` against the route registry and print top_k."""
    from apps_qna.config.route_registry import load_route_registry
    from apps_qna.router.semantic_router import SemanticRouter

    registry = load_route_registry()
    router = SemanticRouter(registry)
    ranked = router.route(args.question, top_k=args.top_k)

    print(f'Question: "{args.question}"')
    print()
    print(f"Top {len(ranked)} routes:")
    for idx, hit in enumerate(ranked, start=1):
        print(
            f"  {idx}. [{hit.score:.3f}] {hit.route_id:<20} "
            f"-> {hit.primary_card}"
        )
    print()
    # W1.1: delegate the abstain decision to SemanticRouter.best, which
    # applies a mode-aware threshold (embedding-mode scores are never
    # exactly zero under BGE-M3, so a keyword-era "score == 0" exit was
    # unreachable on the embedding path).
    if router.best(args.question) is None:
        print("(All scores zero — no token overlap with any route corpus.)")
        return 1
    return 0


def _run_self_eval(args: argparse.Namespace) -> int:
    """Wave 5 — print a delta report between two card packs.

    Surfaces:
        - card-set diff (added / removed)
        - manifest stat diffs (route coverage, interviewer count)
        - per-card word-count change for cards present in both
    """
    from apps_qna.router.pack_loader import load_pack
    from apps_qna.validators.token_budget import _count_words

    pack_dir: Path = args.pack
    prev_dir: Path | None = args.previous

    if not pack_dir.is_dir():
        _log.error("Pack directory not found: %s", pack_dir)
        return 2
    try:
        cur = load_pack(pack_dir)
    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        _log.error("Could not load current pack: %s", exc)
        return 2

    print(f"# Self-eval — {pack_dir}")
    print()
    print(f"- Cards: **{len(cur.cards)}**")
    print(f"- Routes covered: **{len(cur.manifest.get('routes_covered') or [])}**")
    print(f"- Interviewers: **{len(cur.manifest.get('interviewers') or [])}**")
    cur_words = {c.filename: _count_words(c.content) for c in cur.cards}
    print(f"- Total words: **{sum(cur_words.values())}**")
    print()

    if prev_dir is None:
        print("(No --previous supplied; skipping diff.)")
        return 0
    if not prev_dir.is_dir():
        _log.error("Previous pack directory not found: %s", prev_dir)
        return 2
    try:
        prev = load_pack(prev_dir)
    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        _log.error("Could not load previous pack: %s", exc)
        return 2

    cur_set = {c.filename for c in cur.cards}
    prev_set = {c.filename for c in prev.cards}
    added = sorted(cur_set - prev_set)
    removed = sorted(prev_set - cur_set)
    common = sorted(cur_set & prev_set)
    prev_words = {c.filename: _count_words(c.content) for c in prev.cards}

    print(f"## Diff vs {prev_dir}")
    print()
    print(f"- Added: **{len(added)}**")
    for fn in added:
        print(f"  - `{fn}` ({cur_words[fn]} words)")
    print(f"- Removed: **{len(removed)}**")
    for fn in removed:
        print(f"  - `{fn}` ({prev_words[fn]} words)")
    print(f"- Common cards: **{len(common)}**")
    print()

    print("### Word-count delta (top 10 by absolute change)")
    deltas = [(fn, cur_words[fn] - prev_words[fn]) for fn in common]
    deltas.sort(key=lambda x: abs(x[1]), reverse=True)
    for fn, delta in deltas[:10]:
        sign = "+" if delta >= 0 else ""
        print(f"  - `{fn}`: {sign}{delta} words ({prev_words[fn]} → {cur_words[fn]})")
    print()

    print("### Route coverage delta")
    cur_routes = set(cur.manifest.get("routes_covered") or [])
    prev_routes = set(prev.manifest.get("routes_covered") or [])
    print(f"- Newly covered: {sorted(cur_routes - prev_routes) or 'none'}")
    print(f"- No longer covered: {sorted(prev_routes - cur_routes) or 'none'}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    raise SystemExit(main())
