#!/usr/bin/env python3
"""
Prompt Injections
Section 3: Prompt Governance - Injection prompt templates

Provides comprehensive prompt injection capabilities for layering
context, safety measures, and output formatting across the L1-L5 architecture.
"""

from __future__ import annotations

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum

from ...templates.base import BaseTemplate, RenderContext


class InjectionType(str, Enum):
    """Types of prompt injections available."""
    CONTEXT = "context"
    FRAMING = "framing"
    SAFETY = "safety"
    OUTPUT_FORMATTING = "output_formatting"
    TOOL_SELECTION = "tool_selection"
    ROLE_DEFINITION = "role_definition"
    CONSTRAINTS = "constraints"
    EXAMPLES = "examples"
    MEMORY_INJECTION = "memory_injection"
    TRACE_INJECTION = "trace_injection"


class InjectionPriority(str, Enum):
    """Priority levels for prompt injections."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class InjectionTemplate:
    """Template for a specific type of prompt injection."""
    name: str
    injection_type: InjectionType
    template: str
    priority: InjectionPriority = InjectionPriority.MEDIUM
    required_context: List[str] = field(default_factory=list)
    optional_context: List[str] = field(default_factory=list)
    safety_level: str = "standard"
    description: str = ""
    version: str = "1.0"
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render injection template with context."""
        # Validate required context
        missing = [key for key in self.required_context if key not in context]
        if missing:
            raise ValueError(f"Missing required context for injection '{self.name}': {missing}")
        
        # Simple template substitution
        result = self.template
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", str(value))
        
        return result


@dataclass
class InjectionResult:
    """Result of applying a prompt injection."""
    original_prompt: str
    injected_prompt: str
    injection_type: InjectionType
    injection_name: str
    applied_at: float = field(default_factory=time.time)
    context_used: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None


class BaseInjectionStrategy(ABC):
    """Base class for injection strategies."""
    
    @abstractmethod
    def apply_injection(self, base_prompt: str, injection: InjectionTemplate, 
                       context: Dict[str, Any]) -> InjectionResult:
        """Apply injection to base prompt."""
        pass
    
    @abstractmethod
    def can_apply(self, injection_type: InjectionType) -> bool:
        """Check if strategy can apply given injection type."""
        pass


class PrefixInjectionStrategy(BaseInjectionStrategy):
    """Strategy that injects prompts as prefix."""
    
    def apply_injection(self, base_prompt: str, injection: InjectionTemplate, 
                       context: Dict[str, Any]) -> InjectionResult:
        """Apply injection as prefix to base prompt."""
        try:
            injection_text = injection.render(context)
            injected_prompt = f"{injection_text}\n\n{base_prompt}"
            
            return InjectionResult(
                original_prompt=base_prompt,
                injected_prompt=injected_prompt,
                injection_type=injection.injection_type,
                injection_name=injection.name,
                context_used=context,
            )
        except Exception as e:
            return InjectionResult(
                original_prompt=base_prompt,
                injected_prompt=base_prompt,
                injection_type=injection.injection_type,
                injection_name=injection.name,
                success=False,
                error_message=str(e),
            )
    
    def can_apply(self, injection_type: InjectionType) -> bool:
        """Can apply any injection type as prefix."""
        return True


class SuffixInjectionStrategy(BaseInjectionStrategy):
    """Strategy that injects prompts as suffix."""
    
    def apply_injection(self, base_prompt: str, injection: InjectionTemplate, 
                       context: Dict[str, Any]) -> InjectionResult:
        """Apply injection as suffix to base prompt."""
        try:
            injection_text = injection.render(context)
            injected_prompt = f"{base_prompt}\n\n{injection_text}"
            
            return InjectionResult(
                original_prompt=base_prompt,
                injected_prompt=injected_prompt,
                injection_type=injection.injection_type,
                injection_name=injection.name,
                context_used=context,
            )
        except Exception as e:
            return InjectionResult(
                original_prompt=base_prompt,
                injected_prompt=base_prompt,
                injection_type=injection.injection_type,
                injection_name=injection.name,
                success=False,
                error_message=str(e),
            )
    
    def can_apply(self, injection_type: InjectionType) -> bool:
        """Can apply output formatting and constraints as suffix."""
        return injection_type in [InjectionType.OUTPUT_FORMATTING, InjectionType.CONSTRAINTS]


