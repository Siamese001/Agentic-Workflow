"""W8B — integrated modular lane evidence finalization and parent RUN_LINKS binding."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.run_bundle_index import RUN_BUNDLE_INDEX_FILENAME, repo_relative_posix
from apps_rg.runtime.run_correlation_links import RUN_LINKS_FILENAME
from apps_rg.runtime.section_evidence_package import (
    CORRELATED_CLI_RUN_ENV,
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    SUBPHASE_COVERAGE_INDEX_ARTIFACT,
)
from apps_rg.runtime.section_binding_taxonomy import W4_VERIFIED_EXTERNAL_ARTIFACTS
from apps_rg.runtime.section_l7_binding_lane_integration import finalize_section_l7_binding

INTEGRATED_LANE_EVIDENCE_STATUS_ARTIFACT = "integrated_lane_evidence_status.json"
INTEGRATED_LANE_PRE_RUN_FAILURE_ARTIFACT = "integrated_lane_pre_run_failure.json"
L7_VERIFIER_DIAGNOSIS_ARTIFACT = "integrated_l7_verifier_diagnosis.json"
BINDING_MANIFEST_ARTIFACT = "section_l7_binding_manifest.json"

_CORRELATION_METHOD_ANCESTOR_CLI = "modular_r4_ancestor_cli_run_dir"

_SHADOW_ARTIFACT_DENYLIST: frozenset[str] = frozenset(
    {
        "orchestrate_full_resume",
        "resume_package_x3",
        "executive_summary_demo",
        "generated_lane_rollup.json",
    }
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    return raw if isinstance(raw, dict) else None


def discover_integrated_cli_run_from_path(repo_root: Path, path: Path) -> Path | None:
    """Resolve ``artifacts/apps_rg/runs/cli_*`` ancestor of a modular lane run dir."""
    resolved = path.resolve()
    runs_root = (repo_root / "artifacts" / "apps_rg" / "runs").resolve()
    for parent in [resolved, *resolved.parents]:
        if not parent.is_dir() or not parent.name.startswith("cli_"):
            continue
        try:
            if parent.parent.resolve() == runs_root:
                return parent
        except (OSError, ValueError):
            continue
    return None


def discover_integrated_cli_run_by_ancestor(
    repo_root: Path,
    artifact_dir: Path,
) -> tuple[Path | None, str | None]:
    hit = discover_integrated_cli_run_from_path(repo_root, artifact_dir)
    if hit is not None:
        return hit, _CORRELATION_METHOD_ANCESTOR_CLI
    return None, None


def _lane_x3_from_artifact_dir(artifact_dir: Path) -> str | None:
    for name in ("x3_disposition.json", "exit_disposition_receipt.json", "x3_disposition_receipt.json"):
        doc = _load_json(artifact_dir / name)
        if not doc:
            continue
        for key in ("x3_code", "x3_disposition", "disposition", "final_disposition"):
            val = doc.get(key)
            if isinstance(val, dict):
                val = val.get("x3_code") or val.get("code")
            code = str(val or "").strip()
            if code and not code.startswith("{"):
                return code
    return None


def _lane_outcome_from_dir(artifact_dir: Path) -> str:
    if not artifact_dir.is_dir():
        return "MISSING"
    if (artifact_dir / "l2_output.json").is_file():
        x3 = _lane_x3_from_artifact_dir(artifact_dir)
        if x3:
            return x3
        return "EXECUTED"
    return "INCOMPLETE"


def emit_integrated_lane_pre_run_failure(
    *,
    sections_root: Path,
    integrated_dir: Path,
    repo_root: Path,
    lane_id: str,
    blocker: str,
    dispatch_result: Mapping[str, Any] | None = None,
    lane_exec_status: str = "",
) -> Path:
    """Write explicit PRE_RUN_BLOCKED receipt when Phase1 cannot resolve a lane run dir."""
    lane_root = Path(sections_root) / lane_id
    lane_root.mkdir(parents=True, exist_ok=True)
    out_path = lane_root / INTEGRATED_LANE_PRE_RUN_FAILURE_ARTIFACT
    doc: dict[str, Any] = {
        "schema_version": "integrated_lane_pre_run_failure_v1",
        "generated_at_utc": _utc_now(),
        "lane_id": lane_id,
        "status": "PRE_RUN_BLOCKED",
        "blocker": str(blocker or "PHASE1_NO_RUN_DIR").strip() or "PHASE1_NO_RUN_DIR",
        "lane_exec_status": str(lane_exec_status or ""),
        "integrated_run_id": integrated_dir.name,
        "sections_root_rel": repo_relative_posix(repo_root, Path(sections_root).resolve()),
        "dispatch_result": dict(dispatch_result) if isinstance(dispatch_result, Mapping) else {},
        "expected_run_dir_pattern": (
            f"{repo_relative_posix(repo_root, integrated_dir)}/modular_r4/sections/"
            f"{lane_id}/real/<run_id>/"
        ),
    }
    out_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path


def load_integrated_lane_pre_run_failure(integrated_dir: Path, lane_id: str) -> dict[str, Any] | None:
    """Load pre-run failure receipt from modular sections tree when present."""
    path = (
        Path(integrated_dir)
        / "modular_r4"
        / "sections"
        / lane_id
        / INTEGRATED_LANE_PRE_RUN_FAILURE_ARTIFACT
    )
    return _load_json(path)


def _resolve_lane_run_dir(
    repo_root: Path,
    integrated_dir: Path,
    lane: str,
) -> tuple[Path | None, str, str | None]:
    """Return (run_dir, resolution_tag, pointer_run_id)."""
    lane_base = integrated_dir / "modular_r4" / "sections" / lane
    pre_run = load_integrated_lane_pre_run_failure(integrated_dir, lane)
    if pre_run and str(pre_run.get("blocker") or "").strip():
        return None, "pre_run_blocked", None
    if not lane_base.is_dir():
        return None, "lane_section_root_absent", None

    for ptr_name in ("latest_successful_real_run.json", "latest_real_run.json"):
        ptr = lane_base / ptr_name
        if not ptr.is_file():
            continue
        doc = _load_json(ptr)
        if not doc:
            continue
        rel = str(doc.get("run_dir") or doc.get("run_dir_repo_relative") or "").strip()
        rid = str(doc.get("run_id") or "").strip() or None
        if rel:
            rd = (repo_root / rel).resolve() if not Path(rel).is_absolute() else Path(rel).resolve()
            if rd.is_dir():
                return rd, ptr_name, rid

    real_root = lane_base / "real"
    if real_root.is_dir():
        candidates: list[tuple[float, Path, str]] = []
        for child in real_root.iterdir():
            if not child.is_dir() or not (child / "l2_output.json").is_file():
                continue
            candidates.append((child.stat().st_mtime, child, child.name))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best = candidates[0]
            return best[1], "newest_real_subdir_scan", best[2]
    return None, "no_run_dir", None


def _parent_l7_ref_rows(repo_root: Path, integrated_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for filename in W4_VERIFIED_EXTERNAL_ARTIFACTS:
        source = integrated_dir / filename
        rows.append(
            {
                "artifact_name": filename,
                "source_path": repo_relative_posix(repo_root, source)
                if source.is_file()
                else None,
                "sha256": _sha256_file(source) if source.is_file() else "",
                "exists": source.is_file(),
                "trust_status": "verified_external" if source.is_file() else "missing",
            }
        )
    manifest = integrated_dir / "integrated_runtime_artifact_manifest.json"
    rows.append(
        {
            "artifact_name": "integrated_runtime_artifact_manifest.json",
            "source_path": repo_relative_posix(repo_root, manifest)
            if manifest.is_file()
            else None,
            "sha256": _sha256_file(manifest) if manifest.is_file() else "",
            "exists": manifest.is_file(),
            "trust_status": "verified_external" if manifest.is_file() else "missing",
        }
    )
    return rows


def build_missing_lane_record(
    *,
    lane_id: str,
    reason: str,
    integrated_dir: Path,
    repo_root: Path,
    recipe_fatal: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    expected = (
        f"{repo_relative_posix(repo_root, integrated_dir)}/modular_r4/sections/"
        f"{lane_id}/real/<run_id>/"
    )
    rec_reason = reason
    if recipe_fatal:
        rec_reason = str(recipe_fatal.get("decisive_reason_code") or reason)
    return {
        "lane": lane_id,
        "lane_id": lane_id,
        "status": "NOT_RUN",
        "proof_mode": "unknown",
        "run_id": "",
        "root_path": None,
        "bundle_index_ref": None,
        "evidence_package_index_ref": None,
        "evidence_package_index_sha256": "",
        "section_l7_binding_manifest_ref": None,
        "section_l7_binding_manifest_sha256": "",
        "lane_outcome": "NOT_RUN",
        "lane_x3": None,
        "missing_reason": rec_reason,
        "expected_run_dir": expected,
        "expected_run_dir_pattern": expected,
        "product_certification_impact": "integrated_r4_product_proof_blocked",
        "parent_integrated_run_id": integrated_dir.name,
        "parent_l7_artifact_refs": _parent_l7_ref_rows(repo_root, integrated_dir),
        "exists": False,
        "producer": "apps_rg.runtime.integrated_lane_evidence_packaging.build_missing_lane_record",
        "explicit_non_claims": [
            "lane did not execute under integrated modular_r4 envelope",
            "NOT_RUN is explicit; not silent skip",
            "no section-only proof upgraded to product proof",
            "no shadow offline rollup consumed as lane evidence",
        ],
    }


def build_executed_lane_bundle_ref(
    *,
    repo_root: Path,
    integrated_dir: Path,
    lane: str,
    run_dir: Path,
    run_id: str,
    resolution_tag: str,
) -> dict[str, Any]:
    root_posix = repo_relative_posix(repo_root, run_dir.resolve())
    bundle_ix = run_dir / RUN_BUNDLE_INDEX_FILENAME
    ev_pkg = run_dir / EVIDENCE_PACKAGE_INDEX_ARTIFACT
    bind = run_dir / BINDING_MANIFEST_ARTIFACT
    subphase = run_dir / SUBPHASE_COVERAGE_INDEX_ARTIFACT
    return {
        "lane": lane,
        "lane_id": lane,
        "status": "EXECUTED",
        "proof_mode": "real",
        "run_id": run_id,
        "root_path": root_posix,
        "bundle_index_ref": repo_relative_posix(repo_root, bundle_ix)
        if bundle_ix.is_file()
        else None,
        "bundle_index_sha256": _sha256_file(bundle_ix) if bundle_ix.is_file() else "",
        "evidence_package_index_ref": repo_relative_posix(repo_root, ev_pkg)
        if ev_pkg.is_file()
        else None,
        "evidence_package_index_sha256": _sha256_file(ev_pkg) if ev_pkg.is_file() else "",
        "section_l7_binding_manifest_ref": repo_relative_posix(repo_root, bind)
        if bind.is_file()
        else None,
        "section_l7_binding_manifest_sha256": _sha256_file(bind) if bind.is_file() else "",
        "spine_subphase_coverage_index_ref": repo_relative_posix(repo_root, subphase)
        if subphase.is_file()
        else None,
        "lane_outcome": _lane_outcome_from_dir(run_dir),
        "lane_x3": _lane_x3_from_artifact_dir(run_dir),
        "missing_reason": None,
        "run_dir_resolution": resolution_tag,
        "parent_integrated_run_id": integrated_dir.name,
        "parent_l7_artifact_refs": _parent_l7_ref_rows(repo_root, integrated_dir),
        "exists": bundle_ix.is_file() and ev_pkg.is_file() and bind.is_file(),
        "producer": "apps_rg.runtime.integrated_lane_evidence_packaging.build_executed_lane_bundle_ref",
        "explicit_non_claims": [
            "lane evidence package is narrative audit linkage only",
            "parent L7 refs are verified external hashes only",
            "orchestrate_full_resume and resume_package_x3 are not lane evidence",
        ],
    }


def maybe_finalize_lane_evidence_package(
    repo_root: Path,
    artifact_dir: Path,
    *,
    section_id: str,
    run_id: str,
    correlation_id: str | None = None,
) -> dict[str, Any] | None:
    """Finalize lane evidence when run dir lives under integrated ``cli_*/modular_r4``."""
    integrated = discover_integrated_cli_run_from_path(repo_root, artifact_dir)
    if integrated is None:
        return None

    ev_path = artifact_dir / EVIDENCE_PACKAGE_INDEX_ARTIFACT
    if ev_path.is_file():
        return {"skipped": "already_finalized", "evidence_package_index_path": ev_path}

    runtime_payload: dict[str, Any] = {
        "run_id": run_id,
        "section_id": section_id,
        "correlation_id": correlation_id or integrated.name,
        "integrated_cli_run_ref": repo_relative_posix(repo_root, integrated),
        "command_surface": f"python -m apps_rg --section {section_id}",
    }
    manifest_path = artifact_dir / "run_manifest.json"
    if manifest_path.is_file():
        mdoc = _load_json(manifest_path)
        if mdoc:
            runtime_payload.update(
                {
                    k: mdoc[k]
                    for k in ("command", "provider_requested", "runtime_generation_status")
                    if k in mdoc
                }
            )

    finalize_section_l7_binding(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
        repo_root=repo_root,
        command_surface=runtime_payload.get("command_surface"),
    )
    return {
        "finalized": True,
        "integrated_run_dir": integrated,
        "evidence_package_index_path": ev_path,
    }


def _fatal_by_lane(recipe_lane_policy: Mapping[str, Any] | None) -> dict[str, Mapping[str, Any]]:
    out: dict[str, Mapping[str, Any]] = {}
    if not recipe_lane_policy:
        return out
    for row in recipe_lane_policy.get("fatal_lane_failures") or []:
        if isinstance(row, dict):
            lane = str(row.get("section_lane") or "").strip()
            if lane:
                out[lane] = row
    return out


def _record_from_section_calls(
    section_call_records: list[dict[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for raw in section_call_records or []:
        if not isinstance(raw, dict):
            continue
        lane = str(raw.get("section_lane") or "").strip()
        if lane:
            out[lane] = raw
    return out


def diagnose_l7_verifier_layout_mismatch(integrated_dir: Path) -> dict[str, Any] | None:
    """If spine proof reports missing L7 while files exist on disk, record diagnosis."""
    spine_path = integrated_dir / "agentic_core_spine_proof.json"
    if not spine_path.is_file():
        return None
    spine = _load_json(spine_path)
    if not spine:
        return None
    texts: list[str] = []
    if isinstance(spine.get("blocking_gaps"), list):
        texts.extend(str(x) for x in spine["blocking_gaps"])
    if isinstance(spine.get("verifier_notes"), list):
        texts.extend(str(x) for x in spine["verifier_notes"])
    blob = json.dumps(spine, ensure_ascii=False).upper()
    missing_claim = "MISSING" in blob or "NOT_FOUND" in blob
    if not missing_claim:
        return None

    present: list[str] = []
    absent: list[str] = []
    for name in W4_VERIFIED_EXTERNAL_ARTIFACTS:
        p = integrated_dir / name
        if p.is_file():
            present.append(name)
        else:
            absent.append(name)

    if not present or not missing_claim:
        return None

    return {
        "classification": "L7_VERIFIER_LAYOUT_MISMATCH",
        "generated_at_utc": _utc_now(),
        "integrated_run_id": integrated_dir.name,
        "spine_proof_path": spine_path.name,
        "l7_files_present_on_disk": present,
        "l7_files_absent_on_disk": absent,
        "verifier_blocking_signals": texts[:12],
        "explicit_non_claims": [
            "files exist at integrated run root but spine verifier still reports gaps",
            "W8B does not rewrite agentic_core spine verifier",
            "packaging-only diagnosis for operator repair",
        ],
    }


def discover_integrated_modular_lane_bundle_refs(
    repo_root: Path,
    integrated_dir: Path,
    *,
    section_call_records: list[dict[str, Any]] | None = None,
    recipe_lane_policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build W8B lane_bundle_refs from ``modular_r4/sections`` tree + explicit NOT_RUN rows."""
    repo_root = Path(repo_root)
    integrated_dir = Path(integrated_dir)
    fatal_map = _fatal_by_lane(recipe_lane_policy)
    call_map = _record_from_section_calls(section_call_records)
    refs: list[dict[str, Any]] = []

    for lane in GENERATED_LANES:
        run_dir, resolution, run_id = _resolve_lane_run_dir(repo_root, integrated_dir, lane)
        if run_dir is not None and run_id:
            refs.append(
                build_executed_lane_bundle_ref(
                    repo_root=repo_root,
                    integrated_dir=integrated_dir,
                    lane=lane,
                    run_dir=run_dir,
                    run_id=run_id,
                    resolution_tag=resolution,
                )
            )
            continue

        reason = "PHASE1_NO_RUN_DIR"
        pre_run = load_integrated_lane_pre_run_failure(integrated_dir, lane)
        if pre_run and str(pre_run.get("blocker") or "").strip():
            reason = str(pre_run["blocker"]).strip()
        elif lane in fatal_map:
            reason = str(fatal_map[lane].get("decisive_reason_code") or reason)
        elif lane in call_map:
            reason = str(call_map[lane].get("decisive_reason_code") or reason)
        missing_rec = build_missing_lane_record(
            lane_id=lane,
            reason=reason,
            integrated_dir=integrated_dir,
            repo_root=repo_root,
            recipe_fatal=fatal_map.get(lane) or call_map.get(lane),
        )
        if pre_run:
            fail_path = (
                integrated_dir
                / "modular_r4"
                / "sections"
                / lane
                / INTEGRATED_LANE_PRE_RUN_FAILURE_ARTIFACT
            )
            if fail_path.is_file():
                missing_rec["pre_run_failure_ref"] = repo_relative_posix(repo_root, fail_path)
        refs.append(missing_rec)

    refs.sort(key=lambda r: (str(r.get("lane") or ""), str(r.get("status") or "")))
    return refs


