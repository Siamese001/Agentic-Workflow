"""W1.0 — rigor-critical gates must be C0 sidecar, retired with proof, or require runtime X2."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_product_shape_ssot import product_shape_gate_ids_for_lane
from tests.unit.apps_rg.section_rigor.gate_coverage_registry import (
    C0_SIDECAR_GATE_IDS,
    RETIRED_GATE_REFS,
    gate_accounting_status,
    is_gate_verdict_known,
    validate_retired_gate_ref,
)
from tests.unit.apps_rg.section_rigor.lane_registry import spec_for_lane

REPO_ROOT = Path(__file__).resolve().parents[4]
PROOF_ROOT = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_0e41a1c13cfe" / "lanes"


def _load_x2_gate_rows(lane: str) -> dict[str, dict]:
    path = PROOF_ROOT / lane / "x2_gate_outputs.json"
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = doc.get("gates") or []
    out: dict[str, dict] = {}
    for row in rows:
        if isinstance(row, dict) and row.get("gate_id"):
            out[str(row["gate_id"])] = row
    return out


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_all_critical_gates_accounted(lane: str) -> None:
    critical = spec_for_lane(lane).critical_gates
    shape_ids = set(product_shape_gate_ids_for_lane(lane))
    for gate_id in sorted(critical):
        status = gate_accounting_status(gate_id)
        assert status != "UNCLASSIFIED", f"{lane}:{gate_id}"
        if status == "REQUIRES_RUNTIME_X2" and gate_id not in shape_ids:
            # Universal/style gates are allowed outside product_shape SSOT list
            assert gate_id.startswith("x2_"), gate_id


def test_synthetic_unclassified_gate_red_path() -> None:
    assert gate_accounting_status("x2___synthetic_unregistered_gate___") == "UNCLASSIFIED"


def test_retired_refs_have_required_fields() -> None:
    for ref in RETIRED_GATE_REFS.values():
        validate_retired_gate_ref(ref)


def test_c0_sidecar_disjoint_from_retired() -> None:
    overlap = C0_SIDECAR_GATE_IDS & set(RETIRED_GATE_REFS)
    assert not overlap, f"C0/RETIRED overlap: {overlap}"


def test_missing_gate_verdict_is_unknown_red_path() -> None:
    assert not is_gate_verdict_known({"gate_id": "x2_json_parse_valid"})
    assert not is_gate_verdict_known(None)


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_emitted_x2_gates_have_known_verdict_when_fixture_present(lane: str) -> None:
    x2_by_id = _load_x2_gate_rows(lane)
    if not x2_by_id:
        pytest.skip(f"no x2 fixture for {lane}")
    missing_verdict: list[str] = []
    for gate_id, row in x2_by_id.items():
        if not is_gate_verdict_known(row):
            missing_verdict.append(gate_id)
    assert not missing_verdict, f"{lane}: missing GateVerdict pass field: {missing_verdict}"


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_stale_fixture_absent_non_runtime_gates_are_c0_or_retired(lane: str) -> None:
    """Gates absent from stale proof bundle: C0/RETIRED required; REQUIRES_RUNTIME_X2 may be stale-inventory only."""
    x2_by_id = _load_x2_gate_rows(lane)
    if not x2_by_id:
        pytest.skip(f"no x2 fixture for {lane}")
    unaccounted: list[str] = []
    for gate_id in spec_for_lane(lane).critical_gates:
        if gate_id in x2_by_id:
            continue
        status = gate_accounting_status(gate_id)
        if status in ("C0_SIDECAR", "RETIRED", "REQUIRES_RUNTIME_X2"):
            continue
        unaccounted.append(f"{gate_id}:{status}")
    assert not unaccounted, f"{lane}: unclassified absent-from-stale: {unaccounted}"


def test_rigor_gate_absent_from_x2_must_be_c0_or_retired_red_path() -> None:
    """Synthetic gate marker → UNCLASSIFIED (red-path registry)."""
    assert gate_accounting_status("x2___ghost_not_in_maps___") == "UNCLASSIFIED"
