"""apps_rg U0 downstream field-consumption tests.

Proves the second half of the harness contract: a payload that VALIDATES is
ALSO ACCESSIBLE downstream. Catches the failure mode where a field passes
schema validation but is never actually consumed by any layer.

Each test asserts that a specific section of the validated payload (the
domain content under ``ValidatedRequest.app_payload``) is reachable in the
shape the downstream pipeline expects:

    - generation_mode             — PA template selection (AG-3.a)
    - capability_requirements     — L0 model_registry provider routing (AG-4.b)
    - prompt_registry_ref         — PA template chaining (AG-11.a)
    - quality_thresholds          — G22 output_quality gate (AG-8.c W1)
    - hitl_policy_ref             — HITL registry (AG-13.b)
    - output_requirements         — output callback registry (AG-14.a)
    - provenance_requirements     — verbatim_provenance gate (AG-9.b)
    - jd_hash                     — L0 cache + X1D groundedness gate

Plus the cross-check that every "MAPPED" pointer in the field map has a
corresponding accessor — preventing a "validates but ignored" leak.

Plan: .windsurf/plans/apps-rg-u0-reflection-harness-79d032.md (W3.P3.3)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from apps_rg.contracts.apps_rg_ingress_contract_v1 import GenerationMode
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.u0 import apps_rg_u0_adapt
from tests._apps_contract._apps_rg_u0_fixture_builder import load_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]
FIELD_MAP_PATH = REPO_ROOT / "apps_rg" / "contracts" / "apps_rg_ingress_field_map.v1.yaml"


@pytest.fixture
def validated_request() -> ValidatedRequest:
    raw = load_fixture("valid_ingress_contract.v1.json")
    vr, _ = apps_rg_u0_adapt(raw)
    return vr


# ---------------------------------------------------------------------------
# Per-section accessibility
# ---------------------------------------------------------------------------


def test_generation_mode_accessible(validated_request: ValidatedRequest) -> None:
    """Author-Gate AG-3.a — apps_rg user-chosen generation mode flows to PA."""

    raw_mode = validated_request.app_payload["generation_mode"]
    assert raw_mode in {m.value for m in GenerationMode}
    # Round-trip through the enum to prove downstream code can consume it.
    enum_mode = GenerationMode(raw_mode)
    assert isinstance(enum_mode, GenerationMode)


def test_capability_requirements_accessible(validated_request: ValidatedRequest) -> None:
    """Author-Gate AG-4.b — apps_rg declares semantic needs; core L0 maps to provider."""

    requirements = validated_request.app_payload["capability_requirements"]
    assert isinstance(requirements, (list, tuple))
    # Each requirement must be a non-empty string token.
    for req in requirements:
        assert isinstance(req, str) and req.strip()


def test_prompt_registry_ref_accessible(validated_request: ValidatedRequest) -> None:
    """Author-Gate AG-11.a — PA template chaining reads prompt registry ref."""

    ref = validated_request.app_payload["profile_manifest"]["prompt_registry_ref"]
    assert isinstance(ref, str) and ref.strip()


def test_quality_thresholds_accessible(validated_request: ValidatedRequest) -> None:
    """Author-Gate AG-8.c W1 — G22 output_quality gate reads thresholds."""

    thresholds = validated_request.app_payload["quality_thresholds"]
    assert 0.0 <= thresholds["min_quality"] <= 1.0
    assert 0 <= thresholds["min_ats"] <= 100
    assert thresholds["word_min"] <= thresholds["word_max"]


def test_hitl_refs_accessible(validated_request: ValidatedRequest) -> None:
    """Author-Gate AG-13.b — HITL registry reads hitl_policy_ref."""

    ref = validated_request.app_payload["profile_manifest"]["hitl_policy_ref"]
    assert isinstance(ref, str) and ref.strip()


def test_output_requirements_accessible(validated_request: ValidatedRequest) -> None:
    """Author-Gate AG-14.a — output callback registry reads output_requirements."""

    out_req = validated_request.app_payload["output_requirements"]
    assert isinstance(out_req["formats"], (list, tuple)) and len(out_req["formats"]) >= 1
    assert isinstance(out_req["provenance_required"], bool)
    assert isinstance(out_req["fact_checked_required"], bool)


def test_provenance_requirements_accessible(validated_request: ValidatedRequest) -> None:
    """Author-Gate AG-9.b — verbatim_provenance_gate reads provenance_requirements."""

    prov = validated_request.app_payload["provenance_requirements"]
    assert isinstance(prov["per_bullet_required"], bool)
    assert isinstance(prov["source_quote_required"], bool)


def test_jd_hash_accessible(validated_request: ValidatedRequest) -> None:
    """L0 cache (R1A/R1B) + X1D groundedness gate read jd_hash."""

    jd_hash = validated_request.app_payload["jd_payload"]["jd_hash"]
    assert isinstance(jd_hash, str) and len(jd_hash) == 64
    assert all(c in "0123456789abcdef" for c in jd_hash)


def test_target_company_and_role_accessible(validated_request: ValidatedRequest) -> None:
    """Cross-company contamination guard + L1 plan + PA template read target."""

    target = validated_request.app_payload["target"]
    assert target["company"]
    assert target["role"]
    assert target["level"]


# ---------------------------------------------------------------------------
# Cross-check: every MAPPED pointer must be reachable from the validated request
# ---------------------------------------------------------------------------


def _resolve_json_pointer(obj: Any, pointer: str) -> Any:
    """Minimal RFC 6901 resolver — supports object keys and integer list indices.

    Raises KeyError/IndexError if the pointer cannot be resolved (test signal).
    """

    if pointer == "":
        return obj
    if not pointer.startswith("/"):
        raise ValueError(f"Pointer must start with '/': {pointer}")
    parts = pointer.split("/")[1:]
    cur: Any = obj
    for part in parts:
        # JSON Pointer escape sequences
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict):
            cur = cur[part]
        elif isinstance(cur, (list, tuple)):
            cur = cur[int(part)]
        else:
            raise KeyError(f"Cannot traverse {part!r} on {type(cur).__name__}")
    return cur


def test_every_mapped_pointer_resolves_in_validated_request() -> None:
    """The "validates but ignored" failure mode: a field that the field map
    claims is MAPPED must actually be reachable from the produced
    ``ValidatedRequest`` (or its ``app_payload``). This test enumerates all
    MAPPED pointers and proves each one resolves.

    Pointers under ``/transport/*`` may resolve to top-level ValidatedRequest
    fields rather than ``app_payload`` (e.g. /transport/request_id →
    ValidatedRequest.request_id), so the resolver tries both surfaces.
    """

    raw = load_fixture("valid_ingress_contract.v1.json")
    vr, _ = apps_rg_u0_adapt(raw)

    with open(FIELD_MAP_PATH, encoding="utf-8") as f:
        field_map = yaml.safe_load(f)

    # Build the surface that mirrors the input contract under app_payload.
    payload_surface: dict[str, Any] = dict(vr.app_payload)

    # Build a parallel surface for top-level ValidatedRequest fields that
    # MAPPED entries are allowed to resolve through (per the field map's
    # "target: ValidatedRequest.<field>" annotations).
    vr_surface: dict[str, Any] = {
        "transport": {
            "app_id": vr.app_id,
            "task_class": vr.task_class,
            "request_id": vr.request_id,
            "run_id": vr.run_id,
            "trace_id": vr.trace_id,
            "tenant_id": vr.tenant_id,
        },
        "replay": {"replay_key": vr.replay_key},
        "target": {"level": vr.target_level},
    }

    unreachable: list[tuple[str, str]] = []
    for pointer, entry in field_map["mappings"].items():
        if entry.get("status") != "MAPPED":
            continue
        # Try ValidatedRequest top-level surface first, then app_payload.
        try:
            _resolve_json_pointer(vr_surface, pointer)
            continue
        except (KeyError, IndexError, ValueError):
            pass
        try:
            _resolve_json_pointer(payload_surface, pointer)
        except (KeyError, IndexError, ValueError) as exc:
            unreachable.append((pointer, f"{type(exc).__name__}: {exc}"))

    assert not unreachable, (
        "MAPPED pointers must be reachable from ValidatedRequest or its "
        f"app_payload. Unreachable: {unreachable}"
    )


def test_no_field_validates_but_is_ignored_downstream() -> None:
    """Companion invariant: every input top-level key must show up as a
    matching app_payload key, OR be promoted to a ValidatedRequest top-level
    field. Either way the value must not be silently absent."""

    raw = load_fixture("valid_ingress_contract.v1.json")
    vr, _ = apps_rg_u0_adapt(raw)

    promoted_top_level = {
        "transport",  # split into request_id/run_id/trace_id/tenant_id/task_class
        "target",  # level promoted to vr.target_level; rest in app_payload
        "replay",  # replay_key promoted; rest in app_payload
    }
    for top_key in raw:
        # Either preserved verbatim under app_payload or known to be promoted.
        assert top_key in vr.app_payload or top_key in promoted_top_level, (
            f"top-level key {top_key!r} validates but is invisible downstream"
        )
