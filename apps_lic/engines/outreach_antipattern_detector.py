"""apps_lic Outreach Anti-Pattern Detector (SE-P0a).

Hard-fail on any of the 15 default forbidden patterns + configurable extension
patterns loaded from exit_rubric.yaml ``antipattern_extension_patterns``.

Contract
--------
- Fail-closed: any matched pattern → DetectionResult.is_clean=False
- Does NOT rewrite content
- Produces evidence_refs (match positions) and reason_codes per pattern
- Explicit test fixtures supported (pass pre-built patterns list)
- No provider calls, no state writes, no subprocess

15 default hard-fail patterns (from plan SE-P0a spec):
  1.  PASSIVE_SEEKER_TONE         "I would love to learn more"
  2.  UNEVIDENCED_SELF_ASSESSMENT  "I think I'd be a great fit"
  3.  STATUS_DEFLATING             "looking for new opportunities" / "open to new opportunities"
  4.  LOW_STATUS_FRAMING           "quick question" / "picking your brain"
  5.  SCRAPER_OPENER               "I saw your company"
  6.  SCRAPER_FLATTERY             "I noticed you"
  7.  BUZZWORD_FILLER              "thought leader" / "luminary" / "stalwart"
  8.  GENERIC_LINKEDIN_CLICHE      "would love to connect"
  9.  EM_DASH                      em dash (—) or en dash (–)
  10. ADMIRATION_WITHOUT_ARTIFACT  "I admire your work" without specific artifact reference
  11. PASSION_FILLER               "I'm passionate about"
  12. PREMATURE_LOGISTICS          compensation/salary/visa/relocation before first reply
  13. THREE_PARA_INTRO             >120 words before CTA
  14. PASSIVE_CLOSE                "Please let me know if you have any questions"
  15. NOISE_OPENER                 "Hope this finds you well" / "Hope you're doing well"

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-canonical-spine-wireup-e7c2a5.md SE-P0a
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Pattern definition type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AntiPattern:
    """A single anti-pattern rule.

    ``pattern_text`` is treated as a case-insensitive regex unless
    ``is_regex=False``, in which case it is a literal substring match.
    """

    pattern_id: str
    reason_code: str
    description: str
    pattern_text: str       # regex or literal substring
    is_regex: bool = True   # False → literal case-insensitive substring match


# ---------------------------------------------------------------------------
# Evidence for a single match
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PatternMatch:
    """Evidence for a single pattern match in the draft text."""

    pattern_id: str
    reason_code: str
    description: str
    matched_text: str
    start_pos: int
    end_pos: int


# ---------------------------------------------------------------------------
# Detection result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DetectionResult:
    """Result of running the anti-pattern detector on a draft.

    is_clean=True means no patterns matched — draft is clean.
    is_clean=False means ≥1 pattern matched — draft must be blocked.

    matches contains one PatternMatch per matched pattern (first match only
    per pattern to avoid flooding evidence_refs).
    """

    is_clean: bool
    matches: Tuple[PatternMatch, ...]
    evidence_refs: Tuple[str, ...]    # e.g. ["AP_001:pos=45-78", "AP_009:pos=120-121"]
    reason_codes: Tuple[str, ...]     # e.g. ("PASSIVE_SEEKER_TONE", "EM_DASH")
    draft_word_count: int


# ---------------------------------------------------------------------------
# Default 15 hard-fail patterns
# ---------------------------------------------------------------------------

_DEFAULT_PATTERNS: Tuple[AntiPattern, ...] = (
    AntiPattern(
        pattern_id="AP_001",
        reason_code="PASSIVE_SEEKER_TONE",
        description="Passive seeker tone — implies desperate availability",
        pattern_text=r"i would love to learn more",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_002",
        reason_code="UNEVIDENCED_SELF_ASSESSMENT",
        description="Un-evidenced self-assessment — claim without proof",
        pattern_text=r"i think i('d| would) be a great fit",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_003",
        reason_code="STATUS_DEFLATING",
        description="Status-deflating availability signal",
        pattern_text=r"(looking for new opportunities|open to new opportunities)",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_004",
        reason_code="LOW_STATUS_FRAMING",
        description="Low-status framing of the ask",
        pattern_text=r"(quick question|picking your brain)",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_005",
        reason_code="SCRAPER_OPENER",
        description="Scraper-tagged opener that signals mass-outreach",
        pattern_text=r"i saw your company",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_006",
        reason_code="SCRAPER_FLATTERY",
        description="Scraper-tagged flattery opener",
        pattern_text=r"i noticed you",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_007",
        reason_code="BUZZWORD_FILLER",
        description="Buzzword filler — signals generic/template content",
        pattern_text=r"(thought leader|luminary|stalwart)",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_008",
        reason_code="GENERIC_LINKEDIN_CLICHE",
        description="Generic LinkedIn connection cliché",
        pattern_text=r"would love to connect",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_009",
        reason_code="EM_DASH",
        description="Em dash (—) or en dash (–) — brand voice violation",
        pattern_text="[—–]",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_010",
        reason_code="ADMIRATION_WITHOUT_ARTIFACT",
        description="Generic admiration without specific artifact reference",
        pattern_text=r"i admire your work",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_011",
        reason_code="PASSION_FILLER",
        description="Passion filler — generic enthusiasm signal",
        pattern_text=r"i'?m passionate about",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_012",
        reason_code="PREMATURE_LOGISTICS",
        description="Compensation/salary/visa/relocation mention before first reply",
        pattern_text=r"(compensation|salary|visa|relocation|work authorization|sponsorship)",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_013",
        reason_code="THREE_PARA_INTRO",
        description=">120 words before CTA (three-paragraph intro bloat)",
        pattern_text="__WORD_COUNT_BEFORE_CTA__",  # handled specially
        is_regex=False,
    ),
    AntiPattern(
        pattern_id="AP_014",
        reason_code="PASSIVE_CLOSE",
        description="Passive close — low-status sign-off",
        pattern_text=r"please let me know if you have any questions",
        is_regex=True,
    ),
    AntiPattern(
        pattern_id="AP_015",
        reason_code="NOISE_OPENER",
        description="Noise opener — generic filler that wastes the first line",
        pattern_text=r"hope (this finds you|you('re| are) doing) well",
        is_regex=True,
    ),
)

# CTA patterns used to detect where the CTA begins (for AP_013)
_CTA_PATTERNS = re.compile(
    r"(would you be|are you open|happy to|let me know|feel free|"
    r"reach out|connect|chat|call|meet|coffee|30 min|15 min)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------

class OutreachAntipatternDetector:
    """Detects forbidden anti-patterns in outreach draft text.

    Usage::

        detector = OutreachAntipatternDetector()
        result = detector.detect(draft_text)
        if not result.is_clean:
            # fail-closed — do not produce draft
            raise ...

    Custom extension patterns can be injected at construction time (for
    test fixtures) or loaded from exit_rubric.yaml at runtime via
    ``from_rubric_config()``.
    """

    def __init__(
        self,
        *,
        extension_patterns: Optional[List[AntiPattern]] = None,
    ) -> None:
        self._patterns: Tuple[AntiPattern, ...] = _DEFAULT_PATTERNS + tuple(
            extension_patterns or []
        )

    @classmethod
    def from_rubric_config(
        cls,
        rubric: Dict[str, Any],
    ) -> "OutreachAntipatternDetector":
        """Build detector with extension patterns from exit_rubric.yaml content.

        ``rubric`` is the parsed YAML dict. Extension patterns are read from
        ``antipattern_extension_patterns`` list (may be absent or empty).
        """
        raw_extensions = rubric.get("antipattern_extension_patterns") or []
        ext_patterns = []
        for i, entry in enumerate(raw_extensions):
            if isinstance(entry, dict):
                ext_patterns.append(AntiPattern(
                    pattern_id=entry.get("id", f"EXT_{i:03d}"),
                    reason_code=entry.get("reason_code", "EXTENSION_ANTIPATTERN"),
                    description=entry.get("description", entry.get("pattern", "")),
                    pattern_text=entry.get("pattern", ""),
                    is_regex=entry.get("is_regex", False),
                ))
            elif isinstance(entry, str):
                ext_patterns.append(AntiPattern(
                    pattern_id=f"EXT_{i:03d}",
                    reason_code="EXTENSION_ANTIPATTERN",
                    description=entry,
                    pattern_text=entry,
                    is_regex=False,
                ))
        return cls(extension_patterns=ext_patterns)

    @property
    def pattern_count(self) -> int:
        return len(self._patterns)

    @property
    def patterns(self) -> Tuple[AntiPattern, ...]:
        return self._patterns

    def detect(self, draft_text: str) -> DetectionResult:
        """Run all patterns against ``draft_text``.

        Returns DetectionResult. is_clean=False if any pattern matched.
        Does not modify or rewrite ``draft_text``.
        """
        text_lower = draft_text.lower()
        word_count = len(draft_text.split())
        matches: List[PatternMatch] = []

        for pattern in self._patterns:
            m = self._check_pattern(pattern, draft_text, text_lower, word_count)
            if m is not None:
                matches.append(m)

        matches_tuple = tuple(matches)
        evidence_refs = tuple(
            f"{m.pattern_id}:{m.reason_code}:pos={m.start_pos}-{m.end_pos}"
            for m in matches_tuple
        )
        reason_codes = tuple(m.reason_code for m in matches_tuple)

        return DetectionResult(
            is_clean=len(matches) == 0,
            matches=matches_tuple,
            evidence_refs=evidence_refs,
            reason_codes=reason_codes,
            draft_word_count=word_count,
        )

    def _check_pattern(
        self,
        pattern: AntiPattern,
        text: str,
        text_lower: str,
        word_count: int,
    ) -> Optional[PatternMatch]:
        """Return PatternMatch if pattern fires, else None."""

        # AP_013 — word count before CTA heuristic
        if pattern.pattern_id == "AP_013":
            return self._check_three_para_intro(pattern, text)

        if pattern.is_regex:
            try:
                m = re.search(pattern.pattern_text, text_lower)
                if m:
                    return PatternMatch(
                        pattern_id=pattern.pattern_id,
                        reason_code=pattern.reason_code,
                        description=pattern.description,
                        matched_text=text[m.start():m.end()],
                        start_pos=m.start(),
                        end_pos=m.end(),
                    )
            except re.error:
                return None
        else:
            needle = pattern.pattern_text.lower()
            pos = text_lower.find(needle)
            if pos >= 0:
                return PatternMatch(
                    pattern_id=pattern.pattern_id,
                    reason_code=pattern.reason_code,
                    description=pattern.description,
                    matched_text=text[pos:pos + len(needle)],
                    start_pos=pos,
                    end_pos=pos + len(needle),
                )
        return None

    def _check_three_para_intro(
        self,
        pattern: AntiPattern,
        text: str,
    ) -> Optional[PatternMatch]:
        """AP_013: Fail if >120 words appear before the first CTA-like phrase."""
        cta_match = _CTA_PATTERNS.search(text)
        if cta_match is None:
            # No CTA found — count all words; >120 → fail
            total_words = len(text.split())
            if total_words > 120:
                return PatternMatch(
                    pattern_id=pattern.pattern_id,
                    reason_code=pattern.reason_code,
                    description=pattern.description,
                    matched_text=f"[no CTA found; {total_words} total words]",
                    start_pos=0,
                    end_pos=len(text),
                )
            return None

        pre_cta = text[: cta_match.start()]
        words_before_cta = len(pre_cta.split())
        if words_before_cta > 120:
            return PatternMatch(
                pattern_id=pattern.pattern_id,
                reason_code=pattern.reason_code,
                description=pattern.description,
                matched_text=f"[{words_before_cta} words before CTA at pos {cta_match.start()}]",
                start_pos=0,
                end_pos=cta_match.start(),
            )
        return None
