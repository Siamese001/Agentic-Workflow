"""
L1 Cognitive Planning - Core Query Building

Implements pure planning operations for building core registry queries
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, ValidationError


# ============================================================================
# L5 SAFETY & LOGGING INFRASTRUCTURE
# ============================================================================

class QueryType(str, Enum):
    """Supported core query types with L5 safety validation"""
    REGISTRY_LOOKUP = "registry_lookup"
    LAYER_DISCOVERY = "layer_discovery"
    INTERFACE_QUERY = "interface_query"
    CAPABILITY_SCAN = "capability_scan"
    STATE_INSPECTION = "state_inspection"


class QueryPurpose(str, Enum):
    """Query purpose types with L5 safety enforcement"""
    DISCOVERY = "discovery"
    VALIDATION = "validation"
    COORDINATION = "coordination"
    MONITORING = "monitoring"
    DEBUGGING = "debugging"


class CoreQuerySafetyPolicy(BaseModel):
    """L5 Safety policy for core query building operations"""
    max_query_depth: int = Field(default=10, description="Maximum query nesting depth")
    max_result_items: int = Field(default=1000, description="Maximum result items per query")
    allowed_query_types: List[str] = Field(default_factory=lambda: [t.value for t in QueryType])
    require_context_validation: bool = Field(default=True)
    prevent_injection: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class CoreQuerySafetyValidator:
    """L5 Safety validator for core query building operations"""
    
    def __init__(self, policy: CoreQuerySafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.CoreQuerySafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = ["drop", "delete", "truncate", "exec", "eval"]
        self._max_query_length = 2048  # Maximum query string length
    
    def validate_query_input(self, query_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates query input against L5 safety policies"""
        try:
            # Check query depth
            query_depth = query_input.get("depth", 0)
            if query_depth > self.policy.max_query_depth:
                error_msg = f"Query too deep: {query_depth} > {self.policy.max_query_depth}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check query type
            query_type = query_input.get("query_type", "")
            if query_type not in self.policy.allowed_query_types:
                error_msg = f"Prohibited query type: {query_type}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            query_string = str(query_input.get("query", "")).lower()
            for pattern in self._dangerous_patterns:
                if pattern in query_string:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check query length
            if len(query_string) > self._max_query_length:
                error_msg = f"Query too long: {len(query_string)} > {self._max_query_length}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Validate context if required
            if self.policy.require_context_validation:
                context = query_input.get("context", {})
                if not isinstance(context, dict):
                    error_msg = "Invalid context: must be dictionary"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class CoreQueryRequest:
    """Input request for core query building operations"""
    query_intent: str
    target_layer: str
    query_type: QueryType
    purpose: QueryPurpose
    context: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None
    query_options: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class CoreQueryResult:
    """Output result from core query building operations"""
    built_query: str
    query_parameters: Dict[str, Any]
    execution_plan: Dict[str, Any]
    safety_metadata: Dict[str, Any]
    estimated_complexity: str
    query_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class CoreQueryBuilderInterface(ABC):
    """Abstract interface for core query building operations"""
    
    @abstractmethod
    async def build_query(self, request: CoreQueryRequest) -> CoreQueryResult:
        """Build a core registry query based on the request"""
        pass
    
    @abstractmethod
    async def validate_query_structure(self, query: str) -> tuple[bool, Optional[str]]:
        """Validate the structure of a built query"""
        pass
    
    @abstractmethod
    async def estimate_query_complexity(self, query: str, context: Dict[str, Any]) -> str:
        """Estimate the complexity of executing the query"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class CoreQueryBuilder(CoreQueryBuilderInterface):
    """
    L1 Cognitive Planning implementation for building core registry queries.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[CoreQuerySafetyPolicy] = None):
        self.safety_policy = safety_policy or CoreQuerySafetyPolicy()
        self.safety_validator = CoreQuerySafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Query building templates and patterns
        self._query_templates = {
            QueryType.REGISTRY_LOOKUP: "SELECT * FROM registry WHERE layer = '{target}' AND type = '{query_type}'",
            QueryType.LAYER_DISCOVERY: "DISCOVER LAYERS WHERE capabilities CONTAINS '{capability}'",
            QueryType.INTERFACE_QUERY: "QUERY INTERFACES FOR '{target}' WITH METHOD '{method}'",
            QueryType.CAPABILITY_SCAN: "SCAN CAPABILITIES IN LAYER '{layer}' FILTER BY {filters}",
            QueryType.STATE_INSPECTION: "INSPECT STATE OF '{target}' WITH CONTEXT {context}"
        }
        
        self.logger.info("CoreQueryBuilder initialized with L5 safety policies")
    
    async def build_query(self, request: CoreQueryRequest) -> CoreQueryResult:
        """
        Build a core registry query based on the request parameters.
        
        Args:
            request: Core query building request with all necessary parameters
            
        Returns:
            CoreQueryResult: Structured result with built query and metadata
            
        Raises:
            ValidationError: If request parameters are invalid
            SafetyError: If query violates safety policies
        """
        self.logger.info(f"Building core query for {request.query_type} on {request.target_layer}")
        
        try:
            # L5 Safety validation
            query_input = {
                "query_type": request.query_type.value,
                "depth": request.query_options.get("depth", 1),
                "query": request.query_intent,
                "context": request.context
            }
            
            is_valid, error_msg = self.safety_validator.validate_query_input(query_input)
            if not is_valid:
                raise SafetyError(f"Query validation failed: {error_msg}")
            
            # Build query based on type and intent
            template = self._query_templates.get(request.query_type)
            if not template:
                raise ValidationError(f"Unsupported query type: {request.query_type}")
            
            # Substitute parameters in template
            built_query = self._substitute_query_parameters(
                template, 
                request.target_layer, 
                request.query_intent,
                request.query_options
            )
            
            # Validate query structure
            structure_valid, structure_error = await self.validate_query_structure(built_query)
            if not structure_valid:
                raise ValidationError(f"Invalid query structure: {structure_error}")
            
            # Estimate complexity
            complexity = await self.estimate_query_complexity(built_query, request.context)
            
            # Generate execution plan
            execution_plan = self._generate_execution_plan(request, built_query)
            
            # Generate safety metadata
            safety_metadata = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_risk_score(built_query, request),
                "constraints_applied": request.constraints or {}
            }
            
            # Generate unique query ID
            query_id = self._generate_query_id(request)
            
            result = CoreQueryResult(
                built_query=built_query,
                query_parameters={
                    "target_layer": request.target_layer,
                    "query_type": request.query_type.value,
                    "purpose": request.purpose.value,
                    "options": request.query_options
                },
                execution_plan=execution_plan,
                safety_metadata=safety_metadata,
                estimated_complexity=complexity,
                query_id=query_id
            )
            
            self.logger.info(f"Successfully built query {query_id} with complexity {complexity}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to build core query: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback query in non-fail-closed mode
            return self._create_fallback_query(request, str(e))
    
    async def validate_query_structure(self, query: str) -> tuple[bool, Optional[str]]:
        """Validate the structure of a built query"""
        try:
            if not query or not query.strip():
                return False, "Query is empty"
            
            # Check for balanced parentheses/brackets
            if query.count('(') != query.count(')'):
                return False, "Unbalanced parentheses"
            
            if query.count('{') != query.count('}'):
                return False, "Unbalanced braces"
            
            # Check for proper query termination
            if not query.rstrip().endswith(';') and not query.rstrip().endswith(')'):
                return False, "Query not properly terminated"
            
            # Additional structural checks based on query type
            if "SELECT" in query.upper():
                if "FROM" not in query.upper():
                    return False, "SELECT query missing FROM clause"
            
            return True, None
            
        except Exception as e:
            return False, f"Structure validation error: {str(e)}"
    
    async def estimate_query_complexity(self, query: str, context: Dict[str, Any]) -> str:
        """Estimate the complexity of executing the query"""
        try:
            complexity_score = 0
            
            # Base complexity from query length
            complexity_score += len(query) // 100
            
            # Complexity from query type
            if "JOIN" in query.upper():
                complexity_score += 3
            if "SUBQUERY" in query.upper() or "EXISTS" in query.upper():
                complexity_score += 2
            if "AGGREGATE" in query.upper() or "GROUP BY" in query.upper():
                complexity_score += 2
            
            # Complexity from context size
            context_size = len(str(context))
            complexity_score += context_size // 500
            
            # Map score to complexity level
            if complexity_score <= 3:
                return "low"
            elif complexity_score <= 7:
                return "medium"
            else:
                return "high"
                
        except Exception as e:
            self.logger.warning(f"Complexity estimation failed: {str(e)}")
            return "medium"  # Safe default
    
    def _substitute_query_parameters(
        self, 
        template: str, 
        target_layer: str, 
        query_intent: str,
        options: Dict[str, Any]
    ) -> str:
        """Substitute parameters into query template"""
        try:
            substitutions = {
                "{target}": target_layer,
                "{query_type}": query_intent,
                "{capability}": options.get("capability", ""),
                "{method}": options.get("method", ""),
                "{layer}": target_layer,
                "{filters}": str(options.get("filters", {})),
                "{context}": str(options.get("context", {}))
            }
            
            result = template
            for placeholder, value in substitutions.items():
                result = result.replace(placeholder, str(value))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Parameter substitution failed: {str(e)}")
            raise
    
    def _generate_execution_plan(self, request: CoreQueryRequest, query: str) -> Dict[str, Any]:
        """Generate execution plan for the built query"""
        return {
            "query": query,
            "target_layer": request.target_layer,
            "execution_order": [
                "validate_permissions",
                "establish_connection", 
                "execute_query",
                "process_results",
                "cleanup_resources"
            ],
            "estimated_duration_ms": len(query) * 2,  # Rough estimate
            "required_resources": ["connection_pool", "query_parser", "result_processor"],
            "fallback_strategy": "cached_result_if_available"
        }
    
    def _calculate_risk_score(self, query: str, request: CoreQueryRequest) -> float:
        """Calculate risk score for the query (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for complex queries
        if len(query) > 500:
            risk_score += 0.2
        
        # Increase risk for certain query types
        if request.query_type in [QueryType.STATE_INSPECTION, QueryType.CAPABILITY_SCAN]:
            risk_score += 0.1
        
        # Increase risk for deep queries
        depth = request.query_options.get("depth", 1)
        if depth > 5:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_query_id(self, request: CoreQueryRequest) -> str:
        """Generate unique query identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.query_type.value}:{request.target_layer}:{timestamp}"
        return f"query_{hash(content) % 1000000:06d}"
    
    def _create_fallback_query(self, request: CoreQueryRequest, error: str) -> CoreQueryResult:
        """Create safe fallback query when main building fails"""
        fallback_query = f"SELECT * FROM registry WHERE layer = '{request.target_layer}' LIMIT 10;"
        
        return CoreQueryResult(
            built_query=fallback_query,
            query_parameters={"fallback": True, "error": error},
            execution_plan={"fallback": True},
            safety_metadata={"fallback_mode": True},
            estimated_complexity="low",
            query_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when query violates safety policies"""
    
    def __init__(self, message: str, policy_violation: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.policy_violation = policy_violation
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.policy_violation:
            return f"[SAFETY_VIOLATION: {self.policy_violation}] {base_msg}"
        return f"[SAFETY_ERROR] {base_msg}"


class QueryBuilderError(Exception):
    """Raised for general query building errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, operation: Optional[str] = None, query_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or "QUERY_BUILDER_ERROR"
        self.operation = operation
        self.query_type = query_type
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        op_info = f" in {self.operation}" if self.operation else ""
        type_info = f" for {self.query_type}" if self.query_type else ""
        return f"[{self.error_code}]{op_info}{type_info} {base_msg}"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_core_query_builder(safety_policy: Optional[CoreQuerySafetyPolicy] = None) -> CoreQueryBuilder:
    """Factory function to create CoreQueryBuilder with optional custom safety policy"""
    return CoreQueryBuilder(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_query_request(request: CoreQueryRequest) -> tuple[bool, Optional[str]]:
    """Validate core query request parameters"""
    try:
        if not request.query_intent or not request.query_intent.strip():
            return False, "Query intent cannot be empty"
        
        if not request.target_layer or not request.target_layer.strip():
            return False, "Target layer cannot be empty"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"