"""PA.1 BOM resolver — twelve slot/manifest sub-stages (PA.1A–PA.1L).

Each stage has a strict input → typed output mapping per the spec
(lines 402–828). The resolver is **deterministic and pure** — it does not
fetch templates, mixins, or evidence; callers pass concrete content via the
``sources`` mapping and the resolver returns typed slot blocks plus a
:class:`PromptBOMResolved` struct that mirrors the spec literal.

Validation rules from each PA.1x sub-section are enforced:

    PA.1A S0   — must be present, must be hash-validated, never user-supplied
    PA.1B D0   — must align with route risk; must include retrieved-content
                 controls when C0 is present
    PA.1C I0   — must be approved + agent-compatible
    PA.1D E0   — exemplars must be safe + budget-aware (or empty)
    PA.1E C0   — chunk classes (MUST_USE/SUPPORTING/CONTRADICTS/BACKGROUND/
                 EXCLUDED) preserved
    PA.1F M0   — provider-compliant, no chain-of-thought exposure
    PA.1G U0   — origin_trust=user_turn, role override neutralized
    PA.1H Y0   — promoted via L6→UWG→L4 only
    PA.1I H0   — bounded re-entry, retry within threshold
    PA.1J R0   — schema parseable + provider-compatible
    PA.1K Tools — every tool registry-valid + capability-token-allowed
    PA.1L Exec metadata — replay fields complete + hashes consistent
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Mapping

from .input_contracts import UpstreamInputBundle

# ---------------------------------------------------------------------------
# Slot-block dataclasses (spec literal names)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class S0Block:
    content: str
    system_version_hash: str
    valid: bool
    reason: str = ""


@dataclass(frozen=True)
class D0FenceBlock:
    content: str
    fences_applied: tuple[str, ...]
    matches_route_risk: bool
    includes_retrieved_content_controls: bool
    valid: bool
    reason: str = ""


@dataclass(frozen=True)
class I0InstructionBlock:
    content: str
    mixin_ids: tuple[str, ...]
    approved: bool
    agent_compatible: bool
    valid: bool
    reason: str = ""


@dataclass(frozen=True)
class E0ExemplarBlock:
    content: str
    exemplar_ids: tuple[str, ...]
    safe: bool
    budget_safe: bool


@dataclass(frozen=True)
class C0GroundedContextBlock:
    must_use: tuple[dict[str, Any], ...]
    supporting: tuple[dict[str, Any], ...]
    contradicts: tuple[dict[str, Any], ...]
    background: tuple[dict[str, Any], ...]
    excluded: tuple[dict[str, Any], ...]
    support_score: float
    unresolved_gaps: tuple[str, ...]
    contradictions_preserved: bool
    valid: bool
    reason: str = ""


@dataclass(frozen=True)
class M0MetaControlBlock:
    content: str
    provider_compliant: bool
    no_cot_exposure: bool


@dataclass(frozen=True)
class U0NeutralizedTaskBlock:
    content: str
    raw_text_hash: str
    neutralized_text_hash: str
    origin_trust: str
    injection_score: float
    disposition: str  # clean | sanitized | reject
    stripped_segments: tuple[str, ...] = ()
    retained_constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class Y0LearningPriorBlock:
    content: str
    promoted_via_l6_uwg_l4: bool
    policy_hash_compatible: bool
    accepted: bool
    reason: str = ""


@dataclass(frozen=True)
class H0HealingHintBlock:
    content: str
    same_policy_hash: bool
    same_blueprint_hash: bool
    no_scope_widening: bool
    retry_count: int
    accepted: bool
    reason: str = ""


@dataclass(frozen=True)
class R0SchemaBinding:
    schema: dict[str, Any]
    schema_version: str
    parseable: bool
    provider_compatible: bool
    can_represent_abstain: bool
    can_represent_citations: bool
    valid: bool
    reason: str = ""


@dataclass(frozen=True)
class ToolBindingManifest:
    tools: tuple[dict[str, Any], ...]
    capability_token: str
    sandbox_envelope: dict[str, Any]
    every_tool_in_registry: bool
    every_tool_allowed_by_token: bool
    valid: bool
    reason: str = ""


@dataclass(frozen=True)
class ExecutionMetadataBlock:
    replay_key: str
    policy_hash: str
    blueprint_hash: str
    plan_id: str
    route_id: str
    trace_root: str
    run_id: str
    attempt_id: str
    idempotency_nonce: str
    model_id: str
    provider_lane: str
    temperature: float | None
    thinking_level: str
    tokenizer_id: str
    budget_ceiling: int
    manifest_input_list: tuple[str, ...]
    signature_key_reference: str
    deterministic_inputs_separated: bool
    hashes_consistent: bool
    valid: bool
    reason: str = ""


@dataclass(frozen=True)
class PromptBOMResolved:
    """Spec PA.1 BOM literal — full bill of materials."""

    bom_id: str
    system_version_hash: str
    policy_hash: str
    agent_spec_id: str
    route_contract_id: str
    plan_id: str
    evidence_contract_id: str
    s0: S0Block
    d0: D0FenceBlock
    i0: I0InstructionBlock
    e0: E0ExemplarBlock
    c0: C0GroundedContextBlock
    m0: M0MetaControlBlock
    u0: U0NeutralizedTaskBlock
    y0: Y0LearningPriorBlock
    h0: H0HealingHintBlock
    r0: R0SchemaBinding
    tool_binding_manifest: ToolBindingManifest
    execution_metadata: ExecutionMetadataBlock
    slots_requested: tuple[str, ...]
    slots_available: tuple[str, ...]
    slots_missing: tuple[str, ...]
    valid: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Resolver helpers
# ---------------------------------------------------------------------------


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _resolve_s0(
    bundle: UpstreamInputBundle,
    sources: Mapping[str, Any],
) -> S0Block:
    """PA.1A — system identity. Must be present + hash-validated."""
    content = str(sources.get("s0_content", ""))
    sys_hash = bundle.governance.system_version_hash or bundle.execution.policy_hash or ""
    if not content:
        return S0Block("", sys_hash, valid=False, reason="s0_missing")
    if "[USER:" in content or "user said:" in content.lower():
        return S0Block(content, sys_hash, valid=False, reason="s0_contains_user_input")
    if not sys_hash:
        return S0Block(content, "", valid=False, reason="s0_no_system_version_hash")
    return S0Block(content, sys_hash, valid=True)


def _resolve_d0(
    bundle: UpstreamInputBundle,
    sources: Mapping[str, Any],
    has_c0: bool,
) -> D0FenceBlock:
    """PA.1B — developer fences. Must align with route risk; must include
    retrieved-content controls when C0 is present."""
    fences = tuple(sources.get("d0_fences") or bundle.governance.role_fences)
    content = "\n".join(fences) if fences else ""
    risk = (bundle.plan.risk_hint or "").lower()
    posture = (bundle.governance.allowed_tool_posture or "").lower()
    aligned = bool(fences) and (
        risk in {"low", "medium", "high"} or posture in {"none", "read_only", "limited", "full"}
    )
    rc_controls_required = has_c0
    # B2 hardening: a fence saying merely "in this context" is NOT a
    # retrieved-content control. Require an anchored phrase that mentions
    # "retrieved" content / context / data / chunks. The bare word "context"
    # is too common in normal English to count.
    _rc_anchors = (
        "retrieved content",
        "retrieved-content",
        "retrieved context",
        "retrieved data",
        "retrieved chunk",
        "retrieved chunks",
        "treat retrieved",
    )
    rc_present = any(any(anchor in f.lower() for anchor in _rc_anchors) for f in fences)
    if not fences:
        return D0FenceBlock("", (), False, False, valid=False, reason="d0_empty")
    if rc_controls_required and not rc_present:
        return D0FenceBlock(
            content,
            fences,
            aligned,
            False,
            valid=False,
            reason="d0_missing_retrieved_content_controls",
        )
    return D0FenceBlock(content, fences, aligned, rc_present or not rc_controls_required, valid=True)


def _resolve_i0(
    bundle: UpstreamInputBundle,
    sources: Mapping[str, Any],
) -> I0InstructionBlock:
    """PA.1C — instructional. Approved mixins + agent-compatible."""
    mixin_ids = tuple(sources.get("i0_mixin_ids", ()))
    content = str(sources.get("i0_content", ""))
    approved = bool(sources.get("i0_approved", True))
    compatible = bool(sources.get("i0_agent_compatible", True))
    if not approved:
        return I0InstructionBlock(
            content, mixin_ids, False, compatible, valid=False, reason="i0_not_approved"
        )
    if not compatible:
        return I0InstructionBlock(
            content, mixin_ids, approved, False, valid=False, reason="i0_agent_incompatible"
        )
    return I0InstructionBlock(content, mixin_ids, True, True, valid=True)


def _resolve_e0(sources: Mapping[str, Any]) -> E0ExemplarBlock:
    """PA.1D — exemplars (optional). Safe + budget-aware."""
    ids = tuple(sources.get("e0_exemplar_ids", ()))
    content = str(sources.get("e0_content", ""))
    safe = bool(sources.get("e0_safe", True))
    budget_safe = bool(sources.get("e0_budget_safe", True))
    return E0ExemplarBlock(content, ids, safe, budget_safe)


def _resolve_c0(bundle: UpstreamInputBundle) -> C0GroundedContextBlock:
    """PA.1E — grounded retrieved context. Five chunk classes preserved."""
    classes = bundle.evidence.evidence_classes or {}

    def _coerce(item: Any) -> dict[str, Any]:
        if isinstance(item, Mapping):
            return dict(item)
        # str / int / anything atomic becomes an {id: ...} singleton.
        return {"id": str(item)}

    def _to_dicts(key: str) -> tuple[dict[str, Any], ...]:
        items = classes.get(key, ())
        # G1 hardening: a bare string like "chunk-abc" was previously iterated
        # per-character (yielding {"id":"c"}, {"id":"h"}, ...). Treat strings
        # and non-iterables as a single-element collection.
        if isinstance(items, (str, bytes)) or isinstance(items, Mapping):
            items = (items,)
        elif not hasattr(items, "__iter__"):
            items = (items,)
        return tuple(_coerce(x) for x in items)

    must_use = _to_dicts("must_use")
    supporting = _to_dicts("supporting")
    contradicts = _to_dicts("contradicts")
    background = _to_dicts("background")
    excluded = _to_dicts("excluded")

    contradictions_preserved = len(contradicts) > 0 if bundle.evidence.contradiction_flags else True
    valid = True
    reason = ""
    if bundle.plan.grounding_required and not (must_use or supporting):
        valid = False
        reason = "c0_grounding_required_no_supporting_evidence"
    if bundle.evidence.contradiction_flags and not contradictions_preserved:
        valid = False
        reason = "c0_contradictions_dropped"

    return C0GroundedContextBlock(
        must_use=must_use,
        supporting=supporting,
        contradicts=contradicts,
        background=background,
        excluded=excluded,
        support_score=float(bundle.evidence.support_score or 0.0),
        unresolved_gaps=bundle.evidence.unresolved_gaps,
        contradictions_preserved=contradictions_preserved,
        valid=valid,
        reason=reason,
    )


def _resolve_m0(bundle: UpstreamInputBundle, sources: Mapping[str, Any]) -> M0MetaControlBlock:
    """PA.1F — meta-controls. Provider-compliant + no CoT exposure."""
    content = str(sources.get("m0_content", ""))
    provider = (bundle.route.provider_lane or "").lower()
    # OpenAI reasoning models forbid "think step by step" style instructions.
    has_cot_exposure = any(
        marker in content.lower()
        for marker in ("show your reasoning", "expose chain-of-thought", "reveal scratchpad")
    )
    provider_compliant = True
    if provider in {"openai_reasoning"} and "step by step" in content.lower():
        provider_compliant = False
    return M0MetaControlBlock(
        content=content,
        provider_compliant=provider_compliant,
        no_cot_exposure=not has_cot_exposure,
    )


def _resolve_u0(bundle: UpstreamInputBundle) -> U0NeutralizedTaskBlock:
    """PA.1G — neutralized user task. origin_trust=user_turn enforced."""
    raw = bundle.execution.raw_user_task
    neutral = bundle.execution.neutralized_user_task or raw
    raw_hash = _sha(raw)
    neutral_hash = _sha(neutral)
    disposition = "clean" if raw == neutral else "sanitized"
    return U0NeutralizedTaskBlock(
        content=neutral,
        raw_text_hash=raw_hash,
        neutralized_text_hash=neutral_hash,
        origin_trust=bundle.execution.origin_trust or "user_turn",
        injection_score=0.0 if raw == neutral else 0.5,
        disposition=disposition,
        stripped_segments=(),
        retained_constraints=(),
    )


def _resolve_y0(bundle: UpstreamInputBundle, sources: Mapping[str, Any]) -> Y0LearningPriorBlock:
    """PA.1H — learning priors. L6→UWG→L4 promotion required."""
    content = str(sources.get("y0_content", ""))
    promoted = bool(sources.get("y0_promoted_via_l6_uwg_l4", False))
    policy_compatible = bool(sources.get("y0_policy_hash_compatible", True))
    accepted = bool(content) and promoted and policy_compatible
    reason = ""
    if content and not promoted:
        reason = "y0_not_promoted_via_l6_uwg_l4"
    elif content and not policy_compatible:
        reason = "y0_policy_hash_incompatible"
    return Y0LearningPriorBlock(content, promoted, policy_compatible, accepted, reason)


def _resolve_h0(sources: Mapping[str, Any]) -> H0HealingHintBlock:
    """PA.1I — healing hints. Same policy_hash + blueprint_hash + retry-bounded."""
    content = str(sources.get("h0_content", ""))
    same_policy = bool(sources.get("h0_same_policy_hash", True))
    same_blueprint = bool(sources.get("h0_same_blueprint_hash", True))
    no_scope_widen = bool(sources.get("h0_no_scope_widening", True))
    retry = int(sources.get("h0_retry_count", 0))
    max_retry = int(sources.get("h0_max_retry", 2))
    accepted = bool(content) and same_policy and same_blueprint and no_scope_widen and retry <= max_retry
    reason = ""
    if content:
        if not same_policy:
            reason = "h0_policy_hash_mismatch"
        elif not same_blueprint:
            reason = "h0_blueprint_hash_mismatch"
        elif not no_scope_widen:
            reason = "h0_scope_widening_detected"
        elif retry > max_retry:
            reason = "h0_retry_threshold_exceeded"
    return H0HealingHintBlock(content, same_policy, same_blueprint, no_scope_widen, retry, accepted, reason)


def _schema_has_field(schema: Mapping[str, Any], field_keywords: tuple[str, ...]) -> bool:
    """Return True iff ``schema`` *structurally* declares a field whose key
    matches any of ``field_keywords``.

    Walks JSON-Schema-shaped dicts:

      * top-level keys
      * ``properties`` (object schemas)
      * ``items.properties`` (array-of-object schemas)
      * ``oneOf`` / ``anyOf`` / ``allOf`` branches

    This avoids the substring-match fragility of ``str(schema)`` — a narrative
    ``description`` containing the word "abstain" will no longer be confused
    with an actual ``abstained`` field.
    """
    if not isinstance(schema, Mapping):
        return False

    def _names(node: Any) -> set[str]:
        out: set[str] = set()
        if isinstance(node, Mapping):
            props = node.get("properties")
            if isinstance(props, Mapping):
                out.update(str(k) for k in props.keys())
            items = node.get("items")
            if isinstance(items, Mapping):
                out |= _names(items)
            for combinator in ("oneOf", "anyOf", "allOf"):
                branches = node.get(combinator)
                if isinstance(branches, (list, tuple)):
                    for b in branches:
                        out |= _names(b)
        return out

    field_names = _names(schema) | {str(k) for k in schema.keys()}
    field_names_lower = {n.lower() for n in field_names}
    for kw in field_keywords:
        kw_l = kw.lower()
        if any(kw_l in name for name in field_names_lower):
            return True
    return False


def _resolve_r0(bundle: UpstreamInputBundle, sources: Mapping[str, Any]) -> R0SchemaBinding:
    """PA.1J — response schema. Parseable + provider-compatible."""
    schema = dict(sources.get("r0_schema") or bundle.governance.response_schema_contract or {})
    schema_version = str(sources.get("r0_schema_version", "")) or str(schema.get("version", ""))
    parseable = isinstance(schema, dict) and len(schema) > 0
    provider_compatible = parseable and bool(sources.get("r0_provider_compatible", True))
    # Prefer explicit boolean flags on the schema; fall back to structural
    # field detection. NEVER do substring-match on the dict's repr — that
    # caused false positives when ``description`` contained the word.
    explicit_abstain = bool(schema.get("can_abstain", False))
    explicit_cite = bool(schema.get("can_cite", False))
    can_abstain = parseable and (explicit_abstain or _schema_has_field(schema, ("abstain", "refuse")))
    can_cite = parseable and (explicit_cite or _schema_has_field(schema, ("citation", "source", "reference")))
    valid = parseable and provider_compatible
    reason = ""
    if not parseable:
        reason = "r0_schema_unparseable"
    elif not provider_compatible:
        reason = "r0_schema_provider_incompatible"
    return R0SchemaBinding(
        schema=schema,
        schema_version=schema_version,
        parseable=parseable,
        provider_compatible=provider_compatible,
        can_represent_abstain=can_abstain,
        can_represent_citations=can_cite,
        valid=valid,
        reason=reason,
    )


def _resolve_tools(bundle: UpstreamInputBundle, sources: Mapping[str, Any]) -> ToolBindingManifest:
    """PA.1K — tool binding. Registry + capability-token validation."""
    tools = tuple(dict(t) for t in (sources.get("tools") or ()))
    cap_token = str(bundle.governance.capability_token or sources.get("capability_token", ""))
    sandbox = dict(bundle.governance.sandbox_envelope or {})
    registry = set(sources.get("tool_registry", ()))
    allowed_by_token = set(sources.get("tools_allowed_by_token", ()))
    every_in_registry = all(t.get("name", "") in registry for t in tools) if registry else True
    every_allowed = all(t.get("name", "") in allowed_by_token for t in tools) if allowed_by_token else True
    valid = every_in_registry and every_allowed
    reason = ""
    if not every_in_registry:
        reason = "tool_registry_mismatch"
    elif not every_allowed:
        reason = "tool_capability_token_mismatch"
    return ToolBindingManifest(
        tools=tools,
        capability_token=cap_token,
        sandbox_envelope=sandbox,
        every_tool_in_registry=every_in_registry,
        every_tool_allowed_by_token=every_allowed,
        valid=valid,
        reason=reason,
    )


def _resolve_exec_metadata(bundle: UpstreamInputBundle, sources: Mapping[str, Any]) -> ExecutionMetadataBlock:
    """PA.1L — replay & execution metadata. Hashes consistent + replay complete."""
    blueprint = str(sources.get("blueprint_hash", "")) or bundle.execution.policy_hash
    manifest_inputs = tuple(sources.get("manifest_input_list", ()))
    sig_key = str(sources.get("signature_key_reference", ""))
    deterministic = bool(sources.get("deterministic_inputs_separated", True))
    hashes = {
        bundle.plan.policy_hash,
        bundle.route.policy_hash,
        bundle.governance.policy_hash,
        bundle.execution.policy_hash,
    } - {""}
    hashes_consistent = len(hashes) <= 1
    valid = bool(bundle.execution.replay_key) and hashes_consistent
    reason = ""
    if not bundle.execution.replay_key:
        reason = "execution_replay_key_missing"
    elif not hashes_consistent:
        reason = "execution_policy_hash_mismatch"
    return ExecutionMetadataBlock(
        replay_key=bundle.execution.replay_key,
        policy_hash=bundle.execution.policy_hash,
        blueprint_hash=blueprint,
        plan_id=bundle.execution.plan_id or bundle.plan.plan_id,
        route_id=bundle.execution.route_id or bundle.route.route_id,
        trace_root=bundle.execution.trace_root,
        run_id=str(sources.get("run_id", "")),
        attempt_id=str(sources.get("attempt_id", "")),
        idempotency_nonce=bundle.execution.idempotency_nonce,
        model_id=bundle.execution.model_id or bundle.route.model_id,
        provider_lane=bundle.execution.provider_target or bundle.route.provider_lane,
        temperature=bundle.route.temperature,
        thinking_level=bundle.route.thinking_level,
        tokenizer_id=bundle.execution.tokenizer_target,
        budget_ceiling=int(sources.get("budget_ceiling", 0)),
        manifest_input_list=manifest_inputs,
        signature_key_reference=sig_key,
        deterministic_inputs_separated=deterministic,
        hashes_consistent=hashes_consistent,
        valid=valid,
        reason=reason,
    )


# ---------------------------------------------------------------------------
# Public resolver
# ---------------------------------------------------------------------------


def resolve_bom(
    bundle: UpstreamInputBundle,
    sources: Mapping[str, Any] | None = None,
) -> PromptBOMResolved:
    """Resolve all 12 sub-stages into a :class:`PromptBOMResolved`.

    ``sources`` is a flat dict that supplies content for slots whose actual
    text is loaded from a registry by the caller (S0/D0/I0/E0/M0/Y0/H0/R0/
    tools/replay).
    """
    src: Mapping[str, Any] = sources or {}
    s0 = _resolve_s0(bundle, src)
    has_c0 = bool(bundle.evidence.evidence_classes) or bool(bundle.evidence.verified_chunks)
    d0 = _resolve_d0(bundle, src, has_c0=has_c0)
    i0 = _resolve_i0(bundle, src)
    e0 = _resolve_e0(src)
    c0 = _resolve_c0(bundle)
    m0 = _resolve_m0(bundle, src)
    u0 = _resolve_u0(bundle)
    y0 = _resolve_y0(bundle, src)
    h0 = _resolve_h0(src)
    r0 = _resolve_r0(bundle, src)
    tools = _resolve_tools(bundle, src)
    exec_meta = _resolve_exec_metadata(bundle, src)

    requested = tuple(bundle.route.required_slots) or ("S0", "D0", "I0", "U0", "R0")
    available: list[str] = []
    if s0.valid:
        available.append("S0")
    if d0.valid:
        available.append("D0")
    if i0.valid:
        available.append("I0")
    if e0.exemplar_ids or e0.content:
        available.append("E0")
    if c0.valid and (c0.must_use or c0.supporting or c0.background):
        available.append("C0")
    if m0.content:
        available.append("M0")
    if u0.content:
        available.append("U0")
    if y0.accepted:
        available.append("Y0")
    if h0.accepted:
        available.append("H0")
    if r0.valid:
        available.append("R0")
    missing = tuple(s for s in requested if s not in available)

    reasons: list[str] = []
    for blk in (s0, d0, i0, c0, y0, h0, r0, tools, exec_meta):
        r = getattr(blk, "reason", "")
        if r:
            reasons.append(r)

    valid = (
        s0.valid and d0.valid and i0.valid and r0.valid and tools.valid and exec_meta.valid and not missing
    )

    return PromptBOMResolved(
        bom_id=str(src.get("bom_id", bundle.execution.bom_id)),
        system_version_hash=bundle.governance.system_version_hash,
        policy_hash=bundle.governance.policy_hash or bundle.execution.policy_hash,
        agent_spec_id=str(bundle.governance.agent_spec.get("id", "")),
        route_contract_id=bundle.route.route_id,
        plan_id=bundle.plan.plan_id,
        evidence_contract_id=str(bundle.evidence.policy_hash or ""),
        s0=s0,
        d0=d0,
        i0=i0,
        e0=e0,
        c0=c0,
        m0=m0,
        u0=u0,
        y0=y0,
        h0=h0,
        r0=r0,
        tool_binding_manifest=tools,
        execution_metadata=exec_meta,
        slots_requested=requested,
        slots_available=tuple(available),
        slots_missing=missing,
        valid=valid,
        reasons=tuple(reasons),
    )


__all__ = [
    "C0GroundedContextBlock",
    "D0FenceBlock",
    "E0ExemplarBlock",
    "ExecutionMetadataBlock",
    "H0HealingHintBlock",
    "I0InstructionBlock",
    "M0MetaControlBlock",
    "PromptBOMResolved",
    "R0SchemaBinding",
    "S0Block",
    "ToolBindingManifest",
    "U0NeutralizedTaskBlock",
    "Y0LearningPriorBlock",
    "resolve_bom",
]
