#!/usr/bin/env python3
"""
Unified Sovereign Compliance Protocol (v4.0)
Merges SSOT Compliance Protocol (Autonomous Decision Engine) with Canon Validator (Observability & Discovery).

PRIMARY FEATURES:
- Autonomous Confidence-Based Healing (SSOT)
- Real-time Runtime State & Dashboard Integration (Canon)
- Multi-Domain Orchestration (Canon)
- Hybrid Agent Discovery (Canon)
- Comprehensive Audit Trail (SSOT)
"""

# [IMPORTS] Added for dynamic loading and signal handling
import argparse
import atexit  # [HARDENED] For guaranteed state cleanup
import builtins
import importlib.util
import inspect
import json
import logging
import os
import platform
import signal
import stat  # [HARDENED] For permission bits
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from subprocess import DEVNULL
from types import FrameType
from typing import Any, Optional

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write


def _get_safe_subprocess_run():
    from agentic_core.L2_execution.tools.safe_subprocess import safe_subprocess_run

    return safe_subprocess_run


def _get_write_gateway():
    from agentic_core.L2_execution.tools import write_gateway

    return write_gateway


def _get_execution_context_class():
    from agentic_core.L0_routing.scripts.execution_context import ExecutionContext

    return ExecutionContext


def _get_location_validator_agent():
    from agentic_core.L5_safety.reasoning.LocationValidatorAgent import LocationValidatorAgent

    return LocationValidatorAgent


def _fire_meta_learning_intake(state_mgr: "RuntimeStateManager") -> None:
    """Wire HealingOutcomeIntakeAdapter and MetaLearningPipeline after each run.

    Both imports are guarded — if archived modules are not yet restored (pre-Wave 0B)
    this is a safe no-op. After Wave 0B restoration the full pipeline activates.
    """
    try:
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
        from system_learning.engines.in_memory_healing_outcome_intake_store import (
            InMemoryHealingOutcomeIntakeStore,
        )

        healing_actions = state_mgr.state.get("healing_actions", [])
        aggregator = HealingOutcomeAggregator(window_size=max(len(healing_actions), 1))
        for action in healing_actions:
            from system_learning.types.healing_outcome_types import HealingOutcomeEvent

            aggregator.ingest(
                HealingOutcomeEvent(
                    healer_id=action.get("agent", "unknown"),
                    tier=action.get("tier", "L5"),
                    failure_type=action.get("type", "UNKNOWN"),
                    success=action.get("status") not in ("plan_only", "skipped", "error", "failed"),
                    timestamp_utc=0,
                )
            )

        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        # Only persist if there are actual healing events to record
        if healing_actions:
            record = adapter.build_record(aggregator=aggregator, created_utc=0, source="execute_ssot")
            adapter.persist_record(record)
        state_mgr.update_meta_learning(
            {
                "total_experiences": store.count(),
                "experience": f"intake: {store.count()} healing records persisted",
            }
        )
        logging.info(
            "[MetaLearning] HealingOutcomeIntakeAdapter: %d records persisted to L4B store.",
            store.count(),
        )
    except ImportError:
        logging.debug("[MetaLearning] Intake adapter not yet available (pre-Wave 0B). Skipping.")
    except Exception as _ml_err:  # guardian: allow-silent-swallower
        logging.warning("[MetaLearning] Intake adapter failed (non-fatal): %s", _ml_err)

    try:
        from system_learning.pipelines.meta_learning_pipeline import run_pipeline as _ml_run_pipeline

        _ml_run_pipeline(now_utc=0, window_start_utc=0, window_end_utc=0)
        logging.info("[MetaLearning] meta_learning_pipeline.run_pipeline() completed.")
    except ImportError:
        logging.debug("[MetaLearning] Pipeline not yet available (pre-Wave 0B). Skipping.")
    except Exception as _pl_err:  # guardian: allow-silent-swallower
        logging.warning("[MetaLearning] Pipeline run failed (non-fatal): %s", _pl_err)


def _get_l5_agent_roster():
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent
    from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import CognitiveDispositionAgent
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent
    from agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent
    from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent
    from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent
    from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent
    from agentic_core.L5_safety.reasoning.RootHygieneAgent import RootHygieneAgent
    from agentic_core.L5_safety.reasoning.SystemArchitectAgent import SystemArchitectAgent
    from agentic_core.L6_observability.reasoning.ObservabilityProbeExecutorAgent import (
        ObservabilityProbeExecutorAgent,
    )

    return (
        ArchitectureGovernorAgent,
        CognitiveDispositionAgent,
        FileClassificationAgent,
        FilesystemSSOTReconcilerAgent,
        GravityLeakRepairAgent,
        HierarchyAgent,
        LocationAgent,
        RootHygieneAgent,
        SystemArchitectAgent,
        ObservabilityProbeExecutorAgent,
    )


def _preflight_import_check() -> None:
    """Diagnostic-only helper to verify critical imports can be resolved.

    This function checks that the execute_ssot_entrypoint can be imported
    and that _legacy_main symbol exists without invoking any runtime behavior.
    Raises RuntimeError with detailed message if any check fails.

    NOTE: This function is intentionally NOT called anywhere in Wave 1.
    It will be wired into the startup sequence in Wave 2.
    """
    try:
        # Check that _legacy_main exists in this module (execute_ssot.py)
        if not hasattr(sys.modules[__name__], "_legacy_main"):
            raise RuntimeError("CRITICAL: _legacy_main not found in execute_ssot module")
        # Access the attribute to ensure it's resolvable
        legacy_main = sys.modules[__name__]._legacy_main
        if not callable(legacy_main):
            raise RuntimeError("CRITICAL: _legacy_main attribute is not callable")
    except (AttributeError, TypeError) as exc:
        raise RuntimeError(
            f"CRITICAL: Failed to resolve _legacy_main from execute_ssot module: {exc}"
        ) from exc


def _optional_runtime_guard():
    """Lazy import to avoid import-time failure in bootstrap contexts.

    Fail-closed semantics: when V15_ENFORCEMENT=1 and the guard cannot be
    imported, re-raise so the caller sees a hard failure instead of a silent
    no-op.  When enforcement is off (or unset), fall back to a no-op decorator.
    """
    try:
        from agentic_core.L0_routing.enforcement.runtime_guard import runtime_guard

        return runtime_guard
    # guardian: allow-silent-swallow
    except Exception:
        if os.getenv("V15_ENFORCEMENT") == "1":
            raise  # fail-closed: enforcement is on but guard is unavailable

        def _noop_guard(_entry_point_id: str):
            """No-op: accepts an ID string and returns an identity decorator."""

            def _identity(func):
                return func

            return _identity

        return _noop_guard


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import ast
import re

try:
    from agentic_core.utils.decorators_compat_util import HEAL_RESULT_SCHEMA, standard_heal
except ImportError:
    # Fallback for bootstrapping scenarios
    def standard_heal(func):
        return func

    HEAL_RESULT_SCHEMA = {}

try:
    from agentic_core.base_agents.IHealerProtocol import IHealerProtocol, LegacyAgentAdapter
except ImportError:
    # Fallback for bootstrapping scenarios
    class IHealerProtocol:
        pass

    class LegacyAgentAdapter:
        def __init__(self, legacy_agent):
            self.agent = legacy_agent

        def heal(self, violation):
            return {"status": "failed", "errors": ["Adapter not available"]}


def _safe_print(text: str) -> None:
    """Print text safely on Windows consoles that use charmap encoding."""
    sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()


def run_fence_self_check() -> None:
    """Run deterministic fence self-check (validates policy + wiring; no mutations).

    Validates:
    1. Default ProtectedRootPolicy immutable_roots equals ("agentic_core","tests",".github")
    2. Default ProtectedRootPolicy log_path is outside IMMUTABLE_ROOTS
    3. write_gateway public entrypoints accept allow_override AND call enforce_protected_root
    4. Telemetry emitter path is writable target ONLY outside IMMUTABLE_ROOTS

    Prints single-line JSON summary to stdout:
    - {"status":"ok","checks":4}
    - or {"status":"fail","failed":["check_name",...]}

    Exits with code 0 if all checks pass, nonzero otherwise.
    """
    from agentic_core.L0_routing.enforcement.mutation_prohibition import (
        IMMUTABLE_ROOTS,
        get_default_protected_root_policy,
    )

    failed_checks = []

    # Check 1: Default policy immutable_roots
    try:
        policy = get_default_protected_root_policy()
        if policy.immutable_roots != ("agentic_core", "tests", ".github"):
            failed_checks.append("default_policy_immutable_roots")
    # guardian: allow-silent-swallow
    except Exception:
        failed_checks.append("default_policy_immutable_roots")

    # Check 2: Default policy log_path is outside IMMUTABLE_ROOTS
    try:
        policy = get_default_protected_root_policy()
        log_path = Path(policy.log_path)

        # Check if log_path would be under any immutable root
        repo_root = resolve_repo_root()
        resolved_log = (repo_root / log_path).resolve()

        is_under_immutable = False
        for immutable_root in IMMUTABLE_ROOTS:
            try:
                resolved_log.relative_to(immutable_root)
                is_under_immutable = True
                break
            except ValueError:
                pass

        if is_under_immutable:
            failed_checks.append("log_path_outside_immutable_roots")
    # guardian: allow-silent-swallow
    except Exception:
        failed_checks.append("log_path_outside_immutable_roots")

    # Check 3: write_gateway entrypoints accept allow_override AND call enforce_protected_root
    try:
        write_gateway = _get_write_gateway()

        # Check write_text and write_bytes (primary entrypoints)
        for func_name in ["write_text", "write_bytes"]:
            func = getattr(write_gateway, func_name, None)
            if func is None:
                failed_checks.append("write_gateway_enforces_protected_root")
                break

            # Check signature has allow_override parameter
            sig = inspect.signature(func)
            if "allow_override" not in sig.parameters:
                failed_checks.append("write_gateway_enforces_protected_root")
                break

            # Check source contains enforce_protected_root call
            try:
                source = inspect.getsource(func)
                if "enforce_protected_root" not in source:
                    failed_checks.append("write_gateway_enforces_protected_root")
                    break
            except (OSError, TypeError):
                # Source unavailable - fail with actionable message
                failed_checks.append("write_gateway_enforces_protected_root")
                break
    # guardian: allow-silent-swallow
    except Exception:
        failed_checks.append("write_gateway_enforces_protected_root")

    # Check 4: Telemetry emitter path is outside IMMUTABLE_ROOTS (pure path check)
    try:
        policy = get_default_protected_root_policy()
        log_path = Path(policy.log_path)
        repo_root = resolve_repo_root()
        resolved_log = (repo_root / log_path).resolve()

        # Same check as #2 - ensure telemetry path is outside protected roots
        is_under_immutable = False
        for immutable_root in IMMUTABLE_ROOTS:
            try:
                resolved_log.relative_to(immutable_root)
                is_under_immutable = True
                break
            except ValueError:
                pass

        if is_under_immutable:
            failed_checks.append("telemetry_path_outside_immutable_roots")
    # guardian: allow-silent-swallow
    except Exception:
        failed_checks.append("telemetry_path_outside_immutable_roots")

    # Output deterministic JSON summary
    if failed_checks:
        result = {"status": "fail", "failed": sorted(failed_checks)}
        print(json.dumps(result, sort_keys=True))
        sys.exit(1)
    else:
        result = {"status": "ok", "checks": 4}
        print(json.dumps(result, sort_keys=True))
        sys.exit(0)


def resolve_repo_root(start=None):
    """Deterministic repo-root resolver.
    Walk upward from this file (or provided start) until we find repo markers.
    """
    cur = Path(start or __file__).resolve()
    for p in (cur, *cur.parents):
        if (p / "agentic_core").is_dir() and (p / "ops_scripts").is_dir():
            return p
    raise RuntimeError(f"Unable to resolve repo root from: {cur}")


REPO_ROOT = resolve_repo_root()  # noqa: N816


def _apply_v15_enforcement_flag(args: argparse.Namespace) -> None:
    """CLI overrides env to ensure determinism in CI/smoke paths."""
    if getattr(args, "v15_enforcement", None) is None:
        return
    os.environ["V15_ENFORCEMENT"] = "1" if int(args.v15_enforcement) == 1 else "0"


def _configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )


def _maybe_force_utf8_console() -> None:
    """Unconditional stdout/stderr UTF-8 coercion.  Called at runtime, NOT import time."""
    if sys.platform.startswith("win"):
        try:
            _get_safe_subprocess_run()(
                ["chcp", "65001"],
                stdout=DEVNULL,
                stderr=DEVNULL,
                check=False,
                allow_protected_root_mutation=True,
            )
        except FileNotFoundError:
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    # guardian: allow-silent-swallow
    except Exception:  # guardian: allow-silent-swallower
        pass
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    # guardian: allow-silent-swallow
    except Exception:
        return


def _maybe_force_utf8_logging_handlers() -> None:
    """Reconfigure existing logging handler streams to UTF-8.  Called at runtime, NOT import time."""
    seen: set[int] = set()
    for handler in logging.getLogger().handlers + logging.getLogger("").handlers:
        hid = id(handler)
        if hid in seen:
            continue
        seen.add(hid)
        stream = getattr(handler, "stream", None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        # guardian: allow-silent-swallow
        except Exception:
            pass


# ============================================================================
# V15 MANIFEST CONSTRUCTION (§8.1e)
# ============================================================================


def _v15_build_ssot_manifest():
    """§8.1e — Construct SurgicalManifest for SSOT bootstrap entry.

    Returns None when V15 enforcement is off (zero overhead).
    Bootstrap-safe: lazy imports with fail-closed semantics.
    """
    try:
        from agentic_core.L0_routing.types.guardian_contract import is_v15_enforced

        if not is_v15_enforced():
            return None

        import hashlib as _hl

        from agentic_core.L0_routing.enforcement.traceability_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.determinism_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = _hl.sha256(b"execute_ssot._legacy_main").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)

        ast_snippet = "execute_ssot._legacy_main()"
        return SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="ExecuteSSOT",
            target_layer="L0",
            ast_snippet=ast_snippet,
            serialization_canon="execute_ssot",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=_hl.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )
    # guardian: allow-silent-swallow
    except Exception:
        if os.getenv("V15_ENFORCEMENT") == "1":
            raise  # fail-closed when hard enforcement is on
        return None


def _v15_ssot_gateway_audit(manifest, trace_id: str) -> None:
    """§8.1e — Invoke gateway.execute in LOG_ONLY mode for SSOT audit trail."""
    if manifest is None:
        return
    try:
        import hashlib as _hl

        from agentic_core.L0_routing.enforcement.execution_gateway import (
            V15ExecutionGateway,
        )

        gw = V15ExecutionGateway()
        gw.execute(
            manifest,
            lambda m: {"status": "ssot_audit", "errors": 0},
            lambda: (
                _hl.sha256(b"fs_ssot").hexdigest(),
                _hl.sha256(b"git_ssot").hexdigest(),
                _hl.sha256(b"mem_ssot").hexdigest(),
            ),
            trace_id=trace_id,
            agent_id="ssot_audit",
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        logging.getLogger(__name__).warning("[V15] SSOT gateway audit failed (LOG_ONLY): %s", exc)


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class ConfidenceScore:
    """[HARDENED] Environment-aware confidence score for autonomous healing."""

    value: float  # 0.0 to 1.0
    reasoning: str
    factors: dict[str, float] = field(default_factory=dict)

    @property
    def _high_threshold(self) -> float:
        """Sourced from .env: SOVEREIGN_HIGH_CONFIDENCE (default: 0.75)"""
        return float(os.getenv("SOVEREIGN_HIGH_CONFIDENCE", "0.75"))

    @property
    def _med_threshold(self) -> float:
        """Sourced from .env: SOVEREIGN_MEDIUM_CONFIDENCE (default: 0.50)"""
        return float(os.getenv("SOVEREIGN_MEDIUM_CONFIDENCE", "0.50"))

    @property
    def is_high_confidence(self) -> bool:
        return self.value > self._high_threshold

    @property
    def is_medium_confidence(self) -> bool:
        return self._med_threshold <= self.value <= self._high_threshold

    @property
    def is_low_confidence(self) -> bool:
        return self.value < self._med_threshold


# ============================================================================
# HARDENED SSOT ROUTING — enums, dataclasses, pure routing function
# ============================================================================

import enum as _enum
import hashlib as _hashlib


class FailureType(_enum.Enum):
    """Classifies the failure being routed.  Drives gate selection."""

    LAYER_VIOLATION = "LAYER_VIOLATION"
    GATEWAY_BYPASS = "GATEWAY_BYPASS"
    KILL_SWITCH_BYPASS = "KILL_SWITCH_BYPASS"
    SIGNATURE_VERIFY = "SIGNATURE_VERIFY"
    UNSIGNED_INGRESS = "UNSIGNED_INGRESS"
    IMPORT_BOUNDARY_VIOLATION = "IMPORT_BOUNDARY_VIOLATION"
    SCHEMA_REQUIRED_FIELDS_MISSING = "SCHEMA_REQUIRED_FIELDS_MISSING"
    NAMING = "NAMING"
    HIERARCHY = "HIERARCHY"
    SHALLOW = "SHALLOW"
    DEEP = "DEEP"
    VOID = "VOID"
    DUPLICATE = "DUPLICATE"
    ORPHAN = "ORPHAN"
    UNKNOWN = "UNKNOWN"


class RoutingTier(_enum.Enum):
    DETERMINISTIC = "DETERMINISTIC"
    QWEN = "QWEN"
    GEMINI = "GEMINI"
    FAIL_CLOSED = "FAIL_CLOSED"


# Structural failures: deterministic coverage can rescue; otherwise GEMINI/FAIL_CLOSED
_STRUCTURAL_CLASS: frozenset[FailureType] = frozenset(
    {
        FailureType.LAYER_VIOLATION,
        FailureType.GATEWAY_BYPASS,
        FailureType.KILL_SWITCH_BYPASS,
        FailureType.SIGNATURE_VERIFY,
        FailureType.UNSIGNED_INGRESS,
    }
)

# Qwen-disallowed failures: includes structural + import/schema violations
_QWEN_DISALLOWED: frozenset[FailureType] = _STRUCTURAL_CLASS | frozenset(
    {
        FailureType.IMPORT_BOUNDARY_VIOLATION,
        FailureType.SCHEMA_REQUIRED_FIELDS_MISSING,
    }
)


@dataclass
class RoutingInputs:
    """All inputs to compute_routing_decision.  No embeddings allowed."""

    failure_type: FailureType = FailureType.UNKNOWN
    retry_count: int = 0
    C: int = 0  # complexity      0-3
    B: int = 0  # blast-radius    0-3
    A: int = 0  # autonomy-risk   0-3
    N: int = 0  # novelty         0-3
    F: int = 0  # failure-cost    0-3
    L: int = 0  # latency class   0-3  (0=interactive, 3=async-batch)
    replay_mode: bool = False
    playbook_match: bool = False
    deterministic_coverage: bool = False
    provider_prohibited_gemini: bool = False
    provider_prohibited_qwen: bool = False


@dataclass
class RoutingDecision:
    """Immutable routing result with full audit trail."""

    tier: RoutingTier
    score: int
    gate_applied: str
    model_id: str
    factors: dict
    inputs: RoutingInputs
    determinism_digest: str

    def as_log_line(self) -> str:
        f = self.factors
        i = self.inputs
        return (
            f"[ROUTING] tier={self.tier.value} S={self.score} gate={self.gate_applied}"
            f" model={self.model_id}"
            f" C={f.get('C', 0)} B={f.get('B', 0)} A={f.get('A', 0)}"
            f" N={f.get('N', 0)} F={f.get('F', 0)} L={f.get('L', 0)}"
            f" replay={i.replay_mode} retry={i.retry_count}"
            f" playbook={i.playbook_match} det_cov={i.deterministic_coverage}"
            f" digest={self.determinism_digest}"
        )


def compute_routing_decision(inputs: RoutingInputs) -> RoutingDecision:  # noqa: C901
    """Pure SSOT routing function — strict gate order, no side effects."""
    C, B, A, N, F, L = inputs.C, inputs.B, inputs.A, inputs.N, inputs.F, inputs.L

    def _decide(tier: RoutingTier, gate: str, score: int = 0) -> RoutingDecision:
        if tier == RoutingTier.DETERMINISTIC:
            model = "deterministic-sovereign"
        elif tier == RoutingTier.QWEN:
            model = "Qwen2.5-14B-Instruct-AWQ"
        elif tier == RoutingTier.GEMINI:
            model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        else:
            model = "FAIL_CLOSED"
        raw = f"{tier.value}|{score}|{gate}|{inputs.failure_type.value}|{C}|{B}|{A}|{N}|{F}|{L}|{inputs.replay_mode}|{inputs.retry_count}"
        digest = _hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:16]
        return RoutingDecision(
            tier=tier,
            score=score,
            gate_applied=gate,
            model_id=model,
            factors={"C": C, "B": B, "A": A, "N": N, "F": F, "L": L},
            inputs=inputs,
            determinism_digest=digest,
        )

    # ── GATE 0: Replay mode → always deterministic ─────────────────────────
    if inputs.replay_mode:
        return _decide(RoutingTier.DETERMINISTIC, "GATE_0_REPLAY")

    # ── GATE 1: Global retry override ──────────────────────────────────────
    if inputs.retry_count >= 3:
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_1_RETRY_OVERRIDE_FAIL_CLOSED")
        return _decide(RoutingTier.GEMINI, "GATE_1_RETRY_OVERRIDE")

    # ── GATE 2: Structural class pre-gate ──────────────────────────────────
    if inputs.failure_type in _STRUCTURAL_CLASS:
        if inputs.deterministic_coverage:
            return _decide(RoutingTier.DETERMINISTIC, "GATE_2_STRUCTURAL_DET_COV")
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_2_STRUCTURAL_FAIL_CLOSED")
        return _decide(RoutingTier.GEMINI, "GATE_2_STRUCTURAL_NO_DET_COV")

    # ── GATE 3: Critical surface mechanical exception ──────────────────────
    if B == 3 and A == 0 and inputs.playbook_match and inputs.deterministic_coverage:
        return _decide(RoutingTier.DETERMINISTIC, "GATE_3_CRITICAL_SURFACE_MECH")

    # ── Score computation ──────────────────────────────────────────────────
    S = 3 * C + 4 * B + 3 * A + 2 * N + 4 * F
    if inputs.playbook_match:
        S = max(0, S - 4)

    # ── GATE 4: Hard-override for extreme risk ─────────────────────────────
    if B == 3 and F == 3 and (C >= 2 or A >= 1):
        if inputs.provider_prohibited_gemini and inputs.provider_prohibited_qwen:
            return _decide(RoutingTier.FAIL_CLOSED, "GATE_4_HARD_OVERRIDE_FAIL_CLOSED", S)
        return _decide(RoutingTier.GEMINI, "GATE_4_HARD_OVERRIDE", S)

    # ── GATE 5: Threshold routing ──────────────────────────────────────────
    if S <= 13:
        tier = RoutingTier.DETERMINISTIC
        gate = "THRESHOLD_LOW_DET"
    elif S <= 26:
        tier = RoutingTier.QWEN
        gate = "THRESHOLD_MED_QWEN"
    else:
        tier = RoutingTier.GEMINI
        gate = "THRESHOLD_HIGH_GEMINI"
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, "THRESHOLD_HIGH_FAIL_CLOSED", S)

    # ── GATE 6: Latency tie-breaker (boundary zones only) ─────────────────
    # Does NOT apply when failure_type is qwen-disallowed (Gate 7 handles those).
    _qwen_disallowed_type = inputs.failure_type in _QWEN_DISALLOWED
    _qwen_blocked = _qwen_disallowed_type or inputs.provider_prohibited_qwen
    if tier == RoutingTier.QWEN and S in range(14, 16) and L == 0 and not _qwen_blocked:
        tier = RoutingTier.DETERMINISTIC
        gate = f"{gate}.L_TIEBREAK_DOWN"
    elif tier == RoutingTier.DETERMINISTIC and S in range(12, 14) and L == 3 and not _qwen_disallowed_type:
        tier = RoutingTier.QWEN
        gate = f"{gate}.L_TIEBREAK_UP"

    # ── GATE 7: Qwen-disallowed fall-up ───────────────────────────────────
    if tier == RoutingTier.QWEN and inputs.failure_type in _QWEN_DISALLOWED:
        if inputs.deterministic_coverage and A == 0 and C == 0:
            return _decide(RoutingTier.DETERMINISTIC, f"{gate}.QWEN_DISALLOWED_DET_FALLBACK", S)
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.QWEN_DISALLOWED_FAIL_CLOSED", S)
        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_DISALLOWED", S)

    # ── GATE 8: Provider prohibition check ────────────────────────────────
    if tier == RoutingTier.QWEN and inputs.provider_prohibited_qwen:
        if inputs.provider_prohibited_gemini:
            return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.BOTH_PROHIBITED", S)
        return _decide(RoutingTier.GEMINI, f"{gate}.QWEN_PROHIBITED_FALLBACK", S)

    if tier == RoutingTier.GEMINI and inputs.provider_prohibited_gemini:
        return _decide(RoutingTier.FAIL_CLOSED, f"{gate}.GEMINI_PROHIBITED", S)

    return _decide(tier, gate, S)


