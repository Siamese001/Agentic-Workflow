"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""

from __future__ import annotations

# LEGACY CODE BELOW - COMMENTED OUT
# """Message Body Composer Agent - Core Message Generator (K.3)

# This agent generates LinkedIn message bodies with strict Metric binding and Archetype-specific structure.
# Enforces LIC-QA-041 Metric binding and transition phrase requirements.

# Layer: L2_execution
# Responsibilities:
# - Generate core message body with Archetype-specific structure
# - Enforce Metric binding (every Metric links to Resume Evidence ID)
# - Use Archetype-specific transition phrases verbatim
# - Validate message structure and flow

# Non-responsibilities:
# - Route classification
# - CTA generation
# - Final assembly
# """

# from dataclasses import dataclass, field
# from typing import Any
# import logging
# import re

# [SSOT IMPORT] Structure blueprint is the single source of truth

# Logger: Any = logging.getLogger(__name__)


# @dataclass
# class MessageBodyConfig:
#     """TODO: Add docstring."""

#     TEMPERATURE: float = 0.6
#     max_attempts: int = 3


# @dataclass
# class MessageBodyResult:
#     """Docstring."""

#     body: str
#     metrics_used: list[str]
#     evidence_bindings: dict[str, str]
#     validation_results: list[ValidationResult]
#     temperature_log: list[dict[str, Any]]
#     success: bool
#     attempts: int


# class MessageBodyComposer:
#     """
#     K.3 - Core Message Generator

#     Strict Requirements:
#     - Metric Binding (LIC-QA-041): Every Metric must link to Resume Evidence ID
#     - Micro-Structure: Use Archetype-specific transition phrase exactly
#     - No unbound metrics allowed (BLOCK immediately)
#     """

#     ARCHETYPE_TRANSITIONS: Any = {
#         "C_LEVEL": "Two strategic insights from my experience:",
#         "VP_LEVEL": "Two key achievements that align with your priorities:",
#         "DIRECTOR": "Two relevant accomplishments from my background:",
#         "MANAGER": "Two specific examples of my impact:",
#         "RECRUITER": "Two qualifications that match your requirements:",
#     }

#     def __init__(
#         self,
#         config: MessageBodyConfig | None = None,
#         gate_executor: IntegrityGateExecutorAgent | None = None,
#         recovery_loop: AdaptiveRecoveryLoop | None = None,
#     ):
#         SELF.CONFIG = config or MessageBodyConfig()
#         self.gate_executor = gate_executor or IntegrityGateExecutorAgent()
#         self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
#             initial_temperature=self.config.temperature
#         )

#     def generate_message_body(
#         self, Archetype: str, resume_evidence: dict[str, str], context: dict[str, Any]
#     ) -> MessageBodyResult:
#         """
#         Generate message body with Metric binding validation.

#         Args:
#             Archetype: Target Archetype (C_LEVEL, RECRUITER, etc.)
#             resume_evidence: Dict mapping evidence IDs to content
#             context: Additional context (JD, company, etc.)

#         Returns:
#             MessageBodyResult with body and validation details
#         """
#         self.recovery_loop.reset(self.config.temperature)
#         validation_results: Any = []
#         for attempt in range(1, self.config.max_attempts + 1):
#             BODY: Any = self._generate_content(
#                 ARCHETYPE=Archetype,
#                 resume_evidence=resume_evidence,
#                 CONTEXT=context,
#                 TEMPERATURE=self.recovery_loop.current_temperature,
#                 ATTEMPT=attempt,
#             )
#             hygiene_result: Any = self.gate_executor.execute_hygiene_scan(body)
#             validation_results.append(hygiene_result)
#             if not hygiene_result.passed:
#                 RECOVERY: Any = self.recovery_loop.record_failure(
#                     gate_id=hygiene_result.gate_id,
#                     MESSAGE=hygiene_result.message,
#                     DETAILS=hygiene_result.details,
#                 )
#                 if not recovery.should_retry:
#                     break
#                 continue
#             metrics_used: Any = self._extract_metrics(body)
#             evidence_bindings: Any = self._bind_metrics_to_evidence(metrics_used, resume_evidence)
#             binding_result: Any = self.gate_executor.execute_metric_binding_gate(
#                 CONTENT=body, evidence_ids=evidence_bindings, gate_id="VG_METRIC_BINDING"
#             )
#             validation_results.append(binding_result)
#             if not binding_result.passed:
#                 RECOVERY: Any = self.recovery_loop.record_failure(
#                     gate_id=binding_result.gate_id,
#                     MESSAGE=binding_result.message,
#                     DETAILS=binding_result.details,
#                 )
#                 if not recovery.should_retry:
#                     break
#                 continue
#             transition_result: Any = self._validate_transition_phrase(body, Archetype)
#             validation_results.append(transition_result)
#             if not transition_result.passed:
#                 RECOVERY: Any = self.recovery_loop.record_failure(
#                     gate_id=transition_result.gate_id,
#                     MESSAGE=transition_result.message,
#                     DETAILS=transition_result.details,
#                 )
#                 if not recovery.should_retry:
#                     break
#                 continue
#             self.gate_executor.results = validation_results
#             return MessageBodyResult(
#                 BODY=body,
#                 metrics_used=metrics_used,
#                 evidence_bindings=evidence_bindings,
#                 validation_results=validation_results,
#                 temperature_log=self.recovery_loop.get_temperature_log(),
#                 SUCCESS=True,
#                 ATTEMPTS=attempt,
#             )
#         return MessageBodyResult(
#             BODY="",
#             metrics_used=[],
#             evidence_bindings={},
#             validation_results=validation_results,
#             temperature_log=self.recovery_loop.get_temperature_log(),
#             SUCCESS=False,
#             ATTEMPTS=self.config.max_attempts,
#         )

