"""
Prompt Builder - Centralized prompt construction with layering enforcement.

Section 11: Prompt Builder - Provides centralized prompt building with
layering enforcement (Framing/Context/Reasoning/Tooling/Safety/Output),
prompt diffing, and regression evaluation.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
import logging
import difflib
import hashlib

# Import existing layered injection bundles

logger = logging.getLogger(__name__)


class PromptLayer(str, Enum):
    """Prompt layer enumeration for enforced layering."""
    FRAMING = "framing"
    CONTEXT = "context"
    L1_PLANNING = "l1_planning"
    L2_EXECUTION = "l2_execution"
    L3_ORCHESTRATION = "l3_orchestration"
    L4_MEMORY = "l4_memory"
    L5_SAFETY = "l5_safety"
    REASONING = "reasoning"
    TOOLING = "tooling"
    OUTPUT = "output"


@dataclass
class PromptComponent:
    """Individual prompt component with layer metadata."""
    layer: PromptLayer
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher priority components come first within layer


@dataclass
class PromptBuildResult:
    """Result of prompt building operation."""
    prompt_id: str
    final_prompt: str
    components_used: List[PromptComponent]
    build_metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    build_time_ms: int = 0


@dataclass
class PromptDiff:
    """Result of prompt diffing operation."""
    prompt_id_1: str
    prompt_id_2: str
    similarity_score: float
    added_content: List[str]
    removed_content: List[str]
    modified_content: List[str]
    unified_diff: str


@dataclass
class PromptEvaluation:
    """Result of prompt regression evaluation."""
    prompt_id: str
    baseline_prompt_id: Optional[str]
    quality_score: float
    safety_score: float
    performance_metrics: Dict[str, float]
    regression_detected: bool
    evaluation_details: Dict[str, Any]


class PromptBuilder:
    """
    Centralized prompt builder with enforced layering.

    Provides structured prompt construction using layered injection bundles,
    prompt diffing capabilities, and regression evaluation.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize prompt builder with configuration.

        Args:
            config: Builder configuration including layer ordering and constraints
        """
        self.config = config or {}
        self._layer_order = self._get_default_layer_order()
        self._bundle_cache: Dict[str, Any] = {}

    def _get_default_layer_order(self) -> List[PromptLayer]:
        """Get default layer ordering for prompt construction."""
        return [
            PromptLayer.FRAMING,
            PromptLayer.CONTEXT,
            PromptLayer.L1_PLANNING,
            PromptLayer.L2_EXECUTION,
            PromptLayer.L3_ORCHESTRATION,
            PromptLayer.L4_MEMORY,
            PromptLayer.L5_SAFETY,
            PromptLayer.REASONING,
            PromptLayer.TOOLING,
            PromptLayer.OUTPUT,
        ]

    def build_prompt(
        self,
        components: List[PromptComponent],
        enforce_layering: bool = True,
        allow_cross_layer: bool = False
    ) -> PromptBuildResult:
        """
        Build a prompt from components with layering enforcement.

        Args:
            components: List of prompt components
            enforce_layering: Whether to enforce strict layer ordering
            allow_cross_layer: Whether to allow cross-layer dependencies

        Returns:
            PromptBuildResult with constructed prompt and metadata
        """
        start_time = datetime.now(UTC)

        try:
            # Validate layering if enforced
            if enforce_layering:
                validation_result = self._validate_layering(components, allow_cross_layer)
                if not validation_result["valid"]:
                    return PromptBuildResult(
                        prompt_id="",
                        final_prompt="",
                        components_used=[],
                        success=False,
                        error=validation_result["error"],
                        build_time_ms=int((datetime.now(UTC) - start_time).total_seconds() * 1000)
                    )

            # Sort components by layer order and priority
            sorted_components = self._sort_components(components)

            # Apply injection bundles
            enhanced_components = self._apply_injection_bundles(sorted_components)

            # Construct final prompt
            final_prompt = self._construct_prompt(enhanced_components)

            # Generate prompt ID
            prompt_id = self._generate_prompt_id(final_prompt)

            build_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            return PromptBuildResult(
                prompt_id=prompt_id,
                final_prompt=final_prompt,
                components_used=enhanced_components,
                build_metadata={
                    "layer_enforced": enforce_layering,
                    "components_count": len(components),
                    "layers_used": list(set(comp.layer for comp in components)),
                    "build_timestamp": datetime.now(UTC).isoformat()
                },
                success=True,
                build_time_ms=build_time
            )

        except Exception as e:
            build_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            logger.error(f"Prompt building failed: {str(e)}")

            return PromptBuildResult(
                prompt_id="",
                final_prompt="",
                components_used=[],
                success=False,
                error=str(e),
                build_time_ms=build_time
            )

    def _validate_layering(
        self,
        components: List[PromptComponent],
        allow_cross_layer: bool
    ) -> Dict[str, Any]:
        """
        Validate component layering compliance.

        Args:
            components: Components to validate
            allow_cross_layer: Whether cross-layer dependencies are allowed

        Returns:
            Validation result with validity status and error details
        """
        # Check for proper layer ordering
        layer_indices = {layer: idx for idx, layer in enumerate(self._layer_order)}

        for i, component in enumerate(components):
            if component.layer not in layer_indices:
                return {
                    "valid": False,
                    "error": f"Unknown layer: {component.layer}"
                }

        # If cross-layer is not allowed, check for violations
        if not allow_cross_layer:
            for i in range(len(components) - 1):
                current_idx = layer_indices[components[i].layer]
                next_idx = layer_indices[components[i + 1].layer]

                if next_idx < current_idx:
                    return {
                        "valid": False,
                        "error": f"Layer violation: {components[i + 1].layer} cannot come after {components[i].layer}"
                    }

        return {"valid": True}

    def _sort_components(self, components: List[PromptComponent]) -> List[PromptComponent]:
        """
        Sort components by layer order and priority.

        Args:
            components: Components to sort

        Returns:
            Sorted components
        """
        layer_indices = {layer: idx for idx, layer in enumerate(self._layer_order)}

        return sorted(
            components,
            key=lambda comp: (layer_indices[comp.layer], -comp.priority)
        )

    def _apply_injection_bundles(
        self,
        components: List[PromptComponent]
    ) -> List[PromptComponent]:
        """
        Apply appropriate injection bundles to components.

        Args:
            components: Components to enhance

        Returns:
            Enhanced components with bundle injections applied
        """
        enhanced = []

        for component in components:
            # Get appropriate bundle for layer
            bundle = self._get_bundle_for_layer(component.layer)

            if bundle:
                # Apply bundle enhancement
                enhanced_content = self._apply_bundle_to_component(
                    component, bundle
                )
                enhanced_component = PromptComponent(
                    layer=component.layer,
                    content=enhanced_content,
                    metadata={
                        **component.metadata,
                        "bundle_applied": bundle.__class__.__name__
                    },
                    priority=component.priority
                )
                enhanced.append(enhanced_component)
            else:
                enhanced.append(component)

        return enhanced

    def _get_bundle_for_layer(self, layer: PromptLayer) -> Optional[Any]:
        """Get appropriate injection bundle for layer."""
        # Import here to avoid circular imports
        from .InjectionPolicies.Layered_Injection_Bundles.framing import FramingBundle, FramingType

        # Map layers to bundles (simplified implementation)
        if layer == PromptLayer.FRAMING:
            return FramingBundle(
                bundle_id=f"{layer.value}_bundle",
                framing_type=FramingType.OBJECTIVE,
                templates=[],
                metadata={"layer": layer.value}
            )

        # For other layers, return None for now (can be extended later)
        return None

    def _apply_bundle_to_component(
        self,
        component: PromptComponent,
        bundle: Any
    ) -> str:
        """Apply bundle enhancement to component content."""
        # Simplified bundle application
        if hasattr(bundle, 'apply_framing'):
            return bundle.apply_framing(component.content, component.metadata)
        elif hasattr(bundle, 'apply_context'):
            return bundle.apply_context(component.content, component.metadata)
        else:
            # Default enhancement
            return f"[{component.layer.value.upper()}]\n{component.content}"

    def _construct_prompt(self, components: List[PromptComponent]) -> str:
        """Construct final prompt from components."""
        sections = []

        for component in components:
            if component.content.strip():
                sections.append(component.content.strip())

        return "\n\n".join(sections)

    def _generate_prompt_id(self, prompt: str) -> str:
        """Generate unique ID for prompt."""
        hash_input = f"{prompt}_{datetime.now(UTC).isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def diff_prompts(
        self,
        prompt_1: str,
        prompt_2: str,
        prompt_id_1: Optional[str] = None,
        prompt_id_2: Optional[str] = None
    ) -> PromptDiff:
        """
        Compare two prompts and generate diff.

        Args:
            prompt_1: First prompt
            prompt_2: Second prompt
            prompt_id_1: ID of first prompt (optional)
            prompt_id_2: ID of second prompt (optional)

        Returns:
            PromptDiff with comparison results
        """
        # Generate IDs if not provided
        if not prompt_id_1:
            prompt_id_1 = self._generate_prompt_id(prompt_1)
        if not prompt_id_2:
            prompt_id_2 = self._generate_prompt_id(prompt_2)

        # Split prompts into lines for comparison
        lines_1 = prompt_1.splitlines(keepends=True)
        lines_2 = prompt_2.splitlines(keepends=True)

        # Generate unified diff
        unified_diff = ''.join(difflib.unified_diff(
            lines_1, lines_2,
            fromfile=f"prompt_{prompt_id_1}",
            tofile=f"prompt_{prompt_id_2}",
            lineterm=''
        ))

        # Calculate similarity score
        similarity = difflib.SequenceMatcher(None, prompt_1, prompt_2).ratio()

        # Identify changes
        added = []
        removed = []
        modified = []

        for line in unified_diff.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                added.append(line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                removed.append(line[1:])

        return PromptDiff(
            prompt_id_1=prompt_id_1,
            prompt_id_2=prompt_id_2,
            similarity_score=similarity,
            added_content=added,
            removed_content=removed,
            modified_content=modified,
            unified_diff=unified_diff
        )

    def evaluate_prompt_regression(
        self,
        current_prompt: str,
        baseline_prompt: Optional[str] = None,
        baseline_prompt_id: Optional[str] = None,
        evaluation_metrics: Optional[List[str]] = None
    ) -> PromptEvaluation:
        """
        Evaluate prompt for regression against baseline.

        Args:
            current_prompt: Current prompt to evaluate
            baseline_prompt: Baseline prompt for comparison
            baseline_prompt_id: ID of baseline prompt
            evaluation_metrics: List of metrics to evaluate

        Returns:
            PromptEvaluation with regression analysis
        """
        current_prompt_id = self._generate_prompt_id(current_prompt)

        # Default evaluation metrics
        if not evaluation_metrics:
            evaluation_metrics = ["length", "complexity", "safety", "clarity"]

        # Calculate quality scores (simplified implementation)
        quality_score = self._calculate_quality_score(current_prompt)
        safety_score = self._calculate_safety_score(current_prompt)

        # Performance metrics
        performance_metrics = {
            "length": len(current_prompt),
            "line_count": len(current_prompt.splitlines()),
            "word_count": len(current_prompt.split()),
            "complexity": self._calculate_complexity(current_prompt),
        }

        # Check for regression if baseline provided
        regression_detected = False
        if baseline_prompt:
            diff = self.diff_prompts(baseline_prompt, current_prompt, baseline_prompt_id, current_prompt_id)

            # Simple regression detection
            if diff.similarity_score < 0.8:  # Significant changes
                regression_detected = True

        return PromptEvaluation(
            prompt_id=current_prompt_id,
            baseline_prompt_id=baseline_prompt_id,
            quality_score=quality_score,
            safety_score=safety_score,
            performance_metrics=performance_metrics,
            regression_detected=regression_detected,
            evaluation_details={
                "metrics_evaluated": evaluation_metrics,
                "evaluation_timestamp": datetime.now(UTC).isoformat()
            }
        )

    def _calculate_quality_score(self, prompt: str) -> float:
        """Calculate quality score for prompt (simplified)."""
        # Simple quality metrics
        score = 0.0

        # Length appropriateness
        word_count = len(prompt.split())
        if 50 <= word_count <= 500:
            score += 0.3
        elif 20 <= word_count <= 1000:
            score += 0.2

        # Structure presence
        if '\n' in prompt:  # Has structure
            score += 0.2

        # Clear instructions
        if any(keyword in prompt.lower() for keyword in ['please', 'should', 'must', 'ensure']):
            score += 0.3

        # No obvious issues
        if not prompt.strip().endswith('.'):  # Not just a statement
            score += 0.2

        return min(1.0, score)

    def _calculate_safety_score(self, prompt: str) -> float:
        """Calculate safety score for prompt (simplified)."""
        # Check for potentially unsafe patterns
        unsafe_patterns = [
            'ignore safety', 'bypass', 'override', 'disable',
            'ignore instructions', 'disregard rules'
        ]

        prompt_lower = prompt.lower()
        unsafe_count = sum(1 for pattern in unsafe_patterns if pattern in prompt_lower)

        # High safety score if no unsafe patterns
        if unsafe_count == 0:
            return 1.0
        else:
            return max(0.0, 1.0 - (unsafe_count * 0.2))

    def _calculate_complexity(self, prompt: str) -> float:
        """Calculate complexity score for prompt."""
        # Simple complexity metrics
        word_count = len(prompt.split())
        sentence_count = len(prompt.split('. '))

        if sentence_count == 0:
            return 0.0

        avg_words_per_sentence = word_count / sentence_count
        complexity = min(1.0, avg_words_per_sentence / 20.0)

        return complexity


# =============================================================================
# Convenience Functions
# =============================================================================

def create_prompt_builder(config: Optional[Dict[str, Any]] = None) -> PromptBuilder:
    """Create a new PromptBuilder instance."""
    return PromptBuilder(config)


def build_simple_prompt(
    base_content: str,
    layer: PromptLayer = PromptLayer.CONTEXT,
    metadata: Optional[Dict[str, Any]] = None
) -> PromptBuildResult:
    """Build a simple single-layer prompt."""
    builder = PromptBuilder()
    component = PromptComponent(
        layer=layer,
        content=base_content,
        metadata=metadata or {}
    )
    return builder.build_prompt([component])


__all__ = [
    "PromptBuilder",
    "PromptLayer",
    "PromptComponent",
    "PromptBuildResult",
    "PromptDiff",
    "PromptEvaluation",
    "create_prompt_builder",
    "build_simple_prompt"
]





