"""Required-gate registry for the ADG audit pipeline manifest.

This is the declarative proof contract. Every entry here is expected to
appear in the gate-invocation manifest at certification time. The wrapper
(``tools/adg/run_full_adg_audit.py``) cross-checks this list against the
manifest produced by a given ``generate_full_adg.py`` run and fails
certification if any entry is missing.

Why a Python module (not YAML): type-checked at import time, easy to import
from both the generator (emitter) and the wrapper (consumer) without
needing a YAML parser, matches the style of other ``tools/generate/``
contract files.

Adding a new gate: append an entry. Removing a gate is a breaking change
to the proof contract — requires ADR and a plan.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

GatePhase = Literal["preflight", "build", "post-commit-validation", "post-ADG-subprocess"]
GateKind = Literal["python_function", "validation", "subprocess"]
BlockingMode = Literal["hard_fail", "soft_warn", "advisory"]


@dataclass(frozen=True)
class RequiredGate:
    """One row in the proof contract."""

    name: str
    phase: GatePhase
    kind: GateKind
    blocking_mode: BlockingMode
    # If True, the gate MUST appear in the manifest in certification mode.
    # Advisory gates that the generator may legitimately not instrument are
    # marked False; they are listed here for documentation only.
    required_in_manifest: bool = True


# The ordered registry. Order is stable and used by docs + wrapper output.
REQUIRED_GATES: tuple[RequiredGate, ...] = (
    # --- Pre-flight (python_function, invoked directly by main()) ---
    RequiredGate("mcp_config_drift", "preflight", "python_function", "hard_fail"),
    RequiredGate("wal_checkpoint", "preflight", "python_function", "hard_fail"),
    RequiredGate("locked_files", "preflight", "python_function", "hard_fail"),
    # --- Post-ADG subprocess chain (the 5 gates run via
    #     _run_post_adg_gate / _run_post_adg_gates_parallel). These are
    #     the primary anti-silent-skip site targeted by this plan. ---
    RequiredGate("wiring", "post-ADG-subprocess", "subprocess", "hard_fail"),
    RequiredGate("config-ref", "post-ADG-subprocess", "subprocess", "hard_fail"),
    RequiredGate("lifecycle", "post-ADG-subprocess", "subprocess", "hard_fail"),
    RequiredGate("except-contract", "post-ADG-subprocess", "subprocess", "hard_fail"),
    RequiredGate("test-coverage", "post-ADG-subprocess", "subprocess", "hard_fail"),
    # --- Structural validation gates (python_function; instrumented
    #     opportunistically by validation/gates.py via the recorder).
    #     Listed as required_in_manifest=True because the generator emits
    #     them via the _record_validation_gate helper at gate exit. ---
    RequiredGate("p0_violations", "post-commit-validation", "validation", "hard_fail"),
    RequiredGate("p1_ratchet", "post-commit-validation", "validation", "hard_fail"),
    RequiredGate("p2_ratchet", "build", "validation", "hard_fail"),
    RequiredGate("dead_production_imports", "post-commit-validation", "validation", "hard_fail"),
    RequiredGate("structural_conformance", "post-commit-validation", "validation", "hard_fail"),
    RequiredGate("agentic_antipatterns", "post-commit-validation", "validation", "hard_fail"),
    RequiredGate("witness_tier_gates", "post-commit-validation", "validation", "hard_fail"),
)


def required_gate_names() -> set[str]:
    """Return the set of gate names that MUST appear in a certification manifest."""
    return {g.name for g in REQUIRED_GATES if g.required_in_manifest}


def find_gate(name: str) -> RequiredGate | None:
    for g in REQUIRED_GATES:
        if g.name == name:
            return g
    return None
