"""
L5 Agentic Core - L3 Orchestration Layer - DAG Engine
Implements L3 Orchestration Layer for Directed Acyclic Graph execution coordination
"""

from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid
import time
from collections import defaultdict, deque

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    """L5 Node status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"

class ExecutionMode(Enum):
    """L5 Execution mode enumeration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    FAILOVER = "failover"

@dataclass
class DAGConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_nodes: int = 100
    max_depth: int = 10
    max_execution_time: float = 300.0  # 5 minutes
    max_parallel_nodes: int = 5
    require_safety_checkpoints: bool = True
    safety_level: str = "strict"

@dataclass
class DAGNode:
    """L5 DAG node structure with full type safety"""
    node_id: str
    node_type: str  # "tool", "parser", "validator"
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error_message: str = ""
    execution_time: float = 0.0
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class DAGEdge:
    """L5 DAG edge structure"""
    source_node: str
    target_node: str
    condition: str = ""  # Optional condition for edge traversal
    data_mapping: Dict[str, str] = field(default_factory=dict)  # Map outputs to inputs

@dataclass
class DAGExecution:
    """L5 DAG execution structure"""
    execution_id: str
    dag_id: str
    nodes: List[DAGNode] = field(default_factory=list)
    edges: List[DAGEdge] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    status: NodeStatus = NodeStatus.PENDING
    start_time: str = ""
    end_time: str = ""
    execution_graph: Dict[str, List[str]] = field(default_factory=dict)
    safety_validated: bool = False
    timestamp: str = ""

