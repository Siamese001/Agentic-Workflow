"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/integrations\gates\post_ens_resume_gates.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations\gates\post_ens_resume_gates is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/integrations\gates\post_ens_resume_gates.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """POST-ENS Resume Gates — Evaluate after ensemble selection.
# 
# Gates that run after the ensemble has selected a winner, before any write.
# W4 implements anti-fabrication and credential integrity gates.
# 
# Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W1, W4)
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
# from agentic_core.runtime_gates.builtins.candidate_acceptance_guard import (
#     CandidateAcceptanceGuard,
# )
# 
# _log = logging.getLogger("apps_rg.gates.post_ens")
# 
# 
# def candidate_acceptance_guard_callable(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """Core-owned: ensures rejected candidates are never written.
#     
#     Bridges apps_rg artifact format to core CandidateAcceptanceGuard.
#     """
#     return CandidateAcceptanceGuard.evaluate(artifact, context)
# 
# 
# def _extract_quantified_claims(text: str) -> list[dict[str, Any]]:
#     """Extract numeric claims from text for verification.
#     
#     Returns list of claims with number, context, and position.
#     """
#     # Pattern: number + surrounding context (±10 chars)
#     # Matches: $12M, 15%, 500 users, 3 years, etc.
#     pattern = r'(?i)(?:\$?\d+(?:\.\d+)?[\s]?[MKBkm]?(?:illion)?(?:\%|\s*(?:users?|customers?|years?|months?|days?|\%|percent|x|times?))?)'
#     
#     claims = []
#     for match in re.finditer(pattern, text):
#         claim_text = match.group(0)
#         start = max(0, match.start() - 15)
#         end = min(len(text), match.end() + 15)
#         context = text[start:end]
#         
#         claims.append({
#             "number": claim_text,
#             "context": context,
#             "position": match.start(),
#         })
#     
#     return claims
# 
# 
# def _extract_stated_tenure(text: str) -> list[int]:
#     """Extract stated years of experience from text.
#     
#     Matches patterns like "15+ years", "over 10 years", "8 years of experience"
#     """
#     patterns = [
#         r'(?i)(\d+)\+?\s*years?\s+(?:of\s+)?experience',
#         r'(?i)(\d+)\+?\s*years?\s+in',
#         r'(?i)over\s+(\d+)\s*years?',
#         r'(?i)(\d+)\+?\s*years?\s+building',
#     ]
#     
#     years = []
#     for pattern in patterns:
#         for match in re.finditer(pattern, text):
#             try:
#                 year = int(match.group(1))
#                 years.append(year)
#             except (ValueError, IndexError):
#                 continue
#     
#     return years
# 
# 
# def provenance_required_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W4: Quantified claims must have provenance sources.
#     
#     Anti-fabrication gate: any numeric claim in the text must be traceable
#     to a source in the master resume or company brief.
#     """
#     gate_id = "provenance_required"
#     
#     # Extract text from artifact
#     text = ""
#     if isinstance(artifact, dict):
#         text = artifact.get("text", "")
#     elif hasattr(artifact, "text"):
#         text = str(getattr(artifact, "text", ""))
#     
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for provenance check",
#             reason_codes=("missing_text",),
#         )
#     
#     # Extract quantified claims
#     claims = _extract_quantified_claims(text)
#     
#     if not claims:
#         # No quantified claims = nothing to verify (pass)
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason="No quantified claims requiring provenance",
#             reason_codes=("no_claims",),
#         )
#     
#     # Get provenance sources from context
#     provenance_sources = context.get("provenance_sources", [])
#     master_resume_text = context.get("master_resume_text", "")
#     
#     # Check each claim against sources
#     unverified_claims = []
#     verified_count = 0
#     
#     for claim in claims:
#         claim_num = claim["number"]
#         claim_context = claim["context"]
#         
#         # Check if claim number appears in any source
#         verified = False
#         
#         # Check master resume
#         if master_resume_text and claim_num.lower() in master_resume_text.lower():
#             verified = True
#         
#         # Check other provenance sources
#         for source in provenance_sources:
#             source_text = source.get("text", "") if isinstance(source, dict) else str(source)
#             if claim_num.lower() in source_text.lower():
#                 verified = True
#                 break
#         
#         if verified:
#             verified_count += 1
#         else:
#             unverified_claims.append(claim)
#     
#     # W4 strict: all claims must be verified
#     if unverified_claims:
#         _log.warning(
#             "[W4] %d unverified quantified claims: %s",
#             len(unverified_claims),
#             [c["number"] for c in unverified_claims[:3]],
#         )
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,
#             reason=f"{len(unverified_claims)} quantified claims lack provenance verification",
#             reason_codes=(
#                 "unverified_claims",
#                 f"count:{len(unverified_claims)}",
#                 f"claims:{[c['number'] for c in unverified_claims[:3]]}",
#             ),
#             evidence_refs=tuple(f"claim:{c['number']}" for c in unverified_claims[:5]),
#         )
#     
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason=f"All {verified_count} quantified claims have provenance",
#         reason_codes=("all_claims_verified", f"count:{verified_count}"),
#     )
# 
# 
# def figure_citation_verification_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W4: Numeric claims must appear in master_resume.
#     
#     Credential integrity gate: verifies that numeric figures cited in
#     generated text actually exist in the source master resume.
#     """
#     gate_id = "figure_citation_verification"
#     
#     # Extract text
#     text = ""
#     if isinstance(artifact, dict):
#         text = artifact.get("text", "")
#     elif hasattr(artifact, "text"):
#         text = str(getattr(artifact, "text", ""))
#     
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for citation verification",
#             reason_codes=("missing_text",),
#         )
#     
#     # Get master resume for verification
#     master_resume_text = context.get("master_resume_text", "")
#     if not master_resume_text:
#         # No master resume to verify against — cannot verify
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="master_resume_text not provided for verification",
#             reason_codes=("missing_master_resume", "verification_impossible"),
#         )
#     
#     # Extract numeric claims
#     claims = _extract_quantified_claims(text)
#     
#     if not claims:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason="No numeric citations to verify",
#             reason_codes=("no_citations",),
#         )
#     
#     # Verify each claim against master resume
#     fabricated_claims = []
#     verified_count = 0
#     
#     for claim in claims:
#         claim_num = claim["number"]
#         
#         # Normalize for comparison (remove spaces, lowercase)
#         normalized_claim = claim_num.lower().replace(" ", "")
#         normalized_resume = master_resume_text.lower().replace(" ", "")
#         
#         if normalized_claim in normalized_resume:
#             verified_count += 1
#         else:
#             fabricated_claims.append(claim)
#     
#     if fabricated_claims:
#         _log.error(
#             "[W4] %d fabricated claims not in master_resume: %s",
#             len(fabricated_claims),
#             [c["number"] for c in fabricated_claims[:3]],
#         )
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,
#             reason=f"{len(fabricated_claims)} numeric claims not found in master_resume (fabrication risk)",
#             reason_codes=(
#                 "fabricated_claims_detected",
#                 f"count:{len(fabricated_claims)}",
#             ),
#             evidence_refs=tuple(
#                 f"fabricated:{c['number']}" for c in fabricated_claims[:5]
#             ),
#         )
#     
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason=f"All {verified_count} numeric citations verified in master_resume",
#         reason_codes=("all_citations_verified", f"count:{verified_count}"),
#     )
# 
# 
# def tenure_accuracy_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W4: Prose-stated years must match computed years ±1.
#     
#     Credential integrity gate: verifies that stated years of experience
#     in generated text matches the actual computed years from work history.
#     """
#     gate_id = "tenure_accuracy"
#     
#     # Extract text
#     text = ""
#     if isinstance(artifact, dict):
#         text = artifact.get("text", "")
#     elif hasattr(artifact, "text"):
#         text = str(getattr(artifact, "text", ""))
#     
#     if not text:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="No text available for tenure check",
#             reason_codes=("missing_text",),
#         )
#     
#     # Get computed years from context
#     computed_years = context.get("computed_years_experience")
#     if computed_years is None:
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.UNKNOWN,
#             reason="computed_years_experience not provided",
#             reason_codes=("missing_computed_tenure",),
#         )
#     
#     # Extract stated years from text
#     stated_years = _extract_stated_tenure(text)
#     
#     if not stated_years:
#         # No stated years in text — nothing to verify
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.PASS,
#             reason="No stated years of experience in text",
#             reason_codes=("no_stated_tenure",),
#         )
#     
#     # Check each stated year against computed (±1 tolerance)
#     inaccurate_statements = []
#     
#     for stated in stated_years:
#         # Allow ±1 year tolerance for rounding
#         if abs(stated - computed_years) > 1:
#             inaccurate_statements.append({
#                 "stated": stated,
#                 "computed": computed_years,
#                 "delta": stated - computed_years,
#             })
#     
#     if inaccurate_statements:
#         _log.warning(
#             "[W4] Tenure inaccuracy: stated %s vs computed %s",
#             [s["stated"] for s in inaccurate_statements],
#             computed_years,
#         )
#         return GateVerdict(
#             gate_id=gate_id,
#             result=Result.FAIL,
#             reason=f"{len(inaccurate_statements)} tenure statements exceed ±1 year tolerance",
#             reason_codes=(
#                 "tenure_inaccuracy",
#                 f"stated:{inaccurate_statements[0]['stated']}",
#                 f"computed:{computed_years}",
#             ),
#             evidence_refs=tuple(
#                 f"stated:{s['stated']},computed:{s['computed']}" 
#                 for s in inaccurate_statements[:3]
#             ),
#         )
#     
#     return GateVerdict(
#         gate_id=gate_id,
#         result=Result.PASS,
#         reason=f"All stated tenure within ±1 year of computed {computed_years} years",
#         reason_codes=("tenure_accurate", f"computed:{computed_years}"),
#     )
# 
# 
# def anti_fabrication_composite_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
#     """W4: Composite anti-fabrication gate running all W4 checks.
#     
#     Convenience gate that runs provenance, citation, and tenure checks
#     and returns aggregated result.
#     """
#     gates = [
#         ("provenance", provenance_required_gate),
#         ("citation", figure_citation_verification_gate),
#         ("tenure", tenure_accuracy_gate),
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
#             gate_id="anti_fabrication_composite",
#             result=Result.FAIL,
#             reason=f"Anti-fabrication failures: {', '.join(f[0] for f in failures)}",
#             reason_codes=tuple(f"fail:{f[0]}" for f in failures),
#         )
#     
#     if unknowns and not passes:
#         return GateVerdict(
#             gate_id="anti_fabrication_composite",
#             result=Result.UNKNOWN,
#             reason=f"Anti-fabrication indeterminate: {', '.join(u[0] for u in unknowns)}",
#             reason_codes=tuple(f"unknown:{u[0]}" for u in unknowns),
#         )
#     
#     return GateVerdict(
#         gate_id="anti_fabrication_composite",
#         result=Result.PASS,
#         reason=f"Anti-fabrication passed: {len(passes)} checks",
#         reason_codes=tuple(f"pass:{p[0]}" for p in passes),
#     )
# 
# 
# __all__ = [
#     "candidate_acceptance_guard_callable",
#     "provenance_required_gate",
#     "figure_citation_verification_gate",
#     "tenure_accuracy_gate",
#     "anti_fabrication_composite_gate",
# ]
# 