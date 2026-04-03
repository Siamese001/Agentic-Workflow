"""
ADG Precision Hardening Schema

Defines the precision hardening data structures for execution-grade semantic graphs.
Transforms high-volume structural ADG into quantitatively governed precision graph.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Any
import hashlib

# =============================================================================
# SECTION 1: NODE GRANULARITY EXPANSION
# =============================================================================

class PrecisionNodeType(Enum):
    """Enhanced node types for precision hardening"""
    SYMBOL = "symbol"           # Original functions, classes, modules
    CODE_BLOCK = "code_block"   # Function decomposition blocks
    EXPRESSION_UNIT = "expression_unit"  # Fine-grained expressions
    CONTROL_BRANCH = "control_branch"    # Control flow branches
    DATA_ORIGIN = "data_origin"         # Data source nodes
    DATA_TRANSFORMATION = "data_transformation"  # Data processing nodes
    DATA_SINK = "data_sink"              # Data destination nodes
    FILESYSTEM_OPERATION = "filesystem_operation"
    NETWORK_CALL = "network_call"
    DATABASE_OPERATION = "database_operation"
    SUBPROCESS_INVOCATION = "subprocess_invocation"
    IN_MEMORY_STATE_MUTATION = "in_memory_state_mutation"

@dataclass(frozen=True)
class NodeSpan:
    """AST span information for precise positioning"""
    start: int
    end: int
    line: int
    column: int
    end_line: int
    end_column: int

@dataclass(frozen=True)
class PrecisionNodeAttributes:
    """Enhanced node attributes for precision hardening"""
    node_type: PrecisionNodeType
    span: NodeSpan
    file_path: str
    enclosing_symbol: Optional[str]
    logical_sequence_id: int
    control_path_id: Optional[str] = None
    temporal_order: Optional[int] = None
    type_surface: Optional[str] = None

# =============================================================================
# SECTION 2: SEMANTIC EDGE TAXONOMY
# =============================================================================

class SemanticEdgeType(Enum):
    """Semantic edge types replacing generic edges"""
    INVOKES_FUNCTION = "invokes_function"
    READS_VARIABLE = "reads_variable"
    WRITES_VARIABLE = "writes_variable"
    MUTATES_STATE = "mutates_state"
    BRANCHES_TO = "branches_to"
    HANDLES_EXCEPTION = "handles_exception"
    EMITS_SIDE_EFFECT = "emits_side_effect"
    RETURNS_VALUE_TO = "returns_value_to"
    AWAITS_COROUTINE = "awaits_coroutine"
    DATA_ORIGINATES_FROM = "data_originates_from"
    DATA_TRANSFORMS_TO = "data_transforms_to"
    DATA_FLOWS_TO = "data_flows_to"
    EXECUTES_BEFORE = "executes_before"
    EXECUTES_AFTER = "executes_after"
    VALIDATES_EXPRESSION = "validates_expression"
    COVERS_BRANCH = "covers_branch"
    OBSERVES_SIDE_EFFECT = "observes_side_effect"
    VIOLATES_POLICY_AT = "violates_policy_at"
    PROPAGATES_VIOLATION_TO = "propagates_violation_to"

@dataclass(frozen=True)
class SemanticEdgeAttributes:
    """Enhanced edge attributes for semantic precision"""
    edge_type: SemanticEdgeType
    source_span: Optional[NodeSpan] = None
    target_span: Optional[NodeSpan] = None
    confidence: float = 1.0
    dynamic_resolution: Optional[Dict[str, Any]] = None

# =============================================================================
# SECTION 3: TYPE SURFACE ENRICHMENT
# =============================================================================

@dataclass(frozen=True)
class TypeSurface:
    """Type information for semantic enrichment"""
    inferred_type: Optional[str]
    possible_types: List[str] = field(default_factory=list)
    nullability: bool = False
    shape_signature: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class VariableAttributes:
    """Variable tracking for data flow lineage"""
    source_origin: str
    mutation_count: int
    lineage_chain: List[str]
    type_surface: Optional[TypeSurface] = None

# =============================================================================
# SECTION 4: PRECISION GRAPH STRUCTURE
# =============================================================================

@dataclass
class PrecisionGraph:
    """Precision graph with enhanced structure"""
    nodes: Dict[str, PrecisionNodeAttributes] = field(default_factory=dict)
    edges: Dict[str, SemanticEdgeAttributes] = field(default_factory=dict)
    edge_types: Dict[str, SemanticEdgeType] = field(default_factory=dict)

    # Type surfaces
    type_surfaces: Dict[str, TypeSurface] = field(default_factory=dict)
    variable_attributes: Dict[str, VariableAttributes] = field(default_factory=dict)

    # Coverage tracking
    functions_analyzed: Set[str] = field(default_factory=set)
    functions_with_blocks: Set[str] = field(default_factory=set)
    variables_with_lineage: Set[str] = field(default_factory=set)
    side_effects_modeled: Set[str] = field(default_factory=set)
    calls_resolved: Set[str] = field(default_factory=set)

    def add_node(self, node_id: str, attributes: PrecisionNodeAttributes) -> None:
        """Add a precision node"""
        self.nodes[node_id] = attributes

    def add_edge(self, edge_id: str, attributes: SemanticEdgeAttributes) -> None:
        """Add a semantic edge"""
        self.edges[edge_id] = attributes
        self.edge_types[edge_id] = attributes.edge_type

    def _compute_graph_hash(self) -> str:
        """Compute deterministic graph hash"""
        hash_input = ""

        # Hash nodes
        for node_id in sorted(self.nodes.keys()):
            attrs = self.nodes[node_id]
            hash_input += f"{node_id}:{attrs.node_type.value}:{attrs.logical_sequence_id}"

        # Hash edges
        for edge_id in sorted(self.edges.keys()):
            attrs = self.edges[edge_id]
            hash_input += f"{edge_id}:{attrs.edge_type.value}"

        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

# =============================================================================
# SECTION 5: METRICS AND VALIDATION
# =============================================================================

@dataclass(frozen=True)
class PrecisionMetrics:
    """Precision hardening metrics"""
    block_level_coverage_ratio: float
    lineage_completeness_score: float
    control_path_coverage: float
    side_effect_coverage: float
    call_resolution_rate: float
    type_annotation_coverage: float
    test_to_execution_link_rate: float
    violation_trace_completeness: float
    generic_edge_ratio: float
    semantic_edge_density: float
    ordering_completeness: float
    graph_hash: str
    replay_signature: Optional[str] = None

@dataclass
class ValidationReport:
    """Precision hardening validation report"""
    passed: bool
    metrics: Optional[PrecisionMetrics] = None
    hard_gates_passed: Optional[Dict[str, bool]] = None
    hard_gate_failures: Optional[List[str]] = None
    error_message: Optional[str] = None
    block_coverage_breakdown: Optional[Dict[str, float]] = None
    lineage_completeness_breakdown: Optional[Dict[str, float]] = None
    control_path_coverage_breakdown: Optional[Dict[str, float]] = None
    side_effect_coverage_breakdown: Optional[Dict[str, float]] = None
    call_resolution_breakdown: Optional[Dict[str, float]] = None
    edge_type_distribution: Optional[Dict[str, int]] = None
    node_type_distribution: Optional[Dict[str, int]] = None
    density_analysis: Optional[Dict[str, Any]] = None
    backward_compatibility_check: bool = True
    existing_queries_functional: bool = True
    violation_count_preserved: bool = True

# =============================================================================
# SECTION 6: CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class PrecisionConfig:
    """Configuration for precision hardening"""

    # Coverage thresholds (Section 11)
    BLOCK_LEVEL_COVERAGE_THRESHOLD = 0.95
    LINEAGE_COMPLETENESS_THRESHOLD = 0.90
    CONTROL_PATH_COVERAGE_THRESHOLD = 0.95
    SIDE_EFFECT_COVERAGE_THRESHOLD = 0.20  # Realistic for general codebase
    CALL_RESOLUTION_RATE_THRESHOLD = 0.95
    TYPE_ANNOTATION_COVERAGE_THRESHOLD = 0.90
    TEST_TO_EXECUTION_LINK_THRESHOLD = 0.90
    VIOLATION_TRACE_COMPLETENESS_THRESHOLD = 0.95

    # Quality thresholds
    GENERIC_EDGE_RATIO_TARGET = 0.0
    ORDERING_COMPLETENESS_TARGET = 1.0

    # Graph stability
    MAX_DENSITY_CHANGE_PERCENT = 10.0
    MIN_NODE_COUNT = 1000
    MIN_EDGE_COUNT = 5000

# Export all public symbols
__all__ = [
    # Node types
    "PrecisionNodeType",
    "NodeSpan",
    "PrecisionNodeAttributes",

    # Edge types
    "SemanticEdgeType",
    "SemanticEdgeAttributes",

    # Type surfaces
    "TypeSurface",
    "VariableAttributes",

    # Graph structure
    "PrecisionGraph",

    # Metrics and validation
    "PrecisionMetrics",
    "ValidationReport",

    # Configuration
    "PrecisionConfig",
]
