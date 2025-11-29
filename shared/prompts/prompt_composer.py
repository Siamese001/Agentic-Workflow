"""
Prompt Composer - Instructional Injection v5 Framework

Automatically combines prompt layers with hierarchical inheritance support for subatomic agents.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .framing_layer import FramingLayer
from .context_layer import ContextLayer
from .reasoning_layer import ReasoningLayer
from .tooling_layer import ToolingLayer
from .safety_layer import SafetyLayer
from .output_layer import OutputLayer


@dataclass
class AgentProfile:
    """Profile defining which v5 layers and parameters to activate for a subatomic agent."""
    agent_name: str
    agent_type: str  # "content", "structure", "validation", "analysis"
    
    # Layer activation flags
    enable_framing: bool = True
    enable_context: bool = True
    enable_reasoning: bool = True
    enable_tooling: bool = True
    enable_safety: bool = True
    enable_output: bool = True
    
    # Layer-specific parameters
    framing_params: Dict[str, Any] = None
    context_params: Dict[str, Any] = None
    reasoning_params: Dict[str, Any] = None
    tooling_params: Dict[str, Any] = None
    safety_params: Dict[str, Any] = None
    output_params: Dict[str, Any] = None
    
    # Inheritance settings
    inherit_from_parent: bool = True
    parent_modifications: Dict[str, Any] = None


class PromptComposer:
    """Composes complete prompts from v5 framework layers with inheritance support."""
    
    def __init__(self):
        self.layers = {
            'framing': FramingLayer(),
            'context': ContextLayer(),
            'reasoning': ReasoningLayer(),
            'tooling': ToolingLayer(),
            'safety': SafetyLayer(),
            'output': OutputLayer()
        }
        self.profiles = {}
    
    def register_profile(self, profile: AgentProfile) -> None:
        """Register an agent profile for reuse."""
        self.profiles[profile.agent_name] = profile
    
    def compose_prompt(self, profile: AgentProfile, parent_prompt: Optional[str] = None) -> str:
        """Compose complete prompt from agent profile with optional inheritance."""
        prompt_sections = []
        
        # Add inherited parent prompt if specified
        if parent_prompt and profile.inherit_from_parent:
            prompt_sections.append(f"# INHERITED PARENT CONTEXT\n{parent_prompt}\n")
        
        # Compose each enabled layer
        if profile.enable_framing:
            framing_section = self._compose_framing_layer(profile)
            if framing_section:
                prompt_sections.append(f"# FRAMING LAYER\n{framing_section}")
        
        if profile.enable_context:
            context_section = self._compose_context_layer(profile)
            if context_section:
                prompt_sections.append(f"# CONTEXT LAYER\n{context_section}")
        
        if profile.enable_reasoning:
            reasoning_section = self._compose_reasoning_layer(profile)
            if reasoning_section:
                prompt_sections.append(f"# REASONING LAYER\n{reasoning_section}")
        
        if profile.enable_tooling:
            tooling_section = self._compose_tooling_layer(profile)
            if tooling_section:
                prompt_sections.append(f"# TOOLING LAYER\n{tooling_section}")
        
        if profile.enable_safety:
            safety_section = self._compose_safety_layer(profile)
            if safety_section:
                prompt_sections.append(f"# SAFETY LAYER\n{safety_section}")
        
        if profile.enable_output:
            output_section = self._compose_output_layer(profile)
            if output_section:
                prompt_sections.append(f"# OUTPUT LAYER\n{output_section}")
        
        # Apply parent modifications if specified
        if profile.parent_modifications and parent_prompt:
            composed_prompt = "\n\n".join(prompt_sections)
            composed_prompt = self._apply_parent_modifications(composed_prompt, profile.parent_modifications)
            return composed_prompt
        
        return "\n\n".join(prompt_sections)
    
    def _compose_framing_layer(self, profile: AgentProfile) -> str:
        """Compose framing layer based on profile parameters."""
        params = profile.framing_params or {}
        
        sections = []
        if 'goal' in params:
            sections.append(FramingLayer.global_goal_state(
                params['goal'], 
                params.get('context', '')
            ))
        
        if 'success_criteria' in params:
            sections.append(FramingLayer.success_criteria(params['success_criteria']))
        
        if 'task_mode' in params:
            sections.append(FramingLayer.task_mode_declaration(
                params['task_mode'],
                params.get('mode_description', '')
            ))
        
        if 'scope' in params:
            sections.append(FramingLayer.scope_boundaries(
                params['scope'],
                params.get('constraints', []),
                params.get('forbidden', [])
            ))
        
        if 'efficiency' in params:
            sections.append(FramingLayer.cost_latency_targets(
                params.get('max_tokens'),
                params.get('max_time'),
                params.get('efficiency_mode', 'balanced')
            ))
        
        return "\n\n".join(sections)
    
    def _compose_context_layer(self, profile: AgentProfile) -> str:
        """Compose context layer based on profile parameters."""
        params = profile.context_params or {}
        
        sections = []
        if 'user_input' in params:
            sections.append(ContextLayer.untrusted_block_wrapping(
                params['user_input'],
                params.get('source', 'user')
            ))
        
        if 'canonicalization' in params:
            sections.append(ContextLayer.canonicalization_rules())
        
        if 'pruning' in params:
            sections.append(ContextLayer.context_pruning_rules(
                params.get('relevance_threshold', 0.7),
                params.get('token_budget', 8000)
            ))
        
        if 'consistency_fields' in params:
            sections.append(ContextLayer.cross_field_consistency_check(
                params['consistency_fields']
            ))
        
        if 'ordering' in params:
            sections.append(ContextLayer.structured_context_ordering(
                params['ordering']
            ))
        
        return "\n\n".join(sections)
    
    def _compose_reasoning_layer(self, profile: AgentProfile) -> str:
        """Compose reasoning layer based on profile parameters."""
        params = profile.reasoning_params or {}
        
        sections = []
        if 'failure_modes' in params:
            sections.append(ReasoningLayer.failure_anticipation(params['failure_modes']))
        
        if 'multi_branch' in params:
            sections.append(ReasoningLayer.multi_branch_thinking(
                params.get('branches', 3)
            ))
        
        sections.append(ReasoningLayer.confidence_uncertainty())
        sections.append(ReasoningLayer.reason_then_answer())
        sections.append(ReasoningLayer.error_simulation())
        
        return "\n\n".join(sections)
    
    def _compose_tooling_layer(self, profile: AgentProfile) -> str:
        """Compose tooling layer based on profile parameters."""
        params = profile.tooling_params or {}
        
        sections = []
        if 'tools' in params:
            sections.append(ToolingLayer.tool_feedback_loop(params['tools']))
        
        sections.append(ToolingLayer.evidence_binding())
        sections.append(ToolingLayer.cross_tool_reconciliation())
        sections.append(ToolingLayer.shadow_validation())
        sections.append(ToolingLayer.model_switch_aware())
        
        return "\n\n".join(sections)
    
    def _compose_safety_layer(self, profile: AgentProfile) -> str:
        """Compose safety layer based on profile parameters."""
        sections = [
            SafetyLayer.prompt_injection_shield(),
            SafetyLayer.data_instruction_separation(),
            SafetyLayer.constitutional_guardrails(),
            SafetyLayer.delegation_guardrails(),
            SafetyLayer.expanded_adversarial_mode()
        ]
        
        return "\n\n".join(sections)
    
    def _compose_output_layer(self, profile: AgentProfile) -> str:
        """Compose output layer based on profile parameters."""
        params = profile.output_params or {}
        
        sections = [OutputLayer.strict_json_output()]
        
        if 'schema' in params:
            sections.append(OutputLayer.schema_enforcement(
                params['schema'],
                params.get('example')
            ))
        
        if 'field_order' in params:
            sections.append(OutputLayer.stability_contracts(
                params['field_order'],
                params.get('naming_convention', 'snake_case')
            ))
        
        sections.append(OutputLayer.error_envelope_normalization())
        
        if 'minimality' in params:
            sections.append(OutputLayer.minimality_constraints(
                params.get('max_fields'),
                params.get('max_depth'),
                params.get('max_array_length')
            ))
        
        return "\n\n".join(sections)
    
    def _apply_parent_modifications(self, prompt: str, modifications: Dict[str, Any]) -> str:
        """Apply parent-level modifications to composed prompt."""
        # Implementation for parent modifications
        # This could include parameter overrides, constraint additions, etc.
        return prompt
    
    def create_subatomic_profile(self, 
                                name: str,
                                agent_type: str,
                                parent_profile: Optional[str] = None,
                                customizations: Optional[Dict[str, Any]] = None) -> AgentProfile:
        """Create a subatomic agent profile with inheritance from parent."""
        
        # Base profiles for different agent types
        base_profiles = {
            'content': {
                'framing_params': {'task_mode': 'synthesis'},
                'reasoning_params': {'multi_branch': True, 'branches': 3},
                'tooling_params': {'tools': {}},
                'output_params': {'schema': {}}
            },
            'structure': {
                'framing_params': {'task_mode': 'analytical'},
                'reasoning_params': {'multi_branch': False},
                'tooling_params': {'tools': {}},
                'context_params': {'consistency_fields': {}}
            },
            'validation': {
                'framing_params': {'task_mode': 'adversarial'},
                'reasoning_params': {'failure_modes': []},
                'safety_params': {'enhanced_mode': True},
                'output_params': {'minimality': True}
            },
            'analysis': {
                'framing_params': {'task_mode': 'meta'},
                'reasoning_params': {'multi_branch': True, 'branches': 5},
                'tooling_params': {'tools': {}},
                'context_params': {'pruning': True}
            }
        }
        
        base_config = base_profiles.get(agent_type, {})
        
        # Apply customizations
        if customizations:
            for layer, params in customizations.items():
                if f"{layer}_params" in base_config:
                    base_config[f"{layer}_params"].update(params)
                else:
                    base_config[f"{layer}_params"] = params
        
        return AgentProfile(
            agent_name=name,
            agent_type=agent_type,
            inherit_from_parent=parent_profile is not None,
            **base_config
        )


# Pre-defined profiles for common subatomic agent types
def create_content_enhancer_profile() -> AgentProfile:
    """Create profile for content enhancement subatomic agent."""
    return AgentProfile(
        agent_name="content_enhancer",
        agent_type="content",
        framing_params={
            'goal': "Enhance content quality, clarity, and impact while preserving original meaning",
            'success_criteria': [
                "Improved readability and clarity",
                "Enhanced professional tone",
                "Preserved factual accuracy",
                "Optimized for target audience"
            ],
            'task_mode': 'synthesis',
            'efficiency': {'max_tokens': 2000, 'efficiency_mode': 'balanced'}
        },
        reasoning_params={
            'multi_branch': True,
            'branches': 3
        },
        output_params={
            'schema': {
                'type': 'object',
                'properties': {
                    'enhanced_content': {'type': 'string'},
                    'improvements': {'type': 'array'},
                    'confidence': {'type': 'number'}
                }
            }
        }
    )


def create_structure_optimizer_profile() -> AgentProfile:
    """Create profile for structure optimization subatomic agent."""
    return AgentProfile(
        agent_name="structure_optimizer",
        agent_type="structure",
        framing_params={
            'goal': "Optimize content structure for logical flow and readability",
            'success_criteria': [
                "Logical information hierarchy",
                "Clear section organization",
                "Optimal information flow",
                "Consistent formatting"
            ],
            'task_mode': 'analytical'
        },
        context_params={
            'consistency_fields': {
                'headings': 'Section heading hierarchy and formatting',
                'flow': 'Information progression and transitions',
                'balance': 'Content distribution across sections'
            }
        }
    )


def create_quality_validator_profile() -> AgentProfile:
    """Create profile for quality validation subatomic agent."""
    return AgentProfile(
        agent_name="quality_validator",
        agent_type="validation",
        framing_params={
            'goal': "Validate content quality, accuracy, and compliance with requirements",
            'success_criteria': [
                "Factual accuracy verification",
                "Grammar and style compliance",
                "Requirement satisfaction",
                "Quality threshold achievement"
            ],
            'task_mode': 'adversarial'
        },
        reasoning_params={
            'failure_modes': [
                "Factual inaccuracies",
                "Grammar errors",
                "Style inconsistencies",
                "Requirement violations"
            ]
        },
        output_params={
            'minimality': True,
            'max_fields': 5
        }
    )
