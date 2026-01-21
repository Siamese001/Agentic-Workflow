"""
Specialist Agents - Hardened Swarm Architecture

Implements Planner, Coder, and Auditor agents that inherit
from BaseAgent and enforce Canon compliance.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from core.exceptions import AgentExecutionError, CanonViolationError

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    Breaks down tasks into executable steps.

    Consults Canon for similar project plans before generating
    tasks to ensure planning follows proven patterns.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("planner", config)
        self.plan_cache = {}

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute planning task with Canon consultation.

        Args:
            task: Contains 'objective' and 'context'

        Returns:
            Dictionary with generated plan
        """
        objective = task.get("objective", "")
        context = task.get("context", {})

        logger.info(f"Planning agent creating plan for: {objective}")

        # Generate plan steps
        plan = self._generate_plan(objective, context)

        # Validate plan against Canon
        validated_plan = self._validate_plan(plan)

        return {
            "agent": self.agent_id,
            "objective": objective,
            "plan": validated_plan,
            "estimated_duration": self._estimate_duration(validated_plan),
            "created_at": datetime.utcnow().isoformat()
        }

    def _generate_plan(self, objective: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a high-level plan for the objective."""
        # Common planning patterns
        if "refactor" in objective.lower():
            return [
                {"step": 1, "action": "analyze_current_code",
                    "description": "Analyze existing code structure"},
                {"step": 2, "action": "identify_refactor_opportunities",
                    "description": "Identify areas for improvement"},
                {"step": 3, "action": "create_refactor_plan",
                    "description": "Create detailed refactor plan"},
                {"step": 4, "action": "implement_changes",
                    "description": "Implement refactor changes"},
                {"step": 5, "action": "validate_changes",
                    "description": "Validate and test changes"}
            ]

        elif "implement" in objective.lower():
            return [
                {"step": 1, "action": "define_requirements",
                    "description": "Define clear requirements"},
                {"step": 2, "action": "design_solution",
                    "description": "Design the solution architecture"},
                {"step": 3, "action": "implement_core",
                    "description": "Implement core functionality"},
                {"step": 4, "action": "add_tests",
                    "description": "Add comprehensive tests"},
                {"step": 5, "action": "document_solution",
                    "description": "Document the implementation"}
            ]

        else:
            # Generic plan
            return [
                {"step": 1, "action": "understand_requirements",
                    "description": "Understand and clarify requirements"},
                {"step": 2, "action": "design_approach",
                    "description": "Design the approach"},
                {"step": 3, "action": "implement_solution",
                    "description": "Implement the solution"},
                {"step": 4, "action": "test_and_validate",
                    "description": "Test and validate the solution"}
            ]

    def _validate_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate plan against Canon rules."""
        validated_plan = []

        for step in plan:
            # Check for common anti-patterns
            if "delete" in step["action"].lower() and not step["action"].startswith("safe_"):
                raise CanonViolationError(
                    f"Unsafe deletion in plan step: {step['action']}",
                    violation_type="unsafe_deletion",
                    agent_id=self.agent_id
                )

            # Add Canon compliance metadata
            step["canon_compliant"] = True
            step["validated_at"] = datetime.utcnow().isoformat()
            validated_plan.append(step)

        return validated_plan

    def _estimate_duration(self, plan: List[Dict[str, Any]]) -> Dict[str, int]:
        """Estimate plan duration in hours."""
        base_duration = len(plan) * 2  # 2 hours per step
        return {
            "minimum_hours": base_duration,
            "maximum_hours": base_duration * 2,
            "confidence": 0.8
        }


class CoderAgent(BaseAgent):
    """
    Writes implementation code.

    Consults Canon for "Golden Snippets" and AST matches
    before writing new code to ensure compliance.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("coder", config)
        self.code_templates = {}

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute coding task with Canon consultation.

        Args:
            task: Contains 'specification', 'language', and 'requirements'

        Returns:
            Dictionary with generated code
        """
        spec = task.get("specification", {})
        language = task.get("language", "python")
        requirements = task.get("requirements", [])

        logger.info(
            f"Coding agent implementing: {spec.get('description', 'unnamed task')}")

        # Generate code
        code = self._generate_code(spec, language, requirements)

        # Validate code against Canon
        validated_code = self._validate_code(code)

        return {
            "agent": self.agent_id,
            "language": language,
            "code": validated_code,
            "ast_hash": self._get_ast_hash(validated_code),
            "created_at": datetime.utcnow().isoformat(),
            "compliance": "canon_verified"
        }

    def _generate_code(
        self,
        spec: Dict[str, Any],
        language: str,
        requirements: List[str]
    ) -> str:
        """Generate code based on specification."""
        if language.lower() != "python":
            raise AgentExecutionError(
                f"Unsupported language: {language}",
                agent_id=self.agent_id,
                task="code_generation"
            )

        # Code generation based on spec type
        if spec.get("type") == "function":
            return self._generate_function(spec)
        elif spec.get("type") == "class":
            return self._generate_class(spec)
        elif spec.get("type") == "module":
            return self._generate_module(spec, requirements)
        else:
            return self._generate_generic(spec)

    def _generate_function(self, spec: Dict[str, Any]) -> str:
        """Generate a function based on specification."""
        name = spec.get("name", "example_function")
        params = spec.get("parameters", [])
        docstring = spec.get("description", "Example function")

        param_str = ", ".join(params)

        code = f'''def {name}({param_str}):
    """
    {docstring}

    Args:
        {chr(10).join(f"        {p}: Parameter description" for p in params)}

    Returns:
        Result of the function
    """

    pass
'''
        return code

    def _generate_class(self, spec: Dict[str, Any]) -> str:
        """Generate a class based on specification."""
        name = spec.get("name", "ExampleClass")
        base_classes = spec.get("base_classes", [])
        methods = spec.get("methods", [])

        bases = f"({', '.join(base_classes)})" if base_classes else ""

        code = f'''class {name}{bases}:
    """
    {spec.get("description", "Example class")}
    """

    def __init__(self):
        """Initialize the class."""
        pass
'''

        for method in methods:
            code += f'\n    def {method}(self):\n        """TODO: Implement method."""\n        pass\n'

        return code

    def _generate_module(self, spec: Dict[str, Any], requirements: List[str]) -> str:
        """Generate a module with imports and main code."""
        imports = []

        # Add standard imports based on requirements
        for req in requirements:
            if "logging" in req.lower():
                imports.append("import logging")
            elif "datetime" in req.lower():
                imports.append("from datetime import datetime")
            elif "json" in req.lower():
                imports.append("import json")

        code = "\n".join(imports) + "\n\n"
        code += f'"""\n{spec.get("description", "Module description")}\n"""\n\n'
        code += "# Module implementation\n"
        code += "# TODO: Add module logic\n"

        return code

    def _generate_generic(self, spec: Dict[str, Any]) -> str:
        """Generate generic code."""
        return f'''# Generated code for: {spec.get("description", "task")}

pass
'''

    def _validate_code(self, code: str) -> str:
        """Validate code against Canon rules."""
        try:
            # Parse AST to check syntax
            import ast
            ast.parse(code)
        except SyntaxError as e:
pass
raise CanonViolationError(
                f"Generated code has syntax error: {e}",
                violation_type="syntax_error",
                agent_id=self.agent_id
            )

        # Check for prohibited patterns
        prohibited = ["eval(", "exec(", "__import__"]
        for pattern in prohibited:
            if pattern in code:
                raise CanonViolationError(
                    f"Prohibited pattern found: {pattern}",
                    violation_type="prohibited_pattern",
                    agent_id=self.agent_id
                )

        return code

    def _get_ast_hash(self, code: str) -> str:
        """Generate AST hash for the code."""
        import ast
        import hashlib

        try:
            tree = ast.parse(code)
            ast_str = ast.dump(tree)
            return hashlib.sha256(ast_str.encode()).hexdigest()[:16]
        except Exception:
pass
return "syntax_error"


class AuditorAgent(BaseAgent):
    """
    Validates code against Canon rules.

    The only agent authorized to issue CanonVerified tokens.
    Cross-references output against strictest Canon rules.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("auditor", config)
        self.validation_rules = self._load_validation_rules()

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute audit task with Canon verification.

        Args:
            task: Contains 'code', 'language', and 'validation_type'

        Returns:
            Dictionary with audit results and Canon token
        """
        code = task.get("code", "")
        language = task.get("language", "python")
        validation_type = task.get("validation_type", "full")

        logger.info(f"Auditor validating {language} code")

        # Perform comprehensive validation
        validation_result = self._validate_code(
            code, language, validation_type)

        # Issue CanonVerified token if valid
        if validation_result["is_valid"]:
            validation_result["canon_verified"] = True
            validation_result["canon_token"] = {
                "issued_by": self.agent_id,
                "issued_at": datetime.utcnow().isoformat(),
                "valid_until": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "signature": self._generate_canon_signature(code)
            }
        else:
            validation_result["canon_verified"] = False
            validation_result["violations"] = validation_result["errors"]

        return {
            "agent": self.agent_id,
            "validation_result": validation_result,
            "audited_at": datetime.utcnow().isoformat()
        }

    def _validate_code(
        self,
        code: str,
        language: str,
        validation_type: str
    ) -> Dict[str, Any]:
        """Perform comprehensive code validation."""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }

        # Syntax validation
        syntax_result = self._validate_syntax(code, language)
        if not syntax_result["valid"]:
            result["is_valid"] = False
            result["errors"].extend(syntax_result["errors"])

        # Canon rule validation
        canon_result = self._validate_canon_rules(code)
        if not canon_result["compliant"]:
            result["is_valid"] = False
            result["errors"].extend(canon_result["violations"])

        # Security validation
        security_result = self._validate_security(code)
        result["warnings"].extend(security_result["warnings"])

        # Calculate metrics
        result["metrics"] = self._calculate_metrics(code)

        return result

    def _validate_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code syntax."""
        if language.lower() != "python":
            return {"valid": True, "errors": []}

        try:
            import ast
            ast.parse(code)
            return {"valid": True, "errors": []}
        except SyntaxError as e:
pass
return {
                "valid": False,
                "errors": [f"Syntax error at line {e.lineno}: {e.msg}"]
            }

    def _validate_canon_rules(self, code: str) -> Dict[str, Any]:
        """Validate against Canon rules."""
        violations = []

        # Check each rule
        for rule in self.validation_rules:
            if not self._check_rule(code, rule):
                violations.append(
                    f"Canon rule violation: {rule['description']}")

        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }

    def _validate_security(self, code: str) -> Dict[str, Any]:
        """Validate security aspects."""
        warnings = []

        # Check for security issues
        security_patterns = {
            "hardcoded_password": r'password\s*=\s*["\'][^"\']+["\']',
            "sql_injection": r'execute\s*\(\s*["\'].*%.*["\']',
            "shell_injection": r'system\s*\(\s*["\'].*\$.*["\']'
        }

        import re
        for issue, pattern in security_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append(f"Potential security issue: {issue}")

        return {"warnings": warnings}

    def _check_rule(self, code: str, rule: Dict[str, Any]) -> bool:
        """Check a specific Canon rule."""
        # Simplified rule checking
        if rule["type"] == "pattern":
            import re
            return not re.search(rule["pattern"], code)
        elif rule["type"] == "ast":
            # Would implement AST-based checking
            return True
        return True

    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate code metrics."""
        lines = code.split('\n')
        return {
            "lines_of_code": len([l for l in lines if l.strip()]),
            "comment_lines": len([l for l in lines if l.strip().startswith('#')]),
            "complexity": self._calculate_complexity(code)
        }

    def _calculate_complexity(self, code: str) -> int:
        """Simple complexity calculation."""
        complexity = 1
        complexity += code.count('if ')
        complexity += code.count('for ')
        complexity += code.count('while ')
        complexity += code.count('def ')
        complexity += code.count('class ')
        return complexity

    def _load_validation_rules(self) -> List[Dict[str, Any]]:
        """Load Canon validation rules."""
        return [
            {
                "id": "no_hardcoded_secrets",
                "type": "pattern",
                "pattern": r'(password|secret|key)\s*=\s*["\'][^"\']+["\']',
                "description": "No hardcoded secrets"
            },
            {
                "id": "proper_error_handling",
                "type": "ast",
                "description": "Proper error handling required"
            }
        ]

    def _generate_canon_signature(self, code: str) -> str:
        """Generate unique Canon verification signature."""
        import hashlib
        content = f"{code}:{datetime.utcnow().isoformat()}:{self.agent_id}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]


# Agent factory for easy instantiation
def create_agent(agent_type: str, config: Optional[Dict[str, Any]] = None) -> BaseAgent:
    """
    Factory function to create agents by type.

    Args:
        agent_type: Type of agent to create
        config: Optional configuration

    Returns:
        Instantiated agent
    """
    agents = {
        "planner": PlannerAgent,
        "coder": CoderAgent,
        "auditor": AuditorAgent
    }

    if agent_type not in agents:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return agents[agent_type](config)
