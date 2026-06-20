#!/usr/bin/env python3
"""W0 baseline: compiled-prompt fingerprints for PA core-law rollout (Brown targeting).

Emits per-lane artifacts under:
  artifacts/apps_rg/runtime_proofs/<section>/baseline/core_law_rollout_w0_<ts>/

Also writes rollup:
  docs/reports/apps_rg/sections_pa_core_law_rollout_w0_baseline.md
  docs/reports/apps_rg/sections_pa_core_law_rollout_w0_baseline.json
"""
from __future__ import annotations

import inspect
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

TARGET_COMPANY = "Brown & Brown"
TARGET_ROLE = "SVP IT Strategy & Innovation"
JD_PATH = _REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
BRIEF_PATH = _REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"

PRODUCT_SHAPE_MARKER = "PRODUCT_SHAPE (deterministic X2 authority"
_CHARS_PER_TOKEN = 3
_SAFETY = 1.12


def _utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    base = max(1, len(text) // _CHARS_PER_TOKEN)
    return max(1, int(base * _SAFETY))


def _load_brown_targeting() -> tuple[str, str]:
    jd = JD_PATH.read_text(encoding="utf-8")
    brief = BRIEF_PATH.read_text(encoding="utf-8")
    return jd, brief


def _split_product_shape(content: str) -> tuple[str, str]:
    idx = content.find(PRODUCT_SHAPE_MARKER)
    if idx < 0:
        return content, ""
    return content[:idx].rstrip(), content[idx:].rstrip()


def _count_x2(section_id: str, text: str) -> int:
    prefix = section_id.replace("_", "_")
    # section-specific x2 gate id prefix patterns
    patterns = {
        "headline": r"x2_headline_",
        "competencies": r"x2_competenc",
        "executive_summary": r"x2_exec_summary_",
        "unify_bullets": r"x2_unify_",
        "unify_narrative": r"x2_unify_",
        "ibm_bullets": r"x2_ibm_",
        "ibm_narrative": r"x2_ibm_",
    }
    pat = patterns.get(section_id, r"x2_")
    return len(re.findall(pat, text))


def _analyze_compiled(section_id: str, content: str) -> dict[str, Any]:
    static_part, product_shape = _split_product_shape(content)
    return {
        "compiled_chars_total": len(content),
        "compiled_tokens_estimate": estimate_tokens(content),
        "static_slots_chars": len(static_part),
        "static_slots_tokens_estimate": estimate_tokens(static_part),
        "product_shape_chars": len(product_shape),
        "product_shape_tokens_estimate": estimate_tokens(product_shape),
        "product_shape_present": bool(product_shape),
        "count_no_fabrication": content.count("NO FABRICATION"),
        "count_claim_ledger": content.lower().count("claim_ledger"),
        "count_x2_total": _count_x2(section_id, content),
        "count_x2_in_static_slots": _count_x2(section_id, static_part),
        "count_x2_in_product_shape": _count_x2(section_id, product_shape),
        "count_pa_core_law": content.count("pa_core_law"),
        "count_pa_truth_oath": content.count("pa_truth_oath"),
    }


def _static_file_metrics(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False}
    text = path.read_text(encoding="utf-8")
    return {
        "path": path.relative_to(_REPO).as_posix(),
        "exists": True,
        "chars": len(text),
        "lines": text.count("\n") + 1,
        "count_no_fabrication": text.count("NO FABRICATION"),
        "count_claim_ledger": text.lower().count("claim_ledger"),
        "count_x2": len(re.findall(r"x2_", text)),
    }


def _legacy_i0_chars(fn: Callable[..., str]) -> dict[str, Any]:
    src = inspect.getsource(fn)
    return {
        "source": f"{fn.__module__}.{fn.__name__}",
        "chars": len(src),
        "lines": src.count("\n") + 1,
        "count_no_fabrication": src.count("NO FABRICATION"),
        "count_claim_ledger": src.lower().count("claim_ledger"),
        "count_x2": len(re.findall(r"x2_", src)),
    }


def _fact_lines_from_pool(pool: Any) -> str:
    return "\n".join(
        f"- {row['fact_id']}: {row['claim_text']}"
        + (f" | tech: {', '.join(row['technologies'])}" if row.get('technologies') else "")
        for row in pool.bullet_rows
    )


def _forbidden_employers() -> str:
    return "- IBM\n- Unify Consulting\n- InsurTech\n- EY"


def _ensure_pa_proof_metadata(meta: dict[str, Any], pool: Any) -> dict[str, Any]:
    """Ensure finalize_section_compiled_with_proof_pool has evidence_authority."""
    from apps_rg.runtime.product_evidence_authority import attach_product_evidence_law_to_metadata

    out = dict(meta or {})
    ea = out.get("evidence_authority")
    if isinstance(ea, dict) and str(ea.get("authority") or "").strip():
        return out
    return attach_product_evidence_law_to_metadata(out, pool=pool)


def _brown_pool_payload(pool: Any, *, jd: str, brief: str) -> dict[str, Any]:
    return {
        "run_id": "core_law_rollout_w0",
        "target_title": TARGET_ROLE,
        "target_company": TARGET_COMPANY,
        "jd_text": jd,
        "briefing": brief,
        "selected_fact_plan": pool.selected_fact_plan,
        "allowed_fact_ids": list(pool.allowed_fact_ids_ordered),
        "proof_pool_metadata": _ensure_pa_proof_metadata(dict(pool.proof_pool_metadata or {}), pool),
    }


def _compile_executive_summary(jd: str, brief: str) -> str:
    from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt

    payload = {
        "product_visible": False,
        "proof_pool_metadata": {"proof_pool_type": "selected_role_fact_set"},
        "run_id": "w0_exec_ref",
        "target_title": TARGET_ROLE,
        "target_company": TARGET_COMPANY,
        "jd_text": jd,
        "briefing": brief,
        "allowed_fact_ids": ["fact_governance_003"],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_governance_003",
                    "claim_text": "Implemented Basel III / CCAR frameworks.",
                    "confidence": "HIGH",
                }
            ],
        },
        "evidence_capsule_disabled": True,
    }
    compiled = compile_executive_summary_prompt(payload, run_id="w0_exec_ref")
    return str(compiled.artifact.messages[0]["content"])


