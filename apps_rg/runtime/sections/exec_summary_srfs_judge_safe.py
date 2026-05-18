"""Deterministic SRFS executive_summary judge-safe repair (apps_rg only).

Tightens S2/S5 prose and claim_ledger IDs to match allowed_fact_packet vocabulary
without weakening X2/X3 or invoking a second Qwen pass.
"""

from __future__ import annotations

import copy
import re
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import split_sentences, srfs_x2_mode_active

# Judge-risk mechanism phrases (not in current SRFS proof pool claim_text).
_JUDGE_RISK_S2_RE = re.compile(
    r"\b(deterministic\s+routing|multi-agent\s+orchestration|graph-aware\s+retrieval|"
    r"sandboxed\s+execution|replayable\s+traces|human\s+escalation\s+controls)\b",
    re.IGNORECASE,
)

_BANNED_PROSE_FRAGMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bwith\s+applied\s+depth\b", re.I), ""),
    (re.compile(r"\bapplied\s+depth\b", re.I), ""),
    (re.compile(r"\bdocumented\s+credential\s+training\b", re.I), ""),
    (re.compile(r"\bcredentialed\s+foundation\s+strength\b", re.I), ""),
    (re.compile(r"\breinforcing\s+credentialed\s+strength\b", re.I), ""),
    (re.compile(r"\bpredictable\s+program\s+governance\b", re.I), ""),
    (re.compile(r"\bquantitative\s+methods\s+and\s+distributed\s+systems\s+engineering\b", re.I), ""),
    (re.compile(r",\s*ensuring\s+seamless\s+integration\s+into\s+enterprise\s+operations\b", re.I), ""),
    (re.compile(r",\s*as summarized in the platform record above\b", re.I), ""),
    (re.compile(r",\s*supporting the platform outcomes above\b", re.I), ""),
    (re.compile(r",\s*closing the executive platform arc above\b", re.I), ""),
    (re.compile(r",\s*with the executive platform record\b", re.I), ""),
    (re.compile(r"\bexecutive platform record above\b", re.I), ""),
    (re.compile(r"\bplatform record above\b", re.I), ""),
    (re.compile(r"\brecord above\b", re.I), ""),
    (re.compile(r"\s{2,}"), " "),
)


def _facts_index(selected_facts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in selected_facts:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("fact_id") or row.get("candidate_fact_id") or "").strip()
        if fid:
            out[fid] = row
    return out


def agentic_ai_supported_in_facts(selected_facts: list[dict[str, Any]]) -> bool:
    for row in selected_facts:
        if not isinstance(row, dict):
            continue
        if "agentic" in str(row.get("claim_text") or "").lower():
            return True
    return False


def build_fact_tight_s1_sentence(selected_facts: list[dict[str, Any]]) -> str:
    """S1 thesis — add agentic AI only when present in allowed SRFS facts."""
    if agentic_ai_supported_in_facts(selected_facts):
        return (
            "Engineering executive building governed agentic AI platforms for "
            "regulated enterprise environments."
        )
    return (
        "Engineering executive building governed AI platforms for regulated enterprise environments."
    )


def build_fact_tight_s2_sentence(selected_facts: list[dict[str, Any]]) -> str:
    """S2 mechanism sentence using vocabulary from allowed executive_summary facts only."""
    by_id = _facts_index(selected_facts)
    if "fact_engineering_platform_005" in by_id:
        if "fact_governance_003" in by_id:
            return (
                "Designs cloud-native microservices across AWS and Databricks Lakehouse with "
                "enterprise data pipelines, vector services, API gateways, and automated validation "
                "frameworks that strengthen reliability and auditability."
            )
        return (
            "Designs cloud-native microservices across AWS and Databricks Lakehouse with "
            "enterprise data pipelines, vector services, API gateways, and identity controls "
            "that strengthen reliability and auditability."
        )
    if "fact_quant_hpc_001" in by_id or "fact_quant_hpc_002" in by_id:
        return (
            "Re-architects containerized microservices and parallel HPC workflows that enable "
            "real-time stress testing and lower end-to-end latency while strengthening reliability."
        )
    if "fact_governance_003" in by_id:
        return (
            "Implements Basel III and CCAR data lineage, cataloging, and automated validation "
            "frameworks that cut regulatory reporting errors and strengthen auditability."
        )
    return (
        "Designs governed platform execution with validation controls that strengthen "
        "reliability and auditability."
    )


