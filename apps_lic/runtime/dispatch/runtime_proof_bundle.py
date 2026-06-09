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
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_W5_VALIDATION_EXIT,
    sr.FILENAME_EXIT_DISPOSITION,
    sr.FILENAME_SPINE_MANIFEST,
)

R4_CANONICAL_STAGE_ORDER: tuple[str, ...] = (
    "INGRESS",
    "U0",
    "L1",
    "L0",
    "C0",
    "C0.3",
    "PA",
    "L3",
    "L2",
    "W4.CANDIDATES",
    "C0.3.POSTGEN",
    "W5.VALIDATION_EXIT",
    "EXIT",
)

R4_STAGE_ORDER_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_W5_VALIDATION_EXIT,
    sr.FILENAME_EXIT_DISPOSITION,
)

R4_EXPECTED_CHAIN_EDGES: tuple[tuple[str, str], ...] = (
    (sr.FILENAME_INGRESS_RAW, sr.FILENAME_U0_RECEIPT),
    (sr.FILENAME_U0_RECEIPT, sr.FILENAME_L1_PLAN),
    (sr.FILENAME_L1_PLAN, sr.FILENAME_ROUTE_CONTRACT),
    (sr.FILENAME_ROUTE_CONTRACT, sr.FILENAME_C0_FEC),
    (sr.FILENAME_C0_FEC, sr.FILENAME_C03_SENDER_PROOF),
    (sr.FILENAME_C03_SENDER_PROOF, sr.FILENAME_PA_RECEIPT),
    (sr.FILENAME_PA_RECEIPT, sr.FILENAME_L3_WORKFLOW),
    (sr.FILENAME_L3_WORKFLOW, sr.FILENAME_L2_EXECUTION),
    (sr.FILENAME_L2_EXECUTION, sr.FILENAME_W4_CANDIDATE_BATCH),
    (sr.FILENAME_W4_CANDIDATE_BATCH, sr.FILENAME_C03_POSTGEN_VALIDATION),
    (sr.FILENAME_C03_POSTGEN_VALIDATION, sr.FILENAME_W5_VALIDATION_EXIT),
    (sr.FILENAME_W5_VALIDATION_EXIT, sr.FILENAME_EXIT_DISPOSITION),
)

C0_BLOCK_REQUIRED_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_FEC_SUMMARY,
    sr.FILENAME_SPINE_MANIFEST,
)

C0_BLOCK_FORBIDDEN_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_W5_VALIDATION_EXIT,
    sr.FILENAME_EXIT_DISPOSITION,
)

C0_BLOCK_STAGE_ORDER: tuple[str, ...] = (
    "INGRESS",
    "U0",
    "L1",
    "L0",
    "C0",
)

C0_BLOCK_STAGE_ORDER_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
)

C0_BLOCK_EXPECTED_CHAIN_EDGES: tuple[tuple[str, str], ...] = (
    (sr.FILENAME_INGRESS_RAW, sr.FILENAME_U0_RECEIPT),
    (sr.FILENAME_U0_RECEIPT, sr.FILENAME_L1_PLAN),
    (sr.FILENAME_L1_PLAN, sr.FILENAME_ROUTE_CONTRACT),
    (sr.FILENAME_ROUTE_CONTRACT, sr.FILENAME_C0_FEC),
)


C03_BLOCK_REQUIRED_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_FEC_SUMMARY,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_SPINE_MANIFEST,
)

C03_BLOCK_FORBIDDEN_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_W5_VALIDATION_EXIT,
    sr.FILENAME_EXIT_DISPOSITION,
)

C03_BLOCK_STAGE_ORDER: tuple[str, ...] = (
    "INGRESS",
    "U0",
    "L1",
    "L0",
    "C0",
    "C0.3",
)

C03_BLOCK_STAGE_ORDER_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_C03_SENDER_PROOF,
)

C03_BLOCK_EXPECTED_CHAIN_EDGES: tuple[tuple[str, str], ...] = (
    (sr.FILENAME_INGRESS_RAW, sr.FILENAME_U0_RECEIPT),
    (sr.FILENAME_U0_RECEIPT, sr.FILENAME_L1_PLAN),
    (sr.FILENAME_L1_PLAN, sr.FILENAME_ROUTE_CONTRACT),
    (sr.FILENAME_ROUTE_CONTRACT, sr.FILENAME_C0_FEC),
    (sr.FILENAME_C0_FEC, sr.FILENAME_C03_SENDER_PROOF),
)


C03_POSTGEN_BLOCK_REQUIRED_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_FEC_SUMMARY,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_SPINE_MANIFEST,
)

C03_POSTGEN_BLOCK_FORBIDDEN_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_W5_VALIDATION_EXIT,
    sr.FILENAME_EXIT_DISPOSITION,
)

C03_POSTGEN_BLOCK_STAGE_ORDER: tuple[str, ...] = (
    "INGRESS",
    "U0",
    "L1",
    "L0",
    "C0",
    "C0.3",
    "PA",
    "L3",
    "L2",
    "W4.CANDIDATES",
    "C0.3.POSTGEN",
)

C03_POSTGEN_BLOCK_STAGE_ORDER_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
)

