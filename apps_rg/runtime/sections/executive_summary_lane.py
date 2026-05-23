"""Executive summary section lane — ``python -m apps_rg --section executive_summary``.

Lane-scoped modular runtime (proof pool → section graph binding shim → PA → L2 → section X2/X3/L6).
**Not** the integrated R4 governed spine (U0→L1→L0→C0→PA→L2→Exit). Invoked from
``apps_rg.runtime.orchestration.canonical_dispatch`` section branch only.

**W3 classification:** ``declared_temporary_slice`` until one-spine convergence.
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg --section executive_summary"
    )

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_DECLARED_TEMPORARY_SLICE,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_DECLARED_TEMPORARY_SLICE
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# SRFS + full 8-slot PA prompts are large; model JSON (display + claim_ledger + self_check) often exceeds 700 tokens.
_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS = int(
    os.environ.get("APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS", "2048")
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
    pass  # dotenv not installed, rely on system env

from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    classify_ledger_parse_state,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.sections.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
)
from apps_rg.runtime.sections.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.providers.qwen_vllm_provider import (
    DEFAULT_QWEN_MODEL,
    ProviderResult,
    build_qwen_request,
)
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.validators.executive_summary_x2 import build_sentence_claim_coverage, run_x2_gates
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    build_executive_summary_judge_packet,
    write_executive_summary_judge_packet,
)
from apps_rg.runtime.judges.executive_summary_x1d import run_llm_judges
from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3 as _aggregate_executive_summary_x3
from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run, prepare_runtime_proof_run_dir
from apps_rg.runtime.section_cli_defaults import coalesce_lane_provider_resolution_source
from apps_rg.runtime.section_proof.section_input_usage_ledger import build_section_input_usage_ledger_v1
from apps_rg.runtime.shadow.executive_summary_l6 import build_l6_shadow_package
from apps_rg.runtime.sections.executive_summary_proof_bundle import (
    emit_executive_summary_post_x3_proof_artifacts,
    write_executive_summary_artifact_inventory,
)
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict


PROMPT_ID = "executive_summary.generate_scratch_v1"
EXEC_SUMMARY_TEMP_DEFAULT = 0.45
EXEC_SUMMARY_TEMP_RANGE = (0.35, 0.55)
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = (
    "enterprise AI platform leadership, agentic AI systems, runtime governance, "
    "LLMOps, retrieval, production reliability, engineering leadership"
)
BRIEFING_DEFAULT = "regulated enterprise environment, platform modernization, AI governance, scalable delivery"

# Full PDF extraction briefings can exceed vLLM max_model_len (prompt + max_tokens). Cap before compile.
_DEFAULT_EXEC_SUMMARY_BRIEFING_CAP_CHARS = 12000


def _args_target_title(args: argparse.Namespace) -> str:
    return (
        str(getattr(args, "target_title", None) or getattr(args, "target_role", None) or TARGET_TITLE_DEFAULT)
        .strip()
        or TARGET_TITLE_DEFAULT
    )


def _args_jd_text(args: argparse.Namespace) -> str:
    return (
        str(getattr(args, "jd_text", None) or getattr(args, "jd", None) or JD_TEXT_DEFAULT).strip()
        or JD_TEXT_DEFAULT
    )


def truncate_briefing_for_exec_summary_vllm(briefing: str) -> tuple[str, dict[str, Any] | None]:
    """Prepare briefing via ranked section selection (see executive_summary_briefing)."""
    from apps_rg.runtime.sections.executive_summary_briefing import (
        prepare_briefing_for_executive_summary,
    )

    selected, receipt = prepare_briefing_for_executive_summary(briefing)
    if receipt.get("fail_closed"):
        return selected, receipt
    if receipt.get("briefing_excluded_chars", 0) == 0 and receipt.get("briefing_original_chars", 0) == len(
        str(briefing or "")
    ):
        return selected, None
    return selected, receipt


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
BASE_POINTER = REPO_ROOT / "apps_rg" / "resume" / "base" / "active_base_resume_pointer.json"
BASE_JSON_DEFAULT = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
LANE_KEY = "executive_summary"
PROMPT_TEMPLATE = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_base_resume() -> tuple[dict[str, Any], Path, str]:
    if BASE_POINTER.exists():
        pointer = json.loads(BASE_POINTER.read_text(encoding="utf-8"))
        ref = pointer.get("active_resume_path") or pointer.get("base_resume_json_ref") or "apps_rg/resume/base/amit_ayer_base_resume_v1.json"
        path = REPO_ROOT / ref
    else:
        path = BASE_JSON_DEFAULT
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw), path, hashlib.sha256(raw.encode()).hexdigest()


def extract_allowed_facts(base_resume: dict[str, Any]) -> tuple[list[dict[str, Any]], set[str]]:
    """Collect bullets in résumé order; no hard-coded bullet IDs or employer filters."""
    facts_obj = base_resume.get("facts", base_resume)
    selected: list[dict[str, Any]] = []
    for emp in facts_obj.get("employment", []):
        employer = emp.get("employer", "")
        for bullet in emp.get("bullets", []):
            bid = bullet.get("bullet_id")
            if not bid:
                continue
            selected.append(
                {
                    "fact_id": bid,
                    "claim_text": bullet.get("text", ""),
                    "source_employment": employer,
                    "metric_raw": bullet.get("metric_raw", "") if bullet.get("has_metric") else "",
                    "domain": bullet.get("domain", ""),
                    "technologies": bullet.get("technologies", []),
                }
            )
    allowed = {row["fact_id"] for row in selected}
    for row in selected:
        if row.get("metric_raw"):
            allowed.add(f"{row['fact_id']}_metric_{sha16(row['metric_raw'])[:8]}")
    return selected, allowed


def build_selected_fact_plan(selected_facts: list[dict[str, Any]]) -> dict[str, Any]:
    top = selected_facts[:4]
    return {
        "section_id": "executive_summary",
        "selection_method": "resume_document_order_top_n",
        "facts": top,
        "required_fact_ids": [row["fact_id"] for row in top],
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    selected_fact_plan: dict[str, Any],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    allowed_fact_ids_ordered: list[str] | None = None,
) -> dict[str, Any]:
    ids = allowed_fact_ids_ordered if allowed_fact_ids_ordered is not None else list(selected_fact_plan.get("required_fact_ids") or [])
    payload = {
        "run_id": datetime.now(timezone.utc).strftime("exec_summary_%Y%m%d_%H%M%S"),
        "section_id": "executive_summary",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": ids,
        "writable_context_scope": "executive_summary_only",
        "full_resume_writable": False,
        "monolithic_prompt_invoked": False,
        "strategic_tailor_v1_invoked": False,
    }
    return payload


L2_BRIDGE_PHRASE_PATTERN = re.compile(
    r"\bthis (?:was|is) achieved (?:while|through|by)\b",
    re.IGNORECASE,
)
L2_PASSIVE_CYCLE_PATTERN = re.compile(
    r"\b(?:lab-to-production\s+)?cycle time was reduced\b",
    re.IGNORECASE,
)


def check_l2_resume_voice(resume_display_text: str) -> tuple[bool, str | None]:
    """Dispatch-level voice checks aligned with X2 first-person and bridge-phrase gates."""
    from apps_rg.runtime.validators.executive_summary_x2 import FIRST_PERSON_PATTERN

    if FIRST_PERSON_PATTERN.search(resume_display_text):
        return False, "First-person pronoun found (third person only; never I/me/my/we/our)"
    if L2_BRIDGE_PHRASE_PATTERN.search(resume_display_text):
        return False, "Bridge phrase 'This was achieved...' is forbidden"
    if L2_PASSIVE_CYCLE_PATTERN.search(resume_display_text):
        return False, "Passive cycle-time phrasing (use active voice: reduced cycle time from...)"
    return True, None


def check_executive_summary_narrative_shape(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]] | None = None,
    *,
    graph_only_fact_tight_synthesis: bool = False,
) -> tuple[bool, str | None]:
    """Dispatch-level narrative quality checks (not X2 gates): stacking and enumeration risk."""
    from apps_rg.runtime.validators.executive_summary_x2 import ACTION_VERB_OPENERS, split_sentences

    sentences = split_sentences(resume_display_text)
    if not sentences:
        return False, "Empty executive summary"

    action_openers = set(ACTION_VERB_OPENERS) | {"generated", "integrated", "enhanced", "built"}
    for sentence in sentences:
        if sentence.count(",") >= 6:
            return False, "Long capability enumeration list in a single sentence"

    claims = claim_ledger or []
    if (
        not graph_only_fact_tight_synthesis
        and len(sentences) >= 3
        and claims
        and len(sentences) == len(claims)
    ):
        from difflib import SequenceMatcher

        action_starts = 0
        near_verbatim_rows = 0
        for sentence, row in zip(sentences, claims):
            first = sentence.split()[0].lower().strip(",.;:") if sentence.split() else ""
            if first in action_openers:
                action_starts += 1
            claim_text = str(row.get("claim_text") or "").strip()
            if claim_text:
                ratio = SequenceMatcher(
                    None, claim_text.lower(), str(sentence).strip().lower()
                ).ratio()
                if ratio >= 0.72:
                    near_verbatim_rows += 1
        if near_verbatim_rows >= len(sentences) - 1 and action_starts >= len(sentences) - 1:
            return False, "One displayed sentence per claim-ledger row (sentence-stacked proof)"

    return True, None


def build_prompt_messages(runtime_payload: dict[str, Any]) -> list[dict[str, str]]:
    """PA-assembled messages via ``section_prompt_adapter`` + executive_summary template (W4)."""
    run_id = str(runtime_payload.get("run_id") or "exec_summary_prompt_build")
    compiled = compile_executive_summary_prompt(runtime_payload, run_id=run_id)
    return compiled.artifact.messages


def parse_model_json(raw: str) -> tuple[dict[str, Any] | None, str]:
    """Lenient parse for downstream objects; X2 x2_json_parse_valid uses unmodified raw_output."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed, ""
    except json.JSONDecodeError as exc:
        return None, f"JSON parse failed: {exc}"
    return None, "Model output was not a JSON object."


def coerce_resume_display_sentence_count_band(resume: str) -> str:
    """No post-hoc sentence-band coercion — X2 enforces 4–5 sentences."""
    return resume


def normalize_executive_summary_llm_output(
    parsed: dict[str, Any],
    runtime_selected_fact_plan: dict[str, Any],
) -> dict[str, Any]:
    """Collapse legacy R0 aliases; runtime owns selected_fact_plan (no model echo for proof SSOT)."""
    resume = str(
        parsed.get("resume_display_text")
        or parsed.get("executive_summary")
        or ""
    ).strip()
    resume = coerce_resume_display_sentence_count_band(resume)
    claims = parsed.get("claim_ledger")
    if claims is None:
        claims = parsed.get("claim_ledger_emitted")
    if not isinstance(claims, list):
        claims = []
    jd_al = parsed.get("jd_alignment")
    if not isinstance(jd_al, dict):
        jd_al = {"targeting_only": True, "jd_used_as_proof": False}
    gap = parsed.get("gap_notes") if isinstance(parsed.get("gap_notes"), list) else []
    changelog = parsed.get("change_log") if isinstance(parsed.get("change_log"), list) else []
    self_chk = parsed.get("self_check") if isinstance(parsed.get("self_check"), dict) else {}
    out: dict[str, Any] = {
        "resume_display_text": resume,
        "selected_fact_plan": runtime_selected_fact_plan,
        "claim_ledger": claims,
        "jd_alignment": jd_al,
        "gap_notes": gap,
        "change_log": changelog,
        "self_check": self_chk,
    }
    for key in (
        "source_sensitive_phrase_ledger",
        "input_payload_hash",
        "output_payload_hash",
        "claim_ledger_hash",
        "allowed_fact_ids_hash",
    ):
        if key in parsed:
            out[key] = parsed[key]
    return out


