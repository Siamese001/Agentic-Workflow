"""Prompt Planning Orchestrator - Coordinates prompt engineering and governance operations.

This orchestrator manages the planning phase for prompt operations,
including template selection, parameter optimization, and compliance checks.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Types of prompts for different use cases."""
    GENERATION = "generation"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    SUMMARIZATION = "summarization"
    TRANSFORMATION = "transformation"
    QUESTION_ANSWERING = "question_answering"


class PromptComplexity(Enum):
    """Complexity levels for prompt planning."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ADVANCED = "advanced"


@dataclass
class PromptTemplate:
    """Prompt template definition."""
    id: str
    name: str
    template: str
    prompt_type: PromptType
    complexity: PromptComplexity
    parameters: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptPlanningConfig:
    """Configuration for prompt planning orchestrator."""
    enable_template_optimization: bool = True
    enable_compliance_checking: bool = True
    enable_parameter_tuning: bool = True
    max_template_variants: int = 5
    default_temperature: float = 0.7
    log_level: str = "INFO"


@dataclass
class PromptPlanningResult:
    """Result of prompt planning orchestration."""
    success: bool
    optimized_templates: List[PromptTemplate] = field(default_factory=list)
    selected_template: Optional[PromptTemplate] = None
    parameter_recommendations: Dict[str, Any] = field(default_factory=dict)
    compliance_results: Dict[str, Any] = field(default_factory=dict)
    performance_estimates: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptPlanningOrchestrator:
    """Orchestrator for planning prompt engineering operations."""

    def __init__(self, config: Optional[PromptPlanningConfig] = None):
        self.config = config or PromptPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, prompt_request: Dict[str, Any]) -> PromptPlanningResult:
        """Execute the prompt planning orchestration.
        
        Args:
            prompt_request: Dictionary containing prompt requirements and context
            
        Returns:
            PromptPlanningResult: Complete planning result with optimized templates
        """
        self.logger.info(f"Starting prompt planning for request: {prompt_request.get('task_type', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(prompt_request)
            
            # Generate base template candidates
            base_templates = self._generate_template_candidates(prompt_request)
            
            # Optimize templates if enabled
            optimized_templates = []
            if self.config.enable_template_optimization:
                optimized_templates = self._optimize_templates(base_templates, prompt_request)
            else:
                optimized_templates = base_templates
            
            # Select best template
            selected_template = self._select_best_template(optimized_templates, prompt_request)
            
            # Generate parameter recommendations
            parameter_recommendations = self._generate_parameters(selected_template, prompt_request)
            
            # Perform compliance checks
            compliance_results = {}
            if self.config.enable_compliance_checking:
                compliance_results = self._check_compliance(selected_template, prompt_request)
            
            # Estimate performance
            performance_estimates = self._estimate_performance(selected_template, parameter_recommendations)
            
            result = PromptPlanningResult(
                success=True,
                optimized_templates=optimized_templates,
                selected_template=selected_template,
                parameter_recommendations=parameter_recommendations,
                compliance_results=compliance_results,
                performance_estimates=performance_estimates,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "task_type": prompt_request.get("task_type"),
                    "template_count": len(optimized_templates),
                    "orchestrator": "PromptPlanningOrchestrator"
                }
            )
            
            self.logger.info(f"Successfully planned prompt with {len(optimized_templates)} template variants")
            return result
            
        except Exception as e:
            self.logger.error(f"Prompt planning failed: {str(e)}")
            return PromptPlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "PromptPlanningOrchestrator"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate prompt planning request."""
        if not request:
            raise ValueError("Prompt request cannot be empty")
        
        if "task_type" not in request:
            raise ValueError("Task type is required in prompt request")
        
        if "context" not in request:
            raise ValueError("Context is required in prompt request")

    def _generate_template_candidates(self, request: Dict[str, Any]) -> List[PromptTemplate]:
        """Generate base template candidates based on request."""
        task_type = request.get("task_type", "generation")
        
        # Map task types to prompt types
        type_mapping = {
            "generate": PromptType.GENERATION,
            "classify": PromptType.CLASSIFICATION,
            "extract": PromptType.EXTRACTION,
            "summarize": PromptType.SUMMARIZATION,
            "transform": PromptType.TRANSFORMATION,
            "qa": PromptType.QUESTION_ANSWERING
        }
        
        prompt_type = type_mapping.get(task_type.lower(), PromptType.GENERATION)
        
        # Generate base templates
        templates = []
        for i in range(3):  # Generate 3 base variants
            template = PromptTemplate(
                id=f"template_{i+1}",
                name=f"{task_type}_template_{i+1}",
                template=f"Base template for {task_type} - Variant {i+1}",
                prompt_type=prompt_type,
                complexity=PromptComplexity.MODERATE,
                parameters={"temperature": self.config.default_temperature},
                examples=[],
                constraints={"max_tokens": 1000}
            )
            templates.append(template)
        
        return templates

    def _optimize_templates(self, templates: List[PromptTemplate], request: Dict[str, Any]) -> List[PromptTemplate]:
        """Optimize templates based on request context."""
        optimized = []
        
        for template in templates:
            # Create optimized variants
            for complexity in [PromptComplexity.SIMPLE, PromptComplexity.MODERATE, PromptComplexity.COMPLEX]:
                variant = PromptTemplate(
                    id=f"{template.id}_{complexity.value}",
                    name=f"{template.name}_{complexity.value}",
                    template=template.template.replace("Base", f"{complexity.value.title()}"),
                    prompt_type=template.prompt_type,
                    complexity=complexity,
                    parameters=template.parameters.copy(),
                    examples=template.examples.copy(),
                    constraints=template.constraints.copy()
                )
                optimized.append(variant)
        
        return optimized[:self.config.max_template_variants]

    def _select_best_template(self, templates: List[PromptTemplate], request: Dict[str, Any]) -> Optional[PromptTemplate]:
        """Select the best template based on request requirements."""
        if not templates:
            return None
        
        # Simple selection based on complexity preference
        complexity_preference = request.get("complexity_preference", "moderate")
        
        for template in templates:
            if template.complexity.value == complexity_preference:
                return template
        
        # Fallback to first template
        return templates[0]

    def _generate_parameters(self, template: Optional[PromptTemplate], request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parameter recommendations for the selected template."""
        if not template:
            return {}
        
        base_params = {
            "temperature": self.config.default_temperature,
            "max_tokens": 1000,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        # Adjust based on complexity
        if template.complexity == PromptComplexity.SIMPLE:
            base_params["temperature"] = 0.3
            base_params["max_tokens"] = 500
        elif template.complexity == PromptComplexity.COMPLEX:
            base_params["temperature"] = 0.9
            base_params["max_tokens"] = 2000
        elif template.complexity == PromptComplexity.ADVANCED:
            base_params["temperature"] = 1.0
            base_params["max_tokens"] = 3000
        
        return base_params

    def _check_compliance(self, template: Optional[PromptTemplate], request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform compliance checks on the selected template."""
        if not template:
            return {"compliant": False, "reason": "No template selected"}
        
        # Simple compliance checks
        checks = {
            "has_template": bool(template.template),
            "has_valid_type": template.prompt_type in PromptType,
            "has_valid_complexity": template.complexity in PromptComplexity,
            "within_token_limit": template.constraints.get("max_tokens", 1000) <= 4000
        }
        
        return {
            "compliant": all(checks.values()),
            "checks": checks,
            "warnings": [k for k, v in checks.items() if not v]
        }

    def _estimate_performance(self, template: Optional[PromptTemplate], params: Dict[str, Any]) -> Dict[str, float]:
        """Estimate performance metrics for the template."""
        if not template:
            return {}
        
        # Simple performance estimates based on complexity and parameters
        base_score = 0.8
        
        # Adjust for complexity
        complexity_multipliers = {
            PromptComplexity.SIMPLE: 0.7,
            PromptComplexity.MODERATE: 0.8,
            PromptComplexity.COMPLEX: 0.9,
            PromptComplexity.ADVANCED: 0.95
        }
        
        score = base_score * complexity_multipliers.get(template.complexity, 0.8)
        
        # Adjust for temperature
        temp = params.get("temperature", 0.7)
        if temp < 0.3:
            score *= 0.9  # Too deterministic
        elif temp > 0.9:
            score *= 0.85  # Too random
        
        return {
            "quality_score": min(score, 1.0),
            "latency_estimate": 1.0 + (params.get("max_tokens", 1000) / 1000),
            "cost_estimate": params.get("max_tokens", 1000) / 1000,
            "reliability_score": 0.9
        }


# Factory function for easy instantiation
def create_prompt_planning_orchestrator(
    enable_template_optimization: bool = True,
    enable_compliance_checking: bool = True,
    **kwargs
) -> PromptPlanningOrchestrator:
    """Create a configured prompt planning orchestrator."""
    config = PromptPlanningConfig(
        enable_template_optimization=enable_template_optimization,
        enable_compliance_checking=enable_compliance_checking,
        **kwargs
    )
    return PromptPlanningOrchestrator(config)


# Convenience function for direct usage
def plan_prompt_engineering(
    task_type: str,
    context: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan prompt engineering from simple parameters.
    
    Args:
        task_type: Type of task (generate, classify, extract, etc.)
        context: Context information for the prompt
        config: Optional configuration overrides
        
    Returns:
        Dict: Planning result with templates and recommendations
    """
    # Build request
    request = {
        "task_type": task_type,
        "context": context,
        "complexity_preference": context.get("complexity", "moderate")
    }
    
    # Create orchestrator and execute
    orchestrator_config = PromptPlanningConfig(**config) if config else None
    orchestrator = PromptPlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "optimized_templates": [
            {
                "id": t.id,
                "name": t.name,
                "template": t.template,
                "prompt_type": t.prompt_type.value,
                "complexity": t.complexity.value,
                "parameters": t.parameters,
                "examples": t.examples,
                "constraints": t.constraints
            }
            for t in result.optimized_templates
        ],
        "selected_template": {
            "id": result.selected_template.id,
            "name": result.selected_template.name,
            "template": result.selected_template.template,
            "prompt_type": result.selected_template.prompt_type.value,
            "complexity": result.selected_template.complexity.value
        } if result.selected_template else None,
        "parameter_recommendations": result.parameter_recommendations,
        "compliance_results": result.compliance_results,
        "performance_estimates": result.performance_estimates,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }


if __name__ == "__main__":
    # Example usage
    example_request = {
        "task_type": "generate",
        "context": {
            "domain": "customer_service",
            "complexity": "moderate",
            "language": "english"
        }
    }
    
    result = plan_prompt_engineering(
        task_type="generate",
        context=example_request["context"]
    )
    print(f"Prompt planning result: {result}")