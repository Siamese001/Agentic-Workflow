"""
L5 Agentic Core - L1 Planning Layer - Signal Types
Implements L1 Cognitive Planning Layer for signal type definitions
"""

from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalCategory(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    USER_INPUT = "user_input"
    SYSTEM_EVENT = "system_event"
    FEEDBACK = "feedback"
    ERROR = "error"
    SAFETY = "safety"
    PERFORMANCE = "performance"

class SignalPriority(Enum):
    """L5 Signal priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5

@dataclass
class SignalConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_signal_size: int = 10000  # 10KB
    allowed_categories: List[SignalCategory] = field(default_factory=lambda: list(SignalCategory))
    requires_validation: bool = True
    safety_level: str = "strict"

@dataclass
class SignalType:
    """L5 Signal type structure with full type safety"""
    type_id: str
    category: SignalCategory
    priority: SignalPriority
    description: str
    schema: Dict[str, Any] = field(default_factory=dict)
    validation_rules: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class SignalInstance:
    """L5 Signal instance structure"""
    signal_id: str
    signal_type: SignalType
    data: Dict[str, Any]
    source: str
    confidence: float = 1.0
    processed: bool = False
    timestamp: str = ""

@dataclass
class SignalResult:
    """L5 Result structure with full type safety"""
    success: bool
    signals: List[SignalInstance] = field(default_factory=list)
    signal_types: List[SignalType] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

class SignalProcessor(ABC):
    """L5 Abstract base - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def define_signal_type(self, type_data: Dict[str, Any]) -> SignalType:
        """Define a signal type with L5 safety constraints"""
        pass
    
    @abstractmethod
    def create_signal(self, signal_data: Dict[str, Any]) -> SignalInstance:
        """Create a signal instance"""
        pass
    
    @abstractmethod
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class SignalTypesImpl(SignalProcessor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure signal type management with no side effects
    """
    
    def __init__(self, constraints: Optional[SignalConstraints] = None):
        self.constraints = constraints or SignalConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.signal_types: Dict[str, SignalType] = {}
        self.signals: Dict[str, SignalInstance] = {}
        self._initialize_default_types()
    
    def _initialize_default_types(self):
        """Initialize default signal types"""
        default_types = [
            SignalType(
                type_id="user_query",
                category=SignalCategory.USER_INPUT,
                priority=SignalPriority.HIGH,
                description="User query or request",
                schema={"query": "string", "context": "object"},
                validation_rules=["query_required", "no_code_injection"],
                safety_validated=True,
                timestamp=self._get_timestamp()
            ),
            SignalType(
                type_id="system_error",
                category=SignalCategory.ERROR,
                priority=SignalPriority.CRITICAL,
                description="System error event",
                schema={"error_code": "string", "message": "string", "stack_trace": "string"},
                validation_rules=["error_code_required"],
                safety_validated=True,
                timestamp=self._get_timestamp()
            ),
            SignalType(
                type_id="safety_violation",
                category=SignalCategory.SAFETY,
                priority=SignalPriority.CRITICAL,
                description="Safety policy violation",
                schema={"violation_type": "string", "severity": "string", "context": "object"},
                validation_rules=["violation_type_required", "severity_valid"],
                safety_validated=True,
                timestamp=self._get_timestamp()
            ),
            SignalType(
                type_id="performance_metric",
                category=SignalCategory.PERFORMANCE,
                priority=SignalPriority.LOW,
                description="Performance monitoring signal",
                schema={"metric_name": "string", "value": "number", "unit": "string"},
                validation_rules=["metric_name_required", "value_numeric"],
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
        ]
        
        for signal_type in default_types:
            self.signal_types[signal_type.type_id] = signal_type
    
    def define_signal_type(self, type_data: Dict[str, Any]) -> SignalType:
        """Define a signal type following L5 architecture principles"""
        self.logger.info(f"Defining signal type: {type_data}")
        
        # L5 Input validation
        self._validate_input(type_data)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(type_data):
            raise SecurityError("Signal type data failed L5 safety validation")
        
        # Create signal type with L5 structure
        signal_type = SignalType(
            type_id=type_data.get("type_id", self._generate_type_id()),
            category=SignalCategory(type_data.get("category", "user_input")),
            priority=SignalPriority(type_data.get("priority", 3)),
            description=type_data.get("description", ""),
            schema=type_data.get("schema", {}),
            validation_rules=type_data.get("validation_rules", []),
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        # Store signal type
        self.signal_types[signal_type.type_id] = signal_type
        
        self.logger.info(f"Successfully defined signal type: {signal_type.type_id}")
        return signal_type
    
    def create_signal(self, signal_data: Dict[str, Any]) -> SignalInstance:
        """Create a signal instance following L5 principles"""
        self.logger.info(f"Creating signal: {signal_data}")
        
        # L5 Input validation
        self._validate_input(signal_data)
        
        # Get signal type
        type_id = signal_data.get("type_id")
        if type_id not in self.signal_types:
            raise ValueError(f"Unknown signal type: {type_id}")
        
        signal_type = self.signal_types[type_id]
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(signal_data):
            raise SecurityError("Signal data failed L5 safety validation")
        
        # Validate signal data against schema
        self._validate_signal_data(signal_data, signal_type)
        
        # Create signal instance
        signal = SignalInstance(
            signal_id=signal_data.get("signal_id", self._generate_signal_id()),
            signal_type=signal_type,
            data=signal_data.get("data", {}),
            source=signal_data.get("source", "unknown"),
            confidence=signal_data.get("confidence", 1.0),
            processed=False,
            timestamp=self._get_timestamp()
        )
        
        # Store signal
        self.signals[signal.signal_id] = signal
        
        self.logger.info(f"Successfully created signal: {signal.signal_id}")
        return signal
    
    def get_signal_type(self, type_id: str) -> Optional[SignalType]:
        """Retrieve a signal type by ID"""
        return self.signal_types.get(type_id)
    
    def get_signal(self, signal_id: str) -> Optional[SignalInstance]:
        """Retrieve a signal by ID"""
        return self.signals.get(signal_id)
    
    def list_signal_types(self) -> List[SignalType]:
        """List all defined signal types"""
        return list(self.signal_types.values())
    
    def list_signals(self, category: Optional[SignalCategory] = None) -> List[SignalInstance]:
        """List signals, optionally filtered by category"""
        signals = list(self.signals.values())
        if category:
            signals = [s for s in signals if s.signal_type.category == category]
        return signals
    
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            data_str = str(data).lower()
            for pattern in dangerous_patterns:
                if pattern in data_str:
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check data size
            if len(str(data)) > self.constraints.max_signal_size:
                self.logger.error("Signal data exceeds size limit")
                return False
            
            self.logger.info("Signal data passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, data: Dict[str, Any]) -> None:
        """L5 Input validation"""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if not data:
            raise ValueError("Data cannot be empty")
    
    def _validate_signal_data(self, signal_data: Dict[str, Any], signal_type: SignalType) -> None:
        """Validate signal data against signal type schema"""
        data = signal_data.get("data", {})
        schema = signal_type.schema
        
        for field, field_type in schema.items():
            if field not in data:
                raise ValueError(f"Required field missing: {field}")
            
            # Basic type validation
            if field_type == "string" and not isinstance(data[field], str):
                raise ValueError(f"Field {field} must be string")
            elif field_type == "number" and not isinstance(data[field], (int, float)):
                raise ValueError(f"Field {field} must be number")
            elif field_type == "object" and not isinstance(data[field], dict):
                raise ValueError(f"Field {field} must be object")
    
    def _generate_type_id(self) -> str:
        """Generate unique signal type ID"""
        import uuid
        return f"type_{uuid.uuid4().hex[:8]}"
    
    def _generate_signal_id(self) -> str:
        """Generate unique signal ID"""
        import uuid
        return f"signal_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class SignalTypesInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, processor: SignalProcessor):
        self._processor = processor
    
    def create_signal_type(self, type_data: Dict[str, Any]) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            signal_type = self._processor.define_signal_type(type_data)
            return {
                "success": True,
                "type_id": signal_type.type_id,
                "category": signal_type.category.value,
                "priority": signal_type.priority.value,
                "description": signal_type.description,
                "safety_validated": signal_type.safety_validated,
                "timestamp": signal_type.timestamp
            }
        except Exception as e:
            self.logger.error(f"Signal type creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def create_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """L5 Interface method - creates signal safely"""
        try:
            signal = self._processor.create_signal(signal_data)
            return {
                "success": True,
                "signal_id": signal.signal_id,
                "type_id": signal.signal_type.type_id,
                "source": signal.source,
                "confidence": signal.confidence,
                "timestamp": signal.timestamp
            }
        except Exception as e:
            self.logger.error(f"Signal creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class SignalTypesFactory:
    """L5 Factory for creating signal type instances"""
    
    @staticmethod
    def create_processor(constraints: Optional[SignalConstraints] = None) -> SignalProcessor:
        return SignalTypesImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[SignalConstraints] = None) -> SignalTypesInterface:
        processor = SignalTypesFactory.create_processor(constraints)
        return SignalTypesInterface(processor)

# L5 Export for module usage
__all__ = [
    "SignalCategory",
    "SignalPriority",
    "SignalConstraints",
    "SignalType",
    "SignalInstance",
    "SignalResult",
    "SignalProcessor",
    "SignalTypesImpl",
    "SignalTypesInterface",
    "SignalTypesFactory",
    "SecurityError"
]
