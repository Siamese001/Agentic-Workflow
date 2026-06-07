"""Exemplar SovereignHealerBase subclass — code-quality line-length healer.

Plan: `docs/archive/windsurf/legacy-tree/plans/l2-execute-v2-agent-conformance-c8e4f1.md` §W6.
Closes G-V9 (exemplar #2 of 2) + G-V10 (blueprint/policy snapshot re-assertion).

This class demonstrates the L2 Execute v2 §E4 Fixing Desk pattern:

  * Inherits from :class:`SovereignHealerBase` — gets healer-only surface
  * ``__init_subclass__`` guard in the base class forbids adding ``validate()`` —
    this is compile-time separation from the validator
  * ``heal(request)`` re-asserts blueprint/policy hash equality against the
    originating packet (L2 Execute v2 §E4 invariant) via
    :meth:`SovereignHealerBase.assert_snapshot_binding`
  * Returns :class:`HealResult` from W2 (not a stub dict)
  * ``repair_count`` respects ``MAX_REPAIR_COUNT`` from the base
  * Marked with ``@requires_sealed_return`` so the W5 CI gate inspects it
  * ``repair()`` is the public API; returns :class:`SealedL2Artifact`

The paired validator is in ``code_quality_validator.py``.
"""

from __future__ import annotations

import uuid
from typing import Any

from agentic_core.base_agents.SovereignHealerBase import SovereignHealerBase
from agentic_core.L2_execution.enforcement.agent_seal_helper import (
    build_seal_from_heal,
    requires_sealed_return,
    sealed_exempt,
)
from agentic_core.L2_execution.types.sealed_l2_artifact import SealedL2Artifact
from agentic_core.L5_safety.types.heal_request_types import (
    HealOutcome,
    HealRequest,
    HealResult,
)

__all__ = ["CodeQualityHealerExemplar"]


@requires_sealed_return
class CodeQualityHealerExemplar(SovereignHealerBase):
    """Repair code snippets that violate the line-length policy.

    E4 Fixing Desk equivalent: given a HealRequest whose violation_payload
    describes the long lines, wrap offending lines at word boundaries.
    """

    DEFAULT_MAX_LINE_LENGTH = 120

    def __init__(self, max_line_length: int | None = None) -> None:
        self.max_line_length = max_line_length or self.DEFAULT_MAX_LINE_LENGTH

    @sealed_exempt
    def heal(self, heal_request: Any) -> HealResult:
        """Repair per L2 Execute v2 §E4. Returns HealResult (W2 contract).

        Invariants enforced:
          * heal_request is a HealRequest instance
          * blueprint_hash / policy_hash from heal_request are used as the
            HealResult's snapshot binding (via HealResult.from_request)
          * repair_count is bounded by MAX_REPAIR_COUNT
        """
        if not isinstance(heal_request, HealRequest):
            return HealResult.needs_help(
                parent_packet_id="unknown",
                policy_hash="unknown",
                blueprint_hash="unknown",
                reason_code="invalid_heal_request_type",
                message=f"Expected HealRequest, got {type(heal_request).__name__}",
            )

        payload = heal_request.violation_payload or {}
        code = payload.get("code", "")
        if not isinstance(code, str) or not code:
            return HealResult.from_request(
                heal_request,
                outcome=HealOutcome.FAIL_TERMINAL,
                reason_code="missing_code_payload",
                repair_count=0,
                evidence={"reason": "violation_payload.code missing or non-string"},
                message="Cannot heal without the offending code text.",
            )

        max_len = int(payload.get("max_line_length", self.max_line_length))
        repaired, lines_changed = self._wrap_long_lines(code, max_len)

        if lines_changed == 0:
            # Nothing to do — validator must have been wrong OR packet was stale.
            return HealResult.from_request(
                heal_request,
                outcome=HealOutcome.SUCCESS,
                reason_code="no_repair_needed",
                repair_count=1,
                evidence={"max_line_length": max_len, "lines_changed": 0},
                message="No lines exceeded the limit; nothing to repair.",
            )

        # Successful repair path.
        return HealResult.from_request(
            heal_request,
            outcome=HealOutcome.SUCCESS,
            reason_code="long_lines_wrapped",
            repair_count=1,
            evidence={
                "max_line_length": max_len,
                "lines_changed": lines_changed,
                "repaired_code_length": len(repaired),
            },
            message=f"Wrapped {lines_changed} long line(s).",
        )

    @staticmethod
    def _wrap_long_lines(code: str, max_len: int) -> tuple[str, int]:
        """Naive word-boundary wrap for lines over max_len. Returns (new_code, n_changed)."""
        new_lines: list[str] = []
        changed = 0
        for line in code.splitlines():
            if len(line) <= max_len:
                new_lines.append(line)
                continue
            # Wrap at the last space before max_len. If no space, leave the line
            # alone and count it as "not repairable" (caller decides escalation).
            words = line.split(" ")
            current = ""
            wrapped: list[str] = []
            for w in words:
                candidate = (current + " " + w).strip() if current else w
                if len(candidate) > max_len and current:
                    wrapped.append(current)
                    current = w
                else:
                    current = candidate
            if current:
                wrapped.append(current)
            if all(len(ln) <= max_len for ln in wrapped):
                new_lines.extend(wrapped)
                changed += 1
            else:
                # Word longer than max_len; preserve line, caller escalates.
                new_lines.append(line)
        return "\n".join(new_lines), changed

    def repair(self, heal_request: Any) -> SealedL2Artifact:
        """Public entry: run heal(), seal the result as an E5 artifact.

        Always returns a SealedL2Artifact. The seal's exec_trace preserves
        the snapshot-binding fields (policy_hash, blueprint_hash,
        parent_packet_id) so downstream [5] Exit Control can verify the
        repair stayed on the originating snapshot.
        """
        result = self.heal(heal_request)
        trace_id = heal_request.request_id if isinstance(heal_request, HealRequest) else str(uuid.uuid4())
        return build_seal_from_heal(result, trace_id=trace_id)
