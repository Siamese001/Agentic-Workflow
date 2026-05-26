"""W3.2 — shared narrative mechanical X2 helpers (one sentence, metrics, overlap, openers)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences
from apps_rg.runtime.validators.executive_summary_x2 import EXEC_SUMMARY_MECHANICAL_OPENERS

DEFAULT_NARRATIVE_METRIC_CAP = 2
DEFAULT_BULLET_OVERLAP_MIN_WORDS = 5


def check_narrative_exactly_one_sentence(narrative: str) -> tuple[bool, int, str | None]:
    text = str(narrative or "").strip()
    sentences = split_sentences(text)
    count = len(sentences)
    if count != 1 or not text:
        return False, count, f"expected 1 sentence, found {count}"
    return True, count, None


def check_narrative_forbidden_opener(narrative: str) -> tuple[bool, str | None, str | None]:
    text = str(narrative or "").strip()
    if not text:
        return False, None, "empty narrative"
    first = re.sub(r"^[^A-Za-z0-9]+", "", text).split(None, 1)[0].lower().rstrip(".,;:")
    if first in EXEC_SUMMARY_MECHANICAL_OPENERS:
        return False, first, f"forbidden mechanical opener: {first}"
    return True, None, None


def count_narrative_metric_hits(
    narrative: str,
    *,
    metric_patterns: tuple[tuple[str, re.Pattern[str] | str], ...],
) -> int:
    hits = 0
    for _label, pat in metric_patterns:
        if isinstance(pat, re.Pattern):
            if pat.search(narrative):
                hits += 1
        elif str(pat).lower() in narrative.lower():
            hits += 1
    return hits


UNIFY_NARRATIVE_METRIC_PATTERNS: tuple[tuple[str, re.Pattern[str] | str], ...] = (
    ("22m", re.compile(r"\$22\s*m", re.I)),
    ("20pct", re.compile(r"20\s*%")),
    ("8to28", re.compile(r"8\s*(to|→|-|–)\s*28", re.I)),
    ("cycle", re.compile(r"six\s+months.*three\s+weeks", re.I)),
)

IBM_NARRATIVE_METRIC_PATTERNS: tuple[tuple[str, re.Pattern[str] | str], ...] = (
    ("15m", re.compile(r"\$15\s*m", re.I)),
    ("999", "99.9%"),
    ("30pct", re.compile(r"\b30\s*%")),
    ("25pct", re.compile(r"\b25\s*%")),
    ("50pct", re.compile(r"\b50\s*%")),
)


def check_narrative_metric_cap(
    narrative: str,
    *,
    metric_patterns: tuple[tuple[str, re.Pattern[str] | str], ...],
    max_metrics: int = DEFAULT_NARRATIVE_METRIC_CAP,
) -> tuple[bool, int, str | None]:
    hits = count_narrative_metric_hits(narrative, metric_patterns=metric_patterns)
    if hits > max_metrics:
        return False, hits, f"metric anchors {hits} exceed cap {max_metrics}"
    return True, hits, None


def check_narrative_bullet_overlap_threshold(
    narrative: str,
    companion_bullet_texts: str,
    *,
    min_prefix_words: int = DEFAULT_BULLET_OVERLAP_MIN_WORDS,
) -> tuple[bool, str | None, str | None]:
    """Fail when narrative copies a bullet-leading word prefix (structure bleed)."""
    nl = str(narrative or "").lower()
    for line in str(companion_bullet_texts or "").splitlines():
        line = line.strip()
        if not line:
            continue
        body = line.split(":", 1)[-1].strip() if ":" in line else line
        words = re.findall(r"[A-Za-z0-9%$]+", body.lower())
        if len(words) < min_prefix_words:
            continue
        prefix = " ".join(words[:min_prefix_words])
        if prefix and prefix in nl:
            return False, prefix, "narrative copies bullet-leading phrase"
    return True, None, None


def register_narrative_mechanical_x2_gates(
    add: Any,
    narrative_sentence: str,
    *,
    lane_prefix: str,
    companion_bullet_texts: str = "",
    metric_patterns: tuple[tuple[str, re.Pattern[str] | str], ...],
    max_metrics: int = DEFAULT_NARRATIVE_METRIC_CAP,
) -> None:
    st_ok, st_n, st_fail = check_narrative_exactly_one_sentence(narrative_sentence)
    add(
        f"x2_{lane_prefix}_narrative_exactly_one_sentence_mechanical",
        st_ok,
        st_n,
        1,
        st_fail or "single sentence required",
    )
    opener_ok, opener_hit, opener_fail = check_narrative_forbidden_opener(narrative_sentence)
    add(
        f"x2_{lane_prefix}_narrative_forbidden_opener",
        opener_ok,
        opener_hit or "none",
        "no mechanical opener",
        opener_fail,
    )
    metric_ok, metric_n, metric_fail = check_narrative_metric_cap(
        narrative_sentence,
        metric_patterns=metric_patterns,
        max_metrics=max_metrics,
    )
    add(
        f"x2_{lane_prefix}_narrative_metric_cap",
        metric_ok,
        metric_n,
        f"<={max_metrics}",
        metric_fail,
    )
    overlap_ok, overlap_hit, overlap_fail = check_narrative_bullet_overlap_threshold(
        narrative_sentence,
        companion_bullet_texts,
    )
    add(
        f"x2_{lane_prefix}_narrative_bullet_overlap_threshold",
        overlap_ok,
        overlap_hit or "none",
        f">={DEFAULT_BULLET_OVERLAP_MIN_WORDS} word prefix",
        overlap_fail,
    )


__all__ = [
    "DEFAULT_BULLET_OVERLAP_MIN_WORDS",
    "DEFAULT_NARRATIVE_METRIC_CAP",
    "IBM_NARRATIVE_METRIC_PATTERNS",
    "UNIFY_NARRATIVE_METRIC_PATTERNS",
    "check_narrative_bullet_overlap_threshold",
    "check_narrative_exactly_one_sentence",
    "check_narrative_forbidden_opener",
    "check_narrative_metric_cap",
    "count_narrative_metric_hits",
    "register_narrative_mechanical_x2_gates",
]
