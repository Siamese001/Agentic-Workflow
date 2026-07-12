"""L1 Plan Contract — AG-RGGOV-W6 Core Contract.

Canonical dataclass for L1 planning output. Mapping projections are recursively
frozen at construction so a frozen contract cannot carry mutable nested state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY, RuntimePosture


class FrozenContractDict(dict):
    """JSON-compatible recursively immutable mapping used by frozen contracts."""

    __slots__ = ()

    @staticmethod
    def _immutable(*_args: Any, **_kwargs: Any) -> None:
        raise TypeError("L1PlanContract mappings are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable
    __ior__ = _immutable

    def __copy__(self) -> "FrozenContractDict":
        return self

    def __deepcopy__(self, _memo: dict[int, Any]) -> "FrozenContractDict":
        return self


class FrozenContractList(list):
    """JSON-compatible recursively immutable list used by frozen contracts."""

    __slots__ = ()

    @staticmethod
    def _immutable(*_args: Any, **_kwargs: Any) -> None:
        raise TypeError("L1PlanContract sequences are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    __iadd__ = _immutable
    __imul__ = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    pop = _immutable
    remove = _immutable
    reverse = _immutable
    sort = _immutable

    def __copy__(self) -> "FrozenContractList":
        return self

    def __deepcopy__(self, _memo: dict[int, Any]) -> "FrozenContractList":
        return self


def _freeze_contract_value(value: Any) -> Any:
    if isinstance(value, (FrozenContractDict, FrozenContractList)):
        return value
    if isinstance(value, Mapping):
        return FrozenContractDict(
            (key, _freeze_contract_value(item)) for key, item in value.items()
        )
    if isinstance(value, list):
        return FrozenContractList(_freeze_contract_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze_contract_value(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze_contract_value(item) for item in value)
    return value


def _stable_capsule_digest(capsule: Mapping[str, Any]) -> str:
    body = dict(capsule)
    body.pop("capsule_digest", None)
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def _walk_mapping_keys(payload: Any) -> set[str]:
    if isinstance(payload, Mapping):
        out = set(payload.keys())
        for value in payload.values():
            out.update(_walk_mapping_keys(value))
        return out
    if isinstance(payload, (list, tuple)):
        out: set[str] = set()
        for value in payload:
            out.update(_walk_mapping_keys(value))
        return out
    return set()


def _validate_embedded_planning_capsule(task_spec: Mapping[str, Any]) -> None:
    capsule = task_spec.get("apps_rg_planning_capsule")
    capsule_ref = str(task_spec.get("apps_rg_planning_capsule_ref") or "").strip()
    if capsule is None and not capsule_ref:
        return
    if not isinstance(capsule, Mapping):
        raise ValueError("L1PlanContract: embedded apps_rg planning capsule must be a mapping")
    declared = str(capsule.get("capsule_digest") or "").strip()
    computed = _stable_capsule_digest(capsule)
    if not declared or declared != computed:
        raise ValueError(
            "L1PlanContract: apps_rg planning capsule digest mismatch "
            f"declared={declared!r} computed={computed!r}"
        )
    if capsule_ref != declared:
        raise ValueError(
            "L1PlanContract: apps_rg_planning_capsule_ref must equal capsule_digest"
        )
    if capsule.get("schema_version") != "apps_rg_l1_planning_capsule.v1":
        raise ValueError("L1PlanContract: unsupported apps_rg planning capsule schema")
    if capsule.get("authority_class") != "PLANNING_ADVISORY_ONLY":
        raise ValueError("L1PlanContract: invalid apps_rg planning capsule authority_class")
    forbidden = _ROUTE_AUTHORITY_KEYS & _walk_mapping_keys(capsule)
    if forbidden:
        raise ValueError(
            "L1PlanContract: apps_rg planning capsule contains route-authority keys "
            f"{sorted(forbidden)}"
        )
    ambiguity = capsule.get("ambiguity_register")
    if not isinstance(ambiguity, Mapping):
        raise ValueError("L1PlanContract: apps_rg planning capsule ambiguity_register missing")
    expected_status = "BLOCKED" if ambiguity.get("blocks_progress") else "READY"
    if capsule.get("planning_status") != expected_status:
        raise ValueError(
            "L1PlanContract: apps_rg planning_status conflicts with ambiguity register"
        )


@dataclass(frozen=True, slots=True)
class L1PlanContract:
    """L1 planning output contract.

    Contains planning decisions, routing requirements, and execution
    prerequisites. It never grants route, evidence, prompt, execution, or write
    authority.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    task_plan: tuple[str, ...] = field(default_factory=tuple)
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)

    grounding_required: bool = False
    apps_research_call_required: bool = False
    model_generation_required: bool = False
    write_authority_present: bool = False

    tenant_id: str = ""
    profile_manifest_digest: str = ""
    target_level: str = ""

    task_spec: Mapping[str, Any] = field(default_factory=dict)
    query_spec: Mapping[str, Any] = field(default_factory=dict)
    support_expectation: Mapping[str, Any] = field(default_factory=dict)
    output_expectation: Mapping[str, Any] = field(default_factory=dict)
    policy_refs: Mapping[str, str] = field(default_factory=dict)

    multiple_work_units_hint: bool = False
    merge_required_hint: bool = False
    per_unit_quality_selection_hint: bool = False
    candidate_generation_expected_hint: bool = False

    planning_timestamp: str = ""
    schema_version: str = "W6.0"
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    signature: str = ""
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_READ_ONLY)
    gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)
    replay_key: str = ""
    snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    l5_certification_ref: str = ""

    non_authority_assertion: Mapping[str, bool] = field(default_factory=dict)
    planning_prior_refs: tuple[str, ...] = field(default_factory=tuple)
    route_hints: Mapping[str, str] = field(default_factory=dict)

    work_shape: str = ""
    task_shape: str = ""
    route_profile_ref: str = ""

    prompt_bom_refs: tuple[str, ...] = field(default_factory=tuple)
    judge_eval_expectation_refs: tuple[str, ...] = field(default_factory=tuple)

    validation_receipt_id: str = ""
    ambiguity_register: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref

        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"L1PlanContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )

        _validate_embedded_planning_capsule(self.task_spec)

        for field_name in (
            "task_spec",
            "query_spec",
            "support_expectation",
            "output_expectation",
            "policy_refs",
            "non_authority_assertion",
            "route_hints",
            "ambiguity_register",
        ):
            object.__setattr__(
                self,
                field_name,
                _freeze_contract_value(getattr(self, field_name)),
            )

        if self.non_authority_assertion:
            _validate_non_authority_assertion(self.non_authority_assertion)
        if self.route_hints:
            _validate_route_hints(self.route_hints)
        if self.prompt_bom_refs:
            _validate_ref_tuple(self.prompt_bom_refs, "prompt_bom_refs")
        if self.judge_eval_expectation_refs:
            _validate_ref_tuple(
                self.judge_eval_expectation_refs,
                "judge_eval_expectation_refs",
            )


