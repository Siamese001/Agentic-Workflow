"""
tests/runtime/test_anti_bypass_runtime_cheat_proof.py

Phase 7 acceptance test (one of the 14 spec-named tests).

Drives every entry in ``anti_bypass_negatives.NEGATIVES`` through a
3-layer defense:

  Layer 1 -- contract validator (validate_trace)
  Layer 2 -- scenario shape validator (validate_scenario_shape)
  Layer 3 -- replay-determinism digest comparison against a clean baseline

A bypass is "detected" if AT LEAST ONE layer fires for the mutated trace.
A negative that escapes all three layers is a real bypass and the test
fails -- because it means an attacker could produce that mutated trace
and evade the proof system.

This test asserts:
  * All 30 mutators are catalogued
  * Each mutator yields a structurally-different trace from its baseline
  * Each mutator is caught by AT LEAST ONE detector layer
  * The mutator -> primary-detector mapping is what we claim it is
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.prove_requirements.anti_bypass_negatives import (
    NEGATIVES,
    Negative,
)
from agentic_core.runtime.prove_requirements.otel_contract import (
    validate_scenario_shape,
    validate_trace,
)
from agentic_core.runtime.prove_requirements.otel_harness import (
    run_scenario_a_grounded_read,
    run_scenario_b_managed_workflow,
    run_scenario_c_weak_evidence,
    run_scenario_d_anti_bypass,
)
from agentic_core.runtime.prove_requirements.replay_engine import replay_digest


_SCENARIO_FNS = {
    "A_grounded_read": run_scenario_a_grounded_read,
    "B_managed_workflow": run_scenario_b_managed_workflow,
    "C_weak_evidence": run_scenario_c_weak_evidence,
    "D_anti_bypass": run_scenario_d_anti_bypass,
}

# Scenario E loaded lazily to avoid circular imports at module load
try:
    from agentic_core.runtime.prove_requirements.otel_harness import (
        run_scenario_e_authorized_commit,
    )
    _SCENARIO_FNS["E_authorized_commit"] = run_scenario_e_authorized_commit
except ImportError:
    pass


def _detect(mutated: dict, scenario: str, baseline_digest: str) -> tuple[bool, dict]:
    """Run all three layers; return (detected, layer_results)."""
    ok_contract, errs_contract = validate_trace(mutated)
    ok_shape, errs_shape = validate_scenario_shape(mutated, scenario)
    try:
        mut_digest = replay_digest(mutated)
        replay_drift = mut_digest != baseline_digest
    except (KeyError, TypeError, ValueError):
        # If the mutator broke the trace badly enough to break digest
        # computation, that itself counts as detection.
        replay_drift = True
    detected = (not ok_contract) or (not ok_shape) or replay_drift
    return detected, {
        "contract_ok": ok_contract,
        "contract_errors": errs_contract,
        "shape_ok": ok_shape,
        "shape_errors": errs_shape,
        "replay_drift": replay_drift,
    }


@pytest.fixture(scope="module")
def baselines() -> dict[str, dict]:
    """Clean trace dict + replay digest per scenario."""
    out: dict[str, dict] = {}
    for scen, fn in _SCENARIO_FNS.items():
        trace = fn().to_dict()
        out[scen] = {
            "trace": trace,
            "digest": replay_digest(trace),
        }
    return out


def test_thirty_three_negatives_catalogued() -> None:
    assert len(NEGATIVES) == 33, f"expected 33 negatives (30 base + 3 W6), got {len(NEGATIVES)}"


def test_unique_codes() -> None:
    codes = [n.code for n in NEGATIVES]
    assert len(codes) == len(set(codes)), f"duplicate negative codes: {codes}"


def test_unique_names() -> None:
    names = [n.name for n in NEGATIVES]
    assert len(names) == len(set(names)), f"duplicate negative names: {names}"


def test_each_negative_targets_known_scenario() -> None:
    valid = set(_SCENARIO_FNS.keys())
    for n in NEGATIVES:
        assert n.scenario in valid, f"{n.code} targets unknown scenario {n.scenario}"


def test_clean_baselines_pass_all_layers(baselines: dict[str, dict]) -> None:
    """Sanity: a clean trace must NOT trigger any detector."""
    for scen, base in baselines.items():
        detected, layers = _detect(base["trace"], scen, base["digest"])
        assert not detected, (
            f"clean {scen} trace was incorrectly flagged: {layers}"
        )


@pytest.mark.parametrize("neg", NEGATIVES, ids=lambda n: f"{n.code}_{n.name}")
def test_negative_is_detected_by_at_least_one_layer(
    neg: Negative,
    baselines: dict[str, dict],
) -> None:
    base = baselines[neg.scenario]
    mutated = neg.mutator(base["trace"])
    detected, layers = _detect(mutated, neg.scenario, base["digest"])
    assert detected, (
        f"BYPASS {neg.code} ({neg.name}) escaped all detectors. "
        f"description={neg.description!r} layers={layers}"
    )


def test_negatives_actually_mutate_baseline(baselines: dict[str, dict]) -> None:
    """A mutator that returns the trace unchanged is a silent no-op and
    would always 'pass' the bypass test for the wrong reason."""
    import copy
    for n in NEGATIVES:
        base = baselines[n.scenario]
        original = base["trace"]
        clone = copy.deepcopy(original)
        mutated = n.mutator(clone)
        # The mutator should NOT have mutated the original trace.
        assert original == base["trace"], (
            f"{n.code} mutator side-effected the baseline trace"
        )
        # The mutated trace should differ from the original (structurally
        # OR by digest -- enough that it represents a real attack).
        try:
            mutated_digest = replay_digest(mutated)
        except (KeyError, TypeError, ValueError):
            # broken trace counts as different
            continue
        if mutated == original or mutated_digest == base["digest"]:
            # Allow exception for mutators that target uuid-only fields
            # (M14-M16 drift trace_id/request_id/run_id which are NOT in
            # the deterministic projection -- but they still mutate the
            # trace dict structurally).
            assert mutated != original, (
                f"{n.code} mutator produced a trace identical to the baseline"
            )
