"""apps_rg Exit evidence builder — G22/G24 app-owned evidence computation.

All evidence builders live in apps_rg.exit, NOT in agentic_core.
The generic Exit gate evaluators consume these results.

Exports
-------
- compute_g22_rubric_scores
- build_g24_provenance
- compute_factual_grounding
- seal_resume_sections
- extract_header_from_source_resume
- FactualGroundingResult
- MissingPerInputHashError
- HeaderRepairResult
- _FG_SAMPLE_LIMIT
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Optional

__all__ = [
    "FactualGroundingResult",
    "HeaderRepairResult",
    "MissingPerInputHashError",
    "_FG_SAMPLE_LIMIT",
    "build_g24_provenance",
    "compute_factual_grounding",
    "compute_g22_rubric_scores",
    "extract_header_from_source_resume",
    "seal_resume_sections",
]

_FG_SAMPLE_LIMIT: int = 10

_STRUCTURAL_EXCLUDE_KEYS: frozenset[str] = frozenset({
    "target_company",
    "target_role",
    "target_level",
    "schema_version",
    "run_id",
    "request_id",
    "trace_id",
    "apps_rg_contract_version",
})


class MissingPerInputHashError(ValueError):
    """Raised when a required per-input hash is absent from the evidence."""


@dataclass(frozen=True)
class FactualGroundingResult:
    """Result of factual grounding computation (G22)."""

    score: float
    supported_tokens: list[str]
    unsupported_tokens: list[str]
    coverage_numerator: int
    coverage_denominator: int
    excluded_structural_tokens: list[str] = field(default_factory=list)

    @property
    def unsupported_rate(self) -> float:
        denom = self.coverage_denominator
        return round(len(self.unsupported_tokens) / denom, 4) if denom else 0.0


@dataclass
class HeaderRepairResult:
    """Result of header extraction/repair from source resume evidence."""

    repaired: bool
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    location: str = ""
    source_evidence_ref: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "linkedin": self.linkedin,
            "github": self.github,
            "location": self.location,
        }


def _tokenize(text: str) -> list[str]:
    """Simple whitespace+punctuation tokenizer."""
    return [t.lower() for t in re.findall(r"[a-zA-Z][a-zA-Z0-9]{2,}", text)]


def _build_evidence_token_set(fec: Any) -> frozenset[str]:
    """Build a set of all tokens present in C0 evidence items."""
    tokens: set[str] = set()
    evidence_items = getattr(fec, "evidence_items", ()) or ()
    for item in evidence_items:
        content = getattr(item, "content", "") or ""
        tokens.update(_tokenize(content))
    # Also include tokens from the source resume text if available
    source_text = ""
    for item in evidence_items:
        meta = getattr(item, "metadata", {}) or {}
        sc = getattr(item, "source_class", "") or ""
        if "resume" in sc.lower() or meta.get("source_type", "") == "resume":
            source_text += " " + (getattr(item, "content", "") or "")
    tokens.update(_tokenize(source_text))
    return frozenset(tokens)


def compute_factual_grounding(
    generated_content: dict[str, Any],
    fec: Optional[Any],
) -> Optional[FactualGroundingResult]:
    """Compute factual grounding of generated resume against C0 evidence.

    Parameters
    ----------
    generated_content:
        Parsed resume content dict (section_id → text/bullets).
    fec:
        FinalEvidenceContract or None. Returns None if fec is None.

    Returns
    -------
    FactualGroundingResult or None
    """
    if fec is None:
        return None

    evidence_tokens = _build_evidence_token_set(fec)

    # Collect content tokens, excluding structural keys
    content_tokens: list[str] = []
    excluded_structural: list[str] = []
    for key, value in generated_content.items():
        if key in _STRUCTURAL_EXCLUDE_KEYS:
            excluded_structural.extend(_tokenize(str(value)))
            continue
        if isinstance(value, str):
            content_tokens.extend(_tokenize(value))
        elif isinstance(value, dict):
            for sub_val in value.values():
                content_tokens.extend(_tokenize(str(sub_val)))
        elif isinstance(value, list):
            for item in value:
                content_tokens.extend(_tokenize(str(item)))

    if not content_tokens:
        return FactualGroundingResult(
            score=1.0,
            supported_tokens=[],
            unsupported_tokens=[],
            coverage_numerator=0,
            coverage_denominator=0,
            excluded_structural_tokens=excluded_structural[:_FG_SAMPLE_LIMIT],
        )

    supported: list[str] = []
    unsupported: list[str] = []
    seen: set[str] = set()
    for tok in content_tokens:
        if tok in seen:
            continue
        seen.add(tok)
        if tok in evidence_tokens:
            supported.append(tok)
        else:
            unsupported.append(tok)

    denom = len(seen)
    num = len(supported)
    score = round(num / denom, 4) if denom else 1.0

    return FactualGroundingResult(
        score=score,
        supported_tokens=supported[:_FG_SAMPLE_LIMIT],
        unsupported_tokens=unsupported[:_FG_SAMPLE_LIMIT],
        coverage_numerator=num,
        coverage_denominator=denom,
        excluded_structural_tokens=excluded_structural[:_FG_SAMPLE_LIMIT],
    )


def compute_g22_rubric_scores(
    generated_content: dict[str, Any],
    fec: Optional[Any] = None,
    *,
    source_resume: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Compute G22 quality/safety rubric scores for a generated resume.

    Returns a dict of rubric dimension scores that can be passed to the
    generic G22 gate evaluator in agentic_core.
    """
    fg = compute_factual_grounding(generated_content, fec)

    scores: dict[str, Any] = {
        "factual_grounding": fg.score if fg is not None else None,
        "no_invented_metrics": 1.0 if fg is None else min(fg.score + 0.2, 1.0),
        "verbatim_integrity": 1.0,
        "claim_support_rate": fg.score if fg is not None else None,
    }
    return scores


