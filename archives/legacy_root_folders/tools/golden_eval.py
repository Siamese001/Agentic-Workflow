# FILE: 10_10/golden_eval.py
"""
Golden State Evaluator (v10_10 · Phase 3 — Batch D)
===================================================

This module provides a deterministic evaluation harness for the v10_10
agentic workflow.

It is deliberately *pure*:

    • No LLM calls.
    • No orchestration, execution, or planning.
    • Only consumes already‑materialised runtime artefacts
      (typically the final L4 state patch exported as JSON).

The main responsibilities are:

    1. Define *golden* evaluation scenarios that exercise the
       Phase‑3 control knobs and capabilities (G1–G37), in
       particular:

           • HYDE on vs HYDE off
           • RRF strategy variants
           • QA council size (1 vs N)
           • Correction‑loop depth (0 -> N)
           • Telemetry‑aware routing modes
           • Deterministic "golden mode" configuration

    2. Provide deterministic, machine‑verifiable scoring of a
       *single* workflow patch against a GoldenExpectation.

    3. Expose a small CLI suitable for CI/CD:

           python -m golden_eval \
             --patch run_output.json \
             --expectation golden_expectations.json \
             --scenario-id hyde_on_weighted \
             --out eval_report.json

The actual execution of the workflow (calling main_v10_10 or
run_batch_v10_10) is *not* handled here; that is the job of
simulation.py and separate test harnesses.  This module only
defines scenarios and evaluates data.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import json
import sys

from core.models.models import CostSnapshot
from observability import emit_golden_eval_event, get_all_events
from runtime.trace.trace_reconstruction import get_routing_trace


# =============================================================================
# Internal helpers
# =============================================================================

_MISSING = object()


class ModelLike:
    """
    Lightweight drop‑in replacement for a small subset of the Pydantic
    BaseModel API used elsewhere in the codebase.

    All evaluation models in this module are simple dataclasses that
    inherit from ModelLike, which provides:

        • model_dump() -> dict
        • model_dump_json(indent=2, by_alias=False) -> str

    This keeps golden_eval completely independent from Pydantic while
    preserving the familiar interface expected by upstream tooling.
    """

    # Pydantic v2 compatibility
    def model_dump(self) -> Dict[str, Any]:  # type: ignore[override]
        if is_dataclass(self):
            return asdict(self)  # type: ignore[arg-type]
        return dict(self.__dict__)

    def model_dump_json(
        self,
        indent: int = 2,
        by_alias: bool = False,  # kept for signature compatibility, unused
    ) -> str:  # type: ignore[override]
        return json.dumps(self.model_dump(), indent=indent, sort_keys=True)


def _as_mapping(obj: Any) -> Mapping[str, Any]:
    """
    Best‑effort view of an arbitrary object as a mapping.
    """
    if obj is None:
        return {}
    if isinstance(obj, Mapping):
        return obj
    # Pydantic v2 style
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()  # type: ignore[call-arg]
        except TypeError:
            # Older Pydantic
            pass
    if hasattr(obj, "dict"):
        try:
            return obj.dict()  # type: ignore[call-arg]
        except TypeError:
            pass
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return {}


def _safe_get_attr_or_item(obj: Any, name: str, default: Any = _MISSING) -> Any:
    """
    Helper that tries both attribute and mapping access.
    """
    if obj is None:
        return default
    if isinstance(obj, Mapping) and name in obj:
        return obj[name]
    if hasattr(obj, name):
        return getattr(obj, name)
    return default


def _dotted_get(obj: Any, path: str, default: Any = _MISSING) -> Any:
    """
    Generic dotted‑path lookup against nested dicts / models.

    Example:
        _dotted_get(patch, "config.knobs.hyde_enabled")
    """
    current: Any = obj
    for part in path.split("."):
        if current is None:
            return default
        if isinstance(current, Mapping):
            if part not in current:
                return default
            current = current[part]
        else:
            current = _safe_get_attr_or_item(current, part, default)
            if current is default:
                return default
    return current


def _normalize_title(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _count_where(items: Iterable[Any], predicate) -> int:
    return sum(1 for x in items if predicate(x))


def _summarise_resilience_events() -> Dict[str, Any]:
    """Build a coarse resilience summary from in-memory telemetry events.

    This is META-layer only and does not affect runtime behaviour.
    """

    summary: Dict[str, Any] = {
        "event_counts": {},
    }

    try:
        for evt in get_all_events():
            name = getattr(evt, "name", "") or "unknown"
            attrs = getattr(evt, "attributes", {}) or {}
            event_type = attrs.get("event_type", "")

            if event_type not in {"resilience_trace", "resilience_retry", "resilience_give_up", "resilience_breaker_open"} and not name.startswith("resilience_"):
                continue

            key = name or event_type or "unknown"
            summary["event_counts"][key] = summary["event_counts"].get(key, 0) + 1
    except Exception:
        # Evaluation helpers must never break golden evaluation.
        pass

    return summary


# =============================================================================
# Field‑level expectations
# =============================================================================


class Comparator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GE = "ge"
    LT = "lt"
    LE = "le"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    NON_EMPTY = "non_empty"
    APPROX = "approx"
    LEN_GE = "len_ge"
    LEN_LE = "len_le"


@dataclass
class FieldExpectation(ModelLike):
    """
    Generic field‑level expectation expressed as a dotted path into
    the state patch.

    Example JSON shape (for load_expectations):

        {
          "path": "config.knobs.hyde_enabled",
          "comparator": "eq",
          "expected": true,
          "weight": 2.0,
          "hard_fail": true,
          "description": "HYDE enabled in knob config"
        }
    """

    path: str
    comparator: Comparator = Comparator.EQ
    expected: Any = None
    weight: float = 1.0
    hard_fail: bool = False
    description: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FieldExpectation":
        data = dict(data)
        comp = data.get("comparator", Comparator.EQ)
        if not isinstance(comp, Comparator):
            data["comparator"] = Comparator(str(comp))
        return cls(**data)


# =============================================================================
# Golden expectations & scenarios
# =============================================================================


@dataclass
class GoldenExpectation(ModelLike):
    """
    Declarative description of what a single workflow run is expected
    to look like under a specific golden scenario.

    The expectation is intentionally high‑level and tolerant of minor
    implementation details; it focuses on invariants that should hold
    if the Phase‑3 capabilities (G1–G37) are wired correctly.
    """

    # Identity
    scenario_id: str
    description: str = ""
    tags: List[str] = field(default_factory=list)

    # Section / drafting expectations
    required_sections: List[str] = field(default_factory=list)
    min_section_coverage: float = 1.0  # 0–1 inclusive

    # Retrieval / RAG
    min_evidence: Optional[int] = None
    expect_used_hyde: Optional[bool] = None
    expect_rrf_strategy: Optional[str] = None  # "disabled" | "simple" | "weighted"
    # Council / correction
    expect_council_size: Optional[int] = None
    expect_correction_max_iterations: Optional[int] = None

    # Telemetry & routing
    expect_telemetry_routing_mode: Optional[str] = None
    require_telemetry: bool = False
    require_cost_snapshot: bool = False
    require_correction_audit: bool = False

    # QA / safety
    allowed_qa_failures: int = 0
    max_blocking_safety_findings: int = 0

    # Optional low‑level dotted expectations
    field_expectations: List[FieldExpectation] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GoldenExpectation":
        data = dict(data)
        fe_raw = data.get("field_expectations") or []
        if isinstance(fe_raw, list):
            data["field_expectations"] = [
                fx if isinstance(fx, FieldExpectation) else FieldExpectation.from_dict(fx)
                for fx in fe_raw
            ]
        tags = data.get("tags")
        if tags is None:
            data["tags"] = []
        return cls(**data)


@dataclass
class ScenarioKnobs(ModelLike):
    """
    Minimal, string‑only description of Phase‑3 knob settings for a
    scenario.  This mirrors Phase3Knobs from main_v10_10 but avoids
    importing runtime modules.

    These values are intended to be passed directly into
    main_v10_10.run_workflow by simulation.py.
    """

    hyde_enabled: bool
    rrf_strategy: str  # "disabled" | "simple" | "weighted"
    council_size: int
    correction_loop_max_iterations: int
    telemetry_routing_mode: str  # "disabled" | "log_only" | "enforced"
    rrf_weights: Optional[Dict[str, float]] = None


@dataclass
class GoldenScenario(ModelLike):
    """
    Complete description of a golden scenario used by simulation.py.

        • knobs      -> how to configure main_v10_10 / run_batch_v10_10
        • expectation -> how to evaluate the resulting state patch
    """

    scenario_id: str
    description: str
    knobs: ScenarioKnobs
    expectation: GoldenExpectation


# =============================================================================
# Evaluation metrics & reports
# =============================================================================


@dataclass
class EvalMetric(ModelLike):
    name: str
    score: float
    passed: bool
    reason: str
    weight: float = 1.0
    category: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalReport(ModelLike):
    scenario_id: str
    passed: bool
    total_score: float
    metrics: List[EvalMetric]
    summary: Dict[str, Any] = field(default_factory=dict)
    scenario_description: str = ""
    scenario_tags: List[str] = field(default_factory=list)

    @classmethod
    def from_metrics(
        cls,
        scenario_id: str,
        expectation: GoldenExpectation,
        metrics: List[EvalMetric],
        summary: Optional[Dict[str, Any]] = None,
    ) -> "EvalReport":
        if not metrics:
            total_score = 0.0
            passed = False
        else:
            num = sum(m.score * max(m.weight, 0.0) for m in metrics)
            denom = sum(max(m.weight, 0.0) for m in metrics) or 1.0
            total_score = max(0.0, min(1.0, num / denom))
            passed = all(m.passed for m in metrics)

        return cls(
            scenario_id=scenario_id,
            passed=passed,
            total_score=total_score,
            metrics=metrics,
            summary=summary or {},
            scenario_description=expectation.description,
            scenario_tags=list(expectation.tags),
        )


# =============================================================================
# Scenario registry (canonical golden scenarios)
# =============================================================================


def _build_default_scenarios() -> Dict[str, GoldenScenario]:
    """
    Canonical golden scenarios used in Phase‑3 testing.

    These are intentionally generic and only talk about knobs and
    observable invariants — they do not encode any specific user
    prompts or corpus content.
    """

    # Base set of required sections for all scenarios.
    default_sections = ["Introduction", "Answer", "Conclusion"]

    # 1) HYDE disabled, simple RRF, single‑agent council, no correction loop.
    knobs_baseline = ScenarioKnobs(
        hyde_enabled=False,
        rrf_strategy="simple",
        council_size=1,
        correction_loop_max_iterations=0,
        telemetry_routing_mode="log_only",
        rrf_weights=None,
    )
    expectation_baseline = GoldenExpectation(
        scenario_id="baseline_hyde_off_simple",
        description=(
            "Baseline run with HYDE disabled, simple RRF fusion, single QA "
            "agent, no correction loop, and telemetry in log‑only mode."
        ),
        tags=["baseline", "hyde_off", "rrf_simple", "council_1", "corr_0", "telemetry_log_only"],
        required_sections=list(default_sections),
        min_section_coverage=1.0,
        min_evidence=1,
        expect_used_hyde=False,
        expect_rrf_strategy="simple",
        expect_council_size=1,
        expect_correction_max_iterations=0,
        expect_telemetry_routing_mode="log_only",
        require_telemetry=True,
        require_cost_snapshot=True,
        require_correction_audit=False,
        allowed_qa_failures=0,
        max_blocking_safety_findings=0,
    )

    # 2) HYDE enabled with simple RRF (primarily tests HYDE plumbing).
    knobs_hyde_on = ScenarioKnobs(
        hyde_enabled=True,
        rrf_strategy="simple",
        council_size=1,
        correction_loop_max_iterations=0,
        telemetry_routing_mode="log_only",
        rrf_weights=None,
    )
    expectation_hyde_on = GoldenExpectation(
        scenario_id="hyde_on_simple",
        description=(
            "HYDE enabled with simple RRF, single QA agent, and no correction loop. "
            "Used to verify HYDE‑specific retrieval behaviour."
        ),
        tags=["hyde_on", "rrf_simple", "council_1", "corr_0", "telemetry_log_only"],
        required_sections=list(default_sections),
        min_section_coverage=1.0,
        min_evidence=1,
        expect_used_hyde=True,
        expect_rrf_strategy="simple",
        expect_council_size=1,
        expect_correction_max_iterations=0,
        expect_telemetry_routing_mode="log_only",
        require_telemetry=True,
        require_cost_snapshot=True,
        require_correction_audit=False,
        allowed_qa_failures=0,
        max_blocking_safety_findings=0,
    )

    # 3) HYDE disabled, weighted RRF, multi‑agent QA council, bounded correction.
    knobs_rrf_weighted_multi = ScenarioKnobs(
        hyde_enabled=False,
        rrf_strategy="weighted",
        council_size=3,
        correction_loop_max_iterations=2,
        telemetry_routing_mode="enforced",
        rrf_weights={"bm25": 0.6, "dense": 0.4},
    )
    expectation_rrf_weighted_multi = GoldenExpectation(
        scenario_id="hyde_off_rrf_weighted_council3",
        description=(
            "HYDE disabled, weighted RRF across BM25+dense retrieval, QA council of "
            "size 3, and correction loop allowing up to 2 iterations. Telemetry "
            "routing is enforced (dynamic routing informed by metrics)."
        ),
        tags=["hyde_off", "rrf_weighted", "council_3", "corr_2", "telemetry_enforced"],
        required_sections=list(default_sections),
        min_section_coverage=1.0,
        min_evidence=2,
        expect_used_hyde=False,
        expect_rrf_strategy="weighted",
        expect_council_size=3,
        expect_correction_max_iterations=2,
        expect_telemetry_routing_mode="enforced",
        require_telemetry=True,
        require_cost_snapshot=True,
        require_correction_audit=True,
        allowed_qa_failures=1,
        max_blocking_safety_findings=0,
    )

    # 4) HYDE enabled, weighted RRF, multi‑agent council, bounded correction.
    knobs_hyde_on_rrf_weighted_multi = ScenarioKnobs(
        hyde_enabled=True,
        rrf_strategy="weighted",
        council_size=3,
        correction_loop_max_iterations=2,
        telemetry_routing_mode="enforced",
        rrf_weights={"bm25": 0.5, "dense": 0.5},
    )
    expectation_hyde_on_rrf_weighted_multi = GoldenExpectation(
        scenario_id="hyde_on_rrf_weighted_council3",
        description=(
            "HYDE enabled together with weighted RRF and a QA council of size 3.  "
            "The correction loop is allowed up to 2 iterations with telemetry‑"
            "enforced routing."
        ),
        tags=["hyde_on", "rrf_weighted", "council_3", "corr_2", "telemetry_enforced"],
        required_sections=list(default_sections),
        min_section_coverage=1.0,
        min_evidence=2,
        expect_used_hyde=True,
        expect_rrf_strategy="weighted",
        expect_council_size=3,
        expect_correction_max_iterations=2,
        expect_telemetry_routing_mode="enforced",
        require_telemetry=True,
        require_cost_snapshot=True,
        require_correction_audit=True,
        allowed_qa_failures=1,
        max_blocking_safety_findings=0,
    )

    # 5) Deterministic "golden mode" profile.
    #    This assumes the runtime exposes a dedicated profile named "golden".
    knobs_golden_mode = ScenarioKnobs(
        hyde_enabled=False,
        rrf_strategy="simple",
        council_size=3,
        correction_loop_max_iterations=1,
        telemetry_routing_mode="log_only",
        rrf_weights=None,
    )
    expectation_golden_mode = GoldenExpectation(
        scenario_id="golden_mode",
        description=(
            "Deterministic golden‑mode configuration with fixed seeds and "
            "stable model choices. Intended for regression testing."
        ),
        tags=["golden_mode", "deterministic"],
        required_sections=list(default_sections),
        min_section_coverage=1.0,
        min_evidence=1,
        expect_used_hyde=False,
        expect_rrf_strategy="simple",
        expect_council_size=3,
        expect_correction_max_iterations=1,
        expect_telemetry_routing_mode="log_only",
        require_telemetry=True,
        require_cost_snapshot=True,
        require_correction_audit=True,
        allowed_qa_failures=0,
        max_blocking_safety_findings=0,
        field_expectations=[
            # These dotted paths intentionally talk about high‑level config
            # rather than deeply nested details so that they stay robust to
            # minor refactors of the underlying runtime.
            FieldExpectation(
                path="config.execution_profile_name",
                comparator=Comparator.EQ,
                expected="golden",
                weight=2.0,
                hard_fail=True,
                description="Golden execution profile should be active.",
            ),
            FieldExpectation(
                path="config.meta_profile_name",
                comparator=Comparator.EQ,
                expected="golden",
                weight=1.5,
                hard_fail=True,
                description="Golden meta‑profile should be active.",
            ),
            FieldExpectation(
                path="config.seed",
                comparator=Comparator.EQ,
                expected=42,
                weight=2.0,
                hard_fail=True,
                description="Deterministic seed must be 42 for golden mode.",
            ),
        ],
    )

    scenarios = [
        GoldenScenario(
            scenario_id=expectation_baseline.scenario_id,
            description=expectation_baseline.description,
            knobs=knobs_baseline,
            expectation=expectation_baseline,
        ),
        GoldenScenario(
            scenario_id=expectation_hyde_on.scenario_id,
            description=expectation_hyde_on.description,
            knobs=knobs_hyde_on,
            expectation=expectation_hyde_on,
        ),
        GoldenScenario(
            scenario_id=expectation_rrf_weighted_multi.scenario_id,
            description=expectation_rrf_weighted_multi.description,
            knobs=knobs_rrf_weighted_multi,
            expectation=expectation_rrf_weighted_multi,
        ),
        GoldenScenario(
            scenario_id=expectation_hyde_on_rrf_weighted_multi.scenario_id,
            description=expectation_hyde_on_rrf_weighted_multi.description,
            knobs=knobs_hyde_on_rrf_weighted_multi,
            expectation=expectation_hyde_on_rrf_weighted_multi,
        ),
        GoldenScenario(
            scenario_id=expectation_golden_mode.scenario_id,
            description=expectation_golden_mode.description,
            knobs=knobs_golden_mode,
            expectation=expectation_golden_mode,
        ),
    ]

    return {s.scenario_id: s for s in scenarios}


# Public registry that other modules (e.g. simulation.py) can import.
GOLDEN_SCENARIOS: Dict[str, GoldenScenario] = _build_default_scenarios()


# =============================================================================
# Core evaluation helpers
# =============================================================================


def _extract_sections(state_patch: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    # Prefer a flat "drafted_sections" key if present.
    sections = state_patch.get("drafted_sections")
    if not sections:
        drafting = state_patch.get("drafting") or {}
        sections = drafting.get("sections")

    if not isinstance(sections, list):
        return []

    out: List[Mapping[str, Any]] = []
    for item in sections:
        if not isinstance(item, Mapping):
            item = _as_mapping(item)
        out.append(item)
    return out


def _extract_rag_evidence(state_patch: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    evidence = state_patch.get("rag_evidence")
    if not evidence:
        rag = state_patch.get("rag") or {}
        evidence = rag.get("evidence")

    if not isinstance(evidence, list):
        return []

    out: List[Mapping[str, Any]] = []
    for item in evidence:
        if not isinstance(item, Mapping):
            item = _as_mapping(item)
        out.append(item)
    return out


def _extract_correction_state(state_patch: Mapping[str, Any]) -> Mapping[str, Any]:
    candidate = (
        state_patch.get("correction_loop_state")
        or state_patch.get("correction_state")
        or state_patch.get("correction")
        or state_patch.get("correction_loop")
    )
    return _as_mapping(candidate)


def _extract_knob(state_patch: Mapping[str, Any], knob_name: str) -> Any:
    """
    Attempt to recover a Phase‑3 knob value from the patch by checking
    several common locations.
    """

    # 1) Top‑level knobs
    knobs = state_patch.get("knobs") or state_patch.get("phase3_knobs")
    value = _safe_get_attr_or_item(knobs, knob_name, _MISSING)
    if value is not _MISSING:
        return value

    # 2) Config object
    config = state_patch.get("config") or state_patch.get("workflow_config")
    if config is not None:
        value = _safe_get_attr_or_item(config, knob_name, _MISSING)
        if value is not _MISSING:
            return value
        inner_knobs = _safe_get_attr_or_item(config, "knobs", _MISSING)
        if inner_knobs is not _MISSING:
            value = _safe_get_attr_or_item(inner_knobs, knob_name, _MISSING)
            if value is not _MISSING:
                return value

    # 3) Workflow metadata
    meta = state_patch.get("workflow_metadata") or state_patch.get("metadata")
    if meta is not None:
        for container_name in ("knobs", "phase3_knobs"):
            container = _safe_get_attr_or_item(meta, container_name, _MISSING)
            if container is not _MISSING:
                value = _safe_get_attr_or_item(container, knob_name, _MISSING)
                if value is not _MISSING:
                    return value

    # 4) Fallback: allow direct top‑level key
    if knob_name in state_patch:
        return state_patch[knob_name]

    return None


def _detect_telemetry(state_patch: Mapping[str, Any]) -> bool:
    telemetry = (
        state_patch.get("telemetry_summary")
        or state_patch.get("telemetry")
        or state_patch.get("telemetry_events")
    )
    if telemetry:
        return True
    # Some pipelines may record telemetry counts under observability.
    observability = state_patch.get("observability") or {}
    telemetry_counts = observability.get("telemetry_counts")
    return bool(telemetry_counts)


def _detect_cost_snapshot(state_patch: Mapping[str, Any]) -> bool:
    if any(
        key in state_patch
        for key in ("cost_snapshot", "cost", "token_usage", "usage")
    ):
        return True
    meta = state_patch.get("workflow_metadata") or {}
    return any(
        key in meta for key in ("cost_snapshot", "cost", "token_usage", "usage")
    )


def _detect_correction_audit(state_patch: Mapping[str, Any]) -> bool:
    return bool(
        state_patch.get("correction_audit_log")
        or state_patch.get("correction_events")
        or state_patch.get("correction_history")
    )


# -----------------------------------------------------------------------------
# Metric implementations
# -----------------------------------------------------------------------------


def _metric_sections(
    state_patch: Mapping[str, Any],
    expectation: GoldenExpectation,
) -> Optional[EvalMetric]:
    if not expectation.required_sections:
        return None

    sections = _extract_sections(state_patch)
    titles = {_normalize_title(str(s.get("title", ""))) for s in sections}
    required_norm = [_normalize_title(t) for t in expectation.required_sections]
    num_present = sum(1 for t in required_norm if t in titles)

    coverage = num_present / max(len(required_norm), 1)
    passed = coverage >= expectation.min_section_coverage

    return EvalMetric(
        name="sections_coverage",
        category="drafting",
        score=max(0.0, min(1.0, coverage)),
        passed=passed,
        weight=2.0,
        reason=f"{num_present}/{len(required_norm)} required sections present.",
        details={
            "required_sections": expectation.required_sections,
            "present_titles": sorted(titles),
            "coverage": coverage,
            "min_required": expectation.min_section_coverage,
        },
    )


def _metric_rag_and_hyde(
    state_patch: Mapping[str, Any],
    expectation: GoldenExpectation,
) -> List[EvalMetric]:
    metrics: List[EvalMetric] = []

    evidence = _extract_rag_evidence(state_patch)
    num_evidence = len(evidence)
    min_evidence = expectation.min_evidence

    if min_evidence is not None:
        ratio = num_evidence / max(min_evidence, 1)
        passed = num_evidence >= min_evidence
        metrics.append(
            EvalMetric(
                name="rag_evidence_coverage",
                category="retrieval",
                score=max(0.0, min(1.0, ratio)),
                passed=passed,
                weight=1.5,
                reason=f"{num_evidence} evidence items (min required {min_evidence}).",
                details={"num_evidence": num_evidence, "min_required": min_evidence},
            )
        )

    if expectation.expect_used_hyde is not None:
        # Prefer explicit flag, then fall back to RAGResult.used_hyde.
        used_hyde = state_patch.get("rag_used_hyde")
        if used_hyde is None:
            rag_obj = state_patch.get("rag") or {}
            used_hyde = _safe_get_attr_or_item(rag_obj, "used_hyde", False)

        used_hyde_bool = bool(used_hyde)
        passed = used_hyde_bool == expectation.expect_used_hyde
        metrics.append(
            EvalMetric(
                name="hyde_usage",
                category="retrieval",
                score=1.0 if passed else 0.0,
                passed=passed,
                weight=2.0,
                reason=(
                    f"HYDE usage is {used_hyde_bool!r}, "
                    f"expected {expectation.expect_used_hyde!r}."
                ),
                details={
                    "used_hyde": used_hyde_bool,
                    "expected_used_hyde": expectation.expect_used_hyde,
                },
            )
        )

    # RRF strategy & council size are validated in a separate helper.
    return metrics


def _metric_rrf_and_council(
    state_patch: Mapping[str, Any],
    expectation: GoldenExpectation,
) -> List[EvalMetric]:
    metrics: List[EvalMetric] = []

    # RRF strategy
    if expectation.expect_rrf_strategy is not None:
        # Try several locations for RRF strategy.
        actual_strategy = (
            _extract_knob(state_patch, "rrf_strategy")
            or _dotted_get(state_patch, "retrieval_config.rrf_strategy")
            or _dotted_get(state_patch, "retrieval.rrf_strategy")
            or state_patch.get("rrf_strategy")
        )
        passed = str(actual_strategy) == str(expectation.expect_rrf_strategy)
        metrics.append(
            EvalMetric(
                name="rrf_strategy",
                category="retrieval",
                score=1.0 if passed else 0.0,
                passed=passed,
                weight=1.5,
                reason=(
                    f"RRF strategy is {actual_strategy!r}, "
                    f"expected {expectation.expect_rrf_strategy!r}."
                ),
                details={
                    "actual": actual_strategy,
                    "expected": expectation.expect_rrf_strategy,
                },
            )
        )

    # Council size
    if expectation.expect_council_size is not None:
        actual_council_size = (
            _extract_knob(state_patch, "council_size")
            or _dotted_get(state_patch, "retrieval_config.qa_council_size")
            or _dotted_get(state_patch, "retrieval.qa_council_size")
            or state_patch.get("council_size")
        )
        try:
            actual_council_size_int = int(actual_council_size)
        except (TypeError, ValueError):
            actual_council_size_int = -1

        passed = actual_council_size_int == int(expectation.expect_council_size)
        metrics.append(
            EvalMetric(
                name="qa_council_size",
                category="qa",
                score=1.0 if passed else 0.0,
                passed=passed,
                weight=1.5,
                reason=(
                    f"QA council size is {actual_council_size_int}, "
                    f"expected {expectation.expect_council_size}."
                ),
                details={
                    "actual": actual_council_size_int,
                    "expected": expectation.expect_council_size,
                },
            )
        )

    return metrics


def _metric_correction_loop(
    state_patch: Mapping[str, Any],
    expectation: GoldenExpectation,
) -> Optional[EvalMetric]:
    corr = _extract_correction_state(state_patch)
    if not corr:
        if expectation.expect_correction_max_iterations is None:
            return None
        # No correction info when we expected some -> hard fail metric.
        return EvalMetric(
            name="correction_loop_state_missing",
            category="correction",
            score=0.0,
            passed=False,
            weight=2.0,
            reason="Correction loop state not present in patch.",
            details={},
        )

    iteration = corr.get("iteration", 0)
    max_iterations = corr.get("max_iterations", iteration)

    expected_max = expectation.expect_correction_max_iterations
    if expected_max is None:
        # Only validate basic invariant.
        passed = iteration <= max_iterations
        score = 1.0 if passed else 0.0
        reason = (
            "Correction loop iteration within configured limit."
            if passed
            else "Correction loop iteration exceeded configured limit."
        )
    else:
        passed = (max_iterations == expected_max) and (iteration <= expected_max)
        score = 1.0 if passed else 0.0
        reason = (
            f"Correction loop iteration={iteration}, max_iterations={max_iterations}, "
            f"expected max={expected_max}."
        )

    return EvalMetric(
        name="correction_loop",
        category="correction",
        score=score,
        passed=passed,
        weight=1.5,
        reason=reason,
        details={
            "iteration": iteration,
            "max_iterations": max_iterations,
            "expected_max_iterations": expected_max,
            "terminated_reason": corr.get("terminated_reason"),
        },
    )


def _metric_qa(
    state_patch: Mapping[str, Any],
    expectation: GoldenExpectation,
) -> Optional[EvalMetric]:
    qa_findings = state_patch.get("qa_findings") or []
    if not isinstance(qa_findings, list):
        return None

    num_total = len(qa_findings)
    num_failed = _count_where(
        qa_findings,
        lambda f: not bool(_as_mapping(f).get("passed", False)),
    )

    allowed = max(expectation.allowed_qa_failures, 0)
    passed = num_failed <= allowed
    score = 1.0 if passed else 0.0

    return EvalMetric(
        name="qa_failures",
        category="qa",
        score=score,
        passed=passed,
        weight=1.5,
        reason=(
            f"{num_failed}/{num_total} QA checks failed; "
            f"allowed <= {allowed}."
        ),
        details={
            "num_failed": num_failed,
            "num_total": num_total,
            "allowed_qa_failures": allowed,
        },
    )


def _metric_safety(
    state_patch: Mapping[str, Any],
    expectation: GoldenExpectation,
) -> List[EvalMetric]:
    metrics: List[EvalMetric] = []

    safety_findings = state_patch.get("safety_findings") or []
    if not isinstance(safety_findings, list):
        safety_findings = []

    num_blocking = _count_where(
        safety_findings,
        lambda f: bool(_as_mapping(f).get("blocking", False)),
    )

    max_blocking = max(expectation.max_blocking_safety_findings, 0)
    passed_safety = num_blocking <= max_blocking

    metrics.append(
        EvalMetric(
            name="safety_blocking_findings",
            category="safety",
            score=1.0 if passed_safety else 0.0,
            passed=passed_safety,
            weight=2.0,
            reason=(
                f"{num_blocking} blocking safety findings "
                f"(max allowed {max_blocking})."
            ),
            details={
                "num_blocking": num_blocking,
                "max_allowed": max_blocking,
            },
        )
    )

    # Gate consistency: if blocking findings exist, safety_passed must be False.
    safety_passed_flag = bool(state_patch.get("safety_passed", False))
    expected_gate = num_blocking == 0
    gate_consistent = safety_passed_flag == expected_gate

    metrics.append(
        EvalMetric(
            name="safety_gate_consistency",
            category="safety",
            score=1.0 if gate_consistent else 0.0,
            passed=gate_consistent,
            weight=1.5,
            reason=(
                "Safety gate consistent with findings."
                if gate_consistent
                else "Safety gate inconsistent with blocking findings."
            ),
            details={
                "safety_passed": safety_passed_flag,
                "num_blocking": num_blocking,
            },
        )
    )

    return metrics


def _metric_telemetry_and_cost(
    state_patch: Mapping[str, Any],
    expectation: GoldenExpectation,
) -> List[EvalMetric]:
    metrics: List[EvalMetric] = []

    # Telemetry routing mode knob.
    if expectation.expect_telemetry_routing_mode is not None:
        actual_mode = (
            _extract_knob(state_patch, "telemetry_routing_mode")
            or _dotted_get(state_patch, "config.telemetry_routing_mode")
            or state_patch.get("telemetry_routing_mode")
        )
        passed = str(actual_mode) == str(expectation.expect_telemetry_routing_mode)
        metrics.append(
            EvalMetric(
                name="telemetry_routing_mode",
                category="telemetry",
                score=1.0 if passed else 0.0,
                passed=passed,
                weight=1.5,
                reason=(
                    f"Telemetry routing mode is {actual_mode!r}, "
                    f"expected {expectation.expect_telemetry_routing_mode!r}."
                ),
                details={
                    "actual": actual_mode,
                    "expected": expectation.expect_telemetry_routing_mode,
                },
            )
        )

    # Presence of telemetry events / summary.
    if expectation.require_telemetry:
        has_telemetry = _detect_telemetry(state_patch)
        metrics.append(
            EvalMetric(
                name="telemetry_present",
                category="telemetry",
                score=1.0 if has_telemetry else 0.0,
                passed=has_telemetry,
                weight=1.0,
                reason=(
                    "Telemetry events present in patch."
                    if has_telemetry
                    else "Telemetry events missing from patch."
                ),
                details={},
            )
        )

    # Presence of cost snapshot.
    if expectation.require_cost_snapshot:
        has_cost = _detect_cost_snapshot(state_patch)
        metrics.append(
            EvalMetric(
                name="cost_snapshot_present",
                category="cost",
                score=1.0 if has_cost else 0.0,
                passed=has_cost,
                weight=1.0,
                reason=(
                    "Cost snapshot present in patch."
                    if has_cost
                    else "Cost snapshot missing from patch."
                ),
                details={},
            )
        )

    # Presence of correction audit events.
    if expectation.require_correction_audit:
        has_audit = _detect_correction_audit(state_patch)
        metrics.append(
            EvalMetric(
                name="correction_audit_present",
                category="correction",
                score=1.0 if has_audit else 0.0,
                passed=has_audit,
                weight=1.0,
                reason=(
                    "Correction audit log present in patch."
                    if has_audit
                    else "Correction audit log missing from patch."
                ),
                details={},
            )
        )

    return metrics


def _metric_field_expectations(
    state_patch: Mapping[str, Any],
    field_expectations: List[FieldExpectation],
) -> List[EvalMetric]:
    metrics: List[EvalMetric] = []

    for fe in field_expectations:
        value = _dotted_get(state_patch, fe.path, default=_MISSING)

        if value is _MISSING:
            passed = False
            score = 0.0
            reason = f"Missing field at path '{fe.path}'."
        else:
            passed = _apply_comparator(value, fe)
            score = 1.0 if passed else 0.0
            reason = (
                f"Field '{fe.path}' satisfies {fe.comparator.value}."
                if passed
                else f"Field '{fe.path}' violates expectation {fe.comparator.value}."
            )

        metrics.append(
            EvalMetric(
                name=f"field:{fe.path}",
                category="field_expectation",
                score=score,
                passed=passed,
                weight=fe.weight,
                reason=reason,
                details={
                    "path": fe.path,
                    "comparator": fe.comparator.value,
                    "expected": fe.expected,
                    "value": None if value is _MISSING else value,
                    "hard_fail": fe.hard_fail,
                },
            )
        )

    return metrics


def _apply_comparator(value: Any, fe: FieldExpectation) -> bool:
    comp = fe.comparator
    expected = fe.expected

    if comp is Comparator.EXISTS:
        return value is not _MISSING

    if comp is Comparator.NON_EMPTY:
        if value is _MISSING:
            return False
        if isinstance(value, (str, list, dict, tuple, set)):
            return len(value) > 0
        return bool(value)

    if comp is Comparator.LEN_GE:
        try:
            return len(value) >= int(expected)
        except Exception:
            return False

    if comp is Comparator.LEN_LE:
        try:
            return len(value) <= int(expected)
        except Exception:
            return False

    if comp is Comparator.EQ:
        return value == expected

    if comp is Comparator.NE:
        return value != expected

    if comp is Comparator.GT:
        try:
            return float(value) > float(expected)
        except Exception:
            return False

    if comp is Comparator.GE:
        try:
            return float(value) >= float(expected)
        except Exception:
            return False

    if comp is Comparator.LT:
        try:
            return float(value) < float(expected)
        except Exception:
            return False

    if comp is Comparator.LE:
        try:
            return float(value) <= float(expected)
        except Exception:
            return False

    if comp is Comparator.CONTAINS:
        try:
            return expected in value
        except Exception:
            return False

    if comp is Comparator.NOT_CONTAINS:
        try:
            return expected not in value
        except Exception:
            return False

    if comp is Comparator.IN:
        try:
            return value in expected  # type: ignore[operator]
        except Exception:
            return False

    if comp is Comparator.NOT_IN:
        try:
            return value not in expected  # type: ignore[operator]
        except Exception:
            return False

    if comp is Comparator.APPROX:
        try:
            # Fixed tolerance; can be adjusted if needed by changing weight semantics.
            tol = 1e-6
            return abs(float(value) - float(expected)) <= tol
        except Exception:
            return False

    # Fallback: fail closed.
    return False


# =============================================================================
# Public evaluation API
# =============================================================================


def evaluate_patch(
    state_patch: Mapping[str, Any],
    expectation: GoldenExpectation,
) -> EvalReport:
    """
    Evaluate a single state patch (typically final_state_patch from L3/L4)
    against a GoldenExpectation.

    The `state_patch` is expected to be shaped approximately like:

        {
            "strategy_text": str | None,
            "rag_evidence": [ { "text": ..., "score": ..., "source": ... }, ... ],
            "drafted_sections": [ { "title": ..., "text": ..., ... }, ... ],
            "qa_findings": [ { "id": ..., "passed": bool, ... }, ... ],
            "safety_findings": [ { "id": ..., "category": ..., "blocking": bool, ... }, ... ],
            "correction_loop_state": {
                "iteration": int,
                "max_iterations": int,
                "surfaces_triggered": [...],
                "last_signal": str | None,
                "terminated_reason": str | None,
            },
            "safety_passed": bool,
            "telemetry_summary": ...,
            "cost_snapshot": ...,
        }

    Exact keys are not required; the evaluator uses best‑effort extraction
    and will mark missing data as failing individual metrics with an
    explanatory reason.
    """
    patch_map = _as_mapping(state_patch)
    metrics: List[EvalMetric] = []

    # 1. Sections
    m_sections = _metric_sections(patch_map, expectation)
    if m_sections is not None:
        metrics.append(m_sections)

    # 2. RAG / HYDE
    metrics.extend(_metric_rag_and_hyde(patch_map, expectation))

    # 3. RRF & council size
    metrics.extend(_metric_rrf_and_council(patch_map, expectation))

    # 4. Correction loop
    m_corr = _metric_correction_loop(patch_map, expectation)
    if m_corr is not None:
        metrics.append(m_corr)

    # 5. QA
    m_qa = _metric_qa(patch_map, expectation)
    if m_qa is not None:
        metrics.append(m_qa)

    # 6. Safety
    metrics.extend(_metric_safety(patch_map, expectation))

    # 7. Telemetry / cost / correction audit
    metrics.extend(_metric_telemetry_and_cost(patch_map, expectation))

    # 8. Arbitrary field expectations
    if expectation.field_expectations:
        metrics.extend(
            _metric_field_expectations(patch_map, expectation.field_expectations)
        )

    report = EvalReport.from_metrics(
        scenario_id=expectation.scenario_id,
        expectation=expectation,
        metrics=metrics,
        summary={
            "required_sections": expectation.required_sections,
            "min_section_coverage": expectation.min_section_coverage,
            "allowed_qa_failures": expectation.allowed_qa_failures,
            "max_blocking_safety_findings": expectation.max_blocking_safety_findings,
        },
    )

    # Phase-4: emit a GoldenEvalEvent for observability (best-effort only).
    try:
        workflow_id = _dotted_get(patch_map, "workflow_id", default=None)
        if workflow_id is None:
            workflow_id = patch_map.get("workflow_id")
        if workflow_id is None:
            workflow_id = "unknown"

        routing_trace = get_routing_trace() or None
        resilience_summary = _summarise_resilience_events()
        if not resilience_summary.get("event_counts"):
            resilience_summary = None

        raw_cost = patch_map.get("cost_snapshot")
        cost_snapshot_obj: Optional[CostSnapshot] = None
        if isinstance(raw_cost, Mapping):
            try:
                cost_snapshot_obj = CostSnapshot(**raw_cost)  # type: ignore[arg-type]
            except Exception:
                cost_snapshot_obj = None

        emit_golden_eval_event(
            workflow_id=str(workflow_id),
            scenario_id=expectation.scenario_id,
            passed=report.passed,
            score=report.total_score,
            summary=report.summary,
            routing_trace=routing_trace,
            council_summary=None,
            resilience_summary=resilience_summary,
            cost_snapshot=cost_snapshot_obj,
        )
    except Exception:
        # Observability must not break evaluation.
        pass

    return report


# =============================================================================
# JSON I/O helpers
# =============================================================================


def load_expectations(path: str | Path) -> List[GoldenExpectation]:
    """
    Load GoldenExpectation objects from a JSON file.

    Supported shapes:

        1) JSON array of expectation objects:
            [
              { "scenario_id": "...", ... },
              { "scenario_id": "...", ... }
            ]

        2) JSON object mapping scenario_id -> expectation object:
            {
              "scenario_a": { "required_sections": [...], ... },
              "scenario_b": { ... }
            }

    In the second form the scenario_id key will be injected into the
    expectation object if missing.
    """
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))

    records: List[Dict[str, Any]] = []

    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, Mapping):
                raise ValueError("Each expectation must be a JSON object.")
            records.append(dict(item))
    elif isinstance(raw, Mapping):
        for scenario_id, cfg in raw.items():
            if not isinstance(cfg, Mapping):
                raise ValueError("Each expectation must be a JSON object.")
            rec = dict(cfg)
            rec.setdefault("scenario_id", str(scenario_id))
            records.append(rec)
    else:
        raise ValueError(
            "Expectation JSON must be either an array of objects or an "
            "object mapping scenario_id -> expectation."
        )

    return [GoldenExpectation.from_dict(r) for r in records]


def save_report(report: EvalReport, path: str | Path) -> None:
    """
    Save an EvalReport to a JSON file.
    """
    path = Path(path)
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")


# =============================================================================
# CLI entrypoint
# =============================================================================


def _select_expectation(
    expectations: List[GoldenExpectation],
    scenario_id: Optional[str],
) -> GoldenExpectation:
    if not expectations:
        raise ValueError("No expectations were loaded.")

    if scenario_id is None:
        if len(expectations) == 1:
            return expectations[0]
        raise ValueError(
            "Multiple expectations available; please provide --scenario-id."
        )

    for exp in expectations:
        if exp.scenario_id == scenario_id:
            return exp

    raise ValueError(f"No expectation with scenario_id={scenario_id!r} found.")


def _load_patch(path: str | Path) -> Mapping[str, Any]:
    """
    Load a patch JSON file.

    Supported shapes:
        • Single JSON object -> returned as-is.
        • JSON object mapping scenario_id -> patch -> caller should
          select by scenario_id before passing to evaluate_patch.
    """
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, Mapping):
        return raw
    raise ValueError("Patch JSON must be a single JSON object (mapping).")


def _cli(argv: Optional[Sequence[str]] = None) -> None:
    """
    Simple CLI intended for CI pipelines.

    Example:

        python -m golden_eval \
            --patch state_patch.json \
            --expectation golden_expectations.json \
            --scenario-id hyde_on_rrf_weighted_council3 \
            --out eval_report.json

    If --expectation is omitted or set to the literal string "builtin",
    the built‑in GOLDEN_SCENARIOS registry is used.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Golden State Evaluator (v10_10)")
    parser.add_argument("--patch", required=True, help="Path to state_patch JSON.")
    parser.add_argument(
        "--expectation",
        required=False,
        help="Path to GoldenExpectation JSON. "
        'If omitted or set to "builtin", built‑in scenarios are used.',
    )
    parser.add_argument(
        "--scenario-id",
        required=False,
        help="Scenario identifier to select within the expectations.",
    )
    parser.add_argument(
        "--out",
        required=False,
        help="Optional path to write EvalReport JSON; defaults to stdout.",
    )

    args = parser.parse_args(argv)

    try:
        patch_data = _load_patch(args.patch)

        # Determine expectations source.
        if args.expectation is None or args.expectation == "builtin":
            if not args.scenario_id:
                raise ValueError(
                    "When using built‑in scenarios you must provide --scenario-id."
                )
            scenario = GOLDEN_SCENARIOS.get(args.scenario_id)
            if scenario is None:
                raise ValueError(
                    f"Unknown built‑in scenario_id {args.scenario_id!r}. "
                    f"Available: {sorted(GOLDEN_SCENARIOS.keys())}"
                )
            expectation = scenario.expectation
        else:
            expectations = load_expectations(args.expectation)
            expectation = _select_expectation(expectations, args.scenario_id)

        report = evaluate_patch(patch_data, expectation)

        if args.out:
            save_report(report, args.out)
        else:
            print(report.model_dump_json(indent=2))

        # Exit non‑zero if failed.
        sys.exit(0 if report.passed else 2)

    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"Golden eval failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI
    _cli()




