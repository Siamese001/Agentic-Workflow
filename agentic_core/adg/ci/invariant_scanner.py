"""ADG CI Invariant Scanner -- pre-merge policy enforcement.

Implements core invariant rules:

RULE A: No LLM provider SDK import outside SovereignLLMGateway
RULE B: No embedding instantiation outside EmbeddingFactory (EmbeddingSovereignAgent)
RULE C: No upward mutation edges (layer boundary enforcement)
RULE D: No duplicate method definitions within a class (RCA fix — catches FallbackClient.generate)
RULE G: No unreachable code after raise (RCA fix — catches Logger.warning after raise)

Each rule produces a list of Violation objects with offending edge,
minimal path witness, and policy_id.

Exit codes:
    0 = all invariants pass
    1 = one or more violations found
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from typing import TYPE_CHECKING, Any

from agentic_core.adg.schema import (
    ALLOWED_LAYER_EDGES,
    EMBEDDING_SYMBOLS,
    GATEWAY_ALLOWLIST,
    PROVIDER_SDK_SYMBOLS,
    module_path_to_layer,
)

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_POLICY_LLM_EGRESS = "ADG::Policy::LLM_EGRESS_SINGLETON"
_POLICY_EMBEDDING_FACTORY = "ADG::Policy::EMBEDDING_FACTORY_SINGLETON"
_POLICY_LAYER_BOUNDARY = "ADG::Policy::LAYER_BOUNDARY_DOWNWARD_ONLY"
_POLICY_DYNAMIC_EXEC = "ADG::Policy::NO_DYNAMIC_EXECUTION"
_POLICY_DUPLICATE_METHOD = "ADG::Policy::NO_DUPLICATE_METHOD"
_POLICY_UNREACHABLE_AFTER_RAISE = "ADG::Policy::NO_UNREACHABLE_AFTER_RAISE"

# S3: Allowlisted paths for dynamic execution (e.g. REPL, test harnesses)
_DYNAMIC_EXEC_ALLOWLIST: frozenset[str] = frozenset(
    {
        "tests/",
        "ops_scripts/",
        "tools/",
        "agentic_core/adg/",
    }
)

_SOVEREIGN_LLM_GW_PATH = GATEWAY_ALLOWLIST["SovereignLLMGateway"]
_EMBEDDING_GW_PATH = GATEWAY_ALLOWLIST["EmbeddingSovereignAgent"]


@dataclass
class Violation:
    """A single invariant violation."""

    rule: str
    policy_id: str
    offending_edge: str
    from_module: str
    to_symbol: str
    source_file: str
    line_no: int
    witness: str

    def format(self) -> str:
        return (
            f"VIOLATION [{self.rule}] policy={self.policy_id}\n"
            f"  from:    {self.from_module}\n"
            f"  to:      {self.to_symbol}\n"
            f"  file:    {self.source_file}:{self.line_no}\n"
            f"  witness: {self.witness}\n"
            f"  edge:    {self.offending_edge}"
        )


@dataclass
class ScanReport:
    """Full report of an invariant scan."""

    violations: list[Violation] = field(default_factory=list)
    new_edges_count: int = 0
    digest: str = ""
    scan_result: object = field(default=None, repr=False)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def print_summary(self) -> None:
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "InvariantScanResult.print_summary")
        if self.passed:
            print(f"ADG-INVARIANT-SCAN: PASSED (new_edges={self.new_edges_count}, digest={self.digest})")
        else:
            print(f"ADG-INVARIANT-SCAN: FAILED ({len(self.violations)} violation(s))")
            for v in self.violations:
                print(v.format())

    def exit_code(self) -> int:
        return 0 if self.passed else 1


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _symbol_name(adg_name: str) -> str:
    prefix = "ADG::Symbol::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _is_gateway_module(rel_path: str, gateway_path: str) -> bool:
    norm = rel_path.replace("\\", "/")
    gw = gateway_path.replace("\\", "/")
    return norm == gw or norm.endswith(gw)


def _layer_num(label: str) -> int | None:
    if label.startswith("L") and len(label) == 2 and label[1].isdigit():
        return int(label[1])
    return None


class InvariantScanner:
    """Runs all three invariant rules against a ScanResult."""

    def __init__(self, strict: bool = True) -> None:
        self.strict = strict

    def scan(self, result: ScanResult) -> ScanReport:
        """Run all invariant rules and return a ScanReport."""
        report = ScanReport(
            new_edges_count=len(result.edges),
            digest=result.digest,
            scan_result=result,
        )
        report.violations.extend(self._rule_a_no_llm_bypass(result))
        report.violations.extend(self._rule_b_no_embedding_bypass(result))
        report.violations.extend(self._rule_c_no_upward_layer_mutation(result))
        report.violations.extend(self._rule_f_dynamic_exec(result))
        report.violations.extend(self._rule_d_duplicate_method(result))
        report.violations.extend(self._rule_g_unreachable_after_raise(result))
        return report

    def _rule_a_no_llm_bypass(self, result: ScanResult) -> list[Violation]:
        """RULE A: No LLM provider SDK import outside SovereignLLMGateway."""
        violations: list[Violation] = []
        provider_bases = {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}

        for edge in result.edges:
            if edge.relation_type not in ("imports", "invokes_provider"):
                continue
            sym = _symbol_name(edge.to_name)
            sym_base = sym.split(".")[0]
            if sym_base not in provider_bases:
                continue
            from_rel = _module_rel(edge.from_name)
            if _is_gateway_module(from_rel, _SOVEREIGN_LLM_GW_PATH):
                continue
            if from_rel.endswith("client_wrappers.py"):
                continue
            witness = (
                f"{from_rel} directly imports/calls provider SDK '{sym}' "
                f"without routing through SovereignLLMGateway "
                f"({_SOVEREIGN_LLM_GW_PATH})"
            )
            violations.append(
                Violation(
                    rule="RULE_A",
                    policy_id=_POLICY_LLM_EGRESS,
                    offending_edge=f"{edge.from_name} --{edge.relation_type}--> {edge.to_name}",
                    from_module=from_rel,
                    to_symbol=sym,
                    source_file=edge.source_file,
                    line_no=edge.line_no,
                    witness=witness,
                )
            )
        return violations

    def _rule_b_no_embedding_bypass(self, result: ScanResult) -> list[Violation]:
        """RULE B: No embedding instantiation outside EmbeddingSovereignAgent."""
        violations: list[Violation] = []

        for edge in result.edges:
            if edge.edge_kind != "embedding" or edge.relation_type != "instantiates":
                continue
            from_rel = _module_rel(edge.from_name)
            if _is_gateway_module(from_rel, _EMBEDDING_GW_PATH):
                continue
            sym = _symbol_name(edge.to_name)
            if sym not in EMBEDDING_SYMBOLS:
                continue
            witness = (
                f"{from_rel} instantiates embedding symbol '{sym}' "
                f"without routing through EmbeddingSovereignAgent "
                f"({_EMBEDDING_GW_PATH})"
            )
            violations.append(
                Violation(
                    rule="RULE_B",
                    policy_id=_POLICY_EMBEDDING_FACTORY,
                    offending_edge=f"{edge.from_name} --{edge.relation_type}--> {edge.to_name}",
                    from_module=from_rel,
                    to_symbol=sym,
                    source_file=edge.source_file,
                    line_no=edge.line_no,
                    witness=witness,
                )
            )
        return violations

    def _rule_c_no_upward_layer_mutation(self, result: ScanResult) -> list[Violation]:
        """RULE C: No upward import/write edges (lower layer importing higher layer)."""
        violations: list[Violation] = []

        for edge in result.edges:
            if edge.relation_type not in ("imports", "writes_to", "invokes_provider"):
                continue

            from_rel = _module_rel(edge.from_name)
            from_layer = module_path_to_layer(from_rel)

            to_rel = _module_rel(edge.to_name)
            to_layer = module_path_to_layer(to_rel)

            if from_layer == "L_UNKNOWN" or to_layer == "L_UNKNOWN":
                continue
            if from_layer == to_layer:
                continue

            pair = (from_layer, to_layer)
            if pair in ALLOWED_LAYER_EDGES:
                continue

            all_l_layers = {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}
            if from_layer not in all_l_layers or to_layer not in all_l_layers:
                continue

            from_num = _layer_num(from_layer)
            to_num = _layer_num(to_layer)
            if from_num is None or to_num is None:
                continue
            if from_num < to_num:
                witness = (
                    f"Upward edge: {from_rel} (layer={from_layer}) "
                    f"imports/writes {to_rel} (layer={to_layer}). "
                    f"Only downward edges are allowed."
                )
                violations.append(
                    Violation(
                        rule="RULE_C",
                        policy_id=_POLICY_LAYER_BOUNDARY,
                        offending_edge=(f"{edge.from_name} --{edge.relation_type}--> {edge.to_name}"),
                        from_module=from_rel,
                        to_symbol=to_rel,
                        source_file=edge.source_file,
                        line_no=edge.line_no,
                        witness=witness,
                    )
                )
        return violations

    def _rule_f_dynamic_exec(self, result: ScanResult) -> list[Violation]:
        """RULE F (S3): No dynamic execution (eval/exec/importlib) in sovereign layers.

        Allowlisted: tests/, ops_scripts/, tools/, agentic_core/adg/
        """
        violations: list[Violation] = []

        for edge in result.edges:
            if edge.edge_kind != "dynamic_exec":
                continue
            from_rel = _module_rel(edge.from_name)
            # Check allowlist
            if any(from_rel.startswith(allowed) for allowed in _DYNAMIC_EXEC_ALLOWLIST):
                continue
            sym = edge.symbol or _symbol_name(edge.to_name)
            witness = (
                f"{from_rel} uses dynamic execution '{sym}' which bypasses static analysis and governance."
            )
            violations.append(
                Violation(
                    rule="RULE_F",
                    policy_id=_POLICY_DYNAMIC_EXEC,
                    offending_edge=f"{edge.from_name} --{edge.relation_type}--> {edge.to_name}",
                    from_module=from_rel,
                    to_symbol=sym,
                    source_file=edge.source_file,
                    line_no=edge.line_no,
                    witness=witness,
                )
            )
        return violations


    def _rule_d_duplicate_method(self, result: ScanResult) -> list[Violation]:
        """RULE D: No duplicate method definitions within the same class.

        Catches the pattern:
            class Foo:
                def bar(self): ...   # first definition
                def bar(self): ...   # duplicate — second silently shadows first
        """
        violations: list[Violation] = []
        for edge in result.edges:
            if edge.relation_type != "duplicate_method":
                continue
            from_rel = _module_rel(edge.from_name)
            sym = edge.symbol
            witness = (
                f"{from_rel} contains duplicate method definition '{sym}'. "
                f"The second definition at line {edge.line_no} silently shadows the first."
            )
            violations.append(
                Violation(
                    rule="RULE_D",
                    policy_id=_POLICY_DUPLICATE_METHOD,
                    offending_edge=f"{edge.from_name} --duplicate_method--> {edge.to_name}",
                    from_module=from_rel,
                    to_symbol=_symbol_name(edge.to_name),
                    source_file=edge.source_file,
                    line_no=edge.line_no,
                    witness=witness,
                )
            )
        return violations

    def _rule_g_unreachable_after_raise(self, result: ScanResult) -> list[Violation]:
        """RULE G: No unreachable statements after a bare raise in exception handlers.

        Catches the pattern:
            except Exception as e:
                raise
                Logger.warning(...)   # <-- unreachable dead code
        """
        violations: list[Violation] = []
        for edge in result.edges:
            if edge.relation_type != "unreachable_after_raise":
                continue
            from_rel = _module_rel(edge.from_name)
            raise_line = edge.symbol.replace("raise_at_line_", "")
            witness = (
                f"{from_rel} has unreachable statement at line {edge.line_no} "
                f"(follows unconditional raise at line {raise_line}). Dead code."
            )
            violations.append(
                Violation(
                    rule="RULE_G",
                    policy_id=_POLICY_UNREACHABLE_AFTER_RAISE,
                    offending_edge=f"{edge.from_name} --unreachable_after_raise--> {edge.to_name}",
                    from_module=from_rel,
                    to_symbol="unreachable_code",
                    source_file=edge.source_file,
                    line_no=edge.line_no,
                    witness=witness,
                )
            )
        return violations


def run_ci_scan(
    repo_root: str = ".",
    diff_files: list[str] | None = None,
    commit_sha: str = "",
    print_digest: bool = True,
    include_tests: bool = True,
) -> ScanReport:
    """Main CI entry point."""
    from pathlib import Path

    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=Path(repo_root), include_tests=include_tests)

    if diff_files is not None:
        result = scanner.scan_files(diff_files, commit_sha=commit_sha)
    else:
        result = scanner.scan(commit_sha=commit_sha)

    if print_digest:
        result.print_digest()

    inv_scanner = InvariantScanner()
    return inv_scanner.scan(result)


__all__ = [
    "InvariantScanner",
    "Violation",
    "ScanReport",
    "run_ci_scan",
    "_POLICY_DYNAMIC_EXEC",
    "_POLICY_DUPLICATE_METHOD",
    "_POLICY_UNREACHABLE_AFTER_RAISE",
]