def prune_exec_summary_claim_ledger_orphans(
    parsed: dict[str, Any],
    allowed_fact_ids: set[str],
) -> None:
    """Drop or repair claim_ledger source_fact_ids outside the active proof pool allowlist."""
    from apps_rg.runtime.validators.fact_id_typo_repair import repair_fact_id_against_allowlist

    ledger = parsed.get("claim_ledger")
    if not isinstance(ledger, list):
        return
    changelog = parsed.setdefault("change_log", [])
    if not isinstance(changelog, list):
        changelog = []
        parsed["change_log"] = changelog
    for row in ledger:
        if not isinstance(row, dict):
            continue
        cleaned: list[str] = []
        for sid in row.get("source_fact_ids") or []:
            fixed = repair_fact_id_against_allowlist(str(sid), allowed_fact_ids)
            base = fixed.split("_metric_")[0]
            if fixed in allowed_fact_ids or base in allowed_fact_ids:
                cleaned.append(fixed if fixed in allowed_fact_ids else base)
        if cleaned != list(row.get("source_fact_ids") or []):
            changelog.append(
                {
                    "operation": "prune_exec_summary_claim_ledger_orphans",
                    "reason": "align_claim_ledger_with_active_proof_pool",
                    "before": row.get("source_fact_ids"),
                    "after": cleaned,
                }
            )
        row["source_fact_ids"] = cleaned


def _srfs_join_fragments_as_one_sentence(frags: list[str], *, max_parts: int = 3) -> str:
    """Join fact-derived fragments so :func:`split_sentences` counts one S4/S5 (SRFS arc)."""
    parts: list[str] = []
    for raw in frags[:max_parts]:
        t = str(raw or "").strip()
        if not t:
            continue
        t = t.rstrip(".!?")
        if t:
            parts.append(t)
    if not parts:
        return ""
    body = "; ".join(parts)
    return (body[0].upper() + body[1:] + ".") if body else ""


def _first_sentence_from_prose(chunk: str, *, min_len: int = 40, max_len: int = 320) -> str:
    """One sentence for stub glue: split on first strong period after min_len, else hard-cap."""
    c = " ".join(str(chunk).split()).strip()
    if not c:
        return c
    for i, ch in enumerate(c):
        if ch == "." and i + 1 >= min_len:
            return c[: i + 1].strip()
    if len(c) <= max_len:
        return c if c.endswith((".", "!", "?")) else c + "."
    return c[:max_len].rstrip() + "..."


def _fact_body_for_mock_synthesis(claim_text: str) -> str:
    """Use résumé bullet body without leading ``Label:`` clause so stub prose avoids X2 colon-stitch failures."""
    t = str(claim_text).strip()
    if ": " in t and not t.lower().startswith("http"):
        return t.split(": ", 1)[1].strip()
    return t


def _srfs_active_payload(runtime_payload: dict[str, Any]) -> bool:
    return False


def _proof_pool_mode_from_payload(runtime_payload: dict[str, Any]) -> str:
    from apps_rg.runtime.dispatch.input_authority_prompt_block import proof_pool_mode_from_metadata

    pp = runtime_payload.get("proof_pool_metadata") or {}
    return proof_pool_mode_from_metadata(pp if isinstance(pp, dict) else None)


def _build_mock_output_srfs(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    """Offline SRFS stub: five-sentence arc, >=95 words when possible, X2 SRFS gates safe."""
    facts = list(runtime_payload["selected_fact_plan"]["facts"])
    claims: list[dict[str, Any]] = []
    for f in facts:
        bid = str(f["fact_id"])
        ids: list[str] = [bid]
        if f.get("metric_raw"):
            ids.append(f"{bid}_metric_{sha16(str(f['metric_raw']))[:8]}")
        raw_ct = str(f.get("claim_text") or "").strip() or bid
        body = _fact_body_for_mock_synthesis(raw_ct) or raw_ct
        claims.append({"claim_text": body, "source_fact_ids": ids})

    s1 = (
        "Engineering executive building production-grade governed AI platforms for regulated enterprise environments."
    )
    mech_frags: list[str] = []
    commercial_frags: list[str] = []
    cred_frag: str | None = None
    for c in claims:
        body = c["claim_text"]
        bl = body.lower()
        is_cred = any(
            x in bl
            for x in ("fellow", "actuar", "society of actuaries", "aws certified", "databricks", "certification")
        )
        is_comm = bool(re.search(r"[\d$]|revenue|margin|million", bl))
        if is_cred:
            frag = _first_sentence_from_prose(body)
            if frag and cred_frag is None:
                cred_frag = frag
            continue
        if is_comm:
            commercial_frags.append(_first_sentence_from_prose(body) or body)
            continue
        frag = (_first_sentence_from_prose(body) or body).rstrip(".")
        if frag:
            mech_frags.append(frag)

    mech_join = ", ".join(mech_frags[:3]) if mech_frags else (
        "deterministic routing, multi-agent orchestration, graph-aware retrieval, validation controls, and traceability"
    )
    s2 = (
        f"Designs and operates governed runtime architectures that combine {mech_join} to improve reliability, "
        "auditability, and deployment discipline."
    )
    s3 = (
        "Leads the full platform lifecycle across architecture, operating model, engineering scale-out, and "
        "commercialization, converting delivery work into reusable platform services adopted across enterprise programs."
    )
    if commercial_frags:
        s4 = _srfs_join_fragments_as_one_sentence(commercial_frags[:2])
        if not s4:
            s4 = "Captured measurable operating outcomes reflected in the cited executive fact lines."
    else:
        s4 = "Delivered measurable engineering and platform outcomes grounded in the selected executive fact set."

    if cred_frag:
        cf0 = cred_frag.strip()
        if re.match(r"(?i)^holds\b", cf0):
            tail = re.sub(r"(?i)^holds\s+", "", cf0).strip().rstrip(".")
            s5 = (
                f"Pairs {tail} with quantitative engineering and actuarial discipline grounded in the credential fact lines."
            )
        else:
            s5 = cf0
        if not s5.endswith((".", "!", "?")):
            s5 += "."
    else:
        s5 = "Brings disciplined ownership across complex programs while keeping claims confined to selected fact proof."

    if s5.strip().lower().startswith("holds certifications"):
        s5 = (
            "Professional credentials reinforce delivery credibility for regulated stakeholders when the fact ledger "
            "supports them."
        )

    text = f"{s1} {s2} {s3} {s4} {s5}"
    wc = len(re.findall(r"\S+", text))
    if wc > 160:
        s2 = (
            "Designs and operates governed runtime architectures that combine deterministic routing, multi-agent "
            "orchestration, graph-aware retrieval, validation controls, and traceability to improve reliability, "
            "auditability, and deployment discipline."
        )
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc > 160 and commercial_frags:
        cf0 = (commercial_frags[0] or "").strip()
        if cf0:
            s4 = cf0[0].upper() + cf0[1:] if len(cf0) > 1 else cf0.upper()
            if not s4.endswith((".", "!", "?")):
                s4 += "."
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc > 160:
        s4 = "Delivered measurable engineering outcomes grounded in selected executive facts."
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc > 160:
        s3 = (
            "Leads platform lifecycle and commercialization, converting delivery into reusable services across programs."
        )
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc > 160:
        s5 = "Brings disciplined ownership across programs grounded in selected executive facts."
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc > 160:
        s4 = "Delivered measurable outcomes grounded in selected facts."
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))

    pool_small = False
    if wc < 95:
        s3 = s3.rstrip()
        if s3.endswith("."):
            s3 = (
                s3[:-1]
                + ", stressing stakeholder alignment, governed change management, and predictable delivery tempo."
            )
        else:
            s3 += (
                " The operating model stresses stakeholder alignment, governed change management, and predictable delivery "
                "tempo."
            )
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc < 95:
        s2 = s2.rstrip()
        if s2.endswith("."):
            s2 = (
                s2[:-1]
                + ", with additional controls for policy enforcement, evidence retention, and replay-friendly audit traces."
            )
        else:
            s2 += " Additional controls cover policy enforcement, evidence retention, and replay-friendly audit traces."
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc < 95:
        pool_small = True

    # Padding for the 95-word floor can push the stub over 160 words; re-trim to satisfy the SRFS density gate.
    if wc > 160:
        s2 = (
            "Designs governed runtime architectures combining deterministic routing, orchestration, retrieval, "
            "validation, and traceability to improve reliability and auditability."
        )
        s3 = (
            "Leads platform lifecycle and commercialization across enterprise programs and reusable service adoption."
        )
        s4 = "Delivered measurable outcomes grounded in selected executive facts."
        s5 = "Brings disciplined ownership across programs while respecting the offline contract proof pool."
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc > 160:
        s1 = "Engineering executive building governed AI platforms for regulated enterprise environments."
        text = f"{s1} {s2} {s3} {s4} {s5}"
        wc = len(re.findall(r"\S+", text))
    if wc < 95:
        pool_small = True

    self_check: dict[str, Any] = {
        "no_first_person": True,
        "no_inline_source_tags": True,
        "fit_to_evidence": True,
    }
    if pool_small:
        self_check["selected_fact_pool_too_small"] = True
        self_check["selected_fact_pool_too_small_reason"] = "offline_srfs_mock_compact_facts"

    return {
        "resume_display_text": text,
        "claim_ledger": claims,
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
        "gap_notes": [],
        "change_log": [{"operation": "offline_contract_stub", "reason": "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB_SRFS"}],
        "self_check": self_check,
    }


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    """Offline-contract stub: four- or five-sentence executive paragraph (same product shape as live)."""
    if _srfs_active_payload(runtime_payload):
        return _build_mock_output_srfs(runtime_payload)
    facts = list(runtime_payload["selected_fact_plan"]["facts"])
    claims: list[dict[str, Any]] = []
    for f in facts:
        bid = str(f["fact_id"])
        ids: list[str] = [bid]
        if f.get("metric_raw"):
            ids.append(f"{bid}_metric_{sha16(str(f['metric_raw']))[:8]}")
        raw_ct = str(f.get("claim_text") or "").strip() or bid
        body = _fact_body_for_mock_synthesis(raw_ct) or raw_ct
        claims.append({"claim_text": body, "source_fact_ids": ids})

    if claims:
        s2 = _first_sentence_from_prose(claims[min(1, len(claims) - 1)]["claim_text"])
        s3 = _first_sentence_from_prose(claims[min(2, len(claims) - 1)]["claim_text"])
        s4 = _first_sentence_from_prose(claims[-1]["claim_text"])
        text = (
            "Engineering executive accountable for governed AI platform delivery, deterministic runtime controls, "
            "and production-grade reliability across enterprise programs. "
            f"{s2} "
            f"{s3} "
            f"{s4}"
        )
    else:
        text = (
            "Engineering executive focused on governed AI platforms and deterministic runtime controls for enterprise programs. "
            "The operating model binds architecture, delivery governance, and measurable platform outcomes for regulated enterprises. "
            "Traceability, policy gating, and repeatable execution remain the operational through-line across modernization programs. "
            "Commercial and technical leadership stay aligned as teams scale governed agentic capabilities into production."
        )

    return {
        "resume_display_text": text,
        "claim_ledger": claims,
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
        "gap_notes": [],
        "change_log": [{"operation": "offline_contract_stub", "reason": "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"}],
        "self_check": {"no_first_person": True, "no_inline_source_tags": True, "fit_to_evidence": True},
    }


