"""Deterministic merge: modular lane L2 snapshots + base resume → rg_output_schema JSON (no providers).

``rg_output_schema.json`` is product-shaped; lane L2 payloads and assembler ``final_resume_assembled_v1`` are not.
This module maps validated lane outputs plus locked/base employment into a single schema-valid document
when inputs satisfy gates (and optional REAL_LLM-only policy).
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Mapping

from apps_rg.l2_recipe.rg_output_jsonschema_validate import validate_rg_output_object
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_product_shape_export_bounds import (
    COMPETENCIES_EXPORT_MAX_CATEGORIES,
    EXEC_SUMMARY_EXPORT_MAX_CHARS,
    EXEC_SUMMARY_EXPORT_MAX_WORDS,
    EXEC_SUMMARY_EXPORT_MIN_WORDS,
    RG_BULLET_MAX_CHARS,
)

# Locked roles that are not driven by generated lanes must provide enough base bullets to
# populate ``rg_output.sections.experience[*].bullets``. Default minimum is three (schema);
# ``exp_early_career_001`` is allowed one bullet per résumé SSOT.
_MIN_LOCKED_BULLETS_BY_FACT_ID: Final[Mapping[str, int]] = {"exp_early_career_001": 1}

_MONTHS: Final[tuple[str, ...]] = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _facts(base: dict[str, Any]) -> dict[str, Any]:
    return base.get("facts", base) if isinstance(base.get("facts"), dict) else base


def _word_count(text: str) -> int:
    # Whitespace tokens — the SAME counter the lane word-budget rung and X2 caps
    # use (len(text.split())). The previous \b\w+\b regex counted hyphenated/
    # slashed compounds as multiple words, so a lane-certified 140-word exec
    # summary re-counted as 144 here and export rejected the certified product
    # (patch_run_22, 2026-06-11). One tokenizer, one authority.
    return len(text.split())


def _parse_year_month(raw: str) -> tuple[int, int] | None:
    s = raw.strip()
    m = re.match(r"^(\d{4})-(\d{2})$", s)
    if not m:
        return None
    y, mo = int(m.group(1)), int(m.group(2))
    if not 1 <= mo <= 12:
        return None
    return y, mo


def _format_rg_dates(start_date: str, end_date: str, *, is_current: bool) -> str:
    """Shape employment dates for rg_output_schema pattern (en-dash)."""
    sm = _parse_year_month(start_date) if start_date else None
    start_part = ""
    if sm:
        y, mo = sm
        start_part = f"{_MONTHS[mo - 1]} {y}"
    elif re.match(r"^\d{4}$", start_date.strip()):
        start_part = start_date.strip()
    elif re.match(r"^pre[- ]?2002$", start_date.strip(), re.I):
        start_part = "Pre-2002"
    else:
        start_part = start_date.strip() or "Jan 2020"

    end_low = end_date.strip().lower()
    if is_current or end_low in {"present", "current", ""}:
        return f"{start_part} \u2013 Present"
    em = _parse_year_month(end_date)
    if em:
        y, mo = em
        return f"{start_part} \u2013 {_MONTHS[mo - 1]} {y}"
    if re.match(r"^\d{4}$", end_date.strip()):
        return f"{start_part} \u2013 {end_date.strip()}"
    return f"{start_part} \u2013 {end_date.strip() or 'Present'}"


def _norm_bullet_text(raw: str) -> str:
    t = " ".join(raw.split())
    return t.strip()


def _maybe_truncate_bullet_text(text: str, export_warnings: list[str] | None) -> str:
    if len(text) > RG_BULLET_MAX_CHARS:
        if export_warnings is not None and "bullet_text_truncated" not in export_warnings:
            export_warnings.append("bullet_text_truncated")
        head = text[: max(0, RG_BULLET_MAX_CHARS - 3)].rstrip()
        boundary = head.rfind(" ")
        if boundary >= int(RG_BULLET_MAX_CHARS * 0.65):
            head = head[:boundary].rstrip()
        return head.rstrip(" ,;:") + "..."
    return text


def _lane_bullets_to_rg(
    lane_bullets: list[Any],
    *,
    max_bullets: int = 5,
    min_bullets: int = 3,
    export_warnings: list[str] | None = None,
) -> tuple[list[dict[str, Any]] | None, str]:
    if not isinstance(lane_bullets, list):
        return None, "lane_bullets_not_list"
    rows: list[dict[str, Any]] = []
    for b in lane_bullets[:max_bullets]:
        if not isinstance(b, dict):
            continue
        text = _norm_bullet_text(str(b.get("text") or b.get("bullet_text") or ""))
        if len(text) < 20:
            return None, "bullet_text_too_short"
        text = _maybe_truncate_bullet_text(text, export_warnings)
        ent: dict[str, Any] = {"text": text}
        sid = b.get("source_fact_id") or b.get("bullet_id") or b.get("fact_id")
        if sid:
            ent["source_id"] = str(sid)
        if b.get("has_metric") is not None:
            ent["has_metric"] = bool(b.get("has_metric"))
        rows.append(ent)
    if len(rows) < min_bullets:
        return None, "insufficient_lane_bullets"
    return rows, ""


def _competencies_to_skills(competencies: Any) -> dict[str, Any] | None:
    if not isinstance(competencies, list) or not competencies:
        return None
    categories: list[dict[str, Any]] = []
    for cat in competencies[:COMPETENCIES_EXPORT_MAX_CATEGORIES]:
        if not isinstance(cat, dict):
            continue
        cat_name = str(cat.get("category_label") or "").strip() or "Capabilities"
        terms_raw = cat.get("terms") or []
        items: list[str] = []
        if isinstance(terms_raw, list):
            for t in terms_raw[:8]:
                if isinstance(t, dict):
                    txt = str(t.get("text") or "").strip()
                else:
                    txt = str(t).strip()
                if txt and txt not in items:
                    items.append(txt)
        if not items:
            continue
        categories.append({"name": cat_name, "items": items[:8]})
    if not categories:
        return None
    return {"categories": categories}


def _education_from_base(base: dict[str, Any]) -> list[dict[str, Any]]:
    edu = list(_facts(base).get("education") or [])
    out: list[dict[str, Any]] = []
    for e in edu:
        if not isinstance(e, dict):
            continue
        rec: dict[str, Any] = {
            "degree": str(e.get("degree") or "").strip(),
            "institution": str(e.get("institution") or "").strip(),
        }
        if len(rec["degree"]) < 2:
            continue
        if len(rec["institution"]) < 2:
            continue
        y = e.get("year")
        if y is not None and y != "":
            ys = str(y).strip()
            if re.match(r"^\d{4}$", ys):
                rec["year"] = ys
        maj = e.get("major")
        if isinstance(maj, str) and maj.strip():
            rec["major"] = maj.strip()
        hon = e.get("honors")
        if isinstance(hon, str) and hon.strip():
            rec["honors"] = hon.strip()
        out.append(rec)
    return out


def _certs_from_base(base: dict[str, Any]) -> list[dict[str, Any]]:
    certs = list(_facts(base).get("certifications") or [])
    out: list[dict[str, Any]] = []
    for c in certs:
        if not isinstance(c, dict):
            continue
        name = str(c.get("name") or "").strip()
        if not name:
            continue
        issuer = str(c.get("issuer") or c.get("issuing_organization") or "").strip()
        row: dict[str, Any] = {"name": name}
        if issuer:
            row["issuer"] = issuer
        yr = c.get("year") or c.get("date")
        if yr is not None and str(yr).strip():
            row["date"] = str(yr).strip()
        out.append(row)
    return out


def _candidate_name(base: dict[str, Any]) -> str:
    if isinstance(base.get("candidate_name"), str) and base["candidate_name"].strip():
        return base["candidate_name"].strip()
    hdr = base.get("header")
    if isinstance(hdr, dict):
        n = str(hdr.get("name") or "").strip()
        if n:
            return n
    return ""


def _contact_from_base(base: dict[str, Any]) -> dict[str, str]:
    """Header contact fields aligned with base resume (phone, email, linkedin, github)."""
    facts = _facts(base)
    hdr_top = base.get("header") if isinstance(base.get("header"), dict) else {}
    hdr_facts = facts.get("header") if isinstance(facts.get("header"), dict) else {}
    merged: dict[str, Any] = {**hdr_facts, **hdr_top}
    out: dict[str, str] = {}
    for k in ("phone", "email", "linkedin", "github"):
        raw = merged.get(k)
        if raw is None:
            continue
        s = str(raw).strip()
        if s:
            out[k] = s
    return out


@dataclass
class RgOutputBuildResult:
    """Outcome of deterministic rg_output construction (merge uses no providers)."""

    rg_output: dict[str, Any] | None
    ok: bool
    failure_reason: str
    schema_valid: bool
    schema_error: str
    merge_receipt: dict[str, Any] = field(default_factory=dict)
    provider_called: bool = False
    synthesized_sections_detected: bool = False


def _fp16(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_rg_output_from_modular_sections(
    *,
    lane_l2_by_id: Mapping[str, Any],
    base_resume: dict[str, Any],
    input_package: Any,
    modular_root: Path,
    artifact_dir: Path,
    run_id: str,
    reject_mocked_lanes: bool = True,
    generated_at_utc: str | None = None,
) -> RgOutputBuildResult:
    """Merge lane L2 dicts and canonical base resume into rg_output_schema-shaped JSON.

    * **Fails** if any required lane is missing, narratives empty, executive summary invalid,
      competencies missing, or schema validation fails.
    * If *reject_mocked_lanes* is True, any lane with ``runtime_generation_status == MOCKED``
      fails the merge (plumbing-only lanes cannot authorize recipe context).
    """
    art = artifact_dir.resolve()
    receipt: dict[str, Any] = {
        "builder_id": "modular_rg_output_builder_v1",
        "run_id": run_id,
        "reject_mocked_lanes": reject_mocked_lanes,
        "lanes_seen": sorted(lane_l2_by_id.keys()),
        "required_lanes": list(GENERATED_LANES),
        "provider_called": False,
        "synthesized_sections_detected": False,
        "no_synthetic_bullets_assertion": True,
        "locked_employment_source_count": 0,
        "locked_employment_mapped_count": 0,
        "compact_early_career_excluded_count": 0,
        "excluded_locked_roles": [],
        "export_shape_warnings": [],
    }
    export_warnings: list[str] = receipt["export_shape_warnings"]

    gen_at = generated_at_utc or datetime.now(timezone.utc).isoformat()

    if reject_mocked_lanes:
        for lk, blob in lane_l2_by_id.items():
            if not isinstance(blob, dict):
                receipt["failure"] = f"lane_not_object:{lk}"
                return RgOutputBuildResult(
                    None,
                    False,
                    receipt["failure"],
                    False,
                    receipt["failure"],
                    receipt,
                )
            st = str(blob.get("runtime_generation_status") or "").strip().upper()
            if st == "MOCKED":
                receipt["failure"] = f"mocked_lane_rejected:{lk}"
                return RgOutputBuildResult(
                    None,
                    False,
                    receipt["failure"],
                    False,
                    receipt["failure"],
                    receipt,
                )

    missing = [lk for lk in GENERATED_LANES if lk not in lane_l2_by_id]
    if missing:
        r = f"missing_required_lanes:{','.join(missing)}"
        receipt["failure"] = r
        return RgOutputBuildResult(None, False, r, False, r, receipt)

    headline = lane_l2_by_id["headline"]
    exec_l2 = lane_l2_by_id["executive_summary"]
    uni_b = lane_l2_by_id["unify_bullets"]
    uni_n = lane_l2_by_id["unify_narrative"]
    ibm_b = lane_l2_by_id["ibm_bullets"]
    ibm_n = lane_l2_by_id["ibm_narrative"]
    insurtech_b = lane_l2_by_id["insurtech_bullets"]
    insurtech_n = lane_l2_by_id["insurtech_narrative"]
    ey_b = lane_l2_by_id["ey_bullets"]
    ey_n = lane_l2_by_id["ey_narrative"]
    comp_l2 = lane_l2_by_id["competencies"]

    for label, blob in (
        ("headline", headline),
        ("executive_summary", exec_l2),
        ("unify_bullets", uni_b),
        ("unify_narrative", uni_n),
        ("ibm_bullets", ibm_b),
        ("ibm_narrative", ibm_n),
        ("insurtech_bullets", insurtech_b),
        ("insurtech_narrative", insurtech_n),
        ("ey_bullets", ey_b),
        ("ey_narrative", ey_n),
        ("competencies", comp_l2),
    ):
        if not isinstance(blob, dict):
            receipt["failure"] = f"lane_payload_invalid:{label}"
            return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    uni_narrative_sentence = str(uni_n.get("narrative_sentence") or "").strip()
    ibm_narrative_sentence = str(ibm_n.get("narrative_sentence") or "").strip()
    insurtech_narrative_sentence = str(insurtech_n.get("narrative_sentence") or "").strip()
    ey_narrative_sentence = str(ey_n.get("narrative_sentence") or "").strip()

    hl = str(headline.get("headline_line") or "").strip()
    if not hl:
        receipt["failure"] = "missing_headline_line"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    exec_text = str(exec_l2.get("resume_display_text") or "").strip()
    if len(exec_text) < 10:
        receipt["failure"] = "missing_executive_summary"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)
    wc = _word_count(exec_text)
    if (
        wc < EXEC_SUMMARY_EXPORT_MIN_WORDS
        or wc > EXEC_SUMMARY_EXPORT_MAX_WORDS
        or len(exec_text) > EXEC_SUMMARY_EXPORT_MAX_CHARS
    ):
        receipt["failure"] = "executive_summary_out_of_rg_bounds"
        receipt["export_bounds"] = {
            "word_count": wc,
            "max_words": EXEC_SUMMARY_EXPORT_MAX_WORDS,
            "char_len": len(exec_text),
            "max_chars": EXEC_SUMMARY_EXPORT_MAX_CHARS,
        }
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    for lab, sent in (
        ("unify_narrative", uni_narrative_sentence),
        ("ibm_narrative", ibm_narrative_sentence),
        ("insurtech_narrative", insurtech_narrative_sentence),
        ("ey_narrative", ey_narrative_sentence),
    ):
        if len(sent) < 20:
            receipt["failure"] = f"missing_or_short_{lab}"
            return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    skills = _competencies_to_skills(comp_l2.get("competencies"))
    if skills is None:
        receipt["failure"] = "missing_competencies"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    uni_lane_bullets, uerr = _lane_bullets_to_rg(
        list(uni_b.get("bullets") or []),
        max_bullets=6,
        export_warnings=export_warnings,
    )
    if uni_lane_bullets is None:
        receipt["failure"] = f"unify_bullets_invalid:{uerr}"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    ibm_lane_bullets, ierr = _lane_bullets_to_rg(
        list(ibm_b.get("bullets") or []),
        max_bullets=5,
        export_warnings=export_warnings,
    )
    if ibm_lane_bullets is None:
        receipt["failure"] = f"ibm_bullets_invalid:{ierr}"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    insurtech_lane_bullets, inerr = _lane_bullets_to_rg(
        list(insurtech_b.get("bullets") or []),
        max_bullets=5,
        export_warnings=export_warnings,
    )
    if insurtech_lane_bullets is None:
        receipt["failure"] = f"insurtech_bullets_invalid:{inerr}"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    ey_lane_bullets, eyerr = _lane_bullets_to_rg(
        list(ey_b.get("bullets") or []),
        max_bullets=5,
        export_warnings=export_warnings,
    )
    if ey_lane_bullets is None:
        receipt["failure"] = f"ey_bullets_invalid:{eyerr}"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    employment = list(_facts(base_resume).get("employment") or [])
    if not employment:
        receipt["failure"] = "base_has_no_employment"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    receipt["locked_employment_source_count"] = sum(1 for e in employment if isinstance(e, dict))

    def _locked_bullet_rows(emp_row: dict[str, Any]) -> list[dict[str, Any]]:
        out_rows: list[dict[str, Any]] = []
        for b in list(emp_row.get("bullets") or [])[:6]:
            if not isinstance(b, dict):
                continue
            txt = _norm_bullet_text(str(b.get("text") or ""))
            if len(txt) < 20:
                continue
            txt = _maybe_truncate_bullet_text(txt, export_warnings)
            ent2: dict[str, Any] = {"text": txt}
            bid = b.get("bullet_id")
            if bid:
                ent2["source_id"] = str(bid)
            if b.get("has_metric") is not None:
                ent2["has_metric"] = bool(b.get("has_metric"))
            out_rows.append(ent2)
        return out_rows

    experience_out: list[dict[str, Any]] = []
    for emp in employment:
        if not isinstance(emp, dict):
            continue
        fact_id = str(emp.get("fact_id") or "")
        title = str(emp.get("title") or "").strip()
        company = str(emp.get("employer") or "").strip()
        location = str(emp.get("location") or "Remote").strip()
        dates = _format_rg_dates(
            str(emp.get("start_date") or ""),
            str(emp.get("end_date") or ""),
            is_current=bool(emp.get("is_current")),
        )
        role_narrative: str | None = None
        if fact_id == "exp_unify_001":
            bullets = uni_lane_bullets
            role_narrative = uni_narrative_sentence
        elif fact_id == "exp_ibm_001":
            bullets = ibm_lane_bullets
            role_narrative = ibm_narrative_sentence
        elif fact_id == "exp_insurtech_001":
            bullets = insurtech_lane_bullets
            role_narrative = insurtech_narrative_sentence
        elif fact_id == "exp_ey_001":
            bullets = ey_lane_bullets
            role_narrative = ey_narrative_sentence
        else:
            bullets = _locked_bullet_rows(emp)
            locked_rn = str(emp.get("role_narrative") or "").strip()
            role_narrative = locked_rn if len(locked_rn) >= 20 else None
            min_locked = _MIN_LOCKED_BULLETS_BY_FACT_ID.get(fact_id, 3)
            if len(bullets) < min_locked:
                receipt["failure"] = f"locked_employment_insufficient_bullets:{fact_id}"
                receipt["excluded_locked_roles"] = []
                return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

        row: dict[str, Any] = {
            "title": title or "Role",
            "company": company or "Company",
            "location": location,
            "dates": dates,
            "bullets": bullets,
        }
        if role_narrative:
            row["role_narrative"] = role_narrative
        experience_out.append(row)

    receipt["excluded_locked_roles"] = []
    receipt["compact_early_career_excluded_count"] = 0
    receipt["locked_employment_mapped_count"] = len(experience_out)

    if len(experience_out) < 1 or len(experience_out) > 5:
        receipt["failure"] = "experience_role_count_out_of_bounds"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    edu = _education_from_base(base_resume)
    if len(edu) < 1:
        receipt["failure"] = "education_mapping_empty"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    cname = _candidate_name(base_resume)
    if not cname:
        receipt["failure"] = "missing_candidate_name"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    t_role = (getattr(input_package, "target_role", None) or "").strip() or "Target Role"
    t_co = (getattr(input_package, "target_company", None) or "").strip() or "Target Company"

    skill_c_json = json.dumps(skills["categories"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    uni_b_json = json.dumps(uni_lane_bullets, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    ibm_b_json = json.dumps(ibm_lane_bullets, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    insurtech_b_json = json.dumps(insurtech_lane_bullets, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    ey_b_json = json.dumps(ey_lane_bullets, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    hl_out = hl if len(hl) <= 240 else hl[:240]
    contact_info = _contact_from_base(base_resume)

    rg: dict[str, Any] = {
        "schema_version": "master_resume_v2.16",
        "candidate_name": cname,
        "target_role": t_role,
        "target_company": t_co,
        "generated_at": gen_at,
        "headline_line": hl_out,
        "sections": {
            "summary": {"text": exec_text, "word_count": wc},
            "experience": experience_out,
            "skills": skills,
            "education": edu,
            "certifications": _certs_from_base(base_resume),
        },
        "citations": [],
        "gaps": [],
        "metadata": {
            "generation_mode": "tailor_existing",
            "template_id": "modular_rg_output_v1",
            "slot_fingerprints": {
                "S0": f"modular_headline_sha:{_fp16(hl)}",
                "I0": f"modular_exec_sha:{_fp16(exec_text)}",
                "C0": f"modular_comp_sha:{_fp16(skill_c_json)}",
                "U0": f"modular_unify_b_sha:{_fp16(uni_b_json)}",
                "Y0": f"modular_ibm_b_sha:{_fp16(ibm_b_json)}",
                "T0": f"modular_insurtech_b_sha:{_fp16(insurtech_b_json)}",
                "E0": f"modular_ey_b_sha:{_fp16(ey_b_json)}",
                "R0": run_id,
            },
        },
    }
    if contact_info:
        rg["contact_info"] = contact_info

    ok_schema, err = validate_rg_output_object(rg)
    receipt["headline_line_preview"] = hl[:120]
    receipt["experience_roles"] = len(experience_out)
    receipt["schema_valid"] = ok_schema
    receipt["schema_error"] = err
    receipt["headline_line_exported"] = True
    out_dir = modular_root / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    if not ok_schema:
        receipt["failure"] = err or "schema_validation_failed"
        try:
            receipt["final_resume_rel"] = None
            receipt["artifact_dir_rel"] = modular_root.resolve().relative_to(art).as_posix()
        except ValueError:
            receipt["artifact_dir_rel"] = str(modular_root)
        return RgOutputBuildResult(
            None,
            False,
            receipt["failure"],
            False,
            err,
            receipt,
        )

    out_path = out_dir / "final_resume.json"
    _write_json(out_path, rg)
    try:
        receipt["final_resume_rel"] = out_path.resolve().relative_to(art).as_posix()
    except ValueError:
        receipt["final_resume_path"] = str(out_path.resolve())
    receipt["ok"] = True
    return RgOutputBuildResult(
        rg,
        True,
        "",
        True,
        "",
        receipt,
        provider_called=False,
        synthesized_sections_detected=False,
    )


def load_lane_l2_from_section_refs(
    repo_root: Path,
    section_output_refs: Mapping[str, str],
    *,
    rollup_lanes: Mapping[str, Any] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Load per-lane ``l2_output.json`` from modular section refs (product SSOT path).

    Returns ``(lane_l2_by_id, errors_by_lane)`` where *errors_by_lane* lists lanes that
    could not be loaded (missing ref, missing file, invalid JSON).
    """
    from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

    rr = repo_root.resolve()
    lanes_meta = rollup_lanes if isinstance(rollup_lanes, dict) else {}
    out: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for lane in GENERATED_LANES:
        rel = section_output_refs.get(lane)
        if not isinstance(rel, str) or not rel.strip():
            errors[lane] = "missing_section_output_ref"
            continue
        path = (rr / rel.strip().replace("\\", "/")).resolve()
        if not path.is_file():
            errors[lane] = f"missing_l2_output_json:{rel}"
            continue
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors[lane] = f"l2_output_unreadable:{exc}"
            continue
        if not isinstance(blob, dict):
            errors[lane] = "l2_output_not_object"
            continue
        row = lanes_meta.get(lane)
        if isinstance(row, dict):
            st = row.get("runtime_generation_status")
            if st is not None:
                blob = {**blob, "runtime_generation_status": st}
        out[lane] = blob
    return out, errors


def extract_lane_l2_from_assembled_final(final_resume_path: Path) -> dict[str, dict[str, Any]]:
    """Parse ``final_resume_assembled_v1`` JSON; return ``section_id -> l2_output_snapshot``."""
    raw = json.loads(final_resume_path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for sec in raw.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        if sec.get("section_kind") != "generated_lane":
            continue
        sid = sec.get("section_id")
        snap = sec.get("l2_output_snapshot")
        if isinstance(sid, str) and isinstance(snap, dict):
            out[sid] = snap
    return out


__all__ = [
    "RgOutputBuildResult",
    "build_rg_output_from_modular_sections",
    "extract_lane_l2_from_assembled_final",
    "load_lane_l2_from_section_refs",
]
