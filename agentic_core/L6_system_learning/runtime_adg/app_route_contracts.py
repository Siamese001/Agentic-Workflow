"""Tier 2 per-app-route contract schema for runtime certification (Phase B.2).

Design references
-----------------
- ``docs/reference/runtime_certification/contract_span_binding_matrix.md`` v2
- ``docs/reports/runtime_certification/phase_a_trace_inventory.md``
- Sibling Tier 1: ``system_learning/runtime_adg/span_contracts.py``

What this module does
---------------------
Defines the typed schema that future certification-harness code will use
to represent **per-app-route** contract bindings (one schema object per
apps_* app, per declared route shape). This module is **schema only** -
no trace collection, no certification evaluation, no runtime emitter
change. No app becomes runtime-certified by importing this module.

Style
-----
Matches the existing repo convention: frozen dataclasses with slots, no
pydantic. Mirrors the ``_CategoryContract`` shape at
``system_learning/runtime_adg/span_contracts.py:44-58``.

Invariants enforced at construction
-----------------------------------
- R3_grounded_read contracts MUST include the 8 canonical R3 contracts.
- build_time_compiler contracts MUST NOT require the full R3 chain.
- evaluator_only / core_adjacent_utility contracts MUST have
  ``compensating_controls`` when ``certification_level`` is
  ``FORMAL_EXCEPTION_VERIFIED``, or when the route shape is a formal
  exception class.
- R3 apps MUST forbid ``CommitRequest`` unless the route shape is a
  future ``R3R4_managed_workflow`` (not yet defined).
- ``manifest_hash`` MUST be non-empty if ``certification_level`` is
  ``TRACE_OBSERVED`` or higher.
- ``normalized_cert_alias`` MUST be non-empty on every binding.
- Ambiguous Phase A statuses (``UNKNOWN_NEEDS_RUNTIME_RUN``,
  ``NOT_FOUND``) force ``live_trace_required=True`` on the binding.

What this module is NOT
-----------------------
- Not a trace collector (Phase C).
- Not a certification evaluator (Phase D).
- Not a CI gate (Phase E).
- Not a promotion workflow (Phase F).
- Not an emitter.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enums (not StrEnum — 3.10 compatibility across the repo)
# ---------------------------------------------------------------------------


class CertificationLevel(str, Enum):
    """Four-level certification ladder.

    See contract_span_binding_matrix.md §3. Promotion is monotonic;
    demotion requires loss of evidence.
    """

    STATIC_EVIDENCE = "STATIC_EVIDENCE"
    TRACE_OBSERVED = "TRACE_OBSERVED"
    RUNTIME_CERTIFIED = "RUNTIME_CERTIFIED"
    FORMAL_EXCEPTION_VERIFIED = "FORMAL_EXCEPTION_VERIFIED"


class PhaseAStatus(str, Enum):
    """Per-contract Phase A findings.

    See contract_span_binding_matrix.md §4.1 legend.
    """

    EXISTS_MATCHES_MATRIX = "EXISTS_MATCHES_MATRIX"
    EXISTS_NEEDS_ATTRIBUTE_HARDENING = "EXISTS_NEEDS_ATTRIBUTE_HARDENING"
    EXISTS_NAME_MISMATCH = "EXISTS_NAME_MISMATCH"
    TELEMETRY_MARKER_ONLY = "TELEMETRY_MARKER_ONLY"
    LEDGER_EVENT_ONLY = "LEDGER_EVENT_ONLY"
    STUB_ONLY = "STUB_ONLY"
    NOT_FOUND = "NOT_FOUND"
    UNKNOWN_NEEDS_RUNTIME_RUN = "UNKNOWN_NEEDS_RUNTIME_RUN"


class RouteShape(str, Enum):
    """Four route shapes in scope for runtime certification.

    See contract_span_binding_matrix.md §2. R3R4_managed_workflow is
    reserved for future durable-write apps and is NOT yet defined as
    an enum member here — adding it requires an Author-Gate decision.
    """

    build_time_compiler = "build_time_compiler"
    R3_grounded_read = "R3_grounded_read"
    evaluator_only = "evaluator_only"
    core_adjacent_utility = "core_adjacent_utility"


_FORMAL_EXCEPTION_ROUTES: frozenset[RouteShape] = frozenset(
    {RouteShape.evaluator_only, RouteShape.core_adjacent_utility}
)

_AMBIGUOUS_PHASE_A: frozenset[PhaseAStatus] = frozenset(
    {PhaseAStatus.UNKNOWN_NEEDS_RUNTIME_RUN, PhaseAStatus.NOT_FOUND}
)

# Canonical 8 R3 contracts (post-W14). Order matters for parent-chain
# semantics in §4.1 of the design matrix.
R3_GROUNDED_READ_CONTRACTS: tuple[str, ...] = (
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
    "RetrievalPlan",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",  # equivalence group — PromptEnvelope accepted
    "SealedArtifact",
    "ExitReviewPacket",
)

# Set of contract names forbidden on R3 apps (R3R4 discriminator, §9.3).
R3_FORBIDDEN_CONTRACTS: frozenset[str] = frozenset({"CommitRequest"})

# apps_qna minimal span set for build_time_compiler route (§5.1).
BUILD_TIME_COMPILER_CONTRACTS: tuple[str, ...] = (
    "ValidatedRequest",
    "build.pack_artifact",
    "ledger.emit",
)

# Contract names that MUST NOT appear in a build_time_compiler required
# set — these are R3-chain contracts. See §5.2.
BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS: frozenset[str] = frozenset(
    {
        "L1PlanContract",
        "RouteContract",
        "RetrievalPlan",
        "FinalEvidenceContract",
        "CompiledPromptArtifact",
        "PromptEnvelope",
        "SealedArtifact",
        "ExitReviewPacket",
        "CommitRequest",
    }
)


# ---------------------------------------------------------------------------
# Attribute + binding shapes
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RequiredAttribute:
    """One required attribute on a certifying span.

    See contract_span_binding_matrix.md §8 for the global required-10
    list, and §4.1 for per-contract attribute additions.
    """

    name: str
    required: bool
    description: str
    failure_if_missing: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("RequiredAttribute.name must be non-empty")
        if not self.description:
            raise ValueError("RequiredAttribute.description must be non-empty")
        if not self.failure_if_missing:
            raise ValueError(
                "RequiredAttribute.failure_if_missing must be non-empty"
            )


@dataclass(frozen=True, slots=True)
class ContractSpanBinding:
    """One binding between a canonical contract name and existing emitters.

    This is the Tier-2 analogue of the Tier-1 ``_CategoryContract`` in
    ``span_contracts.py``. The binding is harness-internal — it does NOT
    require the emitter to emit ``normalized_cert_alias`` as a span name.
    """

    contract_name: str
    normalized_cert_alias: str
    accepted_emitter_categories: tuple[str, ...]
    accepted_span_name_patterns: tuple[str, ...]
    accepted_emitter_files: tuple[str, ...]
    phase_a_status: PhaseAStatus
    required_attributes: tuple[RequiredAttribute, ...]
    live_trace_required: bool
    failure_conditions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.contract_name:
            raise ValueError("ContractSpanBinding.contract_name must be non-empty")
        if not self.normalized_cert_alias:
            raise ValueError(
                "ContractSpanBinding.normalized_cert_alias must be non-empty "
                f"(contract_name={self.contract_name!r})"
            )
        # Ambiguous Phase A status forces live_trace_required=True per the
        # design matrix v2 §4.1 "Live trace required?" column.
        if (
            self.phase_a_status in _AMBIGUOUS_PHASE_A
            and not self.live_trace_required
        ):
            raise ValueError(
                f"ContractSpanBinding({self.contract_name!r}): "
                f"phase_a_status={self.phase_a_status.value} is ambiguous; "
                "live_trace_required MUST be True"
            )
        if not self.failure_conditions:
            raise ValueError(
                f"ContractSpanBinding({self.contract_name!r}): "
                "failure_conditions must be non-empty"
            )


# ---------------------------------------------------------------------------
# Top-level per-app-route contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AppRouteContract:
    """One apps_* app's runtime-certification contract for one route shape.

    Exactly one ``AppRouteContract`` per (app_name, route_shape) pair.
    An app with multiple ``claimed_routes`` in its spine_manifest would
    produce multiple ``AppRouteContract`` objects.

    See contract_span_binding_matrix.md §§2-7 for the conceptual model.
    """

    app_name: str
    route_shape: RouteShape
    static_runtime_mode: str  # APP_OVERLAY_STATIC_EVIDENCE | FORMAL_EXCEPTION_STATIC_EVIDENCE
    manifest_path: str
    manifest_hash: str
    certification_level: CertificationLevel
    required_contracts: tuple[str, ...]
    bindings: tuple[ContractSpanBinding, ...]
    forbidden_contracts: frozenset[str] = field(default_factory=frozenset)
    formal_exception_reason_code: str = ""
    compensating_controls: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.app_name or not self.app_name.startswith("apps_"):
            raise ValueError(
                f"AppRouteContract.app_name must be an apps_* directory name; "
                f"got {self.app_name!r}"
            )
        if not self.manifest_path:
            raise ValueError("AppRouteContract.manifest_path must be non-empty")

        # manifest_hash required from TRACE_OBSERVED upward.
        if (
            self.certification_level
            in (
                CertificationLevel.TRACE_OBSERVED,
                CertificationLevel.RUNTIME_CERTIFIED,
                CertificationLevel.FORMAL_EXCEPTION_VERIFIED,
            )
            and not self.manifest_hash
        ):
            raise ValueError(
                f"AppRouteContract({self.app_name!r}): manifest_hash must be "
                f"non-empty when certification_level={self.certification_level.value}"
            )

        # R3: must include the 8 canonical contracts, must forbid CommitRequest.
        if self.route_shape == RouteShape.R3_grounded_read:
            missing = [
                c
                for c in R3_GROUNDED_READ_CONTRACTS
                if c not in self.required_contracts
                # Honor the CompiledPromptArtifact <-> PromptEnvelope
                # equivalence group: either name satisfies the contract.
                and not (
                    c == "CompiledPromptArtifact"
                    and "PromptEnvelope" in self.required_contracts
                )
            ]
            if missing:
                raise ValueError(
                    f"AppRouteContract({self.app_name!r}, R3_grounded_read): "
                    f"required_contracts missing canonical R3 entries: {missing}"
                )
            if "CommitRequest" not in self.forbidden_contracts:
                raise ValueError(
                    f"AppRouteContract({self.app_name!r}, R3_grounded_read): "
                    "CommitRequest MUST be in forbidden_contracts (R3-vs-R3R4 "
                    "discriminator, design matrix §9.3)"
                )

        # build_time_compiler: must NOT require the R3 chain.
        if self.route_shape == RouteShape.build_time_compiler:
            overlap = BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS.intersection(
                self.required_contracts
            )
            if overlap:
                raise ValueError(
                    f"AppRouteContract({self.app_name!r}, build_time_compiler): "
                    f"required_contracts must NOT include R3-chain entries: "
                    f"{sorted(overlap)} (design matrix §5.2 forbidden claims)"
                )

        # Formal exceptions: must carry compensating_controls.
        is_formal_exception_route = self.route_shape in _FORMAL_EXCEPTION_ROUTES
        is_formal_exception_level = (
            self.certification_level == CertificationLevel.FORMAL_EXCEPTION_VERIFIED
        )
        if is_formal_exception_route or is_formal_exception_level:
            if not self.compensating_controls:
                raise ValueError(
                    f"AppRouteContract({self.app_name!r}): route_shape="
                    f"{self.route_shape.value}, certification_level="
                    f"{self.certification_level.value} requires non-empty "
                    "compensating_controls"
                )

        # Every binding must have a non-empty normalized_cert_alias. The
        # ContractSpanBinding __post_init__ enforces this; we re-check at
        # the contract level so the error surfaces with app context.
        for b in self.bindings:
            if not b.normalized_cert_alias:
                raise ValueError(
                    f"AppRouteContract({self.app_name!r}): binding for "
                    f"{b.contract_name!r} has empty normalized_cert_alias"
                )

    # -- Serialization round-trip ------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Lossless serialization to a plain dict (JSON-safe)."""
        d = asdict(self)
        # Convert enums and frozenset to JSON-safe primitives.
        d["route_shape"] = self.route_shape.value
        d["certification_level"] = self.certification_level.value
        d["forbidden_contracts"] = sorted(self.forbidden_contracts)
        for b in d["bindings"]:
            b["phase_a_status"] = (
                b["phase_a_status"].value
                if isinstance(b["phase_a_status"], PhaseAStatus)
                else b["phase_a_status"]
            )
        return d

    def to_json(self) -> str:
        """JSON serialization for cert-report archival."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppRouteContract:
        """Round-trip loader for archived cert contracts."""
        bindings = tuple(
            ContractSpanBinding(
                contract_name=b["contract_name"],
                normalized_cert_alias=b["normalized_cert_alias"],
                accepted_emitter_categories=tuple(b["accepted_emitter_categories"]),
                accepted_span_name_patterns=tuple(b["accepted_span_name_patterns"]),
                accepted_emitter_files=tuple(b["accepted_emitter_files"]),
                phase_a_status=PhaseAStatus(b["phase_a_status"]),
                required_attributes=tuple(
                    RequiredAttribute(**ra) for ra in b["required_attributes"]
                ),
                live_trace_required=bool(b["live_trace_required"]),
                failure_conditions=tuple(b["failure_conditions"]),
            )
            for b in data["bindings"]
        )
        return cls(
            app_name=data["app_name"],
            route_shape=RouteShape(data["route_shape"]),
            static_runtime_mode=data["static_runtime_mode"],
            manifest_path=data["manifest_path"],
            manifest_hash=data["manifest_hash"],
            certification_level=CertificationLevel(data["certification_level"]),
            required_contracts=tuple(data["required_contracts"]),
            bindings=bindings,
            forbidden_contracts=frozenset(data.get("forbidden_contracts", ())),
            formal_exception_reason_code=data.get("formal_exception_reason_code", ""),
            compensating_controls=tuple(data.get("compensating_controls", ())),
            notes=data.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# Default binding catalogs (harness-internal; source: binding matrix v2 §4.1)
# ---------------------------------------------------------------------------


def _std_required_attrs() -> tuple[RequiredAttribute, ...]:
    """The standard cert-harness attribute set applied to every binding.

    See contract_span_binding_matrix.md §8 for the canonical list.
    """
    return (
        RequiredAttribute(
            name="app_name",
            required=True,
            description="apps_* directory name of the emitting app",
            failure_if_missing="attribute_missing:app_name",
        ),
        RequiredAttribute(
            name="route_shape",
            required=True,
            description="Route shape from the app's spine_manifest.yaml claimed_routes",
            failure_if_missing="attribute_missing:route_shape",
        ),
        RequiredAttribute(
            name="run_id",
            required=True,
            description="Request correlation id",
            failure_if_missing="attribute_missing:run_id",
        ),
        RequiredAttribute(
            name="contract_name",
            required=True,
            description="Canonical contract name for cert-harness binding",
            failure_if_missing="attribute_missing:contract_name",
        ),
        RequiredAttribute(
            name="contract_id",
            required=True,
            description="Per-contract unique id",
            failure_if_missing="attribute_missing:contract_id",
        ),
        RequiredAttribute(
            name="manifest_hash",
            required=True,
            description="SHA-256 of the app's spine_manifest.yaml at run time",
            failure_if_missing="attribute_missing:manifest_hash",
        ),
    )


def _r3_bindings() -> tuple[ContractSpanBinding, ...]:
    """Default R3 bindings per design matrix v2 §4.1 / §7.2."""
    std = _std_required_attrs()
    return (
        ContractSpanBinding(
            contract_name="ValidatedRequest",
            normalized_cert_alias="app.<app_name>.intake.validated_request",
            accepted_emitter_categories=("L5.ingress.telemetry",),
            accepted_span_name_patterns=("ingress.*", "intake.*", "*.stamp_trace"),
            accepted_emitter_files=(
                "agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py",
            ),
            phase_a_status=PhaseAStatus.EXISTS_NAME_MISMATCH,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=(
                "span missing from matching category",
                "contract_name mismatched",
                "contract_id empty",
            ),
        ),
        ContractSpanBinding(
            contract_name="L1PlanContract",
            normalized_cert_alias="app.<app_name>.l1.plan_contract",
            accepted_emitter_categories=("L1.planning", "L1.c0_context"),
            accepted_span_name_patterns=("l1.plan.*", "planning.*", "c0_context.*"),
            accepted_emitter_files=(
                "agentic_core/L1_cognition/planning/otel.py",
                "agentic_core/L1_cognition/c0_context/observability.py",
            ),
            phase_a_status=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=(
                "span missing",
                "parent_contract_id does not match request_id",
            ),
        ),
        ContractSpanBinding(
            contract_name="RouteContract",
            normalized_cert_alias="app.<app_name>.l0.route_contract",
            accepted_emitter_categories=("L0.route.select",),
            accepted_span_name_patterns=(
                "heal_router.v1.route",
                "router.*",
                "route.select",
                "l0.route",
                "route.contract",
                "*.v1.route",
            ),
            accepted_emitter_files=(
                "agentic_core/L6_observability/heal_router_otel.py",
                "system_learning/runtime_adg/span_contracts.py",
            ),
            phase_a_status=PhaseAStatus.EXISTS_MATCHES_MATRIX,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=(
                "span missing",
                "route_target not in manifest claimed routing targets",
            ),
        ),
        ContractSpanBinding(
            contract_name="RetrievalPlan",
            normalized_cert_alias="app.<app_name>.c0.retrieval_plan",
            accepted_emitter_categories=("C0.retrieval",),
            accepted_span_name_patterns=("c0.retrieval.*", "c0_3.*", "retrieval.plan"),
            accepted_emitter_files=(
                "agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/otel.py",
            ),
            phase_a_status=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=("span missing", "k <= 0"),
        ),
        ContractSpanBinding(
            contract_name="FinalEvidenceContract",
            normalized_cert_alias="app.<app_name>.c0.final_evidence_contract",
            accepted_emitter_categories=("C0.final_evidence",),
            accepted_span_name_patterns=(),  # unresolved, populated in Phase C
            accepted_emitter_files=(),
            phase_a_status=PhaseAStatus.UNKNOWN_NEEDS_RUNTIME_RUN,
            required_attributes=std,
            live_trace_required=True,  # forced by ambiguous Phase A status
            failure_conditions=("span missing", "evidence_hash empty"),
        ),
        ContractSpanBinding(
            contract_name="CompiledPromptArtifact",
            normalized_cert_alias="app.<app_name>.pa.compiled_prompt_artifact",
            accepted_emitter_categories=(
                "L2.model.invoke",
                "L2.canonical_registry",
                "GenAI.semconv",
            ),
            accepted_span_name_patterns=(
                "invoke_agent *",
                "prompt.compile.*",
                "l2.prompt.*",
            ),
            accepted_emitter_files=(
                "agentic_core/L2_execution/observability/l2_otel_emitter.py",
                "agentic_core/L6_observability/semconv/gen_ai.py",
            ),
            phase_a_status=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=(
                "span missing",
                "contract_name not in equivalence group {CompiledPromptArtifact, PromptEnvelope}",
            ),
        ),
        ContractSpanBinding(
            contract_name="SealedArtifact",
            normalized_cert_alias="app.<app_name>.l2.sealed_artifact",
            accepted_emitter_categories=("L2.step.seal",),
            accepted_span_name_patterns=(
                "l2.step.seal",
                "step.seal",
                "execution.seal",
                "*.seal",
            ),
            accepted_emitter_files=(
                "agentic_core/L2_execution/observability/l2_otel_emitter.py",
                "agentic_core/L2_execution/observability/l2_resolution_spans.py",
            ),
            phase_a_status=PhaseAStatus.EXISTS_MATCHES_MATRIX,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=(
                "span missing",
                "artifact_hash empty",
                "grounded=False with gate_disposition=allow",
            ),
        ),
        ContractSpanBinding(
            contract_name="ExitReviewPacket",
            normalized_cert_alias="app.<app_name>.exit.review_packet",
            accepted_emitter_categories=("Exit.disposition", "Exit.eval_v6"),
            accepted_span_name_patterns=("exit.*", "exit_eval.*", "disposition.*"),
            accepted_emitter_files=(
                "agentic_core/L3_orchestration/exit_eval/otel_sdk_sink.py",
                "agentic_core/L3_orchestration/exit_eval/v6/otel.py",
                "agentic_core/L3_orchestration/exit_eval/v6/return_payload.py",
            ),
            phase_a_status=PhaseAStatus.EXISTS_MATCHES_MATRIX,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=("span missing", "emitted without SealedArtifact"),
        ),
    )


def _build_time_compiler_bindings() -> tuple[ContractSpanBinding, ...]:
    """apps_qna minimal 3-span surface per design matrix v2 §5.1."""
    std = _std_required_attrs()
    return (
        ContractSpanBinding(
            contract_name="ValidatedRequest",
            normalized_cert_alias="app.apps_qna.intake.validated_request",
            accepted_emitter_categories=("L5.ingress.telemetry",),
            accepted_span_name_patterns=("ingress.*", "intake.*", "*.stamp_trace"),
            accepted_emitter_files=(
                "agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py",
            ),
            phase_a_status=PhaseAStatus.EXISTS_NAME_MISMATCH,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=("span missing", "contract_id empty"),
        ),
        ContractSpanBinding(
            contract_name="build.pack_artifact",
            normalized_cert_alias="app.apps_qna.build.pack_artifact",
            accepted_emitter_categories=(),  # TBD in Phase B apps_qna walk
            accepted_span_name_patterns=(),
            accepted_emitter_files=(),
            phase_a_status=PhaseAStatus.UNKNOWN_NEEDS_RUNTIME_RUN,
            required_attributes=std,
            live_trace_required=True,  # forced by ambiguous status
            failure_conditions=(
                "span missing",
                "output_pack_hash not 64-char hex sha256",
            ),
        ),
        ContractSpanBinding(
            contract_name="ledger.emit",
            normalized_cert_alias="app.apps_qna.ledger.emit",
            accepted_emitter_categories=("apps_qna.ledger",),
            accepted_span_name_patterns=("ledger.emit", "apps_qna.ledger.*"),
            accepted_emitter_files=(),  # Phase B.2 does not pin emitter file yet
            phase_a_status=PhaseAStatus.TELEMETRY_MARKER_ONLY,
            required_attributes=std,
            live_trace_required=False,
            failure_conditions=(
                "span missing",
                "terminal-event enum value unrecognized",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Factory helpers (schema-only — no runtime evaluation)
# ---------------------------------------------------------------------------


def build_r3_grounded_read_contract(
    app_name: str,
    manifest_path: str,
    manifest_hash: str,
    static_runtime_mode: str = "APP_OVERLAY_STATIC_EVIDENCE",
) -> AppRouteContract:
    """Build an R3_grounded_read contract for an apps_* app.

    Returns a schema object only. Does NOT read runtime traces.
    Does NOT certify anything. Does NOT change app behavior.
    """
    return AppRouteContract(
        app_name=app_name,
        route_shape=RouteShape.R3_grounded_read,
        static_runtime_mode=static_runtime_mode,
        manifest_path=manifest_path,
        manifest_hash=manifest_hash,
        certification_level=CertificationLevel.STATIC_EVIDENCE,
        required_contracts=R3_GROUNDED_READ_CONTRACTS,
        bindings=_r3_bindings(),
        forbidden_contracts=frozenset(R3_FORBIDDEN_CONTRACTS),
        notes=(
            "R3_grounded_read contract derived from binding matrix v2 §4.1. "
            "CommitRequest is forbidden (R3-vs-R3R4 discriminator §9.3)."
        ),
    )


def build_build_time_compiler_contract(
    app_name: str,
    manifest_path: str,
    manifest_hash: str,
    static_runtime_mode: str = "APP_OVERLAY_STATIC_EVIDENCE",
) -> AppRouteContract:
    """Build a build_time_compiler contract (currently apps_qna only).

    Returns a schema object only. Does NOT read runtime traces.
    Does NOT certify anything. Does NOT change app behavior.
    """
    return AppRouteContract(
        app_name=app_name,
        route_shape=RouteShape.build_time_compiler,
        static_runtime_mode=static_runtime_mode,
        manifest_path=manifest_path,
        manifest_hash=manifest_hash,
        certification_level=CertificationLevel.STATIC_EVIDENCE,
        required_contracts=BUILD_TIME_COMPILER_CONTRACTS,
        bindings=_build_time_compiler_bindings(),
        forbidden_contracts=BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS,
        notes=(
            "build_time_compiler contract per design matrix v2 §5. Does NOT "
            "assert R3-chain spans; the full L1->L0->C0->PA->L2->Exit chain "
            "is explicitly forbidden for this route shape."
        ),
    )


def build_formal_exception_contract(
    app_name: str,
    route_shape: RouteShape,
    manifest_path: str,
    manifest_hash: str,
    reason_code: str,
    compensating_controls: tuple[str, ...],
    static_runtime_mode: str = "FORMAL_EXCEPTION_STATIC_EVIDENCE",
) -> AppRouteContract:
    """Build a formal-exception contract (evaluator_only / core_adjacent_utility).

    Returns a schema object only. Does NOT read runtime traces.
    Does NOT certify anything. Does NOT change app behavior.
    """
    if route_shape not in _FORMAL_EXCEPTION_ROUTES:
        raise ValueError(
            f"build_formal_exception_contract: route_shape must be one of "
            f"{{evaluator_only, core_adjacent_utility}}; got {route_shape.value}"
        )
    if not reason_code:
        raise ValueError(
            "build_formal_exception_contract: reason_code must be non-empty "
            "(e.g., 'shared_library_surface', 'regulatory_domain')"
        )
    if not compensating_controls:
        raise ValueError(
            "build_formal_exception_contract: compensating_controls must be "
            "non-empty for a formal-exception contract"
        )
    return AppRouteContract(
        app_name=app_name,
        route_shape=route_shape,
        static_runtime_mode=static_runtime_mode,
        manifest_path=manifest_path,
        manifest_hash=manifest_hash,
        certification_level=CertificationLevel.STATIC_EVIDENCE,
        required_contracts=(),  # formal exceptions have empty required sets
        bindings=(),
        forbidden_contracts=frozenset(),
        formal_exception_reason_code=reason_code,
        compensating_controls=compensating_controls,
        notes=(
            f"Formal exception contract for route_shape={route_shape.value}, "
            f"reason_code={reason_code!r}. Empty required-contract set is by "
            "design; evidence is proven via compensating_controls (design "
            "matrix v2 §6)."
        ),
    )


__all__ = [
    "AppRouteContract",
    "BUILD_TIME_COMPILER_CONTRACTS",
    "BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS",
    "CertificationLevel",
    "ContractSpanBinding",
    "PhaseAStatus",
    "R3_FORBIDDEN_CONTRACTS",
    "R3_GROUNDED_READ_CONTRACTS",
    "RequiredAttribute",
    "RouteShape",
    "build_build_time_compiler_contract",
    "build_formal_exception_contract",
    "build_r3_grounded_read_contract",
]