def infer_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]] | None = None,
    *,
    graph_only_fact_tight_synthesis: bool = False,
    artifact_dir: Path | None = None,
) -> tuple[str, str]:
    """Product quality follows X2 + repair ledger (P1 counted regen policy)."""
    _ = (resume_display_text, claim_ledger, graph_only_fact_tight_synthesis)
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    from apps_rg.runtime.section_repair_ledger import infer_product_quality_with_repair_ledger

    return infer_product_quality_with_repair_ledger(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason="REAL_LLM output passed all deterministic X2 gates.",
        artifact_dir=artifact_dir,
    )


def _synthesis_shape_reject_reason(
    resume_display_text: str,
    parsed: dict[str, Any] | None,
    *,
    selected_facts: list[dict[str, Any]] | None = None,
) -> tuple[bool, str]:
    """Return (all_ok, semicolon-joined failure reasons) for pre-X2 synthesis shape."""
    from apps_rg.runtime.sections.executive_summary_composition import check_human_exec_voice
    from apps_rg.runtime.validators.executive_summary_x2 import (
        GENERIC_FILLER,
        check_exec_summary_evidence_utilization,
        check_exec_summary_meta_filler_patterns,
        check_exec_summary_no_credential_dump,
        check_exec_summary_no_mechanism_inventory,
        check_exec_summary_paragraph_max_words,
        check_exec_summary_sentence_count_4_5,
        check_inferred_bridge_claims,
        check_north_star_style_example_echo_unsupported,
        check_cross_fact_display_conflation,
        check_exec_summary_mechanical_opener_stack,
        check_resume_display_colon_space_discipline,
        check_synthesis_quality,
        FIRST_PERSON_PATTERN,
    )

    text = str(resume_display_text or "")
    failures: list[str] = []
    if FIRST_PERSON_PATTERN.search(text):
        failures.append("First-person pronoun found")
    syn_ok, syn_reason = check_synthesis_quality(text)
    if not syn_ok and syn_reason:
        failures.append(syn_reason)
    mech_stack_ok, mech_stack_reason = check_exec_summary_mechanical_opener_stack(text)
    if not mech_stack_ok and mech_stack_reason:
        failures.append(mech_stack_reason)
    if isinstance(parsed, dict):
        conf_ok, conf_reason = check_cross_fact_display_conflation(
            text, list(parsed.get("claim_ledger") or [])
        )
        if not conf_ok and conf_reason:
            failures.append(conf_reason)
    meta_ok, meta_reason = check_exec_summary_meta_filler_patterns(text)
    if not meta_ok and meta_reason:
        failures.append(meta_reason)
    colon_ok, colon_reason = check_resume_display_colon_space_discipline(text)
    if not colon_ok and colon_reason:
        failures.append(colon_reason)
    sent_ok, sent_reason = check_exec_summary_sentence_count_4_5(text)
    if not sent_ok and sent_reason:
        failures.append(sent_reason)
    util_ok, util_reason = check_exec_summary_evidence_utilization(
        text, parsed, selected_facts=selected_facts
    )
    if not util_ok and util_reason:
        failures.append(util_reason)
    bounds_ok, bounds_reason = check_exec_summary_paragraph_max_words(text, parsed)
    if not bounds_ok and bounds_reason:
        failures.append(bounds_reason)
    voice_exec_ok, voice_exec_reason = check_human_exec_voice(text)
    if not voice_exec_ok and voice_exec_reason:
        failures.append(voice_exec_reason)
    filler_hits = [p for p in GENERIC_FILLER if p in text.lower()]
    if filler_hits:
        failures.append(f"generic_filler:{','.join(filler_hits)}")
    bridge_ok, bridge_reason = check_inferred_bridge_claims(text, selected_facts)
    if not bridge_ok and bridge_reason:
        failures.append(bridge_reason)
    mech_ok, mech_reason = check_exec_summary_no_mechanism_inventory(text)
    if not mech_ok and mech_reason:
        failures.append(mech_reason)
    cred_ok, cred_reason = check_exec_summary_no_credential_dump(text)
    if not cred_ok and cred_reason:
        failures.append(cred_reason)
    if selected_facts is not None:
        star_ok, star_reason = check_north_star_style_example_echo_unsupported(text, selected_facts)
        if not star_ok and star_reason:
            failures.append(star_reason)
    if isinstance(parsed, dict):
        from apps_rg.runtime.validators.executive_summary_x2 import (
            check_claim_ledger_materialized_or_gap_excused,
        )

        ledger = list(parsed.get("claim_ledger") or [])
        gaps = list(parsed.get("gap_notes") or [])
        mat_ok, mat_reason = check_claim_ledger_materialized_or_gap_excused(
            text, ledger, gaps
        )
        if not mat_ok and mat_reason:
            failures.append(mat_reason)
    if failures:
        return False, "; ".join(failures)
    return True, ""


def _shape_failure_count(
    resume_display_text: str,
    parsed: dict[str, Any] | None,
    *,
    selected_facts: list[dict[str, Any]] | None = None,
) -> int:
    ok, reason = _synthesis_shape_reject_reason(
        resume_display_text, parsed, selected_facts=selected_facts
    )
    if ok:
        return 0
    return len([part for part in str(reason).split(";") if part.strip()])


def _regen_candidate_preferred(
    *,
    new_fail_count: int,
    new_ledger_rows: int,
    new_word_count: int,
    best_fail_count: int,
    best_ledger_rows: int,
    best_word_count: int,
    monotonicity_accepted: bool,
) -> bool:
    """Prefer candidates that improve shape without trading away weave coverage."""
    if monotonicity_accepted:
        if new_fail_count < best_fail_count:
            return True
        if new_fail_count == best_fail_count and new_ledger_rows > best_ledger_rows:
            return True
        if (
            new_fail_count == best_fail_count
            and new_ledger_rows == best_ledger_rows
            and new_word_count >= best_word_count
        ):
            return True
        return False
    # Monotonicity-rejected drafts may not replace a stronger accepted baseline.
    if new_fail_count < best_fail_count:
        return new_ledger_rows >= best_ledger_rows and new_word_count >= int(best_word_count * 0.9)
    if new_fail_count == best_fail_count:
        return new_ledger_rows > best_ledger_rows and new_word_count >= best_word_count
    return False


def _build_synthesis_repair_user(
    reject_reason: str,
    *,
    attempt_index: int,
    prior_word_count: int,
    prior_ledger_rows: int,
    last_monotonicity_rejected: bool = False,
) -> str:
    blob = str(reject_reason or "").lower()
    attempt_note = ""
    if attempt_index == 1:
        attempt_note = "SECOND rewrite — prior draft still failed shape gates. "
    elif attempt_index >= 2:
        attempt_note = "FINAL rewrite — prior drafts still failed shape gates. "
    length_note = ""
    if "exceeds maximum" in blob:
        length_note = (
            "LENGTH: trim to one executive paragraph (4–5 sentences) without dropping supported proof; "
            "do not remove claim_ledger rows. "
        )
    else:
        length_note = (
            f"LENGTH: keep at least {prior_word_count} words unless trimming only to fix max-word overflow; "
            "do NOT compress or shorten to fix style — expand/restructure instead. "
        )
    if last_monotonicity_rejected:
        length_note += (
            "PRIOR REGEN SHRANK OR DROPPED CLAIM ROWS — next draft must maintain or increase word count "
            f"and claim_ledger rows (minimum {prior_ledger_rows} rows, prefer 5+ when pool has 6+ facts). "
        )
    utilization_note = ""
    if "claim_ledger_rows" in blob or "need_at_least" in blob or "sentence_" in blob:
        utilization_note = (
            "EVIDENCE_WEAVE: add claim_ledger OBJECT rows (one per major sentence) with distinct source_fact_ids "
            "from selected_fact_plan; weave unused high-confidence facts into prose — no repeated sentence themes. "
            "Prefer 5 sentences when the fact pool has 6+ facts. "
        )
    mechanism_note = ""
    if "mechanism_inventory" in blob or "mechanism inventory" in blob:
        mechanism_note = (
            "MECHANISM_CONTROL: sentence 1 = thesis + operating domain ONLY (no routing/orchestration/GraphRAG list). "
            "Max two mechanism terms in any later sentence, only when verbatim in facts. "
            "Do not repeat the same platform sentence twice. "
        )
    meta_note = ""
    if "meta or filler" in blob or "this individual" in blob or "additionally" in blob:
        meta_note = (
        "VOICE: third-person executive (Technology strategy executive who… / Enterprise technology leader who… / Led…); "
        "avoid narrow 'engineering executive' opener when TARGET_TITLE is SVP IT strategy; "
        "no Additionally/Furthermore openers; no \"with extensive experience\" opener. "
        )
    filler_note = ""
    if "generic_filler" in blob or "proven track record" in blob or "bridge phrases" in blob:
        filler_note = (
            'FORBIDDEN PHRASES: "proven track record", "results-driven", "seasoned executive", '
            '"dynamic leader", "strategic leader" — use fact-backed outcomes instead. '
        )
    conflation_note = ""
    if "cross_fact_display_conflation" in blob or "mechanical_opener_stack" in blob:
        conflation_note = (
            "ATTRIBUTION: one major proof theme per sentence — do NOT merge governed AI platform "
            "(fact_engineering_platform_001) with Basel/CCAR 40% reporting-error reduction "
            "(fact_governance_003) or margin expansion (fact_engineering_platform_006) in one causal line. "
            "Weave team 8-to-28 scale (fact_exec_002) into commercialization when selected. "
            "Vary sentence openers; no Led/Successfully/Also/Built chains. "
        )
    return (
        f"SYNTHESIS REJECTED: {reject_reason}. {attempt_note}{length_note}{utilization_note}"
        f"{mechanism_note}{meta_note}{filler_note}{conflation_note}"
        "Return a NEW complete JSON object (RAW JSON only; first char {, last char }). "
        "Rewrite resume_display_text as exactly 4 or 5 period-delimited sentences (one executive paragraph), "
        "fit_to_evidence integrated narrative — not 2-3 compressed sentences; do not pad with filler. "
        "Sentence 1 must be grammatically complete; vary openers (avoid five Led/Built/Delivered chains). "
        "No certification labels in display text. "
        "FORBIDDEN: \"this individual\", \"this executive\", \"the candidate\", "
        "Additionally/Furthermore as sentence openers, "
        "\"An experienced engineering executive with a strong background\", "
        "\"An experienced technology strategy executive with a demonstrated ability\", recruiter filler. "
        "NEVER name TARGET_COMPANY in resume_display_text. "
        "Do NOT use label: detail stitching; no credential/certification dump. "
        "Do NOT end on Fellow of the Society of Actuaries, AWS Certified, Databricks, or credential inventories. "
        "Prioritize platform, governance, commercial, and scale facts from selected_fact_plan. "
        "Use ONLY selected facts for proof; JD and briefing are targeting-only. "
        "THIRD PERSON ONLY. Keep jd_used_as_proof=false. "
        "Expand claim_ledger when adding new supported claims; never emit flat fact-id strings only."
    )


