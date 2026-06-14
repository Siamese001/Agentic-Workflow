"""Unit tests for agentic_core.runtime.prove_requirements.tier_fixture_bootstrap.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
Deterministic Tier 0..6 fixture bootstrap. Tests the pure / deterministic
surface only — scenario-key normalization, replay-run indexing, path classifiers,
the SHA256 ``_deterministic_digest`` (same seed → same digest), and the trace /
replay / e2e / generic payload builders that pick the right shape per path.
No filesystem materialization is exercised (``materialize`` writes under
``artifacts/`` and is excluded from this pure-surface suite).
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.runtime.prove_requirements import tier_fixture_bootstrap as boot


class TestDeterministicDigest:
    def test_sha256_prefix_and_value(self) -> None:
        out = boot._deterministic_digest("A_grounded_read")
        expected = "sha256:" + hashlib.sha256(b"A_grounded_read").hexdigest()
        assert out == expected

    def test_same_seed_same_digest(self) -> None:
        assert boot._deterministic_digest("k") == boot._deterministic_digest("k")

    def test_different_seed_different_digest(self) -> None:
        assert boot._deterministic_digest("k1") != boot._deterministic_digest("k2")


class TestScenarioKey:
    @pytest.mark.parametrize(
        "rel,expected",
        [
            ("traces/scenario_A_grounded_read.json", "A_grounded_read"),
            ("replay/replay_A_grounded_read_run_1.json", "A_grounded_read"),
            ("replay/replay_A_grounded_read_run_2.json", "A_grounded_read"),
            ("replay/replay_A_grounded_read_run_3.json", "A_grounded_read"),
            ("misc/plain_name.json", "plain_name"),
        ],
    )
    def test_scenario_key_normalization(self, rel: str, expected: str) -> None:
        assert boot._scenario_key(rel) == expected

    def test_replay_pair_shares_scenario_key(self) -> None:
        k1 = boot._scenario_key("replay/replay_M_c0_no_execute_run_1.json")
        k2 = boot._scenario_key("replay/replay_M_c0_no_execute_run_2.json")
        assert k1 == k2 == "M_c0_no_execute"


class TestReplayRunIndex:
    @pytest.mark.parametrize(
        "rel,expected",
        [
            ("replay/replay_x_run_1.json", 1),
            ("replay/replay_x_run_2.json", 2),
            ("replay/replay_x_run_3.json", 3),
            ("replay/replay_x.json", 0),
            ("traces/scenario_x.json", 0),
        ],
    )
    def test_run_index(self, rel: str, expected: int) -> None:
        assert boot._replay_run_index(rel) == expected


class TestPathClassifiers:
    def test_is_replay_path_true(self) -> None:
        assert boot._is_replay_path("artifacts/x/replay/replay_a_run_1.json") is True

    def test_is_replay_path_requires_both_dir_and_prefix(self) -> None:
        # In replay dir but not replay_ prefix.
        assert boot._is_replay_path("artifacts/x/replay/scenario_a.json") is False

    def test_is_replay_path_dir_check_normalizes_backslashes(self) -> None:
        # The "/replay/" directory check normalizes backslashes, but
        # ``Path.stem`` on POSIX treats a backslash string as one segment,
        # so ``.startswith("replay_")`` is False → overall False.
        assert boot._is_replay_path("artifacts\\x\\replay\\replay_a_run_1.json") is False

    def test_is_replay_path_forward_slash_true(self) -> None:
        assert boot._is_replay_path("artifacts/x/replay/replay_a_run_1.json") is True

    def test_is_trace_path(self) -> None:
        assert boot._is_trace_path("artifacts/x/traces/scenario_a.json") is True
        assert boot._is_trace_path("artifacts/x/replay/replay_a_run_1.json") is False

    def test_is_e2e_path(self) -> None:
        assert boot._is_e2e_path("artifacts/e2e/receipt.json") is True
        assert boot._is_e2e_path("artifacts/traces/x.json") is False


class TestScenarioExtras:
    def test_static_drift_extras_full(self) -> None:
        extras = boot._maybe_static_drift_extras(boot._STATIC_DRIFT_KEY)
        assert extras["step1_req_id"] == boot._STATIC_DRIFT_REQ_ID
        assert extras["expected_fail_reason"] == boot._STATIC_DRIFT_EFR
        assert extras["drift_detected"] is True
        assert extras["gate_result"] == "BLOCKED"

    def test_non_drift_scenario_omits_drift_fields(self) -> None:
        extras = boot._maybe_static_drift_extras("M_c0_no_execute")
        assert extras["step1_req_id"] == "REQ-C0-NO-EXECUTE-001"
        assert "drift_detected" not in extras

    def test_unknown_scenario_yields_empty(self) -> None:
        assert boot._maybe_static_drift_extras("ZZ_not_a_scenario") == {}

    def test_tier4_rows_registered_in_scenario_extras(self) -> None:
        assert boot._SCENARIO_EXTRAS["AV_l5_authority_registry_bind"] == (
            "REQ-L5-AUTHORITY-REGISTRY-BIND-001",
            "L5_AUTHORITY_REGISTRY_BIND_REQUIRED",
        )

    def test_trace_rich_extras_tuple_coerced_to_list(self) -> None:
        out = boot._maybe_trace_rich_extras("M_c0_no_execute")
        assert isinstance(out["evidence_refs"], list)

    def test_trace_rich_extras_unknown_empty(self) -> None:
        assert boot._maybe_trace_rich_extras("ZZ_not_a_scenario") == {}


class TestPayloadDispatch:
    def test_trace_payload_shape(self) -> None:
        p = boot._trace_payload("A_grounded_read")
        assert p["fixture_kind"] == "deterministic_bootstrap_trace"
        assert p["scenario_id"] == "scenario_A_grounded_read"
        assert p["invariant_digest"] == boot._deterministic_digest("A_grounded_read")

    def test_replay_payload_shape_and_digest_matches_trace(self) -> None:
        trace = boot._trace_payload("A_grounded_read")
        replay = boot._replay_payload("A_grounded_read", 1)
        # Replay pairs for the same scenario share the invariant digest.
        assert replay["invariant_digest"] == trace["invariant_digest"]
        assert replay["replay_run_index"] == 1
        assert replay["fixture_kind"] == "deterministic_bootstrap_replay"

    def test_payload_for_routes_trace(self) -> None:
        p = boot._payload_for("artifacts/x/traces/scenario_A_grounded_read.json")
        assert p["fixture_kind"] == "deterministic_bootstrap_trace"

    def test_payload_for_routes_replay(self) -> None:
        p = boot._payload_for("artifacts/x/replay/replay_A_grounded_read_run_2.json")
        assert p["fixture_kind"] == "deterministic_bootstrap_replay"
        assert p["replay_run_index"] == 2

    def test_payload_for_routes_e2e(self) -> None:
        p = boot._payload_for("artifacts/e2e/some_receipt.json")
        assert p["fixture_kind"] == "deterministic_bootstrap_e2e"

    def test_payload_for_routes_generic(self) -> None:
        p = boot._payload_for("artifacts/other/unknown.json")
        assert p["fixture_kind"] == "deterministic_bootstrap_generic"

    def test_payload_for_routes_tier6_reference_policy(self) -> None:
        p = boot._payload_for(boot._TIER6_REFERENCE_ONLY_POLICY_REL)
        assert p["policy_name"] == "TIER6_NON_BLOCKING_REFERENCE_POLICY"
        assert p["total_reference_only_rows"] == len(boot._TIER6_REFERENCE_ONLY_REQ_IDS)


class TestSummarize:
    def test_summarize_counts(self) -> None:
        created, existing = boot._summarize(
            {"a": "created", "b": "exists", "c": "created"}
        )
        assert (created, existing) == (2, 1)
