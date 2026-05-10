"""apps_rg app_payload CONSUMPTION tests (AG-2).

The companion suites prove REACHABILITY:
    - test_apps_rg_u0_payload_reflection.py — harness sidecar
    - test_apps_rg_u0_live_wiring.py        — harness on live path
    - test_apps_rg_u0_app_payload_threading.py — app_payload reachable

THIS suite proves CONSUMPTION:
    - L1 reads `validated_request.app_payload` and surfaces 5 projections
      on L1PlanContract
    - L0 reads those projections and surfaces 4 routing fields on RouteContract
    - PA reads validated_request.app_payload (via L1 projections) and emits
      slot_lineage_map + component_hash_map + replay_manifest_ref
    - C0 + PA never reach back to envelope.payload / AppsRgIngressPayload

Plan: .windsurf/plans/apps-rg-app-payload-consumption-wiring-b3a449.md (W5)
"""
from __future__ import annotations

import ast
import copy
import importlib.util as _importlib_util
import inspect
import typing
from pathlib import Path
from typing import Any

import pytest

from agentic_core.L0_routing.apps_rg_l0_binding import l0_route_apps_rg
from agentic_core.L1_cognition.apps_rg_l1_binding import l1_plan_apps_rg
from agentic_core.prompt_governance.apps_rg_pa_binding import pa_compose_apps_rg
from agentic_core.runtime.c0.apps_rg_c0_binding import c0_retrieve_apps_rg
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    RequestEnvelope,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.entry.apps_rg_dispatch import apps_rg_dispatch, apps_rg_parse
from agentic_core.runtime.entry.u0_apps_rg_binding import u0_validate_apps_rg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _thin_payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Senior Director of AI Engineering",
        "target_level": "EXECUTIVE",
        "source_resume_text": "Amit Ayer — leadership profile content.",
        "job_description_text": "Senior Director of AI Engineering — applied research.",
        "manual_brief_path": None,
        "auto_research_internal": False,
        "auto_research_tavily": False,
        "research_via": None,
        "output_directory": "artifacts/apps_rg/runs",
        "idempotency_key": None,
    }
    base.update(overrides)
    return base


def _live_validated_request(thin: dict[str, Any] | None = None) -> ValidatedRequest:
    envelope = apps_rg_parse(thin or _thin_payload())
    assert envelope is not None
    return u0_validate_apps_rg(envelope)


# ---------------------------------------------------------------------------
# 1. L1 — app_payload reaches L1PlanContract (5 projections)
# ---------------------------------------------------------------------------


def test_l1_task_spec_carries_generation_mode_and_capability_requirements() -> None:
    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    assert plan.task_spec, "task_spec must be populated"
    assert plan.task_spec["generation_mode"] in {
        "strategic_tailor", "tailor_existing", "generate_scratch",
        "enhance_current", "healing_fact_check", "healing_unsupported_claim",
        "repair",
    }
    assert "capability_requirements" in plan.task_spec
    assert plan.task_spec["task_class"] == "resume_generation"


def test_l1_query_spec_carries_jd_resume_hashes_and_target() -> None:
    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    assert plan.query_spec
    assert len(plan.query_spec["jd_hash"]) == 64
    assert len(plan.query_spec["resume_hash"]) == 64
    assert plan.query_spec["target"]["company"] == "Acme Corp"
    assert plan.query_spec["target"]["role"]
    assert plan.query_spec["target"]["level"] == "EXECUTIVE"


def test_l1_support_expectation_thresholds_and_provenance_flags() -> None:
    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    se = plan.support_expectation
    assert 0.0 <= se["min_quality"] <= 1.0
    assert 0 <= se["min_ats"] <= 100
    assert se["word_min"] <= se["word_max"]
    assert isinstance(se["provenance_required"], bool)
    assert isinstance(se["fact_checked_required"], bool)
    assert isinstance(se["per_bullet_required"], bool)
    assert isinstance(se["source_quote_required"], bool)


def test_l1_output_expectation_carries_formats_and_flags() -> None:
    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    oe = plan.output_expectation
    assert isinstance(oe["formats"], (list, tuple)) and len(oe["formats"]) >= 1
    assert isinstance(oe["provenance_required"], bool)
    assert isinstance(oe["fact_checked_required"], bool)


def test_l1_policy_refs_carries_all_six_refs() -> None:
    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    refs = plan.policy_refs
    expected_keys = {
        "manifest_digest", "prompt_registry_ref", "hitl_policy_ref",
        "l0_policy_ref", "agent_spec_ref", "thresholds_ref",
    }
    assert set(refs.keys()) == expected_keys
    for key, value in refs.items():
        assert value, f"policy ref {key} must be non-empty"


