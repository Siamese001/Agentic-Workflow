"""
Command-line interface for résumé analysis and job matching optimization.

Improves résumé quality by coordinating multi-agent workflow execution with configurable analysis parameters.
"""

from __future__ import annotations

import argparse
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Mapping, Sequence, Optional, Callable, TypeVar, cast

# ---------------------------------------------------------------------------
# Optional / dynamic imports of Phase-0 and Phase-3 modules
# ---------------------------------------------------------------------------

# We keep imports resilient to minor API drift. If the "real" types or helpers
# are present, they are used; otherwise we fall back to looser types so that
# this module remains importable and testable in isolation.

T = TypeVar("T")


def _safe_import(name: str) -> Any:
    try:
        return __import__(name)
    except Exception:  # pragma: no cover - defensive
        return None


# Core type containers
_models = _safe_import("models")
_config_profiles = _safe_import("config_profiles_v10_10")
_meta_profile = _safe_import("meta_profile")
_runtime_utils = _safe_import("runtime_utils")
_observability = _safe_import("observability")

# L1–L5 layers
_l1 = _safe_import("l1")
_l2 = _safe_import("l2")
_l3 = _safe_import("l3")
_l4 = _safe_import("l4")
_l5 = _safe_import("l5")

# ---------------------------------------------------------------------------
# Canonical type aliases (resolved if present, otherwise relaxed to Any)
# ---------------------------------------------------------------------------

ExecutionContext = getattr(_models, "ExecutionContext", Any) if _models else Any
WorkflowOutput = getattr(_models, "WorkflowOutput", Any) if _models else Any
RoutingPolicy = getattr(_config_profiles, "RoutingPolicy", Any) if _config_profiles else Any
SandboxConfig = getattr(_config_profiles, "SandboxConfig", Any) if _config_profiles else Any
ExecutionProfile = getattr(_config_profiles, "ExecutionProfile", Any) if _config_profiles else Any
MetaProfileSnapshot = getattr(_meta_profile, "MetaProfileSnapshot", Any) if _meta_profile else Any

TelemetryClient = getattr(_observability, "TelemetryClient", Any) if _observability else Any


# ---------------------------------------------------------------------------
# Phase‑3 knobs (G1–G3, G11–G14, G15–G18 integration surface)
# ---------------------------------------------------------------------------

class RRFStrategy(str, Enum):
    """
    Strategy for Reciprocal Rank Fusion in retrieval / evidence fusion.

    Exposed at the entrypoint so that experiments can be performed without
    changing internal modules.
    """
    DISABLED = "disabled"
    SIMPLE = "simple"
    WEIGHTED = "weighted"


class TelemetryRoutingMode(str, Enum):
    """
    How routing decisions incorporate telemetry (for dynamic routing, G15–G18).
    """
    DISABLED = "disabled"
    LOG_ONLY = "log_only"
    ENFORCED = "enforced"


@dataclass(frozen=True)
class Phase3Knobs:
    """
    Phase‑3 control knobs surfaced at the entrypoint.

    These are injected into workflow metadata so that all L1–L5 layers can
    consult them without needing direct parameter wiring from the entrypoint.
    """
    hyde_enabled: bool = False
    rrf_strategy: RRFStrategy = RRFStrategy.SIMPLE
    rrf_weights: Optional[Mapping[str, float]] = None
    council_size: int = 1
    correction_loop_max_iterations: int = 2
    telemetry_routing_mode: TelemetryRoutingMode = TelemetryRoutingMode.LOG_ONLY


# ---------------------------------------------------------------------------
# Workflow metadata and ExecutionContext construction helpers
# ---------------------------------------------------------------------------

def _resolve_execution_profile(name: str) -> ExecutionProfile:
    """
    Resolve an ExecutionProfile by name using config_profiles_v10_10.

    Deterministic configuration is enforced via profile names (G1).
    """
    if _config_profiles is None:
        raise RuntimeError("config_profiles_v10_10 module is required but missing")

    get_profile = getattr(_config_profiles, "get_execution_profile", None)
    if callable(get_profile):
        return cast(ExecutionProfile, get_profile(name))

    # Fallback: directly access attribute by name, or return name as a sentinel.
    profile = getattr(_config_profiles, name, None)
    if profile is None:
        raise ValueError(f"Unknown execution profile: {name}")
    return cast(ExecutionProfile, profile)


