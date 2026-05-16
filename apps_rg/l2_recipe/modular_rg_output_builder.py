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
from apps_rg.runtime.reports.generated_lane_rollup import GENERATED_LANES

# Canonical base entries that aggregate multiple early roles into one narrative line
# cannot satisfy rg_output ``experience[*].bullets`` minItems=3 without extra base facts.
_COMPACT_EARLY_CAREER_FACT_IDS: Final[frozenset[str]] = frozenset({"exp_early_career_001"})

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
    return len(re.findall(r"\b\w+\b", text.strip()))


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


def _lane_bullets_to_rg(
    lane_bullets: list[Any],
    *,
    max_bullets: int = 5,
    min_bullets: int = 3,
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
        if len(text) > 250:
            text = text[:250]
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
    for cat in competencies[:6]:
        if not isinstance(cat, dict):
            continue
        _ = str(cat.get("category_label") or "Capabilities").strip() or "Capabilities"
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
        categories.append({"name": "Other", "items": items[:8]})
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
        out.append(rec)
    return out


def _certs_from_base(base: dict[str, Any]) -> list[dict[str, Any]]:
    certs = list(_facts(base).get("certifications") or [])
    out: list[dict[str, Any]] = []
    for c in certs:
        if not isinstance(c, dict):
            continue
        name = str(c.get("name") or "").strip()
        issuer = str(c.get("issuer") or c.get("issuing_organization") or "").strip()
        if not name or not issuer:
            continue
        row: dict[str, Any] = {"name": name, "issuer": issuer}
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
    }

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
    comp_l2 = lane_l2_by_id["competencies"]

    for label, blob in (
        ("headline", headline),
        ("executive_summary", exec_l2),
        ("unify_bullets", uni_b),
        ("unify_narrative", uni_n),
        ("ibm_bullets", ibm_b),
        ("ibm_narrative", ibm_n),
        ("competencies", comp_l2),
    ):
        if not isinstance(blob, dict):
            receipt["failure"] = f"lane_payload_invalid:{label}"
            return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    hl = str(headline.get("headline_line") or "").strip()
    if not hl:
        receipt["failure"] = "missing_headline_line"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    exec_text = str(exec_l2.get("resume_display_text") or "").strip()
    if len(exec_text) < 10:
        receipt["failure"] = "missing_executive_summary"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)
    wc = _word_count(exec_text)
    if wc < 10 or wc > 60 or len(exec_text) > 500:
        receipt["failure"] = "executive_summary_out_of_rg_bounds"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    for lab, narr in (("unify_narrative", uni_n), ("ibm_narrative", ibm_n)):
        sent = str(narr.get("narrative_sentence") or "").strip()
        if len(sent) < 20:
            receipt["failure"] = f"missing_or_short_{lab}"
            return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    skills = _competencies_to_skills(comp_l2.get("competencies"))
    if skills is None:
        receipt["failure"] = "missing_competencies"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    uni_lane_bullets, uerr = _lane_bullets_to_rg(list(uni_b.get("bullets") or []))
    if uni_lane_bullets is None:
        receipt["failure"] = f"unify_bullets_invalid:{uerr}"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    ibm_lane_bullets, ierr = _lane_bullets_to_rg(list(ibm_b.get("bullets") or []))
    if ibm_lane_bullets is None:
        receipt["failure"] = f"ibm_bullets_invalid:{ierr}"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    employment = list(_facts(base_resume).get("employment") or [])
    if not employment:
        receipt["failure"] = "base_has_no_employment"
        return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

    receipt["locked_employment_source_count"] = sum(1 for e in employment if isinstance(e, dict))

    def _locked_bullet_rows(emp_row: dict[str, Any]) -> list[dict[str, Any]]:
        out_rows: list[dict[str, Any]] = []
        for b in list(emp_row.get("bullets") or [])[:5]:
            if not isinstance(b, dict):
                continue
            txt = _norm_bullet_text(str(b.get("text") or ""))
            if len(txt) < 20:
                continue
            if len(txt) > 250:
                txt = txt[:250]
            ent2: dict[str, Any] = {"text": txt}
            bid = b.get("bullet_id")
            if bid:
                ent2["source_id"] = str(bid)
            if b.get("has_metric") is not None:
                ent2["has_metric"] = bool(b.get("has_metric"))
            out_rows.append(ent2)
        return out_rows

    experience_out: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
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
        if fact_id == "exp_unify_001":
            bullets = uni_lane_bullets
        elif fact_id == "exp_ibm_001":
            bullets = ibm_lane_bullets
        else:
            bullets = _locked_bullet_rows(emp)
            if fact_id in _COMPACT_EARLY_CAREER_FACT_IDS and len(bullets) < 3:
                excluded.append(
                    {
                        "fact_id": fact_id or "(missing_fact_id)",
                        "reason": (
                            "compact_early_career_row omitted from rg_output.experience: "
                            "locked base has fewer than three schema-length bullets "
                            "(rg_output_schema requires minItems 3 per role); no synthetic bullets added"
                        ),
                        "locked_bullets_found": len(bullets),
                        "employer": company,
                        "title": title,
                    },
                )
                continue
            if len(bullets) < 3:
                receipt["failure"] = f"locked_employment_insufficient_bullets:{fact_id}"
                receipt["excluded_locked_roles"] = excluded
                return RgOutputBuildResult(None, False, receipt["failure"], False, receipt["failure"], receipt)

        experience_out.append(
            {
                "title": title or "Role",
                "company": company or "Company",
                "location": location,
                "dates": dates,
                "bullets": bullets,
            },
        )

    receipt["excluded_locked_roles"] = excluded
    receipt["compact_early_career_excluded_count"] = len(excluded)
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

    rg: dict[str, Any] = {
        "schema_version": "master_resume_v2.16",
        "candidate_name": cname,
        "target_role": t_role,
        "target_company": t_co,
        "generated_at": gen_at,
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
                "R0": run_id,
            },
        },
    }

    ok_schema, err = validate_rg_output_object(rg)
    receipt["headline_line_preview"] = hl[:120]
    receipt["experience_roles"] = len(experience_out)
    receipt["schema_valid"] = ok_schema
    receipt["schema_error"] = err
    receipt["unmapped_lane_note"] = (
        "headline_line is required for merge eligibility but rg_output_schema has no headline field; "
        "value captured in merge receipt only."
    )
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
]
