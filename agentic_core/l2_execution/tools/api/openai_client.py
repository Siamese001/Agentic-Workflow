"""
L5 Agentic Core - L2 Execution Layer - OpenAI API Client
Implements L2 Pure Execution Layer for safe OpenAI API interactions
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import json
import time

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"

class APIStatus(Enum):
    """L5 API status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    AUTH_ERROR = "auth_error"
    INVALID_REQUEST = "invalid_request"
    TIMEOUT = "timeout"
    CONTENT_FILTERED = "content_filtered"

@dataclass
class APIConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_tokens: int = 1000
    max_temperature: float = 1.0
    max_requests_per_minute: int = 60
    allowed_models: List[ModelType] = field(default_factory=lambda: [ModelType.GPT_3_5_TURBO, ModelType.GPT_4O_MINI])
    require_content_filter: bool = True
    safety_level: str = "strict"

@dataclass
class Message:
    """L5 Message structure with full type safety"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: str = ""

@dataclass
class ChatCompletion:
    """L5 Chat completion structure"""
    request_id: str
    model: ModelType
    messages: List[Message]
    response: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = ""
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class APIResponse:
    """L5 API response structure"""
    request_id: str
    status: APIStatus
    completion: Optional[ChatCompletion] = None
    error_message: str = ""
    safety_validated: bool = False
    timestamp: str = ""

class OpenAIClient(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def chat_completion(self, messages: List[Message], model: ModelType, constraints: APIConstraints) -> APIResponse:
        """Execute chat completion with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, messages: List[Message]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class OpenAIClientImpl(OpenAIClient):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure OpenAI API execution with comprehensive safety
    """
    
    def __init__(self, api_key: str, constraints: Optional[APIConstraints] = None):
        self.api_key = api_key
        self.constraints = constraints or APIConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.request_count = 0
        self.last_request_time = 0
    
    def chat_completion(self, messages: List[Message], model: ModelType, constraints: Optional[APIConstraints] = None) -> APIResponse:
        """Execute chat completion following L5 architecture principles"""
        api_constraints = constraints or self.constraints
        self.logger.info(f"Executing chat completion with model: {model.value}")
        
        # L5 Input validation
        self._validate_input(messages, model)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(messages):
            raise SecurityError("Messages failed L5 safety validation")
        
        # Rate limiting
        if not self._check_rate_limit(api_constraints):
            return APIResponse(
                request_id=self._generate_request_id(),
                status=APIStatus.RATE_LIMITED,
                error_message="Rate limit exceeded",
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        
        try:
            # Validate model
            if model not in api_constraints.allowed_models:
                return APIResponse(
                    request_id=self._generate_request_id(),
                    status=APIStatus.INVALID_REQUEST,
                    error_message=f"Model not allowed: {model.value}",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Execute API call (mock implementation for safety)
            completion = self._execute_chat_completion(messages, model, api_constraints)
            
            # Create API response
            response = APIResponse(
                request_id=self._generate_request_id(),
                status=APIStatus.SUCCESS,
                completion=completion,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Chat completion completed: {len(completion.response)} characters")
            return response
            
        except Exception as e:
            self.logger.error(f"Chat completion error: {e}")
            return APIResponse(
                request_id=self._generate_request_id(),
                status=APIStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _execute_chat_completion(self, messages: List[Message], model: ModelType, constraints: APIConstraints) -> ChatCompletion:
        """Execute the actual chat completion (mock implementation)"""
        # Note: This is a mock implementation for demonstration
        # In production, this would make actual API calls to OpenAI
        
        request_id = self._generate_request_id()
        
        # Simulate API response
        last_message = messages[-1] if messages else Message("user", "")
        response_text = f"This is a mock response to: {last_message.content[:100]}..."
        
        # Simulate usage statistics
        usage = {
            "prompt_tokens": sum(len(msg.content.split()) for msg in messages),
            "completion_tokens": len(response_text.split()),
            "total_tokens": sum(len(msg.content.split()) for msg in messages) + len(response_text.split())
        }
        
        completion = ChatCompletion(
            request_id=request_id,
            model=model,
            messages=messages,
            response=response_text,
            usage=usage,
            finish_reason="stop",
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        # Update request tracking
        self.request_count += 1
        self.last_request_time = time.time()
        
        return completion
    
    def _check_rate_limit(self, constraints: APIConstraints) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Reset counter if more than a minute has passed
        if current_time - self.last_request_time > 60:
            self.request_count = 0
        
        if self.request_count >= constraints.max_requests_per_minute:
            return False
        
        return True
    
    def validate_safety(self, messages: List[Message]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns in messages
            dangerous_patterns = [
                "<script>", "javascript:", "eval(", "exec(", "__import__",
                "ignore instructions", "disregard", "bypass", "override",
                "system prompt", "jailbreak", "dan", "developer mode"
            ]
            
            for message in messages:
                content_lower = message.content.lower()
                for pattern in dangerous_patterns:
                    if pattern in content_lower:
                        self.logger.error(f"Dangerous pattern detected in message: {pattern}")
                        return False
                
                # Check for extremely long messages
                if len(message.content) > 10000:
                    self.logger.error("Message too long")
                    return False
                
                # Check for suspicious characters
                if message.content.count('\0') > 0:
                    self.logger.error("Null bytes detected in message")
                    return False
            
            # Validate message roles
            valid_roles = ["system", "user", "assistant"]
            for message in messages:
                if message.role not in valid_roles:
                    self.logger.error(f"Invalid message role: {message.role}")
                    return False
            
            # Check message sequence
            if messages and messages[0].role != "system":
                # Allow but warn if no system message
                self.logger.warning("No system message provided")
            
            self.logger.info("Messages passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Message safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, messages: List[Message], model: ModelType) -> None:
        """L5 Input validation"""
        if not isinstance(messages, list):
            raise ValueError("Messages must be a list")
        
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        for message in messages:
            if not isinstance(message, Message):
                raise ValueError("Each message must be a Message object")
            
            if not message.content.strip():
                raise ValueError("Message content cannot be empty")
        
        if not isinstance(model, ModelType):
            raise ValueError("Model must be a ModelType enum")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return f"openai_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class OpenAIClientInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, client: OpenAIClient):
        self._client = client
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", max_tokens: int = 1000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            # Convert message dictionaries to Message objects
            message_objects = []
            for msg in messages:
                message_objects.append(Message(
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    timestamp=self._get_timestamp()
                ))
            
            model_type = ModelType(model)
            constraints = APIConstraints(max_tokens=max_tokens)
            
            response = self._client.chat_completion(message_objects, model_type, constraints)
            
            if response.completion:
                return {
                    "success": response.status == APIStatus.SUCCESS,
                    "request_id": response.request_id,
                    "model": response.completion.model.value,
                    "response": response.completion.response,
                    "usage": response.completion.usage,
                    "finish_reason": response.completion.finish_reason,
                    "safety_validated": response.completion.safety_validated,
                    "timestamp": response.completion.timestamp
                }
            else:
                return {
                    "success": False,
                    "error": response.error_message,
                    "status": response.status.value,
                    "safety_validated": response.safety_validated
                }
        except Exception as e:
            self.logger.error(f"OpenAI chat completion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# L5 Factory pattern
class OpenAIClientFactory:
    """L5 Factory for creating OpenAI client instances"""
    
    @staticmethod
    def create_client(api_key: str, constraints: Optional[APIConstraints] = None) -> OpenAIClient:
        return OpenAIClientImpl(api_key, constraints)
    
    @staticmethod
    def create_interface(api_key: str, constraints: Optional[APIConstraints] = None) -> OpenAIClientInterface:
        client = OpenAIClientFactory.create_client(api_key, constraints)
        return OpenAIClientInterface(client)

# L5 Export for module usage
__all__ = [
    "ModelType",
    "APIStatus",
    "APIConstraints",
    "Message",
    "ChatCompletion",
    "APIResponse",
    "OpenAIClient",
    "OpenAIClientImpl",
    "OpenAIClientInterface",
    "OpenAIClientFactory",
    "SecurityError"
]
