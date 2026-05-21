"""Deterministic SRFS executive_summary judge-safe repair (apps_rg only).

Tightens S2/S5 prose and claim_ledger IDs to match allowed_fact_packet vocabulary
without weakening X2/X3 or invoking a second Qwen pass.
"""

from __future__ import annotations

import copy
import json
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
    (re.compile(r"\bbalance engineering execution and governance depth\b", re.I), ""),
    (re.compile(r"\bacross regulated platform programs\b", re.I), ""),
    (re.compile(r"\s{2,}"), " "),
)

_UNSUPPORTED_DENSITY_MICRO_TAILS: tuple[str, ...] = (
    ", integrating identity controls and highly available execution layers",
    ", while strengthening regulated program delivery and audit-ready governance",
)


def _strip_unsupported_density_micro_tails(sentence: str) -> str:
    """Remove legacy density-repair tails not grounded in SRFS claim_text."""
    s = str(sentence or "").strip()
    low = s.lower()
    for tail in _UNSUPPORTED_DENSITY_MICRO_TAILS:
        pos = low.find(tail.lower())
        if pos < 0:
            continue
        s = s[:pos].rstrip()
        if s and not s.endswith((".", "!", "?")):
            s += "."
        low = s.lower()
    return s


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


def _facts_support_blob(selected_facts: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in selected_facts:
        if not isinstance(row, dict):
            continue
        parts.append(str(row.get("claim_text") or ""))
        for mv in row.get("metric_values") or []:
            parts.append(str(mv))
        parts.append(str(row.get("metric_raw") or ""))
    return " ".join(parts).lower()


def _phrase_supported(phrase: str, blob: str) -> bool:
    return str(phrase or "").strip().lower() in blob


def _sentence_has_unsupported_business_metric(sentence: str, blob: str) -> bool:
    sl = str(sentence or "").lower()
    if "gross margin" in sl and "gross margin" not in blob:
        return True
    if re.search(r"\b\d+\s*%", sl):
        for m in re.findall(r"\b(\d+)\s*%", sl):
            if f"{m}%" not in blob and f"{m} %" not in blob:
                return True
    return False


def _sentence_has_unsupported_mechanism_stack(sentence: str, blob: str) -> bool:
    sl = str(sentence or "").lower()
    risky = (
        "vector services",
        "api gateways",
        "cloud-native microservices",
        "data pipelines",
        "operates cloud-native",
        "designs and operates cloud-native",
    )
    return any(r in sl and r not in blob for r in risky)


def _sentence_has_unsupported_commercialization(sentence: str, blob: str) -> bool:
    sl = str(sentence or "").lower()
    risky = (
        "commercialization",
        "reusable platform services",
        "bespoke delivery",
        "enterprise programs",
        "engineering scale-out",
        "operating model",
        "adopted across",
        "converting bespoke",
        "converting delivery",
        "full platform lifecycle",
    )
    return any(r in sl and r not in blob for r in risky)


def _sentence_s1_s2_thesis_echo(s1: str, s2: str) -> bool:
    """True when S2 repeats S1 thesis phrasing instead of mechanism delivery."""
    a = str(s1 or "").lower()
    b = str(s2 or "").lower()
    if "governed agentic ai platform" in a and "governed agentic ai platform" in b:
        return True
    return False


def _sentence_s1_s3_thesis_echo(s1: str, s3: str) -> bool:
    """True when S3 repeats S1 governed-platform thesis instead of lifecycle scope."""
    return _sentence_s1_s2_thesis_echo(s1, s3)


def _sentence_s1_s2_capability_redundant(s1: str, s2: str) -> bool:
    """True when S2 repeats the full fact_engineering_platform_001 capability stack from S1."""
    s2l = str(s2 or "").lower()
    stack_markers = (
        "deterministic routing",
        "multi-agent orchestration",
        "graphrag",
        "sandboxed execution",
        "policy gating",
    )
    if sum(1 for m in stack_markers if m in s2l) >= 3:
        return True
    return _sentence_s1_s2_thesis_echo(s1, s2)


def _srfs_slice_has_platform_004(slice_ids: frozenset[str]) -> bool:
    return any(
        str(fid).strip() == "fact_engineering_platform_004"
        or str(fid).strip().startswith("fact_engineering_platform_004_metric_")
        for fid in slice_ids
    )


def _platform_004_row(by_id: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Prefer platform_004* rows that carry the lab-to-production cycle metric."""
    cycle_row: dict[str, Any] | None = None
    fallback: dict[str, Any] | None = None
    for fid, row in by_id.items():
        if fid != "fact_engineering_platform_004" and not str(fid).startswith(
            "fact_engineering_platform_004_metric_"
        ):
            continue
        claim = str(row.get("claim_text") or "").strip()
        blob = f"{claim} {' '.join(str(x) for x in row.get('metric_values') or [])}"
        if claim and _sentence_has_supported_cycle_metric(claim, blob.lower()):
            return row
        if str(fid).startswith("fact_engineering_platform_004_metric_"):
            cycle_row = row
        elif fid == "fact_engineering_platform_004":
            fallback = row
    return cycle_row or fallback


def _platform_004_cycle_metric_text(by_id: dict[str, dict[str, Any]]) -> str:
    """Lifecycle/outcome metric text from fact_engineering_platform_004* rows."""
    for fid in sorted(by_id.keys()):
        if fid == "fact_engineering_platform_004" or fid.startswith(
            "fact_engineering_platform_004_metric_"
        ):
            raw = str(by_id[fid].get("claim_text") or "").strip()
            blob = f"{raw} {' '.join(str(x) for x in by_id[fid].get('metric_values') or [])}"
            low = blob.lower()
            if "month" in low and "week" in low:
                return raw
    row = _platform_004_row(by_id)
    return str(row.get("claim_text") or "").strip() if row else ""


def _split_claim_at_metric_clause(claim_text: str) -> tuple[str, str]:
    """Split combined platform_004 claim into lifecycle clause and cycle-outcome tail."""
    raw = str(claim_text or "").strip()
    if not raw:
        return "", ""
    low = raw.lower()
    for sep in ("reducing lab-to-production", "from six months", "from 6 months"):
        if sep in low:
            idx = low.index(sep)
            head = raw[:idx].strip().rstrip(",").rstrip(".")
            tail = raw[idx:].strip().rstrip(".")
            return head, tail
    return raw, ""


def _platform_004_lifecycle_clause_for_s3(by_id: dict[str, dict[str, Any]]) -> str:
    """S3 lifecycle clause — verbatim SRFS text without the six-month/three-week outcome tail."""
    row = _platform_004_row(by_id)
    if row is None:
        return ""
    claim = str(row.get("claim_text") or "").strip()
    blob = f"{claim} {' '.join(str(x) for x in row.get('metric_values') or [])}"
    if claim and _sentence_has_supported_cycle_metric(claim, blob.lower()):
        head, _tail = _split_claim_at_metric_clause(claim)
        return head
    return claim


def _platform_004_cycle_outcome_clause_for_s4(by_id: dict[str, dict[str, Any]]) -> str:
    """S4 outcome clause — cycle metric tail from platform_004* rows when present."""
    row = _platform_004_row(by_id)
    if row is not None:
        claim = str(row.get("claim_text") or "").strip()
        blob = f"{claim} {' '.join(str(x) for x in row.get('metric_values') or [])}"
        if claim and _sentence_has_supported_cycle_metric(claim, blob.lower()):
            _head, tail = _split_claim_at_metric_clause(claim)
            if tail:
                return tail
    return _platform_004_cycle_metric_text(by_id)


def _sentence_s3_carries_cycle_metric(sentence: str) -> bool:
    sl = str(sentence or "").lower()
    return ("month" in sl or "6 months" in sl) and ("week" in sl or "3 weeks" in sl)


def _sentence_s3_org_scale_violation(sentence: str) -> bool:
    """S3 lifecycle bridge must not carry team-scale / org-span metrics (X2 shape gate)."""
    sl = str(sentence or "").lower()
    return bool(re.search(r"\b8\s+to\s+28\b", sl)) or "specialist" in sl


def _sentence_s3_s4_duplicate_lifecycle_opener(s3: str, s4: str) -> bool:
    """True when S3 and S4 repeat the same leading lifecycle clause from platform_004."""
    s3l = str(s3 or "").lower().strip()
    s4l = str(s4 or "").lower().strip()
    if not s3l or not s4l:
        return False
    prefix = "standardized ai lifecycle practices"
    return s3l.startswith(prefix) and s4l.startswith(prefix)


def _sentence_s3_has_unsupported_embellishment(sentence: str, blob: str) -> bool:
    sl = str(sentence or "").lower()
    risky = (
        "operating model scale-out and enterprise program adoption",
        "through operating model scale-out",
        "enterprise program adoption",
    )
    return any(r in sl and r not in blob for r in risky)


def _sentence_s2_drops_governance_metric(sentence: str, by_id: dict[str, dict[str, Any]]) -> bool:
    if "fact_governance_003" not in by_id:
        return False
    claim = str(by_id["fact_governance_003"].get("claim_text") or "").lower()
    if "40%" not in claim and "by 40" not in claim:
        return False
    sl = str(sentence or "").lower()
    return "40%" not in sl and "by 40" not in sl


def _sentence_s2_governance_wrong_tense(sentence: str, by_id: dict[str, dict[str, Any]]) -> bool:
    """True when governance fact is past-tense Implemented but prose uses present Implements."""
    if "fact_governance_003" not in by_id:
        return False
    claim = str(by_id["fact_governance_003"].get("claim_text") or "").strip().lower()
    sl = str(sentence or "").lower()
    if not claim.startswith("implemented"):
        return False
    if re.search(r"\bimplements\b", sl) and any(
        p in sl for p in ("basel", "ccar", "regulatory reporting")
    ):
        return True
    return False


def _governance_003_claim_sentence(by_id: dict[str, dict[str, Any]]) -> str:
    claim = str(by_id.get("fact_governance_003", {}).get("claim_text") or "").strip()
    if not claim:
        return ""
    return claim.rstrip(".") + "."


def _sentence_s3_mechanism_lifecycle_stitch(sentence: str) -> bool:
    """True when S3 merges platform mechanism with lifecycle in one stitched sentence."""
    sl = str(sentence or "").lower()
    if ";" in sl:
        return True
    return ("standardized ai lifecycle" in sl or "intake, validation" in sl) and (
        "designed and operationalized" in sl
        or "deterministic routing" in sl
        or "regulated enterprise workflows" in sl
    )


def _sentence_s3_bas_lifecycle_stitch(sentence: str) -> bool:
    """True when S3 fuses Basel/CCAR governance with lifecycle operating-model language."""
    sl = str(sentence or "").lower()
    gov = any(p in sl for p in ("basel", "ccar", "regulatory reporting errors"))
    lifecycle = any(
        p in sl
        for p in ("lifecycle", "operating model", "engineering scale-out", "architecture")
    )
    return gov and lifecycle


def _sentence_has_supported_cycle_metric(sentence: str, blob: str) -> bool:
    sl = str(sentence or "").lower()
    if not (("month" in sl or "6 months" in sl) and ("week" in sl or "3 weeks" in sl)):
        return False
    return (
        "6 months to 3 weeks" in blob
        or "six months to three weeks" in blob
        or ("6 months" in blob and "3 weeks" in blob)
    )


def _sentence_supports_004_lifecycle_arc(s3: str, blob: str) -> bool:
    """True when S3 already carries a supported lifecycle clause without Basel stitch."""
    if _sentence_has_unsupported_commercialization(s3, blob):
        return False
    sl = str(s3 or "").lower()
    if _sentence_s3_bas_lifecycle_stitch(s3):
        return False
    lifecycle_ok = any(
        p in sl
        for p in (
            "standardized ai lifecycle",
            "lab-to-production",
            "six months",
            "three weeks",
            "6 months",
            "3 weeks",
        )
    )
    return lifecycle_ok and (
        "lifecycle" in blob or "month" in blob or "week" in blob
    )


def _sentence_s2_dual_thread_overload(sentence: str) -> bool:
    """True when S2 fuses platform mechanism and Basel/CCAR governance in one run-on."""
    sl = str(sentence or "").lower()
    platform_thread = any(
        p in sl
        for p in (
            "graphrag",
            "multi-agent",
            "agentic ai platform capabilities",
            "deterministic routing",
        )
    )
    gov_thread = any(p in sl for p in ("basel", "ccar", "regulatory reporting errors"))
    return platform_thread and gov_thread


def _sentence_s4_needs_fact_tight_rewrite(
    sentence: str,
    selected_facts: list[dict[str, Any]],
    blob: str,
) -> bool:
    """True when S4 adds outcomes beyond fact_exec_002 / allowed substrate."""
    if _sentence_has_supported_cycle_metric(sentence, blob):
        return False
    by_id = _facts_index(selected_facts)
    if "fact_exec_002" not in by_id:
        return (
            _sentence_has_unsupported_business_metric(sentence, blob)
            or _sentence_has_unsupported_commercialization(sentence, blob)
        )
    sl = str(sentence or "").lower()
    claim = str(by_id["fact_exec_002"].get("claim_text") or "").lower()
    risky = (
        "revenue",
        "revenue growth",
        "significant revenue",
        "significant growth",
        "gross margin",
        "commercialization",
        "ip-led",
        "$22",
    )
    if any(r in sl and r not in claim and r not in blob for r in risky):
        return True
    return (
        _sentence_has_unsupported_business_metric(sentence, blob)
        or _sentence_has_unsupported_commercialization(sentence, blob)
    )


def _sentence_s3_needs_lifecycle_rewrite(sentence: str) -> bool:
    """True when S3 reads as tactical tooling without lifecycle / operating-model scope."""
    sl = str(sentence or "").lower()
    tactical = "dependency graph" in sl or "legacy-system analysis" in sl
    lifecycle = any(
        p in sl for p in ("lifecycle", "operating model", "engineering scale-out", "architecture")
    )
    return tactical and not lifecycle


def build_fact_tight_s2_sentence(selected_facts: list[dict[str, Any]]) -> str:
    """S2 mechanism — governance thread or narrow mechanism, not a repeat of S1 capability stack."""
    by_id = _facts_index(selected_facts)
    if "fact_governance_003" in by_id:
        gov = _governance_003_claim_sentence(by_id)
        if gov:
            return gov
    if "fact_engineering_platform_001" in by_id and "fact_engineering_platform_002" in by_id:
        return (
            "Applies software dependency graph intelligence to expose dependency chains "
            "and reduce refactor risk across governed platform delivery."
        )
    if "fact_engineering_platform_001" in by_id:
        return (
            "Operationalizes policy gating and validation controls that strengthen "
            "reliability and auditability for regulated enterprise workflows."
        )
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


def _platform_001_regulated_workflows_clause(by_id: dict[str, dict[str, Any]]) -> str:
    """Narrow platform-delivery clause from fact_engineering_platform_001 without mechanism stack."""
    row = by_id.get("fact_engineering_platform_001")
    if not isinstance(row, dict):
        return ""
    claim = str(row.get("claim_text") or "").strip()
    low = claim.lower()
    marker = ", including"
    if marker in low:
        return claim[: low.index(marker)].strip().rstrip(",")
    if "regulated enterprise workflows" in low:
        return claim
    return ""


def _platform_004_claim_has_cycle_metric(by_id: dict[str, dict[str, Any]]) -> bool:
    return _platform_004_row(by_id) is not None and bool(
        _platform_004_cycle_metric_text(by_id)
    )


def build_fact_tight_s3_sentence(selected_facts: list[dict[str, Any]]) -> str:
    """S3 lifecycle / delivery scope — executive platform arc, not standalone tactical tooling."""
    by_id = _facts_index(selected_facts)
    lifecycle_clause = _platform_004_lifecycle_clause_for_s3(by_id)
    if lifecycle_clause:
        return lifecycle_clause.rstrip(".") + "."
    row_004 = _platform_004_row(by_id)
    if row_004 is not None:
        lifecycle = str(row_004.get("claim_text") or "").strip()
        if lifecycle and not _sentence_has_supported_cycle_metric(lifecycle, lifecycle.lower()):
            return lifecycle.rstrip(".") + "."
    has_001 = "fact_engineering_platform_001" in by_id
    has_002 = "fact_engineering_platform_002" in by_id
    has_003 = "fact_governance_003" in by_id
    if has_001 and has_003 and has_002:
        return (
            "Leads platform lifecycle across architecture and operating model with engineering "
            "scale-out; uses dependency graph intelligence to reduce refactor risk; implements "
            "Basel III and CCAR validation frameworks that cut regulatory reporting errors by 40%."
        )
    if has_001 and has_003:
        return (
            "Leads platform lifecycle across architecture, operating model, and engineering scale-out, "
            "and implements Basel III and CCAR data lineage, cataloging, and automated validation "
            "frameworks that cut regulatory reporting errors by 40%."
        )
    if has_001 and has_002:
        return (
            "Leads platform lifecycle across architecture, operating model, and engineering scale-out, "
            "applying software dependency graph intelligence to expose dependency chains and reduce "
            "refactor risk."
        )
    if has_001:
        return (
            "Leads platform lifecycle work across architecture, operating model, and "
            "engineering scale-out for governed agentic AI delivery."
        )
    if has_002:
        return (
            "Advances platform lifecycle delivery through software dependency graph intelligence "
            "that accelerates legacy-system analysis and reduces refactor risk."
        )
    if has_003:
        return str(by_id["fact_governance_003"].get("claim_text") or "").strip().rstrip(".") + "."
    return "Leads platform lifecycle work across architecture and engineering scale-out."


def _capitalize_sentence_start(text: str) -> str:
    s = str(text or "").strip()
    if s and s[0].islower():
        return s[0].upper() + s[1:]
    return s


def build_fact_tight_s4_sentence(selected_facts: list[dict[str, Any]]) -> str:
    """S4 measurable outcomes — metrics only from cited fact claim_text / metric_values."""
    by_id = _facts_index(selected_facts)
    if _platform_004_claim_has_cycle_metric(by_id):
        if _platform_001_regulated_workflows_clause(by_id) and _platform_004_lifecycle_clause_for_s3(by_id):
            outcome = _platform_004_cycle_outcome_clause_for_s4(by_id)
            if outcome:
                return _capitalize_sentence_start(outcome.rstrip(".") + ".")
    row_004 = _platform_004_row(by_id)
    if row_004 is not None and _platform_004_claim_has_cycle_metric(by_id):
        full = str(row_004.get("claim_text") or "").strip()
        if full:
            return _capitalize_sentence_start(full.rstrip(".") + ".")
    cycle = _platform_004_cycle_metric_text(by_id)
    if cycle:
        return _capitalize_sentence_start(cycle.rstrip(".") + ".")
    if "fact_exec_002" in by_id:
        return str(by_id["fact_exec_002"].get("claim_text") or "").strip().rstrip(".") + "."
    if "fact_governance_003" in by_id:
        return str(by_id["fact_governance_003"].get("claim_text") or "").strip().rstrip(".") + "."
    return "Delivers measurable platform outcomes supported by the selected fact plan."


def build_fact_tight_s5_sentence(selected_facts: list[dict[str, Any]]) -> str:
    """S5 executive arc closure — credentials tied to governed platform and risk-aware design."""
    by_id = _facts_index(selected_facts)
    if "fact_certs_001" not in by_id:
        return (
            "Brings AWS, Databricks, and platform credentials that align with the selected executive facts."
        )
    if "fact_quant_hpc_003" in by_id:
        cert_claim = str(by_id["fact_certs_001"].get("claim_text") or "").strip()
        if cert_claim.lower().startswith("holds "):
            cert_claim = cert_claim[6:].strip()
        if cert_claim:
            return (
                f"Brings {cert_claim.rstrip('.')} together with derivatives pricing and "
                "capital modeling experience to strengthen enterprise risk discipline on "
                "regulated platform programs."
            )
        return (
            "Brings AWS, Databricks, and FSA credentials together with derivatives pricing and "
            "capital modeling experience to strengthen enterprise risk discipline on regulated "
            "platform programs."
        )
    return (
        "Brings AWS, Databricks, and FSA credentials to strengthen enterprise risk discipline "
        "on regulated platform programs."
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
        or "platform/governance depth" in sl
        or "balance engineering execution" in sl
        or "across regulated platform programs" in sl
        or sl.strip().startswith("pairs aws")
        or sl.strip().startswith("holds ")
        or sl.strip().startswith("holds certifications")
        or sl.strip().startswith("combines aws")
        or sl.strip().startswith("applies aws")
        or " applies aws" in sl
        or " applies " in sl and "credentials" in sl
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
        for tail in (
            r",\s*integrating identity controls and highly available execution layers\.?$",
            r",\s*integrating identity controls\.?$",
        ):
            s = re.sub(tail, ".", s, flags=re.I)
    if role == 3:
        for tail in (
            r",\s*through operating model scale-out and enterprise program adoption\.?$",
            r",\s*through operating model scale-out\.?$",
            r",\s*with operating model scale-out and enterprise program adoption\.?$",
        ):
            s = re.sub(tail, ".", s, flags=re.I)
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


def _source_fact_ids_for_s1(selected_facts: list[dict[str, Any]], slice_ids: frozenset[str]) -> list[str]:
    by_id = _facts_index(selected_facts)
    for fid in ("fact_engineering_platform_001", "fact_engineering_platform_005", "fact_engineering_platform_006"):
        if fid in by_id and fid in slice_ids:
            return [fid]
    for fid in sorted(slice_ids):
        if fid in by_id:
            return [fid]
    return []


def _source_fact_ids_for_s2(selected_facts: list[dict[str, Any]], slice_ids: frozenset[str]) -> list[str]:
    by_id = _facts_index(selected_facts)
    if "fact_engineering_platform_001" in by_id and "fact_governance_003" in by_id:
        if "fact_governance_003" in slice_ids:
            return ["fact_governance_003"]
    if "fact_engineering_platform_001" in by_id and "fact_engineering_platform_002" in by_id:
        ids = [
            x
            for x in ("fact_engineering_platform_002", "fact_engineering_platform_001")
            if x in slice_ids
        ]
        return ids[:1] if ids else []
    if "fact_engineering_platform_001" in by_id:
        return ["fact_engineering_platform_001"] if "fact_engineering_platform_001" in slice_ids else []
    if "fact_engineering_platform_005" in by_id and "fact_governance_003" in by_id:
        return [x for x in ("fact_engineering_platform_005", "fact_governance_003") if x in slice_ids]
    if "fact_engineering_platform_005" in by_id:
        return ["fact_engineering_platform_005"] if "fact_engineering_platform_005" in slice_ids else []
    if "fact_governance_003" in by_id:
        return ["fact_governance_003"] if "fact_governance_003" in slice_ids else []
    return []


def _source_fact_ids_for_s3(
    selected_facts: list[dict[str, Any]],
    slice_ids: frozenset[str],
    sentence: str = "",
) -> list[str]:
    by_id = _facts_index(selected_facts)
    sl = str(sentence or "").lower()
    ids: list[str] = []
    if "fact_exec_002" in by_id and "fact_exec_002" in slice_ids:
        if any(k in sl for k in ("scaled ml", "8 to 28", "platform leads", "specialists")):
            ids.append("fact_exec_002")
    if "fact_engineering_platform_004" in by_id and "fact_engineering_platform_004" in slice_ids:
        if any(
            k in sl
            for k in (
                "lifecycle",
                "lab-to-production",
                "bespoke",
                "reusable",
                "six months",
                "three weeks",
                "auditability",
                "standardized ai lifecycle",
            )
        ):
            ids.append("fact_engineering_platform_004")
    if "fact_engineering_platform_001" in by_id and "fact_engineering_platform_001" in slice_ids:
        if any(
            k in sl
            for k in (
                "lifecycle",
                "operating model",
                "architecture",
                "scale-out",
                "agentic ai delivery",
                "regulated enterprise workflows",
            )
        ):
            ids.append("fact_engineering_platform_001")
    if "fact_engineering_platform_002" in by_id and "fact_engineering_platform_002" in slice_ids:
        if any(k in sl for k in ("dependency graph", "legacy-system", "refactor risk")):
            ids.append("fact_engineering_platform_002")
    if "fact_governance_003" in by_id and "fact_governance_003" in slice_ids:
        if any(k in sl for k in ("basel", "ccar", "40%", "regulatory reporting")):
            ids.append("fact_governance_003")
    if not ids and "fact_engineering_platform_001" in by_id and "fact_engineering_platform_001" in slice_ids:
        ids.append("fact_engineering_platform_001")
    return ids


def _source_fact_ids_for_s4(selected_facts: list[dict[str, Any]], slice_ids: frozenset[str]) -> list[str]:
    by_id = _facts_index(selected_facts)
    sl_candidates: list[str] = []
    for fid in slice_ids:
        if fid == "fact_engineering_platform_004" or fid.startswith(
            "fact_engineering_platform_004_metric_"
        ):
            sl_candidates.append("fact_engineering_platform_004")
            break
    if sl_candidates:
        return sl_candidates
    if "fact_exec_002" in by_id and "fact_exec_002" in slice_ids:
        return ["fact_exec_002"]
    if "fact_governance_003" in by_id and "fact_governance_003" in slice_ids:
        return ["fact_governance_003"]
    return []


def _source_fact_ids_for_s5(
    selected_facts: list[dict[str, Any]],
    slice_ids: frozenset[str],
    sentence: str,
) -> list[str]:
    by_id = _facts_index(selected_facts)
    ids: list[str] = []
    if "fact_certs_001" in by_id and "fact_certs_001" in slice_ids:
        ids.append("fact_certs_001")
    sl = str(sentence or "").lower()
    if (
        (
            "actuarial" in sl
            or "derivatives pricing" in sl
            or "capital modeling" in sl
            or "grounds governed" in sl
            or "risk-aware ai validation" in sl
            or "brings aws" in sl
            or "quantitative rigor" in sl
            or "enterprise risk discipline" in sl
        )
        and "fact_quant_hpc_003" in by_id
        and "fact_quant_hpc_003" in slice_ids
    ):
        ids.append("fact_quant_hpc_003")
    return ids


def _sync_claim_row_for_sentence(
    claim_ledger: list[dict[str, Any]],
    sentence_index: int,
    new_sentence: str,
    *,
    source_fact_ids: list[str] | None = None,
) -> None:
    if sentence_index < len(claim_ledger) and isinstance(claim_ledger[sentence_index], dict):
        claim_ledger[sentence_index]["claim_text"] = new_sentence.strip().rstrip(".")
        if source_fact_ids is not None:
            claim_ledger[sentence_index]["source_fact_ids"] = list(source_fact_ids)


_SRFS_DENSITY_GATE_MIN = 95
_CREDENTIAL_MARKERS = (
    "aws",
    "certified",
    "databricks",
    "fellow",
    "credentials",
    "fsa",
    "society of actuaries",
)


def _resume_word_count(resume_display_text: str) -> int:
    from apps_rg.runtime.validators.executive_summary_x2 import _resume_word_count as _wc

    return _wc(resume_display_text)


def _resume_sentence_count(resume_display_text: str) -> int:
    return len([s for s in split_sentences(resume_display_text) if str(s).strip()])


def _normalize_sentence_for_dup(sentence: str) -> str:
    return re.sub(r"\s+", " ", str(sentence or "").lower().strip().rstrip("."))


def _sentences_substantially_duplicate(a: str, b: str) -> bool:
    if not a or not b:
        return False
    if a == b:
        return True
    if "regulatory reporting errors by 40" in a and "regulatory reporting errors by 40" in b:
        return True
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    if len(shorter) >= 40 and shorter in longer:
        return True
    wa = set(re.findall(r"[a-z0-9]+", a))
    wb = set(re.findall(r"[a-z0-9]+", b))
    if not wa or not wb:
        return False
    inter = len(wa & wb)
    union = len(wa | wb)
    return inter / union >= 0.72


def duplicate_sentence_or_claim_count(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]] | None,
) -> int:
    """Count duplicate sentence pairs and duplicate claim_text rows."""
    sentences = [
        _normalize_sentence_for_dup(s) for s in split_sentences(resume_display_text) if str(s).strip()
    ]
    dup = 0
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            if _sentences_substantially_duplicate(sentences[i], sentences[j]):
                dup += 1
    claims: list[str] = []
    for row in claim_ledger or []:
        if not isinstance(row, dict):
            continue
        ct = _normalize_sentence_for_dup(str(row.get("claim_text") or ""))
        if ct:
            claims.append(ct)
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            if _sentences_substantially_duplicate(claims[i], claims[j]):
                dup += 1
    return dup


def _has_s5_credentials(resume_display_text: str) -> bool:
    sentences = [s for s in split_sentences(resume_display_text) if str(s).strip()]
    if not sentences:
        return False
    for sent in (sentences[-1], *sentences):
        sl = sent.lower()
        if any(marker in sl for marker in _CREDENTIAL_MARKERS):
            return True
    return False


def _s5_credentials_required(
    pre_parsed: dict[str, Any],
    slice_ids: frozenset[str],
) -> bool:
    if "fact_certs_001" not in slice_ids:
        return False
    if _has_s5_credentials(str(pre_parsed.get("resume_display_text") or "")):
        return True
    plan = pre_parsed.get("executive_summary_composition_plan")
    if not isinstance(plan, dict):
        return False
    for bs in plan.get("brushstrokes") or []:
        if not isinstance(bs, dict):
            continue
        if bs.get("brushstroke_id") == "B4_business_role_fit":
            req = [str(x).strip() for x in (bs.get("required_fact_ids") or []) if str(x).strip()]
            if "fact_certs_001" in req:
                return True
    return False


def _brushstroke_coverage(
    parsed: dict[str, Any],
    slice_ids: frozenset[str],
) -> tuple[int, int]:
    from apps_rg.runtime.sections.executive_summary_composition import _fact_id_base

    plan = parsed.get("executive_summary_composition_plan")
    if not isinstance(plan, dict):
        return 0, 0
    allowed = {_fact_id_base(x) for x in slice_ids}
    cited: set[str] = set()
    for row in parsed.get("claim_ledger") or []:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            cited.add(_fact_id_base(str(fid)))
    total = 0
    supported = 0
    for bs in plan.get("brushstrokes") or []:
        if not isinstance(bs, dict) or bs.get("support_status") == "SKIPPED":
            continue
        total += 1
        req = [_fact_id_base(str(x)) for x in (bs.get("required_fact_ids") or []) if str(x).strip()]
        if any(r in cited or r in allowed for r in req):
            supported += 1
    return supported, total


def collect_monotonic_x2_failed_gates(
    parsed: dict[str, Any],
    selected_facts: list[dict[str, Any]],
    srfs_integration: dict[str, Any] | None,
) -> list[str]:
    """Subset of SRFS X2 gates used for judge-safe repair monotonic acceptance."""
    from apps_rg.runtime.sections.executive_summary_composition import (
        check_brushstroke_fact_support,
        check_dominant_brushstroke_coherence,
        check_mechanism_inventory_control,
    )
    from apps_rg.runtime.validators.executive_summary_x2 import (
        check_srfs_density_word_count,
        check_srfs_sentence_count_4_5,
        check_srfs_sentence_responsibility_shape,
    )

    if not isinstance(parsed, dict) or not srfs_x2_mode_active(srfs_integration):
        return []

    text = str(parsed.get("resume_display_text") or "")
    slice_ids = frozenset(
        str(x).strip()
        for x in (srfs_integration or {}).get("executive_summary_selected_fact_ids") or []
        if str(x).strip()
    )
    plan = parsed.get("executive_summary_composition_plan")
    ledger = list(parsed.get("claim_ledger") or [])
    failed: list[str] = []

    checks: list[tuple[str, tuple[bool, str | None]]] = [
        (
            "x2_exec_summary_srfs_density_word_count",
            check_srfs_density_word_count(text, parsed, srfs_integration),
        ),
        (
            "x2_exec_summary_srfs_sentence_count_4_5",
            check_srfs_sentence_count_4_5(text, srfs_integration),
        ),
        (
            "x2_exec_summary_srfs_sentence_responsibility_shape",
            check_srfs_sentence_responsibility_shape(text, srfs_integration),
        ),
    ]
    if isinstance(plan, dict):
        checks.extend(
            [
                (
                    "x2_exec_summary_dominant_brushstroke_coherence",
                    check_dominant_brushstroke_coherence(text, plan),
                ),
                (
                    "x2_exec_summary_mechanism_inventory_control",
                    check_mechanism_inventory_control(text),
                ),
                (
                    "x2_exec_summary_brushstroke_fact_support",
                    check_brushstroke_fact_support(plan, ledger, slice_ids),
                ),
            ]
        )

    for gate_id, (ok, _reason) in checks:
        if not ok:
            failed.append(gate_id)
    return failed


def evaluate_judge_safe_repair_monotonicity(
    pre_parsed: dict[str, Any],
    post_parsed: dict[str, Any],
    selected_facts: list[dict[str, Any]],
    srfs_integration: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compare pre/post repair for monotonic X2 and prose-quality constraints."""
    slice_ids = frozenset(
        str(x).strip()
        for x in (srfs_integration or {}).get("executive_summary_selected_fact_ids") or []
        if str(x).strip()
    )
    pre_text = str(pre_parsed.get("resume_display_text") or "")
    post_text = str(post_parsed.get("resume_display_text") or "")
    pre_wc = _resume_word_count(pre_text)
    post_wc = _resume_word_count(post_text)
    pre_sc = _resume_sentence_count(pre_text)
    post_sc = _resume_sentence_count(post_text)
    pre_failed = collect_monotonic_x2_failed_gates(pre_parsed, selected_facts, srfs_integration)
    post_failed = collect_monotonic_x2_failed_gates(post_parsed, selected_facts, srfs_integration)
    pre_dup = duplicate_sentence_or_claim_count(pre_text, list(pre_parsed.get("claim_ledger") or []))
    post_dup = duplicate_sentence_or_claim_count(post_text, list(post_parsed.get("claim_ledger") or []))
    pre_cov = _brushstroke_coverage(pre_parsed, slice_ids)
    post_cov = _brushstroke_coverage(post_parsed, slice_ids)
    s5_required = _s5_credentials_required(pre_parsed, slice_ids)
    pre_s5 = _has_s5_credentials(pre_text)
    post_s5 = _has_s5_credentials(post_text)

    rejection_reasons: list[str] = []
    if pre_wc >= _SRFS_DENSITY_GATE_MIN and post_wc < _SRFS_DENSITY_GATE_MIN:
        rejection_reasons.append("post_repair_word_count_below_density_gate_min")
    if post_wc < pre_wc:
        rejection_reasons.append("word_count_regression")
    if pre_sc in (4, 5) and post_sc not in (4, 5):
        rejection_reasons.append("sentence_count_arc_regression")
    if post_sc < pre_sc:
        rejection_reasons.append("sentence_count_decreased")
    if post_dup > pre_dup:
        rejection_reasons.append("duplicate_sentence_or_claim_introduced")
    if s5_required and pre_s5 and not post_s5:
        rejection_reasons.append("s5_credentials_dropped")
    if post_cov[0] < pre_cov[0]:
        rejection_reasons.append("brushstroke_coverage_regression")
    new_failures = sorted(set(post_failed) - set(pre_failed))
    if new_failures:
        rejection_reasons.append(f"new_x2_failures:{','.join(new_failures)}")

    unchanged = (
        pre_text.strip() == post_text.strip()
        and json.dumps(pre_parsed.get("claim_ledger"), sort_keys=True)
        == json.dumps(post_parsed.get("claim_ledger"), sort_keys=True)
    )
    accepted = not rejection_reasons

    return {
        "repair_candidate_accepted": accepted,
        "rejection_reason": "; ".join(rejection_reasons) if rejection_reasons else None,
        "monotonic_x2_check": {
            "pre_repair_failed_gates": pre_failed,
            "post_repair_failed_gates": post_failed,
            "new_failures": new_failures,
            "post_failed_subset_of_pre": set(post_failed) <= set(pre_failed),
        },
        "pre_repair_word_count": pre_wc,
        "post_repair_word_count": post_wc,
        "pre_repair_sentence_count": pre_sc,
        "post_repair_sentence_count": post_sc,
        "pre_repair_failed_gates": pre_failed,
        "post_repair_failed_gates": post_failed,
        "duplicate_detection_result": {"pre": pre_dup, "post": post_dup},
        "brushstroke_coverage_before": {"supported": pre_cov[0], "total": pre_cov[1]},
        "brushstroke_coverage_after": {"supported": post_cov[0], "total": post_cov[1]},
        "brushstroke_coverage_delta": post_cov[0] - pre_cov[0],
        "s5_required": s5_required,
        "pre_had_s5_credentials": pre_s5,
        "post_had_s5_credentials": post_s5,
        "chosen_text_source": "repair_candidate" if accepted else "pre_repair",
        "repair_unchanged": unchanged,
    }


def apply_srfs_judge_safe_repair(
    parsed: dict[str, Any],
    selected_facts: list[dict[str, Any]],
    srfs_integration: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Tighten resume_display_text and claim_ledger for X1D factual-support alignment.

    Returns (parsed, receipt_meta). Rejects repair candidates that regress monotonic X2 constraints.
    """
    if not isinstance(parsed, dict) or not srfs_x2_mode_active(srfs_integration):
        return parsed, None

    pre = copy.deepcopy(parsed)
    candidate = _apply_srfs_judge_safe_repair_core(parsed, selected_facts, srfs_integration)
    meta = evaluate_judge_safe_repair_monotonicity(pre, candidate, selected_facts, srfs_integration)
    meta["schema"] = "srfs_judge_safe_repair_v2"
    meta["repaired"] = bool(meta.get("repair_candidate_accepted")) and not meta.get("repair_unchanged")
    meta["before_resume_display_text"] = pre.get("resume_display_text")
    meta["after_resume_display_text"] = (
        candidate.get("resume_display_text")
        if meta.get("repair_candidate_accepted")
        else pre.get("resume_display_text")
    )
    if meta.get("repair_candidate_accepted"):
        return candidate, meta
    return pre, meta


def _apply_srfs_judge_safe_repair_core(
    parsed: dict[str, Any],
    selected_facts: list[dict[str, Any]],
    srfs_integration: dict[str, Any] | None,
) -> dict[str, Any]:
    """Apply judge-safe sentence rewrites (candidate; caller runs monotonic acceptance)."""
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

    blob = _facts_support_blob(selected_facts)
    s1_idx = 0
    s2_idx = 1
    s3_idx = 2
    if len(sentences) >= 5:
        s4_idx, s5_idx = 3, 4
    elif len(sentences) == 4:
        s4_idx, s5_idx = 3, -1
    else:
        s4_idx, s5_idx = 2, -1

    if agentic_ai_supported_in_facts(selected_facts):
        s1 = sentences[s1_idx]
        if "agentic" not in s1.lower() or "platform record above" in s1.lower():
            new_s1 = build_fact_tight_s1_sentence(selected_facts)
            _replace_sentence(sentences, s1_idx, new_s1)
            if len(ledger) > s1_idx:
                _sync_claim_row_for_sentence(
                    ledger,
                    s1_idx,
                    new_s1,
                    source_fact_ids=_source_fact_ids_for_s1(selected_facts, slice_ids),
                )

    by_id = _facts_index(selected_facts)
    s2 = _strip_unsupported_density_micro_tails(sentences[s2_idx])
    if s2 != sentences[s2_idx]:
        _replace_sentence(sentences, s2_idx, s2)
        if len(ledger) > s2_idx and isinstance(ledger[s2_idx], dict):
            _sync_claim_row_for_sentence(
                ledger,
                s2_idx,
                s2,
                source_fact_ids=ledger[s2_idx].get("source_fact_ids"),
            )
    if (
        _JUDGE_RISK_S2_RE.search(s2)
        or _sentence_has_unsupported_mechanism_stack(s2, blob)
        or _sentence_has_unsupported_business_metric(s2, blob)
        or _sentence_s2_dual_thread_overload(s2)
        or _sentence_s1_s2_capability_redundant(sentences[s1_idx], s2)
        or _sentence_s2_drops_governance_metric(s2, by_id)
        or _sentence_s2_governance_wrong_tense(s2, by_id)
    ):
        new_s2 = build_fact_tight_s2_sentence(selected_facts)
        _replace_sentence(sentences, s2_idx, new_s2)
        _sync_claim_row_for_sentence(
            ledger,
            s2_idx,
            new_s2,
            source_fact_ids=_source_fact_ids_for_s2(selected_facts, slice_ids),
        )

    has_004_slice = _srfs_slice_has_platform_004(slice_ids)

    if len(sentences) >= 3:
        s3 = sentences[s3_idx]
        needs_s3 = (
            _sentence_has_unsupported_commercialization(s3, blob)
            or _sentence_s3_needs_lifecycle_rewrite(s3)
            or _sentence_s3_bas_lifecycle_stitch(s3)
            or _sentence_s3_mechanism_lifecycle_stitch(s3)
            or _sentence_s3_carries_cycle_metric(s3)
            or _sentence_s3_has_unsupported_embellishment(s3, blob)
            or _sentence_s3_org_scale_violation(s3)
            or _sentence_s1_s3_thesis_echo(sentences[s1_idx], s3)
            or (
                has_004_slice
                and not _sentence_supports_004_lifecycle_arc(s3, blob)
            )
        )
        if needs_s3:
            new_s3 = build_fact_tight_s3_sentence(selected_facts)
            _replace_sentence(sentences, s3_idx, new_s3)
            _sync_claim_row_for_sentence(
                ledger,
                s3_idx,
                new_s3,
                source_fact_ids=_source_fact_ids_for_s3(selected_facts, slice_ids, new_s3),
            )

    if len(sentences) >= 3 and len(sentences) >= 4:
        s3_now = sentences[s3_idx]
        s4_now = sentences[s4_idx]
        if _sentence_s3_s4_duplicate_lifecycle_opener(s3_now, s4_now):
            by_id_dup = _facts_index(selected_facts)
            head = _platform_004_lifecycle_clause_for_s3(by_id_dup)
            if head:
                new_s3 = _capitalize_sentence_start(head.rstrip(".") + ".")
            else:
                new_s3 = build_fact_tight_s3_sentence(selected_facts)
            _replace_sentence(sentences, s3_idx, new_s3)
            _sync_claim_row_for_sentence(
                ledger,
                s3_idx,
                new_s3,
                source_fact_ids=_source_fact_ids_for_s3(selected_facts, slice_ids, new_s3),
            )

    if len(sentences) >= 4:
        s4 = sentences[s4_idx]
        new_s4 = build_fact_tight_s4_sentence(selected_facts)
        # When platform_004 is in SRFS, S4 must be the cycle-metric row only — never preserve
        # a mixed Qwen S4 that also carries unsupported $22M / gross-margin commercial lines.
        replace_s4 = has_004_slice or (
            s4.strip() != new_s4.strip()
            or _sentence_s4_needs_fact_tight_rewrite(s4, selected_facts, blob)
        )
        if replace_s4:
            _replace_sentence(sentences, s4_idx, new_s4)
            _sync_claim_row_for_sentence(
                ledger,
                s4_idx,
                new_s4,
                source_fact_ids=_source_fact_ids_for_s4(selected_facts, slice_ids),
            )

    if len(sentences) == 5 and "fact_certs_001" in slice_ids:
        new_s5 = build_fact_tight_s5_sentence(selected_facts)
        _replace_sentence(sentences, s5_idx, new_s5)
        if len(ledger) > s5_idx:
            _sync_claim_row_for_sentence(
                ledger,
                s5_idx,
                new_s5,
                source_fact_ids=_source_fact_ids_for_s5(selected_facts, slice_ids, new_s5),
            )

    if len(sentences) == 5 and len(ledger) >= 5:
        for idx, id_fn in (
            (0, lambda sf, si: _source_fact_ids_for_s1(sf, si)),
            (1, lambda sf, si: _source_fact_ids_for_s2(sf, si)),
            (2, lambda sf, si: _source_fact_ids_for_s3(sf, si, sentences[2])),
            (3, lambda sf, si: _source_fact_ids_for_s4(sf, si)),
            (4, lambda sf, si: _source_fact_ids_for_s5(sf, si, sentences[4])),
        ):
            _sync_claim_row_for_sentence(
                ledger,
                idx,
                sentences[idx],
                source_fact_ids=id_fn(selected_facts, slice_ids),
            )

    cleaned = []
    for i, s in enumerate(sentences):
        role = (1, 2, 3, 4, 5)[min(i, 4)] if len(sentences) == 5 else (1, 2, 3, 4)[min(i, 3)]
        cleaned.append(
            dedupe_trailing_clause_repeats(polish_srfs_sentence_fragments(s, role))
        )
    out["resume_display_text"] = strip_judge_banned_prose(" ".join(cleaned))
    out["claim_ledger"] = ledger
    return out
