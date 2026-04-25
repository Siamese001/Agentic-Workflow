"""Concrete ``JudgeProtocol`` implementations.

These adapters wrap real LLM providers behind the ``JudgeProtocol``
contract defined in ``graders.llm_judge``. They share:

- **Timeout discipline** (H8): every call is wrapped in a hard deadline;
  overruns surface as ``TimeoutError``, which the gate layer translates
  to ``JUDGE_TIMEOUT``.
- **Abstain protocol** (grader_composition_spec §5.1): prompts instruct
  the judge to return UNKNOWN when evidence is insufficient; responses
  are parsed with an explicit abstain path.
- **Isolation** (v4_hardening_addendum §H2.1): adapters do NOT share a
  session with the primary agent — each judge call is stateless.

Adapter selection:

- ``AnthropicJudge`` — uses the Anthropic Messages API.
- ``OpenAIJudge`` — uses the OpenAI Chat Completions API.
- ``HttpJudge`` — provider-agnostic generic HTTP adapter for custom
  endpoints or local vLLM/Ollama servers.

All adapters depend only on ``tools.enhanced_http`` internally (if
available) for retry/backoff/timeout wrapping — falling back to
``urllib`` when the helper is unavailable so judges still work in
minimal test environments.
"""

from agentic_core.L3_orchestration.exit_eval.judges.anthropic_judge import (
    AnthropicJudge,
)
from agentic_core.L3_orchestration.exit_eval.judges.http_judge import HttpJudge
from agentic_core.L3_orchestration.exit_eval.judges.openai_judge import (
    OpenAIJudge,
)
from agentic_core.L3_orchestration.exit_eval.judges.prompt_templates import (
    RUBRIC_PROMPTS,
    build_judge_prompt,
)

__all__ = [
    "AnthropicJudge",
    "HttpJudge",
    "OpenAIJudge",
    "RUBRIC_PROMPTS",
    "build_judge_prompt",
]
