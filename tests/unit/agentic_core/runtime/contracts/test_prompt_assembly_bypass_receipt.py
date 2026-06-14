"""Unit tests for agentic_core.runtime.contracts.prompt_assembly_bypass_receipt.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``prompt_assembly_bypass_receipt`` (L_RUNTIME) is the typed proof that Prompt
Assembly lawfully did NOT run. Frozen dataclass with strict __post_init__ guards
(non-empty ids, required==False, allowed bypass reasons, pinned schema version)
plus a deterministic-digest helper and factory. Coverage targets the allowed-reason
set, every guard branch, to_dict shape, and digest determinism/stability.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.prompt_assembly_bypass_receipt import (
    ALLOWED_PA_BYPASS_REASONS,
    PA_BYPASS_RECEIPT_SCHEMA_VERSION,
    PromptAssemblyBypassReceipt,
    build_prompt_assembly_bypass_receipt,
    compute_pa_bypass_digest,
)

_REASON = "NO_MODEL_EXECUTION_REQUIRED"


def _valid(**overrides: object) -> PromptAssemblyBypassReceipt:
    kwargs: dict = {
        "run_id": "run-1",
        "request_id": "req-1",
        "trace_root": "trace-1",
        "route_contract_id": "rc-1",
        "route_id": "route-1",
        "prompt_assembly_bypass_reason": _REASON,
    }
    kwargs.update(overrides)
    return PromptAssemblyBypassReceipt(**kwargs)  # type: ignore[arg-type]


class TestAllowedReasons:
    def test_reason_set(self) -> None:
        assert ALLOWED_PA_BYPASS_REASONS == frozenset({
            "NO_MODEL_EXECUTION_REQUIRED",
            "TERMINAL_SHORTCIRCUIT_NO_PROMPT",
            "CACHE_REUSE_NO_PROMPT",
            "FALLBACK_NO_PROMPT",
        })

    def test_schema_version_value(self) -> None:
        assert PA_BYPASS_RECEIPT_SCHEMA_VERSION == "1.0"


class TestConstruction:
    def test_minimal_valid_defaults(self) -> None:
        r = _valid()
        assert r.prompt_assembly_required is False
        assert r.model_execution_required is False
        assert r.schema_version == PA_BYPASS_RECEIPT_SCHEMA_VERSION

    @pytest.mark.parametrize("reason", sorted(ALLOWED_PA_BYPASS_REASONS))
    def test_all_allowed_reasons_accepted(self, reason: str) -> None:
        assert _valid(prompt_assembly_bypass_reason=reason).prompt_assembly_bypass_reason == reason


class TestPostInitGuards:
    @pytest.mark.parametrize("field", ["run_id", "request_id", "trace_root", "route_id"])
    def test_empty_required_string_raises(self, field: str) -> None:
        with pytest.raises(ValueError, match=f"{field} must be a non-empty string"):
            _valid(**{field: ""})

    def test_prompt_assembly_required_true_raises(self) -> None:
        with pytest.raises(ValueError, match="prompt_assembly_required must be False"):
            _valid(prompt_assembly_required=True)

    def test_model_execution_required_true_raises(self) -> None:
        with pytest.raises(ValueError, match="model_execution_required must be False"):
            _valid(model_execution_required=True)

    def test_bad_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="prompt_assembly_bypass_reason must be one of"):
            _valid(prompt_assembly_bypass_reason="SOMETHING_ELSE")

    def test_bad_schema_version_raises(self) -> None:
        with pytest.raises(ValueError, match="schema_version must be"):
            _valid(schema_version="9.9")


class TestFrozen:
    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _valid().run_id = "x"  # type: ignore[misc]


class TestToDict:
    def test_to_dict_shape(self) -> None:
        d = _valid(deterministic_digest="sha256:abc").to_dict()
        assert d["schema_version"] == "1.0"
        assert d["run_id"] == "run-1"
        assert d["prompt_assembly_required"] is False
        assert d["model_execution_required"] is False
        assert d["prompt_assembly_bypass_reason"] == _REASON
        assert d["deterministic_digest"] == "sha256:abc"


class TestDigest:
    def test_digest_prefix(self) -> None:
        digest = compute_pa_bypass_digest({"run_id": "r"})
        assert digest.startswith("sha256:")
        assert len(digest) == len("sha256:") + 64

    def test_digest_deterministic(self) -> None:
        payload = {
            "schema_version": "1.0",
            "run_id": "r",
            "request_id": "q",
            "trace_root": "t",
            "route_contract_id": "rc",
            "route_id": "ro",
            "prompt_assembly_required": False,
            "model_execution_required": False,
            "prompt_assembly_bypass_reason": _REASON,
        }
        assert compute_pa_bypass_digest(payload) == compute_pa_bypass_digest(dict(payload))

    def test_digest_ignores_unstable_fields(self) -> None:
        base = {k: "v" for k in ["run_id", "request_id"]}
        with_extra = dict(base)
        with_extra["noise"] = "should-not-matter"
        assert compute_pa_bypass_digest(base) == compute_pa_bypass_digest(with_extra)

    def test_digest_changes_with_stable_field(self) -> None:
        a = compute_pa_bypass_digest({"run_id": "a"})
        b = compute_pa_bypass_digest({"run_id": "b"})
        assert a != b


class TestFactory:
    def test_factory_builds_valid_receipt(self) -> None:
        r = build_prompt_assembly_bypass_receipt(
            run_id="run-1",
            request_id="req-1",
            trace_root="trace-1",
            route_contract_id="rc-1",
            route_id="route-1",
            prompt_assembly_bypass_reason=_REASON,
        )
        assert r.prompt_assembly_required is False
        assert r.deterministic_digest.startswith("sha256:")

    def test_factory_digest_matches_helper(self) -> None:
        r = build_prompt_assembly_bypass_receipt(
            run_id="run-1",
            request_id="req-1",
            trace_root="trace-1",
            route_contract_id="rc-1",
            route_id="route-1",
            prompt_assembly_bypass_reason=_REASON,
        )
        expected = compute_pa_bypass_digest({
            "schema_version": PA_BYPASS_RECEIPT_SCHEMA_VERSION,
            "run_id": "run-1",
            "request_id": "req-1",
            "trace_root": "trace-1",
            "route_contract_id": "rc-1",
            "route_id": "route-1",
            "prompt_assembly_required": False,
            "model_execution_required": False,
            "prompt_assembly_bypass_reason": _REASON,
        })
        assert r.deterministic_digest == expected
