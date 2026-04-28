"""Tier 2 Batch A fixture invariants.

Static, deterministic checks. Asserts the four OTEL reference modules
and two replay fixture pairs created for Batch A satisfy the contract
declared in TIER2_REMAINING_PROOF_GAPS.md and the bootstrap discipline.

This test does NOT execute replay machinery, does NOT emit OTEL spans,
does NOT run a proof harness, and does NOT mutate runtime state. It
inspects on-disk metadata only.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Mapping

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- #
# OTEL reference modules                                                      #
# --------------------------------------------------------------------------- #

OTEL_MODULE_TABLE: Mapping[str, tuple[str, str]] = {
    "agentic_core.runtime.prove_requirements.tier2_otel_refs.l2_ptc_sandbox_spans": (
        "REQ-L2-PTC-SANDBOX-001",
        "PTC_SANDBOX_REQUIRED",
    ),
    "agentic_core.runtime.prove_requirements.tier2_otel_refs.l2_verify_then_execute_spans": (
        "REQ-L2-VERIFY-THEN-EXECUTE-001",
        "VERIFY_THEN_EXECUTE_REQUIRED",
    ),
    "agentic_core.runtime.prove_requirements.tier2_otel_refs.pa_provider_aware_render_spans": (
        "REQ-PA-PROVIDER-AWARE-RENDER-001",
        "PROVIDER_TEMPLATE_NOT_DECLARED",
    ),
    "agentic_core.runtime.prove_requirements.tier2_otel_refs.pa_airlock_security_spans": (
        "REQ-PA-AIRLOCK-SECURITY-001",
        "PA_AIRLOCK_SECURITY_BLOCKED",
    ),
}


@pytest.mark.parametrize(
    "module_name,expected",
    list(OTEL_MODULE_TABLE.items()),
    ids=[m.rsplit(".", 1)[-1] for m in OTEL_MODULE_TABLE],
)
def test_otel_ref_module_metadata(module_name: str, expected: tuple[str, str]) -> None:
    expected_req_id, expected_efr = expected
    mod = importlib.import_module(module_name)

    assert getattr(mod, "STEP1_REQ_ID") == expected_req_id
    assert getattr(mod, "EXPECTED_FAIL_REASON") == expected_efr

    span_names = getattr(mod, "SPAN_NAMES")
    assert isinstance(span_names, tuple) and span_names, "SPAN_NAMES must be a non-empty tuple"
    assert all(isinstance(s, str) and s for s in span_names), "all SPAN_NAMES must be non-empty str"
    assert len(set(span_names)) == len(span_names), "SPAN_NAMES must be unique"


def test_otel_ref_modules_emit_no_spans() -> None:
    """Static guard: OTEL ref modules must not import an exporter or emit spans.

    Cheap text-level inspection. No span emission paths allowed.
    """
    forbidden_substrings = (
        "opentelemetry.sdk",
        "trace.get_tracer(",
        "tracer.start_as_current_span",
        "tracer.start_span",
        ".set_attribute(",
        ".add_event(",
        ".end()",
    )
    refs_dir = REPO_ROOT / "agentic_core" / "runtime" / "prove_requirements" / "tier2_otel_refs"
    files = sorted(p for p in refs_dir.glob("*.py") if p.name != "__init__.py")
    assert files, "expected Tier 2 OTEL ref modules to exist on disk"
    for path in files:
        text = path.read_text(encoding="utf-8")
        for needle in forbidden_substrings:
            assert needle not in text, f"{path.name} must not contain '{needle}'"


# --------------------------------------------------------------------------- #
# Replay fixture pairs                                                        #
# --------------------------------------------------------------------------- #

REPLAY_PAIRS: Mapping[str, tuple[str, str, str]] = {
    "K_l6_signal_fusion_rca": (
        "REQ-L6-SIGNAL-FUSION-RCA-001",
        "L6_SIGNAL_FUSION_FROM_UNSEALED_RECORD_BLOCKED",
        "scenario_K_l6_signal_fusion_rca",
    ),
    "L_e2e_mutation_boundary": (
        "REQ-E2E-MUTATION-BOUNDARY-001",
        "E2E_MUTATION_BOUNDARY_FAULT_MISSING",
        "scenario_L_e2e_mutation_boundary",
    ),
}


@pytest.mark.parametrize("scenario_key,expected", list(REPLAY_PAIRS.items()))
def test_replay_pair_invariants(scenario_key: str, expected: tuple[str, str, str]) -> None:
    expected_req_id, expected_efr, expected_scenario_id = expected
    base = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof" / "replay"
    run_1 = base / f"replay_{scenario_key}_run_1.json"
    run_2 = base / f"replay_{scenario_key}_run_2.json"

    assert run_1.is_file() and run_2.is_file()

    d1 = json.loads(run_1.read_text(encoding="utf-8"))
    d2 = json.loads(run_2.read_text(encoding="utf-8"))

    for d, idx in ((d1, 1), (d2, 2)):
        for field in ("step1_req_id", "scenario_id", "expected_fail_reason", "invariant_digest", "replay_run_id"):
            assert field in d, f"missing field {field} in run_{idx}"
        assert d["step1_req_id"] == expected_req_id
        assert d["scenario_id"] == expected_scenario_id
        assert d["expected_fail_reason"] == expected_efr
        assert d["replay_run_index"] == idx
        assert d["invariant_digest"].startswith("sha256:")

    # Determinism contract: matching invariant_digest across run_1 and run_2.
    assert d1["invariant_digest"] == d2["invariant_digest"]
    # Run IDs must differ.
    assert d1["replay_run_id"] != d2["replay_run_id"]


# --------------------------------------------------------------------------- #
# Tier 2 mapping wiring                                                       #
# --------------------------------------------------------------------------- #


def test_tier2_metadata_wires_batch_a_refs() -> None:
    from agentic_core.runtime.prove_requirements import tier2_step1_metadata as t2

    otel = t2.OTEL_SPAN_REFERENCES
    replay = t2.REPLAY_REFERENCES

    # OTEL-only rows now reference the dedicated Batch A modules.
    assert any("l2_ptc_sandbox_spans.py" in p for p in otel["REQ-L2-PTC-SANDBOX-001"])
    assert any("l2_verify_then_execute_spans.py" in p for p in otel["REQ-L2-VERIFY-THEN-EXECUTE-001"])
    assert any("pa_provider_aware_render_spans.py" in p for p in otel["REQ-PA-PROVIDER-AWARE-RENDER-001"])
    assert any("pa_airlock_security_spans.py" in p for p in otel["REQ-PA-AIRLOCK-SECURITY-001"])

    # Replay-only rows now reference the K / L deterministic pairs.
    assert any("replay_K_l6_signal_fusion_rca_run_1.json" in p for p in replay["REQ-L6-SIGNAL-FUSION-RCA-001"])
    assert any("replay_K_l6_signal_fusion_rca_run_2.json" in p for p in replay["REQ-L6-SIGNAL-FUSION-RCA-001"])
    assert any("replay_L_e2e_mutation_boundary_run_1.json" in p for p in replay["REQ-E2E-MUTATION-BOUNDARY-001"])
    assert any("replay_L_e2e_mutation_boundary_run_2.json" in p for p in replay["REQ-E2E-MUTATION-BOUNDARY-001"])
