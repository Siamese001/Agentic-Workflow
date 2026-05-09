"""U0 User-Text Airlock — isolates untrusted user content before PA.

Detects and neutralizes prompt injection attempts in user-controlled inputs:
- "ignore previous instructions" / "you are now ..."
- Tool/model/schema/policy override attempts
- Hidden instruction blocks in markdown/HTML/XML

Per PROMPT_BOUNDARY_CONTRACT.md §3.1.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from apps_rg.prompt_assembly._pa_boundary import make_pa_boundary_receipt, PABoundaryStatus
from apps_rg.airlocks._otel_spans import airlock_span, emit_airlock_event

_log = logging.getLogger(__name__)


class U0ThreatLevel(str, Enum):
    """Threat classification for user content."""

    CLEAN = "CLEAN"
    SUSPICIOUS = "SUSPICIOUS"  # flagged patterns but not definitive
    NEUTRALIZED = "NEUTRALIZED"  # threat detected and neutralized
    REJECTED = "REJECTED"  # hard reject (severe injection attempt)


class U0PatternClass(str, Enum):
    """Pattern classes detected by U0 scanner."""

    IGNORE_PREVIOUS = "ignore_previous_instructions"
    ROLE_OVERRIDE = "role_override_attempt"
    SYSTEM_MESSAGE_FAKE = "fake_system_message"
    TOOL_OVERRIDE = "tool_override_attempt"
    MODEL_OVERRIDE = "model_override_attempt"
    SCHEMA_OVERRIDE = "schema_override_attempt"
    POLICY_OVERRIDE = "policy_override_attempt"
    HIDDEN_MARKDOWN = "hidden_markdown_instruction"
    HIDDEN_HTML = "hidden_html_instruction"
    HIDDEN_XML = "hidden_xml_instruction"
    CREDENTIAL_EXFIL = "credential_exfiltration_attempt"


# Pattern definitions: (regex, pattern_class, severity)
# Severity: 1=info, 2=warn/neutralize, 3=reject
_U0_PATTERNS: list[tuple[re.Pattern, U0PatternClass, int]] = [
    # Ignore previous / role override
    (re.compile(r"ignore\s+(all\s+)?(previous|prior|earlier)\s+(instructions?|commands?|prompts?)", re.IGNORECASE), U0PatternClass.IGNORE_PREVIOUS, 3),
    (re.compile(r"you\s+are\s+now\s+(?:a\s+)?", re.IGNORECASE), U0PatternClass.ROLE_OVERRIDE, 2),
    (re.compile(r"from\s+now\s+on\s+you\s+are", re.IGNORECASE), U0PatternClass.ROLE_OVERRIDE, 2),
    # Fake system/developer messages
    (re.compile(r"\[\s*system\s*\]|\{\s*system\s*\}|system\s+message\s*:", re.IGNORECASE), U0PatternClass.SYSTEM_MESSAGE_FAKE, 3),
    (re.compile(r"\[\s*developer\s*\]|\{\s*developer\s*\}|developer\s+message\s*:", re.IGNORECASE), U0PatternClass.SYSTEM_MESSAGE_FAKE, 3),
    # Tool/model/schema/policy overrides
    (re.compile(r"(?:use|call|invoke)\s+(?:different|other|new)\s+(?:tool|function|api)", re.IGNORECASE), U0PatternClass.TOOL_OVERRIDE, 2),
    (re.compile(r"switch\s+(?:to|model|provider)\s+", re.IGNORECASE), U0PatternClass.MODEL_OVERRIDE, 2),
    (re.compile(r"change\s+(?:output\s+)?format\s+(?:to|into)", re.IGNORECASE), U0PatternClass.SCHEMA_OVERRIDE, 2),
    (re.compile(r"disable\s+(?:safety|guardrails?|restrictions?|policies?)", re.IGNORECASE), U0PatternClass.POLICY_OVERRIDE, 3),
    # Hidden blocks (markdown comment, HTML comment, XML CDATA)
    (re.compile(r"<!?--.*?-->", re.DOTALL | re.IGNORECASE), U0PatternClass.HIDDEN_MARKDOWN, 1),
    (re.compile(r"<\?xml.*?\?>", re.DOTALL | re.IGNORECASE), U0PatternClass.HIDDEN_XML, 1),
    (re.compile(r"<!\[CDATA\[.*?\]\]>", re.DOTALL | re.IGNORECASE), U0PatternClass.HIDDEN_XML, 1),
    # Credential exfiltration patterns
    (re.compile(r"(?:send|email|post|transmit|exfiltrate)\s+(?:to|at|via)\s+", re.IGNORECASE), U0PatternClass.CREDENTIAL_EXFIL, 3),
]


@dataclass(frozen=True)
class U0Detection:
    """Single detection record."""

    pattern_class: str
    matched_text: str
    position: int
    severity: int


@dataclass(frozen=True)
class U0AirlockResult:
    """Result of U0 airlock processing."""

    original_hash: str
    processed_text: str
    threat_level: str
    detections: list[dict[str, Any]]
    neutralized_count: int
    receipt: dict[str, Any]


class U0Airlock:
    """U0 User-Text Airlock.

    Detects prompt injection patterns and either:
    - Returns CLEAN with assembly_security_pass_receipt
    - Returns NEUTRALIZED (patterns removed/replaced) with injection_neutralization_receipt
    - Raises U0RejectionError (severity 3 patterns) with unsafe_payload_rejection_receipt
    """

    def __init__(self, max_input_size: int = 500_000):
        self._max_input_size = max_input_size
        self._patterns = _U0_PATTERNS

    def process(
        self,
        user_text: str,
        *,
        request_id: str = "",
        run_id: str = "",
        trace_id: str = "",
        route_id: str = "",
        source_ref: str = "u0_input",
    ) -> U0AirlockResult:
        """Process user text through U0 airlock.

        Args:
            user_text: Raw user-controlled input (CLI args, wizard input, brief content)
            request_id: Request identifier for receipt
            run_id: Run identifier for receipt
            trace_id: Trace identifier for receipt
            route_id: Route identifier for receipt
            source_ref: Source reference for lineage

        Returns:
            U0AirlockResult with processed text and receipt

        Raises:
            U0RejectionError: If hard rejection patterns detected (severity 3)
        """
        if len(user_text) > self._max_input_size:
            with airlock_span(
                "pa.unsafe_payload_rejection",
                airlock="U0_USER_TEXT",
                request_id=request_id,
                run_id=run_id,
                trace_id=trace_id,
                reason="SIZE_LIMIT_EXCEEDED",
            ):
                pass
            raise U0RejectionError(
                f"Input exceeds max size ({self._max_input_size} chars)",
                receipt=self._make_rejection_receipt(
                    user_text, "SIZE_LIMIT_EXCEEDED", request_id, run_id, trace_id, route_id
                ),
            )

        original_hash = hashlib.sha256(user_text.encode()).hexdigest()[:16]
        detections: list[U0Detection] = []

        # Scan for patterns
        for pattern, pclass, severity in self._patterns:
            for match in pattern.finditer(user_text):
                detections.append(U0Detection(
                    pattern_class=pclass.value,
                    matched_text=match.group(0)[:100],  # truncated
                    position=match.start(),
                    severity=severity,
                ))

        # Determine outcome
        max_severity = max((d.severity for d in detections), default=0)

        if max_severity >= 3:
            # Hard reject
            reason_codes = [d.pattern_class for d in detections if d.severity >= 3]
            receipt = self._make_rejection_receipt(
                user_text, "INJECTION_REJECTED", request_id, run_id, trace_id, route_id, reason_codes
            )
            with airlock_span(
                "pa.unsafe_payload_rejection",
                airlock="U0_USER_TEXT",
                request_id=request_id,
                run_id=run_id,
                trace_id=trace_id,
                reason_codes=",".join(reason_codes),
                detection_count=len(detections),
            ):
                pass
            raise U0RejectionError(
                f"Severe injection patterns detected: {reason_codes}",
                receipt=receipt,
                detections=[{
                    "pattern_class": d.pattern_class,
                    "position": d.position,
                    "severity": d.severity,
                } for d in detections if d.severity >= 3],
            )

        # Neutralize or pass through
        processed_text, neutralized_count = self._neutralize(user_text, detections)
        processed_hash = hashlib.sha256(processed_text.encode()).hexdigest()[:16]

        if neutralized_count > 0:
            threat_level = U0ThreatLevel.NEUTRALIZED.value
            reason_codes = ["NEUTRALIZED", "INJECTION_PATTERNS_DETECTED"]
        elif detections:
            threat_level = U0ThreatLevel.SUSPICIOUS.value
            reason_codes = ["SUSPICIOUS_PATTERNS_NOTED"]
        else:
            threat_level = U0ThreatLevel.CLEAN.value
            reason_codes = ["CLEAN"]

        receipt = make_pa_boundary_receipt(
            request_id=request_id or "NOT_BOUND",
            run_id=run_id or "NOT_BOUND",
            trace_id=trace_id or "NOT_BOUND",
            route_id=route_id or "NOT_BOUND",
            policy_hash="u0_airlock_v1",
            blueprint_hash=original_hash,
            prompt_hash=processed_hash,
            compiled_artifact_hash="NOT_BOUND",  # U0 is pre-PA
            bom_hash="NOT_BOUND",
            registry_hash="NOT_BOUND",
            template_hash="NOT_BOUND",
            source_refs={"source": source_ref, "original_hash": original_hash},
            lineage_refs={
                "airlock": "U0_USER_TEXT",
                "detections": str(len(detections)),
                "neutralized": str(neutralized_count),
            },
            status=PABoundaryStatus.PA_SECURITY_PASS if threat_level != U0ThreatLevel.REJECTED else PABoundaryStatus.PA_SECURITY_GAP,
            reason_codes=reason_codes,
            unavailable_fields=["compiled_artifact_hash", "bom_hash", "registry_hash", "template_hash"],
        )

        _log.info(
            "[U0] processed: threat_level=%s detections=%d neutralized=%d",
            threat_level, len(detections), neutralized_count,
        )

        # OTEL span for boundary observability
        span_name = "pa.injection_neutralization" if neutralized_count > 0 else "pa.airlock_security_pass"
        with airlock_span(
            span_name,
            airlock="U0_USER_TEXT",
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            threat_level=threat_level,
            detection_count=len(detections),
            neutralized_count=neutralized_count,
        ):
            pass

        return U0AirlockResult(
            original_hash=original_hash,
            processed_text=processed_text,
            threat_level=threat_level,
            detections=[{
                "pattern_class": d.pattern_class,
                "matched_text": d.matched_text,
                "position": d.position,
                "severity": d.severity,
            } for d in detections],
            neutralized_count=neutralized_count,
            receipt=receipt.to_dict(),
        )

    def _neutralize(self, text: str, detections: list[U0Detection]) -> tuple[str, int]:
        """Neutralize detected patterns by replacement/masking.

        Returns (processed_text, neutralized_count).
        """
        # Sort by position descending so we can replace from end to start
        sorted_dets = sorted(detections, key=lambda d: d.position, reverse=True)
        processed = text
        neutralized = 0

        for det in sorted_dets:
            if det.severity >= 2:  # Only neutralize warn-level and above
                start = det.position
                end = start + len(det.matched_text)
                replacement = f"[U0_NEUTRALIZED:{det.pattern_class}]"
                processed = processed[:start] + replacement + processed[end:]
                neutralized += 1

        return processed, neutralized

    def _make_rejection_receipt(
        self,
        text: str,
        reason: str,
        request_id: str,
        run_id: str,
        trace_id: str,
        route_id: str,
        reason_codes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create rejection receipt."""
        receipt = make_pa_boundary_receipt(
            request_id=request_id or "NOT_BOUND",
            run_id=run_id or "NOT_BOUND",
            trace_id=trace_id or "NOT_BOUND",
            route_id=route_id or "NOT_BOUND",
            policy_hash="u0_airlock_v1",
            blueprint_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
            prompt_hash="NOT_BOUND",
            compiled_artifact_hash="NOT_BOUND",
            bom_hash="NOT_BOUND",
            registry_hash="NOT_BOUND",
            template_hash="NOT_BOUND",
            source_refs={"source": "u0_input", "outcome": "REJECTED"},
            lineage_refs={"airlock": "U0_USER_TEXT", "reason": reason},
            status=PABoundaryStatus.PA_SECURITY_GAP,
            reason_codes=reason_codes or [reason],
            unavailable_fields=["prompt_hash", "compiled_artifact_hash", "bom_hash", "registry_hash", "template_hash"],
        )
        return receipt.to_dict()


class U0RejectionError(RuntimeError):
    """U0 airlock hard rejection."""

    def __init__(
        self,
        message: str,
        receipt: dict[str, Any],
        detections: list[dict[str, Any]] | None = None,
    ):
        super().__init__(message)
        self.receipt = receipt
        self.detections = detections or []


def process_user_text(
    user_text: str,
    *,
    request_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    route_id: str = "",
    source_ref: str = "u0_input",
) -> U0AirlockResult:
    """Convenience function for U0 airlock processing."""
    airlock = U0Airlock()
    return airlock.process(
        user_text,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        route_id=route_id,
        source_ref=source_ref,
    )


__all__ = [
    "U0Airlock",
    "U0AirlockResult",
    "U0Detection",
    "U0PatternClass",
    "U0RejectionError",
    "U0ThreatLevel",
    "process_user_text",
]