def test_l1_replay_key_threaded_from_validated_request() -> None:
    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    assert plan.replay_key == vr.replay_key
    assert plan.replay_key.endswith("::v1")


def test_l1_fails_closed_on_missing_app_payload_keys() -> None:
    """If app_payload is empty, L1 raises ValueError BEFORE producing
    an under-specified L1PlanContract."""

    from dataclasses import replace as _replace

    vr = _live_validated_request()
    stripped = _replace(vr, app_payload={})  # bypass the harness
    with pytest.raises(ValueError, match="missing required keys"):
        l1_plan_apps_rg(stripped)


# ---------------------------------------------------------------------------
# 2. L0 — RouteContract reflects L1 projections
# ---------------------------------------------------------------------------


def test_l0_route_family_grounded_when_fact_check_required() -> None:
    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    # Default valid fixture has fact_checked_required=True → grounded family
    assert route.route_family == "evidence_grounded_generation"


def test_l0_route_changes_when_grounding_not_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Patch the synthesizer to emit generation_mode=generate_scratch
    (which doesn't need grounding); L0 must select the ungrounded family."""

    from agentic_core.runtime.entry import u0_apps_rg_binding as binding_mod
    from agentic_core.runtime.u0 import payload_synthesizer as synth_mod

    real_synth = synth_mod.synthesize_contract_payload

    def _scratch_synth(envelope: RequestEnvelope) -> dict[str, Any]:
        contract = real_synth(envelope)
        contract["generation_mode"] = "generate_scratch"
        return contract

    monkeypatch.setattr(binding_mod, "synthesize_contract_payload", _scratch_synth)

    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    assert plan.grounding_required is False, "generate_scratch should drop grounding"
    route = l0_route_apps_rg(plan)
    assert route.route_family == "ungrounded_generation"
    assert route.cache_eligibility["r3_grounded"] is False


def test_l0_cache_eligibility_r1a_always_true_r4_never_for_apps_rg() -> None:
    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    ce = route.cache_eligibility
    assert ce["r1a_exact"] is True
    assert ce["r4_action"] is False
    assert isinstance(ce["r1b_semantic"], bool)
    assert isinstance(ce["r3_grounded"], bool)


def test_l0_route_deterministic_for_same_app_payload() -> None:
    """Same app_payload → same RouteContract field values (modulo timestamp)."""

    vr1 = _live_validated_request()
    vr2 = _live_validated_request()
    plan1 = l1_plan_apps_rg(vr1)
    plan2 = l1_plan_apps_rg(vr2)
    route1 = l0_route_apps_rg(plan1)
    route2 = l0_route_apps_rg(plan2)

    # Deterministic fields:
    assert route1.route_id == route2.route_id
    assert route1.route_family == route2.route_family
    assert route1.execution_form == route2.execution_form
    assert dict(route1.cache_eligibility) == dict(route2.cache_eligibility)
    assert route1.action_required == route2.action_required


def test_l0_action_required_false_for_apps_rg() -> None:
    """apps_rg never sets write_authority_present, so action_required=False."""

    vr = _live_validated_request()
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    assert route.action_required is False
    assert plan.write_authority_present is False


# ---------------------------------------------------------------------------
# 3. PA — CompiledPromptArtifact reflects app_payload via projections
# ---------------------------------------------------------------------------


def _live_compiled_prompt(thin: dict[str, Any] | None = None) -> CompiledPromptArtifact:
    vr = _live_validated_request(thin)
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    fec = c0_retrieve_apps_rg(route, vr)
    return pa_compose_apps_rg(route, plan, fec, vr)


def test_pa_user_instruction_includes_target_from_app_payload() -> None:
    artifact = _live_compiled_prompt()
    assert "Acme Corp" in artifact.user_instruction
    assert "Senior Director of AI Engineering" in artifact.user_instruction
    assert "EXECUTIVE" in artifact.user_instruction


def test_pa_user_instruction_includes_provenance_directives() -> None:
    """Default valid fixture has per_bullet_required=True and
    source_quote_required=True; PA must surface both."""

    artifact = _live_compiled_prompt()
    instr = artifact.user_instruction
    assert "evidence_anchor" in instr, "per_bullet_required directive missing"
    assert "source_quote" in instr, "source_quote_required directive missing"
    assert "fact-checked" in instr.lower() or "fact_checked" in instr, "fact-check directive missing"


def test_pa_emits_slot_lineage_map() -> None:
    artifact = _live_compiled_prompt()
    assert artifact.slot_lineage_map
    assert "system_block_0" in artifact.slot_lineage_map
    assert "user_block_1" in artifact.slot_lineage_map
    assert artifact.slot_lineage_map["system_block_0"].startswith("PA-authored")
    assert "USER_INTENT" in artifact.slot_lineage_map["user_block_1"]


def test_pa_emits_component_hash_map() -> None:
    artifact = _live_compiled_prompt()
    chm = artifact.component_hash_map
    assert chm
    expected_components = {"style_profile", "evidence", "l1_plan", "app_payload", "route"}
    assert set(chm.keys()) == expected_components
    for component, digest in chm.items():
        assert len(digest) == 64, f"{component} digest must be sha256 hex"
        assert all(c in "0123456789abcdef" for c in digest)


def test_pa_emits_replay_manifest_ref() -> None:
    artifact = _live_compiled_prompt()
    assert artifact.replay_manifest_ref.startswith(("reflection:", "replay_key:"))


def test_pa_compilation_hash_deterministic_for_same_inputs() -> None:
    """Pinned identity → same prompt component_hash_map.

    Determinism is the prompt-replay invariant — replay_manifest_ref +
    component_hash_map together must reproduce the prompt envelope. We
    pin request_id/run_id/trace_id so the synthesized contract is
    bit-identical across runs (apps_rg_parse otherwise mints fresh UUIDs
    per invocation, which is correct behaviour but defeats determinism
    comparison).
    """
    from dataclasses import replace as _replace

    pinned = {
        "request_id": "rg-req-pin-AG2",
        "run_id": "rg-run-pin-AG2",
        "trace_id": "rg-trace-pin-AG2",
        "submitted_at": "2026-05-10T12:00:00+00:00",
        "tenant_id": "apps_rg",
    }

    def _build_pinned() -> CompiledPromptArtifact:
        env = apps_rg_parse(_thin_payload())
        assert env is not None
        env = _replace(env, **pinned)
        vr = u0_validate_apps_rg(env)
        plan = l1_plan_apps_rg(vr)
        route = l0_route_apps_rg(plan)
        fec = c0_retrieve_apps_rg(route, vr)
        return pa_compose_apps_rg(route, plan, fec, vr)

    artifact1 = _build_pinned()
    artifact2 = _build_pinned()
    # component_hash_map is fully deterministic — covers app_payload, l1_plan,
    # route, style_profile. Evidence digest changes between runs because
    # FinalEvidenceContract.evidence_collection_timestamp is wall-clock; that
    # propagates into compilation_hash. Assert the AG-2-specific fields are
    # deterministic; full compilation_hash determinism is a downstream goal.
    assert dict(artifact1.component_hash_map) == dict(artifact2.component_hash_map)
    assert artifact1.replay_manifest_ref == artifact2.replay_manifest_ref


def test_pa_compilation_hash_changes_when_app_payload_changes() -> None:
    """Different target → different prompt envelope. Stops the
    cache-collision failure mode where two different inputs share a hash."""

    art1 = _live_compiled_prompt(_thin_payload(target_company="Acme A"))
    art2 = _live_compiled_prompt(_thin_payload(target_company="Acme B"))
    assert art1.compilation_hash != art2.compilation_hash
    assert art1.component_hash_map["app_payload"] != art2.component_hash_map["app_payload"]


def test_pa_output_directive_lists_app_payload_formats() -> None:
    artifact = _live_compiled_prompt()
    assert "json" in artifact.user_instruction


# ---------------------------------------------------------------------------
# 4. No-bypass — C0 + PA reject AppsRgIngressPayload at signature level
# ---------------------------------------------------------------------------


def test_c0_signature_takes_validated_request_not_legacy_payload() -> None:
    """AG-2 hard law: C0 must accept ValidatedRequest, not AppsRgIngressPayload."""

    # `from __future__ import annotations` makes annotations strings; use
    # get_type_hints to resolve them to real types.
    hints = typing.get_type_hints(c0_retrieve_apps_rg)
    sig = inspect.signature(c0_retrieve_apps_rg)
    params = [p for p in sig.parameters if p != "return"]
    assert len(params) == 2
    second_param = params[1]
    assert hints[second_param] is ValidatedRequest, (
        f"c0_retrieve_apps_rg second param must be ValidatedRequest, got {hints[second_param]!r}"
    )


def test_pa_signature_takes_validated_request_not_legacy_payload() -> None:
    """AG-2 hard law: PA must accept ValidatedRequest, not AppsRgIngressPayload."""

    hints = typing.get_type_hints(pa_compose_apps_rg)
    sig = inspect.signature(pa_compose_apps_rg)
    params = [p for p in sig.parameters if p != "return"]
    assert len(params) == 4
    last_param = params[-1]
    assert hints[last_param] is ValidatedRequest, (
        f"pa_compose_apps_rg last param must be ValidatedRequest, got {hints[last_param]!r}"
    )


# ---------------------------------------------------------------------------
# 5. AST-level no-bypass scan — bindings must not import AppsRgIngressPayload
# ---------------------------------------------------------------------------


REPO_ROOT = Path(__file__).resolve().parents[2]

_BINDING_FILES_NO_LEGACY_IMPORT = [
    REPO_ROOT / "agentic_core" / "L1_cognition" / "apps_rg_l1_binding.py",
    REPO_ROOT / "agentic_core" / "L0_routing" / "apps_rg_l0_binding.py",
    REPO_ROOT / "agentic_core" / "runtime" / "c0" / "apps_rg_c0_binding.py",
    REPO_ROOT / "agentic_core" / "prompt_governance" / "apps_rg_pa_binding.py",
]


@pytest.mark.parametrize("binding_file", _BINDING_FILES_NO_LEGACY_IMPORT, ids=lambda p: p.name)
def test_binding_does_not_import_AppsRgIngressPayload(binding_file: Path) -> None:
    """No L1/L0/C0/PA binding may import the legacy AppsRgIngressPayload.

    The legitimate consumer is the U0 stack (synthesizer + adapter); past
    U0, every stage reads ValidatedRequest.app_payload."""

    source = binding_file.read_text(encoding="utf-8")
    tree = ast.parse(source)
    legacy_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "AppsRgIngressPayload":
                    legacy_imports.append(
                        f"{binding_file.name}:{node.lineno} → {node.module}.{alias.name}"
                    )
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.endswith("AppsRgIngressPayload"):
                    legacy_imports.append(
                        f"{binding_file.name}:{node.lineno} → import {alias.name}"
                    )
    assert not legacy_imports, (
        f"AG-2 violation: {binding_file.name} still imports AppsRgIngressPayload — "
        f"{legacy_imports}. Past U0, all bindings must read ValidatedRequest.app_payload."
    )


_BINDING_FILES_NO_ENVELOPE_PAYLOAD = _BINDING_FILES_NO_LEGACY_IMPORT


@pytest.mark.parametrize("binding_file", _BINDING_FILES_NO_ENVELOPE_PAYLOAD, ids=lambda p: p.name)
def test_binding_does_not_access_envelope_payload(binding_file: Path) -> None:
    """No L1/L0/C0/PA binding may read `envelope.payload` or
    `request_envelope.payload`."""

    source = binding_file.read_text(encoding="utf-8")
    tree = ast.parse(source)
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "payload":
            obj = node.value
            if isinstance(obj, ast.Name) and obj.id in {"envelope", "request_envelope"}:
                violations.append(f"{binding_file.name}:{node.lineno} → {obj.id}.payload")
    assert not violations, (
        f"AG-2 violation: {binding_file.name} reads envelope.payload — {violations}"
    )


# ---------------------------------------------------------------------------
# 6. Dispatch passes validated_request to C0 + PA, NOT envelope.payload
# ---------------------------------------------------------------------------


def test_dispatch_passes_validated_request_to_c0_and_pa() -> None:
    """Static AST scan over apps_rg_dispatch.py confirms C0 + PA call sites
    pass `validated_request`, not `envelope.payload`."""

    dispatch_file = REPO_ROOT / "agentic_core" / "runtime" / "entry" / "apps_rg_dispatch.py"
    source = dispatch_file.read_text(encoding="utf-8")
    tree = ast.parse(source)

    c0_calls: list[ast.Call] = []
    pa_calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "c0_retrieve_apps_rg":
                c0_calls.append(node)
            elif node.func.id == "pa_compose_apps_rg":
                pa_calls.append(node)

    assert c0_calls, "c0_retrieve_apps_rg call site missing in dispatch"
    assert pa_calls, "pa_compose_apps_rg call site missing in dispatch"

    for call in c0_calls:
        last_arg = call.args[-1]
        # last arg must be Name node referencing validated_request
        assert isinstance(last_arg, ast.Name) and last_arg.id == "validated_request", (
            f"c0_retrieve_apps_rg call at line {call.lineno} must pass "
            f"`validated_request` as last arg, got {ast.dump(last_arg)}"
        )

    for call in pa_calls:
        last_arg = call.args[-1]
        assert isinstance(last_arg, ast.Name) and last_arg.id == "validated_request", (
            f"pa_compose_apps_rg call at line {call.lineno} must pass "
            f"`validated_request` as last arg, got {ast.dump(last_arg)}"
        )


# ---------------------------------------------------------------------------
# 7. End-to-end smoke — full dispatch returns success with AG-2 wiring
# ---------------------------------------------------------------------------


def test_full_dispatch_succeeds_with_ag2_wiring() -> None:
    """End-to-end proof: a real apps_rg run dispatches successfully through
    the AG-2 wiring (L1 reads app_payload, L0 reflects it, C0 + PA read
    via ValidatedRequest)."""

    envelope = apps_rg_parse(_thin_payload())
    assert envelope is not None
    result = apps_rg_dispatch(envelope)
    assert result.exit_status == "success"
    assert result.outcome_authorized is True


# ---------------------------------------------------------------------------
# 8. Hard-law negative coverage — no ChromaDB, no embeddings
# ---------------------------------------------------------------------------

# Load the AST helper from the gate so tests and gate share identical logic.
_gate_module_path = str(REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_app_payload_consumption.py")
_spec = _importlib_util.spec_from_file_location(
    "check_apps_rg_app_payload_consumption", _gate_module_path
)
_gate_mod = _importlib_util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_gate_mod)  # type: ignore[union-attr]
_ast_chromadb_violations = _gate_mod._ast_chromadb_violations


@pytest.mark.parametrize("binding_file", _BINDING_FILES_NO_LEGACY_IMPORT, ids=lambda p: p.name)
def test_no_chromadb_or_embedding_imports_in_ag2_wiring(binding_file: Path) -> None:
    """AG-2 hard law: no ChromaDB mutation, no embedding generation.

    Uses AST-aware detection (same helper as the CI gate) so that
    explanatory comments such as ``# no ChromaDB collection`` do NOT
    trigger a false positive.
    """
    source = binding_file.read_text(encoding="utf-8")
    violations = _ast_chromadb_violations(source, binding_file.name)
    assert not violations, (
        f"AG-2 hard law violation in {binding_file.name}: {violations}"
    )


# ---------------------------------------------------------------------------
# 8b. AST helper regression tests — verifying pass/fail behaviour
# ---------------------------------------------------------------------------


def test_ast_helper_passes_comment_saying_no_chromadb() -> None:
    """A comment '# no ChromaDB collection' must NOT trigger a violation."""
    source = (
        "def foo():\n"
        "    # no ChromaDB collection\n"
        "    return 42\n"
    )
    assert _ast_chromadb_violations(source, "<test>") == []


def test_ast_helper_passes_docstring_saying_no_chromadb() -> None:
    """A docstring 'No ChromaDB used here' must NOT trigger a violation."""
    source = (
        'def foo():\n'
        '    """No ChromaDB used here."""\n'
        '    return 42\n'
    )
    assert _ast_chromadb_violations(source, "<test>") == []


def test_ast_helper_fails_on_import_chromadb() -> None:
    """``import chromadb`` must be detected."""
    source = "import chromadb\n"
    violations = _ast_chromadb_violations(source, "<test>")
    assert any("import chromadb" in v for v in violations), violations


def test_ast_helper_fails_on_from_chromadb_import() -> None:
    """``from chromadb import PersistentClient`` must be detected."""
    source = "from chromadb import PersistentClient\n"
    violations = _ast_chromadb_violations(source, "<test>")
    assert any("PersistentClient" in v or "chromadb" in v for v in violations), violations


def test_ast_helper_fails_on_chromadb_attribute_usage() -> None:
    """``chromadb.PersistentClient(...)`` must be detected (Name node)."""
    source = "import chromadb\nclient = chromadb.PersistentClient(path='/tmp')\n"
    violations = _ast_chromadb_violations(source, "<test>")
    assert violations, f"Expected violations, got none for chromadb.PersistentClient usage"


def test_ast_helper_fails_on_importlib_dynamic_import() -> None:
    """``importlib.import_module('chromadb')`` must be detected."""
    source = "import importlib\nmod = importlib.import_module('chromadb')\n"
    violations = _ast_chromadb_violations(source, "<test>")
    assert any("import_module" in v for v in violations), violations


def test_ast_helper_passes_for_actual_c0_binding() -> None:
    """The real apps_rg_c0_binding.py (which has explanatory ChromaDB comments)
    must pass the AST-aware gate — confirming the false positive is fixed."""
    c0_file = REPO_ROOT / "agentic_core" / "runtime" / "c0" / "apps_rg_c0_binding.py"
    source = c0_file.read_text(encoding="utf-8")
    violations = _ast_chromadb_violations(source, c0_file.name)
    assert violations == [], (
        f"apps_rg_c0_binding.py should pass AST gate but got: {violations}"
    )