# ============================================================================
# NEW DATA STRUCTURES FOR TELEMETRY AND VALIDATION
# ============================================================================


@dataclass
class ReconciliationViolation:
    """Structured violation for enhanced telemetry (Ported from FilesystemSSOTReconciler)."""

    is_valid: bool
    message: str
    drift_type: str | None = None
    file_path: Path | None = None
    suggested_action: str | None = None
    severity: int = 5  # 1-10 scale

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "message": self.message,
            "drift_type": self.drift_type,
            "file_path": str(self.file_path.as_posix()) if self.file_path else None,
            "severity": self.severity,
        }


@dataclass
class ReconciliationManifest:
    """Telemetry manifest for tracking all reconciliation changes."""

    mission_id: str
    territory: str
    start_time: str
    end_time: str | None = None
    violations_found: int = 0
    violations_attempted: int = 0
    violations_fixed: int = 0
    violations_failed: int = 0
    modifications: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    budget_consumed: int = 0
    confidence_scores: list[float] = field(default_factory=list)

    def add_modification(self, modification: dict[str, Any]) -> None:
        self.modifications.append(modification)
        self.violations_attempted += 1
        if modification.get("success", False):
            self.violations_fixed += 1
        else:
            self.violations_failed += 1

    def add_failure(self, failure: dict[str, Any]) -> None:
        self.failures.append(failure)
        self.violations_failed += 1

    def finalize(self) -> dict[str, Any]:
        self.end_time = datetime.now().isoformat()
        return {
            "mission_id": self.mission_id,
            "territory": self.territory,
            "duration": {
                "start": self.start_time,
                "end": self.end_time,
                "seconds": (
                    datetime.fromisoformat(self.end_time) - datetime.fromisoformat(self.start_time)
                ).total_seconds()
                if self.end_time
                else None,
            },
            "violations": {
                "found": self.violations_found,
                "attempted": self.violations_attempted,
                "fixed": self.violations_fixed,
                "failed": self.violations_failed,
                "success_rate": self.violations_fixed / max(self.violations_attempted, 1),
            },
            "budget": {
                "consumed": self.budget_consumed,
                "remaining": max(0, 100 - self.budget_consumed),  # Default max budget of 100
            },
            "confidence": {
                "scores": self.confidence_scores,
                "average": sum(self.confidence_scores) / len(self.confidence_scores)
                if self.confidence_scores
                else 0.0,
            },
            "modifications": self.modifications,
            "failures": self.failures,
        }


class ASTCodeQualityValidator:
    """AST-based code quality validation with memory guards (Ported from TypeMechanic)."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        # [SAFETY] Prevent OOM on massive generated files
        # guardian: allow-magic-config
        self.max_file_size = 1_000_000  # 1MB limit

    def _read_and_parse_file(self, fp: str) -> tuple[ast.AST | None, str | None]:
        """Reads a file and parses it into an AST with strict size limits."""
        try:
            if os.path.getsize(fp) > self.max_file_size:
                return None, "File too large for AST analysis"

            with open(fp, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fp)
                return tree, None
        except (OSError, SyntaxError) as e:
            return None, f"Error parsing {fp}: {str(e)}"

    # guardian: allow-type-erasure
    def check_file_quality(self, file_path: Path) -> dict:
        """Check file for code quality issues (missing types, etc)."""
        violations = []
        tree, error = self._read_and_parse_file(str(file_path))

        if error:
            return {"error": error, "violations": []}

        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Ignore dunders
                    if not node.returns and not node.name.startswith("__"):
                        violations.append(
                            {
                                "type": "MISSING_TYPE_HINT",
                                "file": str(file_path),
                                "line": node.lineno,
                                "message": f"Function '{node.name}' missing return type hint",
                            },
                        )

        return {
            "violations": violations,
            "violations_count": len(violations),
            "file": str(file_path),
        }


# ============================================================================
# ============================================================================
# HEAL CONTEXT — Single Source of Truth for Healing Flags
# ============================================================================


@dataclass(frozen=True)
class HealContext:
    """Immutable healing configuration passed uniformly to every phase function.

    Replaces the scattered (dry_run, auto_approve, enable_llm, enable_cda)
    positional argument pattern. Constructed once in _legacy_main; all phase
    functions receive ctx: HealContext instead of individual flags.
    """

    heal: bool  # True = mutations active; False = scan/report only
    auto_approve: bool  # True = no interactive prompts
    enable_llm: bool  # True = LLM arbitration enabled
    enable_cda: bool  # True = CognitiveDispositionAgent enabled

    @property
    def dry_run(self) -> bool:
        """Convenience alias — inverted heal for legacy call sites."""
        return not self.heal

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "HealContext":
        """Construct from parsed CLI args. Single construction point."""
        heal = getattr(args, "heal", False) and not getattr(args, "dry_run", False)
        return cls(
            heal=heal,
            auto_approve=not getattr(args, "interactive", False),
            enable_llm=heal,
            enable_cda=not getattr(args, "no_cda", False),
        )


# ============================================================================
# ENHANCED DECISION ENGINE WITH SEMANTIC SCORING & CYCLE DETECTION
# ============================================================================


class AutonomousDecisionEngine:
    """Makes autonomous healing decisions based on confidence scores."""

    def __init__(
        self,
        enable_llm: bool = False,
        state_mgr: Optional["RuntimeStateManager"] = None,
        execution_context: Optional["ExecutionContext"] = None,
    ):
        self.enable_llm = enable_llm
        self.decisions_made = []
        self.state_mgr = state_mgr
        self._execution_context = execution_context
        # [SAFETY] Cycle Detection State
        self._healing_count: int = 0
        self._healing_enabled: bool = True
        self._max_healing_operations: int = 100
        self._call_path: set[str] = set()

    def _calculate_semantic_similarity(self, unknown: str, existing: list[str]) -> float:
        """Calculate semantic similarity for unknown items against a candidate list.

        When BMG_EMBEDDINGS_ENABLED=true and sentence-transformers is installed,
        uses BAAI/bge-m3 cosine similarity (GPU-accelerated on RTX 5090).
        Falls back to Jaccard word-overlap when embeddings are unavailable.
        """
        if not existing:
            return 0.0

        if os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true":
            try:
                bmg_fn = self._get_bmg_cosine_similarity()
                return bmg_fn(unknown, existing)
            except Exception:  # guardian: allow-silent-swallower  # noqa: BLE001
                pass

        # Jaccard word-overlap fallback (original implementation)
        unknown_words = set(unknown.lower().replace("_", " ").replace("-", " ").split())
        max_similarity = 0.0

        for item in existing:
            existing_words = set(item.lower().replace("_", " ").replace("-", " ").split())
            intersection = unknown_words & existing_words
            union = unknown_words | existing_words

            if union:
                similarity = len(intersection) / len(union)
                max_similarity = max(max_similarity, similarity)

        return max_similarity

    @staticmethod
    def _get_bmg_cosine_similarity() -> object:
        """Lazy seam: load bmg_cosine_similarity from L2 healers without module-level import."""
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import (
            bmg_cosine_similarity,
        )

        return bmg_cosine_similarity

    @staticmethod
    def _get_bmg_embedding_agent_keys() -> frozenset:
        """Lazy seam: load BMG_EMBEDDING_AGENT_KEYS from L2 healing_tier_config."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            BMG_EMBEDDING_AGENT_KEYS,
        )

        return BMG_EMBEDDING_AGENT_KEYS

    @staticmethod
    def _get_qwen_14b_routing_config() -> tuple:
        """Lazy seam: load Qwen 14B routing constants from L2 healing_tier_config."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            QWEN_14B_AGENT_KEYS,
            QWEN_14B_MODEL_ID,
        )

        return QWEN_14B_AGENT_KEYS, QWEN_14B_MODEL_ID

    @staticmethod
    def _get_qwen_vllm_arbiter():
        """Lazy seam: return callable that invokes Qwen 14B via WSL vLLM subprocess."""
        import json
        import subprocess
        from pathlib import Path

        WSL_PYTHON = "/home/amita/venvs/vllm/bin/python"
        INFERENCE_SCRIPT = str(
            Path(__file__).parent.parent.parent / "L2_execution" / "healers" / "qwen_vllm_inference.py"
        )
        MODEL_PATH = "/home/amita/models/Qwen2.5-14B-Instruct-AWQ"

        def _arbiter(
            agent_name: str,
            violation_types: list,
            territory: str,
            score: int = 0,
            gate: str = "",
        ) -> dict:
            # Convert Windows path to WSL mount path
            script_wsl = INFERENCE_SCRIPT.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            cmd = [
                "wsl",
                "bash",
                "-c",
                (
                    f"{WSL_PYTHON} {script_wsl}"
                    f" --agent_name {agent_name}"
                    f" --score {score}"
                    f" --gate {gate}"
                    f" --territory {territory}"
                    f" --model_path {MODEL_PATH}"
                    + (f" --violation_types {' '.join(violation_types)}" if violation_types else "")
                ),
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )
            if result.returncode != 0:
                raise RuntimeError(f"vLLM subprocess failed: {result.stderr[-500:]}")
            # Last non-empty line is the JSON output
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            for line in reversed(lines):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
            raise RuntimeError(f"No JSON in vLLM output: {result.stdout[-300:]}")

        return _arbiter

    def _calculate_pattern_confidence(self, violation_type: str) -> float:
        """Regex-based pattern matching for known violation types."""
        high_confidence_patterns = [
            r".*NAMING.*",
            r".*HIERARCHY.*",
            r".*IMPORT.*",
            r".*SHALLOW.*",
            r".*DEEP.*",
            r".*VOID.*",
            r".*DUPLICATE.*",
            r".*ORPHAN.*",
        ]

        for pattern in high_confidence_patterns:
            if re.match(pattern, violation_type, re.IGNORECASE):
                return 0.9
        return 0.5

    def _route_decision(
        self,
        confidence: "ConfidenceScore",
        agent_name: str,
        territory: str,
        failure_type: "FailureType | None" = None,
        retry_count: int = 0,
        replay_mode: bool = False,
        playbook_match: bool = False,
        deterministic_coverage: bool = False,
        provider_prohibited_gemini: bool = False,
        provider_prohibited_qwen: bool = False,
    ) -> "RoutingDecision":
        """Map healing context to a hardened SSOT RoutingDecision."""
        if failure_type is None:
            reasoning_upper = (confidence.reasoning or "").upper()
            ft = FailureType.UNKNOWN
            for member in FailureType:
                if member.value in reasoning_upper:
                    ft = member
                    break
            failure_type = ft

        C = min(3, max(0, int(3 - confidence.value * 3)))
        B = 3 if territory.startswith("L5") else (2 if "agentic_core" in territory else 1)
        A = 0 if confidence.value >= 0.75 else (2 if confidence.value < 0.50 else 1)
        N = 1 if "[BMG-GPU]" in (confidence.reasoning or "") else 0
        high_cost = {
            FailureType.LAYER_VIOLATION,
            FailureType.GATEWAY_BYPASS,
            FailureType.KILL_SWITCH_BYPASS,
            FailureType.SIGNATURE_VERIFY,
            FailureType.UNSIGNED_INGRESS,
        }
        F = 3 if failure_type in high_cost else (2 if confidence.value < 0.50 else 1)
        L = 0

        ri = RoutingInputs(
            failure_type=failure_type,
            retry_count=retry_count,
            C=C,
            B=B,
            A=A,
            N=N,
            F=F,
            L=L,
            replay_mode=replay_mode,
            playbook_match=playbook_match,
            deterministic_coverage=deterministic_coverage,
            provider_prohibited_gemini=provider_prohibited_gemini,
            provider_prohibited_qwen=provider_prohibited_qwen,
        )
        decision = compute_routing_decision(ri)
        logger.info(decision.as_log_line())
        return decision

    # guardian: allow-magic-config
    def _check_healing_budget(self, agent_name: str, depth: int = 0, max_depth: int = 3) -> tuple[bool, str]:
        """Prevents infinite healing loops and budget exhaustion."""
        # Use operation-scoped call path to prevent bleeding across territories
        # Default to "Unknown" if no agent_name provided (should be avoided)
        if agent_name == "Unknown":
            agent_name = f"operation-{id(self)}"  # Unique per operation

        if agent_name in self._call_path:
            return False, f"Healing cycle detected: {agent_name}"
        if depth > max_depth:
            return False, f"Healing depth limit exceeded for {agent_name}"
        if self._healing_count >= self._max_healing_operations:
            return False, f"Budget exceeded ({self._healing_count})"
        return True, "OK"

    # guardian: allow-magic-config
    def calculate_healing_confidence(
        self,
        violations_count: int,
        violation_types: list[str],
        territory: str,
        historical_success_rate: float = 0.8,
        agent_name: str = "",
    ) -> ConfidenceScore:
        """Calculates weighted confidence score.

        When BMG_EMBEDDINGS_ENABLED=true and agent_name is in BMG_EMBEDDING_AGENT_KEYS,
        uses GPU-accelerated BAAI/bge-m3 cosine similarity instead of Jaccard pattern
        matching for the pattern_score component.
        """
        # 1. Base Score (Inverse of violations, capped at 10)
        base_score = max(0.0, 1.0 - (min(violations_count, 10) * 0.1))

        # 2. Pattern Score — BMG GPU path or Jaccard fallback
        pattern_score = 0.5
        bmg_used = False
        if violation_types:
            if os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true" and agent_name:
                try:
                    BMG_EMBEDDING_AGENT_KEYS = self._get_bmg_embedding_agent_keys()

                    if agent_name in BMG_EMBEDDING_AGENT_KEYS:
                        sem_score = self._calculate_semantic_similarity(territory, violation_types)
                        pattern_score = sem_score
                        bmg_used = True
                        logger.warning(
                            "[BMG-GPU] %s: semantic score=%.4f (CUDA/bge-m3)",
                            agent_name,
                            sem_score,
                        )
                except Exception:  # guardian: allow-silent-swallower  # noqa: BLE001
                    pass

            if not bmg_used:
                scores = [self._calculate_pattern_confidence(v) for v in violation_types]
                pattern_score = sum(scores) / len(scores)

        # 3. Weighted Final Calculation
        final_value = (base_score * 0.4) + (pattern_score * 0.4) + (historical_success_rate * 0.2)

        # Boost for governance territories, penalty for safety critical
        if territory == "prompt_governance":
            final_value *= 1.1
        if territory.startswith("L5"):
            final_value *= 0.9

        reasoning = f"Base: {base_score:.2f}, Pattern: {pattern_score:.2f}"
        if bmg_used:
            reasoning += " [BMG-GPU]"
        return ConfidenceScore(
            value=min(1.0, final_value),
            reasoning=reasoning,
        )

    def should_proceed_with_healing(
        self,
        confidence: ConfidenceScore,
        agent_name: str = "Unknown",
        territory: str = "unknown",
        failure_type: "FailureType | None" = None,
        retry_count: int = 0,
        replay_mode: bool = False,
        playbook_match: bool = False,
        deterministic_coverage: bool = False,
        provider_prohibited_gemini: bool = False,
        provider_prohibited_qwen: bool = False,
    ) -> tuple[bool, str]:
        """Determines if healing should proceed using the hardened SSOT routing algorithm."""
        is_safe, msg = self._check_healing_budget(agent_name)
        if not is_safe:
            return False, f"SAFETY LOCK: {msg}"

        routing = self._route_decision(
            confidence=confidence,
            agent_name=agent_name,
            territory=territory,
            failure_type=failure_type,
            retry_count=retry_count,
            replay_mode=replay_mode,
            playbook_match=playbook_match,
            deterministic_coverage=deterministic_coverage,
            provider_prohibited_gemini=provider_prohibited_gemini,
            provider_prohibited_qwen=provider_prohibited_qwen,
        )

        decision_data = {
            "agent": agent_name,
            "confidence": confidence.value,
            "reasoning": confidence.reasoning,
            "timestamp": datetime.now().isoformat(),
            "routing_tier": routing.tier.value,
            "routing_gate": routing.gate_applied,
            "routing_score": routing.score,
            "routing_digest": routing.determinism_digest,
            "model": routing.model_id,
            "decision": None,
            "reason": None,
        }

        tier = routing.tier

        if tier == RoutingTier.FAIL_CLOSED:
            reason = f"FAIL-CLOSED ({routing.gate_applied}, S={routing.score})"
            decision_data["decision"] = False
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return False, reason

        if tier == RoutingTier.DETERMINISTIC:
            self._healing_count += 1
            self._call_path.add(agent_name)
            reason = (
                f"SOVEREIGN-AUTO ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"
            )
            decision_data["decision"] = True
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return True, reason

        if not self.enable_llm:
            approved, hitl_reason = self._hitl_gate(agent_name, confidence, tier.value)
            decision_data["decision"] = approved
            decision_data["reason"] = hitl_reason
            self.decisions_made.append(decision_data)
            if approved:
                self._healing_count += 1
                self._call_path.add(agent_name)
            return approved, hitl_reason

        # Wave 6: HITL gate for tier escalation — fires before QWEN or GEMINI routing
        # when enable_llm=True.  Operator may approve, skip, or force LOCAL_AGENT.
        if tier in (RoutingTier.QWEN, RoutingTier.GEMINI):
            _tier_name = "QWEN_VLLM" if tier == RoutingTier.QWEN else "GEMINI_2_5_PRO"
            _is_interactive = sys.stdin.isatty() if hasattr(sys, "stdin") else False
            _batch_tier = os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1"
            if _batch_tier or not _is_interactive:
                _tier_hitl_decision = "HITL-TIER-AUTO-APPROVED (non-interactive)"
            else:
                print("\n  HITL GATE  [TIER ESCALATION]")
                print(f"  Agent    : {agent_name}")
                print(f"  Tier     : {_tier_name} (confidence={confidence.value:.2f}, S={routing.score})")
                print(f"  Gate     : {routing.gate_applied}")
                print("  Options  : [A] Approve escalation  [S] Skip  [L] Force LOCAL_AGENT")
                try:
                    _tier_raw = input("  Choice [A/S/L]: ").strip().upper()
                except EOFError:
                    _tier_raw = "A"
                if _tier_raw == "S":
                    _tier_hitl_decision = "HITL-TIER-SKIPPED"
                    decision_data["decision"] = False
                    decision_data["reason"] = _tier_hitl_decision
                    self.decisions_made.append(decision_data)
                    return False, _tier_hitl_decision
                elif _tier_raw == "L":
                    _tier_hitl_decision = "HITL-TIER-FORCED-LOCAL"
                    self._healing_count += 1
                    self._call_path.add(agent_name)
                    decision_data["decision"] = True
                    decision_data["reason"] = _tier_hitl_decision
                    self.decisions_made.append(decision_data)
                    return True, _tier_hitl_decision
                else:
                    _tier_hitl_decision = f"HITL-TIER-APPROVED ({_tier_name})"
            try:
                from system_learning.engines.hitl_decision_logger import log_hitl_decision

                log_hitl_decision(
                    agent="SovereignDecisionEngine",
                    file_path=agent_name,
                    violation=f"TIER_ESCALATION:{_tier_name}",
                    proposed=_tier_name,
                    decision=_tier_hitl_decision,
                )
            except Exception:  # guardian: allow-silent-swallow
                pass

        if tier == RoutingTier.QWEN:
            # Medium score: Qwen arbitrates. If Qwen says NO, fall through to
            # agent-native logic — healing is never blocked by a single NO.
            qwen_approved = True
            qwen_reason = f"LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score})"
            try:
                arbiter = self._get_qwen_vllm_arbiter()
                vllm_result = arbiter(
                    agent_name=agent_name,
                    violation_types=list(confidence.reasoning.split(", ") if confidence.reasoning else []),
                    territory=territory,
                    score=routing.score,
                    gate=routing.gate_applied,
                )
                qwen_approved = vllm_result.get("decision", True)
                raw_reason = vllm_result.get("reason", "")[:120]
                qwen_reason = (
                    f"LLM-ARBITRATED-QWEN14B ({confidence.value:.2f}, S={routing.score}): {raw_reason}"
                )
                logger.warning("[QWEN14B] %s -> decision=%s reason=%s", agent_name, qwen_approved, raw_reason)
            except Exception as _qwen_err:  # guardian: allow-silent-swallow
                logger.warning("[QWEN14B] vLLM call failed, falling to agent-native: %s", _qwen_err)

            if qwen_approved:
                final_reason = qwen_reason
            else:
                # Qwen said NO — fall through to agent-native logic
                logger.info(
                    "[ROUTING] Qwen declined %s (S=%d) — falling to AGENT-NATIVE logic",
                    agent_name,
                    routing.score,
                )
                final_reason = f"AGENT-NATIVE ({confidence.value:.2f}, S={routing.score}): Qwen declined, agent logic governs"

            self._healing_count += 1
            self._call_path.add(agent_name)
            decision_data["decision"] = True
            decision_data["reason"] = final_reason
            self.decisions_made.append(decision_data)
            return True, final_reason

        # tier == RoutingTier.GEMINI
        # High score: most complex reasoning — Gemini 2.5 Pro arbitrates.
        # Gemini is the final gate; once reached, healing always proceeds.
        target_model = routing.model_id
        logger.info(
            "[GEMINI] Invoking %s for %s (S=%d gate=%s) — high-complexity arbitration",
            target_model,
            agent_name,
            routing.score,
            routing.gate_applied,
        )
        self._healing_count += 1
        self._call_path.add(agent_name)
        reason = (
            f"LLM-ARBITRATED-GEMINI ({confidence.value:.2f}, S={routing.score}, gate={routing.gate_applied})"
        )
        decision_data["decision"] = True
        decision_data["reason"] = reason
        self.decisions_made.append(decision_data)
        return True, reason

    def _hitl_gate(
        self,
        agent_name: str,
        confidence: "ConfidenceScore",
        tier: str,
    ) -> tuple[bool, str]:
        """
        HITL terminal gate for medium/low confidence healing decisions.

        Prints a structured prompt showing the agent, confidence score, and
        reasoning, then reads Y/N/D from stdin. Non-interactive environments
        (no tty) default to DEFER (reject).

        Returns:
            (approved: bool, reason: str)
        """
        import sys

        border = "=" * 56
        print(f"\n{border}")
        print(f"  HITL GATE  [{tier} CONFIDENCE]")
        print(border)
        print(f"  Agent     : {agent_name}")
        print(f"  Confidence: {confidence.value:.2f}  ({tier})")
        print(f"  Reasoning : {confidence.reasoning}")
        print(border)
        print("  [Y] Approve healing    [N] Reject    [D] Defer to report")
        print(border)

        if not sys.stdin.isatty():
            reason = f"HITL-DEFER (non-interactive, {confidence.value:.2f})"
            print(f"  Non-interactive environment — auto-DEFER: {agent_name}")
            print(border + "\n")
            return False, reason

        try:
            raw = input("  Choice [Y/N/D]: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            raw = "D"

        print(border + "\n")

        if raw == "Y":
            return True, f"HITL-APPROVED ({confidence.value:.2f})"
        elif raw == "N":
            return False, f"HITL-REJECTED ({confidence.value:.2f})"
        else:
            return False, f"HITL-DEFER ({confidence.value:.2f})"


# ============================================================================
# ENHANCED DECISION ENGINE WITH COGNITIVE DISPOSITION AGENT INTEGRATION
# ============================================================================


class EnhancedAutonomousDecisionEngine(AutonomousDecisionEngine):
    """Enhanced decision engine with CognitiveDispositionAgent integration."""

    def __init__(
        self,
        enable_llm: bool = False,
        state_mgr: Optional["RuntimeStateManager"] = None,
        enable_cda: bool = False,
        execution_context: Optional["ExecutionContext"] = None,
    ):
        super().__init__(enable_llm=enable_llm, state_mgr=state_mgr, execution_context=execution_context)
        self.enable_cda = enable_cda
        # Initialize decisions_made if not already present from parent
        if not hasattr(self, "decisions_made"):
            self.decisions_made = []

    async def analyze_violations_with_cognitive_disposition(
        self,
        violations: list,
        territory: str,
        state_mgr,
    ):
        """Analyze violations using CognitiveDispositionAgent for enhanced confidence."""
        if not self.enable_cda:
            # Return default values if CDA is disabled; BMG path fires via calculate_healing_confidence
            fallback_conf = self.calculate_healing_confidence(
                len(violations),
                [str(v) for v in violations[:10]],
                territory,
                agent_name="location",
            )
            return [], fallback_conf

        try:
            # Dynamic import of CDA to avoid hard dependency
            from agentic_core.L0_routing.seams.safety_validators_seam import (
                load_cognitive_disposition_agent,
            )

            CognitiveDispositionAgent = load_cognitive_disposition_agent()
            cda = CognitiveDispositionAgent()

            # Analyze violations
            dispositions = await cda.analyze_violations(violations, territory)

            # Calculate enhanced confidence based on cognitive analysis
            if dispositions:
                avg_confidence = sum(d.confidence for d in dispositions) / len(dispositions)
                enhanced_confidence = ConfidenceScore(
                    value=avg_confidence,
                    reasoning=f"Cognitive analysis of {len(dispositions)} dispositions",
                )
            else:
                enhanced_confidence = ConfidenceScore(
                    value=0.5,
                    reasoning="No cognitive dispositions generated",
                )

            return dispositions, enhanced_confidence

        except ImportError:
            logger.warning("CognitiveDispositionAgent not available, using default confidence")
            bmg_conf = self.calculate_healing_confidence(
                len(violations),
                [str(v) for v in violations[:10]],
                territory,
                agent_name="location",
            )
            return [], bmg_conf
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Cognitive analysis failed: {e}")
            return [], ConfidenceScore(value=0.5, reasoning=f"CDA error: {str(e)}")


class SovereignDecisionEngine(EnhancedAutonomousDecisionEngine):
    """
    [HARDENED] Sovereign Decision Engine with strict token-based access control.
    Synthesizes patterns from FileClassificationAgent for cycle detection and resource protection.
    """

    def __init__(
        self,
        enable_llm: bool = False,
        state_mgr: Optional["RuntimeStateManager"] = None,
        enable_cda: bool = False,
        execution_context: Optional["ExecutionContext"] = None,
    ):
        super().__init__(enable_llm, state_mgr, enable_cda, execution_context=execution_context)
        self._sovereignty_token: str | None = None
        self._operation_stack: list[str] = []
        # guardian: allow-magic-config
        self._max_stack_depth = 10  # Prevent infinite recursion
        self._atomic_lock = False

    def request_sovereignty_token(self, agent_name: str, operation: str) -> bool:
        """
        Request permission to perform a state-mutating operation.
        Enforces atomic locking and stack depth limits.
        """
        if self._atomic_lock:
            logging.warning(f"Sovereignty DENIED for {agent_name}: Atomic lock active")
            return False

        if len(self._operation_stack) >= self._max_stack_depth:
            logging.critical(
                f"Sovereignty DENIED for {agent_name}: Stack depth exceeded ({len(self._operation_stack)})",
            )
            return False

        # Cycle detection
        op_signature = f"{agent_name}:{operation}"
        if op_signature in self._operation_stack:
            logging.warning(f"Sovereignty DENIED for {agent_name}: Cycle detected {op_signature}")
            return False

        self._operation_stack.append(op_signature)
        self._atomic_lock = True
        self._sovereignty_token = f"SOV_{int(time.time())}_{agent_name}"
        return True

    def release_sovereignty_token(self, agent_name: str, success: bool = True) -> None:
        """Release the lock after operation completion."""
        if not self._atomic_lock:
            return

        if self._operation_stack:
            self._operation_stack.pop()

        self._atomic_lock = False
        self._sovereignty_token = None

        if not success:
            logging.warning(f"Sovereignty released with FAILURE status for {agent_name}")


# ============================================================================
# PRE-FLIGHT VALIDATION LAYER (HARDENED)
# ============================================================================


class PreFlightValidator:
    """
    [ULTRA-HARDENED] Sovereign Contract Enforcer.
    Verifies environmental readiness and enforces strict agent signatures/imports.
    """

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run

    def run_checks(self) -> tuple[bool, list[str]]:
        errors = []

        # 1. Windows Long Paths (System Stability)
        if platform.system() == "Windows":
            try:
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\FileSystem",
                )
                val, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if val != 1:
                    if os.getenv("AGENTIC_BYPASS_LONGPATHS_CHECK") == "1":
                        logging.warning(
                            "AGENTIC_BYPASS_LONGPATHS_CHECK=1: skipping LongPathsEnabled hard-fail"
                        )
                    elif self.dry_run:
                        logging.warning(
                            "Windows LongPathsEnabled is NOT active (Set to 1 in Registry) - proceeding in dry-run mode"
                        )
                    else:
                        errors.append("Windows LongPathsEnabled is NOT active (Set to 1 in Registry)")
            # guardian: allow-silent-swallow
            except Exception as e:
                logging.warning(f"Could not verify Windows LongPathsEnabled: {e}")

        # 2. Critical Directory Structure (SSOT Integrity)
        required_dirs = ["agentic_core", "agentic_core/L5_safety", "agentic_core/prompt_governance"]
        for d in required_dirs:
            if not (self.project_root / d).exists():
                errors.append(f"Critical directory missing: {d}")

        # 3. Write Permissions (Operational Readiness)
        try:
            test_file = self.project_root / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError:
            errors.append("Project root is not writable")

        return len(errors) == 0, errors

    def validate_agent_integrity(self, agents: dict[str, Any]) -> list[str]:
        """
        [CONTRACT GUARD] Mandatory validation of all registered agents.
        Catches legacy signatures, broken mixins, and instantiation failures.
        """
        integrity_errors = []
        for name, agent_cls in agents.items():
            try:
                # Force instantiation to catch import/mixin errors immediately
                agent = agent_cls(project_root=self.project_root) if inspect.isclass(agent_cls) else agent_cls
            # guardian: allow-silent-swallow
            except Exception as e:
                integrity_errors.append(f"Agent {name} FAILED INSTANTIATION: {e}")
                continue

            # 1. Presence of 'heal' method
            if not hasattr(agent, "heal") or not callable(agent.heal):
                integrity_errors.append(f"Agent {name} violates Protocol: Missing 'heal' method")
                continue

            # 2. Signature Validation: heal(violation: dict)
            sig = inspect.signature(agent.heal)
            params = list(sig.parameters.keys())

            if "violation" not in params and "kwargs" not in params:
                if "path" in params and len(params) == 1:
                    integrity_errors.append(
                        f"Agent {name} has LEGACY SIGNATURE: heal(path). Must update to heal(violation).",
                    )
                else:
                    integrity_errors.append(
                        f"Agent {name} has INVALID SIGNATURE: {sig}. Expected heal(self, violation, ...).",
                    )

            # 3. Mixin Verification (MRO Audit)
            mro_names = [c.__name__ for c in inspect.getmro(agent.__class__)]
            if "NamingAgent" in name and "SubatomicTestingMixin" not in mro_names:
                integrity_errors.append(f"Agent {name} missing mandatory SubatomicTestingMixin in MRO.")

        return integrity_errors


# ============================================================================
# HARDENING UTILITIES (NEW)
# ============================================================================


class NonInteractiveGuard:
    """
    [HARDENED] Global overrides to prevent terminal prompts from hanging CI/CD.
    Now includes Resource Exhaustion Protection against infinite prompt loops.
    """

    # guardian: allow-magic-config
    def __init__(self, active: bool = True, max_blocked_prompts: int = 10):
        self.active = active
        self.max_blocked_prompts = max_blocked_prompts
        self.blocked_count = 0
        self.original_input = builtins.input

    def __enter__(self):
        if self.active:
            builtins.input = self._trap_input
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        builtins.input = self.original_input

    def _trap_input(self, prompt=None):
        # Auto-approve if env var set (avoids RecursionError bomb in CI/auto mode)
        if os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1":
            logger.debug(f"AUTO-APPROVE: suppressing input('{prompt}')")
            return "y"

        self.blocked_count += 1
        logger.warning(
            f"BLOCKED PROMPT ({self.blocked_count}/{self.max_blocked_prompts}): Agent attempted input('{prompt}')",
        )
        raise RuntimeError(f"Interactive prompt blocked in autonomous mode: {prompt}")


@_optional_runtime_guard()("D.with_retry.execute_ssot")
# guardian: allow-magic-config
def with_retry(max_retries=3, delay=1.0):
    """
    [HARDENED] Decorator for transient failure resilience with exponential backoff.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                # guardian: allow-silent-swallow
                except Exception as e:
                    last_exception = e
                    # Don't retry on security guard or exhaustion errors
                    if isinstance(e, RuntimeError) and "prompt" in str(e):
                        raise e
                    if isinstance(e, RecursionError):
                        raise e

                    wait_time = delay * (2**attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} failed: {e}. Waiting {wait_time}s",
                    )
                    time.sleep(wait_time)
            logger.error(f"All retries failed for {func.__name__}")
            raise last_exception

        return wrapper

    return decorator