def retry_qwen_for_synthesis(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    *,
    selected_facts: list[dict[str, Any]] | None = None,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
) -> tuple[str, dict[str, Any], str]:
    """Bounded same-authority regeneration when pre-X2 synthesis shape checks fail."""
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        synthesis_regen_max_attempts,
        synthesis_regeneration_enabled,
    )
    from apps_rg.runtime.sections.executive_summary_synthesis_monotonic import (
        evaluate_synthesis_regen_monotonicity,
    )

    if not synthesis_regeneration_enabled():
        return raw_output, parsed, ""

    first_text = str(parsed.get("resume_display_text") or "")
    shape_ok, reject_reason = _synthesis_shape_reject_reason(
        first_text, parsed, selected_facts=selected_facts
    )
    if shape_ok:
        return raw_output, parsed, ""

    max_attempts = synthesis_regen_max_attempts()
    regen_receipt: dict[str, Any] = {
        "schema": "executive_summary_synthesis_regen_v2",
        "triggered": True,
        "reject_reason": reject_reason,
        "first_pass_resume_word_count": len(re.findall(r"\S+", first_text)),
        "first_pass_claim_ledger_rows": len(list(parsed.get("claim_ledger") or [])),
        "max_attempts": max_attempts,
        "attempts": [],
    }
    current_raw = raw_output
    current_parsed = parsed
    parse_err = ""
    baseline_messages = list(messages)
    last_mono_rejected = False

    best_raw = raw_output
    best_parsed = parsed
    best_fail_count = _shape_failure_count(first_text, parsed, selected_facts=selected_facts)
    best_ledger_rows = len(list(parsed.get("claim_ledger") or []))

    for attempt in range(max_attempts):
        resume_text = str(current_parsed.get("resume_display_text") or "")
        prior_wc = len(re.findall(r"\S+", resume_text))
        prior_ledger_rows = len(list(current_parsed.get("claim_ledger") or []))
        shape_ok, reject_reason = _synthesis_shape_reject_reason(
            resume_text, current_parsed, selected_facts=selected_facts
        )
        if shape_ok:
            regen_receipt["accepted"] = True
            regen_receipt["accepted_via"] = "shape_pass"
            regen_receipt["final_resume_word_count"] = prior_wc
            if artifact_dir is not None:
                write_json(artifact_dir / "synthesis_regen_receipt.json", regen_receipt)
            return current_raw, current_parsed, parse_err

        repair_user = _build_synthesis_repair_user(
            reject_reason,
            attempt_index=attempt,
            prior_word_count=prior_wc,
            prior_ledger_rows=prior_ledger_rows,
            last_monotonicity_rejected=last_mono_rejected,
        )
        repair_messages = [
            *baseline_messages,
            {"role": "assistant", "content": current_raw},
            {"role": "user", "content": repair_user},
        ]
        repair_payload = {**provider_payload, "messages": repair_messages}
        result = call_qwen_vllm(
            tag_reasoning_lane(repair_payload, LANE_KEY),
            artifact_dir=artifact_dir,
            run_id=run_id,
        )
        attempt_record: dict[str, Any] = {
            "attempt": attempt + 1,
            "reject_reason": reject_reason,
            "runtime_status": result.runtime_generation_status,
        }
        last_mono_rejected = False
        if result.runtime_generation_status != "REAL_LLM":
            attempt_record["skipped"] = "non_real_llm"
            regen_receipt["attempts"].append(attempt_record)
            break
        new_raw = result.raw_model_output
        new_parsed, new_err = parse_model_json(new_raw)
        parse_err = new_err or ""
        attempt_record["parse_ok"] = bool(new_parsed)
        if new_parsed:
            regen_text = str(new_parsed.get("resume_display_text") or "")
            attempt_record["regen_resume_word_count"] = len(re.findall(r"\S+", regen_text))
            attempt_record["regen_claim_ledger_rows"] = len(list(new_parsed.get("claim_ledger") or []))
            new_fail_count = _shape_failure_count(
                regen_text, new_parsed, selected_facts=selected_facts
            )
            attempt_record["shape_failure_count"] = new_fail_count
            mono_ok, mono_detail = evaluate_synthesis_regen_monotonicity(
                prior_parsed=current_parsed,
                prior_reject_reason=reject_reason,
                new_parsed=new_parsed,
            )
            attempt_record["monotonicity"] = mono_detail
            new_ledger_rows = len(list(new_parsed.get("claim_ledger") or []))
            if mono_ok:
                current_raw = new_raw
                current_parsed = new_parsed
                if artifact_dir is not None and attempt == 0:
                    write_json(artifact_dir / "provider_response_synthesis_regen.json", result.to_dict())
            else:
                last_mono_rejected = True
                attempt_record["skipped"] = "monotonicity_rejected"
            if _regen_candidate_preferred(
                new_fail_count=new_fail_count,
                new_ledger_rows=new_ledger_rows,
                new_word_count=attempt_record["regen_resume_word_count"],
                best_fail_count=best_fail_count,
                best_ledger_rows=best_ledger_rows,
                best_word_count=len(re.findall(r"\S+", str(best_parsed.get("resume_display_text") or ""))),
                monotonicity_accepted=mono_ok,
            ):
                best_fail_count = new_fail_count
                best_ledger_rows = new_ledger_rows
                best_raw = new_raw
                best_parsed = new_parsed
                attempt_record["best_candidate"] = True
        else:
            attempt_record["parse_error"] = new_err
        regen_receipt["attempts"].append(attempt_record)

    final_text = str(current_parsed.get("resume_display_text") or "")
    final_ok, final_reason = _synthesis_shape_reject_reason(
        final_text, current_parsed, selected_facts=selected_facts
    )
    final_fail_count = _shape_failure_count(
        final_text, current_parsed, selected_facts=selected_facts
    )
    best_wc = len(re.findall(r"\S+", str(best_parsed.get("resume_display_text") or "")))
    if (
        not final_ok
        and best_fail_count == 0
        and _regen_candidate_preferred(
            new_fail_count=best_fail_count,
            new_ledger_rows=best_ledger_rows,
            new_word_count=best_wc,
            best_fail_count=final_fail_count,
            best_ledger_rows=len(list(current_parsed.get("claim_ledger") or [])),
            best_word_count=len(re.findall(r"\S+", final_text)),
            monotonicity_accepted=True,
        )
    ):
        current_raw = best_raw
        current_parsed = best_parsed
        regen_receipt["accepted_via"] = "best_candidate_fallback"
        final_text = str(current_parsed.get("resume_display_text") or "")
        final_ok, final_reason = _synthesis_shape_reject_reason(
            final_text, current_parsed, selected_facts=selected_facts
        )
        regen_receipt["best_candidate_shape_failure_count"] = best_fail_count
    elif final_ok:
        regen_receipt["accepted_via"] = regen_receipt.get("accepted_via") or "shape_pass_after_regen"

    regen_receipt["accepted"] = final_ok
    if not final_ok:
        regen_receipt["final_reject_reason"] = final_reason
    regen_receipt["final_resume_word_count"] = len(re.findall(r"\S+", final_text))
    regen_receipt["final_claim_ledger_rows"] = len(list(current_parsed.get("claim_ledger") or []))
    if artifact_dir is not None:
        if regen_receipt.get("triggered") and regen_receipt.get("attempts"):
            from apps_rg.runtime.section_repair_ledger import (
                KIND_REGEN_LLM,
                record_repair,
                set_authoritative_attempt,
            )

            regen_accepted = bool(regen_receipt.get("accepted"))
            record_repair(
                artifact_dir,
                kind=KIND_REGEN_LLM,
                operation="synthesis_regen",
                reason=str(regen_receipt.get("reject_reason") or regen_receipt.get("final_reject_reason") or "")[
                    :240
                ],
                replaced_l2=regen_accepted,
            )
            if regen_accepted:
                set_authoritative_attempt(
                    artifact_dir,
                    2,
                    reason="synthesis_regen_shape_pass",
                )
        write_json(artifact_dir / "synthesis_regen_receipt.json", regen_receipt)
    return current_raw, current_parsed, parse_err


