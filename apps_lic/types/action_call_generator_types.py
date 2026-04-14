"""Action Call Generator Agent - CTA Generator (K.5)
from agentic_core.runtime.contracts.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This agent generates Route-specific CTAs with strict character limits.
Enforces CONNECTION_REQ ≤300 chars and SHORT_NEW 360-380 chars post-normalization.

Layer: L2_execution
Responsibilities:
- Generate CTA based on Route type
- Enforce Route-specific character limits
- Ensure time-bound or specific asks
- Validate clarity and actionability

Non-responsibilities:
- Route classification
- Message body composition
- Final assembly
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any
from tqdm import tqdm

# [SSOT IMPORT] Structure blueprint is the single source of truth


class RouteType(Enum):
    """Docstring."""

    INMAIL: Any = "INMAIL"
    CONNECTION_REQ: Any = "CONNECTION_REQ"
    SHORT_NEW: Any = "SHORT_NEW"
    FOLLOW_UP: Any = "FOLLOW_UP"


@dataclass
class CtaConfig:
    """Docstring."""

    TEMPERATURE: float = 0.5
    max_attempts: int = 3


@dataclass
class CtaResult:
    """Docstring."""

    cta: str
    RouteType: RouteType
    char_count: int
    is_time_bound: bool
    is_specific: bool
    validation_results: list[Any]
    temperature_log: list[dict[str, Any]]
    success: bool
    attempts: int


class ActionCallGenerator:
    """
    K.5 - CTA Generator

    Route-Specific Constraints:
    - CONNECTION_REQ: ≤300 characters total message
    - SHORT_NEW: 360-380 characters total message
    - MUST ensure ask is time-bound or specific
    - VG_CTA_CLARITY validates actionability
    """

    ROUTE_CHAR_LIMITS: Any = {
        RouteType.CONNECTION_REQ: 300,
        RouteType.SHORT_NEW: (360, 380),
        RouteType.INMAIL: 1900,
        RouteType.FOLLOW_UP: 1000,
    }
    TIME_BOUND_PATTERNS: Any = [
        "\\b(?:next|this)\\s+(?:week|tuesday|wednesday|thursday|friday|monday)\\b",
        "\\b(?:tomorrow|today)\\b",
        "\\b\\d{1,2}(?:am|pm)\\b",
        # guardian: allow-path-string
        "\\b(?:january|february|march|april|may|june)"
        + "|(july|august|september|october|november|december)"
        + "\\s+\\d{1,2}\\b",
    ]
    SPECIFIC_ACTION_PATTERNS: Any = [
        "\\b(?:connect|call|meet|discuss|schedule|chat|talk|explore)\\b",
        "\\b(?:coffee|conversation|meeting|discussion|call)\\b",
    ]

    def __init__(
        self,
        config: CTAConfig | None = None,
        gate_executor: Any | None = None,
        recovery_loop: Any | None = None,
    ):
        self.config = config or CTAConfig()
        self.gate_executor = gate_executor or Any()
        self.recovery_loop = recovery_loop or Any(initial_temperature=self.config.TEMPERATURE)

    def generate_cta(self, RouteType: RouteType, message_body: str, context: dict[str, Any]) -> CTAResult:
        """Docstring.
        Generate CTA with Route-specific validation.

        Args:
            RouteType: Type of outreach Route
            message_body: Message body (for total char count validation)
            context: Additional context (Archetype, company, etc.)

        Returns:
            CTAResult with CTA and validation details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ActionCallGenerator.generate_cta"
        )

        self.recovery_loop.reset(self.config.TEMPERATURE)
        validation_results: Any = []
        for attempt in tqdm(range(1, self.config.max_attempts + 1), desc="Processing", unit="item"):
            cta: Any = self._generate_content(
                RouteType=RouteType,
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt,
            )
            hygiene_result: Any = self.gate_executor.execute_hygiene_scan(cta)
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
            total_message: Any = f"{message_body}\n\n{cta}"
            char_count: Any = len(total_message)
            char_limit_result: Any = self._validate_character_limit(
                RouteType=RouteType,
                total_message=total_message,
                char_count=char_count,
            )
            validation_results.append(char_limit_result)
            if not char_limit_result.passed:
                recovery: Any = self.recovery_loop.record_failure(
                    gate_id=char_limit_result.gate_id,
                    message=char_limit_result.message,
                    details=char_limit_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            is_time_bound: Any = self._check_time_bound(cta)
            is_specific: Any = self._check_specific_action(cta)
            clarity_result: Any = self._validate_cta_clarity(cta, is_time_bound, is_specific)
            validation_results.append(clarity_result)
            if not clarity_result.passed:
                recovery: Any = self.recovery_loop.record_failure(
                    gate_id=clarity_result.gate_id,
                    message=clarity_result.message,
                    details=clarity_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            self.gate_executor.results = validation_results
            return CTAResult(
                cta=cta,
                RouteType=RouteType,
                char_count=char_count,
                is_time_bound=is_time_bound,
                is_specific=is_specific,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt,
            )
        return CTAResult(
            cta="",
            RouteType=RouteType,
            char_count=0,
            is_time_bound=False,
            is_specific=False,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts,
        )

    def _generate_content(
        self,
        RouteType: RouteType,
        context: dict[str, Any],
        temperature: float,
        attempt: int,
    ) -> str:
        """
        Generate CTA content using LLM.
        Placeholder for actual LLM integration.
        """
        if RouteType == RouteType.CONNECTION_REQ:
            return "Would you be open to connecting to discuss potential synergies?"
        elif RouteType == RouteType.SHORT_NEW:
            return "I'd welcome the opportunity to schedule a brief call next Tuesday or Wednesday to explore how my experience aligns with your team's priorities. Are you available for a 15-minute conversation?"
        elif RouteType == RouteType.INMAIL:
            return "I'd appreciate the opportunity to discuss how my background in scaling technology organizations could support your strategic initiatives. Would you be available for a brief call next week? I'm flexible on timing and happy to work around your schedule."
        else:
            return "Looking forward to continuing our conversation. Are you available for a quick call this week?"

    def _validate_character_limit(self, RouteType: RouteType, total_message: str, char_count: int) -> Any:
        """
        Validate Route-specific character limits.
        BLOCKS if limit exceeded.
        """
        limit = self.ROUTE_CHAR_LIMITS.get(RouteType)
        if isinstance(limit, tuple):
            min_chars, max_chars = limit
            if min_chars <= char_count <= max_chars:
                return Any(
                    gate_id="VG_CTA_CHAR_LIMIT",
                    passed=True,
                    Severity="INFO",
                    message=f"Character limit satisfied: {char_count} chars ({min_chars}-{max_chars})",
                    signature=f"CHARLIMIT:OK:{char_count}",
                )
            return Any(
                gate_id="VG_CTA_CHAR_LIMIT",
                passed=False,
                Severity="BLOCK",
                message=f"BLOCKED: Character count {char_count} outside range ({min_chars}-{max_chars})",
                details={
                    "char_count": char_count,
                    "min": min_chars,
                    "max": max_chars,
                    "Route": RouteType.value,
                },
            )
        else:
            if char_count <= limit:
                return Any(
                    gate_id="VG_CTA_CHAR_LIMIT",
                    passed=True,
                    Severity="INFO",
                    message=f"Character limit satisfied: {char_count} chars (max {limit})",
                    signature=f"CHARLIMIT:OK:{char_count}",
                )
            return Any(
                gate_id="VG_CTA_CHAR_LIMIT",
                passed=False,
                Severity="BLOCK",
                message=f"BLOCKED: Character count {char_count} exceeds limit {limit}",
                details={"char_count": char_count, "limit": limit, "Route": RouteType.value},
            )

    def _check_time_bound(self, cta: str) -> bool:
        """Check if CTA contains time-bound language"""
        import re

        cta_lower = cta.lower()
        for pattern in self.TIME_BOUND_PATTERNS:
            if re.search(pattern, cta_lower):
                return True
        return False

    def _check_specific_action(self, cta: str) -> bool:
        """Check if CTA contains specific action language"""
        cta_lower = cta.lower()
        for pattern in self.SPECIFIC_ACTION_PATTERNS:
            if re.search(pattern, cta_lower):
                return True
        return False

    def _validate_cta_clarity(self, cta: str, is_time_bound: bool, is_specific: bool) -> Any:
        """
        Validate CTA clarity - must be time-bound or specific.
        BLOCKS if neither condition met.
        """
        if is_time_bound or is_specific:
            clarity_type = []
            if is_time_bound:
                clarity_type.append("time-bound")
            if is_specific:
                clarity_type.append("specific action")
            return Any(
                gate_id="VG_CTA_CLARITY",
                passed=True,
                Severity="INFO",
                message=f"CTA clarity satisfied: {' and '.join(clarity_type)}",
                signature="CLARITY:OK",
                details={"time_bound": is_time_bound, "specific": is_specific},
            )
        return Any(
            gate_id="VG_CTA_CLARITY",
            passed=False,
            Severity="BLOCK",
            message="BLOCKED: CTA lacks clarity - must be time-bound or specific",
            details={
                "time_bound": is_time_bound,
                "specific": is_specific,
                "cta_preview": cta[:100],
            },
        )


def create_action_call_generator(config: CTAConfig | None = None) -> ActionCallGenerator:
    """Docstring.
    Factory function to create ActionCallGenerator instance"""
    return ActionCallGenerator(config=config)
