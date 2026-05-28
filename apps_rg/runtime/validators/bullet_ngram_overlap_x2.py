"""N-gram overlap X2 gate helpers for bullet generation (W3: Bullet Proof Bundle Redesign).

Implements deterministic anti-leakage gates:
- x2_base_resume_ngram_overlap: generated bullet must not copy base resume prose (threshold <= 0.25)
- x2_e0_example_ngram_overlap: generated bullet must not copy E0 example text (threshold <= 0.20)

Deployed in WARN mode first to calibrate thresholds against live runs before activating as hard fails.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Sequence

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_RESUME_NGRAM_THRESHOLD = 0.25  # Fraction of n-grams allowed to overlap with base resume
E0_EXAMPLE_NGRAM_THRESHOLD = 0.20  # Fraction of n-grams allowed to overlap with E0 examples
NGRAM_SIZE = 4  # Default n-gram window size (4-gram avoids false positives on single domain terms)

# Gate IDs
GATE_ID_BASE_RESUME = "x2_base_resume_ngram_overlap"
GATE_ID_E0_EXAMPLE = "x2_e0_example_ngram_overlap"

_TOKEN_RE = re.compile(r"[a-z0-9$'%]+")


def _tokenize(text: str) -> list[str]:
    """Lowercase word/token list from text."""
    return _TOKEN_RE.findall(str(text or "").lower())


def extract_ngrams(tokens: Sequence[str], n: int) -> set[tuple[str, ...]]:
    """All contiguous n-grams from a token sequence."""
    if len(tokens) < n:
        return set()
    return {tuple(tokens[i: i + n]) for i in range(len(tokens) - n + 1)}


def compute_max_ngram_overlap(
    generated_text: str,
    reference_text: str,
    n: int = NGRAM_SIZE,
) -> float:
    """Fraction of n-grams in generated_text that appear in reference_text.

    Returns a value in [0.0, 1.0]. 0.0 means no overlap; 1.0 means all
    n-grams from generated_text exist in reference_text.

    Args:
        generated_text: The bullet text output from the model.
        reference_text: The reference corpus to test against (base resume bullets or E0 examples).
        n: N-gram window size. Defaults to 4.

    Returns:
        Overlap fraction (generated n-grams found in reference / total generated n-grams).
    """
    gen_tokens = _tokenize(generated_text)
    ref_tokens = _tokenize(reference_text)
    gen_ngrams = extract_ngrams(gen_tokens, n)
    if not gen_ngrams:
        return 0.0
    ref_ngrams = extract_ngrams(ref_tokens, n)
    overlap = gen_ngrams & ref_ngrams
    return len(overlap) / len(gen_ngrams)


def compute_max_ngram_overlap_multi_reference(
    generated_text: str,
    references: Sequence[str],
    n: int = NGRAM_SIZE,
) -> float:
    """Max overlap fraction across multiple reference texts."""
    if not references:
        return 0.0
    combined_ref = " ".join(str(r) for r in references if r)
    return compute_max_ngram_overlap(generated_text, combined_ref, n=n)


# ---------------------------------------------------------------------------
# IBM base-resume reference extraction
# ---------------------------------------------------------------------------

def load_ibm_base_resume_bullet_texts() -> list[str]:
    """Load IBM employment bullet texts from the canonical base resume JSON.

    Returns claim-free reference texts (the `text` field from each bul_ibm_* bullet).
    These are used as the reference corpus for x2_base_resume_ngram_overlap.
    """
    from pathlib import Path
    import json

    base_path = Path("apps_rg/resume/base/amit_ayer_base_resume_v1.json")
    if not base_path.exists():
        return []
    try:
        with base_path.open(encoding="utf-8") as f:
            base = json.load(f)
        employment = (base.get("facts") or {}).get("employment") or []
        ibm_texts: list[str] = []
        for exp in employment:
            if not isinstance(exp, dict):
                continue
            if str(exp.get("employer") or "").upper() != "IBM":
                continue
            for bullet in exp.get("bullets") or []:
                txt = str(bullet.get("text") or "").strip()
                if txt:
                    ibm_texts.append(txt)
        return ibm_texts
    except Exception:  # guardian: allow-silent-swallow -- gate fails open (WARN mode)
        return []


def load_unify_base_resume_bullet_texts() -> list[str]:
    """Load Unify employment bullet texts from the canonical base resume JSON."""
    from pathlib import Path
    import json

    base_path = Path("apps_rg/resume/base/amit_ayer_base_resume_v1.json")
    if not base_path.exists():
        return []
    try:
        with base_path.open(encoding="utf-8") as f:
            base = json.load(f)
        employment = (base.get("facts") or {}).get("employment") or []
        unify_texts: list[str] = []
        for exp in employment:
            if not isinstance(exp, dict):
                continue
            employer = str(exp.get("employer") or "").upper()
            if "UNIFY" not in employer:
                continue
            for bullet in exp.get("bullets") or []:
                txt = str(bullet.get("text") or "").strip()
                if txt:
                    unify_texts.append(txt)
        return unify_texts
    except Exception:  # guardian: allow-silent-swallow -- gate fails open (WARN mode)
        return []


# ---------------------------------------------------------------------------
# Gate runner helpers
# ---------------------------------------------------------------------------

@dataclass
class NgramOverlapResult:
    gate_id: str
    passed: bool
    warn_only: bool
    bullet_id: str
    overlap_fraction: float
    threshold: float
    reference_source: str
    failure_reason: str | None


def check_bullet_base_resume_ngram_overlap(
    bullet_id: str,
    bullet_text: str,
    base_resume_texts: list[str],
    *,
    threshold: float = BASE_RESUME_NGRAM_THRESHOLD,
    n: int = NGRAM_SIZE,
    warn_only: bool = True,
) -> NgramOverlapResult:
    """Check a single bullet against base resume reference texts."""
    overlap = compute_max_ngram_overlap_multi_reference(bullet_text, base_resume_texts, n=n)
    passed_gate = overlap <= threshold
    return NgramOverlapResult(
        gate_id=GATE_ID_BASE_RESUME,
        passed=passed_gate or warn_only,
        warn_only=warn_only,
        bullet_id=bullet_id,
        overlap_fraction=round(overlap, 4),
        threshold=threshold,
        reference_source="base_resume_bullets",
        failure_reason=(
            f"{bullet_id}: {overlap:.2%} 4-gram overlap with base resume (threshold {threshold:.0%})"
            if not passed_gate
            else None
        ),
    )


def check_bullet_e0_example_ngram_overlap(
    bullet_id: str,
    bullet_text: str,
    e0_texts: list[str],
    *,
    threshold: float = E0_EXAMPLE_NGRAM_THRESHOLD,
    n: int = NGRAM_SIZE,
    warn_only: bool = True,
) -> NgramOverlapResult:
    """Check a single bullet against E0 example reference texts."""
    overlap = compute_max_ngram_overlap_multi_reference(bullet_text, e0_texts, n=n)
    passed_gate = overlap <= threshold
    return NgramOverlapResult(
        gate_id=GATE_ID_E0_EXAMPLE,
        passed=passed_gate or warn_only,
        warn_only=warn_only,
        bullet_id=bullet_id,
        overlap_fraction=round(overlap, 4),
        threshold=threshold,
        reference_source="e0_examples",
        failure_reason=(
            f"{bullet_id}: {overlap:.2%} 4-gram overlap with E0 examples (threshold {threshold:.0%})"
            if not passed_gate
            else None
        ),
    )


def run_bullet_ngram_overlap_gates(
    bullets: list[dict[str, Any]],
    *,
    section_id: str,
    base_resume_texts: list[str] | None = None,
    e0_texts: list[str] | None = None,
    base_resume_threshold: float = BASE_RESUME_NGRAM_THRESHOLD,
    e0_threshold: float = E0_EXAMPLE_NGRAM_THRESHOLD,
    n: int = NGRAM_SIZE,
    warn_only: bool = True,
) -> tuple[
    bool,  # base_resume gate overall pass
    list[NgramOverlapResult],  # base_resume results per bullet
    bool,  # e0 gate overall pass
    list[NgramOverlapResult],  # e0 results per bullet
]:
    """Run both ngram overlap gates across all bullets in a section.

    Returns (base_resume_gate_pass, base_results, e0_gate_pass, e0_results).
    In WARN mode (warn_only=True) the gate always passes but records violations.
    """
    bullet_id_prefix = "bul_ibm_" if section_id == "ibm_bullets" else "bul_unify_"

    if base_resume_texts is None:
        if section_id == "ibm_bullets":
            base_resume_texts = load_ibm_base_resume_bullet_texts()
        else:
            base_resume_texts = load_unify_base_resume_bullet_texts()

    base_results: list[NgramOverlapResult] = []
    e0_results: list[NgramOverlapResult] = []

    for b in bullets:
        if not isinstance(b, dict):
            continue
        bid = str(b.get("bullet_id") or "")
        if not bid.startswith(bullet_id_prefix):
            continue
        text = str(b.get("bullet_text") or "").strip()
        if not text:
            continue

        if base_resume_texts:
            base_results.append(
                check_bullet_base_resume_ngram_overlap(
                    bid, text, base_resume_texts,
                    threshold=base_resume_threshold, n=n, warn_only=warn_only,
                )
            )
        if e0_texts:
            e0_results.append(
                check_bullet_e0_example_ngram_overlap(
                    bid, text, e0_texts,
                    threshold=e0_threshold, n=n, warn_only=warn_only,
                )
            )

    base_pass = all(r.passed for r in base_results) if base_results else True
    e0_pass = all(r.passed for r in e0_results) if e0_results else True
    return base_pass, base_results, e0_pass, e0_results


__all__ = [
    "BASE_RESUME_NGRAM_THRESHOLD",
    "E0_EXAMPLE_NGRAM_THRESHOLD",
    "GATE_ID_BASE_RESUME",
    "GATE_ID_E0_EXAMPLE",
    "NGRAM_SIZE",
    "NgramOverlapResult",
    "check_bullet_base_resume_ngram_overlap",
    "check_bullet_e0_example_ngram_overlap",
    "compute_max_ngram_overlap",
    "compute_max_ngram_overlap_multi_reference",
    "extract_ngrams",
    "load_ibm_base_resume_bullet_texts",
    "load_unify_base_resume_bullet_texts",
    "run_bullet_ngram_overlap_gates",
]
