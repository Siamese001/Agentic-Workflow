"""Message Body Composer Agent - Core Message Generator (K.3)


LOGGER = logging.getLogger(__name__)
This agent generates LinkedIn message bodies with strict metric binding and archetype-specific struc
    ture.
Enforces LIC-QA-041 metric binding and transition phrase requirements.

Layer: L2_execution
Responsibilities:
- Generate core message body with archetype-specific structure
- Enforce metric binding (every metric links to Resume Evidence ID)
- Use archetype-specific transition phrases verbatim
- Validate message structure and flow

Non-responsibilities:
- Route classification
- CTA generation
- Final assembly
"""


import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MessageBodyConfig:
    """TODO: Add docstring."""

    TEMPERATURE: float = 0.6
    max_attempts: int = 3


@dataclass
class MessageBodyResult:
    """Docstring."""
    body: str
    metrics_used: List[str]
    evidence_bindings: Dict[str, str]
    validation_results: List[ValidationResult]
    temperature_log: List[Dict[str, Any]]
    success: bool
    attempts: int


class MessageBodyComposer:
    """
    K.3 - Core Message Generator

    Strict Requirements:
    - Metric Binding (LIC-QA-041): Every metric must link to Resume Evidence ID
    - Micro-Structure: Use archetype-specific transition phrase exactly
    - No unbound metrics allowed (BLOCK immediately)
    """

    ARCHETYPE_TRANSITIONS = {
        'C_LEVEL': "Two strategic insights from my experience:",
        'VP_LEVEL': "Two key achievements that align with your priorities:",
        'DIRECTOR': "Two relevant accomplishments from my background:",
        'MANAGER': "Two specific examples of my impact:",
        'RECRUITER': "Two qualifications that match your requirements:"
    }

    def __init__(
        self,
        config: Optional[MessageBodyConfig] = None,
        gate_executor: Optional[IntegrityGateExecutor] = None,
        recovery_loop: Optional[AdaptiveRecoveryLoop] = None
    ):
        self.config = config or MessageBodyConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutor()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature
        )

    def generate_message_body(
        self,
        archetype: str,
        resume_evidence: Dict[str, str],
        context: Dict[str, Any]
    ) -> MessageBodyResult:
        """
        Generate message body with metric binding validation.

        Args:
            archetype: Target archetype (C_LEVEL, RECRUITER, etc.)
            resume_evidence: Dict mapping evidence IDs to content
            context: Additional context (JD, company, etc.)

        Returns:
            MessageBodyResult with body and validation details
        """
        self.recovery_loop.reset(self.config.temperature)
        validation_results = []

        for attempt in range(1, self.config.max_attempts + 1):
            body = self._generate_content(
                archetype=archetype,
                resume_evidence=resume_evidence,
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt
            )

            hygiene_result = self.gate_executor.execute_hygiene_scan(body)
            validation_results.append(hygiene_result)

            if not hygiene_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=hygiene_result.gate_id,
                    message=hygiene_result.message,
                    details=hygiene_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            metrics_used = self._extract_metrics(body)
            evidence_bindings = self._bind_metrics_to_evidence(
                metrics_used,
                resume_evidence
            )

            binding_result = self.gate_executor.execute_metric_binding_gate(
                content=body,
                evidence_ids=evidence_bindings,
                gate_id='VG_METRIC_BINDING'
            )
            validation_results.append(binding_result)

            if not binding_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=binding_result.gate_id,
                    message=binding_result.message,
                    details=binding_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            transition_result = self._validate_transition_phrase(
                body, archetype)
            validation_results.append(transition_result)

            if not transition_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=transition_result.gate_id,
                    message=transition_result.message,
                    details=transition_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            self.gate_executor.results = validation_results

            return MessageBodyResult(
                body=body,
                metrics_used=metrics_used,
                evidence_bindings=evidence_bindings,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt
            )

        return MessageBodyResult(
            body="",
            metrics_used=[],
            evidence_bindings={},
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts
        )

    def _generate_content(
        self,
        archetype: str,
        resume_evidence: Dict[str, str],
        context: Dict[str, Any],
        temperature: float,
        attempt: int
    ) -> str:
        """
        Generate message body content using LLM.
        Placeholder for actual LLM integration.
        """
        transition = self.ARCHETYPE_TRANSITIONS.get(
            archetype, "Two key points:")

        return f"""I noticed your work at {context.get('company', 'your company')}.

{transition}

1. Led 30% revenue growth through strategic initiatives
2. Managed $5M budget with 95% efficiency

Would you be open to a brief conversation?"""

    def _extract_metrics(self, content: str) -> List[str]:
        """Extract all metrics from content"""
        metric_pattern = r'\b\d+% |\b\d+x\b |\b\$\d+[KMB]?(?: \.\d+)?[KMB]?\b |\b\d +\+?\b(?=\s+(?: team | p\
                                                                                                 eople | projects | clients))'
        return re.findall(metric_pattern, content)

    def _bind_metrics_to_evidence(
        self,
        metrics: List[str],
        resume_evidence: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Bind each metric to a resume evidence ID.
        Returns dict mapping metric to evidence ID.
        """
        bindings = {}

        for metric in metrics:
            for evidence_id, evidence_text in resume_evidence.items():
                if metric in evidence_text:
                    bindings[metric] = evidence_id
                    break

        return bindings

    def _validate_transition_phrase(
        self,
        content: str,
        archetype: str
    ) -> ValidationResult:
        """
        Validate archetype-specific transition phrase is used verbatim.
        BLOCKS if phrase is missing or modified.
        """
        expected_phrase = self.ARCHETYPE_TRANSITIONS.get(archetype)

        if not expected_phrase:
            return ValidationResult(
                gate_id='VG_TRANSITION_PHRASE',
                passed=True,
                severity='INFO',
                message=f"No transition phrase required for archetype {archetype}"
            )

        if expected_phrase in content:
            return ValidationResult(
                gate_id='VG_TRANSITION_PHRASE',
                passed=True,
                severity='INFO',
                message=f"Transition phrase verified: '{expected_phrase}'",
                signature=f"TRANS:OK:{hash(expected_phrase) % 10000}"
            )

        return ValidationResult(
            gate_id='VG_TRANSITION_PHRASE',
            passed=False,
            severity='BLOCK',
            message=f"BLOCKED: Required transition phrase not found",
            details={
                'expected': expected_phrase,
                'archetype': archetype,
                'content_preview': content[:200]
            }
        )


def create_message_body_composer(
    config: Optional[MessageBodyConfig] = None
) -> MessageBodyComposer:
    """Factory function to create MessageBodyComposer instance"""
    return MessageBodyComposer(config=config)