C03_POSTGEN_BLOCK_EXPECTED_CHAIN_EDGES: tuple[tuple[str, str], ...] = (
    (sr.FILENAME_INGRESS_RAW, sr.FILENAME_U0_RECEIPT),
    (sr.FILENAME_U0_RECEIPT, sr.FILENAME_L1_PLAN),
    (sr.FILENAME_L1_PLAN, sr.FILENAME_ROUTE_CONTRACT),
    (sr.FILENAME_ROUTE_CONTRACT, sr.FILENAME_C0_FEC),
    (sr.FILENAME_C0_FEC, sr.FILENAME_C03_SENDER_PROOF),
    (sr.FILENAME_C03_SENDER_PROOF, sr.FILENAME_PA_RECEIPT),
    (sr.FILENAME_PA_RECEIPT, sr.FILENAME_L3_WORKFLOW),
    (sr.FILENAME_L3_WORKFLOW, sr.FILENAME_L2_EXECUTION),
    (sr.FILENAME_L2_EXECUTION, sr.FILENAME_W4_CANDIDATE_BATCH),
    (sr.FILENAME_W4_CANDIDATE_BATCH, sr.FILENAME_C03_POSTGEN_VALIDATION),
)


W5_VALIDATION_EXIT_BLOCK_REQUIRED_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_FEC_SUMMARY,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_W5_VALIDATION_EXIT,
    sr.FILENAME_EXIT_DISPOSITION,
    sr.FILENAME_SPINE_MANIFEST,
)

W5_VALIDATION_EXIT_BLOCK_STAGE_ORDER: tuple[str, ...] = (
    "INGRESS",
    "U0",
    "L1",
    "L0",
    "C0",
    "C0.3",
    "PA",
    "L3",
    "L2",
    "W4.CANDIDATES",
    "C0.3.POSTGEN",
    "W5.VALIDATION_EXIT",
    "EXIT",
)

W5_VALIDATION_EXIT_BLOCK_STAGE_ORDER_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_W5_VALIDATION_EXIT,
    sr.FILENAME_EXIT_DISPOSITION,
)

W5_VALIDATION_EXIT_BLOCK_EXPECTED_CHAIN_EDGES: tuple[tuple[str, str], ...] = (
    (sr.FILENAME_INGRESS_RAW, sr.FILENAME_U0_RECEIPT),
    (sr.FILENAME_U0_RECEIPT, sr.FILENAME_L1_PLAN),
    (sr.FILENAME_L1_PLAN, sr.FILENAME_ROUTE_CONTRACT),
    (sr.FILENAME_ROUTE_CONTRACT, sr.FILENAME_C0_FEC),
    (sr.FILENAME_C0_FEC, sr.FILENAME_C03_SENDER_PROOF),
    (sr.FILENAME_C03_SENDER_PROOF, sr.FILENAME_PA_RECEIPT),
    (sr.FILENAME_PA_RECEIPT, sr.FILENAME_L3_WORKFLOW),
    (sr.FILENAME_L3_WORKFLOW, sr.FILENAME_L2_EXECUTION),
    (sr.FILENAME_L2_EXECUTION, sr.FILENAME_W4_CANDIDATE_BATCH),
    (sr.FILENAME_W4_CANDIDATE_BATCH, sr.FILENAME_C03_POSTGEN_VALIDATION),
    (sr.FILENAME_C03_POSTGEN_VALIDATION, sr.FILENAME_W5_VALIDATION_EXIT),
    (sr.FILENAME_W5_VALIDATION_EXIT, sr.FILENAME_EXIT_DISPOSITION),
)


W4_CANDIDATE_BLOCK_REQUIRED_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_FEC_SUMMARY,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_SPINE_MANIFEST,
)

W4_CANDIDATE_BLOCK_FORBIDDEN_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_W5_VALIDATION_EXIT,
    sr.FILENAME_EXIT_DISPOSITION,
)

W4_CANDIDATE_BLOCK_STAGE_ORDER: tuple[str, ...] = (
    "INGRESS",
    "U0",
    "L1",
    "L0",
    "C0",
    "C0.3",
    "PA",
    "L3",
    "L2",
    "W4.CANDIDATES",
)

W4_CANDIDATE_BLOCK_STAGE_ORDER_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
)

W4_CANDIDATE_BLOCK_EXPECTED_CHAIN_EDGES: tuple[tuple[str, str], ...] = (
    (sr.FILENAME_INGRESS_RAW, sr.FILENAME_U0_RECEIPT),
    (sr.FILENAME_U0_RECEIPT, sr.FILENAME_L1_PLAN),
    (sr.FILENAME_L1_PLAN, sr.FILENAME_ROUTE_CONTRACT),
    (sr.FILENAME_ROUTE_CONTRACT, sr.FILENAME_C0_FEC),
    (sr.FILENAME_C0_FEC, sr.FILENAME_C03_SENDER_PROOF),
    (sr.FILENAME_C03_SENDER_PROOF, sr.FILENAME_PA_RECEIPT),
    (sr.FILENAME_PA_RECEIPT, sr.FILENAME_L3_WORKFLOW),
    (sr.FILENAME_L3_WORKFLOW, sr.FILENAME_L2_EXECUTION),
    (sr.FILENAME_L2_EXECUTION, sr.FILENAME_W4_CANDIDATE_BATCH),
)


R5_REQUIRED_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_EXIT_DISPOSITION,
    sr.FILENAME_SPINE_MANIFEST,
)

R5_FORBIDDEN_STAGE_FILES: tuple[str, ...] = (
    sr.FILENAME_C0_FEC,
    sr.FILENAME_C03_SENDER_PROOF,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_W4_CANDIDATE_BATCH,
    sr.FILENAME_C03_POSTGEN_VALIDATION,
    sr.FILENAME_W5_VALIDATION_EXIT,
)

