"""Fail-closed E1/E2 authority validation for apps_rg governed L2."""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import replace
from typing import Any, Mapping

from apps_rg.runtime.bindings.l2_authority_contracts import (
    AuthorityGateReceipt,
    FrozenExecutionRoom,
    L2AuthorityError,
    SignedAppsRgL2ExecutionPacket,
    _require,
    _string,
    _tuple_strings,
    sha256_hex,
)
from apps_rg.runtime.bindings.u0_binding import (
    APPS_RG_U0_AUTHORITY_CONTRACT_ID,
    AppsRgU0AuthorityReceipt,
    apps_rg_u0_authority_receipt_digest,
)
from apps_rg.runtime.providers.provider_aliases import (
    is_external_apps_rg_provider,
    normalize_apps_rg_provider_alias,
)


def _component_hash(prompt_artifact: Any, *keys: str) -> str:
    values = getattr(prompt_artifact, "component_hash_map", {}) or {}
    if isinstance(values, Mapping):
        for key in keys:
            value = _string(values.get(key))
            if value:
                return value
    return ""


def _identity_values(obj: Any) -> tuple[str, str, str, str, str]:
    return (
        _string(getattr(obj, "request_id", "")),
        _string(getattr(obj, "run_id", "")),
        _string(getattr(obj, "app_id", "")),
        _string(getattr(obj, "trace_id", "") or getattr(obj, "trace_root", "")),
        _string(getattr(obj, "tenant_id", "")),
    )


def _authority_receipt_passed(validated_request: Any) -> bool:
    receipt = getattr(validated_request, "authority_validation_receipt", None)
    if receipt is None:
        return False
    observed = (
        getattr(receipt, "allowed", None),
        getattr(receipt, "passed", None),
        getattr(receipt, "validation_passed", None),
    )
    return any(value is True for value in observed) and not any(
        value is False for value in observed
    )


def _validate_u0_authority_receipt_binding(validated_request: Any) -> None:
    """Require the exact identity- and digest-bound receipt emitted by Apps RG U0."""
    receipt = getattr(validated_request, "authority_validation_receipt", None)
    _require(
        isinstance(receipt, AppsRgU0AuthorityReceipt),
        "V0_U0_AUTHORITY_RECEIPT_MALFORMED",
        "ValidatedRequest must carry the typed Apps RG U0 authority receipt",
        "authority_validation_receipt",
    )
    _require(
        receipt.validation_passed is True,
        "V0_U0_AUTHORITY_RECEIPT_NOT_PASS",
        "Apps RG U0 authority validation must be an explicit PASS",
        "validation_passed",
    )
    _require(
        receipt.authority_contract_id == APPS_RG_U0_AUTHORITY_CONTRACT_ID,
        "V0_U0_AUTHORITY_RECEIPT_CONTRACT_MISMATCH",
        "U0 authority receipt contract identity is invalid",
        "authority_contract_id",
    )
    request_identity = {
        "request_id": _string(getattr(validated_request, "request_id", "")),
        "run_id": _string(getattr(validated_request, "run_id", "")),
        "trace_id": _string(getattr(validated_request, "trace_id", "")),
        "trace_root": _string(
            getattr(validated_request, "trace_root", "")
            or getattr(validated_request, "trace_id", "")
        ),
        "tenant_id": _string(getattr(validated_request, "tenant_id", "")),
        "app_id": _string(getattr(validated_request, "app_id", "")),
    }
    receipt_identity = {
        key: _string(getattr(receipt, key, "")) for key in request_identity
    }
    _require(
        all(request_identity.values())
        and all(receipt_identity.values())
        and receipt_identity == request_identity,
        "V0_U0_AUTHORITY_RECEIPT_IDENTITY_MISMATCH",
        f"U0 authority receipt identity must match ValidatedRequest: {receipt_identity}",
        "authority_validation_receipt",
    )
    request_digest = _string(getattr(validated_request, "payload_digest", ""))
    _require(
        bool(request_digest) and receipt.validated_input_digest == request_digest,
        "V0_U0_AUTHORITY_RECEIPT_INPUT_DIGEST_MISMATCH",
        "U0 authority receipt validated-input digest must match ValidatedRequest",
        "validated_input_digest",
    )
    expected_receipt_digest = apps_rg_u0_authority_receipt_digest(receipt)
    observed_receipt_digest = _string(receipt.authority_receipt_digest)
    _require(
        bool(observed_receipt_digest)
        and hmac.compare_digest(observed_receipt_digest, expected_receipt_digest),
        "V0_U0_AUTHORITY_RECEIPT_DIGEST_MISMATCH",
        "U0 authority receipt digest does not verify",
        "authority_receipt_digest",
    )
    _require(
        bool(_string(receipt.validation_timestamp))
        and bool(_string(receipt.validator_version))
        and bool(receipt.forbidden_fields_checked),
        "V0_U0_AUTHORITY_RECEIPT_MALFORMED",
        "U0 authority receipt validation metadata is incomplete",
        "authority_validation_receipt",
    )


