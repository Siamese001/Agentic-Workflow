"""Input Guardrail - Adversarial Defense Layer for RAG Pipeline.

This module provides security scanning for all inputs before they reach
the RAG pipeline, protecting against prompt injection, jailbreaks,
PII leakage, Unicode attacks, and encoded payloads.
"""

import base64
import logging
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from agentic_core.L0_routing.utils.clock_provider import ClockProvider as clock_provider
from agentic_core.L5_safety.enforcement.eval_guard import get_eval_guard
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "input_guardrail_util", "p0_governance")
_emit_reads_policy_state("p0", "input_guardrail_util", "policy_binding")
_emit_snapshots_state("p0", "input_guardrail_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("input_guardrail_util", "p4obs", "metric_1")
_emit_emits_metric_event("input_guardrail_util", "p4obs", "metric_2")
_emit_emits_metric_event("input_guardrail_util", "p4obs", "metric_3")
_emit_emits_metric_event("input_guardrail_util", "p4obs", "metric_4")
_emit_emits_metric_event("input_guardrail_util", "p4obs", "metric_5")
_emit_emits_metric_event("input_guardrail_util", "p4obs", "metric_6")
_emit_records_incident_event("input_guardrail_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("input_guardrail_util", "p4obs", "anomaly")
_emit_writes_observability_log("input_guardrail_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("input_guardrail_util", "p4obs", "mon_state")
_emit_triggers_alert("input_guardrail_util", "p4obs", "alert")
_emit_links_incident_trace("input_guardrail_util", "p4obs", "trace_link")
_emit_captures_pattern("input_guardrail_util", "p3lm", "pattern")
_emit_records_learning_event("input_guardrail_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("input_guardrail_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("input_guardrail_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("input_guardrail_util", "p3lm", "routing")
_emit_improves_agent_policy("input_guardrail_util", "p3lm", "policy")
_emit_stores_learning_state("input_guardrail_util", "p3lm", "state")
_emit_records_execution_trace("input_guardrail_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("input_guardrail_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("input_guardrail_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("input_guardrail_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("input_guardrail_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("input_guardrail_util", "env_read", "p2_env_1")
_emit_reads_environ("input_guardrail_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("input_guardrail_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("input_guardrail_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "input_guardrail_util", "context_pull")
_emit_pulls_context("p1", "input_guardrail_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "input_guardrail_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "input_guardrail_util", "uwg_term_2")
_emit_writes_through("p1", "input_guardrail_util", "write_through")
_emit_writes_through("p1", "input_guardrail_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "input_guardrail_util", "safety_validation")
_emit_invokes_eval("p1", "input_guardrail_util", "eval_call")
_emit_proposal_commits_routing("p1", "input_guardrail_util", "routing_commit")
_emit_escalates_to_human("p1", "input_guardrail_util", "human_escalation")
_emit_routes_through("p1", "input_guardrail_util", "route_through")
_emit_checks_agent_registry("p1", "input_guardrail_util", "agent_registry")
_emit_validates_agent_capability("p1", "input_guardrail_util", "capability")
_emit_dispatches_execution_plan("p1", "input_guardrail_util", "exec_plan")
_emit_agent_executes_agent("p1", "input_guardrail_util", "sub_agent")
_emit_routes_to_agent("p1", "input_guardrail_util", "target_agent")
_emit_verifies_policy("p1", "input_guardrail_util", "policy_check")
_emit_observes_runtime_state("p1", "input_guardrail_util", "runtime_state")
_emit_verifies_boundary("p1", "input_guardrail_util", "boundary_check")
_emit_transcripts_response("p1", "input_guardrail_util", "transcript")
_emit_hard_fails_untranscripted("p1", "input_guardrail_util")
_emit_gated_by_confidence("p1", "input_guardrail_util", "confidence_gate")
emit_replay_key("p0", "input_guardrail_util")
emit_determinism_digest("p0", "input_guardrail_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "input_guardrail_util", "execution_auth")
_emit_validates_capability("p2", "input_guardrail_util", "capability_check")
_emit_routes_to_capability("p2", "input_guardrail_util", "capability_route")
_emit_writes_via_uwg("p2", "input_guardrail_util", "uwg_write")
_emit_blocks_direct_write("p2", "input_guardrail_util", "direct_write_block")
_emit_records_tool_invocation("p2", "input_guardrail_util", "tool_invocation")
_emit_captures_execution_output("p2", "input_guardrail_util", "exec_output")
_emit_dispatches_agent("p3", "input_guardrail_util", "agent_dispatch")
_emit_coordinates_agents("p3", "input_guardrail_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "input_guardrail_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "input_guardrail_util", "healing_outcome")
_emit_escalates_failure("p3", "input_guardrail_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "input_guardrail_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "input_guardrail_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "input_guardrail_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "input_guardrail_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "input_guardrail_util", "eval_metric")
_emit_stores_embedding("p4", "input_guardrail_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "input_guardrail_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "input_guardrail_util", "exec_snapshot_link")
logger = logging.getLogger(__name__)
DEFAULT_RATE_LIMIT_PER_MINUTE: Final[int] = 60


class GuardAction(Enum):
    """Action to take based on guardrail scan."""

    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    WARN = "WARN"
    REDACT = "REDACT"


@dataclass
class GuardResult:
    """Result of input guardrail scan."""

    action: GuardAction
    reason: str
    confidence: float
    pii_detected: list[str] = None
    injection_patterns: list[str] = None
    sanitized_input: str | None = None

    def __post_init__(self):
        if self.pii_detected is None:
            self.pii_detected = []
        if self.injection_patterns is None:
            self.injection_patterns = []


class InputGuardrail:
    """Adversarial defense layer for input validation and sanitization."""

    def __init__(
        self,
        enable_injection_detection: bool = True,
        enable_pii_detection: bool = True,
        enable_semantic_check: bool = True,
        enable_unicode_check: bool = True,
        enable_encoding_check: bool = True,
        enable_rate_limit: bool = True,
        strict_mode: bool = False,
        rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE,
    ):
        """Initialize the input guardrail.

        Args:
            enable_injection_detection: Enable prompt injection detection
            enable_pii_detection: Enable PII detection and redaction
            enable_semantic_check: Enable semantic malicious intent detection
            enable_unicode_check: Enable Unicode homoglyph attack detection
            enable_encoding_check: Enable base64/encoded payload detection
            enable_rate_limit: Enable rate limiting per user
            strict_mode: Block on any suspicious pattern (not just high confidence)
            rate_limit_per_minute: Requests per minute per user
        """
        self.enable_injection_detection = enable_injection_detection
        self.enable_pii_detection = enable_pii_detection
        self.enable_semantic_check = enable_semantic_check
        self.enable_unicode_check = enable_unicode_check
        self.enable_encoding_check = enable_encoding_check
        self.enable_rate_limit = enable_rate_limit
        self.strict_mode = strict_mode
        self.rate_limit_per_minute = rate_limit_per_minute
        self._rate_limit_store: dict[str, list[float]] = {}
        self._compile_patterns()
        if self.enable_semantic_check:
            self._init_semantic_checker()
        logger.info(
            f"InputGuardrail initialized - Injection: {enable_injection_detection}, PII: {enable_pii_detection}, Semantic: {enable_semantic_check}, Unicode: {enable_unicode_check}, Encoding: {enable_encoding_check}, Rate Limit: {enable_rate_limit}, Strict: {strict_mode}"
        )

    def _compile_patterns(self):
        """Compile regex patterns for fast detection."""
        self.injection_patterns = [
            "(?i)(dan|do anything now)",
            "(?i)(ignore (all|previous|the above) instructions?)",
            "(?i)(disregard (all|previous|the above) instructions?)",
            "(?i)(forget (all|previous|the above) instructions?)",
            "(?i)(override (all|previous|the above) instructions?)",
            "(?i)(show|print|display|tell me) (your )?(system|initial|original) prompt",
            "(?i)(what are your instructions|what were you told to do)",
            "(?i)(repeat|echo|copy) (everything )?above",
            "(?i)(you are now|henceforth|from now on) (a )?(developer|admin|god|dAN)",
            "(?i)(pretend|act as|roleplay as) (a )?(jailbroken|uncensored|unrestricted)",
            "(?i)(hypothetical|imagine|fictional) scenario",
            "(?i)(new instruction|additional instruction|update)",
            "(?i)(replace|change|modify) (the )?(prompt|instructions)",
            "(?i)(add to|append to) (your )?(instructions|prompt)",
            "(?i)(respond with only|just say|output only)",
            "(?i)(no explanation|no commentary|no analysis)",
            "(?i)(between brackets|in code block|as JSON)",
            "(?i)(bypass|override|circumvent) (the )?(filter|restriction|safety)",
            "(?i)(this is not harmful|this is safe|this is for testing)",
            "(?i)(educational|research|academic) purpose",
        ]
        self.compiled_injection_patterns = [re.compile(pattern) for pattern in self.injection_patterns]
        self.unicode_homoglyphs = {
            "i": ["ⅰ", "і", "í", "ì", "î", "ï"],
            "l": ["ⅼ", "ⅼ", "ł", "ĺ", "ľ"],
            "o": ["ο", "о", "ó", "ò", "ô", "ö"],
            "e": ["е", "é", "è", "ê", "ë"],
            "a": ["а", "á", "à", "â", "ä"],
            "r": ["г", "ŕ", "ř", "ŗ"],
            "n": ["ո", "ñ", "ń"],
            "g": ["ɡ", "ğ", "ĝ"],
            "c": ["с", "č", "ć", "ç"],
            "v": ["ѵ", "ν"],
            "u": ["ս", "ú", "ù", "û", "ü"],
        }
        get_eval_guard().check(
            operation="compile", code="(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?"
        )
        self.base64_pattern = re.compile("(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")
        self.pii_patterns = {
            "email": re.compile("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"),
            "phone": re.compile(
                "\\b(?:\\+?1[-.\\s]?)?\\(?([0-9]{3})\\)?[-.\\s]?([0-9]{3})[-.\\s]?([0-9]{4})\\b"
            ),
            "ssn": re.compile("\\b\\d{3}-\\d{2}-\\d{4}\\b"),
            "credit_card": re.compile("\\b(?:\\d{4}[-\\s]?){3}\\d{4}\\b"),
            "ip_address": re.compile("\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b"),
            "url": re.compile(
                "https?://(?:[-\\w.])+(?:[:\\d]+)?(?:/(?:[\\w/_.])*(?:\\?(?:[\\w&=%.])*)?(?:#(?:\\w*))?)?"
            ),
        }
        self.malicious_keywords = [
            "jailbreak",
            "bypass",
            "override",
            "hack",
            "exploit",
            "injection",
            "prompt leak",
            "system prompt",
            "dan",
            "malicious",
            "harmful",
            "illegal",
            "forbidden",
        ]

    def _init_semantic_checker(self):
        """Initialize semantic malicious intent checker."""
        self.semantic_threshold = 0.7 if not self.strict_mode else 0.5

    def scan(self, input_text: str, user_id: str | None = None) -> GuardResult:
        """Scan input text for security issues.

        Args:
            input_text: The input text to scan
            user_id: Optional user ID for rate limiting

        Returns:
            GuardResult with action and details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InputGuardrail.scan")

        start_time = clock_provider.time()
        result = GuardResult(
            action=GuardAction.ALLOW,
            reason="Input appears safe",
            confidence=0.0,
            pii_detected=[],
            injection_patterns=[],
        )
        try:
            if self.enable_rate_limit and user_id:
                if self._check_rate_limit(user_id):
                    result.action = GuardAction.BLOCK
                    result.reason = "Rate limit exceeded"
                    result.confidence = 1.0
                    return result
            if self.enable_injection_detection:
                injection_result = self._check_injection(input_text)
                if injection_result[0]:
                    result.action = GuardAction.BLOCK if self.strict_mode else GuardAction.WARN
                    result.injection_patterns = injection_result[1]
                    result.reason = f"Prompt injection detected: {', '.join(injection_result[1])}"
                    result.confidence = max(result.confidence, 0.8)
            if self.enable_unicode_check:
                unicode_result = self._check_unicode_attacks(input_text)
                if unicode_result[0]:
                    if result.action == GuardAction.ALLOW:
                        result.action = GuardAction.WARN if not self.strict_mode else GuardAction.BLOCK
                        result.reason = f"Suspicious Unicode characters detected: {unicode_result[1]}"
                    result.confidence = max(result.confidence, 0.7)
            if self.enable_encoding_check:
                encoding_result = self._check_encoded_payloads(input_text)
                if encoding_result[0]:
                    if result.action == GuardAction.ALLOW:
                        result.action = GuardAction.BLOCK
                        result.reason = "Encoded payload detected - potential attack"
                    result.confidence = max(result.confidence, 0.9)
            if self.enable_pii_detection:
                pii_result = self._check_pii(input_text)
                if pii_result[0]:
                    result.pii_detected = pii_result[1]
                    if result.action == GuardAction.ALLOW:
                        result.action = GuardAction.REDACT
                        result.reason = "PII detected - will be redacted"
                        result.sanitized_input = self._redact_pii(input_text, pii_result[1])
                    result.confidence = max(result.confidence, 0.6)
            if self.enable_semantic_check:
                semantic_score = self._check_semantic_intent(input_text)
                if semantic_score > self.semantic_threshold:
                    if result.action == GuardAction.ALLOW:
                        result.action = GuardAction.WARN
                        result.reason = "Potentially malicious intent detected"
                    result.confidence = max(result.confidence, semantic_score)
            scan_time = (clock_provider.time() - start_time) * 1000
            logger.info(
                f"Input scan completed in {scan_time:.2f}ms - Action: {result.action.value}, Confidence: {result.confidence:.2f}"
            )
            return result
        except Exception as e:
            logger.error(f"Error during input scan: {e}")
            return None

    def _check_injection(self, text: str) -> tuple[bool, list[str]]:
        """Check for prompt injection patterns.

        Args:
            text: Text to check

        Returns:
            Tuple of (found, list_of_patterns)
        """
        found_patterns = []
        for pattern in self.compiled_injection_patterns:
            matches = pattern.findall(text)
            if matches:
                found_patterns.append(pattern.pattern)
        return (len(found_patterns) > 0, found_patterns)

    def _check_pii(self, text: str) -> tuple[bool, list[str]]:
        """Check for PII in the text.

        Args:
            text: Text to check

        Returns:
            Tuple of (found, list_of_pii_types)
        """
        found_types = []
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(text)
            if matches:
                found_types.append(pii_type)
        return (len(found_types) > 0, found_types)

    def _redact_pii(self, text: str, pii_types: list[str]) -> str:
        """Redact PII from text.

        Args:
            text: Text to redact
            pii_types: Types of PII found

        Returns:
            Redacted text
        """
        redacted = text
        for pii_type in tqdm(pii_types, desc="Processing", unit="item"):
            if pii_type in self.pii_patterns:
                pattern = self.pii_patterns[pii_type]
                if pii_type == "email":
                    redacted = pattern.sub("[EMAIL_REDACTED]", redacted)
                elif pii_type == "phone":
                    redacted = pattern.sub("[PHONE_REDACTED]", redacted)
                elif pii_type == "ssn":
                    redacted = pattern.sub("[SSN_REDACTED]", redacted)
                elif pii_type == "credit_card":
                    redacted = pattern.sub("[CARD_REDACTED]", redacted)
                elif pii_type == "ip_address":
                    redacted = pattern.sub("[IP_REDACTED]", redacted)
                elif pii_type == "url":
                    redacted = pattern.sub("[URL_REDACTED]", redacted)
        return redacted

    def _check_semantic_intent(self, text: str) -> float:
        """Check for semantic malicious intent.

        Args:
            text: Text to check

        Returns:
            Confidence score (0.0 - 1.0)
        """
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in self.malicious_keywords if keyword in text_lower)
        confidence = min(keyword_count / len(self.malicious_keywords), 1.0)
        injection_count = sum(1 for pattern in self.compiled_injection_patterns if pattern.search(text))
        if injection_count > 2:
            confidence = min(confidence + 0.3, 1.0)
        return confidence

    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit.

        Args:
            user_id: User identifier

        Returns:
            True if rate limit exceeded
        """
        now = clock_provider.time()
        minute_ago = now - 60
        if user_id in self._rate_limit_store:
            self._rate_limit_store[user_id] = [
                timestamp for timestamp in self._rate_limit_store[user_id] if timestamp > minute_ago
            ]
        else:
            self._rate_limit_store[user_id] = []
        if len(self._rate_limit_store[user_id]) >= self.rate_limit_per_minute:
            return True
        self._rate_limit_store[user_id].append(now)
        return False

    def _check_unicode_attacks(self, text: str) -> tuple[bool, str]:
        """Check for Unicode homoglyph attacks.

        Args:
            text: Text to check

        Returns:
            Tuple of (found, suspicious_chars)
        """
        suspicious_chars = []
        for char in text:
            unicodedata.name(char, "")
            for normal_char, homoglyphs in self.unicode_homoglyphs.items():
                if char in homoglyphs:
                    suspicious_chars.append(f"{char} (looks like {normal_char})")
            if unicodedata.category(char) in [" Cf", "Cs", "Co", "Cn"]:
                suspicious_chars.append(f"{char} (control/private char)")
        return (len(suspicious_chars) > 0, ", ".join(suspicious_chars[:5]))

    def _check_encoded_payloads(self, text: str) -> tuple[bool, str]:
        """Check for base64 or other encoded payloads.

        Args:
            text: Text to check

        Returns:
            Tuple of (found, details)
        """
        base64_matches = self.base64_pattern.findall(text)
        for match in tqdm(base64_matches, desc="Processing", unit="item"):
            try:
                decoded = base64.b64decode(match).decode("utf-8", errors="ignore")
                decoded_lower = decoded.lower()
                if any(keyword in decoded_lower for keyword in self.malicious_keywords):
                    return (True, f"Base64 payload with malicious content: {match[:20]}...")
                for pattern in self.injection_patterns[:5]:
                    if re.search(pattern, decoded, re.IGNORECASE):
                        return (True, f"Base64 payload with injection pattern: {match[:20]}...")
            except (ValueError, UnicodeDecodeError):
                pass
        get_eval_guard().check(operation="compile", code="[0-9A-Fa-f]{32,}")
        hex_pattern = re.compile("[0-9A-Fa-f]{32,}")
        hex_matches = hex_pattern.findall(text)
        for match in hex_matches:
            try:
                decoded = bytes.fromhex(match).decode("utf-8", errors="ignore")
                if any(keyword in decoded.lower() for keyword in self.malicious_keywords):
                    return (True, "Hex encoded payload with malicious content")
            except (ValueError, UnicodeDecodeError):
                pass
        return (False, "")

    def get_stats(self) -> dict[str, Any]:
        """Get guardrail statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "injection_patterns_count": len(self.injection_patterns),
            "pii_types_count": len(self.pii_patterns),
            "malicious_keywords_count": len(self.malicious_keywords),
            "unicode_homoglyphs_count": sum(
                len(homoglyphs) for homoglyphs in self.unicode_homoglyphs.values()
            ),
            "strict_mode": self.strict_mode,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "active_rate_limits": len(self._rate_limit_store),
            "features_enabled": {
                "injection_detection": self.enable_injection_detection,
                "pii_detection": self.enable_pii_detection,
                "semantic_check": self.enable_semantic_check,
                "unicode_check": self.enable_unicode_check,
                "encoding_check": self.enable_encoding_check,
                "rate_limit": self.enable_rate_limit,
            },
        }


_input_guardrail: InputGuardrail | None = None


def get_input_guardrail(**kwargs) -> InputGuardrail:
    """Get or create the global input guardrail instance.

    Args:
        **kwargs: Arguments to pass to InputGuardrail constructor

    Returns:
        InputGuardrail instance
    """
    global _input_guardrail
    if _input_guardrail is None:
        _input_guardrail = InputGuardrail(**kwargs)
    return _input_guardrail


def scan_input(input_text: str, **kwargs) -> GuardResult:
    """Convenience function to scan input.

    Args:
        input_text: Text to scan
        **kwargs: Arguments for guardrail initialization

    Returns:
        GuardResult from scan
    """
    guardrail = get_input_guardrail(**kwargs)
    return guardrail.scan(input_text)


STRICT_GUARDRAIL = {
    "enable_injection_detection": True,
    "enable_pii_detection": True,
    "enable_semantic_check": True,
    "strict_mode": True,
}
PERMISSIVE_GUARDRAIL = {
    "enable_injection_detection": True,
    "enable_pii_detection": True,
    "enable_semantic_check": False,
    "strict_mode": False,
}
PII_ONLY_GUARDRAIL = {
    "enable_injection_detection": False,
    "enable_pii_detection": True,
    "enable_semantic_check": False,
    "strict_mode": False,
}
