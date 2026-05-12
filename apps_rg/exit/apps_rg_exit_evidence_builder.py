"""apps_rg-owned exit evidence builders for G22 and G24 gate evaluation.

These functions encapsulate all resume-generation-specific evidence
construction.  Core agentic_core code MUST NOT reference resume rubric
concepts, ATS readability, jd_hash, resume_hash, or target_role_spec_hash.

The evidence dicts produced here are passed unchanged into the generic
ExitGateHarness.evaluate() call in agentic_core/runtime/exit/apps_rg_exit_binding.py.

No apps_rg-specific terms appear in any generic core contract as a result of
this module.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.runtime.contracts.compiled_prompt_artifact import (
        CompiledPromptArtifact,
    )
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.runtime.contracts.sealed_workflow_types import SealedSectionArtifact

# ── Section key mapping: L2 flat output → canonical G21 section IDs ──────────
# Only keys that have a canonical equivalent are mapped.
# header_block is NOT synthesised from target_* fields — omitted if absent.
_SECTION_KEY_MAP: dict[str, str] = {
    "executive_summary": "professional_summary",
    "experience": "experience_block",
    "skills": "skills_block",
    "education": "education_block",
    "certifications": "certifications_block",
}

# Role-alignment keyword heuristic — broad coverage for executive IT roles.
# Scores keyword overlap between the professional_summary text and target_role.
_ROLE_KEYWORD_POOL = frozenset([
    "strategy", "strategic", "transformation", "innovation", "architecture",
    "enterprise", "platform", "governance", "leadership", "delivery",
    "technology", "digital", "ai", "data", "cloud", "executive", "svp", "vp",
    "director", "program", "portfolio", "roadmap", "stakeholder", "operating",
    "operational", "scalable", "modernization",
])

# Specificity: numeric evidence pattern (years, percentages, $, metrics)
_SPECIFICITY_PATTERN = re.compile(
    r"\b(\d+\+?\s*(?:years?|yrs?|months?|mos?)\b"
    r"|\d+\s*%"
    r"|\$\s*\d"
    r"|\b\d{4}\b"            # years like 2018
    r"|\b\d+[xX]\b"          # multipliers like 3x
    r"|\b\d+\s*(?:M|B|K)\b"  # dollar magnitudes
    r")",
    re.IGNORECASE,
)


def seal_resume_sections(
    content: "dict[str, Any] | None",
    run_id: str,
) -> "tuple[SealedSectionArtifact, ...]":
    """Map L2 flat output keys to canonical SealedSectionArtifact objects.

    Key mapping (L2 key → canonical section_id):
      executive_summary  → professional_summary
      experience         → experience_block
      skills             → skills_block
      education          → education_block
      certifications     → certifications_block  (only when present)

    Hard rule: header_block is NOT fabricated from target_company / target_role /
    target_level. It is only created from actual candidate identity data if present
    in a dedicated "header" / "contact" key. If that key is absent, header_block
    is omitted and G21 will correctly FAIL for that section.

    Each SealedSectionArtifact carries:
      - node_id:        canonical section ID
      - run_id:         threaded from the sealed artifact
      - sealed_content: JSON serialisation of the section value
      - content_digest: SHA-256 of sealed_content (hex)
      - app_context:    "apps_rg"
      - payload_ref:    pointer back to generated_resume.json section key

    Returns an empty tuple when content is None or empty.
    """
    if not content:
        return ()

    from agentic_core.runtime.contracts.sealed_workflow_types import (  # noqa: PLC0415
        SealedSectionArtifact,
    )

    sections: list[SealedSectionArtifact] = []

    # Map known L2 keys to canonical IDs.
    for l2_key, canonical_id in _SECTION_KEY_MAP.items():
        if l2_key not in content:
            continue
        section_value = content[l2_key]
        sealed_content = json.dumps(section_value, ensure_ascii=False)
        content_digest = hashlib.sha256(sealed_content.encode("utf-8")).hexdigest()
        sections.append(SealedSectionArtifact(
            node_id=canonical_id,
            run_id=run_id,
            app_context="apps_rg",
            sealed_content=sealed_content,
            content_digest=content_digest,
            payload_ref=f"generated_resume.json#{l2_key}",
        ))

    # header_block: only from explicit candidate header/contact data.
    # target_company / target_role / target_level are NOT used.
    header_src = content.get("header") or content.get("contact") or None
    if header_src and isinstance(header_src, dict):
        sealed_content = json.dumps(header_src, ensure_ascii=False)
        content_digest = hashlib.sha256(sealed_content.encode("utf-8")).hexdigest()
        sections.append(SealedSectionArtifact(
            node_id="header_block",
            run_id=run_id,
            app_context="apps_rg",
            sealed_content=sealed_content,
            content_digest=content_digest,
            payload_ref="generated_resume.json#header",
        ))

    return tuple(sections)


def compute_g22_rubric_scores(
    content: "dict[str, Any] | None",
    sealed: "SealedL2Artifact",
) -> dict[str, float]:
    """Compute deterministic per-dimension scores for G22 gate evaluation.

    Derives scores from structural properties of the generated resume JSON
    rather than relying on LLM judges.  All scores are in [0.0, 1.0].

    Returns {} when content is None (unparseable payload).

    Dimensions computed here:
    - format_compliance:    fraction of required top-level keys present (4 keys).
    - ats_readability:      1.0 when all chars are printable ASCII, else penalised.
    - no_fabrication:       1.0 unless content contains fabrication marker strings.
    - concision:            1.0 for <=1500 words; penalised linearly beyond that.
    - role_alignment:       keyword-overlap between professional_summary text and
                            known executive IT role terms.  Deterministic, no LLM.
    - specificity:          ratio of numeric evidence tokens to total words,
                            capped at 1.0.  Proxies verifiable claim density.
    - overall_pass_threshold: harmonic mean of the six deterministic dimensions.

    NOTE: factual_grounding is NOT computed here.
    It is computed separately by compute_factual_grounding() and merged into
    this dict by exit_finalize_apps_rg when a FinalEvidenceContract is available
    (grounded runs).  For generate_scratch runs (fec=None) the key stays absent
    and G22 evaluates UNKNOWN on that dimension.  Do NOT fake this score here.
    """
    if content is None:
        return {}

    # format_compliance: 4 required top-level keys for master_resume_v2 schema.
    required_keys = {"executive_summary", "experience", "education", "skills"}
    present_keys = required_keys & set(content.keys())
    format_compliance = len(present_keys) / len(required_keys)

    # ats_readability: penalise non-printable or non-ASCII chars.
    raw_text = json.dumps(content)
    non_ascii = sum(1 for c in raw_text if ord(c) > 127 or not c.isprintable())
    ats_readability = max(0.0, 1.0 - non_ascii / max(len(raw_text), 1))

    # no_fabrication: zero if any known fabrication marker found.
    _FABRICATION_MARKERS = ("FABRICATED", "PLACEHOLDER", "TODO", "HALLUCINATED")
    content_upper = raw_text.upper()
    no_fabrication = 0.0 if any(m in content_upper for m in _FABRICATION_MARKERS) else 1.0

    # concision: 1.0 for <=1500 words, linear penalty above.
    word_count = len(raw_text.split())
    concision = min(1.0, 1500.0 / max(word_count, 1)) if word_count > 1500 else 1.0

    # role_alignment: keyword overlap between professional_summary / executive_summary
    # text and the role keyword pool.  Normalised to [0, 1] by pool fraction.
    summary_src = content.get("professional_summary") or content.get("executive_summary") or ""
    if isinstance(summary_src, dict):
        summary_text = " ".join(str(v) for v in summary_src.values())
    elif isinstance(summary_src, list):
        summary_text = " ".join(str(v) for v in summary_src)
    else:
        summary_text = str(summary_src)
    summary_tokens = frozenset(re.findall(r"[a-zA-Z]+", summary_text.lower()))
    keyword_hits = len(summary_tokens & _ROLE_KEYWORD_POOL)
    # Normalise: hitting >=8 keywords → 1.0; linear below.
    role_alignment = min(1.0, keyword_hits / 8.0)

    # specificity: density of numeric evidence patterns relative to total words.
    full_text = json.dumps(content, ensure_ascii=False)
    numeric_hits = len(_SPECIFICITY_PATTERN.findall(full_text))
    total_words = max(len(full_text.split()), 1)
    # 1 numeric token per 40 words → 1.0; capped.
    specificity = min(1.0, (numeric_hits * 40) / total_words)

    # overall_pass_threshold: harmonic mean of six deterministic dimensions.
    dims = [format_compliance, ats_readability, no_fabrication, concision,
            role_alignment, specificity]
    harmonic = len(dims) / sum(1.0 / max(d, 1e-9) for d in dims)

    return {
        "format_compliance": round(format_compliance, 4),
        "ats_readability": round(ats_readability, 4),
        "no_fabrication": round(no_fabrication, 4),
        "concision": round(concision, 4),
        "role_alignment": round(role_alignment, 4),
        "specificity": round(specificity, 4),
        "overall_pass_threshold": round(harmonic, 4),
        # factual_grounding intentionally absent — see docstring.
    }


_FG_SAMPLE_LIMIT: int = 25  # max tokens in supported/unsupported samples

# Structural/control keys whose *values* must NOT be scored as resume claims.
# These are either schema metadata or target-spec fields injected by the pipeline,
# not content authored by the LLM from the candidate's evidence.
_FG_EXCLUDED_KEYS: frozenset[str] = frozenset([
    "target_company",
    "target_role",
    "target_level",
    "schema_version",
    "stub_mode",
    "evidence_anchor",  # key label, not a claim
    "app_id",
    "run_id",
    "trace_id",
    "request_id",
    "tenant_id",
])


def _extract_claim_text(obj: Any, depth: int = 0) -> list[str]:
    """Recursively extract string values from a resume dict, skipping excluded keys.

    Only *values* are collected — JSON key names are structural tokens and must
    not pollute the scoring surface.  Excluded keys (schema/control fields) have
    their values suppressed entirely.

    Returns a list of raw string values; caller joins and tokenises.
    """
    if depth > 10:
        return []
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, (int, float, bool)) or obj is None:
        return [str(obj)]
    if isinstance(obj, list):
        parts: list[str] = []
        for item in obj:
            parts.extend(_extract_claim_text(item, depth + 1))
        return parts
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            if k in _FG_EXCLUDED_KEYS:
                continue
            parts.extend(_extract_claim_text(v, depth + 1))
        return parts
    return []


@dataclasses.dataclass(frozen=True)
class FactualGroundingResult:
    """Structured result from compute_factual_grounding.

    score is identical in value to the previous float return so all
    downstream consumers that only need the float are unaffected.

    supported_token_samples / unsupported_token_samples are top-N
    illustrative tokens only — not exhaustive claim refs.  They are
    intended for diagnostic / explainability use, not gate logic.

    excluded_structural_tokens lists sample tokens that were suppressed
    because they came from excluded structural/control keys — these never
    affect the score.

    source_evidence_refs identifies which FEC evidence items were used.
    decisive_reason is a human-readable one-liner explaining the score.
    """

    score: float
    supported_token_samples: list[str]
    unsupported_token_samples: list[str]
    excluded_structural_tokens: list[str]
    source_evidence_refs: list[str]
    decisive_reason: str

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def compute_factual_grounding(
    content: "dict[str, Any] | None",
    fec: Any,
) -> "FactualGroundingResult | None":
    """Compute a factual_grounding score by comparing generated text to source evidence.

    Strategy: token-overlap between the generated resume text and the source
    resume evidence items from FinalEvidenceContract.  This is a deterministic
    proxy — it measures how much of the generated vocabulary was grounded in the
    supplied evidence rather than invented.

    Returns:
        FactualGroundingResult with score, token samples, evidence refs, and
            a decisive_reason string.  score is in [0.0, 1.0].
        None: when content is None, fec is None, or FEC contains no
            resume/jd evidence items (cannot score — do not fabricate).

    Score computation is identical to the previous float-return version:
    - Numeric tokens (dates, years, $-values) are weighted 2x.
    - Score = sum(matched_weight) / sum(total_weight).

    Samples are capped at _FG_SAMPLE_LIMIT tokens each to keep artifact size bounded.
    Supported samples are unique matched tokens; unsupported are unique unmatched tokens
    that are not JSON structural tokens (keys, brackets, etc.).
    """
    if content is None:
        return None
    if fec is None:
        return None

    evidence_items = getattr(fec, "evidence_items", None) or []

    # Collect source-resume and JD evidence items.
    used_sources: list[str] = []
    evidence_text_parts: list[str] = []
    for item in evidence_items:
        src = getattr(item, "source", "") or ""
        item_content = getattr(item, "content", "") or ""
        if item_content and ("resume" in src.lower() or "jd" in src.lower()):
            evidence_text_parts.append(item_content)
            used_sources.append(src)

    if not evidence_text_parts:
        return None

    evidence_combined = " ".join(evidence_text_parts).lower()
    evidence_tokens = frozenset(re.findall(r"[a-zA-Z0-9]+", evidence_combined))

    # --- Claim-value extraction -------------------------------------------
    # Score only over claim-bearing string values; skip JSON key names and
    # control/schema fields (target_company, schema_version, stub_mode, etc.).
    claim_parts = _extract_claim_text(content)
    claim_text = " ".join(claim_parts).lower()
    generated_tokens = re.findall(r"[a-zA-Z0-9]+", claim_text)

    # Compute excluded_structural_tokens for diagnostics: tokens present in the
    # full JSON serialisation but absent from claim-only text.
    full_json_text = json.dumps(content, ensure_ascii=False).lower()
    full_json_tokens: set[str] = set(re.findall(r"[a-zA-Z0-9]+", full_json_text))
    claim_token_set: set[str] = set(generated_tokens)
    _excluded_raw = full_json_tokens - claim_token_set

    if not generated_tokens:
        return FactualGroundingResult(
            score=1.0,
            supported_token_samples=[],
            unsupported_token_samples=[],
            excluded_structural_tokens=sorted(_excluded_raw)[:_FG_SAMPLE_LIMIT],
            source_evidence_refs=used_sources,
            decisive_reason="generated content is empty — vacuously grounded",
        )

    # Weighted token overlap — numerics count 2x (highest fabrication risk).
    _NUMERIC = re.compile(r"^\d")

    matched_weight = 0.0
    total_weight = 0.0
    seen_supported: dict[str, float] = {}   # tok → weight (for ranking)
    seen_unsupported: dict[str, float] = {}

    for tok in generated_tokens:
        w = 2.0 if _NUMERIC.match(tok) else 1.0
        total_weight += w
        if tok in evidence_tokens:
            matched_weight += w
            if tok not in seen_supported:
                seen_supported[tok] = w
        else:
            if tok not in seen_unsupported and len(tok) > 2:
                seen_unsupported[tok] = w

    score = round(matched_weight / max(total_weight, 1.0), 4)

    # Build samples: rank by weight desc (numerics first), then alpha.
    def _top_n(d: dict[str, float], n: int) -> list[str]:
        return [t for t, _ in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]

    supported_samples = _top_n(seen_supported, _FG_SAMPLE_LIMIT)
    unsupported_samples = _top_n(seen_unsupported, _FG_SAMPLE_LIMIT)
    excluded_structural = sorted(
        t for t in _excluded_raw if len(t) > 2
    )[:_FG_SAMPLE_LIMIT]

    unmatched_count = len(seen_unsupported)
    decisive_reason = (
        f"score={score:.4f}: {len(seen_supported)} unique matched tokens, "
        f"{unmatched_count} unique unmatched claim tokens out of "
        f"{len(generated_tokens)} total claim tokens (weighted); "
        f"{len(excluded_structural)} structural tokens excluded from scoring"
    )

    return FactualGroundingResult(
        score=score,
        supported_token_samples=supported_samples,
        unsupported_token_samples=unsupported_samples,
        excluded_structural_tokens=excluded_structural,
        source_evidence_refs=used_sources,
        decisive_reason=decisive_reason,
    )


class MissingPerInputHashError(ValueError):
    """Raised when a required per-input hash is absent from component_hash_map.

    Callers that need a fail-soft path (e.g. exit_finalize_apps_rg) should
    catch this and supply an empty dict as the g24_provenance evidence value,
    which will cause G24 to evaluate as UNKNOWN rather than falsely PASS.
    """

    def __init__(self, missing_keys: list[str]) -> None:
        self.missing_keys = missing_keys
        super().__init__(
            f"G24 provenance cannot be built: required per-input hash(es) missing "
            f"from component_hash_map: {missing_keys}.  "
            f"evidence_digest is an aggregate and must NOT substitute for named "
            f"per-input provenance fields (jd_hash, resume_hash, target_role_spec_hash)."
        )


def build_g24_provenance(
    sealed: "SealedL2Artifact",
    prompt: "CompiledPromptArtifact",
    pkg: Any,
) -> dict[str, Any]:
    """Build the g24_provenance dict from real, deterministic pipeline artifacts.

    All values are cryptographic digests or stable refs derived directly from
    sealed pipeline contracts — no fake placeholders.

    Per-input hashes MUST be present in prompt.component_hash_map under the keys
    "jd_hash", "resume_hash", and "target_role_spec_hash" (deposited there by the
    apps_rg PA binding).  If any required key is missing or empty, this function
    raises MissingPerInputHashError so the caller can supply {} as the G24 evidence
    value, causing G24 to evaluate as UNKNOWN rather than falsely PASS.

    evidence_digest is used ONLY for aggregate_evidence_hash.  It must NEVER
    substitute for jd_hash, resume_candidate_profile_hash, or target_role_spec_hash
    because it is an aggregate digest over all evidence, not over any single input.

    Hash mapping:
    - jd_hash              → g24_provenance["jd_hash"]
    - resume_hash          → g24_provenance["resume_candidate_profile_hash"]
    - target_role_spec_hash→ g24_provenance["target_role_spec_hash"]
    - evidence_digest      → g24_provenance["aggregate_evidence_hash"] ONLY
    - sealed_hash          → g24_provenance["replay_key"] + ["output_artifact_digest"]
    """
    evidence_digest: str = getattr(prompt, "evidence_digest", "") or ""
    compilation_hash: str = getattr(prompt, "compilation_hash", "") or ""
    sealed_hash: str = sealed.compilation_hash or ""

    # Read per-input hashes from component_hash_map (populated by apps_rg PA binding).
    # NO fallback to evidence_digest — a missing key means the provenance is incomplete.
    chm: dict[str, str] = dict(getattr(prompt, "component_hash_map", None) or {})
    jd_hash: str = chm.get("jd_hash") or ""
    resume_hash: str = chm.get("resume_hash") or ""
    target_role_spec_hash: str = chm.get("target_role_spec_hash") or ""

    missing: list[str] = [
        k for k, v in [
            ("jd_hash", jd_hash),
            ("resume_hash", resume_hash),
            ("target_role_spec_hash", target_role_spec_hash),
        ]
        if not v
    ]
    if missing:
        raise MissingPerInputHashError(missing)

    # Section artifact refs from the package.
    section_refs_json: str = json.dumps(
        [s.node_id for s in pkg.sealed_sections] if pkg.sealed_sections else []
    )

    return {
        "replay_key": sealed_hash,
        "resume_candidate_profile_hash": resume_hash,
        "jd_hash": jd_hash,
        "target_role_spec_hash": target_role_spec_hash,
        "aggregate_evidence_hash": evidence_digest,
        "prompt_profile_ref": f"ppr::apps_rg::resume_generation::v1::{compilation_hash[:16]}",
        "output_schema_ref": "schema::apps_rg::master_resume_v2::v2.16",
        "rubric_ref": "aer::apps_rg::resume_generation::v1",
        "threshold_profile_ref": "tpr::apps_rg::resume_generation::v1",
        "grader_roster_ref": "grr::apps_rg::resume_generation::v1",
        "workflow_manifest_ref": pkg.workflow_ref or "wfm::apps_rg::resume_generation::v1",
        "sealed_section_artifact_refs": section_refs_json,
        "sealed_workflow_artifact_ref": pkg.package_id,
        "output_artifact_digest": sealed_hash,
    }
