"""U0 ValidatedRequest -> L1 L1PlanContract bridge.

Pure shape mapping. No semantic interpretation, no I/O, no model call.
Per the L1 spec (02_L1_Reasoning), this layer is the smallest possible
adapter that turns the bounded U0 ticket into the C0-input L1PlanContract.

Caller must already have a passing ``ValidatedRequest`` from
``agentic_core.L0_routing.intake.IntakePipeline``. Bridge does not validate
again; it trusts the U0 stamp.

Mapping rules (deliberately deterministic):

  user_task_text       <- vr.normalized_payload (or "" if None)
  task_spec            <- f"intake.{vr.request_shape_class}" (e.g.
                          "intake.api_json", "intake.chat_text")
  query_spec           <- "user_query" if grounding_required else
                          "internal_action"
  grounding_required   <- True by default; callers may override

The bridge returns the L1PlanContract that flows into L0/C0. It does not
itself decide grounding need — that is L1's reasoning_plan stage. We
default to True (fail-closed: assume grounding needed unless a higher
layer disables it).
"""
from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval.route_contract import L1PlanContract
from agentic_core.L0_routing.intake.validated_request import ValidatedRequest


def validated_request_to_plan_contract(
    vr: ValidatedRequest,
    *,
    grounding_required: bool = True,
    task_spec_override: str | None = None,
    query_spec_override: str | None = None,
) -> L1PlanContract:
    """Translate a passing :class:`ValidatedRequest` into a
    :class:`L1PlanContract` ready for L0 routing.

    Args:
        vr: A successfully-stamped intake slip. ``permitted_next_layer``
            MUST be ``"L1"`` (intake's invariant; we re-assert here).
        grounding_required: Fail-closed default True. Higher-layer policy
            (e.g. an internal-action route) may pass False.
        task_spec_override: If provided, overrides the derived task_spec.
        query_spec_override: If provided, overrides the derived query_spec.

    Returns:
        Frozen :class:`L1PlanContract`.

    Raises:
        ValueError: If the validated request was not authorized for L1
            (defense-in-depth — should never happen if intake honored its
            own invariants).
    """
    if vr.permitted_next_layer != "L1":
        raise ValueError(
            "validated_request_to_plan_contract: vr.permitted_next_layer "
            f"must be 'L1', got {vr.permitted_next_layer!r}"
        )
    if vr.downstream_authority != "none":
        raise ValueError(
            "validated_request_to_plan_contract: vr.downstream_authority "
            "must be 'none' (intake never grants downstream authority)"
        )

    user_text = vr.normalized_payload or ""
    task_spec = task_spec_override or f"intake.{vr.request_shape_class}"
    query_spec = query_spec_override or (
        "user_query" if grounding_required else "internal_action"
    )
    return L1PlanContract(
        task_spec=task_spec,
        query_spec=query_spec,
        user_task_text=user_text,
        grounding_required=grounding_required,
    )


__all__ = ["validated_request_to_plan_contract"]