class DAGEngine(ABC):
    """L5 Abstract base - ensures L3 orchestration behavior"""
    
    @abstractmethod
    def create_dag(self, nodes: List[DAGNode], edges: List[DAGEdge], constraints: DAGConstraints) -> DAGExecution:
        """Create DAG with L5 safety constraints"""
        pass
    
    @abstractmethod
    def execute_dag(self, dag: DAGExecution, mode: ExecutionMode) -> DAGExecution:
        """Execute DAG with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, dag: DAGExecution) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class DAGEngineImpl(DAGEngine):
    """
    L5 Implementation - L3 Orchestration Layer
    Pure DAG orchestration execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[DAGConstraints] = None):
        self.constraints = constraints or DAGConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.active_executions: Dict[str, DAGExecution] = {}
        
        # Initialize L2 execution engines (factories)
        from ..l2_execution.execution_engines.tool_invocation import ToolInvocationEngineFactory
        from ..l2_execution.execution_engines.validation import ValidationEngineFactory
        from ..l2_execution.parsing_engines.text_parser import TextParserFactory
        from ..l2_execution.parsing_engines.json_parser import JSONParserFactory
        from ..l2_execution.parsing_engines.yaml_parser import YAMLParserFactory
        
        self.tool_engine = ToolInvocationEngineFactory.create_engine()
        self.validation_engine = ValidationEngineFactory.create_engine()
        self.text_parser = TextParserFactory.create_parser()
        self.json_parser = JSONParserFactory.create_parser()
        self.yaml_parser = YAMLParserFactory.create_parser()
    
    def create_dag(self, nodes: List[DAGNode], edges: List[DAGEdge], constraints: Optional[DAGConstraints] = None) -> DAGExecution:
        """Create DAG following L5 architecture principles"""
        dag_constraints = constraints or self.constraints
        self.logger.info(f"Creating DAG with {len(nodes)} nodes and {len(edges)} edges")
        
        # L5 Input validation
        self._validate_dag_input(nodes, edges)
        
        # Create DAG execution
        dag_id = self._generate_dag_id()
        execution_id = self._generate_execution_id()
        
        # Build execution graph
        execution_graph = self._build_execution_graph(nodes, edges)
        
        # Validate DAG structure
        self._validate_dag_structure(nodes, edges, execution_graph, dag_constraints)
        
        dag = DAGExecution(
            execution_id=execution_id,
            dag_id=dag_id,
            nodes=nodes,
            edges=edges,
            execution_graph=execution_graph,
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        # Store active execution
        self.active_executions[execution_id] = dag
        
        self.logger.info(f"DAG created successfully: {dag_id}")
        return dag
    
    def execute_dag(self, dag: DAGExecution, mode: ExecutionMode) -> DAGExecution:
        """Execute DAG following L5 architecture principles"""
        self.logger.info(f"Executing DAG {dag.dag_id} with mode: {mode.value}")
        
        # L5 Input validation
        self._validate_execution_input(dag, mode)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(dag):
            raise SecurityError("DAG execution failed L5 safety validation")
        
        # Initialize execution
        dag.status = NodeStatus.RUNNING
        dag.start_time = self._get_timestamp()
        dag.execution_mode = mode
        
        try:
            # Execute based on mode
            if mode == ExecutionMode.SEQUENTIAL:
                self._execute_sequential(dag)
            elif mode == ExecutionMode.PARALLEL:
                self._execute_parallel(dag)
            elif mode == ExecutionMode.HYBRID:
                self._execute_hybrid(dag)
            elif mode == ExecutionMode.FAILOVER:
                self._execute_failover(dag)
            else:
                raise ValueError(f"Unsupported execution mode: {mode}")
            
            # Finalize execution
            dag.end_time = self._get_timestamp()
            
            # Determine final status
            failed_nodes = [n for n in dag.nodes if n.status == NodeStatus.FAILED]
            if failed_nodes:
                dag.status = NodeStatus.FAILED
            else:
                dag.status = NodeStatus.COMPLETED
            
            self.logger.info(f"DAG execution completed: {dag.status.value}")
            return dag
            
        except Exception as e:
            self.logger.error(f"DAG execution error: {e}")
            dag.status = NodeStatus.FAILED
            dag.end_time = self._get_timestamp()
            return dag
    
    def _execute_sequential(self, dag: DAGExecution) -> None:
        """Execute DAG nodes sequentially"""
        # Get topological order
        execution_order = self._get_topological_order(dag)
        
        for node_id in execution_order:
            node = self._find_node(dag, node_id)
            if node:
                self._execute_node(dag, node)
                
                # Check if node failed and should stop execution
                if node.status == NodeStatus.FAILED:
                    self.logger.error(f"Node {node_id} failed, stopping sequential execution")
                    break
    
    def _execute_parallel(self, dag: DAGExecution) -> None:
        """Execute DAG nodes in parallel where possible"""
        # Get execution levels (nodes that can run in parallel)
        execution_levels = self._get_execution_levels(dag)
        
        for level_nodes in execution_levels:
            # Limit parallel nodes
            level_nodes = level_nodes[:self.constraints.max_parallel_nodes]
            
            # Execute nodes in parallel (simplified implementation)
            for node_id in level_nodes:
                node = self._find_node(dag, node_id)
                if node:
                    self._execute_node(dag, node)
            
            # Check if any node failed
            failed_nodes = [n for n in dag.nodes if n.status == NodeStatus.FAILED]
            if failed_nodes:
                self.logger.error("Parallel execution failed, stopping")
                break
    
    def _execute_hybrid(self, dag: DAGExecution) -> None:
        """Execute DAG with hybrid strategy"""
        # Use parallel for independent nodes, sequential for dependent chains
        execution_levels = self._get_execution_levels(dag)
        
        for level_nodes in execution_levels:
            if len(level_nodes) == 1:
                # Single node - execute sequentially
                node = self._find_node(dag, level_nodes[0])
                if node:
                    self._execute_node(dag, node)
            else:
                # Multiple nodes - execute in parallel
                level_nodes = level_nodes[:self.constraints.max_parallel_nodes]
                for node_id in level_nodes:
                    node = self._find_node(dag, node_id)
                    if node:
                        self._execute_node(dag, node)
            
            # Check for failures
            failed_nodes = [n for n in dag.nodes if n.status == NodeStatus.FAILED]
            if failed_nodes:
                break
    
    def _execute_failover(self, dag: DAGExecution) -> None:
        """Execute DAG with failover strategy"""
        # Try sequential first, fall back to parallel if needed
        try:
            self._execute_sequential(dag)
        except Exception as e:
            self.logger.warning(f"Sequential execution failed, trying parallel: {e}")
            # Reset node statuses
            for node in dag.nodes:
                if node.status == NodeStatus.FAILED:
                    node.status = NodeStatus.PENDING
                    node.error_message = ""
            
            self._execute_parallel(dag)
    
    def _execute_node(self, dag: DAGExecution, node: DAGNode) -> bool:
        """Execute individual DAG node"""
        self.logger.info(f"Executing node: {node.node_id}")
        
        node.status = NodeStatus.RUNNING
        node.timestamp = self._get_timestamp()
        
        try:
            # Prepare node parameters with data from dependencies
            prepared_params = self._prepare_node_parameters(dag, node)
            
            # Execute based on node type
            if node.node_type == "tool":
                result = self._execute_tool_node(node, prepared_params)
            elif node.node_type == "parser":
                result = self._execute_parser_node(node, prepared_params)
            elif node.node_type == "validator":
                result = self._execute_validator_node(node, prepared_params)
            else:
                raise ValueError(f"Unsupported node type: {node.node_type}")
            
            # Update node with result
            node.result = result
            node.status = NodeStatus.COMPLETED
            node.safety_validated = True
            
            self.logger.info(f"Node {node.node_id} completed successfully")
            return True
            
        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error_message = str(e)
            node.safety_validated = False
            
            self.logger.error(f"Node {node.node_id} failed: {e}")
            return False
    
    def _execute_tool_node(self, node: DAGNode, params: Dict[str, Any]) -> Any:
        """Execute tool node"""
        from ..l2_execution.execution_engines.tool_invocation import ExecutionMode
        
        tool_name = node.operation
        tool_params = params
        
        # Execute tool via tool engine
        execution = self.tool_engine.invoke_tool(tool_name, tool_params, ExecutionMode.SYNCHRONOUS)
        
        if execution.status != NodeStatus.SUCCESS:
            raise Exception(f"Tool execution failed: {execution.error_message}")
        
        return execution.result
    
    def _execute_parser_node(self, node: DAGNode, params: Dict[str, Any]) -> Any:
        """Execute parser node"""
        parser_type = node.operation
        parse_data = params.get("data", "")
        parse_mode = params.get("mode", "parse")
        
        from ..l2_execution.parsing_engines.text_parser import ParseMode as TextParseMode
        from ..l2_execution.parsing_engines.json_parser import ParseMode as JSONParseMode
        from ..l2_execution.parsing_engines.yaml_parser import ParseMode as YAMLParseMode
        
        if parser_type == "text":
            from ..l2_execution.parsing_engines.text_parser import ParseConstraints
            constraints = ParseConstraints()
            response = self.text_parser.parse(parse_data, TextParseMode(parse_mode), constraints)
        elif parser_type == "json":
            from ..l2_execution.parsing_engines.json_parser import ParseConstraints
            constraints = ParseConstraints()
            response = self.json_parser.parse(parse_data, JSONParseMode(parse_mode), constraints)
        elif parser_type == "yaml":
            from ..l2_execution.parsing_engines.yaml_parser import ParseConstraints
            constraints = ParseConstraints()
            response = self.yaml_parser.parse(parse_data, YAMLParseMode(parse_mode), constraints)
        else:
            raise ValueError(f"Unsupported parser type: {parser_type}")
        
        if not response.result:
            raise Exception(f"Parser execution failed: {response.error_message}")
        
        return response.result
    
    def _execute_validator_node(self, node: DAGNode, params: Dict[str, Any]) -> Any:
        """Execute validator node"""
        validation_data = params.get("data", {})
        validation_rules = params.get("rules", [])
        
        from ..l2_execution.execution_engines.validation import ValidationConstraints, ValidationRule, ValidationType
        
        # Convert rules to ValidationRule objects
        rules = []
        for rule_dict in validation_rules:
            rules.append(ValidationRule(
                rule_id=rule_dict.get("rule_id", ""),
                validation_type=ValidationType(rule_dict.get("validation_type", "type")),
                field_path=rule_dict.get("field_path", "$"),
                parameters=rule_dict.get("parameters", {}),
                error_message=rule_dict.get("error_message", ""),
                required=rule_dict.get("required", True)
            ))
        
        constraints = ValidationConstraints()
        report = self.validation_engine.validate(validation_data, rules, constraints)
        
        if report.overall_status.value != "valid":
            raise Exception(f"Validation failed: {report.results}")
        
        return report
    
    def _prepare_node_parameters(self, dag: DAGExecution, node: DAGNode) -> Dict[str, Any]:
        """Prepare node parameters with data from dependencies"""
        prepared_params = node.parameters.copy()
        
        # Find edges that provide data to this node
        for edge in dag.edges:
            if edge.target_node == node.node_id:
                source_node = self._find_node(dag, edge.source_node)
                if source_node and source_node.result:
                    # Map outputs to inputs
                    for output_key, input_key in edge.data_mapping.items():
                        if hasattr(source_node.result, output_key):
                            prepared_params[input_key] = getattr(source_node.result, output_key)
                        elif isinstance(source_node.result, dict) and output_key in source_node.result:
                            prepared_params[input_key] = source_node.result[output_key]
        
        return prepared_params
    
    def _build_execution_graph(self, nodes: List[DAGNode], edges: List[DAGEdge]) -> Dict[str, List[str]]:
        """Build execution graph from nodes and edges"""
        graph = defaultdict(list)
        
        for edge in edges:
            graph[edge.source_node].append(edge.target_node)
        
        return dict(graph)
    
    def _get_topological_order(self, dag: DAGExecution) -> List[str]:
        """Get topological order of nodes for execution"""
        # Build adjacency list and in-degree count
        in_degree = {node.node_id: 0 for node in dag.nodes}
        
        for edge in dag.edges:
            in_degree[edge.target_node] += 1
        
        # Queue for nodes with no dependencies
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Reduce in-degree for dependent nodes
            for neighbor in dag.execution_graph.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _get_execution_levels(self, dag: DAGExecution) -> List[List[str]]:
        """Get execution levels (nodes that can run in parallel)"""
        levels = []
        processed = set()
        
        while len(processed) < len(dag.nodes):
            current_level = []
            
            for node in dag.nodes:
                if node.node_id not in processed:
                    # Check if all dependencies are processed
                    deps_processed = all(dep in processed for dep in node.dependencies)
                    if deps_processed:
                        current_level.append(node.node_id)
            
            if not current_level:
                break  # Circular dependency or error
            
            levels.append(current_level)
            processed.update(current_level)
        
        return levels
    
    def _find_node(self, dag: DAGExecution, node_id: str) -> Optional[DAGNode]:
        """Find node by ID"""
        for node in dag.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def _validate_dag_structure(self, nodes: List[DAGNode], edges: List[DAGEdge], graph: Dict[str, List[str]], constraints: DAGConstraints) -> None:
        """Validate DAG structure"""
        # Check node count
        if len(nodes) > constraints.max_nodes:
            raise ValueError(f"Too many nodes: {len(nodes)} > {constraints.max_nodes}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(graph):
            raise ValueError("Circular dependencies detected in DAG")
        
        # Check DAG depth
        depth = self._calculate_dag_depth(nodes, graph)
        if depth > constraints.max_depth:
            raise ValueError(f"DAG too deep: {depth} > {constraints.max_depth}")
        
        # Validate node dependencies
        for node in nodes:
            for dep in node.dependencies:
                if not any(n.node_id == dep for n in nodes):
                    raise ValueError(f"Node {node.node_id} depends on non-existent node {dep}")
    
    def _has_circular_dependencies(self, graph: Dict[str, List[str]]) -> bool:
        """Check for circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def _calculate_dag_depth(self, nodes: List[DAGNode], graph: Dict[str, List[str]]) -> int:
        """Calculate maximum depth of DAG"""
        def get_depth(node_id, visited=None):
            if visited is None:
                visited = set()
            
            if node_id in visited:
                return float('inf')  # Circular dependency
            
            visited.add(node_id)
            
            neighbors = graph.get(node_id, [])
            if not neighbors:
                return 1
            
            max_depth = 0
            for neighbor in neighbors:
                depth = get_depth(neighbor, visited.copy())
                max_depth = max(max_depth, depth)
            
            return max_depth + 1
        
        return max(get_depth(node.node_id) for node in nodes)
    
    def validate_safety(self, dag: DAGExecution) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check execution count
            if len(self.active_executions) > self.constraints.max_nodes:
                self.logger.error("Too many active executions")
                return False
            
            # Validate node safety
            for node in dag.nodes:
                # Check node parameters for dangerous content
                for key, value in node.parameters.items():
                    if isinstance(value, str):
                        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
                        value_lower = value.lower()
                        for pattern in dangerous_patterns:
                            if pattern in value_lower:
                                self.logger.error(f"Dangerous pattern in node {node.node_id}: {pattern}")
                                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"DAG safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_dag_input(self, nodes: List[DAGNode], edges: List[DAGEdge]) -> None:
        """L5 DAG input validation"""
        if not isinstance(nodes, list):
            raise ValueError("Nodes must be a list")
        
        if not isinstance(edges, list):
            raise ValueError("Edges must be a list")
        
        if not nodes:
            raise ValueError("Nodes cannot be empty")
        
        for node in nodes:
            if not isinstance(node, DAGNode):
                raise ValueError("Each node must be a DAGNode object")
        
        for edge in edges:
            if not isinstance(edge, DAGEdge):
                raise ValueError("Each edge must be a DAGEdge object")
    
    def _validate_execution_input(self, dag: DAGExecution, mode: ExecutionMode) -> None:
        """L5 Execution input validation"""
        if not isinstance(dag, DAGExecution):
            raise ValueError("DAG must be a DAGExecution object")
        
        if not isinstance(mode, ExecutionMode):
            raise ValueError("Mode must be an ExecutionMode enum")
    
    def _generate_dag_id(self) -> str:
        """Generate unique DAG ID"""
        return f"dag_{uuid.uuid4().hex[:8]}"
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        return f"exec_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class DAGEngineInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, engine: DAGEngine):
        self._engine = engine
    
    def create_dag(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            # Convert dictionaries to DAG objects
            dag_nodes = []
            for node_dict in nodes:
                dag_nodes.append(DAGNode(
                    node_id=node_dict.get("node_id", ""),
                    node_type=node_dict.get("node_type", "tool"),
                    operation=node_dict.get("operation", ""),
                    parameters=node_dict.get("parameters", {}),
                    dependencies=node_dict.get("dependencies", []),
                    outputs=node_dict.get("outputs", [])
                ))
            
            dag_edges = []
            for edge_dict in edges:
                dag_edges.append(DAGEdge(
                    source_node=edge_dict.get("source_node", ""),
                    target_node=edge_dict.get("target_node", ""),
                    condition=edge_dict.get("condition", ""),
                    data_mapping=edge_dict.get("data_mapping", {})
                ))
            
            constraints = DAGConstraints()
            dag = self._engine.create_dag(dag_nodes, dag_edges, constraints)
            
            return {
                "success": True,
                "dag_id": dag.dag_id,
                "execution_id": dag.execution_id,
                "node_count": len(dag.nodes),
                "edge_count": len(dag.edges),
                "safety_validated": dag.safety_validated,
                "timestamp": dag.timestamp
            }
        except Exception as e:
            self.logger.error(f"DAG creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def execute_dag(self, execution_id: str, mode: str = "sequential") -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            execution_mode = ExecutionMode(mode)
            
            # Get DAG from active executions
            if execution_id not in self._engine.active_executions:
                return {
                    "success": False,
                    "error": "Execution ID not found",
                    "safety_validated": False
                }
            
            dag = self._engine.active_executions[execution_id]
            result = self._engine.execute_dag(dag, execution_mode)
            
            return {
                "success": result.status == NodeStatus.COMPLETED,
                "execution_id": result.execution_id,
                "dag_id": result.dag_id,
                "status": result.status.value,
                "execution_mode": result.execution_mode.value,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "node_statuses": {node.node_id: node.status.value for node in result.nodes},
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"DAG execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class DAGEngineFactory:
    """L5 Factory for creating DAG engine instances"""
    
    @staticmethod
    def create_engine(constraints: Optional[DAGConstraints] = None) -> DAGEngine:
        return DAGEngineImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[DAGConstraints] = None) -> DAGEngineInterface:
        engine = DAGEngineFactory.create_engine(constraints)
        return DAGEngineInterface(engine)

# L5 Export for module usage
__all__ = [
    "NodeStatus",
    "ExecutionMode",
    "DAGConstraints",
    "DAGNode",
    "DAGEdge",
    "DAGExecution",
    "DAGEngine",
    "DAGEngineImpl",
    "DAGEngineInterface",
    "DAGEngineFactory",
    "SecurityError"
]