class ContextInjectionStrategy(BaseInjectionStrategy):
    """Strategy for context-aware injections."""
    
    def apply_injection(self, base_prompt: str, injection: InjectionTemplate, 
                       context: Dict[str, Any]) -> InjectionResult:
        """Apply context injection with appropriate placement."""
        try:
            injection_text = injection.render(context)
            
            # For context injections, try to place after any existing context
            if "CONTEXT:" in base_prompt:
                # Insert after existing context
                parts = base_prompt.split("CONTEXT:", 1)
                injected_prompt = f"{parts[0]}CONTEXT:\n{injection_text}\n{parts[1]}"
            else:
                # Add as prefix
                injected_prompt = f"CONTEXT:\n{injection_text}\n\n{base_prompt}"
            
            return InjectionResult(
                original_prompt=base_prompt,
                injected_prompt=injected_prompt,
                injection_type=injection.injection_type,
                injection_name=injection.name,
                context_used=context,
            )
        except Exception as e:
            return InjectionResult(
                original_prompt=base_prompt,
                injected_prompt=base_prompt,
                injection_type=injection.injection_type,
                injection_name=injection.name,
                success=False,
                error_message=str(e),
            )
    
    def can_apply(self, injection_type: InjectionType) -> bool:
        """Can apply context and memory injections."""
        return injection_type in [InjectionType.CONTEXT, InjectionType.MEMORY_INJECTION]


class PromptInjectionManager:
    """Manages prompt injection templates and application strategies."""
    
    def __init__(self):
        self.templates: Dict[str, InjectionTemplate] = {}
        self.strategies: List[BaseInjectionStrategy] = [
            PrefixInjectionStrategy(),
            SuffixInjectionStrategy(),
            ContextInjectionStrategy(),
        ]
        
        # Initialize default templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self) -> None:
        """Initialize default injection templates."""
        
        # Context injection
        self.register_template(InjectionTemplate(
            name="context_layer",
            injection_type=InjectionType.CONTEXT,
            template="You are operating in the following context:\n{context_description}\nCurrent layer: {layer}\nTask: {task}",
            priority=InjectionPriority.HIGH,
            required_context=["context_description", "layer", "task"],
            description="Injects operational context and layer information",
        ))
        
        # Safety injection
        self.register_template(InjectionTemplate(
            name="safety_guardrails",
            injection_type=InjectionType.SAFETY,
            template="SAFETY GUIDELINES:\n1. Do not provide harmful, unethical, or dangerous information\n2. Respect user privacy and confidentiality\n3. Follow all applicable laws and regulations\n4. If unsure about safety, err on the side of caution",
            priority=InjectionPriority.CRITICAL,
            description="Injects safety guardrails and ethical guidelines",
        ))
        
        # Role definition
        self.register_template(InjectionTemplate(
            name="role_definition",
            injection_type=InjectionType.ROLE_DEFINITION,
            template="ROLE: {role}\nEXPERTISE: {expertise}\nRESPONSIBILITIES: {responsibilities}",
            priority=InjectionPriority.HIGH,
            required_context=["role", "expertise", "responsibilities"],
            description="Defines the AI agent's role and responsibilities",
        ))
        
        # Output formatting
        self.register_template(InjectionTemplate(
            name="json_output_format",
            injection_type=InjectionType.OUTPUT_FORMATTING,
            template="OUTPUT FORMAT:\nPlease provide your response in valid JSON format with the following structure:\n{{\n  \"response\": \"your main response\",\n  \"confidence\": \"high/medium/low\",\n  \"reasoning\": \"brief explanation of your reasoning\"\n}}",
            priority=InjectionPriority.MEDIUM,
            description="Requests JSON formatted output",
        ))
        
        # Constraints
        self.register_template(InjectionTemplate(
            name="response_constraints",
            injection_type=InjectionType.CONSTRAINTS,
            template="CONSTRAINTS:\n- Response length: {max_length} words maximum\n- Complexity: {complexity_level}\n- Tone: {tone}\n- Avoid: {forbidden_topics}",
            priority=InjectionPriority.MEDIUM,
            required_context=["max_length", "complexity_level", "tone"],
            optional_context=["forbidden_topics"],
            description="Applies response constraints and guidelines",
        ))
        
        # Tool selection
        self.register_template(InjectionTemplate(
            name="tool_selection_guidance",
            injection_type=InjectionType.TOOL_SELECTION,
            template="AVAILABLE TOOLS: {available_tools}\nSELECTION CRITERIA: {selection_criteria}\nPlease select and use the most appropriate tool for this task.",
            priority=InjectionPriority.MEDIUM,
            required_context=["available_tools", "selection_criteria"],
            description="Guides tool selection for task execution",
        ))
        
        # Memory injection
        self.register_template(InjectionTemplate(
            name="memory_context",
            injection_type=InjectionType.MEMORY_INJECTION,
            template="MEMORY CONTEXT:\nPrevious interactions: {previous_interactions}\nKey information remembered: {key_information}\nUser preferences: {user_preferences}",
            priority=InjectionPriority.MEDIUM,
            required_context=["previous_interactions", "key_information"],
            optional_context=["user_preferences"],
            description="Injects memory context from previous interactions",
        ))
        
        # Trace injection
        self.register_template(InjectionTemplate(
            name="trace_context",
            injection_type=InjectionType.TRACE_INJECTION,
            template="TRACE CONTEXT:\nTrace ID: {trace_id}\nCurrent Step: {current_step}\nPrevious Steps: {previous_steps}\nGoal: {goal}",
            priority=InjectionPriority.LOW,
            required_context=["trace_id", "current_step", "goal"],
            optional_context=["previous_steps"],
            description="Injects trace context for debugging and monitoring",
        ))
    
    def register_template(self, template: InjectionTemplate) -> None:
        """Register a new injection template."""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[InjectionTemplate]:
        """Get injection template by name."""
        return self.templates.get(name)
    
    def list_templates(self, injection_type: Optional[InjectionType] = None) -> List[str]:
        """List available template names, optionally filtered by type."""
        if injection_type:
            return [name for name, template in self.templates.items() 
                   if template.injection_type == injection_type]
        return list(self.templates.keys())
    
    def list_injection_types(self) -> List[str]:
        """List available injection types."""
        return [t.value for t in InjectionType]
    
    def get_injection_prompt(self, injection_type: str, context: Dict[str, Any], 
                           template_name: Optional[str] = None) -> Optional[str]:
        """Get injection prompt by type and context."""
        try:
            inj_type = InjectionType(injection_type)
            
            if template_name:
                template = self.get_template(template_name)
                if template and template.injection_type == inj_type:
                    return template.render(context)
            else:
                # Get first template of matching type
                for template in self.templates.values():
                    if template.injection_type == inj_type:
                        return template.render(context)
            
            return None
        except (ValueError, KeyError):
            return None
    
    def apply_injection(self, base_prompt: str, injection_name: str, 
                       context: Dict[str, Any]) -> InjectionResult:
        """Apply a specific injection to base prompt."""
        template = self.get_template(injection_name)
        if not template:
            return InjectionResult(
                original_prompt=base_prompt,
                injected_prompt=base_prompt,
                injection_type=InjectionType.CONTEXT,  # Default
                injection_name=injection_name,
                success=False,
                error_message=f"Template '{injection_name}' not found",
            )
        
        # Find appropriate strategy
        strategy = None
        for s in self.strategies:
            if s.can_apply(template.injection_type):
                strategy = s
                break
        
        if not strategy:
            strategy = self.strategies[0]  # Fallback to prefix strategy
        
        return strategy.apply_injection(base_prompt, template, context)
    
    def apply_multiple_injections(self, base_prompt: str, 
                                 injections: List[Dict[str, Any]]) -> List[InjectionResult]:
        """Apply multiple injections to base prompt."""
        results = []
        current_prompt = base_prompt
        
        for injection_config in injections:
            injection_name = injection_config.get("name")
            context = injection_config.get("context", {})
            
            result = self.apply_injection(current_prompt, injection_name, context)
            results.append(result)
            
            if result.success:
                current_prompt = result.injected_prompt
        
        return results
    
    def get_templates_by_priority(self, priority: InjectionPriority) -> List[InjectionTemplate]:
        """Get templates filtered by priority."""
        return [template for template in self.templates.values() 
               if template.priority == priority]
    
    def validate_context_for_template(self, template_name: str, 
                                    context: Dict[str, Any]) -> List[str]:
        """Validate context for a specific template."""
        template = self.get_template(template_name)
        if not template:
            return [f"Template '{template_name}' not found"]
        
        issues = []
        
        # Check required context
        for key in template.required_context:
            if key not in context:
                issues.append(f"Missing required context: {key}")
        
        return issues


