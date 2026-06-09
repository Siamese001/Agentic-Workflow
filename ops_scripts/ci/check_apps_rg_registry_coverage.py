#!/usr/bin/env python3
"""CI gate: apps_rg registry coverage against canonical SSOTs.

Checks the non-numeric registry families from
``apps-rg-contract-registry-ssot-drift-a4f1c8`` W4:

- generated lane registries cover ``GENERATED_LANES``
- proof judge rosters derive from ``section_judge_policy``
- advertised product-shape X2 gates are emitted at runtime
- proof-source literals are not retyped in drift-prone product-code files

Bypass: ``APPS_RG_REGISTRY_COVERAGE_BYPASS=1``
Advisory: ``APPS_RG_REGISTRY_COVERAGE_ADVISORY=1``
"""

from __future__ import annotations

import ast
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.judges.graph_skills_x1d_rubric_contract import LANE_RUBRIC_MODULES
from apps_rg.runtime.judges.x1d_judge_transport_contract import PROOF_JUDGE_PROVIDER_KEYS
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.section_judge_policy import (
    REQUIRED_JUDGE_PROVIDER_KEYS,
    all_canonical_section_policies,
)
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape
from apps_rg.runtime.sections.section_x2_x1d_contract import (
    all_lane_x2_x1d_specs,
    extract_runtime_x2_gate_ids,
)
from apps_rg.runtime.x1d_judge_policy import APPS_RG_E2E_DEFAULT_X1D_JUDGES

EXPECTED_PROOF_SOURCE = "augmented_skills_graph"
ARTIFACT = REPO_ROOT / "artifacts" / "ci" / "apps_rg_registry_coverage.json"
ALIGNMENT_MATRIX = (
    REPO_ROOT
    / "artifacts"
    / "apps_rg"
    / "prompt_authority"
    / "x2_x1d_alignment_matrix.json"
)
ALLOWED_NON_GENERATED_ALIGNMENT_SECTIONS = frozenset(
    {"education", "certifications", "early_career"}
)
PROOF_SOURCE_LITERAL_SCAN_PATHS: tuple[Path, ...] = (
    REPO_ROOT / "apps_rg" / "runtime" / "validators" / "proof_pool_source_fact_validation.py",
    REPO_ROOT / "apps_rg" / "fact_inventory" / "competencies_graph_skills_proof_pool.py",
    REPO_ROOT / "apps_rg" / "runtime" / "product_evidence_authority.py",
    REPO_ROOT / "apps_rg" / "runtime" / "evidence" / "canonical_section_evidence_set.py",
)


@dataclass(frozen=True)
class RegistryCoverageViolation:
    family: str
    code: str
    detail: str
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "family": self.family,
            "code": self.code,
            "detail": self.detail,
            "path": self.path,
        }


def _csv_tuple(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in str(raw or "").split(",") if part.strip())


def _set_gap(
    *,
    family: str,
    registry_name: str,
    actual: Iterable[str],
    expected: Iterable[str],
    path: str = "",
    allowed_extra: Iterable[str] = (),
) -> list[RegistryCoverageViolation]:
    actual_set = set(actual)
    expected_set = set(expected)
    allowed_extra_set = set(allowed_extra)
    out: list[RegistryCoverageViolation] = []
    missing = sorted(expected_set - actual_set)
    if missing:
        out.append(
            RegistryCoverageViolation(
                family,
                "registry_missing_ssot_keys",
                f"{registry_name} missing SSOT keys: {missing}",
                path,
            )
        )
    unexpected = sorted(actual_set - expected_set - allowed_extra_set)
    if unexpected:
        out.append(
            RegistryCoverageViolation(
                family,
                "registry_unexpected_keys",
                f"{registry_name} has keys outside SSOT: {unexpected}",
                path,
            )
        )
    return out


