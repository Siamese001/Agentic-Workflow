import re
from typing import Callable, Any, Dict, List, Optional
from pydantic import BaseModel
import instructor
from openai import OpenAI
import os
import logging


logger = logging.getLogger(__name__)
class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    fixed_content: Optional[str] = None

class AutoRemediator:
    def __init__(self):
        # Lightweight client for fast fixes
        self.client = instructor.patch(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        self.model = "gpt-4o-mini" # Cheap & fast for remediation

    def validate_and_fix(
        self,
        content: str,
        validators: Dict[str, Callable[[str], bool]],
        fix_strategies: Dict[str, str], # Map error_name -> strategy ('regex' or 'llm')
        max_retries: int = 3
    ) -> ValidationResult:

        current_content = content

        for attempt in range(max_retries + 1):
            errors = []

            # 1. Run all validators
            for check_name, validator_func in validators.items():
                if not validator_func(current_content):
                    errors.append(check_name)

            # Success condition
            if not errors:
                return ValidationResult(is_valid=True, errors=[], fixed_content=current_content)

            # If we are out of retries, fail
            if attempt == max_retries:
                return ValidationResult(is_valid=False,
                    errors=errors,
                    fixed_content=current_content)

            # 2. Attempt Remediation
            logger.error(f"🔧 Auto-Remediator: Fixing {errors} (Attempt {attempt+1}/{max_retries})")
            current_content = self._apply_fixes(current_content, errors, fix_strategies)

        return ValidationResult(is_valid=False, errors=errors, fixed_content=current_content)

    def _apply_fixes(self, content: str, errors: List[str], strategies: Dict[str, str]) -> str:
        """Applies regex or LLM fixes based on error type."""
        new_content = content

        for error in errors:
            strategy = strategies.get(error)

            if not strategy:
                continue

            # Strategy: Regex Fix (defined as "regex:PATTERN:REPLACEMENT")
            if strategy.startswith("regex:"):
                _, pattern, replacement = strategy.split(":", 2)
                new_content = re.sub(pattern, replacement, new_content)

            # Strategy: LLM Fix (defined as "llm:INSTRUCTION")
            elif strategy.startswith("llm:"):
                _, instruction = strategy.split(":", 1)
                new_content = self._llm_rewrite(new_content, instruction)

        return new_content

    def _llm_rewrite(self, content: str, instruction: str) -> str:
        """Calls a cheap model to fix specific semantic issues."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                    "content": f"You are a text editor.
                        . Fix the text below.
                        . Requirement: {instruction}.
                        . Output ONLY the fixed text.
                        ."},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content.strip()

# --- Example Usage Logic (to place in your main script) ---
# remediator = AutoRemediator()
# result = remediator.validate_and_fix(
#    content=generated_bullet_points,
#    validators={
#        "ends_with_period": lambda x: x.strip().endswith("."),
#        "no_passive_voice": lambda x: " was " not in x
#    },
#    fix_strategies={
#        "ends_with_period": "regex:$:.",  # Append dot at end
#        "no_passive_voice": "llm:Rewrite to active voice"
#    }
# )
