"""W9 Boundary Hardening — LLM Judge Gateway (Core-Owned)

Gateway for LLM-as-judge evaluation. Provides profile-only mode for W9
deterministic-only implementation.

W9 Status: PROFILE_ONLY
- No active LLM backend invocation
- Deterministic graders used instead
- Full LLM gateway scaffolded for future activation

Core owns gateway. Apps do NOT call providers directly.
"""
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum, auto


class LLMGatewayMode(Enum):
    """Operating modes for LLM judge gateway."""
    PROFILE_ONLY = auto()  # W9 mode: deterministic only
    PASS_THROUGH = auto()  # Pass to configured backend
    FAIL_CLOSED = auto()   # Return error on any call


@dataclass(frozen=True)
class LLMJudgeConfig:
    """Configuration for LLM judge backend."""
    provider: str = "qwen_vllm"  # qwen_vllm, anthropic, openai
    timeout_seconds: float = 30.0
    max_retries: int = 2
    fail_closed: bool = True
    endpoint_url: str = "http://localhost:8000/v1"


class LLMJudgeGateway:
    """Gateway for LLM judge invocations.
    
    W9: Operating in PROFILE_ONLY mode.
    All judge evaluation goes through deterministic graders.
    
    Future activation: Set mode=PASS_THROUGH with valid config.
    """
    
    def __init__(
        self,
        mode: LLMGatewayMode = LLMGatewayMode.PROFILE_ONLY,
        config: Optional[LLMJudgeConfig] = None
    ):
        self._mode = mode
        self._config = config or LLMJudgeConfig()
    
    @property
    def mode(self) -> LLMGatewayMode:
        """Current gateway operating mode."""
        return self._mode
    
    @property
    def is_active(self) -> bool:
        """Check if LLM backend is active."""
        return self._mode == LLMGatewayMode.PASS_THROUGH
    
    def evaluate(
        self,
        prompt: str,
        dimension: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt LLM evaluation (or return profile-only response).
        
        Args:
            prompt: Evaluation prompt
            dimension: Dimension being evaluated
            context: Evaluation context
            
        Returns:
            Dict with result or error indicating gateway mode
        """
        if self._mode == LLMGatewayMode.PROFILE_ONLY:
            return {
                "status": "PROFILE_ONLY",
                "dimension": dimension,
                "message": "LLM judge gateway in PROFILE_ONLY mode. Use deterministic graders.",
                "score": None,
                "reasoning": "W9: deterministic graders active. LLM backend not invoked.",
            }
        
        elif self._mode == LLMGatewayMode.FAIL_CLOSED:
            return {
                "status": "ERROR",
                "dimension": dimension,
                "message": "LLM judge gateway in FAIL_CLOSED mode",
                "score": None,
                "reasoning": "Gateway configured to fail closed",
            }
        
        elif self._mode == LLMGatewayMode.PASS_THROUGH:
            # Future: actual LLM backend invocation
            # For now, return stub indicating not implemented
            return {
                "status": "NOT_IMPLEMENTED",
                "dimension": dimension,
                "message": "PASS_THROUGH mode not yet activated",
                "score": None,
                "reasoning": "LLM backend invocation pending activation",
            }
        
        return {
            "status": "UNKNOWN_MODE",
            "dimension": dimension,
            "message": f"Unknown gateway mode: {self._mode}",
        }


# ─────────────────────────────────────────────────────────────────────────────
# W9 Default Gateway (PROFILE_ONLY)
# ─────────────────────────────────────────────────────────────────────────────

# W9 uses deterministic graders only
default_llm_gateway = LLMJudgeGateway(mode=LLMGatewayMode.PROFILE_ONLY)


def get_llm_gateway() -> LLMJudgeGateway:
    """Get the default LLM judge gateway.
    
    W9: Returns PROFILE_ONLY gateway.
    """
    return default_llm_gateway