def _resolve_routing_policy(name: str) -> RoutingPolicy:
    """
    Resolve a RoutingPolicy by name using config_profiles_v10_10 (G29–G33).
    """
    if _config_profiles is None:
        raise RuntimeError("config_profiles_v10_10 module is required but missing")

    get_policy = getattr(_config_profiles, "get_routing_policy", None)
    if callable(get_policy):
        return cast(RoutingPolicy, get_policy(name))

    policy = getattr(_config_profiles, name, None)
    if policy is None:
        raise ValueError(f"Unknown routing policy: {name}")
    return cast(RoutingPolicy, policy)


def _resolve_sandbox_config(name: str) -> SandboxConfig:
    """
    Resolve a SandboxConfig by name using config_profiles_v10_10.
    """
    if _config_profiles is None:
        raise RuntimeError("config_profiles_v10_10 module is required but missing")

    get_sandbox = getattr(_config_profiles, "get_sandbox_config", None)
    if callable(get_sandbox):
        return cast(SandboxConfig, get_sandbox(name))

    sandbox = getattr(_config_profiles, name, None)
    if sandbox is None:
        raise ValueError(f"Unknown sandbox profile: {name}")
    return cast(SandboxConfig, sandbox)


def _resolve_meta_profile_snapshot(name: str) -> MetaProfileSnapshot:
    """
    Resolve MetaProfileSnapshot using meta_profile module (G2).
    """
    if _meta_profile is None:
        raise RuntimeError("meta_profile module is required but missing")

    build_snapshot = getattr(_meta_profile, "build_meta_profile_snapshot", None)
    if callable(build_snapshot):
        return cast(MetaProfileSnapshot, build_snapshot(name))

    # Fallback: simple constructor if available
    snapshot_cls = getattr(_meta_profile, "MetaProfileSnapshot", None)
    if snapshot_cls is not None:
        return cast(MetaProfileSnapshot, snapshot_cls(name=name))

    # Last resort: opaque dict snapshot
    return cast(MetaProfileSnapshot, {"name": name})