_NAA_REQUIRED_KEYS = frozenset(
    {"no_evidence_retrieval", "no_pa_assembly", "no_model_call", "no_c0_import"}
)
_ROUTE_AUTHORITY_KEYS = frozenset(
    {"route_id", "route_family", "execution_form", "selected_route_reason", "route_digest"}
)


def _validate_non_authority_assertion(naa: Mapping[str, bool]) -> None:
    present_keys = set(naa.keys())
    missing_keys = _NAA_REQUIRED_KEYS - present_keys
    if missing_keys:
        raise ValueError(
            "L1PlanContract.non_authority_assertion: missing required keys "
            f"{sorted(missing_keys)}. All of {_NAA_REQUIRED_KEYS} must be present when NAA is asserted."
        )
    extra_keys = present_keys - _NAA_REQUIRED_KEYS
    if extra_keys:
        raise ValueError(
            "L1PlanContract.non_authority_assertion: unknown keys "
            f"{sorted(extra_keys)}. Only {_NAA_REQUIRED_KEYS} are allowed."
        )
    for key, value in naa.items():
        if value is not True:
            raise ValueError(
                f"L1PlanContract.non_authority_assertion: key '{key}' must be True, got {value!r}. "
                "All NAA assertions must affirmatively be True."
            )


def _validate_route_hints(hints: Mapping[str, str]) -> None:
    for key in hints.keys():
        if key in _ROUTE_AUTHORITY_KEYS:
            raise ValueError(
                f"L1PlanContract.route_hints: forbidden route-authority key '{key}'. "
                f"Route hints must not contain {_ROUTE_AUTHORITY_KEYS}."
            )


def _validate_ref_tuple(refs: tuple[str, ...], field_name: str) -> None:
    forbidden_prompt_patterns = [
        "generate",
        "create",
        "write",
        "produce",
        "resume",
        "cv",
        "cover letter",
    ]
    for index, ref in enumerate(refs):
        if not isinstance(ref, str):
            raise ValueError(
                f"L1PlanContract.{field_name}[{index}]: must be str, got {type(ref).__name__}"
            )
        if "\n" in ref or "\r" in ref:
            raise ValueError(
                f"L1PlanContract.{field_name}[{index}]: ref must not contain newlines"
            )
        if "<prompt>" in ref or "</prompt>" in ref or ("<" in ref and ">" in ref):
            raise ValueError(
                f"L1PlanContract.{field_name}[{index}]: ref must not contain XML tags or prompt content"
            )
        if len(ref) > 256:
            raise ValueError(
                f"L1PlanContract.{field_name}[{index}]: ref length {len(ref)} exceeds max 256"
            )
        ref_lower = ref.lower()
        for pattern in forbidden_prompt_patterns:
            if pattern in ref_lower and " " in ref_lower:
                raise ValueError(
                    f"L1PlanContract.{field_name}[{index}]: ref appears to contain prompt content: "
                    f"'{ref[:30]}...'"
                )