def _compile_headline(jd: str, brief: str) -> str:
    from apps_rg.runtime.dispatch.headline_pa import compile_headline_prompt
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    pool = resolve_section_proof_pool(
        section="headline",
        repo_root=_REPO,
        target_company=TARGET_COMPANY,
        target_title=TARGET_ROLE,
        jd_text=jd,
        briefing_text=brief,
        product_visible=False,
        fixture_dev_only_bypass=True,
        non_product_certified=True,
    )
    payload = _brown_pool_payload(pool, jd=jd, brief=brief)
    out = compile_headline_prompt(
        payload,
        companion_context="",
        fact_lines=_fact_lines_from_pool(pool),
        forbidden_employer_lines=_forbidden_employers(),
        run_id="w0_headline",
    )
    return str(out.artifact.messages[0]["content"])


def _compile_competencies(jd: str, brief: str) -> str:
    from apps_rg.runtime.dispatch.competencies_pa import compile_competencies_prompt
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=_REPO,
        target_company=TARGET_COMPANY,
        target_title=TARGET_ROLE,
        jd_text=jd,
        briefing_text=brief,
        product_visible=False,
        fixture_dev_only_bypass=True,
        non_product_certified=True,
    )
    payload = _brown_pool_payload(pool, jd=jd, brief=brief)
    out = compile_competencies_prompt(
        payload,
        companion_context="",
        fact_lines=_fact_lines_from_pool(pool),
        run_id="w0_competencies",
    )
    return str(out.artifact.messages[0]["content"])


def _unify_ibm_brown_payload(
    *,
    section: str,
    jd: str,
    brief: str,
    header_key: str,
    header: dict[str, Any],
    allowed: list[str],
    plan: dict[str, Any],
    path: Path,
    base_hash: str,
) -> dict[str, Any]:
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    pool = resolve_section_proof_pool(
        section=section,
        repo_root=_REPO,
        target_company=TARGET_COMPANY,
        target_title=TARGET_ROLE,
        jd_text=jd,
        briefing_text=brief,
        product_visible=False,
        fixture_dev_only_bypass=True,
        non_product_certified=True,
    )
    common = dict(
        base_json_path=path,
        base_hash=base_hash,
        selected_fact_plan=plan,
        allowed_fact_ids=set(allowed),
        target_title=TARGET_ROLE,
        target_company=TARGET_COMPANY,
        jd_text=jd,
        briefing=brief,
    )
    if header_key == "unify_header":
        from apps_rg.runtime.sections.unify_bullets_lane import build_runtime_payload as build_rp

        rp = build_rp(unify_header=header, **common)
    else:
        from apps_rg.runtime.sections.ibm_bullets_lane import build_runtime_payload as build_rp

        rp = build_rp(ibm_header=header, **common)
    rp["proof_pool_metadata"] = _ensure_pa_proof_metadata(dict(pool.proof_pool_metadata or {}), pool)
    rp["allowed_fact_ids"] = list(pool.allowed_fact_ids_ordered) or allowed
    return rp


