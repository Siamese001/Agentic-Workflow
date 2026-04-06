from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Strategist BioWriter Agent - Executive Summary Generator (K.1)


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This agent generates executive summaries with zero-tolerance validation.
Enforces strict word count, voice constraints, and grounding requirements.

Layer: L2_execution
Responsibilities:
- Generate executive summary from bullet pool
- Enforce 118-135 word count (strict)
- Block first-person pronouns (I, My, We)
- Validate all claims against evidence

Non-responsibilities:
- Headline generation
- Bullet synthesis
- Gap analysis
"""
import re
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
    _emit_signs_execution_trace,
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

# [SSOT IMPORT] Structure blueprint is the single source of truth


@dataclass
class BioWriterConfig:
    """TODO: Add docstring."""

    min_words: int = 118
    max_words: int = 135
    VOICE: str = "THIRD_PERSON_IMPLIED"
    TEMPERATURE: float = 0.6
    max_attempts: int = 3


class BioWriterResult:
    """Docstring."""

    summary: str
    word_count: int
    validation_results: list[ValidationResult]
    temperature_log: list[dict[str, Any]]
    success: bool
    attempts: int


class StrategistBioWriter:
    """
    K.1 - Executive Summary Generator

    Zero Tolerance Constraints:
    - Length: Strict 118-135 words
    - Voice: Third-Person Implied ONLY (block I/My/We)
    - Grounding: All claims must exist in Bullet_Pool
    """

    FIRST_PERSON_PATTERNS: Any = [
        "\\bI\\b",
        "\\bmy\\b",
        "\\bme\\b",
        "\\bmine\\b",
        "\\bwe\\b",
        "\\bour\\b",
        "\\bus\\b",
        "\\bours\\b",
    ]

    def __init__(
        self,
        config: BioWriterConfig | None = None,
        gate_executor: IntegrityGateExecutorAgent | None = None,
        recovery_loop: AdaptiveRecoveryLoop | None = None,
    ):
        self.config = config or BioWriterConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutorAgent()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature,
        )

    def generate_summary(self, bullet_pool: list[str], context: dict[str, Any]) -> BioWriterResult:
        """
        Generate executive summary with validation loop.

        Args:
            bullet_pool: List of achievement bullets for grounding
            context: Additional context (JD, industry, etc.)

        Returns:
            BioWriterResult with summary and validation details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "StrategistBioWriter.generate_summary"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:StrategistBioWriter.generate_summary".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.recovery_loop.reset(self.config.temperature)
        validation_results: Any = []
        for attempt in range(1, self.config.max_attempts + 1):
            summary: Any = self._generate_content(
                bullet_pool=bullet_pool,
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt,
            )
            hygiene_result: Any = self.gate_executor.execute_hygiene_scan(summary)
            validation_results.append(hygiene_result)
            if not hygiene_result.passed:
                recovery: Any = self.recovery_loop.record_failure(
                    gate_id=hygiene_result.gate_id,
                    message=hygiene_result.message,
                    details=hygiene_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            voice_result: Any = self._validate_voice(summary)
            validation_results.append(voice_result)
            if not voice_result.passed:
                recovery: Any = self.recovery_loop.record_failure(
                    gate_id=voice_result.gate_id,
                    message=voice_result.message,
                    details=voice_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            word_count_result: Any = self.gate_executor.execute_word_count_gate(
                content=summary,
                min_words=self.config.min_words,
                max_words=self.config.max_words,
                gate_id="VG_MANDATORY_WORD_COUNT_COMPLIANCE",
            )
            validation_results.append(word_count_result)
            if not word_count_result.passed:
                recovery: Any = self.recovery_loop.record_failure(
                    gate_id=word_count_result.gate_id,
                    message=word_count_result.message,
                    details=word_count_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            grounding_result: Any = self.gate_executor.execute_grounding_check(
                content=summary,
                evidence_pool=bullet_pool,
                gate_id="VG_SUMMARY_GROUNDING_CHECK",
            )
            validation_results.append(grounding_result)
            if not grounding_result.passed:
                recovery: Any = self.recovery_loop.record_failure(
                    gate_id=grounding_result.gate_id,
                    message=grounding_result.message,
                    details=grounding_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            self.gate_executor.results = validation_results
            return BioWriterResult(
                summary=summary,
                word_count=len(summary.split()),
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt,
            )
        return BioWriterResult(
            summary="",
            word_count=0,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts,
        )

    def _generate_content(
        self,
        bullet_pool: list[str],
        context: dict[str, Any],
        temperature: float,
        attempt: int,
    ) -> str:
        """
        Generate summary content using LLM.
        This is a placeholder - actual implementation would call LLM.
        """
        self._build_prompt(bullet_pool, context, attempt)
        return f"Placeholder summary for attempt {attempt} at temp {temperature}"

    def _build_prompt(self, bullet_pool: list[str], context: dict[str, Any], attempt: int) -> str:
        """Build prompt for summary generation"""
        evidence_section = "\n".join(f"- {bullet}" for bullet in bullet_pool[:10])
        prompt = f"""Generate an executive summary for a resume.\n\nSTRICT REQUIREMENTS:\n1. Word Count: EXACTLY 118-135 words (count carefully)\n2. Voice: Third-person implied ONLY (NO "I", "my", "we", "our")\n3. Grounding: Every Claim must come from the evidence below\n4. Style: Professional, specific, achievement-focused\n\nEVIDENCE POOL:\n{evidence_section}\n\nTARGET INDUSTRY: {context.get("industry", "Technology")}\nSENIORITY: {context.get("seniority", "Senior")}\n\nATTEMPT: {attempt}/3\n\nGenerate the executive summary now:"""
        return prompt

    def _validate_voice(self, content: str) -> ValidationResult:
        """
        Validate third-person voice constraint.
        BLOCKS if first-person pronouns detected.
        """
        violations = []
        for pattern in self.FIRST_PERSON_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append(
                    {
                        "pronoun": match.group(),
                        "position": match.start(),
                        "context": content[max(0, match.start() - 20) : match.end() + 20],
                    },
                )
        if violations:
            return ValidationResult(
                gate_id="VG_THIRD_PERSON_VOICE",
                passed=False,
                Severity="BLOCK",
                message=f"BLOCKED: {len(violations)} first-person pronouns detected",
                details={"violations": violations[:5]},
            )
        return ValidationResult(
            gate_id="VG_THIRD_PERSON_VOICE",
            passed=True,
            Severity="INFO",
            message="Voice constraint satisfied - third-person only",
            signature=f"VOICE:OK:{hash(content) % 10000}",
        )


def create_strategist_biowriter(config: BioWriterConfig | None = None) -> StrategistBioWriter:
    """Factory function to create StrategistBioWriter instance"""
    return StrategistBioWriter(config=config)
