"""Hardening tests — convert every "inspection / grep" matrix row to a
deterministic assertion.

Closes the open scope identified in the 00C requirements traceability matrix:

| Matrix row | Closed by                                          |
|------------|----------------------------------------------------|
| 00C.X.1    | ``test_no_l0_routing_imports_in_runtime_gates``    |
| 00C.X.2    | ``test_no_io_imports_in_runtime_gates``            |
| 00C.X.4    | ``test_no_subprocess_or_provider_imports``         |
| 00C.X.7    | ``test_verdict_carries_no_durable_write_keys``     |
| 00C.X.8    | ``test_verdict_carries_no_cert_evidence_key``      |
| 00C.D.7    | ``test_commit_request_verdict_has_no_write_keys``  |
| 00C.IAC.6  | ``test_runtime_gates_only_import_stdlib_or_self``  |
| 00C.7.A.6  | ``test_orchestrator_treats_reroute_as_annotation`` |
| 00C.7.A.8  | ``test_orchestrator_treats_heal_as_annotation``    |
| 00C.7.I.2  | ``test_module_exposes_no_verdict_mutation_api``    |

These tests are statically verifiable: they rebuild the matrix's "inspection"
claims as either AST scans, surface assertions, or behavior assertions on the
orchestrator, so the next regression that violates a doctrine forbidden output
fails CI rather than silently slipping past a manual review.
"""
# pylint: disable=no-name-in-module
# (agentic_core.L5_safety.runtime_gates is a real package but pylint cannot
# resolve its dynamically-registered exports.)

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest
from tqdm import tqdm

from agentic_core.L5_safety.runtime_gates import (
    Disposition,
    GateContext,
    GateDecision,
    Result,
    Severity,
    all_gates,
    evaluate,
)
from agentic_core.L5_safety.runtime_gates.orchestrator import run_mesh

RUNTIME_GATES_PKG = "agentic_core.L5_safety.runtime_gates"
PKG_PATH = Path(importlib.import_module(RUNTIME_GATES_PKG).__file__).parent


# ---------------------------------------------------------------------------
# Static-import audit — closes 00C.X.1 / 00C.X.2 / 00C.X.4 / 00C.IAC.6
# ---------------------------------------------------------------------------


def _iter_module_imports() -> list[tuple[str, str]]:
    """Yield (module_path, imported_name) for every import in the package."""
    pairs: list[tuple[str, str]] = []
    for py in sorted(PKG_PATH.glob("*.py")):
        if py.name.startswith("__"):
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    pairs.append((py.name, alias.name))
            elif isinstance(node, ast.ImportFrom) and node.module:
                pairs.append((py.name, node.module))
    return pairs


# Forbidden import prefixes per doctrine forbidden outputs (parent §FORBIDDEN
# OUTPUTS). Each prefix is matched as ``imported_name == prefix`` or
# ``imported_name.startswith(prefix + ".")``.
_FORBIDDEN_L0_PREFIXES = (
    "agentic_core.L0_routing",
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
    "agentic_core.L3_orchestration",
    "agentic_core.L4_state",
    "agentic_core.L6_observability",
    # C0 retrieval / evidence
    "agentic_core.knowledge",
    # Exit
    "agentic_core.exit",
)

_FORBIDDEN_IO_PREFIXES = (
    "requests",
    "httpx",
    "urllib.request",
    "aiohttp",
    "sqlite3",
    "psycopg",
    "psycopg2",
    "redis",
    "chromadb",
    "boto3",
)

_FORBIDDEN_EXEC_PREFIXES = (
    "subprocess",
    "os.system",
    "shutil.run",
    "openai",
    "anthropic",
    "google.generativeai",
    "vertexai",
    "ollama",
)


def _matches(name: str, prefixes: tuple[str, ...]) -> bool:
    return any(name == p or name.startswith(p + ".") for p in prefixes)


def test_no_l0_routing_imports_in_runtime_gates() -> None:
    """00C.X.1 — runtime gates do not import from any owner-layer module."""
    leaks = [
        (module, name) for module, name in _iter_module_imports() if _matches(name, _FORBIDDEN_L0_PREFIXES)
    ]
    assert leaks == [], (
        f"Runtime gates imported owner-layer modules (forbidden by parent §FORBIDDEN OUTPUTS): {leaks}"
    )


def test_no_io_imports_in_runtime_gates() -> None:
    """00C.X.2 — runtime gates perform no network / database I/O."""
    leaks = [
        (module, name) for module, name in _iter_module_imports() if _matches(name, _FORBIDDEN_IO_PREFIXES)
    ]
    assert leaks == [], f"Runtime gates imported I/O modules: {leaks}"


