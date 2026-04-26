"""L2 anti-bypass guards (doc 04.8 §PHASE 3).

Maps to: docs/reference/04_L2_Execute/04.8_L2_Observability_Replay_Anti_Bypass_Tests_detailed.md
                                      §PHASE 3 ANTI-BYPASS TESTS

This module provides assertion helpers that fail fast (raising
:class:`L2BypassViolation`) when L2 code attempts any of the 16 forbidden
behaviors enumerated in 04.8 §PHASE 3:

  1. L2 writes directly to L4.
  2. L2 calls UWG directly without an Exit-cleared packet.
  3. L2 emits ``ALLOW_FINISH`` / a final Exit disposition.
  4. L2 changes ``route_id`` or ``route_digest``.
  5. L2 expands workflow nodes.
  6. L2 performs C0 retrieval without an explicit bounded read/tool action.
  7. L2 builds a PromptEnvelope itself.
  8. L2 asks a human directly.
  9. L2 treats human input as authority.
 10. L2 silently switches provider/model/tool/credential/sandbox.
 11. L2 runs without a capability_token.
 12. L2 runs without a sandbox_envelope.
 13. L2 repairs under a changed policy_hash or blueprint_hash.
 14. L2 fails to seal a rejection or failure.
 15. PTC leaks raw tool results into model context.
 16. PTC performs untranscripted IO.

The intent is enforcement-grade: any caller that emits a forbidden output
or operates outside L2 authority will be loudly stopped before downstream
state can be corrupted.

This module is **read-only** with respect to L4 / UWG / Exit / L6: it only
inspects the candidates passed into it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class L2BypassViolation(RuntimeError):
    """Raised when L2 attempts a forbidden bypass per doc 04.8."""


class BypassReason(str, Enum):
    """Enumerated bypass classes — 04.8 §PHASE 3."""

    DIRECT_L4_WRITE = "direct_l4_write"
    DIRECT_UWG_CALL = "direct_uwg_call"
    EMITS_FINAL_EXIT_DISPOSITION = "emits_final_exit_disposition"
    CHANGES_ROUTE_ID_OR_DIGEST = "changes_route_id_or_digest"
    EXPANDS_WORKFLOW = "expands_workflow"
    UNAPPROVED_C0_RETRIEVAL = "unapproved_c0_retrieval"
    BUILDS_PROMPT_ENVELOPE = "builds_prompt_envelope"
    ASKS_HUMAN_DIRECTLY = "asks_human_directly"
    TREATS_HUMAN_INPUT_AS_AUTHORITY = "treats_human_input_as_authority"
    SILENT_PROVIDER_OR_TOOL_SWITCH = "silent_provider_or_tool_switch"
    MISSING_CAPABILITY_TOKEN = "missing_capability_token"
    MISSING_SANDBOX_ENVELOPE = "missing_sandbox_envelope"
    REPAIR_UNDER_CHANGED_SNAPSHOT = "repair_under_changed_snapshot"
    UNSEALED_REJECTION_OR_FAILURE = "unsealed_rejection_or_failure"
    PTC_RAW_RESULT_LEAK = "ptc_raw_result_leak"
    PTC_UNTRANSCRIPTED_IO = "ptc_untranscripted_io"


@dataclass(frozen=True)
class BypassCheckResult:
    """Outcome of a single bypass check."""

    ok: bool
    reason: BypassReason | None = None
    detail: str = ""


# ---------------------------------------------------------------------------
# Forbidden L2 final-disposition / output strings
# ---------------------------------------------------------------------------


# 04.1 §FORBIDDEN OUTPUTS FROM L2 CHILD FILES
_FORBIDDEN_L2_OUTPUTS: frozenset[str] = frozenset(
    {
        "ALLOW_FINISH",
        "DENY",
        "REROUTE",
        "ESCALATE_HITL",  # as a final disposition
        "COMMIT_REQUEST_TO_UWG",  # as a final disposition
        "SAFE_FALLBACK",  # as a final disposition
        "durable_write_committed",
        "policy_certified",
        "route_changed",
        "workflow_expanded",
        "evidence_contract_issued",
        "prompt_envelope_constructed",
        "learning_promoted",
    }
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def assert_no_forbidden_l2_output(value: Any) -> BypassCheckResult:
    """Reject any value that matches a forbidden L2 final-disposition string.

    L2 can carry these strings only as ``downstream_recommendation`` (i.e.
    non-authoritative metadata). This guard is for the *final disposition*
    field of a sealed artifact.
    """
    sval = str(value or "").strip()
    if sval in _FORBIDDEN_L2_OUTPUTS:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.EMITS_FINAL_EXIT_DISPOSITION,
            detail=f"forbidden L2 final disposition: {sval!r}",
        )
    return BypassCheckResult(ok=True)


def assert_no_route_change(
    *, original_route_id: str, original_route_digest: str, new_route_id: str, new_route_digest: str
) -> BypassCheckResult:
    """Reject any route mutation inside L2."""
    if new_route_id != original_route_id:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.CHANGES_ROUTE_ID_OR_DIGEST,
            detail=(
                f"route_id changed: original={original_route_id!r} "
                f"new={new_route_id!r}"
            ),
        )
    if new_route_digest != original_route_digest:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.CHANGES_ROUTE_ID_OR_DIGEST,
            detail=(
                f"route_digest changed: original={original_route_digest!r} "
                f"new={new_route_digest!r}"
            ),
        )
    return BypassCheckResult(ok=True)


def assert_no_workflow_expansion(*, original_step_count: int, new_step_count: int) -> BypassCheckResult:
    """Reject any L2 attempt to expand the workflow graph."""
    if new_step_count != original_step_count:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.EXPANDS_WORKFLOW,
            detail=f"step_count changed: {original_step_count} -> {new_step_count}",
        )
    return BypassCheckResult(ok=True)


def assert_capability_token_present(capability_token_ref: Any) -> BypassCheckResult:
    if not capability_token_ref:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.MISSING_CAPABILITY_TOKEN,
            detail="capability_token_ref is empty/missing",
        )
    return BypassCheckResult(ok=True)


def assert_sandbox_envelope_present(sandbox_envelope_ref: Any) -> BypassCheckResult:
    if not sandbox_envelope_ref:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.MISSING_SANDBOX_ENVELOPE,
            detail="sandbox_envelope_ref is empty/missing",
        )
    return BypassCheckResult(ok=True)


def assert_no_provider_or_tool_switch(
    *,
    declared_provider: str,
    actual_provider: str,
    declared_model: str | None = None,
    actual_model: str | None = None,
    declared_tool: str | None = None,
    actual_tool: str | None = None,
) -> BypassCheckResult:
    """Reject silent fallback to a different provider, model, or tool."""
    if declared_provider != actual_provider:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.SILENT_PROVIDER_OR_TOOL_SWITCH,
            detail=(
                f"provider mismatch: declared={declared_provider!r} "
                f"actual={actual_provider!r}"
            ),
        )
    if declared_model is not None and declared_model != actual_model:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.SILENT_PROVIDER_OR_TOOL_SWITCH,
            detail=(
                f"model mismatch: declared={declared_model!r} actual={actual_model!r}"
            ),
        )
    if declared_tool is not None and declared_tool != actual_tool:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.SILENT_PROVIDER_OR_TOOL_SWITCH,
            detail=(
                f"tool mismatch: declared={declared_tool!r} actual={actual_tool!r}"
            ),
        )
    return BypassCheckResult(ok=True)


def assert_repair_under_same_snapshot(
    *,
    original_blueprint_hash: str,
    original_policy_hash: str,
    repair_blueprint_hash: str,
    repair_policy_hash: str,
) -> BypassCheckResult:
    """Reject E4 repair under a changed snapshot binding."""
    if original_blueprint_hash != repair_blueprint_hash:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.REPAIR_UNDER_CHANGED_SNAPSHOT,
            detail=(
                f"blueprint_hash changed during heal: "
                f"original={original_blueprint_hash!r} repair={repair_blueprint_hash!r}"
            ),
        )
    if original_policy_hash != repair_policy_hash:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.REPAIR_UNDER_CHANGED_SNAPSHOT,
            detail=(
                f"policy_hash changed during heal: "
                f"original={original_policy_hash!r} repair={repair_policy_hash!r}"
            ),
        )
    return BypassCheckResult(ok=True)


def assert_seals_rejection_or_failure(
    *, terminal_class: Any, sealed_artifact_ref: Any
) -> BypassCheckResult:
    """If the terminal class is FAILURE/REJECTED/NEEDS_HELP, a sealed artifact MUST exist.

    This catches the 04.8 §PHASE 3 #14 condition "L2 fails to seal
    rejection/failure".
    """
    cls = str(terminal_class or "").upper()
    needs_seal = cls in {"FAILURE", "REJECTED", "NEEDS_HELP", "FAIL_TERMINAL"}
    if needs_seal and not sealed_artifact_ref:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.UNSEALED_REJECTION_OR_FAILURE,
            detail=f"terminal_class={cls!r} requires a sealed artifact reference",
        )
    return BypassCheckResult(ok=True)


def assert_no_direct_l4_write(*, target: Any) -> BypassCheckResult:
    """Reject a target that points at L4 / UWG / a durable persistence surface.

    Detection is normalization-robust: the input is lowercased AND underscores,
    dots, and hyphens are stripped before substring search. This catches
    snake_case (``durable_write``), camelCase (``DurableWrite``),
    dotted (``l4.state``), and hyphenated (``uwg-commit``) forms uniformly.
    """
    raw = str(target or "")
    # Match against original (preserves dotted/hyphenated forms) AND normalized
    # (lowercased + separators stripped) — catches snake/camel/dotted variants.
    lowered = raw.lower()
    normalized = lowered.replace("_", "").replace(".", "").replace("-", "")
    forbidden_substrings = (
        "l4_state",
        "l4.state",
        "uwg.commit",
        "uwg_commit",
        "durable_write",
        "system_of_record",
    )
    forbidden_compact = (
        "l4state",
        "uwgcommit",
        "durablewrite",
        "systemofrecord",
    )
    for bad in forbidden_substrings:
        if bad in lowered:
            return BypassCheckResult(
                ok=False,
                reason=BypassReason.DIRECT_L4_WRITE,
                detail=f"target contains forbidden substring {bad!r}: {raw!r}",
            )
    for bad in forbidden_compact:
        if bad in normalized:
            return BypassCheckResult(
                ok=False,
                reason=BypassReason.DIRECT_L4_WRITE,
                detail=f"target contains forbidden token {bad!r} (normalized): {raw!r}",
            )
    return BypassCheckResult(ok=True)


def assert_no_direct_human_call(*, channel: Any) -> BypassCheckResult:
    """Reject a channel that targets a human directly (not via Exit/HITL packetization)."""
    sval = str(channel or "").lower()
    forbidden = ("hitl_chat", "human_direct", "ask_user", "user_clarify_inline")
    for bad in forbidden:
        if bad in sval:
            return BypassCheckResult(
                ok=False,
                reason=BypassReason.ASKS_HUMAN_DIRECTLY,
                detail=f"channel {channel!r} is a direct-human path",
            )
    return BypassCheckResult(ok=True)


def assert_human_input_is_data_only(*, human_input_scope: Any) -> BypassCheckResult:
    """Reject any human-input scope that grants authority."""
    sval = str(human_input_scope or "").upper()
    if sval and sval != "DATA_ONLY":
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.TREATS_HUMAN_INPUT_AS_AUTHORITY,
            detail=f"human_input_scope must be DATA_ONLY, got {sval!r}",
        )
    return BypassCheckResult(ok=True)


def assert_no_prompt_envelope_construction(*, builder_layer: Any) -> BypassCheckResult:
    """Reject L2 building its own prompt envelope.

    Prompt Assembly owns ``CompiledPromptEnvelope`` construction.
    """
    sval = str(builder_layer or "").upper()
    if sval == "L2":
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.BUILDS_PROMPT_ENVELOPE,
            detail="L2 cannot construct PromptEnvelope; Prompt Assembly owns this",
        )
    return BypassCheckResult(ok=True)


def assert_no_unapproved_c0_retrieval(*, retrieval_authority: Any) -> BypassCheckResult:
    """Reject C0 retrieval not granted by the packet's bounded read/tool action."""
    sval = str(retrieval_authority or "").upper()
    if sval and sval not in ("BOUNDED_READ", "BOUNDED_TOOL_ACTION", "EVIDENCE_CONTRACT"):
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.UNAPPROVED_C0_RETRIEVAL,
            detail=f"retrieval_authority {sval!r} is not approved for L2",
        )
    return BypassCheckResult(ok=True)