def _s5_depth_tail_from_cert_fact(cert_claim: str) -> str:
    """Depth clause allowed only when supported by fact_certs_001 claim_text (no invented domains)."""
    cl = str(cert_claim or "").lower()
    if "actuar" in cl or "fellow of the society" in cl or "fsa" in cl:
        return "actuarial quantitative rigor and enterprise risk discipline"
    if "statistic" in cl:
        return "statistics and quantitative rigor"
    if "causal" in cl:
        return "causal inference and quantitative rigor"
    if "distributed" in cl:
        return "distributed systems engineering depth"
    return "quantitative rigor and enterprise risk discipline"


def build_fact_tight_s5_sentence(selected_facts: list[dict[str, Any]]) -> str:
    """S5 integrated credibility — credentials woven into platform/governance arc (no meta 'above')."""
    by_id = _facts_index(selected_facts)
    if "fact_certs_001" not in by_id:
        return (
            "Brings AWS, Databricks, and platform credentials that align with the selected executive facts."
        )
    depth = _s5_depth_tail_from_cert_fact(str(by_id["fact_certs_001"].get("claim_text") or ""))
    return (
        f"Combines AWS, Databricks, and FSA credentials with {depth} to balance engineering "
        "execution, governance, and commercialization across regulated platform programs."
    )


def s5_needs_integrated_rewrite(sentence: str) -> bool:
    """True when S5 reads as inventory/meta rather than integrated credibility."""
    sl = str(sentence or "").lower()
    return (
        "above" in sl
        or "record above" in sl
        or "platform record" in sl
        or "as shown above" in sl
        or "credential pointer" in sl
        or sl.strip().startswith("pairs aws")
        or sl.strip().startswith("holds ")
        or sl.strip().startswith("holds certifications")
    )


def polish_srfs_sentence_fragments(sentence: str, role: int) -> str:
    s = str(sentence or "").strip()
    if role == 2:
        s = re.sub(
            r",\s*for highly available execution layers\.?$",
            " across highly available execution layers.",
            s,
            flags=re.I,
        )
    if role == 3:
        s = re.sub(
            r",\s*through operating model scale-out\.?$",
            " with operating model scale-out.",
            s,
            flags=re.I,
        )
    return s.strip()


def dedupe_trailing_clause_repeats(sentence: str) -> str:
    """Remove duplicated comma-clauses when density micro-repair overlaps prior prose."""
    body = str(sentence or "").rstrip()
    end = ""
    if body.endswith((".", "!", "?")):
        end = body[-1]
        body = body[:-1]
    for _ in range(4):
        m = re.search(r",\s+([^,]+)$", body)
        if not m:
            break
        frag = m.group(1).strip().lower()
        earlier = body[: m.start()].lower()
        if frag and frag in earlier:
            body = body[: m.start()]
            continue
        break
    return (body + end).strip()


def strip_judge_banned_prose(text: str) -> str:
    out = str(text or "")
    for pattern, repl in _BANNED_PROSE_FRAGMENTS:
        out = pattern.sub(repl, out)
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r",\s*,", ",", out)
    out = re.sub(r"\s+\.", ".", out)
    return re.sub(r"\s{2,}", " ", out).strip()


def canonicalize_srfs_claim_ledger_source_fact_ids(
    claim_ledger: list[dict[str, Any]],
    *,
    executive_summary_fact_ids: frozenset[str],
) -> list[dict[str, Any]]:
    """Collapse *_metric_* sub-IDs to canonical base fact_id when base is in the SRFS slice."""
    out: list[dict[str, Any]] = []
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        patched = copy.deepcopy(row)
        new_ids: list[str] = []
        seen: set[str] = set()
        for fid in patched.get("source_fact_ids") or []:
            s = str(fid).strip()
            if not s:
                continue
            if "_metric_" in s:
                base = s.split("_metric_", 1)[0]
                if base in executive_summary_fact_ids:
                    s = base
            if s not in seen:
                seen.add(s)
                new_ids.append(s)
        patched["source_fact_ids"] = new_ids
        out.append(patched)
    return out


