"""
Base Template Implementation

Provides comprehensive template rendering and management for prompt
governance across the L1-L5 architecture.
"""

from __future__ import annotations

import asyncio
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator
from enum import Enum
from pathlib import Path
import json
import yaml

from ..builder import PromptBuilder


class TemplateType(str, Enum):
    """Types of templates supported."""
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"
    JINJA2 = "jinja2"
    MUSTACHE = "mustache"


class ValidationLevel(str, Enum):
    """Template validation levels."""
    NONE = "none"
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    FULL = "full"


@dataclass
class TemplateMetadata:
    """Metadata for template tracking and governance."""
    name: str
    version: str = "1.0"
    description: str = ""
    author: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    category: str = ""
    template_type: TemplateType = TemplateType.TEXT
    validation_level: ValidationLevel = ValidationLevel.SYNTAX
    required_variables: List[str] = field(default_factory=list)
    optional_variables: List[str] = field(default_factory=list)
    max_length: Optional[int] = None
    safety_checks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
            "category": self.category,
            "template_type": self.template_type.value,
            "validation_level": self.validation_level.value,
            "required_variables": self.required_variables,
            "optional_variables": self.optional_variables,
            "max_length": self.max_length,
            "safety_checks": self.safety_checks,
        }


@dataclass
class RenderContext:
    """Context for template rendering."""
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    safety_mode: bool = True
    trace_execution: bool = False
    cache_enabled: bool = True
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get variable value with default."""
        return self.variables.get(name, default)
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set variable value."""
        self.variables[name] = value
    
    def has_variable(self, name: str) -> bool:
        """Check if variable exists."""
        return name in self.variables


class TemplateValidationError(Exception):
    """Template validation failed."""
    pass


class TemplateRenderError(Exception):
    """Template rendering failed."""
    pass