def _load_unify_employment() -> tuple[Any, ...]:
    from apps_rg.runtime.sections.unify_bullets_lane import (
        build_selected_fact_plan,
        extract_unify_employment,
        load_base_resume,
    )

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_unify_employment(base)
    plan = build_selected_fact_plan(facts)
    return base, path, base_hash, header, facts, allowed, plan


def _load_ibm_employment() -> tuple[Any, ...]:
    from apps_rg.runtime.sections.ibm_bullets_lane import (
        build_selected_fact_plan,
        extract_ibm_employment,
        load_base_resume,
    )

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_ibm_employment(base)
    plan = build_selected_fact_plan(facts)
    return base, path, base_hash, header, facts, allowed, plan


def _compile_unify_bullets(jd: str, brief: str) -> str:
    from apps_rg.runtime.dispatch.unify_bullets_pa import compile_unify_bullets_prompt
    from apps_rg.runtime.sections.unify_bullets_pa import _legacy_i0

    _, path, base_hash, header, facts, allowed, plan = _load_unify_employment()
    rp = _unify_ibm_brown_payload(
        section="unify_bullets",
        jd=jd,
        brief=brief,
        header_key="unify_header",
        header=header,
        allowed=sorted(allowed),
        plan=plan,
        path=path,
        base_hash=base_hash,
    )
    out = compile_unify_bullets_prompt(rp, run_id="w0_unify_bullets")
    content = str(out.artifact.messages[0]["content"])
    return content


def _compile_unify_narrative(jd: str, brief: str) -> str:
    from apps_rg.runtime.dispatch.unify_narrative_pa import compile_unify_narrative_prompt

    _, path, base_hash, header, facts, allowed, plan = _load_unify_employment()
    rp = _unify_ibm_brown_payload(
        section="unify_narrative",
        jd=jd,
        brief=brief,
        header_key="unify_header",
        header=header,
        allowed=sorted(allowed),
        plan=plan,
        path=path,
        base_hash=base_hash,
    )
    fact_lines = "\n".join(
        f"- {f['fact_id']}: {f['claim_text']}" for f in (plan.get("facts") or facts)
    )
    out = compile_unify_narrative_prompt(rp, fact_lines, run_id="w0_unify_narrative")
    return str(out.artifact.messages[0]["content"])


def _compile_ibm_bullets(jd: str, brief: str) -> str:
    from apps_rg.runtime.dispatch.ibm_bullets_pa import compile_ibm_bullets_prompt

    _, path, base_hash, header, facts, allowed, plan = _load_ibm_employment()
    rp = _unify_ibm_brown_payload(
        section="ibm_bullets",
        jd=jd,
        brief=brief,
        header_key="ibm_header",
        header=header,
        allowed=sorted(allowed),
        plan=plan,
        path=path,
        base_hash=base_hash,
    )
    out = compile_ibm_bullets_prompt(rp, run_id="w0_ibm_bullets")
    return str(out.artifact.messages[0]["content"])


def _compile_ibm_narrative(jd: str, brief: str) -> str:
    from apps_rg.runtime.dispatch.ibm_narrative_pa import compile_ibm_narrative_prompt

    _, path, base_hash, header, facts, allowed, plan = _load_ibm_employment()
    rp = _unify_ibm_brown_payload(
        section="ibm_narrative",
        jd=jd,
        brief=brief,
        header_key="ibm_header",
        header=header,
        allowed=sorted(allowed),
        plan=plan,
        path=path,
        base_hash=base_hash,
    )
    fact_lines = "\n".join(
        f"- {f['fact_id']}: {f['claim_text']}" for f in (plan.get("facts") or facts)
    )
    out = compile_ibm_narrative_prompt(rp, fact_lines, run_id="w0_ibm_narrative")
    return str(out.artifact.messages[0]["content"])


