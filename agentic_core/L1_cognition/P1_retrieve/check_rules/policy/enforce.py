"""
01_agentic_core/L1_cognition/P1_retrieve/check_rules/policy/enforce.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 67f2d671dc15d5de00c4a796234383852fd07f916408cf0c56dfa7c2e6e68f35
"""


from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Critical dangerous patterns for safety validation
CRITICAL_PATTERNS: List[str] = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__",
    r"subprocess\.",
    r"os\.system",
    r"\.\./.*\.\.",
]

# Maximum data size for safety validation (1MB)
MAX_DATA_SIZE: int = 1_000_000


class EnforceDataBudgetSafetyType(Enum):
    """Typed enumeration for deterministic safety operations."""

    APPLY = "apply"
    ENFORCE = "enforce"
    VALIDATE = "validate"


@dataclass
class EnforceDataBudgetSafetyConstraints:
    """
    Safety constraints for data budget enforcement - fail-closed behavior.

    Attributes:
        max_risk_score: Maximum acceptable risk score (0.0-1.0).
        allowed_operations: List of permitted operation types.
        safety_level: Safety enforcement level (strict/permissive).
        requires_approval: Whether operations require explicit approval.
    """

    max_risk_score: float = 0.5
    allowed_operations: List[str] = field(
        default_factory=lambda: ["apply", "enforce", "validate"]
    )
    safety_level: str = "strict"
    requires_approval: bool = True


@dataclass
class EnforceDataBudgetSafetyResult:
    """
    Result structure for data budget enforcement with full type safety.

    Attributes:
        success: Whether the operation completed successfully.
        safety_score: Calculated safety score (0.0=safe, 1.0=dangerous).
        risk_assessment: Detailed risk assessment dictionary.
        errors: List of error messages encountered.
        safety_validated: Whether safety validation passed.
        timestamp: ISO timestamp of result creation.
    """

    success: bool
    safety_score: float = 0.0
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class EnforceDataBudgetSafetySafety(ABC):
    """L5 Abstract base - ensures L5 pure safety behavior"""
    
    @abstractmethod
    def apply_safety(self, data: Dict[str, Any]) -> EnforceDataBudgetSafetyResult:
        """Apply safety checks with L5 constraints"""
        ...
    
    @abstractmethod
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        ...