def _snapshot_value(route_contract: Any, prefix: str) -> str:
    needle = f"{prefix}:"
    for ref in _tuple_strings(getattr(route_contract, "snapshot_refs", ())):
        if ref.startswith(needle):
            return ref[len(needle) :]
    return ""


def _verify_route_signature(
    route_contract: Any,
    route_digest: str,
    route_signature: str,
) -> bytes:
    from apps_rg.runtime.bindings.l0_route_evidence import (
        resolve_route_hmac_secret,
        sign_route_digest,
    )

    secret = resolve_route_hmac_secret()
    _require(
        bool(secret),
        "V0_ROUTE_SIGNING_SECRET_UNAVAILABLE",
        "the L0 route signing secret is required to verify RouteContract authority",
        "hmac_sig",
    )
    expected = sign_route_digest(route_digest, secret=secret)
    _require(
        bool(expected) and hmac.compare_digest(expected, route_signature),
        "V0_ROUTE_SIGNATURE_INVALID",
        "RouteContract HMAC does not verify against route_digest",
        "hmac_sig",
    )
    return secret


def _verify_prompt_signature_refs(
    prompt_artifact: Any,
    prompt_hash: str,
    prompt_signature: str,
) -> None:
    refs = _tuple_strings(getattr(prompt_artifact, "gate_verdict_refs", ()))
    manifest_refs = tuple(
        ref.split(":", 1)[1] for ref in refs if ref.startswith("pa_manifest:")
    )
    hmac_refs = tuple(
        ref.split(":", 1)[1] for ref in refs if ref.startswith("pa_hmac:")
    )
    _require(
        bool(prompt_signature),
        "V0_UNSIGNED_PROMPT",
        "CompiledPromptArtifact must carry the PA.7 HMAC signature",
        "signature",
    )
    _require(
        bool(manifest_refs) and prompt_hash in manifest_refs,
        "V0_PROMPT_MANIFEST_REF_MISMATCH",
        "PA manifest gate ref must match CompiledPromptArtifact.compilation_hash",
        "gate_verdict_refs",
    )
    _require(
        bool(hmac_refs) and any(prompt_signature.startswith(ref) for ref in hmac_refs),
        "V0_PROMPT_SIGNATURE_REF_MISMATCH",
        "PA HMAC gate ref must match CompiledPromptArtifact.signature",
        "gate_verdict_refs",
    )


def _validate_identity(
    prompt_artifact: Any,
    route_contract: Any,
    validated_request: Any,
) -> None:
    cpa = _identity_values(prompt_artifact)
    route = _identity_values(route_contract)
    request = _identity_values(validated_request)
    names = ("request_id", "run_id", "app_id", "trace_id", "tenant_id")
    for index, name in enumerate(names):
        values = (cpa[index], route[index], request[index])
        _require(
            all(values) and len(set(values)) == 1,
            "V0_IDENTITY_CHAIN_MISMATCH",
            f"{name} must be non-empty and identical across U0, L0, and PA: {values}",
            name,
        )


