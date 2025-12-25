"""
ToolsmithAgent - L2 Tool Creation Agent

Dynamically creates and manages tools for the agentic system.
Generates specialized tools based on requirements.
"""
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol

LOGGER = logging.getLogger(__name__)


@dataclass
class ToolSpec:
    """Specification for a tool."""
    name: str
    description: str
    parameters: Dict[str, Dict]
    function: Callable
    category: str = "general"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "category": self.category,
            "version": self.version,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class GeneratedTool:
    """A dynamically generated tool."""
    spec: ToolSpec
    code: str
    imports: List[str]
    dependencies: List[str]
    test_code: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "spec": self.spec.to_dict(),
            "code": self.code,
            "imports": self.imports,
            "dependencies": self.dependencies,
            "has_tests": bool(self.test_code)
        }


class ToolTemplate:
    """Template for generating tools."""

    FUNCTION_TEMPLATE = '''
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

    CLASS_TEMPLATE = '''
class {name}:
    """
    {description}
    """

    def __init__(self{init_params}):
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


class ToolsmithAgent:
    """
    Creates and manages tools dynamically.

    Features:
    - Generates tools from specifications
    - Validates tool implementations
    - Manages tool registry
    - Provides tool templates
    """

    def __init__(self):
        """Initialize the ToolsmithAgent."""
        self.tools: Dict[str, GeneratedTool] = {}
        self.templates: Dict[str, str] = {}
        self.categories = {
            "file": "File manipulation tools",
            "network": "Network and API tools",
            "data": "Data processing tools",
            "validation": "Validation and checking tools",
            "utility": "General utility tools"
        }

        # Load templates
        self._load_templates()

        LOGGER.info("ToolsmithAgent initialized")

    def _load_templates(self):
        """Load tool generation templates."""
        self.templates.update({
            "file_reader": ToolTemplate.FUNCTION_TEMPLATE.format(
                name="read_file",
                params="file_path: str, encoding: str = 'utf-8'",
                return_type="str",
                description="Read contents of a file",
                param_docs="        file_path: Path to the file\n        encoding: File encoding",
                return_description="File contents as string",
                implementation='''    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()'''
            ),
            "file_writer": ToolTemplate.FUNCTION_TEMPLATE.format(
                name="write_file",
                params="file_path: str, content: str, encoding: str = 'utf-8'",
                return_type="bool",
                description="Write content to a file",
                param_docs="        file_path: Path to the file\n        content: Content to write\n        encoding: File encoding",
                return_description="True if successful",
                implementation='''    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        return False'''
            ),
            "json_validator": ToolTemplate.FUNCTION_TEMPLATE.format(
                name="validate_json",
                params="data: Any, schema: Dict",
                return_type="Dict[str, Any]",
                description="Validate data against JSON schema",
                param_docs="        data: Data to validate\n        schema: JSON schema",
                return_description="Validation result",
                implementation='''    try:
        import jsonschema
        jsonschema.validate(data, schema)
        return {"valid": True, "errors": []}
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}'''
            )
        })

    def create_tool_from_spec(self, spec: ToolSpec) -> GeneratedTool:
        """
        Create a tool from a specification.

        Args:
            spec: Tool specification

        Returns:
            Generated tool
        """
        # Generate code based on spec
        if self._is_simple_function(spec):
            code = self._generate_function_code(spec)
        else:
            code = self._generate_class_code(spec)

        # Extract imports
        imports = self._extract_imports(code)

        # Identify dependencies
        dependencies = self._identify_dependencies(code)

        # Generate test code
        test_code = self._generate_test_code(spec)

        # Create tool
        tool = GeneratedTool(
            spec=spec,
            code=code,
            imports=imports,
            dependencies=dependencies,
            test_code=test_code
        )

        # Register tool
        self.tools[spec.name] = tool

        LOGGER.info(f"Created tool: {spec.name}")
        return tool

    def _is_simple_function(self, spec: ToolSpec) -> bool:
        """Check if tool should be a simple function."""
        return len(spec.parameters) <= 5 and spec.category != "complex"

    def _generate_function_code(self, spec: ToolSpec) -> str:
        """Generate function code for a tool."""
        # Build parameter list
        params = []
        param_docs = []

        for param_name, param_info in spec.parameters.items():
            param_type = param_info.get("type", "Any")
            default = param_info.get("default")

            if default is not None:
                params.append(f"{param_name}: {param_type} = {default}")
            else:
                params.append(f"{param_name}: {param_type}")

            param_docs.append(f"        {param_name}: {param_info.get('description', 'No description')}")

        param_str = ", ".join(params)
        param_doc_str = "\n".join(param_docs)

        # Generate implementation based on category
        implementation = self._get_implementation(spec)

        return ToolTemplate.FUNCTION_TEMPLATE.format(
            name=spec.name,
            params=param_str,
            return_type=spec.parameters.get("return", {}).get("type", "Any"),
            description=spec.description,
            param_docs=param_doc_str,
            return_description=spec.parameters.get("return", {}).get("description", "Result"),
            implementation=implementation
        )

    def _generate_class_code(self, spec: ToolSpec) -> str:
        """Generate class code for a complex tool."""
        # Build initialization parameters
        init_params = []
        init_body = []

        for param_name, param_info in spec.parameters.items():
            if param_info.get("required", True):
                init_params.append(f", {param_name}: {param_info.get('type', 'Any')}")
                init_body.append(f"        self.{param_name} = {param_name}")

        init_param_str = "".join(init_params)
        init_body_str = "\n".join(init_body)

        # Build execute method
        method_params = ""
        method_param_docs = ""

        return ToolTemplate.CLASS_TEMPLATE.format(
            name=spec.name,
            description=spec.description,
            init_params=init_param_str,
            init_body=init_body_str,
            method_params=method_params,
            method_param_docs=method_param_docs,
            return_type=spec.parameters.get("return", {}).get("type", "Any"),
            return_description=spec.parameters.get("return", {}).get("description", "Result"),
            method_implementation="pass  # TODO: Implement"
        )

    def _get_implementation(self, spec: ToolSpec) -> str:
        """Get implementation code based on tool category and name."""
        # Check for existing template
        template_key = f"{spec.category}_{spec.name}"
        if template_key in self.templates:
            return self.templates[template_key].split("Implementation:\n")[-1].strip()

        # Generate generic implementation
        if "read" in spec.name.lower():
            return '''    # Read operation
    try:
        result = await perform_read_operation()
        return result
    except Exception as e:
        logger.error(f"Read failed: {e}")
        raise'''

        elif "write" in spec.name.lower():
            return '''    # Write operation
    try:
        result = await perform_write_operation()
        return result
    except Exception as e:
        logger.error(f"Write failed: {e}")
        raise'''

        elif "validate" in spec.name.lower():
            return '''    # Validation logic
    try:
        # Perform validation
        is_valid = check_validity()
        return {"valid": is_valid}
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {"valid": False, "error": str(e)}'''

        else:
            return '''    # TODO: Implement tool logic
    raise NotImplementedError("Tool implementation pending")'''

    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        lines = code.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)

        return imports

    def _identify_dependencies(self, code: str) -> List[str]:
        """Identify external dependencies from code."""
        dependencies = []

        # Common patterns
        patterns = [
            "import jsonschema",
            "import requests",
            "import pandas",
            "import numpy",
            "from fastapi",
            "from pydantic"
        ]

        for pattern in patterns:
            if pattern in code:
                lib = pattern.split()[-1].split('.')[0]
                if lib not in dependencies:
                    dependencies.append(lib)

        return dependencies

    def _generate_test_code(self, spec: ToolSpec) -> str:
        """Generate test code for the tool."""
        test_name = f"test_{spec.name}"

        return f'''
async def {test_name}():
    """Test the {spec.name} tool."""
    # TODO: Implement test
    pass
'''

    def create_file_tool(self, name: str, operation: str) -> GeneratedTool:
        """
        Create a file manipulation tool.

        Args:
            name: Tool name
            operation: Operation type (read/write/delete)

        Returns:
            Generated tool
        """
        spec = ToolSpec(
            name=f"{operation}_{name}",
            description=f"{operation.capitalize()} {name} file",
            parameters={
                "file_path": {
                    "type": "str",
                    "description": "Path to the file",
                    "required": True
                }
            },
            function=lambda x: x,  # Placeholder
            category="file"
        )

        return self.create_tool_from_spec(spec)

    def create_api_tool(self, name: str, endpoint: str, method: str = "GET") -> GeneratedTool:
        """
        Create an API interaction tool.

        Args:
            name: Tool name
            endpoint: API endpoint
            method: HTTP method

        Returns:
            Generated tool
        """
        spec = ToolSpec(
            name=f"{method.lower()}_{name}",
            description=f"Make {method} request to {endpoint}",
            parameters={
                "url": {
                    "type": "str",
                    "description": "Request URL",
                    "required": True
                },
                "headers": {
                    "type": "Dict[str, str]",
                    "description": "Request headers",
                    "required": False
                },
                "data": {
                    "type": "Any",
                    "description": "Request data",
                    "required": False
                }
            },
            function=lambda x: x,  # Placeholder
            category="network"
        )

        return self.create_tool_from_spec(spec)

    def get_tool(self, name: str) -> Optional[GeneratedTool]:
        """Get a registered tool by name."""
        return self.tools.get(name)

    def list_tools(self, category: str = None) -> List[Dict]:
        """
        List all tools.

        Args:
            category: Filter by category

        Returns:
            List of tool specifications
        """
        tools = []

        for tool in self.tools.values():
            if category is None or tool.spec.category == category:
                tools.append(tool.spec.to_dict())

        return tools

    def save_tool(self, name: str, directory: Path = None) -> bool:
        """
        Save a tool to file.

        Args:
            name: Tool name
            directory: Output directory

        Returns:
            True if saved successfully
        """
        tool = self.get_tool(name)
        if not tool:
            return False

        directory = directory or Path("generated_tools")
        directory.mkdir(exist_ok=True)

        # Save main code
        file_path = directory / f"{name}.py"
        with open(file_path, 'w') as f:
            f.write(tool.code)

        # Save tests if available
        if tool.test_code:
            test_path = directory / f"test_{name}.py"
            with open(test_path, 'w') as f:
                f.write(tool.test_code)

        # Save spec
        spec_path = directory / f"{name}_spec.json"
        with open(spec_path, 'w') as f:
            json.dump(tool.spec.to_dict(), f, indent=2)

        LOGGER.info(f"Saved tool {name} to {directory}")
        return True

    def get_statistics(self) -> Dict:
        """Get tool creation statistics."""
        stats = {
            "total_tools": len(self.tools),
            "by_category": {},
            "with_tests": 0,
            "categories": list(self.categories.keys())
        }

        for tool in self.tools.values():
            # Count by category
            cat = tool.spec.category
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

            # Count with tests
            if tool.test_code:
                stats["with_tests"] += 1

        return stats


# Global instance
_toolsmith_agent: Optional[ToolsmithAgent] = None


def get_toolsmith_agent() -> ToolsmithAgent:
    """Get or create the global ToolsmithAgent instance."""
    global _toolsmith_agent
    if _toolsmith_agent is None:
        _toolsmith_agent = ToolsmithAgent()
    return _toolsmith_agent


def initialize_toolsmith_agent():
    """Initialize the ToolsmithAgent system."""
    get_toolsmith_agent()
    LOGGER.info("ToolsmithAgent system initialized")


# Convenience functions
def create_file_tool(name: str, operation: str) -> GeneratedTool:
    """Create a file manipulation tool."""
    agent = get_toolsmith_agent()
    return agent.create_file_tool(name, operation)


def create_api_tool(name: str, endpoint: str, method: str = "GET") -> GeneratedTool:
    """Create an API interaction tool."""
    agent = get_toolsmith_agent()
    return agent.create_api_tool(name, endpoint, method)
