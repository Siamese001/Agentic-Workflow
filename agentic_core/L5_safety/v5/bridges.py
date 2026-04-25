"""v5 ↔ v4/CI bridges.

Closes the "honest delegation" gap from the v5 review pass. The v5 module
itself does not re-implement static lane gates, runtime guardrails, LLM
gateway / tool egress, A2A handoff, registry resolution, or UWG promotion —
those are owned by existing v4 modules and CI. But it MUST hand callers
deterministic adapters so that:

1. v5 contracts (``GovernanceReviewRequest``, ``CapabilityTokenV5``,
   ``RiskTierBandV5``, etc.) flow into v4 functions without each caller
   re-writing the conversion.
2. v4 outputs (``GuardrailBankVerdict``, ``HandoffValidationResult``,
   policy-rule violation tuples, registry-snapshot match booleans, blueprint
   path-allowed booleans) flow back into the spec-line-731-745
   ``governance_reports`` shape.

Design contract
---------------

- **No v4 logic is duplicated.** Each bridge is ≤ 30 lines.
- **No v4 imports are required at module load time.** Bridges import lazily
  inside each function so v5 stays usable in environments where v4 isn't
  installed (e.g. partial test fixtures).
- **Each bridge is total over its inputs.** No bridge raises on a healthy v4
  object; bridges only raise when the caller passes a malformed input.
- **Each bridge returns a JSON-serializable dict.** That dict is what
  ``governance_plane.certify_packet`` lifts into ``governance_reports``.

Spec references
---------------

- Static lane S1–S5: spec lines 197–295
- Runtime R1/R2 universal+agent guardrails: spec lines 311–345
- Runtime R4 handoff: spec lines 364–380
- Runtime R8 LLM gateway: spec lines 466–499
- Runtime R9 tool/connector egress: spec lines 501–521
- Authority context G2: spec lines 92–161 (registry resolution + policy bundle)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from agentic_core.L5_safety.v5.contracts import CapabilityTokenV5
from agentic_core.L5_safety.v5.types import RiskTierBandV5

__all__ = [
    "bridge_blueprint_paths",
    "bridge_guardrail_bank",
    "bridge_handoff_validation",
    "bridge_policy_bundle",
    "bridge_registry_token_match",
    "map_v5_band_to_v4",
]


# ---------------------------------------------------------------------------
# Risk-tier mapping
# ---------------------------------------------------------------------------


def map_v5_band_to_v4(band: RiskTierBandV5) -> str:
    """Collapse v5's CRITICAL band onto v4's HIGH for downstream rails.

    v4 (``runtime_rails.RiskTierBand``) is ``Literal['LOW','MODERATE','HIGH']``.
    v5 added ``CRITICAL`` (spec line 71) which v4 never sees. We map
    CRITICAL → HIGH so v4 selectors that branch on the highest band still
    fire correctly. Pure incident-driven escalation (CRITICAL band, no
    structural breach) is handled in the v5 decision rail, not in v4.
    """
    if band == RiskTierBandV5.CRITICAL:
        return "HIGH"
    return band.value


# ---------------------------------------------------------------------------
# S1 — Structure blueprint (static lane)
# ---------------------------------------------------------------------------


def bridge_blueprint_paths(
    *,
    declared_paths: Sequence[str | Path],
) -> dict[str, Any]:
    """Spec S1 (lines 212–225) — structure blueprint path checks.

    Validates a sequence of repo-relative paths against the canonical
    structure blueprint. Returns a JSON-serializable verdict dict suitable
    for ``governance_reports['static_report']``.
    """
    from agentic_core.L5_safety.config.structure_blueprint import (
        has_forbidden_layer_prefix,
        is_path_allowed,
    )

    rejections: list[dict[str, str]] = []
    accepted: list[str] = []
    for raw in declared_paths:
        rel = str(raw)
        try:
            allowed = is_path_allowed(rel)
        except (ValueError, OSError) as exc:
            rejections.append({"path": rel, "reason": f"path_rejected: {exc}"})
            continue
        if not allowed:
            rejections.append({"path": rel, "reason": "not_in_blueprint"})
            continue
        # Filename-level forbidden-prefix check (e.g. "L5_..." in non-L5 layer).
        leaf = Path(rel).name
        prefix_violation = has_forbidden_layer_prefix(leaf)
        if prefix_violation:
            rejections.append({"path": rel, "reason": f"forbidden_prefix:{prefix_violation}"})
            continue
        accepted.append(rel)
    return {
        "checked": len(declared_paths),
        "accepted": accepted,
        "rejected": rejections,
        "passed": len(rejections) == 0,
    }


# ---------------------------------------------------------------------------
# R1/R2 — Guardrail bank (runtime lane)
# ---------------------------------------------------------------------------


def bridge_guardrail_bank(
    *,
    stage: str,
    outcomes: Sequence[Any],
) -> dict[str, Any]:
    """Spec R1/R2 (lines 311–345) — universal + agent-domain guardrail bank.

    Args:
        stage: ``"ingress"``, ``"egress"``, or ``"guard_model"``.
        outcomes: a tuple of v4 ``GuardrailOutcome`` instances from
            upstream guardrail evaluation. Pass empty tuple if no
            evaluation ran (the v4 resolver is total).

    Returns the ``GuardrailBankVerdict`` as a dict, ready for
    ``governance_reports['runtime_guardrail_report']``.
    """
    from agentic_core.L5_safety.identity.guardrail_bank import (  # type: ignore[import-not-found]
        resolve_bank_verdict,
    )

    if stage not in {"ingress", "egress", "guard_model"}:
        raise ValueError(f"bridge_guardrail_bank: invalid stage {stage!r}")
    # GuardrailStage is a typing.Literal, not an Enum — pass the string.
    verdict = resolve_bank_verdict(stage, tuple(outcomes))  # type: ignore[arg-type]
    payload = verdict.to_dict()
    # Normalize v4 'verdict' key onto v5 'decision' so governance_plane
    # rail logic can match a single field name across all bridge reports.
    if "decision" not in payload and "verdict" in payload:
        payload["decision"] = payload["verdict"]
    return payload


# ---------------------------------------------------------------------------
# R4 — A2A handoff validation (runtime lane)
# ---------------------------------------------------------------------------


def bridge_handoff_validation(
    *,
    source_chain: Any,
    target_agent: Any,
    requested_scope_added: Sequence[str] = (),
    requested_scope_removed: Sequence[str] = (),
    risk_tier_band: RiskTierBandV5 = RiskTierBandV5.LOW,
) -> dict[str, Any]:
    """Spec R4 (lines 364–380) — A2A handoff validation.

    Thin wrapper that maps v5's RiskTierBandV5 (4 bands incl. CRITICAL)
    onto v4's RiskTierBand (3 bands) before calling
    ``runtime_rails.validate_handoff``.
    """
    from agentic_core.L5_safety.identity.runtime_rails import (  # type: ignore[import-not-found]
        validate_handoff,
    )

    v4_band = map_v5_band_to_v4(risk_tier_band)
    result = validate_handoff(
        source_chain=source_chain,
        target_agent=target_agent,
        requested_scope_added=tuple(requested_scope_added),
        requested_scope_removed=tuple(requested_scope_removed),
        risk_tier_band=v4_band,  # type: ignore[arg-type]
    )
    return result.to_dict()


# ---------------------------------------------------------------------------
# G2 — Policy bundle validation (authority context)
# ---------------------------------------------------------------------------


def bridge_policy_bundle(*, rules: Sequence[Any]) -> dict[str, Any]:
    """Spec G2 (lines 99–108) — policy bundle integrity.

    Args:
        rules: tuple of v4 ``PolicyRule`` records.

    Returns a dict with ``violations`` (tuple of human-readable strings)
    and ``passed`` boolean for ``governance_reports['policy_validation_report']``.
    """
    from agentic_core.L5_safety.identity.runtime_rails import (  # type: ignore[import-not-found]
        validate_policy_bundle,
    )

    violations = validate_policy_bundle(tuple(rules))
    return {
        "violations": list(violations),
        "rule_count": len(rules),
        "passed": len(violations) == 0,
    }


# ---------------------------------------------------------------------------
# G2 — Registry token verification (authority context)
# ---------------------------------------------------------------------------


def bridge_registry_token_match(
    *,
    capability_token: CapabilityTokenV5,
    current_snapshot: Any,
) -> dict[str, Any]:
    """Spec G2 (lines 116–131) — verify token's registry digest matches snapshot.

    Spec line 7: every certification binds the registry digest. If a token
    was issued against a different registry version, the token is no longer
    valid — even if the principal chain is intact.
    """
    from agentic_core.L5_safety.identity.registries import (  # type: ignore[import-not-found]
        verify_token_against_registry,
    )

    # The v4 helper takes the registry digest. CapabilityTokenV5 doesn't
    # expose a registry_digest field directly — the token-vs-registry binding
    # lives in ``allowed_args_hash`` for v5. We pass the registry digest set
    # from the current snapshot's canonical hash and let v4 compare.
    token_digest = capability_token.allowed_args_hash
    matched, reason = verify_token_against_registry(
        token_registry_digest=token_digest,
        current_snapshot=current_snapshot,
    )
    return {
        "matched": bool(matched),
        "reason": reason,
        "token_digest": token_digest,
    }
