"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/integrations\gates\per_cand_resume_gates.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations\gates\per_cand_resume_gates is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/integrations\gates\per_cand_resume_gates.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """PER-CAND Resume Gates — Evaluate individual candidates.
# 
# Gates that run per ensemble candidate (before winner selection).
# W5 implements rigorous resume domain quality checks.
# 
# Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W5)
# """
# 
# from __future__ import annotations
# 
# import logging
# import re
# from typing import Any
# 
# from agentic_core.L5_safety.runtime_gates.types import Result
# from agentic_core.runtime_gates import GateVerdict
# 
# _log = logging.getLogger("apps_rg.gates.per_cand")
# 
# 
# # W5: Forbidden filler words and buzzwords
# FORBIDDEN_FILLERS = frozenset([
#     "synergy", "synergies", "synergistic",
#     "leverage", "leveraging", "leveraged",
#     "paradigm", "paradigms",
#     "thinking outside the box",
#     "low-hanging fruit",
#     "move the needle",
#     "boil the ocean",
#     "circle back",
#     "double-click",
#     "ecosystem", "ecosystems",
#     "disruptive", "disruption",
#     "innovative", "innovation"  # Context-dependent, flagged for review
# ])
# 
# 
# def _extract_text(artifact: Any) -> str:
#     """Extract text from artifact."""
#     if isinstance(artifact, dict):
#         return artifact.get("text", "")
#     elif hasattr(artifact, "text"):
#         return str(getattr(artifact, "text", ""))
#     return ""
# 
# 
# def _count_words(text: str) -> int:
#     """Count words in text."""
#     return len(text.split())
# 
# 
# def _split_sentences(text: str) -> list[str]:
#     """Split text into sentences."""
#     # Simple sentence splitting on .!? followed by space or end
#     sentences = re.split(r'[.!?]+\s+', text)
#     return [s.strip() for s in sentences if s.strip()]
# 
# 
# def _count_quantified_outcomes(text: str) -> int:
#     """Count numeric claims/outcomes in text."""
#     # Pattern: number with %, $, or unit
#     pattern = r'(?i)(?:\$?\d+(?:\.\d+)?[\s]?[MKBkm]?(?:illion)?(?:\%|\s*(?:users?|customers?|revenue?|savings?|percent|\%|x|times?))?)'
#     matches = re.findall(pattern, text)
#     return len(matches)
# 
# 
# def length_parity_strict_gate(
#     artifact: Any,
#     context: dict[str, Any],
#     *,
#     tolerance: float = 0.15,
#     tolerance_below: float | None = None,
#     tolerance_above: float | None = None,
# ) -> GateVerdict:
#     """W5: Word count within tolerance of base section length.
# 
#     Ensures generated text maintains similar length to source material,
#     preventing both over-expansion and excessive compression.
# 
#     W1 update: Supports asymmetric tolerance (e.g., -10%/+25% for exec_summary).
#     Backward compatible: if tolerance_below/tolerance_above not provided,
#     uses symmetric tolerance parameter (default ±15%).
#     """
#     gate_id = "length_parity_strict"
# 
#     text = _extract_text(artifact)
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for length check",
#             reason_codes=("missing_text",),
#         )
# 
#     # Get reference length from context (base section or seed)
#     reference_word_count = context.get("reference_word_count")
#     if reference_word_count is None:
#         # Try to get from seed text in context
#         seed_text = context.get("seed_text", "")
#         if seed_text:
#             reference_word_count = _count_words(seed_text)
# 
#     if reference_word_count is None or reference_word_count == 0:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No reference length available for parity check",
#             reason_codes=("missing_reference",),
#         )
# 
#     actual_word_count = _count_words(text)
# 
#     # W1: Support asymmetric tolerance (exec_summary: -10%/+25%)
#     tb = tolerance_below if tolerance_below is not None else tolerance
#     ta = tolerance_above if tolerance_above is not None else tolerance
# 
#     # Use round() to avoid floating point truncation issues
#     min_words = round(reference_word_count * (1 - tb))
#     max_words = round(reference_word_count * (1 + ta))
# 
#     if min_words <= actual_word_count <= max_words:
#         tolerance_str = f"-{tb*100:.0f}%/+{ta*100:.0f}%" if (tb != ta) else f"±{tolerance*100:.0f}%"
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason=f"Length parity: {actual_word_count} words (ref: {reference_word_count}, {tolerance_str})",
#             reason_codes=("length_within_tolerance", f"words:{actual_word_count}"),
#             evidence_refs=(
#                 f"reference:{reference_word_count}",
#                 f"actual:{actual_word_count}",
#                 f"range:[{min_words},{max_words}]",
#                 f"tolerance_below:{tb}",
#                 f"tolerance_above:{ta}",
#             ),
#         )
# 
#     _log.warning(
#         "[W5] Length parity fail: %d words (expected %d-%d)",
#         actual_word_count, min_words, max_words
#     )
# 
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.FAIL,
#         reason=f"Length outside tolerance: {actual_word_count} words (ref: {reference_word_count}, range: [{min_words},{max_words}])",
#         reason_codes=(
#             "length_outside_tolerance",
#             f"words:{actual_word_count}",
#             f"reference:{reference_word_count}",
#         ),
#         evidence_refs=(
#             f"reference:{reference_word_count}",
#             f"actual:{actual_word_count}",
#             f"min:{min_words}",
#             f"max:{max_words}",
#             f"tolerance_below:{tb}",
#             f"tolerance_above:{ta}",
#         ),
#     )
# 
# 
# def quantified_outcome_count_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W5: Exec summary must contain ≥2 numeric claims.
#     
#     Ensures executive summaries have concrete, measurable outcomes.
#     """
#     gate_id = "quantified_outcome_count"
#     
#     text = _extract_text(artifact)
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for outcome counting",
#             reason_codes=("missing_text",),
#         )
#     
#     outcome_count = _count_quantified_outcomes(text)
#     min_required = 2
#     
#     if outcome_count >= min_required:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason=f"Quantified outcomes: {outcome_count} (min: {min_required})",
#             reason_codes=("sufficient_outcomes", f"count:{outcome_count}"),
#             evidence_refs=(f"outcomes:{outcome_count}",),
#         )
#     
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.FAIL,
#         reason=f"Insufficient quantified outcomes: {outcome_count} (min: {min_required})",
#         reason_codes=(
#             "insufficient_outcomes",
#             f"count:{outcome_count}",
#             f"min_required:{min_required}",
#         ),
#         evidence_refs=(f"outcomes:{outcome_count}",),
#     )
# 
# 
# def target_company_name_absence_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W5: Prose must NOT contain target_company string.
#     
#     Prevents resume from appearing overly customized or contrived.
#     Authenticity guard — candidates should be positioned by capability,
#     not flattery.
#     """
#     gate_id = "target_company_name_absence"
#     
#     text = _extract_text(artifact)
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for company name check",
#             reason_codes=("missing_text",),
#         )
#     
#     target_company = context.get("target_company")
#     if not target_company:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="target_company not provided in context",
#             reason_codes=("missing_target_company",),
#         )
#     
#     # Case-insensitive check
#     text_lower = text.lower()
#     company_lower = target_company.lower()
#     
#     if company_lower in text_lower:
#         _log.warning(
#             "[W5] Target company name '%s' found in text",
#             target_company
#         )
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,
#             reason=f"Target company name '{target_company}' present in prose",
#             reason_codes=(
#                 "target_company_present",
#                 f"company:{target_company}",
#             ),
#             evidence_refs=(
#                 f"found:{target_company}",
#                 "violation:authenticity",
#             ),
#         )
#     
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason=f"Target company name '{target_company}' not found in prose",
#         reason_codes=("target_company_absent", f"company:{target_company}"),
#     )
# 
# 
# def forbidden_filler_strict_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W5: Reject candidates with banned buzzwords.
#     
#     Enforces professional, authentic language without clichés.
#     """
#     gate_id = "forbidden_filler_strict"
#     
#     text = _extract_text(artifact)
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for filler check",
#             reason_codes=("missing_text",),
#         )
#     
#     text_lower = text.lower()
#     violations = []
#     
#     for filler in FORBIDDEN_FILLERS:
#         if filler.lower() in text_lower:
#             violations.append(filler)
#     
#     if violations:
#         _log.warning(
#             "[W5] Forbidden fillers found: %s",
#             violations[:5]  # Log first 5
#         )
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,
#             reason=f"{len(violations)} forbidden buzzwords/fillers found",
#             reason_codes=(
#                 "forbidden_filler_found",
#                 f"count:{len(violations)}",
#                 f"examples:{violations[:3]}",
#             ),
#             evidence_refs=tuple(f"found:{v}" for v in violations[:5]),
#         )
#     
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason="No forbidden buzzwords or fillers found",
#         reason_codes=("no_forbidden_fillers",),
#     )
# 
# 
# def sentence_max_length_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W5: No sentence >40 words.
#     
#     Ensures readability and executive-appropriate brevity.
#     """
#     gate_id = "sentence_max_length"
#     
#     text = _extract_text(artifact)
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for sentence length check",
#             reason_codes=("missing_text",),
#         )
#     
#     max_words = 40
#     sentences = _split_sentences(text)
#     violations = []
#     
#     for i, sentence in enumerate(sentences):
#         word_count = len(sentence.split())
#         if word_count > max_words:
#             violations.append({
#                 "index": i,
#                 "words": word_count,
#                 "preview": sentence[:50] + "..." if len(sentence) > 50 else sentence,
#             })
#     
#     if violations:
#         _log.warning(
#             "[W5] %d sentences exceed %d words",
#             len(violations), max_words
#         )
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,
#             reason=f"{len(violations)} sentences exceed {max_words} words",
#             reason_codes=(
#                 "sentence_too_long",
#                 f"violations:{len(violations)}",
#             ),
#             evidence_refs=tuple(
#                 f"sentence:{v['index']},words:{v['words']}" for v in violations[:3]
#             ),
#         )
#     
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason=f"All {len(sentences)} sentences within {max_words} words",
#         reason_codes=("sentences_within_limit", f"count:{len(sentences)}"),
#     )
# 
# 
# def archetype_lead_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W5: Sentence 1 must contain archetype string.
# 
#     Ensures executive summary immediately establishes candidate archetype.
#     """
#     gate_id = "archetype_lead"
# 
#     text = _extract_text(artifact)
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for archetype check",
#             reason_codes=("missing_text",),
#         )
# 
#     archetype = context.get("archetype")
#     if not archetype:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="archetype not provided in context",
#             reason_codes=("missing_archetype",),
#         )
# 
#     sentences = _split_sentences(text)
#     if not sentences:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No sentences found in text",
#             reason_codes=("no_sentences",),
#         )
# 
#     first_sentence = sentences[0].lower()
#     archetype_lower = archetype.lower()
# 
#     # Check for archetype or synonyms
#     archetype_parts = archetype_lower.split()
#     found = any(part in first_sentence for part in archetype_parts if len(part) > 3)
# 
#     if found:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason=f"Archetype '{archetype}' found in opening sentence",
#             reason_codes=("archetype_present", f"archetype:{archetype}"),
#         )
# 
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.FAIL,
#         reason=f"Opening sentence lacks archetype '{archetype}'",
#         reason_codes=(
#             "archetype_missing",
#             f"archetype:{archetype}",
#             f"first_sentence:{first_sentence[:50]}...",
#         ),
#         evidence_refs=(
#             f"expected:{archetype}",
#             f"actual:{first_sentence[:50]}",
#         ),
#     )
# 
# 
# # W1: New gates for exec_summary structural and provenance validation
# 
# 
# def structural_slot_coverage_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W1: Exec summary must contain 4 required structural slots.
# 
#     Required slots:
#     - archetype: opening establishes candidate archetype
#     - quantified_outcomes: at least one numeric claim (%, $, scale)
#     - engagement_model: consulting/operating mode description
#     - value_thesis: business value proposition
# 
#     Uses keyword heuristics to detect slot presence.
#     """
#     gate_id = "structural_slot_coverage"
# 
#     text = _extract_text(artifact)
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for structural slot check",
#             reason_codes=("missing_text",),
#         )
# 
#     text_lower = text.lower()
#     sentences = _split_sentences(text)
# 
#     # Detect slots using keyword heuristics
#     slots = {
#         "archetype": False,
#         "quantified_outcomes": False,
#         "engagement_model": False,
#         "value_thesis": False,
#     }
# 
#     # Slot 1: archetype - first sentence should contain role/archetype keywords
#     # Archetype is checked separately by archetype_lead_gate; we'll use a lighter check here
#     archetype_keywords = ["leader", "executive", "svp", "vp", "director", "head", "chief", "officer", "president"]
#     if sentences:
#         first_lower = sentences[0].lower()
#         if any(kw in first_lower for kw in archetype_keywords):
#             slots["archetype"] = True
# 
#     # Slot 2: quantified_outcomes - numeric patterns (% $ M B K numbers)
#     if _count_quantified_outcomes(text) >= 1:
#         slots["quantified_outcomes"] = True
# 
#     # Slot 3: engagement_model - consulting/operating model keywords
#     engagement_keywords = [
#         "consulting", "advisory", "engagement", "partnership", "operating", "delivery",
#         "model", "approach", "method", "framework", "practice", "methodology"
#     ]
#     if any(kw in text_lower for kw in engagement_keywords):
#         slots["engagement_model"] = True
# 
#     # Slot 4: value_thesis - business value keywords
#     value_keywords = [
#         "value", "growth", "revenue", "profit", "savings", "efficiency", "roi",
#         "return", "impact", "outcome", "result", "transformation", "scale"
#     ]
#     if any(kw in text_lower for kw in value_keywords):
#         slots["value_thesis"] = True
# 
#     missing = [s for s, present in slots.items() if not present]
# 
#     if not missing:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason=f"All 4 structural slots present: {', '.join(slots.keys())}",
#             reason_codes=("structural_complete", f"slots:{len(slots)}"),
#             evidence_refs=tuple(f"slot:{s}=present" for s in slots.keys()),
#         )
# 
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.FAIL,
#         reason=f"Missing structural slots: {', '.join(missing)}",
#         reason_codes=("structural_incomplete", f"missing:{','.join(missing)}"),
#         evidence_refs=tuple(f"slot:{s}={'present' if present else 'missing'}" for s, present in slots.items()),
#     )
# 
# 
# def unsupported_appended_claim_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W1: Repaired candidates must have provenance for appended content.
# 
#     When a candidate is repaired via deterministic expansion (appending a
#     marquee outcome), the appended sentence must have provenance refs.
#     Prevents padding with unsupported claims.
#     """
#     gate_id = "unsupported_appended_claim"
# 
#     # If no repair was applied, gate passes silently
#     repair_applied = context.get("repair_applied", False)
#     if not repair_applied:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason="No repair applied — no appended claim to validate",
#             reason_codes=("no_repair",),
#         )
# 
#     # Repair was applied — check for provenance
#     appended_refs = context.get("appended_sentence_source_refs", [])
#     if not appended_refs:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,
#             reason="Repair applied but no provenance refs for appended content",
#             reason_codes=("missing_provenance", "appended_claim_unsupported"),
#             evidence_refs=("repair_applied:true", "provenance_refs:empty"),
#         )
# 
#     # Validate that refs point to allowed sources
#     allowed_sources = {"marquee_outcomes", "master_bullets", "validated_facts"}
#     source_types = {ref.split(":")[0] for ref in appended_refs if ":" in ref}
#     invalid_sources = source_types - allowed_sources
# 
#     if invalid_sources:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,
#             reason=f"Appended claim has invalid source types: {', '.join(invalid_sources)}",
#             reason_codes=("invalid_provenance", f"invalid:{','.join(invalid_sources)}"),
#             evidence_refs=tuple(f"ref:{r}" for r in appended_refs[:5]),
#         )
# 
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason=f"Appended claim has valid provenance ({len(appended_refs)} refs)",
#         reason_codes=("provenance_valid", f"refs:{len(appended_refs)}"),
#         evidence_refs=tuple(f"ref:{r}" for r in appended_refs[:5]),
#     )
# 
# 
# def per_cand_quality_composite_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W5: Composite PER-CAND gate running all W5 checks.
#     
#     Aggregated quality check for ensemble candidate evaluation.
#     """
#     gates = [
#         ("length_parity", length_parity_strict_gate),
#         ("quantified_outcomes", quantified_outcome_count_gate),
#         ("target_company_absent", target_company_name_absence_gate),
#         ("forbidden_filler", forbidden_filler_strict_gate),
#         ("sentence_length", sentence_max_length_gate),
#         ("archetype_lead", archetype_lead_gate),
#     ]
#     
#     failures = []
#     passes = []
#     unknowns = []
#     
#     for name, gate_fn in gates:
#         verdict = gate_fn(artifact, context)
#         if verdict.result == Result.FAIL:
#             failures.append((name, verdict))
#         elif verdict.result == Result.PASS:
#             passes.append((name, verdict))
#         else:
#             unknowns.append((name, verdict))
#     
#     # Composite result
#     if failures:
#         return GateVerdict(
#             gate_id="per_cand_quality_composite",
#             result=Result.FAIL,
#             reason=f"PER-CAND quality failures: {', '.join(f[0] for f in failures)}",
#             reason_codes=tuple(f"fail:{f[0]}" for f in failures),
#         )
#     
#     if unknowns and not passes:
#         return GateVerdict(
#             gate_id="per_cand_quality_composite",
#             result=Result.UNKNOWN,
#             reason=f"PER-CAND quality indeterminate: {', '.join(u[0] for u in unknowns)}",
#             reason_codes=tuple(f"unknown:{u[0]}" for u in unknowns),
#         )
#     
#     return GateVerdict(
#         gate_id="per_cand_quality_composite",
#         result=Result.PASS,
#         reason=f"PER-CAND quality passed: {len(passes)} checks",
#         reason_codes=tuple(f"pass:{p[0]}" for p in passes),
#     )
# 
# 
# def tail_repetition_detected_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """Deferred scope: Detect tail repetition from vLLM min_tokens hard floor.
# 
#     W3 monitoring: Post-hoc gate to detect when vLLM min_tokens produces
#     repetitive output. This is a MONITORING gate, not a hard block.
# 
#     Returns WARNING if repetition detected for telemetry/alerting.
#     """
#     from collections import Counter
# 
#     gate_id = "tail_repetition_detected"
#     text = _extract_text(artifact)
# 
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text for repetition analysis",
#             reason_codes=("missing_text",),
#         )
# 
#     words = text.lower().split()
#     if len(words) < 30:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason="Text too short for tail repetition detection",
#             reason_codes=("short_text", "no_tail"),
#         )
# 
#     # Analyze last 30 tokens
#     last_30 = words[-30:]
#     trigrams = [" ".join(last_30[i:i+3]) for i in range(len(last_30) - 2)]
#     trigram_counts = Counter(trigrams)
#     max_count = max(trigram_counts.values()) if trigrams else 0
# 
#     if max_count >= 3:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,  # FAIL for monitoring purposes (not blocking)
#             reason=f"Severe tail repetition detected (trigram count={max_count})",
#             reason_codes=(
#                 "tail_repetition",
#                 f"max_trigram:{max_count}",
#                 "vllm_min_tokens_side_effect",
#             ),
#             evidence_refs=(f"last_30:{ ' '.join(last_30[-10:]) }",),
#         )
# 
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason="No significant tail repetition detected",
#         reason_codes=("no_repetition", f"max_trigram:{max_count}"),
#     )
# 
# 
# # Deferred scope: VLLM rollback trigger infrastructure
# VLLM_ROLLBACK_STATE: dict[str, Any] = {
#     "repetition_count": 0,
#     "total_checked": 0,
#     "rollback_triggered": False,
#     "last_rollback_at": None,
# }
# """Tracks repetition rate for VLLM min_tokens rollback decision."""
# 
# 
# def check_vllm_rollback_trigger(
#     repetition_detected: bool,
#     threshold: float = 0.05,
#     window_size: int = 100,
# ) -> dict[str, Any]:
#     """Deferred scope: Check if VLLM min_tokens should be rolled back.
# 
#     W3 monitoring: Tracks repetition rate across production runs.
#     If rate exceeds threshold (default 5%), triggers rollback to W1+W2 stack.
# 
#     Args:
#         repetition_detected: Whether current candidate showed repetition
#         threshold: Repetition rate threshold for rollback (default 0.05 = 5%)
#         window_size: Rolling window size for rate calculation
# 
#     Returns:
#         Dict with rollback decision and current rate
#     """
#     global VLLM_ROLLBACK_STATE
# 
#     VLLM_ROLLBACK_STATE["total_checked"] += 1
#     if repetition_detected:
#         VLLM_ROLLBACK_STATE["repetition_count"] += 1
# 
#     # Compute rolling rate (simplified; production would use deque)
#     total = VLLM_ROLLBACK_STATE["total_checked"]
#     count = VLLM_ROLLBACK_STATE["repetition_count"]
# 
#     # For rolling window, cap at window_size
#     if total > window_size:
#         # Simplified: just use total rate (production: use collections.deque)
#         rate = count / total if total > 0 else 0.0
#     else:
#         rate = count / total if total > 0 else 0.0
# 
#     should_rollback = rate > threshold and not VLLM_ROLLBACK_STATE["rollback_triggered"]
# 
#     if should_rollback:
#         VLLM_ROLLBACK_STATE["rollback_triggered"] = True
#         VLLM_ROLLBACK_STATE["last_rollback_at"] = VLLM_ROLLBACK_STATE["total_checked"]
#         _log.warning(
#             "[DEFERRED SCOPE] VLLM min_tokens rollback triggered! "
#             f"Repetition rate {rate*100:.1f}% > threshold {threshold*100:.1f}%"
#         )
# 
#     return {
#         "repetition_rate": round(rate, 4),
#         "repetition_rate_percent": f"{rate*100:.2f}%",
#         "should_rollback": should_rollback,
#         "already_rolled_back": VLLM_ROLLBACK_STATE["rollback_triggered"],
#         "window_checked": total,
#         "window_repetitions": count,
#     }
# 
# 
# def reset_vllm_rollback_state() -> None:
#     """Reset VLLM rollback state (for testing or re-enable after fix)."""
#     global VLLM_ROLLBACK_STATE
#     VLLM_ROLLBACK_STATE = {
#         "repetition_count": 0,
#         "total_checked": 0,
#         "rollback_triggered": False,
#         "last_rollback_at": None,
#     }
#     _log.info("[DEFERRED SCOPE] VLLM rollback state reset")
# 
# 
# def first_person_lead_ban_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W4: Ban first-person leading verbs in exec_summary.
# 
#     Recruiters expect 3rd-person executive voice.
#     Rejects candidates starting with "I have", "I am", "I specialize", etc.
# 
#     Args:
#         artifact: The generated text artifact
#         context: Gate context (may contain 'banned_leads' override)
# 
#     Returns:
#         GateVerdict: PASS if no first-person lead, FAIL if found
#     """
#     gate_id = "first_person_lead_ban"
# 
#     text = _extract_text(artifact)
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for first-person check",
#             reason_codes=("missing_text",),
#         )
# 
#     # Get first sentence
#     sentences = _split_sentences(text)
#     if not sentences:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason="No sentences to check",
#             reason_codes=("no_sentences",),
#         )
# 
#     first_sentence = sentences[0].strip()
#     first_lower = first_sentence.lower()
# 
#     # Default banned first-person leads (can be overridden via context)
#     banned_leads = context.get(
#         "banned_first_person_leads",
#         [
#             "i have ",
#             "i am ",
#             "i'm ",
#             "i specialize",
#             "i bring ",
#             "i offer ",
#             "i deliver ",
#             "i lead ",
#             "i managed ",
#             "i worked ",
#             "my experience",
#             "my background",
#             "my expertise",
#         ],
#     )
# 
#     for banned in banned_leads:
#         if banned.lower() in first_lower:
#             return GateVerdict(
#                 gate_id=gate_id,
#                 result=Result.FAIL,
#                 reason=f"First sentence uses first-person lead: '{banned.strip()}'",
#                 reason_codes=(
#                     "first_person_lead",
#                     f"lead:{banned.strip()}",
#                     "voice:expect_3rd_person",
#                 ),
#                 evidence_refs=(f"first_sentence:{first_sentence[:60]}",),
#             )
# 
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason="First sentence uses 3rd-person executive voice",
#         reason_codes=("third_person_voice", "executive_tone"),
#     )
# 
# 
# __all__ = [
#     "length_parity_strict_gate",
#     "quantified_outcome_count_gate",
#     "target_company_name_absence_gate",
#     "forbidden_filler_strict_gate",
#     "sentence_max_length_gate",
#     "archetype_lead_gate",
#     "structural_slot_coverage_gate",  # W1
#     "unsupported_appended_claim_gate",  # W1
#     "first_person_lead_ban_gate",  # W4
#     "tail_repetition_detected_gate",  # Deferred scope: W3 monitoring
#     "check_vllm_rollback_trigger",  # Deferred scope: W3 rollback
#     "reset_vllm_rollback_state",  # Deferred scope: W3 reset
#     "VLLM_ROLLBACK_STATE",  # Deferred scope: rollback state
#     "per_cand_quality_composite_gate",
# ]
# 