class EnforceDataBudgetSafetyImpl(EnforceDataBudgetSafetySafety):
    """
    L5 Implementation - L5 Safety/Policy Layer
    Fail-closed safety enforcement with comprehensive policy checks
    """
    
    def __init__(self, constraints: Optional[EnforceDataBudgetSafetyConstraints] = None):
        self.constraints = constraints or EnforceDataBudgetSafetyConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._safety_rules = self._initialize_safety_rules()
    
    def apply_safety(self, data: Dict[str, Any]) -> EnforceDataBudgetSafetyResult:
        """Apply safety checks following L5 architecture principles"""
        self.logger.info(f"Applying safety checks to data")
        
        # L5 Input validation
        self._validate_input(data)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(data):
            raise SecurityError("Data failed L5 safety validation")
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(data)
        
        # Perform risk assessment
        risk_assessment = self._assess_risks(data)
        
        # Create result with L5 structure
        result = EnforceDataBudgetSafetyResult(
            success=safety_score <= self.constraints.max_risk_score,
            safety_score=safety_score,
            risk_assessment=risk_assessment,
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        self.logger.info(f"Safety check completed: score={safety_score}, passed={result.success}")
        return result
    
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for critical dangerous patterns
            critical_patterns = [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"eval\s*\(",
                r"exec\s*\(",
                r"__import__",
                r"subprocess\.",
                r"os\.system",
                r"\.\./.*\.\.",
            ]
            
            data_str = str(data).lower()
            for pattern in critical_patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    self.logger.error(f"Critical dangerous pattern detected: {pattern}")
                    return False
            
            # Check data size limits
            if len(data_str) > 1000000:  # 1MB limit
                self.logger.error("Data exceeds safety size limit")
                return False
            
            self.logger.info("Data passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, data: Dict[str, Any]) -> None:
        """L5 Input validation"""
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
        
        if not data:
            raise ValueError("Input cannot be empty")
    
    def _calculate_safety_score(self, data: Dict[str, Any]) -> float:
        """Calculate L5 safety score (0.0 = safe, 1.0 = dangerous)"""
        score = 0.0
        data_str = str(data).lower()
        
        # Check for suspicious patterns
        suspicious_patterns = [
            ("password", 0.3),
            ("secret", 0.3),
            ("token", 0.2),
            ("key", 0.1),
            ("admin", 0.2),
            ("root", 0.3),
        ]
        
        for pattern, weight in suspicious_patterns:
            if pattern in data_str:
                score += weight
        
        # Check complexity
        if len(data_str) > 10000:
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_risks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        risks = {
            "injection_risk": self._check_injection_risk(data),
            "size_risk": self._check_size_risk(data),
            "complexity_risk": self._check_complexity_risk(data),
            "pattern_risk": self._check_pattern_risk(data)
        }
        
        return {
            "risks": risks,
            "overall_risk": "low" if all(r == "low" for r in risks.values()) else "medium" if any(r == "medium" for r in risks.values()) else "high"
        }
    
    def _check_injection_risk(self, data: Dict[str, Any]) -> str:
        """Check for injection risks"""
        injection_patterns = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        data_str = str(data)
        
        for pattern in injection_patterns:
            if pattern in data_str:
                return "high"
        
        return "low"
    
    def _check_size_risk(self, data: Dict[str, Any]) -> str:
        """Check size-related risks"""
        size = len(str(data))
        
        if size > 100000:
            return "high"
        elif size > 10000:
            return "medium"
        else:
            return "low"
    
    def _check_complexity_risk(self, data: Dict[str, Any]) -> str:
        """Check complexity risks based on nesting depth."""
        try:
            depth = self._calculate_depth(data)
            if depth > 10:
                return "high"
            elif depth > 5:
                return "medium"
            else:
                return "low"
        except (TypeError, RecursionError) as e:
            self._logger.warning("Complexity check failed: %s", e)
            return "high"  # Fail-closed
    
    def _check_pattern_risk(self, data: Dict[str, Any]) -> str:
        """Check for risky patterns"""
        risky_patterns = ["eval", "exec", "import", "subprocess", "os.system"]
        data_str = str(data).lower()
        
        for pattern in risky_patterns:
            if pattern in data_str:
                return "high"
        
        return "low"
    
    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate nesting depth"""
        if isinstance(obj, dict):
            return max([self._calculate_depth(v, current_depth + 1) for v in obj.values()], default=current_depth)
        elif isinstance(obj, list):
            return max([self._calculate_depth(item, current_depth + 1) for item in obj], default=current_depth)
        else:
            return current_depth
    
    def _initialize_safety_rules(self) -> List[Dict[str, Any]]:
        """Initialize L5 safety rules"""
        return [
            {"name": "no_injection", "pattern": r"(union|select|insert|update|delete|drop)", "severity": "high"},
            {"name": "no_scripts", "pattern": r"<script", "severity": "high"},
            {"name": "no_eval", "pattern": r"eval\s*\(", "severity": "high"},
            {"name": "size_limit", "max_size": 1000000, "severity": "medium"}
        ]
    
class SecurityError(Exception):
    """
    Security exception for fail-closed behavior.

    Attributes:
        message: Human-readable error description.
        context: Additional context about the security violation.
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}


class EnforceDataBudgetSafetyInterface:
    """Interface for data budget enforcement ensuring contract compliance."""

    def __init__(self, safety: EnforceDataBudgetSafetySafety) -> None:
        self._safety = safety

    def apply_safety(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safety checks."""
        try:
            result = self._safety.apply_safety(data)
            return {
                "success": result.success,
                "safety_score": result.safety_score,
                "risk_assessment": result.risk_assessment,
                "errors": result.errors,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp,
            }
        except SecurityError:
            raise
        except ValueError as e:
            raise SecurityError(
                f"Validation failed: {e}", context={"error_type": "validation"}
            ) from e
        except Exception as e:
            raise SecurityError(
                f"Safety application failed: {e}", context={"error_type": "execution"}
            ) from e


class EnforceDataBudgetSafetyFactory:
    """Factory for creating data budget enforcement handlers."""

    @staticmethod
    def create_safety(
        safety_level: str = "strict",
    ) -> EnforceDataBudgetSafetyInterface:
        """Create a configured safety handler."""
        constraints = EnforceDataBudgetSafetyConstraints(safety_level=safety_level)
        safety = EnforceDataBudgetSafetyImpl(constraints)
        return EnforceDataBudgetSafetyInterface(safety)


def enforce_data_budget(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function for enforcing data budget constraints.

    Args:
        data: Data to apply safety checks to.

    Returns:
        Dictionary containing safety result.

    Raises:
        SecurityError: If safety check fails any validation.
        ValueError: If input validation fails.
    """
    safety = EnforceDataBudgetSafetyFactory.create_safety()
    return safety.apply_safety(data)


__all__ = [
    "EnforceDataBudgetSafetyType",
    "EnforceDataBudgetSafetyConstraints",
    "EnforceDataBudgetSafetyResult",
    "EnforceDataBudgetSafetySafety",
    "EnforceDataBudgetSafetyImpl",
    "EnforceDataBudgetSafetyInterface",
    "EnforceDataBudgetSafetyFactory",
    "SecurityError",
    "enforce_data_budget",
    "CRITICAL_PATTERNS",
    "MAX_DATA_SIZE",
]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        test_data = {"test": "safe_data", "value": 123}
        result = enforce_data_budget(test_data)
        logger.info("Safety check successful: %s", result)
    except SecurityError as e:
        logger.error("Security error: %s (context: %s)", e.message, e.context)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
