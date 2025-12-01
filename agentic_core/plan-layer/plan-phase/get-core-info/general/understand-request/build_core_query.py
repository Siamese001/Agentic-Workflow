"""
L5 Agentic Core - Plan Layer - Build Core Query
Implements L1 Cognitive Planning Layer for core query construction
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """L5 Typed query enumeration for deterministic behavior"""
    CORE_REGISTRY = "core_registry"
    LAYER_PARAMETER = "layer_parameter"
    SYSTEM_STATE = "system_state"
    SAFETY_CHECK = "safety_check"

@dataclass
class QueryConstraints:
    """L5 Safety constraints for query construction - fail-closed behavior"""
    max_depth: int = 5
    allowed_operations: List[str] = field(default_factory=lambda: ["read", "validate", "filter"])
    safety_level: str = "strict"
    requires_approval: bool = True

@dataclass
class CoreQuery:
    """L5 Core query structure with full type safety"""
    query_type: QueryType
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: QueryConstraints = field(default_factory=QueryConstraints)
    context: Optional[Dict[str, Any]] = None
    safety_validated: bool = False

class QueryBuilder(ABC):
    """L5 Abstract base for query builders - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def build(self, query_type: QueryType, parameters: Dict[str, Any]) -> CoreQuery:
        """Build a core query with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, query: CoreQuery) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class CoreQueryBuilder(QueryBuilder):
    """
    L5 Core Query Builder - Implements L1 Cognitive Planning Layer
    Pure planning functionality with no side effects
    """
    
    def __init__(self, constraints: Optional[QueryConstraints] = None):
        self.constraints = constraints or QueryConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def build(self, query_type: QueryType, parameters: Dict[str, Any]) -> CoreQuery:
        """
        Build core query following L5 architecture principles
        
        Args:
            query_type: Type of query to build
            parameters: Query parameters
            
        Returns:
            CoreQuery: L5 structured query with safety validation
            
        Raises:
            ValueError: If parameters violate L5 constraints
        """
        self.logger.info(f"Building {query_type.value} query with parameters: {parameters}")
        
        # L5 Input validation
        self._validate_parameters(query_type, parameters)
        
        # Create query with L5 structure
        query = CoreQuery(
            query_type=query_type,
            parameters=parameters,
            constraints=self.constraints,
            context={"build_timestamp": self._get_timestamp()}
        )
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(query):
            raise SecurityError("Query failed L5 safety validation")
        
        query.safety_validated = True
        self.logger.info(f"Successfully built and validated {query_type.value} query")
        
        return query
    
    def validate_safety(self, query: CoreQuery) -> bool:
        """
        L5 Safety validation with fail-closed behavior
        
        Args:
            query: Query to validate
            
        Returns:
            bool: True if safe, False otherwise (fail-closed)
        """
        try:
            # Check query depth
            if self._calculate_depth(query.parameters) > self.constraints.max_depth:
                self.logger.error("Query exceeds maximum depth")
                return False
            
            # Validate allowed operations
            if not self._validate_operations(query.parameters):
                self.logger.error("Query contains disallowed operations")
                return False
            
            # Check for injection patterns
            if self._contains_injection_patterns(query.parameters):
                self.logger.error("Query contains potential injection patterns")
                return False
            
            self.logger.info("Query passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed behavior
    
    def _validate_parameters(self, query_type: QueryType, parameters: Dict[str, Any]) -> None:
        """L5 Parameter validation"""
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a dictionary")
        
        if not parameters:
            raise ValueError("Parameters cannot be empty")
        
        # Query type specific validation
        if query_type == QueryType.CORE_REGISTRY:
            required_keys = ["registry_type", "query_scope"]
            for key in required_keys:
                if key not in parameters:
                    raise ValueError(f"Missing required parameter: {key}")
    
    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate nesting depth for L5 validation"""
        if isinstance(obj, dict):
            return max([self._calculate_depth(v, current_depth + 1) for v in obj.values()], default=current_depth)
        elif isinstance(obj, list):
            return max([self._calculate_depth(item, current_depth + 1) for item in obj], default=current_depth)
        else:
            return current_depth
    
    def _validate_operations(self, parameters: Dict[str, Any]) -> bool:
        """Validate operations against L5 allowed list"""
        param_str = str(parameters).lower()
        for op in self.constraints.allowed_operations:
            if op in param_str:
                return True
        return False
    
    def _contains_injection_patterns(self, parameters: Dict[str, Any]) -> bool:
        """L5 Injection pattern detection"""
        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
        param_str = str(parameters).lower()
        return any(pattern in param_str for pattern in dangerous_patterns)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class CoreQueryBuilderInterface:
    """L5 Interface for core query builder - ensures contract compliance"""
    
    def __init__(self, builder: QueryBuilder):
        self._builder = builder
    
    def build_safe_query(self, query_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        L5 Interface method - builds and validates query safely
        
        Args:
            query_type: String representation of query type
            parameters: Query parameters
            
        Returns:
            Dict: Serializable query result
            
        Raises:
            SecurityError: If query fails safety validation
        """
        try:
            query_enum = QueryType(query_type.lower())
            query = self._builder.build(query_enum, parameters)
            return {
                "query_type": query.query_type.value,
                "parameters": query.parameters,
                "safety_validated": query.safety_validated,
                "context": query.context
            }
        except ValueError as e:
            raise SecurityError(f"Invalid query type: {e}")
        except Exception as e:
            raise SecurityError(f"Query building failed: {e}")

# L5 Factory for dependency injection
class CoreQueryBuilderFactory:
    """L5 Factory for creating query builders with proper configuration"""
    
    @staticmethod
    def create_builder(safety_level: str = "strict") -> CoreQueryBuilderInterface:
        """Create configured query builder"""
        constraints = QueryConstraints(safety_level=safety_level)
        builder = CoreQueryBuilder(constraints)
        return CoreQueryBuilderInterface(builder)

# L5 Main execution point
def build_core_query(query_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    L5 Main function - builds core query with full safety validation
    
    Args:
        query_type: Type of query to build
        parameters: Query parameters
        
    Returns:
        Dict: Validated query structure
        
    Raises:
        SecurityError: If query fails any validation
    """
    factory = CoreQueryBuilderFactory()
    builder = factory.create_builder()
    return builder.build_safe_query(query_type, parameters)

if __name__ == "__main__":
    # L5 Test execution
    try:
        test_params = {
            "registry_type": "core",
            "query_scope": "system",
            "filters": {"active": True}
        }
        result = build_core_query("core_registry", test_params)
        logger.info(f"L5 Query build successful: {result}")
    except SecurityError as e:
        logger.error(f"L5 Security error: {e}")
    except Exception as e:
        logger.error(f"L5 Unexpected error: {e}")