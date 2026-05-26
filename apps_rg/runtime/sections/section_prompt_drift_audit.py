"""Audit PA template YAML against section_product_shape_ssot (prompt/code drift guard)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from apps_rg.runtime.sections.section_product_shape_ssot import (
    SectionProductShape,
    all_generated_lane_shapes,
    section_product_shape,
)
from apps_rg.runtime.sections.section_prompt_authority_ssot import resolve_repo_template_path

_APPS_RG_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT = _APPS_RG_ROOT.parent
_CONTRACT_DIR = _APPS_RG_ROOT / "prompt_assembly" / "section_prompt_contracts"


@dataclass(frozen=True)
class DriftViolation:
    section_id: str
    kind: str
    detail: str
    path: str


def _repo_path(ref: str) -> Path:
    return resolve_repo_template_path(ref)


def _load_contract(section_id: str) -> dict[str, Any]:
    path = _CONTRACT_DIR / f"{section_id}.contract.yaml"
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return dict(data) if isinstance(data, dict) else {}


def _template_paths_for_section(shape: SectionProductShape) -> list[Path]:
    paths: list[Path] = []
    primary = _repo_path(shape.template_ref)
    if primary.is_file():
        paths.append(primary)
    stem = primary.stem
    pa_slots = primary.parent / f"{stem}.pa_slots.yaml"
    if pa_slots.is_file():
        paths.append(pa_slots)
    contract = _load_contract(shape.section_id)
    ref = str(contract.get("apps_rg_prompt_template_ref") or "").strip()
    if ref and ref != shape.template_ref:
        alt = _repo_path(ref)
        if alt.is_file() and alt not in paths:
            paths.append(alt)
    return paths


def audit_template_text(shape: SectionProductShape, text: str, *, path_label: str) -> list[DriftViolation]:
    violations: list[DriftViolation] = []
    for pattern in shape.forbidden_text_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(
                DriftViolation(
                    shape.section_id,
                    "forbidden_pattern",
                    f"matches forbidden /{pattern}/",
                    path_label,
                )
            )
    if shape.required_any_text_patterns:
        if not any(re.search(p, text, re.IGNORECASE) for p in shape.required_any_text_patterns):
            violations.append(
                DriftViolation(
                    shape.section_id,
                    "missing_required_any_pattern",
                    f"none matched (OR): {list(shape.required_any_text_patterns)}",
                    path_label,
                )
            )
    missing_all: list[str] = []
    for pattern in shape.required_all_text_patterns:
        if not re.search(pattern, text, re.IGNORECASE):
            missing_all.append(pattern)
    if missing_all:
        violations.append(
            DriftViolation(
                shape.section_id,
                "missing_required_all_patterns",
                f"not all matched (AND): {missing_all}",
                path_label,
            )
        )
    return violations


def audit_section_template(shape: SectionProductShape) -> list[DriftViolation]:
    violations: list[DriftViolation] = []
    paths = _template_paths_for_section(shape)
    if not paths:
        violations.append(
            DriftViolation(
                shape.section_id,
                "template_missing",
                f"no template file for ref {shape.template_ref}",
                str(shape.template_ref),
            )
        )
        return violations
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    label = ", ".join(str(p.relative_to(_REPO_ROOT)) for p in paths)
    violations.extend(audit_template_text(shape, combined, path_label=label))
    return violations


def audit_contract_template_ref(shape: SectionProductShape) -> list[DriftViolation]:
    contract = _load_contract(shape.section_id)
    ref = str(contract.get("apps_rg_prompt_template_ref") or "").strip()
    if ref != shape.template_ref:
        return [
            DriftViolation(
                shape.section_id,
                "contract_template_ref_mismatch",
                f"contract apps_rg_prompt_template_ref={ref!r} != ssot {shape.template_ref!r}",
                str(_CONTRACT_DIR / f"{shape.section_id}.contract.yaml"),
            )
        ]
    return []


def audit_critical_gates_registered(shape: SectionProductShape) -> list[DriftViolation]:
    try:
        from tests.unit.apps_rg.section_rigor.lane_registry import (  # guardian: allow-layer-violation -- drift audit cross-checks lane rigor SSOT in tests
            spec_for_lane,
        )
    except ImportError:
        return []
    try:
        spec = spec_for_lane(shape.section_id)
    except KeyError:
        return [
            DriftViolation(
                shape.section_id,
                "lane_registry_missing",
                "no LaneRigorSpec for section",
                "tests/unit/apps_rg/section_rigor/lane_registry.py",
            )
        ]
    missing = [g for g in shape.required_gate_ids if g not in spec.critical_gates]
    if missing:
        return [
            DriftViolation(
                shape.section_id,
                "critical_gate_not_registered",
                f"SSOT gates not in lane_registry critical_gates: {missing}",
                "tests/unit/apps_rg/section_rigor/lane_registry.py",
            )
        ]
    return []


def audit_section(shape: SectionProductShape) -> list[DriftViolation]:
    return (
        audit_section_template(shape)
        + audit_contract_template_ref(shape)
        + audit_critical_gates_registered(shape)
    )


def audit_all_generated_lanes() -> list[DriftViolation]:
    out: list[DriftViolation] = []
    for shape in all_generated_lane_shapes():
        out.extend(audit_section(shape))
    return out


def assert_zero_drift() -> None:
    violations = audit_all_generated_lanes()
    if violations:
        lines = [f"{v.section_id}:{v.kind}:{v.detail} ({v.path})" for v in violations]
        raise AssertionError("section prompt/product-shape drift:\n" + "\n".join(lines))


__all__ = [
    "DriftViolation",
    "assert_zero_drift",
    "audit_all_generated_lanes",
    "audit_section",
    "audit_section_template",
]