def enrich_parsed_for_x2(
    parsed: dict[str, Any] | None,
    *,
    coverage: dict[str, Any],
    input_payload_hash: str,
    allowed_fact_ids: set[str],
    runtime_payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Attach coverage and stable hashes for X2 metadata gates (same coverage object as artifact)."""
    if parsed is None:
        return None
    enriched = dict(parsed)
    enriched["text_claim_coverage"] = coverage
    if runtime_payload:
        from apps_rg.runtime.c0.c03_graph_ref_policy import (
            build_c0_graph_diagnostics,
            merge_graph_targeting_jd_alignment,
        )

        gt_pa = runtime_payload.get("graph_targeting_for_pa") or {}
        bridge = runtime_payload.get("section_fec_bridge")
        bindings: list[dict[str, Any]] = []
        projection: dict[str, Any] = dict(gt_pa.get("role_family_projection") or {})
        if isinstance(bridge, dict):
            room = bridge.get("c0_evidence_room") or {}
            c03 = room.get("c03") if isinstance(room.get("c03"), dict) else {}
            projection = dict(
                projection or c03.get("role_family_projection") or bridge.get("role_family_projection") or {}
            )
            bindings = list(c03.get("bindings") or [])
        enriched["jd_alignment"] = merge_graph_targeting_jd_alignment(
            enriched.get("jd_alignment") if isinstance(enriched.get("jd_alignment"), dict) else {},
            role_family_projection=projection,
        )
        enriched["c0_graph_diagnostics"] = build_c0_graph_diagnostics(
            bindings,
            role_family_projection=projection,
            resume_display_text=str(enriched.get("resume_display_text") or ""),
        )
    output_body = {
        key: enriched[key]
        for key in (
            "resume_display_text",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
            "text_claim_coverage",
        )
        if key in enriched
    }
    enriched["input_payload_hash"] = input_payload_hash
    enriched["output_payload_hash"] = sha16(json.dumps(output_body, sort_keys=True))
    enriched["claim_ledger_hash"] = sha16(json.dumps(enriched.get("claim_ledger") or [], sort_keys=True))
    enriched["allowed_fact_ids_hash"] = sha16(json.dumps(sorted(allowed_fact_ids), sort_keys=True))
    return enriched


def resolve_provider_model_name(
    provider_request_data: dict[str, Any] | None,
    provider_result_data: dict[str, Any] | None,
) -> str | None:
    if provider_result_data:
        model = provider_result_data.get("model")
        if model:
            return model
    if provider_request_data:
        model = provider_request_data.get("model")
        if model:
            return model
    return None


def write_x2_gate_outputs(
    path: Path,
    gates: list[dict[str, Any]],
    *,
    section_id: str | None = None,
) -> None:
    if section_id:
        from apps_rg.runtime.sections.section_x2_gate_outputs import (
            write_section_x2_gate_outputs,
        )

        write_section_x2_gate_outputs(path.parent, section_id, gates)
        return
    failed = [g["gate_id"] for g in gates if not g["pass"]]
    passed_count = sum(1 for g in gates if g["pass"])
    failed_count = len(failed)
    write_json(
        path,
        {
            "gates": gates,
            "failed_gates": failed,
            "x2_passed": passed_count,
            "x2_failed": failed_count,
            "total_x2_gates": len(gates),
        },
    )


def run_executive_summary_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
) -> dict[str, Any]:
    """Single end-to-end executive_summary run (qwen_vllm): artifacts + X2/X1D/X3."""
    from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
    from apps_rg.runtime.c0.section_proof_loader import (
        apply_proof_pool_to_usage_ledger,
        load_section_proof_for_lane,
    )

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
        section_id="executive_summary",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    selected_fact_plan = pool.selected_fact_plan
    allowed_fact_ids = pool.allowed_fact_ids
    allowed_fact_ids_ordered = list(pool.allowed_fact_ids_ordered)
    proof_pool_metadata = pool.proof_pool_metadata

    provider_resolution_source = coalesce_lane_provider_resolution_source(
        explicit=getattr(args, "provider_resolution_source", None),
        resolved_provider=str(args.provider),
    )
    briefing_raw = str(getattr(args, "briefing", "") or "")
    briefing_eff, briefing_trunc_meta = truncate_briefing_for_exec_summary_vllm(briefing_raw)
    if isinstance(briefing_trunc_meta, dict) and briefing_trunc_meta.get("fail_closed"):
        raise RuntimeError(
            str(briefing_trunc_meta.get("truncation_or_selection_reason") or "briefing_fail_closed")
        )
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        selected_fact_plan=selected_fact_plan,
        target_title=_args_target_title(args),
        target_company=str(getattr(args, "target_company", None) or TARGET_COMPANY_DEFAULT),
        jd_text=_args_jd_text(args),
        briefing=briefing_eff,
        allowed_fact_ids_ordered=allowed_fact_ids_ordered,
    )
    if briefing_trunc_meta is not None:
        runtime_payload["briefing_selection"] = briefing_trunc_meta
    runtime_payload["proof_pool_metadata"] = proof_pool_metadata
    if pool.proof_source == "augmented_skills_graph":
        runtime_payload["graph_only_claim_authority"] = True
        runtime_payload["base_resume_claim_authority"] = False
    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    from apps_rg.runtime.section_repair_ledger import init_ledger

    init_ledger(
        artifact_dir,
        section_id="executive_summary",
        run_id=str(runtime_payload["run_id"]),
    )
    if briefing_trunc_meta is not None:
        write_json(artifact_dir / "briefing_selection_receipt.json", briefing_trunc_meta)
    from apps_rg.runtime.spine.c0_fec_compose import (
        merge_compiled_prompt_artifact_fec_fields,
        wire_spine_c0_fec_for_section,
    )

    wire_spine_c0_fec_for_section(
        artifact_dir=artifact_dir,
        section_id="executive_summary",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
    )
    runtime_payload["section_front_spine_receipt_ref"] = "section_front_spine_receipt.json"
    runtime_payload["proof_pool_front_spine_preconditions"] = {
        "precondition_status": "PASS",
        "status": "PASS",
        "required_contracts": list(front_spine.contracts_emitted().keys()),
        "satisfied": all(front_spine.contracts_emitted().values()),
        "proof_pool_entry_allowed": True,
        "validated_request_ref": "validated_request.json",
        "l1_plan_contract_ref": "l1_plan_contract.json",
        "route_contract_ref": "route_contract.json",
        "receipt_ref": "section_front_spine_receipt.json",
        "canonical_c0_claimed": False,
        "canonical_exit_claimed": False,
        "product_certification": "NOT_CLAIMED",
    }
    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )
    from apps_rg.runtime.sections.lane_artifact_io import runtime_payload_for_json

    payload_for_json = runtime_payload_for_json(runtime_payload)
    input_payload_hash = sha16(json.dumps(payload_for_json, sort_keys=True))
    from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
        ExecutiveSummaryEvidenceCapsuleError,
        _capsule_enabled,
        compile_executive_summary_evidence_capsule,
        write_evidence_capsule_receipt,
    )
    from apps_rg.runtime.sections.executive_summary_token_budget import (
        ExecutiveSummaryTokenBudgetExceeded,
        apply_executive_summary_token_budget_policy,
        estimate_tokens_approximate,
        write_token_budget_receipt,
    )

    evidence_capsule_block_reason: str | None = None
    if _capsule_enabled(runtime_payload):
        try:
            baseline_payload = dict(runtime_payload)
            baseline_payload["evidence_capsule_active"] = False
            baseline_payload["evidence_capsule_disabled"] = True
            baseline_compiled = compile_executive_summary_prompt(
                baseline_payload, run_id=runtime_payload["run_id"]
            )
            before_capsule_est = estimate_tokens_approximate(
                str(baseline_compiled.artifact.messages[0].get("content") or "")
            )
            _, capsule_receipt = compile_executive_summary_evidence_capsule(runtime_payload)
            if before_capsule_est and capsule_receipt.get("capsule_token_estimate") is not None:
                capsule_receipt["capsule_reduction_estimate"] = max(
                    0,
                    before_capsule_est
                    - int(capsule_receipt["capsule_token_estimate"]),
                )
            write_evidence_capsule_receipt(artifact_dir, capsule_receipt)
            section_compiled = compile_executive_summary_prompt(
                runtime_payload, run_id=runtime_payload["run_id"]
            )
            after_capsule_est = estimate_tokens_approximate(
                str(section_compiled.artifact.messages[0].get("content") or "")
            )
            runtime_payload["prompt_token_estimates"] = {
                "before_capsule_prompt_estimate": before_capsule_est,
                "after_capsule_prompt_estimate": after_capsule_est,
            }
        except ExecutiveSummaryEvidenceCapsuleError as cap_exc:
            evidence_capsule_block_reason = str(
                cap_exc.receipt.get("fail_closed_reason") or cap_exc
            )
            write_evidence_capsule_receipt(artifact_dir, cap_exc.receipt)
            runtime_payload["evidence_capsule_policy"] = {
                "fail_closed": True,
                "fail_closed_reason": evidence_capsule_block_reason,
            }
            section_compiled = compile_executive_summary_prompt(
                runtime_payload, run_id=runtime_payload["run_id"]
            )
    else:
        section_compiled = compile_executive_summary_prompt(
            runtime_payload, run_id=runtime_payload["run_id"]
        )

    token_budget_block_reason: str | None = None
    token_budget_receipt: dict[str, Any] | None = None
    max_out_tokens = int(
        os.environ.get(
            "APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS",
            str(_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS),
        )
    )
    if not evidence_capsule_block_reason:
        try:
            section_compiled, token_budget_receipt = apply_executive_summary_token_budget_policy(
                section_compiled,
                runtime_payload=runtime_payload,
                provider=str(args.provider),
                model=str(os.environ.get("QWEN_VLLM_MODEL", DEFAULT_QWEN_MODEL)),
                requested_max_output_tokens=max_out_tokens,
            )
            write_token_budget_receipt(artifact_dir, token_budget_receipt)
        except ExecutiveSummaryTokenBudgetExceeded as budget_exc:
            token_budget_receipt = budget_exc.receipt
            write_token_budget_receipt(artifact_dir, token_budget_receipt)
            token_budget_block_reason = str(
                token_budget_receipt.get("fail_closed_reason") or budget_exc
            )
            runtime_payload["token_budget_policy"] = {
                "fail_closed": True,
                "fail_closed_reason": token_budget_block_reason,
                "dispatch_allowed": False,
                "prompt_shape_preserved": token_budget_receipt.get("prompt_shape_preserved"),
                "evidence_contract_preserved": token_budget_receipt.get(
                    "evidence_contract_preserved"
                ),
            }
    messages = section_compiled.artifact.messages
    compiled_prompt = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    prompt_hash = sha16(compiled_prompt)
    write_json(artifact_dir / "runtime_payload.json", payload_for_json)
    pp_c03 = proof_pool_metadata or {}
    c03_doc = pp_c03.get("c03_graphrag_bound")
    if isinstance(c03_doc, dict):
        write_json(artifact_dir / "c03_graphrag_bound.json", c03_doc)
    native_c03 = pp_c03.get("native_c03_final_evidence")
    if isinstance(native_c03, dict):
        write_json(artifact_dir / "native_c03_final_evidence.json", native_c03)
    fec_snap = pp_c03.get("final_evidence_contract_snapshot")
    if isinstance(fec_snap, dict):
        write_json(artifact_dir / "final_evidence_contract_snapshot.json", fec_snap)
    (artifact_dir / "compiled_prompt.txt").write_text(
        json.dumps(messages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_json(
        artifact_dir / "compiled_prompt_artifact.json",
        merge_compiled_prompt_artifact_fec_fields(
            {
                "section_id": section_compiled.section_id,
                "contract_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "pa_shell_ref": "apps_rg/prompt_assembly/templates/strategic_tailor_v1.yaml",
                "prompt_bom_ref": "apps_rg/prompt_assembly/prompt_bom.yaml",
                "selected_template_id": section_compiled.artifact.template_id,
                "compiler_template_id": section_compiled.artifact.template_id,
                "prompt_hash": prompt_hash,
                "component_hash_map": {
                    "pa_prompt_hash": section_compiled.artifact.prompt_hash,
                    "provider_prompt_hash": prompt_hash,
                },
                "pa_prompt_hash": section_compiled.artifact.prompt_hash,
                "provider_prompt_hash": prompt_hash,
                "slot_count": section_compiled.artifact.slot_count,
                "proof_source": pool.proof_source,
                "proof_pool_ref": pool.proof_pool_ref,
                "proof_pool_digest": pool.proof_pool_digest,
                "base_resume_fallback_used": pool.base_resume_fallback_used,
                "graph_only_claim_authority": pool.proof_source == "augmented_skills_graph",
                "c03_graphrag_bound_status": (proof_pool_metadata or {}).get("c03_graphrag_bound_status"),
                "allowed_source_fact_ids_count": len(allowed_fact_ids),
                **(
                    {
                        "token_budget_trim_applied": token_budget_receipt.get("trim_applied"),
                        "token_budget_receipt_ref": "token_budget_receipt.json",
                    }
                    if token_budget_receipt
                    else {}
                ),
                **(
                    {
                        "evidence_capsule_active": True,
                        "evidence_capsule_receipt_ref": "evidence_capsule_receipt.json",
                    }
                    if runtime_payload.get("evidence_capsule_active")
                    else {}
                ),
            },
            runtime_payload,
        ),
    )

    provider_request_data = None
    provider_result_data = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"

    from apps_rg.runtime.section_l2_lane_integration import prepare_section_l2_before_provider

    prepare_section_l2_before_provider(
        artifact_dir,
        "executive_summary",
        runtime_payload,
        provider_lane=str(args.provider),
    )

    provider_req: Any = None
    provider_payload: dict[str, Any] = {}
    if evidence_capsule_block_reason:
        provider_request_data = {
            "provider_requested": str(args.provider),
            "provider_attempted": False,
            "blocked_before_dispatch": True,
            "fail_closed_reason": evidence_capsule_block_reason,
            "max_tokens": max_out_tokens,
            "evidence_capsule_receipt_ref": "evidence_capsule_receipt.json",
            "mock_fallback_allowed": False,
        }
        write_json(artifact_dir / "provider_request.json", provider_request_data)
        result = ProviderResult(
            provider_requested=str(args.provider),
            provider_attempted=False,
            provider_available=False,
            exact_provider_error=f"L2_BLOCK:{evidence_capsule_block_reason}",
            runtime_generation_status="BLOCKED",
            model=str(os.environ.get("QWEN_VLLM_MODEL", DEFAULT_QWEN_MODEL)),
            raw_model_output="",
            provider_response={
                "evidence_capsule_blocked": True,
                "reason": evidence_capsule_block_reason,
            },
        )
        req_model = str(provider_request_data.get("model") or DEFAULT_QWEN_MODEL)
    elif token_budget_block_reason:
        provider_request_data = {
            "provider_requested": str(args.provider),
            "provider_attempted": False,
            "blocked_before_dispatch": True,
            "fail_closed_reason": token_budget_block_reason,
            "max_tokens": max_out_tokens,
            "token_budget_receipt_ref": "token_budget_receipt.json",
            "mock_fallback_allowed": False,
        }
        write_json(artifact_dir / "provider_request.json", provider_request_data)
        result = ProviderResult(
            provider_requested=str(args.provider),
            provider_attempted=False,
            provider_available=False,
            exact_provider_error=f"L2_BLOCK:{token_budget_block_reason}",
            runtime_generation_status="BLOCKED",
            model=str(os.environ.get("QWEN_VLLM_MODEL", DEFAULT_QWEN_MODEL)),
            raw_model_output="",
            provider_response={"token_budget_blocked": True, "reason": token_budget_block_reason},
        )
        req_model = str(provider_request_data.get("model") or DEFAULT_QWEN_MODEL)
    else:
        provider_req, provider_payload = build_qwen_request(
            messages=messages,
            prompt_hash=prompt_hash,
            input_payload_hash=input_payload_hash,
            temperature=args.temperature,
            max_tokens=max_out_tokens,
        )
        provider_payload = tag_reasoning_lane(provider_payload, LANE_KEY)
        provider_request_data = provider_req.to_dict()
        if token_budget_receipt:
            provider_request_data["token_budget"] = {
                "trim_applied": token_budget_receipt.get("trim_applied"),
                "compiled_prompt_tokens_after_trim": token_budget_receipt.get(
                    "compiled_prompt_tokens_after_trim"
                ),
                "available_input_tokens": token_budget_receipt.get("available_input_tokens"),
                "provider_context_window": token_budget_receipt.get("provider_context_window"),
            }
        write_json(artifact_dir / "provider_request.json", provider_request_data)
        req_model = str(provider_payload.get("model", DEFAULT_QWEN_MODEL))
    if evidence_capsule_block_reason or token_budget_block_reason:
        pass
    else:
        result = call_qwen_vllm(
            provider_payload,
            artifact_dir=artifact_dir,
            run_id=str(runtime_payload.get("run_id") or "") or None,
        )
    provider_result_data = result.to_dict()
    raw_output = result.raw_model_output
    runtime_generation_status = result.runtime_generation_status
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    parse_error = ""
    if result.runtime_generation_status == "REAL_LLM":
        parsed, parse_error = parse_model_json(raw_output)
        if parsed:
            raw_output, parsed, parse_error = retry_qwen_for_synthesis(
                messages,
                provider_payload,
                raw_output,
                parsed,
                selected_facts=list(selected_fact_plan.get("facts") or []),
                artifact_dir=artifact_dir,
                run_id=str(runtime_payload.get("run_id") or "") or None,
            )
        if parsed:
            parsed = normalize_executive_summary_llm_output(parsed, selected_fact_plan)
            prune_exec_summary_claim_ledger_orphans(parsed, allowed_fact_ids)
            from apps_rg.runtime.section_repair_policy import graph_only_reformat_allowed

            if pool.proof_source == "augmented_skills_graph" and graph_only_reformat_allowed():
                from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
                    apply_graph_only_generation_quality_repair,
                    parsed_to_raw_model_output_json as _graph_quality_to_raw,
                )
                from apps_rg.runtime.section_repair_ledger import (
                    KIND_DETERMINISTIC_REWRITE,
                    record_repair,
                )

                _plan_facts = list(selected_fact_plan.get("facts") or [])
                parsed, graph_quality_meta = apply_graph_only_generation_quality_repair(
                    parsed,
                    allowed_fact_ids=allowed_fact_ids,
                    plan_facts=_plan_facts,
                )
                write_json(artifact_dir / "graph_only_generation_quality_repair.json", graph_quality_meta)
                if graph_quality_meta.get("applied") and not graph_quality_meta.get(
                    "skipped_x2_regression"
                ):
                    record_repair(
                        artifact_dir,
                        kind=KIND_DETERMINISTIC_REWRITE,
                        operation="graph_only_generation_quality_repair",
                        reason=str(
                            graph_quality_meta.get("cross_fact_conflation_reason")
                            or graph_quality_meta.get("mechanical_opener_stack_reason")
                            or graph_quality_meta.get("x2_regression_check")
                            or "graph_only_synthesis_violations"
                        )[:240],
                        replaced_l2=True,
                    )
                raw_output = _graph_quality_to_raw(parsed)
        if parsed and isinstance(parsed, dict):
            coerced_resume = coerce_resume_display_sentence_count_band(
                str(parsed.get("resume_display_text") or ""),
            )
            if coerced_resume != parsed.get("resume_display_text"):
                parsed["resume_display_text"] = coerced_resume
            if result.runtime_generation_status == "REAL_LLM":
                raw_output = json.dumps(
                    {k: v for k, v in parsed.items() if k != "selected_fact_plan"},
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
    elif str(result.runtime_generation_status) == OFFLINE_CONTRACT_STUB_RUNTIME_STATUS:
        parsed, parse_error = parse_model_json(raw_output)
        if parsed:
            parsed = normalize_executive_summary_llm_output(parsed, selected_fact_plan)
        else:
            parsed = None
            if not parse_error:
                parse_error = "offline_contract_stub: model JSON parse failed"
    else:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    resume_display_text = (parsed or {}).get("resume_display_text") or raw_output or ""
    _pp_meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    _painting_active = bool(
        _pp_meta.get("graph_skills_proof_pool") or pool.proof_source == "augmented_skills_graph"
    )
    if parsed and isinstance(parsed, dict) and _painting_active:
        from apps_rg.runtime.sections.executive_summary_composition import (
            attach_composition_to_parsed,
            build_executive_summary_composition_plan,
        )

        parsed["resume_display_text"] = resume_display_text
        _plan_facts = list(selected_fact_plan.get("facts") or [])
        composition_plan = build_executive_summary_composition_plan(
            selected_facts=_plan_facts,
            allowed_fact_ids=allowed_fact_ids,
            target_role=str(
                getattr(args, "target_role", None) or getattr(args, "target_title", None) or ""
            ),
            target_company=str(args.target_company or ""),
            proof_pool_metadata=_pp_meta,
        )
        parsed = attach_composition_to_parsed(
            parsed,
            composition_plan,
            resume_display_text=resume_display_text,
        )
        write_json(artifact_dir / "executive_summary_composition_plan.json", composition_plan)
        resume_display_text = str(parsed.get("resume_display_text") or resume_display_text)
        claim_ledger = list(parsed.get("claim_ledger") or [])
    else:
        claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed, parse_error=parse_error, raw_output=raw_output
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
    )
    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)
    if parsed and isinstance(parsed, dict):
        from apps_rg.runtime.sections.section_authority_repairs import (
            apply_exec_summary_display_authority_repairs,
        )

        parsed = apply_exec_summary_display_authority_repairs(
            parsed,
            allowed_fact_ids=allowed_fact_ids,
            plan_facts=list(selected_fact_plan.get("facts") or []),
            artifact_dir=artifact_dir,
            target_company=str(getattr(args, "target_company", "") or ""),
        )
        from apps_rg.runtime.sections.executive_summary_voice_repair import (
            finalize_executive_summary_coherence,
        )

        parsed, finalize_receipt = finalize_executive_summary_coherence(
            parsed,
            selected_facts=list(selected_fact_plan.get("facts") or []),
        )
        if artifact_dir is not None:
            write_json(
                artifact_dir / "executive_summary_finalize_coherence.json",
                finalize_receipt,
            )
            if finalize_receipt.get("voice_repair", {}).get("repaired") or finalize_receipt.get(
                "gap_excuses_added"
            ):
                from apps_rg.runtime.section_repair_ledger import (
                    KIND_MECHANICAL,
                    record_repair,
                )

                record_repair(
                    artifact_dir,
                    kind=KIND_MECHANICAL,
                    operation="executive_summary_finalize_coherence",
                    reason=str(
                        finalize_receipt.get("materialization_reason")
                        or "display_ledger_coherence"
                    )[:240],
                    replaced_l2=True,
                )
        resume_display_text = str(parsed.get("resume_display_text") or resume_display_text)
        claim_ledger = list(parsed.get("claim_ledger") or claim_ledger)
    coverage = build_sentence_claim_coverage(resume_display_text, claim_ledger, allowed_fact_ids)
    parsed_for_x2 = enrich_parsed_for_x2(
        parsed,
        coverage=coverage,
        input_payload_hash=input_payload_hash,
        allowed_fact_ids=allowed_fact_ids,
        runtime_payload=runtime_payload,
    )
    model_name = resolve_provider_model_name(provider_request_data, provider_result_data)
    selected_facts_for_x2 = list(selected_fact_plan.get("facts") or [])
    temperature = float(args.temperature)

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "executive_summary",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "product_quality_reason": "",
        "resume_display_text": resume_display_text,
        "selected_fact_plan": selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment")
        or {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "text_claim_coverage": coverage,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "allowed_fact_ids_hash": (parsed_for_x2 or {}).get("allowed_fact_ids_hash"),
    }
    write_json(artifact_dir / "l2_output.json", l2_output)
    (artifact_dir / "resume_display_text.txt").write_text(resume_display_text + "\n", encoding="utf-8")
    write_json(artifact_dir / "selected_fact_plan.json", l2_output["selected_fact_plan"])
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    sfp_for_usage = (parsed or {}).get("selected_fact_plan") or selected_fact_plan
    ad_res = artifact_dir.resolve()
    try:
        trace_rr = ad_res.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        trace_rr = ad_res.as_posix()
    req_id = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="executive_summary",
        run_id=str(runtime_payload["run_id"]),
        request_id=req_id,
        trace_root=trace_rr,
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=sfp_for_usage if isinstance(sfp_for_usage, dict) else {"facts": []},
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        jd_text=_args_jd_text(args),
        target_title=_args_target_title(args),
        target_company=str(args.target_company),
        briefing_text=str(args.briefing),
        jd_alignment=l2_output.get("jd_alignment"),
    )
    usage_doc = apply_proof_pool_to_usage_ledger(usage_doc, pool)
    runtime_payload["proof_pool_metadata"] = pool.proof_pool_metadata
    write_json(artifact_dir / "section_input_usage_ledger.json", usage_doc)

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_mode = "mocked" if args.mock_judges else "blocked_if_unavailable"
    judge_packet = build_executive_summary_judge_packet(
        resume_display_text=resume_display_text,
        claim_ledger=claim_ledger,
        allowed_fact_packet=selected_facts_for_x2,
        allowed_fact_ids=allowed_fact_ids,
        target_title=_args_target_title(args),
        target_company=str(args.target_company),
        jd_text=_args_jd_text(args),
        briefing_text=str(args.briefing),
        parsed_output=parsed_for_x2,
    )
    judge_packet_ref = write_executive_summary_judge_packet(
        artifact_dir / "executive_summary_judge_packet.json",
        judge_packet,
    )
    x1d = [
        j.to_dict()
        for j in run_llm_judges(
            resume_display_text=resume_display_text,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            mode=judge_mode,
            artifact_base=artifact_dir,
            judge_packet=judge_packet,
            judge_packet_ref=judge_packet_ref,
            compiled_prompt=compiled_prompt,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    trace = {
        "runtime_path": "apps_rg.runtime.sections.executive_summary_lane",
        "prompt_id": PROMPT_ID,
        "provider": args.provider,
        "provider_resolution_source": provider_resolution_source,
        "temperature": temperature,
        "monolithic_prompt_invoked": False,
        "section_prompt_adapter": True,
        "contract_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "pa_shell_ref": "apps_rg/prompt_assembly/templates/strategic_tailor_v1.yaml",
        "prompt_bom_ref": "apps_rg/prompt_assembly/prompt_bom.yaml",
        "selected_template_id": section_compiled.artifact.template_id,
        "compiler_template_id": section_compiled.artifact.template_id,
        "prompt_hash": prompt_hash,
        "component_hash_map": {
            "pa_prompt_hash": section_compiled.artifact.prompt_hash,
            "provider_prompt_hash": prompt_hash,
        },
        "w3_execution_path_bucket": W3_EXECUTION_PATH_BUCKET,
        "w3_execution_path_plan_slug": W3_EXECUTION_PATH_PLAN_SLUG,
    }
    trace = attach_reasoning_to_prompt_trace(
        trace,
        provider=args.provider,
        lane_key=LANE_KEY,
        provider_result_data=provider_result_data if isinstance(provider_result_data, dict) else None,
    )
    write_json(artifact_dir / "prompt_selection_trace.json", trace)
    write_json(artifact_dir / "fact_check_result.json", {"passed": False, "failed_gates": [], "status": "pending"})
    write_json(
        artifact_dir / "real_l2_generation_result.json",
        {
            "provider_attempted": args.provider,
            "runtime_generation_status": runtime_generation_status,
            "prompt_hash": prompt_hash,
            "model": model_name,
            "input_payload_hash": input_payload_hash,
            "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
            "status": "pending",
        },
    )
    write_json(artifact_dir / "x3_disposition.json", {"x3_code": "PENDING", "status": "pending"})
    write_json(artifact_dir / "section_metric_receipt.json", {"status": "pending", "prompt_hash": prompt_hash})
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", [], section_id="executive_summary")

    from apps_rg.runtime.product_evidence_authority import x2_proof_pool_gate_flags

    pp_x2 = runtime_payload.get("proof_pool_metadata") or proof_pool_metadata or {}
    proof_pool_x2_active, _srfs_slice_x2_active = x2_proof_pool_gate_flags(pp_x2)

    x2 = [
        g.to_dict()
        for g in run_x2_gates(
        resume_display_text=resume_display_text,
        parsed_output=parsed_for_x2,
        claim_ledger=claim_ledger,
        text_claim_coverage=coverage,
        allowed_fact_ids=allowed_fact_ids,
        target_company=args.target_company,
        jd_text=args.jd_text,
        temperature=temperature,
        runtime_generation_status=runtime_generation_status,
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        artifacts_dir=artifact_dir,
        provider_requested=args.provider,
        provider_attempted=args.provider,
        model_name=model_name,
        prompt_hash=prompt_hash,
        compiled_prompt=compiled_prompt,
        raw_output=raw_output,
        target_role=args.target_role if hasattr(args, "target_role") else None,
        selected_facts=selected_facts_for_x2,
        x1d_judges=x1d,
        proof_pool_metadata=pp_x2 if proof_pool_x2_active else None,
        proof_pool_ref=str(pool.proof_pool_ref or ""),
        proof_pool_digest=str(pool.proof_pool_digest or ""),
        )
    ]
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        write_x2_source_fact_pool_receipt,
    )

    for g in x2:
        obs = g.get("observed_value")
        if isinstance(obs, dict) and obs.get("x2_source_fact_pool_status"):
            write_x2_source_fact_pool_receipt(artifact_dir, obs)
            break
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2, section_id="executive_summary")
    from apps_rg.runtime.section_repair_ledger import load_ledger, record_x2_run

    _ledger = load_ledger(artifact_dir) or {}
    record_x2_run(
        artifact_dir,
        run_number=len(list(_ledger.get("x2_runs") or [])) + 1,
        after_l2_source=str(_ledger.get("authoritative_l2_source") or "initial_llm"),
        x2_gates=x2,
    )
    write_json(
        artifact_dir / "fact_check_result.json",
        {
            "passed": not [g for g in x2 if not g["pass"]],
            "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        },
    )

    x2_failed_initial = [g for g in x2 if not g["pass"]]
    if runtime_generation_status == "REAL_LLM" and not x2_failed_initial and parsed_for_x2:
        from apps_rg.runtime.section_repair_policy import judge_remediation_regen_allowed
        from apps_rg.runtime.sections.executive_summary_judge_remediation import (
            evaluate_judge_remediation_trigger,
            rerun_soft_failed_judges,
            rerun_x2_after_judge_remediation,
            retry_qwen_for_judge_remediation,
        )
        from apps_rg.runtime.validators.executive_summary_x2 import collect_unused_allowed_fact_ids

        if judge_remediation_regen_allowed():
            trigger_ok, trigger_receipt = evaluate_judge_remediation_trigger(
                x1d,
                runtime_generation_status=runtime_generation_status,
                x2_passed=True,
            )
            write_json(artifact_dir / "judge_remediation_trigger.json", trigger_receipt)
            if trigger_ok:
                _pre_raw = raw_output
                _pre_parsed = dict(parsed_for_x2)
                _pre_resume = resume_display_text
                _pre_ledger = list(claim_ledger)
                _pre_x2 = list(x2)
                unused_ids = collect_unused_allowed_fact_ids(claim_ledger, allowed_fact_ids)
                raw_output, parsed_regen, _j_receipt = retry_qwen_for_judge_remediation(
                    messages,
                    provider_payload,
                    raw_output,
                    parsed_for_x2,
                    x1d_judges=x1d,
                    trigger_receipt=trigger_receipt,
                    selected_fact_plan=selected_fact_plan,
                    allowed_fact_ids=allowed_fact_ids,
                    unused_fact_ids=unused_ids,
                    artifact_dir=artifact_dir,
                    run_id=str(runtime_payload.get("run_id") or "") or None,
                )
                if _j_receipt.get("accepted") or _j_receipt.get("prefilter_applied"):
                    from apps_rg.runtime.section_repair_ledger import (
                        KIND_REGEN_LLM,
                        record_repair,
                        set_authoritative_attempt,
                    )

                    record_repair(
                        artifact_dir,
                        kind=KIND_REGEN_LLM,
                        operation="judge_remediation_regen",
                        reason=str(_j_receipt.get("trigger_reason") or "judge_remediation")[:240],
                        replaced_l2=True,
                    )
                    parsed = parsed_regen
                    from apps_rg.runtime.sections.section_authority_repairs import (
                        apply_exec_summary_display_authority_repairs,
                    )

                    parsed = apply_exec_summary_display_authority_repairs(
                        parsed,
                        allowed_fact_ids=allowed_fact_ids,
                        plan_facts=list(selected_fact_plan.get("facts") or []),
                        artifact_dir=artifact_dir,
                        target_company=str(getattr(args, "target_company", "") or ""),
                    )
                    resume_display_text = str(parsed.get("resume_display_text") or resume_display_text)
                    claim_ledger = list(parsed.get("claim_ledger") or claim_ledger)
                    coverage = build_sentence_claim_coverage(
                        resume_display_text, claim_ledger, allowed_fact_ids
                    )
                    parsed_for_x2 = enrich_parsed_for_x2(
                        parsed,
                        coverage=coverage,
                        input_payload_hash=input_payload_hash,
                        allowed_fact_ids=allowed_fact_ids,
                        runtime_payload=runtime_payload,
                    )
                    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
                    (artifact_dir / "resume_display_text.txt").write_text(
                        resume_display_text + "\n", encoding="utf-8"
                    )
                    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
                    write_json(artifact_dir / "text_claim_coverage.json", coverage)
                    x2_regen = rerun_x2_after_judge_remediation(
                        resume_display_text=resume_display_text,
                        parsed_for_x2=parsed_for_x2,
                        claim_ledger=claim_ledger,
                        text_claim_coverage=coverage,
                        allowed_fact_ids=allowed_fact_ids,
                        args=args,
                        temperature=temperature,
                        runtime_generation_status=runtime_generation_status,
                        artifact_dir=artifact_dir,
                        model_name=model_name,
                        prompt_hash=prompt_hash,
                        compiled_prompt=compiled_prompt,
                        raw_output=raw_output,
                        selected_facts=selected_facts_for_x2,
                        x1d_judges=x1d,
                        proof_pool_metadata=pp_x2 if proof_pool_x2_active else None,
                        proof_pool_ref=str(pool.proof_pool_ref or ""),
                        proof_pool_digest=str(pool.proof_pool_digest or ""),
                    )
                    if not [g for g in x2_regen if not g["pass"]]:
                        x2 = x2_regen
                        _ledger2 = load_ledger(artifact_dir) or {}
                        record_x2_run(
                            artifact_dir,
                            run_number=len(list(_ledger2.get("x2_runs") or [])) + 1,
                            after_l2_source="regen_llm",
                            x2_gates=x2,
                        )
                        set_authoritative_attempt(
                            artifact_dir,
                            2,
                            reason="judge_remediation_regen_x2_pass",
                        )
                        x1d = rerun_soft_failed_judges(
                            resume_display_text=resume_display_text,
                            claim_ledger=claim_ledger,
                            judge_packet=judge_packet,
                            judge_packet_ref=judge_packet_ref,
                            compiled_prompt=compiled_prompt,
                            artifact_dir=artifact_dir,
                            judge_keys=judge_keys,
                            judge_mode=judge_mode,
                            prior_judges=x1d,
                        )
                        write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})
                        write_x2_gate_outputs(
                            artifact_dir / "x2_gate_outputs.json", x2, section_id="executive_summary"
                        )
                        write_json(
                            artifact_dir / "fact_check_result.json",
                            {
                                "passed": True,
                                "failed_gates": [],
                                "judge_remediation_applied": True,
                            },
                        )
                        l2_output["resume_display_text"] = resume_display_text
                        l2_output["claim_ledger"] = claim_ledger
                        l2_output["text_claim_coverage"] = coverage
                        write_json(artifact_dir / "l2_output.json", l2_output)
                    else:
                        raw_output = _pre_raw
                        parsed = _pre_parsed
                        parsed_for_x2 = _pre_parsed
                        resume_display_text = _pre_resume
                        claim_ledger = _pre_ledger
                        x2 = _pre_x2
                        coverage = build_sentence_claim_coverage(
                            resume_display_text, claim_ledger, allowed_fact_ids
                        )
                        (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
                        (artifact_dir / "resume_display_text.txt").write_text(
                            resume_display_text + "\n", encoding="utf-8"
                        )
                        write_json(artifact_dir / "claim_ledger.json", claim_ledger)
                        write_json(artifact_dir / "text_claim_coverage.json", coverage)
                        l2_output["resume_display_text"] = resume_display_text
                        l2_output["claim_ledger"] = claim_ledger
                        l2_output["text_claim_coverage"] = coverage
                        write_json(artifact_dir / "l2_output.json", l2_output)
                        _j_receipt["reverted"] = "post_regen_x2_failed"
                        write_json(artifact_dir / "judge_remediation_receipt.json", _j_receipt)

    _graph_only_repaired = False
    _repair_meta_path = artifact_dir / "graph_only_generation_quality_repair.json"
    if _repair_meta_path.is_file():
        try:
            _graph_only_repaired = bool(
                json.loads(_repair_meta_path.read_text(encoding="utf-8")).get("repaired")
            )
        except (json.JSONDecodeError, OSError):  # guardian: allow-default-fallback -- P2 burndown: fail-soft optional boundary
            _graph_only_repaired = False

    product_quality_status, product_quality_reason = infer_product_quality(
        runtime_generation_status,
        x2,
        resume_display_text,
        claim_ledger,
        graph_only_fact_tight_synthesis=_graph_only_repaired,
        artifact_dir=artifact_dir,
    )
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    from apps_rg.runtime.section_repair_ledger import attach_ledger_summary_to_l2

    attach_ledger_summary_to_l2(l2_output, artifact_dir)
    write_json(artifact_dir / "l2_output.json", l2_output)

    from apps_rg.runtime.spine.section_x3_finalize import finalize_section_lane_x3

    x3 = finalize_section_lane_x3(
        artifact_dir=artifact_dir,
        section_id="executive_summary",
        runtime_payload=runtime_payload,
        aggregate_x3_fn=_aggregate_executive_summary_x3,
        resume_display_text=resume_display_text,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
    )
    from apps_rg.runtime.section_l2_lane_integration import finalize_section_l2_after_output
    from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
        finalize_section_runtime_exhaust_before_l6,
        gate_section_l6_shadow_after_exhaust,
    )
  # guardian: allow-default-fallback -- P2 burndown: fail-soft optional boundary
    finalize_section_l2_after_output(artifact_dir, "executive_summary", runtime_payload)
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "executive_summary", runtime_payload, repo_root=REPO_ROOT
    )

    emit_executive_summary_post_x3_proof_artifacts(
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        x3=x3,
        x2_gates=x2,
    )

    proof_bundle = compute_lane_proof_bundle(
        args,
        section_id="executive_summary",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
    )
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=proof_bundle,
    )
    write_json(artifact_dir / "l2_output.json", l2_output)

    l6_temp = float(args.temperature)
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=None,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)
    post_rt = artifact_dir / "post_runtime"
    post_rt.mkdir(parents=True, exist_ok=True)
    write_json(post_rt / "l6_shadow_eval_package.json", l6)
    write_executive_summary_artifact_inventory(repo_root=REPO_ROOT, artifact_dir=artifact_dir)
    real_result = {
        "provider_attempted": args.provider,
        "provider_available": bool(provider_result_data and provider_result_data.get("provider_available")),
        "exact_provider_error": (provider_result_data or {}).get("exact_provider_error"),
        "runtime_generation_status": runtime_generation_status,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "temperature": temperature,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "allowed_fact_ids_hash": (parsed_for_x2 or {}).get("allowed_fact_ids_hash"),
        "raw_model_output": raw_output,
        "parsed_model_output": parsed_for_x2,
        "resume_display_text": resume_display_text,
        "selected_fact_plan": l2_output["selected_fact_plan"],
        "claim_ledger": claim_ledger,
        "text_claim_coverage": coverage,
        "fact_check_result": {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
        "product_quality_status": product_quality_status,
        "x3_disposition_ref": str(artifact_dir / "x3_disposition.json"),
        "l6_shadow_eval_package_ref": str(artifact_dir / "l6_shadow_eval_package.json"),
    }
    attach_lane_proof_bundle_fields(
        real_result,
        runtime_generation_status=runtime_generation_status,
        bundle=proof_bundle,
    )
    write_json(artifact_dir / "real_l2_generation_result.json", real_result)
    _smr_es = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "executive_summary",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": product_quality_status,
        "x2_failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        "x3_code": x3.x3_code,
        "proof_eligible": proof_bundle["proof_eligible"],
        "judge_proof_eligible": proof_bundle["judge_proof_eligible"],
    }
    merge_normalized_srfs_reporting_into_dict(
        _smr_es,
        section_id="executive_summary",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_es)
    output_lines = []
    output_lines.append("L2_EXECUTIVE_SUMMARY_OUTPUT:")
    output_lines.append(resume_display_text if resume_display_text else f"BLOCKED: {parse_error}")
    output_lines.append("")
    output_lines.append("X1D_LLM_JUDGE_OUTPUTS:")
    output_lines.append("| Provider | Mode | Score | Threshold | Pass | Decisive Failure | Error |")
    output_lines.append("|---|---|---:|---:|---|---|---|")
    for judge in x1d:
        output_lines.append(
            f"| {judge['provider_name']} | {judge['evaluator_mode']} | {judge.get('score')} | {judge.get('threshold')} | {judge.get('pass')} | {judge.get('decisive_failure')} | {judge.get('exact_provider_error') or ''} |"
        )
    output_lines.append("")
    output_lines.append("X2_DETERMINISTIC_GATE_OUTPUTS:")
    for gate in x2:
        output_lines.append(f"- {gate['gate_id']}: {'PASS' if gate['pass'] else 'FAIL'}")
    output_lines.append("")
    output_lines.append("X3_DISPOSITION:")
    output_lines.append(json.dumps(x3.to_dict(), indent=2))
    output_lines.append("")
    output_lines.append("L6_SHADOW_EVAL_PACKAGE:")
    output_lines.append(str(artifact_dir / "l6_shadow_eval_package.json"))
    output_lines.append("offline_only=true")
    output_text = "\n".join(output_lines)
    (artifact_dir / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")
    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    from apps_rg.runtime.section_one_spine_certification_lane_integration import (
        finalize_section_one_spine_certification,
    )

    finalize_section_one_spine_certification(
        artifact_dir,
        "executive_summary",
        runtime_payload,
        proof_bundle=proof_bundle,
        runtime_generation_status=runtime_generation_status,
    )
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="executive_summary",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        provider_resolution_source=provider_resolution_source,
        proof_eligible=proof_bundle["proof_eligible"],
        proof_scope=proof_bundle["proof_scope"],
        test_only_mock_provider=proof_bundle["test_only_mock_provider"],
        runtime_certification=proof_bundle["runtime_certification"],
        x1d_runtime_status=proof_bundle["x1d_runtime_status"],
        judge_proof_eligible=proof_bundle["judge_proof_eligible"],
        provider_proof_eligible=proof_bundle["provider_proof_eligible"],
        test_only_mock_judges=proof_bundle["test_only_mock_judges"],
        proof_closeout_note=proof_bundle.get("proof_closeout_note") or None,
    )
    from apps_rg.runtime.section_l7_binding_lane_integration import finalize_section_l7_binding

    finalize_section_l7_binding(
        artifact_dir,
        section_id="executive_summary",
        runtime_payload=runtime_payload,
        repo_root=REPO_ROOT,
        command_surface="python -m apps_rg --section executive_summary",
    )
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "args": args,
        "runtime_payload": runtime_payload,
        "base_path": base_path,
        "base_hash": base_hash,
        "selected_fact_plan_initial": selected_fact_plan,
        "allowed_fact_ids": allowed_fact_ids,
        "section_compiled": section_compiled,
        "messages": messages,
        "input_payload_hash": input_payload_hash,
        "prompt_hash": prompt_hash,
        "compiled_prompt": compiled_prompt,
        "provider_request_data": provider_request_data,
        "provider_result_data": provider_result_data,
        "raw_output": raw_output,
        "parsed": parsed,
        "parse_error": parse_error,
        "parse_status": parse_status,
        "canon_doc": canon_doc,
        "runtime_generation_status": runtime_generation_status,
        "claim_ledger": claim_ledger,
        "resume_display_text": resume_display_text,
        "coverage": coverage,
        "parsed_for_x2": parsed_for_x2,
        "model_name": model_name,
        "temperature": temperature,
        "l2_output": l2_output,
        "x1d": x1d,
        "x2": x2,
        "x3": x3,
        "trace": trace,
        "product_quality_status": product_quality_status,
        "product_quality_reason": product_quality_reason,
        "provider_requested_resolved": prq,
        "provider_attempted_resolved": pratt,
        "output_text": output_text,
    }


__all__ = [
    "BRIEFING_DEFAULT",
    "EXEC_SUMMARY_TEMP_DEFAULT",
    "EXEC_SUMMARY_TEMP_RANGE",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "PROMPT_ID",
    "PROMPT_TEMPLATE",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "BASE_JSON_DEFAULT",
    "BASE_POINTER",
    "truncate_briefing_for_exec_summary_vllm",
    "build_mock_output",
    "build_prompt_messages",
    "build_runtime_payload",
    "build_selected_fact_plan",
    "check_executive_summary_narrative_shape",
    "check_l2_resume_voice",
    "enrich_parsed_for_x2",
    "extract_allowed_facts",
    "infer_product_quality",
    "load_base_resume",
    "parse_model_json",
    "resolve_provider_model_name",
    "retry_qwen_for_synthesis",
    "run_executive_summary_execution",
    "sha16",
    "write_json",
    "write_x2_gate_outputs",
]
