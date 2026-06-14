"""Unit tests for agentic_core.runtime.contracts.c0_bypass_receipt.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``c0_bypass_receipt`` (L_RUNTIME) carries the typed proof that C0 retrieval
lawfully did NOT run. Exhaustive coverage of the frozen ``C0BypassReceipt``
dataclass, its ``__post_init__`` invariants (grounding_required/c0_required MUST
be False, allowed bypass reasons, schema version pin), the ``build_*`` factory,
and digest determinism of ``compute_c0_bypass_digest``.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.c0_bypass_receipt import (
    ALLOWED_C0_BYPASS_REASONS,
    C0_BYPASS_RECEIPT_SCHEMA_VERSION,
    C0BypassReceipt,
    build_c0_bypass_receipt,
    compute_c0_bypass_digest,
)

_VALID_KW = dict(
    run_id="run-1",
    request_id="req-1",
    trace_root="trace-1",
    route_contract_id="rc-1",
    route_id="route-1",
    c0_bypass_reason="NOT_REQUIRED",
)


class TestAllowedReasons:
    def test_reason_set_members(self) -> None:
        assert ALLOWED_C0_BYPASS_REASONS == frozenset({
            "GROUNDING_NOT_REQUIRED",
            "TERMINAL_SHORTCIRCUIT_NO_RETRIEVAL",
            "CACHE_REUSE_PRIOR_EVIDENCE",
            "FALLBACK_NO_RETRIEVAL",
            "BYPASS_PRELOADED_CONTEXT",
            "BYPASS_CACHE_RETURN",
            "BYPASS_FALLBACK",
            "NOT_REQUIRED",
        })

    def test_schema_version(self) -> None:
        assert C0_BYPASS_RECEIPT_SCHEMA_VERSION == "1.0"


class TestConstruction:
    def test_defaults(self) -> None:
        r = C0BypassReceipt(**_VALID_KW)
        assert r.grounding_required is False
        assert r.c0_required is False
        assert r.schema_version == C0_BYPASS_RECEIPT_SCHEMA_VERSION
        assert r.deterministic_digest == ""

    @pytest.mark.parametrize("reason", sorted(ALLOWED_C0_BYPASS_REASONS))
    def test_all_allowed_reasons_accepted(self, reason: str) -> None:
        r = C0BypassReceipt(**{**_VALID_KW, "c0_bypass_reason": reason})
        assert r.c0_bypass_reason == reason

    def test_frozen(self) -> None:
        r = C0BypassReceipt(**_VALID_KW)
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.run_id = "mutated"  # type: ignore[misc]

    def test_to_dict_round(self) -> None:
        r = C0BypassReceipt(**_VALID_KW)
        d = r.to_dict()
        assert d["run_id"] == "run-1"
        assert d["grounding_required"] is False
        assert d["c0_bypass_reason"] == "NOT_REQUIRED"
        assert d["schema_version"] == "1.0"


class TestPostInitInvariants:
    @pytest.mark.parametrize("field", ["run_id", "request_id", "trace_root", "route_id"])
    def test_empty_required_string_raises(self, field: str) -> None:
        with pytest.raises(ValueError, match="non-empty string"):
            C0BypassReceipt(**{**_VALID_KW, field: ""})

    def test_grounding_required_true_raises(self) -> None:
        with pytest.raises(ValueError, match="grounding_required must be False"):
            C0BypassReceipt(**{**_VALID_KW, "grounding_required": True})

    def test_c0_required_true_raises(self) -> None:
        with pytest.raises(ValueError, match="c0_required must be False"):
            C0BypassReceipt(**{**_VALID_KW, "c0_required": True})

    def test_unknown_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="c0_bypass_reason must be one of"):
            C0BypassReceipt(**{**_VALID_KW, "c0_bypass_reason": "MADE_UP"})

    def test_wrong_schema_version_raises(self) -> None:
        with pytest.raises(ValueError, match="schema_version must be"):
            C0BypassReceipt(**{**_VALID_KW, "schema_version": "9.9"})


class TestDigestDeterminism:
    def test_same_input_same_digest(self) -> None:
        payload = {
            "schema_version": "1.0",
            "run_id": "r",
            "request_id": "q",
            "trace_root": "t",
            "route_contract_id": "rc",
            "route_id": "ro",
            "grounding_required": False,
            "c0_required": False,
            "c0_bypass_reason": "NOT_REQUIRED",
        }
        assert compute_c0_bypass_digest(payload) == compute_c0_bypass_digest(dict(payload))

    def test_digest_prefix_and_changes_on_input(self) -> None:
        base = {"run_id": "a", "c0_bypass_reason": "NOT_REQUIRED"}
        d1 = compute_c0_bypass_digest(base)
        d2 = compute_c0_bypass_digest({"run_id": "b", "c0_bypass_reason": "NOT_REQUIRED"})
        assert d1.startswith("sha256:")
        assert d1 != d2

    def test_digest_ignores_unstable_fields(self) -> None:
        # Fields outside _DIGEST_STABLE_FIELDS must not affect the digest.
        a = compute_c0_bypass_digest({"run_id": "a"})
        b = compute_c0_bypass_digest({"run_id": "a", "extraneous": "noise"})
        assert a == b


class TestBuildFactory:
    def test_build_populates_digest(self) -> None:
        r = build_c0_bypass_receipt(
            run_id="run-1",
            request_id="req-1",
            trace_root="trace-1",
            route_contract_id="rc-1",
            route_id="route-1",
            c0_bypass_reason="NOT_REQUIRED",
        )
        assert r.deterministic_digest.startswith("sha256:")
        assert r.grounding_required is False
        assert r.c0_required is False

    def test_build_is_deterministic(self) -> None:
        kw = dict(
            run_id="run-1",
            request_id="req-1",
            trace_root="trace-1",
            route_contract_id="rc-1",
            route_id="route-1",
            c0_bypass_reason="BYPASS_CACHE_RETURN",
        )
        assert build_c0_bypass_receipt(**kw).deterministic_digest == (
            build_c0_bypass_receipt(**kw).deterministic_digest
        )

    def test_build_rejects_unknown_reason(self) -> None:
        with pytest.raises(ValueError, match="c0_bypass_reason must be one of"):
            build_c0_bypass_receipt(
                run_id="run-1",
                request_id="req-1",
                trace_root="trace-1",
                route_contract_id="rc-1",
                route_id="route-1",
                c0_bypass_reason="NOPE",
            )
