"""Deterministic X2 gates for DOCX render evidence (final_resume + manifest + emitted docx)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.assembly.final_resume_x2 import (
    CANONICAL_ASSEMBLED_SECTION_ORDER,
    GENERATED_LANE_IDS,
    LOCKED_EMBEDDED_ORDER_IDS,
    LOCKED_INVARIANT_IDS,
    GateResult,
)

try:
    from docx import Document  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    Document = None  # type: ignore[misc, assignment]


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


def _doc_plaintext(doc_path: Path) -> str:
    if Document is None:
        raise RuntimeError("python-docx is required for DOCX render verification")
    doc = Document(str(doc_path))
    return "\n".join(p.text for p in doc.paragraphs)


def _ordered_find(haystack: str, needles: list[str]) -> bool:
    pos = 0
    for n in needles:
        if not n:
            continue
        i = haystack.find(n, pos)
        if i < 0:
            return False
        pos = i + len(n)
    return True


def candidate_identity_docx_verdict(hay: str, id_blob: Any) -> tuple[bool, str | None, Any]:
    """Check DOCX plaintext contains assembled ``candidate_identity`` strings verbatim.

    Returns ``(pass, failure_reason, observed)``. Skips (pass) when ``candidate_identity`` is
    absent (legacy ``final_resume``) or has no name/contact to verify.
    """
    if not isinstance(id_blob, dict):
        return True, None, "skipped_no_candidate_identity"
    cname = str(id_blob.get("candidate_name") or "").strip()
    hc_raw = id_blob.get("header_contact")
    hc = hc_raw if isinstance(hc_raw, dict) else {}
    if not cname and not hc:
        return True, None, "skipped_empty_identity_fields"
    if not (hay or "").strip():
        return False, "empty_docx_plaintext", {"candidate_name": cname, "has_contact": bool(hc)}
    if cname and cname not in hay:
        return False, "candidate_name not found verbatim", cname
    needles: list[str] = []
    if hc:
        order_ct = ("phone", "email", "linkedin", "github", "location")
        needles = [str(hc[k]).strip() for k in order_ct if hc.get(k) and str(hc[k]).strip()]
        if needles and not _ordered_find(hay, needles):
            return False, "header_contact fields not found in document order", needles
    return True, None, {"candidate_name_set": bool(cname), "contact_field_count": len(needles)}


def run_docx_render_x2_gates(
    *,
    repo_root: Path,
    render_manifest_blob: dict[str, Any],
    final_resume_blob: dict[str, Any],
    docx_manifest_blob: dict[str, Any],
    final_resume_path: Path,
    docx_manifest_path: Path,
    docx_output_path: Path,
    receipt_path: Path,
    output_dir: Path,
    expected_docx_basename: str,
) -> list[GateResult]:
    gates: list[GateResult] = []
    _ = repo_root

    _add(
        gates,
        "x2_docx_file_created",
        docx_output_path.is_file(),
        str(docx_output_path),
        "file exists",
    )

    src = render_manifest_blob.get("sources") or {}
    logical = str(src.get("final_resume_hash_logical") or "").strip()
    fr_log = str(final_resume_blob.get("final_resume_hash") or "").strip()
    _add(gates, "x2_docx_source_final_resume_hash_matches", logical == fr_log and bool(logical), logical, fr_log)

    mf_sha_recorded = str(src.get("docx_manifest_sha256_bytes") or "").strip()
    mf_sha_actual = hashlib.sha256(docx_manifest_path.read_bytes()).hexdigest() if docx_manifest_path.is_file() else ""
    _add(
        gates,
        "x2_docx_source_manifest_hash_matches",
        bool(mf_sha_recorded) and mf_sha_recorded == mf_sha_actual,
        mf_sha_recorded,
        mf_sha_actual,
    )

    mo = [str(x) for x in (render_manifest_blob.get("section_render_order") or [])]
    canon = list(CANONICAL_ASSEMBLED_SECTION_ORDER)
    dm = [str(x) for x in (docx_manifest_blob.get("section_render_order") or [])]
    _add(
        gates,
        "x2_docx_section_order_matches_manifest",
        mo == dm and mo == canon,
        mo,
        canon,
    )

    inv_order = docx_manifest_blob.get("locked_copy_invariants_projection_order")
    inv_order_list = (
        list(inv_order) if isinstance(inv_order, list) else list(LOCKED_INVARIANT_IDS)
    )
    inv_order_list = [str(x) for x in inv_order_list]

    evid = render_manifest_blob.get("render_evidence") or []
    evid_l = evid if isinstance(evid, list) else []
    by_sid: dict[str, dict[str, Any]] = {}
    for r in evid_l:
        if isinstance(r, dict) and r.get("section_id"):
            by_sid[str(r["section_id"])] = r

    narrative_ids = canon
    all_rendered_ok = True
    missing_reason = ""
    for sec_id in narrative_ids + inv_order_list:
        row = by_sid.get(sec_id)
        if not isinstance(row, dict) or int(row.get("block_count") or 0) < 1:
            all_rendered_ok = False
            missing_reason = f"missing render row for {sec_id}"
            break
        eb = row.get("expected_plaintext_blocks")
        if not isinstance(eb, list) or len(eb) == 0:
            all_rendered_ok = False
            missing_reason = f"empty plaintext blocks for {sec_id}"
            break
    _add(
        gates,
        "x2_docx_all_sections_rendered",
        all_rendered_ok,
        sorted(by_sid.keys()),
        [*narrative_ids, *inv_order_list],
        missing_reason if not all_rendered_ok else None,
    )

    hay = ""
    if docx_output_path.is_file() and Document is not None:
        try:
            hay = _doc_plaintext(docx_output_path)
        except (OSError, RuntimeError, ValueError):  # guardian: allow-default-fallback -- P2 burndown: fail-soft optional boundary
            hay = ""

    id_ok, id_fail, id_obs = candidate_identity_docx_verdict(hay, final_resume_blob.get("candidate_identity"))
    _add(
        gates,
        "x2_docx_candidate_identity_verbatim",
        id_ok,
        id_obs,
        None,
        id_fail,
    )

    gen_blocks: list[str] = []
    for sid in GENERATED_LANE_IDS:
        row = by_sid.get(sid)
        eb = row.get("expected_plaintext_blocks") if isinstance(row, dict) else None
        if isinstance(eb, list):
            gen_blocks.extend(str(x) for x in eb)
    gen_ok = bool(hay) and _ordered_find(hay, gen_blocks)
    _add(gates, "x2_docx_generated_text_preserved", gen_ok, len(gen_blocks), "ordered substrings")

    lock_blocks: list[str] = []
    for sid in LOCKED_EMBEDDED_ORDER_IDS:
        row = by_sid.get(sid)
        eb = row.get("expected_plaintext_blocks") if isinstance(row, dict) else None
        if isinstance(eb, list):
            lock_blocks.extend(str(x) for x in eb)
    lock_ok = bool(hay) and _ordered_find(hay, lock_blocks)
    _add(gates, "x2_docx_locked_copy_preserved", lock_ok, len(lock_blocks), "ordered substrings")

    inv_blob = final_resume_blob.get("locked_copy_invariants")
    inv_blob = inv_blob if isinstance(inv_blob, dict) else {}

    def inv_list(key: str) -> Any:
        sub = inv_blob.get(key)
        if not isinstance(sub, dict):
            return None
        raw = sub.get("copied_text_exact")
        if not isinstance(raw, str):
            return None
        return json.loads(raw)

    cmp_ok = True
    try:
        cn = inv_list("company_names")
        if not isinstance(cn, list):
            cmp_ok = False
        elif hay:
            cmp_ok = _ordered_find(hay, [str(x) for x in cn])
        else:
            cmp_ok = False
    except (json.JSONDecodeError, TypeError, KeyError):
        cmp_ok = False
    _add(gates, "x2_docx_company_names_preserved", cmp_ok, cmp_ok)

    ttl_ok = True
    try:
        tt = inv_list("titles")
        if not isinstance(tt, list) or not hay:
            ttl_ok = False
        else:
            ttl_ok = _ordered_find(hay, [str(x) for x in tt])
    except (json.JSONDecodeError, TypeError, KeyError):
        ttl_ok = False
    _add(gates, "x2_docx_titles_preserved", ttl_ok, ttl_ok)

    loc_ok = True
    try:
        lc = inv_list("locations")
        if not isinstance(lc, list) or not hay:
            loc_ok = False
        else:
            loc_ok = _ordered_find(hay, [str(x) for x in lc])
    except (json.JSONDecodeError, TypeError, KeyError):
        loc_ok = False
    _add(gates, "x2_docx_locations_preserved", loc_ok, loc_ok)

    dates_ok = True
    try:
        dr = inv_list("dates")
        if not isinstance(dr, list) or not hay:
            dates_ok = False
        else:
            for row in dr:
                if not isinstance(row, dict):
                    dates_ok = False
                    break
                for k in ("start_date", "end_date"):
                    v = row.get(k)
                    if v is None:
                        continue
                    if str(v) not in hay:
                        dates_ok = False
                        break
                if not dates_ok:
                    break
    except (json.JSONDecodeError, TypeError, KeyError):
        dates_ok = False
    _add(gates, "x2_docx_dates_preserved", dates_ok, dates_ok)

    allowed = frozenset(
        {
            "docx_render_manifest.json",
            "docx_render_x2_gate_outputs.json",
            "docx_render_receipt.json",
            expected_docx_basename,
        },
    )
    allowed_lc = frozenset({name.lower() for name in allowed})
    prov = []
    qwen = []
    judge = []
    stray = []
    if output_dir.is_dir():
        for f in output_dir.iterdir():
            if not f.is_file():
                continue
            ln = f.name.lower()
            if ln not in allowed_lc:
                stray.append(f.name)
                continue
            if "provider_" in ln and ln.endswith(".json"):
                prov.append(f.name)
            if "qwen" in ln:
                qwen.append(f.name)
            if "x1d" in ln or "llm_judge" in ln:
                judge.append(f.name)
    stray_ok = len(stray) == 0
    _add(
        gates,
        "x2_docx_no_provider_calls",
        len(prov) == 0 and stray_ok,
        {"provider_hits": prov, "unexpected_files": stray},
        [],
    )
    _add(
        gates,
        "x2_docx_no_qwen_calls",
        len(qwen) == 0 and stray_ok,
        {"qwen_hits": qwen, "unexpected_files": stray},
        [],
    )
    _add(
        gates,
        "x2_docx_no_judge_calls",
        len(judge) == 0 and stray_ok,
        {"judge_hits": judge, "unexpected_files": stray},
        [],
    )

    _add(
        gates,
        "x2_docx_render_receipt_present",
        receipt_path.is_file(),
        str(receipt_path),
        "receipt exists",
    )

    return gates


def gates_all_pass(results: list[GateResult]) -> bool:
    return all(r.pass_ for r in results)


def failures(results: list[GateResult]) -> list[str]:
    return [r.gate_id for r in results if not r.pass_]


def gate_records_to_blob(
    gates: list[GateResult],
    *,
    evaluated_at_utc: str,
    all_pass_res: bool,
    failed_gate_ids_res: list[str],
) -> dict[str, Any]:
    return {
        "gate_family": "docx_render_x2",
        "evaluated_at_utc": evaluated_at_utc,
        "all_pass": all_pass_res,
        "failed_gate_ids": failed_gate_ids_res,
        "gates": [g.to_dict() for g in gates],
    }