def finalize_integrated_run_lane_evidence(
    repo_root: Path,
    integrated_artifact_dir: Path,
    *,
    correlation_id: str | None = None,
    section_call_records: list[dict[str, Any]] | None = None,
    recipe_lane_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Finalize per-lane evidence under integrated run and refresh parent RUN_LINKS."""
    repo_root = Path(repo_root)
    integrated_dir = Path(integrated_artifact_dir)
    cid = str(correlation_id or integrated_dir.name).strip() or integrated_dir.name

    prev_corr = os.environ.get(CORRELATED_CLI_RUN_ENV)
    os.environ[CORRELATED_CLI_RUN_ENV] = repo_relative_posix(repo_root, integrated_dir)
    finalized_lanes: list[str] = []
    try:
        for lane in GENERATED_LANES:
            run_dir, _resolution, run_id = _resolve_lane_run_dir(repo_root, integrated_dir, lane)
            if run_dir is None or not run_id:
                continue
            maybe_finalize_lane_evidence_package(
                repo_root,
                run_dir,
                section_id=lane,
                run_id=run_id,
                correlation_id=cid,
            )
            finalized_lanes.append(lane)
    finally:
        if prev_corr is None:
            os.environ.pop(CORRELATED_CLI_RUN_ENV, None)
        else:
            os.environ[CORRELATED_CLI_RUN_ENV] = prev_corr

    lane_refs = discover_integrated_modular_lane_bundle_refs(
        repo_root,
        integrated_dir,
        section_call_records=section_call_records,
        recipe_lane_policy=recipe_lane_policy,
    )

    l7_diag = diagnose_l7_verifier_layout_mismatch(integrated_dir)
    status_doc: dict[str, Any] = {
        "schema_version": "integrated_lane_evidence_status_v1",
        "generated_at_utc": _utc_now(),
        "integrated_run_id": integrated_dir.name,
        "correlation_id": cid,
        "lanes_finalized": finalized_lanes,
        "lane_bundle_ref_count": len(lane_refs),
        "executed_lane_count": sum(1 for r in lane_refs if r.get("status") == "EXECUTED"),
        "not_run_lane_count": sum(1 for r in lane_refs if r.get("status") == "NOT_RUN"),
        "missing_lanes": [
            {
                "lane_id": r["lane_id"],
                "reason": r.get("missing_reason"),
                "expected_run_dir_pattern": r.get("expected_run_dir_pattern"),
            }
            for r in lane_refs
            if r.get("status") == "NOT_RUN"
        ],
        "shadow_artifacts_rejected": sorted(_SHADOW_ARTIFACT_DENYLIST),
        "explicit_non_claims": [
            "parent integrated evidence does not consume orchestrate_full_resume rollup",
            "parent integrated evidence does not consume resume_package_x3",
            "parent integrated evidence does not consume executive_summary_demo",
            "product certification not upgraded by packaging alone",
        ],
    }
    if l7_diag:
        status_doc["l7_verifier_diagnosis"] = l7_diag
        (integrated_dir / L7_VERIFIER_DIAGNOSIS_ARTIFACT).write_text(
            json.dumps(l7_diag, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    (integrated_dir / INTEGRATED_LANE_EVIDENCE_STATUS_ARTIFACT).write_text(
        json.dumps(status_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    from apps_rg.runtime.run_correlation_links import build_run_links_document, write_run_links

    links_doc = build_run_links_document(
        repo_root,
        integrated_dir,
        integrated_run_id=integrated_dir.name,
        correlation_id=cid,
        notes="W8B modular_r4 lane evidence packaging",
        lane_bundle_refs_override=lane_refs,
    )
    write_run_links(integrated_dir, links_doc)

    exec_row = next((r for r in lane_refs if r.get("lane") == "executive_summary"), None)
    return {
        "integrated_run_dir": integrated_dir,
        "run_links_path": integrated_dir / RUN_LINKS_FILENAME,
        "lane_bundle_refs": lane_refs,
        "lane_bundle_refs_count": len(lane_refs),
        "finalized_lanes": finalized_lanes,
        "executive_summary_status": (exec_row or {}).get("status"),
        "executive_summary_missing_reason": (exec_row or {}).get("missing_reason"),
        "l7_verifier_diagnosis": l7_diag,
        "integrated_lane_evidence_status_path": integrated_dir / INTEGRATED_LANE_EVIDENCE_STATUS_ARTIFACT,
    }


__all__ = [
    "INTEGRATED_LANE_EVIDENCE_STATUS_ARTIFACT",
    "INTEGRATED_LANE_PRE_RUN_FAILURE_ARTIFACT",
    "L7_VERIFIER_DIAGNOSIS_ARTIFACT",
    "build_executed_lane_bundle_ref",
    "build_missing_lane_record",
    "discover_integrated_cli_run_by_ancestor",
    "discover_integrated_cli_run_from_path",
    "discover_integrated_modular_lane_bundle_refs",
    "diagnose_l7_verifier_layout_mismatch",
    "emit_integrated_lane_pre_run_failure",
    "finalize_integrated_run_lane_evidence",
    "load_integrated_lane_pre_run_failure",
    "maybe_finalize_lane_evidence_package",
]