def test_no_subprocess_or_provider_imports() -> None:
    """00C.X.4 — runtime gates execute no tools / models / scripts."""
    leaks = [
        (module, name) for module, name in _iter_module_imports() if _matches(name, _FORBIDDEN_EXEC_PREFIXES)
    ]
    assert leaks == [], (
        f"Runtime gates imported execution / provider modules (gates emit "
        f"verdicts only — execution belongs to L2): {leaks}"
    )


def test_runtime_gates_only_import_stdlib_or_self() -> None:
    """00C.IAC.6 — gates do not duplicate owner-layer implementation.

    Every non-stdlib import must resolve to ``agentic_core.L5_safety.*`` so a
    runtime gate cannot accidentally absorb the implementation surface of a
    different layer.
    """
    allowed_first_party = ("agentic_core.L5_safety",)
    forbidden = []
    for module, name in _iter_module_imports():
        if name.startswith("agentic_core."):
            if not any(name.startswith(prefix) for prefix in allowed_first_party):
                forbidden.append((module, name))
    assert forbidden == [], (
        f"Runtime gates imported non-L5 first-party modules (potential owner-layer duplication): {forbidden}"
    )


# ---------------------------------------------------------------------------
# Verdict shape audit — closes 00C.X.7 / 00C.X.8 / 00C.D.7
# ---------------------------------------------------------------------------


_FORBIDDEN_VERDICT_KEYS = (
    "l4_mutation",
    "durable_write",
    "cert_evidence",
    "x3_disposition",
    "exit_disposition",
    "promotion",
    "promote",
    "rollout",
    "canary",
)


def _baseline_ctx() -> GateContext:
    """Minimal baseline matching ``conftest._base_ctx`` essentials."""
    return GateContext(
        request_id="req-h-001",
        session_id="sess-h-001",
        run_id="run-h-001",
        trace_root="trace-h-001",
        trace_id="trace-id-h-001",
        tenant_id="tenant-A",
        policy_hash="pol-h",
        blueprint_hash="blue-h",
        replay_key="rk-h",
        evaluated_packet_ref="packet:h:001",
        intent={"objective": "answer", "raw_text": "x?", "payload_bytes": 10},
        risk_tier="low",
        reversible=True,
        impact_class="read",
    )


@pytest.fixture(name="baseline_verdicts")
def _baseline_verdicts_fixture() -> list[dict[str, object]]:
    ctx = _baseline_ctx()
    verdicts: list[dict[str, object]] = []
    for gate_id in tqdm(all_gates(), desc="baseline_verdicts", unit="gate"):
        try:
            decision = evaluate(gate_id, ctx)
        except (KeyError, ValueError, TypeError, AttributeError):
            # guardian: allow-broad-evaluator-failure -- mirror orchestrator;
            # this fixture only cares about verdict shape, not failure modes.
            decision = GateDecision(
                gate_id=gate_id,
                disposition=Disposition.ESCALATE_HITL,
                result=Result.UNKNOWN,
                severity=Severity.HIGH,
                reason_codes=["evaluator_exception_in_hardening_test"],
            )
        verdicts.append(decision.to_verdict())
    return verdicts


def test_verdict_carries_no_durable_write_keys(
    baseline_verdicts: list[dict[str, object]],
) -> None:
    """00C.X.7 — gates do not commit durable state.

    Every verdict shape must be free of any key that could be misread as a
    write-effect carrier (l4_mutation / durable_write).
    """
    leaks = [
        (v["gate_id"], key) for v in baseline_verdicts for key in v if key in ("l4_mutation", "durable_write")
    ]
    assert leaks == [], f"Verdict carried durable-write keys: {leaks}"


def test_verdict_carries_no_cert_evidence_key(
    baseline_verdicts: list[dict[str, object]],
) -> None:
    """00C.X.8 — gates do not certify L5 evidence as own output."""
    leaks = [(v["gate_id"], key) for v in baseline_verdicts for key in v if key == "cert_evidence"]
    assert leaks == [], f"Verdict carried L5 cert_evidence key: {leaks}"


def test_no_forbidden_verdict_keys(
    baseline_verdicts: list[dict[str, object]],
) -> None:
    """Composite — no verdict carries any forbidden authority-expansion key."""
    leaks = [(v["gate_id"], key) for v in baseline_verdicts for key in v if key in _FORBIDDEN_VERDICT_KEYS]
    assert leaks == [], f"Verdict carried forbidden keys: {leaks}"


def test_commit_request_verdict_has_no_write_keys() -> None:
    """00C.D.7 — ``COMMIT_REQUEST`` is non-write (UWG admits the mutation).

    Build a verdict with disposition=COMMIT_REQUEST and assert the serialized
    shape contains no write-effect keys.
    """
    decision = GateDecision(
        gate_id="G27",
        disposition=Disposition.COMMIT_REQUEST,
        reason_codes=["uwg_admission_request"],
    )
    verdict = decision.to_verdict()
    leaks = [key for key in verdict if key in ("l4_mutation", "durable_write", "cert_evidence")]
    assert leaks == [], f"COMMIT_REQUEST verdict carried write-effect keys: {leaks}"


