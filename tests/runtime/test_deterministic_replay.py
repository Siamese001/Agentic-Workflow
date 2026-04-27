"""
tests/runtime/test_deterministic_replay.py

Phase 6 acceptance test (one of the 14 spec-named tests).

Asserts that:
  * Each scenario produced replay_run_1.json and replay_run_2.json artifacts
  * replay_comparison.json exists and reports all_scenarios_match=true
  * The deterministic projection (uuid + clock stripped) yields identical
    SHA-256 digests across the two runs of every scenario
  * The set of fields that DID match (deterministic) and DID NOT
    (nondeterministic) is exactly what the contract declares
  * Per-span deterministic fields are byte-identical -- not just the
    aggregate digest, but each span's deterministic projection too

This is the FOUNDATIONAL replay test. PROVEN status for any record that
needs replay evidence still requires the runtime stage to actually emit
the relevant span (Phase 4 wiring), plus the anti-bypass negatives in
Phase 7 to fire on tamper attempts.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.prove_requirements.replay_engine import (
    DETERMINISTIC_FIELDS,
    NONDETERMINISTIC_FIELDS,
    deterministic_projection,
    replay_digest,
)


EXPECTED_SCENARIOS = (
    "A_grounded_read",
    "B_managed_workflow",
    "C_weak_evidence",
    "D_anti_bypass",
    "E_authorized_commit",
)


@pytest.fixture(scope="module")
def replay_dir(proof_artifacts: Path) -> Path:
    return proof_artifacts / "replay"


@pytest.fixture(scope="module")
def comparison(replay_dir: Path) -> dict:
    p = replay_dir / "replay_comparison.json"
    if not p.exists():
        pytest.fail(f"missing replay_comparison.json at {p}")
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def replay_pairs(replay_dir: Path) -> dict[str, tuple[dict, dict]]:
    out: dict[str, tuple[dict, dict]] = {}
    for scen in EXPECTED_SCENARIOS:
        p1 = replay_dir / f"replay_{scen}_run_1.json"
        p2 = replay_dir / f"replay_{scen}_run_2.json"
        if not p1.exists() or not p2.exists():
            pytest.fail(f"missing replay run files for {scen}")
        out[scen] = (
            json.loads(p1.read_text(encoding="utf-8")),
            json.loads(p2.read_text(encoding="utf-8")),
        )
    return out


def test_replay_dir_exists(replay_dir: Path) -> None:
    assert replay_dir.exists() and replay_dir.is_dir()


def test_replay_comparison_artifact_present(comparison: dict) -> None:
    assert "all_scenarios_match" in comparison
    assert "scenarios" in comparison


def test_all_four_scenarios_match(comparison: dict) -> None:
    assert comparison["all_scenarios_match"] is True, (
        f"replay-determinism failed: {comparison}"
    )


def test_each_scenario_pair_files_exist(replay_dir: Path) -> None:
    for scen in EXPECTED_SCENARIOS:
        assert (replay_dir / f"replay_{scen}_run_1.json").exists()
        assert (replay_dir / f"replay_{scen}_run_2.json").exists()


def test_each_scenario_digest_matches(replay_pairs: dict[str, tuple[dict, dict]]) -> None:
    for scen, (run1, run2) in replay_pairs.items():
        d1 = replay_digest(run1)
        d2 = replay_digest(run2)
        assert d1 == d2, (
            f"scenario {scen} replay digest drift: run_1={d1[:16]}..., run_2={d2[:16]}..."
        )


def test_uuid_fields_DID_differ_across_runs(replay_pairs: dict[str, tuple[dict, dict]]) -> None:
    """Sanity-check: trace_id/request_id/run_id are FRESH per run.
    If they were equal, the recorder would not be doing fresh uuid
    generation and the determinism guarantee would be vacuous."""
    for scen, (run1, run2) in replay_pairs.items():
        assert run1["trace_id"] != run2["trace_id"], f"{scen} trace_id was reused"
        assert run1["request_id"] != run2["request_id"], f"{scen} request_id was reused"
        assert run1["run_id"] != run2["run_id"], f"{scen} run_id was reused"


def test_deterministic_field_list_documented_in_artifact(comparison: dict) -> None:
    listed = comparison.get("fields_compared_deterministic", [])
    assert set(listed) == set(DETERMINISTIC_FIELDS), (
        f"comparison artifact deterministic field list drift: {listed} vs {DETERMINISTIC_FIELDS}"
    )


def test_nondeterministic_field_list_documented_in_artifact(comparison: dict) -> None:
    listed = comparison.get("fields_compared_nondeterministic", [])
    assert set(listed) == set(NONDETERMINISTIC_FIELDS), (
        f"comparison artifact nondeterministic field list drift: {listed} vs {NONDETERMINISTIC_FIELDS}"
    )


def test_per_span_deterministic_projection_matches(replay_pairs: dict[str, tuple[dict, dict]]) -> None:
    """Stronger than aggregate-digest: each span's deterministic projection
    must be byte-identical across runs."""
    for scen, (run1, run2) in replay_pairs.items():
        proj1 = deterministic_projection(run1)["spans"]
        proj2 = deterministic_projection(run2)["spans"]
        assert len(proj1) == len(proj2), f"{scen} span_count drift"
        for left, right in zip(proj1, proj2):
            assert left["path"] == right["path"], f"{scen} span path drift: {left['path']} vs {right['path']}"
            assert left["fields"] == right["fields"], (
                f"{scen} span {left['path']} field drift: {left['fields']} vs {right['fields']}"
            )


def test_no_span_diffs_reported(comparison: dict) -> None:
    for entry in comparison["scenarios"]:
        diffs = entry.get("span_diffs", [])
        assert not diffs, f"scenario {entry['scenario']} had unexpected span diffs: {diffs[:3]}"


def test_digest_format_is_sha256_hex(comparison: dict) -> None:
    for entry in comparison["scenarios"]:
        d = entry["deterministic_digest_run_1"]
        assert isinstance(d, str) and len(d) == 64
        int(d, 16)  # must parse as hex
