"""CardPackBuilder — renders the 18 templates into a numbered card pack.

Determinism contract:
- Same Interview + same QnaBuildConfig → byte-identical output (modulo
  built_at timestamp, which lives only in pack_manifest.json).
- All file I/O uses LF line endings unless QnaBuildConfig.line_ending == "crlf".
- StrictUndefined is on — missing variables are errors, not blanks.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    UndefinedError,
)

from apps_qna import __version__ as _BUILDER_VERSION
from apps_qna.config.build_config import QnaBuildConfig
from apps_qna.config.route_registry import RouteRegistry, load_route_registry
from apps_qna.integrations.spine_adapter import (
    emit_pack_lifecycle_event,
    ensure_pack_dir,
    pack_build_span,
    write_card_text,
    write_pack_manifest_json,
)
from apps_qna.types.qna_types import (
    BuildMetadata,
    CardPackManifest,
    Interview,
)

_log = logging.getLogger(__name__)

_TEMPLATE_DIR_DEFAULT = Path(__file__).parent.parent / "templates"

# (filename, template_name, panelize, card_type, priority, paste_order, load_strategy)
# - panelize=True: render once per interviewer in panel mode.
# - card_type: "rule" (always-on, governs all answers) or "skill" (loaded by route).
# - priority: "must" | "should" | "may" — paste-strategy ordering hint.
# - paste_order: integer for the paste sequence into a ChatGPT Project workspace.
# - load_strategy: "always_on" | "primary" | "specialist" | "post_rehearsal".
_CARD_SPECS: list[tuple[str, str, bool, str, str, int, str]] = [
    ("00_RUNTIME_ROOT.md", "00_runtime_root.md.j2", False, "rule", "must", 0, "always_on"),
    ("01_ROUTING_MANIFEST.md", "01_routing_manifest.md.j2", False, "rule", "must", 1, "always_on"),
    ("02_LIVE_MODE.md", "02_live_mode.md.j2", False, "rule", "must", 2, "always_on"),
    ("03_INTERVIEWER_LENS.md", "03_interviewer_lens.md.j2", True, "rule", "must", 3, "always_on"),
    ("04_COMPANY_OVERLAY.md", "04_company_overlay.md.j2", False, "rule", "must", 4, "always_on"),
    ("05_ARCHITECTURE_CORE.md", "05_architecture_core.md.j2", False, "skill", "should", 5, "primary"),
    ("06_DATA_PLATFORM.md", "06_data_platform.md.j2", False, "skill", "may", 6, "specialist"),
    ("07_MEASUREMENT.md", "07_measurement.md.j2", False, "skill", "may", 7, "specialist"),
    ("08_GOVERNANCE.md", "08_governance.md.j2", False, "skill", "should", 8, "primary"),
    ("09_SEMANTIC_GROUNDING.md", "09_semantic_grounding.md.j2", False, "skill", "may", 9, "specialist"),
    ("10_DS_TO_PLATFORM.md", "10_ds_to_platform.md.j2", False, "skill", "should", 10, "primary"),
    ("11_GLOBAL_ENGINEERING.md", "11_global_engineering.md.j2", False, "skill", "should", 11, "primary"),
    ("12_PRODUCTIZATION.md", "12_productization.md.j2", False, "skill", "should", 12, "primary"),
    ("13_EXECUTIVE_FIT.md", "13_executive_fit.md.j2", False, "skill", "should", 13, "primary"),
    ("14_STAR_BANK.md", "14_star_bank.md.j2", False, "skill", "should", 14, "primary"),
    ("15_RCA.md", "15_rca.md.j2", False, "skill", "should", 15, "primary"),
    ("16_CROSS_EXAM.md", "16_cross_exam.md.j2", False, "skill", "should", 16, "primary"),
    ("17_QUESTIONS_AND_90_DAY_PLAN.md", "17_questions_and_90_day_plan.md.j2", False, "skill", "should", 17, "primary"),
    ("19_SOURCE_REGISTER.md", "19_source_register.md.j2", False, "rule", "must", 19, "always_on"),
    ("20_GLOSSARY.md", "20_glossary.md.j2", False, "rule", "should", 20, "always_on"),
    ("21_LIKELY_QUESTIONS.md", "21_likely_questions.md.j2", False, "rule", "may", 21, "always_on"),
    ("22_LEARNINGS.md", "22_learnings.md.j2", False, "rule", "may", 22, "post_rehearsal"),
]

# Back-compat alias: legacy _CARDS shape (filename, template, panelize).
_CARDS: list[tuple[str, str, bool]] = [
    (spec[0], spec[1], spec[2]) for spec in _CARD_SPECS
]

TEMPLATE_SET_VERSION = "v2"

# ChatGPT 5.5-Thinking Project file upload cap. When the optimized paste
# manifest exceeds this, the manifest sets `paste_exceeds_chatgpt_limit=True`
# and the builder logs a warning recommending tighter likely_questions scope.
_CHATGPT_PROJECT_FILE_CAP = 25


class BuilderError(Exception):
    """Raised when the builder cannot satisfy its contract."""


@dataclass(frozen=True)
class CardRender:
    """One rendered card ready to write."""

    filename: str
    content: str


class CardPackBuilder:
    """Renders 18 templates into a card-pack directory."""

    def __init__(
        self,
        config: QnaBuildConfig | None = None,
        route_registry: RouteRegistry | None = None,
    ) -> None:
        self._config = config or QnaBuildConfig()
        self._registry = route_registry or load_route_registry()
        template_dir = self._config.template_dir or _TEMPLATE_DIR_DEFAULT
        if not template_dir.is_dir():
            raise BuilderError(f"Template directory not found: {template_dir}")
        self._env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            lstrip_blocks=True,
            autoescape=False,
        )
        self._template_dir = template_dir

    def build(
        self,
        interview: Interview,
        output_dir: Path,
        extra_context: dict[str, Any] | None = None,
    ) -> CardPackManifest:
        """Render all cards and write them to output_dir.

        Args:
            interview: Typed interview-prep input bundle.
            output_dir: Destination directory. Created if missing.
            extra_context: Optional extra Jinja variables for content blocks
                that aren't first-class fields on Interview (architecture
                content, governance points, executive-fit thesis, etc.).

        Returns:
            A CardPackManifest describing the written pack.

        Raises:
            BuilderError: directory exists and `force=False`, or a template
                referenced an undefined variable.
            FileExistsError: output dir is non-empty and force=False.
        """
        with pack_build_span(
            "apps_qna.v1.pack.build",
            attributes={
                "qna.slug": interview.build_metadata.interview_slug
                if interview.build_metadata
                else "unknown",
                "qna.template_set": TEMPLATE_SET_VERSION,
                "qna.builder_version": _BUILDER_VERSION,
                "qna.output_dir": str(output_dir),
            },
        ) as span:
            if output_dir.exists() and any(output_dir.iterdir()):
                if not self._config.force:
                    raise FileExistsError(
                        f"Output directory not empty: {output_dir} (use --force)"
                    )
            # UWG-routed directory creation (constitutional §3 — all
            # filesystem mutations go through the L2 write gateway).
            ensure_pack_dir(output_dir)

            renders = self._render_all(interview, extra_context or {})
            span.set_attribute("qna.cards_rendered", len(renders))
            for r in renders:
                self._write(output_dir / r.filename, r.content)

            manifest = self._build_manifest(interview, renders, output_dir)
            manifest_path = output_dir / "pack_manifest.json"
            # Manifest write through the dedicated UWG facade — same atomic
            # contract as cards, but flagged as the canonical pack-manifest
            # write for future audit-trail filtering.
            manifest_payload = (
                json.dumps(manifest.model_dump(mode="json"), indent=2, default=str)
                + "\n"
            )
            if self._config.line_ending == "crlf":
                manifest_payload = manifest_payload.replace("\n", "\r\n")
            write_pack_manifest_json(manifest_path, manifest_payload)
            span.set_attribute("qna.routes_covered", len(manifest.routes_covered))
            span.set_attribute(
                "qna.paste_exceeds_chatgpt_limit",
                bool(manifest.paste_exceeds_chatgpt_limit),
            )
            _log.info(
                "Built %d-card pack at %s (template_set=%s)",
                len(renders),
                output_dir,
                TEMPLATE_SET_VERSION,
            )
        # W1.4 — emit pack-lifecycle ledger row. Constitutional §29
        # paired-marker contract: the OTEL span above IS the marker side;
        # this is the library-write half. Fail-soft per the helper's
        # contract — ledger errors never abort the build.
        slug = (
            interview.build_metadata.interview_slug
            if interview.build_metadata
            else "unknown"
        )
        primary_interviewer = (
            interview.interviewers[0].name if interview.interviewers else None
        )
        emit_pack_lifecycle_event(
            event_kind="pack_build",
            prediction={
                "interview_slug": slug,
                "interviewer": primary_interviewer,
                "card_count": len(renders),
                "routes_covered": list(manifest.routes_covered),
                "paste_set_size": len(manifest.pasted_cards),
                "paste_exceeds_chatgpt_limit": bool(
                    manifest.paste_exceeds_chatgpt_limit
                ),
                "template_set_version": TEMPLATE_SET_VERSION,
                "builder_version": _BUILDER_VERSION,
            },
            score_band=(
                "clean"
                if not manifest.paste_exceeds_chatgpt_limit
                else "self_eval_drift"
            ),
            repo_area=str(output_dir),
        )
        return manifest

    # ---------- internal ----------

    def _render_all(
        self,
        interview: Interview,
        extra: dict[str, Any],
    ) -> list[CardRender]:
        ctx_base = self._base_context(interview, extra)
        is_panel = (
            self._config.multi_interviewer_mode == "panel"
            or len(interview.interviewers) > 1
        )
        renders: list[CardRender] = []
        for spec in _CARD_SPECS:
            filename, tpl_name, panelize, card_type, priority, paste_order, load_strategy = spec
            card_meta = {
                "card_id": filename.replace(".md", ""),
                "card_type": card_type,
                "priority": priority,
                "paste_order": paste_order,
                "load_strategy": load_strategy,
            }
            template = self._env.get_template(tpl_name)
            if panelize and is_panel:
                for idx, interviewer in enumerate(interview.interviewers):
                    suffix = chr(ord("A") + idx)  # 03A, 03B, ...
                    panel_filename = filename.replace(
                        "03_", f"03{suffix}_"
                    ).replace(
                        "_LENS.md",
                        f"_LENS_{interviewer.name.upper().replace(' ', '_')}.md",
                    )
                    panel_meta = {
                        **card_meta,
                        "card_id": panel_filename.replace(".md", ""),
                    }
                    ctx = {
                        **ctx_base,
                        "interviewer": interviewer,
                        "card_meta": panel_meta,
                    }
                    renders.append(
                        CardRender(
                            filename=panel_filename,
                            content=self._render(template, ctx, panel_filename),
                        )
                    )
            else:
                ctx = {**ctx_base, "card_meta": card_meta}
                if panelize:
                    # single mode — interviewer is the first one
                    ctx["interviewer"] = interview.interviewers[0]
                renders.append(
                    CardRender(
                        filename=filename,
                        content=self._render(template, ctx, filename),
                    )
                )
        return renders

    def _render(
        self,
        template: Any,
        ctx: dict[str, Any],
        filename: str,
    ) -> str:
        try:
            return template.render(**ctx)
        except UndefinedError as exc:
            raise BuilderError(
                f"Template render failed for {filename}: {exc}. "
                "A required variable was not provided. "
                "Either populate the field on Interview or pass it via "
                "extra_context."
            ) from exc

    def _base_context(
        self,
        interview: Interview,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        candidate_first_name = extra.get("candidate_first_name", "Candidate")
        lead = interview.interviewers[0] if interview.interviewers else None
        ctx: dict[str, Any] = {
            "interview": interview,
            "company": interview.company,
            "role": interview.role,
            "jd": interview.jd,
            "experience": interview.experience,
            "research": interview.research,
            "include_research_register": self._config.include_research_register,
            "candidate_first_name": candidate_first_name,
            "lead_interviewer_name": lead.name if lead else "the interviewer",
            "routes": self._registry.routes,
            "tie_breaker_rules": self._registry.tie_breaker_rules,
            # Reasonable defaults that a thin smoke fixture can rely on.
            "ingest_only_examples": extra.get(
                "ingest_only_examples",
                [
                    "decisioning org responsible for many clients",
                    "GenAI from chatbots to agents to AI orchestration",
                    "remember to mention LLM as a Judge",
                ],
            ),
            "interview_bottom_line": extra.get(
                "interview_bottom_line",
                f"{candidate_first_name} can build trusted, governed agentic "
                "systems that scale across data science, product, platform, "
                "and global engineering.",
            ),
            "always_on_thesis": extra.get(
                "always_on_thesis",
                "The visible layer is the conversational agent. The real "
                "system is the trusted data contract, the model lifecycle, "
                "the orchestration layer, the governance controls, the user "
                "experience, and the operating model working together.",
            ),
            "answer_spine_steps": extra.get(
                "answer_spine_steps",
                [
                    "Start with the business decision.",
                    "Identify the trusted data or semantic contract.",
                    "Explain the agentic workflow.",
                    "Name the control point or gate.",
                    "Translate uncertainty honestly.",
                    "Tie to client or end-user outcome.",
                    "Show how it scales through platform and operating model.",
                ],
            ),
            "better_framings": extra.get(
                "better_framings",
                [
                    "The agent is only as reliable as the semantic layer and evaluation system behind it.",
                    "For measurement, I would rather expose a calibrated range than a false point estimate.",
                    "I separate advisory outputs from state-changing actions.",
                    "I treat Text-to-SQL as a governed runtime, not a chatbot feature.",
                    "The data contract, model registry, eval suite, and approval gates all have to move together.",
                ],
            ),
            "interview_posture_criteria": extra.get(
                "interview_posture_criteria",
                [
                    "Be technical without sounding academic.",
                    "Connect statistical rigor to product UX.",
                    "Build safe agentic systems clients can trust.",
                    "Lead distributed engineering teams without becoming a bottleneck.",
                    "Avoid generic GenAI hype.",
                ],
            ),
            # Specialist-card content blocks — supplied by extra_context.
            # Defaults are minimal placeholders so smoke-fixture builds work.
            "architecture_content_blocks": extra.get(
                "architecture_content_blocks", []
            ),
            "data_platform_anchors": extra.get("data_platform_anchors", []),
            "data_platform_talking_points": extra.get(
                "data_platform_talking_points", []
            ),
            "measurement_anchors": extra.get("measurement_anchors", []),
            "measurement_talking_points": extra.get(
                "measurement_talking_points", []
            ),
            "governance_control_surfaces": extra.get(
                "governance_control_surfaces", []
            ),
            "governance_talking_points": extra.get(
                "governance_talking_points", []
            ),
            "semantic_grounding_talking_points": extra.get(
                "semantic_grounding_talking_points", []
            ),
            "mlops_lifecycle_anchors": extra.get("mlops_lifecycle_anchors", []),
            "ds_to_platform_talking_points": extra.get(
                "ds_to_platform_talking_points", []
            ),
            "global_engineering_anchors": extra.get(
                "global_engineering_anchors", []
            ),
            "global_engineering_talking_points": extra.get(
                "global_engineering_talking_points", []
            ),
            "productization_talking_points": extra.get(
                "productization_talking_points", []
            ),
            "productization_kpi_anchors": extra.get(
                "productization_kpi_anchors", []
            ),
            "executive_fit_thesis": extra.get(
                "executive_fit_thesis",
                f"{candidate_first_name} fits this role because they build "
                f"governed agentic systems where measurement intelligence "
                f"and platform reuse matter.",
            ),
            "executive_fit_proof_points": extra.get(
                "executive_fit_proof_points", []
            ),
            "executive_fit_close_patterns": extra.get(
                "executive_fit_close_patterns", []
            ),
            "cross_exam_depth_anchors": extra.get(
                "cross_exam_depth_anchors", []
            ),
            "questions_for_lead": extra.get("questions_for_lead", []),
            "questions_for_panel": extra.get("questions_for_panel", []),
            "plan_days_1_30": extra.get("plan_days_1_30", []),
            "plan_days_31_60": extra.get("plan_days_31_60", []),
            "plan_days_61_90": extra.get("plan_days_61_90", []),
            # Wave 3 — Glossary + Likely Questions cards.
            "glossary_entries": extra.get(
                "glossary_entries",
                list(interview.research.glossary_entries)
                if interview.research and interview.research.glossary_entries
                else [],
            ),
            "likely_questions": extra.get(
                "likely_questions",
                list(interview.research.likely_questions)
                if interview.research and interview.research.likely_questions
                else [],
            ),
        }
        return ctx

    def _write(self, path: Path, content: str) -> None:
        # Normalize line endings deterministically. The actual durable byte
        # write is delegated to the spine adapter (UWG), which gives us
        # atomic writes, mutation-ledger audit trail, and source-root
        # protection. apps_qna pack output lives in reports/qna/<slug>/,
        # which is not a UWG-protected source root.
        if self._config.line_ending == "lf":
            content = content.replace("\r\n", "\n")
        else:
            content = content.replace("\r\n", "\n").replace("\n", "\r\n")
        # Manifest is JSON; cards are markdown. Both flow through UWG via
        # the same write_card_text helper — the manifest helper is reserved
        # for the explicit pack_manifest.json call below.
        write_card_text(path, content, encoding="utf-8")

    def _build_manifest(
        self,
        interview: Interview,
        renders: list[CardRender],
        output_dir: Path,
    ) -> CardPackManifest:
        emitted = {r.filename for r in renders}
        routes_covered = [
            r.id for r in self._registry.routes if r.primary_card in emitted
        ]
        rendered_filenames = [r.filename for r in renders]
        pasted = self._compute_pasted_cards(rendered_filenames, interview)
        exceeds = len(pasted) > _CHATGPT_PROJECT_FILE_CAP
        if exceeds:
            _log.warning(
                "Paste manifest has %d cards, exceeding ChatGPT %d-file cap. "
                "Consider declaring interview.research.likely_questions to trim "
                "unused skill cards.",
                len(pasted),
                _CHATGPT_PROJECT_FILE_CAP,
            )
        return CardPackManifest(
            interview_slug=interview.slug,
            built_at=interview.build_metadata.built_at
            if interview.build_metadata.built_at
            else datetime.now(timezone.utc),
            builder_version=_BUILDER_VERSION,
            template_set_version=TEMPLATE_SET_VERSION,
            cards=rendered_filenames,
            routes_covered=routes_covered,
            interviewers=[i.name for i in interview.interviewers],
            pasted_cards=pasted,
            paste_exceeds_chatgpt_limit=exceeds,
        )

    def _compute_pasted_cards(
        self,
        rendered_filenames: list[str],
        interview: Interview,
    ) -> list[str]:
        """Multi-tier paste optimization (Anthropic Skills/Rules guideline).

        Tiers:
            - always_on    -> always paste
            - primary      -> paste only if its route is in likely_questions
            - specialist   -> paste only if its route is in likely_questions
            - post_rehearsal -> never paste (archive on disk only)

        Falls back to the full skill set when likely_questions is empty —
        the conservative default that preserves prior behavior.
        """
        # Build filename -> load_strategy from _CARD_SPECS, treating panel-mode
        # lens cards (03A_..., 03B_...) as inheriting card 03's strategy.
        load_strategy_by_file: dict[str, str] = {}
        for spec in _CARD_SPECS:
            filename, _, _, _, _, _, load_strategy = spec
            load_strategy_by_file[filename] = load_strategy

        def strategy_for(filename: str) -> str:
            if filename in load_strategy_by_file:
                return load_strategy_by_file[filename]
            # Panel-mode lens: 03A_INTERVIEWER_LENS_NAME.md -> "03_INTERVIEWER_LENS.md"
            if filename.startswith("03") and "_LENS" in filename:
                return load_strategy_by_file.get("03_INTERVIEWER_LENS.md", "always_on")
            return "always_on"  # safe default — never accidentally drop unknowns

        # Determine relevant routes for this interview.
        likely = (
            list(interview.research.likely_questions)
            if interview.research and interview.research.likely_questions
            else []
        )
        if likely:
            relevant_route_ids = {lq.route_id for lq in likely}
        else:
            # Conservative default — keep all skills.
            relevant_route_ids = {r.id for r in self._registry.routes}

        # Compute the set of skill cards reachable from the relevant routes.
        relevant_skill_cards: set[str] = set()
        for route in self._registry.routes:
            if route.id in relevant_route_ids:
                relevant_skill_cards.add(route.primary_card)
                relevant_skill_cards.update(route.optional_specialists)

        pasted: list[str] = []
        for filename in rendered_filenames:
            strategy = strategy_for(filename)
            if strategy == "post_rehearsal":
                continue  # archive on disk only — never in paste set
            if strategy == "always_on":
                pasted.append(filename)
                continue
            # primary / specialist: gated by route relevance
            if filename in relevant_skill_cards:
                pasted.append(filename)
        return pasted
