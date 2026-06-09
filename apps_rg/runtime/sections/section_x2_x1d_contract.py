"""Per-lane X2 (deterministic) vs X1D (soft judge) contract audits for all GENERATED_LANES.

SSOT authority: ``section_product_shape_ssot`` gate IDs must match ``run_*_x2_gates`` emission,
alignment-matrix samples, and judge rubric bounds. Executive-summary synthesis/judge-packet
extensions live in ``executive_summary_x2_x1d_contract``.
"""

from __future__ import annotations

import ast
import importlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_product_shape_parity import judge_rubric_shape_constraints
from apps_rg.runtime.sections.section_product_shape_ssot import (
    RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
    RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS,
    RETIRED_UNIFY_BULLETS_X2_GATE_IDS,
    section_product_shape,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ALIGNMENT_MATRIX = _REPO_ROOT / "artifacts" / "apps_rg" / "prompt_authority" / "x2_x1d_alignment_matrix.json"

# Lane Python modules that invoke run_*_x2_gates in the product path.
_STATIC_LANE_MODULE_IMPORT: dict[str, str] = {
    "headline": "apps_rg.runtime.sections.headline_lane",
    "executive_summary": "apps_rg.runtime.sections.executive_summary_lane",
    "competencies": "apps_rg.runtime.sections.competencies_lane_execution",
    "unify_bullets": "apps_rg.runtime.sections.unify_bullets_lane",
    "unify_narrative": "apps_rg.runtime.sections.unify_narrative_lane",
    "ibm_bullets": "apps_rg.runtime.sections.ibm_bullets_lane",
    "ibm_narrative": "apps_rg.runtime.sections.ibm_narrative_lane_execution",
}
_ROLE_EPISODE_MODULE_IMPORT = "apps_rg.runtime.sections.role_episode_lane"


def _lane_module_imports() -> dict[str, str]:
    out = dict(_STATIC_LANE_MODULE_IMPORT)
    for lane in GENERATED_LANES:
        shape = section_product_shape(lane)
        if shape.x2_module_ref.endswith("/role_episode_lane.py"):
            out[lane] = _ROLE_EPISODE_MODULE_IMPORT
    missing = sorted(set(GENERATED_LANES) - set(out))
    if missing:
        raise RuntimeError(f"_LANE_MODULE_IMPORT missing GENERATED_LANES coverage: {missing}")
    return {lane: out[lane] for lane in GENERATED_LANES}


_LANE_MODULE_IMPORT: dict[str, str] = _lane_module_imports()

_X1D_WIRING_GATES: frozenset[str] = frozenset(
    {"x2_x1d_required_judges_present", "x2_x1d_schema_valid"}
)


@dataclass(frozen=True)
class LaneX2X1dSpec:
    section_id: str
    x2_module_ref: str
    x2_run_function: str
    lane_module_import: str
    x1d_judge_module_ref: str
    x2_gates_sample: tuple[str, ...]
    retired_gate_ids: frozenset[str]


@dataclass(frozen=True)
class X2X1dDriftViolation:
    section_id: str
    kind: str
    detail: str
    path: str = ""


def _module_from_repo_ref(ref: str) -> Any:
    mod_path = ref.replace("/", ".").removesuffix(".py")
    return importlib.import_module(mod_path)


def _discover_x2_run_function(x2_module: Any) -> str:
    candidates = [
        name
        for name in dir(x2_module)
        if name.startswith("run_") and name.endswith("_x2_gates") and callable(getattr(x2_module, name))
    ]
    if len(candidates) == 1:
        return candidates[0]
    if hasattr(x2_module, "run_x2_gates"):
        return "run_x2_gates"
    raise RuntimeError(f"cannot discover run_*_x2_gates in {x2_module.__name__}: {candidates}")


def _alignment_rows() -> dict[str, dict[str, Any]]:
    if not _ALIGNMENT_MATRIX.is_file():
        return {}
    data = json.loads(_ALIGNMENT_MATRIX.read_text(encoding="utf-8"))
    return {row["section_id"]: row for row in data.get("sections") or []}


def retired_gate_ids_for_section(section_id: str) -> frozenset[str]:
    retired: set[str] = set(RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS)
    if section_id == "executive_summary":
        retired |= RETIRED_EXEC_SUMMARY_X2_GATE_IDS
    if section_id == "unify_bullets":
        retired |= RETIRED_UNIFY_BULLETS_X2_GATE_IDS
    return frozenset(retired)


def lane_x2_x1d_spec(section_id: str) -> LaneX2X1dSpec:
    if section_id not in GENERATED_LANES:
        raise KeyError(f"not a generated lane: {section_id!r}")
    shape = section_product_shape(section_id)
    x2_module = _module_from_repo_ref(shape.x2_module_ref)
    row = _alignment_rows().get(section_id) or {}
    x1d_ref = str(row.get("x1d_judge_profile_ref") or "").strip()
    if not x1d_ref:
        raise KeyError(f"alignment matrix missing x1d_judge_profile_ref for {section_id}")
    x2_run_function = str(row.get("x2_run_function") or "").strip()
    if not x2_run_function:
        x2_run_function = _discover_x2_run_function(x2_module)
    if not callable(getattr(x2_module, x2_run_function, None)):
        raise KeyError(f"{shape.x2_module_ref} missing x2_run_function {x2_run_function!r} for {section_id}")
    samples = tuple(str(g).strip() for g in (row.get("x2_gates_sample") or ()) if str(g).strip())
    return LaneX2X1dSpec(
        section_id=section_id,
        x2_module_ref=shape.x2_module_ref,
        x2_run_function=x2_run_function,
        lane_module_import=_LANE_MODULE_IMPORT[section_id],
        x1d_judge_module_ref=x1d_ref,
        x2_gates_sample=samples,
        retired_gate_ids=retired_gate_ids_for_section(section_id),
    )


def all_lane_x2_x1d_specs() -> tuple[LaneX2X1dSpec, ...]:
    return tuple(lane_x2_x1d_spec(lane) for lane in GENERATED_LANES)


def _module_gate_id_constants(tree: ast.Module) -> dict[str, str]:
    """Map module-level names to gate_id strings (e.g. TEXT_COVERAGE_INTEGRITY_GATE_ID)."""
    consts: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        val = node.value
        if isinstance(val, ast.Constant) and isinstance(val.value, str) and val.value.startswith("x2_"):
            consts[node.targets[0].id] = val.value
    return consts


def _first_add_gate_id(arg0: ast.expr, consts: dict[str, str]) -> str | None:
    if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
        return arg0.value
    if isinstance(arg0, ast.Name) and arg0.id in consts:
        return consts[arg0.id]
    return None


def _helper_registered_x2_gate_ids(run_fn_src: str) -> frozenset[str]:
    """Gate IDs emitted via shared bullet/narrative mechanical helpers (W2/W3)."""
    out: set[str] = set()
    bullet_match = re.search(
        r"register_bullet_line_discipline_x2_gates\s*\([^)]*lane_prefix\s*=\s*[\"'](\w+)[\"']"
        r"[^)]*section_id\s*=\s*[\"'](\w+)[\"']",
        run_fn_src,
        re.DOTALL,
    )
    if bullet_match:
        prefix, section_id = bullet_match.group(1), bullet_match.group(2)
        out.update(
            {
                f"x2_{prefix}_bullet_no_embedded_newline",
                f"x2_{prefix}_bullet_single_thought",
                f"x2_{prefix}_bullet_no_paragraph_block",
            },
        )
        if section_id == "ibm_bullets":
            out.add("x2_ibm_narrative_slot_reservation")
    narrative_match = re.search(
        r"register_narrative_mechanical_x2_gates\s*\([^)]*lane_prefix\s*=\s*[\"'](\w+)[\"']",
        run_fn_src,
        re.DOTALL,
    )
    if narrative_match:
        prefix = narrative_match.group(1)
        out.update(
            {
                f"x2_{prefix}_narrative_exactly_one_sentence_mechanical",
                f"x2_{prefix}_narrative_forbidden_opener",
                f"x2_{prefix}_narrative_metric_cap",
                f"x2_{prefix}_narrative_bullet_overlap_threshold",
            },
        )
    return frozenset(out)


def extract_runtime_x2_gate_ids(
    *,
    x2_module_ref: str | None = None,
    x2_run_function: str | None = None,
    x2_module: Any | None = None,
) -> frozenset[str]:
    """AST-extract gate_id literals from a lane's ``run_*_x2_gates`` add(...) calls."""
    mod = x2_module if x2_module is not None else _module_from_repo_ref(str(x2_module_ref))
    run_fn = x2_run_function or _discover_x2_run_function(mod)
    if getattr(mod, "__name__", "") == "apps_rg.runtime.sections.role_episode_lane":
        role_gate_map = getattr(mod, "ROLE_EPISODE_X2_GATE_IDS_BY_RUN_FUNCTION", {})
        if run_fn in role_gate_map:
            return frozenset(role_gate_map[run_fn])
    src = Path(mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    consts = _module_gate_id_constants(tree)
    gate_ids: set[str] = set()
    run_fn_src = ""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == run_fn:
            run_fn_src = ast.get_source_segment(src, node) or ""
            for sub in ast.walk(node):
                if not isinstance(sub, ast.Call):
                    continue
                func = sub.func
                if isinstance(func, ast.Name) and func.id == "add" and sub.args:
                    gate_id = _first_add_gate_id(sub.args[0], consts)
                    if gate_id:
                        gate_ids.add(gate_id)
            break
    gate_ids |= set(_helper_registered_x2_gate_ids(run_fn_src))
    if run_fn == "run_x2_gates" and "executive_summary_x2" in getattr(mod, "__name__", ""):
        from apps_rg.runtime.validators.executive_summary_x2 import POST_X2_X1D_WIRING_GATE_IDS

        gate_ids |= set(POST_X2_X1D_WIRING_GATE_IDS)
    if not gate_ids:
        raise RuntimeError(f"{mod.__name__}.{run_fn}: no add('gate_id', ...) literals found")
    return frozenset(gate_ids)


def _load_x1d_rubrics(x1d_module_ref: str) -> list[tuple[str, str]]:
    mod = _module_from_repo_ref(x1d_module_ref)
    out: list[tuple[str, str]] = []
    for name in sorted(dir(mod)):
        if not name.endswith("_RUBRIC"):
            continue
        val = getattr(mod, name, None)
        if isinstance(val, str) and val.strip():
            out.append((name, val))
    return out


def _audit_lane_ssot_runtime(
    spec: LaneX2X1dSpec,
    runtime_gates: frozenset[str],
) -> list[X2X1dDriftViolation]:
    out: list[X2X1dDriftViolation] = []
    shape = section_product_shape(spec.section_id)
    shape_gates = frozenset(shape.required_gate_ids)
    missing = sorted(shape_gates - runtime_gates)
    if missing:
        out.append(
            X2X1dDriftViolation(
                spec.section_id,
                "ssot_gate_missing_in_runtime",
                f"product-shape gates not emitted by {spec.x2_run_function}: {missing}",
                spec.x2_module_ref,
            )
        )
    retired_hits = sorted(spec.retired_gate_ids & runtime_gates)
    if retired_hits:
        out.append(
            X2X1dDriftViolation(
                spec.section_id,
                "retired_gate_in_runtime",
                f"retired gates still emitted: {retired_hits}",
                spec.x2_module_ref,
            )
        )
    missing_wiring = sorted(_X1D_WIRING_GATES - runtime_gates)
    if missing_wiring:
        out.append(
            X2X1dDriftViolation(
                spec.section_id,
                "x1d_wiring_gate_missing",
                f"{spec.x2_run_function} missing orchestration gates: {missing_wiring}",
                spec.x2_module_ref,
            )
        )
    for sample in spec.x2_gates_sample:
        if sample not in runtime_gates:
            out.append(
                X2X1dDriftViolation(
                    spec.section_id,
                    "alignment_matrix_sample_missing",
                    f"x2_x1d_alignment_matrix sample {sample!r} not in {spec.x2_run_function}",
                    spec.x2_module_ref,
                )
            )
    return out


def _audit_lane_judge_rubric(spec: LaneX2X1dSpec) -> list[X2X1dDriftViolation]:
    # Executive summary rubrics live in executive_summary_judge_packet (checked in extended audit).
    if spec.section_id == "executive_summary":
        return []
    out: list[X2X1dDriftViolation] = []
    shape = section_product_shape(spec.section_id)
    for rubric_name, rubric in _load_x1d_rubrics(spec.x1d_judge_module_ref):
        issues = judge_rubric_shape_constraints(shape, rubric)
        if issues:
            out.append(
                X2X1dDriftViolation(
                    spec.section_id,
                    "judge_rubric_looser_than_ssot",
                    f"{rubric_name}: {issues}",
                    spec.x1d_judge_module_ref,
                )
            )
        retired_hits = sorted(g for g in spec.retired_gate_ids if g in rubric)
        if retired_hits:
            out.append(
                X2X1dDriftViolation(
                    spec.section_id,
                    "judge_rubric_retired_gate_id",
                    f"{rubric_name} mentions retired gates: {retired_hits}",
                    spec.x1d_judge_module_ref,
                )
            )
    if not _load_x1d_rubrics(spec.x1d_judge_module_ref):
        out.append(
            X2X1dDriftViolation(
                spec.section_id,
                "judge_rubric_missing",
                f"no *_RUBRIC constant in {spec.x1d_judge_module_ref}",
                spec.x1d_judge_module_ref,
            )
        )
    return out


def _audit_lane_execution_wiring(spec: LaneX2X1dSpec) -> list[X2X1dDriftViolation]:
    out: list[X2X1dDriftViolation] = []
    lane_mod = importlib.import_module(spec.lane_module_import)
    lane_src = Path(lane_mod.__file__).read_text(encoding="utf-8")
    x2_call = f"for g in {spec.x2_run_function}("
    role_shared_call = "run_role_episode_x2_gates(" if spec.lane_module_import == _ROLE_EPISODE_MODULE_IMPORT else ""
    if x2_call not in lane_src and (not role_shared_call or role_shared_call not in lane_src):
        out.append(
            X2X1dDriftViolation(
                spec.section_id,
                "lane_missing_x2_invocation",
                f"lane must call {x2_call}" if not role_shared_call else f"lane must call {role_shared_call}",
                spec.lane_module_import.replace(".", "/") + ".py",
            )
        )
    if "x1d_judges=" not in lane_src:
        out.append(
            X2X1dDriftViolation(
                spec.section_id,
                "lane_missing_x1d_wiring",
                f"lane must pass x1d_judges= into {spec.x2_run_function}",
                spec.lane_module_import.replace(".", "/") + ".py",
            )
        )
    return out


def audit_lane_x2_x1d_drift(section_id: str) -> list[X2X1dDriftViolation]:
    """Run generic X2/X1D drift checks for one generated lane."""
    spec = lane_x2_x1d_spec(section_id)
    runtime_gates = extract_runtime_x2_gate_ids(
        x2_module_ref=spec.x2_module_ref,
        x2_run_function=spec.x2_run_function,
    )
    violations: list[X2X1dDriftViolation] = []
    violations.extend(_audit_lane_ssot_runtime(spec, runtime_gates))
    violations.extend(_audit_lane_judge_rubric(spec))
    violations.extend(_audit_lane_execution_wiring(spec))
    if section_id == "executive_summary":
        from apps_rg.runtime.sections.executive_summary_x2_x1d_contract import (
            audit_executive_summary_extended_drift,
        )

        violations.extend(audit_executive_summary_extended_drift(runtime_gates))
    return violations


def audit_all_generated_lanes_x2_x1d_drift() -> list[X2X1dDriftViolation]:
    """Audit every GENERATED_LANE; empty list means aligned."""
    out: list[X2X1dDriftViolation] = []
    for lane in GENERATED_LANES:
        out.extend(audit_lane_x2_x1d_drift(lane))
    return out


def assert_all_generated_lanes_x2_x1d_contract() -> None:
    violations = audit_all_generated_lanes_x2_x1d_drift()
    if violations:
        lines = "\n".join(f"  [{v.section_id}:{v.kind}] {v.detail} ({v.path})" for v in violations)
        raise AssertionError(f"generated-lane X2/X1D contract drift:\n{lines}")


__all__ = [
    "LaneX2X1dSpec",
    "X2X1dDriftViolation",
    "all_lane_x2_x1d_specs",
    "assert_all_generated_lanes_x2_x1d_contract",
    "audit_all_generated_lanes_x2_x1d_drift",
    "audit_lane_x2_x1d_drift",
    "extract_runtime_x2_gate_ids",
    "lane_x2_x1d_spec",
    "retired_gate_ids_for_section",
]