def _write_lane_artifact(
    section_id: str,
    ts: str,
    content: str,
    metrics: dict[str, Any],
    static_ssot: list[dict[str, Any]],
) -> Path:
    out_dir = (
        _REPO
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / section_id
        / "baseline"
        / f"core_law_rollout_w0_{ts}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "compiled_prompt.txt").write_text(content, encoding="utf-8")
    doc = {
        "section_id": section_id,
        "target_company": TARGET_COMPANY,
        "target_role": TARGET_ROLE,
        "jd_path": JD_PATH.relative_to(_REPO).as_posix(),
        "brief_path": BRIEF_PATH.relative_to(_REPO).as_posix(),
        "compiled": metrics,
        "static_ssot": static_ssot,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "w0_baseline_metrics.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_dir


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    headers = [
        "section",
        "static_ssot_chars",
        "compiled_tokens",
        "static_slots_tokens",
        "product_shape_tokens",
        "NO FABRICATION",
        "claim_ledger",
        "x2_static",
        "x2_product_shape",
        "priority",
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        lines.append(
            "| "
            + " | ".join(
                str(r.get(h, ""))
                for h in headers
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    import os

    from apps_rg.runtime.spine.front_contracts import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    os.environ.setdefault("PYTEST_CURRENT_TEST", "ops_scripts.apps_rg.core_law_rollout_w0_baseline")
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        return _main_inner()
    finally:
        deactivate_fixture_dev_bypass()


def _main_inner() -> int:
    ts = _utc_ts()
    jd, brief = _load_brown_targeting()

    from apps_rg.runtime.sections.ibm_bullets_pa import _legacy_i0 as ibm_bullets_i0
    from apps_rg.runtime.sections.unify_bullets_pa import _legacy_i0 as unify_bullets_i0

    static_catalog: dict[str, list[dict[str, Any]]] = {
        "headline": [
            _static_file_metrics(_REPO / "apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml"),
        ],
        "competencies": [
            _static_file_metrics(
                _REPO / "apps_rg/prompt_assembly/templates/competency_selector_v2.pa_slots.yaml"
            ),
        ],
        "unify_bullets": [
            _static_file_metrics(_REPO / "apps_rg/prompt_assembly/templates/unify_bullet_tailor_v1.yaml"),
            _legacy_i0_chars(unify_bullets_i0),
        ],
        "unify_narrative": [
            _static_file_metrics(
                _REPO / "apps_rg/prompt_assembly/templates/unify_position_narrative_v1.yaml"
            ),
        ],
        "ibm_bullets": [
            _static_file_metrics(_REPO / "apps_rg/prompt_assembly/templates/ibm_bullet_tailor_v1.yaml"),
            _legacy_i0_chars(ibm_bullets_i0),
        ],
        "ibm_narrative": [
            _static_file_metrics(
                _REPO / "apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml"
            ),
        ],
        "executive_summary": [
            _static_file_metrics(
                _REPO
                / "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
            ),
        ],
        "_shared": [
            _static_file_metrics(
                _REPO / "apps_rg/prompt_assembly/templates/w7_strategic_tailor_shell_slots.yaml"
            ),
            _static_file_metrics(_REPO / "apps_rg/prompt_assembly/pa_core_law_v1.yaml"),
        ],
    }

    compilers: list[tuple[str, Callable[[str, str], str]]] = [
        ("executive_summary", _compile_executive_summary),
        ("headline", _compile_headline),
        ("competencies", _compile_competencies),
        ("unify_bullets", _compile_unify_bullets),
        ("unify_narrative", _compile_unify_narrative),
        ("ibm_bullets", _compile_ibm_bullets),
        ("ibm_narrative", _compile_ibm_narrative),
    ]

    rollup_rows: list[dict[str, Any]] = []
    artifact_dirs: dict[str, str] = {}
    errors: dict[str, str] = {}

    for section_id, fn in compilers:
        try:
            content = fn(jd, brief)
            metrics = _analyze_compiled(section_id, content)
            ssot = static_catalog.get(section_id, [])
            out_dir = _write_lane_artifact(section_id, ts, content, metrics, ssot)
            artifact_dirs[section_id] = out_dir.relative_to(_REPO).as_posix()

            static_chars = sum(
                int(x.get("chars") or 0) for x in ssot if x.get("exists")
            )
            priority = "P0"
            if section_id in ("competencies",):
                priority = "P1"
            elif section_id in ("unify_bullets", "ibm_bullets"):
                priority = "P2"
            elif section_id in ("unify_narrative", "ibm_narrative"):
                priority = "P3"
            elif section_id == "executive_summary":
                priority = "REF"

            rollup_rows.append(
                {
                    "section": section_id,
                    "static_ssot_chars": static_chars,
                    "compiled_tokens": metrics["compiled_tokens_estimate"],
                    "static_slots_tokens": metrics["static_slots_tokens_estimate"],
                    "product_shape_tokens": metrics["product_shape_tokens_estimate"],
                    "NO FABRICATION": metrics["count_no_fabrication"],
                    "claim_ledger": metrics["count_claim_ledger"],
                    "x2_static": metrics["count_x2_in_static_slots"],
                    "x2_product_shape": metrics["count_x2_in_product_shape"],
                    "priority": priority,
                    "artifact_dir": artifact_dirs[section_id],
                }
            )
        except Exception as exc:  # guardian: w0 baseline must not abort whole rollup
            errors[section_id] = f"{type(exc).__name__}: {exc}"

    rollup_rows.sort(key=lambda r: -int(r.get("compiled_tokens") or 0))

    report_json = {
        "wave": "W0",
        "plan_id": "sections-pa-core-law-rollout-c3a8f1",
        "timestamp": ts,
        "targeting": {
            "company": TARGET_COMPANY,
            "role": TARGET_ROLE,
            "jd_path": JD_PATH.relative_to(_REPO).as_posix(),
            "brief_path": BRIEF_PATH.relative_to(_REPO).as_posix(),
        },
        "token_estimate": {
            "method": "approximate_chars_div_3_with_safety_margin",
            "safety_multiplier": _SAFETY,
            "chars_per_token": _CHARS_PER_TOKEN,
        },
        "lanes": rollup_rows,
        "errors": errors,
        "static_catalog": static_catalog,
        "findings": {
            "p0_token_debt": [
                r["section"]
                for r in rollup_rows
                if r.get("priority") == "P0"
            ],
            "x2_in_static_slots_nonzero": [
                r["section"]
                for r in rollup_rows
                if int(r.get("x2_static") or 0) > 0
            ],
            "governance_echo_high_claim_ledger": [
                r["section"]
                for r in rollup_rows
                if int(r.get("claim_ledger") or 0) >= 8
            ],
        },
    }

    json_path = _REPO / "docs/reports/apps_rg/sections_pa_core_law_rollout_w0_baseline.json"
    md_path = _REPO / "docs/reports/apps_rg/sections_pa_core_law_rollout_w0_baseline.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_json, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Sections PA Core-Law Rollout — W0 Baseline",
        "",
        f"**Generated:** {report_json['timestamp']} (UTC)  ",
        f"**Plan:** [sections-pa-core-law-rollout-c3a8f1.md](../../.codex/plans/sections-pa-core-law-rollout-c3a8f1.md)  ",
        f"**Targeting:** {TARGET_COMPANY} / {TARGET_ROLE}",
        "",
        "## Compiled prompt fingerprints (Brown JD + briefing)",
        "",
        _markdown_table(rollup_rows),
        "",
        "## Findings",
        "",
        f"- **P0 static debt (plan):** {', '.join(report_json['findings']['p0_token_debt']) or 'none'}",
        f"- **Lanes with `x2_*` in static slots (should → 0 after rollout):** "
        f"{', '.join(report_json['findings']['x2_in_static_slots_nonzero']) or 'none'}",
        f"- **High `claim_ledger` echo (≥8):** "
        f"{', '.join(report_json['findings']['governance_echo_high_claim_ledger']) or 'none'}",
        "",
        "## Per-lane artifacts",
        "",
    ]
    for sid, rel in sorted(artifact_dirs.items()):
        md_lines.append(f"- **{sid}:** [{rel}]({rel})")
    if errors:
        md_lines.extend(["", "## Errors", ""])
        for sid, err in errors.items():
            md_lines.append(f"- **{sid}:** `{err}`")
    md_lines.append("")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps({"ok": not errors, "json": json_path.as_posix(), "md": md_path.as_posix(), "errors": errors}))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