def _build_workflow_metadata(
    *,
    workflow_id: str,
    execution_profile_name: str,
    routing_policy_name: str,
    sandbox_profile_name: str,
    meta_profile_name: str,
    knobs: Phase3Knobs,
    user_request: Any,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a rich metadata envelope for the workflow (G24–G28).

    This metadata is attached to the ExecutionContext and should be treated
    as the single source of truth for Phase‑3 knobs inside L1–L5.
    """
    metadata: Dict[str, Any] = {
        "workflow_id": workflow_id,
        "execution_profile_name": execution_profile_name,
        "routing_policy_name": routing_policy_name,
        "sandbox_profile_name": sandbox_profile_name,
        "meta_profile_name": meta_profile_name,
        "phase3_knobs": asdict(knobs),
        "user_request_summary": _summarize_user_request(user_request),
    }

    if extra:
        # Deterministic: extra keys override base keys in a defined last-wins order.
        metadata.update(extra)

    return metadata


def _summarize_user_request(user_request: Any) -> Any:
    """
    Lightweight, non-lossy summary of the user request.

    We avoid heavy transformation here to keep determinism and make sure
    this function is cheap enough to be always-on.
    """
    if isinstance(user_request, str):
        # Truncate to a safe length for metadata; full text remains elsewhere.
        return {
            "type": "text",
            "preview": user_request[:256],
            "length": len(user_request),
        }
    if isinstance(user_request, Mapping):
        return {
            "type": "mapping",
            "keys": sorted(map(str, user_request.keys())),
        }
    if isinstance(user_request, Sequence) and not isinstance(user_request, (bytes, bytearray)):
        return {
            "type": "sequence",
            "length": len(user_request),
        }
    return {"type": type(user_request).__name__}


def _build_execution_context(
    *,
    user_request: Any,
    workflow_id: str,
    execution_profile_name: str,
    routing_policy_name: str,
    sandbox_profile_name: str,
    meta_profile_name: str,
    knobs: Phase3Knobs,
    telemetry_client: Optional[TelemetryClient] = None,
    extra_workflow_metadata: Optional[Mapping[str, Any]] = None,
) -> ExecutionContext:
    """
    Construct an ExecutionContext using Phase‑0 types (G1, G2, G27, G34).

    Prefers a canonical builder from runtime_utils if available; otherwise
    falls back to a simple, well‑structured dict that is compatible with
    typical usages in L1–L5.
    """
    routing_policy = _resolve_routing_policy(routing_policy_name)
    sandbox_config = _resolve_sandbox_config(sandbox_profile_name)
    execution_profile = _resolve_execution_profile(execution_profile_name)
    meta_profile_snapshot = _resolve_meta_profile_snapshot(meta_profile_name)

    workflow_metadata = _build_workflow_metadata(
        workflow_id=workflow_id,
        execution_profile_name=execution_profile_name,
        routing_policy_name=routing_policy_name,
        sandbox_profile_name=sandbox_profile_name,
        meta_profile_name=meta_profile_name,
        knobs=knobs,
        user_request=user_request,
        extra=extra_workflow_metadata,
    )

    # Preferred: centralized builder in runtime_utils
    build_ctx = getattr(_runtime_utils, "build_execution_context", None) if _runtime_utils else None
    if callable(build_ctx):
        return cast(
            ExecutionContext,
            build_ctx(
                user_request=user_request,
                routing_policy=routing_policy,
                sandbox_config=sandbox_config,
                execution_profile=execution_profile,
                meta_profile_snapshot=meta_profile_snapshot,
                workflow_metadata=workflow_metadata,
                telemetry_client=telemetry_client,
            ),
        )

    # Fallback: direct dataclass / object instantiation if available
    if hasattr(_models, "ExecutionContext") and isinstance(ExecutionContext, type):
        try:
            return ExecutionContext(  # type: ignore[call-arg]
                user_request=user_request,
                routing_policy=routing_policy,
                sandbox_config=sandbox_config,
                execution_profile=execution_profile,
                meta_profile_snapshot=meta_profile_snapshot,
                workflow_metadata=workflow_metadata,
                telemetry_client=telemetry_client,
            )
        except TypeError:
            # If the signature differs, try a more generic path below.
            pass

    # Last-resort fallback: plain dict-style context.
    return cast(
        ExecutionContext,
        {
            "user_request": user_request,
            "routing_policy": routing_policy,
            "sandbox_config": sandbox_config,
            "execution_profile": execution_profile,
            "meta_profile_snapshot": meta_profile_snapshot,
            "workflow_metadata": workflow_metadata,
            "telemetry_client": telemetry_client,
        },
    )


# ---------------------------------------------------------------------------
# Generic helper for discovering and calling L1–L5 layer functions
# ---------------------------------------------------------------------------

def _discover_layer_fn(module: Any, candidates: Sequence[str]) -> Callable[..., Any]:
    """
    Find the first callable in `module` whose name appears in `candidates`.

    This allows the entrypoint to be robust to minor naming differences
    while still enforcing the L1–L5 sequencing contract.
    """
    if module is None:
        raise RuntimeError("Layer module is missing")

    for name in candidates:
        fn = getattr(module, name, None)
        if callable(fn):
            return fn

    raise AttributeError(
        f"Could not find any of the candidate functions {candidates} in module {module.__name__!r}"
    )


# ---------------------------------------------------------------------------
# Core public API: run_workflow
# ---------------------------------------------------------------------------

def run_workflow(
    user_request: Any,
    *,
    # Profile wiring
    execution_profile_name: str = "default",
    routing_policy_name: str = "default",
    sandbox_profile_name: str = "default",
    meta_profile_name: str = "default",
    # Phase‑3 knobs
    hyde_enabled: bool = False,
    rrf_strategy: RRFStrategy = RRFStrategy.SIMPLE,
    rrf_weights: Optional[Mapping[str, float]] = None,
    council_size: int = 1,
    correction_loop_max_iterations: int = 2,
    telemetry_routing_mode: TelemetryRoutingMode = TelemetryRoutingMode.LOG_ONLY,
    # Misc controls
    workflow_id: Optional[str] = None,
    telemetry_client: Optional[TelemetryClient] = None,
    extra_workflow_metadata: Optional[Mapping[str, Any]] = None,
) -> WorkflowOutput:
    """
    Execute a single workflow through the L1→L2→L3→L4→L5 stack and return a
    strongly typed WorkflowOutput (or equivalent object produced by L5).

    Parameters
    ----------
    user_request:
        Arbitrary input payload representing the user's request. Downstream
        layers may interpret this as a prompt, conversation turn, etc.

    execution_profile_name, routing_policy_name, sandbox_profile_name, meta_profile_name:
        Deterministic handles referencing configuration profiles (G1, G2, G27).

    hyde_enabled, rrf_strategy, rrf_weights, council_size,
    correction_loop_max_iterations, telemetry_routing_mode:
        Phase‑3 knobs (G3–G10, G11–G14, G15–G18). These are persisted into the
        ExecutionContext metadata so all layers can consult them.

    workflow_id:
        Optional external identifier. If not provided, a UUID4 is generated.

    telemetry_client:
        Optional telemetry sink; if omitted, layers fall back to their defaults.

    extra_workflow_metadata:
        Optional extra key-value pairs injected into workflow metadata.
    """
    knobs = Phase3Knobs(
        hyde_enabled=hyde_enabled,
        rrf_strategy=rrf_strategy,
        rrf_weights=rrf_weights,
        council_size=council_size,
        correction_loop_max_iterations=correction_loop_max_iterations,
        telemetry_routing_mode=telemetry_routing_mode,
    )

    effective_workflow_id = workflow_id or str(uuid.uuid4())

    # 1) Build ExecutionContext with all profile & meta-profile wiring.
    execution_context = _build_execution_context(
        user_request=user_request,
        workflow_id=effective_workflow_id,
        execution_profile_name=execution_profile_name,
        routing_policy_name=routing_policy_name,
        sandbox_profile_name=sandbox_profile_name,
        meta_profile_name=meta_profile_name,
        knobs=knobs,
        telemetry_client=telemetry_client,
        extra_workflow_metadata=extra_workflow_metadata,
    )

    # 2) L1 — Planning only (G3, G4, G8, G9, G34, G35)
    l1_fn = _discover_layer_fn(
        _l1,
        candidates=(
            "build_workflow_plan_bundle",
            "build_workflow_plan",
            "plan_workflow",
        ),
    )
    plan_bundle = l1_fn(execution_context)

    # 3) L2 — Execution only (G5, G7, G11–G14, G36)
    l2_fn = _discover_layer_fn(
        _l2,
        candidates=(
            "execute_workflow_plan_bundle",
            "execute_workflow_plan",
            "run_execution_layer",
        ),
    )
    l2_result = l2_fn(plan_bundle, execution_context)

    # 4) L3 — Orchestration (DAG + correction) (G4–G10, G34–G36)
    l3_fn = _discover_layer_fn(
        _l3,
        candidates=(
            "run_workflow_graph",
            "orchestrate_workflow",
            "run_orchestration_layer",
        ),
    )
    l3_result = l3_fn(l2_result, execution_context)

    # 5) L4 — State mutation only (G34–G36)
    l4_fn = _discover_layer_fn(
        _l4,
        candidates=(
            "persist_workflow_state",
            "apply_state_mutations",
            "run_state_layer",
        ),
    )
    l4_result = l4_fn(l3_result, execution_context)

    # 6) L5 — Safety enforcement only (G19–G23)
    l5_fn = _discover_layer_fn(
        _l5,
        candidates=(
            "enforce_safety_policies",
            "enforce_safety",
            "run_safety_layer",
        ),
    )
    final_output = l5_fn(l4_result, execution_context)

    # The L5 layer is authoritative for the return type. In a fully wired
    # system, this should be a models.WorkflowOutput instance.
    return cast(WorkflowOutput, final_output)


# ---------------------------------------------------------------------------
# CLI entrypoint for manual and scripted runs
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a single v10_10 workflow job through the L1–L5 pipeline.",
    )

    # Minimal user payload: free-form text. More structured callers should
    # use run_workflow() directly instead of the CLI.
    parser.add_argument(
        "prompt",
        help="User prompt or request text.",
    )

    # Profile selection
    parser.add_argument(
        "--execution-profile",
        default="default",
        help="ExecutionProfile name (default: %(default)s).",
    )
    parser.add_argument(
        "--routing-policy",
        default="default",
        help="RoutingPolicy name (default: %(default)s).",
    )
    parser.add_argument(
        "--sandbox-profile",
        default="default",
        help="SandboxConfig profile name (default: %(default)s).",
    )
    parser.add_argument(
        "--meta-profile",
        default="default",
        help="Meta-profile name for meta_profile wiring (default: %(default)s).",
    )

    # Phase‑3 knobs
    parser.add_argument(
        "--hyde",
        action="store_true",
        help="Enable HYDE retrieval augmentation.",
    )
    parser.add_argument(
        "--rrf-strategy",
        choices=[s.value for s in RRFStrategy],
        default=RRFStrategy.SIMPLE.value,
        help="RRF strategy for evidence fusion (default: %(default)s).",
    )
    parser.add_argument(
        "--rrf-weight",
        action="append",
        metavar="KEY=VALUE",
        help=(
            "RRF weight override in KEY=VALUE form. "
            "May be specified multiple times."
        ),
    )
    parser.add_argument(
        "--council-size",
        type=int,
        default=1,
        help="QA / agent council size (default: %(default)s).",
    )
    parser.add_argument(
        "--correction-max-iters",
        type=int,
        default=2,
        help=(
            "Maximum iterations of the correction loop in orchestration "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--telemetry-routing-mode",
        choices=[m.value for m in TelemetryRoutingMode],
        default=TelemetryRoutingMode.LOG_ONLY.value,
        help="Telemetry routing mode (default: %(default)s).",
    )

    # Misc
    parser.add_argument(
        "--workflow-id",
        default=None,
        help="Optional explicit workflow ID; if omitted, a UUID4 is generated.",
    )

    return parser.parse_args(argv)


def _parse_rrf_weights(pairs: Optional[Sequence[str]]) -> Optional[Dict[str, float]]:
    if not pairs:
        return None
    weights: Dict[str, float] = {}
    for item in pairs:
        if "=" not in item:
            raise ValueError(f"Invalid --rrf-weight spec (expected KEY=VALUE): {item!r}")
        key, value_str = item.split("=", 1)
        key = key.strip()
        value_str = value_str.strip()
        if not key:
            raise ValueError(f"Invalid --rrf-weight key in: {item!r}")
        try:
            value = float(value_str)
        except ValueError as exc:
            raise ValueError(f"Invalid --rrf-weight numeric value in: {item!r}") from exc
        weights[key] = value
    return weights


def main(argv: Optional[Sequence[str]] = None) -> None:
    """
    CLI wrapper intended for manual experiments and golden runs.

    For programmatic usage, prefer calling run_workflow() directly.
    """
    args = _parse_args(argv)
    rrf_weights = _parse_rrf_weights(args.rrf_weight)

    output = run_workflow(
        user_request=args.prompt,
        execution_profile_name=args.execution_profile,
        routing_policy_name=args.routing_policy,
        sandbox_profile_name=args.sandbox_profile,
        meta_profile_name=args.meta_profile,
        hyde_enabled=args.hyde,
        rrf_strategy=RRFStrategy(args.rrf_strategy),
        rrf_weights=rrf_weights,
        council_size=args.council_size,
        correction_loop_max_iterations=args.correction_max_iters,
        telemetry_routing_mode=TelemetryRoutingMode(args.telemetry_routing_mode),
        workflow_id=args.workflow_id,
    )

    # For CLI use, print a minimal, stable representation. We assume that a
    # WorkflowOutput either has a 'to_dict' method or is directly printable.
    if hasattr(output, "to_dict"):
        import json

        print(json.dumps(output.to_dict(), indent=2, sort_keys=True))
    else:
        print(output)


if __name__ == "__main__":  # pragma: no cover - CLI behavior
    main()



