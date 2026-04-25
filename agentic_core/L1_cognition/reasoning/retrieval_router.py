"""Agentic retrieval router — Tier 1 deterministic intent classifier (ADR-064).

Maps an incoming query plus caller hints to a fully-populated retrieval plan
covering: query transform, reranker mode, reflective-loop flag, dim tier,
collections, hydration mode, and a latency budget. The plan composes every
other ADR in the W1–W6 family at query time so the calling agent does not
have to leak a dozen knobs upward.

This module is the **Tier 1** rule-based classifier. Telemetry-weighted
selection (Tier 2) is in ``router_weights.yaml`` and is loaded if present;
when absent, the deterministic defaults from ADR-064 §3 win.

The router is deliberately LLM-free at the routing step itself — Tier 1
classification runs in microseconds, predictable across processes, and adds
no failure modes to a hot path. The transforms it selects MAY be LLM-backed,
but that is a separate stage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Final


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class IntentClass(Enum):
    """Coarse query intent. Authoritative list per ADR-064 §2."""

    CODE_CONCEPT = "code_concept"
    CODE_LOCATOR = "code_locator"
    PROSE_FACTUAL = "prose_factual"
    PROSE_COMPOUND = "prose_compound"
    PROSE_ABSTRACT_WHY = "prose_abstract_why"
    METADATA_FILTER = "metadata_filter"
    TRACE_LOOKUP = "trace_lookup"
    INCIDENT_RECALL = "incident_recall"
    UNKNOWN = "unknown"


class SLO(Enum):
    """Caller-side latency SLO. Drives the budget+downgrade ladder."""

    INTERACTIVE = "interactive"
    """≤ 800 ms — Cascade C0 live loop, chat retrieval."""

    BACKGROUND = "background"
    """≤ 3 s — session-scoped analytics, scorer features."""

    BATCH = "batch"
    """≤ 30 s — nightly audit, drift detection, bulk similarity."""


SLO_BUDGETS_MS: Final[dict[SLO, int]] = {
    SLO.INTERACTIVE: 800,
    SLO.BACKGROUND: 3000,
    SLO.BATCH: 30_000,
}


@dataclass(frozen=True)
class RouterHints:
    """Per-call constraints from the caller.

    ``allowed_tiers`` and ``allowed_collections`` narrow the router's choice;
    they never widen it. Empty / None means "no narrowing".
    """

    slo: SLO = SLO.INTERACTIVE
    allowed_tiers: tuple[str, ...] | None = None
    allowed_collections: tuple[str, ...] | None = None
    fail_on_unsatisfiable: bool = False


@dataclass
class RetrievalPlan:
    """The router's output. Composes every retrieval-stage knob.

    This dataclass intentionally lives next to the router rather than in the
    canonical ``agentic_core/knowledge/retrieval/retrieval_plan.py`` module:
    the canonical RetrievalPlan handles the full prefilter + replay-key
    contract today; this is the **router-emitted** subset that downstream
    code adapts into the canonical shape. Once ADR-064 lands in production
    the two converge into one type.
    """

    intent_class: IntentClass
    query_transform: str
    reranker_mode: str
    reflective: bool
    dim_tier: str
    collections: tuple[str, ...]
    hydration_mode: str
    latency_budget_ms: int
    route_reason: str
    downgrades: tuple[str, ...] = field(default_factory=tuple)
    """Telemetry: ordered list of downgrades applied to fit the budget."""


class RouteUnsatisfiableError(RuntimeError):
    """Raised only when caller passes ``fail_on_unsatisfiable=True``.

    The default behavior is to degrade to identity baseline and emit a
    downgrade event rather than raise — see ADR-064 §5 R3.
    """


# ---------------------------------------------------------------------------
# Tier 1 — deterministic classifier (no LLM, microsecond cost)
# ---------------------------------------------------------------------------


_QUESTION_WORD_RE = re.compile(r"^\s*(?:what|why|how|when|where|who|which)\b", re.IGNORECASE)
_WHY_RE = re.compile(r"^\s*(?:why|how come)\b", re.IGNORECASE)
_CONJUNCTION_RE = re.compile(r"\b(?:and|or|plus|also|as well as)\b", re.IGNORECASE)
_FILEPATH_RE = re.compile(r"[A-Za-z0-9_]+\.(?:py|md|yaml|json|jsonl|toml|sql)\b")
_DOTTED_SYMBOL_RE = re.compile(r"\b[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\b", re.IGNORECASE)
_CODE_TOKEN_RE = re.compile(
    r"(?:[A-Z][a-zA-Z0-9]+[A-Z][a-zA-Z0-9]+)"  # CamelCase
    r"|(?:[a-z]+_[a-z_0-9]+)"  # snake_case
    r"|(?:\b\w+\(\))"  # function() call
)
_METADATA_LAYER_RE = re.compile(r"\bin\s+layer\s+L\d\b", re.IGNORECASE)
_METADATA_DATE_RE = re.compile(r"\bsince\s+\d{4}\b", re.IGNORECASE)
_METADATA_DIR_RE = re.compile(r"\bin\s+`[^`]+`", re.IGNORECASE)
_METADATA_TYPE_RE = re.compile(r"\bonly\s+(?:adr|plan|test|incident|trace)s?\b", re.IGNORECASE)
_TRACE_RE = re.compile(r"\b(?:trace[_ ]id|span[_ ]id|agent[_ ]class|trace_lookup)\b", re.IGNORECASE)
_INCIDENT_RE = re.compile(r"\b(?:rca|incident|outage|post[ _-]mortem)\b", re.IGNORECASE)


def _has_metadata_cue(query: str) -> bool:
    return any(
        rx.search(query)
        for rx in (
            _METADATA_LAYER_RE,
            _METADATA_DATE_RE,
            _METADATA_DIR_RE,
            _METADATA_TYPE_RE,
        )
    )


def _is_filepath_only(query: str) -> bool:
    """A lone filepath or dotted symbol with no NL framing."""

    stripped = query.strip()
    if " " in stripped:
        return False
    return bool(_FILEPATH_RE.search(stripped) or _DOTTED_SYMBOL_RE.search(stripped))


def _has_code_tokens(query: str) -> bool:
    return bool(_CODE_TOKEN_RE.search(query) or _FILEPATH_RE.search(query))


def _is_compound(query: str) -> bool:
    if not _CONJUNCTION_RE.search(query):
        return False
    # Heuristic: at least two clauses around a conjunction => compound.
    parts = _CONJUNCTION_RE.split(query)
    return sum(1 for p in parts if len(p.split()) >= 2) >= 2


def classify_intent(query: str) -> IntentClass:
    """Map a query to its intent class via ordered rules.

    Order matters and matches ADR-064 §3 / W3.2 routing rubric.
    """

    if not query.strip():
        return IntentClass.UNKNOWN

    if _TRACE_RE.search(query):
        return IntentClass.TRACE_LOOKUP
    if _INCIDENT_RE.search(query):
        return IntentClass.INCIDENT_RECALL
    if _has_metadata_cue(query):
        return IntentClass.METADATA_FILTER

    is_question = bool(_QUESTION_WORD_RE.match(query)) or query.rstrip().endswith("?")
    code = _has_code_tokens(query)

    if _is_filepath_only(query):
        return IntentClass.CODE_LOCATOR

    if _WHY_RE.match(query):
        return IntentClass.PROSE_ABSTRACT_WHY

    if _is_compound(query) and len(query.split()) > 20:
        return IntentClass.PROSE_COMPOUND

    if is_question and code:
        return IntentClass.CODE_CONCEPT

    if is_question and len(query.split()) <= 12:
        return IntentClass.PROSE_FACTUAL

    if code:
        return IntentClass.CODE_LOCATOR

    return IntentClass.UNKNOWN


# ---------------------------------------------------------------------------
# Tier 2 — class-to-plan mapping (defaults; YAML may override)
# ---------------------------------------------------------------------------


_DEFAULT_PLANS: Final[dict[IntentClass, dict[str, object]]] = {
    IntentClass.CODE_CONCEPT: {
        "collections": ("code_chunks", "docs"),
        "query_transform": "hyde",
        "reranker_mode": "cross_encoder_late",
        "reflective": True,
        "dim_tier": "hot-interactive",
        "hydration_mode": "none",
    },
    IntentClass.CODE_LOCATOR: {
        "collections": ("code_chunks",),
        "query_transform": "identity",
        "reranker_mode": "cross_encoder",
        "reflective": False,
        "dim_tier": "hot-interactive",
        "hydration_mode": "none",
    },
    IntentClass.PROSE_FACTUAL: {
        "collections": ("docs", "incidents_rca"),
        "query_transform": "multi_query",
        "reranker_mode": "cross_encoder",
        "reflective": False,
        "dim_tier": "hot-interactive",
        "hydration_mode": "parent",
    },
    IntentClass.PROSE_COMPOUND: {
        "collections": ("docs", "code_chunks"),
        "query_transform": "decomposition",
        "reranker_mode": "cross_encoder",
        "reflective": True,
        "dim_tier": "hot-interactive",
        "hydration_mode": "parent",
    },
    IntentClass.PROSE_ABSTRACT_WHY: {
        "collections": ("docs", "incidents_rca"),
        "query_transform": "step_back",
        "reranker_mode": "cross_encoder",
        "reflective": True,
        "dim_tier": "hot-interactive",
        "hydration_mode": "parent",
    },
    IntentClass.METADATA_FILTER: {
        "collections": ("docs", "code_chunks"),
        "query_transform": "self_query",
        "reranker_mode": "cross_encoder",
        "reflective": False,
        "dim_tier": "hot-interactive",
        "hydration_mode": "parent",
    },
    IntentClass.TRACE_LOOKUP: {
        "collections": ("traces",),
        "query_transform": "identity",
        "reranker_mode": "heuristic",
        "reflective": False,
        "dim_tier": "warm-analytics",
        "hydration_mode": "parent",
    },
    IntentClass.INCIDENT_RECALL: {
        "collections": ("incidents_rca", "docs"),
        "query_transform": "step_back",
        "reranker_mode": "cross_encoder",
        "reflective": True,
        "dim_tier": "hot-interactive",
        "hydration_mode": "parent",
    },
    IntentClass.UNKNOWN: {
        "collections": ("code_chunks", "docs"),
        "query_transform": "identity",
        "reranker_mode": "cross_encoder",
        "reflective": False,
        "dim_tier": "hot-interactive",
        "hydration_mode": "none",
    },
}


# ---------------------------------------------------------------------------
# Latency-budget downgrade ladder (per ADR-064 §5)
# ---------------------------------------------------------------------------


# Approximate per-stage budgets in ms. Empirical tuning happens via
# ADR-061 nightly evals; these are the seed values.
_STAGE_BUDGETS_MS: Final[dict[str, dict[str, int]]] = {
    "reflective_loop": {"true": 2000, "false": 0},
    "reranker_mode": {
        "none": 0,
        "heuristic": 50,
        "cross_encoder": 250,
        "cross_encoder_late": 500,
    },
    "dim_tier": {
        "hot-interactive": 200,
        "warm-analytics": 100,
        "cold-batch": 50,
        "tiny-prefilter": 25,
    },
    "query_transform": {
        "identity": 0,
        "multi_query": 200,
        "hyde": 250,
        "step_back": 250,
        "decomposition": 400,
        "self_query": 200,
    },
}


def _implied_budget_ms(plan: dict[str, object]) -> int:
    return (
        _STAGE_BUDGETS_MS["reflective_loop"]["true" if plan["reflective"] else "false"]
        + _STAGE_BUDGETS_MS["reranker_mode"][str(plan["reranker_mode"])]
        + _STAGE_BUDGETS_MS["dim_tier"][str(plan["dim_tier"])]
        + _STAGE_BUDGETS_MS["query_transform"][str(plan["query_transform"])]
    )


_DOWNGRADE_LADDER = (
    # (key, target_value, label)
    ("reflective", False, "drop_reflective"),
    ("reranker_mode", "cross_encoder", "downgrade_reranker_to_cross_encoder"),
    ("reranker_mode", "heuristic", "downgrade_reranker_to_heuristic"),
    ("dim_tier", "warm-analytics", "downgrade_dim_tier_to_warm"),
    ("query_transform", "identity", "drop_query_transform"),
)


def _apply_downgrades(plan: dict[str, object], slo_budget_ms: int) -> tuple[dict[str, object], list[str]]:
    """Walk the downgrade ladder until ``_implied_budget_ms <= slo_budget_ms``.

    Returns the (possibly mutated) plan and the ordered list of downgrade
    labels applied.
    """

    plan = dict(plan)
    applied: list[str] = []
    for key, target, label in _DOWNGRADE_LADDER:
        if _implied_budget_ms(plan) <= slo_budget_ms:
            break
        if plan.get(key) == target:
            continue
        plan[key] = target
        applied.append(label)
    return plan, applied


# ---------------------------------------------------------------------------
# Public router class
# ---------------------------------------------------------------------------


class RetrievalRouter:
    """Map (query, hints) → ``RetrievalPlan`` deterministically.

    Threading: stateless. Safe for concurrent use.
    """

    def __init__(self) -> None:
        # Tier-2 weighted selection lives here; loaded lazily from
        # ``config/retrieval/router_weights.yaml`` when present. v1 keeps
        # the deterministic defaults from ADR-064 §3.
        self._weights: dict[str, dict[str, dict[str, float]]] = {}

    def route(
        self,
        query: str,
        hints: RouterHints | None = None,
    ) -> RetrievalPlan:
        intent = classify_intent(query)
        hints = hints or RouterHints()
        slo_budget = SLO_BUDGETS_MS[hints.slo]

        plan_dict = dict(_DEFAULT_PLANS[intent])

        # Caller-hint narrowing: drop disallowed collections / tiers.
        if hints.allowed_collections is not None:
            cols = tuple(
                c
                for c in plan_dict["collections"]
                if c in hints.allowed_collections  # type: ignore[operator]
            )
            if not cols and not hints.fail_on_unsatisfiable:
                # Fall back to whatever the caller permitted.
                cols = tuple(hints.allowed_collections)
            elif not cols:
                raise RouteUnsatisfiableError(
                    f"intent={intent.value} required collections "
                    f"{plan_dict['collections']!r} but caller allowed only "
                    f"{hints.allowed_collections!r}"
                )
            plan_dict["collections"] = cols

        if hints.allowed_tiers is not None and plan_dict["dim_tier"] not in hints.allowed_tiers:
            if hints.fail_on_unsatisfiable:
                raise RouteUnsatisfiableError(
                    f"intent={intent.value} requested tier "
                    f"{plan_dict['dim_tier']!r} but caller allowed only "
                    f"{hints.allowed_tiers!r}"
                )
            # Pick the first allowed tier as a safe default.
            plan_dict["dim_tier"] = hints.allowed_tiers[0]

        # Budget enforcement.
        plan_dict, downgrades = _apply_downgrades(plan_dict, slo_budget)
        if _implied_budget_ms(plan_dict) > slo_budget:
            if hints.fail_on_unsatisfiable:
                raise RouteUnsatisfiableError(
                    f"intent={intent.value} cannot fit slo={hints.slo.value} "
                    f"(implied={_implied_budget_ms(plan_dict)}ms, "
                    f"budget={slo_budget}ms)"
                )
            # Fall through: degraded plan still emitted.

        return RetrievalPlan(
            intent_class=intent,
            query_transform=str(plan_dict["query_transform"]),
            reranker_mode=str(plan_dict["reranker_mode"]),
            reflective=bool(plan_dict["reflective"]),
            dim_tier=str(plan_dict["dim_tier"]),
            collections=tuple(plan_dict["collections"]),  # type: ignore[arg-type]
            hydration_mode=str(plan_dict["hydration_mode"]),
            latency_budget_ms=min(_implied_budget_ms(plan_dict), slo_budget),
            route_reason=f"intent={intent.value}",
            downgrades=tuple(downgrades),
        )


__all__ = [
    "IntentClass",
    "RetrievalPlan",
    "RetrievalRouter",
    "RouteUnsatisfiableError",
    "RouterHints",
    "SLO",
    "SLO_BUDGETS_MS",
    "classify_intent",
]
