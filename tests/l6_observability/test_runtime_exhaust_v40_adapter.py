from __future__ import annotations

import json
from pathlib import Path

from agentic_core.L6_observability.shadow_eval.adapters import (
    from_section_artifacts,
    validate_v40_shadow_exhaust,
)


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_artifacts(root: Path) -> None:
    common = {
        "run_id": "run-v40",
        "request_id": "req-v40",
        "trace_root": "trace-v40",
        "policy_hash": "policy-v40",
        "blueprint_hash": "blueprint-v40",
        "replay_key": "replay-v40",
        "generated_at_utc": "2026-06-13T00:00:00+00:00",
    }
    _write(root / "runtime_exhaust_bundle.json", {**common, "route_id": "route-v40"})
    _write(root / "exit_disposition_receipt.json", {**common, "x3_code": "X3D_ALLOW_FINISH"})
    _write(root / "x3_disposition.json", {"x3_code": "X3D_ALLOW_FINISH", "pass": True})
    _write(root / "route_contract.json", {**common, "route_id": "route-v40"})
    _write(root / "l2_output.json", {**common, "section_id": "summary"})


def test_v40_adapter_requires_non_missing_l5_certification_ref(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)
    raw = from_section_artifacts(tmp_path, tmp_path, section_id="summary")

    valid, gaps = validate_v40_shadow_exhaust(raw)

    assert valid is False
    assert "L5_CERT_REF_MISSING" in gaps


def test_v40_adapter_builds_valid_exhaust_when_required_refs_exist(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)
    raw = from_section_artifacts(
        tmp_path,
        tmp_path,
        section_id="summary",
        session_id="sess-v40",
        tenant_id="tenant-v40",
        l5_certification_ref="l5-cert-ref:v40",
    )

    valid, gaps = validate_v40_shadow_exhaust(raw)

    assert valid is True
    assert gaps == []
    assert raw["runtime_boundary_crossed"] is True
    assert raw["l5_certification_ref"] == "l5-cert-ref:v40"