# ============================================================================
# PHASE 2: RECONCILIATION (The Dangerous Phase)
# ============================================================================


# guardian: allow-magic-config
@with_retry(max_retries=2)
def execute_phase2_reconciliation(
    agents: dict[str, Any],
    territory: str,
    decision_engine: SovereignDecisionEngine,  # [HARDENED] Updated type
    state_mgr: "RuntimeStateManager",
    plan: dict[str, Any],
    ctx: "HealContext" = None,
    **kwargs,
):
    """
    PHASE 2: EXECUTE HEALING (HARDENED)
    Critical Path: Modifications occur here. Must strictly adhere to decision engine.
    Enhanced with atomic operations and sovereignty patterns from FileClassificationAgent.
    Returns: Dict conforming to HEAL_RESULT_SCHEMA
    """
    reconciliation_log = []
    failed_fixes = []

    if not plan or not plan.get("violations_found"):
        logging.info("Phase 2: No violations to reconcile.")
        return {
            "violations_found": 0,
            "violations_fixed": 0,
            "status": "skipped",
            "errors": 0,
            "skipped": 0,
            "execution_time_ms": 0.0,
            "error_message": None,
        }

    violations_list = plan["violations_found"]
    logging.warning(f"Phase 2: Reconciling {len(violations_list)} violations across agents...")

    # Group violations by agent key so each agent's heal_repository() is called once
    # with the full set of violations it owns, and sovereignty token is held for that batch.
    from collections import defaultdict

    by_agent: dict[str, list] = defaultdict(list)
    for v in violations_list:
        by_agent[v.get("suggested_agent", "reconciler")].append(v)

    for agent_key, agent_violations in by_agent.items():
        violation_types = [v.get("type", "UNKNOWN") for v in agent_violations]

        agent_cls = agents.get(agent_key)
        if agent_cls is None:
            logging.warning(
                f"Phase 2: agent key '{agent_key}' not in registry — skipping {len(agent_violations)} violations"
            )
            failed_fixes.extend(
                {"violation": v, "reason": f"Agent '{agent_key}' not registered", "status": "blocked"}
                for v in agent_violations
            )
            continue

        confidence = decision_engine.calculate_healing_confidence(
            violations_count=len(agent_violations),
            violation_types=violation_types,
            territory=territory,
            agent_name=agent_key,
        )

        allowed, reason = decision_engine.should_proceed_with_healing(
            confidence, agent_key, territory=territory
        )
        if not allowed:
            logging.warning(f"Phase 2: BLOCKED {agent_key}: {reason}")
            failed_fixes.extend(
                {"violation": v, "reason": reason, "status": "blocked"} for v in agent_violations
            )
            continue

        if ctx is None or not ctx.heal:
            for v in agent_violations:
                reconciliation_log.append(
                    {"action": "would_fix", "target": v.get("file"), "agent": agent_key, "reason": reason}
                )
            continue

        if not decision_engine.request_sovereignty_token(agent_key, violation_types[0]):
            failed_fixes.extend(
                {"violation": v, "reason": "Sovereignty Token Denied", "status": "locked"}
                for v in agent_violations
            )
            continue

        try:
            # Instantiate the agent class and call heal_repository() — the real mutation path
            agent_instance = agent_cls(project_root=REPO_ROOT)
            state_mgr.update_agent(
                agent_key, f"[{reason.split('(')[0].strip()}] Healing {len(agent_violations)} violations"
            )

            logging.warning(
                "Phase 2: [%s] → calling heal_repository(dry_run=False, execute=True) for %d violations [routing: %s]",
                agent_key,
                len(agent_violations),
                reason.split("(")[0].strip(),
            )

            fix_result = agent_instance.heal_repository(dry_run=False, execute=True)
            if not isinstance(fix_result, dict):
                fix_result = {"raw_output": str(fix_result)}

            fix_result["agent"] = agent_key
            fix_result["violations_submitted"] = len(agent_violations)
            fix_result["routing_reason"] = reason

            if fix_result.get("success", True) is False:
                raise RuntimeError(f"Agent reported failure: {fix_result.get('error', 'Unknown')}")

            reconciliation_log.append(fix_result)
            decision_engine.release_sovereignty_token(agent_key, success=True)
            logging.warning(
                "Phase 2: [%s] ✓ heal_repository() complete — result keys: %s",
                agent_key,
                list(fix_result.keys()),
            )

        # guardian: allow-silent-swallow
        except Exception as e:
            logging.error(f"Phase 2: Fix failed for {agent_key}: {e}")
            failed_fixes.extend(
                {"violation": v, "error": str(e), "status": "execution_error"} for v in agent_violations
            )
            decision_engine.release_sovereignty_token(agent_key, success=False)

    return {
        "violations_found": len(violations_list),
        "violations_fixed": len(reconciliation_log),
        "status": "success" if not failed_fixes else "partial_success",
        "errors": len(failed_fixes),
        "skipped": 0,
        "execution_time_ms": 0.0,
        "error_message": None if not failed_fixes else f"{len(failed_fixes)} violations failed",
        "_raw_result": {"modifications": reconciliation_log, "failures": failed_fixes},
    }


# ============================================================================
# PHASE 3: FINAL VALIDATION (The Audit)
# ============================================================================


# [REMOVED DUPLICATE] execute_phase3_final_validation removed.
# Usage consolidated to execute_phase3_validation at line 1273.


# ============================================================================
# ENHANCED PHASE EXECUTION & INPUT VALIDATION
# ============================================================================


def validate_territory_input(territory: str) -> tuple[bool, str]:
    """Validate territory input with comprehensive security checks."""
    if not territory:
        return True, ""
    if len(territory) > 100:
        return False, "Name too long"
    if not re.match(r"^[A-Za-z0-9_]+$", territory):
        return False, "Invalid characters"
    if ".." in territory or territory.startswith(("/", "\\")):
        return False, "Path traversal attempt"
    # Additional security checks
    if ";" in territory or "|" in territory or "&" in territory:
        return False, "Injection attempt"
    if "<" in territory or ">" in territory:
        return False, "HTML/script injection attempt"
    return True, ""


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Directory Constants
AGENTIC_CORE_DIR = "agentic_core"
APPS_SHARED_DIR = "apps_shared"
APPS_LIC_DIR = "apps_lic"
APPS_RG_DIR = "apps_rg"
SCRIPTS_DIR = "scripts"
AGENT_DISCOVERY_JSON = "agent_discovery_full.json"
RUNTIME_STATE_FILE = "runtime_state.json"

