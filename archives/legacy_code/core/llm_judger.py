"""
LLM-Based Semantic Judger for Canon Validation

This component uses structured LLM calls to validate semantic equivalence
between retrieved patterns and new code, mitigating false-positive matches
in the vector search results.
"""

import ast
import json
import logging
from typing import Dict, List, Optional, Tuple

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

from schemas.canon_models import CanonEntry

logger = logging.getLogger(__name__)


class SemanticJudgement(BaseModel):
    """Result of semantic judgement by LLM."""

    is_equivalent: bool = Field(
        description="Whether the retrieved pattern is semantically equivalent to the new code"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence score for the judgement"
    )
    reasoning: str = Field(
        description="Detailed reasoning for the judgement"
    )
    structural_match: bool = Field(
        description="Whether the AST structures match closely"
    )
    functional_match: bool = Field(
        description="Whether the functionality is equivalent"
    )
    risk_assessment: str = Field(
        description="Assessment of risk if this pattern is applied"
    )


class LLMJudger:
    """
    LLM-Based Judger for semantic validation of canon patterns.

    Uses structured outputs with Instructor to ensure consistent,
    parseable judgements from the LLM.
    """

    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """Initialize the LLM Judger."""
        # Configure OpenAI client with Instructor
        client = OpenAI(api_key=api_key)
        self.llm = instructor.from_openai(client)
        self.model = model

        logger.info(f"LLM Judger initialized with model: {model}")

    def judge_pattern_equivalence(
        self,
        candidate_patterns: List[CanonEntry],
        new_code: str,
        new_ast: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> Tuple[Optional[CanonEntry], SemanticJudgement]:
        """
        Judge if any of the candidate patterns are semantically equivalent to new code.

        Args:
            candidate_patterns: Retrieved patterns from cache
            new_code: The new code to validate
            new_ast: AST of the new code (optional, will be generated if not provided)
            context: Additional context about the validation task

        Returns:
            Tuple of (best_matching_pattern, judgement_result)
        """
        if not candidate_patterns:
            return None, SemanticJudgement(
                is_equivalent=False,
                confidence=0.0,
                reasoning="No candidate patterns provided",
                structural_match=False,
                functional_match=False,
                risk_assessment="Unknown - no patterns to compare"
            )

        # Generate AST for new code if not provided
        if new_ast is None:
            try:
                tree = ast.parse(new_code)
                new_ast = ast.dump(tree, include_attributes=True)
            except SyntaxError as e:
logger.error(f"Failed to parse new code: {e}")
                return None, SemanticJudgement(
                    is_equivalent=False,
                    confidence=0.0,
                    reasoning=f"New code has syntax error: {e}",
                    structural_match=False,
                    functional_match=False,
                    risk_assessment="High - syntax error in new code"
                )

        best_match = None
        best_judgement = None
        highest_confidence = 0.0

        # Judge each candidate pattern
        for pattern in candidate_patterns:
            judgement = self._compare_single_pattern(
                pattern, new_code, new_ast, context)

            if judgement.is_equivalent and judgement.confidence > highest_confidence:
                best_match = pattern
                best_judgement = judgement
                highest_confidence = judgement.confidence

        # If no equivalent patterns found, return the highest confidence judgement
        if best_match is None and candidate_patterns:
            # Return the first pattern's judgement as "not equivalent"
            best_judgement = self._compare_single_pattern(
                candidate_patterns[0], new_code, new_ast, context
            )

        return best_match, best_judgement or SemanticJudgement(
            is_equivalent=False,
            confidence=0.0,
            reasoning="No judgement could be made",
            structural_match=False,
            functional_match=False,
            risk_assessment="Unknown"
        )

    def _compare_single_pattern(
        self,
        pattern: CanonEntry,
        new_code: str,
        new_ast: Dict,
        context: Optional[str] = None
    ) -> SemanticJudgement:
        """Compare a single pattern against new code using LLM."""

        # Prepare the comparison prompt
        prompt = self._build_comparison_prompt(
            pattern, new_code, new_ast, context)

        try:
            # Get structured judgement from LLM
            judgement = self.llm.chat.completions.create(
                model=self.model,
                response_model=SemanticJudgement,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert Python code analyst specializing in semantic equivalence.

                        Your task is to determine if a retrieved code pattern is semantically equivalent
                        to new code that needs validation. Consider:

                        1. Structural equivalence (AST similarity)
                        2. Functional equivalence (does it do the same thing)
                        3. Context appropriateness
                        4. Risk assessment if applied

                        Be conservative - if unsure, mark as not equivalent.
                        Provide detailed reasoning for your decision."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1  # Low temperature for consistent judgements
            )

            logger.debug(
                f"LLM Judgement: {judgement.is_equivalent} (confidence: {judgement.confidence})")
            return judgement

        except Exception as e:
logger.error(f"Failed to get LLM judgement: {e}")
            return SemanticJudgement(
                is_equivalent=False,
                confidence=0.0,
                reasoning=f"LLM error: {str(e)}",
                structural_match=False,
                functional_match=False,
                risk_assessment="Unknown - LLM error"
            )

    def _build_comparison_prompt(
        self,
        pattern: CanonEntry,
        new_code: str,
        new_ast: Dict,
        context: Optional[str] = None
    ) -> str:
        """Build the comparison prompt for the LLM."""

        prompt = f"""# Code Pattern Comparison

## Retrieved Pattern
**Policy Key:** {pattern.policy_key}
**Success Rate:** {pattern.get_success_rate():.2%}
**Risk Score:** {pattern.risk_score}
**Latency:** {pattern.latency_ms}ms

### Pattern AST:
json
{json.dumps(pattern.ast_json, indent=2)[:2000]}...


### Pattern Metadata:
- Success Count: {pattern.success_count}
- Failure Count: {pattern.failure_count}
- Project Tag: {pattern.project_tag}
- Last Validated: {pattern.last_validated.isoformat()}
"""

        if pattern.metadata.get('meta_prompt'):
            prompt += f"\n### Learned from Failures:\n{pattern.metadata['meta_prompt']}\n"

        prompt += f"""

## New Code for Validation

{new_code}


### New Code AST:
json
{json.dumps(new_ast, indent=2)[:2000]}...

"""

        if context:
            prompt += f"""
## Context
{context}
"""

        prompt += """

## Task
Determine if the retrieved pattern is semantically equivalent to the new code.
Consider whether applying the same validation/fix would be appropriate.

Pay special attention to:
1. Are the code structures fundamentally the same?
2. Would the same Canon rule apply?
3. Is the pattern's success rate relevant here?
4. Are there any risks in applying this pattern?

Provide your structured judgement.
"""

        return prompt

    def validate_canon_key(
        self,
        pattern: CanonEntry,
        expected_policy_key: str
    ) -> SemanticJudgement:
        """
        Validate if a pattern matches the expected policy key.

        This is used to ensure retrieved patterns are relevant to the specific
        Canon rule being evaluated.
        """
        prompt = f"""# Policy Key Validation

## Pattern
**Pattern Policy Key:** {pattern.policy_key}
**Expected Policy Key:** {expected_policy_key}

## Pattern Details
- Success Rate: {pattern.get_success_rate():.2%}
- Risk Score: {pattern.risk_score}
- Project: {pattern.project_tag}

## Task
Determine if this pattern is relevant for the expected policy key.
Consider if the validation logic would be appropriate.
"""

        try:
            judgement = self.llm.chat.completions.create(
                model=self.model,
                response_model=SemanticJudgement,
                messages=[
                    {
                        "role": "system",
                        "content": "You are validating Canon rule relevance. Be strict about policy key matching."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )

            return judgement

        except Exception as e:
logger.error(f"Failed to validate policy key: {e}")
            return SemanticJudgement(
                is_equivalent=False,
                confidence=0.0,
                reasoning=f"Validation error: {str(e)}",
                structural_match=False,
                functional_match=False,
                risk_assessment="Unknown"
            )


# Singleton instance
_judger = None


def get_judger() -> LLMJudger:
    """Get the global LLM Judger instance."""
    global _judger
    if _judger is None:
        _judger = LLMJudger()
    return _judger
