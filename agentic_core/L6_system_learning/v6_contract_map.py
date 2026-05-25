"""V6 Contract Ownership Map — programmatic encoding of v6 lines 291-308.

The v6 spec assigns each of the 14 phases (S1A..S4D) to authoritative
engines. This module encodes that map as importable Python so that:

1. CI can verify each named engine actually exists in the repo.
2. Drift between the spec and implementation is detected automatically.
3. Tooling can reverse-look up the v6 phase responsible for a given engine.

The encoding deliberately uses dotted import paths (e.g.
``"agentic_core.L6_system_learning.engines.telemetry_consumer"``) rather than class names so
the contract verifier only needs ``importlib.util.find_spec`` to confirm
presence — no instantiation, no side-effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class V6PhaseContract:
    """One row of the v6 contract ownership map.

    Attributes
    ----------
    phase_id : ``"S1A"``..``"S4D"``.
    title : v6-prose phase title (e.g. ``"Gather Exhaust"``).
    contract_description : verbatim authoritative-contract column from v6.
    modules : tuple of importable dotted module paths providing the contract.
    """

    phase_id: str
    title: str
    contract_description: str
    modules: tuple[str, ...]


_V6_CONTRACT_RAW: tuple[V6PhaseContract, ...] = (
    V6PhaseContract(
        phase_id="S1A",
        title="Gather Exhaust",
        contract_description="telemetry consumer, historical ingestion, OTel store adapter, prompt tracer",
        modules=(
            "agentic_core.L6_system_learning.engines.telemetry_consumer",
            "agentic_core.L6_system_learning.engines.historical_ingestion_orchestrator",
            "agentic_core.L6_system_learning.engines.historical_backfill_engine",
            "agentic_core.L6_system_learning.engines.prompt_execution_tracer",
            "agentic_core.L6_observability.otel_runtime_ingest",
        ),
    ),
    V6PhaseContract(
        phase_id="S1B",
        title="Normalize Evidence",
        contract_description="trace feature extractor, meta-learning inbox, lineage binder",
        modules=(
            "agentic_core.L6_system_learning.engines.trace_feature_extractor",
            "agentic_core.L6_system_learning.engines.meta_learning_bus",
            "agentic_core.L6_system_learning.engines.prompt_provenance_builder",
            "agentic_core.L6_system_learning.engines.meta_learning_replay_binding",
        ),
    ),
    V6PhaseContract(
        phase_id="S1C",
        title="Observer Law",
        contract_description="surface isolation validator, stage barrier enforcer, invariant checks",
        modules=(
            "agentic_core.L6_system_learning.engines.surface_isolation_validator",
            "agentic_core.L6_system_learning.engines.stage_barrier_enforcer",
        ),
    ),
    V6PhaseContract(
        phase_id="S2A",
        title="Outcome Evals",
        contract_description="outcome evaluator, groundedness evaluator, citation/support scorer",
        modules=(
            "agentic_core.L6_system_learning.engines.outcome_evaluation_engine",
            "agentic_core.L6_observability.utils.evaluation.rag_evaluators",
        ),
    ),
    V6PhaseContract(
        phase_id="S2B",
        title="Trajectory Evals",
        contract_description="trajectory evaluator, trace rubric scorer, retry/thrash detector",
        modules=(
            "agentic_core.L6_system_learning.engines.trajectory_evaluation_engine",
            "agentic_core.L6_system_learning.engines.trajectory_divergence_scorer",
        ),
    ),
    V6PhaseContract(
        phase_id="S2C",
        title="Governance Regression",
        contract_description="gate regression checker, prompt drift detector, shadow drift analyzer",
        modules=(
            "agentic_core.L6_system_learning.engines.g_gate_regression_checker",
            "agentic_core.L6_system_learning.engines.prompt_drift_detector",
            "agentic_core.L6_system_learning.engines.shadow_drift_analyzer",
        ),
    ),
    V6PhaseContract(
        phase_id="S2D",
        title="Human Calibration",
        contract_description="human calibration engine, HITL decision logger, golden-set review",
        modules=(
            "agentic_core.L6_system_learning.engines.human_calibration_engine",
            "agentic_core.L6_system_learning.engines.hitl_decision_logger",
        ),
    ),
    V6PhaseContract(
        phase_id="S3A",
        title="Signal Fusion",
        contract_description="signal aggregator, signal grouping, BUS P / BUS T fusion",
        modules=(
            "agentic_core.L6_system_learning.engines.signal_aggregator_engine",
            "agentic_core.L6_system_learning.engines.signal_grouping_engine",
        ),
    ),
    V6PhaseContract(
        phase_id="S3B",
        title="Incident RCA",
        contract_description="RCA engine, cluster analyzer, pattern analysis",
        modules=(
            "agentic_core.L6_system_learning.engines.rca_engine",
            "agentic_core.L6_system_learning.engines.rca_cluster_engine",
            "agentic_core.L6_system_learning.engines.pattern_analysis_engine",
        ),
    ),
    V6PhaseContract(
        phase_id="S3C",
        title="Rule Drafting",
        contract_description="prompt proposer, policy proposer, rubric/config/retrieval-profile proposer",
        modules=(
            "agentic_core.L6_system_learning.engines.rule_drafting_engine",
            "agentic_core.L6_system_learning.engines.l1_model_proposer",
            "agentic_core.L6_system_learning.engines.l5_policy_proposer",
            "agentic_core.L6_system_learning.engines.rag_proposer",
            "agentic_core.L6_system_learning.engines.retrieval_profile_proposal",
        ),
    ),
    V6PhaseContract(
        phase_id="S4A",
        title="Gauntlet",
        contract_description="approval gauntlet, deterministic replay, regression runner, retrieval replay check",
        modules=(
            "agentic_core.L6_system_learning.engines.approval_gauntlet_engine",
            "agentic_core.L6_system_learning.engines.deterministic_replay_engine",
            "agentic_core.L6_system_learning.engines.gauntlet_gate",
            "agentic_core.L6_system_learning.engines.retrieval_profile_replay_check",
        ),
    ),
    V6PhaseContract(
        phase_id="S4B",
        title="Approve / Reject",
        contract_description="approval gate, system-learning admission gate, eval freshness gate",
        modules=(
            "agentic_core.L6_system_learning.engines.system_learning_admission_gate",
            "agentic_core.L6_system_learning.engines.eval_freshness_gate",
            "agentic_core.L6_system_learning.engines.eval_gated_l4_writer",
        ),
    ),
    V6PhaseContract(
        phase_id="S4C",
        title="UWG Master Clerk",
        contract_description="L4 state writer, L4 audit reader, L4 version store",
        modules=(
            "agentic_core.L6_system_learning.engines.l4_state_writer",
            "agentic_core.L6_system_learning.engines.l4_audit_reader",
            "agentic_core.L6_system_learning.engines.l4_version_store",
        ),
    ),
    V6PhaseContract(
        phase_id="S4D",
        title="Ledger Proof",
        contract_description="replay binding, state digest, startup integrity, rollout receipt generator",
        modules=(
            "agentic_core.L6_system_learning.engines.meta_learning_replay_binding",
            "agentic_core.L6_system_learning.engines.meta_learning_state_digest",
            "agentic_core.L6_system_learning.engines.faiss_startup_integrity",
        ),
    ),
)


V6_CONTRACT_MAP: Mapping[str, V6PhaseContract] = MappingProxyType(
    {row.phase_id: row for row in _V6_CONTRACT_RAW}
)
"""Frozen registry, keyed by phase id (``S1A``..``S4D``)."""


def all_modules() -> tuple[str, ...]:
    """Flat tuple of every dotted module path mentioned in the map."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for row in _V6_CONTRACT_RAW:
        for mod in row.modules:
            if mod not in seen_set:
                seen.append(mod)
                seen_set.add(mod)
    return tuple(seen)


def phase_for_module(dotted_path: str) -> tuple[str, ...]:
    """Return the phase ids that claim ``dotted_path`` as part of their contract."""
    return tuple(row.phase_id for row in _V6_CONTRACT_RAW if dotted_path in row.modules)


__all__ = [
    "V6PhaseContract",
    "V6_CONTRACT_MAP",
    "all_modules",
    "phase_for_module",
]