def _replace_sentence(sentences: list[str], index: int, new_sentence: str) -> None:
    if 0 <= index < len(sentences):
        s = new_sentence.strip()
        if s and not s.endswith((".", "!", "?")):
            s += "."
        sentences[index] = s


def _sync_claim_row_for_sentence(
    claim_ledger: list[dict[str, Any]],
    sentence_index: int,
    new_sentence: str,
) -> None:
    if sentence_index < len(claim_ledger) and isinstance(claim_ledger[sentence_index], dict):
        claim_ledger[sentence_index]["claim_text"] = new_sentence.strip().rstrip(".")


def apply_srfs_judge_safe_repair(
    parsed: dict[str, Any],
    selected_facts: list[dict[str, Any]],
    srfs_integration: dict[str, Any] | None,
) -> dict[str, Any]:
    """Tighten resume_display_text and claim_ledger for X1D factual-support alignment."""
    if not isinstance(parsed, dict) or not srfs_x2_mode_active(srfs_integration):
        return parsed

    out = copy.deepcopy(parsed)
    slice_ids = frozenset(
        str(x).strip()
        for x in (srfs_integration or {}).get("executive_summary_selected_fact_ids") or []
        if str(x).strip()
    )

    ledger = list(out.get("claim_ledger") or [])
    if ledger and slice_ids:
        ledger = canonicalize_srfs_claim_ledger_source_fact_ids(
            ledger, executive_summary_fact_ids=slice_ids
        )
        out["claim_ledger"] = ledger

    text = strip_judge_banned_prose(str(out.get("resume_display_text") or ""))
    sentences = [s for s in split_sentences(text) if str(s).strip()]
    if len(sentences) not in (4, 5):
        out["resume_display_text"] = text
        return out

    s1_idx = 0
    s2_idx = 1
    s5_idx = 4 if len(sentences) == 5 else 3

    if agentic_ai_supported_in_facts(selected_facts):
        s1 = sentences[s1_idx]
        if "agentic" not in s1.lower() or "platform record above" in s1.lower():
            new_s1 = build_fact_tight_s1_sentence(selected_facts)
            _replace_sentence(sentences, s1_idx, new_s1)
            if len(ledger) > s1_idx:
                _sync_claim_row_for_sentence(ledger, s1_idx, new_s1)

    s2 = sentences[s2_idx]
    if _JUDGE_RISK_S2_RE.search(s2) or any(
        t in s2.lower()
        for t in ("orchestration", "graph-aware", "deterministic routing", "multi-agent")
    ):
        new_s2 = build_fact_tight_s2_sentence(selected_facts)
        _replace_sentence(sentences, s2_idx, new_s2)
        _sync_claim_row_for_sentence(ledger, s2_idx, new_s2)

    if len(sentences) == 5 and "fact_certs_001" in slice_ids:
        if s5_needs_integrated_rewrite(sentences[s5_idx]):
            new_s5 = build_fact_tight_s5_sentence(selected_facts)
            _replace_sentence(sentences, s5_idx, new_s5)
            if len(ledger) > s5_idx:
                _sync_claim_row_for_sentence(ledger, s5_idx, new_s5)

    cleaned = []
    for i, s in enumerate(sentences):
        role = (1, 2, 3, 4, 5)[min(i, 4)] if len(sentences) == 5 else (1, 2, 3, 4)[min(i, 3)]
        cleaned.append(
            dedupe_trailing_clause_repeats(polish_srfs_sentence_fragments(s, role))
        )
    out["resume_display_text"] = strip_judge_banned_prose(" ".join(cleaned))
    out["claim_ledger"] = ledger
    return out
