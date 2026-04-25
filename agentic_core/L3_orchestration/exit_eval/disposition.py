"""Disposition taxonomy — X3A/X3B/X3C/X3D/X3E.

See v4 §X3 Dispositions and hardening addendum H3 (break-glass).

Produces a sealed-folder envelope compatible with
``agentic_core.L3_orchestration.exit_control.classify_exit``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Disposition(str, Enum):
    """The five terminal dispositions for a runtime run."""

    DENY = "X3A"  # deny / reroute
    ESCALATE = "X3B"  # HITL escalation
    COMMIT = "X3C"  # commit to UWG / L4
    ALLOW = "X3D"  # allow / finish, no durable write
    BREAK_GLASS = "X3E"  # emergency override (H3)


class ReasonCode(str, Enum):
    """Canonical reason codes.

    New in v4 over v3:

    - Trajectory gate (X1E): ``WRONG_TOOL``, ``ARG_EXTRACTION_FAIL``, ...
    - Adversarial gate (X1F): ``PROMPT_INJECTION_DETECTED``, ...
    - Consistency gate (X1G): ``CONSISTENCY_FAIL``, ``INSUFFICIENT_HISTORY``
    - Judge protocol: ``JUDGE_ABSTAINED``, ``JUDGE_TIMEOUT``, ``JUDGE_ERROR``
    - Fault modes (H8): ``RUBRIC_UNAVAILABLE``, ``GRADER_EXCEPTION``,
      ``AUDIT_UNAVAILABLE``
    - Hardening (H1): ``REWARD_HACK_SUSPECT``
    - Break-glass (H3): ``BREAK_GLASS_INVOKED``
    """

    # X1A
    POLICY_CONFLICT = "POLICY_CONFLICT"

    # X1B
    SCHEMA_VIOLATION = "SCHEMA_VIOLATION"
    FORMAT_MISMATCH = "FORMAT_MISMATCH"
    INSTRUCTION_BYPASS = "INSTRUCTION_BYPASS"

    # X1C
    SANDBOX_BREACH = "SANDBOX_BREACH"
    UNAUTHORIZED_MUTATION = "UNAUTHORIZED_MUTATION"
    ENV_CONTAMINATED = "ENV_CONTAMINATED"
    TRIAL_STATE_LEAK = "TRIAL_STATE_LEAK"

    # X1D
    UNGROUNDED = "UNGROUNDED"
    CITATION_INVALID = "CITATION_INVALID"
    LOW_FAITHFULNESS = "LOW_FAITHFULNESS"

    # X1E
    WRONG_TOOL = "WRONG_TOOL"
    ARG_EXTRACTION_FAIL = "ARG_EXTRACTION_FAIL"
    STEP_INEFFICIENT = "STEP_INEFFICIENT"
    REASONING_INCOHERENT = "REASONING_INCOHERENT"
    HANDOFF_MISROUTED = "HANDOFF_MISROUTED"
    TRAJECTORY_SUSPECT = "TRAJECTORY_SUSPECT"

    # X1F
    PROMPT_INJECTION_DETECTED = "PROMPT_INJECTION_DETECTED"
    SYSTEM_PROMPT_LEAK = "SYSTEM_PROMPT_LEAK"
    JAILBREAK_DETECTED = "JAILBREAK_DETECTED"
    BIAS_DELTA_EXCEEDED = "BIAS_DELTA_EXCEEDED"
    ADVERSARIAL_CRASH = "ADVERSARIAL_CRASH"

    # X1G
    CONSISTENCY_FAIL = "CONSISTENCY_FAIL"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    CONSISTENCY_HISTORY_UNAVAILABLE = "CONSISTENCY_HISTORY_UNAVAILABLE"

    # Judge protocol / fault modes (H8)
    JUDGE_ABSTAINED = "JUDGE_ABSTAINED"
    JUDGE_TIMEOUT = "JUDGE_TIMEOUT"
    JUDGE_ERROR = "JUDGE_ERROR"
    GRADER_EXCEPTION = "GRADER_EXCEPTION"
    RUBRIC_UNAVAILABLE = "RUBRIC_UNAVAILABLE"
    AUDIT_UNAVAILABLE = "AUDIT_UNAVAILABLE"

    # Hardening
    REWARD_HACK_SUSPECT = "REWARD_HACK_SUSPECT"
    BREAK_GLASS_INVOKED = "BREAK_GLASS_INVOKED"


@dataclass(frozen=True)
class DispositionEnvelope:
    """The sealed-folder envelope produced by the evaluation pipeline.

    Shape aligns with the ``classify_exit`` contract in
    ``exit_control.exit_controller``:

    - ``deny`` / ``deny_reason`` — set for DENY (X3A).
    - Fields consumed by L5 classification — set for ESCALATE (X3B).
    - Neither set — COMMIT (X3C) or ALLOW (X3D) path; the caller chooses
      which based on whether the run is a commit candidate.
    """

    disposition: Disposition
    deny: bool
    deny_reason: str | None
    reason_codes: tuple[ReasonCode, ...]
    hitl_reason: str | None = None
    run_id: str = ""
    track: str = ""
    trajectory_class: str = ""
    # Break-glass audit link (H3) — populated only for X3E runs.
    break_glass_audit_id: str | None = None
    # Extras the orchestrator may need to attach (e.g. trajectory snapshot
    # for the HITL packet — hardening addendum §X3B enhancement).
    extras: dict[str, object] = field(default_factory=dict)

    def to_sealed_folder(self) -> dict[str, object]:
        """Serialize as a ``sealed_folder`` mapping for ``classify_exit``.

        Only fields relevant to ``classify_exit`` are emitted. Evaluation
        metadata (reason_codes, track, etc.) rides on BUS P separately.
        """
        env: dict[str, object] = {}
        if self.deny:
            env["deny"] = True
            if self.deny_reason:
                env["deny_reason"] = self.deny_reason
            return env
        # Non-DENY envelopes carry HITL classification context when
        # escalating. Downstream ``classify_escalation_class`` consumes
        # these fields; we pass the reason codes so L5 policy can route.
        if self.disposition is Disposition.ESCALATE:
            env["reason_codes"] = [rc.value for rc in self.reason_codes]
            if self.hitl_reason:
                env["hitl_reason"] = self.hitl_reason
        env["run_id"] = self.run_id
        env["track"] = self.track
        return env


__all__ = ["Disposition", "DispositionEnvelope", "ReasonCode"]