# Global injection manager
_injection_manager: Optional[PromptInjectionManager] = None


def get_injection_manager() -> PromptInjectionManager:
    """Get the global injection manager instance."""
    global _injection_manager
    if _injection_manager is None:
        _injection_manager = PromptInjectionManager()
    return _injection_manager


def get_injection_prompt(injection_type: str, context: Dict[str, Any], 
                        template_name: Optional[str] = None) -> Optional[str]:
    """Get injection prompt by type and context."""
    return get_injection_manager().get_injection_prompt(injection_type, context, template_name)


def apply_injection(base_prompt: str, injection_name: str, 
                   context: Dict[str, Any]) -> InjectionResult:
    """Apply injection to base prompt."""
    return get_injection_manager().apply_injection(base_prompt, injection_name, context)


def list_injection_types() -> List[str]:
    """List available injection types."""
    return get_injection_manager().list_injection_types()


def list_templates(injection_type: Optional[str] = None) -> List[str]:
    """List available template names."""
    if injection_type:
        try:
            inj_type = InjectionType(injection_type)
            return get_injection_manager().list_templates(inj_type)
        except ValueError:
            return []
    return get_injection_manager().list_templates()


__all__ = [
    'get_injection_prompt',
    'apply_injection',
    'list_injection_types',
    'list_templates',
    'PromptInjectionManager',
    'InjectionTemplate',
    'InjectionType',
    'InjectionPriority',
    'InjectionResult',
    'get_injection_manager',
]