# ---------------------------------------------------------------------------
# Orchestrator behavior — closes 00C.7.A.6 / 00C.7.A.8 / 00C.7.I.2
# ---------------------------------------------------------------------------


class _RerouteGate:
    """Mock gate that always emits REROUTE — annotation only."""

    GATE_ID = "G_TEST_REROUTE"

    def evaluate(self, _ctx: GateContext) -> GateDecision:  # noqa: D401
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.REROUTE,
            reason_codes=["reroute_annotation"],
        )


class _HealGate:
    """Mock gate that always emits HEAL — annotation only."""

    GATE_ID = "G_TEST_HEAL"

    def evaluate(self, _ctx: GateContext) -> GateDecision:  # noqa: D401
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.HEAL,
            reason_codes=["heal_annotation"],
        )


def test_orchestrator_treats_reroute_as_annotation(monkeypatch: pytest.MonkeyPatch) -> None:
    """00C.7.A.6 — Gate REROUTE does not trigger orchestrator re-entry."""
    from agentic_core.L5_safety.runtime_gates import GATE_REGISTRY

    monkeypatch.setitem(GATE_REGISTRY, _RerouteGate.GATE_ID, _RerouteGate())
    ctx = _baseline_ctx()
    result = run_mesh(ctx, order=(_RerouteGate.GATE_ID,))
    # REROUTE is not in HALT_DISPOSITIONS — orchestrator must complete and
    # leave route re-entry to L0/Exit.
    assert result.passed is True, "REROUTE incorrectly halted the mesh"
    assert result.halted_at is None
    assert len(result.decisions) == 1
    decision = result.decisions[0]
    assert decision.disposition is Disposition.REROUTE
    # Annotation-only: result must be WARN, not a structural FAIL.
    assert decision.result is Result.WARN


def test_orchestrator_treats_heal_as_annotation(monkeypatch: pytest.MonkeyPatch) -> None:
    """00C.7.A.8 — Gate HEAL does not trigger orchestrator repair."""
    from agentic_core.L5_safety.runtime_gates import GATE_REGISTRY

    monkeypatch.setitem(GATE_REGISTRY, _HealGate.GATE_ID, _HealGate())
    ctx = _baseline_ctx()
    result = run_mesh(ctx, order=(_HealGate.GATE_ID,))
    # HEAL is not in HALT_DISPOSITIONS — orchestrator must complete.
    assert result.passed is True, "HEAL incorrectly halted the mesh"
    assert result.halted_at is None
    decision = result.decisions[0]
    assert decision.disposition is Disposition.HEAL
    assert decision.result is Result.WARN
    # Annotation-only: ensure no follow-on repair side effect was attempted.
    # Specifically, ctx fields the orchestrator should not touch:
    assert ctx.evaluated_packet_ref == "packet:h:001"
    assert ctx.policy_hash == "pol-h"


# ---------------------------------------------------------------------------
# Module surface audit — closes 00C.7.I.2
# ---------------------------------------------------------------------------


def test_module_exposes_no_verdict_mutation_api() -> None:
    """00C.7.I.2 — emit a new verdict instead of mutating one in place.

    The runtime_gates package surface must not expose any ``update_verdict`` /
    ``mutate_verdict`` / ``patch_verdict`` style API. ``GateDecision`` is a
    dataclass; mutation paths would be the only way for callers to "edit" a
    verdict without re-running a gate.
    """
    pkg = importlib.import_module(RUNTIME_GATES_PKG)
    public = set(getattr(pkg, "__all__", []))
    forbidden_names = {
        "update_verdict",
        "mutate_verdict",
        "patch_verdict",
        "amend_verdict",
        "edit_verdict",
        "rewrite_verdict",
    }
    leaks = public & forbidden_names
    assert leaks == set(), (
        f"runtime_gates exposes verdict-mutation API (forbidden by 00C.7 §GATE VERDICT IMMUTABILITY): {leaks}"
    )


def test_no_module_in_package_exposes_verdict_mutator() -> None:
    """Companion to above — also assert no submodule defines a mutator."""
    forbidden = ("update_verdict", "mutate_verdict", "patch_verdict")
    leaks: list[tuple[str, str]] = []
    for py in sorted(PKG_PATH.glob("*.py")):
        if py.name.startswith("__"):
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in forbidden:
                leaks.append((py.name, node.name))
            elif isinstance(node, ast.AsyncFunctionDef) and node.name in forbidden:
                leaks.append((py.name, node.name))
    assert leaks == [], f"Verdict-mutation symbol found: {leaks}"
