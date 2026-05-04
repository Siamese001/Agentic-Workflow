"""Minimal optional agentic_core shim for standalone apps_shared usage.

Installs lightweight fallback modules into ``sys.modules`` when the real
``agentic_core`` package is unavailable. This keeps imports, unit tests, and
static analysis working without changing production behavior when the full stack
is present.
"""

from __future__ import annotations

import json
import sys
import types
from dataclasses import dataclass
from enum import Enum
from typing import Any


class LayerSegment(str, Enum):
    """Small fallback enum matching the lifecycle trace layer names used here."""

    L0_ROUTING = "L0_ROUTING"
    L1_REASONING = "L1_REASONING"
    L2_EXECUTION = "L2_EXECUTION"
    L3_ORCHESTRATION = "L3_ORCHESTRATION"
    L4_STATE = "L4_STATE"


@dataclass(frozen=True)
class ExecutionCycle:
    """Minimal fallback execution cycle."""

    cid: str
    attempt: int = 1


class CIDRegistry:
    """Deterministic, in-memory fallback registry for tests and standalone use."""

    def __init__(self) -> None:
        self._attempts: dict[str, int] = {}

    def new_cycle(self, cid: str) -> ExecutionCycle:
        attempt = self._attempts.get(cid, 0) + 1
        self._attempts[cid] = attempt
        return ExecutionCycle(cid=cid, attempt=attempt)


@dataclass(frozen=True)
class _RiskLevel:
    value: str = "LOW"


@dataclass(frozen=True)
class _RiskDecision:
    allow: bool = True
    level: _RiskLevel = _RiskLevel()
    reasons: tuple[str, ...] = ()


class ConfCalibRiskGate:
    """Null-object fallback risk gate."""

    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> _RiskDecision:
        return _RiskDecision()


class _LifecycleModule(types.ModuleType):
    """Module that lazily returns no-op emitters for lifecycle trace helpers."""

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_emit") or name in {
            "emit_replay_key",
            "emit_determinism_digest",
            "record_execution_trace",
        }:

            def _noop(*args: Any, **kwargs: Any) -> None:
                return None

            return _noop
        raise AttributeError(name)


def canonical_bytes(obj: Any) -> bytes:
    """Best-effort deterministic bytes for hashing in standalone mode."""

    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def _ensure_module(name: str, module: types.ModuleType) -> None:
    if name not in sys.modules:
        sys.modules[name] = module


def install() -> None:
    """Install fallback modules if real agentic_core is missing."""

    try:
        __import__("agentic_core")
        return
    except ModuleNotFoundError:
        pass

    agentic_core = types.ModuleType("agentic_core")
    runtime = types.ModuleType("agentic_core.runtime")
    contracts = types.ModuleType("agentic_core.runtime.contracts")
    lifecycle = _LifecycleModule("agentic_core.runtime.contracts.lifecycle_trace_contract")
    lifecycle.LayerSegment = LayerSegment

    interfaces = types.ModuleType("agentic_core.interfaces")
    execution = types.ModuleType("agentic_core.interfaces.execution")
    execution.CIDRegistry = CIDRegistry
    execution.ExecutionCycle = ExecutionCycle

    determinism = types.ModuleType("agentic_core.interfaces.determinism")
    determinism.canonical_bytes = canonical_bytes

    l0_routing = types.ModuleType("agentic_core.L0_routing")
    l0_config = types.ModuleType("agentic_core.L0_routing.config")
    path_constants = types.ModuleType("agentic_core.L0_routing.config.path_constants")
    path_constants.BATCH_SIZE = 32
    path_constants.BUFFER_SIZE = 8192
    path_constants.DEFAULT_SLEEP = 1.0
    path_constants.DEFAULT_TIMEOUT = 300
    path_constants.MAX_DEPTH = 6
    path_constants.MAX_FILES = 1000
    path_constants.MAX_RETRIES = 3
    path_constants.THRESHOLD = 0.95
    path_constants.AGENTIC_CORE_DIR = "agentic_core"
    path_constants.APPS_LIC_DIR = "apps_lic"
    path_constants.APPS_RG_DIR = "apps_rg"
    path_constants.APPS_SHARED_DIR = "apps_shared"
    path_constants.TESTS_DIR = "tests"
    path_constants.DISCOVERY_EXCLUDED_TERRITORIES = frozenset()
    path_constants.GLOBAL_EXCLUDED_DIRS = frozenset({"__pycache__", ".git", ".pytest_cache"})
    path_constants.SOVEREIGN_EXCLUDED_FOLDERS = frozenset()

    l5_safety = types.ModuleType("agentic_core.L5_safety")
    enforcement = types.ModuleType("agentic_core.L5_safety.enforcement")
    conf_calib_gate = types.ModuleType("agentic_core.L5_safety.enforcement.conf_calib_gate")
    conf_calib_gate.ConfCalibRiskGate = ConfCalibRiskGate

    _ensure_module("agentic_core", agentic_core)
    _ensure_module("agentic_core.runtime", runtime)
    _ensure_module("agentic_core.runtime.contracts", contracts)
    _ensure_module("agentic_core.runtime.contracts.lifecycle_trace_contract", lifecycle)
    _ensure_module("agentic_core.interfaces", interfaces)
    _ensure_module("agentic_core.interfaces.execution", execution)
    _ensure_module("agentic_core.interfaces.determinism", determinism)
    _ensure_module("agentic_core.L0_routing", l0_routing)
    _ensure_module("agentic_core.L0_routing.config", l0_config)
    _ensure_module("agentic_core.L0_routing.config.path_constants", path_constants)
    _ensure_module("agentic_core.L5_safety", l5_safety)
    _ensure_module("agentic_core.L5_safety.enforcement", enforcement)
    _ensure_module("agentic_core.L5_safety.enforcement.conf_calib_gate", conf_calib_gate)
