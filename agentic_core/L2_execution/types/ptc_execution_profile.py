"""PTC Execution Contracts — profile, script envelope, sandbox receipt (doc 04.7).

Maps to: docs/reference/04_L2_Execute/04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox_detailed.md

Three contracts owned by L2 sandbox execution:

  * :class:`PTCExecutionProfile` — what the sandbox is allowed to run.
  * :class:`PTCScriptEnvelope`   — the signed script package that runs.
  * :class:`PTCSandboxReceipt`   — the sealed receipt the sandbox emits.

Design invariants (per 04.7):

1. Raw tool outputs MUST stay in the sandbox. They appear in the receipt
   only as opaque ``raw_result_refs_sandbox_only``. They do NOT enter
   model/L1/L3 reasoning context.
2. Stdout summary returned to L1/L3 must conform to the expected schema,
   be size-bounded, and exclude raw rows / secrets / unapproved credentials.
3. Untranscripted IO is fail-closed (``fail_closed_on_untranscripted_io``
   defaults to True). If the sandbox observes a file/network touch outside
   the allowlist, the receipt is sealed in REJECTED.
4. Human modifications return as data only. A modified script must
   re-enter L5/E2 validation before execution
   (``l5_reclearance_required_on_modify``).
5. PowerShell is not a default-allowed language. Shell access requires
   explicit policy permission.
6. PTC cannot commit state to L4. The receipt records receipts only.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class PTCScriptLanguage(str, Enum):
    """04.7 §PHASE 1 PTCExecutionProfile.script_language."""

    PYTHON = "python"
    BASH = "bash"
    POWERSHELL_DISALLOWED_IF_POLICY_BLOCKS = "powershell_disallowed_if_policy_blocks"
    OTHER_APPROVED = "other_approved"


class RawResultContextPolicy(str, Enum):
    """04.7 §PHASE 1 PTCExecutionProfile.raw_result_context_policy."""

    SANDBOX_ONLY = "SANDBOX_ONLY"


class StdoutReturnPolicy(str, Enum):
    """04.7 §PHASE 1 PTCExecutionProfile.stdout_return_policy."""

    SUMMARY_ONLY = "SUMMARY_ONLY"
    STRUCTURED_CARD_ONLY = "STRUCTURED_CARD_ONLY"


class PTCResultClass(str, Enum):
    """04.7 §PHASE 1 PTCSandboxReceipt.result_class.

    Mirrors the v3/v4 ResultClass at the PTC layer so the sandbox can
    classify its own outcome before it is rolled up into an AttemptReceipt.
    """

    SUCCESS = "SUCCESS"
    DEGRADED_SUCCESS = "DEGRADED_SUCCESS"
    SOFT_REPAIRABLE = "SOFT_REPAIRABLE"
    FAIL_TERMINAL = "FAIL_TERMINAL"
    NEEDS_HELP = "NEEDS_HELP"
    REJECTED = "REJECTED"


class UntranscriptedIOStatus(str, Enum):
    """04.7 §PHASE 4 — fail-closed status of IO transcript checks."""

    CLEAN = "CLEAN"
    DETECTED = "DETECTED"
    UNAVAILABLE = "UNAVAILABLE"


class CapabilityViolationStatus(str, Enum):
    """04.7 §PHASE 4 — capability check status."""

    CLEAN = "CLEAN"
    DETECTED = "DETECTED"


class SandboxEscapeStatus(str, Enum):
    """04.7 §PHASE 4 — sandbox escape detection status."""

    CLEAN = "CLEAN"
    DETECTED = "DETECTED"


# ---------------------------------------------------------------------------
# 1. PTCExecutionProfile (04.7 §PHASE 1.1)
# ---------------------------------------------------------------------------


class PTCContractError(ValueError):
    """Raised when a PTC contract is constructed in violation of doc 04.7."""


@dataclass(frozen=True)
class HumanReviewThreshold:
    """04.7 §PHASE 1.1 human_review_thresholds.

    The three values feed L5/E2 logic that decides whether a script must be
    routed to a human reviewer before execution:

      * ``confidence_below`` — script confidence score under this triggers
        review.
      * ``risk_above`` — risk score over this triggers review.
      * ``policy_ambiguity_above`` — policy ambiguity score over this
        triggers L5 certification evidence requirement.
    """

    confidence_below: float = 0.6
    risk_above: float = 0.7
    policy_ambiguity_above: float = 0.4


@dataclass(frozen=True)
class PTCExecutionProfile:
    """04.7 §PHASE 1.1 — what the sandbox is allowed to do.

    Constructed by L0/L3 (the route-aware actor) and signed before reaching
    L2. L2 reads this profile only; it does not synthesize one.
    """

    ptc_profile_id: str
    route_id: str
    execution_form: str
    script_language: PTCScriptLanguage
    allowed_tool_calls: tuple[str, ...]
    max_tool_calls: int
    max_runtime_ms: int
    max_stdout_bytes: int
    max_stderr_bytes: int
    max_raw_result_bytes: int
    human_review_thresholds: HumanReviewThreshold = field(default_factory=HumanReviewThreshold)
    context_freeze_required: bool = True
    raw_result_context_policy: RawResultContextPolicy = RawResultContextPolicy.SANDBOX_ONLY
    stdout_return_policy: StdoutReturnPolicy = StdoutReturnPolicy.SUMMARY_ONLY
    l5_reclearance_required_on_modify: bool = True
    fail_closed_on_untranscripted_io: bool = True

    def __post_init__(self) -> None:
        if not self.allowed_tool_calls:
            raise PTCContractError("allowed_tool_calls must not be empty")
        if self.max_tool_calls < 1:
            raise PTCContractError(f"max_tool_calls must be >= 1, got {self.max_tool_calls}")
        if self.max_runtime_ms < 1:
            raise PTCContractError("max_runtime_ms must be > 0")
        for cap_name, cap_val in (
            ("max_stdout_bytes", self.max_stdout_bytes),
            ("max_stderr_bytes", self.max_stderr_bytes),
            ("max_raw_result_bytes", self.max_raw_result_bytes),
        ):
            if cap_val < 0:
                raise PTCContractError(f"{cap_name} must be >= 0, got {cap_val}")
        if not self.context_freeze_required:
            raise PTCContractError(
                "context_freeze_required must be True per 04.7 §PHASE 1.1"
            )
        if self.raw_result_context_policy is not RawResultContextPolicy.SANDBOX_ONLY:
            raise PTCContractError(
                "raw_result_context_policy must be SANDBOX_ONLY per 04.7 §PHASE 4"
            )

    def tool_is_allowed(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tool_calls


# ---------------------------------------------------------------------------
# 2. PTCScriptEnvelope (04.7 §PHASE 1.2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PTCScriptEnvelope:
    """04.7 §PHASE 1.2 — signed script package.

    ``script_text_ref`` is an opaque reference to the script content (the
    sandbox loads it through the governed channel; we do not attach raw text
    to the envelope). ``script_digest`` MUST be a content hash for replay.
    """

    ptc_script_envelope_id: str
    approved_work_order_ref: str
    script_text_ref: str
    script_digest: str
    imports_allowlist: tuple[str, ...]
    filesystem_allowlist: tuple[str, ...]
    network_allowlist: tuple[str, ...]
    tool_call_manifest: tuple[str, ...]
    expected_stdout_schema: str
    deterministic_seed: str
    replay_key: str
    disallowed_patterns: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.script_digest:
            raise PTCContractError("script_digest must be non-empty")
        if not self.approved_work_order_ref:
            raise PTCContractError("approved_work_order_ref must be non-empty")
        if not self.expected_stdout_schema:
            raise PTCContractError("expected_stdout_schema must be non-empty")
        if not self.replay_key:
            raise PTCContractError("replay_key must be non-empty")


# ---------------------------------------------------------------------------
# 3. PTCSandboxReceipt (04.7 §PHASE 1.3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PTCToolCallReceipt:
    """One tool call inside the PTC sandbox.

    The result is captured by ``raw_result_ref`` (sandbox-only), not by
    inlining the raw bytes on the receipt itself.
    """

    tool_call_id: str
    tool_name: str
    args_hash: str
    raw_result_ref: str
    return_code: int
    started_at_unix: float
    ended_at_unix: float
    error: str | None = None


@dataclass(frozen=True)
class PTCSandboxReceipt:
    """04.7 §PHASE 1.3 — sealed receipt the sandbox emits.

    Invariants enforced at construction:

      * ``raw_result_refs_sandbox_only`` may not contain inline content; we
        check that each entry is a ref string, not bulk bytes (length cap).
      * If ``untranscripted_io_status`` is DETECTED, the result must be
        REJECTED (fail-closed).
      * If ``capability_violation_status`` is DETECTED, the result must be
        REJECTED.
      * If ``sandbox_escape_status`` is DETECTED, the result must be
        REJECTED.
    """

    ptc_sandbox_receipt_id: str
    script_envelope_ref: str
    context_freeze_receipt_ref: str
    context_unfreeze_receipt_ref: str
    tool_call_receipts: tuple[PTCToolCallReceipt, ...]
    raw_result_refs_sandbox_only: tuple[str, ...]
    stdout_summary_ref: str
    stderr_summary_ref: str
    untranscripted_io_status: UntranscriptedIOStatus
    capability_violation_status: CapabilityViolationStatus
    sandbox_escape_status: SandboxEscapeStatus
    result_class: PTCResultClass
    deterministic_digest: str
    sealed_at: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        # Refs MUST be opaque strings, not bulk bytes inlined as strings.
        for idx, ref in enumerate(self.raw_result_refs_sandbox_only):
            if not isinstance(ref, str):
                raise PTCContractError(
                    f"raw_result_refs_sandbox_only[{idx}] must be a string ref"
                )
            # Heuristic guard: a "ref" should be short. >2 KB is bulk leakage.
            if len(ref) > 2048:
                raise PTCContractError(
                    f"raw_result_refs_sandbox_only[{idx}] is too large to be a ref "
                    f"(len={len(ref)} > 2048); raw payload must NOT inline into the receipt"
                )

        if (
            self.untranscripted_io_status is UntranscriptedIOStatus.DETECTED
            and self.result_class is not PTCResultClass.REJECTED
        ):
            raise PTCContractError(
                "untranscripted_io_status=DETECTED requires result_class=REJECTED (fail-closed)"
            )
        if (
            self.capability_violation_status is CapabilityViolationStatus.DETECTED
            and self.result_class is not PTCResultClass.REJECTED
        ):
            raise PTCContractError(
                "capability_violation_status=DETECTED requires result_class=REJECTED"
            )
        if (
            self.sandbox_escape_status is SandboxEscapeStatus.DETECTED
            and self.result_class is not PTCResultClass.REJECTED
        ):
            raise PTCContractError(
                "sandbox_escape_status=DETECTED requires result_class=REJECTED"
            )

    def is_clean(self) -> bool:
        """True iff the sandbox observed no fail-closed conditions."""
        return (
            self.untranscripted_io_status is UntranscriptedIOStatus.CLEAN
            and self.capability_violation_status is CapabilityViolationStatus.CLEAN
            and self.sandbox_escape_status is SandboxEscapeStatus.CLEAN
        )


__all__ = [
    "CapabilityViolationStatus",
    "HumanReviewThreshold",
    "PTCContractError",
    "PTCExecutionProfile",
    "PTCResultClass",
    "PTCSandboxReceipt",
    "PTCScriptEnvelope",
    "PTCScriptLanguage",
    "PTCToolCallReceipt",
    "RawResultContextPolicy",
    "SandboxEscapeStatus",
    "StdoutReturnPolicy",
    "UntranscriptedIOStatus",
]
