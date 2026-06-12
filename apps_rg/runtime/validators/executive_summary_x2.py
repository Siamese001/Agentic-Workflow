"""Deterministic X2 gates for executive summary runtime slice."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from dataclasses import dataclass, asdict
from typing import Any

from apps_rg.runtime.section_judge_policy import REQUIRED_JUDGE_PROVIDER_KEYS
from apps_rg.runtime.section_model_limits import SECTION_MODEL_ID
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

EXEC_SUMMARY_MIN_SENTENCES = 6
EXEC_SUMMARY_MAX_SENTENCES = 6
EXEC_SUMMARY_MAX_WORDS = 140
EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE = 45
EXPECTED_PROMPT_TEMPLATE_REF = "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
EXPECTED_PROMPT_ID = "executive_summary.generate_scratch_v1"
EXPECTED_PA_SHELL_TEMPLATE_ID = "strategic_tailor_v1"

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
    "this summary",
    "the candidate",
    "this individual",
    "this executive",
    "additionally, their",
    "furthermore, their",
    "additionally,",
    "furthermore,",
    "an experienced engineering executive with a strong background",
    "an experienced leader in regulated",
    "with extensive experience in",
    "with extensive experience",
]


# Finite-verb pattern: matches common present/past tense verbs and auxiliary constructions.
# A sentence is a fragment if it has NO finite verb — it's a noun phrase or participial phrase.
# We use a conservative heuristic: look for at least one token that is a finite verb form.
_FINITE_VERB_RE = re.compile(
    r"\b("
    r"is|are|was|were|has|have|had|does|do|did|"
    r"can|could|will|would|shall|should|may|might|must|"
    r"[a-z]{3,}s\b|"  # third-person singular (e.g. "enables", "improves")
    r"[a-z]{3,}ed\b|"  # past tense / past participle (e.g. "reduced", "scaled")
    r"[a-z]{3,}es\b"   # third-person plural form (e.g. "establishes")
    r")",
    re.IGNORECASE,
)

# Noun-phrase-only starters that signal a fragment sentence when the rest is participial.
# Pattern: "NOUN_PHRASE, <participial_phrase>." with no finite verb.
_PARTICIPIAL_OPENER_RE = re.compile(
    r"^[A-Z][^.!?]*,\s+(built|established|formed|developed|grounded|rooted|"
    r"founded|centered|driven|designed|shaped|created)\s+through\b",
    re.IGNORECASE,
)


def check_exec_summary_no_sentence_fragment(
    resume_display_text: str,
) -> tuple[bool, str | None]:
    """Reject executive summary display text that contains a grammatical fragment.

    A fragment is any sentence that either:
    1. Matches the participial-opener pattern (noun phrase + ', built/established through...')
    2. Has no finite verb token (pure noun-phrase sentence)

    RC-B from plan exec-summary-rc-structural-repair-f4a8c2: fact_quant_hpc_003
    preferred_c0_display_text 'FSA-chartered quantitative foundation, built through...'
    was a fragment that Gemini-class judges flagged as S4 sentence quality failure.
    """
    fragments: list[str] = []
    for i, sent in enumerate(split_sentences(resume_display_text)):
        sent_stripped = sent.strip()
        if not sent_stripped:
            continue
        if _PARTICIPIAL_OPENER_RE.search(sent_stripped):
            fragments.append(f"S{i + 1}(participial_fragment): {sent_stripped[:80]}")
            continue
        if not _FINITE_VERB_RE.search(sent_stripped):
            fragments.append(f"S{i + 1}(no_finite_verb): {sent_stripped[:80]}")
    if fragments:
        return False, f"Sentence fragment(s) detected in resume_display_text: {fragments}"
    return True, None


_DISPLAY_OVERRIDE_REQUIRED_SUBSTRINGS: dict[str, str] = {
    "fact_quant_hpc_003": "fsa-chartered actuarial work in capital modeling",
    "fact_engineering_platform_002": "dependency graph intelligence enables accelerated legacy-system analysis",
}


def check_exec_summary_display_override_compliance(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """When a DISPLAY_OVERRIDE fact is cited, require its stable middle anchor in display prose."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        FACT_C0_DISPLAY_OVERRIDES,
    )

    low = str(resume_display_text or "").lower()
    cited: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            base = str(fid).split("_metric_")[0]
            if base:
                cited.add(base)
    missing: list[str] = []
    for fid in FACT_C0_DISPLAY_OVERRIDES:
        if fid not in cited:
            continue
        anchor = _DISPLAY_OVERRIDE_REQUIRED_SUBSTRINGS.get(fid, "")
        if anchor and anchor not in low:
            missing.append(f"{fid} missing anchor '{anchor}'")
    if missing:
        return False, "DISPLAY_OVERRIDE compliance failed: " + "; ".join(missing)
    return True, None


def check_judge_packet_display_override_parity(
    *,
    judge_allowed_fact_packet: list[dict[str, Any]] | None,
    cited_fact_ids: list[str] | set[str] | None,
) -> tuple[bool, str | None]:
    """Verify every cited fact with a C0 display override carries display_override_text in the judge packet.

    Closes Bug:ExecSummaryJudgeDisplayOverrideInvisible by failing the lane closed when the X1D
    judge packet rows lose the FACT_C0_DISPLAY_OVERRIDES substrate that Qwen receives. Symmetry
    requirement: gen-prompt DISPLAY_OVERRIDE present <=> judge-packet display_override_text present.
    """
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        FACT_C0_DISPLAY_OVERRIDES,
    )

    rows = judge_allowed_fact_packet or []
    cited_raw = list(cited_fact_ids or [])
    cited: set[str] = set()
    for fid in cited_raw:
        s = str(fid).strip()
        if not s:
            continue
        cited.add(s)
        base = s.split("_metric_")[0]
        if base:
            cited.add(base)
    packet_overrides_by_fid: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("fact_id") or "").strip()
        if not fid:
            continue
        text = str(row.get("display_override_text") or "").strip()
        if text:
            packet_overrides_by_fid[fid] = text
    missing: list[str] = []
    for fid, expected in FACT_C0_DISPLAY_OVERRIDES.items():
        if fid not in cited:
            continue
        expected_clean = str(expected or "").strip()
        if not expected_clean:
            continue
        actual = packet_overrides_by_fid.get(fid, "").strip()
        if not actual:
            base = fid.split("_metric_")[0]
            actual = packet_overrides_by_fid.get(base, "").strip()
        if actual != expected_clean:
            missing.append(fid)
    if missing:
        return (
            False,
            f"judge_packet_missing_display_override_text:{','.join(sorted(missing))} "
            f"(see Bug:ExecSummaryJudgeDisplayOverrideInvisible)",
        )
    return True, None


def check_exec_summary_strategy_no_commercialization_thread(
    resume_display_text: str,
    *,
    target_role: str | None = None,
) -> tuple[bool, str | None]:
    """SVP strategy lane must not resurrect the deprecated commercialization identity thread."""
    from apps_rg.runtime.sections.executive_summary_pa import is_strategy_executive_target_title

    if not is_strategy_executive_target_title(str(target_role or "")):
        return True, "skipped_not_strategy_lane"
    if "commercialization" in str(resume_display_text or "").lower():
        return (
            False,
            "SVP strategy lane forbids 'commercialization' in resume_display_text; use digital innovation framing",
        )
    return True, None


def check_exec_summary_meta_filler_patterns(resume_display_text: str) -> tuple[bool, str | None]:
    lowered = resume_display_text.lower()
    hits: list[str] = []
    for phrase in EXEC_SUMMARY_FORBIDDEN_META_PHRASES:
        if phrase in lowered:
            hits.append(phrase)
    for phrase in EXEC_SUMMARY_FORBIDDEN_META_PHRASES_LOOSE:
        if phrase in lowered:
            hits.append(phrase)
    for i, sent in enumerate(split_sentences(resume_display_text)):
        words = [w.lower().strip(".,;:") for w in sent.split() if w.strip()]
        if words and words[0] in ("additionally", "furthermore", "moreover"):
            hits.append(f"sentence_{i}_opens_with_{words[0]}")
    if hits:
        return False, f"Executive summary meta or filler scaffolding: {hits}"
    return True, None


def check_resume_display_colon_space_discipline(resume_display_text: str) -> tuple[bool, str | None]:
    """Block colon-space clause stitching (claim-title : prose) in user-visible summary."""
    if ": " in resume_display_text:
        return False, "Colon-space clause stitching is forbidden in resume_display_text."
    return True, None


def check_transport_envelope_stub_false(
    artifacts_dir: Path | None,
    provider_requested: str | None,
) -> tuple[bool, str | None]:
    """Reject synthetic harness responses that set stub:true on the vLLM JSON envelope."""
    if str(provider_requested or "").strip().lower() != "external_claude":
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

