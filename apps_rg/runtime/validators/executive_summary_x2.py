"""Deterministic X2 gates for executive summary runtime slice."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from dataclasses import dataclass, asdict
from typing import Any


FIRST_PERSON_PATTERN = re.compile(r"\b(I|me|my|mine|we|our|ours)\b", re.IGNORECASE)
EM_DASH = "—"
INLINE_SOURCE_PATTERN = re.compile(r"\[(source|fact|citation)\s*:[^\]]+\]", re.IGNORECASE)
GENERIC_FILLER = [
    "proven track record",
    "seasoned executive",
    "dynamic leader",
    "visionary leader",
    "results-driven",
    "cutting-edge technologies",
    "market position",
    "strategic leader",
    "passionate",
    "transformative",
]

EXEC_SUMMARY_FORBIDDEN_META_PHRASES = [
    "across the scope described in selected facts",
    "with active-voice delivery and governance discipline",
    "active-voice delivery",
    "governance discipline",
    "same fact plan",
    "canonical facts used as proof",
]

EXEC_SUMMARY_FORBIDDEN_META_PHRASES_LOOSE = [
    "selected facts",
]


def check_exec_summary_meta_filler_patterns(resume_display_text: str) -> tuple[bool, str | None]:
    lowered = resume_display_text.lower()
    hits: list[str] = []
    for phrase in EXEC_SUMMARY_FORBIDDEN_META_PHRASES:
        if phrase in lowered:
            hits.append(phrase)
    for phrase in EXEC_SUMMARY_FORBIDDEN_META_PHRASES_LOOSE:
        if phrase in lowered:
            hits.append(phrase)
    if hits:
        return False, f"Executive summary meta or filler scaffolding: {hits}"
    return True, None


def check_resume_display_colon_space_discipline(resume_display_text: str) -> tuple[bool, str | None]:
    """Block colon-space clause stitching (claim-title : prose) in user-visible summary."""
    if ": " in resume_display_text:
        return False, "Colon-space clause stitching is forbidden in resume_display_text."
    return True, None


def check_qwen_transport_envelope_stub_false(
    artifacts_dir: Path | None,
    provider_requested: str | None,
) -> tuple[bool, str | None]:
    """Reject synthetic harness responses that set stub:true on the vLLM JSON envelope."""
    if str(provider_requested or "").strip().lower() != "qwen_vllm":
        return True, None
    if artifacts_dir is None:
        return True, None
    path = artifacts_dir / "provider_response.json"
    if not path.is_file():
        return True, None
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"provider_response.json unreadable for stub check: {exc}"
    nested: dict[str, Any] | None = None
    if isinstance(envelope, dict):
        pr = envelope.get("provider_response")
        nested = pr if isinstance(pr, dict) else None
        if nested is None and envelope.get("stub") is True:
            nested = envelope
    if nested is None:
        return True, None
    if nested.get("stub") is True:
        return (
            False,
            "provider_response.stub is true — synthetic/test harness; not REAL_LLM transport proof.",
        )
    return True, None


# Action verbs that indicate bullet-pattern sentence stacking
ACTION_VERB_OPENERS = (
    "designed", "strengthened", "generated", "reduced", "architected",
    "built", "implemented", "delivered", "created", "led", "scaled",
    "productized", "standardized", "operationalized", "spearheaded",
    "drove", "driven", "managed", "oversaw", "directed",
)

# Phrases that must have direct source support
SOURCE_SENSITIVE_PHRASES = [
    "regulated enterprise workflows",
    "regulated environments",
    "compliance",
    "audit",
    "governance framework",
]

# Bridge claim phrases that are forbidden without direct support
INFERRED_BRIDGE_PHRASES = [
    "regulated enterprise workflows",
    "compliance",
    "market position",
    "enterprise-wide transformation",
    "strategic leader",
    "proven track record",
    "industry-leading",
    "mission-critical",
    "scalable and resilient infrastructure",
]

# Industry/domain claims that need direct support
INDUSTRY_DOMAIN_CLAIMS = [
    "regulated industries",
    "financial services",
    "healthcare",
    "insurance",
    "banking",
    "public sector",
    "compliance domain",
]

# Allowed top-level fields in model output
ALLOWED_TOP_LEVEL_FIELDS = {
    "resume_display_text",
    "selected_fact_plan",
    "claim_ledger",
    "jd_alignment",
    "gap_notes",
    "change_log",
    "self_check",
    "text_claim_coverage",
    "source_sensitive_phrase_ledger",
    "input_payload_hash",
    "output_payload_hash",
    "claim_ledger_hash",
    "allowed_fact_ids_hash",
}

# Required runtime artifacts
REQUIRED_ARTIFACTS = [
    "provider_request.json",
    "real_l2_generation_result.json",
    "runtime_payload.json",
    "prompt_selection_trace.json",
    "claim_ledger.json",
    "canonical_claim_ledger_v2.json",
    "text_claim_coverage.json",
    "fact_check_result.json",
    "x2_gate_outputs.json",
    "x3_disposition.json",
    "section_metric_receipt.json",
]

# Allowed model names
ALLOWED_MODELS = ["Qwen/Qwen2.5-32B-Instruct-AWQ"]

# Required X1D judge providers
REQUIRED_JUDGE_PROVIDERS = ["gemini_pro", "openai_chatgpt", "anthropic_claude"]


@dataclass
class X2GateResult:
    gate_id: str
    gate_type: str
    pass_: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None
    evidence_ref: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def has_jd_phrase_copy(text: str, jd_text: str, max_words: int = 4) -> tuple[bool, str | None]:
    """Detect copied JD phrases longer than max_words."""
    if not text or not jd_text:
        return False, None
    words = re.findall(r"[A-Za-z0-9#+/.]+", jd_text.lower())
    text_lower = " ".join(re.findall(r"[A-Za-z0-9#+/.]+", text.lower()))
    if len(words) <= max_words:
        return False, None
    for i in range(0, len(words) - max_words):
        phrase = " ".join(words[i : i + max_words + 1])
        if phrase and phrase in text_lower:
            return True, phrase
    return False, None


def detect_bullet_like_stacking(text: str) -> tuple[bool, str | None, int]:
    """Heuristic for one-fact-per-sentence action-verb stacking.
    
    Returns: (is_stacking, reason, consecutive_action_count)
    """
    sentences = split_sentences(text)
    if len(sentences) < 3:
        return False, None, 0
    
    action_openers = 0
    consecutive_actions = 0
    max_consecutive = 0
    
    for sentence in sentences:
        first = sentence.split()[0].lower().strip(",.;:") if sentence.split() else ""
        if first in ACTION_VERB_OPENERS:
            action_openers += 1
            consecutive_actions += 1
            max_consecutive = max(max_consecutive, consecutive_actions)
        else:
            consecutive_actions = 0
    
    # Fail if 4+ consecutive action verbs or 4+ total action openers
    if max_consecutive >= 4:
        return True, f"{max_consecutive} consecutive sentences start with action verbs (bullet pattern)", max_consecutive
    if action_openers >= 4:
        return True, f"{action_openers} sentences start with action verbs (mechanical list)", action_openers
    
    return False, None, action_openers


MECHANICAL_PROOF_OPENERS = frozenset({"productized", "designed", "strengthened", "standardized"})


def check_synthesis_quality(text: str) -> tuple[bool, str | None]:
    """Check if output reads like executive synthesis vs bullet conversion.
    
    Returns: (pass, reason)
    """
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return False, "Output too short for executive summary"

    if re.search(r"\bthis was achieved while\b", text, re.IGNORECASE):
        return False, "Bridge phrase 'This was achieved while' indicates bullet-like stacking"

    mechanical_hits = 0
    for sentence in sentences:
        first = sentence.split()[0].lower().strip(",.;:") if sentence.split() else ""
        if first in MECHANICAL_PROOF_OPENERS:
            mechanical_hits += 1
    if mechanical_hits >= 3:
        return False, (
            "Mechanical proof sequence detected "
            "(Productized/Designed/Strengthened/Standardized opener pattern)"
        )

    # Check for mechanical one-fact-per-sentence pattern
    is_stacking, reason, _ = detect_bullet_like_stacking(text)
    if is_stacking:
        return False, f"Sentence stacking detected: {reason}"

    if len(sentences) >= 4:
        short_action_sentences = 0
        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue
            first = words[0].lower().strip(",.;:")
            if first in ACTION_VERB_OPENERS and len(words) <= 22:
                short_action_sentences += 1
        if short_action_sentences >= 4:
            return False, "One short proof-style sentence per fact (bullet conversion pattern)"

    # Check average sentence length (executive summaries have varied length)
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
    if avg_len < 12:
        return False, f"Average sentence length {avg_len:.1f} words suggests choppy bullet conversion"
    
    return True, None


def check_claim_ledger_orphan_source_ids(
    claim_ledger: list[dict[str, Any]], allowed_fact_ids: set[str]
) -> tuple[bool, str | None]:
    """Every ledger row must cite only allowed_fact_ids (including metric-suffixed ids)."""
    for i, row in enumerate(claim_ledger):
        if not isinstance(row, dict):
            continue
        ids = row.get("source_fact_ids") or []
        if not ids:
            return False, f"claim_ledger[{i}] missing source_fact_ids"
        for sid in ids:
            if sid not in allowed_fact_ids:
                return False, f"claim_ledger[{i}] orphan source_fact_id {sid!r} (not in allowed set)"
    return True, None


def check_claim_coverage_accounting(
    resume_display_text: str,
    parsed_output: dict[str, Any] | None,
    text_claim_coverage: dict[str, Any],
    claim_ledger: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """Verify coverage accounting consistency.
    
    Returns: (pass, reason)
    """
    # Count sentences in displayed text
    displayed_sentences = split_sentences(resume_display_text)
    displayed_count = len(displayed_sentences)
    
    # Count sentences in coverage
    coverage_sentences = text_claim_coverage.get("sentences", [])
    coverage_count = len(coverage_sentences)
    
    if displayed_count != coverage_count:
        return False, f"Sentence count mismatch: displayed={displayed_count}, coverage={coverage_count}"
    
    # Build set of all source_fact_ids in claim_ledger
    ledger_fact_ids = set()
    for claim in claim_ledger:
        source_ids = claim.get("source_fact_ids", [])
        ledger_fact_ids.update(source_ids)
    
    # Every sentence must have at least one material claim
    # Every material claim must map to source_fact_ids that exist in ledger
    for row in coverage_sentences:
        material_claims = row.get("material_claims", [])
        if not material_claims:
            return False, f"Sentence {row.get('sentence_index')} has no material claims"
        
        for claim in material_claims:
            source_ids = claim.get("source_fact_ids", [])
            if not source_ids:
                return False, f"Material claim has no source_fact_ids"
            # Check that at least one source fact ID is in the ledger
            if not any(sid in ledger_fact_ids or "_metric_" in sid for sid in source_ids):
                return False, f"Material claim has source_fact_ids not found in claim_ledger"
    
    return True, None


def _ledger_claim_tokens(claim_text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9$%]+", claim_text.lower()) if len(t) > 3]


def ledger_row_materialized_in_display(claim: dict[str, Any], resume_display_text: str) -> bool:
    """Rough token-overlap check: claim corroborated by resume body (mirrors sentence coverage heuristics)."""
    ct = str(claim.get("claim_text") or "").strip()
    if not ct:
        return False
    resume_l = resume_display_text.lower()
    tokens = _ledger_claim_tokens(ct)
    if not tokens:
        return True
    hits = sum(1 for t in tokens if t in resume_l)
    need = max(1, min(3, len(tokens)))
    return hits >= need


def gap_notes_excuse_ledger_claim(claim: dict[str, Any], gap_notes: list[Any]) -> bool:
    """Explicit escape: gap_notes must name a source_fact_id and/or a long token from the claim."""
    if not isinstance(gap_notes, list) or not gap_notes:
        return False
    blob = " ".join(str(g) for g in gap_notes).lower()
    for sid in claim.get("source_fact_ids") or []:
        base = str(sid).split("_metric_")[0].lower()
        if len(base) > 3 and base in blob:
            return True
    for t in _ledger_claim_tokens(str(claim.get("claim_text") or "").strip())[:8]:
        if len(t) >= 8 and t in blob:
            return True
    return False


def check_claim_ledger_claim_text_non_empty(claim_ledger: list[dict[str, Any]]) -> tuple[bool, str | None]:
    """Each ledger row must carry non-empty material claim prose (post normalize: claim_text only).

    Rows with only source_fact_ids and no claim/claim_text fail here before coverage gates.
    """
    bad_parts: list[str] = []
    for i, row in enumerate(claim_ledger):
        if not isinstance(row, dict):
            bad_parts.append(f"idx={i} source_fact_ids=[] reason=not_a_dict")
            continue
        ct = str(row.get("claim_text") or "").strip()
        if not ct:
            ids = list(row.get("source_fact_ids") or [])
            bad_parts.append(f"idx={i} source_fact_ids={ids!r}")
    if bad_parts:
        return False, "claim_ledger rows missing non-empty claim_text: " + "; ".join(bad_parts)
    return True, None


def check_claim_ledger_materialized_or_gap_excused(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    gap_notes: list[Any],
) -> tuple[bool, str | None]:
    """Each claim_ledger row must appear in resume text OR be explicitly excused in gap_notes."""
    bad: list[str] = []
    for i, claim in enumerate(claim_ledger):
        if not isinstance(claim, dict):
            continue
        if ledger_row_materialized_in_display(claim, resume_display_text):
            continue
        if gap_notes_excuse_ledger_claim(claim, gap_notes):
            continue
        bad.append(f"idx={i}")
    if bad:
        return False, "claim_ledger rows not materialized in resume_display_text without gap_notes excuse: " + ", ".join(
            bad
        )
    return True, None


def check_source_sensitive_phrases(
    text: str,
    selected_facts: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """Check if sensitive phrases have direct source support.
    
    Returns: (pass, reason)
    """
    text_lower = text.lower()
    
    # Build set of supported phrases from selected facts
    supported_phrases = set()
    for fact in selected_facts:
        claim_text = fact.get("claim_text", "").lower()
        achievement = fact.get("achievement_summary", "").lower()
        combined = claim_text + " " + achievement
        
        # Check if any sensitive phrase appears in source facts
        for phrase in SOURCE_SENSITIVE_PHRASES:
            if phrase in combined:
                supported_phrases.add(phrase)
    
    # Check if any sensitive phrase in output is NOT supported
    unsupported_in_output = []
    for phrase in SOURCE_SENSITIVE_PHRASES:
        if phrase in text_lower and phrase not in supported_phrases:
            unsupported_in_output.append(phrase)
    
    if unsupported_in_output:
        return False, f"Unsupported sensitive phrases: {unsupported_in_output}"
    
    return True, None


def check_required_fields(parsed_output: dict[str, Any] | None) -> tuple[bool, str | None]:
    """Check if required L2 fields exist and are non-empty."""
    if parsed_output is None:
        return False, "parsed_output is None"
    
    required_fields = [
        "resume_display_text",
        "selected_fact_plan",
        "claim_ledger",
        "jd_alignment",
        "gap_notes",
        "change_log",
        "self_check",
        "text_claim_coverage",
    ]
    
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in parsed_output:
            missing_fields.append(field)
        elif parsed_output[field] is None or parsed_output[field] == "":
            empty_fields.append(field)
        elif field == "claim_ledger" and not parsed_output[field]:
            empty_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    if empty_fields:
        return False, f"Empty required fields: {', '.join(empty_fields)}"
    
    return True, None


def check_required_artifacts(artifacts_dir: Path) -> tuple[bool, str | None]:
    """Check if required runtime artifacts exist."""
    missing = []
    for artifact in REQUIRED_ARTIFACTS:
        artifact_path = artifacts_dir / artifact
        if not artifact_path.exists():
            missing.append(artifact)
    
    if missing:
        return False, f"Missing required artifacts: {', '.join(missing)}"
    return True, None


def check_json_parse_valid(parsed_output: dict[str, Any] | None, raw_output: str | None) -> tuple[bool, str | None]:
    """Check if provider output was parsed from JSON without repair ambiguity."""
    if parsed_output is None:
        return False, "parsed_output is None - parsing failed"
    
    if raw_output is None or raw_output == "":
        return False, "raw_output is missing"

    if "```" in raw_output:
        return False, "Raw output contains markdown code fences"

    stripped = raw_output.strip()
    if not stripped.startswith("{"):
        return False, "Raw output must start with '{' (strict JSON only)"
    if not stripped.endswith("}"):
        return False, "Raw output must end with '}' (strict JSON only)"
    
    # Try to parse raw output to verify it's valid JSON
    try:
        json.loads(stripped)
    except json.JSONDecodeError as e:
        return False, f"Raw output is not valid JSON: {e}"
    
    return True, None


def check_no_extra_fields(parsed_output: dict[str, Any] | None) -> tuple[bool, str | None]:
    """Check if model emits extra top-level fields outside the allowed schema."""
    if parsed_output is None:
        return False, "parsed_output is None"
    
    extra_fields = []
    for field in parsed_output.keys():
        if field not in ALLOWED_TOP_LEVEL_FIELDS:
            extra_fields.append(field)
    
    if extra_fields:
        return False, f"Extra unrecognized fields: {', '.join(extra_fields)}"
    return True, None


def check_material_clause_coverage(
    resume_display_text: str,
    text_claim_coverage: dict[str, Any],
    selected_facts: list[dict[str, Any]] | None,
) -> tuple[bool, str | None]:
    """Check if every material clause has support."""
    # Material clause types we care about
    material_keywords = [
        "platform", "architecture", "governance", "control",
        "retrieval", "context", "evaluation", "commercial impact",
        "team", "cycle-time", "delivery", "leadership", "senior",
        "industry", "domain", "$", "%", "revenue", "margin",
        "uptime", "cost", "month", "week", "year",
    ]
    
    sentences = split_sentences(resume_display_text)
    coverage_sentences = text_claim_coverage.get("sentences", [])
    
    unsupported_clauses = []
    
    for idx, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        # Check if sentence contains material keywords
        is_material = any(kw in sentence_lower for kw in material_keywords)
        
        if is_material:
            # Find matching coverage row
            if idx < len(coverage_sentences):
                coverage_row = coverage_sentences[idx]
                material_claims = coverage_row.get("material_claims", [])
                has_supported_claim = any(
                    claim.get("support_status") == "SUPPORTED"
                    for claim in material_claims
                )
                if not has_supported_claim:
                    unsupported_clauses.append(sentence[:50])
    
    if unsupported_clauses:
        return False, f"Material clauses without support: {len(unsupported_clauses)}"
    return True, None


def check_metric_fact_id_granularity(text_claim_coverage: dict[str, Any]) -> tuple[bool, str | None]:
    """Ensure every metric maps to a granular metric fact ID."""
    coverage_sentences = text_claim_coverage.get("sentences", [])
    
    for row in coverage_sentences:
        material_claims = row.get("material_claims", [])
        for claim in material_claims:
            claim_text = claim.get("claim_text", "").lower()
            # Check for metrics
            has_metric = bool(
                re.search(r"\$\d+", claim_text) or  # Dollar amounts
                re.search(r"\d+%", claim_text) or  # Percentages
                re.search(r"\d+\s*(month|week|day|year|hour)", claim_text) or  # Time
                re.search(r"\d+\s*(team|staff|employee|person)", claim_text)  # Team size
            )
            if has_metric:
                source_ids = claim.get("source_fact_ids", [])
                # Check if any source ID is granular (contains metric indicator)
                has_granular = any(
                    "_metric_" in sid or "metric" in sid.lower() or 
                    any(ch.isdigit() for ch in sid)
                    for sid in source_ids
                )
                if not has_granular:
                    return False, f"Metric without granular source fact ID: {claim_text[:50]}"
    
    return True, None


def check_inferred_bridge_claims(resume_display_text: str, selected_facts: list[dict[str, Any]] | None) -> tuple[bool, str | None]:
    """Check for unsupported bridge language in text."""
    text_lower = resume_display_text.lower()
    
    # Build set of supported phrases from selected facts
    supported_phrases = set()
    if selected_facts:
        for fact in selected_facts:
            claim_text = fact.get("claim_text", "").lower()
            achievement = fact.get("achievement_summary", "").lower()
            combined = claim_text + " " + achievement
            for phrase in INFERRED_BRIDGE_PHRASES:
                if phrase in combined:
                    supported_phrases.add(phrase)
    
    unsupported_phrases = []
    for phrase in INFERRED_BRIDGE_PHRASES:
        if phrase in text_lower and phrase not in supported_phrases:
            unsupported_phrases.append(phrase)
    
    if unsupported_phrases:
        return False, f"Unsupported bridge phrases: {', '.join(unsupported_phrases)}"
    return True, None


def check_jd_as_proof_zero(claim_ledger: list[dict[str, Any]], jd_text: str) -> tuple[bool, str | None]:
    """Block JD-derived experience claims."""
    for claim in claim_ledger:
        source_ids = claim.get("source_fact_ids", [])
        for sid in source_ids:
            if "jd" in sid.lower() or "target_role" in sid.lower() or "jd_only" in sid.lower():
                return False, f"JD-derived claim found: {sid}"
    return True, None


def check_briefing_as_proof_zero(claim_ledger: list[dict[str, Any]]) -> tuple[bool, str | None]:
    """Block briefing-derived candidate claims."""
    for claim in claim_ledger:
        source_ids = claim.get("source_fact_ids", [])
        for sid in source_ids:
            if "briefing" in sid.lower() or "company_brief" in sid.lower():
                return False, f"Briefing-derived claim found: {sid}"
    return True, None


def check_target_title_inflation(resume_display_text: str, target_company: str, target_role: str | None = None) -> tuple[bool, str | None]:
    """Block inflated target-title framing."""
    text_lower = resume_display_text.lower()
    
    # Check if target company name appears with "at" or similar implying employment
    if target_company:
        company_lower = target_company.lower().strip()
        if company_lower:
            # Check for patterns like "SVP at {company}" or "CTO at {company}"
            patterns = [
                rf"\b(svp|cto|cfo|ceo|vp|director|head)\s+at\s+{re.escape(company_lower)}",
                rf"\bat\s+{re.escape(company_lower)}\b.*\b(svp|cto|cfo|ceo|vp|director|head)\b",
            ]
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return False, f"Target title inflation detected: claims role at {target_company}"
    
    return True, None


def check_unsupported_industry_claims(resume_display_text: str, selected_facts: list[dict[str, Any]] | None) -> tuple[bool, str | None]:
    """Block unsupported industry/domain claims."""
    text_lower = resume_display_text.lower()
    
    # Build set of supported industry phrases from selected facts
    supported_industries = set()
    if selected_facts:
        for fact in selected_facts:
            claim_text = fact.get("claim_text", "").lower()
            achievement = fact.get("achievement_summary", "").lower()
            combined = claim_text + " " + achievement
            for industry in INDUSTRY_DOMAIN_CLAIMS:
                if industry in combined:
                    supported_industries.add(industry)
    
    unsupported_industries = []
    for industry in INDUSTRY_DOMAIN_CLAIMS:
        if industry in text_lower and industry not in supported_industries:
            unsupported_industries.append(industry)
    
    if unsupported_industries:
        return False, f"Unsupported industry claims: {', '.join(unsupported_industries)}"
    return True, None


def check_judge_rows_present(x1d_judges: list[dict[str, Any]] | None) -> tuple[bool, str | None]:
    """Check if all required judge provider rows are present."""
    if x1d_judges is None:
        return False, "x1d_judges is None"
    
    present_providers = {j.get("provider_key") for j in x1d_judges}
    missing = [p for p in REQUIRED_JUDGE_PROVIDERS if p not in present_providers]
    
    if missing:
        return False, f"Missing required judge providers: {', '.join(missing)}"
    return True, None


def check_judge_raw_responses_written(artifacts_dir: Path, x1d_judges: list[dict[str, Any]] | None) -> tuple[bool, str | None]:
    """Check if raw response artifacts exist for attempted judges."""
    if x1d_judges is None:
        return False, "x1d_judges is None"
    
    missing = []
    for judge in x1d_judges:
        provider_key = judge.get("provider_key")
        raw_response_ref = judge.get("raw_response_ref")
        
        if not raw_response_ref and judge.get("evaluator_mode") in ("MODEL_BACKED", "BLOCKED_RESPONSE_PARSE_ERROR"):
            # Should have raw response for model-backed or parse error
            missing.append(f"{provider_key} (no raw_response_ref)")
    
    if missing:
        return False, f"Missing raw responses: {', '.join(missing)}"
    return True, None


def check_judge_schema_valid(judge: dict[str, Any]) -> tuple[bool, str | None]:
    """Check if a judge row has valid schema."""
    required_fields = [
        "judge_id", "provider_name", "provider_key", "evaluator_mode",
        "provider_status", "model_name", "pass", "decisive_failure",
    ]
    
    missing = [f for f in required_fields if f not in judge]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    
    return True, None


def build_sentence_claim_coverage(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> dict[str, Any]:
    """Map every displayed sentence to material claim support.

    This is intentionally strict for the overlay. It relies on the model's claim ledger
    and does not invent support after the fact.
    """
    sentences = split_sentences(resume_display_text)
    coverage_rows = []
    overall_pass = True

    for idx, sentence in enumerate(sentences, 1):
        matching_claims = []
        sentence_lower = sentence.lower()
        for claim in claim_ledger:
            claim_text = str(claim.get("claim_text") or "").strip()
            if not claim_text:
                continue
            claim_tokens = [t for t in re.findall(r"[A-Za-z0-9$%]+", claim_text.lower()) if len(t) > 3]
            token_hits = sum(1 for token in claim_tokens if token in sentence_lower)
            if token_hits >= max(1, min(3, len(claim_tokens))):
                matching_claims.append(claim)

        material_claims = []
        if not matching_claims:
            material_claims.append({
                "claim_text": sentence,
                "source_fact_ids": [],
                "support_status": "UNSUPPORTED",
                "reason": "No claim_ledger row maps to this displayed sentence.",
            })
            sentence_pass = False
            overall_pass = False
        else:
            sentence_pass = True
            for claim in matching_claims:
                source_ids = list(claim.get("source_fact_ids") or [])
                valid_source_ids = [sid for sid in source_ids if sid in allowed_fact_ids or "_metric_" in sid]
                status = "SUPPORTED" if valid_source_ids else "UNSUPPORTED"
                if status != "SUPPORTED":
                    sentence_pass = False
                    overall_pass = False
                material_claims.append({
                    "claim_text": claim_text,
                    "source_fact_ids": source_ids,
                    "support_status": status,
                    "reason": "Mapped from claim_ledger.",
                })
        coverage_rows.append({
            "sentence_index": idx,
            "sentence_text": sentence,
            "material_claims": material_claims,
            "sentence_pass": sentence_pass,
        })

    return {"sentences": coverage_rows, "overall_pass": overall_pass}


def run_x2_gates(
    *,
    resume_display_text: str,
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    text_claim_coverage: dict[str, Any],
    allowed_fact_ids: set[str],
    target_company: str,
    jd_text: str,
    temperature: float,
    runtime_generation_status: str,
    monolithic_prompt_invoked: bool,
    strategic_tailor_v1_invoked: bool,
    artifacts_dir: Path | None = None,
    provider_requested: str | None = None,
    provider_attempted: str | None = None,
    model_name: str | None = None,
    prompt_hash: str | None = None,
    compiled_prompt: str | None = None,
    raw_output: str | None = None,
    x1d_judges: list[dict[str, Any]] | None = None,
    target_role: str | None = None,
    selected_facts: list[dict[str, Any]] | None = None,
) -> list[X2GateResult]:
    gates: list[X2GateResult] = []
    artifacts_dir = artifacts_dir or Path("artifacts/apps_rg/runtime_proofs/executive_summary")

    def add(gate_id: str, passed: bool, observed: Any, threshold: Any, reason: str | None = None) -> None:
        gates.append(X2GateResult(gate_id, "deterministic", passed, observed, threshold, None if passed else reason, gate_id))

    # Existing gates
    add("x2_schema_valid", parsed_output is not None, parsed_output is not None, True, "Model output did not parse to expected JSON object.")
    add("x2_claim_ledger_present", bool(claim_ledger), len(claim_ledger), ">0", "claim_ledger is empty or missing.")
    add("x2_sentence_coverage_present", bool(text_claim_coverage.get("sentences")), len(text_claim_coverage.get("sentences", [])), ">0", "text_claim_coverage missing.")
    add("x2_sentence_coverage_pass", text_claim_coverage.get("overall_pass") is True, text_claim_coverage.get("overall_pass"), True, "One or more displayed sentences lack supported claims.")

    source_coverage_ok = bool(claim_ledger) and all(
        any((sid in allowed_fact_ids) or ("_metric_" in sid) for sid in (claim.get("source_fact_ids") or []))
        for claim in claim_ledger
    )
    add("x2_source_fact_coverage_100", source_coverage_ok, "100%" if source_coverage_ok else "<100%", "100%", "One or more claims lack allowed source_fact_ids.")

    orphan_ok, orphan_reason = check_claim_ledger_orphan_source_ids(claim_ledger, allowed_fact_ids)
    add("x2_claim_ledger_orphan_zero", orphan_ok, orphan_reason or "ok", "no_orphans", orphan_reason)

    ledger_text_ok, ledger_text_reason = check_claim_ledger_claim_text_non_empty(claim_ledger)
    add(
        "x2_claim_ledger_claim_text_non_empty",
        ledger_text_ok,
        ledger_text_reason or "all_rows_non_empty",
        "non_empty_claim_text_each_row",
        ledger_text_reason,
    )

    unsupported = []
    mixed = []
    overbroad = []
    for row in text_claim_coverage.get("sentences", []):
        for claim in row.get("material_claims", []):
            status = claim.get("support_status")
            if status == "UNSUPPORTED":
                unsupported.append(claim)
            if status == "MIXED":
                mixed.append(claim)
            if status == "OVERBROAD":
                overbroad.append(claim)
    add("x2_unsupported_claim_zero", not unsupported, len(unsupported), 0, "Unsupported claims present.")
    add("x2_mixed_claim_zero", not mixed, len(mixed), 0, "Mixed claims present.")
    add("x2_overbroad_claim_zero", not overbroad, len(overbroad), 0, "Overbroad claims present.")

    copied, phrase = has_jd_phrase_copy(resume_display_text, jd_text)
    add("x2_jd_phrase_copy_violation_zero", not copied, phrase, None, f"JD phrase copied: {phrase}")
    add("x2_em_dash_count_zero", EM_DASH not in resume_display_text, resume_display_text.count(EM_DASH), 0, "Em dash found.")
    add("x2_inline_source_tags_absent", not INLINE_SOURCE_PATTERN.search(resume_display_text), bool(INLINE_SOURCE_PATTERN.search(resume_display_text)), False, "Inline source/citation tag leaked into resume display text.")
    add("x2_no_word_count_target", True, "fit_to_evidence", "fit_to_evidence", None)
    add("x2_no_monolithic_prompt", not monolithic_prompt_invoked, monolithic_prompt_invoked, False, "Monolithic prompt invoked.")
    add("x2_no_strategic_tailor_v1", not strategic_tailor_v1_invoked, strategic_tailor_v1_invoked, False, "strategic_tailor_v1 invoked.")
    add("x2_temperature_in_profile", 0.35 <= temperature <= 0.55, temperature, "0.35-0.55", "Temperature outside executive_summary profile.")
    add("x2_first_person_zero", not FIRST_PERSON_PATTERN.search(resume_display_text), bool(FIRST_PERSON_PATTERN.search(resume_display_text)), False, "First-person pronoun found.")
    lowered_text = resume_display_text.lower()
    lowered_company = (target_company or "").lower().strip()
    target_company_as_experience = bool(
        lowered_company and any(f"{prefix} {lowered_company}" in lowered_text for prefix in ("at", "for", "with"))
    )
    add("x2_target_company_as_experience_zero", not target_company_as_experience, target_company_as_experience, False, "Target company used as candidate experience/employer.")
    filler_hits = [phrase for phrase in GENERIC_FILLER if phrase in resume_display_text.lower()]
    add("x2_generic_filler_zero", not filler_hits, filler_hits, [], "Generic filler found.")
    meta_filler_ok, meta_filler_reason = check_exec_summary_meta_filler_patterns(resume_display_text)
    add(
        "x2_exec_summary_meta_filler_zero",
        meta_filler_ok,
        meta_filler_reason or "ok",
        [],
        meta_filler_reason,
    )
    colon_stitch_ok, colon_stitch_reason = check_resume_display_colon_space_discipline(resume_display_text)
    add(
        "x2_exec_summary_colon_stitch_zero",
        colon_stitch_ok,
        colon_stitch_reason or "ok",
        [],
        colon_stitch_reason,
    )
    stacked, stack_reason, _ = detect_bullet_like_stacking(resume_display_text)
    add("x2_sentence_stacking_zero", not stacked, stack_reason, None, "Bullet-like sentence stacking detected.")
    
    # New synthesis quality gate
    synthesis_ok, synthesis_reason = check_synthesis_quality(resume_display_text)
    add("x2_executive_summary_synthesis_quality", synthesis_ok, synthesis_reason, None, synthesis_reason)
    
    # New coverage accounting gate
    accounting_ok, accounting_reason = check_claim_coverage_accounting(
        resume_display_text, parsed_output, text_claim_coverage, claim_ledger
    )
    add("x2_claim_coverage_accounting_consistent", accounting_ok, accounting_reason, None, accounting_reason)

    gap_notes_list = (parsed_output or {}).get("gap_notes") if isinstance((parsed_output or {}).get("gap_notes"), list) else []
    ledger_mat_ok, ledger_mat_reason = check_claim_ledger_materialized_or_gap_excused(
        resume_display_text, claim_ledger, gap_notes_list
    )
    add(
        "x2_claim_ledger_materialized_or_gap_excused",
        ledger_mat_ok,
        ledger_mat_reason or "ok",
        "materialized_or_gap",
        ledger_mat_reason,
    )

    # New source-sensitive phrase gate
    if selected_facts:
        source_ok, source_reason = check_source_sensitive_phrases(resume_display_text, selected_facts)
        add("x2_source_sensitive_phrases_supported", source_ok, source_reason, None, source_reason)
    else:
        add("x2_source_sensitive_phrases_supported", True, "skipped", "skipped", None)

    # New expanded X2 gates
    # Gate 1: x2_required_fields_complete
    required_fields_ok, required_fields_reason = check_required_fields(parsed_output)
    add("x2_required_fields_complete", required_fields_ok, required_fields_reason, None, required_fields_reason)

    # Gate 2: x2_required_artifacts_written
    artifacts_ok, artifacts_reason = check_required_artifacts(artifacts_dir)
    add("x2_required_artifacts_written", artifacts_ok, artifacts_reason, None, artifacts_reason)

    # Gate 3: x2_json_parse_valid
    json_parse_ok, json_parse_reason = check_json_parse_valid(parsed_output, raw_output)
    add("x2_json_parse_valid", json_parse_ok, json_parse_reason, None, json_parse_reason)

    # Gate 4: x2_no_extra_unrecognized_fields
    no_extra_ok, no_extra_reason = check_no_extra_fields(parsed_output)
    add("x2_no_extra_unrecognized_fields", no_extra_ok, no_extra_reason, None, no_extra_reason)

    # Gate 5: x2_material_clause_coverage_100
    material_clause_ok, material_clause_reason = check_material_clause_coverage(resume_display_text, text_claim_coverage, selected_facts)
    add("x2_material_clause_coverage_100", material_clause_ok, material_clause_reason, None, material_clause_reason)

    # Gate 6: x2_metric_fact_id_granularity
    metric_granular_ok, metric_granular_reason = check_metric_fact_id_granularity(text_claim_coverage)
    add("x2_metric_fact_id_granularity", metric_granular_ok, metric_granular_reason, None, metric_granular_reason)

    # Gate 7: x2_no_inferred_bridge_claims
    bridge_ok, bridge_reason = check_inferred_bridge_claims(resume_display_text, selected_facts)
    add("x2_no_inferred_bridge_claims", bridge_ok, bridge_reason, None, bridge_reason)

    # Gate 8: x2_jd_as_proof_zero
    jd_proof_ok, jd_proof_reason = check_jd_as_proof_zero(claim_ledger, jd_text)
    add("x2_jd_as_proof_zero", jd_proof_ok, jd_proof_reason, None, jd_proof_reason)

    # Gate 9: x2_briefing_as_proof_zero
    briefing_proof_ok, briefing_proof_reason = check_briefing_as_proof_zero(claim_ledger)
    add("x2_briefing_as_proof_zero", briefing_proof_ok, briefing_proof_reason, None, briefing_proof_reason)

    # Gate 10: x2_target_title_inflation_zero
    title_inflation_ok, title_inflation_reason = check_target_title_inflation(resume_display_text, target_company, target_role)
    add("x2_target_title_inflation_zero", title_inflation_ok, title_inflation_reason, None, title_inflation_reason)

    # Gate 11: x2_unsupported_industry_claim_zero
    industry_claim_ok, industry_claim_reason = check_unsupported_industry_claims(resume_display_text, selected_facts)
    add("x2_unsupported_industry_claim_zero", industry_claim_ok, industry_claim_reason, None, industry_claim_reason)

    # Gate 12: x2_provider_requested_attempted
    provider_attempted_ok = provider_requested == provider_attempted if provider_requested else True
    add("x2_provider_requested_attempted", provider_attempted_ok, f"requested={provider_requested}, attempted={provider_attempted}", "must match", "Provider requested does not match provider attempted.")

    # Gate 13: x2_no_silent_mock_fallback
    no_mock_fallback_ok = not (
        provider_requested == "qwen_vllm" and runtime_generation_status in ("MOCKED", "STUBBED")
    )
    add("x2_no_silent_mock_fallback", no_mock_fallback_ok, f"provider={provider_requested}, status={runtime_generation_status}", "no silent mock", "Silent mock or stub fallback detected.")

    stub_env_ok, stub_env_reason = check_qwen_transport_envelope_stub_false(artifacts_dir, provider_requested)
    add(
        "x2_qwen_provider_stub_transport_zero",
        stub_env_ok,
        stub_env_reason or "ok",
        "stub_transport_absent",
        stub_env_reason,
    )

    # Gate 14: x2_model_name_allowed — exercised only for qwen_vllm (REAL_LLM provider proof lane).
    qwen_proof_lane = str(provider_requested or "").strip().lower() == "qwen_vllm"
    model_allowed_ok = (
        not qwen_proof_lane
        or (
            runtime_generation_status == "REAL_LLM"
            and bool(model_name)
            and model_name in ALLOWED_MODELS
        )
    )
    model_observed = (
        "skipped_provider_not_qwen_vllm" if not qwen_proof_lane else (model_name or "unknown")
    )
    add(
        "x2_model_name_allowed",
        model_allowed_ok,
        model_observed,
        ALLOWED_MODELS,
        "Model name must match allowlist when qwen_vllm asserts REAL_LLM provider proof.",
    )

    # Gate 15: x2_prompt_hash_known
    prompt_hash_ok = bool(prompt_hash and prompt_hash != "")
    if prompt_hash_ok and compiled_prompt:
        expected_hash = hashlib.sha256(compiled_prompt.encode()).hexdigest()[:16]
        prompt_hash_ok = prompt_hash == expected_hash
    add("x2_prompt_hash_known", prompt_hash_ok, prompt_hash or "missing", "valid hash", "Prompt hash missing or invalid.")

    # Gate 16: x2_input_output_hashes_present
    input_output_hashes_ok = bool(
        parsed_output and
        parsed_output.get("input_payload_hash") and
        parsed_output.get("output_payload_hash")
    )
    add("x2_input_output_hashes_present", input_output_hashes_ok, input_output_hashes_ok, True, "Missing input/output hashes.")

    # Gate 17: x2_x1d_required_judges_present
    judges_present_ok, judges_present_reason = check_judge_rows_present(x1d_judges)
    add("x2_x1d_required_judges_present", judges_present_ok, judges_present_reason, None, judges_present_reason)

    # Gate 18: x2_x1d_raw_responses_written
    raw_responses_ok, raw_responses_reason = check_judge_raw_responses_written(artifacts_dir, x1d_judges)
    add("x2_x1d_raw_responses_written", raw_responses_ok, raw_responses_reason, None, raw_responses_reason)

    # Gate 19: x2_x1d_schema_valid (only for BLOCKED providers with valid schema - not a failure for blocked)
    if x1d_judges:
        # Check if all blocked providers have valid schema
        blocked_with_invalid_schema = []
        for judge in x1d_judges:
            evaluator_mode = judge.get("evaluator_mode", "")
            if evaluator_mode.startswith("BLOCKED_"):
                schema_ok, _ = check_judge_schema_valid(judge)
                if not schema_ok:
                    blocked_with_invalid_schema.append(judge.get("provider_key", "unknown"))
        x1d_schema_ok = len(blocked_with_invalid_schema) == 0
        add("x2_x1d_schema_valid", x1d_schema_ok, blocked_with_invalid_schema, [], f"Blocked providers with invalid schema: {blocked_with_invalid_schema}")
    else:
        add("x2_x1d_schema_valid", False, "no judges", "judges present", "No X1D judges to validate.")
    
    return gates


def gates_pass(gates: list[X2GateResult]) -> bool:
    return all(g.pass_ for g in gates)


def failed_gate_ids(gates: list[X2GateResult]) -> list[str]:
    return [g.gate_id for g in gates if not g.pass_]
