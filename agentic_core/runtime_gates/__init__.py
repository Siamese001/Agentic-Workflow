"""Runtime Gates — Fused gate authority for apps_* domain generation.

This package provides the RuntimeGateEngine, a unified gate execution authority
that apps register into. agentic_core owns runtime gate authority, write
admission, and fail-closed semantics; apps own their domain-specific gate
definitions and callables.

Exports:
    RuntimeGateEngine: Single entrypoint for gate execution
    WriteAdmissionGuard: Authority layer for resume_data mutation
    GateBundle: Aggregated verdicts from gate evaluation
    GateDefinition: Static gate definition
    GateVerdict: Verdict from a single gate
    JudgeVerdict: Verdict from an online judge (normalized to GateVerdict)
    GatePlacement: Lifecycle placement enum
    GateEnforcement: Enforcement level enum
    WriteAdmissionReceipt: Receipt authorizing/denying write
"""

from agentic_core.runtime_gates.definitions import (
    GateDefinition,
    GateEnforcement,
    GatePlacement,
    GateVerdict,
    JudgeVerdict,
)
from agentic_core.runtime_gates.engine import RuntimeGateEngine, GatePack
from agentic_core.runtime_gates.gate_bundle import GateBundle
from agentic_core.runtime_gates.write_admission import (
    WriteAdmissionGuard,
    WriteAdmissionReceipt,
)

__all__ = [
    # Engine and authority
    "RuntimeGateEngine",
    "GatePack",
    "WriteAdmissionGuard",
    # Verdicts and bundles
    "GateBundle",
    "GateVerdict",
    "JudgeVerdict",
    "WriteAdmissionReceipt",
    # Definitions and enums
    "GateDefinition",
    "GateEnforcement",
    "GatePlacement",
]