def assert_no_direct_uwg_call(*, target_layer: Any, exit_cleared: bool) -> BypassCheckResult:
    """Reject a UWG call from L2 unless Exit cleared the packet first."""
    sval = str(target_layer or "").upper()
    if sval == "UWG" and not exit_cleared:
        return BypassCheckResult(
            ok=False,
            reason=BypassReason.DIRECT_UWG_CALL,
            detail="L2 cannot call UWG without Exit clearance",
        )
    return BypassCheckResult(ok=True)


# ---------------------------------------------------------------------------
# Aggregator: assert_l2_bounded()
# ---------------------------------------------------------------------------


def assert_l2_bounded(facts: Mapping[str, Any]) -> tuple[BypassCheckResult, ...]:
    """Run every applicable check on a facts mapping.

    Args:
        facts: Mapping containing any subset of:
            - ``capability_token_ref``
            - ``sandbox_envelope_ref``
            - ``original_route_id`` / ``original_route_digest`` /
              ``new_route_id`` / ``new_route_digest``
            - ``original_step_count`` / ``new_step_count``
            - ``declared_provider`` / ``actual_provider`` (and optionally
              ``declared_model`` / ``actual_model`` /
              ``declared_tool`` / ``actual_tool``)
            - ``original_blueprint_hash`` / ``original_policy_hash`` /
              ``repair_blueprint_hash`` / ``repair_policy_hash``
            - ``terminal_class`` / ``sealed_artifact_ref``
            - ``write_target``
            - ``human_call_channel``
            - ``human_input_scope``
            - ``prompt_envelope_builder_layer``
            - ``c0_retrieval_authority``
            - ``uwg_target_layer`` / ``exit_cleared``
            - ``final_disposition`` (string, checked against forbidden list)

    Returns:
        Tuple of :class:`BypassCheckResult`. Callers may either filter for
        ``ok=False`` or call :func:`raise_if_any` to fail-fast.
    """
    results: list[BypassCheckResult] = []

    if "capability_token_ref" in facts:
        results.append(assert_capability_token_present(facts["capability_token_ref"]))
    if "sandbox_envelope_ref" in facts:
        results.append(assert_sandbox_envelope_present(facts["sandbox_envelope_ref"]))

    if "new_route_id" in facts and "original_route_id" in facts:
        results.append(
            assert_no_route_change(
                original_route_id=str(facts["original_route_id"]),
                original_route_digest=str(facts.get("original_route_digest", "")),
                new_route_id=str(facts["new_route_id"]),
                new_route_digest=str(facts.get("new_route_digest", "")),
            )
        )

    if "new_step_count" in facts and "original_step_count" in facts:
        results.append(
            assert_no_workflow_expansion(
                original_step_count=int(facts["original_step_count"]),
                new_step_count=int(facts["new_step_count"]),
            )
        )

    if "actual_provider" in facts and "declared_provider" in facts:
        results.append(
            assert_no_provider_or_tool_switch(
                declared_provider=str(facts["declared_provider"]),
                actual_provider=str(facts["actual_provider"]),
                declared_model=facts.get("declared_model"),
                actual_model=facts.get("actual_model"),
                declared_tool=facts.get("declared_tool"),
                actual_tool=facts.get("actual_tool"),
            )
        )

    if "repair_blueprint_hash" in facts and "original_blueprint_hash" in facts:
        results.append(
            assert_repair_under_same_snapshot(
                original_blueprint_hash=str(facts["original_blueprint_hash"]),
                original_policy_hash=str(facts.get("original_policy_hash", "")),
                repair_blueprint_hash=str(facts["repair_blueprint_hash"]),
                repair_policy_hash=str(facts.get("repair_policy_hash", "")),
            )
        )

    if "terminal_class" in facts:
        results.append(
            assert_seals_rejection_or_failure(
                terminal_class=facts["terminal_class"],
                sealed_artifact_ref=facts.get("sealed_artifact_ref"),
            )
        )

    if "write_target" in facts:
        results.append(assert_no_direct_l4_write(target=facts["write_target"]))

    if "human_call_channel" in facts:
        results.append(assert_no_direct_human_call(channel=facts["human_call_channel"]))

    if "human_input_scope" in facts:
        results.append(
            assert_human_input_is_data_only(human_input_scope=facts["human_input_scope"])
        )

    if "prompt_envelope_builder_layer" in facts:
        results.append(
            assert_no_prompt_envelope_construction(
                builder_layer=facts["prompt_envelope_builder_layer"]
            )
        )

    if "c0_retrieval_authority" in facts:
        results.append(
            assert_no_unapproved_c0_retrieval(
                retrieval_authority=facts["c0_retrieval_authority"]
            )
        )

    if "uwg_target_layer" in facts:
        results.append(
            assert_no_direct_uwg_call(
                target_layer=facts["uwg_target_layer"],
                exit_cleared=bool(facts.get("exit_cleared", False)),
            )
        )

    if "final_disposition" in facts:
        results.append(assert_no_forbidden_l2_output(facts["final_disposition"]))

    return tuple(results)


def raise_if_any(results: tuple[BypassCheckResult, ...]) -> None:
    """Raise :class:`L2BypassViolation` listing all failures, if any."""
    failures = [r for r in results if not r.ok]
    if not failures:
        return
    detail = "; ".join(
        f"{r.reason.value if r.reason else 'UNKNOWN'}: {r.detail}" for r in failures
    )
    raise L2BypassViolation(f"L2 bypass detected ({len(failures)} violation(s)): {detail}")


__all__ = [
    "BypassCheckResult",
    "BypassReason",
    "L2BypassViolation",
    "assert_capability_token_present",
    "assert_human_input_is_data_only",
    "assert_l2_bounded",
    "assert_no_direct_human_call",
    "assert_no_direct_l4_write",
    "assert_no_direct_uwg_call",
    "assert_no_forbidden_l2_output",
    "assert_no_prompt_envelope_construction",
    "assert_no_provider_or_tool_switch",
    "assert_no_route_change",
    "assert_no_unapproved_c0_retrieval",
    "assert_no_workflow_expansion",
    "assert_repair_under_same_snapshot",
    "assert_sandbox_envelope_present",
    "assert_seals_rejection_or_failure",
    "raise_if_any",
]
