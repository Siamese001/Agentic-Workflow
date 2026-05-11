"""Resume-domain judge implementations — generic core infrastructure.

These judges are app-agnostic LLM-as-judge evaluators for resume generation
quality dimensions. They are invoked via LLMJudgeGateway using provider profiles
supplied by the calling app's grader roster (e.g. apps_rg/config/domain_contract/).

Apps wire to these judges through config (provider_profile_ref + grader_ref) only.
No apps_* code lives in this package.
"""

from agentic_core.runtime.judges.resume_judges.executive_positioning import (
    ExecutivePositioningJudge,
)

__all__ = ["ExecutivePositioningJudge"]
