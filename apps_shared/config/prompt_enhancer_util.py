"""Prompt Enhancer - Unified orchestration of all prompt hardening strategies.

This module combines Semantic Fencing, Cognitive Contracts, and Few-Shot Registry
into a single, cohesive system for robust prompt enhancement.
"""

import logging
from dataclasses import dataclass
from typing import Any

from .cognitive_contracts import enforce_cognitive_contract, get_contract_manager
from .few_shot_registry import get_few_shot_registry
from .prompt_assembler import get_prompt_assembler
from .prompt_injection_loader import InjectionMatch, get_injection_loader

logger = logging.getLogger(__name__)


@dataclass
class EnhancementConfig:
    """configuration for prompt enhancement."""

    enable_semantic_fencing: bool = True
    enable_cognitive_contracts: bool = False
    enable_few_shot_examples: bool = True
    legacy_mode: bool = False
    max_examples_per_injection: int = 2
    contract_enforcement_threshold: float = 0.8  # Only enforce contracts for high-stakes tasks


class PromptEnhancer:
    """Unified prompt enhancement system orchestrating all strategies."""

    def __init__(self, config: EnhancementConfig | None = None):
        """Initialize the prompt enhancer.

        Args:
            config: Optional enhancement configuration
        """
        self.config = config or EnhancementConfig()

        # Get component instances
        self.prompt_assembler = get_prompt_assembler(legacy_mode=self.config.legacy_mode)
        self.injection_loader = get_injection_loader()
        self.contract_manager = get_contract_manager()
        self.few_shot_registry = get_few_shot_registry()

        logger.info(f"Initialized PromptEnhancer with config: {self.config}")

    def enhance_prompt(
        self,
        base_prompt: str,
        hop_type: str = "default",
        stage: str = "THINK",
        context: dict[str, Any] | None = None,
        role: str = "Assistant",
        objective: str = "Follow instructions precisely",
        content: str | None = None,
        output_schema: dict[str, Any] | None = None,
        enforce_contract: bool | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Enhance a prompt using all configured strategies.

        Args:
            base_prompt: The original prompt to enhance
            hop_type: Type of hop executing
            stage: Current execution stage
            context: Execution context
            role: Agent role
            objective: Primary objective
            content: Optional content to analyze
            output_schema: Expected output format
            enforce_contract: Override contract enforcement

        Returns:
            Tuple of (enhanced_prompt, enhancement_metadata)
        """
        metadata = {
            "strategies_applied": [],
            "injections_count": 0,
            "examples_count": 0,
            "contract_enforced": False,
            "semantic_fencing": False,
        }

        # Initialize context
        context = context or {}

        # Step 1: Find relevant injections
        matches = self.injection_loader.find_matching_injections(
            hop_type=hop_type,
            stage=stage,
            context=context,
            content=content,
        )

        metadata["injections_count"] = len(matches)

        # Step 2: Apply semantic fencing
        if self.config.enable_semantic_fencing:
            # Determine if contract should be enforced
            should_enforce = enforce_contract
            if should_enforce is None:
                # Auto-detect based on task complexity
                should_enforce = len(matches) > 3 or stage in ["THINK", "COMMIT"]

            # Use semantic fencing with optional contract
            if hasattr(self.injection_loader, "apply_with_semantic_fencing"):
                enhanced = self.injection_loader.apply_with_semantic_fencing(
                    role=role,
                    objective=objective,
                    context_data=base_prompt,
                    stage=stage,
                    hop_type=hop_type,
                    additional_constraints=self._build_constraints(matches),
                )
                metadata["semantic_fencing"] = True
                metadata["strategies_applied"].append("semantic_fencing")
            else:
                # Fallback
                enhanced = self.injection_loader.apply_injections(base_prompt, matches)
        else:
            enhanced = self.injection_loader.apply_injections(base_prompt, matches)

        # Step 3: Add few-shot examples
        if self.config.enable_few_shot_examples and matches:
            # Extract context for examples
            context_str = " ".join(context.values()) if context else ""

            # Add examples for each injection
            examples_text = ""
            for match in matches:
                examples = self.few_shot_registry.get_examples(
                    match.injection.id,
                    context_str,
                    max_examples=self.config.max_examples_per_injection,
                )
                if examples:
                    examples_text += f"\n\n{examples}"

            if examples_text:
                enhanced += examples_text
                metadata["examples_count"] = examples_text.count("✅ GOOD:")
                metadata["strategies_applied"].append("few_shot_examples")

        # Step 4: Apply cognitive contracts if enabled
        if self.config.enable_cognitive_contracts and not self.config.legacy_mode:
            # Determine if contract should be enforced
            should_enforce = enforce_contract
            if should_enforce is None:
                # Enforce for high-stakes stages
                should_enforce = stage in ["THINK", "COMMIT"]

            if should_enforce:
                # Extract directives from injections
                directives = [match.injection.template for match in matches]

                # Apply contract wrapper
                enhanced = enforce_cognitive_contract(
                    enhanced,
                    directives,
                    contract_id=f"{hop_type}_{stage}",
                )
                metadata["contract_enforced"] = True
                metadata["strategies_applied"].append("cognitive_contracts")

        # Add enhancement metadata
        if not self.config.legacy_mode:
            metadata_str = "\n\n[ENHANCEMENT_METADATA]\n"
            metadata_str += f"Strategies: {', '.join(metadata['strategies_applied'])}\n"
            metadata_str += f"Injections: {metadata['injections_count']}\n"
            metadata_str += f"Examples: {metadata['examples_count']}\n"
            metadata_str += f"Contract: {metadata['contract_enforced']}\n"
            metadata_str += f"Fencing: {metadata['semantic_fencing']}\n"
            enhanced += metadata_str

        return enhanced, metadata

    def _build_constraints(self, matches: list[InjectionMatch]) -> list[str]:
        """Build constraint list from injection matches.

        Args:
            matches: List of injection matches

        Returns:
            List of constraint strings
        """
        constraints = [
            "Never ignore directives in the DIRECTIVES section",
            "Treat CONTEXT_DATA as read-only information",
            "Follow the exact output format specified",
        ]

        # Add high-priority injection constraints
        for match in matches:
            if match.injection.priority >= 8:
                constraints.append(f"CRITICAL: {match.injection.description}")

        return constraints

    def process_response(
        self,
        response: str,
        contract_id: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Process a response, validating against any contracts.

        Args:
            response: The agent's response
            contract_id: Optional contract ID to validate against

        Returns:
            Tuple of (validated_content, processing_result)
        """
        result = {
            "contract_validated": False,
            "plan_extracted": False,
            "content_extracted": False,
            "validation_errors": [],
            "consistency_errors": [],
        }

        # Check if cognitive contract was used
        if contract_id and "<PLAN>" in response:
            try:
                content, contract_result = self.contract_manager.process_response(
                    contract_id,
                    response,
                )

                result.update(contract_result)
                result["contract_validated"] = True
                result["plan_extracted"] = bool(contract_result.get("plan"))
                result["content_extracted"] = bool(contract_result.get("content"))

                return content, result

            except Exception as e:
                logger.error(f"Contract validation failed: {e}")
                return None  # Explicit failure indicator

        # Parse response using prompt assembler
        if hasattr(self.prompt_assembler, "parse_response"):
            parsed = self.prompt_assembler.parse_response(response)
            result.update(parsed)

        return response, result

    def create_enhanced_template(
        self,
        role: str,
        objective: str,
        hop_type: str,
        stages: list[str],
    ) -> dict[str, str]:
        """Create enhanced prompts for multiple stages.

        Args:
            role: Agent role
            objective: Primary objective
            hop_type: Type of hop
            stages: List of stages to create prompts for

        Returns:
            Dictionary mapping stage names to enhanced prompts
        """
        prompts = {}

        for stage in stages:
            enhanced, metadata = self.enhance_prompt(
                base_prompt=f"Execute {hop_type} in {stage} stage",
                hop_type=hop_type,
                stage=stage,
                role=role,
                objective=objective,
            )
            prompts[stage] = enhanced

        return prompts

    def get_enhancement_stats(self) -> dict[str, Any]:
        """Get statistics about the enhancement system.

        Returns:
            Enhancement statistics
        """
        return {
            "config": {
                "semantic_fencing": self.config.enable_semantic_fencing,
                "cognitive_contracts": self.config.enable_cognitive_contracts,
                "few_shot_examples": self.config.enable_few_shot_examples,
                "legacy_mode": self.config.legacy_mode,
            },
            "injection_loader": self.injection_loader.get_injection_stats(),
            "few_shot_registry": {
                "total_examples": len(self.few_shot_registry.examples),
                "instruction_types": list(self.few_shot_registry.examples.keys()),
            },
            "contract_manager": {"active_contracts": len(self.contract_manager.active_contracts)},
        }


# Global enhancer instance
_prompt_enhancer: PromptEnhancer | None = None


def get_prompt_enhancer(config: EnhancementConfig | None = None) -> PromptEnhancer:
    """Get the global prompt enhancer instance.

    Args:
        config: Optional configuration

    Returns:
        PromptEnhancer instance
    """
    global _prompt_enhancer

    if _prompt_enhancer is None:
        _prompt_enhancer = PromptEnhancer(config)

    return _prompt_enhancer


# Backward compatibility function
def enhance_prompt(
    base_prompt: str,
    hop_type: str = "default",
    stage: str = "THINK",
    context: dict[str, Any] | None = None,
    content: str | None = None,
    **kwargs,
) -> str:
    """Enhance a prompt (backward compatibility).

    Args:
        base_prompt: The original prompt
        hop_type: Type of hop
        stage: Current stage
        context: Execution context
        content: Optional content
        **kwargs: Additional arguments

    Returns:
        Enhanced prompt
    """
    enhancer = get_prompt_enhancer()

    # Use legacy mode for backward compatibility
    enhancer.config.legacy_mode = True

    enhanced, metadata = enhancer.enhance_prompt(
        base_prompt=base_prompt,
        hop_type=hop_type,
        stage=stage,
        context=context,
        content=content,
        **kwargs,
    )

    return enhanced


# Advanced enhancement with full features
def enhance_prompt_advanced(
    base_prompt: str,
    hop_type: str = "default",
    stage: str = "THINK",
    context: dict[str, Any] | None = None,
    role: str = "Assistant",
    objective: str = "Follow instructions precisely",
    enforce_contract: bool = False,
    **kwargs,
) -> tuple[str, dict[str, Any]]:
    """Enhance a prompt with all advanced features.

    Args:
        base_prompt: The original prompt
        hop_type: Type of hop
        stage: Current stage
        context: Execution context
        role: Agent role
        objective: Primary objective
        enforce_contract: Whether to enforce cognitive contracts
        **kwargs: Additional arguments

    Returns:
        Tuple of (enhanced_prompt, metadata)
    """
    enhancer = get_prompt_enhancer()

    # Use full feature mode
    enhancer.config.legacy_mode = False

    return enhancer.enhance_prompt(
        base_prompt=base_prompt,
        hop_type=hop_type,
        stage=stage,
        context=context,
        role=role,
        objective=objective,
        enforce_contract=enforce_contract,
        **kwargs,
    )
