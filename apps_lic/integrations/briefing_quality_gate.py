"""apps_lic.integrations.briefing_quality_gate — D3-P1.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-deferred-scope-followup-d3f9b2.md W3 D3-P1

Evaluates the quality of an apps_research briefing result on three axes:

  1. **Coverage**  — sufficient evidence items to support an outreach draft.
  2. **Recency**   — research result is fresh enough for the recipient class.
  3. **Source diversity** — evidence items come from multiple distinct sources.

Returns an immutable BriefingQualityDecision. The gate is **policy-gated**:
marginal quality does NOT hard-fail — it emits a quality_level ("pass" /
"marginal" / "fail") and caller decides routing:

  pass     → proceed to R4 as normal
  marginal → proceed to R4 but flag for potential HITL review (plan note:
             "Must not block R4 when quality is marginal")
  fail     → emit DispatchFailurePacket (APPS_RESEARCH_WEAK_SUPPORT or
             APPS_RESEARCH_STALE) — caller's responsibility

Decision-only invariants
------------------------
- No durable writes.
- No provider API calls.
- No subprocess calls.
- Config loaded from apps_lic/config/briefing_quality_policy.yaml on first use
  (lazy, cached at class level). Missing config → conservative defaults apply.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from apps_lic.integrations.research_reason_codes import (
    APPS_RESEARCH_STALE,
    APPS_RESEARCH_WEAK_SUPPORT,
)

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "briefing_quality_policy.yaml"


def _load_policy() -> dict:
    try:
        import yaml  # type: ignore[import]
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- config load is best-effort; missing
        # YAML falls back to conservative defaults, never crashes the gate.
        return {}


@lru_cache(maxsize=1)
def _policy() -> dict:
    return _load_policy()


def _get(cfg: dict, *keys: str, default: Any = None) -> Any:
    node = cfg
    for k in keys:
        if not isinstance(node, dict):
            return default
        node = node.get(k, default)
        if node is default:
            return default
    return node


# ---------------------------------------------------------------------------
# Thresholds (also in briefing_quality_policy.yaml — these are hard defaults)
# ---------------------------------------------------------------------------

_DEFAULT_COVERAGE_MIN_ITEMS = 2
_DEFAULT_COVERAGE_MARGINAL_ITEMS = 1
_DEFAULT_RECENCY_FAIL_DAYS: dict[str, int] = {
    "executive": 7,
    "recruiter": 30,
    "default": 14,
}
_DEFAULT_RECENCY_MARGINAL_DAYS: dict[str, int] = {
    "executive": 14,
    "recruiter": 60,
    "default": 30,
}
_DEFAULT_MIN_UNIQUE_SOURCES = 2


@dataclass(frozen=True)
class BriefingQualityDecision:
    """Immutable result of a briefing quality evaluation.

    Fields
    ------
    quality_level : "pass" | "marginal" | "fail"
    coverage_ok   : True if coverage check passed (not marginal, not fail).
    recency_ok    : True if recency check passed.
    diversity_ok  : True if source diversity check passed.
    evidence_count    : Number of evidence items found.
    unique_sources    : Number of distinct source domains/labels.
    age_days          : Age of the research result in days (None = unknown).
    fail_reasons      : List of human-readable strings describing fail/marginal issues.
    r5_reason_code    : When quality_level=="fail", the R5 code to use. Empty otherwise.
    """

    quality_level: str
    coverage_ok: bool
    recency_ok: bool
    diversity_ok: bool
    evidence_count: int
    unique_sources: int
    age_days: Optional[float]
    fail_reasons: tuple = field(default_factory=tuple)
    r5_reason_code: str = ""


class BriefingQualityGate:
    """Evaluates briefing quality on coverage, recency, and source diversity.

    Usage::

        gate = BriefingQualityGate()
        decision = gate.evaluate(research_result, recipient_class="EXECUTIVE")
        if decision.quality_level == "fail":
            return DispatchFailurePacket(r5_reason_code=decision.r5_reason_code, ...)
    """

    def __init__(self, policy: dict | None = None) -> None:
        self._policy = policy if policy is not None else _policy()

    def _coverage_thresholds(self) -> tuple[int, int]:
        """Return (min_pass, min_marginal) evidence item counts."""
        min_pass = _get(
            self._policy, "coverage", "min_evidence_items", default=_DEFAULT_COVERAGE_MIN_ITEMS
        )
        min_marginal = _get(
            self._policy, "coverage", "marginal_evidence_items", default=_DEFAULT_COVERAGE_MARGINAL_ITEMS
        )
        return int(min_pass), int(min_marginal)

    def _recency_thresholds(self, recipient_class: str) -> tuple[int, int]:
        """Return (fail_days, marginal_days) for the given recipient class."""
        rc = recipient_class.lower()
        bucket = "executive" if rc in {"executive", "c_level", "cto", "vp_eng"} else (
            "recruiter" if rc in {"recruiter", "senior_ta"} else "default"
        )
        fail_days = _get(
            self._policy, "recency", bucket, "fail_days",
            default=_DEFAULT_RECENCY_FAIL_DAYS.get(bucket, 14),
        )
        marginal_days = _get(
            self._policy, "recency", bucket, "marginal_days",
            default=_DEFAULT_RECENCY_MARGINAL_DAYS.get(bucket, 30),
        )
        return int(fail_days), int(marginal_days)

    def _diversity_threshold(self) -> int:
        return int(_get(
            self._policy, "diversity", "min_unique_sources",
            default=_DEFAULT_MIN_UNIQUE_SOURCES,
        ))

    @staticmethod
    def _extract_evidence_items(research_result: Any) -> list:
        items = getattr(research_result, "evidence_items", None)
        if items is None:
            items = getattr(research_result, "items", [])
        return list(items) if items else []

    @staticmethod
    def _extract_age_days(research_result: Any) -> Optional[float]:
        age = getattr(research_result, "age_days", None)
        if age is not None:
            try:
                return float(age)
            except (TypeError, ValueError):
                pass
        return None

    @staticmethod
    def _count_unique_sources(evidence_items: list) -> int:
        seen: set[str] = set()
        for ev in evidence_items:
            label = str(getattr(ev, "label", getattr(ev, "source", f"ev_{id(ev)}")))
            # Use domain prefix as diversity unit
            uri = str(getattr(ev, "uri", getattr(ev, "source_uri", label)))
            domain = uri.split("/")[0] if "/" in uri else label
            seen.add(domain)
        return len(seen)

    def evaluate(
        self,
        research_result: Any,
        *,
        recipient_class: str = "default",
    ) -> BriefingQualityDecision:
        """Evaluate research result quality.

        Parameters
        ----------
        research_result : Any
            Object with attributes: evidence_items, age_days, confidence_score.
        recipient_class : str
            Recipient class string — affects recency thresholds.

        Returns
        -------
        BriefingQualityDecision
        """
        evidence_items = self._extract_evidence_items(research_result)
        age_days = self._extract_age_days(research_result)
        unique_sources = self._count_unique_sources(evidence_items)
        evidence_count = len(evidence_items)

        fail_reasons: list[str] = []
        hard_fail = False
        r5_code = ""

        # ---- Coverage check ----
        min_pass, min_marginal = self._coverage_thresholds()
        if evidence_count >= min_pass:
            coverage_ok = True
        elif evidence_count >= min_marginal:
            coverage_ok = False
            fail_reasons.append(
                f"coverage_marginal: {evidence_count} items < min_pass={min_pass}"
            )
        else:
            coverage_ok = False
            hard_fail = True
            r5_code = APPS_RESEARCH_WEAK_SUPPORT
            fail_reasons.append(
                f"coverage_fail: {evidence_count} items < marginal_min={min_marginal}"
            )

        # ---- Recency check ----
        fail_days, marginal_days = self._recency_thresholds(recipient_class)
        if age_days is None:
            recency_ok = True  # unknown age — conservative pass
        elif age_days > fail_days:
            recency_ok = False
            hard_fail = True
            r5_code = r5_code or APPS_RESEARCH_STALE
            fail_reasons.append(
                f"recency_fail: age_days={age_days:.1f} > fail_threshold={fail_days} "
                f"(recipient_class={recipient_class})"
            )
        elif age_days > marginal_days:
            recency_ok = False
            fail_reasons.append(
                f"recency_marginal: age_days={age_days:.1f} > marginal_threshold={marginal_days}"
            )
        else:
            recency_ok = True

        # ---- Diversity check ----
        min_div = self._diversity_threshold()
        if unique_sources >= min_div:
            diversity_ok = True
        else:
            diversity_ok = False
            fail_reasons.append(
                f"diversity_marginal: {unique_sources} unique_sources < min={min_div}"
            )

        # ---- Determine quality_level ----
        if hard_fail:
            quality_level = "fail"
        elif fail_reasons:
            quality_level = "marginal"
        else:
            quality_level = "pass"

        return BriefingQualityDecision(
            quality_level=quality_level,
            coverage_ok=coverage_ok,
            recency_ok=recency_ok,
            diversity_ok=diversity_ok,
            evidence_count=evidence_count,
            unique_sources=unique_sources,
            age_days=age_days,
            fail_reasons=tuple(fail_reasons),
            r5_reason_code=r5_code,
        )
