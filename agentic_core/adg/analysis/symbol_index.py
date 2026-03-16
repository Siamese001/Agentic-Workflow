"""E11: Cross-File Symbol Resolution Index.

Builds a queryable index of ``symbol_name -> defining_module`` from the
``exports`` edges emitted by E1 (``_SymbolInventoryVisitor``).

The index enables downstream passes to:
  - Resolve an imported name to the module that defines it
  - Feed the ``_all_registry`` used by E2 star-import resolution
  - Cross-reference dead imports (E6) against actual exported symbols
  - Support future Protocol/ABC coverage checks (E8)

Usage::

    from agentic_core.adg.analysis.symbol_index import SymbolIndex

    index = SymbolIndex.build(scan_result)
    module = index.resolve("my_function")          # -> "ADG::Module::pkg/mod.py"
    exports = index.exports_of("pkg/mod.py")       # -> ["func_a", "MyClass"]
    all_registry = index.build_all_registry()      # module dotted path -> [names]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "symbol_index", "p0_governance")
_emit_reads_policy_state("p0", "symbol_index", "policy_binding")
_emit_snapshots_state("p0", "symbol_index", "state_snapshot")
emit_replay_key("p0", "symbol_index")
emit_determinism_digest("p0", "symbol_index")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"


@dataclass
class SymbolIndex:
    """Queryable cross-file symbol → defining-module index.

    Attributes:
        symbol_to_module:  ``{symbol_name: module_adg_name}`` mapping built
                           from ``exports`` edges.  When a name is exported
                           by multiple modules the *last encountered* wins
                           (non-deterministic across scan order unless edges
                           are pre-sorted, which they are in ``ScanResult``).
        module_to_symbols: ``{module_adg_name: [symbol_name, ...]}`` reverse
                           mapping built at the same time.
        total_exports:     total number of ``exports`` edges processed.
    """

    symbol_to_module: dict[str, str] = field(default_factory=dict)
    module_to_symbols: dict[str, list[str]] = field(default_factory=dict)
    total_exports: int = 0

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def build(cls, result: ScanResult) -> SymbolIndex:
        """Build the index from all ``exports`` edges in *result*."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SymbolIndex.build")

        idx = cls()
        for edge in result.edges:
            if edge.relation_type != "exports":
                continue
            symbol = edge.symbol
            module = edge.from_name
            if not symbol or not module.startswith(_MODULE_PREFIX):
                continue
            idx.symbol_to_module[symbol] = module
            idx.module_to_symbols.setdefault(module, []).append(symbol)
            idx.total_exports += 1
        for lst in idx.module_to_symbols.values():
            lst.sort()
        return idx

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def resolve(self, symbol_name: str) -> str | None:
        """Return the ADG module name that exports *symbol_name*, or None."""
        return self.symbol_to_module.get(symbol_name)

    def exports_of(self, module_rel_or_adg: str) -> list[str]:
        """Return the list of exported symbol names for a module.

        Accepts either the repo-relative path (``pkg/mod.py``) or the full
        ADG name (``ADG::Module::pkg/mod.py``).
        """
        adg_name = (
            module_rel_or_adg
            if module_rel_or_adg.startswith(_MODULE_PREFIX)
            else f"{_MODULE_PREFIX}{module_rel_or_adg}"
        )
        return list(self.module_to_symbols.get(adg_name, []))

    def build_all_registry(self) -> dict[str, list[str]]:
        """Build an ``__all__``-style registry keyed by dotted module path.

        Converts ``ADG::Module::pkg/sub/mod.py`` → ``pkg.sub.mod`` and
        maps it to the list of exported symbol names.  Useful as the
        ``all_registry`` argument to ``_ImportVisitor`` for E2 star-import
        resolution.
        """
        registry: dict[str, list[str]] = {}
        for adg_name, symbols in self.module_to_symbols.items():
            if not adg_name.startswith(_MODULE_PREFIX):
                continue
            rel = adg_name[len(_MODULE_PREFIX) :]
            dotted = rel.replace("/", ".").replace("\\", ".")
            if dotted.endswith(".py"):
                dotted = dotted[:-3]
            if dotted.endswith(".__init__"):
                dotted = dotted[: -len(".__init__")]
            registry[dotted] = list(symbols)
        return registry

    def stats(self) -> dict:
        """Return summary statistics about the index."""
        return {
            "total_exports": self.total_exports,
            "unique_symbols": len(self.symbol_to_module),
            "modules_with_exports": len(self.module_to_symbols),
        }


__all__ = [
    "SymbolIndex",
]
