"""Unit tests for agentic_core.runtime.contracts.identity.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core
runtime-identity contract. ``RuntimeIdentityEnvelope`` is the SSOT identity
envelope for one runtime invocation; its hostile-verifier invariants
(non-empty run/request/trace/replay ids, schema pinning, bool git_dirty) and
the deterministic_digest (stable fields only — volatile timing/commit fields
excluded) are exercised exhaustively here.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.identity import (
    IDENTITY_ENVELOPE_SCHEMA_VERSION,
    RuntimeIdentityEnvelope,
    build_runtime_identity_envelope,
    compute_identity_deterministic_digest,
)


def _kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "run_id": "run-1",
        "request_id": "req-1",
        "trace_root": "trace-1",
        "replay_key": "replay-1",
        "policy_hash": "ph-1",
        "blueprint_hash": "bh-1",
        "caller_surface": "cli",
        "entrypoint_command": "python -m apps_rg",
        "started_at_utc": "2026-06-14T00:00:00+00:00",
        "git_commit": "abc123",
        "git_dirty": False,
    }
    base.update(overrides)
    return base


class TestSchemaConstant:
    def test_schema_version_value(self) -> None:
        assert IDENTITY_ENVELOPE_SCHEMA_VERSION == "1.0"


class TestBuilder:
    def test_builds_and_binds_digest(self) -> None:
        env = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        assert isinstance(env, RuntimeIdentityEnvelope)
        assert env.deterministic_digest.startswith("sha256:")
        assert env.schema_version == IDENTITY_ENVELOPE_SCHEMA_VERSION

    def test_optional_fields_default(self) -> None:
        env = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        assert env.registry_digest_set == {}
        assert env.route_contract_id == ""
        assert env.route_id == ""
        assert env.app_name == ""

    def test_git_dirty_coerced_to_bool(self) -> None:
        env = build_runtime_identity_envelope(**_kwargs(git_dirty=1))  # type: ignore[arg-type]
        assert env.git_dirty is True


class TestDigestDeterminism:
    def test_digest_reproducible(self) -> None:
        a = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        b = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        assert a.deterministic_digest == b.deterministic_digest

    @pytest.mark.parametrize(
        "volatile",
        [
            {"started_at_utc": "2099-01-01T00:00:00+00:00"},
            {"git_commit": "ffffff"},
            {"git_dirty": True},
        ],
    )
    def test_volatile_fields_excluded_from_digest(self, volatile: dict[str, object]) -> None:
        base = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        mutated = build_runtime_identity_envelope(**_kwargs(**volatile))  # type: ignore[arg-type]
        assert base.deterministic_digest == mutated.deterministic_digest

    @pytest.mark.parametrize(
        "stable",
        [
            {"run_id": "run-2"},
            {"request_id": "req-2"},
            {"trace_root": "trace-2"},
            {"replay_key": "replay-2"},
            {"policy_hash": "ph-2"},
            {"blueprint_hash": "bh-2"},
            {"route_id": "route-2"},
            {"app_name": "apps_qna"},
            {"caller_surface": "http"},
        ],
    )
    def test_stable_fields_change_digest(self, stable: dict[str, object]) -> None:
        base = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        mutated = build_runtime_identity_envelope(**_kwargs(**stable))  # type: ignore[arg-type]
        assert base.deterministic_digest != mutated.deterministic_digest

    def test_compute_digest_matches_builder(self) -> None:
        env = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        recomputed = compute_identity_deterministic_digest(env.to_dict())
        assert recomputed == env.deterministic_digest

    def test_registry_digest_set_participates(self) -> None:
        base = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        with_reg = build_runtime_identity_envelope(
            **_kwargs(registry_digest_set={"a": "1"})  # type: ignore[arg-type]
        )
        assert base.deterministic_digest != with_reg.deterministic_digest

    def test_registry_digest_set_order_invariant(self) -> None:
        one = build_runtime_identity_envelope(
            **_kwargs(registry_digest_set={"a": "1", "b": "2"})  # type: ignore[arg-type]
        )
        two = build_runtime_identity_envelope(
            **_kwargs(registry_digest_set={"b": "2", "a": "1"})  # type: ignore[arg-type]
        )
        assert one.deterministic_digest == two.deterministic_digest


class TestPostInitInvariants:
    @pytest.mark.parametrize("name", ["run_id", "request_id", "trace_root", "replay_key"])
    def test_empty_mandatory_id_raises(self, name: str) -> None:
        with pytest.raises(ValueError, match=f"{name} must be a non-empty string"):
            build_runtime_identity_envelope(**_kwargs(**{name: ""}))  # type: ignore[arg-type]

    @pytest.mark.parametrize("name", ["run_id", "request_id", "trace_root", "replay_key"])
    def test_non_string_mandatory_id_raises(self, name: str) -> None:
        # Construct directly to bypass builder coercion paths.
        kwargs = _kwargs(**{name: None})
        with pytest.raises(ValueError, match="non-empty string"):
            RuntimeIdentityEnvelope(**kwargs)  # type: ignore[arg-type]

    def test_bad_schema_version_raises(self) -> None:
        kwargs = _kwargs()
        with pytest.raises(ValueError, match="schema_version must be"):
            RuntimeIdentityEnvelope(schema_version="2.0", **kwargs)  # type: ignore[arg-type]

    def test_non_bool_git_dirty_raises(self) -> None:
        kwargs = _kwargs(git_dirty="yes")
        with pytest.raises(ValueError, match="git_dirty must be bool"):
            RuntimeIdentityEnvelope(**kwargs)  # type: ignore[arg-type]


class TestFrozenAndToDict:
    def test_frozen(self) -> None:
        env = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        with pytest.raises(dataclasses.FrozenInstanceError):
            env.run_id = "other"  # type: ignore[misc]

    def test_to_dict_has_all_keys(self) -> None:
        env = build_runtime_identity_envelope(**_kwargs())  # type: ignore[arg-type]
        d = env.to_dict()
        for key in (
            "schema_version", "run_id", "request_id", "trace_root", "replay_key",
            "policy_hash", "blueprint_hash", "registry_digest_set", "route_contract_id",
            "route_id", "app_name", "caller_surface", "entrypoint_command",
            "started_at_utc", "git_commit", "git_dirty", "deterministic_digest",
        ):
            assert key in d

    def test_to_dict_registry_is_plain_dict(self) -> None:
        env = build_runtime_identity_envelope(
            **_kwargs(registry_digest_set={"a": "1"})  # type: ignore[arg-type]
        )
        assert env.to_dict()["registry_digest_set"] == {"a": "1"}
        assert isinstance(env.to_dict()["registry_digest_set"], dict)
