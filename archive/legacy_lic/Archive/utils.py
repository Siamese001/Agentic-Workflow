# File: utils.py
# Description: General-purpose utilities for the LIC workflow.

__version__ = "11.10"

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from collections import defaultdict

from models import CircuitState, Archetype, CircuitBreakerOpenError

# ============================================================================
# NEW v11.6: CIRCUIT BREAKER (FEATURE 4.1)
# ============================================================================

class CircuitBreaker:
    """
    Circuit breaker for API calls - prevents cascade failures
    FEATURE 4.1 from SUPREME_SPELL
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        timeout_seconds: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self.last_failure_time and datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
            else:
                raise CircuitBreakerOpenError("API circuit breaker is OPEN - waiting for recovery")
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == CircuitState.HALF_OPEN:
                # Test request succeeded, close circuit
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise

# ============================================================================
# NEW v11.6: CONTEXT MANAGER (GAP 7.1-7.3)
# ============================================================================

class ContextManager:
    """
    Intelligent context window management with priority-based truncation
    GAP 7.1, 7.2, 7.3 from v10.22
    """
    
    SECTION_PRIORITIES = {
        "job_description": 100,      # Highest - never truncate
        "recipient_profile": 90,
        "company_context": 80,
        "sender_profile": 70,
        "rag_recent": 60,
        "rag_historical": 40,
        "examples": 30,              # Lowest - truncate first
    }
    
    MAX_CONTEXT_TOKENS = 180000  # Conservative estimate
    
    @classmethod
    def truncate_intelligently(
        cls,
        context_sections: Dict[str, str],
        max_tokens: int = MAX_CONTEXT_TOKENS
    ) -> Dict[str, str]:
        """
        Truncate context sections by priority if exceeding token limit
        """
        # Rough estimate: 4 chars = 1 token
        total_chars = sum(len(text) for text in context_sections.values())
        estimated_tokens = total_chars // 4
        
        if estimated_tokens <= max_tokens:
            return context_sections
        
        # Sort sections by priority
        sorted_sections = sorted(
            context_sections.items(),
            key=lambda x: cls.SECTION_PRIORITIES.get(x[0], 50),
            reverse=True
        )
        
        truncated = {}
        running_tokens = 0
        token_budget = max_tokens
        
        for section_name, section_text in sorted_sections:
            section_tokens = len(section_text) // 4
            
            if running_tokens + section_tokens <= token_budget:
                truncated[section_name] = section_text
                running_tokens += section_tokens
            else:
                # Truncate this section to fit remaining budget
                remaining_tokens = token_budget - running_tokens
                remaining_chars = remaining_tokens * 4
                
                if remaining_chars > 100:  # Only include if meaningful
                    truncated[section_name] = section_text[:remaining_chars] + "... [truncated]"
                    running_tokens = token_budget
                break
        
        return truncated
    
    @classmethod
    def detect_overflow(cls, context_text: str) -> Tuple[bool, int]:
        """
        Detect if context exceeds safe limits
        
        Returns:
            (is_overflow, estimated_tokens)
        """
        estimated_tokens = len(context_text) // 4
        is_overflow = estimated_tokens > cls.MAX_CONTEXT_TOKENS
        return is_overflow, estimated_tokens

# ============================================================================
# NEW v11.6: ADAPTIVE TEMPERATURE CONTROLLER (FEATURE 2.2)
# ============================================================================

class AdaptiveTemperatureController:
    """
    Progressive temperature escalation for retry attempts
    FEATURE 2.2 from SUPREME_SPELL
    """
    
    BASE_TEMPERATURES = {
        Archetype.C_LEVEL: 0.45,
        Archetype.EXECUTIVE: 0.50,
        Archetype.SENIOR_TA: 0.55,
        Archetype.RECRUITER: 0.65
    }
    ESCALATION_STEP = 0.15
    MAX_TEMPERATURE = 0.95
    
    def __init__(self):
        self.attempt_history: Dict[str, List[float]] = defaultdict(list)
        self.success_temperatures: Dict[str, float] = {}
    
    def get_temperature(
        self,
        component: str,
        archetype: Archetype,
        attempt: int
    ) -> float:
        """Get temperature for this generation attempt"""
        base_temp = self.BASE_TEMPERATURES[archetype]
        escalated_temp = min(
            self.MAX_TEMPERATURE,
            base_temp + (attempt - 1) * self.ESCALATION_STEP
        )
        
        self.attempt_history[f"{archetype.value}_{component}"].append(escalated_temp)
        
        return escalated_temp
    
    def record_success(
        self,
        component: str,
        archetype: Archetype,
        temperature: float
    ):
        """Record which temperature succeeded for learning"""
        key = f"{archetype.value}_{component}"
        self.success_temperatures[key] = temperature