def _alignment_section_ids(path: Path = ALIGNMENT_MATRIX) -> tuple[str, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(str(row.get("section_id") or "") for row in data.get("sections") or [])


def audit_lane_registry_coverage(
    *,
    generated_lanes: Sequence[str] = GENERATED_LANES,
    lane_spec_ids: Sequence[str] | None = None,
    alignment_ids: Sequence[str] | None = None,
    rubric_lane_ids: Sequence[str] | None = None,
    policy_section_ids: Sequence[str] | None = None,
) -> list[RegistryCoverageViolation]:
    expected = tuple(generated_lanes)
    specs = (
        tuple(spec.section_id for spec in all_lane_x2_x1d_specs())
        if lane_spec_ids is None
        else tuple(lane_spec_ids)
    )
    alignment = _alignment_section_ids() if alignment_ids is None else tuple(alignment_ids)
    rubric = (
        tuple(lane for _family, lane, _module in LANE_RUBRIC_MODULES)
        if rubric_lane_ids is None
        else tuple(rubric_lane_ids)
    )
    policies = (
        tuple(all_canonical_section_policies().keys())
        if policy_section_ids is None
        else tuple(policy_section_ids)
    )

    out: list[RegistryCoverageViolation] = []
    out.extend(
        _set_gap(
            family="lane_registry",
            registry_name="all_lane_x2_x1d_specs",
            actual=specs,
            expected=expected,
            path="apps_rg/runtime/sections/section_x2_x1d_contract.py",
        )
    )
    out.extend(
        _set_gap(
            family="lane_registry",
            registry_name="x2_x1d_alignment_matrix.sections",
            actual=alignment,
            expected=expected,
            allowed_extra=ALLOWED_NON_GENERATED_ALIGNMENT_SECTIONS,
            path="artifacts/apps_rg/prompt_authority/x2_x1d_alignment_matrix.json",
        )
    )
    out.extend(
        _set_gap(
            family="lane_registry",
            registry_name="LANE_RUBRIC_MODULES",
            actual=rubric,
            expected=expected,
            path="apps_rg/runtime/judges/graph_skills_x1d_rubric_contract.py",
        )
    )
    out.extend(
        _set_gap(
            family="lane_registry",
            registry_name="section_judge_policy",
            actual=policies,
            expected=expected,
            allowed_extra={"final_aggregate_resume"},
            path="apps_rg/runtime/section_judge_policy.py",
        )
    )
    return out


def audit_judge_registry_coverage(
    *,
    required_provider_keys: Sequence[str] = REQUIRED_JUDGE_PROVIDER_KEYS,
    harness_default_csv: str = APPS_RG_E2E_DEFAULT_X1D_JUDGES,
    transport_provider_keys: Sequence[str] = PROOF_JUDGE_PROVIDER_KEYS,
    policy_provider_map: Mapping[str, Sequence[str]] | None = None,
) -> list[RegistryCoverageViolation]:
    required = tuple(required_provider_keys)
    harness = _csv_tuple(harness_default_csv)
    transport = tuple(transport_provider_keys)
    policies = (
        {
            section: tuple(policy.required_judge_providers)
            for section, policy in all_canonical_section_policies().items()
            if policy.judge_required_for_proof
        }
        if policy_provider_map is None
        else {str(k): tuple(v) for k, v in policy_provider_map.items()}
    )
    policy_union = tuple(
        provider
        for provider in required
        if provider in {p for roster in policies.values() for p in roster}
    )

    out: list[RegistryCoverageViolation] = []
    if "anthropic_claude" in required:
        out.append(
            RegistryCoverageViolation(
                "judge_registry",
                "self_judge_in_required_roster",
                "REQUIRED_JUDGE_PROVIDER_KEYS includes anthropic_claude",
                "apps_rg/runtime/section_judge_policy.py",
            )
        )
    if harness != required:
        out.append(
            RegistryCoverageViolation(
                "judge_registry",
                "harness_default_not_policy_roster",
                f"APPS_RG_E2E_DEFAULT_X1D_JUDGES={harness!r}; expected {required!r}",
                "apps_rg/runtime/x1d_judge_policy.py",
            )
        )
    if transport != required:
        out.append(
            RegistryCoverageViolation(
                "judge_registry",
                "transport_roster_not_policy_roster",
                f"PROOF_JUDGE_PROVIDER_KEYS={transport!r}; expected {required!r}",
                "apps_rg/runtime/judges/x1d_judge_transport_contract.py",
            )
        )
    actual_policy_union = tuple(sorted({p for roster in policies.values() for p in roster}))
    expected_policy_union = tuple(sorted(required))
    if actual_policy_union != expected_policy_union:
        out.append(
            RegistryCoverageViolation(
                "judge_registry",
                "policy_panel_union_not_required_roster",
                f"policy union={actual_policy_union!r}; expected {expected_policy_union!r}",
                "apps_rg/runtime/section_judge_policy.py",
            )
        )
    for section, roster in policies.items():
        if "anthropic_claude" in roster:
            out.append(
                RegistryCoverageViolation(
                    "judge_registry",
                    "self_judge_in_section_policy",
                    f"{section} roster includes anthropic_claude",
                    "apps_rg/runtime/section_judge_policy.py",
                )
            )
        extra = sorted(set(roster) - set(required))
        if extra:
            out.append(
                RegistryCoverageViolation(
                    "judge_registry",
                    "section_policy_provider_not_in_required_roster",
                    f"{section} has providers outside required roster: {extra}",
                    "apps_rg/runtime/section_judge_policy.py",
                )
            )
    if not policy_union and required:
        out.append(
            RegistryCoverageViolation(
                "judge_registry",
                "no_policy_uses_required_roster",
                "No proof-required section policy uses the required proof roster",
                "apps_rg/runtime/section_judge_policy.py",
            )
        )
    return out


def audit_gate_advertise_emit_coverage(
    *,
    generated_lanes: Sequence[str] = GENERATED_LANES,
    advertised_gate_ids_by_lane: Mapping[str, Iterable[str]] | None = None,
    runtime_gate_ids_by_lane: Mapping[str, Iterable[str]] | None = None,
) -> list[RegistryCoverageViolation]:
    out: list[RegistryCoverageViolation] = []
    for lane in generated_lanes:
        advertised = (
            frozenset(advertised_gate_ids_by_lane[lane])
            if advertised_gate_ids_by_lane is not None
            else frozenset(section_product_shape(lane).required_gate_ids)
        )
        if runtime_gate_ids_by_lane is not None:
            runtime = frozenset(runtime_gate_ids_by_lane[lane])
            path = "<injected>"
        else:
            spec = next(spec for spec in all_lane_x2_x1d_specs() if spec.section_id == lane)
            runtime = extract_runtime_x2_gate_ids(
                x2_module_ref=spec.x2_module_ref,
                x2_run_function=spec.x2_run_function,
            )
            path = spec.x2_module_ref
        missing = sorted(advertised - runtime)
        if missing:
            out.append(
                RegistryCoverageViolation(
                    "gate_registry",
                    "advertised_gate_not_emitted",
                    f"{lane} advertises gates not emitted by runtime: {missing}",
                    path,
                )
            )
    return out


def _exact_string_literal_locations(path: Path, value: str) -> list[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == value:
            lines.append(int(getattr(node, "lineno", 0)))
    return sorted(line for line in lines if line > 0)


def audit_proof_source_literal_coverage(
    *,
    proof_source_value: str = PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    scan_paths: Sequence[Path] = PROOF_SOURCE_LITERAL_SCAN_PATHS,
) -> list[RegistryCoverageViolation]:
    out: list[RegistryCoverageViolation] = []
    if proof_source_value != EXPECTED_PROOF_SOURCE:
        out.append(
            RegistryCoverageViolation(
                "proof_source_registry",
                "proof_source_ssot_value_changed",
                f"PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH={proof_source_value!r}; expected {EXPECTED_PROOF_SOURCE!r}",
                "apps_rg/runtime/proof_pool_resolver.py",
            )
        )
    for path in scan_paths:
        p = Path(path)
        if not p.is_file():
            out.append(
                RegistryCoverageViolation(
                    "proof_source_registry",
                    "proof_source_scan_file_missing",
                    f"scan path missing: {p}",
                    str(p),
                )
            )
            continue
        hits = _exact_string_literal_locations(p, EXPECTED_PROOF_SOURCE)
        if hits:
            if p.is_absolute():
                try:
                    rel = p.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
                except ValueError:
                    rel = p.resolve().as_posix()
            else:
                rel = p.as_posix()
            out.append(
                RegistryCoverageViolation(
                    "proof_source_registry",
                    "proof_source_literal_retyped",
                    f"{rel} retypes {EXPECTED_PROOF_SOURCE!r} at lines {hits}; import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH",
                    rel,
                )
            )
    return out


def audit_apps_rg_registry_coverage() -> list[RegistryCoverageViolation]:
    out: list[RegistryCoverageViolation] = []
    out.extend(audit_lane_registry_coverage())
    out.extend(audit_judge_registry_coverage())
    out.extend(audit_gate_advertise_emit_coverage())
    out.extend(audit_proof_source_literal_coverage())
    return out


def _write_report(violations: Sequence[RegistryCoverageViolation]) -> None:
    payload = {
        "gate": "APPS-RG-REGISTRY-COVERAGE",
        "status": "PASS" if not violations else "FAIL",
        "generated_lanes": list(GENERATED_LANES),
        "required_judge_provider_keys": list(REQUIRED_JUDGE_PROVIDER_KEYS),
        "proof_source": PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        "violation_count": len(violations),
        "violations": [v.to_dict() for v in violations],
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    _ = argv
    if os.environ.get("APPS_RG_REGISTRY_COVERAGE_BYPASS", "").strip() == "1":
        print("BYPASS - APPS_RG_REGISTRY_COVERAGE_BYPASS=1")
        _write_report([])
        return 0
    advisory = os.environ.get("APPS_RG_REGISTRY_COVERAGE_ADVISORY", "").strip() == "1"
    violations = audit_apps_rg_registry_coverage()
    _write_report(violations)
    if not violations:
        print("OK - apps_rg registry coverage matches SSOT")
        print(f"artifact: {ARTIFACT.relative_to(REPO_ROOT).as_posix()}")
        return 0
    print(f"FAIL - apps_rg registry coverage drift ({len(violations)} violation(s))")
    for v in violations:
        print(f"  [{v.family}:{v.code}] {v.detail} ({v.path})")
    print(f"artifact: {ARTIFACT.relative_to(REPO_ROOT).as_posix()}")
    if advisory:
        print("ADVISORY - APPS_RG_REGISTRY_COVERAGE_ADVISORY=1 (exit 0)")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
