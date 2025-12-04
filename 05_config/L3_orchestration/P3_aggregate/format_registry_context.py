"""
L5 Agentic Core - Plan Layer - format_registry_context
Implements L1 Cognitive Planning Layer for format registry context operations
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FormatRegistryContextPlanType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = "default"
    CORE = "core"
    SYSTEM = "system"

@dataclass
class FormatRegistryContextPlanConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_depth: int = 5
    allowed_operations: List[str] = field(default_factory=lambda: ["read", "validate", "filter"])
    safety_level: str = "strict"
    requires_approval: bool = True

@dataclass
class FormatRegistryContextPlanResult:
    """L5 Result structure with full type safety"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

class FormatRegistryContextPlanProcessor(ABC):
    """L5 Abstract base - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> FormatRegistryContextPlanResult:
        """Process data with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class FormatRegistryContextPlanImpl(FormatRegistryContextPlanProcessor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure planning functionality with no side effects
    """
    
    def __init__(self, constraints: Optional[FormatRegistryContextPlanConstraints] = None):
        self.constraints = constraints or FormatRegistryContextPlanConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process(self, input_data: Dict[str, Any]) -> FormatRegistryContextPlanResult:
        """Process input following L5 architecture principles"""
        self.logger.info(f"Processing {input_data}")
        
        # L5 Input validation
        self._validate_input(input_data)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(input_data):
            raise SecurityError("Input failed L5 safety validation")
        
        # Create result with L5 structure
        result = FormatRegistryContextPlanResult(
            success=True,
            data={"processed": True, "input": input_data},
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        self.logger.info(f"Successfully processed: {result.success}")
        return result
    
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            data_str = str(data).lower()
            for pattern in dangerous_patterns:
                if pattern in data_str:
                    self.logger.error(f" Dangerous pattern detected: {pattern}")
                    return False
            
            # Check data size
            if len(str(data)) > 1000000:  # 1MB limit
                self.logger.error("Data exceeds size limit")
                return False
            
            self.logger.info("Data passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """L5 Input validation"""
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")
        
        if not input_data:
            raise ValueError("Input cannot be empty")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class FormatRegistryContextPlanInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, processor: FormatRegistryContextPlanProcessor):
        self._processor = processor
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            result = self._processor.process(input_data)
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            raise SecurityError(f"Execution failed: {e}")

# L5 Factory
class FormatRegistryContextPlanFactory:
    """L5 Factory for creating processors with proper configuration"""
    
    @staticmethod
    def create_processor(safety_level: str = "strict") -> FormatRegistryContextPlanInterface:
        """Create configured processor"""
        constraints = FormatRegistryContextPlanConstraints(safety_level=safety_level)
        processor = FormatRegistryContextPlanImpl(constraints)
        return FormatRegistryContextPlanInterface(processor)

# L5 Main execution point
def format_registry_context(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    L5 Main function - format registry context operations
    
    Args:
        input_data: Input data to process
        
    Returns:
        Dict: Processed result
        
    Raises:
        SecurityError: If execution fails any safety check
    """
    factory = FormatRegistryContextPlanFactory()
    processor = factory.create_processor()
    return processor.execute(input_data)

if __name__ == "__main__":
    # L5 Test execution
    try:
        test_data = {"test": True}
        result = format_registry_context(test_data)
        logger.info(f"L5 Execution successful: {result}")
    except SecurityError as e:
        logger.error(f"L5 Security error: {e}")
    except Exception as e:
        logger.error(f"L5 Unexpected error: {e}")