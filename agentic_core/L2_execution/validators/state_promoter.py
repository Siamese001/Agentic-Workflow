"""
StatePromoter Validator - Safely promotes SoftState content to HardState.

The StatePromoter validates content from the high-temperature LLM scratchpad
and promotes it to immutable HardState only if it passes validation.
If validation fails, it triggers a self-correction loop.
"""


import logging
import json
from datetime import datetime

from pydantic import BaseModel, ValidationError

    InferenceEngine, InferenceRequest, InferenceMode
)

logger = logging.getLogger(__name__)

class ValidationResult(str, Enum):
    """Possible validation results."""
    PASSED = "passed"
    FAILED = "failed"
    REQUIRES_CORRECTION = "requires_correction"

@dataclass
class PromotionResult:
    """Result of a state promotion attempt."""
    success: bool
    key: str
    validation_result: ValidationResult
    promoted_content: Optional[Any] = None
    error_message: Optional[str] = None
    correction_attempts: int = 0
    execution_time_ms: float = 0.0

@dataclass
class ValidationRule:
    """A validation rule for content promotion."""
    name: str
    validator: Callable[[Any], bool]
    error_message: str
    is_critical: bool = True

class StatePromoter:
    """
    Validates and promotes content from SoftState to HardState.

    The promoter ensures that only validated, schema-compliant content
    """

    def __init__(
        self,
        max_correction_attempts: int = 3,
        enable_self_correction: bool = True,
        inference_engine: Optional[InferenceEngine] = None
    ):
        """Initialize state promoter.

        Args:
            max_correction_attempts: Maximum attempts at self-correction
            enable_self_correction: Enable automatic self-correction loops
            inference_engine: Optional inference engine for corrections
        """
        self.max_correction_attempts = max_correction_attempts
        self.enable_self_correction = enable_self_correction
        self.inference_engine = inference_engine or InferenceEngine()
        self._validation_rules: Dict[str, List[ValidationRule]] = {}
        self._pydantic_schemas: Dict[str, Type[BaseModel]] = {}

        logger.info(
            "state_promoter_initialized",
            extra={
                "max_correction_attempts": max_correction_attempts,
                "self_correction_enabled": enable_self_correction
            }
        )

    def register_validation_rule(self, key: str, rule: ValidationRule) -> None:
        """Register a validation rule for a specific key.

        Args:
            key: The content key to validate
            rule: Validation rule to apply
        """
        if key not in self._validation_rules:
            self._validation_rules[key] = []
        self._validation_rules[key].append(rule)

        logger.debug(
            "validation_rule_registered",
            extra={"key": key, "rule": rule.name, "critical": rule.is_critical}
        )

    def register_pydantic_schema(self, key: str, schema: Type[BaseModel]) -> None:
        """Register a Pydantic schema for content validation.

        Args:
            key: The content key to validate
            schema: Pydantic schema class
        """
        self._pydantic_schemas[key] = schema

        logger.debug(
            "pydantic_schema_registered",
            extra={"key": key, "schema": schema.__name__}
        )

    async def promote(
        """Docstring."""
        self,
        context: SignalContext,
        key: str,
        schema_name: Optional[str] = None
    ) -> PromotionResult:
        """
        Promote content from SoftState to HardState after validation.

        Args:
            context: Signal context containing states
            key: The key in SoftState to promote
            schema_name: Optional schema name for validation

        Returns:
            Promotion result with status and details
        """
        start_time = datetime.utcnow()

        # Check if key exists in SoftState
        if key not in context.soft_state.drafts:
            return PromotionResult(
                success=False,
                key=key,
                validation_result=ValidationResult.FAILED,
                error_message=f"Key '{key}' not found in SoftState"
            )

        content = context.soft_state.drafts[key]
        correction_attempts = 0

        # Validation loop
        while correction_attempts <= self.max_correction_attempts:
            # Validate content
            validation_result = await self._validate_content(
                content, key, schema_name
            )

            if validation_result == ValidationResult.PASSED:
                # Promote to HardState
                success = context.promote_soft_to_hard(key, schema_name)
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                if success:
                    logger.info(
                        "state_promotion_successful",
                        extra={
                            "execution_id": context.hard_state.execution_id,
                            "key": key,
                            "attempts": correction_attempts + 1
                        }
                    )

                    return PromotionResult(
                        success=True,
                        key=key,
                        validation_result=ValidationResult.PASSED,
                        promoted_content=content,
                        correction_attempts=correction_attempts,
                        execution_time_ms=execution_time
                    )

            elif validation_result == ValidationResult.FAILED:
                # Critical validation failure, cannot recover
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                return PromotionResult(
                    success=False,
                    key=key,
                    validation_result=ValidationResult.FAILED,
                    error_message="Critical validation failure",
                    correction_attempts=correction_attempts,
                    execution_time_ms=execution_time
                )

            elif validation_result == ValidationResult.REQUIRES_CORRECTION:
                # Attempt self-correction
                if not self.enable_self_correction:
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    return PromotionResult(
                        success=False,
                        key=key,
                        validation_result=ValidationResult.REQUIRES_CORRECTION,
                        error_message="Self-correction disabled",
                        correction_attempts=correction_attempts,
                        execution_time_ms=execution_time
                    )

                correction_attempts += 1
                if correction_attempts > self.max_correction_attempts:
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    return PromotionResult(
                        success=False,
                        key=key,
                        validation_result=ValidationResult.FAILED,
                        error_message=f"Max correction attempts ({self.max_correction_attempts}) exceeded",


                        correction_attempts=correction_attempts,
                        execution_time_ms=execution_time
                    )

                # Generate correction prompt
                correction_prompt = self._generate_correction_prompt(
                    content, key, schema_name
                )

                # Request correction from LLM
                try:
                    correction_request = InferenceRequest(
                        prompt=correction_prompt,
                        context=context,
                        mode=InferenceMode.VALIDATION,  # Low temperature for corrections
                        temperature_override=0.1  # Very low temp for precise corrections
                    )

                    result = await self.inference_engine.infer(correction_request)

                    # Update content with correction
                    try:
                        corrected_content = json.loads(result.content)
                        content = corrected_content
                        context.soft_state.drafts[key] = content
                        context.soft_state.record_revision(
                            key, context.soft_state.drafts[key], content
                        )
                    except json.JSONDecodeError:
                        # If not JSON, use raw content
                        content = result.content
                        context.soft_state.drafts[key] = content
                        context.soft_state.record_revision(
                            key, context.soft_state.drafts[key], content
                        )

                    logger.info(
                        "self_correction_attempted",
                        extra={
                            "execution_id": context.hard_state.execution_id,
                            "key": key,
                            "attempt": correction_attempts
                        }
                    )

                except Exception as e:
                    logger.error(
                        "self_correction_failed",
                        extra={
                            "execution_id": context.hard_state.execution_id,
                            "key": key,
                            "error": str(e)
                        },
                        exc_info=True
                    )
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    return PromotionResult(
                        success=False,
                        key=key,
                        validation_result=ValidationResult.FAILED,
                        error_message=f"Self-correction failed: {str(e)}",
                        correction_attempts=correction_attempts,
                        execution_time_ms=execution_time
                    )

        # Should not reach here
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        return PromotionResult(
            success=False,
            key=key,
            validation_result=ValidationResult.FAILED,
            error_message="Unexpected error in promotion loop",
            correction_attempts=correction_attempts,
            execution_time_ms=execution_time
        )

    async def _validate_content(
        """Docstring."""
        self,
        content: Any,
        key: str,
        schema_name: Optional[str] = None
    ) -> ValidationResult:
        """Validate content against registered rules and schemas.

        Args:
            content: Content to validate
            key: Content key for rule lookup
            schema_name: Optional schema name for validation

        Returns:
            Validation result
        """
        # Pydantic schema validation
        if key in self._pydantic_schemas:
            try:
                schema = self._pydantic_schemas[key]
                if isinstance(content, dict):
                    schema(**content)
                else:
                    # Try to parse if it's a JSON string
                    parsed = json.loads(content) if isinstance(content, str) else content
                    schema(**parsed)
            except ValidationError as e:
                logger.warning(
                    "pydantic_validation_failed",
                    extra={
                        "key": key,
                        "errors": e.errors()
                    }
                )
                return ValidationResult.REQUIRES_CORRECTION
            except Exception as e:
                logger.error(
                    "schema_validation_error",
                    extra={
                        "key": key,
                        "error": str(e)
                    }
                )
                return ValidationResult.FAILED

        # Custom validation rules
        if key in self._validation_rules:
            for rule in self._validation_rules[key]:
                try:
                    if not rule.validator(content):
                        logger.warning(
                            "validation_rule_failed",
                            extra={
                                "key": key,
                                "rule": rule.name,
                                "critical": rule.is_critical
                            }
                        )
                        return ValidationResult.FAILED if rule.is_critical else ValidationResult.REQ
    UIRES_CORRECTION
                except Exception as e:
                    logger.error(
                        "validation_rule_error",
                        extra={
                            "key": key,
                            "rule": rule.name,
                            "error": str(e)
                        }
                    )
                    return ValidationResult.FAILED

        return ValidationResult.PASSED

    def _generate_correction_prompt(
        self,
        content: Any,
        key: str,
        schema_name: Optional[str] = None
    ) -> str:
        """Generate a prompt for content correction.

        Args:
            content: The invalid content
            key: Content key
            schema_name: Optional schema name

        Returns:
            Correction prompt
        """
        prompt = f"""Please correct the following content to make it valid.

Key: {key}
Schema: {schema_name or 'No specific schema'}

Invalid Content:
{json.dumps(content, indent=2) if isinstance(content, dict) else content}

"""

        # Add schema information if available
        if key in self._pydantic_schemas:
            schema = self._pydantic_schemas[key]
            prompt += f"""
Expected Schema (Pydantic model: {schema.__name__}):
{json.dumps(schema.model_json_schema(), indent=2)}

"""

        # Add failed validation rules
        if key in self._validation_rules:
            prompt += "\nFailed validation rules:\n"
            for rule in self._validation_rules[key]:
                prompt += f"- {rule.name}: {rule.error_message}\n"

        prompt += """
Please provide the corrected content as valid JSON only.
Do not include explanations or additional text.
"""

        return prompt

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of registered validations.

        Returns:
            Dictionary with validation statistics
        """
        return {
            "registered_rules": {
                key: [rule.name for rule in rules]
                for key, rules in self._validation_rules.items()
            },
            "registered_schemas": {
                key: schema.__name__
                for key, schema in self._pydantic_schemas.items()
            },
            "total_rules": sum(len(rules) for rules in self._validation_rules.values()),
            "total_schemas": len(self._pydantic_schemas)
        }

# Factory functions for common validation patterns

def create_email_validator() -> StatePromoter:
    """Create a StatePromoter configured for email validation."""
    promoter = StatePromoter()

    # Email content validation
    promoter.register_validation_rule(
        "email_content",
        ValidationRule(
            name="has_recipient",
            validator=lambda x: isinstance(x, dict) and "recipient" in x,
            error_message="Email must have a recipient",
            is_critical=True
        )
    )

    promoter.register_validation_rule(
        "email_content",
        ValidationRule(
            name="has_subject",
            validator=lambda x: isinstance(x, dict) and "subject" in x,
            error_message="Email must have a subject",
            is_critical=True
        )
    )

    promoter.register_validation_rule(
        "email_content",
        ValidationRule(
            name="subject_length",
            validator=lambda x: len(str(x.get("subject", ""))) <= 200,
            error_message="Subject must be 200 characters or less",
            is_critical=False
        )
    )

    return promoter

def create_resume_validator() -> StatePromoter:
    """Create a StatePromoter configured for resume validation."""
    promoter = StatePromoter()

    # Resume section validation
    promoter.register_validation_rule(
        "experience_section",
        ValidationRule(
            name="has_entries",
            validator=lambda x: isinstance(x, list) and len(x) > 0,
            error_message="Experience section must have at least one entry",
            is_critical=True
        )
    )

    promoter.register_validation_rule(
        "experience_section",
        ValidationRule(
            name="valid_dates",
            validator=lambda x: all(
                isinstance(entry, dict) and "start_date" in entry
                for entry in x
            ),
            error_message="All experience entries must have start dates",
            is_critical=True
        )
    )

    return promoter