#     def _generate_content(
#         self,
#         Archetype: str,
#         resume_evidence: dict[str, str],
#         context: dict[str, Any],
#         temperature: float,
#         attempt: int,
#     ) -> str:
#         """
#         Generate message body content using LLM.
#         Placeholder for actual LLM integration.
#         """
#         TRANSITION = self.ARCHETYPE_TRANSITIONS.get(Archetype, "Two key points:")
#         return f"I noticed your work at {context.get('company', 'your company')}.\n\n{TRANSITION}\n\n1. Led 30% revenue growth through strategic initiatives\n2. Managed $5M budget with 95% efficiency\n\nWould you be open to a brief conversation?"

#     def _extract_metrics(self, content: str) -> list[str]:
#         """Extract all metrics from content"""
#         metric_pattern = "\\b\\d+%|\\b\\d+x\\b|\\b\\$\\d+[KMB]?(?:\\.\\d+)?[KMB]?\\b|\\b\\d+\\+?\\b(?=\\s+(?:team|people|projects|clients))"
#         return re.findall(metric_pattern, content)

#     def _bind_metrics_to_evidence(
#         self, metrics: list[str], resume_evidence: dict[str, str]
#     ) -> dict[str, str]:
#         """
#         Bind each Metric to a resume evidence ID.
#         Returns dict mapping Metric to evidence ID.
#         """
#         BINDINGS = {}
#         for Metric in metrics:
#             for evidence_id, evidence_text in resume_evidence.items():
#                 if Metric in evidence_text:
#                     BINDINGS[METRIC] = evidence_id
#                     break
#         return BINDINGS

#     def _validate_transition_phrase(self, content: str, Archetype: str) -> ValidationResult:
#         """
#         Validate Archetype-specific transition phrase is used verbatim.
#         BLOCKS if phrase is Missing or modified.
#         """
#         expected_phrase = self.ARCHETYPE_TRANSITIONS.get(Archetype)
#         if not expected_phrase:
#             return ValidationResult(
#                 gate_id="VG_TRANSITION_PHRASE",
#                 PASSED=True,
#                 SEVERITY="INFO",
#                 MESSAGE=f"No transition phrase required for Archetype {Archetype}",
#             )
#         if expected_phrase in content:
#             return ValidationResult(
#                 gate_id="VG_TRANSITION_PHRASE",
#                 PASSED=True,
#                 SEVERITY="INFO",
#                 MESSAGE=f"Transition phrase verified: '{expected_phrase}'",
#                 SIGNATURE=f"TRANS:OK:{hash(expected_phrase) % 10000}",
#             )
#         return ValidationResult(
#             gate_id="VG_TRANSITION_PHRASE",
#             PASSED=False,
#             SEVERITY="BLOCK",
#             MESSAGE="BLOCKED: Required transition phrase not found",
#             DETAILS={
#                 "expected": expected_phrase,
#                 "Archetype": Archetype,
#                 "content_preview": content[:200],
#             },
#         )


# def create_message_body_composer(config: MessageBodyConfig | None = None) -> MessageBodyComposer:
#     """Factory function to create MessageBodyComposer instance"""
#     return MessageBodyComposer(config=config)


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_lic.engines.message_body_composer', "module_loaded")
