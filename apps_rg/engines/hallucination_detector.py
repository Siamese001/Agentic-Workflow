"""Resume bullet hallucination / overclaim heuristics for QA (deterministic, legacy tests)."""

from __future__ import annotations

import re

# Snapshot blocklist enforced by regression tests (`test_hallucination_detector.py`).
_SUPERLATIVES: frozenset[str] = frozenset(
    {
        "revolutionary",
        "groundbreaking",
        "unprecedented",
        "unparalleled",
        "game-changing",
        "world-class",
        "best-in-class",
        "cutting-edge",
    }
)

_DIGIT_PERCENT_3PLUS = re.compile(r"\b(\d{3,})\s*%")
_MAG_1000 = re.compile(r"\b1000\s*%")
_MAG_4PLUS = re.compile(r"\b\d{4,}\s*%")
_OVERCLAIM_ACC = re.compile(r"\b100\s*%\s+accuracy\b", re.I)
_SHORT_HORIZON = re.compile(
    r"\b(?:month|months|week|weeks|quarter|quarters|90\s*-?\s*days?|ninety\s+days?)\b",
    re.I,
)


def _superlative_hits(lowered_blob: str) -> int:
    total = 0
    for phrase in _SUPERLATIVES:
        if "-" in phrase:
            if phrase in lowered_blob:
                total += 1
            continue
        if re.search(rf"\b{re.escape(phrase)}\b", lowered_blob):
            total += 1
    return total


class HallucinationDetector:
    """Lightweight hallucination heuristic used by deterministic resume QA pipelines."""

    _GENERIC_SUPERLATIVES = sorted(_SUPERLATIVES)

    _SUSPICIOUS_PATTERNS = (
        "implausible_growth",
        "implausible_growth_with_horizon",
        "overclaim_phrase",
        "excessive_superlatives",
    )

    def check_batch(self, texts: list[str]) -> dict[str, object]:
        issues: list[str] = []

        lowered_joined = "\n".join(texts).lower()
        sup_total = max(
            (_superlative_hits(t.lower()) for t in texts),
            default=0,
        )
        sup_total = max(sup_total, _superlative_hits(lowered_joined))

        if sup_total >= 2:
            issues.append("excessive_superlatives:g3")

        for raw in texts:
            ln = raw.lower()

            pct = _DIGIT_PERCENT_3PLUS.search(raw)
            if pct is not None and len(pct.group(1)) >= 3:
                if _SHORT_HORIZON.search(ln):
                    issues.append("implausible_growth_with_horizon:g4")
                elif not _SHORT_HORIZON.search(ln):
                    issues.append("implausible_growth:triple_no_horizon")

            if _MAG_1000.search(ln) or _MAG_4PLUS.search(ln):
                if not _SHORT_HORIZON.search(ln):
                    issues.append("implausible_growth:large_percent")

            if _OVERCLAIM_ACC.search(raw):
                issues.append("overclaim_phrase:accuracy")

        seen_kind: set[str] = set()
        deduped: list[str] = []
        for item in issues:
            kind = item.split(":", 1)[0]
            if kind in seen_kind:
                continue
            seen_kind.add(kind)
            deduped.append(item)
        issues = deduped

        score = 0.8 if sup_total >= 2 else 1.0

        return {"issues": issues, "score": score}
