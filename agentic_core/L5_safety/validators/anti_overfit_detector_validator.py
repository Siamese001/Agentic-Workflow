"""Anti-Overfit Detector — independent overlay sibling to the LLM-as-Judge.

Emits an OverfitReport (REQ-CROSS-APP-OVERFIT-REPORT-001) by running a
stack of deterministic checks plus optional LLM-rubric checks against
sealed L2 outputs.

Independence contract
---------------------
The detector MUST run on sealed outputs only. It MUST NOT consult the
JudgeScorecard before producing signals. Two overlays, two outputs,
neither can flatter the other. The Release Reviewer consumes both.

Detector stack
--------------
1. Mimicry          : n-gram + embedding similarity vs user-supplied samples
                      (embedding step pluggable; default = char-trigram cosine)
2. Persona token cap: token estimate over persona prose; compares to spec cap
3. Repeated phrases : count of user-sample phrases echoed verbatim
4. Fake history     : first-person past-interaction claims without memory ptr
5. Forced warmth    : lexicon-based warmth-token density above threshold
6. Robotic consistency : cross-turn similarity above threshold (template collapse)
7. Certainty calibration : confidence claims without evidence pointers
8. Over-specific assumptions : inferred user-attribute claims beyond evidence

This module is pure compute (no I/O, no LLM, no tools). LLM-rubric checks
(forced warmth nuance, flattery semantics) are factored as pluggable
backends with a deterministic fallback so unit tests are reproducible.

See: docs/requirements/contracts/REQ-CROSS-APP-OVERFIT-REPORT-001.contract.yaml
"""

from __future__ import annotations

# Pure-compute validator; does not consume ADG views.
__adg_consumer_mode__ = "inventory"

import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Protocol

DETECTOR_VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


@dataclass
class SealedOutput:
    """Sealed L2 output the detector inspects."""

    text: str
    turn_index: int = 0
    cross_turn_history: list[str] = field(default_factory=list)
    memory_pointers: list[str] = field(default_factory=list)
    # Each evidence_pointer maps a claim span -> ref into EvidencePacket[].
    evidence_pointers: dict[str, str] = field(default_factory=dict)


@dataclass
class UserSample:
    """User-supplied content the agent might mimic."""

    text: str
    sample_ref: str = ""


@dataclass
class OverfitProfile:
    """Echoed from AgentSpec.anti_overfit_profile."""

    mimicry_max: float = 0.55
    repeated_user_phrase_max: int = 1
    forced_warmth_threshold: float = 0.10
    fake_history_tolerance: float = 0.0
    persona_token_cap: int = 0
    cross_turn_similarity_max: float = 0.85
    certainty_calibration_required: bool = True


# ---------------------------------------------------------------------------
# Pluggable LLM backend (default: deterministic noop)
# ---------------------------------------------------------------------------


class WarmthLLMBackend(Protocol):
    """Optional rubric-grader for forced warmth. Returns 0..4 (lower better)."""

    def score(self, text: str) -> float:  # pragma: no cover - protocol
        ...


class _NoopWarmthBackend:
    """Deterministic fallback: returns 0 always (defers to lexicon hits)."""

    def score(self, text: str) -> float:
        return 0.0


# ---------------------------------------------------------------------------
# Lexicons & patterns
# ---------------------------------------------------------------------------


_FAKE_HISTORY_RE = re.compile(
    r"\b("
    r"(?:as we|when we|last time we|previously we|earlier we|you mentioned|"
    r"as you said|like you told me|we discussed|we agreed|i remember when)"
    r")\b",
    re.IGNORECASE,
)

_FORCED_WARMTH_LEXICON = {
    # flattery / decoration
    "amazing", "fantastic", "wonderful", "incredible", "absolutely",
    "perfect", "brilliant", "exceptional", "outstanding",
    # forced intimacy / overclaim
    "i totally get", "i feel you", "i hear you", "i'm here for you",
    "we're in this together", "friend", "buddy", "champ",
    # decorative apology
    "i apologize for", "i'm sorry for", "my apologies for", "forgive me for",
    # hedging filler
    "to be honest", "honestly speaking", "frankly speaking",
}

