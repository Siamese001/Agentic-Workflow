"""Unit tests for agentic_core.runtime.contracts.l1_plan_contract.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 runtime-contract surface.
``l1_plan_contract`` (fan_in=40, L_RUNTIME) is the L1 planning-output contract.
Its __post_init__ enforces the L5 cert-ref fail-closed guard plus non-authority
assertion, route-hint authority rejection, and ref-tuple hygiene — exhaustive coverage.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY, RuntimePosture

_NAA_OK = {
    "no_evidence_retrieval": True,
    "no_pa_assembly": True,
    "no_model_call": True,
    "no_c0_import": True,
}


def _plan(**overrides: object) -> L1PlanContract:
    base: dict[str, object] = dict(
        request_id="req-1",
        run_id="run-1",
        app_id="apps_rg",
        trace_id="trace-1",
        l5_certification_ref="cert-ref-1",
    )
    base.update(overrides)
    return L1PlanContract(**base)  # type: ignore[arg-type]


class TestConstructionAndDefaults:
    def test_valid_construction(self) -> None:
        p = _plan()
        assert p.request_id == "req-1"
        assert p.app_id == "apps_rg"

    def test_scalar_defaults(self) -> None:
        p = _plan()
        assert p.grounding_required is False
        assert p.apps_research_call_required is False
        assert p.model_generation_required is False
        assert p.write_authority_present is False
        assert p.schema_version == "W6.0"
        assert p.tenant_id == ""
        assert p.target_level == ""
        assert p.work_shape == ""

    def test_collection_defaults_empty(self) -> None:
        p = _plan()
        assert p.task_plan == ()
        assert p.required_capabilities == ()
        assert p.task_spec == {}
        assert p.policy_refs == {}
        assert p.non_authority_assertion == {}
        assert p.route_hints == {}
        assert p.prompt_bom_refs == ()

    def test_posture_default_read_only(self) -> None:
        p = _plan()
        assert isinstance(p.posture, RuntimePosture)
        assert p.posture == POSTURE_READ_ONLY

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _plan().work_shape = "x"  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        assert not hasattr(_plan(), "__dict__")


class TestCertRefInvariant:
    def test_missing_raises(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _plan(l5_certification_ref="")

    @pytest.mark.parametrize("bad", ["   ", "\t"])
    def test_blank_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _plan(l5_certification_ref=bad)


class TestNonAuthorityAssertion:
    def test_valid_naa(self) -> None:
        assert _plan(non_authority_assertion=dict(_NAA_OK)).non_authority_assertion == _NAA_OK

    def test_missing_key_raises(self) -> None:
        naa = dict(_NAA_OK)
        del naa["no_model_call"]
        with pytest.raises(ValueError, match="missing required keys"):
            _plan(non_authority_assertion=naa)

    def test_extra_key_raises(self) -> None:
        naa = dict(_NAA_OK)
        naa["bogus"] = True
        with pytest.raises(ValueError, match="unknown keys"):
            _plan(non_authority_assertion=naa)

    def test_false_value_raises(self) -> None:
        naa = dict(_NAA_OK)
        naa["no_c0_import"] = False
        with pytest.raises(ValueError, match="must be True"):
            _plan(non_authority_assertion=naa)


class TestRouteHints:
    def test_clean_hints_ok(self) -> None:
        assert _plan(route_hints={"prefer": "fast"}).route_hints == {"prefer": "fast"}

    @pytest.mark.parametrize(
        "key",
        ["route_id", "route_family", "execution_form", "selected_route_reason", "route_digest"],
    )
    def test_authority_key_raises(self, key: str) -> None:
        with pytest.raises(ValueError, match="forbidden route-authority key"):
            _plan(route_hints={key: "x"})


class TestRefTupleHygiene:
    def test_clean_refs_ok(self) -> None:
        assert _plan(prompt_bom_refs=("bom-001", "bom-002")).prompt_bom_refs == ("bom-001", "bom-002")

    def test_newline_raises(self) -> None:
        with pytest.raises(ValueError, match="newlines"):
            _plan(prompt_bom_refs=("bad\nref",))

    def test_xml_tag_raises(self) -> None:
        with pytest.raises(ValueError, match="XML tags or prompt content"):
            _plan(prompt_bom_refs=("<prompt>x</prompt>",))

    def test_too_long_raises(self) -> None:
        with pytest.raises(ValueError, match="exceeds max 256"):
            _plan(prompt_bom_refs=("x" * 257,))

    def test_prompt_content_pattern_raises(self) -> None:
        with pytest.raises(ValueError, match="prompt content"):
            _plan(prompt_bom_refs=("please generate output",))

    def test_judge_eval_refs_validated_too(self) -> None:
        with pytest.raises(ValueError, match="newlines"):
            _plan(judge_eval_expectation_refs=("bad\rref",))