def _reject_upstream_unknowns(*objects: Any) -> None:
    refs: list[str] = []
    for obj in objects:
        refs.extend(_tuple_strings(getattr(obj, "gate_verdict_refs", ())))
        refs.extend(_tuple_strings(getattr(obj, "route_gate_refs", ())))
    blocked_tokens = (
        ":UNKNOWN",
        "=UNKNOWN",
        ":FAIL",
        "=FAIL",
        ":DENY",
        "=DENY",
        ":BLOCK",
        "=BLOCK",
    )
    blocked = tuple(
        ref for ref in refs if any(token in ref.upper() for token in blocked_tokens)
    )
    _require(
        not blocked,
        "V0_UPSTREAM_GATE_NOT_PASS",
        f"UNKNOWN or non-pass upstream GateVerdict refs are terminal: {blocked}",
        "gate_verdict_refs",
    )


def build_signed_execution_packet(
    prompt_artifact: Any,
    route_contract: Any,
    validated_request: Any,
    *,
    attempt_number: int = 1,
) -> SignedAppsRgL2ExecutionPacket:
    """Build a packet whose authority is inherited from signed U0/L0/PA contracts."""
    _require(
        prompt_artifact is not None,
        "V0_MISSING_PROMPT",
        "CompiledPromptArtifact is required",
    )
    _require(
        route_contract is not None,
        "V0_MISSING_ROUTE",
        "RouteContract is required",
    )
    _require(
        validated_request is not None,
        "V0_MISSING_REQUEST",
        "ValidatedRequest is required",
    )
    _validate_identity(prompt_artifact, route_contract, validated_request)
    _reject_upstream_unknowns(prompt_artifact, route_contract, validated_request)

    route_id = _string(getattr(route_contract, "route_id", ""))
    route_digest = _string(getattr(route_contract, "route_digest", ""))
    route_signature = _string(
        getattr(route_contract, "hmac_sig", "")
        or getattr(route_contract, "signature", "")
    )
    request_signature = _string(getattr(validated_request, "signature", ""))
    prompt_signature = _string(getattr(prompt_artifact, "signature", ""))
    _require(
        bool(route_id),
        "V0_MISSING_ROUTE_ID",
        "RouteContract.route_id is required",
        "route_id",
    )
    _require(
        bool(route_digest),
        "V0_MISSING_ROUTE_DIGEST",
        "RouteContract.route_digest is required",
        "route_digest",
    )
    _require(
        bool(route_signature),
        "V0_UNSIGNED_ROUTE",
        "RouteContract must carry hmac_sig or signature",
        "hmac_sig",
    )
    packet_signing_secret = _verify_route_signature(
        route_contract,
        route_digest,
        route_signature,
    )
    _validate_u0_authority_receipt_binding(validated_request)
    request_proof = request_signature or _string(
        getattr(validated_request, "payload_digest", "")
    )
    _require(
        bool(request_proof),
        "V0_MISSING_REQUEST_PROOF",
        "ValidatedRequest payload proof is required",
        "payload_digest",
    )

    prompt_replay = _string(getattr(prompt_artifact, "replay_key", ""))
    route_replay = _string(getattr(route_contract, "replay_key", ""))
    request_replay = _string(getattr(validated_request, "replay_key", ""))
    _require(
        bool(prompt_replay) and prompt_replay == route_replay == request_replay,
        "V0_REPLAY_CHAIN_MISMATCH",
        "replay_key must be non-empty and identical across U0, L0, and PA",
        "replay_key",
    )

    l5_refs = (
        _string(getattr(prompt_artifact, "l5_certification_ref", "")),
        _string(getattr(route_contract, "l5_certification_ref", "")),
        _string(getattr(validated_request, "l5_certification_ref", "")),
    )
    _require(
        all(l5_refs) and len(set(l5_refs)) == 1,
        "V0_L5_CHAIN_MISMATCH",
        f"l5_certification_ref must be identical across U0, L0, and PA: {l5_refs}",
        "l5_certification_ref",
    )

    _require(
        bool(getattr(route_contract, "model_generation_required", False)),
        "E3_UNSUPPORTED_EXECUTION_LANE",
        "apps_rg governed L2 currently supports the MODEL lane only",
        "model_generation_required",
    )
    _require(
        not bool(getattr(route_contract, "write_authority_present", False))
        and not bool(getattr(route_contract, "action_required", False)),
        "V0_SIDE_EFFECT_AUTHORITY_REJECTED",
        "apps_rg L2 may not receive write/action authority",
        "write_authority_present",
    )

    canonical_provider = normalize_apps_rg_provider_alias(
        _string(getattr(prompt_artifact, "target_provider", ""))
    )
    _require(
        is_external_apps_rg_provider(canonical_provider),
        "E3_LIVE_REQUIRED_PROVIDER_REJECTED",
        f"product L2 requires an external governed provider; got {canonical_provider!r}",
        "target_provider",
    )

    target_model = _string(getattr(prompt_artifact, "target_model", ""))
    route_models = _tuple_strings(getattr(route_contract, "allowed_models", ()))
    prompt_models = _tuple_strings(getattr(prompt_artifact, "allowed_models", ()))
    provider_requirement_ref = _string(
        getattr(route_contract, "provider_model_requirement_ref", "")
    )
    _require(
        bool(target_model),
        "V1_MISSING_MODEL",
        "target_model is required",
        "target_model",
    )
    _require(
        bool(provider_requirement_ref),
        "V11_MISSING_PROVIDER_MODEL_REQUIREMENT",
        "RouteContract.provider_model_requirement_ref is required for MODEL execution",
        "provider_model_requirement_ref",
    )
    if route_models and prompt_models:
        effective_models = tuple(sorted(set(route_models) & set(prompt_models)))
    elif route_models:
        effective_models = tuple(sorted(set(route_models)))
    elif prompt_models:
        effective_models = tuple(sorted(set(prompt_models)))
    else:
        effective_models = (target_model,)
    _require(
        target_model in effective_models,
        "V1_MODEL_SCOPE_MISMATCH",
        "target_model must match the signed provider/model requirement",
        "allowed_models",
    )

    route_tools = set(_tuple_strings(getattr(route_contract, "allowed_tools", ())))
    prompt_tools = set(_tuple_strings(getattr(prompt_artifact, "allowed_tools", ())))
    _require(
        (not route_tools and not prompt_tools) or prompt_tools.issubset(route_tools),
        "V1_TOOL_SCOPE_MISMATCH",
        "CompiledPromptArtifact.allowed_tools must be a subset of RouteContract.allowed_tools",
        "allowed_tools",
    )

    route_sandbox_required = bool(getattr(route_contract, "sandbox_required", False))
    prompt_sandbox_required = bool(
        getattr(prompt_artifact, "sandbox_required", False)
    )
    route_egress = _string(getattr(route_contract, "egress_policy_ref", ""))
    prompt_egress = _string(getattr(prompt_artifact, "egress_policy_ref", ""))
    route_networks = _tuple_strings(getattr(route_contract, "allowed_networks", ()))
    prompt_networks = _tuple_strings(
        getattr(prompt_artifact, "allowed_networks", ())
    )
    route_roots = _tuple_strings(getattr(route_contract, "allowed_file_roots", ()))
    prompt_roots = _tuple_strings(
        getattr(prompt_artifact, "allowed_file_roots", ())
    )
    sandbox_payload = {
        "sandbox_required": route_sandbox_required or prompt_sandbox_required,
        "egress_policy_ref": route_egress or prompt_egress or provider_requirement_ref,
        "allowed_networks": route_networks or prompt_networks,
        "allowed_file_roots": route_roots or prompt_roots,
        "allowed_tools": tuple(sorted(route_tools or prompt_tools)),
        "allowed_models": effective_models,
        "provider_model_requirement_ref": provider_requirement_ref,
    }
    _require(
        (not route_egress or not prompt_egress or route_egress == prompt_egress)
        and (
            not route_networks
            or not prompt_networks
            or route_networks == prompt_networks
        )
        and (not route_roots or not prompt_roots or route_roots == prompt_roots),
        "V15_SANDBOX_CHAIN_MISMATCH",
        "RouteContract and CompiledPromptArtifact sandbox constraints must not contradict",
        "sandbox_envelope",
    )

    prompt_hash = _string(getattr(prompt_artifact, "compilation_hash", ""))
    _require(
        bool(prompt_hash),
        "V3_MISSING_COMPILATION_HASH",
        "prompt hash is required",
        "compilation_hash",
    )
    _verify_prompt_signature_refs(prompt_artifact, prompt_hash, prompt_signature)
    evidence_ref = _string(getattr(prompt_artifact, "evidence_digest", ""))
    _require(
        bool(evidence_ref),
        "V13_MISSING_EVIDENCE_REF",
        "FinalEvidenceContract digest is required",
        "evidence_digest",
    )

    max_tokens = int(getattr(prompt_artifact, "max_tokens", 0) or 0)
    _require(
        0 < max_tokens <= 131_072,
        "V20_INVALID_TOKEN_BUDGET",
        "max_tokens must be within the governed ceiling",
        "max_tokens",
    )
    budget = {
        "max_tokens": max_tokens,
        "timeout_ms": max_tokens * 15,
        "retry_ceiling": 3,
        "repair_ceiling": 3,
        "max_output_bytes": max_tokens * 8,
        "circuit_breaker_open": False,
    }

    component_values = tuple(
        sorted(
            _string(value)
            for value in (
                getattr(prompt_artifact, "component_hash_map", {}) or {}
            ).values()
            if _string(value)
        )
    )
    registry_refs = tuple(
        value
        for value in (
            _string(getattr(route_contract, "workflow_registry_ref", "")),
            _string(
                getattr(route_contract, "registry_resolution_receipt_ref", "")
            ),
            provider_requirement_ref,
            *_tuple_strings(getattr(route_contract, "snapshot_refs", ())),
        )
        if value
    )
    registry_digest_set = tuple(sorted(set(component_values + registry_refs)))
    _require(
        bool(registry_digest_set),
        "V11_MISSING_REGISTRY_DIGEST",
        "registry digest set is required",
        "registry_digest_set",
    )

    capability_payload = {
        "route_digest": route_digest,
        "provider_model_requirement_ref": provider_requirement_ref,
        "allowed_tools": tuple(sorted(route_tools)),
        "allowed_models": effective_models,
        "allowed_networks": sandbox_payload["allowed_networks"],
        "allowed_file_roots": sandbox_payload["allowed_file_roots"],
        "side_effect_class": "READ",
    }
    capability_scope_digest = sha256_hex(capability_payload)
    sandbox_envelope_digest = sha256_hex(sandbox_payload)
    policy_hash = (
        _snapshot_value(route_contract, "policy_hash")
        or _component_hash(prompt_artifact, "policy", "policy_hash")
        or _string(getattr(route_contract, "route_policy_ref", ""))
        or l5_refs[0]
    )
    blueprint_hash = (
        _snapshot_value(route_contract, "blueprint_hash")
        or _component_hash(
            prompt_artifact,
            "blueprint",
            "agent_spec",
            "agent_spec_hash",
        )
        or prompt_hash
    )
    signature_chain = (
        f"u0:{request_proof}",
        f"l0:{route_signature}",
        f"pa:{prompt_signature}",
    )
    signature_chain_digest = sha256_hex(signature_chain)
    attempt = int(attempt_number)
    _require(
        attempt > 0,
        "V19_INVALID_ATTEMPT_NUMBER",
        "attempt_number must be positive",
        "attempt_number",
    )
    attempt_seed = hashlib.sha256(
        "|".join((prompt_replay, prompt_hash, route_id, str(attempt))).encode(
            "utf-8"
        )
    ).hexdigest()
    request_id, run_id, app_id, trace_id, tenant_id = _identity_values(
        prompt_artifact
    )

    packet = SignedAppsRgL2ExecutionPacket(
        schema_version="apps_rg.l2_execution_packet.v2",
        request_id=request_id,
        run_id=run_id,
        app_id=app_id,
        trace_id=trace_id,
        tenant_id=tenant_id,
        route_id=route_id,
        workflow_id=_string(getattr(route_contract, "workflow_ref", "")),
        node_id=_string(getattr(route_contract, "node_id", "")),
        step_id=_string(getattr(route_contract, "step_id", "")),
        execution_lane="MODEL",
        capability_scope_digest=capability_scope_digest,
        sandbox_envelope_digest=sandbox_envelope_digest,
        sandbox_required=bool(sandbox_payload["sandbox_required"]),
        egress_policy_ref=str(sandbox_payload["egress_policy_ref"]),
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        prompt_hash=prompt_hash,
        replay_key=prompt_replay,
        attempt_number=attempt,
        attempt_seed=attempt_seed,
        snapshot_manifest=_string(
            getattr(prompt_artifact, "replay_manifest_ref", "")
        ),
        idempotency_key=f"{request_id}:{run_id}:{route_id}",
        registry_digest_set=registry_digest_set,
        compiled_prompt_artifact_ref=prompt_hash,
        final_evidence_contract_ref=evidence_ref,
        canonical_provider=canonical_provider,
        target_model=target_model,
        allowed_tools=tuple(sorted(prompt_tools)),
        allowed_models=effective_models,
        allowed_networks=sandbox_payload["allowed_networks"],
        allowed_file_roots=sandbox_payload["allowed_file_roots"],
        side_effect_class="READ",
        budget=budget,
        signature_chain=signature_chain,
        signature_chain_digest=signature_chain_digest,
    )
    packet_digest = sha256_hex(packet.unsigned_payload())
    packet_signature = hmac.new(
        packet_signing_secret,
        packet_digest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return replace(
        packet,
        packet_digest=packet_digest,
        packet_signature=packet_signature,
    )


def validate_execution_packet(
    packet: SignedAppsRgL2ExecutionPacket,
    prompt_artifact: Any,
    route_contract: Any,
    validated_request: Any,
) -> tuple[AuthorityGateReceipt, ...]:
    """Validate the immutable packet and return explicit PASS-only runtime gates."""
    _require(
        packet.packet_digest == sha256_hex(packet.unsigned_payload()),
        "V12_PACKET_DIGEST_MISMATCH",
        "execution packet digest does not match its canonical payload",
        "packet_digest",
    )
    route_signature = _string(
        getattr(route_contract, "hmac_sig", "")
        or getattr(route_contract, "signature", "")
    )
    packet_signing_secret = _verify_route_signature(
        route_contract,
        _string(getattr(route_contract, "route_digest", "")),
        route_signature,
    )
    expected_packet_signature = hmac.new(
        packet_signing_secret,
        packet.packet_digest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    _require(
        bool(packet.packet_signature)
        and hmac.compare_digest(expected_packet_signature, packet.packet_signature),
        "V12_PACKET_SIGNATURE_INVALID",
        "execution packet HMAC does not verify",
        "packet_signature",
    )
    _validate_identity(prompt_artifact, route_contract, validated_request)
    _reject_upstream_unknowns(prompt_artifact, route_contract, validated_request)
    _require(
        packet.execution_lane == "MODEL",
        "E3_UNSUPPORTED_EXECUTION_LANE",
        "only MODEL is wired",
    )
    _require(
        packet.side_effect_class == "READ",
        "V15_SIDE_EFFECT_CLASS_REJECTED",
        "L2 side effects must remain READ",
    )
    _require(
        packet.prompt_hash
        == _string(getattr(prompt_artifact, "compilation_hash", "")),
        "V12_PROMPT_HASH_MISMATCH",
        "packet prompt hash mismatch",
    )
    _require(
        packet.replay_key == _string(getattr(prompt_artifact, "replay_key", "")),
        "V24_REPLAY_KEY_MISMATCH",
        "packet replay key mismatch",
    )
    _require(
        packet.target_model in packet.allowed_models,
        "V11_MODEL_NOT_ALLOWED",
        "packet target model is not allowed",
    )
    _require(
        is_external_apps_rg_provider(packet.canonical_provider),
        "E3_LIVE_REQUIRED_PROVIDER_REJECTED",
        "packet provider must be external",
    )
    _require(
        not bool(packet.budget.get("circuit_breaker_open")),
        "V20_CIRCUIT_BREAKER_OPEN",
        "budget circuit breaker is open",
    )
    _require(
        int(packet.budget.get("retry_ceiling", -1)) in range(0, 4),
        "V19_RETRY_BUDGET_INVALID",
        "retry ceiling must be between zero and three",
    )
    _require(
        int(packet.budget.get("max_tokens", 0)) > 0,
        "V20_INVALID_TOKEN_BUDGET",
        "token budget must be positive",
    )

    refs = (f"l2_packet:{packet.packet_digest}",)
    return (
        AuthorityGateReceipt(
            "G11",
            "PASS",
            "MODEL_REGISTRY_BOUND",
            ("canonical_provider", "target_model", "registry_digest_set"),
            refs,
        ),
        AuthorityGateReceipt(
            "G12",
            "PASS",
            "SIGNED_ARGS_AND_IDENTITY_BOUND",
            ("signature_chain", "request_id", "run_id", "route_id"),
            refs,
        ),
        AuthorityGateReceipt(
            "G13",
            "PASS",
            "EVIDENCE_AND_SCHEMA_BOUND",
            ("final_evidence_contract_ref", "prompt_hash"),
            refs,
        ),
        AuthorityGateReceipt(
            "G15",
            "PASS",
            "SANDBOX_ENVELOPE_BOUND",
            ("sandbox_envelope_digest", "allowed_networks", "allowed_file_roots"),
            refs,
        ),
        AuthorityGateReceipt(
            "G19",
            "PASS",
            "RETRY_BUDGET_BOUND",
            ("attempt_number", "retry_ceiling", "repair_ceiling"),
            refs,
        ),
        AuthorityGateReceipt(
            "G20",
            "PASS",
            "EXECUTION_BUDGET_BOUND",
            ("max_tokens", "timeout_ms", "max_output_bytes"),
            refs,
        ),
    )


def freeze_execution_room(
    packet: SignedAppsRgL2ExecutionPacket,
) -> FrozenExecutionRoom:
    room = FrozenExecutionRoom(
        schema_version="apps_rg.frozen_execution_room.v2",
        packet_digest=packet.packet_digest,
        route_id=packet.route_id,
        workflow_id=packet.workflow_id,
        node_id=packet.node_id,
        step_id=packet.step_id,
        execution_lane=packet.execution_lane,
        capability_scope_digest=packet.capability_scope_digest,
        sandbox_envelope_digest=packet.sandbox_envelope_digest,
        sandbox_required=packet.sandbox_required,
        egress_policy_ref=packet.egress_policy_ref,
        policy_hash=packet.policy_hash,
        blueprint_hash=packet.blueprint_hash,
        prompt_hash=packet.prompt_hash,
        replay_key=packet.replay_key,
        attempt_seed=packet.attempt_seed,
        snapshot_manifest=packet.snapshot_manifest,
        idempotency_key=packet.idempotency_key,
        registry_digest_set=packet.registry_digest_set,
        provider_lane=packet.canonical_provider,
        model_id=packet.target_model,
        filesystem_view=packet.allowed_file_roots,
        network_rules=packet.allowed_networks,
        secrets_scope=packet.egress_policy_ref,
        locale="en-US",
        budget=dict(packet.budget),
    )
    return replace(room, room_digest=sha256_hex(room.unsigned_payload()))


__all__ = [
    "AuthorityGateReceipt",
    "FrozenExecutionRoom",
    "L2AuthorityError",
    "SignedAppsRgL2ExecutionPacket",
    "build_signed_execution_packet",
    "freeze_execution_room",
    "sha256_hex",
    "validate_execution_packet",
]
