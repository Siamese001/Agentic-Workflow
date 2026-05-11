"""Judge gateway package.

RB13: apps-rg-zip-based-full-spine-runtime-restoration-v1

Generic LLM judge invocation for agentic_core.
"""

from agentic_core.runtime.judges.judge_registry import (
    JudgeDimension,
    JudgeKind,
    JudgeProfile,
    JudgeRegistry,
    get_judge_registry,
    reset_judge_registry,
)
from agentic_core.runtime.judges.llm_judge_gateway import (
    LLMJudgeGateway,
    LLMJudgeRequest,
    LLMJudgeResponse,
)

__all__ = [
    # Registry
    "JudgeDimension",
    "JudgeKind",
    "JudgeProfile",
    "JudgeRegistry",
    "get_judge_registry",
    "reset_judge_registry",
    # Gateway
    "LLMJudgeGateway",
    "LLMJudgeRequest",
    "LLMJudgeResponse",
]