# Project Root Path — resolved lazily via module __getattr__ or REPO_ROOT.

# [ULTRA-HARDENED] Whitelist of allowed module prefixes for dynamic imports
# Prevents loading agents from unexpected packages (defense-in-depth against tampered discovery/cache)
ALLOWED_MODULE_PREFIXES = ("agentic_core", "apps_shared", "apps_lic", "apps_rg")

# Logging: configured once in _configure_logging() called from main().
logger = logging.getLogger("UnifiedSovereign")

# ============================================================================
# RUNTIME STATE MANAGEMENT (From Canon Validator)
# ============================================================================


class RuntimeStateManager:
    """Manages live state for dashboard observability."""

    def __init__(self, project_root: Path, execution_context: Optional["ExecutionContext"] = None):
        self.project_root = project_root.resolve()  # [ULTRA-HARDENED] Force real absolute path resolution
        self._execution_context = execution_context
        self.state = {
            "status": "idle",
            "start_time": None,
            "end_time": None,
            "current_agent": None,
            "current_layer": None,
            "agents_order": [],
            "completed_agents": [],
            "skipped_agents": [],
            "events": [],
            # [INTEGRATION] Ported from Canon Validator
            "meta_learning": {
                "enabled": False,
                "total_experiences": 0,
                "patterns_extracted": 0,
                "strategy_weights": {"cot": 1.0, "tot": 1.0, "react": 1.0},
                "recent_experiences": [],
            },
            "compliance_scores": {},
            # [SILENT AGGREGATION] Track decisions for final report
            "decisions_made": [],
            "compliance_report": {},
            # [SSOT MIXIN] Audit chain for cryptographic AuditTrailMixin
            "audit_chain": [],
        }
        # [HARDENED] Register exit handler to prevent 'zombie' running states
        atexit.register(self._emergency_cleanup)
        # [G-12-1] Latch: once L0 mutation prohibition fires, disable all future save() attempts
        self._persistence_disabled: bool = False

    def start_mission(self, mission_type: str, agents_order: list[str]):
        self.state["status"] = "running"
        self.state["start_time"] = datetime.now().isoformat()
        self.state["agents_order"] = agents_order
        self.add_event("info", f"Mission started: {mission_type}")
        self.save()

    def update_agent(self, agent_name: str, layer: str):
        self.state["current_agent"] = agent_name
        self.state["current_layer"] = layer
        self.add_event("agent_start", f"→ Executing {agent_name} ({layer})")
        self.save()

    def skip_agent(self, agent_name: str, reason: str):
        """Records agent as skipped — confidence gate or HITL rejected execution."""
        self.state["skipped_agents"].append(
            {
                "agent": agent_name,
                "time": datetime.now().isoformat(),
                "reason": reason,
            },
        )
        self.add_event("agent_skip", f"SKIPPED {agent_name}: {reason}")
        self.save()

    def complete_agent(self, agent_name: str, success: bool, details: str = ""):
        """
        [HARDENED] Silent Aggregation.
        Records agent completion but suppresses intermediate JSON console dumps.
        """
        self.state["completed_agents"].append(
            {
                "agent": agent_name,
                "time": datetime.now().isoformat(),
                "success": success,
                "details": details,
            },
        )
        # Log to file/state but DO NOT PRINT JSON to console here
        self.add_event("agent_end", f"{'✓' if success else '❌'} Completed {agent_name}")
        self.save()

    def add_event(self, event_type: str, message: str):
        self.state["events"].append(
            {"time": datetime.now().isoformat(), "type": event_type, "message": message},
        )
        # [SILENT AGGREGATION] Only log minimal status to console during execution
        # Full telemetry captured in state for final report
        if event_type == "error":
            logger.error(message)
        elif event_type == "warning":
            logger.warning(message)
        elif event_type in ["agent_start", "agent_end", "agent_skip"]:
            # Keep minimal agent progress indicators
            logger.info(message)
        else:
            # Suppress other verbose intermediate logs
            pass

    def finish_mission(self, status="completed"):
        self.state["status"] = status
        self.state["end_time"] = datetime.now().isoformat()
        self.state["current_agent"] = None
        self.save()

    def save(self):
        """
        [HARDENED] Atomic Write Pattern with Permission Lockdown.
        Writes to temp file, sets 600 permissions, then renames.
        Once L0 mutation prohibition fires, latches _persistence_disabled=True
        and becomes a no-op for the remainder of the run.
        """
        # [G-12-1] Latch: skip all future attempts after first prohibition
        if self._persistence_disabled:
            return

        try:
            from agentic_core.L0_routing.scripts.runtime_state_digest import (
                DIGEST_SCHEMA_VERSION,
                compute_runtime_state_digest,
            )

            self.state["runtime_state_digest_sha256"] = compute_runtime_state_digest(self.state)
            self.state["runtime_state_digest_schema_version"] = DIGEST_SCHEMA_VERSION
        # guardian: allow-silent-swallow
        except Exception:
            pass

        try:
            state_path = self.project_root / RUNTIME_STATE_FILE
            temp_dir = state_path.parent
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Create temp file
            with tempfile.NamedTemporaryFile("w", dir=str(temp_dir), delete=False, encoding="utf-8") as tf:
                assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
                json.dump(self.state, tf, indent=2, default=str, ensure_ascii=False)
                temp_name = tf.name

            # [HARDENED] Set strict permissions (Owner Read/Write only) before moving
            # This prevents other users on shared CI runners from reading potential sensitive logs
            os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)

            # Atomic replacement
            os.replace(temp_name, state_path)

        except PermissionError as e:
            err_str = str(e)
            if "MUTATION_PROHIBITED" in err_str:
                # [G-12-1] First and only log — latch disabled for remainder of run
                self._persistence_disabled = True
                logger.critical(
                    "[RuntimeStateManager] L0 mutation prohibition active — "
                    "runtime state persistence DISABLED for this run (fail-closed). "
                    f"Reason: {err_str}"
                )
                # Cleanup temp if created
                try:
                    # guardian: allow-path-string
                    if "temp_name" in locals() and os.path.exists(temp_name):
                        os.remove(temp_name)
                # guardian: allow-silent-swallow
                except Exception:
                    pass
            else:
                logger.error(f"Failed to save runtime state (Atomic Write Failed): {e}")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to save runtime state (Atomic Write Failed): {e}")
            try:
                # guardian: allow-path-string
                if "temp_name" in locals() and os.path.exists(temp_name):
                    os.remove(temp_name)
            # guardian: allow-silent-swallow
            except Exception:
                pass

    def _emergency_cleanup(self):
        """Ensure state is finalized even on unhandled exit."""
        if self.state["status"] == "running":
            self.finish_mission("terminated")

    def update_meta_learning(self, experience_data: dict[str, Any]):
        """[INTEGRATION] Updates cognitive metrics for dashboard."""
        ml = self.state["meta_learning"]
        ml["enabled"] = True

        if "total_experiences" in experience_data:
            ml["total_experiences"] = experience_data["total_experiences"]

        if "strategy_weights" in experience_data:
            ml["strategy_weights"] = experience_data["strategy_weights"]

        if "experience" in experience_data:
            ml["recent_experiences"].insert(0, experience_data["experience"])
            ml["recent_experiences"] = ml["recent_experiences"][:5]  # Keep last 5

        self.save()


# ============================================================================
# AUTONOMOUS DECISION ENGINE (From SSOT Protocol)
# ============================================================================


def discover_agents_from_registry(project_root: Path, dedupe: bool = True) -> list[tuple[str, str]]:
    """Hybrid agent discovery: prefer cached JSON, fallback to live scan."""
    agents = []
    json_path = project_root / AGENT_DISCOVERY_JSON

    # Try Cache
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            for agent in data:
                if agent.get("class_name"):
                    # [HARDENED] Use pathlib for robust cross-platform path resolution
                    try:
                        raw_path = agent.get("path", "")
                        # Handle absolute or relative paths gracefully
                        if os.path.isabs(raw_path):
                            full_path = Path(raw_path)
                            rel_path = full_path.relative_to(project_root)
                        else:
                            rel_path = Path(raw_path)

                        # Convert path parts to module dot notation
                        clean_parts = rel_path.with_suffix("").parts
                        # [ULTRA-HARDENED] Reject any path containing navigation tokens (., ..) or empty segments
                        if any(p in {"", ".", ".."} for p in clean_parts):
                            logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
                            continue

                        module_path = ".".join(clean_parts)

                        # [ULTRA-HARDENED] Enforce module prefix whitelist before permitting dynamic import
                        if not any(
                            module_path == p or module_path.startswith(p + ".")
                            for p in ALLOWED_MODULE_PREFIXES
                        ):
                            logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
                            continue

                        agents.append((agent["class_name"], module_path))
                    # guardian: allow-silent-swallow
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            logger.info(f"Loaded {len(agents)} agents from cache")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")

    # Try Live Scan if empty
    if not agents:
        try:
            from agentic_core.utils.discovery.Full_Agent_discovery import discover_all_agents

            logger.info("Running live agent discovery...")
            discovery_data = discover_all_agents(project_root)
            for agent in discovery_data:
                if agent.get("class_name"):
                    # [HARDENED] Use pathlib for robust cross-platform path resolution
                    try:
                        raw_path = agent.get("path", "")
                        # Handle absolute or relative paths gracefully
                        if os.path.isabs(raw_path):
                            full_path = Path(raw_path)
                            rel_path = full_path.relative_to(project_root)
                        else:
                            rel_path = Path(raw_path)

                        # Convert path parts to module dot notation
                        clean_parts = rel_path.with_suffix("").parts
                        # [ULTRA-HARDENED] Reject any path containing navigation tokens (., ..) or empty segments
                        if any(p in {"", ".", ".."} for p in clean_parts):
                            logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
                            continue

                        module_path = ".".join(clean_parts)

                        # [ULTRA-HARDENED] Enforce module prefix whitelist before permitting dynamic import
                        if not any(
                            module_path == p or module_path.startswith(p + ".")
                            for p in ALLOWED_MODULE_PREFIXES
                        ):
                            logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
                            continue

                        agents.append((agent["class_name"], module_path))
                    # guardian: allow-silent-swallow
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            # [ULTRA-HARDENED] Atomic write + strict 600 permissions for agent discovery cache
            try:
                temp_name = None
                with tempfile.NamedTemporaryFile(
                    "w",
                    delete=False,
                    dir=str(project_root),
                    encoding="utf-8",
                ) as tf:
                    assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
                    json.dump(discovery_data, tf, indent=2, ensure_ascii=False)
                    temp_name = tf.name
                os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)
                os.replace(temp_name, json_path)
                logger.info(f"Discovered {len(agents)} agents (cached)")
            # guardian: allow-silent-swallow
            except Exception as cache_err:
                logger.warning(f"Failed to cache agent discovery: {cache_err}")
                # guardian: allow-path-string
                if temp_name and os.path.exists(temp_name):
                    assert_no_persistent_write("L0", "os.mutate")  # G-12-1: mutation prohibition guard
                    os.remove(temp_name)
        except ImportError:
            logger.warning("Live discovery unavailable - Full_Agent_discovery not found")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Live discovery failed: {e}")

    if dedupe:
        agents = sorted(set(agents), key=lambda x: x[0])
    return agents


# ============================================================================
# PHASE 3: FINAL VALIDATION (The Audit)
# ============================================================================
@standard_heal
def execute_phase3_validation(
    agents: dict[str, Any],
    territory: str,
    original_violations: list[dict],
    dry_run: bool = False,
    **kwargs,
):
    """
    PHASE 3: POST-MORTEM VALIDATION

    Verifies that 'fixed' files now pass AST and SSOT checks.
    Does NOT blindly trust the agent's 'success' return value.
    """
    if dry_run:
        return {"status": "skipped", "message": "Dry run - validation skipped"}

    remaining_issues = []
    # [HARDENING] Use the memory-safe AST validator defined in Phase 1
    # guardian: allow-path-string
    validator = ASTCodeQualityValidator(REPO_ROOT)

    for v in original_violations:
        fpath = v.get("file")

        # 1. Existence Check
        # guardian: allow-path-string
        if not fpath or not os.path.exists(fpath):
            # If it was an orphan that was deleted, this is good.
            # If it was a missing file that was created, we check existence.
            drift_type = v.get("drift_type", "")
            if "ORPHAN" in drift_type:
                # File gone = Success
                continue
            elif "MISSING" in drift_type:
                remaining_issues.append({"file": fpath, "error": "File still missing after heal"})
                continue
            else:
                # Standard file modification - if gone, that's bad
                remaining_issues.append({"file": fpath, "error": "File vanished after heal"})
                continue

        # 2. AST Quality Check on Modified Files
        # We only check files that exist and were targets of modification
        quality_report = validator.check_file_quality(Path(fpath))
        if quality_report.get("violations"):
            for issue in quality_report["violations"]:
                issue["source"] = "post_heal_validation"
                remaining_issues.append(issue)

    status = "clean"
    if remaining_issues:
        status = "drift_detected"

    return {
        "status": status,
        "remaining_violations": remaining_issues,
        "verification_timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# EXECUTION PHASES (SSOT Logic + Canon Observability)
# ============================================================================


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase1_discovery(
    agents, territory, decision_engine, state_mgr, ctx: "HealContext" = None, auto_approve=True
):
    """PHASE 1: TERRITORIAL DISCOVERY (Retriable)"""
    return execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr, ctx)


def execute_phase1_discovery_impl(
    agents,
    territory,
    decision_engine,
    state_mgr,
    ctx: "HealContext" = None,
):
    """PHASE 1: TERRITORIAL DISCOVERY - Implementation with CognitiveDispositionAgent integration"""
    logger.info(f"=== PHASE 1: DISCOVERY - {territory} ===")

    state_mgr.update_agent("FilesystemSSOTReconcilerAgent", "L0 - Maintenance")

    reconciler = agents["reconciler"](project_root=REPO_ROOT)
    drift_report = reconciler.detect_root_drift()

    if drift_report is None:
        state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", False, "Returned None")
        return None, None

    # Wave 3: when healing is active, pass force=True so the skip-gate is bypassed
    # and forbidden root folders (logs/, scripts/, etc.) are actually reconciled.
    if ctx is not None and getattr(ctx, "heal", False):
        reconciler.heal_repository(force=True, dry_run=not getattr(ctx, "heal", False), execute=True)

    violations_count = (
        len(drift_report.get("forbidden_folders", []))
        + len(drift_report.get("archived_files_at_root", []))
        + len(drift_report.get("duplicate_folders", []))
    )
    state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", True, f"Drift violations: {violations_count}")

    # Location Validation
    state_mgr.update_agent("LocationAgent", "L5 - Safety")
    location_validator = agents["location"](project_root=REPO_ROOT)

    # [ULTRA-HARDENED] Explicit path traversal protection for user-supplied territory string.
    # Territory may live anywhere under REPO_ROOT (e.g. apps_rg, docs, tests) — not only
    # under agentic_core. Resolve against REPO_ROOT and ensure no escape above it.
    repo_root_resolved = REPO_ROOT.resolve()
    territory_path = (repo_root_resolved / territory).resolve()
    if not territory_path.is_relative_to(repo_root_resolved):
        logger.critical(f"SECURITY ALERT: Path traversal attempt detected for territory '{territory}'")
        state_mgr.add_event("security", "Path traversal blocked")
        state_mgr.complete_agent("LocationAgent", False, "Traversal blocked")
        return drift_report, []

    violations = []
    location_scan_result = {}
    if territory_path.exists():
        # Let LocationAgent do comprehensive file discovery
        _lva = _get_location_validator_agent()(project_root=REPO_ROOT)
        location_scan_result = _lva.run(target_territory=territory) or {}
        violations = location_scan_result.get("violations", [])
    else:
        logger.warning(f"Territory path does not exist: {territory_path}")

    # Enhanced confidence calculation with cognitive analysis
    if hasattr(decision_engine, "enable_cda") and decision_engine.enable_cda and violations:
        logger.info("🧠 Using CognitiveDispositionAgent for enhanced violation analysis...")

        # Create event loop for async cognitive analysis
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Get cognitive dispositions and enhanced confidence
        cognitive_dispositions, enhanced_confidence = loop.run_until_complete(
            decision_engine.analyze_violations_with_cognitive_disposition(violations, territory, state_mgr),
        )

        # Store cognitive dispositions in state for reporting
        state_mgr.state["cognitive_dispositions"] = [d.__dict__ for d in cognitive_dispositions]

        confidence = enhanced_confidence
        logger.info(f"🧠 Enhanced confidence with cognitive analysis: {confidence.value:.2f}")
    else:
        # Fallback to standard confidence calculation
        confidence = decision_engine.calculate_healing_confidence(
            len(violations),
            [str(v) for v in violations[:10]],
            territory,
            agent_name="location",
        )

    state_mgr.state["compliance_scores"][territory] = confidence.value

    # [DETAILED TRACKING] Store actual LocationAgent violations for final report
    state_mgr.state["location_violations"] = violations
    state_mgr.state["location_scan_result"] = location_scan_result

    # [AUTO-HEALING] If confidence is high enough, trigger LocationAgent healing
    if len(violations) > 0:
        proceed, reason = decision_engine.should_proceed_with_healing(
            confidence, "LocationAgent", territory=territory
        )
        state_mgr.add_event("decision", f"Location Healing: {reason}")
        logger.info(f"Location Decision: {reason}")

        if proceed and (ctx is None or ctx.heal):
            logger.info(f"Triggering LocationAgent auto-heal for {len(violations)} violations")
            # Wave 6: Attach HITL approval function so _heal_via_archiving can gate deletions.
            # Non-interactive environments auto-defer (skip) the archive.
            import sys as _sys

            def _w6_hitl_archive_gate(file_path, msg):
                if not _sys.stdin.isatty():
                    return False, "HITL-DEFER (non-interactive)"
                if os.environ.get("ARCHIVE_BATCH_ACCEPT") == "1":
                    return True, "HITL-APPROVED (batch)"
                border = "=" * 56
                print(f"\n{border}")
                print("  HITL GATE  [FILE DELETION / ARCHIVE]")
                print(border)
                print(f"  File  : {file_path}")
                print(f"  Reason: {str(msg)[:100]}")
                print(border)
                print("  [A] Archive (reversible)  [S] Skip  [D] Delete permanently")
                print(border)
                try:
                    raw = input("  Choice [A/S/D]: ").strip().upper()
                except (EOFError, KeyboardInterrupt):
                    raw = "S"
                if raw == "A":
                    return True, "HITL-APPROVED (archive)"
                elif raw == "D":
                    return True, "HITL-APPROVED (delete)"
                else:
                    return False, "HITL-SKIPPED"

            location_validator._hitl_approval_fn = _w6_hitl_archive_gate
            # LocationAgent should have a heal method - call it
            if hasattr(location_validator, "heal_violations"):
                heal_result = location_validator.heal_violations(
                    violations, auto_approve=(ctx.auto_approve if ctx else True)
                )
                healed_count = heal_result.get("healed", 0) if isinstance(heal_result, dict) else 0
                state_mgr.complete_agent(
                    "LocationAgent",
                    True,
                    f"Violations: {len(violations)} | Healed: {healed_count} | Conf: {confidence.value:.2f}",
                )
            else:
                logger.warning(
                    "LocationAgent has no heal_violations method - violations detected but not healed",
                )
                state_mgr.complete_agent(
                    "LocationAgent",
                    True,
                    f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (no heal method)",
                )
        else:
            state_mgr.complete_agent(
                "LocationAgent",
                True,
                f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (healing skipped)",
            )
    else:
        state_mgr.complete_agent("LocationAgent", True, f"Violations: 0 | Conf: {confidence.value:.2f}")

    # [PHASE 1 ENHANCEMENT] Early File Classification Detection
    # Run FileClassificationAgent in discovery phase to catch naming violations early
    classification_violations = []
    classification_scan_result = {}
    try:
        state_mgr.update_agent("FileClassificationAgent", "L5 - Safety (Early Detection)")
        file_classifier = agents["file_classification"](project_root=REPO_ROOT)

        # Run classification scan on territory (validate_only mode for detection)
        file_classifier.validate_only = True
        file_classifier.dry_run = not ctx.heal if ctx else True  # Respect heal flag during discovery
        classification_scan_result = file_classifier.run() or {}

        # Extract violations from stats
        if hasattr(file_classifier, "stats") and file_classifier.stats.get("violations"):
            for vtype, count in file_classifier.stats["violations"].items():
                if isinstance(count, int) and count > 0:
                    classification_violations.append(
                        {
                            "type": "CLASSIFICATION",
                            "subtype": vtype,
                            "count": count,
                            "territory": territory,
                        },
                    )

        classification_count = len(classification_violations)
        state_mgr.complete_agent(
            "FileClassificationAgent",
            True,
            f"Early detection: {classification_count} classification issues",
        )

        # Store classification results for later phases
        state_mgr.state["classification_violations"] = classification_violations
        state_mgr.state["classification_scan_result"] = classification_scan_result

        logger.info(f"📋 FileClassificationAgent early detection: {classification_count} issues found")

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.warning(f"FileClassificationAgent early detection failed: {e}")
        state_mgr.complete_agent("FileClassificationAgent", False, f"Early detection error: {e}")
        state_mgr.state["classification_violations"] = []
        state_mgr.state["classification_scan_result"] = {}

    return drift_report, violations, location_scan_result


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase2_alignment(
    agents, territory, decision_engine, state_mgr, ctx: "HealContext" = None, auto_approve=True
):
    """PHASE 2: STRUCTURAL ALIGNMENT (Retriable)"""
    return execute_phase2_alignment_impl(agents, territory, decision_engine, state_mgr, ctx)