# Executive-summary mechanical chains (prompt + X1D); includes leading fillers.
EXEC_SUMMARY_MECHANICAL_OPENERS = (
    "led",
    "successfully",
    "also",
    "built",
    "delivered",
    "designed",
    "implemented",
    "architected",
    "productized",
    "scaled",
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
    "executive_strategy_thesis",
    "resume_display_text",
    "executive_summary_text",
    "selected_fact_plan",
    "claim_ledger",
    "jd_alignment",
    "gap_notes",
    "change_log",
    "self_check",
    "sentence_map",
    "brushstroke_map",
    "graph_skill_refs",
    "executive_summary_composition_plan",
    "text_claim_coverage",
    "source_sensitive_phrase_ledger",
    "input_payload_hash",
    "output_payload_hash",
    "claim_ledger_hash",
    "allowed_fact_ids_hash",
    "c0_graph_diagnostics",
    "allowed_fact_utilization_receipt",
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

# Allowed generation model names (apps_rg external Claude generation model SSOT).
ALLOWED_MODELS = [SECTION_MODEL_ID]

# Required X1D judge providers
REQUIRED_JUDGE_PROVIDERS = list(REQUIRED_JUDGE_PROVIDER_KEYS)


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


def check_exec_summary_stock_bridge_count(
    text: str,
    *,
    max_bridges: int = 2,
) -> tuple[bool, str | None]:
    """Advisory/runtime lint: at most ``max_bridges`` stock connectives in display S2–S5."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        EXEC_SUMMARY_STOCK_BRIDGE_PREFIXES,
    )

    sentences = split_sentences(text)
    if len(sentences) < 3:
        return True, None
    body = sentences[1:5] if len(sentences) >= 6 else sentences[1:]
    hits = 0
    matched: list[str] = []
    for sentence in body:
        low = sentence.strip().lower()
        for prefix in EXEC_SUMMARY_STOCK_BRIDGE_PREFIXES:
            if low.startswith(prefix):
                hits += 1
                matched.append(prefix)
                break
    if hits > max_bridges:
        return (
            False,
            f"stock_bridge_stack:{hits}_in_s2_s5_max_{max_bridges}_matched={','.join(matched)}",
        )
    return True, None


def check_exec_summary_mechanical_opener_stack(
    text: str,
    *,
    min_hits: int = 3,
) -> tuple[bool, str | None]:
    """Fail when too many sentences start with resume bullet-chain openers."""
    sentences = split_sentences(text)
    if len(sentences) < min_hits:
        return True, None
    hits = 0
    for sentence in sentences:
        first = sentence.split()[0].lower().strip(",.;:") if sentence.split() else ""
        if first in EXEC_SUMMARY_MECHANICAL_OPENERS:
            hits += 1
    if hits >= min_hits:
        return (
            False,
            f"mechanical_opener_stack:{hits}_sentences_with_{','.join(EXEC_SUMMARY_MECHANICAL_OPENERS[:5])}_style_openers",
        )
    return True, None


def _source_fact_base_id(fid: str) -> str:
    s = str(fid or "").strip()
    if "_metric_" in s:
        return s.split("_metric_", 1)[0]
    return s


def check_cross_fact_display_conflation(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """Detect platform + governance (+ margin) merged into one display sentence."""
    text = str(resume_display_text or "")
    if not text.strip():
        return True, None
    gov_ids = {"fact_governance_003"}
    plat_ids = {"fact_engineering_platform_001", "fact_engineering_platform_006"}
    margin_markers = re.compile(
        r"(?:gross\s+margins?|margin\s+expansion|regulatory\s+reporting\s+errors?|40\s*%)",
        re.IGNORECASE,
    )
    platform_markers = re.compile(
        r"\b(governed\s+enterprise\s+ai\s+platform|agentic\s+ai\s+platform|enterprise\s+ai\s+platform)\b",
        re.IGNORECASE,
    )
    for sentence in split_sentences(text):
        sl = sentence.lower()
        if not margin_markers.search(sentence):
            continue
        has_platform = bool(platform_markers.search(sentence))
        ledger_bases: set[str] = set()
        for row in claim_ledger:
            if not isinstance(row, dict):
                continue
            ct = str(row.get("claim_text") or "").strip()
            if ct and ct not in sentence:
                continue
            for raw in row.get("source_fact_ids") or []:
                ledger_bases.add(_source_fact_base_id(str(raw)))
        row_has_gov = bool(ledger_bases & gov_ids) or (
            "reporting error" in sl and "40" in sl
        )
        row_has_plat = bool(ledger_bases & plat_ids) or has_platform
        if row_has_gov and row_has_plat and margin_markers.search(sentence):
            return (
                False,
                "cross_fact_display_conflation:platform_and_governance_metrics_in_one_sentence",
            )
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        bases = {_source_fact_base_id(str(x)) for x in (row.get("source_fact_ids") or [])}
        if bases & gov_ids and bases & plat_ids:
            ct = str(row.get("claim_text") or "")
            if margin_markers.search(ct) and platform_markers.search(ct):
                return (
                    False,
                    "cross_fact_display_conflation:ledger_row_merges_platform_and_governance",
                )
    return True, None


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
    if len(sentences) < EXEC_SUMMARY_MIN_SENTENCES:
        if EXEC_SUMMARY_MIN_SENTENCES == EXEC_SUMMARY_MAX_SENTENCES:
            return (
                False,
                f"Output has {len(sentences)} sentences; executive synthesis requires exactly "
                f"{EXEC_SUMMARY_MIN_SENTENCES} sentences",
            )
        return (
            False,
            f"Output has {len(sentences)} sentences; executive synthesis requires "
            f"{EXEC_SUMMARY_MIN_SENTENCES}-{EXEC_SUMMARY_MAX_SENTENCES}",
        )
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

    mech_ok, mech_reason = check_exec_summary_mechanical_opener_stack(text)
    if not mech_ok and mech_reason:
        return False, mech_reason

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


def _sensitive_phrase_present(text_lower: str, phrase: str) -> bool:
    """Detect phrase in lowered text without substring false positives on stems.

    Multi-word phrases use substring match. Single-token phrases use word boundaries
    so ``audit`` does not fire on ``auditability`` unless the fact or output actually
    contains the word ``audit``.
    """
    pl = phrase.lower()
    if " " in pl:
        return pl in text_lower
    return re.search(rf"\b{re.escape(pl)}\b", text_lower) is not None


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
            if _sensitive_phrase_present(combined, phrase):
                supported_phrases.add(phrase)
    
    # Check if any sensitive phrase in output is NOT supported
    unsupported_in_output = []
    for phrase in SOURCE_SENSITIVE_PHRASES:
        if _sensitive_phrase_present(text_lower, phrase) and phrase not in supported_phrases:
            unsupported_in_output.append(phrase)
    
    if unsupported_in_output:
        return False, f"Unsupported sensitive phrases: {unsupported_in_output}"
    
    return True, None


def check_executive_strategy_thesis(parsed_output: dict[str, Any] | None) -> tuple[bool, str | None]:
    """SVP strategy lanes require a non-empty executive_strategy_thesis before display prose."""
    if parsed_output is None:
        return False, "parsed_output is None"
    thesis = str(parsed_output.get("executive_strategy_thesis") or "").strip()
    if not thesis:
        return False, "executive_strategy_thesis missing or empty"
    if len(thesis.split()) < 8:
        return False, "executive_strategy_thesis too short for SVP strategy framing"
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


POST_X2_X1D_WIRING_GATE_IDS: frozenset[str] = frozenset(
    {
        "x2_x1d_required_judges_present",
        "x2_x1d_raw_responses_written",
        "x2_x1d_schema_valid",
        "x2_x1d_judge_packet_hash_uniform",
    }
)


def check_x1d_judge_packet_hash_uniform(
    x1d_judges: list[dict[str, Any]] | None,
) -> tuple[bool, str | None]:
    """Every MODEL_BACKED judge must grade the same judge_packet_hash / input_hash."""
    hashes: set[str] = set()
    for judge in x1d_judges or []:
        if not isinstance(judge, dict):
            continue
        if str(judge.get("evaluator_mode") or "") != "MODEL_BACKED":
            continue
        if judge.get("provider_blocked"):
            continue
        h = str(judge.get("judge_packet_hash") or judge.get("input_hash") or "").strip()
        if h:
            hashes.add(h)
    if len(hashes) <= 1:
        return True, None
    return False, f"multiple judge_packet_hash values across panel: {sorted(hashes)}"


def append_executive_summary_x1d_x2_gate_dicts(
    *,
    x1d_judges: list[dict[str, Any]] | None,
    artifacts_dir: Path,
) -> list[dict[str, Any]]:
    """X1D presence/schema gates — run only after post-X2 judge phase."""
    out: list[dict[str, Any]] = []

    def _row(gate_id: str, passed: bool, observed: Any, threshold: Any, reason: str | None) -> None:
        out.append(
            {
                "gate_id": gate_id,
                "gate_type": "deterministic",
                "pass": passed,
                "observed_value": observed,
                "threshold": threshold,
                "failure_reason": None if passed else reason,
                "evidence_ref": gate_id,
            }
        )

    judges_present_ok, judges_present_reason = check_judge_rows_present(
        x1d_judges, required_providers=required_judges_for_section("executive_summary")
    )
    _row(
        "x2_x1d_required_judges_present",
        judges_present_ok,
        judges_present_reason,
        None,
        judges_present_reason,
    )
    raw_responses_ok, raw_responses_reason = check_judge_raw_responses_written(artifacts_dir, x1d_judges)
    _row(
        "x2_x1d_raw_responses_written",
        raw_responses_ok,
        raw_responses_reason,
        None,
        raw_responses_reason,
    )
    if x1d_judges:
        invalid: list[str] = []
        for judge in x1d_judges:
            schema_ok, schema_reason = check_judge_schema_valid(judge)
            if not schema_ok:
                pk = judge.get("provider_key", "unknown")
                invalid.append(f"{pk}: {schema_reason}")
        x1d_schema_ok = len(invalid) == 0
        _row(
            "x2_x1d_schema_valid",
            x1d_schema_ok,
            invalid,
            [],
            None if x1d_schema_ok else "; ".join(invalid),
        )
    else:
        _row(
            "x2_x1d_schema_valid",
            False,
            "no judges",
            "judges present",
            "No X1D judges to validate.",
        )

    hash_uniform_ok, hash_uniform_reason = check_x1d_judge_packet_hash_uniform(x1d_judges)
    _row(
        "x2_x1d_judge_packet_hash_uniform",
        hash_uniform_ok,
        sorted(
            {
                str(j.get("judge_packet_hash") or j.get("input_hash") or "")
                for j in (x1d_judges or [])
                if isinstance(j, dict)
                and str(j.get("evaluator_mode") or "") == "MODEL_BACKED"
                and not j.get("provider_blocked")
            }
            - {""}
        ),
        "single_hash",
        hash_uniform_reason,
    )

    return out


def check_judge_rows_present(
    x1d_judges: list[dict[str, Any]] | None,
    *,
    required_providers: list[str] | None = None,
) -> tuple[bool, str | None]:
    """Check if all required judge provider rows are present."""
    if x1d_judges is None:
        return False, "x1d_judges is None"

    required = list(required_providers or REQUIRED_JUDGE_PROVIDERS)
    present_providers = {j.get("provider_key") for j in x1d_judges}
    missing = [p for p in required if p not in present_providers]
    
    if missing:
        return False, f"Missing required judge providers: {', '.join(missing)}"
    return True, None


def required_judges_for_section(section_id: str) -> list[str]:
    """Per-lane required judge providers, sourced from the recalibrated ``section_judge_policy`` SSOT.

    W0-A (plan ``prompt-gate-ssot-consolidation-e7c9a2``): the Claude-base judge recalibration
    (dual panel = gemini_pro+openai_chatgpt; single panel = gemini_pro; anthropic_claude self-judge
    dropped) never propagated to the legacy module-level ``REQUIRED_JUDGE_PROVIDERS`` 3-list, so
    ``x2_x1d_required_judges_present`` demanded an ``anthropic_claude`` row no recalibrated lane emits
    and ``BLOCKS_GENERATION`` fired on a prompt<->gate disagreement. The required-judges gate must
    require exactly what the policy declares for the lane -- nothing more, nothing less.
    """
    from apps_rg.runtime.section_judge_policy import get_section_judge_policy

    return list(get_section_judge_policy(section_id).required_judge_providers)


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


def _normalize_display_clause(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def _token_overlap_matches(reference_lower: str, sentence_lower: str) -> bool:
    tokens = _ledger_claim_tokens(reference_lower)
    if not tokens:
        return False
    hits = sum(1 for token in tokens if token in sentence_lower)
    return hits >= max(1, min(3, len(tokens)))


def _display_claim_token_overlap_matches(claim_display: str, sentence_lower: str) -> bool:
    """Display ``claim`` overlap: avoid binding S6 capstone to thesis row via generic tokens only."""
    display_norm = _normalize_display_clause(claim_display)
    tokens = _ledger_claim_tokens(display_norm)
    if not tokens:
        return False
    hits = sum(1 for token in tokens if token in sentence_lower)
    need = max(1, min(3, len(tokens)))
    if hits < need:
        return False
    return (hits / len(tokens)) >= 0.45


def _row_sentence_match_strength(sentence: str, row: dict[str, Any]) -> int:
    """Score how well a ledger row binds to one display sentence (higher = display-bound)."""
    sentence_lower = sentence.lower().strip()
    claim_display = str(row.get("claim") or "").strip()
    claim_text = str(row.get("claim_text") or "").strip()

    if claim_display:
        display_norm = _normalize_display_clause(claim_display)
        sentence_norm = _normalize_display_clause(sentence)
        if display_norm == sentence_norm:
            return 100
        if display_norm in sentence_norm or sentence_norm in display_norm:
            return 90
        if _display_claim_token_overlap_matches(claim_display, sentence_lower):
            return 70

    if claim_text and _token_overlap_matches(claim_text.lower(), sentence_lower):
        return 50

    return 0


def _matching_ledger_rows_for_display_sentence(
    sentence: str,
    claim_ledger: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Rows that support this sentence; prefer display ``claim`` over fact ``claim_text`` only."""
    scored: list[tuple[int, dict[str, Any]]] = []
    for row in claim_ledger:
        strength = _row_sentence_match_strength(sentence, row)
        if strength > 0:
            scored.append((strength, row))
    if not scored:
        return []
    scored.sort(key=lambda item: item[0], reverse=True)
    best = scored[0][0]
    if best >= 70:
        top = [row for strength, row in scored if strength == best]
        return top[:1]
    return [row for strength, row in scored if strength == best]


def build_sentence_claim_coverage(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> dict[str, Any]:
    """Map every displayed sentence to material claim support.

    Display sentences bind to ledger ``claim`` (paraphrase shown in resume_display_text);
    fact proof remains ``claim_text`` + ``source_fact_ids``. Does not invent support.
    """
    sentences = split_sentences(resume_display_text)
    coverage_rows = []
    overall_pass = True

    for idx, sentence in enumerate(sentences, 1):
        matching_claims = _matching_ledger_rows_for_display_sentence(sentence, claim_ledger)

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
                claim_line = str(claim.get("claim_text") or "").strip()
                source_ids = list(claim.get("source_fact_ids") or [])
                valid_source_ids = [sid for sid in source_ids if sid in allowed_fact_ids or "_metric_" in sid]
                status = "SUPPORTED" if valid_source_ids else "UNSUPPORTED"
                if status != "SUPPORTED":
                    sentence_pass = False
                    overall_pass = False
                material_claims.append({
                    "claim_text": claim_line,
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


def check_claim_ledger_row_count_matches_sentence_count(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """Strategy lane: one claim_ledger row per displayed sentence."""
    n_sentences = len([s for s in split_sentences(resume_display_text) if str(s).strip()])
    n_rows = len(claim_ledger)
    if n_sentences == n_rows:
        return True, None
    return False, f"display_sentences={n_sentences} claim_ledger_rows={n_rows}"


def check_self_check_claim_ledger_consistent(
    parsed_output: dict[str, Any] | None,
    text_claim_coverage: dict[str, Any],
) -> tuple[bool, str | None]:
    """When the model asserts full ledger coverage, coverage must agree."""
    if not isinstance(parsed_output, dict):
        return True, None
    sc = parsed_output.get("self_check")
    if not isinstance(sc, dict):
        return True, None
    if sc.get("every_material_claim_in_claim_ledger") is not True:
        return True, None
    if text_claim_coverage.get("overall_pass") is True:
        return True, None
    return (
        False,
        "self_check.every_material_claim_in_claim_ledger=true but "
        "text_claim_coverage.overall_pass is false.",
    )


def ledger_row_display_claim_materialized(row: dict[str, Any], resume_display_text: str) -> bool:
    """True when ledger display ``claim`` (not fact ``claim_text`` alone) appears in resume body."""
    claim_display = str(row.get("claim") or "").strip()
    if not claim_display:
        return True
    resume_norm = _normalize_display_clause(resume_display_text)
    display_norm = _normalize_display_clause(claim_display)
    if display_norm and display_norm in resume_norm:
        return True
    return _display_claim_token_overlap_matches(claim_display, resume_display_text.lower())


def check_claim_field_maps_to_display_sentence(
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """Each non-empty ledger ``claim`` must corroborate resume_display_text."""
    orphans: list[str] = []
    for idx, row in enumerate(claim_ledger, 1):
        if not str(row.get("claim") or "").strip():
            continue
        if not ledger_row_display_claim_materialized(row, resume_display_text):
            orphans.append(f"row_{idx}")
    if orphans:
        return False, f"ledger claim not materialized in resume_display_text: {', '.join(orphans)}"
    return True, None


NORTH_STAR_SIGNATURE_PHRASES = (
    "fellow of the society of actuaries",
    "$22m",
    "$22 m",
    "reclaimed $14m",
    "reclaimed $14 m",
    "reclaimed $14",
    "productized ai revenue",
    "gross margins",
    "gross margin expansion",
    "expanding gross margins",
)


def _selected_facts_support_blob(selected_facts: list[dict[str, Any]] | None) -> str:
    parts: list[str] = []
    for fact in selected_facts or []:
        if not isinstance(fact, dict):
            continue
        parts.append(str(fact.get("claim_text") or ""))
        parts.append(str(fact.get("achievement_summary") or ""))
        parts.append(str(fact.get("metric_raw") or ""))
        parts.append(str(fact.get("text") or ""))
    return " ".join(parts).lower()


_GRAPH_EVIDENCE_PERCENT_CAPTURE_RE = re.compile(r"\b(\d+)\s*%")


def _percent_values_from_text(text: str) -> set[str]:
    """Capture N% tokens; avoid trailing \\b after % (fails before punctuation)."""
    return set(_GRAPH_EVIDENCE_PERCENT_CAPTURE_RE.findall(str(text or "").lower()))


def _metric_tokens_from_text(text: str) -> list[str]:
    tokens: list[str] = []
    for m in _GRAPH_EVIDENCE_PERCENT_CAPTURE_RE.findall(str(text or "").lower()):
        tokens.append(f"{m}%")
    if "gross margin" in str(text or "").lower():
        tokens.append("gross margin")
    return tokens


def check_north_star_style_example_echo_unsupported(
    resume_display_text: str,
    selected_facts: list[dict[str, Any]] | None,
) -> tuple[bool, str | None]:
    """Reject visible paste of gold-example metrics/credentials absent from selected facts."""
    blob = _selected_facts_support_blob(selected_facts)
    lower = resume_display_text.lower()
    hits: list[str] = []
    for phrase in NORTH_STAR_SIGNATURE_PHRASES:
        p = phrase.lower()
        if p in lower and p not in blob:
            hits.append(phrase)
    if hits:
        return False, "Style-example echo without selected-fact support: " + ", ".join(hits)
    return True, None


def check_raw_json_no_selected_fact_plan_echo(raw_output: str | None) -> tuple[bool, str | None]:
    """Model JSON must not echo selected_fact_plan; runtime injects it before X2."""
    if raw_output is None or not str(raw_output).strip():
        return True, None
    stripped = str(raw_output).strip()
    if not stripped.startswith("{"):
        return True, None
    try:
        obj = json.loads(stripped)
    except json.JSONDecodeError:
        return True, None
    if isinstance(obj, dict) and "selected_fact_plan" in obj:
        return (
            False,
            "Model emitted selected_fact_plan in raw JSON; runtime owns selected_fact_plan.json",
        )
    return True, None


def check_exec_summary_sentence_count_6(resume_display_text: str) -> tuple[bool, str | None]:
    """Single product shape: exactly six polished sentences."""
    sentences = [s for s in split_sentences(resume_display_text) if str(s).strip()]
    n = len(sentences)
    if n != EXEC_SUMMARY_MIN_SENTENCES:
        return (
            False,
            f"resume_display_text must have exactly {EXEC_SUMMARY_MIN_SENTENCES} sentences; found {n} "
            "(legacy 4–5 and 5–6 bands retired)",
        )
    return True, None


def _collapse_display_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def check_exec_summary_display_roundtrip_integrity(resume_display_text: str) -> tuple[bool, str | None]:
    """Fail when split/join mutates display text or leaves abbrev-guard control bytes."""
    text = str(resume_display_text or "").strip()
    if not text:
        return True, None
    if any(ord(ch) < 32 and ch not in ("\n", "\t") for ch in text):
        return False, "control_characters_in_resume_display_text"
    if "\x1f" in text or "\ue000" in text or "\ue001" in text:
        return False, "abbrev_guard_token_leaked_into_display_text"
    parts = [s for s in split_sentences(text) if str(s).strip()]
    joined = " ".join(parts)
    if _collapse_display_whitespace(joined) != _collapse_display_whitespace(text):
        return False, "split_sentences_join_roundtrip_mismatch"
    return True, None


_CROSS_SENTENCE_DEDUP_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(?:scaled|scaling)\s+(?:the\s+)?ml engineering organization from 8 to 28\b", re.I), "team_8_to_28"),
    (re.compile(r"\b8\s+to\s+28\s+specialists\b", re.I), "team_8_to_28_specialists"),
)


def check_exec_summary_cross_sentence_metric_dedup(resume_display_text: str) -> tuple[bool, str | None]:
    """Fail when the same high-signal metric clause appears in multiple sentences."""
    sentences = split_sentences(resume_display_text)
    for _pat, label in _CROSS_SENTENCE_DEDUP_PATTERNS:
        hits = sum(1 for sent in sentences if _pat.search(sent))
        if hits > 1:
            return False, f"duplicate_metric_across_sentences:{label}:{hits}"
    return True, None


def check_c03_selected_fact_ids_claimable_subset_allowed_fact_ids(
    *,
    allowed_fact_ids: set[str] | list[str] | None,
    proof_pool_metadata: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    """Fail when track/C03 expansion advertises claimable facts outside the proof pool."""
    allowed = {str(x).strip() for x in (allowed_fact_ids or []) if str(x).strip()}
    if not allowed:
        return False, "missing_allowed_fact_ids"
    from apps_rg.runtime.c0.c03_allowlist_coherence import (
        collect_expansion_fact_ids,
        fact_id_in_allowed_pool,
    )

    meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    c03 = meta.get("c03_graphrag_bound")
    track = meta.get("track_weighted_graph_expansion") or {}
    expansion_ids = collect_expansion_fact_ids(c03_bound=c03 if isinstance(c03, dict) else None, track_expansion=track)
    violations = sorted({fid for fid in expansion_ids if not fact_id_in_allowed_pool(fid, allowed)})
    filtered = meta.get("c03_filtered_out_fact_ids") or []
    if violations and not filtered:
        return False, f"claimable_outside_pool:{violations}"
    if violations and filtered and sorted(filtered) != violations:
        return False, f"filtered_out_mismatch:violations={violations}:filtered={filtered}"
    return True, None


def check_exec_summary_sentence_count_5_6(resume_display_text: str) -> tuple[bool, str | None]:
    """Deprecated alias — product band is exactly six sentences."""
    return check_exec_summary_sentence_count_6(resume_display_text)


def check_exec_summary_sentence_count_4_5(resume_display_text: str) -> tuple[bool, str | None]:
    """Deprecated alias — product band is exactly six sentences."""
    return check_exec_summary_sentence_count_6(resume_display_text)


def check_exec_summary_jd_alignment_proof_flags(
    parsed_output: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    """Align with headline/competencies spine: JD/briefing/companion never proof."""
    if not isinstance(parsed_output, dict):
        return False, "missing parsed output"
    jd = parsed_output.get("jd_alignment")
    if not isinstance(jd, dict):
        return False, "jd_alignment must be object"
    if jd.get("targeting_only") is not True:
        return False, "jd_alignment.targeting_only must be true"
    if "jd_used_as_proof" not in jd or jd.get("jd_used_as_proof") is not False:
        return False, "jd_used_as_proof must be present and exactly false"
    if "briefing_used_as_proof" not in jd or jd.get("briefing_used_as_proof") is not False:
        return False, "briefing_used_as_proof must be present and exactly false"
    cmp_raw = jd.get("companion_context_used_as_proof")
    if cmp_raw is True:
        return False, "companion_context_used_as_proof must not be true"
    if cmp_raw is not None and cmp_raw is not False:
        return False, "companion_context_used_as_proof must be boolean false when present"
    gt = jd.get("graph_targeting")
    if not isinstance(gt, dict):
        return False, "jd_alignment.graph_targeting required for executive_summary C0.3 posture"
    if gt.get("fallback_pillar_bridge_used") is True:
        return (
            False,
            "fallback_pillar_bridge_used=true; generic pillar bridge is not release-eligible targeting",
        )
    if gt.get("release_eligible_targeting_proof") is True and gt.get("sqlite_projection_row_found") is not True:
        if gt.get("projection_source") != "sqlite_role_family_projection":
            return (
                False,
                "release_eligible_targeting_proof without sqlite_role_family_projection row",
            )
    if gt.get("projection_source") == "missing_no_taxonomy_pillars":
        return False, "role_family_projection missing; no taxonomy pillar hints"
    if gt.get("release_eligible_targeting_proof") is not True and gt.get("targeting_degraded_explicit") is not True:
        return False, "targeting must be explicit sqlite projection or targeting_degraded_explicit"
    return True, None


EVIDENCE_UTIL_MIN_POOL_FOR_LEDGER_DEPTH = 6
EVIDENCE_UTIL_MIN_LEDGER_ROWS_WHEN_POOL_LARGE = 5
EVIDENCE_UTIL_MIN_POOL_FOR_THIN_SENTENCE = 5
EVIDENCE_UTIL_MIN_WORDS_PER_SENTENCE_WHEN_FOUR = 12


def _pool_too_small_excused(parsed_output: dict[str, Any] | None) -> bool:
    if not isinstance(parsed_output, dict):
        return False
    sc = parsed_output.get("self_check")
    if not isinstance(sc, dict):
        return False
    if sc.get("selected_fact_pool_too_small") is not True:
        return False
    return bool(str(sc.get("selected_fact_pool_too_small_reason") or "").strip())


def _is_cert_fact_id_for_utilization(fact_id: str) -> bool:
    """Credential inventory facts are optional in exec summary; omit from utilization pool size."""
    base = str(fact_id or "").strip().split("_metric_", 1)[0]
    return base.startswith("fact_certs_")


def _selected_fact_pool_size(
    parsed_output: dict[str, Any] | None,
    *,
    selected_facts: list[dict[str, Any]] | None = None,
) -> int:
    if selected_facts is not None:
        return sum(
            1
            for f in selected_facts
            if isinstance(f, dict)
            and str(f.get("fact_id") or "").strip()
            and not _is_cert_fact_id_for_utilization(str(f.get("fact_id") or ""))
        )
    if not isinstance(parsed_output, dict):
        return 0
    plan = parsed_output.get("selected_fact_plan")
    if isinstance(plan, dict):
        facts = plan.get("facts") or []
        return sum(
            1
            for f in facts
            if isinstance(f, dict)
            and str(f.get("fact_id") or "").strip()
            and not _is_cert_fact_id_for_utilization(str(f.get("fact_id") or ""))
        )
    return 0


def _fact_id_base_for_utilization(fid: str) -> str:
    s = str(fid or "").strip()
    return s.split("_metric_", 1)[0] if "_metric_" in s else s


def collect_cited_source_fact_ids(
    claim_ledger: list[dict[str, Any]],
    text_claim_coverage: dict[str, Any] | None = None,
) -> set[str]:
    """Union of fact IDs cited in claim_ledger and text_claim_coverage material claims."""
    cited: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            s = str(fid).strip()
            if not s:
                continue
            cited.add(s)
            cited.add(_fact_id_base_for_utilization(s))
    if isinstance(text_claim_coverage, dict):
        for sent in text_claim_coverage.get("sentences") or []:
            if not isinstance(sent, dict):
                continue
            for mc in sent.get("material_claims") or []:
                if not isinstance(mc, dict):
                    continue
                for fid in mc.get("source_fact_ids") or []:
                    s = str(fid).strip()
                    if not s:
                        continue
                    cited.add(s)
                    cited.add(_fact_id_base_for_utilization(s))
    return cited


def default_allowed_fact_utilization_waivers(allowed_fact_ids: set[str]) -> frozenset[str]:
    """Credential inventory facts may sit in pool without display weave (I0 / no_credential_dump)."""
    return frozenset(
        fid for fid in allowed_fact_ids if fid and _is_cert_fact_id_for_utilization(str(fid))
    )


def resolve_utilization_waived_fact_ids(allowed_fact_ids: set[str]) -> set[str]:
    """Env override: APPS_RG_EXEC_SUMMARY_UTILIZATION_WAIVE_FACT_IDS=comma-separated fact ids."""
    import os

    raw = str(os.environ.get("APPS_RG_EXEC_SUMMARY_UTILIZATION_WAIVE_FACT_IDS") or "").strip()
    if raw:
        explicit = {x.strip() for x in raw.split(",") if x.strip()}
        return {fid for fid in explicit if fid in allowed_fact_ids}
    return set(default_allowed_fact_utilization_waivers(allowed_fact_ids))


def collect_unused_allowed_fact_ids(
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> list[str]:
    cited = collect_cited_source_fact_ids(claim_ledger)
    unused = [fid for fid in sorted(allowed_fact_ids) if fid and fid not in cited]
    return unused


def check_exec_summary_allowed_fact_utilization(
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    *,
    text_claim_coverage: dict[str, Any] | None = None,
    waived_fact_ids: set[str] | None = None,
) -> tuple[bool, str | None, dict[str, Any]]:
    """Every non-waived allowed fact must appear in claim_ledger or text_claim_coverage."""
    allowed = {str(x).strip() for x in allowed_fact_ids if str(x).strip()}
    waived = (
        {str(x).strip() for x in waived_fact_ids if str(x).strip()}
        if waived_fact_ids is not None
        else resolve_utilization_waived_fact_ids(allowed)
    )
    required = allowed - waived
    cited = collect_cited_source_fact_ids(claim_ledger, text_claim_coverage)
    missing: list[str] = []
    for fid in sorted(required):
        base = _fact_id_base_for_utilization(fid)
        if fid not in cited and base not in cited:
            missing.append(fid)
    receipt = {
        "waived_fact_ids": sorted(waived),
        "required_utilization_fact_ids": sorted(required),
        "cited_fact_ids": sorted(cited),
        "unused_required_fact_ids": missing,
        "policy": "cert_facts_waived_by_default",
    }
    if missing:
        return False, f"unused_required_allowed_facts={missing}", receipt
    return True, "ok", receipt


def check_exec_summary_evidence_utilization(
    resume_display_text: str,
    parsed_output: dict[str, Any] | None = None,
    *,
    selected_facts: list[dict[str, Any]] | None = None,
) -> tuple[bool, str | None]:
    """Structural density: weave allowed facts into narrative — not a word-count floor."""
    if _pool_too_small_excused(parsed_output):
        return True, "excused_selected_fact_pool_too_small"
    pool_size = _selected_fact_pool_size(parsed_output, selected_facts=selected_facts)
    if pool_size < EVIDENCE_UTIL_MIN_POOL_FOR_THIN_SENTENCE:
        return True, "ok_pool_below_utilization_threshold"
    ledger = list((parsed_output or {}).get("claim_ledger") or [])
    ledger_rows = sum(
        1
        for row in ledger
        if isinstance(row, dict) and str(row.get("claim_text") or "").strip()
    )
    sentences = [s for s in split_sentences(resume_display_text) if str(s).strip()]
    failures: list[str] = []
    if pool_size >= EVIDENCE_UTIL_MIN_POOL_FOR_LEDGER_DEPTH and ledger_rows < EVIDENCE_UTIL_MIN_LEDGER_ROWS_WHEN_POOL_LARGE:
        failures.append(
            f"claim_ledger_rows_{ledger_rows}_with_pool_{pool_size}_need_at_least_{EVIDENCE_UTIL_MIN_LEDGER_ROWS_WHEN_POOL_LARGE}"
        )
    if len(sentences) == EXEC_SUMMARY_MIN_SENTENCES and pool_size >= EVIDENCE_UTIL_MIN_POOL_FOR_THIN_SENTENCE:
        for i, sent in enumerate(sentences):
            wc = len(re.findall(r"\S+", sent))
            if wc < EVIDENCE_UTIL_MIN_WORDS_PER_SENTENCE_WHEN_FOUR:
                failures.append(
                    f"sentence_{i}_words_{wc}_below_{EVIDENCE_UTIL_MIN_WORDS_PER_SENTENCE_WHEN_FOUR}_with_pool_{pool_size}"
                )
                break
    if failures:
        return False, "; ".join(failures)
    return True, "ok"


def check_exec_summary_paragraph_max_words(
    resume_display_text: str,
    parsed_output: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    """Overflow guard only — no paragraph word minimum (fit_to_evidence + exactly six sentences)."""
    _ = parsed_output
    wc = _resume_word_count(resume_display_text)
    if wc > EXEC_SUMMARY_MAX_WORDS:
        return False, f"executive summary word count {wc} exceeds maximum {EXEC_SUMMARY_MAX_WORDS}"
    return True, "ok"


def check_exec_summary_no_bloated_sentence(resume_display_text: str) -> tuple[bool, str | None]:
    for i, sent in enumerate(split_sentences(resume_display_text)):
        wc = len(re.findall(r"\S+", sent))
        if wc > EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE:
            return False, f"sentence {i} has {wc} words (max {EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE})"
    return True, None


def check_exec_summary_no_mechanism_inventory(
    resume_display_text: str,
    parsed_output: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    from apps_rg.runtime.sections.executive_summary_composition import is_mechanism_inventory_sentence

    diag = (parsed_output or {}).get("c0_graph_diagnostics") if isinstance(parsed_output, dict) else {}
    if not isinstance(diag, dict):
        diag = {}
    for i, sent in enumerate(split_sentences(resume_display_text)):
        inv, reason = is_mechanism_inventory_sentence(sent)
        if inv:
            dom_fact = str(diag.get("dominant_source_fact_id") or "unknown")
            refs = diag.get("dominant_claim_support_graph_refs") or []
            suppressed = diag.get("dominant_suppressed_skill_refs") or []
            ref_tail = ",".join(str(r) for r in refs[:6])
            sup_tail = ",".join(str(r) for r in suppressed[:6])
            return (
                False,
                f"sentence {i}: {reason}; dominant_source_fact={dom_fact}; "
                f"claim_support_graph_refs=[{ref_tail}]; suppressed_skills=[{sup_tail}]",
            )
    return True, None


# Vendor/cloud cert labels — inventory-style (e.g. AWS Associate). Not C0.3 phase-1 FSA rigor.
VENDOR_NAMED_CERT_LABELS: tuple[str, ...] = (
    "aws certified",
    "databricks",
    "certified solutions architect",
    "lakehouse fundamentals",
)

# FSA (Fellow of the Society of Actuaries): C0.3 skills-graph phase-1 rigor signal — not a vendor cert.
FSA_RIGOR_MARKERS: tuple[str, ...] = (
    "fellow of the society of actuaries",
    "society of actuaries",
    "fsa credential",
    "fsa designation",
)
FSA_WORD_RE = re.compile(r"\bfsa\b", re.IGNORECASE)

CREDENTIAL_CONTEXT_MARKERS: tuple[str, ...] = (
    *VENDOR_NAMED_CERT_LABELS,
    *FSA_RIGOR_MARKERS,
    "basel iii",
    "ccar",
)


def _vendor_named_cert_hits(low: str) -> int:
    return sum(1 for m in VENDOR_NAMED_CERT_LABELS if m in low)


def _sentence_has_fsa_rigor(low: str) -> bool:
    if any(m in low for m in FSA_RIGOR_MARKERS):
        return True
    return bool(FSA_WORD_RE.search(low))


def _sentence_fsa_rigor_only(low: str) -> bool:
    """FSA-only sentence: allowed once per summary (C0.3 phase-1), unlike vendor cert dumps."""
    return _sentence_has_fsa_rigor(low) and _vendor_named_cert_hits(low) == 0


def check_exec_summary_no_credential_dump(resume_display_text: str) -> tuple[bool, str | None]:
    from apps_rg.runtime.sections.competencies_certification_contract import is_credential_competency_term

    sentences = split_sentences(resume_display_text)
    fsa_only_indexes = [i for i, s in enumerate(sentences) if _sentence_fsa_rigor_only(s.lower())]
    if len(fsa_only_indexes) > 1:
        return (
            False,
            f"at most one FSA rigor mention allowed (C0.3 phase-1); found sentences {fsa_only_indexes}",
        )

    for i, sent in enumerate(sentences):
        low = sent.lower()
        vendor_hits = _vendor_named_cert_hits(low)
        context_hits = sum(1 for m in CREDENTIAL_CONTEXT_MARKERS if m in low)
        fsa_only = _sentence_fsa_rigor_only(low)

        if fsa_only:
            if vendor_hits >= 1:
                return False, f"sentence {i}: FSA rigor mention mixed with vendor cert labels"
            continue

        if vendor_hits >= 2:
            return False, f"sentence {i}: vendor certification inventory ({vendor_hits} labels)"
        if context_hits >= 3:
            return False, f"sentence {i}: credential or certification inventory block ({context_hits} markers)"
        if is_credential_competency_term(sent) and vendor_hits >= 1:
            return False, f"sentence {i}: vendor cert label in executive summary"
        if is_credential_competency_term(sent):
            return False, f"sentence {i}: named cert label in executive summary"
        if re.search(r"\bcredentials?\s+reinforce\b", low) and (
            vendor_hits >= 1 or _sentence_has_fsa_rigor(low)
        ):
            return False, f"sentence {i}: credential-block closing pattern"
        if i >= 3 and vendor_hits >= 1:
            return False, f"sentence {i}: named vendor cert label in closing band (S4-S6)"
    return True, None


def check_exec_summary_no_competencies_duplication(resume_display_text: str) -> tuple[bool, str | None]:
    low = resume_display_text.lower()
    forbidden = (
        "engineering & platform competencies",
        "platform competencies:",
        "competencies section",
        "category_label",
    )
    hits = [p for p in forbidden if p in low]
    if hits:
        return False, f"competencies section duplication markers: {hits}"
    return True, None


def check_exec_summary_no_certifications_section_duplication(resume_display_text: str) -> tuple[bool, str | None]:
    low = resume_display_text.lower()
    if "certifications & credentials" in low or "certifications and credentials section" in low:
        return False, "certifications section heading duplicated in executive summary"
    return True, None


def check_prompt_template_authority(
    artifacts_dir: Path | None,
    *,
    expected_template_ref: str = EXPECTED_PROMPT_TEMPLATE_REF,
    expected_prompt_id: str = EXPECTED_PROMPT_ID,
) -> tuple[bool, str | None]:
    if artifacts_dir is None:
        return False, "artifacts_dir missing for prompt template authority"
    trace_path = artifacts_dir / "prompt_selection_trace.json"
    artifact_path = artifacts_dir / "compiled_prompt_artifact.json"
    if not trace_path.is_file():
        return False, "prompt_selection_trace.json missing"
    try:
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"prompt_selection_trace unreadable: {exc}"
    if not isinstance(trace, dict):
        return False, "prompt_selection_trace must be object"
    ref = str(
        trace.get("apps_rg_prompt_template_ref") or trace.get("contract_template_ref") or ""
    ).strip()
    prompt_id = str(trace.get("prompt_id") or "").strip()
    shell_id = str(trace.get("compiler_template_id") or trace.get("selected_template_id") or "").strip()
    if ref != expected_template_ref:
        return False, f"apps_rg_prompt_template_ref {ref!r} != expected {expected_template_ref!r}"
    if prompt_id != expected_prompt_id and not prompt_id.endswith(expected_prompt_id):
        return False, f"prompt_id {prompt_id!r} != expected {expected_prompt_id!r}"
    if shell_id and shell_id != EXPECTED_PA_SHELL_TEMPLATE_ID:
        return False, f"PA shell template_id {shell_id!r} != expected {EXPECTED_PA_SHELL_TEMPLATE_ID!r}"
    if artifact_path.is_file():
        try:
            art = json.loads(artifact_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):  # guardian: allow-pass -- optional cross-check
            art = None
        if isinstance(art, dict):
            art_ref = str(
                art.get("apps_rg_prompt_template_ref") or art.get("contract_template_ref") or ""
            ).strip()
            if art_ref and art_ref != expected_template_ref:
                return False, f"compiled_prompt_artifact ref mismatch: {art_ref!r}"
            art_prompt = str(art.get("selected_template_id") or art.get("compiler_template_id") or "").strip()
            if art_prompt and art_prompt != EXPECTED_PA_SHELL_TEMPLATE_ID:
                return False, f"compiled_prompt_artifact shell {art_prompt!r} != {EXPECTED_PA_SHELL_TEMPLATE_ID!r}"
    return True, None


def _resume_word_count(resume_display_text: str) -> int:
    return len(re.findall(r"\S+", str(resume_display_text or "").strip()))


def _graph_evidence_lane_no_commercial_org_cred(s: str, label: str) -> str | None:
    """Shared S2/S3 lane: no $, revenue, margin, org scale, credential language, credential-led openers."""
    sl = s.lower()
    if "$" in s:
        return f"{label}: $ forbidden"
    if re.search(r"\brevenue\b", sl):
        return f"{label}: revenue forbidden"
    if re.search(r"\b(margin|margins)\b", sl):
        return f"{label}: margin language forbidden"
    if re.search(r"\b8\s+to\s+28\b", sl):
        return f"{label}: team span 8-to-28 forbidden"
    if "specialist" in sl:
        return f"{label}: specialist/team-scale language forbidden"
    if re.search(r"\bfellow\b", sl):
        return f"{label}: Fellow/credential language forbidden"
    if "certification" in sl or re.search(r"\bcertified\b", sl):
        return f"{label}: certification language forbidden"
    st = s.strip()
    if not st:
        return f"{label}: empty"
    for bad_start in ("fellow of", "holds", "certified", "credentials"):
        if st.lower().startswith(bad_start):
            return f"{label}: must not start with credential-led opener {bad_start!r}"
    return None


def _graph_evidence_outcomes_sentence_opener_ok(s: str) -> str | None:
    """Outcomes (or combined outcomes+cred) sentence must not lead with credential inventory."""
    st = s.strip()
    if not st:
        return "outcomes sentence empty"
    sl = st.lower()
    for bad_start in ("fellow of", "holds", "certified", "credentials"):
        if sl.startswith(bad_start):
            return f"outcomes sentence must not lead with {bad_start!r}"
    return None


def _graph_evidence_credibility_sentence_opener_ok(s: str) -> str | None:
    st = s.strip()
    if not st:
        return "credibility sentence empty"
    sl = st.lower()
    if sl.startswith("holds certifications"):
        return "S5 must not start with Holds certifications"
    if sl.startswith("credentials"):
        return "S5 must not start with Credentials"
    return None


# Graph-evidence structural gate: six-sentence arc (thesis / mechanism / lifecycle / bridge / outcomes / credibility).
_GRAPH_EVIDENCE_S1_CONNECTOR_PHRASES = (
    "to improve",
    "to reduce",
    "to streamline",
)
_GRAPH_EVIDENCE_S1_CONNECTOR_WORDS = (
    "integrating",
    "combining",
    "through",
    "while",
)
_GRAPH_EVIDENCE_S1_MECHANISM_TERMS = (
    "microservices",
    "hpc",
    "vector services",
    "routing",
    "orchestration",
    "retrieval",
    "pipelines",
)


def check_graph_evidence_sentence_responsibility_shape(
    resume_display_text: str,
    proof_pool_metadata: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    """Graph painting-plan sentence arc."""
    from apps_rg.runtime.sections.executive_summary_composition import (
        check_graph_painting_sentence_responsibility_shape,
    )

    return check_graph_painting_sentence_responsibility_shape(
        resume_display_text, proof_pool_metadata
    )


def _exec_summary_painting_mode_active(
    proof_pool_metadata: dict[str, Any] | None = None,
) -> bool:
    return isinstance(proof_pool_metadata, dict) and bool(
        proof_pool_metadata.get("graph_skills_proof_pool")
    )


def _claim_row_uses_resume_fact_id(fid: str) -> bool:
    s = str(fid or "").strip()
    if not s:
        return False
    if s.upper() == "JD_ONLY":
        return False
    base = s.split("_metric_", 1)[0] if "_metric_" in s else s
    return base.startswith("fact_")


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
    defer_x1d_gates: bool = False,
    target_role: str | None = None,
    selected_facts: list[dict[str, Any]] | None = None,
    proof_pool_metadata: dict[str, Any] | None = None,
    proof_pool_ref: str = "",
    proof_pool_digest: str = "",
) -> list[X2GateResult]:
    gates: list[X2GateResult] = []
    artifacts_dir = artifacts_dir or Path("artifacts/apps_rg/runtime_proofs/executive_summary")

    def add(gate_id: str, passed: bool, observed: Any, threshold: Any, reason: str | None = None) -> None:
        gates.append(X2GateResult(gate_id, "deterministic", passed, observed, threshold, None if passed else reason, gate_id))

    # Existing gates
    add("x2_schema_valid", parsed_output is not None, parsed_output is not None, True, "Model output did not parse to expected JSON object.")
    from apps_rg.runtime.sections.executive_summary_pa import is_strategy_executive_target_title

    strategy_lane = is_strategy_executive_target_title(str(target_role or ""))
    if strategy_lane:
        thesis_ok, thesis_reason = check_executive_strategy_thesis(parsed_output)
        add(
            "x2_executive_strategy_thesis_present",
            thesis_ok,
            (parsed_output or {}).get("executive_strategy_thesis") if parsed_output else None,
            "non_empty_thesis",
            thesis_reason,
        )
    add("x2_claim_ledger_present", bool(claim_ledger), len(claim_ledger), ">0", "claim_ledger is empty or missing.")
    add("x2_sentence_coverage_present", bool(text_claim_coverage.get("sentences")), len(text_claim_coverage.get("sentences", [])), ">0", "text_claim_coverage missing.")
    add("x2_sentence_coverage_pass", text_claim_coverage.get("overall_pass") is True, text_claim_coverage.get("overall_pass"), True, "One or more displayed sentences lack supported claims.")

    self_check_ok, self_check_reason = check_self_check_claim_ledger_consistent(
        parsed_output, text_claim_coverage
    )
    add(
        "x2_self_check_claim_ledger_consistent",
        self_check_ok,
        self_check_reason or "ok",
        "self_check_implies_coverage_pass",
        self_check_reason,
    )
    # Ledger/display parity gates are lane-agnostic rigor invariants (row count == sentence
    # count; each ledger claim materializes in the display body). They are listed as
    # rigor-critical for the lane in section_product_shape_ssot, so they must be emitted on
    # EVERY lane — not only the strategy-executive lane — otherwise the rigor convergence audit
    # injects a deterministic ``rigor_critical_gate_missing_from_runtime_bundle`` BLOCK for any
    # non-strategy target title (e.g. "VP, Global Head of Agentic AI Solutions").
    row_count_ok, row_count_reason = check_claim_ledger_row_count_matches_sentence_count(
        resume_display_text, claim_ledger
    )
    add(
        "x2_claim_ledger_row_count_matches_sentence_count",
        row_count_ok,
        row_count_reason or "ok",
        "sentences_eq_ledger_rows",
        row_count_reason,
    )
    claim_map_ok, claim_map_reason = check_claim_field_maps_to_display_sentence(
        resume_display_text, claim_ledger
    )
    add(
        "x2_claim_field_maps_to_display_sentence",
        claim_map_ok,
        claim_map_reason or "ok",
        "each_claim_in_display",
        claim_map_reason,
    )
    if strategy_lane:
        from apps_rg.runtime.sections.executive_summary_operator_reporting import (
            check_exec_summary_s5_no_derivatives_inventory,
            check_self_check_s5_no_derivatives_inventory,
        )

        s5_inv_ok, s5_inv_reason = check_exec_summary_s5_no_derivatives_inventory(
            resume_display_text,
            allowed_fact_ids=allowed_fact_ids,
            selected_facts=selected_facts,
        )
        add(
            "x2_exec_summary_s5_no_derivatives_inventory",
            s5_inv_ok,
            s5_inv_reason or "ok",
            "no_derivatives_inventory_without_hpc_metric",
            s5_inv_reason,
        )
        s5_sc_ok, s5_sc_reason = check_self_check_s5_no_derivatives_inventory(
            parsed_output,
            resume_display_text,
            allowed_fact_ids=allowed_fact_ids,
            selected_facts=selected_facts,
        )
        add(
            "x2_self_check_s5_no_derivatives_inventory",
            s5_sc_ok,
            s5_sc_reason or "ok",
            "self_check_s5_derivatives_consistent",
            s5_sc_reason,
        )

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
    jd_proof_ok, jd_proof_reason = check_exec_summary_jd_alignment_proof_flags(parsed_output)
    add(
        "x2_exec_summary_jd_alignment_proof_flags",
        jd_proof_ok,
        (parsed_output or {}).get("jd_alignment") if isinstance(parsed_output, dict) else "missing",
        "targeting_only_true_and_proof_flags_false",
        jd_proof_reason,
    )
    add("x2_em_dash_count_zero", EM_DASH not in resume_display_text, resume_display_text.count(EM_DASH), 0, "Em dash found.")
    add("x2_inline_source_tags_absent", not INLINE_SOURCE_PATTERN.search(resume_display_text), bool(INLINE_SOURCE_PATTERN.search(resume_display_text)), False, "Inline source/citation tag leaked into resume display text.")
    para_max_ok, para_max_reason = check_exec_summary_paragraph_max_words(
        resume_display_text, parsed_output
    )
    add(
        "x2_exec_summary_paragraph_max_words",
        para_max_ok,
        para_max_reason or "ok",
        f"max_{EXEC_SUMMARY_MAX_WORDS}_words",
        para_max_reason,
    )
    bloated_ok, bloated_reason = check_exec_summary_no_bloated_sentence(resume_display_text)
    add(
        "x2_exec_summary_no_bloated_sentence",
        bloated_ok,
        bloated_reason or "ok",
        f"max_{EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE}_words_per_sentence",
        bloated_reason,
    )
    add("x2_no_monolithic_prompt", not monolithic_prompt_invoked, monolithic_prompt_invoked, False, "Monolithic prompt invoked.")
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
    sent6_ok, sent6_reason = check_exec_summary_sentence_count_6(resume_display_text)
    add(
        "x2_exec_summary_sentence_count_6",
        sent6_ok,
        sent6_reason or "ok",
        f"exactly_{EXEC_SUMMARY_MIN_SENTENCES}",
        sent6_reason,
    )
    roundtrip_ok, roundtrip_reason = check_exec_summary_display_roundtrip_integrity(
        resume_display_text
    )
    add(
        "x2_exec_summary_display_roundtrip_integrity",
        roundtrip_ok,
        roundtrip_reason or "ok",
        "split_join_and_no_control_chars",
        roundtrip_reason,
    )
    dedup_ok, dedup_reason = check_exec_summary_cross_sentence_metric_dedup(resume_display_text)
    add(
        "x2_exec_summary_cross_sentence_metric_dedup",
        dedup_ok,
        dedup_reason or "ok",
        "no_duplicate_high_signal_metrics",
        dedup_reason,
    )
    allowlist_ok, allowlist_reason = check_c03_selected_fact_ids_claimable_subset_allowed_fact_ids(
        allowed_fact_ids=allowed_fact_ids,
        proof_pool_metadata=proof_pool_metadata,
    )
    add(
        "x2_exec_summary_c03_selected_fact_ids_claimable_subset_allowed_fact_ids",
        allowlist_ok,
        allowlist_reason or "ok",
        "pool_wins_allowlist",
        allowlist_reason,
    )
    util_pool_ok, util_pool_reason, util_pool_receipt = check_exec_summary_allowed_fact_utilization(
        claim_ledger,
        allowed_fact_ids,
        text_claim_coverage=text_claim_coverage,
    )
    add(
        "x2_exec_summary_allowed_fact_utilization",
        util_pool_ok,
        util_pool_reason or "ok",
        "non_waived_allowed_facts_cited",
        util_pool_reason,
    )
    if isinstance(parsed_output, dict) and util_pool_receipt:
        parsed_output.setdefault("allowed_fact_utilization_receipt", util_pool_receipt)
    util_ok, util_reason = check_exec_summary_evidence_utilization(
        resume_display_text,
        parsed_output,
        selected_facts=selected_facts,
    )
    add(
        "x2_exec_summary_evidence_utilization",
        util_ok,
        util_reason or "ok",
        "structural_fact_weave",
        util_reason,
    )
    mech_ok, mech_reason = check_exec_summary_no_mechanism_inventory(
        resume_display_text, parsed_output
    )
    add(
        "x2_exec_summary_no_mechanism_inventory",
        mech_ok,
        mech_reason or "ok",
        "no_mechanism_dump",
        mech_reason,
    )
    cred_ok, cred_reason = check_exec_summary_no_credential_dump(resume_display_text)
    add(
        "x2_exec_summary_no_credential_dump",
        cred_ok,
        cred_reason or "ok",
        "no_credential_inventory_block",
        cred_reason,
    )
    frag_ok, frag_reason = check_exec_summary_no_sentence_fragment(resume_display_text)
    add(
        "x2_exec_summary_no_sentence_fragment",
        frag_ok,
        frag_reason or "ok",
        "no_grammatical_fragments",
        frag_reason,
    )
    override_ok, override_reason = check_exec_summary_display_override_compliance(
        resume_display_text,
        claim_ledger,
    )
    add(
        "x2_exec_summary_display_override_compliance",
        override_ok,
        override_reason or "ok",
        "display_override_anchor_present",
        override_reason,
    )
    comm_ok, comm_reason = check_exec_summary_strategy_no_commercialization_thread(
        resume_display_text,
        target_role=target_role,
    )
    add(
        "x2_exec_summary_strategy_no_commercialization_thread",
        comm_ok,
        comm_reason or "ok",
        "no_commercialization_identity_thread",
        comm_reason,
    )
    comp_dup_ok, comp_dup_reason = check_exec_summary_no_competencies_duplication(resume_display_text)
    add(
        "x2_exec_summary_no_competencies_duplication",
        comp_dup_ok,
        comp_dup_reason or "ok",
        "no_competencies_section_echo",
        comp_dup_reason,
    )
    cert_dup_ok, cert_dup_reason = check_exec_summary_no_certifications_section_duplication(
        resume_display_text
    )
    add(
        "x2_exec_summary_no_certifications_section_duplication",
        cert_dup_ok,
        cert_dup_reason or "ok",
        "no_certifications_heading_echo",
        cert_dup_reason,
    )
    prompt_auth_ok, prompt_auth_reason = check_prompt_template_authority(artifacts_dir)
    add(
        "x2_exec_summary_prompt_template_authority",
        prompt_auth_ok,
        prompt_auth_reason or "ok",
        EXPECTED_PROMPT_ID,
        prompt_auth_reason,
    )
    if _exec_summary_painting_mode_active(proof_pool_metadata):
        from apps_rg.runtime.sections.executive_summary_composition import (
            check_brushstroke_fact_support,
            check_composition_plan_present,
            check_dominant_brushstroke_coherence,
            check_graph_skill_coverage,
            check_human_exec_voice,
            check_mechanism_inventory_control,
            check_no_jd_keyword_stuffing_exec,
            resolve_composition_plan,
        )

        comp_plan = resolve_composition_plan(parsed_output, artifacts_dir=artifacts_dir)
        plan_ok, plan_reason = check_composition_plan_present(
            parsed_output,
            artifacts_dir=artifacts_dir,
            proof_pool_metadata=proof_pool_metadata,
        )
        add(
            "x2_exec_summary_composition_plan_present",
            plan_ok,
            plan_reason or "ok",
            "executive_summary_composition_plan.json",
            plan_reason,
        )
        bs_ok, bs_reason = check_brushstroke_fact_support(comp_plan, claim_ledger, allowed_fact_ids)
        add(
            "x2_exec_summary_brushstroke_fact_support",
            bs_ok,
            bs_reason or "ok",
            "brushstrokes_cite_allowed_facts",
            bs_reason,
        )
        gs_ok, gs_reason = check_graph_skill_coverage(comp_plan, parsed_output)
        add(
            "x2_exec_summary_graph_skill_coverage",
            gs_ok,
            gs_reason or "ok",
            "graph_skill_refs_when_claimed",
            gs_reason,
        )
        dom_ok, dom_reason = check_dominant_brushstroke_coherence(resume_display_text, comp_plan)
        add(
            "x2_exec_summary_dominant_brushstroke_coherence",
            dom_ok,
            dom_reason or "ok",
            "thesis_led_not_mechanism_inventory",
            dom_reason,
        )
        inv_ok, inv_reason = check_mechanism_inventory_control(resume_display_text)
        add(
            "x2_exec_summary_mechanism_inventory_control",
            inv_ok,
            inv_reason or "ok",
            "no_mechanism_dump",
            inv_reason,
        )
        voice_ok, voice_reason = check_human_exec_voice(resume_display_text)
        add(
            "x2_exec_summary_human_exec_voice",
            voice_ok,
            voice_reason or "ok",
            "credible_exec_prose",
            voice_reason,
        )
        jd_stuff_ok, jd_stuff_reason = check_no_jd_keyword_stuffing_exec(resume_display_text, jd_text)
        add(
            "x2_exec_summary_no_jd_keyword_stuffing",
            jd_stuff_ok,
            jd_stuff_reason or "ok",
            "no_jd_mirror_stuffing",
            jd_stuff_reason,
        )
    stacked, stack_reason, _ = detect_bullet_like_stacking(resume_display_text)
    add("x2_sentence_stacking_zero", not stacked, stack_reason, None, "Bullet-like sentence stacking detected.")
    
    # New synthesis quality gate
    synthesis_ok, synthesis_reason = check_synthesis_quality(resume_display_text)
    add("x2_executive_summary_synthesis_quality", synthesis_ok, synthesis_reason, None, synthesis_reason)

    mech_stack_ok, mech_stack_reason = check_exec_summary_mechanical_opener_stack(resume_display_text)
    add(
        "x2_exec_summary_mechanical_opener_stack_zero",
        mech_stack_ok,
        mech_stack_reason or "ok",
        None,
        mech_stack_reason,
    )
    if strategy_lane:
        stock_ok, stock_reason = check_exec_summary_stock_bridge_count(
            resume_display_text,
            max_bridges=2,
        )
        add(
            "x2_exec_summary_stock_bridge_max_two",
            stock_ok,
            stock_reason or "ok",
            "max_two_stock_bridges_in_s2_s5",
            stock_reason,
        )

    conf_ok, conf_reason = check_cross_fact_display_conflation(
        resume_display_text, claim_ledger
    )
    add(
        "x2_exec_summary_cross_fact_conflation_zero",
        conf_ok,
        conf_reason or "ok",
        None,
        conf_reason,
    )

    north_ok, north_reason = check_north_star_style_example_echo_unsupported(
        resume_display_text, selected_facts
    )
    add(
        "x2_north_star_style_echo_unsupported_zero",
        north_ok,
        north_reason or "ok",
        "no_unsupported_style_echo",
        north_reason,
    )

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

    # Source-sensitive phrase gate: emit only when selected_facts substrate is present (W4).
    if selected_facts:
        source_ok, source_reason = check_source_sensitive_phrases(resume_display_text, selected_facts)
        add("x2_source_sensitive_phrases_supported", source_ok, source_reason, None, source_reason)

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

    no_plan_echo_ok, no_plan_echo_reason = check_raw_json_no_selected_fact_plan_echo(raw_output)
    add(
        "x2_no_selected_fact_plan_model_echo",
        no_plan_echo_ok,
        no_plan_echo_reason or "ok",
        "no_model_plan_echo",
        no_plan_echo_reason,
    )

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

    pp_meta = proof_pool_metadata
    pp_x2_active = bool(pp_meta and str(pp_meta.get("proof_pool_type") or "").strip())
    if pp_x2_active:
        from apps_rg.runtime.sections import graph_evidence_contract as _graph_evidence
        from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
            evaluate_proof_pool_source_fact_gate,
            proof_pool_x2_gate_id,
        )

        coll_ex = _graph_evidence.collect_source_fact_ids_from_claim_ledger(claim_ledger)
        ok_ex, env_ex, fail_ex = evaluate_proof_pool_source_fact_gate(
            section_id="executive_summary",
            collected_ids=coll_ex,
            allowed_fact_ids=set(allowed_fact_ids),
            proof_pool_metadata=pp_meta,
            proof_pool_ref=proof_pool_ref,
            proof_pool_digest=proof_pool_digest,
        )
        add(
            proof_pool_x2_gate_id(
                "executive_summary",
                proof_pool_metadata=pp_meta,
                srfs_slice_gate_active=False,
            ),
            ok_ex,
            env_ex,
            "active_proof_pool_allowlist_exact",
            fail_ex,
        )

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
        provider_requested == "external_claude" and runtime_generation_status in ("MOCKED", "STUBBED")
    )
    add("x2_no_silent_mock_fallback", no_mock_fallback_ok, f"provider={provider_requested}, status={runtime_generation_status}", "no silent mock", "Silent mock or stub fallback detected.")

    stub_env_ok, stub_env_reason = check_transport_envelope_stub_false(artifacts_dir, provider_requested)
    add(
        "x2_qwen_provider_stub_transport_zero",
        stub_env_ok,
        stub_env_reason or "ok",
        "stub_transport_absent",
        stub_env_reason,
    )

    # Gate 14: x2_model_name_allowed — exercised only for qwen_vllm (REAL_LLM provider proof lane).
    qwen_proof_lane = str(provider_requested or "").strip().lower() == "external_claude"
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

    if not defer_x1d_gates:
        for gate_dict in append_executive_summary_x1d_x2_gate_dicts(
            x1d_judges=x1d_judges,
            artifacts_dir=artifacts_dir,
        ):
            add(
                gate_dict["gate_id"],
                gate_dict["pass"],
                gate_dict.get("observed_value"),
                gate_dict.get("threshold"),
                gate_dict.get("failure_reason"),
            )
    else:
        # Keep rigor-critical X1D wiring gate IDs present in the initial bundle so
        # convergence audit does not synthesize BLOCK rows when post-X2 judge refresh
        # is intentionally deferred/skipped (e.g. early hard deterministic fails).
        _defer_reason = "deferred_until_post_x2_judge_phase"
        add(
            "x2_x1d_required_judges_present",
            True,
            _defer_reason,
            "post_x2_judge_refresh",
            None,
        )
        add(
            "x2_x1d_raw_responses_written",
            True,
            _defer_reason,
            "post_x2_judge_refresh",
            None,
        )
        add(
            "x2_x1d_schema_valid",
            True,
            _defer_reason,
            "post_x2_judge_refresh",
            None,
        )
        add(
            "x2_x1d_judge_packet_hash_uniform",
            True,
            _defer_reason,
            "post_x2_judge_refresh",
            None,
        )

    from apps_rg.runtime.validators.section_input_usage_x2 import append_section_input_usage_x2_gates

    append_section_input_usage_x2_gates(
        gates,
        artifacts_dir=artifacts_dir,
        allowed_fact_ids=allowed_fact_ids,
        claim_ledger=claim_ledger,
        text_claim_coverage=text_claim_coverage,
    )

    return gates


def gates_pass(gates: list[X2GateResult]) -> bool:
    return all(g.pass_ for g in gates)


def failed_gate_ids(gates: list[X2GateResult]) -> list[str]:
    return [g.gate_id for g in gates if not g.pass_]
