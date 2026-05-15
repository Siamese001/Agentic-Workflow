"""Assemble final_resume.json from rollup + locked copy manifest + canonical base resume (no LLM/registry)."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.assembly.final_resume_manifest import (
    FinalResumePaths,
    build_assembly_manifest,
    resolve_default_paths,
)
from apps_rg.runtime.assembly.final_resume_x2 import (
    CANONICAL_ASSEMBLED_SECTION_ORDER,
    GENERATED_LANE_IDS,
    LOCKED_EMBEDDED_ORDER_IDS,
    LOCKED_INVARIANT_IDS,
    canonical_json_sorted,
    failures,
    gates_all_pass,
    run_final_resume_x2_gates,
    sha256_utf8,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root, sha256_hex


ASSEMBLER_OBJECT_ID = "final_resume_assembled_v1"


def _resolved_run_dir(repo: Path, rel: str) -> Path:
    rel_norm = rel.replace("\\", "/")
    while rel_norm.startswith("./"):
        rel_norm = rel_norm[2:]
    return (repo / rel_norm).resolve()


def _norm_artifact_refs(repo: Path, refs: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, raw in refs.items():
        if not isinstance(raw, str):
            continue
        p = _resolved_run_dir(repo, raw.replace("\\", "/"))
        try:
            out[str(key)] = p.relative_to(repo).as_posix()
        except ValueError:
            out[str(key)] = p.as_posix()
    return out


def assemble_final_resume(paths: FinalResumePaths | None = None) -> dict[str, Any]:
    paths = paths or resolve_default_paths()
    repo = paths.repo_root

    rollup_raw = paths.rollup_json.read_text(encoding="utf-8")
    rollup_blob: dict[str, Any] = json.loads(rollup_raw)

    locked_manifest_raw = paths.locked_manifest.read_text(encoding="utf-8")
    locked_blob: dict[str, Any] = json.loads(locked_manifest_raw)

    base_raw = paths.base_resume.read_text(encoding="utf-8")
    base_digest = sha256_hex(base_raw)
    expected_locked = str(locked_blob.get("base_resume_json_hash") or "")
    if expected_locked and base_digest != expected_locked:
        msg = (
            "canonical base resume sha256 does not match locked_copy_manifest.base_resume_json_hash; "
            f"expected={expected_locked} actual={base_digest}"
        )
        raise ValueError(msg)

    by_manifest = {
        str(s.get("section_id")): s
        for s in (locked_blob.get("sections") or [])
        if isinstance(s, dict) and s.get("section_id")
    }

    sections_out: list[dict[str, Any]] = []
    lanes = rollup_blob.get("lanes") or {}
    if not isinstance(lanes, dict):
        raise ValueError("generated_lane_rollup.lanes must be an object")

    assemble_idx = 0
    for sid in CANONICAL_ASSEMBLED_SECTION_ORDER:
        if sid in GENERATED_LANE_IDS:
            lane = lanes.get(sid)
            if not isinstance(lane, dict):
                raise ValueError(f"rollup missing lane {sid}")
            rd = lane.get("latest_successful_real_artifact_path") or lane.get("rollup_source_run_dir")
            if not isinstance(rd, str) or not rd.strip():
                raise ValueError(f"lane {sid} missing latest_successful_real_artifact_path")
            run_dir = _resolved_run_dir(repo, rd)
            l2_path = run_dir / "l2_output.json"
            snapshot = json.loads(l2_path.read_text(encoding="utf-8"))
            raw_refs = lane.get("artifact_refs") or {}
            if not isinstance(raw_refs, dict):
                raw_refs = {}
            source_refs = _norm_artifact_refs(repo, {str(k): str(v) for k, v in raw_refs.items() if v})
            sec_hash = sha256_utf8(canonical_json_sorted(snapshot))
            x3_disp = source_refs.get("x3_disposition.json") or paths.rel(run_dir / "x3_disposition.json")
            disp_gen = {
                "rollup_lane_key": str(sid),
                "accepted_real_evidence_resolution": str(
                    lane.get("accepted_real_evidence_resolution") or "",
                ),
                "latest_successful_real_artifact_dir": paths.rel(run_dir),
                "x3_disposition_json": x3_disp,
                "rollup_artifact_refs": source_refs,
            }
            sections_out.append(
                {
                    "assemble_order": assemble_idx,
                    "section_id": sid,
                    "section_kind": "generated_lane",
                    "l2_output_snapshot": snapshot,
                    "section_hash": sec_hash,
                    "source_artifact_refs": {
                        **source_refs,
                        "generated_lane_rollup_json": paths.rel(paths.rollup_json),
                    },
                    "disposition_refs": {"generated_lane": disp_gen},
                },
            )
        elif sid in LOCKED_EMBEDDED_ORDER_IDS:
            mf = by_manifest.get(sid)
            if not isinstance(mf, dict):
                raise ValueError(f"locked_copy_manifest missing section {sid}")
            copied = mf.get("copied_text")
            if not isinstance(copied, str):
                raise ValueError(f"locked section {sid} copied_text invalid")
            sec_hash = sha256_utf8(copied)
            locked_disp = {
                "locked_copy_manifest_json": paths.rel(paths.locked_manifest),
                "locked_copy_x2_gate_outputs_json": paths.rel(paths.locked_x2),
            }
            sections_out.append(
                {
                    "assemble_order": assemble_idx,
                    "section_id": sid,
                    "section_kind": "locked_copy_inline",
                    "copied_text_exact": copied,
                    "section_hash": sec_hash,
                    "source_artifact_refs": {
                        "locked_copy_manifest_json": paths.rel(paths.locked_manifest),
                        "canonical_base_resume_json": paths.rel(paths.base_resume),
                        "locked_manifest_section_id": sid,
                    },
                    "disposition_refs": {"locked_copy": locked_disp},
                },
            )
        else:
            raise ValueError(f"unhandled canonical section id {sid}")

        assemble_idx += 1

    locked_invariants: dict[str, Any] = {}
    for inv_id in LOCKED_INVARIANT_IDS:
        mf = by_manifest.get(inv_id)
        if not isinstance(mf, dict):
            raise ValueError(f"locked_copy_manifest missing invariant {inv_id}")
        copied = mf.get("copied_text")
        if not isinstance(copied, str):
            raise ValueError(f"invariant {inv_id} copied_text invalid")
        sec_hash = sha256_utf8(copied)
        locked_disp = {
            "locked_copy_manifest_json": paths.rel(paths.locked_manifest),
            "locked_copy_x2_gate_outputs_json": paths.rel(paths.locked_x2),
        }
        locked_invariants[inv_id] = {
            "manifest_section_id": inv_id,
            "copied_text_exact": copied,
            "section_hash": sec_hash,
            "source_artifact_refs": {
                "locked_copy_manifest_json": paths.rel(paths.locked_manifest),
                "canonical_base_resume_json": paths.rel(paths.base_resume),
            },
            "disposition_refs": {"locked_copy": locked_disp},
        }

    recomputed_lines: list[str] = []
    for s in sections_out:
        recomputed_lines.append(f"{s.get('section_id')}:{s.get('section_hash')}")
    for ik in LOCKED_INVARIANT_IDS:
        sub = locked_invariants.get(ik) or {}
        recomputed_lines.append(f"invariant_{ik}:{sub.get('section_hash')}")
    final_hash = sha256_utf8("\n".join(recomputed_lines))

    final_resume: dict[str, Any] = {
        "assembled_object_id": ASSEMBLER_OBJECT_ID,
        "assembled_at_utc": datetime.now(timezone.utc).isoformat(),
        "assembler_module": "apps_rg.runtime.assembly.final_resume_assembler",
        "inputs": {
            "generated_lane_rollup_json": paths.rel(paths.rollup_json),
            "locked_copy_manifest_json": paths.rel(paths.locked_manifest),
            "canonical_base_resume_json": paths.rel(paths.base_resume),
        },
        "rollup_id": str(rollup_blob.get("rollup_id") or ""),
        "locked_manifest_id": str(locked_blob.get("manifest_id") or ""),
        "canonical_base_resume_sha256_hex": base_digest,
        "verified_base_resume_hash_matches_locked_manifest": bool(expected_locked) and base_digest == expected_locked,
        "sections": sections_out,
        "locked_copy_invariants": locked_invariants,
        "final_resume_hash": final_hash,
        "calls": {
            "provider_calls_made": False,
            "qwen_calls_made": False,
            "judge_calls_made": False,
            "docx_rendered": False,
        },
    }

    gate_results = run_final_resume_x2_gates(
        repo=repo,
        paths=paths,
        final_resume_blob=final_resume,
        rollup_blob=rollup_blob,
        locked_manifest_blob=locked_blob,
    )

    paths.output_dir.mkdir(parents=True, exist_ok=True)
    final_fp = paths.output_dir / "final_resume.json"
    final_fp.write_text(
        json.dumps(final_resume, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    gates_pass = gates_all_pass(gate_results)
    failed = failures(gate_results)

    manifest_fp = paths.output_dir / "final_resume_manifest.json"
    manifest_body = build_assembly_manifest(
        paths=paths,
        rollup_id=str(rollup_blob.get("rollup_id") or ""),
        rollup_generated_at_utc=str(rollup_blob.get("generated_at_utc") or ""),
        gates_passed=sum(1 for g in gate_results if g.pass_),
        gates_total=len(gate_results),
        failed_gate_ids=failed,
        final_resume_hash=final_hash,
    )
    manifest_fp.write_text(
        json.dumps(manifest_body, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    x2_fp = paths.output_dir / "final_resume_x2_gate_outputs.json"
    x2_blob = {
        "gate_family": "final_resume_assembly_x2",
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "all_pass": gates_pass,
        "failed_gate_ids": failed,
        "gates": [g.to_dict() for g in gate_results],
    }
    x2_fp.write_text(
        json.dumps(x2_blob, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    receipt_fp = paths.output_dir / "final_resume_receipt.json"
    receipt_blob = {
        "receipt_id": "final_resume_assembly_receipt_v1",
        "emitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "final_resume_json": paths.rel(final_fp),
        "final_resume_manifest_json": paths.rel(manifest_fp),
        "final_resume_x2_gate_outputs_json": paths.rel(x2_fp),
        "final_resume_hash": final_hash,
        "gates_all_pass": gates_pass,
        "failed_gate_ids": failed,
    }
    receipt_fp.write_text(
        json.dumps(receipt_blob, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    return {
        "paths": {
            "final_resume": final_fp,
            "manifest": manifest_fp,
            "x2": x2_fp,
            "receipt": receipt_fp,
        },
        "final_resume_blob": final_resume,
        "gates_all_pass": gates_pass,
        "failed_gate_ids": failed,
    }


def main() -> None:
    root = find_repo_root()
    res = assemble_final_resume(resolve_default_paths(root))
    print(f"ASSEMBLY_DONE gates_all_pass={res['gates_all_pass']} final_resume_hash={res['final_resume_blob']['final_resume_hash']}")
    if not res["gates_all_pass"]:
        print(f"FAILED_GATES:{','.join(res['failed_gate_ids'])}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
