"""Toolsmith Utility - Deterministic tool generation and management.

This module provides deterministic tool functionality previously
implemented in ToolsmithAgent. Converted from agent to utility script
as part of SCRIPT agent conversion (Micro-wave 6).

Usage:
    from agentic_core.L2_execution.utils.toolsmith_util import (
        ToolSpec, GeneratedTool, generate_tool_from_template, validate_tool_code
    )
    
    # Generate a tool
    tool = generate_tool_from_template("file_reader", category="file")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class ToolSpec:
    """Specification for a tool."""

    name: str
    description: str
    parameters: dict[str, dict]
    function: Any | None = None
    category: str = "general"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "category": self.category,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class GeneratedTool:
    """A dynamically generated tool."""

    spec: ToolSpec
    code: str
    imports: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    test_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "spec": self.spec.to_dict(),
            "code": self.code,
            "imports": self.imports,
            "dependencies": self.dependencies,
            "has_tests": bool(self.test_code),
        }


# Template constants
FUNCTION_TEMPLATE: str = '''
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
async def {name}({params}) -> {return_type}:
    """
    {description}

    Args:
{param_docs}
    Returns:
        {return_description}
    """
    # Implementation
    {implementation}
'''

CLASS_TEMPLATE: str = '''
class {name}:
    """
    {description}
    """

    def __init__(self{init_params}) -> None:
        """Initialize the {name} tool."""
{init_body}
    async def execute{method_params} -> {return_type}:
        """
        Execute the tool.

        Args:
{method_param_docs}
        Returns:
            {return_description}
        """
        # Implementation
        {method_implementation}
'''


# Built-in tool templates
BUILTIN_TEMPLATES: dict[str, str] = {
    "file_reader": FUNCTION_TEMPLATE.format(
        name="read_file",
        params="file_path: str, encoding: str = 'utf-8'",
        return_type="str",
        description="Read contents of a file",
        param_docs="        file_path: Path to the file\n        encoding: File encoding",
        return_description="File contents as string",
        implementation="    with open(file_path, 'r', encoding=encoding) as f:\n        return f.read()",
    ),
    "file_writer": FUNCTION_TEMPLATE.format(
        name="write_file",
        params="file_path: str, content: str, encoding: str = 'utf-8'",
        return_type="bool",
        description="Write content to a file",
        param_docs="        file_path: Path to the file\n        content: Content to write\n        encoding: File encoding",
        return_description="True if successful",
        implementation="    try:\n        with open(file_path, 'w', encoding=encoding) as f:\n            f.write(content)\n        return True\n    except Exception as e:\n        return False",
    ),
    "json_validator": FUNCTION_TEMPLATE.format(
        name="validate_json",
        params="data: Any, schema: dict",
        return_type="dict[str, Any]",
        description="Validate JSON data against schema",
        param_docs="        data: JSON data to validate\n        schema: Validation schema",
        return_description="Validation result with errors if any",
        implementation="    import jsonschema\n    try:\n        jsonschema.validate(data, schema)\n        return {'valid': True, 'errors': []}\n    except Exception as e:\n        return {'valid': False, 'errors': [str(e)]}",
    ),
}


def get_tool_template(template_name: str) -> str | None:
    """Get a built-in tool template.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Template string or None if not found
    """
    return BUILTIN_TEMPLATES.get(template_name)


def list_builtin_templates() -> dict[str, str]:
    """List all available built-in templates.
    
    Returns:
        Dictionary mapping template names to descriptions
    """
    return {
        "file_reader": "Read file contents",
        "file_writer": "Write content to file",
        "json_validator": "Validate JSON against schema",
    }


def generate_tool_from_template(
    template_name: str,
    category: str = "general",
    custom_params: dict[str, Any] | None = None,
) -> GeneratedTool | None:
    """Generate a tool from a template.
    
    Args:
        template_name: Name of the template to use
        category: Tool category
        custom_params: Custom parameters to override defaults
        
    Returns:
        GeneratedTool or None if template not found
    """
    template_code = get_tool_template(template_name)
    if not template_code:
        return None

    # Extract function name from template
    name = template_name

    spec = ToolSpec(
        name=name,
        description=f"Auto-generated {template_name} tool",
        parameters={},
        category=category,
    )

    return GeneratedTool(
        spec=spec,
        code=template_code,
        imports=["agentic_core.mixins.subatomic_testing_mixin"],
        dependencies=[],
    )


def validate_tool_code(code: str) -> dict[str, Any]:
    """Validate generated tool code.
    
    Args:
        code: Python code to validate
        
    Returns:
        Validation result dictionary
    """
    import ast

    try:
        ast.parse(code)
        return {
            "valid": True,
            "syntax_errors": [],
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "syntax_errors": [str(e)],
        }


def get_tool_categories() -> dict[str, str]:
    """Get available tool categories.
    
    Returns:
        Dictionary mapping category IDs to descriptions
    """
    return {
        "file": "File manipulation tools",
        "network": "Network and API tools",
        "data": "Data processing tools",
        "validation": "Validation and checking tools",
        "utility": "General utility tools",
    }


def create_tool_spec(
    name: str,
    description: str,
    parameters: dict[str, dict],
    category: str = "general",
) -> ToolSpec:
    """Create a tool specification.
    
    Args:
        name: Tool name
        description: Tool description
        parameters: Parameter specifications
        category: Tool category
        
    Returns:
        ToolSpec instance
    """
    return ToolSpec(
        name=name,
        description=description,
        parameters=parameters,
        category=category,
    )
