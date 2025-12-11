"""RAG History Request Handler - Handles requests for RAG operation history.

This module provides request handling for RAG history operations,
including validation, processing, and response formatting.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Types of RAG history requests."""
    QUERY_HISTORY = "query_history"
    RETRIEVAL_HISTORY = "retrieval_history"
    GENERATION_HISTORY = "generation_history"
    USER_HISTORY = "user_history"
    SESSION_HISTORY = "session_history"
    PERFORMANCE_HISTORY = "performance_history"


class RequestStatus(Enum):
    """Status of request processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class HistoryRequest:
    """Request for RAG history data."""
    request_id: str
    request_type: RequestType
    parameters: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0  # 0 = normal, 1 = high, 2 = urgent


@dataclass
class HistoryResponse:
    """Response to RAG history request."""
    request_id: str
    status: RequestStatus
    data: Dict[str, Any] = field(default_factory=dict)
    entries: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    processing_time_ms: int = 0


@dataclass
class RequestHandlerConfig:
    """Configuration for request handler."""
    max_concurrent_requests: int = 10
    request_timeout_ms: int = 30000
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 100
    log_level: str = "INFO"


class RAGHistoryRequestHandler:
    """Main class for handling RAG history requests."""

    def __init__(self, config: Optional[RequestHandlerConfig] = None):
        self.config = config or RequestHandlerConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._active_requests = {}
        self._request_cache = {}
        self._rate_limit_tracker = {}

    def handle_request(self, request: HistoryRequest) -> HistoryResponse:
        """Handle a RAG history request.
        
        Args:
            request: History request with parameters and filters
            
        Returns:
            HistoryResponse: Response with requested data or error
        """
        self.logger.info(f"Handling RAG history request: {request.request_id}")
        start_time = datetime.utcnow()
        
        try:
            # Validate request
            self._validate_request(request)
            
            # Check rate limiting
            if self.config.enable_rate_limiting:
                if not self._check_rate_limit(request.user_id):
                    return HistoryResponse(
                        request_id=request.request_id,
                        status=RequestStatus.FAILED,
                        error_message="Rate limit exceeded"
                    )
            
            # Check cache
            cache_key = self._get_cache_key(request)
            if self.config.enable_caching and cache_key in self._request_cache:
                self.logger.debug("Returning cached response")
                cached_response = self._request_cache[cache_key]
                cached_response.processing_time_ms = 0  # Cached response
                return cached_response
            
            # Process request
            response = self._process_request(request)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            response.processing_time_ms = int(processing_time)
            
            # Cache response if successful
            if (self.config.enable_caching and 
                response.status == RequestStatus.COMPLETED):
                self._request_cache[cache_key] = response
                self._cleanup_cache()
            
            self.logger.info(
                f"Request {request.request_id} completed in {processing_time:.2f}ms"
            )
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to handle request {request.request_id}: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HistoryResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )

    def _validate_request(self, request: HistoryRequest) -> None:
        """Validate history request."""
        if not request.request_id:
            raise ValueError("Request ID is required")
        
        if not request.request_type:
            raise ValueError("Request type is required")
        
        # Validate request type specific parameters
        if request.request_type == RequestType.USER_HISTORY and not request.user_id:
            raise ValueError("User ID is required for user history requests")
        
        if request.request_type == RequestType.SESSION_HISTORY and not request.session_id:
            raise ValueError("Session ID is required for session history requests")

    def _check_rate_limit(self, user_id: Optional[str]) -> bool:
        """Check if user has exceeded rate limit."""
        if not user_id:
            return True
        
        now = datetime.utcnow()
        minute_key = now.strftime("%Y%m%d%H%M")
        
        if user_id not in self._rate_limit_tracker:
            self._rate_limit_tracker[user_id] = {}
        
        # Clean old entries
        self._rate_limit_tracker[user_id] = {
            k: v for k, v in self._rate_limit_tracker[user_id].items()
            if k >= minute_key - 5  # Keep last 5 minutes
        }
        
        # Count requests in current minute
        current_count = self._rate_limit_tracker[user_id].get(minute_key, 0)
        
        if current_count >= self.config.rate_limit_per_minute:
            return False
        
        # Increment counter
        self._rate_limit_tracker[user_id][minute_key] = current_count + 1
        return True

    def _get_cache_key(self, request: HistoryRequest) -> str:
        """Generate cache key for request."""
        return f"{request.request_type}_{hash(str(request.parameters))}_{hash(str(request.filters))}"

    def _process_request(self, request: HistoryRequest) -> HistoryResponse:
        """Process the history request."""
        # Mark request as processing
        self._active_requests[request.request_id] = {
            "status": RequestStatus.PROCESSING,
            "started_at": datetime.utcnow()
        }
        
        try:
            # Route to appropriate handler
            if request.request_type == RequestType.QUERY_HISTORY:
                data = self._handle_query_history(request)
            elif request.request_type == RequestType.RETRIEVAL_HISTORY:
                data = self._handle_retrieval_history(request)
            elif request.request_type == RequestType.GENERATION_HISTORY:
                data = self._handle_generation_history(request)
            elif request.request_type == RequestType.USER_HISTORY:
                data = self._handle_user_history(request)
            elif request.request_type == RequestType.SESSION_HISTORY:
                data = self._handle_session_history(request)
            elif request.request_type == RequestType.PERFORMANCE_HISTORY:
                data = self._handle_performance_history(request)
            else:
                raise ValueError(f"Unsupported request type: {request.request_type}")
            
            # Update active requests
            self._active_requests[request.request_id]["status"] = RequestStatus.COMPLETED
            
            return HistoryResponse(
                request_id=request.request_id,
                status=RequestStatus.COMPLETED,
                data=data.get("metadata", {}),
                entries=data.get("entries", []),
                metadata={
                    "processed_at": datetime.utcnow().isoformat(),
                    "handler": "RAGHistoryRequestHandler"
                }
            )
            
        except Exception as e:
            self._active_requests[request.request_id]["status"] = RequestStatus.FAILED
            raise e
        finally:
            # Clean up active requests after delay
            if request.request_id in self._active_requests:
                del self._active_requests[request.request_id]

    def _handle_query_history(self, request: HistoryRequest) -> Dict[str, Any]:
        """Handle query history request."""
        # Simulate query history retrieval
        entries = []
        
        for i in range(10):
            entry = {
                "id": f"query_{i}",
                "query": f"Sample query {i}",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "results_count": np.random.randint(5, 20),
                "response_time_ms": np.random.randint(100, 500)
            }
            entries.append(entry)
        
        return {
            "entries": entries,
            "metadata": {
                "total_queries": len(entries),
                "avg_response_time": sum(e["response_time_ms"] for e in entries) / len(entries)
            }
        }

    def _handle_retrieval_history(self, request: HistoryRequest) -> Dict[str, Any]:
        """Handle retrieval history request."""
        # Simulate retrieval history
        entries = []
        
        for i in range(10):
            entry = {
                "id": f"retrieval_{i}",
                "query_id": f"query_{i}",
                "strategy": "hybrid",
                "documents_retrieved": np.random.randint(10, 50),
                "relevant_docs": np.random.randint(5, 15),
                "precision": np.random.uniform(0.5, 0.9),
                "recall": np.random.uniform(0.6, 0.8)
            }
            entries.append(entry)
        
        return {
            "entries": entries,
            "metadata": {
                "total_retrievals": len(entries),
                "avg_precision": sum(e["precision"] for e in entries) / len(entries)
            }
        }

    def _handle_generation_history(self, request: HistoryRequest) -> Dict[str, Any]:
        """Handle generation history request."""
        # Simulate generation history
        entries = []
        
        for i in range(10):
            entry = {
                "id": f"generation_{i}",
                "query_id": f"query_{i}",
                "model": "gpt-4",
                "prompt_length": np.random.randint(100, 500),
                "response_length": np.random.randint(50, 300),
                "tokens_used": np.random.randint(150, 800),
                "quality_score": np.random.uniform(0.7, 0.95)
            }
            entries.append(entry)
        
        return {
            "entries": entries,
            "metadata": {
                "total_generations": len(entries),
                "avg_quality": sum(e["quality_score"] for e in entries) / len(entries)
            }
        }

    def _handle_user_history(self, request: HistoryRequest) -> Dict[str, Any]:
        """Handle user history request."""
        # Simulate user history
        entries = []
        
        for i in range(10):
            entry = {
                "id": f"user_action_{i}",
                "user_id": request.user_id,
                "action": ["query", "feedback", "rating", "bookmark"][np.random.randint(0, 4)],
                "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "details": f"Action details {i}"
            }
            entries.append(entry)
        
        return {
            "entries": entries,
            "metadata": {
                "user_id": request.user_id,
                "total_actions": len(entries),
                "activity_span_days": 10
            }
        }

    def _handle_session_history(self, request: HistoryRequest) -> Dict[str, Any]:
        """Handle session history request."""
        # Simulate session history
        entries = []
        
        for i in range(10):
            entry = {
                "id": f"session_event_{i}",
                "session_id": request.session_id,
                "event_type": ["start", "query", "click", "end"][np.random.randint(0, 4)],
                "timestamp": (datetime.utcnow() - timedelta(minutes=i*10)).isoformat(),
                "data": f"Event data {i}"
            }
            entries.append(entry)
        
        return {
            "entries": entries,
            "metadata": {
                "session_id": request.session_id,
                "total_events": len(entries),
                "session_duration_minutes": 90
            }
        }

    def _handle_performance_history(self, request: HistoryRequest) -> Dict[str, Any]:
        """Handle performance history request."""
        # Simulate performance metrics
        entries = []
        
        for i in range(10):
            entry = {
                "id": f"metric_{i}",
                "metric_name": ["latency", "throughput", "error_rate", "cpu_usage"][np.random.randint(0, 4)],
                "value": np.random.uniform(0.1, 100),
                "unit": ["ms", "req/s", "%", "%"][np.random.randint(0, 4)],
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat()
            }
            entries.append(entry)
        
        return {
            "entries": entries,
            "metadata": {
                "total_metrics": len(entries),
                "measurement_period": "10 hours"
            }
        }

    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        # Simple cleanup - remove oldest entries if cache is too large
        if len(self._request_cache) > 100:
            items = list(self._request_cache.items())
            self._request_cache = dict(items[-50:])  # Keep last 50

    def get_active_requests(self) -> List[str]:
        """Get list of active request IDs."""
        return list(self._active_requests.keys())

    def cancel_request(self, request_id: str) -> bool:
        """Cancel an active request.
        
        Args:
            request_id: ID of request to cancel
            
        Returns:
            bool: True if request was cancelled
        """
        if request_id in self._active_requests:
            self._active_requests[request_id]["status"] = RequestStatus.CANCELLED
            self.logger.info(f"Cancelled request: {request_id}")
            return True
        return False


# Factory function for easy instantiation
def create_rag_history_request_handler(
    max_concurrent_requests: int = 10,
    request_timeout_ms: int = 30000,
    enable_caching: bool = True,
    **kwargs
) -> RAGHistoryRequestHandler:
    """Create a configured RAG history request handler."""
    config = RequestHandlerConfig(
        max_concurrent_requests=max_concurrent_requests,
        request_timeout_ms=request_timeout_ms,
        enable_caching=enable_caching,
        **kwargs
    )
    return RAGHistoryRequestHandler(config)


# Convenience function for direct usage
def request_rag_history(
    request_type: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Request RAG history with simple parameters.
    
    Args:
        request_type: Type of history request
        user_id: Optional user ID
        session_id: Optional session ID
        filters: Optional filters to apply
        parameters: Optional request parameters
        config: Optional handler configuration overrides
        
    Returns:
        Dict: History response with data
    """
    # Build request
    request = HistoryRequest(
        request_id=f"req_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        request_type=RequestType(request_type),
        user_id=user_id,
        session_id=session_id,
        filters=filters or {},
        parameters=parameters or {}
    )
    
    # Create handler and process
    handler_config = RequestHandlerConfig(**config) if config else None
    handler = RAGHistoryRequestHandler(handler_config)
    response = handler.handle_request(request)
    
    # Convert response to dict for JSON serialization
    return {
        "request_id": response.request_id,
        "status": response.status.value,
        "data": response.data,
        "entries": response.entries,
        "metadata": response.metadata,
        "error_message": response.error_message,
        "processing_time_ms": response.processing_time_ms
    }
