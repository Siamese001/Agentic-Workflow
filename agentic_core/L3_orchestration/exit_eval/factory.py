"""High-level factory — assemble a production-ready exit-eval pipeline.

Glues the moving pieces together so callers don't have to hand-wire each
time:

    rubric loading  →  grader binding  →  Gate construction  →
    BUS sink  +  OTel sink  →  consistency store  →  EvaluationPipeline

Intended consumer: ``agentic_core.L3_orchestration`` wiring code and
higher-level app entrypoints.

The factory requires callers to supply two things:

1. **JudgeProtocol factory** — callable returning a concrete judge
   adapter (Anthropic / OpenAI / HTTP). Kept as an injectable so tests
   can use the fake judge without adapter construction.
2. **BUS sink** — callable accepting ``BusRow`` instances. For local dev
   use ``bus.memory_sink()``; production uses JSONL or Kafka via
   ``bus.jsonl_sink(Path(...))``.

Every component beyond that is assembled here with spec-compliant
defaults (X1F hard sub-gates use the concrete adversarial detectors;
X1D groundedness/faithfulness wire the injected judge).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from agentic_core.L3_orchestration.exit_eval.bus import BusEmitter
from agentic_core.L3_orchestration.exit_eval.consistency import PassKStore
from agentic_core.L3_orchestration.exit_eval.gates import Gate
from agentic_core.L3_orchestration.exit_eval.graders.adversarial import (
    JailbreakGrader,
    PromptInjectionGrader,
    RobustnessGrader,
    SystemPromptLeakGrader,
)
from agentic_core.L3_orchestration.exit_eval.graders.base import Grader
from agentic_core.L3_orchestration.exit_eval.graders.code_based import (
    CitationGrader,
    SchemaGrader,
)
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import (
    JudgeProtocol,
    LLMJudgeGrader,
)
from agentic_core.L3_orchestration.exit_eval.otel_spans import (
    NoOpSpanSink,
    SpanSink,
)
from agentic_core.L3_orchestration.exit_eval.pipeline import (
    ConsistencyPolicy,
    EvaluationPipeline,
)
from agentic_core.L3_orchestration.exit_eval.otel_sdk_sink import build_span_sink
from agentic_core.L3_orchestration.exit_eval.rubric import load_rubric
from agentic_core.tracing.runtime_tracing import bootstrap_runtime_tracing

DEFAULT_RUBRIC_DIR = Path(__file__).resolve().parents[3] / "config" / "exit_eval_rubrics"

# Rubric-version SSOT — added 2026-04-25 per runtime-gate-coverage-hardening
# follow-up. Resolves which file (e.g. x1d_v1.yaml vs x1d_v2.yaml) the factory
# should load for each gate. Reads `_versions.yaml` at the rubric_dir root.
# Falls back to v1 for any gate not declared.
_VERSION_FILENAME = "_versions.yaml"
_FALLBACK_VERSION = "v1"


def _resolve_rubric_version(gate_id: str, rubric_dir: Path) -> str:
    """Resolve which version of a gate rubric to load.

    Order of precedence:
      1. Env var ``EXIT_EVAL_RUBRIC_VERSION_<GATE>`` (e.g. ``..._X1D=v2``)
      2. ``{rubric_dir}/_versions.yaml`` ``versions[<GATE>]`` block
      3. ``v1`` fallback (preserves pre-2026-04-25 behaviour)
    """
    import os  # noqa: PLC0415

    env_key = f"EXIT_EVAL_RUBRIC_VERSION_{gate_id.upper()}"
    env_val = os.environ.get(env_key, "").strip()
    if env_val:
        return env_val
    versions_path = rubric_dir / _VERSION_FILENAME
    if versions_path.exists():
        import yaml  # noqa: PLC0415

        try:
            data = yaml.safe_load(versions_path.read_text(encoding="utf-8")) or {}
            block = data.get("versions") or {}
            if isinstance(block, dict):
                v = block.get(gate_id) or block.get(gate_id.upper())
                if isinstance(v, str) and v.strip():
                    return v.strip()
        except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:  # guardian: allow-log-and-swallow -- version resolution failed: non-fatal; fallback version applied
            # Non-fatal — fall through to v1 default. Surface in logs.
            import logging  # noqa: PLC0415

            logging.getLogger(__name__).warning(
                "[exit_eval.factory] version resolution failed for %s: %s; using %s",
                gate_id,
                exc,
                _FALLBACK_VERSION,
            )
    return _FALLBACK_VERSION


# --------------------------------------------------------------------- #
# Sensible defaults for the code-based grader slots. Callers override by
# passing a ``grader_overrides`` mapping.
# --------------------------------------------------------------------- #


def _default_schema_grader() -> Grader:
    # Accept any non-empty dict for output — production callers override
    # with their request-schema validator.
    return SchemaGrader(
        lambda out: (True, "ok") if isinstance(out, dict) and out else (False, "empty or non-dict output")
    )


def _default_citation_grader() -> Grader:
    return CitationGrader()


@dataclass
class PipelineBundle:
    """Everything a caller needs to evaluate one run."""

    pipeline: EvaluationPipeline
    gates: list[Gate]
    consistency_store: PassKStore | None


def _build_graders_for_gate(
    gate: str,
    judge_factory: Callable[[], JudgeProtocol] | None,
    overrides: Mapping[str, Grader],
) -> dict[str, Grader]:
    """Produce the dimension → grader mapping for a known gate.

    Raises KeyError for any gate this factory doesn't know about; callers
    with custom gates must wire them directly.
    """
    if gate == "X1A":
        # Policy-match grader is caller-specific (reads baseline manifest);
        # require it to be overridden.
        if "policy_match" not in overrides:
            raise KeyError("X1A wiring requires overrides['policy_match'] — policy check is site-specific")
        return {"policy_match": overrides["policy_match"]}

    if gate == "X1B":
        return {
            "schema_complete": overrides.get("schema_complete", _default_schema_grader()),
            "format_fit": overrides.get("format_fit", _default_schema_grader()),
            "instruction_following_sys_over_user": (
                overrides["instruction_following_sys_over_user"]
                if "instruction_following_sys_over_user" in overrides
                else _llm_grader_or_required("instruction_following_sys_over_user", judge_factory)
            ),
        }

    if gate == "X1C":
        required = (
            "sandbox_ok",
            "mutation_authorized",
            "env_clean",
            "no_prior_trial_leakage",
        )
        missing = [d for d in required if d not in overrides]
        if missing:
            raise KeyError(f"X1C wiring requires overrides for: {missing} — safety checks are site-specific")
        return {d: overrides[d] for d in required}

    if gate == "X1D":
        return {
            "citation_support": overrides.get("citation_support", _default_citation_grader()),
            "groundedness": (
                overrides["groundedness"]
                if "groundedness" in overrides
                else _llm_grader_or_required("groundedness", judge_factory)
            ),
            "faithfulness": (
                overrides["faithfulness"]
                if "faithfulness" in overrides
                else _llm_grader_or_required("faithfulness", judge_factory)
            ),
        }

    if gate == "X1E":
        required_code = ("tool_selection_accuracy", "arg_precision", "handoff_correctness")
        missing = [d for d in required_code if d not in overrides]
        if missing:
            raise KeyError(f"X1E wiring requires overrides for trajectory-shape checks: {missing}")
        return {
            **{d: overrides[d] for d in required_code},
            "step_efficiency": overrides.get(
                "step_efficiency",
                _default_schema_grader(),  # deterministic placeholder
            ),
            "reasoning_coherence": (
                overrides["reasoning_coherence"]
                if "reasoning_coherence" in overrides
                else _llm_grader_or_required("reasoning_coherence", judge_factory)
            ),
        }

    if gate == "X1F":
        # Every X1F slot has a concrete deterministic detector — no site overrides needed.
        # Wiring covers BOTH X1F@v1 (5 dims) and X1F@v2 (7 dims). The Gate
        # constructor will only require graders that the loaded rubric declares,
        # so v1 ignores `indirect_injection_resistance` / `tool_result_faithfulness`
        # without complaint, and v2 picks them up.
        wiring: dict[str, Grader] = {
            "prompt_injection_resistance": overrides.get(
                "prompt_injection_resistance", PromptInjectionGrader()
            ),
            "system_prompt_leakage": overrides.get("system_prompt_leakage", SystemPromptLeakGrader()),
            "jailbreak_detection": overrides.get("jailbreak_detection", JailbreakGrader()),
            "bias_fairness": (
                overrides["bias_fairness"]
                if "bias_fairness" in overrides
                else _llm_grader_or_required("bias_fairness", judge_factory)
            ),
            "robustness": overrides.get("robustness", RobustnessGrader()),
            # X1F@v2 dimensions — added 2026-04-25 per
            # runtime-gate-coverage-hardening-7e3f1a (G7 closure).
            # Defaults reuse PromptInjectionGrader as a placeholder for indirect
            # injection (same attack family, differs only by surface); production
            # callers should override with a retrieved-context-aware detector.
            "indirect_injection_resistance": overrides.get(
                "indirect_injection_resistance", PromptInjectionGrader()
            ),
            "tool_result_faithfulness": (
                overrides["tool_result_faithfulness"]
                if "tool_result_faithfulness" in overrides
                else _llm_grader_or_required("tool_result_faithfulness", judge_factory)
            ),
        }
        # Strip dims the loaded rubric does not declare (so v1 callers still pass
        # the Gate constructor's "no extra graders" invariant). The caller will
        # always pass us all dims; the Gate filter happens in build_pipeline.
        return wiring

    raise KeyError(f"build_pipeline: unknown gate {gate!r}")


def _llm_grader_or_required(dimension: str, judge_factory: Callable[[], JudgeProtocol] | None) -> Grader:
    if judge_factory is None:
        raise KeyError(
            f"dimension {dimension!r} needs an LLM judge — "
            "pass judge_factory= or overrides[{dimension!r}]=<Grader>"
        )
    return LLMJudgeGrader(judge_factory())


def build_pipeline(
    gate_ids: list[str],
    *,
    bus_emitter: BusEmitter,
    judge_factory: Callable[[], JudgeProtocol] | None = None,
    grader_overrides: Mapping[str, Grader] | None = None,
    rubric_dir: Path | None = None,
    span_sink: SpanSink | None = None,
    consistency_store: PassKStore | None = None,
    consistency_policy: ConsistencyPolicy | None = None,
) -> PipelineBundle:
    """Assemble a pipeline over ``gate_ids`` (e.g. ``["X1A","X1B","X1D","X1F"]``).

    Defaults:
        rubric_dir: repo ``config/exit_eval_rubrics/``.
        span_sink: ``NoOpSpanSink`` if none passed.
        consistency_store: None (X1G off) unless caller passes one.

    Raises:
        KeyError: if a gate's wiring requires a site-specific grader the
            caller didn't supply, OR if a rubric yaml is missing.
    """
    rubric_dir = rubric_dir or DEFAULT_RUBRIC_DIR
    overrides = dict(grader_overrides or {})
    span_sink = span_sink or NoOpSpanSink()

    # X1G is a pipeline-level policy gate, not a grader-based Gate. When the
    # caller lists ``"X1G"`` in ``gate_ids`` they are enabling the commit-path
    # pass^k check, which requires both a consistency store and policy. Build
    # no Gate for it but validate wiring up-front so the error surfaces at
    # factory time rather than at first evaluate() call.
    x1g_enabled = False
    filtered_gate_ids: list[str] = []
    for gate_id in gate_ids:
        if gate_id == "X1G":
            x1g_enabled = True
            continue
        filtered_gate_ids.append(gate_id)

    if x1g_enabled:
        if not filtered_gate_ids:
            raise KeyError(
                "X1G is a pipeline-level consistency modifier and cannot "
                "be the only gate; include at least one of "
                "X1A/X1B/X1C/X1D/X1E/X1F alongside X1G."
            )
        if consistency_store is None or consistency_policy is None:
            raise KeyError(
                "X1G requested in gate_ids but consistency_store and/or "
                "consistency_policy is None; supply both to enable the "
                "commit-path pass^k gate per v5 §X1G."
            )
        # The x1g_v1.yaml rubric exists as a governance artifact documenting
        # the gate's shape; loading it validates the file is well-formed.
        x1g_rubric_path = rubric_dir / "x1g_v1.yaml"
        if not x1g_rubric_path.exists():
            raise KeyError(f"X1G rubric file missing: {x1g_rubric_path}")
        load_rubric(x1g_rubric_path)  # validate parseability; discard result

    gates: list[Gate] = []
    for gate_id in filtered_gate_ids:
        # Version-aware rubric load — SSOT in {rubric_dir}/_versions.yaml.
        # Defaults to v1 for any gate not declared in the SSOT (back-compat).
        version = _resolve_rubric_version(gate_id, rubric_dir)
        rubric_path = rubric_dir / f"{gate_id.lower()}_{version}.yaml"
        if not rubric_path.exists():
            raise KeyError(f"rubric file missing for {gate_id} (version={version}): {rubric_path}")
        rubric = load_rubric(rubric_path)
        graders = _build_graders_for_gate(gate_id, judge_factory, overrides)
        # Filter graders to the rubric's declared dim set so v1 rubrics do not
        # trip the Gate's "extra graders" invariant when the wiring builder
        # supplies a forward-compat superset (added 2026-04-25 for X1F@v1<->v2).
        declared = {d.name for d in rubric.dimensions}
        graders = {name: g for name, g in graders.items() if name in declared}
        gates.append(Gate(rubric, graders))

    pipeline = EvaluationPipeline(
        gates,
        bus_emitter=bus_emitter,
        span_sink=span_sink,
        consistency_store=consistency_store,
        consistency_policy=consistency_policy,
    )
    return PipelineBundle(pipeline=pipeline, gates=gates, consistency_store=consistency_store)


def build_evaluation_pipeline_with_tracing(
    gates: list[Gate],
    *,
    bus_emitter: BusEmitter,
    consistency_store: PassKStore | None = None,
    consistency_policy: ConsistencyPolicy | None = None,
    service_name: str = "exit_eval",
) -> EvaluationPipeline:
    """Runtime factory — build an ``EvaluationPipeline`` with a live span sink.

    Constructing ``EvaluationPipeline`` directly defaults to a ``NoOpSpanSink``
    (correct for unit/minimal contexts). This factory wires the Exit evaluation
    plane for *production runtime* instead:

    1. Calls :func:`bootstrap_runtime_tracing` **before** resolving a tracer, so
       a recording OTEL provider is installed first when the operator opted in
       (``OTEL_TRACES_EXPORTER`` set). External export stays env-gated / OFF by
       default.
    2. Injects ``build_span_sink(service_name=...)`` — a live OTel-SDK sink when
       OTel is importable, else a graceful ``NoOpSpanSink``.

    The pipeline stays fail-soft; nothing here raises on missing OTel. Direct
    ``EvaluationPipeline(...)`` construction is intentionally left
    no-op-by-default for tests and minimal environments.

    Args:
        gates: already-constructed gates (e.g. ``build_pipeline(...).gates``).
        bus_emitter: BUS sink for P-rows.
        consistency_store / consistency_policy: optional X1G commit-path wiring.
        service_name: OTEL service / tracer name for the span sink.
    """
    bootstrap_runtime_tracing()
    span_sink = build_span_sink(service_name=service_name)
    return EvaluationPipeline(
        gates,
        bus_emitter=bus_emitter,
        consistency_store=consistency_store,
        consistency_policy=consistency_policy,
        span_sink=span_sink,
    )


__all__ = [
    "PipelineBundle",
    "build_evaluation_pipeline_with_tracing",
    "build_pipeline",
]
