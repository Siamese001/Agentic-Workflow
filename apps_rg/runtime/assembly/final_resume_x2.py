"""Deterministic X2 gates for final resume assembly evidence (no provider/judge/registry)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths, resolve_default_paths

CANONICAL_ASSEMBLED_SECTION_ORDER: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "unify_narrative",
    "unify_bullets",
    "ibm_narrative",
    "ibm_bullets",
    "insurtech",
    "ey",
    "early_career",
    "competencies",
    "education",
    "certifications",
)

LOCKED_EMBEDDED_ORDER_IDS: tuple[str, ...] = (
    "insurtech",
    "ey",
    "early_career",
    "education",
    "certifications",
)

LOCKED_INVARIANT_IDS: tuple[str, ...] = ("company_names", "titles", "locations", "dates")

GENERATED_LANE_IDS: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "unify_narrative",
    "unify_bullets",
    "ibm_narrative",
    "ibm_bullets",
    "competencies",
)


def canonical_json_sorted(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_utf8(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class GateResult:
    gate_id: str
    gate_type: str
    pass_: bool
    observed_value: Any
    threshold: Any | None = None
    failure_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["pass"] = d.pop("pass_")
        return d


def _add(
    out: list[GateResult],
    gate_id: str,
    ok: bool,
    observed: Any,
    thresh: Any = None,
    fail: str | None = None,
) -> None:
    out.append(
        GateResult(
            gate_id=gate_id,
            gate_type="deterministic",
            pass_=ok,
            observed_value=observed,
            threshold=thresh,
            failure_reason=None if ok else fail,
        ),
    )


def _run_rel_path(repo_root: Path, rel: str) -> Path:
    rel_norm = rel.replace("\\", "/")
    while rel_norm.startswith("./"):
        rel_norm = rel_norm[2:]
    return (repo_root / rel_norm).resolve()


def run_final_resume_x2_gates(
    *,
    repo: Path,
    paths: FinalResumePaths | None = None,
    final_resume_blob: dict[str, Any],
    rollup_blob: dict[str, Any],
    locked_manifest_blob: dict[str, Any],
) -> list[GateResult]:
    gates: list[GateResult] = []
    paths = paths or resolve_default_paths(repo)
    repo_root = paths.repo_root

    sections = final_resume_blob.get("sections") or []
    ids_in_order = [str(s.get("section_id")) for s in sections if isinstance(s, dict)]
    req = list(CANONICAL_ASSEMBLED_SECTION_ORDER)

    set_ok = set(ids_in_order) == set(req)
    _add(
        gates,
        "x2_all_required_sections_present",
        set_ok,
        ids_in_order,
        sorted(req),
        None if set_ok else "missing or unexpected section ids",
    )

    order_ok = ids_in_order == req
    _add(
        gates,
        "x2_section_order_valid",
        order_ok,
        ids_in_order,
        req,
        None if order_ok else "assembled section ordering invalid",
    )

    lanes = rollup_blob.get("lanes") or {}
    gen_ok = True
    gen_reason = "ok"
    for lane in GENERATED_LANE_IDS:
        row = lanes.get(lane)
        if not isinstance(row, dict):
            gen_ok = False
            gen_reason = f"missing lane {lane}"
            break
        accepted = str(row.get("accepted_real_evidence_resolution") or "")
        if accepted not in ("latest_successful_real_run.json", "coherent_aggregation_pin"):
            gen_ok = False
            gen_reason = f"{lane} resolution not accepted: {accepted}"
            break
        rd = row.get("latest_successful_real_artifact_path") or row.get("rollup_source_run_dir")
        if str(rd or "").strip() == "":
            gen_ok = False
            gen_reason = f"{lane} missing latest_successful_real_artifact_path"
            break

    _add(gates, "x2_generated_sections_from_latest_successful_real", gen_ok, gen_reason, "rollup pointer contract")

    by_manifest = {
        str(s.get("section_id")): s
        for s in (locked_manifest_blob.get("sections") or [])
        if isinstance(s, dict) and s.get("section_id")
    }
    lock_ok = True
    lr = "ok"
    for lid in LOCKED_EMBEDDED_ORDER_IDS + LOCKED_INVARIANT_IDS:
        if lid not in by_manifest:
            lock_ok = False
            lr = f"missing manifest section {lid}"
            break
    _add(
        gates,
        "x2_locked_sections_from_locked_copy_manifest",
        lock_ok,
        lr,
        list(LOCKED_EMBEDDED_ORDER_IDS) + list(LOCKED_INVARIANT_IDS),
    )

    l2_snap_ok = True
    sr = "ok"
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        sid = str(sec.get("section_id", ""))
        if sec.get("section_kind") != "generated_lane":
            continue
        if sid not in GENERATED_LANE_IDS:
            continue
        lane = lanes.get(sid)
        if not isinstance(lane, dict):
            l2_snap_ok = False
            sr = f"rollup missing {sid}"
            break
        rd = lane.get("latest_successful_real_artifact_path") or lane.get("rollup_source_run_dir")
        if not isinstance(rd, str) or not rd:
            l2_snap_ok = False
            sr = f"no run dir for {sid}"
            break
        l2p = _run_rel_path(repo_root, rd) / "l2_output.json"
        try:
            from_disk = json.loads(l2p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            l2_snap_ok = False
            sr = f"{sid} l2 read failed: {exc}"
            break
        snap = sec.get("l2_output_snapshot")
        if from_disk != snap:
            l2_snap_ok = False
            sr = f"{sid} snapshot mismatch vs {paths.rel(l2p)}"
            break

    _add(gates, "x2_no_generated_section_rewritten", l2_snap_ok, sr, "l2 equality")

    lc_ok = True
    lx = "ok"
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        if sec.get("section_kind") != "locked_copy_inline":
            continue
        sid = str(sec.get("section_id"))
        mf = by_manifest.get(sid)
        if not mf:
            lc_ok = False
            lx = f"no manifest slice {sid}"
            break
        if sec.get("copied_text_exact") != mf.get("copied_text"):
            lc_ok = False
            lx = f"locked inline {sid} copied_text mismatch"
            break
    _add(gates, "x2_no_locked_copy_rewritten", lc_ok, lx, "manifest copied_text equality")

    inv_blob = final_resume_blob.get("locked_copy_invariants") or {}
    for inv_id in LOCKED_INVARIANT_IDS:
        gname = {
            "company_names": "x2_company_names_preserved",
            "titles": "x2_titles_preserved",
            "locations": "x2_locations_preserved",
            "dates": "x2_dates_preserved",
        }[inv_id]
        row_inv = inv_blob.get(inv_id) if isinstance(inv_blob, dict) else None
        mf = by_manifest.get(inv_id)
        ok_iv = isinstance(row_inv, dict) and isinstance(mf, dict) and row_inv.get("copied_text_exact") == mf.get(
            "copied_text",
        )
        _add(gates, gname, ok_iv, inv_id if ok_iv else (row_inv, mf))

    edu_sec = next((s for s in sections if isinstance(s, dict) and s.get("section_id") == "education"), None)
    mf_edu = by_manifest.get("education")
    ok_edu = isinstance(edu_sec, dict) and isinstance(mf_edu, dict) and edu_sec.get("copied_text_exact") == mf_edu.get(
        "copied_text",
    )
    _add(gates, "x2_education_preserved", ok_edu, "education" if ok_edu else ("section", mf_edu))

    cert_sec = next((s for s in sections if isinstance(s, dict) and s.get("section_id") == "certifications"), None)
    mf_cert = by_manifest.get("certifications")
    ok_cert = (
        isinstance(cert_sec, dict)
        and isinstance(mf_cert, dict)
        and cert_sec.get("copied_text_exact") == mf_cert.get("copied_text")
    )
    _add(gates, "x2_certifications_preserved", ok_cert, "certifications" if ok_cert else ("section", mf_cert))

    hash_match_ok = True
    hm = "ok"

    def _expected_inline_hash(sec: dict[str, Any]) -> tuple[str | None, str]:
        sid = str(sec.get("section_id", ""))
        kind = sec.get("section_kind")
        if kind == "generated_lane":
            return sha256_utf8(canonical_json_sorted(sec.get("l2_output_snapshot"))), sid
        if kind == "locked_copy_inline":
            return sha256_utf8(str(sec.get("copied_text_exact"))), sid
        return None, sid

    for sec in sections:
        if not isinstance(sec, dict):
            continue
        expect, sid = _expected_inline_hash(sec)
        if expect is None:
            hash_match_ok = False
            hm = f"unknown section_kind for {sid}"
            break
        if str(sec.get("section_hash")) != expect:
            hash_match_ok = False
            hm = f"section_hash mismatch for {sid}"
            break

    if hash_match_ok and isinstance(inv_blob, dict):
        for ik in LOCKED_INVARIANT_IDS:
            sub = inv_blob.get(ik)
            ct = None
            if isinstance(sub, dict):
                ct = sub.get("copied_text_exact")
            expect_iv = sha256_utf8(str(ct))
            declared_iv = "" if not isinstance(sub, dict) else str(sub.get("section_hash"))
            if declared_iv != expect_iv:
                hash_match_ok = False
                hm = f"invariant_hash mismatch for {ik}"
                break

    digest_ok = True
    digest_reason = "ok"
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        sh = str(sec.get("section_hash") or "")
        sd = str(sec.get("section_digest") or "")
        if not sd:
            digest_ok = False
            digest_reason = f"missing section_digest for {sec.get('section_id')}"
            break
        if sh == sd and sec.get("section_kind") == "generated_lane":
            digest_reason = f"section_hash equals section_digest for {sec.get('section_id')} (must differ)"
            digest_ok = False
            break
    _add(gates, "x2_section_digest_present", digest_ok, digest_reason)

    _add(gates, "x2_section_hashes_present", hash_match_ok, hm)

    fh = str(final_resume_blob.get("final_resume_hash") or "")
    fr_ok = bool(fh)
    recomputed_lines: list[str] = []
    for s in sections:
        if isinstance(s, dict):
            recomputed_lines.append(f"{s.get('section_id')}:{s.get('section_hash','')}")
    inv = final_resume_blob.get("locked_copy_invariants") or {}
    if isinstance(inv, dict):
        for ik in LOCKED_INVARIANT_IDS:
            sub = inv.get(ik)
            if isinstance(sub, dict):
                recomputed_lines.append(f"invariant_{ik}:{sub.get('section_hash','')}")
    recomputed = sha256_utf8("\n".join(recomputed_lines))
    fr_match = fh == recomputed
    _add(
        gates,
        "x2_final_resume_hash_present",
        fr_ok and fr_match,
        fh,
        recomputed,
        None if (fr_ok and fr_match) else "final_resume_hash missing or mismatched recomputation",
    )

    refs_ok = True
    disp_ok_all = True
    for s in sections:
        if not isinstance(s, dict):
            continue
        refs = s.get("source_artifact_refs")
        disp = s.get("disposition_refs") or {}
        if not isinstance(refs, dict) or not refs:
            refs_ok = False
            break
        if s.get("section_kind") == "generated_lane":
            gl = disp.get("generated_lane")
            if (
                not isinstance(gl, dict)
                or not gl.get("x3_disposition_json")
                or not gl.get("rollup_lane_key")
                or not gl.get("accepted_real_evidence_resolution")
            ):
                disp_ok_all = False
                break
        if s.get("section_kind") == "locked_copy_inline":
            lk = disp.get("locked_copy")
            if (
                not isinstance(lk, dict)
                or not lk.get("locked_copy_manifest_json")
                or not lk.get("locked_copy_x2_gate_outputs_json")
            ):
                disp_ok_all = False
                break

    inv_refs = isinstance(inv_blob, dict)
    inv_disp = True
    for k in LOCKED_INVARIANT_IDS:
        sub = inv_blob.get(k) if isinstance(inv_blob, dict) else None
        inv_refs = inv_refs and isinstance(sub, dict) and isinstance(sub.get("source_artifact_refs"), dict)
        if not isinstance(sub, dict):
            inv_disp = False
            break
        lcsub = (sub.get("disposition_refs") or {}).get("locked_copy")
        if (
            not isinstance(lcsub, dict)
            or not lcsub.get("locked_copy_manifest_json")
            or not lcsub.get("locked_copy_x2_gate_outputs_json")
        ):
            inv_disp = False
            break

    _add(
        gates,
        "x2_artifact_refs_present",
        refs_ok and inv_refs and disp_ok_all and inv_disp,
        {
            "artifact_refs_ok": refs_ok,
            "invariant_refs_ok": inv_refs,
            "section_disposition_refs_ok": disp_ok_all,
            "invariant_disposition_refs_ok": inv_disp,
        },
    )

    out_dir = paths.output_dir

    allowed_artifact_files = frozenset(
        {
            "final_resume.json",
            "final_resume_manifest.json",
            "final_resume_x2_gate_outputs.json",
            "final_resume_receipt.json",
        },
    )
    prov_hits: list[str] = []
    qwen_hits: list[str] = []
    judge_hits: list[str] = []
    docx_hits: list[str] = []
    if out_dir.is_dir():
        for f in sorted(out_dir.iterdir(), key=lambda p: p.name):
            if not f.is_file():
                continue
            name = f.name.lower()
            if name not in allowed_artifact_files:
                pass
            if "provider_" in name and name.endswith(".json"):
                prov_hits.append(f.name)
            if "qwen" in name or name == "real_l2_generation_result.json":
                qwen_hits.append(f.name)
            if "x1d" in name or "llm_judge" in name or "judge" in name:
                judge_hits.append(f.name)
            if name.endswith(".docx"):
                docx_hits.append(f.name)

    _add(gates, "x2_no_provider_calls", len(prov_hits) == 0, prov_hits, [])
    _add(gates, "x2_no_qwen_calls", len(qwen_hits) == 0, qwen_hits, [])
    _add(gates, "x2_no_judge_calls", len(judge_hits) == 0, judge_hits, [])
    _add(gates, "x2_no_docx_render", len(docx_hits) == 0, docx_hits, [])

    return gates


def gates_all_pass(results: list[GateResult]) -> bool:
    return all(r.pass_ for r in results)


def failures(results: list[GateResult]) -> list[str]:
    return [r.gate_id for r in results if not r.pass_]
