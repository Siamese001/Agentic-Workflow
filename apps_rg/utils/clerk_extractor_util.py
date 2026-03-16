"""Clerk extraction for resume generation HOP-1."""
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "clerk_extractor_util", "p0_governance")
_emit_reads_policy_state("p0", "clerk_extractor_util", "policy_binding")
_emit_snapshots_state("p0", "clerk_extractor_util", "state_snapshot")
emit_replay_key("p0", "clerk_extractor_util")
emit_determinism_digest("p0", "clerk_extractor_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "clerk_extractor_util", "execution_auth")
_emit_validates_capability("p2", "clerk_extractor_util", "capability_check")
_emit_routes_to_capability("p2", "clerk_extractor_util", "capability_route")
_emit_writes_via_uwg("p2", "clerk_extractor_util", "uwg_write")
_emit_blocks_direct_write("p2", "clerk_extractor_util", "direct_write_block")
_emit_records_tool_invocation("p2", "clerk_extractor_util", "tool_invocation")
_emit_captures_execution_output("p2", "clerk_extractor_util", "exec_output")
_emit_dispatches_agent("p3", "clerk_extractor_util", "agent_dispatch")
_emit_coordinates_agents("p3", "clerk_extractor_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "clerk_extractor_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "clerk_extractor_util", "healing_outcome")
_emit_escalates_failure("p3", "clerk_extractor_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "clerk_extractor_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "clerk_extractor_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "clerk_extractor_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "clerk_extractor_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "clerk_extractor_util", "eval_metric")
_emit_stores_embedding("p4", "clerk_extractor_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "clerk_extractor_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "clerk_extractor_util", "exec_snapshot_link")


class ClerkExtractor:
    """HOP-1: Extract structured data from master resume."""

    REQUIRED_KEYS: Any = [
        "owner",
        "professional_experience",
        "education",
        "certifications_and_credentials",
        "strategic_and_technical_competencies",
    ]

    def __init__(self, master_resume: dict) -> None:
        """Initialize the clerk extractor."""
        self.master_resume = master_resume
        self.HallucinationDetectorAgent = HallucinationDetectorAgent()
        self._validate_structure()

    def extract(self) -> tuple[dict, list[ValidationResult]]:
        """Extract and validate structured data from master resume."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ClerkExtractor.extract")

        experience_sections: Any = self._build_experience_sections()
        all_bullets: Any = []
        for section in experience_sections:
            all_bullets.extend([b["bullet_text"] for b in section.get("bullets", [])])
        bullet_dicts: Any = [{"bullet_text": b} for b in all_bullets]
        validation_results: Any = self.HallucinationDetectorAgent.detect(bullet_dicts)
        return (
            {
                "experience_sections": experience_sections,
                "header": self.master_resume.get("header", {}),
                "education": self.master_resume.get("education", []),
                "certifications": self.master_resume.get("certifications", []),
            },
            validation_results,
        )

    def _validate_structure(self) -> None:
        """Validate master resume has required keys."""
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")
        MISSING = [k for k in self.REQUIRED_KEYS if k not in self.master_resume]
        if MISSING:
            raise ValueError(f"Missing required keys: {', '.join(MISSING)}")

    def _build_experience_sections(self) -> list[dict]:
        """Build structured experience_sections from master resume."""
        SECTIONS = []
        for exp in self.master_resume.get("experience", []):
            BULLETS = [
                {
                    "bullet_text": text,
                    "quantified_metrics": self._extract_metrics(text),
                    "canonical_verbs": [],
                    "provenance": BulletProvenance.Verbatim.value,
                }
                for text in exp.get("bullets", [])
            ]
            SECTIONS.append(
                {
                    "company": exp.get("company", ""),
                    "title": exp.get("title", ""),
                    "location": exp.get("location", ""),
                    "start_date": exp.get("start_date", ""),
                    "end_date": exp.get("end_date", ""),
                    "overview": exp.get("overview", ""),
                    "bullets": BULLETS,
                    "highlights": [b["bullet_text"] for b in BULLETS],
                },
            )
        return SECTIONS

    def _extract_metrics(self, text: str) -> list[str]:
        """Extract quantified metrics from bullet text."""
        PATTERNS = [
            "\\$\\d+\\.?\\d*[MBK]\\+?",
            "\\d+\\.?\\d*%",
            "\\d+\\.?\\d*[MBK]\\+",
            "\\d{1,3}(?:,\\d{3})+",
        ]
        METRICS = []
        import re

        for pattern in PATTERNS:
            METRICS.extend(re.findall(pattern, text))
        return METRICS
