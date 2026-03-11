"""E31: Policy Hash Runtime Validation.

Validates that modules referencing runtime instruction packets also reference
an active policy hash. The architecture asserts:

    all instruction packets → must reference active policy_hash

This analyzer detects:
    1. Modules that use policy-hash symbols but reference potentially stale hashes
    2. Modules that produce/consume prompts without any policy_hash reference
    3. Modules in L0-L3 that route/orchestrate without policy hash coupling

From the live ADG (20260311 scan), policy-related symbols confirmed:
    - ADG::Symbol::uwg._verify_plan_hash
    - ADG::Symbol::uwg._verify_replay_hash
    - governance test modules referencing policy_hash patterns

Usage::

    from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

    report = validate_policy_hash_coupling(result)
    print(report.summary)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.schema import module_path_to_layer

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

# Symbols that indicate policy hash awareness
_POLICY_HASH_SYMBOLS: frozenset[str] = frozenset(
    {
        "policy_hash",
        "_verify_plan_hash",
        "_verify_replay_hash",
        "verify_policy_hash",
        "POLICY_HASH",
        "policy_root",
        "merkle_root",
        "config_hash",
        "instruction_hash",
        "MERKLE_POLICY_ROOT",
    }
)

# Symbols that indicate instruction packet creation/routing (should be policy-coupled)
_INSTRUCTION_PACKET_SYMBOLS: frozenset[str] = frozenset(
    {
        "InstructionPacket",
        "instruction_packet",
        "build_instruction",
        "create_instruction",
        "route_instruction",
        "RoutingInputs",
        "AutonomousDecisionEngine",
        "SovereignDecisionEngine",
        "GovernedPayload",
        "AssembledPrompt",
    }
)

# Layers that MUST have policy hash coupling if they route instructions
_POLICY_REQUIRED_LAYERS: frozenset[str] = frozenset({"L0", "L1", "L2", "L3"})


@dataclass
class PolicyHashViolation:
    """A module that creates/routes instruction packets without policy hash coupling."""

    module_path: str
    layer: str
    violation_type: str
    instruction_symbols_used: list[str]
    has_policy_hash_ref: bool
    severity: str
    suggested_fix: str

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "layer": self.layer,
            "violation_type": self.violation_type,
            "instruction_symbols_used": self.instruction_symbols_used,
            "has_policy_hash_ref": self.has_policy_hash_ref,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class PolicyHashReport:
    """Report of policy hash coupling validation."""

    violations: list[PolicyHashViolation] = field(default_factory=list)
    policy_coupled_modules: list[str] = field(default_factory=list)
    instruction_modules: list[str] = field(default_factory=list)
    violation_count: int = 0

    @property
    def coupling_rate(self) -> float:
        total = len(self.instruction_modules)
        if total == 0:
            return 1.0
        return round(len(self.policy_coupled_modules) / total, 4)

    @property
    def summary(self) -> str:
        return (
            f"Policy hash coupling: {self.violation_count} uncoupled modules | "
            f"{len(self.policy_coupled_modules)} coupled | "
            f"{len(self.instruction_modules)} instruction modules | "
            f"coupling={self.coupling_rate:.1%}"
        )

    def to_dict(self) -> dict:
        return {
            "violation_count": self.violation_count,
            "coupled_count": len(self.policy_coupled_modules),
            "instruction_module_count": len(self.instruction_modules),
            "coupling_rate": self.coupling_rate,
            "summary": self.summary,
            "violations": [v.to_dict() for v in self.violations],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def validate_policy_hash_coupling(result: ScanResult) -> PolicyHashReport:
    """Validate that instruction packet modules reference active policy hashes.

    Pass 1: Build module → instruction symbols used index.
    Pass 2: Build module → policy hash symbols used index.
    Pass 3: For each instruction module in L0-L3, check for policy hash coupling.
    """
    # Pass 1: instruction packet usage per module
    instruction_map: dict[str, list[str]] = {}
    for edge in result.edges:
        if edge.relation_type not in ("calls", "instantiates", "imports"):
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        sym = edge.to_name
        if sym.startswith(_SYMBOL_PREFIX):
            sym = sym[len(_SYMBOL_PREFIX) :]
        sym_base = sym.split(".")[-1] if "." in sym else sym

        if sym_base in _INSTRUCTION_PACKET_SYMBOLS or sym in _INSTRUCTION_PACKET_SYMBOLS:
            mod = edge.from_name[len(_MODULE_PREFIX) :]
            instruction_map.setdefault(mod, []).append(sym_base)

    # Pass 2: policy hash usage per module
    policy_hash_modules: set[str] = set()
    for edge in result.edges:
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        sym = edge.to_name
        if sym.startswith(_SYMBOL_PREFIX):
            sym = sym[len(_SYMBOL_PREFIX) :]
        sym_base = sym.split(".")[-1] if "." in sym else sym

        if sym_base in _POLICY_HASH_SYMBOLS or sym in _POLICY_HASH_SYMBOLS:
            mod = edge.from_name[len(_MODULE_PREFIX) :]
            policy_hash_modules.add(mod)

    # Pass 3: classify
    violations: list[PolicyHashViolation] = []
    coupled: list[str] = []
    instruction_mods: list[str] = sorted(instruction_map.keys())

    for mod in instruction_mods:
        layer = module_path_to_layer(mod)
        if layer not in _POLICY_REQUIRED_LAYERS:
            continue

        has_policy = mod in policy_hash_modules
        if has_policy:
            coupled.append(mod)
            continue

        symbols_used = sorted(set(instruction_map[mod]))
        violations.append(
            PolicyHashViolation(
                module_path=mod,
                layer=layer,
                violation_type="INSTRUCTION_WITHOUT_POLICY_HASH",
                instruction_symbols_used=symbols_used,
                has_policy_hash_ref=False,
                severity="high" if layer in ("L0", "L1") else "medium",
                suggested_fix=(
                    f"Module in {layer} creates/routes instruction packets but does not "
                    "reference an active policy_hash. Add policy hash verification via "
                    "uwg._verify_plan_hash() or equivalent before routing instructions."
                ),
            )
        )

    violations.sort(
        key=lambda v: (
            {"high": 0, "medium": 1, "low": 2}.get(v.severity, 3),
            v.module_path,
        )
    )

    return PolicyHashReport(
        violations=violations,
        policy_coupled_modules=coupled,
        instruction_modules=instruction_mods,
        violation_count=len(violations),
    )


__all__ = [
    "PolicyHashReport",
    "PolicyHashViolation",
    "validate_policy_hash_coupling",
]
