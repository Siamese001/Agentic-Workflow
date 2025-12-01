"""
L1 Cognitive Planning - Registry Intent Parsing

Implements pure planning operations for parsing registry intent and extracting
layer parameters with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, ValidationError


# ============================================================================
# L5 SAFETY & LOGGING INFRASTRUCTURE
# ============================================================================

class IntentType(str, Enum):
    """Supported registry intent types with L5 safety validation"""
    DISCOVERY = "discovery"
    COORDINATION = "coordination"
    VALIDATION = "validation"
    MONITORING = "monitoring"
    CONFIGURATION = "configuration"
    EXECUTION = "execution"


class ActionType(str, Enum):
    """Action types extracted from registry intent with L5 safety enforcement"""
    QUERY = "query"
    UPDATE = "update"
    CREATE = "create"
    DELETE = "delete"
    INSPECT = "inspect"
    ORCHESTRATE = "orchestrate"


class RegistryIntentSafetyPolicy(BaseModel):
    """L5 Safety policy for registry intent parsing operations"""
    max_intent_length: int = Field(default=1024, description="Maximum intent string length")
    allowed_intent_types: List[str] = Field(default_factory=lambda: [t.value for t in IntentType])
    allowed_action_types: List[str] = Field(default_factory=lambda: [t.value for t in ActionType])
    require_semantic_validation: bool = Field(default=True)
    prevent_malicious_patterns: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class RegistryIntentSafetyValidator:
    """L5 Safety validator for registry intent parsing operations"""
    
    def __init__(self, policy: RegistryIntentSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.RegistryIntentSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._malicious_patterns = [
            r"drop\s+table", r"delete\s+from", r"truncate\s+table",
            r"exec\s*\(", r"eval\s*\(", r"system\s*\(",
            r"<script", r"javascript:", r"data:text/html"
        ]
        self._suspicious_keywords = ["hack", "exploit", "bypass", "override", "escalate"]
    
    def validate_intent_input(self, intent_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates intent input against L5 safety policies"""
        try:
            # Check intent length
            intent_string = intent_input.get("intent", "")
            if len(intent_string) > self.policy.max_intent_length:
                error_msg = f"Intent too long: {len(intent_string)} > {self.policy.max_intent_length}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for malicious patterns
            intent_lower = intent_string.lower()
            for pattern in self._malicious_patterns:
                if re.search(pattern, intent_lower, re.IGNORECASE):
                    error_msg = f"Malicious pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for suspicious keywords
            for keyword in self._suspicious_keywords:
                if keyword in intent_lower:
                    error_msg = f"Suspicious keyword detected: {keyword}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Validate intent type if provided
            intent_type = intent_input.get("intent_type", "")
            if intent_type and intent_type not in self.policy.allowed_intent_types:
                error_msg = f"Prohibited intent type: {intent_type}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Validate action type if provided
            action_type = intent_input.get("action_type", "")
            if action_type and action_type not in self.policy.allowed_action_types:
                error_msg = f"Prohibited action type: {action_type}"
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
class RegistryIntentRequest:
    """Input request for registry intent parsing operations"""
    intent: str
    context: Dict[str, Any]
    source_layer: str
    target_layers: Optional[List[str]] = None
    parsing_options: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class ParsedIntent:
    """Structured representation of parsed registry intent"""
    intent_type: IntentType
    action_type: ActionType
    primary_target: str
    secondary_targets: List[str]
    parameters: Dict[str, Any]
    constraints: Dict[str, Any]
    confidence_score: float
    metadata: Dict[str, Any]


@dataclass
class LayerParameters:
    """Extracted layer parameters from registry intent"""
    layer_name: str
    required_capabilities: List[str]
    interface_methods: List[str]
    state_requirements: Dict[str, Any]
    execution_constraints: Dict[str, Any]
    safety_requirements: Dict[str, Any]


