"""Safety guard stack agents."""

import json
import re
# import scripts.check_canonical_structure  # TODO: Replace with sovereign equivalent
from typing import Any, Dict

# from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel, Field  # TODO: Replace with sovereign equivalent

# Stub classes for missing dependencies (TODO: Replace with sovereign equivalents)
class BaseAgent:
    """Stub for BaseAgent - TODO: Replace with sovereign equivalent"""
    def __init__(self, context, debug_mode=False):
        self.context = context
        self.debug_mode = debug_mode
    
    def log_info(self, msg):
        print(f"INFO: {msg}")

class BaseModel:
    """Stub for BaseModel - TODO: Replace with sovereign equivalent"""
    pass

def Field(*args, **kwargs):
    """Stub for Field - TODO: Replace with sovereign equivalent"""
    return None

# Stub classes for Constitutional AI types (TODO: Replace with sovereign equivalents)
class RuleType:
    """Stub for RuleType - TODO: Replace with sovereign equivalent"""
    pass

class RuleSeverity:
    """Stub for RuleSeverity - TODO: Replace with sovereign equivalent"""
    pass

class ViolationType:
    """Stub for ViolationType - TODO: Replace with sovereign equivalent"""
    pass

class RuleAction:
    """Stub for RuleAction - TODO: Replace with sovereign equivalent"""
    pass

class ConstitutionalRule:
    """Stub for ConstitutionalRule - TODO: Replace with sovereign equivalent"""
    pass

class ViolationReport:
    """Stub for ViolationReport - TODO: Replace with sovereign equivalent"""
    pass

class ConstitutionalReviewResult:
    """Stub for ConstitutionalReviewResult - TODO: Replace with sovereign equivalent"""
    pass

def track_metrics(name):
    """Stub decorator for track_metrics - TODO: Replace with sovereign equivalent"""
    def decorator(func):
        return func
    return decorator

def detect_bias(context, text, workflow_id=""):
    """Stub for detect_bias - TODO: Replace with sovereign equivalent"""
    return {"bias_detected": False, "score": 0.0}



class PIISanitizerAgent(BaseAgent):
    """Performs local PII detection using regex heuristics."""

    PII_PATTERNS = {
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "PHONE": re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b"),
        "NAME": re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"),
    }

    @track_metrics("run_pii_sanitizer")
    def run(self, resume: Dict[str, object]) -> Dict[str, object]:
        self.log_info("Sanitizing PII (local regex processing)...")
        sanitized_resume = json.loads(json.dumps(resume))

        def sanitize_node(node: Any) -> Any:
            if isinstance(node, dict):
                return {k: sanitize_node(v) for k, v in node.items()}
            if isinstance(node, list):
                return [sanitize_node(item) for item in node]
            if isinstance(node, str):
                return self._sanitize_text(node)
            return node

        sanitized = sanitize_node(sanitized_resume)
        self.log_info("PII sanitization complete.")
        return sanitized

    def _sanitize_text(self, text: str) -> str:
        for pii_type, pattern in self.PII_PATTERNS.items():
            text = pattern.sub(f"[{pii_type}_REDACTED]", text)
        return text


class BiasDetectorAgent(BaseAgent):
    """Runs local bias detection with dynamic constitution rules."""

    @track_metrics("run_bias_detector")
    def run(self, text: str, workflow_id: str = "") -> Dict[str, object]:
        self.log_info("Detecting bias (local processing with dynamic rules)...")
        result = detect_bias(self.context, text, workflow_id)

        if workflow_id:
            self.log_feedback(
                workflow_id,
                "bias_detection",
                "warning" if result["bias_detected"] else "success",
                {"patterns_found": len(result.get("patterns", []))},
            )

        return result


class PromptInjectionDetectorAgent(BaseAgent):
    """Detects prompt-injection attacks."""

    class PIDetectionOutput(BaseModel):
        injection_detected: bool = Field(..., description="True if an attack was detected")
        reason: str = Field(..., description="Explanation for the detection")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the detection")

    @track_metrics("run_pi_detector")
    async def run_async(self, user_input: str, workflow_id: str) -> Dict[str, object]:
        self.log_info("Detecting prompt injection...")

        if not self.config.agent_stacks.enable_prompt_injection_detection:
            self.log_warning("Prompt injection detection is disabled.")
            return {
                "injection_detected": False,
                "reason": "Detector disabled",
                "confidence": 0.0,
            }

        client = self.get_model_client("prompt_injection_model")
        prompt_template = self.prompt_manager.get_template("prompt_injection_detector")

        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"user_input": user_input},
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.prompt_injection_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            self.PIDetectionOutput,
        )
        if error:
            self.log_error(f"PromptInjectionDetector failed validation: {error}")
            return {
                "injection_detected": True,
                "reason": f"Detector validation failed: {error}",
                "confidence": 1.0,
            }

        if validated_output.injection_detected:
            self.log_warning(
                f"PROMPT INJECTION DETECTED (Confidence: {validated_output.confidence}): {validated_output.reason}"
            )

        return validated_output.model_dump()


class ConstitutionalReviewerAgent(BaseAgent):
    """Performs final constitutional review of the output."""

    @track_metrics("run_constitutional_review")
    async def run_async(
        self,
        final_draft: str,
        workflow_id: str,
    ) -> ConstitutionalReviewResult:
        self.log_info("Running final constitutional review...")

        if not self.config.agent_stacks.enable_constitutional_review:
            self.log_warning("Constitutional review is disabled. Passing by default.")
            return ConstitutionalReviewResult(
                review_passed=True,
                violations_found=[],
                feedback="Review disabled",
            )

        client = self.get_model_client("constitutional_review_model")
        prompt_template = self.prompt_manager.get_template("constitutional_review")

        rules = self.context.rules_loader.get_constitution_rules()
        constitution_text = json.dumps(rules)

        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"final_draft": final_draft, "constitution": constitution_text},
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.constitutional_review_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            ConstitutionalReviewResult,
        )
        if error:
            self.log_error(
                f"ConstitutionalReviewer failed validation: {error}. Failing open (passing draft)."
            )
            return ConstitutionalReviewResult(
                review_passed=True,
                violations_found=["VALIDATION_ERROR"],
                feedback=error,
            )

        if not validated_output.review_passed:
            self.log_warning(
                f"CONSTITUTIONAL REVIEW FAILED: {validated_output.violations_found}"
            )

        return validated_output
