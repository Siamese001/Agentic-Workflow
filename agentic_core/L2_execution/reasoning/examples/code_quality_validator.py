"""Exemplar SovereignValidatorBase subclass — code-quality line-length validator.

Plan: `.windsurf/plans/l2-execute-v2-agent-conformance-c8e4f1.md` §W6.
Closes G-V9 (exemplar #1 of 2).

This class demonstrates the L2 Execute v2 §E2 Work Order Check pattern:

  * Inherits from :class:`SovereignValidatorBase` — gets validator-only surface
  * Defines ``validate(packet)`` returning a ValidationVerdict-shaped dict
  * ``__init_subclass__`` guard in the base class forbids adding ``heal()`` —
    this is compile-time separation from the healer
  * Marked with ``@requires_sealed_return`` so the W5 CI gate inspects it
  * ``evaluate()`` is the public API; returns :class:`SealedL2Artifact`

Production agents migrating from the legacy co-located pattern should model
themselves on this structure (and the sibling healer in
``code_quality_healer.py``).
"""
from __future__ import annotations

import time
import uuid
from typing import Any

from agentic_core.base_agents.SovereignValidatorBase import SovereignValidatorBase
from agentic_core.L2_execution.enforcement.agent_seal_helper import (
    build_seal_from_validator,
    requires_sealed_return,
    sealed_exempt,
)
from agentic_core.L2_execution.types.sealed_l2_artifact import SealedL2Artifact

__all__ = ["CodeQualityValidatorExemplar"]


@requires_sealed_return
class CodeQualityValidatorExemplar(SovereignValidatorBase):
    """Validate that code snippets respect a max line-length policy.

    E2 Work Order Check equivalent: inspects a signed packet carrying a
    ``code`` field and optional ``max_line_length`` (default 120), returns
    Approved-to-Start or a sealed rejection.
    """

    DEFAULT_MAX_LINE_LENGTH = 120

    def __init__(self, max_line_length: int | None = None) -> None:
        self.max_line_length = max_line_length or self.DEFAULT_MAX_LINE_LENGTH

    @sealed_exempt
    def validate(self, packet: Any) -> dict[str, Any]:
        """Run the E2 check. Returns a ValidationVerdict-shaped dict.

        Does NOT mutate state. Does NOT attempt repair. Any violation is
        reported in the returned verdict; healing is the sibling healer's job.
        """
        if not isinstance(packet, dict):
            return {
                "is_allowed": False,
                "reason": f"packet must be a dict, got {type(packet).__name__}",
                "evidence": {},
            }
        code = packet.get("code", "")
        if not isinstance(code, str):
            return {
                "is_allowed": False,
                "reason": "packet['code'] must be a string",
                "evidence": {"got_type": type(code).__name__},
            }
        max_len = int(packet.get("max_line_length", self.max_line_length))
        offending_lines: list[tuple[int, int]] = []
        for lineno, line in enumerate(code.splitlines(), start=1):
            if len(line) > max_len:
                offending_lines.append((lineno, len(line)))
        if offending_lines:
            return {
                "is_allowed": False,
                "reason": f"{len(offending_lines)} line(s) exceed {max_len} chars",
                "evidence": {
                    "max_line_length": max_len,
                    "offending_lines": offending_lines,
                },
            }
        return {
            "is_allowed": True,
            "reason": f"all lines within {max_len}-char limit",
            "evidence": {"max_line_length": max_len, "line_count": len(code.splitlines())},
        }

    def evaluate(self, packet: Any) -> SealedL2Artifact:
        """Public entry: run validate(), seal the result as an E5 artifact.

        Always returns a SealedL2Artifact. Approved -> SUCCESS terminal;
        rejected -> REJECTED terminal. The sealed artifact is the handoff
        contract to [5] Exit Control Gate per L2 Execute v2 §E5.
        """
        verdict = self.validate(packet)
        # Map ValidationVerdict to the E2Verdict shape that build_seal_from_validator expects.
        trace_id = str(uuid.uuid4())
        validator_shaped = {
            "decision": "approved" if verdict["is_allowed"] else "rejected",
            "tool_name": f"{type(self).__name__}.validate",
            "reason": verdict["reason"],
            "trace_id": trace_id,
        }
        seal = build_seal_from_validator(
            validator_shaped,
            trace_id=trace_id,
            evidence_bundle={
                "validator_evidence": verdict["evidence"],
                "validator_class": type(self).__name__,
                "sealed_at_monotonic": time.monotonic(),
            },
        )
        return seal
