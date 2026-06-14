"""Unit tests for agentic_core.L0_routing.app_domain_resolver.

Wave 6.1 (P2 untested-module coverage) — pure surface only. Covers the frozen
AppContractRefBundle dataclass (construction, defaults, frozen) and the
deterministic _pick_single_ref helper. The store-backed resolve_* functions
require a live InMemoryAppDomainStore + AppDomainContractRecord and are out of
scope for pure unit coverage.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.app_domain_resolver import (
    AppContractRefBundle,
    _pick_single_ref,
)


def _bundle(**over) -> AppContractRefBundle:
    base = dict(
        app_id="apps_demo",
        task_class="generate",
        domain_contract_ref="dc",
        domain_contract_digest="digest123",
        input_contract_ref="ic",
        output_schema_ref="os",
        rubric_ref="rb",
        threshold_profile_ref="tp",
        grader_roster_ref="gr",
        retrieval_profile_ref="rp",
        prompt_profile_ref="pp",
        capability_profile_ref="cp",
        route_profile_ref="rt",
    )
    base.update(over)
    return AppContractRefBundle(**base)


class TestAppContractRefBundle:
    def test_construction_defaults(self):
        b = _bundle()
        assert b.orchestration_profile_ref == ""
        assert b.app_contract_l4_record_refs == ()

    def test_explicit_optional_fields(self):
        b = _bundle(
            orchestration_profile_ref="orch",
            app_contract_l4_record_refs=("r1", "r2"),
        )
        assert b.orchestration_profile_ref == "orch"
        assert b.app_contract_l4_record_refs == ("r1", "r2")

    def test_frozen(self):
        b = _bundle()
        with pytest.raises(dataclasses.FrozenInstanceError):
            b.app_id = "other"  # type: ignore[misc]

    def test_field_roundtrip(self):
        b = _bundle(rubric_ref="rubric-x", threshold_profile_ref="thr-y")
        assert b.rubric_ref == "rubric-x"
        assert b.threshold_profile_ref == "thr-y"

    def test_equality_value_semantics(self):
        assert _bundle() == _bundle()
        assert _bundle(app_id="a") != _bundle(app_id="b")


class TestPickSingleRef:
    def test_empty_returns_default_empty(self):
        assert _pick_single_ref(()) == ""

    def test_empty_returns_custom_default(self):
        assert _pick_single_ref((), default="fallback") == "fallback"

    def test_single_element(self):
        assert _pick_single_ref(("only",)) == "only"

    @pytest.mark.parametrize(
        "refs,expected",
        [
            (("first", "second"), "first"),
            (("a", "b", "c"), "a"),
        ],
    )
    def test_picks_first_deterministically(self, refs, expected):
        assert _pick_single_ref(refs) == expected
        # determinism: repeated calls identical
        assert _pick_single_ref(refs) == expected
