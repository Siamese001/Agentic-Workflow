"""ADG Visitor Base Classes and Contracts.

Provides the foundation for all AST visitors used in ADG static analysis.
All visitors inherit from BaseADGVisitor and implement the extract_edges method.
"""

from __future__ import annotations

import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@dataclass(frozen=True)
class VisitorContext:
    """Immutable context passed to all visitors during extraction.

    Attributes:
        module_adg_name: Canonical ADG name for the module being scanned
        source_file: Absolute path to the source file being scanned
        repo_root: Repository root path for relative path calculations
    """

    module_adg_name: str
    source_file: str
    repo_root: str = ""


class BaseADGVisitor(ABC, ast.NodeVisitor):
    """Abstract base class for all ADG extraction visitors.

    Contract:
        1. Inherit from BaseADGVisitor and ast.NodeVisitor
        2. Implement extract_edges() to return list of Edge objects
        3. Call self.generic_visit(node) to continue tree traversal
        4. Store edges in self.edges list during visit_* methods
        5. Use self.ctx to access module/file context

    Example:
        class _MyVisitor(BaseADGVisitor):
            def visit_Call(self, node: ast.Call) -> None:
                # Extract edges from call nodes
                edge = self._create_edge("calls", symbol, node.lineno)
                self.edges.append(edge)
                self.generic_visit(node)

            def extract_edges(self) -> list[Edge]:
                return self.edges
    """

    def __init__(self, ctx: VisitorContext) -> None:
        """Initialize visitor with extraction context.

        Args:
            ctx: VisitorContext containing module name and source file path
        """
        super().__init__()
        self.ctx = ctx
        self.edges: list[Edge] = []
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    @abstractmethod
    def extract_edges(self) -> list[Edge]:
        """Return all edges extracted during tree traversal.

        This method is called after the AST walk completes to collect
        all edges discovered by this visitor.

        Returns:
            List of Edge objects extracted from the AST
        """
        pass

    def _create_edge(
        self,
        relation_type: str,
        to_symbol: str,
        line_no: int,
        edge_kind: str = "",
        symbol: str = "",
    ) -> Edge:
        """Factory method to create standardized Edge objects.

        Args:
            relation_type: ADG relation type (e.g., "calls", "imports")
            to_symbol: Target symbol name (canonical or local)
            line_no: Line number in source file
            edge_kind: Optional edge classification
            symbol: Optional symbol that triggered this edge

        Returns:
            Configured Edge dataclass instance
        """
        # Import here to avoid circular dependency
        from agentic_core.adg.contracts.schema_util import canonical_name
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        # Build canonical target name if not already canonical
        if not to_symbol.startswith("ADG::"):
            to_name = canonical_name("Symbol", to_symbol)
        else:
            to_name = to_symbol

        return _Edge(
            from_name=self._module_adg_name,
            relation_type=relation_type,
            to_name=to_name,
            edge_kind=edge_kind or relation_type,
            source_file=self._source_file,
            line_no=line_no,
            symbol=symbol or to_symbol,
        )


class BaseStructuralVisitor(BaseADGVisitor):
    """Base class for structural relationship visitors.

    Structural visitors extract static code relationships:
        - Import relationships
        - Class inheritance
        - Function calls
        - Variable assignments

    These visitors should NOT emit runtime-only edges.
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._local_symbols: set[str] = set()

    def _is_local_symbol(self, name: str) -> bool:
        """Check if a symbol name is locally defined in the module."""
        base_name = name.split(".")[0]
        return base_name in self._local_symbols

    def _register_local(self, name: str) -> None:
        """Register a locally defined symbol name."""
        self._local_symbols.add(name.split(".")[0])


class BaseRuntimeVisitor(BaseADGVisitor):
    """Base class for runtime behavior visitors.

    Runtime visitors extract dynamic/behavioral edges:
        - Execution traces
        - Dynamic invocations
        - Runtime state changes
        - Safety/governance proofs

    These visitors may emit edges that require runtime context.
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._current_function: str = ""
        self._function_stack: list[str] = []

    def _enter_function(self, func_name: str) -> None:
        """Push function context onto stack."""
        self._function_stack.append(self._current_function)
        self._current_function = func_name

    def _exit_function(self) -> None:
        """Pop function context from stack."""
        if self._function_stack:
            self._current_function = self._function_stack.pop()
        else:
            self._current_function = ""


# Visitor registry for discovery
_VISITOR_REGISTRY: dict[str, type[BaseADGVisitor]] = {}


def register_visitor(name: str) -> callable:
    """Decorator to register a visitor class in the registry.

    Args:
        name: Unique identifier for this visitor type

    Returns:
        Decorator function that registers the class

    Example:
        @register_visitor("inheritance")
        class _InheritanceVisitor(BaseStructuralVisitor):
            ...
    """

    def decorator(cls: type[BaseADGVisitor]) -> type[BaseADGVisitor]:
        _VISITOR_REGISTRY[name] = cls
        return cls

    return decorator