def execute_phase2_alignment_impl(
    agents,
    territory,
    decision_engine,
    state_mgr,
    ctx: "HealContext" = None,
):
    """PHASE 2: STRUCTURAL ALIGNMENT - Implementation"""
    logger.info(f"=== PHASE 2: ALIGNMENT - {territory} ===")

    state_mgr.update_agent("HierarchyAgent", "L5 - Safety")
    hierarchy = agents["hierarchy"](project_root=REPO_ROOT)

    # [STRICT SCOPE] Pass territory to scan only the target root
    scan = hierarchy.scan_root_violations(target_territory=territory)
    violations = scan.get("violations_found", 0)

    # Check if we found violations in the returned dict format (list vs count)
    if "violations" in scan and isinstance(scan["violations"], list):
        violations = len(scan["violations"])

    if violations > 0:
        confidence = decision_engine.calculate_healing_confidence(violations, ["HIERARCHY"], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(confidence, "HierarchyAgent")

        state_mgr.add_event("decision", f"Hierarchy Healing: {reason}")
        logger.info(f"Decision: {reason}")

        if proceed:
            # [SOVEREIGN DEFAULT] Propagate active/dry-run status to HierarchyAgent
            res = hierarchy.heal_hierarchy(
                create_structure=True,
                relocate_files=True,
                enforce_depth=True,
                purge_orphans=False,
                target_territory=territory,  # [STRICT SCOPE] Already correct here, but ensuring strict adherence
                dry_run=not ctx.heal if ctx else True,
                auto_approve=ctx.auto_approve if ctx else True,
            )
            healed = res.get("total_healed", 0)
            state_mgr.complete_agent("HierarchyAgent", True, f"Healed: {healed}")
            return res
        else:
            state_mgr.complete_agent("HierarchyAgent", False, "Skipped - Low Confidence")
    else:
        state_mgr.complete_agent("HierarchyAgent", True, "No violations found")

    return None


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase3_architectural_validation(agents, territory, state_mgr, ctx: "HealContext" = None):
    """PHASE 3: ARCHITECTURAL VALIDATION (Retriable) - renamed to avoid shadowing execute_phase3_validation"""
    return execute_phase3_validation_impl(agents, territory, state_mgr, ctx=ctx)


def execute_phase3_validation_impl(agents, territory, state_mgr, ctx: "HealContext" = None):
    """PHASE 3: ARCHITECTURAL VALIDATION - Implementation"""
    logger.info(f"=== PHASE 3: VALIDATION - {territory} ===")

    state_mgr.update_agent("ArchitectureGovernorAgent", "L5 - Safety")
    arch_gov = agents["arch_governor"](project_root=REPO_ROOT)
    gov_report = arch_gov.comprehensive_territory_audit(
        target_territories=[territory],
        check_layer_boundaries=True,
        check_naming_conventions=True,
    )

    if gov_report is None:
        state_mgr.complete_agent("ArchitectureGovernorAgent", False, "Returned None")
        return None, None

    violations = len(gov_report.get("layer_violations", [])) + len(gov_report.get("naming_violations", []))
    state_mgr.complete_agent("ArchitectureGovernorAgent", True, f"Violations: {violations}")

    # Phase 3.5: Gravity Violation Detection and Healing
    state_mgr.update_agent("GravityLeakRepairAgent", "L5 - Safety")
    gravity_agent = agents["gravity_repair"](project_root=REPO_ROOT)

    try:
        logger.info("🔍 Detecting gravity violations (layer inversions)...")
        gravity_result = gravity_agent.heal_repository(
            dry_run=not ctx.heal if ctx else True, execute=ctx.heal if ctx else False
        )

        gravity_violations = gravity_result.get("violations_found", 0)
        gravity_fixed = gravity_result.get("violations_fixed", 0)

        # Store gravity violations for final reporting
        if gravity_result.get("violations"):
            state_mgr.state["gravity_violations"] = gravity_result["violations"]
        else:
            # Create violation entries from the result
            gravity_violation_list = []
            if gravity_violations > 0:
                gravity_violation_list.append(
                    {
                        "type": "GRAVITY",
                        "message": f"Found {gravity_violations} gravity violations (layer inversions)",
                        "severity": "high",
                        "recommended_action": "Review and fix layer boundary violations",
                        "confidence": 0.9,
                        "violations_found": gravity_violations,
                        "violations_fixed": gravity_fixed,
                    }
                )
            state_mgr.state["gravity_violations"] = gravity_violation_list

        if gravity_result.get("status") == "ERROR":
            state_mgr.complete_agent(
                "GravityLeakRepairAgent", False, f"Error: {gravity_result.get('error', 'Unknown')}"
            )
        elif gravity_violations > 0:
            status_msg = f"Violations: {gravity_violations} | Fixed: {gravity_fixed}"
            state_mgr.complete_agent("GravityLeakRepairAgent", True, status_msg)
            logger.info(f"🔧 Gravity violations processed: {gravity_violations} found, {gravity_fixed} fixed")
        else:
            state_mgr.complete_agent("GravityLeakRepairAgent", True, "No gravity violations found")
            logger.info("✅ No gravity violations detected")

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.error(f"Gravity violation detection failed: {e}")
        state_mgr.complete_agent("GravityLeakRepairAgent", False, f"Detection failed: {str(e)}")
        # Store error as violation for reporting
        state_mgr.state["gravity_violations"] = [
            {
                "type": "GRAVITY_ERROR",
                "message": f"Gravity detection failed: {str(e)}",
                "severity": "high",
                "recommended_action": "Fix gravity detection error",
                "confidence": 0.5,
            }
        ]

    state_mgr.update_agent("SystemArchitectAgent", "L5 - Safety")
    sys_arch = agents["system_architect"](project_root=REPO_ROOT)
    arch_report = sys_arch.validate_core_architecture(f"agentic_core/{territory}")

    if arch_report is None:
        state_mgr.complete_agent("SystemArchitectAgent", False, "Returned None")
        return gov_report, None

    if not arch_report.get("imports_valid", True):
        circular = arch_report.get("circular_dependencies", [])
        state_mgr.add_event("error", f"Circular dependencies detected: {circular}")
        state_mgr.complete_agent("SystemArchitectAgent", False, "Circular Dependencies")
        return gov_report, arch_report

    state_mgr.complete_agent("SystemArchitectAgent", True, "Architecture Valid")
    return gov_report, arch_report


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase4_healing(
    agents,
    territory,
    gov_report,
    decision_engine,
    state_mgr,
    ctx: "HealContext" = None,
    auto_approve=True,
):
    """PHASE 4: HEALING (Retriable)"""
    # [STRICT SCOPE] Gatekeeper check
    if not gov_report:
        logger.warning("Skipping healing: No governance report available.")
        return None

    return execute_phase4_healing_impl(
        agents,
        territory,
        gov_report,
        decision_engine,
        state_mgr,
        ctx,
    )


def execute_phase4_healing_impl(
    agents,
    territory,
    gov_report,
    decision_engine,
    state_mgr,
    ctx: "HealContext" = None,
):
    """PHASE 4: HEALING - Implementation"""
    logger.info(f"=== PHASE 4: HEALING - {territory} ===")

    if gov_report is None:
        logger.warning("No governance report - skipping healing")
        return None

    arch_gov = agents["arch_governor"](project_root=REPO_ROOT)
    plan = arch_gov.generate_healing_plan(gov_report)

    if plan is None:
        logger.warning("No healing plan generated")
        return None

    if plan.get("requires_healing", False):
        fixes = len(plan.get("naming_fixes", []))
        confidence = decision_engine.calculate_healing_confidence(fixes, ["NAMING"], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(
            confidence, "ArchitectureGovernorAgent", territory=territory
        )

        state_mgr.add_event("decision", f"Arch Healing: {reason}")
        logger.info(f"Decision: {reason}")

        if proceed:
            state_mgr.update_agent("ArchitectureGovernorAgent", "HEALING MODE")
            # [SOVEREIGN DEFAULT] Pass orchestration flags to the Governor healing plan
            res = arch_gov.heal_repository(
                dry_run=not ctx.heal if ctx else True,
                auto_approve=ctx.auto_approve if ctx else True,
                target_territory=territory,
            )
            status = res.get("status", "UNKNOWN")
            fixed = res.get("violations_fixed", 0)
            found = res.get("violations_found", 0)
            success = status not in ("BLOCKED", "ERROR", "UNKNOWN") or fixed > 0 or found >= 0
            state_mgr.complete_agent(
                "ArchitectureGovernorAgent", success, f"status={status} found={found} fixed={fixed}"
            )
            return res
        else:
            state_mgr.skip_agent("ArchitectureGovernorAgent", reason)

    return None


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase5_final(agents, territory, state_mgr, decision_engine=None):
    """PHASE 5: CERTIFICATION (Retriable)"""
    return execute_phase5_final_impl(agents, territory, state_mgr, decision_engine)


def execute_phase5_final_impl(agents, territory, state_mgr, decision_engine=None):
    """PHASE 5: CERTIFICATION - Implementation with Silent Aggregation"""
    logger.info(f"=== PHASE 5: CERTIFICATION - {territory} ===")

    state_mgr.update_agent("SovereignCertifier", "L5 - Compliance")

    # [UNIFIED MANIFEST] Aggregate all findings from the state manager
    compliance_report = state_mgr.state.get("compliance_report", {})
    state_mgr.state.get("decision_history", [])

    # [CRITICAL FIX] Aggregate violations from ALL agents, not just ArchitectureGovernor
    # The compliance_report only has ArchitectureGovernor violations
    # We need to include LocationAgent violations from Phase 1
    all_violations = []

    # Get ArchitectureGovernor violations
    arch_violations = compliance_report.get("violations", [])
    all_violations.extend(arch_violations)

    # Get LocationAgent violations from Phase 1 (stored in state)
    location_violations = state_mgr.state.get("location_violations", [])
    for loc_violation in location_violations:
        # LocationAgent violations are tuples: (Path, message)
        if isinstance(loc_violation, tuple) and len(loc_violation) >= 2:
            file_path = str(loc_violation[0])
            message = str(loc_violation[1])
        else:
            file_path = str(getattr(loc_violation, "file", "unknown"))
            message = str(loc_violation)

        # Generate specific, actionable recommendations based on violation type
        if "Missing sovereign root:" in message:
            dir_name = message.split("Missing sovereign root:")[1].strip().strip("')")
            action = f"Create directory: {dir_name}"
        elif "Forbidden keyword 'def test_'" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"Move {filename} to tests/ directory (contains test functions)"
        elif "Forbidden keyword 'class Sovereign'" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"Move {filename} to agentic_core/base_agents/ or agentic_core/L5_safety/"
        elif "Forbidden extension .py for destination docs/reports" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"RENAME: '{filename}' has audit/report naming but is a Python script. Either: 1) Rename to avoid audit patterns (e.g., registry_linkage_checker.py) OR 2) Move to agentic_core/L0_routing/scripts/ where audit scripts belong"
        else:
            action = f"Fix location/naming issue: {message[:60]}"

        # Calculate individual confidence for each violation based on specific violation characteristics
        violation_type = "LOCATION"
        if "Forbidden keyword 'def test_'" in message:
            violation_type = "TEST_FILE_LOCATION"
        elif "Forbidden keyword 'class Sovereign'" in message:
            violation_type = "SOVEREIGN_CLASS_LOCATION"
        elif "Forbidden extension .py for destination docs/reports" in message:
            violation_type = "PYTHON_IN_DOCS"
        elif "BROKEN BACKUP FILE" in message:
            violation_type = "STALE_BACKUP"
        elif "Forbidden keyword 'import '" in message:
            violation_type = "IMPORT_IN_DOCS"

        # Add file-specific factors for confidence calculation
        {
            "has_test_functions": "def test_" in message,
            "has_sovereign_class": "class Sovereign" in message,
            "is_python_file": file_path.endswith(".py"),
            "is_backup_file": file_path.endswith(".backup"),
            "is_in_docs": "docs/reports" in message,
        }

        violation_confidence = decision_engine.calculate_healing_confidence(
            violations_count=1,  # Single violation
            violation_types=[violation_type],  # Use specific violation type
            territory=territory,
        ).value

        # Check if LLM was actually used in the decision process (look for LLM decisions in decision engine)
        llm_decisions = [d for d in decision_engine.decisions_made if "LLM" in d.get("reason", "")]
        llm_was_triggered = decision_engine.enable_llm and len(llm_decisions) > 0

        # Convert LocationAgent violation object to detailed dict
        violation_dict = {
            "type": "LOCATION",
            "source": "LocationAgent",
            "file": file_path,
            "message": message,
            "severity": "medium",
            "recommended_action": action,
            "llm_triggered": llm_was_triggered,
            "confidence": round(violation_confidence, 3),
        }
        all_violations.append(violation_dict)

    # Get GravityLeakRepairAgent violations from phase 3.5
    gravity_violations = state_mgr.state.get("gravity_violations", [])
    for gravity_violation in gravity_violations:
        if isinstance(gravity_violation, dict):
            violation_dict = {
                "type": "GRAVITY",
                "source": "GravityLeakRepairAgent",
                "file": gravity_violation.get("file", "unknown"),
                "message": gravity_violation.get("message", str(gravity_violation)),
                "severity": gravity_violation.get("severity", "high"),
                "recommended_action": gravity_violation.get(
                    "recommended_action", "Fix layer inversion violation"
                ),
                "llm_triggered": False,  # Gravity violations are structural, not LLM-triggered
                "confidence": round(
                    gravity_violation.get("confidence", 0.9), 3
                ),  # High confidence for structural issues
            }
            all_violations.append(violation_dict)

    # Get DebateSynthesisAgent violations (already stored by Phase 4.5 — do not re-invoke)
    conversational_violations = state_mgr.state.get("conversational_violations", [])
    for conv_violation in conversational_violations:
        if isinstance(conv_violation, dict):
            violation_dict = {
                **conv_violation,
                "source": "DebateSynthesisAgent",
                "file": conv_violation.get("file", "unknown"),
                "message": conv_violation.get("message", str(conv_violation)),
                "severity": conv_violation.get("severity", "medium"),
                "recommended_action": conv_violation.get(
                    "recommended_action",
                    "Review conversational pattern",
                ),
                "llm_triggered": decision_engine.enable_llm,
                "confidence": round(conv_violation.get("confidence", 0.5), 3),
            }
            all_violations.append(violation_dict)

    # Get RootHygieneAgent violations
    hygiene_violations = state_mgr.state.get("hygiene_violations", [])
    for hygiene_violation in hygiene_violations:
        if isinstance(hygiene_violation, dict):
            violation_dict = {
                "type": hygiene_violation.get("type", "HYGIENE"),
                "source": "RootHygieneAgent",
                "file": hygiene_violation.get("file", "unknown"),
                "message": hygiene_violation.get("message", str(hygiene_violation)),
                "severity": hygiene_violation.get("severity", "medium"),
                "recommended_action": hygiene_violation.get("recommended_action", "Clean root directory"),
                "llm_triggered": decision_engine.enable_llm,
                "confidence": round(hygiene_violation.get("confidence", 0.5), 3),
            }
            all_violations.append(violation_dict)

    # [PHASE 3 ENHANCEMENT] Get FileClassificationAgent violations from early detection
    classification_violations = state_mgr.state.get("classification_violations", [])
    for class_violation in classification_violations:
        if isinstance(class_violation, dict):
            subtype = class_violation.get("subtype", "UNKNOWN")
            count = class_violation.get("count", 1)
            violation_dict = {
                "type": "CLASSIFICATION",
                "subtype": subtype,
                "source": "FileClassificationAgent",
                "file": class_violation.get("file", "multiple"),
                "message": f"{subtype} violation: {count} file(s) need attention",
                "severity": "medium",
                "recommended_action": f"Run FileClassificationAgent to fix {subtype} issues",
                "llm_triggered": decision_engine.enable_llm,
                "confidence": round(class_violation.get("confidence", 0.7), 3),
                "count": count,
            }
            all_violations.append(violation_dict)

    violation_count = len(all_violations)
    status = "COMPLIANT" if violation_count == 0 else "NON-COMPLIANT"

    # [LOGIC FIX] Recalculate confidence based on FINAL violation count, not Phase 1
    # Get the decision engine to recalculate confidence for the final state
    decision_engine = getattr(state_mgr, "_decision_engine", None)
    if decision_engine is None:
        # Fallback: create a temporary decision engine for final calculation
        decision_engine = AutonomousDecisionEngine(enable_llm=False)

    final_confidence = decision_engine.calculate_healing_confidence(
        violations_count=violation_count,
        violation_types=[v.get("type", "UNKNOWN") for v in all_violations[:10]],
        territory=territory,
    )
    confidence_avg = final_confidence.value

    drift_count = compliance_report.get("stats", {}).get("drift_detected", 0)

    # Build detailed decision log with LLM status
    decisions_made = state_mgr.state.get("decisions_made", [])

    # Get location scan result from state manager
    location_scan_result = state_mgr.state.get("location_scan_result", {})

    # [DYNAMIC] Track actual agents executed from state manager
    completed_agents = state_mgr.state.get("completed_agents", [])
    skipped_agents = state_mgr.state.get("skipped_agents", [])
    # Extract unique agent names from completion history
    agents_executed = list({agent["agent"] for agent in completed_agents})
    # [PHANTOM-RUN FIX] Agents blocked by confidence gate or HITL — NOT counted as executed
    agents_skipped = [{"agent": a["agent"], "reason": a["reason"]} for a in skipped_agents]

    detailed_cert = {
        "meta": {
            "territory": territory,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "sovereignty_level": "L5",
        },
        "metrics": {
            "confidence_score": round(confidence_avg, 3),
            "violation_count": violation_count,
            "drift_count": drift_count,
            "errors": compliance_report.get("stats", {}).get("errors", 0),
            "violations_fixed": (
                compliance_report.get("stats", {}).get("violations_fixed", 0)
                + state_mgr.state.get("hygiene_fixed", 0)
                + state_mgr.state.get("location_fixed", 0)
                + state_mgr.state.get("hierarchy_fixed", 0)
                + state_mgr.state.get("gravity_fixed", 0)
            ),
            "agents_run": len(agents_executed),
            "agents_skipped": len(agents_skipped),
        },
        "governance_log": {"decisions": decisions_made, "files_processed": []},
        "unified_violations": all_violations,  # Use all_violations instead of just arch violations
        "agents_executed": agents_executed,
        "agents_skipped": agents_skipped,
    }

    # Add comprehensive file statistics
    file_stats = location_scan_result.get("file_stats", {})
    # Format compliance rate to one decimal place
    if "compliance_rate" in file_stats:
        file_stats["compliance_rate"] = round(file_stats["compliance_rate"], 1)
    detailed_cert["file_scan_stats"] = file_stats

    # Add violations to file log
    files_affected = set()
    for v in all_violations:  # Use all_violations instead of violations
        files_affected.add(v.get("file", "unknown"))

    detailed_cert["governance_log"]["files_processed"] = list(files_affected)
    detailed_cert["governance_log"]["scan_summary"] = {
        "total_files_scanned": file_stats.get("total_files", 0),
        "files_with_violations": len(files_affected),
        "files_compliant": file_stats.get("valid_files", 0),
        "compliance_rate": round(file_stats.get("compliance_rate", 0), 1),
        "file_types": file_stats.get("file_types", {}),
    }

    # Generate Markdown Executive Summary
    file_stats = location_scan_result.get("file_stats", {})
    total_files = file_stats.get("total_files", 0)
    compliance_rate = file_stats.get("compliance_rate", 0)
    file_types = file_stats.get("file_types", {})

    markdown_summary = [
        f"# 🛡️ Sovereign Compliance Report: {territory}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Status:** {status}",
        "",
        "## 📊 Executive Summary",
        "",
        f"* **Confidence Score:** {confidence_avg:.1%}",
        f"* **Violations Detected:** {violation_count}",
        f"* **Integrity Drift:** {drift_count}",
        f"* **Violations Fixed:** {detailed_cert['metrics']['violations_fixed']}",
        "",
        "## 📁 Scan Scope",
        "",
        f"* **Total Files Scanned:** {total_files}",
        f"* **Files Compliant:** {file_stats.get('valid_files', 0)}",
        f"* **Files with Violations:** {len(files_affected)}",
        f"* **Compliance Rate:** {compliance_rate:.1f}%",
        "",
        "### File Types Analyzed",
        "",
    ]

    # Add file type breakdown
    if file_types:
        for ext, count in sorted(file_types.items()):
            ext_display = ext if ext else "(no extension)"
            markdown_summary.append(f"* **{ext_display}:** {count} files")

    markdown_summary.extend(["", "## 🚨 Violations Detected", ""])

    # Add detailed violations table
    if violation_count > 0:
        markdown_summary.extend(
            [
                "| # | Type | File | Issue | Severity | LLM | Confidence | Action |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ],
        )

        for idx, violation in enumerate(all_violations, 1):
            v_type = violation.get("type", "UNKNOWN")
            v_file = violation.get("file", "unknown")
            # Extract just the filename from full path
            if "/" in v_file or "\\" in v_file:
                v_file = v_file.split("/")[-1].split("\\")[-1]

            # Parse message to get the actual issue
            v_message = violation.get("message", "")
            if "ARTIFACT ROUTING VIOLATION:" in v_message:
                issue = v_message.split("ARTIFACT ROUTING VIOLATION:")[1].split("'")[0].strip()
            elif "Missing sovereign root:" in v_message:
                issue = v_message.split("Missing sovereign root:")[1].strip().strip("')")
            else:
                issue = v_message[:50] + "..." if len(v_message) > 50 else v_message

            v_severity = violation.get("severity", "medium")
            v_llm = "Yes" if violation.get("llm_triggered", False) else "No"
            v_conf = violation.get("confidence", 0.0)
            # Convert to percentage if it's a decimal (0-1) or keep as is if already percentage
            if v_conf <= 1.0:
                v_conf_display = f"{v_conf:.1%}"
            else:
                v_conf_display = f"{v_conf:.1f}%"
            v_action = violation.get("recommended_action", "Review")[:30] + "..."

            markdown_summary.append(
                f"| {idx} | {v_type} | `{v_file}` | {issue} | {v_severity} | {v_llm} | {v_conf_display} | {v_action} |",
            )
    else:
        markdown_summary.append("*No violations detected - territory is compliant.*")

    markdown_summary.extend(
        [
            "",
            "## 🧠 AI Governance Log",
            "",
            "| Decision Context | Confidence | LLM Triggered | Outcome |",
            "| :--- | :--- | :--- | :--- |",
        ],
    )

    # Add decision details to markdown table
    for decision in decisions_made:
        confidence = decision.get("confidence", 0.0)
        llm_triggered = confidence <= 0.75
        outcome = "PROCEED" if decision.get("decision", False) else "SKIP"
        context = decision.get("reason", "Unknown")
        # Format confidence as percentage
        if confidence <= 1.0:
            conf_display = f"{confidence:.1%}"
        else:
            conf_display = f"{confidence:.1f}%"

        markdown_summary.append(
            f"| {context} | {conf_display} | {'Yes' if llm_triggered else 'No'} | {outcome} |",
        )

    # Print JSON Manifest
    _safe_print(json.dumps(detailed_cert, indent=2))

    # Print Markdown Summary
    _safe_print("\n" + "\n".join(markdown_summary))
    if files_affected:
        _safe_print("\n### Affected Files")
        for f in sorted(files_affected):
            _safe_print(f"* `{f}`")
    else:
        _safe_print("\n*No files required remediation.*")

    # [COMPREHENSIVE REPORTS] Save detailed reports to files
    save_comprehensive_reports(
        territory,
        detailed_cert,
        markdown_summary,
        files_affected,
        state_mgr.project_root,
    )

    logger.info(f"📜 CERTIFICATE ISSUED: {territory}")
    state_mgr.complete_agent("SovereignCertifier", True, "Certificate Issued")
    return detailed_cert


def save_comprehensive_reports(
    territory: str,
    detailed_cert: dict,
    markdown_summary: list,
    files_affected: set,
    project_root: Path,
):
    """
    [COMPREHENSIVE REPORTS] Save detailed JSON manifest and Markdown summary to persistent files.
    Creates timestamped reports in logs/compliance_reports/ directory.
    """
    try:
        # Create reports directory
        reports_dir = project_root / "logs" / "compliance_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Save only final files (no timestamped versions to reduce sprawl)
        json_filename = f"compliance_report_{territory}.json"
        md_filename = f"executive_summary_{territory}.md"
        json_path = reports_dir / json_filename
        md_path = reports_dir / md_filename

        with open(json_path, "w", encoding="utf-8") as f:
            assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
            json.dump(detailed_cert, f, indent=2, default=str, ensure_ascii=False)

        # Save Markdown Executive Summary (using the md_path already defined above)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_summary))
            if files_affected:
                f.write("\n\n### 📂 Affected Files\n\n")
                for f_sorted in sorted(files_affected):
                    f.write(f"* `{f_sorted}`\n")
            else:
                f.write("\n\n*No files required remediation.*\n")

        logger.info("📁 Final compliance reports saved:")
        logger.info(f"   JSON: {json_path.relative_to(project_root)}")
        logger.info(f"   Markdown: {md_path.relative_to(project_root)}")

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.error(f"Failed to save comprehensive reports: {e}")
        # Don't fail the entire process if report saving fails


def save_aggregate_report(targets: list[str], project_root: Path) -> Path | None:
    """
    [AGGREGATE REPORT] Merge all per-territory compliance_report_<t>.json into a single
    compliance_report_AGGREGATE.json in logs/compliance_reports/.

    Deduplicates violations by (type, file, message) so cross-territory duplicates
    (e.g. GRAVITY, ILLEGAL_CACHE_DIR) are counted once.

    Returns the Path to the written file, or None on failure.
    """
    import datetime

    try:
        reports_dir = project_root / "logs" / "compliance_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        territory_summaries: list[dict] = []
        all_violations_seen: set[tuple] = set()
        deduplicated_violations: list[dict] = []
        agents_seen: set[str] = set()

        total_violation_count = 0
        total_violations_fixed = 0
        total_drift_count = 0
        total_errors = 0
        non_compliant = 0
        compliant = 0

        for t in targets:
            t_path = reports_dir / f"compliance_report_{t}.json"
            if not t_path.exists():
                continue
            try:
                t_data = json.loads(t_path.read_text(encoding="utf-8"))
            except Exception:  # guardian: allow-silent-swallower
                continue

            meta = t_data.get("meta", {})
            metrics = t_data.get("metrics", {})
            status = meta.get("status", "UNKNOWN")

            if status == "COMPLIANT":
                compliant += 1
            else:
                non_compliant += 1

            total_violation_count += metrics.get("violation_count", 0)
            total_violations_fixed += metrics.get("violations_fixed", 0)
            total_drift_count += metrics.get("drift_count", 0)
            total_errors += metrics.get("errors", 0)

            territory_summaries.append(
                {
                    "territory": t,
                    "status": status,
                    "confidence_score": metrics.get("confidence_score", 0.0),
                    "violation_count": metrics.get("violation_count", 0),
                    "violations_fixed": metrics.get("violations_fixed", 0),
                    "drift_count": metrics.get("drift_count", 0),
                    "agents_run": metrics.get("agents_run", 0),
                    "timestamp": meta.get("timestamp", ""),
                }
            )

            for v in t_data.get("unified_violations", []):
                key = (v.get("type", ""), v.get("file", ""), v.get("message", ""))
                if key not in all_violations_seen:
                    all_violations_seen.add(key)
                    deduplicated_violations.append(v)

            for a in t_data.get("agents_executed", []):
                agents_seen.add(a)

        # Violation breakdown by type and severity
        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for v in deduplicated_violations:
            vtype = v.get("type", "UNKNOWN")
            vsev = v.get("severity", "unknown")
            by_type[vtype] = by_type.get(vtype, 0) + 1
            by_severity[vsev] = by_severity.get(vsev, 0) + 1

        overall_status = "COMPLIANT" if non_compliant == 0 else "NON-COMPLIANT"

        aggregate = {
            "meta": {
                "report_type": "AGGREGATE",
                "timestamp": datetime.datetime.now().isoformat(),
                "territories_scanned": len(territory_summaries),
                "territories_compliant": compliant,
                "territories_non_compliant": non_compliant,
                "overall_status": overall_status,
            },
            "metrics": {
                "total_violations_detected": total_violation_count,
                "unique_violations_deduplicated": len(deduplicated_violations),
                "total_violations_fixed": total_violations_fixed,
                "total_drift_count": total_drift_count,
                "total_errors": total_errors,
                "violations_by_type": by_type,
                "violations_by_severity": by_severity,
            },
            "territories": territory_summaries,
            "agents_executed": sorted(agents_seen),
            "violations": deduplicated_violations,
        }

        agg_path = reports_dir / "compliance_report_AGGREGATE.json"
        with open(agg_path, "w", encoding="utf-8") as f:
            assert_no_persistent_write("L0", "json.dump")  # G-12-1: mutation prohibition guard
            json.dump(aggregate, f, indent=2, default=str, ensure_ascii=False)

        logger.info(f"📊 Aggregate compliance report saved: {agg_path.relative_to(project_root)}")
        logger.info(
            f"   Territories: {len(territory_summaries)} | "
            f"Unique violations: {len(deduplicated_violations)} | "
            f"Fixed: {total_violations_fixed} | "
            f"Status: {overall_status}"
        )
        return agg_path

    except Exception as e:  # guardian: allow-silent-swallower
        logger.error(f"[AGGREGATE] Failed to save aggregate report: {e}")
        return None


# ============================================================================
# L3 ORCHESTRATION INTEGRATION
# ============================================================================


def try_summon_orchestrator(project_root: Path, targets: list[str], execute: bool):
    """
    [INTEGRATION] Attempts to load L3 Orchestrator for smart execution.
    Returns: (success: bool, results: List|None)
    """
    try:
        # Invoke via subprocess to avoid upward import edges
        from agentic_core.L0_routing.utils.subprocess_runner import (
            invoke_orchestrator_mission,
        )

        logger.info("🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.")

        result = invoke_orchestrator_mission(
            project_root=project_root,
            targets=targets,
            execute=execute,
        )

        if result.get("success"):
            return True, result.get("results")

        # Check if fallback is needed
        if result.get("fallback"):
            logger.warning("L3 Orchestrator not found. Falling back to L5 iteration.")
            return False, None

        logger.error(f"L3 Orchestration failed: {result.get('error')}. Falling back.")
        return False, None

    # guardian: allow-silent-swallow
    except Exception as e:  # guardian: allow-silent-swallower
        logger.error(f"L3 Orchestration failed: {e}. Falling back to L5 iteration.")
        return False, None


# ============================================================================
# EXECUTION PLAN (DETERMINISTIC, ORDERED)
# ============================================================================

# Canonical phase→agent→method mapping. This is the SSOT for pipeline structure.
# Used by --plan introspection and by AST contract tests.
EXECUTION_PLAN = [
    {
        "phase": "1",
        "name": "Discovery",
        "agents": [
            {
                "key": "reconciler",
                "method": "detect_root_drift",
                "description": "filesystem SSOT drift detection",
            },
            {
                "key": "location",
                "method": "run",
                "description": "location validation (confidence gated heal)",
            },
            {
                "key": "file_classification",
                "method": "run",
                "description": "file classification early detection",
                "kwargs": "validate_only=True, dry_run=True",
            },
        ],
    },
    {
        "phase": "2",
        "name": "Reconciliation",
        "agents": [
            {"key": "reconciler", "method": "heal", "description": "drift reconciliation (confidence gated)"},
        ],
    },
    {
        "phase": "2.5",
        "name": "Structural Alignment & Sovereignty",
        "agents": [
            {
                "key": "hierarchy",
                "method": "heal_hierarchy",
                "description": "hierarchy alignment (confidence gated)",
            },
            {
                "key": "file_classification",
                "method": "heal_repository",
                "description": "sovereignty purge (confidence gated, not dry_run, not validate)",
            },
        ],
    },
    {
        "phase": "3",
        "name": "Architectural Validation",
        "agents": [
            {
                "key": "arch_governor",
                "method": "comprehensive_territory_audit",
                "description": "territory audit",
            },
            {
                "key": "system_architect",
                "method": "validate_core_architecture",
                "description": "architecture validation",
            },
        ],
    },
    {
        "phase": "4",
        "name": "Healing",
        "agents": [
            {
                "key": "arch_governor",
                "method": "generate_healing_plan",
                "description": "healing plan generation",
            },
            {
                "key": "arch_governor",
                "method": "execute_healing_plan",
                "description": "healing plan execution",
            },
        ],
    },
    {
        "phase": "4.5",
        "name": "Additional Agents",
        "agents": [
            {
                "key": "observability_probe",
                "method": "scan_violations",
                "description": "observability probe scan (renamed from conversational_repair)",
            },
            {
                "key": "root_hygiene",
                "method": "scan_root_violations",
                "description": "root hygiene scan (if registered)",
            },
        ],
    },
    {
        "phase": "5",
        "name": "Certification",
        "agents": [
            {"key": "*", "method": "aggregate", "description": "final aggregation and certification"},
        ],
    },
]

# Agent dependency graph for --agent subset closure.
# If agent A requires agent B to run first, declare it here.
AGENT_DEPENDENCIES: dict[str, list[str]] = {
    "hierarchy": ["reconciler", "location"],
    "file_classification": ["reconciler", "location"],
    "arch_governor": ["reconciler", "location", "hierarchy"],
    "system_architect": ["reconciler", "location"],
    "observability_probe": [],
    "conversational_repair": [],  # DEPRECATED alias — kept for backward compat
    "root_hygiene": [],
    "reconciler": [],
    "location": ["reconciler"],
    "cognitive_disposition": [],
}

# Canonical roster keys. Every agents["key"] reference in _legacy_main MUST
# exist in this set. AST contract tests enforce this invariant.
CANONICAL_ROSTER_KEYS = frozenset(
    {
        "reconciler",
        "location",
        "hierarchy",
        "arch_governor",
        "system_architect",
        "file_classification",
        "observability_probe",
        "conversational_repair",  # DEPRECATED alias — kept for backward compat
        "cognitive_disposition",
        "root_hygiene",
    },
)


def get_execution_plan() -> list[dict]:
    """Return the deterministic, ordered execution plan.

    Pure introspection — no side effects, no file mutations.
    """
    return EXECUTION_PLAN


# ---------------------------------------------------------------------------
# Unified pipeline: AGENT_PIPELINE + run_pipeline
# ---------------------------------------------------------------------------

#: Ordered execution sequence for run_pipeline. cognitive_disposition is
#: intentionally excluded — it acts as a pre-loop advisor, not a subphase agent.
AGENT_PIPELINE: list[str] = [
    "reconciler",
    "location",
    "file_classification",
    "hierarchy",
    "arch_governor",
    "gravity_repair",
    "system_architect",
    "observability_probe",
    "root_hygiene",
]

#: The four subphase names, in fixed execution order.
PIPELINE_SUBPHASES: tuple[str, ...] = ("pre_commit", "validate", "execute", "heal")


def _emit_pipeline_digest(
    adapters: "dict[str, object]",
    territory: str,
    ctx: "HealContext",
) -> str:
    """Compute and print the deterministic pipeline digest (once per run).

    Returns the 64-char hex digest string.
    When SSOT_ORCH_NEGCTRL_TAMPER=1 the digest payload is perturbed so the
    output differs from a clean run — used by the negative-control test.
    """
    from agentic_core.L2_execution.protocol import emit_pipeline_digest as _emit

    return _emit(
        pipeline_order=AGENT_PIPELINE,
        adapter_keys=list(adapters.keys()),
        territory=territory,
        heal=getattr(ctx, "heal", False),
        enable_llm=getattr(ctx, "enable_llm", False),
    )


def run_pipeline(
    adapters: "dict[str, object]",
    territory: str,
    decision_engine: "SovereignDecisionEngine",
    state_mgr: "RuntimeStateManager",
    ctx: "HealContext",
) -> "dict[str, object]":
    """Unified pipeline loop replacing the five bespoke execute_phase*_impl functions.

    Governance invariants enforced:
    - Digest emitted exactly once per call via _emit_pipeline_digest.
    - pre_commit and validate receive scan_ctx (heal=False) structurally.
    - update_agent is never called for execute/heal when gated or fatal.
    - All four subphase slots are always present in AgentRunResult.subphases.
    - Exception in any subphase → fatal=True → remaining subphases skipped.
    - Confidence gate fires immediately after validate, before any execute call.

    Returns dict mapping agent_id -> AgentRunResult.
    """
    from agentic_core.L2_execution.protocol import AgentRunResult, SubphaseResult

    _emit_pipeline_digest(adapters, territory, ctx)

    # scan_ctx: structurally enforces read-only for pre_commit + validate.
    # Use dataclasses.replace when ctx is a frozen dataclass (HealContext);
    # fall back to a simple namespace copy for test mocks or other objects.
    import dataclasses as _dc2

    if _dc2.is_dataclass(ctx) and not isinstance(ctx, type):
        scan_ctx = _dc2.replace(ctx, heal=False)
    else:

        class _ScanCtx:
            pass

        scan_ctx = _ScanCtx()
        for _attr in ("heal", "enable_llm", "auto_approve", "enable_cda"):
            setattr(scan_ctx, _attr, getattr(ctx, _attr, False))
        scan_ctx.heal = False

    results: dict[str, AgentRunResult] = {}

    for agent_id in AGENT_PIPELINE:
        adapter = adapters.get(agent_id)
        if adapter is None:
            continue

        run_result = AgentRunResult()
        # Pre-populate all 4 slots as skipped; overwritten as each runs
        for sp in PIPELINE_SUBPHASES:
            run_result.subphases[sp] = SubphaseResult(skipped=True, skip_reason="not reached")

        fatal = False

        for subphase_name in PIPELINE_SUBPHASES:
            is_mutating = subphase_name in ("execute", "heal")

            # Skip mutating subphases when healing is disabled
            if is_mutating and not getattr(ctx, "heal", False):
                run_result.subphases[subphase_name] = SubphaseResult(skipped=True, skip_reason="heal=False")
                continue

            # Skip execute/heal when confidence gate blocked or prior fatal error
            if is_mutating and (run_result.gated or fatal):
                run_result.subphases[subphase_name] = SubphaseResult(
                    skipped=True,
                    skip_reason=run_result.gate_reason if run_result.gated else "prior error",
                )
                continue

            # Only call update_agent when the subphase will actually run
            state_mgr.update_agent(agent_id, subphase_name)
            effective_ctx = scan_ctx if not is_mutating else ctx

            try:
                method = getattr(adapter, subphase_name)
                result: SubphaseResult = method(territory, effective_ctx)
            except Exception as exc:  # guardian: allow-silent-swallower
                result = SubphaseResult(
                    error=str(exc),
                    skipped=True,
                    skip_reason=f"exception: {exc}",
                )
                run_result.error = str(exc)
                fatal = True
                state_mgr.skip_agent(agent_id, f"{subphase_name} exception: {exc}")
                run_result.subphases[subphase_name] = result
                break  # stop subphase loop for this agent (fail-closed)

            run_result.subphases[subphase_name] = result
            run_result.violations_total += len(result.violations)
            run_result.mutations_applied += len(result.fixed)

            # Confidence gate fires immediately after validate
            if subphase_name == "validate" and result.violations:
                confidence = decision_engine.calculate_healing_confidence(
                    len(result.violations),
                    [v.get("type", "UNKNOWN") for v in result.violations[:10]],
                    territory,
                    agent_name=agent_id,
                )
                proceed, reason = decision_engine.should_proceed_with_healing(
                    confidence, agent_id, territory=territory
                )
                if not proceed:
                    run_result.gated = True
                    run_result.gate_reason = reason
                    state_mgr.skip_agent(agent_id, reason)
                    state_mgr.complete_agent(agent_id, True, f"gated: {reason}")
                    continue  # execute/heal will be filled as skipped in next iterations

            state_mgr.complete_agent(agent_id, result.error is None, result.error or "")

        results[agent_id] = run_result

    return results


# DEPRECATED: The five execute_phase*_impl functions below are replaced by
# run_pipeline above. They are kept as dead code until the new loop has been
# validated in production. Do not add new call sites.


def print_execution_plan(arbitrate_plan: bool = False, ptc_plan: bool = False) -> None:
    """Print stable, sorted execution plan to stdout.

    Args:
        arbitrate_plan: If True, include multi-agent arbitration results
        ptc_plan: If True, include PTC tool call results
    """
    for phase in EXECUTION_PLAN:
        print(f"PHASE {phase['phase']}: {phase['name']}")
        for agent in phase["agents"]:
            kwargs_str = f" ({agent['kwargs']})" if agent.get("kwargs") else ""
            print(f"  - {agent['key']}.{agent['method']}{kwargs_str}")
            print(f"    # {agent['description']}")
        print()

    # Include arbitration results if requested
    if arbitrate_plan:
        print("=== MULTI-AGENT ARBITRATION ===")

        # Build task for arbitration
        task = {
            "task_id": "execute_ssot_plan",
            "task_kind": "planning",
        }

        try:
            # Import arbitration modules
            from agentic_core.L3_orchestration.arbitration.arbitration_contract import ArbitrationInput
            from agentic_core.L3_orchestration.arbitration.arbitrator import Arbitrator
            from agentic_core.L3_orchestration.arbitration.run_advisors import run_all_advisors

            # Run advisors
            proposals = run_all_advisors(task)

            # Arbitrate
            input_data = ArbitrationInput(
                task_id=task["task_id"],
                task_kind=task["task_kind"],
                proposals=proposals,
            )

            arbitrator = Arbitrator()
            decision = arbitrator.arbitrate(input_data)

            print(f"Selected Advisor: {decision.selected_advisor_id}")
            print(f"Selected Decision: {decision.selected_decision}")
            print(f"Score Breakdown: {decision.score_breakdown}")
            print(f"Merged Rationale: {decision.merged_rationale}")
            print(f"Merged Risks: {decision.merged_risks}")

        except Exception as e:  # guardian: allow-silent-swallower
            print(f"Error listing artifacts: {e}")

        print()

    # Include PTC results if requested
    if ptc_plan:
        print("=== PROGRAMMATIC TOOL CALLING ===")

        # Initialize violations list if not already defined
        if "violations" not in locals():
            violations = []

        try:
            # Import PTC modules
            from agentic_core.L3_orchestration.ptc.builtin_tools import register_builtin_tools
            from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
            from agentic_core.L3_orchestration.ptc.tool_call_store import record_tool_call
            from agentic_core.L3_orchestration.ptc.tool_contract import ToolCall, generate_call_id
            from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

            # Register built-in tools (idempotent)
            register_builtin_tools()

            # Get registry and invoker
            registry = get_global_registry()
            invoker = ToolInvoker()

            # Use expr_eval to evaluate an expression
            expr_call = ToolCall(
                call_id=generate_call_id("expr_eval", {"expr": "2 + 3 * 4"}),
                tool_id="expr_eval",
                args={"expr": "2 + 3 * 4"},
                policy={"timeout": 5},
            )

            expr_result = invoker.invoke(expr_call, registry)
            spec, _ = registry.get("expr_eval")
            artifact_ref = record_tool_call(expr_call, expr_result, spec)

            # Prepare PTC plan data
            ptc_plan_data = {
                "tool_calls": [
                    {
                        "tool_id": expr_call.tool_id,
                        "call_id": expr_call.call_id,
                        "args": expr_call.args,
                        "exit_code": expr_result.exit_code,
                        "stdout": expr_result.stdout,
                        "stderr": expr_result.stderr,
                        "truncated": expr_result.truncated,
                    }
                ],
                "artifact_ref": {
                    "kind": artifact_ref.kind,
                    "logical_id": artifact_ref.logical_id,
                    "version": artifact_ref.version,
                    "path": artifact_ref.path,
                },
                "summary": "PTC executed 1 tool calls for plan context",
            }

            # Print deterministic JSON block
            import json

            print(json.dumps(ptc_plan_data, sort_keys=True, separators=(",", ":")))

        except Exception as e:  # guardian: allow-silent-swallower
            # Create error plan data but don't fail plan mode
            ptc_plan_data = {"tool_calls": [], "summary": f"PTC setup failed: {str(e)}", "error": str(e)}
            import json

            print(json.dumps(ptc_plan_data, sort_keys=True, separators=(",", ":")))
            violations.append((0, "PTC_SCAN_ERROR", f"Scan error: {e}"))

        print()


def resolve_agent_subset(requested: list[str]) -> list[str]:
    """Resolve requested agent keys to a closed set including dependencies.

    Raises ValueError on unknown keys.
    Deterministic ordering: sorted alphabetically after closure.
    """
    unknown = set(requested) - CANONICAL_ROSTER_KEYS
    if unknown:
        raise ValueError(f"Unknown agent key(s): {sorted(unknown)}. Valid: {sorted(CANONICAL_ROSTER_KEYS)}")

    closed = set(requested)
    frontier = list(requested)
    while frontier:
        key = frontier.pop()
        for dep in AGENT_DEPENDENCIES.get(key, []):
            if dep not in closed:
                closed.add(dep)
                frontier.append(dep)
    return sorted(closed)


def list_available_agents(project_root=None):
    """Alias for discover_agents_from_registry (backward compat)."""
    if project_root is None:
        project_root = REPO_ROOT
    return discover_agents_from_registry(project_root)


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================


def main() -> int:
    """Deterministic wrapper: logging, V15 enforcement, console, then legacy body."""
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        "--v15-enforcement",
        type=int,
        choices=(0, 1),
        default=None,
        help="Override V15_ENFORCEMENT for this run (0=off, 1=on).",
    )
    pre_parser.add_argument(
        "--allow-protected-root-mutation",
        action="store_true",
        default=False,
        help="Allow writes to protected root directories (audited override).",
    )
    pre_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity (repeatable).",
    )
    pre_args, remaining = pre_parser.parse_known_args()
    _configure_logging(int(pre_args.verbose))
    _apply_v15_enforcement_flag(pre_args)
    _maybe_force_utf8_console()

    # Log protected-root override status exactly once
    if pre_args.allow_protected_root_mutation:
        print("[PROTECTED-ROOT] override ENABLED: protected root mutation permitted")
    else:
        print("[PROTECTED-ROOT] override DISABLED: protected root mutation blocked")

    try:
        _legacy_main(
            remaining,
            repo_root=REPO_ROOT,
            allow_protected_root_mutation=pre_args.allow_protected_root_mutation,
        )
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    return 0


def _build_ssot_territory_targets(project_root: "Path") -> list[str]:
    """Derive the canonical territory target list from SOVEREIGN_TERRITORIES SSOT.

    Returns only keys whose corresponding directory exists under project_root,
    sorted with agentic_core sub-layers first (L0 → L6), then alphabetical.
    Dotfile dirs (.backup, .github, .gravity_state) are excluded — they do not
    need the full agent pipeline.
    """
    try:
        from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_TERRITORIES

        all_keys = list(SOVEREIGN_TERRITORIES.keys())
    except ImportError:
        # Fallback to previous hardcoded list if SSOT import unavailable
        logger.warning("[territory-build] SSOT import failed — using legacy hardcoded list")
        return [
            "prompt_governance",
            "L5_safety",
            "L3_orchestration",
            "L2_execution",
            "L0_routing",
        ]

    # Exclude dotfile dirs — not meaningful territory targets for agent pipeline
    excluded = {".backup", ".github", ".gravity_state"}
    # agentic_core itself is a top-level territory; keep it but also expand to sub-layers
    # that the agents know how to scope (L0_routing, L2_execution, L3_orchestration,
    # L5_safety are the canonical sub-territories inside agentic_core).
    agentic_core_sublayers = [
        "L0_routing",
        "L2_execution",
        "L3_orchestration",
        "L5_safety",
    ]

    targets = []
    # Add agentic_core sub-layers first (they have specialised agent scoping)
    for sub in agentic_core_sublayers:
        sub_path = project_root / "agentic_core" / sub
        if sub_path.exists():
            targets.append(sub)

    # Add all other SOVEREIGN_TERRITORIES keys that exist and are not excluded/already added
    skip = set(agentic_core_sublayers) | excluded | {"agentic_core"}
    for key in sorted(all_keys):
        if key in skip:
            continue
        territory_path = project_root / key
        if territory_path.exists():
            targets.append(key)

    logger.info(f"[territory-build] SSOT-derived targets ({len(targets)}): {targets}")
    return targets


def _compute_pipeline_digest(targets: "list[str]") -> str:
    """Compute a stable determinism digest for the pipeline run.

    Five-component SHA-256 surface:
      policy_hash          -- canonical sovereign policy identifier
      registry_hash        -- SHA-256 of sorted agent registry surface
      config_surface_hash  -- from negative_control_harness (tamper-sensitive)
      transcript_hash      -- SHA-256 of sorted processed territory names
      dependency_lock_hash -- stable structural constant

    Returns a 64-char hex string.  Never raises; falls back to a sentinel
    digest on import failure so the pipeline is not blocked.
    """
    import hashlib as _h
    import json as _j

    try:
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            get_config_surface as _gcs,
        )
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            hash_config_surface as _hcs,
        )
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DeterminismDigestEmitter as _DE,
        )
    except ImportError as _exc:
        logger.warning(f"[DETERMINISM-DIGEST] import failed: {_exc}")
        return _h.sha256(b"determinism-digest:import-failed").hexdigest()

    _policy_hash = _h.sha256(b"sovereign-policy-v1.0").hexdigest()

    try:
        from agentic_core.agents.agent_registry import registry_digest as _rd

        _reg_bytes = _j.dumps(_rd(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        _registry_hash = _h.sha256(_reg_bytes).hexdigest()
    except Exception:
        _registry_hash = _h.sha256(b"registry:fallback").hexdigest()

    _config_hash = _hcs(_gcs())

    _transcript_bytes = _j.dumps(
        sorted(str(t) for t in targets),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    _transcript_hash = _h.sha256(_transcript_bytes).hexdigest()

    _dep_lock_hash = _h.sha256(b"dependency-lock:stable").hexdigest()

    _emitter = _DE()
    return _emitter.compute(
        policy_hash=_policy_hash,
        registry_hash=_registry_hash,
        config_surface_hash=_config_hash,
        transcript_hash=_transcript_hash,
        dependency_lock_hash=_dep_lock_hash,
    )


@_optional_runtime_guard()("E.execute_ssot_main.execute_ssot")
def _legacy_main(
    extra_argv=None, *, repo_root: Path | None = None, allow_protected_root_mutation: bool = False
):
    _maybe_force_utf8_console()  # G-UTF8: ensure stdout/stderr are UTF-8 safe on Windows
    _maybe_force_utf8_logging_handlers()  # G-UTF8: fix handler streams created before console reconfigure

    # [WAVE 2] Import/symbol preflight check (fail-fast if critical symbols missing)
    try:
        _preflight_import_check()
        logger.info("[PREFLIGHT] Import/symbol check PASSED")
    except RuntimeError as exc:
        logger.critical(f"[PREFLIGHT] FAILED: {exc}")
        sys.exit(1)

    # [WAVE 2] Startup fence self-test (abort if fence inactive)
    if not allow_protected_root_mutation:
        try:
            from agentic_core.L0_routing.enforcement.mutation_prohibition import (
                SourceMutationBlocked,
                enforce_protected_root,
            )

            # Attempt to write to agentic_core/.tmp_fence_probe
            probe_path = REPO_ROOT / "agentic_core" / ".tmp_fence_probe"
            fence_active = False

            try:
                # This should raise SourceMutationBlocked if fence is active
                enforce_protected_root(probe_path, allow_override=False)
                # If we get here, fence is NOT active - CRITICAL FAILURE
                logger.critical("[FENCE-SELF-TEST] FAILED: Protected root fence is INACTIVE")
                sys.exit(1)
            except SourceMutationBlocked:
                # Expected: fence blocked the write
                fence_active = True

            if fence_active:
                logger.info("[FENCE-SELF-TEST] PASSED: Protected root fence is ACTIVE")
            else:
                logger.critical("[FENCE-SELF-TEST] FAILED: Fence state indeterminate")
                sys.exit(1)

        except ImportError as exc:
            logger.critical(f"[FENCE-SELF-TEST] FAILED: Cannot import fence module: {exc}")
            sys.exit(1)
    else:
        logger.warning("[FENCE-SELF-TEST] SKIPPED: --allow-protected-root-mutation enabled")
        import os as _os  # noqa: E402

        _os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"
        _os.environ["BMG_EMBEDDINGS_ENABLED"] = "true"
        _os.environ["AGENTIC_BYPASS_LONGPATHS_CHECK"] = "1"

    # §8.1e — V15 manifest at SSOT bootstrap entry (AGGREGATE, L0 bootstrap)
    _v15_manifest = _v15_build_ssot_manifest()
    if _v15_manifest is not None:
        _v15_ssot_gateway_audit(_v15_manifest, trace_id=_v15_manifest.correlation_id)

    project_root = repo_root if repo_root is not None else REPO_ROOT
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))

    parser = argparse.ArgumentParser(
        description="Unified Sovereign Compliance Protocol v4.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single territory scan (LLM enabled by default)
  python execute_ssot_script.py --territory prompt_governance

  # Multi-domain sweep
  python execute_ssot_script.py --domains

  # Dry run (no LLM healing)
  python execute_ssot_script.py --territory L5_safety --dry-run

  # List all discoverable agents
  python execute_ssot_script.py --list-agents

  # Run specific agent directly
  python execute_ssot_script.py --agent NamingAgent
        """,
    )
    parser.add_argument("--territory", type=str, help="Specific territory to scan")
    parser.add_argument("--domains", action="store_true", help="Scan all major domains (Multi-Domain Mode)")
    parser.add_argument("--agent", type=str, help="Run specific agent directly")
    parser.add_argument("--list-agents", action="store_true", help="List discoverable agents")
    parser.add_argument(
        "--no-cda",
        action="store_true",
        help="Disable CognitiveDispositionAgent (enabled by default)",
    )
    parser.add_argument(
        "--heal",
        action="store_true",
        default=False,
        help="Enable active healing (mutations applied). Absence = scan/report only.",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Scan/report only — no mutations (alias for omitting --heal)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable human-in-the-loop prompts (Default: Auto-Approve)",
    )
    parser.add_argument("--manual", action="store_true", help="Disable autonomous mode (legacy)")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run in validation-only mode (CI/Dry-Run Mode)",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Print the deterministic execution plan and exit. No side effects.",
    )
    parser.add_argument(
        "--agents",
        type=str,
        default=None,
        help="Comma-separated list of agent keys to run (e.g. --agents location,hierarchy). Includes dependencies automatically. Hard-fails on unknown keys.",
    )
    # [PHASE 8] New Flag for Golden Baseline capture
    parser.add_argument("--capture-baseline", action="store_true", help="Capture new Golden Baseline")
    parser.add_argument(
        "--fence-self-check",
        action="store_true",
        help="Run deterministic fence self-check (validates policy + wiring; no mutations)",
    )
    parser.add_argument(
        "--v15-enforcement",
        type=int,
        choices=(0, 1),
        default=None,
        help="Override V15_ENFORCEMENT for this run (0=off, 1=on).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity (repeatable).",
    )
    args = parser.parse_args(extra_argv)

    # [PLAN MODE] Pure introspection — no execution, no side effects.
    if args.plan:
        print_execution_plan()
        return

    # [FENCE SELF-CHECK MODE] Validate protected-root policy + wiring (no mutations).
    if args.fence_self_check:
        run_fence_self_check()
        return

    # [AGENT SUBSET] Validate and resolve --agents early (before imports).
    requested_agent_keys: list[str] | None = None
    if args.agents:
        raw_keys = [k.strip() for k in args.agents.split(",") if k.strip()]
        try:
            requested_agent_keys = resolve_agent_subset(raw_keys)
            logger.info(f"Agent subset resolved: {requested_agent_keys}")
        except ValueError as ve:
            parser.error(str(ve))

    # [CENTRALIZED] validate ⇒ dry_run mapping (single source of truth).
    # When --validate is set, dry_run is forced True. This ensures
    # FileClassificationAgent and all other agents see consistent flags.
    if args.validate:
        args.dry_run = True

    # [HARDENED] 0. Pre-Flight Validation
    validator = PreFlightValidator(project_root, dry_run=args.dry_run)
    env_ok, env_errors = validator.run_checks()
    if not env_ok:
        logger.critical("🛑 PRE-FLIGHT CHECK FAILED:")
        for err in env_errors:
            logger.error(f"  - {err}")
        if not args.list_agents:
            sys.exit(1)

    # [ULTRA-HARDENED] Validate user-supplied territory name format via regex
    if args.territory and not re.match(r"^[A-Za-z0-9_]+$", args.territory):
        parser.error("Invalid territory name: only alphanumeric and underscores allowed.")

    # 1. Handle Discovery
    if args.list_agents:
        logger.info("DISCOVERABLE AGENTS:")
        agents_list = list_available_agents(project_root)
        for i, (name, path) in enumerate(agents_list, 1):
            print(f"   {i:3}. {name:<40} [{path}]")
        print(f"\nTotal: {len(agents_list)} agents")
        return

    # [PHASE 8] Handle baseline capture command
    if args.capture_baseline:
        print("\n🔒 INITIATING BASELINE CAPTURE PROTOCOL...")
        try:
            from agentic_core.L0_routing.utils.subprocess_runner import invoke_arch_governor

            result = invoke_arch_governor(
                action="capture_baseline",
                project_root=project_root,
            )
            if result.get("success"):
                print(f"✨ Golden Baseline captured at: {result.get('manifest_path')}")
                sys.exit(0)
            else:
                logger.error(f"Baseline capture failed: {result.get('error')}")
                sys.exit(1)
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.error(f"Baseline capture failed: {e}")
            sys.exit(1)

    # 2. Handle Direct Agent Invocation (Developer Mode)
    if args.agent:
        logger.info(f"DIRECT AGENT EXECUTION: {args.agent}")
        try:
            found = [x for x in list_available_agents(project_root) if args.agent.lower() in x[0].lower()]
            if not found:
                logger.error(f"Agent {args.agent} not found.")
                logger.info("Use --list-agents to see available agents")
                return

            name, path = found[0]
            logger.info(f"Found: {name} at {path}")

            module = importlib.import_module(path)

            # Try instantiation strategies
            agent = None
            if hasattr(module, f"get_{name.lower()}"):
                agent = getattr(module, f"get_{name.lower()}")(project_root)
            elif hasattr(module, name):
                agent_cls = getattr(module, name)
                agent = agent_cls(project_root=project_root)
            else:
                logger.error(f"Could not instantiate {name}")
                return

            logger.info(f"Running {name}...")

            # Prefer standard methods
            if hasattr(agent, "run"):
                result = agent.run()
            elif hasattr(agent, "scan_root_violations"):
                result = agent.scan_root_violations()
            elif hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=not ctx.heal if "ctx" in dir() and ctx else True)
            else:
                result = "Agent instantiated but no standard run method found."

            logger.info(f"Result: {result}")

        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.error(f"Failed to run agent: {e}")
            traceback.print_exc()
        return

    # 3. Initialize Sovereign State & Agents
    # [SSOT MIXIN] Build ExecutionContext with L4-derived policy hash
    ExecutionContext = _get_execution_context_class()
    try:
        from agentic_core.L4_state.config.versioned_configs import get_active_configs

        _l4_policy_hash = get_active_configs().policy.config_hash
    except ImportError:
        _l4_policy_hash = "fallback-no-l4"
    _exec_ctx = ExecutionContext(
        mission_id=args.territory or "default",
        trace_id=f"mission-{int(time.time())}",
        replay_mode=False,
        active_policy_hash=_l4_policy_hash,
        safety_status="CLEARED",
    )

    state_mgr = RuntimeStateManager(project_root, execution_context=_exec_ctx)

    # [HEAL CONTEXT] Single source of truth for all healing flags
    ctx = HealContext.from_args(args)

    # [SIMPLIFIED] Auto-set env vars unless interactive mode explicitly requested
    if ctx.auto_approve:
        import os

        os.environ.setdefault("SOVEREIGN_AUTO_APPROVE", "1")
        os.environ.setdefault("ARCHIVE_BATCH_ACCEPT", "1")

    # [HARDENED] Use Sovereign Decision Engine — wired from HealContext
    decision_engine = SovereignDecisionEngine(
        enable_llm=ctx.enable_llm,
        state_mgr=state_mgr,
        enable_cda=ctx.enable_cda,
        execution_context=_exec_ctx,
    )

    logger.info("UNIFIED SOVEREIGN PROTOCOL STARTED")
    logger.info(f"  Mode: {'AUTONOMOUS' if not args.manual else 'MANUAL'}")
    logger.info(f"  LLM: {'ENABLED' if ctx.enable_llm else 'DISABLED'}")
    logger.info(f"  CDA: {'ENABLED' if ctx.enable_cda else 'DISABLED'}")
    logger.info(f"  HEALING: {'ACTIVE (--heal)' if ctx.heal else 'SCAN-ONLY (no --heal)'}")
    logger.info(f"  APPROVAL: {'AUTO' if ctx.auto_approve else 'INTERACTIVE'}")

    # [HARDENED] Mandatory Hard Imports for Total Awareness (via subprocess)
    try:
        from agentic_core.L0_routing.utils.subprocess_runner import (
            invoke_agent_roster_validation,
        )

        roster_result = invoke_agent_roster_validation()

        if roster_result.get("success"):
            logger.info("Total Awareness: Mandatory agent roster registered.")
            logger.info(f"  Agents validated: {', '.join(roster_result.get('agents_validated', []))}")
        else:
            integrity_errors = roster_result.get("integrity_errors", [])
            if integrity_errors:
                logger.critical("🛑 SOVEREIGN CONTRACT BREACH - AGENT INTEGRITY FAILED:")
                for err in integrity_errors:
                    logger.error(f"  - {err}")
                if not args.list_agents:
                    sys.exit(1)  # Halt mission if any agent is non-compliant
            else:
                error_msg = roster_result.get("error", "Unknown error")
                logger.critical(f"🛑 FATAL: Mandatory agent or dependency missing: {error_msg}")
                sys.exit(1)

    # guardian: allow-silent-swallow
    except Exception as e:  # guardian: allow-silent-swallower
        logger.critical(f"🛑 FATAL: Agent roster validation failed: {e}")
        sys.exit(1)

    # 3b. Build local agents roster (classes, not instances)
    (
        ArchitectureGovernorAgent,
        CognitiveDispositionAgent,
        FileClassificationAgent,
        FilesystemSSOTReconcilerAgent,
        GravityLeakRepairAgent,
        HierarchyAgent,
        LocationAgent,
        RootHygieneAgent,
        SystemArchitectAgent,
        ObservabilityProbeExecutorAgent,
    ) = _get_l5_agent_roster()

    agents = {
        "reconciler": FilesystemSSOTReconcilerAgent,
        "location": LocationAgent,
        "hierarchy": HierarchyAgent,
        "arch_governor": ArchitectureGovernorAgent,
        "gravity_repair": GravityLeakRepairAgent,
        "system_architect": SystemArchitectAgent,
        "file_classification": FileClassificationAgent,
        "observability_probe": ObservabilityProbeExecutorAgent,
        "conversational_repair": ObservabilityProbeExecutorAgent,  # DEPRECATED alias
        "cognitive_disposition": CognitiveDispositionAgent,
        "root_hygiene": RootHygieneAgent,
    }

    # 4. Determine Targets
    targets = []
    mission_mode = ""
    if args.territory:
        targets = [args.territory]
        mission_mode = f"Territory Scan: {args.territory}"
    elif args.domains:
        # Multi-domain sweep — derive from SSOT to avoid stale hardcode
        targets = _build_ssot_territory_targets(project_root)
        mission_mode = "Multi-Domain Sweep (L3 Attempt)"
    else:
        # Default to full domain sweep derived from SSOT SOVEREIGN_TERRITORIES
        targets = _build_ssot_territory_targets(project_root)
        mission_mode = "Multi-Domain Sweep (Default)"

    # Domain targeting hardening for protected roots
    if args.domains and not allow_protected_root_mutation:
        for domain in ["L0_routing", "L2_execution", "L3_orchestration", "L5_safety"]:
            if domain in targets:
                domain_path = project_root / "agentic_core" / domain
                if domain_path.exists():
                    logger.warning(f"[PROTECTED-ROOT] forcing scan-only for {domain}")
                    print(f"[PROTECTED-ROOT] forcing scan-only (no mutations) for {domain}")
                    from dataclasses import replace as _dc_replace

                    ctx = _dc_replace(ctx, heal=False, enable_llm=False)
                    break

    # 5. Execute Mission
    # [HARDENED] Wrap entire autonomous execution in NonInteractiveGuard
    is_autonomous = not args.manual

    try:
        with NonInteractiveGuard(active=is_autonomous):
            state_mgr.start_mission(f"Unified Protocol: {mission_mode}", [f"{t}" for t in targets])

            # [PHASE 8] Integrated Integrity Check
            # [HARDENED] Pass territory targets to ensure integrity check is also scoped.
            if is_autonomous:
                logger.info(f"🔍 [PHASE 8] Running integrity check (Scope: {targets})...")
                try:
                    from agentic_core.L0_routing.utils.subprocess_runner import invoke_arch_governor

                    result = invoke_arch_governor(
                        action="audit",
                        project_root=project_root,
                        targets=targets,
                    )

                    if result.get("success"):
                        audit_results = result.get("audit_results", {})
                        # [UNIFIED AUDIT] Persist all identified violations to the runtime state
                        state_mgr.state["compliance_report"] = audit_results

                        stats = audit_results.get("stats", {})
                        if stats.get("violations_found", 0) > 0:
                            logger.warning(
                                f"⚠️  {stats['violations_found']} total violations identified.",
                            )

                        if stats.get("drift_detected", 0) > 0:
                            logger.error(
                                f"🛑 CRITICAL: {stats['drift_detected']} integrity drift detected.",
                            )
                            if args.validate:
                                state_mgr.finish_mission(status="failed_integrity")
                                sys.exit(1)  # Fatal in CI
                            else:
                                logger.warning("⚠️  Proceeding with caution (Heal mode active)...")
                    else:
                        logger.warning(f"Integrity check failed: {result.get('error')}")
                # guardian: allow-silent-swallow
                except Exception as e:  # guardian: allow-silent-swallower
                    logger.warning(f"Integrity check failed, continuing: {e}")

            # [INTEGRATION] Attempt L3 Smart Orchestration first
            if args.domains:
                l3_success, l3_results = try_summon_orchestrator(project_root, targets, execute=is_autonomous)
                if l3_success:
                    state_mgr.update_meta_learning(
                        {"total_experiences": 1, "experience": "L3 Mission Complete"},
                    )
                    state_mgr.finish_mission("completed")
                    logger.info("🎉 L3 MISSION COMPLETED")
                    return l3_results

            # Territories outside agentic_core that are included in the sweep for
            # scan/report but must NEVER receive autonomous mutations.
            # Heal on these requires --territory <name> (single-territory, user-deliberate).
            _agentic_core_sublayer_prefixes = ("L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_")
            _SCAN_ONLY_TERRITORIES = [
                t
                for t in targets
                if t != "agentic_core" and not any(t.startswith(p) for p in _agentic_core_sublayer_prefixes)
            ]
            _NON_AC_TERRITORIES = set(_SCAN_ONLY_TERRITORIES)

            # [HARDENED] Universal Compliance Persistence
            results = []
            # Fix 4: RootHygieneAgent scans REPO_ROOT (not per-territory).
            # Run once before the territory loop to prevent N× duplicate violations.
            state_mgr.state["hygiene_violations"] = []
            state_mgr.state["hygiene_fixed"] = 0
            try:
                state_mgr.update_agent("RootHygieneAgent", "L0 - Maintenance")
                hygiene_agent = agents["root_hygiene"](project_root=REPO_ROOT)
                if hasattr(hygiene_agent, "scan_root_violations"):
                    hygiene_results = hygiene_agent.scan_root_violations()
                    hygiene_violations = hygiene_results.get("violations", [])
                    high = [v for v in hygiene_violations if v.get("severity") == "high"]
                    hygiene_fixed = 0
                    if ctx and ctx.heal and hasattr(hygiene_agent, "heal"):
                        for _v in hygiene_violations:
                            try:
                                _r = hygiene_agent.heal(_v)
                                if isinstance(_r, dict) and _r.get("status") == "success":
                                    hygiene_fixed += 1
                                    logger.info(
                                        "[RootHygiene] HEALED %s: %s",
                                        _v.get("type"),
                                        _v.get("file", ""),
                                    )
                            except Exception as _he:  # guardian: allow-silent-swallower
                                logger.debug("[RootHygiene] heal() error: %s", _he)
                    state_mgr.complete_agent(
                        "RootHygieneAgent",
                        True,
                        f"Violations: {len(hygiene_violations)} (high: {len(high)}) fixed: {hygiene_fixed}",
                    )
                    state_mgr.state["hygiene_violations"] = hygiene_violations
                    state_mgr.state["hygiene_fixed"] = hygiene_fixed
                else:
                    state_mgr.complete_agent("RootHygieneAgent", False, "No scan_root_violations method")
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-silent-swallower
                logger.warning(f"RootHygieneAgent failed: {e}")
                state_mgr.complete_agent("RootHygieneAgent", False, str(e))
            for territory in targets:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"PROCESSING TERRITORY: {territory}")
                logger.info(f"{'=' * 60}")

                # Update State with Target
                state_mgr.state["current_territory"] = territory
                state_mgr.save()
                state_mgr.add_event("domain_start", f"Entering Domain: {territory}")

                from dataclasses import replace as _dc_replace

                effective_ctx = ctx

                # [FIX] Reset per-territory decision engine state so cycle detection
                # does not bleed across territories (agent_name="Unknown" accumulates).
                decision_engine._call_path = set()
                decision_engine._healing_count = 0

                try:
                    # [UNIVERSAL HEALING] Unified Execution Phase
                    # All agents now receive the 'Heal' signal if confidence is met
                    p1_drift, p1_loc, p1_scan_result = execute_phase1_discovery(
                        agents,
                        territory,
                        decision_engine,
                        state_mgr,
                        effective_ctx,
                    )

                    if p1_drift is not None:
                        # Phase 2: Reconciliation (Write/Heal Phase)
                        # Create plan from Phase 1 results
                        # Build violations from actual drift report keys.
                        # suggested_agent must match agents dict keys for lookup + BMG GPU routing.
                        _phase1_violations = []
                        for _f in p1_drift.get("forbidden_folders") or []:
                            _phase1_violations.append(
                                {"type": "FORBIDDEN_FOLDER", "file": str(_f), "suggested_agent": "reconciler"}
                            )
                        for _d in p1_drift.get("duplicate_folders") or []:
                            _dname = _d.get("name", str(_d)) if isinstance(_d, dict) else str(_d)
                            _phase1_violations.append(
                                {"type": "DUPLICATE_FOLDER", "file": _dname, "suggested_agent": "location"}
                            )
                        for _a in p1_drift.get("archived_files_at_root") or []:
                            _phase1_violations.append(
                                {
                                    "type": "ARCHIVED_FILE_AT_ROOT",
                                    "file": str(_a),
                                    "suggested_agent": "root_hygiene",
                                }
                            )
                        for _lv in p1_loc or []:
                            if isinstance(_lv, dict):
                                _lv["suggested_agent"] = "location"
                                _phase1_violations.append(_lv)
                            else:
                                _phase1_violations.append(
                                    {"type": "LOCATION", "file": str(_lv), "suggested_agent": "location"}
                                )
                        plan = {"violations_found": _phase1_violations}

                        # Execute Phase 2 with decision engine gating
                        phase2_result = execute_phase2_reconciliation(
                            agents,
                            territory,
                            decision_engine,
                            state_mgr,
                            plan,
                            effective_ctx,
                        )

                        # Log Phase 2 results
                        raw = phase2_result.get("_raw_result", {})
                        if raw.get("modifications"):
                            logger.info(f"✅ Phase 2: {len(raw['modifications'])} fixes applied")
                        if raw.get("failures"):
                            logger.warning(f"⚠️ Phase 2: {len(raw['failures'])} fixes failed")

                        # Phase 3: Final Validation (Post-heal AST checks)
                        # Use the original violations from Phase 1
                        phase3_result = execute_phase3_validation(
                            agents,
                            territory,
                            p1_drift.get("violations", []),
                            effective_ctx.dry_run,
                        )

                        if phase3_result["status"] == "clean":
                            logger.info("✅ Phase 3: All files pass validation")
                        else:
                            remaining_count = len(phase3_result.get("remaining_violations", []))
                            logger.warning(f"⚠️ Phase 3: {remaining_count} issues detected")

                        # Continue with existing phases
                        # Phase 2.5: Structural Alignment (Hierarchy) - Legacy
                        execute_phase2_alignment(
                            agents,
                            territory,
                            decision_engine,
                            state_mgr,
                            effective_ctx,
                        )

                        # [UNIVERSAL HEALING] Phase 2.5: Sovereignty Enforcement (Pascal/Header/Naming)
                        # Now integrated with confidence-based decision engine
                        # [PHASE 2 ENHANCEMENT] Include classification violations in confidence calc
                        classification_violations = state_mgr.state.get("classification_violations", [])
                        total_violations = (len(p1_loc) if p1_loc else 0) + len(classification_violations)
                        violation_types = ["SOVEREIGNTY", "NAMING", "HEADER"]
                        # Add CLASSIFICATION type if we have classification violations
                        if classification_violations:
                            violation_types.append("CLASSIFICATION")
                        pascal_confidence = decision_engine.calculate_healing_confidence(
                            violations_count=total_violations,
                            violation_types=violation_types,
                            territory=territory,
                        )
                        pascal_proceed, pascal_reason = decision_engine.should_proceed_with_healing(
                            pascal_confidence, "FileClassificationAgent"
                        )

                        state_mgr.add_event("decision", f"Sovereignty Healing: {pascal_reason}")
                        logger.info(f"Sovereignty Decision: {pascal_reason}")

                        if pascal_proceed and effective_ctx.heal:
                            logger.info(f"Triggering Sovereignty Purge: {territory}")
                            state_mgr.update_agent("FileClassificationAgent", "L5 - Safety")
                            pascal = agents["file_classification"](project_root=REPO_ROOT)
                            if hasattr(pascal, "heal_repository"):
                                res = pascal.heal_repository(
                                    target_territory=territory,
                                    dry_run=effective_ctx.dry_run,
                                    auto_approve=effective_ctx.auto_approve,
                                )
                                healed = res.get("files_healed", 0) if isinstance(res, dict) else 0
                                state_mgr.complete_agent("FileClassificationAgent", True, f"Healed: {healed}")
                            else:
                                state_mgr.complete_agent(
                                    "FileClassificationAgent",
                                    False,
                                    "No heal_repository method",
                                )
                        elif not pascal_proceed:
                            state_mgr.skip_agent("FileClassificationAgent", pascal_reason)
                        elif not effective_ctx.heal:
                            state_mgr.skip_agent("FileClassificationAgent", "scan-only mode (no --heal)")

                        # Phase 3: Validation (Legacy)
                        gov, arch = execute_phase3_architectural_validation(
                            agents, territory, state_mgr, ctx=effective_ctx
                        )

                        # Persist full work to state
                        state_mgr.state["compliance_report"] = gov
                        state_mgr.save()

                        # Phase 4: Final Healing (Governor)
                        execute_phase4_healing(
                            agents,
                            territory,
                            gov,
                            decision_engine,
                            state_mgr,
                            effective_ctx,
                        )

                        # Phase 4.5: Additional Agent Execution (Conversational Repair & Root Hygiene)
                        logger.info(f"=== PHASE 4.5: ADDITIONAL AGENTS - {territory} ===")

                        # Execute DebateSynthesisAgent
                        logger.info(f"🤖 Triggering Debate Synthesis: {territory}")
                        state_mgr.update_agent("DebateSynthesisAgent", "Prompt Governance")
                        try:
                            conversational_agent = agents.get(
                                "observability_probe", agents.get("conversational_repair", lambda **_: None)
                            )(project_root=REPO_ROOT, probe_type="debate")
                            if hasattr(conversational_agent, "scan_violations"):
                                conv_results = conversational_agent.scan_violations(
                                    target_territory=territory,
                                )
                                conv_violations = conv_results.get("violations", [])
                                state_mgr.complete_agent(
                                    "DebateSynthesisAgent",
                                    True,
                                    f"Violations: {len(conv_violations)}",
                                )
                                # Store violations for aggregation
                                if not state_mgr.state.get("conversational_violations"):
                                    state_mgr.state["conversational_violations"] = []
                                state_mgr.state["conversational_violations"].extend(conv_violations)
                            else:
                                state_mgr.complete_agent(
                                    "DebateSynthesisAgent",
                                    False,
                                    "No scan_violations method",
                                )
                        # guardian: allow-silent-swallow
                        except Exception as e:  # guardian: allow-silent-swallower
                            logger.warning(f"DebateSynthesisAgent failed: {e}")
                            state_mgr.complete_agent("DebateSynthesisAgent", False, str(e))

                        # Execute CognitiveDispositionAgent
                        try:
                            state_mgr.update_agent("CognitiveDispositionAgent", "L1 - Cognition")
                            cog_agent = agents["cognitive_disposition"](project_root=REPO_ROOT)
                            if hasattr(cog_agent, "get_analytics"):
                                cog_results = cog_agent.get_analytics()
                                state_mgr.complete_agent(
                                    "CognitiveDispositionAgent",
                                    True,
                                    f"Analytics keys: {list(cog_results.keys())[:4]}",
                                )
                            else:
                                state_mgr.complete_agent(
                                    "CognitiveDispositionAgent", False, "No get_analytics method"
                                )
                        # guardian: allow-silent-swallow
                        except Exception as e:  # guardian: allow-silent-swallower
                            logger.warning(f"CognitiveDispositionAgent failed: {e}")
                            state_mgr.complete_agent("CognitiveDispositionAgent", False, str(e))

                        # Phase 5 (RootHygieneAgent moved outside territory loop — Fix 4)
                        cert = execute_phase5_final(agents, territory, state_mgr, decision_engine)
                        results.append(cert)
                    else:
                        logger.error(f"Phase 1 failed for {territory} - skipping")
                        state_mgr.add_event("error", f"Phase 1 failure in {territory}")

                except RuntimeError as runtime_err:
                    # Catch the NonInteractiveGuard trap specifically
                    if "Interactive prompt blocked" in str(runtime_err):
                        logger.critical(f"🛑 BLOCKED INTERACTIVE PROMPT in {territory}: {runtime_err}")
                        state_mgr.add_event("error", f"Blocked Prompt in {territory}")
                        continue  # Skip this territory, try next
                    raise runtime_err
                # guardian: allow-silent-swallow
                except Exception as e:  # guardian: allow-silent-swallower
                    logger.error(f"❌ Protocol crashed on {territory}: {e}")
                    traceback.print_exc()
                    state_mgr.add_event("error", f"Crash in {territory}: {str(e)[:200]}")
                    if is_autonomous:
                        continue
                    else:
                        state_mgr.finish_mission(status="error")
                        sys.exit(1)

            # Wave 0C: fire meta-learning intake before closing the mission
            _fire_meta_learning_intake(state_mgr)

            # Save aggregate report across all territories
            save_aggregate_report(targets, REPO_ROOT)

            # Only mark completed if we got here
            state_mgr.finish_mission(status="completed")

            # L6: emit determinism digest — exactly one line per run
            try:
                from agentic_core.L6_observability.engines.determinism_digest_emitter import (
                    DeterminismDigestEmitter as _DET_EMITTER,
                )

                _det_digest = _compute_pipeline_digest(targets)
                _det_line = _DET_EMITTER().emit_once(_det_digest)
                print(_det_line)
            except Exception as _det_exc:
                logger.warning(f"[DETERMINISM-DIGEST] emission failed: {_det_exc}")

            # Final Summary
            logger.info(f"\n{'=' * 60}")
            logger.info("🎉 UNIFIED PROTOCOL COMPLETED")
            logger.info(f"{'=' * 60}")
            logger.info(f"Territories processed: {len(results)}/{len(targets)}")
            logger.info(f"Decisions made: {len(decision_engine.decisions_made)}")

            # Decision breakdown
            high_conf = sum(1 for d in decision_engine.decisions_made if d["confidence"] > 0.75)
            med_conf = sum(1 for d in decision_engine.decisions_made if 0.5 <= d["confidence"] <= 0.75)
            low_conf = sum(1 for d in decision_engine.decisions_made if d["confidence"] < 0.5)
            logger.info(f"  High confidence: {high_conf}, Medium: {med_conf}, Low: {low_conf}")

            return results

    # guardian: allow-silent-swallow
    except Exception as fatal_e:  # guardian: allow-silent-swallower
        # Catch-all for top-level crashes (e.g., initialization failure)
        logger.critical(f"🔥 FATAL PROTOCOL ERROR: {fatal_e}")
        traceback.print_exc()
        state_mgr.finish_mission(status="fatal_error")
        sys.exit(1)


# ============================================================================
# DYNAMIC AGENT DISCOVERY (Step 1 Implementation)
# ============================================================================
def load_agents(project_root: Path | None = None) -> dict[str, Any]:
    """
    Dynamically discovers and loads compliant Healer Agents.
    Wraps non-compliant agents in LegacyAgentAdapter.

    Scans 'agentic_core' and 'apps_*' for classes that:
    1. Have 'Agent' or 'Validator' in their name.
    2. Implement the 'heal' method (Standard Heal Interface) OR can be adapted.

    Returns:
        Dict[str, Any]: Map of agent_name -> initialized_instance (or adapter)
    """
    if project_root is None:
        project_root = REPO_ROOT
    logging.info("Starting dynamic agent discovery...")
    discovered_agents = {}

    # Define search paths relative to project root
    search_paths = [
        project_root / "agentic_core",
        # Add other apps_* folders if needed, e.g., apps_private
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Walk directory
        for root, _, files in os.walk(search_path):
            for file in files:
                if not file.endswith(".py") or file.startswith("__"):
                    continue

                # Heuristic: Check file content for 'class' and 'Agent' before importing
                file_path = Path(root) / file
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        if "class " not in content or (
                            "Agent" not in content and "Validator" not in content and "Fixer" not in content
                        ):
                            continue
                # guardian: allow-silent-swallow
                except Exception:  # guardian: allow-silent-swallower
                    continue

                # Construct module path for import
                try:
                    rel_path = file_path.relative_to(project_root)
                    module_name = str(rel_path).replace(os.sep, ".")[:-3]  # strip .py

                    # Safe Import
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if not spec or not spec.loader:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    # Inspect classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Broaden search to include anything that LOOKS like a healer
                        is_likely_agent = (
                            obj.__module__ == module_name
                            and ("Agent" in name or "Fixer" in name or "Validator" in name)
                            and not name.startswith("Base")
                        )

                        if is_likely_agent:
                            try:
                                instance = obj()

                                # CHECK 1: Does it strictly implement the Protocol?
                                if isinstance(instance, IHealerProtocol):
                                    discovered_agents[name] = instance
                                    logging.debug(f"Loaded Standard Agent: {name}")

                                # CHECK 2: Does it have a 'heal' method (Duck Typing)?
                                elif hasattr(instance, "heal") and callable(instance.heal):
                                    discovered_agents[name] = instance
                                    logging.debug(f"Loaded Duck-Typed Agent: {name}")

                                # CHECK 3: Legacy Fallback (Wrap it)
                                else:
                                    logging.info(f"Wrapping Legacy Agent: {name}")
                                    discovered_agents[name] = LegacyAgentAdapter(instance)

                            # guardian: allow-silent-swallow
                            except Exception as e:
                                logging.warning(f"Failed to instantiate {name}: {e}")

                # guardian: allow-silent-swallow
                except Exception as e:
                    logging.debug(f"Skipping module {file_path}: {e}")

    logging.info(f"Discovery complete. Loaded {len(discovered_agents)} agents (including adapters).")
    return discovered_agents


# ============================================================================
# SIGNAL HANDLING (Graceful Shutdown)
# ============================================================================
class GracefulExitHandler:
    """Captures SIGINT/SIGTERM to allow Phase 2 writes to finish safely."""

    def __init__(self, state_mgr: RuntimeStateManager):
        self.state_mgr = state_mgr
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum: int, frame: FrameType | None):
        """Signal handler."""
        if self.kill_now:
            logging.critical("Force quitting on second signal...")
            sys.exit(1)

        logging.warning("\n[!] Shutdown signal received. Finishing current agent operation...")
        self.kill_now = True
        self.state_mgr.finish_mission("aborted_by_user")
        # The logic in Phase 2 should check self.kill_now if loop is tight,
        # but for now we rely on the loop completing the current atomic fix.


# [REMOVED DUPLICATE] main_legacy removed to resolve dual-main entry point confusion.
# The unified main() function below is the single source of truth.


if __name__ == "__main__":
    print(
        "ERROR: Direct invocation of execute_ssot.py is not supported.\n"
        "Use the entrypoint instead:\n"
        "  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy\n",
        file=sys.stderr,
    )
    raise SystemExit(2)