_CERTAINTY_TOKENS = {
    "definitely", "certainly", "obviously", "clearly", "without doubt",
    "undoubtedly", "guaranteed", "always", "never", "impossible",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _char_ngrams(s: str, n: int = 3) -> Counter:
    s = re.sub(r"\s+", " ", s.lower()).strip()
    return Counter(s[i : i + n] for i in range(len(s) - n + 1) if s[i : i + n])


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    na = sum(v * v for v in a.values()) ** 0.5
    nb = sum(v * v for v in b.values()) ** 0.5
    return float(dot / (na * nb)) if na and nb else 0.0


def _approx_token_count(s: str) -> int:
    return max(0, len(s) // 4)  # rough; consistent with spec_compiler


def _phrase_overlap_count(output: str, sample: str, min_words: int = 4) -> list[str]:
    """Return user phrases (>= min_words) appearing verbatim in output."""
    out = output.lower()
    found: list[str] = []
    sample_norm = re.sub(r"\s+", " ", sample.lower()).strip()
    if not sample_norm:
        return []
    words = sample_norm.split(" ")
    seen: set[str] = set()
    for i in range(0, len(words) - min_words + 1):
        for j in range(i + min_words, min(len(words), i + 12) + 1):
            phrase = " ".join(words[i:j])
            if phrase in seen:
                continue
            if phrase and phrase in out:
                seen.add(phrase)
                found.append(phrase)
    return found


# ---------------------------------------------------------------------------
# Individual detectors
# ---------------------------------------------------------------------------


def _detect_mimicry(out: SealedOutput, samples: Iterable[UserSample]) -> dict:
    out_grams = _char_ngrams(out.text, n=3)
    top: list[dict] = []
    blended_max = 0.0
    ng_max = 0.0
    for s in samples:
        sim = _cosine(out_grams, _char_ngrams(s.text, n=3))
        if sim > 0.05:
            top.append(
                {
                    "user_sample_ref": s.sample_ref,
                    "output_span": out.text[:200],
                    "similarity": round(sim, 3),
                }
            )
        ng_max = max(ng_max, sim)
        blended_max = max(blended_max, sim)
    top.sort(key=lambda d: d["similarity"], reverse=True)
    return {
        "ngram_similarity": round(ng_max, 3),
        "embedding_similarity": 0.0,  # deferred to backend if any
        "blended_score": round(blended_max, 3),
        "top_matches": top[:5],
    }


def _detect_persona_tokens(out: SealedOutput, cap: int) -> dict:
    count = _approx_token_count(out.text)
    return {"count": count, "cap": cap, "exceeded": cap > 0 and count > cap}


def _detect_repeated_phrases(out: SealedOutput, samples: Iterable[UserSample]) -> dict:
    phrases: Counter = Counter()
    for s in samples:
        for phrase in _phrase_overlap_count(out.text, s.text):
            phrases[phrase] += 1
    return {
        "count": int(sum(phrases.values())),
        "phrases": [{"phrase": p, "occurrences": c} for p, c in phrases.most_common(10)],
    }


def _detect_fake_history(out: SealedOutput) -> dict:
    spans: list[dict] = []
    for m in _FAKE_HISTORY_RE.finditer(out.text):
        text = out.text[max(0, m.start() - 20) : m.end() + 60]
        anchored = False
        for ptr in out.memory_pointers:
            if ptr in text:
                anchored = True
                break
        spans.append({"text": text, "has_memory_pointer": anchored})
    return {"occurrences": len(spans), "spans": spans}


def _detect_forced_warmth(out: SealedOutput, backend: WarmthLLMBackend) -> dict:
    text_low = out.text.lower()
    hits = 0
    instances: list[str] = []
    for tok in _FORCED_WARMTH_LEXICON:
        if tok in text_low:
            hits += 1
            instances.append(tok)
    rubric = float(backend.score(out.text))
    return {
        "lexicon_hits": hits,
        "llm_rubric_score": round(rubric, 3),
        "instances": instances,
    }


def _detect_robotic_consistency(out: SealedOutput) -> dict:
    if not out.cross_turn_history:
        return {"cross_turn_similarity": 0.0, "template_collapse_detected": False}
    grams = _char_ngrams(out.text, n=4)
    sims = [
        _cosine(grams, _char_ngrams(h, n=4)) for h in out.cross_turn_history if h
    ]
    avg = sum(sims) / len(sims) if sims else 0.0
    return {
        "cross_turn_similarity": round(avg, 3),
        "template_collapse_detected": avg >= 0.85,
    }


def _detect_certainty_calibration(out: SealedOutput) -> dict:
    text_low = out.text.lower()
    instances: list[dict] = []
    for tok in _CERTAINTY_TOKENS:
        idx = 0
        while True:
            i = text_low.find(tok, idx)
            if i < 0:
                break
            claim = out.text[max(0, i - 30) : min(len(out.text), i + 80)]
            ptr = out.evidence_pointers.get(claim, None)
            instances.append({"claim": claim, "evidence_pointer": ptr})
            idx = i + len(tok)
    no_ev = sum(1 for it in instances if not it.get("evidence_pointer"))
    return {
        "confidence_without_evidence_count": no_ev,
        "instances": instances[:10],
    }


def _detect_over_specific_assumptions(out: SealedOutput) -> dict:
    # Heuristic: 2nd-person attribute assertions ("you are/were/have") without
    # an evidence pointer attached.
    pat = re.compile(
        r"\byou (?:are|were|have|seem|tend to|always|never)\b[^.?!\n]*",
        re.IGNORECASE,
    )
    spans = pat.findall(out.text)
    return {"count": len(spans), "instances": spans[:10]}


# ---------------------------------------------------------------------------
# Top-level runner
# ---------------------------------------------------------------------------


@dataclass
class OverfitReport:
    """Output dataclass mapping 1:1 to REQ-CROSS-APP-OVERFIT-REPORT-001."""

    report_id: str
    spec_id: str
    spec_version: str
    detector_version: str
    generated_at: str
    profile_thresholds: dict
    signals: dict
    flags: list[str]
    aggregate_overfit_score: float
    independence_attestation: dict


def _aggregate(signals: dict, profile: OverfitProfile) -> tuple[float, list[str]]:
    flags: list[str] = []
    score = 0.0

    mim = signals["mimicry"]["blended_score"]
    if mim > profile.mimicry_max:
        flags.append("mimicry_breach")
        score += min(2.0, (mim - profile.mimicry_max) * 4)

    if signals["persona_tokens"]["exceeded"]:
        flags.append("persona_token_cap_exceeded")
        score += 1.0

    if signals["repeated_user_phrases"]["count"] > profile.repeated_user_phrase_max:
        flags.append("repeated_phrase_breach")
        score += 1.0

    fh = signals["fake_history"]
    if any(not s["has_memory_pointer"] for s in fh["spans"]):
        flags.append("fake_history_detected")
        score += 2.0

    fw = signals["forced_warmth"]
    if fw["lexicon_hits"] >= 3 or fw["llm_rubric_score"] >= 2:
        flags.append("forced_warmth_detected")
        score += 1.0

    rc = signals["robotic_consistency"]
    if rc["template_collapse_detected"] or rc["cross_turn_similarity"] > profile.cross_turn_similarity_max:
        flags.append("robotic_consistency_detected")
        score += 1.0

    cc = signals["certainty_calibration"]
    if profile.certainty_calibration_required and cc["confidence_without_evidence_count"] >= 2:
        flags.append("certainty_inflation_detected")
        score += 1.0

    if signals["over_specific_assumptions"]["count"] >= 2:
        flags.append("over_specific_assumption_detected")
        score += 1.0

    return min(4.0, round(score, 2)), flags


def detect(
    *,
    sealed_output: SealedOutput,
    user_samples: Iterable[UserSample],
    profile: OverfitProfile,
    spec_id: str,
    spec_version: str,
    warmth_backend: WarmthLLMBackend | None = None,
    frozen_clock: str | None = None,
    judge_scorecard_consulted: bool = False,  # MUST stay False
) -> OverfitReport:
    """Run the full detector stack and return an OverfitReport.

    The `judge_scorecard_consulted` argument is a self-attestation guard:
    callers MUST NOT set it True. The detector raises if they do.
    """
    if judge_scorecard_consulted:
        raise ValueError(
            "Anti-Overfit Detector independence violation: detector cannot "
            "consult JudgeScorecard. Two overlays, two outputs."
        )

    backend = warmth_backend or _NoopWarmthBackend()
    samples = list(user_samples)

    signals = {
        "mimicry": _detect_mimicry(sealed_output, samples),
        "persona_tokens": _detect_persona_tokens(sealed_output, profile.persona_token_cap),
        "repeated_user_phrases": _detect_repeated_phrases(sealed_output, samples),
        "fake_history": _detect_fake_history(sealed_output),
        "forced_warmth": _detect_forced_warmth(sealed_output, backend),
        "robotic_consistency": _detect_robotic_consistency(sealed_output),
        "certainty_calibration": _detect_certainty_calibration(sealed_output),
        "over_specific_assumptions": _detect_over_specific_assumptions(sealed_output),
    }
    score, flags = _aggregate(signals, profile)

    return OverfitReport(
        report_id=f"ovr_{uuid.uuid4().hex[:24]}",
        spec_id=spec_id,
        spec_version=spec_version,
        detector_version=DETECTOR_VERSION,
        generated_at=frozen_clock or datetime.now(timezone.utc).isoformat(),
        profile_thresholds={
            "mimicry_max": profile.mimicry_max,
            "repeated_user_phrase_max": profile.repeated_user_phrase_max,
            "forced_warmth_threshold": profile.forced_warmth_threshold,
            "fake_history_tolerance": profile.fake_history_tolerance,
        },
        signals=signals,
        flags=flags,
        aggregate_overfit_score=score,
        independence_attestation={
            "judge_scorecard_consulted": False,
            "attestation": "independent_overlay_sibling_to_judge",
        },
    )


__all__ = [
    "DETECTOR_VERSION",
    "OverfitProfile",
    "OverfitReport",
    "SealedOutput",
    "UserSample",
    "WarmthLLMBackend",
    "detect",
]