class BaseTemplate(ABC):
    """Base class for all prompt templates."""
    
    def __init__(self, name: str, template_content: str, 
                 template_type: TemplateType = TemplateType.TEXT,
                 metadata: Optional[TemplateMetadata] = None):
        self.name = name
        self.template_content = template_content
        self.template_type = template_type
        self.metadata = metadata or TemplateMetadata(name=name, template_type=template_type)
        
        # Rendering statistics
        self.render_count = 0
        self.error_count = 0
        self.last_rendered: Optional[float] = None
        
        # Validation and safety
        self._compiled_template = None
        self._validate_template()
    
    @abstractmethod
    def _compile_template(self) -> Any:
        """Compile template for efficient rendering."""
        pass
    
    @abstractmethod
    def _render_template(self, context: RenderContext) -> str:
        """Render template with given context."""
        pass
    
    def _validate_template(self) -> None:
        """Validate template syntax and structure."""
        if self.metadata.validation_level == ValidationLevel.NONE:
            return
        
        try:
            # Basic syntax validation
            self._validate_syntax()
            
            if self.metadata.validation_level in [ValidationLevel.SEMANTIC, ValidationLevel.FULL]:
                self._validate_semantics()
            
            if self.metadata.validation_level == ValidationLevel.FULL:
                self._validate_safety()
            
            # Compile template for efficient rendering
            self._compiled_template = self._compile_template()
            
        except Exception as e:
            raise TemplateValidationError(f"Template validation failed for '{self.name}': {e}")
    
    def _validate_syntax(self) -> None:
        """Validate template syntax."""
        if not self.template_content.strip():
            raise TemplateValidationError("Template content is empty")
        
        # Check for basic syntax issues based on template type
        if self.template_type == TemplateType.JINJA2:
            self._validate_jinja2_syntax()
        elif self.template_type == TemplateType.JSON:
            self._validate_json_syntax()
        elif self.template_type == TemplateType.YAML:
            self._validate_yaml_syntax()
    
    def _validate_jinja2_syntax(self) -> None:
        """Validate Jinja2 template syntax."""
        try:
            from jinja2 import Environment, meta, TemplateSyntaxError
            env = Environment()
            env.parse(self.template_content)
            
            # Extract variables from template
            ast = env.parse(self.template_content)
            variables = meta.find_undeclared_variables(ast)
            
            # Update metadata with discovered variables
            self.metadata.required_variables = list(variables)
            
        except ImportError:
            # Jinja2 not available, skip detailed validation
            pass
        except TemplateSyntaxError as e:
            raise TemplateValidationError(f"Jinja2 syntax error: {e}")
    
    def _validate_json_syntax(self) -> None:
        """Validate JSON template syntax."""
        try:
            # Check if it's valid JSON with placeholders
            json.loads(self._extract_placeholders_for_validation(self.template_content))
        except json.JSONDecodeError as e:
            raise TemplateValidationError(f"JSON syntax error: {e}")
    
    def _validate_yaml_syntax(self) -> None:
        """Validate YAML template syntax."""
        try:
            yaml.safe_load(self._extract_placeholders_for_validation(self.template_content))
        except yaml.YAMLError as e:
            raise TemplateValidationError(f"YAML syntax error: {e}")
    
    def _extract_placeholders_for_validation(self, content: str) -> str:
        """Replace placeholders with dummy values for validation."""
        # Replace {{variable}} with "dummy_value"
        placeholder_pattern = r'\{\{\s*([^}]+)\s*\}\}'
        return re.sub(placeholder_pattern, '"dummy_value"', content)
    
    def _validate_semantics(self) -> None:
        """Validate template semantics and business rules."""
        # Check for required variables
        if self.metadata.required_variables:
            # Ensure template actually uses the required variables
            used_variables = self._extract_variables()
            missing_vars = set(self.metadata.required_variables) - set(used_variables)
            if missing_vars:
                raise TemplateValidationError(f"Required variables not used in template: {missing_vars}")
        
        # Check length constraints
        if self.metadata.max_length and len(self.template_content) > self.metadata.max_length:
            raise TemplateValidationError(f"Template exceeds maximum length: {len(self.template_content)} > {self.metadata.max_length}")
    
    def _validate_safety(self) -> None:
        """Validate template safety and security."""
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'import\s+',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__',
            r'subprocess',
            r'os\.system',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, self.template_content, re.IGNORECASE):
                raise TemplateValidationError(f"Potentially dangerous pattern detected: {pattern}")
    
    def _extract_variables(self) -> List[str]:
        """Extract variable names from template."""
        if self.template_type == TemplateType.JINJA2:
            # Jinja2 variables: {{variable}}
            matches = re.findall(r'\{\{\s*([^}]+)\s*\}\}', self.template_content)
            return [var.strip().split('.')[0] for var in matches]
        else:
            # Generic placeholder patterns
            patterns = [
                r'\{\{\s*([^}]+)\s*\}\}',  # {{variable}}
                r'\$\{([^}]+)\}',          # ${variable}
                r'\{([^}]+)\}',            # {variable}
            ]
            
            variables = []
            for pattern in patterns:
                matches = re.findall(pattern, self.template_content)
                variables.extend([var.strip() for var in matches])
            
            return list(set(variables))
    
    def render(self, context: Union[Dict[str, Any], RenderContext], 
               validate_variables: bool = True) -> str:
        """Render template with given context."""
        try:
            # Convert dict to RenderContext if needed
            if isinstance(context, dict):
                context = RenderContext(variables=context)
            
            # Validate required variables
            if validate_variables and self.metadata.required_variables:
                missing_vars = []
                for var in self.metadata.required_variables:
                    if not context.has_variable(var):
                        missing_vars.append(var)
                
                if missing_vars:
                    raise TemplateRenderError(f"Missing required variables: {missing_vars}")
            
            # Render the template
            result = self._render_template(context)
            
            # Update statistics
            self.render_count += 1
            self.last_rendered = time.time()
            
            return result
            
        except Exception as e:
            self.error_count += 1
            raise TemplateRenderError(f"Template rendering failed for '{self.name}': {e}")
    
    async def render_async(self, context: Union[Dict[str, Any], RenderContext],
                          validate_variables: bool = True) -> str:
        """Render template asynchronously."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.render, context, validate_variables
        )
    
    def validate_context(self, context: RenderContext) -> List[str]:
        """Validate context and return list of issues."""
        issues = []
        
        # Check required variables
        for var in self.metadata.required_variables:
            if not context.has_variable(var):
                issues.append(f"Missing required variable: {var}")
        
        # Check variable types if specified
        # This could be extended with type checking
        
        return issues
    
    def get_stats(self) -> Dict[str, Any]:
        """Get template usage statistics."""
        return {
            "name": self.name,
            "render_count": self.render_count,
            "error_count": self.error_count,
            "success_rate": (self.render_count - self.error_count) / max(self.render_count, 1),
            "last_rendered": self.last_rendered,
            "template_type": self.template_type.value,
            "validation_level": self.metadata.validation_level.value,
        }
    
    def update_metadata(self, **kwargs) -> None:
        """Update template metadata."""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
        
        self.metadata.updated_at = time.time()
        
        # Re-validate if validation level changed
        if 'validation_level' in kwargs:
            self._validate_template()
    
    def clone(self, new_name: str) -> BaseTemplate:
        """Create a clone of this template with a new name."""
        # Create new metadata
        new_metadata = TemplateMetadata(
            name=new_name,
            version=self.metadata.version,
            description=self.metadata.description,
            author=self.metadata.author,
            tags=self.metadata.tags.copy(),
            category=self.metadata.category,
            template_type=self.metadata.template_type,
            validation_level=self.metadata.validation_level,
            required_variables=self.metadata.required_variables.copy(),
            optional_variables=self.metadata.optional_variables.copy(),
            max_length=self.metadata.max_length,
            safety_checks=self.metadata.safety_checks.copy(),
        )
        
        # Create new template instance
        return self.__class__(
            name=new_name,
            template_content=self.template_content,
            template_type=self.template_type,
            metadata=new_metadata
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization."""
        return {
            "name": self.name,
            "template_content": self.template_content,
            "template_type": self.template_type.value,
            "metadata": self.metadata.to_dict(),
            "stats": self.get_stats(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseTemplate:
        """Create template from dictionary."""
        metadata = TemplateMetadata(**data.get("metadata", {}))
        return cls(
            name=data["name"],
            template_content=data["template_content"],
            template_type=TemplateType(data.get("template_type", "text")),
            metadata=metadata
        )


class TextTemplate(BaseTemplate):
    """Simple text template with variable substitution."""
    
    def _compile_template(self) -> Any:
        """Compile text template."""
        return self.template_content
    
    def _render_template(self, context: RenderContext) -> str:
        """Render text template with variable substitution."""
        result = self.template_content
        
        # Simple variable substitution {{variable}}
        for var_name, var_value in context.variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            result = result.replace(placeholder, str(var_value))
        
        return result


class JsonTemplate(BaseTemplate):
    """JSON template with variable substitution."""
    
    def _compile_template(self) -> Any:
        """Compile JSON template."""
        return self.template_content
    
    def _render_template(self, context: RenderContext) -> str:
        """Render JSON template with variable substitution."""
        # Substitute variables in template
        temp_content = self.template_content
        for var_name, var_value in context.variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            temp_content = temp_content.replace(placeholder, json.dumps(var_value))
        
        # Validate and format JSON
        parsed = json.loads(temp_content)
        return json.dumps(parsed, indent=2)


# Template registry
_template_registry: Dict[str, BaseTemplate] = {}


def register_template(template: BaseTemplate) -> None:
    """Register a template in the global registry."""
    _template_registry[template.name] = template


def get_template(name: str) -> Optional[BaseTemplate]:
    """Get template from registry."""
    return _template_registry.get(name)


def list_templates() -> List[str]:
    """List all registered template names."""
    return list(_template_registry.keys())


__all__ = [
    "BaseTemplate",
    "TextTemplate", 
    "JsonTemplate",
    "TemplateType",
    "ValidationLevel",
    "TemplateMetadata",
    "RenderContext",
    "TemplateValidationError",
    "TemplateRenderError",
    "register_template",
    "get_template",
    "list_templates",
]
