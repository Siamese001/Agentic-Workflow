"""Executive positioning LLM-as-judge — generic core infrastructure.

Evaluates whether a generated resume's summary and top bullets foreground
scope, ownership, scale, and outcomes appropriate for senior+/executive
target levels. Informational-only by default (does not hard-gate X3).

Invocation path:
  apps_rg/config/domain_contract/grader_roster.yaml
    -> grader_ref: rg::executive_positioning_judge::v1
    -> provider_profile_ref: local_qwen_generator
  LLMJudgeGateway._invoke_llm_judge()
    -> ExecutivePositioningJudge.build_prompt()
    -> Qwen2.5-32B-Instruct-AWQ via vLLM (port 8000)
    -> ExecutivePositioningJudge.parse_response()

Constitutional: apps_rg contributes config only. Core owns execution.
See: agentic_core/AGENTS.md §Layer Separation.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

_LOGGER = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are an expert executive resume evaluator. Your task is to assess whether a
generated resume effectively positions the candidate for senior and executive roles
by foregrounding scope, ownership, scale, and measurable outcomes.

Evaluate strictly against the rubric. Return ONLY a JSON object — no prose, no
markdown, no explanation outside the JSON.
"""

_RUBRIC = """\
RUBRIC — executive_positioning (informational dimension):

Score 0.85–1.00 (Strong):
  - Executive summary leads with scope (org size, P&L, headcount, geography).
  - Top 3 bullets each carry at least one quantified outcome OR ownership signal.
  - Language signals authority: "led", "owned", "drove", "accountable for" — not
    "supported", "assisted", "contributed to".
  - Achievements cite results at the enterprise level (revenue, cost savings, NPS,
    market share) where supported by candidate profile evidence.

Score 0.65–0.84 (Moderate):
  - Executive signals present but inconsistent — some bullets generic.
  - Scope mentioned in summary but not threaded through role descriptions.
  - Mix of ownership and support language.

Score 0.40–0.64 (Weak):
  - Summary reads as a mid-level IC rather than a leader.
  - Achievements lack scale or ownership context.
  - Language is primarily task-oriented ("responsible for") rather than
    outcome-oriented ("delivered", "grew", "transformed").

Score 0.00–0.39 (Fail):
  - No executive positioning signals.
  - Reads as a junior/IC resume regardless of target level.
  - No quantified outcomes. No scope signals.

IMPORTANT:
  - Score based ONLY on what is present in the generated resume text.
  - Do not penalise for missing evidence if the candidate profile lacked it.
  - This is informational-only — your score does not gate pipeline exit.
"""


@dataclass
class ExecutivePositioningPrompt:
    system_prompt: str
    user_prompt: str


@dataclass
class ExecutivePositioningResult:
    score: float
    confidence: float
    reasoning: str
    signal_breakdown: dict[str, Any] = field(default_factory=dict)
    parse_error: str | None = None


class ExecutivePositioningJudge:
    """LLM-as-judge for executive positioning quality in generated resumes.

    Consumed by LLMJudgeGateway when profile.judge_kind == LLM_AS_JUDGE
    and grader_ref == 'rg::executive_positioning_judge::v1'.

    This class is instantiated by the gateway — apps do not call it directly.
    """

    GRADER_REF = "rg::executive_positioning_judge::v1"
    IS_STUB = False

    def build_prompt(
        self,
        *,
        candidate_text: str,
        context_metadata: dict[str, Any],
    ) -> ExecutivePositioningPrompt:
        """Build the LLM prompt for executive positioning evaluation."""
        target_role = context_metadata.get("target_role", "unspecified")
        target_level = context_metadata.get("target_level", "unspecified")
        target_company = context_metadata.get("target_company", "unspecified")

        user_prompt = f"""\
{_RUBRIC}

TARGET CONTEXT:
  Role: {target_role}
  Level: {target_level}
  Company: {target_company}

GENERATED RESUME TEXT:
---
{candidate_text[:6000]}
---

Return a JSON object with exactly these fields:
{{
  "score": <float 0.00-1.00>,
  "confidence": <float 0.00-1.00>,
  "reasoning": "<one paragraph, ≤120 words>",
  "signal_breakdown": {{
    "scope_signals_count": <int>,
    "ownership_language_count": <int>,
    "quantified_outcomes_count": <int>,
    "executive_summary_quality": "<strong|moderate|weak|absent>"
  }}
}}
"""
        return ExecutivePositioningPrompt(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    def parse_response(self, raw_response: str) -> ExecutivePositioningResult:
        """Parse the LLM JSON response into a structured result."""
        try:
            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in response")
            data = json.loads(json_match.group())

            score = float(data.get("score", 0.0))
            score = max(0.0, min(1.0, score))

            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))

            reasoning = str(data.get("reasoning", ""))[:500]
            signal_breakdown = data.get("signal_breakdown", {})

            return ExecutivePositioningResult(
                score=score,
                confidence=confidence,
                reasoning=reasoning,
                signal_breakdown=signal_breakdown,
            )
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            _LOGGER.warning(
                "ExecutivePositioningJudge parse_response failed: %s — raw=%r",
                exc,
                raw_response[:200],
            )
            return ExecutivePositioningResult(
                score=0.0,
                confidence=0.0,
                reasoning="",
                parse_error=str(exc),
            )
