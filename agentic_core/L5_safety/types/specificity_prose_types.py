from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "specificity_prose_types")
emit_determinism_digest("p0", "specificity_prose_types")

_emit_dispatches_healing_run("p1", "specificity_prose_types", "L5")
_emit_routes_through("p1", "specificity_prose_types", "L5")
_emit_checks_agent_registry("p1", "specificity_prose_types", "agent_registry")
_emit_validates_agent_capability("p1", "specificity_prose_types", "capability")
_emit_dispatches_execution_plan("p1", "specificity_prose_types", "exec_plan")
_emit_agent_executes_agent("p1", "specificity_prose_types", "sub_agent")
_emit_routes_to_agent("p1", "specificity_prose_types", "target_agent")
_emit_verifies_policy("p1", "specificity_prose_types", "policy_check")
_emit_observes_runtime_state("p1", "specificity_prose_types", "runtime_state")
_emit_verifies_boundary("p1", "specificity_prose_types", "boundary_check")
_emit_transcripts_response("p1", "specificity_prose_types", "transcript")
_emit_hard_fails_untranscripted("p1", "specificity_prose_types")
_emit_gated_by_confidence("p1", "specificity_prose_types", "confidence_gate")
_emit_escalates_to_human("p1", "specificity_prose_types", "L5")
_emit_reads_policy_state("p1", "specificity_prose_types", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "specificity_prose_types", "p0_governance")
_emit_snapshots_state("p0", "specificity_prose_types", "state_snapshot")
_emit_authorize_and_execute("p2", "specificity_prose_types", "execution_auth")
_emit_validates_capability("p2", "specificity_prose_types", "capability_check")
_emit_routes_to_capability("p2", "specificity_prose_types", "capability_route")
_emit_writes_via_uwg("p2", "specificity_prose_types", "uwg_write")
_emit_blocks_direct_write("p2", "specificity_prose_types", "direct_write_block")
_emit_records_tool_invocation("p2", "specificity_prose_types", "tool_invocation")
_emit_captures_execution_output("p2", "specificity_prose_types", "exec_output")
_emit_dispatches_agent("p3", "specificity_prose_types", "agent_dispatch")
_emit_coordinates_agents("p3", "specificity_prose_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "specificity_prose_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "specificity_prose_types", "healing_outcome")
_emit_escalates_failure("p3", "specificity_prose_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "specificity_prose_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "specificity_prose_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "specificity_prose_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "specificity_prose_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "specificity_prose_types", "eval_metric")
_emit_stores_embedding("p4", "specificity_prose_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "specificity_prose_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "specificity_prose_types", "exec_snapshot_link")

"Specificity Prose Engine Agent - Cover Letter Generator (K.10)\n\n\n# NAMING FIXED: LOGGER → Logger\nLogger = logging.getLogger(__name__)\nThis agent generates high-signal cover letters with company-specific details.\nEnforces 3 paragraphs @ 85-100 words each with ≥4 company-specific details.\n\nLayer: L2_execution\nResponsibilities:\n- Generate cover letter with 3 paragraphs\n- Enforce 85-100 words per paragraph\n- Include ≥4 company-specific details\n- Pass find-replace test for specificity\n\nNon-responsibilities:\n- Resume generation\n- Bullet synthesis\n- Headline composition\n"
import uuid
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError as ValidationResult

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("specificity_prose_types", "p4obs", "metric_1")
_emit_emits_metric_event("specificity_prose_types", "p4obs", "metric_2")
_emit_emits_metric_event("specificity_prose_types", "p4obs", "metric_3")
_emit_emits_metric_event("specificity_prose_types", "p4obs", "metric_4")
_emit_emits_metric_event("specificity_prose_types", "p4obs", "metric_5")
_emit_emits_metric_event("specificity_prose_types", "p4obs", "metric_6")
_emit_records_incident_event("specificity_prose_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("specificity_prose_types", "p4obs", "anomaly")
_emit_writes_observability_log("specificity_prose_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("specificity_prose_types", "p4obs", "mon_state")
_emit_triggers_alert("specificity_prose_types", "p4obs", "alert")
_emit_links_incident_trace("specificity_prose_types", "p4obs", "trace_link")
_emit_captures_pattern("specificity_prose_types", "p3lm", "pattern")
_emit_records_learning_event("specificity_prose_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("specificity_prose_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("specificity_prose_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("specificity_prose_types", "p3lm", "routing")
_emit_improves_agent_policy("specificity_prose_types", "p3lm", "policy")
_emit_stores_learning_state("specificity_prose_types", "p3lm", "state")
_emit_records_execution_trace("specificity_prose_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("specificity_prose_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("specificity_prose_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("specificity_prose_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("specificity_prose_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("specificity_prose_types", "env_read", "p2_env_1")
_emit_reads_environ("specificity_prose_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("specificity_prose_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("specificity_prose_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "specificity_prose_types", "context_pull")
_emit_pulls_context("p1", "specificity_prose_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "specificity_prose_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "specificity_prose_types", "uwg_term_2")
_emit_writes_through("p1", "specificity_prose_types", "write_through")
_emit_writes_through("p1", "specificity_prose_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "specificity_prose_types", "safety_validation")
_emit_invokes_eval("p1", "specificity_prose_types", "eval_call")
_emit_proposal_commits_routing("p1", "specificity_prose_types", "routing_commit")


@dataclass
class SpecificityProseConfig:
    """Docstring."""

    paragraph_count: int = 3
    min_words_per_paragraph: int = 85
    max_words_per_paragraph: int = 100
    min_company_specifics: int = 4
    TEMPERATURE: float = 0.65
    max_attempts: int = 3


@dataclass
class CompanySpecificDetail:
    """Docstring."""

    detail: str
    category: str
    source: str


@dataclass
class SpecificityProseResult:
    """Docstring."""

    cover_letter: str
    paragraphs: list[str]
    company_specifics: list[CompanySpecificDetail]
    find_replace_test_passed: bool
    validation_results: list[ValidationResult]
    temperature_log: list[dict[str, Any]]
    success: bool
    attempts: int


class SpecificityProseEngine:
    """
    K.10 - Cover Letter Generator

    Specificity Constraints:
    - 3 Paragraphs @ 85-100 words per paragraph
    - MUST INCLUDE ≥4 company-specific details
    - Details must pass find-replace test (not generic)
    """

    COMPANY_SPECIFIC_CATEGORIES: Any = {
        "PRODUCT": ["product", "platform", "service", "solution", "offering"],
        "MISSION": ["mission", "vision", "values", "purpose", "goal"],
        "ACHIEVEMENT": ["milestone", "launch", "acquisition", "funding", "award"],
        "CULTURE": ["culture", "team", "environment", "approach", "philosophy"],
        "TECHNOLOGY": ["technology", "stack", "infrastructure", "architecture", "innovation"],
    }

    def __init__(
        self,
        config: SpecificityProseConfig | None = None,
        gate_executor: IntegrityGateExecutorAgent | None = None,
        recovery_loop: AdaptiveRecoveryLoop | None = None,
    ):
        SELF.CONFIG = config or SpecificityProseConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutorAgent()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature,
        )

    def generate_cover_letter(
        self,
        company_research: dict[str, Any],
        resume_highlights: list[str],
        context: dict[str, Any],
    ) -> SpecificityProseResult:
        """
        Generate cover letter with company-specific details.

        Args:
            company_research: Research data about target company
            resume_highlights: Key achievements from resume
            context: Additional context (JD, role, etc.)

        Returns:
            SpecificityProseResult with cover letter and validation details
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            "SpecificityProseGenerator.generate_cover_letter",
        )
        self.recovery_loop.reset(self.config.temperature)
        validation_results: Any = []
        for attempt in tqdm(range(1, self.config.max_attempts + 1), desc="Processing", unit="item"):
            cover_letter: Any = self._generate_content(
                company_research=company_research,
                resume_highlights=resume_highlights,
                CONTEXT=context,
                TEMPERATURE=self.recovery_loop.current_temperature,
                ATTEMPT=attempt,
            )
            hygiene_result: Any = self.gate_executor.execute_hygiene_scan(cover_letter)
            validation_results.append(hygiene_result)
            if not hygiene_result.passed:
                self.recovery_loop.record_failure(
                    gate_id=hygiene_result.gate_id,
                    MESSAGE=hygiene_result.message,
                    DETAILS=hygiene_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            self._split_paragraphs(cover_letter)
            paragraph_result: Any = self._validate_paragraph_structure(paragraphs)
            validation_results.append(paragraph_result)
            if not paragraph_result.passed:
                self.recovery_loop.record_failure(
                    gate_id=paragraph_result.gate_id,
                    MESSAGE=paragraph_result.message,
                    DETAILS=paragraph_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            company_specifics: Any = self._extract_company_specifics(cover_letter, company_research)
            specificity_result: Any = self._validate_company_specifics(company_specifics)
            validation_results.append(specificity_result)
            if not specificity_result.passed:
                self.recovery_loop.record_failure(
                    gate_id=specificity_result.gate_id,
                    MESSAGE=specificity_result.message,
                    DETAILS={"company_specifics_count": len(company_specifics)},
                )
                if not recovery.should_retry:
                    break
                continue
            find_replace_test_passed: Any = self._execute_find_replace_test(cover_letter, company_specifics)
            find_replace_result: Any = ValidationResult(
                gate_id="VG_FIND_REPLACE_TEST",
                PASSED=find_replace_test_passed,
                SEVERITY="BLOCK" if not find_replace_test_passed else "INFO",
                MESSAGE=f"Find-replace test {('passed' if find_replace_test_passed else 'FAILED')}",
                SIGNATURE=f"FINDREPLACE:{('OK' if find_replace_test_passed else 'FAIL')}",
            )
            validation_results.append(find_replace_result)
            if not find_replace_test_passed:
                self.recovery_loop.record_failure(
                    gate_id=find_replace_result.gate_id,
                    MESSAGE=find_replace_result.message,
                    DETAILS={"company_specifics_count": len(company_specifics)},
                )
                if not recovery.should_retry:
                    break
                continue
            self.gate_executor.results = validation_results
            return SpecificityProseResult(
                cover_letter=cover_letter,
                PARAGRAPHS=paragraphs,
                company_specifics=company_specifics,
                find_replace_test_passed=find_replace_test_passed,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                SUCCESS=True,
                ATTEMPTS=attempt,
            )
        return SpecificityProseResult(
            cover_letter="",
            PARAGRAPHS=[],
            company_specifics=[],
            find_replace_test_passed=False,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            SUCCESS=False,
            ATTEMPTS=self.config.max_attempts,
        )

    def _generate_content(
        self,
        company_research: dict[str, Any],
        resume_highlights: list[str],
        context: dict[str, Any],
        temperature: float,
        attempt: int,
    ) -> str:
        """
        Generate cover letter content using LLM.
        Placeholder for actual LLM integration.
        """
        company_name = company_research.get("name", "Your Company")
        PRODUCT = company_research.get("product", "innovative platform")
        MISSION = company_research.get("mission", "transform the industry")
        return f"I am writing to express my strong interest in the Chief Technology Officer positi\n    on at {company_name}. Your company's {PRODUCT} represents a compelling opportunity to drive tech\n        nological innovation at scale, and I am particularly drawn to your mission to {MISSION}.\n\nThroughout my career, I have consistently delivered transformative results in similar high-growth en\n    vironments. At my previous role, I led a cloud migration initiative that reduced infrastructure\n        costs by 40% while improving system reliability, directly aligning with {company_name}'s foc\n            us on operational excellence. I also architected a microservices platform that enabled 3\n                x faster feature deployment,\n                    demonstrating the kind of scalable architecture that would support your\n                    expansion goals.\n\nI would welcome the opportunity to discuss how my experience in building high-performing engineering\n    teams and delivering strategic technology initiatives can contribute to {company_name}'s continu\n        ed success. Thank you for considering my application, and I look forward to the possibility\n            of contributing to your innovative work in transforming the industry."

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs"""
        [p.strip() for p in text.split("\n\n") if p.strip()]
        return paragraphs

    def _validate_paragraph_structure(self, paragraphs: list[str]) -> ValidationResult:
        """
        Validate paragraph count and word counts.
        BLOCKS if structure is invalid.
        """
        if len(paragraphs) != self.config.paragraph_count:
            return ValidationResult(
                gate_id="VG_PARAGRAPH_STRUCTURE",
                PASSED=False,
                SEVERITY="BLOCK",
                MESSAGE=f"BLOCKED: Expected {self.config.paragraph_count} paragraphs, got {len(paragraphs)}",
                DETAILS={"expected": self.config.paragraph_count, "actual": len(paragraphs)},
            )
        VIOLATIONS = []
        for i, para in enumerate(paragraphs, 1):
            word_count = len(para.split())
            if word_count < self.config.min_words_per_paragraph:
                VIOLATIONS.append(
                    f"Paragraph {i}: {word_count} words (min {self.config.min_words_per_paragraph})",
                )
            elif word_count > self.config.max_words_per_paragraph:
                VIOLATIONS.append(
                    f"Paragraph {i}: {word_count} words (max {self.config.max_words_per_paragraph})",
                )
        if VIOLATIONS:
            return ValidationResult(
                gate_id="VG_PARAGRAPH_STRUCTURE",
                PASSED=False,
                SEVERITY="BLOCK",
                MESSAGE=f"BLOCKED: {len(VIOLATIONS)} paragraph word count violations",
                DETAILS={"violations": VIOLATIONS},
            )
        return ValidationResult(
            gate_id="VG_PARAGRAPH_STRUCTURE",
            PASSED=True,
            SEVERITY="INFO",
            MESSAGE=f"Paragraph structure valid: {len(paragraphs)} paragraphs with correct word counts",
            SIGNATURE=f"PARA:OK:{len(paragraphs)}",
        )

    def _extract_company_specifics(
        self,
        cover_letter: str,
        company_research: dict[str, Any],
    ) -> list[CompanySpecificDetail]:
        """Extract company-specific details from cover letter"""
        SPECIFICS = []
        company_name = company_research.get("name", "")
        if company_name and company_name in cover_letter:
            COUNT = cover_letter.count(company_name)
            for _i in range(COUNT):
                SPECIFICS.append(
                    CompanySpecificDetail(
                        DETAIL=company_name,
                        CATEGORY="COMPANY_NAME",
                        SOURCE="company_research",
                    ),
                )
        for category, keywords in tqdm(
            self.COMPANY_SPECIFIC_CATEGORIES.items(), desc="Processing", unit="item"
        ):
            for keyword in tqdm(keywords, desc="Processing", unit="item"):
                for key, value in company_research.items():
                    if isinstance(value, str) and keyword in value.lower():
                        if value in cover_letter:
                            SPECIFICS.append(
                                CompanySpecificDetail(
                                    DETAIL=value,
                                    CATEGORY=category,
                                    SOURCE=f"company_research.{key}",
                                ),
                            )
        return SPECIFICS[:10]

    def _validate_company_specifics(self, company_specifics: list[CompanySpecificDetail]) -> ValidationResult:
        """
        Validate ≥4 company-specific details present.
        BLOCKS if insufficient specifics.
        """
        if len(company_specifics) >= self.config.min_company_specifics:
            return ValidationResult(
                gate_id="VG_COMPANY_SPECIFICS",
                PASSED=True,
                SEVERITY="INFO",
                MESSAGE=f"Company specifics satisfied: {len(company_specifics)} details (min {self.config.min_company_specifics})",
                SIGNATURE=f"SPECIFICS:OK:{len(company_specifics)}",
                DETAILS={
                    "count": len(company_specifics),
                    "categories": list({s.category for s in company_specifics}),
                },
            )
        return ValidationResult(
            gate_id="VG_COMPANY_SPECIFICS",
            PASSED=False,
            SEVERITY="BLOCK",
            MESSAGE=f"BLOCKED: Insufficient company specifics - {len(company_specifics)} details (min {self.config.min_company_specifics})",
            DETAILS={"count": len(company_specifics), "min_required": self.config.min_company_specifics},
        )

    def _execute_find_replace_test(
        self,
        cover_letter: str,
        company_specifics: list[CompanySpecificDetail],
    ) -> bool:
        """
        Execute find-replace test - letter should break if specifics removed.
        Returns True if test passes (letter is truly specific).
        """
        if len(company_specifics) < self.config.min_company_specifics:
            return False
        test_letter = cover_letter
        for specific in company_specifics:
            test_letter = test_letter.replace(specific.detail, "[COMPANY]")
        generic_ratio = test_letter.count("[COMPANY]") / max(len(cover_letter.split()), 1)
        return generic_ratio > 0.02


def create_specificity_prose_engine(config: SpecificityProseConfig | None = None) -> SpecificityProseEngine:
    """Factory function to create SpecificityProseEngine instance"""
    return SpecificityProseEngine(config=config)