def get_registered_visitor(name: str) -> type[BaseADGVisitor] | None:
    """Get a registered visitor class by name.

    Args:
        name: Visitor identifier used during registration

    Returns:
        Visitor class if found, None otherwise
    """
    return _VISITOR_REGISTRY.get(name)


def list_registered_visitors() -> list[str]:
    """Return list of all registered visitor names."""
    return list(_VISITOR_REGISTRY.keys())


# Export structural visitors
from .context_control import (
    _BoundaryVerifierVisitor,
    _DeterminismControlVisitor,
    _IOInterceptionVisitor,
    _JITContextVisitor,
)
from .core import _AntipatternVisitor, _CallVisitor
from .dynamic import _DynamicExecutionVisitor, _ImportVisitor, _InternalCallGraphVisitor
from .governance import (
    _CapabilityBudgetVisitor,
    _GovernancePlaneVisitor,
    _SafetyEnforcementVisitor,
    _SandboxAirlockVisitor,
)
from .l4_waves import (
    _AuthoritativeCommitVisitor,
    _MutationRecordAssemblyVisitor,
    _OutboundReadBridgeVisitor,
    _UWGIngressGateVisitor,
)
from .learning import (
    _L5ValidationProofVisitor,
    _LearningProvenanceVisitor,
    _P3LearningMaturityVisitor,
)
from .lifecycle_advanced import (
    _EmbeddingPipelineVisitor,
    _ExecutionTraceVisitor,
    _HandoffExitVisitor,
    _HealerValidatorVisitor,
    _HITLVisitor,
    _PromptSlotVisitor,
)
from .misc import (
    _DecoratorVisitor,
    _SymbolInventoryVisitor,
    _TestTraceabilityVisitor,
    _TypeAnnotationVisitor,
    _UnusedImportVisitor,
)
from .orchestration import (
    _ArchitectureHandoffVisitor,
    _HealingOrchestratorVisitor,
    _P1OrchestrationVisitor,
    _P2ExecutionCapabilityVisitor,
    _P3OrchestrationHealingVisitor,
)
from .p4_waves import (
    _P4ObservabilityGovernanceVisitor,
    _P4StateTelemetryVisitor,
    _RetrievalWiringVisitor,
)
from .runtime_semantic import _EvalSpineVisitor, _ExecutionSemanticVisitor
from .structural import _AttributeVisitor, _CompositionVisitor, _InheritanceVisitor
from .transport_proof import (
    _ExecutionProofVisitor,
    _MutationTransportVisitor,
    _PathControlVisitor,
)

__all__ = [
    # Base classes
    "VisitorContext",
    "BaseADGVisitor",
    "BaseStructuralVisitor",
    "BaseRuntimeVisitor",
    # Registry
    "register_visitor",
    "get_registered_visitor",
    "list_registered_visitors",
    # Structural visitors
    "_InheritanceVisitor",
    "_AttributeVisitor",
    "_CompositionVisitor",
    # Dynamic visitors
    "_DynamicExecutionVisitor",
    "_ImportVisitor",
    "_InternalCallGraphVisitor",
    # Core visitors
    "_CallVisitor",
    "_AntipatternVisitor",
    # Runtime semantic visitors
    "_ExecutionSemanticVisitor",
    "_EvalSpineVisitor",
    # L4/UWG wave visitors
    "_UWGIngressGateVisitor",
    "_MutationRecordAssemblyVisitor",
    "_AuthoritativeCommitVisitor",
    "_OutboundReadBridgeVisitor",
    # Governance visitors
    "_GovernancePlaneVisitor",
    "_SafetyEnforcementVisitor",
    "_SandboxAirlockVisitor",
    "_CapabilityBudgetVisitor",
    # Context & Control visitors
    "_JITContextVisitor",
    "_BoundaryVerifierVisitor",
    "_DeterminismControlVisitor",
    "_IOInterceptionVisitor",
    # Transport & Proof visitors
    "_MutationTransportVisitor",
    "_ExecutionProofVisitor",
    "_PathControlVisitor",
    # Miscellaneous visitors
    "_TestTraceabilityVisitor",
    "_TypeAnnotationVisitor",
    "_DecoratorVisitor",
    "_SymbolInventoryVisitor",
    "_UnusedImportVisitor",
    # Orchestration visitors
    "_ArchitectureHandoffVisitor",
    "_HealingOrchestratorVisitor",
    "_P1OrchestrationVisitor",
    "_P2ExecutionCapabilityVisitor",
    "_P3OrchestrationHealingVisitor",
    # Learning visitors
    "_L5ValidationProofVisitor",
    "_LearningProvenanceVisitor",
    "_P3LearningMaturityVisitor",
    # Handoff exit visitor
    "_HandoffExitVisitor",
    # P4 wave visitors
    "_P4StateTelemetryVisitor",
    "_P4ObservabilityGovernanceVisitor",
    "_RetrievalWiringVisitor",
]