R5_STAGE_ORDER: tuple[str, ...] = (
    "INGRESS",
    "U0",
    "L1",
    "L0",
    "EXIT",
)

R5_STAGE_ORDER_FILES: tuple[str, ...] = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_EXIT_DISPOSITION,
)

R5_EXPECTED_CHAIN_EDGES: tuple[tuple[str, str], ...] = (
    (sr.FILENAME_INGRESS_RAW, sr.FILENAME_U0_RECEIPT),
    (sr.FILENAME_U0_RECEIPT, sr.FILENAME_L1_PLAN),
    (sr.FILENAME_L1_PLAN, sr.FILENAME_ROUTE_CONTRACT),
    (sr.FILENAME_ROUTE_CONTRACT, sr.FILENAME_EXIT_DISPOSITION),
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


def _check_r5_stage_order(artifact_dir: Path) -> list[str]:
    violations: list[str] = []
    for expected_stage, filename in zip(R5_STAGE_ORDER, R5_STAGE_ORDER_FILES, strict=True):
        data = _read_json(artifact_dir / filename)
        if data is None:
            violations.append(f"stage_order_missing:{filename}")
            continue
        actual = data.get("stage")
        if actual != expected_stage:
            violations.append(f"stage_order_mismatch:{filename}:{actual}!={expected_stage}")
    return violations


def _check_c0_block_stage_order(artifact_dir: Path) -> list[str]:
    violations: list[str] = []
    for expected_stage, filename in zip(
        C0_BLOCK_STAGE_ORDER,
        C0_BLOCK_STAGE_ORDER_FILES,
        strict=True,
    ):
        data = _read_json(artifact_dir / filename)
        if data is None:
            violations.append(f"stage_order_missing:{filename}")
            continue
        actual = data.get("stage")
        if actual != expected_stage:
            violations.append(f"stage_order_mismatch:{filename}:{actual}!={expected_stage}")
    return violations


def _check_c03_block_stage_order(artifact_dir: Path) -> list[str]:
    violations: list[str] = []
    for expected_stage, filename in zip(
        C03_BLOCK_STAGE_ORDER,
        C03_BLOCK_STAGE_ORDER_FILES,
        strict=True,
    ):
        data = _read_json(artifact_dir / filename)
        if data is None:
            violations.append(f"stage_order_missing:{filename}")
            continue
        actual = data.get("stage")
        if actual != expected_stage:
            violations.append(f"stage_order_mismatch:{filename}:{actual}!={expected_stage}")
    return violations


def _check_c03_postgen_block_stage_order(artifact_dir: Path) -> list[str]:
    violations: list[str] = []
    for expected_stage, filename in zip(
        C03_POSTGEN_BLOCK_STAGE_ORDER,
        C03_POSTGEN_BLOCK_STAGE_ORDER_FILES,
        strict=True,
    ):
        data = _read_json(artifact_dir / filename)
        if data is None:
            violations.append(f"stage_order_missing:{filename}")
            continue
        actual = data.get("stage")
        if actual != expected_stage:
            violations.append(f"stage_order_mismatch:{filename}:{actual}!={expected_stage}")
    return violations


def _check_w5_validation_exit_block_stage_order(artifact_dir: Path) -> list[str]:
    violations: list[str] = []
    for expected_stage, filename in zip(
        W5_VALIDATION_EXIT_BLOCK_STAGE_ORDER,
        W5_VALIDATION_EXIT_BLOCK_STAGE_ORDER_FILES,
        strict=True,
    ):
        data = _read_json(artifact_dir / filename)
        if data is None:
            violations.append(f"stage_order_missing:{filename}")
            continue
        actual = data.get("stage")
        if actual != expected_stage:
            violations.append(f"stage_order_mismatch:{filename}:{actual}!={expected_stage}")
    return violations


def _check_w4_candidate_block_stage_order(artifact_dir: Path) -> list[str]:
    violations: list[str] = []
    for expected_stage, filename in zip(
        W4_CANDIDATE_BLOCK_STAGE_ORDER,
        W4_CANDIDATE_BLOCK_STAGE_ORDER_FILES,
        strict=True,
    ):
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
        "c03_binding.py",
        "c03_postgen_binding.py",
        "w4_candidate_batch_binding.py",
        "w5_validation_exit_binding.py",
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
    if manifest.get("terminal_w4_candidate_block"):
        violations.append("r4_terminal_w4_candidate_block_true")
    if manifest.get("terminal_c03_postgen_block"):
        violations.append("r4_terminal_c03_postgen_block_true")
    if manifest.get("terminal_w5_validation_exit_block"):
        violations.append("r4_terminal_w5_validation_exit_block_true")
    if manifest.get("w4_candidate_status") != "W4_CANDIDATE_BATCH_READY":
        violations.append(
            f"r4_w4_candidate_status:{manifest.get('w4_candidate_status')!r}"
        )
    try:
        expected_candidates = int(manifest.get("max_candidates") or 1)
        materialized_candidates = int(
            manifest.get("w4_candidate_count_materialized") or 0
        )
    except (TypeError, ValueError):
        expected_candidates = 1
        materialized_candidates = 0
    if materialized_candidates != expected_candidates:
        violations.append(
            f"r4_w4_candidate_count:{materialized_candidates}!={expected_candidates}"
        )
    if expected_candidates > 1 and not list(manifest.get("w4_rejected_candidate_ids") or []):
        violations.append("r4_w4_rejected_candidates_missing")
    if manifest.get("c03_postgen_status") != "C03_POSTGEN_CLAIMS_PASS":
        violations.append(
            f"r4_c03_postgen_status:{manifest.get('c03_postgen_status')!r}"
        )
    if list(manifest.get("c03_postgen_blocked_claims") or []):
        violations.append("r4_c03_postgen_blocked_claims_non_empty")
    if manifest.get("w5_validation_exit_status") != "EXIT_CLEAR_DRAFT":
        violations.append(
            f"r4_w5_validation_exit_status:{manifest.get('w5_validation_exit_status')!r}"
        )
    if manifest.get("w5_x2_status") != "X2_VALIDATION_PASS":
        violations.append(f"r4_w5_x2_status:{manifest.get('w5_x2_status')!r}")
    if manifest.get("w5_x1d_status") not in {
        "X1D_NOT_REQUIRED",
        "X1D_VALIDATION_PASS",
    }:
        violations.append(f"r4_w5_x1d_status:{manifest.get('w5_x1d_status')!r}")
    if list(manifest.get("w5_x1d_missing_judge_ids") or []):
        violations.append("r4_w5_missing_judge_ids_non_empty")
    refs = list(manifest.get("stage_receipt_refs") or [])
    for req in R4_REQUIRED_STAGE_FILES:
        if req not in refs:
            violations.append(f"r4_stage_ref_missing:{req}")
    return violations


def _check_w4_candidate_block_manifest_policy(manifest: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if manifest.get("terminal_r5"):
        violations.append("w4_candidate_block_terminal_r5_true")
    if manifest.get("terminal_w4_candidate_block") is not True:
        violations.append("w4_candidate_block_terminal_flag_missing")
    if manifest.get("terminal_c03_postgen_block") is not False:
        violations.append("w4_candidate_block_c03_postgen_terminal_flag_not_false")
    if manifest.get("terminal_w5_validation_exit_block") is not False:
        violations.append("w4_candidate_block_w5_terminal_flag_not_false")
    if manifest.get("pa_invoked") is not True:
        violations.append(f"w4_candidate_block_pa_invoked:{manifest.get('pa_invoked')!r}")
    if manifest.get("l2_executed") is not True:
        violations.append(f"w4_candidate_block_l2_executed:{manifest.get('l2_executed')!r}")
    if manifest.get("l3_participated") is not True:
        violations.append(
            f"w4_candidate_block_l3_participated:{manifest.get('l3_participated')!r}"
        )
    if manifest.get("c03_postgen_invoked") is not False:
        violations.append(
            f"w4_candidate_block_c03_postgen_invoked:{manifest.get('c03_postgen_invoked')!r}"
        )
    if manifest.get("outcome_authorized") is not False:
        violations.append(
            "w4_candidate_block_outcome_authorized:"
            f"{manifest.get('outcome_authorized')!r}"
        )
    if manifest.get("x3_disposition") != "DENY":
        violations.append(
            f"w4_candidate_block_x3_disposition:{manifest.get('x3_disposition')!r}"
        )
    if manifest.get("exit_status") != "blocked":
        violations.append(f"w4_candidate_block_exit_status:{manifest.get('exit_status')!r}")
    if manifest.get("w4_candidate_status") != "W4_CANDIDATE_BATCH_BLOCKED":
        violations.append(
            f"w4_candidate_block_status:{manifest.get('w4_candidate_status')!r}"
        )
    if not list(manifest.get("w4_blocking_reasons") or []):
        violations.append("w4_candidate_block_reasons_missing")
    refs = list(manifest.get("stage_receipt_refs") or [])
    for req in W4_CANDIDATE_BLOCK_REQUIRED_STAGE_FILES:
        if req not in refs:
            violations.append(f"w4_candidate_block_stage_ref_missing:{req}")
    for forbidden in W4_CANDIDATE_BLOCK_FORBIDDEN_STAGE_FILES:
        if forbidden in refs:
            violations.append(f"w4_candidate_block_forbidden_stage_ref:{forbidden}")
    return violations


def _check_r5_manifest_policy(manifest: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if not manifest.get("terminal_r5"):
        violations.append("r5_terminal_r5_false")
    if manifest.get("x3_disposition") != "DENY":
        violations.append(f"r5_x3_disposition:{manifest.get('x3_disposition')!r}")
    if manifest.get("exit_status") not in {"blocked", "abstain"}:
        violations.append(f"r5_exit_status:{manifest.get('exit_status')!r}")
    if manifest.get("exit_disposition") not in {"blocked", "abstain"}:
        violations.append(f"r5_exit_disposition:{manifest.get('exit_disposition')!r}")
    if manifest.get("outcome_authorized") is not False:
        violations.append(f"r5_outcome_authorized:{manifest.get('outcome_authorized')!r}")
    if manifest.get("route_family") != "R5_FALLBACK":
        violations.append(f"r5_route_family:{manifest.get('route_family')!r}")
    if manifest.get("c0_invoked") is not False:
        violations.append(f"r5_c0_invoked:{manifest.get('c0_invoked')!r}")
    if manifest.get("pa_invoked") is not False:
        violations.append(f"r5_pa_invoked:{manifest.get('pa_invoked')!r}")
    if manifest.get("l2_executed") is not False:
        violations.append(f"r5_l2_executed:{manifest.get('l2_executed')!r}")
    if not str(manifest.get("terminal_reason") or manifest.get("terminal_r5_reason") or "").strip():
        violations.append("r5_terminal_reason_missing")
    if not str(manifest.get("trace_root") or manifest.get("trace_id") or "").strip():
        violations.append("r5_trace_root_missing")
    if not str(manifest.get("no_send_receipt") or "").strip():
        violations.append("r5_no_send_receipt_missing")
    if not str(manifest.get("no_l4_write_receipt") or "").strip():
        violations.append("r5_no_l4_write_receipt_missing")
    if not str(manifest.get("runtime_exhaust_ref") or "").strip():
        violations.append("r5_runtime_exhaust_ref_missing")
    refs = list(manifest.get("stage_receipt_refs") or [])
    for req in R5_REQUIRED_FILES:
        if req not in refs:
            violations.append(f"r5_stage_ref_missing:{req}")
    for forbidden in R5_FORBIDDEN_STAGE_FILES:
        if forbidden in refs:
            violations.append(f"r5_forbidden_stage_ref:{forbidden}")
    return violations


def _check_c0_block_manifest_policy(manifest: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if manifest.get("terminal_r5"):
        violations.append("c0_block_terminal_r5_true")
    if manifest.get("terminal_c0_block") is not True:
        violations.append("c0_block_terminal_flag_missing")
    if manifest.get("pa_invoked") is not False:
        violations.append(f"c0_block_pa_invoked:{manifest.get('pa_invoked')!r}")
    if manifest.get("l2_executed") is not False:
        violations.append(f"c0_block_l2_executed:{manifest.get('l2_executed')!r}")
    if manifest.get("l3_participated") is not False:
        violations.append(f"c0_block_l3_participated:{manifest.get('l3_participated')!r}")
    if manifest.get("outcome_authorized") is not False:
        violations.append(
            f"c0_block_outcome_authorized:{manifest.get('outcome_authorized')!r}"
        )
    if manifest.get("x3_disposition") != "DENY":
        violations.append(f"c0_block_x3_disposition:{manifest.get('x3_disposition')!r}")
    if manifest.get("exit_status") != "blocked":
        violations.append(f"c0_block_exit_status:{manifest.get('exit_status')!r}")
    if not str(manifest.get("c0_block_status") or "").strip():
        violations.append("c0_block_status_missing")
    refs = list(manifest.get("stage_receipt_refs") or [])
    for req in C0_BLOCK_REQUIRED_STAGE_FILES:
        if req not in refs:
            violations.append(f"c0_block_stage_ref_missing:{req}")
    for forbidden in C0_BLOCK_FORBIDDEN_STAGE_FILES:
        if forbidden in refs:
            violations.append(f"c0_block_forbidden_stage_ref:{forbidden}")
    return violations


def _check_c03_block_manifest_policy(manifest: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if manifest.get("terminal_r5"):
        violations.append("c03_block_terminal_r5_true")
    if manifest.get("terminal_c03_block") is not True:
        violations.append("c03_block_terminal_flag_missing")
    if manifest.get("pa_invoked") is not False:
        violations.append(f"c03_block_pa_invoked:{manifest.get('pa_invoked')!r}")
    if manifest.get("l2_executed") is not False:
        violations.append(f"c03_block_l2_executed:{manifest.get('l2_executed')!r}")
    if manifest.get("l3_participated") is not False:
        violations.append(f"c03_block_l3_participated:{manifest.get('l3_participated')!r}")
    if manifest.get("outcome_authorized") is not False:
        violations.append(
            f"c03_block_outcome_authorized:{manifest.get('outcome_authorized')!r}"
        )
    if manifest.get("x3_disposition") != "DENY":
        violations.append(f"c03_block_x3_disposition:{manifest.get('x3_disposition')!r}")
    if manifest.get("exit_status") != "blocked":
        violations.append(f"c03_block_exit_status:{manifest.get('exit_status')!r}")
    if not str(manifest.get("c03_status") or "").strip():
        violations.append("c03_status_missing")
    refs = list(manifest.get("stage_receipt_refs") or [])
    for req in C03_BLOCK_REQUIRED_STAGE_FILES:
        if req not in refs:
            violations.append(f"c03_block_stage_ref_missing:{req}")
    for forbidden in C03_BLOCK_FORBIDDEN_STAGE_FILES:
        if forbidden in refs:
            violations.append(f"c03_block_forbidden_stage_ref:{forbidden}")
    return violations


def _check_c03_postgen_block_manifest_policy(manifest: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if manifest.get("terminal_r5"):
        violations.append("c03_postgen_block_terminal_r5_true")
    if manifest.get("terminal_c03_postgen_block") is not True:
        violations.append("c03_postgen_block_terminal_flag_missing")
    if manifest.get("terminal_w4_candidate_block") is not False:
        violations.append("c03_postgen_block_w4_terminal_flag_not_false")
    if manifest.get("terminal_w5_validation_exit_block") is not False:
        violations.append("c03_postgen_block_w5_terminal_flag_not_false")
    if manifest.get("w4_candidate_status") != "W4_CANDIDATE_BATCH_READY":
        violations.append(
            f"c03_postgen_block_w4_status:{manifest.get('w4_candidate_status')!r}"
        )
    if manifest.get("pa_invoked") is not True:
        violations.append(f"c03_postgen_block_pa_invoked:{manifest.get('pa_invoked')!r}")
    if manifest.get("l2_executed") is not True:
        violations.append(f"c03_postgen_block_l2_executed:{manifest.get('l2_executed')!r}")
    if manifest.get("l3_participated") is not True:
        violations.append(
            f"c03_postgen_block_l3_participated:{manifest.get('l3_participated')!r}"
        )
    if manifest.get("outcome_authorized") is not False:
        violations.append(
            "c03_postgen_block_outcome_authorized:"
            f"{manifest.get('outcome_authorized')!r}"
        )
    if manifest.get("x3_disposition") != "DENY":
        violations.append(
            f"c03_postgen_block_x3_disposition:{manifest.get('x3_disposition')!r}"
        )
    if manifest.get("exit_status") != "blocked":
        violations.append(f"c03_postgen_block_exit_status:{manifest.get('exit_status')!r}")
    if not str(manifest.get("c03_postgen_status") or "").strip():
        violations.append("c03_postgen_status_missing")
    if not list(manifest.get("c03_postgen_blocked_claims") or []):
        violations.append("c03_postgen_blocked_claims_missing")
    refs = list(manifest.get("stage_receipt_refs") or [])
    for req in C03_POSTGEN_BLOCK_REQUIRED_STAGE_FILES:
        if req not in refs:
            violations.append(f"c03_postgen_block_stage_ref_missing:{req}")
    for forbidden in C03_POSTGEN_BLOCK_FORBIDDEN_STAGE_FILES:
        if forbidden in refs:
            violations.append(f"c03_postgen_block_forbidden_stage_ref:{forbidden}")
    return violations


def _check_w5_validation_exit_block_manifest_policy(manifest: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if manifest.get("terminal_r5"):
        violations.append("w5_validation_exit_block_terminal_r5_true")
    if manifest.get("terminal_w5_validation_exit_block") is not True:
        violations.append("w5_validation_exit_block_terminal_flag_missing")
    if manifest.get("terminal_w4_candidate_block") is not False:
        violations.append("w5_validation_exit_block_w4_terminal_flag_not_false")
    if manifest.get("terminal_c03_postgen_block") is not False:
        violations.append("w5_validation_exit_block_c03_postgen_terminal_flag_not_false")
    if manifest.get("w4_candidate_status") != "W4_CANDIDATE_BATCH_READY":
        violations.append(
            f"w5_validation_exit_block_w4_status:{manifest.get('w4_candidate_status')!r}"
        )
    if manifest.get("c03_postgen_status") != "C03_POSTGEN_CLAIMS_PASS":
        violations.append(
            "w5_validation_exit_block_c03_postgen_status:"
            f"{manifest.get('c03_postgen_status')!r}"
        )
    if manifest.get("w5_validation_exit_status") == "EXIT_CLEAR_DRAFT":
        violations.append("w5_validation_exit_block_status_clear")
    if manifest.get("w5_x2_status") == "X2_VALIDATION_PASS":
        if manifest.get("w5_x1d_status") in {"X1D_NOT_REQUIRED", "X1D_VALIDATION_PASS"}:
            violations.append("w5_validation_exit_block_without_x1d_or_x2_failure")
    if manifest.get("pa_invoked") is not True:
        violations.append(f"w5_validation_exit_block_pa_invoked:{manifest.get('pa_invoked')!r}")
    if manifest.get("l2_executed") is not True:
        violations.append(f"w5_validation_exit_block_l2_executed:{manifest.get('l2_executed')!r}")
    if manifest.get("l3_participated") is not True:
        violations.append(
            f"w5_validation_exit_block_l3_participated:{manifest.get('l3_participated')!r}"
        )
    if manifest.get("outcome_authorized") is not False:
        violations.append(
            "w5_validation_exit_block_outcome_authorized:"
            f"{manifest.get('outcome_authorized')!r}"
        )
    if manifest.get("x3_disposition") not in {"DENY", "X3B"}:
        violations.append(
            f"w5_validation_exit_block_x3_disposition:{manifest.get('x3_disposition')!r}"
        )
    if manifest.get("exit_status") not in {"blocked", "review_required"}:
        violations.append(
            f"w5_validation_exit_block_exit_status:{manifest.get('exit_status')!r}"
        )
    refs = list(manifest.get("stage_receipt_refs") or [])
    for req in W5_VALIDATION_EXIT_BLOCK_REQUIRED_STAGE_FILES:
        if req not in refs:
            violations.append(f"w5_validation_exit_block_stage_ref_missing:{req}")
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
    c0_blocked: bool = False,
    c03_blocked: bool = False,
    w4_candidate_blocked: bool = False,
    c03_postgen_blocked: bool = False,
    w5_validation_exit_blocked: bool = False,
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
        checks["stage_receipt_digests"] = _check_stage_receipts(
            artifact_dir,
            R5_STAGE_ORDER_FILES,
            manifest=manifest,
        )
        violations.extend(checks["stage_receipt_digests"])
        checks["stage_order"] = _check_r5_stage_order(artifact_dir)
        violations.extend(checks["stage_order"])
        checks["receipt_chain"] = _check_chain_edges(artifact_dir, R5_EXPECTED_CHAIN_EDGES)
        violations.extend(checks["receipt_chain"])
        checks["single_exit_x3"] = _check_single_exit_x3(artifact_dir, terminal_r5=False)
        violations.extend(checks["single_exit_x3"])
        checks["r5_terminal_exit_policy"] = []
        if manifest.get("x3_disposition") == "DENY" and manifest.get("exit_status") in {
            "blocked",
            "abstain",
        }:
            checks["r5_terminal_exit_policy"].append(
                "terminal_r5_exit_receipt_deny_by_design"
            )
        else:
            violations.append("r5_exit_policy_unexplained")
    elif c0_blocked:
        checks["c0_block_required_files"] = _check_files_present(
            artifact_dir,
            C0_BLOCK_REQUIRED_STAGE_FILES,
        )
        violations.extend(checks["c0_block_required_files"])
        checks["c0_block_forbidden_absent"] = _check_files_absent(
            artifact_dir,
            C0_BLOCK_FORBIDDEN_STAGE_FILES,
        )
        violations.extend(checks["c0_block_forbidden_absent"])
        checks["stage_receipt_digests"] = _check_stage_receipts(
            artifact_dir,
            (
                sr.FILENAME_INGRESS_RAW,
                sr.FILENAME_U0_RECEIPT,
                sr.FILENAME_L1_PLAN,
                sr.FILENAME_ROUTE_CONTRACT,
                sr.FILENAME_C0_FEC,
            ),
            manifest=manifest,
        )
        violations.extend(checks["stage_receipt_digests"])
        checks["stage_order"] = _check_c0_block_stage_order(artifact_dir)
        violations.extend(checks["stage_order"])
        checks["receipt_chain"] = _check_chain_edges(
            artifact_dir,
            C0_BLOCK_EXPECTED_CHAIN_EDGES,
        )
        violations.extend(checks["receipt_chain"])
        checks["c0_block_manifest_policy"] = _check_c0_block_manifest_policy(manifest)
        violations.extend(checks["c0_block_manifest_policy"])
        checks["no_durable_write_outside_exit"] = _check_no_durable_write_outside_exit(
            artifact_dir,
            terminal_r5=False,
        )
        violations.extend(checks["no_durable_write_outside_exit"])
    elif c03_blocked:
        checks["c03_block_required_files"] = _check_files_present(
            artifact_dir,
            C03_BLOCK_REQUIRED_STAGE_FILES,
        )
        violations.extend(checks["c03_block_required_files"])
        checks["c03_block_forbidden_absent"] = _check_files_absent(
            artifact_dir,
            C03_BLOCK_FORBIDDEN_STAGE_FILES,
        )
        violations.extend(checks["c03_block_forbidden_absent"])
        checks["stage_receipt_digests"] = _check_stage_receipts(
            artifact_dir,
            (
                sr.FILENAME_INGRESS_RAW,
                sr.FILENAME_U0_RECEIPT,
                sr.FILENAME_L1_PLAN,
                sr.FILENAME_ROUTE_CONTRACT,
                sr.FILENAME_C0_FEC,
                sr.FILENAME_C03_SENDER_PROOF,
            ),
            manifest=manifest,
        )
        violations.extend(checks["stage_receipt_digests"])
        checks["stage_order"] = _check_c03_block_stage_order(artifact_dir)
        violations.extend(checks["stage_order"])
        checks["receipt_chain"] = _check_chain_edges(
            artifact_dir,
            C03_BLOCK_EXPECTED_CHAIN_EDGES,
        )
        violations.extend(checks["receipt_chain"])
        checks["c03_block_manifest_policy"] = _check_c03_block_manifest_policy(manifest)
        violations.extend(checks["c03_block_manifest_policy"])
        checks["no_durable_write_outside_exit"] = _check_no_durable_write_outside_exit(
            artifact_dir,
            terminal_r5=False,
        )
        violations.extend(checks["no_durable_write_outside_exit"])
    elif w4_candidate_blocked:
        checks["w4_candidate_block_required_files"] = _check_files_present(
            artifact_dir,
            W4_CANDIDATE_BLOCK_REQUIRED_STAGE_FILES,
        )
        violations.extend(checks["w4_candidate_block_required_files"])
        checks["w4_candidate_block_forbidden_absent"] = _check_files_absent(
            artifact_dir,
            W4_CANDIDATE_BLOCK_FORBIDDEN_STAGE_FILES,
        )
        violations.extend(checks["w4_candidate_block_forbidden_absent"])
        checks["stage_receipt_digests"] = _check_stage_receipts(
            artifact_dir,
            W4_CANDIDATE_BLOCK_REQUIRED_STAGE_FILES,
            manifest=manifest,
        )
        violations.extend(checks["stage_receipt_digests"])
        checks["stage_order"] = _check_w4_candidate_block_stage_order(artifact_dir)
        violations.extend(checks["stage_order"])
        checks["receipt_chain"] = _check_chain_edges(
            artifact_dir,
            W4_CANDIDATE_BLOCK_EXPECTED_CHAIN_EDGES,
        )
        violations.extend(checks["receipt_chain"])
        checks["w4_candidate_block_manifest_policy"] = (
            _check_w4_candidate_block_manifest_policy(manifest)
        )
        violations.extend(checks["w4_candidate_block_manifest_policy"])
        checks["no_durable_write_outside_exit"] = _check_no_durable_write_outside_exit(
            artifact_dir,
            terminal_r5=False,
        )
        violations.extend(checks["no_durable_write_outside_exit"])
    elif c03_postgen_blocked:
        checks["c03_postgen_block_required_files"] = _check_files_present(
            artifact_dir,
            C03_POSTGEN_BLOCK_REQUIRED_STAGE_FILES,
        )
        violations.extend(checks["c03_postgen_block_required_files"])
        checks["c03_postgen_block_forbidden_absent"] = _check_files_absent(
            artifact_dir,
            C03_POSTGEN_BLOCK_FORBIDDEN_STAGE_FILES,
        )
        violations.extend(checks["c03_postgen_block_forbidden_absent"])
        checks["stage_receipt_digests"] = _check_stage_receipts(
            artifact_dir,
            C03_POSTGEN_BLOCK_REQUIRED_STAGE_FILES,
            manifest=manifest,
        )
        violations.extend(checks["stage_receipt_digests"])
        checks["stage_order"] = _check_c03_postgen_block_stage_order(artifact_dir)
        violations.extend(checks["stage_order"])
        checks["receipt_chain"] = _check_chain_edges(
            artifact_dir,
            C03_POSTGEN_BLOCK_EXPECTED_CHAIN_EDGES,
        )
        violations.extend(checks["receipt_chain"])
        checks["c03_postgen_block_manifest_policy"] = (
            _check_c03_postgen_block_manifest_policy(manifest)
        )
        violations.extend(checks["c03_postgen_block_manifest_policy"])
        checks["no_durable_write_outside_exit"] = _check_no_durable_write_outside_exit(
            artifact_dir,
            terminal_r5=False,
        )
        violations.extend(checks["no_durable_write_outside_exit"])
    elif w5_validation_exit_blocked:
        checks["w5_validation_exit_block_required_files"] = _check_files_present(
            artifact_dir,
            W5_VALIDATION_EXIT_BLOCK_REQUIRED_STAGE_FILES,
        )
        violations.extend(checks["w5_validation_exit_block_required_files"])
        checks["stage_receipt_digests"] = _check_stage_receipts(
            artifact_dir,
            W5_VALIDATION_EXIT_BLOCK_REQUIRED_STAGE_FILES,
            manifest=manifest,
        )
        violations.extend(checks["stage_receipt_digests"])
        checks["stage_order"] = _check_w5_validation_exit_block_stage_order(artifact_dir)
        violations.extend(checks["stage_order"])
        checks["receipt_chain"] = _check_chain_edges(
            artifact_dir,
            W5_VALIDATION_EXIT_BLOCK_EXPECTED_CHAIN_EDGES,
        )
        violations.extend(checks["receipt_chain"])
        checks["w5_validation_exit_block_manifest_policy"] = (
            _check_w5_validation_exit_block_manifest_policy(manifest)
        )
        violations.extend(checks["w5_validation_exit_block_manifest_policy"])
        checks["single_exit_x3"] = _check_single_exit_x3(artifact_dir, terminal_r5=False)
        violations.extend(checks["single_exit_x3"])
        checks["no_durable_write_outside_exit"] = _check_no_durable_write_outside_exit(
            artifact_dir,
            terminal_r5=False,
        )
        violations.extend(checks["no_durable_write_outside_exit"])
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
        "terminal_c0_block": c0_blocked,
        "terminal_c03_block": c03_blocked,
        "terminal_w4_candidate_block": w4_candidate_blocked,
        "terminal_c03_postgen_block": c03_postgen_blocked,
        "terminal_w5_validation_exit_block": w5_validation_exit_blocked,
        "proof_mode": (
            "terminal_r5"
            if terminal_r5
            else "c0_block"
            if c0_blocked
            else "c03_block"
            if c03_blocked
            else "w4_candidate_block"
            if w4_candidate_blocked
            else "c03_postgen_block"
            if c03_postgen_blocked
            else "w5_validation_exit_block"
            if w5_validation_exit_blocked
            else "r4"
        ),
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
        "canonical_stage_order": (
            list(R5_STAGE_ORDER)
            if terminal_r5
            else list(C0_BLOCK_STAGE_ORDER)
            if c0_blocked
            else list(C03_BLOCK_STAGE_ORDER)
            if c03_blocked
            else list(W4_CANDIDATE_BLOCK_STAGE_ORDER)
            if w4_candidate_blocked
            else list(C03_POSTGEN_BLOCK_STAGE_ORDER)
            if c03_postgen_blocked
            else list(W5_VALIDATION_EXIT_BLOCK_STAGE_ORDER)
            if w5_validation_exit_blocked
            else list(R4_CANONICAL_STAGE_ORDER)
        ),
    }


def write_runtime_proof_bundle(
    artifact_dir: Path,
    manifest: dict[str, Any],
    *,
    terminal_r5: bool,
    c0_blocked: bool = False,
    c03_blocked: bool = False,
    w4_candidate_blocked: bool = False,
    c03_postgen_blocked: bool = False,
    w5_validation_exit_blocked: bool = False,
    repo_root: Path | None = None,
) -> str:
    bundle = build_runtime_proof_bundle(
        artifact_dir,
        manifest,
        terminal_r5=terminal_r5,
        c0_blocked=c0_blocked,
        c03_blocked=c03_blocked,
        w4_candidate_blocked=w4_candidate_blocked,
        c03_postgen_blocked=c03_postgen_blocked,
        w5_validation_exit_blocked=w5_validation_exit_blocked,
        repo_root=repo_root,
    )
    path = artifact_dir / FILENAME_RUNTIME_PROOF_BUNDLE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)
