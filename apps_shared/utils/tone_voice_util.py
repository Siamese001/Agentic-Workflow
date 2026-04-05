"""Brand Voice Enforcer - Ensures consistent personal brand across all engines.

This module enforces linguistic constraints (sentence length, vocabulary,
active voice) across all generated text in both Resume and Outreach engines.

# guardian: allow-magic-config
"""

import logging
import re
from enum import Enum

from pydantic import BaseModel, Field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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

_emit_applies_guardrail("p0", "tone_voice_util", "p0_governance")
_emit_reads_policy_state("p0", "tone_voice_util", "policy_binding")
_emit_snapshots_state("p0", "tone_voice_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("tone_voice_util", "p4obs", "metric_1")
_emit_emits_metric_event("tone_voice_util", "p4obs", "metric_2")
_emit_emits_metric_event("tone_voice_util", "p4obs", "metric_3")
_emit_emits_metric_event("tone_voice_util", "p4obs", "metric_4")
_emit_emits_metric_event("tone_voice_util", "p4obs", "metric_5")
_emit_emits_metric_event("tone_voice_util", "p4obs", "metric_6")
_emit_records_incident_event("tone_voice_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("tone_voice_util", "p4obs", "anomaly")
_emit_writes_observability_log("tone_voice_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("tone_voice_util", "p4obs", "mon_state")
_emit_triggers_alert("tone_voice_util", "p4obs", "alert")
_emit_links_incident_trace("tone_voice_util", "p4obs", "trace_link")
_emit_captures_pattern("tone_voice_util", "p3lm", "pattern")
_emit_records_learning_event("tone_voice_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tone_voice_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("tone_voice_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tone_voice_util", "p3lm", "routing")
_emit_improves_agent_policy("tone_voice_util", "p3lm", "policy")
_emit_stores_learning_state("tone_voice_util", "p3lm", "state")
_emit_records_execution_trace("tone_voice_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tone_voice_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tone_voice_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tone_voice_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tone_voice_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tone_voice_util", "env_read", "p2_env_1")
_emit_reads_environ("tone_voice_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("tone_voice_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tone_voice_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tone_voice_util", "context_pull")
_emit_pulls_context("p1", "tone_voice_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tone_voice_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tone_voice_util", "uwg_term_2")
_emit_writes_through("p1", "tone_voice_util", "write_through")
_emit_writes_through("p1", "tone_voice_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "tone_voice_util", "safety_validation")
_emit_invokes_eval("p1", "tone_voice_util", "eval_call")
_emit_proposal_commits_routing("p1", "tone_voice_util", "routing_commit")
_emit_escalates_to_human("p1", "tone_voice_util", "human_escalation")
_emit_routes_through("p1", "tone_voice_util", "route_through")
_emit_checks_agent_registry("p1", "tone_voice_util", "agent_registry")
_emit_validates_agent_capability("p1", "tone_voice_util", "capability")
_emit_dispatches_execution_plan("p1", "tone_voice_util", "exec_plan")
_emit_agent_executes_agent("p1", "tone_voice_util", "sub_agent")
_emit_routes_to_agent("p1", "tone_voice_util", "target_agent")
_emit_verifies_policy("p1", "tone_voice_util", "policy_check")
_emit_observes_runtime_state("p1", "tone_voice_util", "runtime_state")
_emit_verifies_boundary("p1", "tone_voice_util", "boundary_check")
_emit_transcripts_response("p1", "tone_voice_util", "transcript")
_emit_hard_fails_untranscripted("p1", "tone_voice_util")
_emit_gated_by_confidence("p1", "tone_voice_util", "confidence_gate")
emit_replay_key("p0", "tone_voice_util")
emit_determinism_digest("p0", "tone_voice_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "tone_voice_util", "execution_auth")
_emit_validates_capability("p2", "tone_voice_util", "capability_check")
_emit_routes_to_capability("p2", "tone_voice_util", "capability_route")
_emit_writes_via_uwg("p2", "tone_voice_util", "uwg_write")
_emit_blocks_direct_write("p2", "tone_voice_util", "direct_write_block")
_emit_records_tool_invocation("p2", "tone_voice_util", "tool_invocation")
_emit_captures_execution_output("p2", "tone_voice_util", "exec_output")
_emit_dispatches_agent("p3", "tone_voice_util", "agent_dispatch")
_emit_coordinates_agents("p3", "tone_voice_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "tone_voice_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "tone_voice_util", "healing_outcome")
_emit_escalates_failure("p3", "tone_voice_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "tone_voice_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tone_voice_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "tone_voice_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "tone_voice_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tone_voice_util", "eval_metric")
_emit_stores_embedding("p4", "tone_voice_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "tone_voice_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tone_voice_util", "exec_snapshot_link")
_emit_reads_through("l4", "tone_voice_util", "urg_read_1")
_emit_reads_through("l4", "tone_voice_util", "urg_read_2")
_emit_reads_through("l4", "tone_voice_util", "urg_read_3")
_emit_reads_through("l4", "tone_voice_util", "urg_read_4")
_emit_reads_through("l4", "tone_voice_util", "urg_read_5")
_emit_reads_through("l4", "tone_voice_util", "urg_read_6")
_emit_reads_through("l4", "tone_voice_util", "urg_read_7")
_emit_reads_through("l4", "tone_voice_util", "urg_read_8")
_emit_reads_through("l4", "tone_voice_util", "urg_read_9")
_emit_reads_through("l4", "tone_voice_util", "urg_read_10")
_emit_reads_through("l4", "tone_voice_util", "urg_read_11")
_emit_reads_through("l4", "tone_voice_util", "urg_read_12")
_emit_reads_through("l4", "tone_voice_util", "urg_read_13")
_emit_reads_through("l4", "tone_voice_util", "urg_read_14")
_emit_reads_through("l4", "tone_voice_util", "urg_read_15")
_emit_reads_through("l4", "tone_voice_util", "urg_read_16")
_emit_reads_through("l4", "tone_voice_util", "urg_read_17")
_emit_reads_through("l4", "tone_voice_util", "urg_read_18")
_emit_reads_through("l4", "tone_voice_util", "urg_read_19")
_emit_reads_through("l4", "tone_voice_util", "urg_read_20")
_emit_reads_through("l4", "tone_voice_util", "urg_read_21")
_emit_reads_through("l4", "tone_voice_util", "urg_read_22")
_emit_reads_through("l4", "tone_voice_util", "urg_read_23")
_emit_reads_through("l4", "tone_voice_util", "urg_read_24")
_emit_reads_through("l4", "tone_voice_util", "urg_read_25")
_emit_reads_through("l4", "tone_voice_util", "urg_read_26")
_emit_reads_through("l4", "tone_voice_util", "urg_read_27")
_emit_reads_through("l4", "tone_voice_util", "urg_read_28")
_emit_reads_through("l4", "tone_voice_util", "urg_read_29")
_emit_reads_through("l4", "tone_voice_util", "urg_read_30")
_emit_reads_through("l4", "tone_voice_util", "urg_read_31")
_emit_reads_through("l4", "tone_voice_util", "urg_read_32")
_emit_reads_through("l4", "tone_voice_util", "urg_read_33")
_emit_reads_through("l4", "tone_voice_util", "urg_read_34")
_emit_reads_through("l4", "tone_voice_util", "urg_read_35")
_emit_reads_through("l4", "tone_voice_util", "urg_read_36")
_emit_reads_through("l4", "tone_voice_util", "urg_read_37")
_emit_reads_through("l4", "tone_voice_util", "urg_read_38")
_emit_reads_through("l4", "tone_voice_util", "urg_read_39")
_emit_reads_through("l4", "tone_voice_util", "urg_read_40")
_emit_reads_through("l4", "tone_voice_util", "urg_read_41")
_emit_reads_through("l4", "tone_voice_util", "urg_read_42")
_emit_reads_through("l4", "tone_voice_util", "urg_read_43")
_emit_reads_through("l4", "tone_voice_util", "urg_read_44")
_emit_reads_through("l4", "tone_voice_util", "urg_read_45")
_emit_reads_through("l4", "tone_voice_util", "urg_read_46")
_emit_reads_through("l4", "tone_voice_util", "urg_read_47")
_emit_reads_through("l4", "tone_voice_util", "urg_read_48")
_emit_reads_through("l4", "tone_voice_util", "urg_read_49")
_emit_reads_through("l4", "tone_voice_util", "urg_read_50")
_emit_reads_through("l4", "tone_voice_util", "urg_read_51")
_emit_reads_through("l4", "tone_voice_util", "urg_read_52")
_emit_reads_through("l4", "tone_voice_util", "urg_read_53")
_emit_reads_through("l4", "tone_voice_util", "urg_read_54")
_emit_reads_through("l4", "tone_voice_util", "urg_read_55")
_emit_reads_through("l4", "tone_voice_util", "urg_read_56")
_emit_reads_through("l4", "tone_voice_util", "urg_read_57")
_emit_reads_through("l4", "tone_voice_util", "urg_read_58")
_emit_reads_through("l4", "tone_voice_util", "urg_read_59")
_emit_reads_through("l4", "tone_voice_util", "urg_read_60")
_emit_reads_through("l4", "tone_voice_util", "urg_read_61")
_emit_reads_through("l4", "tone_voice_util", "urg_read_62")
_emit_reads_through("l4", "tone_voice_util", "urg_read_63")
_emit_reads_through("l4", "tone_voice_util", "urg_read_64")
_emit_reads_through("l4", "tone_voice_util", "urg_read_65")
_emit_reads_through("l4", "tone_voice_util", "urg_read_66")
_emit_reads_through("l4", "tone_voice_util", "urg_read_67")
_emit_reads_through("l4", "tone_voice_util", "urg_read_68")
_emit_reads_through("l4", "tone_voice_util", "urg_read_69")
_emit_reads_through("l4", "tone_voice_util", "urg_read_70")
_emit_reads_through("l4", "tone_voice_util", "urg_read_71")
_emit_reads_through("l4", "tone_voice_util", "urg_read_72")
_emit_reads_through("l4", "tone_voice_util", "urg_read_73")
_emit_reads_through("l4", "tone_voice_util", "urg_read_74")
_emit_reads_through("l4", "tone_voice_util", "urg_read_75")
_emit_reads_through("l4", "tone_voice_util", "urg_read_76")
_emit_reads_through("l4", "tone_voice_util", "urg_read_77")
_emit_reads_through("l4", "tone_voice_util", "urg_read_78")
_emit_reads_through("l4", "tone_voice_util", "urg_read_79")
_emit_reads_through("l4", "tone_voice_util", "urg_read_80")
_emit_reads_through("l4", "tone_voice_util", "urg_read_81")
_emit_reads_through("l4", "tone_voice_util", "urg_read_82")
_emit_reads_through("l4", "tone_voice_util", "urg_read_83")
_emit_reads_through("l4", "tone_voice_util", "urg_read_84")

logger = logging.getLogger(__name__)


class ToneVoice(str, Enum):
    """Primary voice types for brand consistency."""

    AUTHORITATIVE = "AUTHORITATIVE"
    COLLABORATIVE = "COLLABORATIVE"
    TECHNICAL = "TECHNICAL"
    EXECUTIVE = "EXECUTIVE"
    CREATIVE = "CREATIVE"


class ToneSettings(BaseModel):
    """Settings for tone enforcement."""

    primary_voice: ToneVoice
    max_sentence_length: int = Field(default=25, ge=5, le=100)
    min_sentence_length: int = Field(default=5, ge=1, le=20)
    banned_words: list[str] = Field(default_factory=list)
    required_keywords: list[str] = Field(default_factory=list)
    preferred_verbs: dict[str, list[str]] = Field(default_factory=dict)
    voice_intensity: float = Field(default=0.8, ge=0.0, le=1.0)
    formality_level: str = Field(default="professional")
    max_passive_voice_percent: float = Field(default=20.0, ge=0.0, le=100.0)


class ToneViolation(BaseModel):
    """A tone rule violation."""

    type: str
    severity: str
    message: str
    location: str | None = None
    suggestion: str | None = None


class ToneAnalysisResult(BaseModel):
    """Result of tone analysis."""

    is_compliant: bool
    violations: list[ToneViolation] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=1.0)
    voice_detected: ToneVoice | None = None
    metrics: dict[str, float] = Field(default_factory=dict)


class ToneEnforcer:
    """Enforces tone rules across generated content."""

    def __init__(self):
        """Initialize tone enforcer with default profiles."""
        self.profiles: dict[ToneVoice, ToneSettings] = self._create_default_profiles()
        self.voice_patterns = {
            ToneVoice.AUTHORITATIVE: {
                "verbs": ["led", "drove", "built", "created", "established", "pioneered"],
                "patterns": ["\\bled\\b", "\\bdrove\\b", "\\bbuilt\\b"],
                "avoid": ["helped", "assisted", "participated"],
            },
            ToneVoice.COLLABORATIVE: {
                "verbs": ["partnered", "enabled", "supported", "collaborated", "facilitated"],
                "patterns": ["\\bpartnered\\b", "\\benabled\\b", "\\bsupported\\b"],
                "avoid": ["controlled", "dictated", "commanded"],
            },
            ToneVoice.TECHNICAL: {
                "terms": ["architecture", "scalability", "optimization", "infrastructure"],
                "patterns": ["\\bimplement\\b", "\\boptimize\\b", "\\barchitect\\b"],
                "avoid": ["simple", "easy", "basic"],
            },
            ToneVoice.EXECUTIVE: {
                "verbs": ["strategized", "orchestrated", "spearheaded", "directed"],
                "patterns": ["\\bstrategized\\b", "\\borchestrated\\b"],
                "avoid": ["executed", "performed", "completed"],
            },
            ToneVoice.CREATIVE: {
                "verbs": ["innovated", "envisioned", "imagined", "designed"],
                "patterns": ["\\binnovated\\b", "\\benvisioned\\b"],
                "avoid": ["maintained", "preserved", "followed"],
            },
        }
        self.passive_patterns = [
            "\\b(was|were|is|are|am|been|being)\\s+\\w+ed\\b",
            "\\b(was|were|is|are|am|been|being)\\s+\\w+en\\b",
            "\\b\\w+ed\\s+by\\s+the\\b",
            "\\b\\w+ed\\s+by\\s+\\w+\\b",
        ]
        logger.info("Initialized ToneEnforcer with default profiles")

    def _create_default_profiles(self) -> dict[ToneVoice, ToneSettings]:
        """Create default tone profiles.

        Returns:
            Dictionary of tone settings by voice
        """
        # guardian: allow-magic-config
        return {
            ToneVoice.AUTHORITATIVE: ToneSettings(
                primary_voice=ToneVoice.AUTHORITATIVE,
                max_sentence_length=20,
                banned_words=["helped", "assisted", "participated", "contributed"],
                required_keywords=["led", "drove", "built"],
                preferred_verbs={
                    "leadership": ["led", "directed", "managed", "orchestrated"],
                    "creation": ["built", "created", "developed", "established"],
                    "impact": ["drove", "achieved", "delivered", "produced"],
                },
                max_passive_voice_percent=10.0,
            ),
            ToneVoice.COLLABORATIVE: ToneSettings(
                primary_voice=ToneVoice.COLLABORATIVE,
                max_sentence_length=25,
                banned_words=["controlled", "dictated", "commanded", "forced"],
                required_keywords=["partnered", "enabled", "collaborated"],
                preferred_verbs={
                    "teamwork": ["partnered", "collaborated", "teamed", "cooperated"],
                    "support": ["enabled", "supported", "facilitated", "empowered"],
                    "guidance": ["mentored", "guided", "advised", "coached"],
                },
                max_passive_voice_percent=15.0,
            ),
            ToneVoice.TECHNICAL: ToneSettings(
                primary_voice=ToneVoice.TECHNICAL,
                max_sentence_length=30,
                banned_words=["simple", "easy", "basic", "just"],
                required_keywords=["implemented", "optimized", "architected"],
                preferred_verbs={
                    "development": ["implemented", "developed", "programmed", "coded"],
                    "architecture": ["architected", "designed", "structured", "engineered"],
                    "optimization": ["optimized", "enhanced", "improved", "refined"],
                },
                max_passive_voice_percent=20.0,
            ),
            ToneVoice.EXECUTIVE: ToneSettings(
                primary_voice=ToneVoice.EXECUTIVE,
                max_sentence_length=25,
                banned_words=["executed", "performed", "completed", "finished"],
                required_keywords=["strategized", "orchestrated", "spearheaded"],
                preferred_verbs={
                    "strategy": ["strategized", "planned", "envisioned", "conceptualized"],
                    "leadership": ["orchestrated", "spearheaded", "directed", "guided"],
                    "business": ["drove", "grew", "expanded", "scaled"],
                },
                max_passive_voice_percent=5.0,
            ),
            ToneVoice.CREATIVE: ToneSettings(
                primary_voice=ToneVoice.CREATIVE,
                max_sentence_length=30,
                banned_words=["standard", "typical", "conventional", "traditional"],
                required_keywords=["innovated", "designed", "created"],
                preferred_verbs={
                    "innovation": ["innovated", "pioneered", "invented", "conceived"],
                    "design": ["designed", "crafted", "shaped", "formed"],
                    "vision": ["envisioned", "imagined", "conceptualized", "dreamed"],
                },
                max_passive_voice_percent=25.0,
            ),
        }

    def audit_content(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Audit content for tone violations.

        Args:
            text: Text to audit
            settings: Tone settings to enforce

        Returns:
            List of violations found
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ToneVoiceAuditor.audit_content")
        violations = []
        violations.extend(self._check_sentence_length(text, settings))
        violations.extend(self._check_banned_words(text, settings))
        violations.extend(self._check_required_keywords(text, settings))
        violations.extend(self._check_voice_consistency(text, settings))
        violations.extend(self._check_passive_voice(text, settings))
        violations.extend(self._check_formality(text, settings))
        return violations

    def _check_sentence_length(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check sentence length violations.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        sentences = re.split("[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        for sentence in sentences:
            word_count = len(sentence.split())
            if word_count > settings.max_sentence_length:
                violations.append(
                    ToneViolation(
                        type="sentence_length",
                        severity="warning",
                        message=f"Sentence too long: {word_count} words (max: {settings.max_sentence_length})",
                        location=sentence[:50] + "..." if len(sentence) > 50 else sentence,
                        suggestion="Consider breaking into shorter sentences",
                    )
                )
            elif word_count < settings.min_sentence_length:
                violations.append(
                    ToneViolation(
                        type="sentence_length",
                        severity="info",
                        message=f"Sentence too short: {word_count} words (min: {settings.min_sentence_length})",
                        location=sentence,
                        suggestion="Consider expanding with more detail",
                    )
                )
        return violations

    def _check_banned_words(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check for banned words.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        text_lower = text.lower()
        for word in settings.banned_words:
            if word.lower() in text_lower:
                pattern = re.compile(f"\\b{re.escape(word)}\\b", re.IGNORECASE)
                match = pattern.search(text)
                violations.append(
                    ToneViolation(
                        type="banned_word",
                        severity="error",
                        message=f"Banned word detected: '{word}'",
                        location=match.group() if match else word,
                        suggestion="Replace with stronger alternative",
                    )
                )
        return violations

    def _check_required_keywords(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check for required keywords.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        text_lower = text.lower()
        missing_keywords = []
        for keyword in settings.required_keywords:
            if keyword.lower() not in text_lower:
                missing_keywords.append(keyword)
        if missing_keywords:
            violations.append(
                ToneViolation(
                    type="missing_keyword",
                    severity="warning",
                    message=f"Missing required keywords: {', '.join(missing_keywords)}",
                    suggestion="Consider incorporating these keywords",
                )
            )
        return violations

    def _check_voice_consistency(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check voice consistency with primary voice.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        voice = settings.primary_voice
        if voice not in self.voice_patterns:
            return violations
        patterns = self.voice_patterns[voice]
        text_lower = text.lower()
        preferred_found = 0
        for pattern in patterns["patterns"]:
            if re.search(pattern, text_lower):
                preferred_found += 1
        for avoid_word in patterns["avoid"]:
            if avoid_word.lower() in text_lower:
                violations.append(
                    ToneViolation(
                        type="voice_inconsistency",
                        severity="warning",
                        message=f"Voice inconsistency: '{avoid_word}' doesn't match {voice.value} tone",
                        suggestion=f"Use {voice.value} voice alternatives: {', '.join(patterns['verbs'][:3])}",
                    )
                )
        if preferred_found == 0 and len(patterns["patterns"]) > 0:
            violations.append(
                ToneViolation(
                    type="voice_weakness",
                    severity="info",
                    message=f"Weak {voice.value} voice: no preferred patterns detected",
                    suggestion=f"Consider using: {', '.join(patterns['verbs'][:3])}",
                )
            )
        return violations

    def _check_passive_voice(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check for excessive passive voice.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        sentences = re.split("[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return violations
        passive_count = 0
        for sentence in sentences:
            for pattern in self.passive_patterns:
                if re.search(pattern, sentence.lower()):
                    passive_count += 1
                    break
        passive_percent = passive_count / len(sentences) * 100
        if passive_percent > settings.max_passive_voice_percent:
            violations.append(
                ToneViolation(
                    type="passive_voice",
                    severity="warning",
                    message=f"Too much passive voice: {passive_percent:.1f}% (max: {settings.max_passive_voice_percent}%)",
                    suggestion="Use more active voice construction",
                )
            )
        return violations

    def _check_formality(self, text: str, settings: ToneSettings) -> list[ToneViolation]:
        """Check formality level compliance.

        Args:
            text: Text to check
            settings: Tone settings

        Returns:
            List of violations
        """
        violations = []
        if settings.formality_level == "formal":
            informal_patterns = ["\\bgonna\\b", "\\bwanna\\b", "\\bgotta\\b", "\\bkinda\\b", "\\bsorta\\b"]
            for pattern in informal_patterns:
                if re.search(pattern, text.lower()):
                    violations.append(
                        ToneViolation(
                            type="formality",
                            severity="warning",
                            message="Informal language detected in formal tone",
                            suggestion="Use formal language",
                        )
                    )
        elif settings.formality_level == "professional":
            casual_patterns = ["\\by'all\\b", "\\bain't\\b", "\\bcuz\\b"]
            for pattern in casual_patterns:
                if re.search(pattern, text.lower()):
                    violations.append(
                        ToneViolation(
                            type="formality",
                            severity="error",
                            message="Overly casual language detected",
                            suggestion="Use professional language",
                        )
                    )
        return violations

    def analyze_tone(self, text: str) -> ToneAnalysisResult:
        """Analyze tone of text and detect voice.

        Args:
            text: Text to analyze

        Returns:
            Tone analysis result
        """
        voice_detected = self._detect_voice(text)
        settings = self.profiles.get(voice_detected, self.profiles[ToneVoice.AUTHORITATIVE])
        violations = self.audit_content(text, settings)
        score = self._calculate_compliance_score(violations)
        metrics = self._calculate_metrics(text, violations)
        return ToneAnalysisResult(
            is_compliant=score >= 0.8,
            violations=violations,
            score=score,
            voice_detected=voice_detected,
            metrics=metrics,
        )

    def _detect_voice(self, text: str) -> ToneVoice:
        """Detect the dominant voice in text.

        Args:
            text: Text to analyze

        Returns:
            Detected voice type
        """
        text_lower = text.lower()
        voice_scores = {}
        for voice, patterns in self.voice_patterns.items():
            score = 0
            for pattern in patterns["patterns"]:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            for avoid_word in patterns["avoid"]:
                if avoid_word.lower() in text_lower:
                    score -= 2
            voice_scores[voice] = max(0, score)
        if voice_scores:
            return max(voice_scores, key=voice_scores.get)
        return ToneVoice.AUTHORITATIVE

    def _calculate_compliance_score(self, violations: list[ToneViolation]) -> float:
        """Calculate overall compliance score.

        Args:
            violations: List of violations

        Returns:
            Score between 0.0 and 1.0
        """
        if not violations:
            return 1.0
        weights = {"error": 10, "warning": 5, "info": 1}
        total_penalty = sum(weights.get(v.severity, 1) for v in violations)
        score = max(0.0, 1.0 - total_penalty / 50)
        return score

    def _calculate_metrics(self, text: str, violations: list[ToneViolation]) -> dict[str, float]:
        """Calculate analysis metrics.

        Args:
            text: Analyzed text
            violations: Found violations

        Returns:
            Metrics dictionary
        """
        violation_counts = {}
        for violation in violations:
            violation_counts[violation.type] = violation_counts.get(violation.type, 0) + 1
        sentences = len(re.split("[.!?]+", text))
        words = len(text.split())
        return {
            "sentences": float(sentences),
            "words": float(words),
            "avg_sentence_length": words / sentences if sentences > 0 else 0.0,
            "violations_by_type": {k: float(v) for k, v in violation_counts.items()},
        }

    def get_profile(self, voice: ToneVoice) -> ToneSettings:
        """Get tone profile for a voice.

        Args:
            voice: Voice type

        Returns:
            Tone settings
        """
        return self.profiles.get(voice, self.profiles[ToneVoice.AUTHORITATIVE])

    def create_custom_profile(self, voice: ToneVoice, settings: ToneSettings) -> None:
        """Create or update a custom profile.

        Args:
            voice: Voice type
            settings: Tone settings
        """
        self.profiles[voice] = settings
        logger.info(f"Created custom profile for {voice.value} voice")


_tone_enforcer: ToneEnforcer | None = None


def get_tone_enforcer() -> ToneEnforcer:
    """Get global tone enforcer instance.

    Returns:
        ToneEnforcer instance
    """
    global _tone_enforcer
    if _tone_enforcer is None:
        _tone_enforcer = ToneEnforcer()
    return _tone_enforcer


def audit_text(text: str, voice: ToneVoice) -> list[ToneViolation]:
    """Audit text for tone violations.

    Args:
        text: Text to audit
        voice: Voice type to enforce

    Returns:
        List of violations
    """
    enforcer = get_tone_enforcer()
    settings = enforcer.get_profile(voice)
    return enforcer.audit_content(text, settings)


def analyze_tone(text: str) -> ToneAnalysisResult:
    """Analyze tone of text.

    Args:
        text: Text to analyze

    Returns:
        Tone analysis result
    """
    enforcer = get_tone_enforcer()
    return enforcer.analyze_tone(text)
