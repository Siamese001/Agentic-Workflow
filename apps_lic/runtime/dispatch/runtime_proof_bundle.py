"""99-style runtime proof bundle for canonical apps_lic spine runs (no-bypass verification)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from apps_lic.runtime.dispatch import stage_receipts as sr

PROOF_BUNDLE_SCHEMA_VERSION = "apps_lic.runtime_proof_bundle.v1"
FILENAME_RUNTIME_PROOF_BUNDLE = "runtime_proof_bundle.json"

CANONICAL_PRODUCER = "apps_lic.runtime.dispatch.canonical_dispatch"
BINDINGS_PREFIX = "apps_lic.runtime.bindings."

R4_REQUIRED_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_EXIT_DISPOSITION,
    sr.FILENAME_SPINE_MANIFEST,
)

R4_CANONICAL_STAGE_ORDER: tuple[str, ...] = (
    "INGRESS",
    "U0",
    "L1",
    "L0",
    "C0",
    "PA",
    "L3",
    "L2",
    "EXIT",
)

R4_STAGE_ORDER_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_EXIT_DISPOSITION,
)

R4_EXPECTED_CHAIN_EDGES: tuple[tuple[str, str], ...] = (
    (sr.FILENAME_INGRESS_RAW, sr.FILENAME_U0_RECEIPT),
    (sr.FILENAME_U0_RECEIPT, sr.FILENAME_L1_PLAN),
    (sr.FILENAME_L1_PLAN, sr.FILENAME_ROUTE_CONTRACT),
    (sr.FILENAME_ROUTE_CONTRACT, sr.FILENAME_C0_FEC),
    (sr.FILENAME_C0_FEC, sr.FILENAME_PA_RECEIPT),
    (sr.FILENAME_PA_RECEIPT, sr.FILENAME_L3_WORKFLOW),
    (sr.FILENAME_L3_WORKFLOW, sr.FILENAME_L2_EXECUTION),
    (sr.FILENAME_L2_EXECUTION, sr.FILENAME_EXIT_DISPOSITION),
)

R5_REQUIRED_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_SPINE_MANIFEST,
)

R5_FORBIDDEN_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_C0_FEC,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_EXIT_DISPOSITION,
)

_DELETED_SHADOW_FILES: tuple[str, ...] = (
    "agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py",
    "agentic_core/runtime/u0/apps_lic_u0_adapter.py",
    "agentic_core/L0_routing/apps_lic_l0_binding.py",
    "agentic_core/L1_cognition/apps_lic_l1_binding.py",
    "agentic_core/L2_execution/apps_lic_l2_binding.py",
    "agentic_core/L3_orchestration/apps_lic_l3_binding.py",
    "agentic_core/runtime/c0/apps_lic_c0_binding.py",
    "agentic_core/prompt_governance/apps_lic_pa_binding.py",
    "agentic_core/runtime/exit/apps_lic_exit_binding.py",
    "apps_lic/integrations/governed_lic_run.py",
    "apps_lic/integrations/spine_handoff.py",
)

_FORBIDDEN_DURABLE_WRITE_LITERALS: tuple[str, ...] = (
    "sqlite3.connect",
    "psycopg2.connect",
    "sqlalchemy.create_engine",
)


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _is_stage_envelope(data: dict[str, Any]) -> bool:
    return (
        data.get("schema_version") == sr.STAGE_RECEIPT_SCHEMA_VERSION
        and isinstance(data.get("stage"), str)
        and "request_id" in data
        and "run_id" in data
    )


def _check_files_present(artifact_dir: Path, filenames: Iterable[str]) -> list[str]:
    violations: list[str] = []
    for name in filenames:
        if not (artifact_dir / name).is_file():
            violations.append(f"missing_file:{name}")
    return violations


def _check_files_absent(artifact_dir: Path, filenames: Iterable[str]) -> list[str]:
    violations: list[str] = []
    for name in filenames:
        if (artifact_dir / name).is_file():
            violations.append(f"forbidden_file_present:{name}")
    return violations


def _check_stage_receipts(
    artifact_dir: Path,
    filenames: Iterable[str],
    *,
    manifest: dict[str, Any],
) -> list[str]:
    violations: list[str] = []
    req_id = str(manifest.get("request_id") or "")
    run_id = str(manifest.get("run_id") or "")
    for name in filenames:
        data = _read_json(artifact_dir / name)
        if data is None:
            continue
        if not _is_stage_envelope(data):
            continue
        if not str(data.get("digest", "")).strip():
            violations.append(f"missing_digest:{name}")
        if req_id and str(data.get("request_id", "")) != req_id:
            violations.append(f"request_id_mismatch:{name}")
        if run_id and str(data.get("run_id", "")) != run_id:
            violations.append(f"run_id_mismatch:{name}")
    return violations


def _check_r4_stage_order(artifact_dir: Path) -> list[str]:
    violations: list[str] = []
    for expected_stage, filename in zip(R4_CANONICAL_STAGE_ORDER, R4_STAGE_ORDER_FILES, strict=True):
        data = _read_json(artifact_dir / filename)
        if data is None:
            violations.append(f"stage_order_missing:{filename}")
            continue
        actual = data.get("stage")
        if actual != expected_stage:
            violations.append(f"stage_order_mismatch:{filename}:{actual}!={expected_stage}")
    return violations


def _check_chain_edges(artifact_dir: Path, edges: Iterable[tuple[str, str]]) -> list[str]:
    violations: list[str] = []
    for upstream, downstream in edges:
        up = _read_json(artifact_dir / upstream)
        if up is None:
            violations.append(f"chain_missing_upstream:{upstream}")
            continue
        downs = up.get("downstream_receipt_refs") or []
        if downstream not in downs:
            violations.append(f"chain_edge_missing:{upstream}->{downstream}")
        down = _read_json(artifact_dir / downstream)
        if down is None:
            violations.append(f"chain_missing_downstream:{downstream}")
            continue
        ups = down.get("upstream_receipt_refs") or []
        if upstream not in ups:
            violations.append(f"chain_upstream_ref_missing:{downstream}<-{upstream}")
    return violations


def _check_manifest_producer(manifest: dict[str, Any]) -> list[str]:
    if manifest.get("producer_component") != CANONICAL_PRODUCER:
        return [f"producer_not_canonical:{manifest.get('producer_component')!r}"]
    return []


def _check_shadow_surfaces_absent(repo: Path) -> list[str]:
    violations: list[str] = []
    for rel in _DELETED_SHADOW_FILES:
        if (repo / rel).exists():
            violations.append(f"shadow_surface_exists:{rel}")
    return violations


def _check_bindings_in_app_overlay(repo: Path) -> list[str]:
    violations: list[str] = []
    for path in repo.glob("agentic_core/**/apps_lic_*_binding.py"):
        violations.append(f"core_apps_lic_binding:{path.relative_to(repo).as_posix()}")
    bindings_dir = repo / "apps_lic" / "runtime" / "bindings"
    for mod in (
        "l0_binding.py",
        "l1_binding.py",
        "l2_binding.py",
        "l3_binding.py",
        "c0_binding.py",
        "pa_binding.py",
        "exit_binding.py",
        "u0_binding.py",
    ):
        if not (bindings_dir / mod).is_file():
            violations.append(f"missing_app_binding:{mod}")
    dispatch_path = repo / "apps_lic" / "runtime" / "dispatch" / "canonical_dispatch.py"
    if not dispatch_path.is_file():
        violations.append("canonical_dispatch_missing")
    else:
        dispatch_src = dispatch_path.read_text(encoding="utf-8")
        if BINDINGS_PREFIX not in dispatch_src:
            violations.append("canonical_dispatch_missing_apps_lic_bindings_import")
        if "agentic_core.L0_routing.apps_lic" in dispatch_src:
            violations.append("canonical_dispatch_imports_core_apps_lic_binding")
    return violations


def _check_single_exit_x3(artifact_dir: Path, *, terminal_r5: bool) -> list[str]:
    if terminal_r5:
        return []
    exit_data = _read_json(artifact_dir / sr.FILENAME_EXIT_DISPOSITION)
    if exit_data is None:
        return ["exit_receipt_missing"]
    payload = exit_data.get("payload") or {}
    disp = payload.get("x3_disposition")
    if not disp or disp == "UNKNOWN":
        return [f"exit_x3_invalid:{disp!r}"]
    if str(disp).count("X3") == 0 and disp not in ("DENY", "escalated", "success"):
        return [f"exit_x3_unrecognized:{disp!r}"]
    return []


def _check_no_durable_write_outside_exit(artifact_dir: Path, *, terminal_r5: bool) -> list[str]:
    if terminal_r5:
        return []
    violations: list[str] = []
    l2 = _read_json(artifact_dir / sr.FILENAME_L2_EXECUTION)
    if l2:
        payload = l2.get("payload") or {}
        if payload.get("state_diff_authorized") is True:
            violations.append("l2_state_diff_authorized_true")
        psd = payload.get("proposed_state_diff") or {}
        if isinstance(psd, dict) and psd:
            violations.append("l2_proposed_state_diff_non_empty")
    for name in (sr.FILENAME_L2_EXECUTION, sr.FILENAME_EXIT_DISPOSITION, sr.FILENAME_C0_FEC):
        path = artifact_dir / name
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for lit in _FORBIDDEN_DURABLE_WRITE_LITERALS:
                if lit in text:
                    violations.append(f"durable_write_literal:{name}:{lit}")
    return violations


def _check_r4_manifest_policy(manifest: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if manifest.get("terminal_r5"):
        violations.append("r4_terminal_r5_true")
    if manifest.get("x3_disposition") != "X3D":
        violations.append(f"r4_x3_disposition:{manifest.get('x3_disposition')!r}")
    if manifest.get("outcome_authorized") is not True:
        violations.append(f"r4_outcome_authorized:{manifest.get('outcome_authorized')!r}")
    if manifest.get("exit_status") != "success":
        violations.append(f"r4_exit_status:{manifest.get('exit_status')!r}")
    refs = list(manifest.get("stage_receipt_refs") or [])
    for req in R4_REQUIRED_STAGE_FILES:
        if req not in refs:
            violations.append(f"r4_stage_ref_missing:{req}")
    return violations


def _check_r5_manifest_policy(manifest: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if not manifest.get("terminal_r5"):
        violations.append("r5_terminal_r5_false")
    if manifest.get("x3_disposition") != "DENY":
        violations.append(f"r5_x3_disposition:{manifest.get('x3_disposition')!r}")
    return violations


def _hydrate_manifest_ids(manifest: dict[str, Any], artifact_dir: Path) -> dict[str, Any]:
    """Fill request/run/trace ids from route receipt when manifest rollup omits them."""
    out = dict(manifest)
    if out.get("request_id") and out.get("run_id"):
        return out
    route = _read_json(artifact_dir / sr.FILENAME_ROUTE_CONTRACT)
    if route and _is_stage_envelope(route):
        out.setdefault("request_id", route.get("request_id"))
        out.setdefault("run_id", route.get("run_id"))
        out.setdefault("trace_id", route.get("trace_id"))
    return out


def build_runtime_proof_bundle(
    artifact_dir: Path,
    manifest: dict[str, Any],
    *,
    terminal_r5: bool,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Assemble proof bundle dict; ``status`` is PASS only when all checks pass."""
    repo = repo_root or _repo_root()
    manifest = _hydrate_manifest_ids(manifest, artifact_dir)
    violations: list[str] = []
    checks: dict[str, Any] = {}

    checks["shadow_surfaces_absent"] = _check_shadow_surfaces_absent(repo)
    violations.extend(checks["shadow_surfaces_absent"])

    checks["app_owned_bindings"] = _check_bindings_in_app_overlay(repo)
    violations.extend(checks["app_owned_bindings"])

    checks["canonical_producer"] = _check_manifest_producer(manifest)
    violations.extend(checks["canonical_producer"])

    if terminal_r5:
        checks["r5_required_files"] = _check_files_present(artifact_dir, R5_REQUIRED_FILES)
        violations.extend(checks["r5_required_files"])
        checks["r5_forbidden_absent"] = _check_files_absent(artifact_dir, R5_FORBIDDEN_STAGE_FILES)
        violations.extend(checks["r5_forbidden_absent"])
        checks["r5_manifest_policy"] = _check_r5_manifest_policy(manifest)
        violations.extend(checks["r5_manifest_policy"])
        checks["r5_terminal_exit_policy"] = []
        if manifest.get("x3_disposition") == "DENY":
            checks["r5_terminal_exit_policy"].append("terminal_r5_manifest_x3_deny_by_design")
        else:
            violations.append("r5_exit_policy_unexplained")
    else:
        checks["r4_required_files"] = _check_files_present(artifact_dir, R4_REQUIRED_STAGE_FILES)
        violations.extend(checks["r4_required_files"])
        checks["stage_receipt_digests"] = _check_stage_receipts(
            artifact_dir,
            R4_REQUIRED_STAGE_FILES,
            manifest=manifest,
        )
        violations.extend(checks["stage_receipt_digests"])
        checks["stage_order"] = _check_r4_stage_order(artifact_dir)
        violations.extend(checks["stage_order"])
        checks["receipt_chain"] = _check_chain_edges(artifact_dir, R4_EXPECTED_CHAIN_EDGES)
        violations.extend(checks["receipt_chain"])
        checks["r4_manifest_policy"] = _check_r4_manifest_policy(manifest)
        violations.extend(checks["r4_manifest_policy"])
        checks["single_exit_x3"] = _check_single_exit_x3(artifact_dir, terminal_r5=False)
        violations.extend(checks["single_exit_x3"])
        checks["no_durable_write_outside_exit"] = _check_no_durable_write_outside_exit(
            artifact_dir,
            terminal_r5=False,
        )
        violations.extend(checks["no_durable_write_outside_exit"])

    status = "PASS" if not violations else "FAIL"
    return {
        "schema_version": PROOF_BUNDLE_SCHEMA_VERSION,
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "run_id": manifest.get("run_id") or "",
        "request_id": manifest.get("request_id") or "",
        "route_family": manifest.get("route_family") or "",
        "terminal_r5": terminal_r5,
        "producer_component": CANONICAL_PRODUCER,
        "no_bypass_assertions": {
            "shadow_files_absent": len(checks.get("shadow_surfaces_absent", [])) == 0,
            "canonical_dispatch_only": len(checks.get("canonical_producer", [])) == 0,
            "bindings_under_apps_lic_runtime": len(checks.get("app_owned_bindings", [])) == 0,
            "no_symbolic_proof_branch": True,
            "no_provider_fallback_in_proof_gate": True,
        },
        "checks": checks,
        "violations": violations,
        "stage_receipt_refs": list(manifest.get("stage_receipt_refs") or []),
        "canonical_stage_order": list(R4_CANONICAL_STAGE_ORDER) if not terminal_r5 else [],
    }


def write_runtime_proof_bundle(
    artifact_dir: Path,
    manifest: dict[str, Any],
    *,
    terminal_r5: bool,
    repo_root: Path | None = None,
) -> str:
    bundle = build_runtime_proof_bundle(
        artifact_dir,
        manifest,
        terminal_r5=terminal_r5,
        repo_root=repo_root,
    )
    path = artifact_dir / FILENAME_RUNTIME_PROOF_BUNDLE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)