@dataclass
class RegistryIntentResult:
    """Output result from registry intent parsing operations"""
    parsed_intent: ParsedIntent
    layer_parameters: List[LayerParameters]
    parsing_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    intent_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class RegistryIntentParserInterface(ABC):
    """Abstract interface for registry intent parsing operations"""
    
    @abstractmethod
    async def parse_intent(self, request: RegistryIntentRequest) -> RegistryIntentResult:
        """Parse registry intent and extract structured information"""
        pass
    
    @abstractmethod
    async def extract_layer_parameters(self, parsed_intent: ParsedIntent) -> List[LayerParameters]:
        """Extract layer-specific parameters from parsed intent"""
        pass
    
    @abstractmethod
    async def validate_intent_semantics(self, intent: str, context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate semantic correctness of registry intent"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class RegistryIntentParser(RegistryIntentParserInterface):
    """
    L1 Cognitive Planning implementation for parsing registry intent.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[RegistryIntentSafetyPolicy] = None):
        self.safety_policy = safety_policy or RegistryIntentSafetyPolicy()
        self.safety_validator = RegistryIntentSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Intent parsing patterns and keywords
        self._intent_patterns = {
            IntentType.DISCOVERY: [
                r"find\s+(\w+)", r"discover\s+(\w+)", r"locate\s+(\w+)",
                r"search\s+for\s+(\w+)", r"identify\s+(\w+)"
            ],
            IntentType.COORDINATION: [
                r"coordinate\s+(?:with|between)\s+(\w+)", r"orchestrate\s+(\w+)",
                r"synchronize\s+(\w+)", r"manage\s+(\w+)"
            ],
            IntentType.VALIDATION: [
                r"validate\s+(\w+)", r"verify\s+(\w+)", r"check\s+(\w+)",
                r"confirm\s+(\w+)", r"ensure\s+(\w+)"
            ],
            IntentType.MONITORING: [
                r"monitor\s+(\w+)", r"track\s+(\w+)", r"observe\s+(\w+)",
                r"watch\s+(\w+)", r"measure\s+(\w+)"
            ],
            IntentType.CONFIGURATION: [
                r"configure\s+(\w+)", r"setup\s+(\w+)", r"adjust\s+(\w+)",
                r"modify\s+(\w+)", r"tune\s+(\w+)"
            ],
            IntentType.EXECUTION: [
                r"execute\s+(\w+)", r"run\s+(\w+)", r"perform\s+(\w+)",
                r"process\s+(\w+)", r"handle\s+(\w+)"
            ]
        }
        
        self._action_patterns = {
            ActionType.QUERY: [r"query", r"get", r"fetch", r"retrieve", r"select"],
            ActionType.UPDATE: [r"update", r"modify", r"change", r"alter", r"edit"],
            ActionType.CREATE: [r"create", r"add", r"insert", r"new", r"generate"],
            ActionType.DELETE: [r"delete", r"remove", r"drop", r"clear", r"destroy"],
            ActionType.INSPECT: [r"inspect", r"examine", r"analyze", r"review", r"audit"],
            ActionType.ORCHESTRATE: [r"orchestrate", r"coordinate", r"manage", r"direct", r"control"]
        }
        
        self.logger.info("RegistryIntentParser initialized with L5 safety policies")
    
    async def parse_intent(self, request: RegistryIntentRequest) -> RegistryIntentResult:
        """
        Parse registry intent and extract structured information.
        
        Args:
            request: Registry intent parsing request with intent string and context
            
        Returns:
            RegistryIntentResult: Structured result with parsed intent and layer parameters
            
        Raises:
            ValidationError: If intent parameters are invalid
            SafetyError: If intent violates safety policies
        """
        self.logger.info(f"Parsing registry intent from {request.source_layer}")
        
        try:
            # L5 Safety validation
            intent_input = {
                "intent": request.intent,
                "intent_type": request.parsing_options.get("expected_type"),
                "action_type": request.parsing_options.get("expected_action")
            }
            
            is_valid, error_msg = self.safety_validator.validate_intent_input(intent_input)
            if not is_valid:
                raise SafetyError(f"Intent validation failed: {error_msg}")
            
            # Validate intent semantics
            semantic_valid, semantic_error = await self.validate_intent_semantics(
                request.intent, request.context
            )
            if not semantic_valid:
                raise ValidationError(f"Semantic validation failed: {semantic_error}")
            
            # Parse intent type and action
            intent_type = await self._extract_intent_type(request.intent)
            action_type = await self._extract_action_type(request.intent)
            
            # Extract targets and parameters
            primary_target, secondary_targets = await self._extract_targets(request.intent)
            parameters = await self._extract_parameters(request.intent, request.context)
            constraints = await self._extract_constraints(request.intent, request.parsing_options)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                request.intent, intent_type, action_type, parameters
            )
            
            # Create parsed intent
            parsed_intent = ParsedIntent(
                intent_type=intent_type,
                action_type=action_type,
                primary_target=primary_target,
                secondary_targets=secondary_targets,
                parameters=parameters,
                constraints=constraints,
                confidence_score=confidence_score,
                metadata={
                    "source_layer": request.source_layer,
                    "target_layers": request.target_layers or [],
                    "parsing_options": request.parsing_options
                }
            )
            
            # Extract layer parameters
            layer_parameters = await self.extract_layer_parameters(parsed_intent)
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_intent_risk_score(request.intent, parsed_intent),
                "constraints_applied": constraints
            }
            
            # Generate unique intent ID
            intent_id = self._generate_intent_id(request, parsed_intent)
            
            result = RegistryIntentResult(
                parsed_intent=parsed_intent,
                layer_parameters=layer_parameters,
                parsing_metadata={
                    "parsing_duration_ms": len(request.intent) * 0.5,  # Rough estimate
                    "patterns_matched": len(self._get_matched_patterns(request.intent)),
                    "complexity_estimate": await self._estimate_parsing_complexity(request.intent)
                },
                safety_validation=safety_validation,
                intent_id=intent_id
            )
            
            self.logger.info(f"Successfully parsed intent {intent_id} with confidence {confidence_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to parse registry intent: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback parsing in non-fail-closed mode
            return self._create_fallback_parsing(request, str(e))
    
    async def extract_layer_parameters(self, parsed_intent: ParsedIntent) -> List[LayerParameters]:
        """Extract layer-specific parameters from parsed intent"""
        try:
            layer_parameters = []
            
            # Extract parameters for primary target layer
            primary_params = await self._extract_parameters_for_layer(
                parsed_intent.primary_target, parsed_intent
            )
            layer_parameters.append(primary_params)
            
            # Extract parameters for secondary target layers
            for target in parsed_intent.secondary_targets:
                secondary_params = await self._extract_parameters_for_layer(target, parsed_intent)
                layer_parameters.append(secondary_params)
            
            return layer_parameters
            
        except Exception as e:
            self.logger.error(f"Failed to extract layer parameters: {str(e)}")
            # Return minimal safe parameters
            return [LayerParameters(
                layer_name=parsed_intent.primary_target,
                required_capabilities=["basic_query"],
                interface_methods=["get_info"],
                state_requirements={},
                execution_constraints={"read_only": True},
                safety_requirements={"validate_input": True}
            )]
    
    async def validate_intent_semantics(self, intent: str, context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate semantic correctness of registry intent"""
        try:
            # Check if intent has meaningful content
            if not intent or len(intent.strip()) < 3:
                return False, "Intent too short to be meaningful"
            
            # Check if intent contains recognizable action/target patterns
            has_action = any(
                action in intent.lower() 
                for actions in self._action_patterns.values() 
                for action in actions
            )
            
            if not has_action:
                return False, "Intent lacks recognizable action pattern"
            
            # Check if intent has target specification
            words = intent.lower().split()
            if len(words) < 2:
                return False, "Intent lacks target specification"
            
            # Validate context relevance
            if context and not isinstance(context, dict):
                return False, "Invalid context format"
            
            return True, None
            
        except Exception as e:
            return False, f"Semantic validation error: {str(e)}"
    
    async def _extract_intent_type(self, intent: str) -> IntentType:
        """Extract intent type from intent string"""
        intent_lower = intent.lower()
        
        for intent_type, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, intent_lower):
                    return intent_type
        
        # Default to discovery if no specific type found
        return IntentType.DISCOVERY
    
    async def _extract_action_type(self, intent: str) -> ActionType:
        """Extract action type from intent string"""
        intent_lower = intent.lower()
        
        for action_type, keywords in self._action_patterns.items():
            for keyword in keywords:
                if keyword in intent_lower:
                    return action_type
        
        # Default to query if no specific action found
        return ActionType.QUERY
    
    async def _extract_targets(self, intent: str) -> Tuple[str, List[str]]:
        """Extract primary and secondary targets from intent"""
        try:
            # Simple target extraction - look for nouns after action keywords
            words = intent.split()
            targets = []
            
            # Find potential targets (simplified heuristic)
            for i, word in enumerate(words):
                if (word.lower() in ["layer", "component", "module", "service", "system"] and 
                    i + 1 < len(words)):
                    potential_target = words[i + 1].strip(".,!?")
                    if potential_target and potential_target not in targets:
                        targets.append(potential_target)
            
            if targets:
                return targets[0], targets[1:]
            else:
                # Fallback: use last word as primary target
                last_word = words[-1].strip(".,!?") if words else "unknown"
                return last_word, []
                
        except Exception as e:
            self.logger.warning(f"Target extraction failed: {str(e)}")
            return "unknown", []
    
    async def _extract_parameters(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from intent and context"""
        parameters = {}
        
        # Extract numeric parameters
        numbers = re.findall(r'\b\d+\b', intent)
        if numbers:
            parameters["numeric_values"] = [int(n) for n in numbers]
        
        # Extract quoted parameters
        quoted = re.findall(r'"([^"]*)"', intent)
        if quoted:
            parameters["string_values"] = quoted
        
        # Merge context parameters
        if context:
            parameters.update(context.get("parameters", {}))
        
        return parameters
    
    async def _extract_constraints(self, intent: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract constraints from intent and options"""
        constraints = {}
        
        # Extract constraint keywords
        constraint_keywords = ["limit", "max", "min", "timeout", "priority"]
        intent_lower = intent.lower()
        
        for keyword in constraint_keywords:
            pattern = rf"{keyword}\s+(\w+)"
            match = re.search(pattern, intent_lower)
            if match:
                constraints[keyword] = match.group(1)
        
        # Add option constraints
        constraints.update(options.get("constraints", {}))
        
        return constraints
    
    async def _calculate_confidence_score(
        self, 
        intent: str, 
        intent_type: IntentType, 
        action_type: ActionType, 
        parameters: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for parsed intent"""
        try:
            score = 0.5  # Base score
            
            # Increase score for clear intent type
            if intent_type != IntentType.DISCOVERY:
                score += 0.1
            
            # Increase score for clear action type
            if action_type != ActionType.QUERY:
                score += 0.1
            
            # Increase score for extracted parameters
            if parameters:
                score += 0.2
            
            # Increase score for intent length (longer = more specific)
            if len(intent) > 10:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Confidence scoring failed: {str(e)}")
            return 0.5  # Safe default
    
    async def _extract_parameters_for_layer(self, layer_name: str, parsed_intent: ParsedIntent) -> LayerParameters:
        """Extract parameters specific to a layer"""
        return LayerParameters(
            layer_name=layer_name,
            required_capabilities=[parsed_intent.action_type.value],
            interface_methods=[f"handle_{parsed_intent.action_type.value}"],
            state_requirements=parsed_intent.parameters.get("state", {}),
            execution_constraints=parsed_intent.constraints,
            safety_requirements={
                "validate_input": True,
                "log_operations": True,
                "enforce_permissions": True
            }
        )
    
    def _get_matched_patterns(self, intent: str) -> List[str]:
        """Get list of patterns that matched the intent"""
        matched = []
        intent_lower = intent.lower()
        
        for intent_type, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, intent_lower):
                    matched.append(f"{intent_type.value}:{pattern}")
        
        return matched
    
    async def _estimate_parsing_complexity(self, intent: str) -> str:
        """Estimate parsing complexity"""
        complexity_score = len(intent) // 50
        
        if complexity_score <= 2:
            return "low"
        elif complexity_score <= 5:
            return "medium"
        else:
            return "high"
    
    def _calculate_intent_risk_score(self, intent: str, parsed_intent: ParsedIntent) -> float:
        """Calculate risk score for the intent (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for certain action types
        if parsed_intent.action_type in [ActionType.DELETE, ActionType.UPDATE]:
            risk_score += 0.3
        
        # Increase risk for complex intents
        if len(intent) > 100:
            risk_score += 0.2
        
        # Increase risk for multiple targets
        if len(parsed_intent.secondary_targets) > 2:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _generate_intent_id(self, request: RegistryIntentRequest, parsed_intent: ParsedIntent) -> str:
        """Generate unique intent identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{parsed_intent.intent_type.value}:{parsed_intent.action_type.value}:{request.intent[:50]}:{timestamp}"
        return f"intent_{hash(content) % 1000000:06d}"
    
    def _create_fallback_parsing(self, request: RegistryIntentRequest, error: str) -> RegistryIntentResult:
        """Create safe fallback parsing when main parsing fails"""
        fallback_intent = ParsedIntent(
            intent_type=IntentType.DISCOVERY,
            action_type=ActionType.QUERY,
            primary_target="registry",
            secondary_targets=[],
            parameters={},
            constraints={"read_only": True},
            confidence_score=0.1,
            metadata={"fallback": True, "error": error}
        )
        
        fallback_params = LayerParameters(
            layer_name="registry",
            required_capabilities=["basic_query"],
            interface_methods=["get_info"],
            state_requirements={},
            execution_constraints={"read_only": True},
            safety_requirements={"validate_input": True}
        )
        
        return RegistryIntentResult(
            parsed_intent=fallback_intent,
            layer_parameters=[fallback_params],
            parsing_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            intent_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when intent violates safety policies"""
    pass


class IntentParsingError(Exception):
    """Raised for general intent parsing errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_registry_intent_parser(safety_policy: Optional[RegistryIntentSafetyPolicy] = None) -> RegistryIntentParser:
    """Factory function to create RegistryIntentParser with optional custom safety policy"""
    return RegistryIntentParser(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_intent_request(request: RegistryIntentRequest) -> tuple[bool, Optional[str]]:
    """Validate registry intent request parameters"""
    try:
        if not request.intent or not request.intent.strip():
            return False, "Intent cannot be empty"
        
        if not request.source_layer or not request.source_layer.strip():
            return False, "Source layer cannot be empty"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"