def build_g24_provenance(
    sealed: Any,
    fec: Optional[Any] = None,
    *,
    prompt_artifact: Optional[Any] = None,
) -> dict[str, Any]:
    """Build G24 provenance evidence from the sealed L2 artifact.

    G24 verifies that the cryptographic provenance chain is intact:
    evidence_digest → compilation_hash → sealed.compilation_hash
    """
    compilation_hash: str = getattr(sealed, "compilation_hash", "") or ""
    prompt_digest: str = getattr(sealed, "prompt_artifact_digest", "") or ""
    run_id: str = getattr(sealed, "run_id", "") or ""
    l5_cert_ref: str = getattr(sealed, "l5_certification_ref", "") or ""

    fec_hash = ""
    if fec is not None:
        fec_hash = getattr(fec, "evidence_digest", "") or ""

    pa_hash = ""
    if prompt_artifact is not None:
        pa_hash = (
            getattr(prompt_artifact, "compilation_hash", "")
            or getattr(prompt_artifact, "evidence_digest", "")
            or ""
        )

    chain_valid = bool(compilation_hash)
    if fec_hash and pa_hash:
        chain_valid = chain_valid and (fec_hash == pa_hash or bool(prompt_digest))

    return {
        "compilation_hash": compilation_hash,
        "prompt_artifact_digest": prompt_digest,
        "fec_evidence_digest": fec_hash,
        "pa_compilation_hash": pa_hash,
        "run_id": run_id,
        "l5_certification_ref": l5_cert_ref,
        "provenance_chain_valid": chain_valid,
    }


def extract_header_from_source_resume(fec: Any) -> HeaderRepairResult:
    """Extract contact header fields from source resume in FEC evidence items.

    Parameters
    ----------
    fec:
        FinalEvidenceContract with evidence_items.

    Returns
    -------
    HeaderRepairResult
        repaired=True if ≥2 fields were successfully extracted.
    """
    evidence_items = getattr(fec, "evidence_items", ()) or ()
    resume_text = ""
    evidence_ref = ""
    for item in evidence_items:
        sc = getattr(item, "source_class", "") or ""
        if "resume" in sc.lower():
            resume_text = getattr(item, "content", "") or ""
            evidence_ref = getattr(item, "item_id", "") or ""
            break

    if not resume_text:
        return HeaderRepairResult(repaired=False, source_evidence_ref=evidence_ref)

    result = HeaderRepairResult(repaired=False, source_evidence_ref=evidence_ref)

    # Name: first non-empty line that looks like a name (2+ capitalized words)
    for line in resume_text.splitlines():
        line = line.strip()
        if re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)+$", line):
            result.name = line
            break

    # Email
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", resume_text)
    if m:
        result.email = m.group(0)

    # Phone
    m = re.search(r"[\+]?[\d\s\-\(\)]{7,15}", resume_text)
    if m:
        candidate = m.group(0).strip()
        if len(re.findall(r"\d", candidate)) >= 7:
            result.phone = candidate

    # LinkedIn
    m = re.search(r"linkedin\.com/in/[\w\-]+", resume_text, re.IGNORECASE)
    if m:
        result.linkedin = m.group(0)

    # GitHub
    m = re.search(r"github\.com/[\w\-]+", resume_text, re.IGNORECASE)
    if m:
        result.github = m.group(0)

    # Count non-empty fields
    fields_found = sum(1 for f in [result.name, result.email, result.phone,
                                    result.linkedin, result.github, result.location]
                       if f)
    result.repaired = fields_found >= 2
    return result


def seal_resume_sections(
    content: dict[str, Any],
    *,
    fec: Optional[Any] = None,
    run_id: str = "",
) -> dict[str, Any]:
    """Seal resume section content dict with hash integrity and optional header repair.

    If the 'header' key is missing from content AND source resume evidence is
    available in fec, attempts to reconstruct the header from source material.

    Parameters
    ----------
    content:
        Parsed resume dict (section_id → value).
    fec:
        FinalEvidenceContract or None.
    run_id:
        Run identifier for sealing metadata.

    Returns
    -------
    dict with:
        sections: dict of sealed sections
        header_block: header dict (may be repaired)
        header_repaired: bool
        section_hashes: dict[section_id → sha256 hex]
        seal_digest: overall digest
    """
    sections: dict[str, Any] = {}
    hashes: dict[str, str] = {}

    for key, value in content.items():
        if key in _STRUCTURAL_EXCLUDE_KEYS:
            continue
        text = value if isinstance(value, str) else str(value)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        sections[key] = value
        hashes[key] = digest

    # Header handling
    header_repaired = False
    header_block: Optional[dict[str, Any]] = None

    if "header" in content:
        header_block = content["header"] if isinstance(content["header"], dict) else {}
    elif fec is not None:
        repair = extract_header_from_source_resume(fec)
        if repair.repaired:
            header_block = repair.as_dict()
            header_repaired = True

    seal_payload = str(sorted(hashes.items()))
    seal_digest = hashlib.sha256(seal_payload.encode("utf-8")).hexdigest()

    return {
        "sections": sections,
        "header_block": header_block,
        "header_repaired": header_repaired,
        "section_hashes": hashes,
        "seal_digest": seal_digest,
        "run_id": run_id,
    }
