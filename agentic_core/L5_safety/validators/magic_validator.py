"""
Magic Configuration Anti-Pattern Detector

Detects hardcoded constants in business logic that should be
externalized to configuration files.

Pattern Detection:
- Hardcoded model names ("gpt-4", "gpt-3.5-turbo")
- Hardcoded timeouts and thresholds
- Hardcoded API endpoints
- Hardcoded magic numbers in business logic
"""

import ast
import re
from pathlib import Path

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)


class MagicConfigDetector(AntiPatternDetector):
    """
    Detects hardcoded configuration values in business logic.

    Magic configuration prevents runtime tuning and
    environment-specific adaptation.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-magic-config"

    # Model name patterns
    MODEL_PATTERNS = [
        r"gpt-[34]",
        r"gpt-3\.5-turbo",
        r"gpt-4-turbo",
        r"gpt-4o",
        r"claude-[23]",
        r"claude-instant",
        r"text-davinci",
        r"text-embedding",
    ]

    # Timeout/threshold parameter names
    CONFIG_PARAM_NAMES = {
        "timeout",
        "threshold",
        "limit",
        "max_",
        "min_",
        "rate",
        "retry",
        "interval",
        "delay",
        "budget",
    }

    # API endpoint patterns
    API_ENDPOINT_PATTERNS = [
        r"https?://api\.",
        r"https?://.*\.openai\.com",
        r"https?://.*\.anthropic\.com",
        r"https?://.*\.pinecone\.io",
    ]

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Add default whitelisted files
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
            "*_config.py",
            "config*.py",
            "settings*.py",
            "*_defaults.py",
        ]

        # Compile patterns
        self._model_regex = re.compile("|".join(self.MODEL_PATTERNS), re.IGNORECASE)
        self._api_regex = re.compile("|".join(self.API_ENDPOINT_PATTERNS), re.IGNORECASE)

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.MAGIC_CONFIGURATION

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect magic configuration patterns in the AST."""
        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        # guardian: allow-silent-swallow
        except Exception:
            source_lines = []

        # Check function/method definitions for hardcoded defaults
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                violations.extend(self._check_function_defaults(node, file_path, source_lines))
            elif isinstance(node, ast.Assign):
                violations.extend(self._check_assignment(node, file_path, source_lines))
            elif isinstance(node, ast.Call):
                violations.extend(self._check_call_arguments(node, file_path, source_lines))

        return violations

    def _check_function_defaults(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
    ) -> list[AntiPatternViolation]:
        """Check function parameter defaults for magic values."""
        violations = []

        # Check for whitelist comment
        if node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return []

        # Check each argument with a default value
        defaults = node.args.defaults
        args = node.args.args[-len(defaults) :] if defaults else []

        for arg, default in zip(args, defaults, strict=False):
            param_name = arg.arg.lower()

            # Check if parameter name suggests configuration
            is_config_param = any(config_name in param_name for config_name in self.CONFIG_PARAM_NAMES)

            if is_config_param and isinstance(default, ast.Constant):
                value = default.value

                # Check for hardcoded numeric values
                if isinstance(value, int | float) and value not in (0, 1, -1, True, False):
                    violations.append(
                        self._create_violation(
                            node,
                            file_path,
                            f"Hardcoded {param_name}={value}",
                            str(value),
                            default.lineno if hasattr(default, "lineno") else node.lineno,
                        ),
                    )

                # Check for model names
                if isinstance(value, str) and self._model_regex.search(value):
                    violations.append(
                        self._create_violation(
                            node,
                            file_path,
                            f"Hardcoded model name '{value}'",
                            value,
                            default.lineno if hasattr(default, "lineno") else node.lineno,
                        ),
                    )

        return violations

    def _check_assignment(
        self,
        node: ast.Assign,
        file_path: Path,
        source_lines: list[str],
    ) -> list[AntiPatternViolation]:
        """Check assignments for magic configuration values."""
        violations = []

        # Check for whitelist comment
        if node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return []

        # Get variable name
        if not node.targets:
            return []

        target = node.targets[0]
        var_name = ""
        if isinstance(target, ast.Name):
            var_name = target.id.lower()
        elif isinstance(target, ast.Attribute):
            var_name = target.attr.lower()

        if not var_name:
            return []

        # Check if variable name suggests configuration
        is_config_var = any(config_name in var_name for config_name in self.CONFIG_PARAM_NAMES)

        # Check for constant string values
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value

            # Check for model names
            if self._model_regex.search(value):
                violations.append(
                    self._create_violation(
                        node,
                        file_path,
                        f"Hardcoded model name '{value}'",
                        value,
                        node.lineno,
                    ),
                )

            # Check for API endpoints
            if self._api_regex.search(value):
                violations.append(
                    self._create_violation(
                        node,
                        file_path,
                        "Hardcoded API endpoint",
                        value[:50] + "..." if len(value) > 50 else value,
                        node.lineno,
                    ),
                )

        # Check for hardcoded numeric config values
        if is_config_var and isinstance(node.value, ast.Constant):
            value = node.value.value
            if isinstance(value, int | float) and value not in (0, 1, -1, True, False):
                violations.append(
                    self._create_violation(
                        node,
                        file_path,
                        f"Hardcoded {var_name}={value}",
                        str(value),
                        node.lineno,
                    ),
                )

        return violations

    def _check_call_arguments(
        self,
        node: ast.Call,
        file_path: Path,
        source_lines: list[str],
    ) -> list[AntiPatternViolation]:
        """Check function call arguments for magic values."""
        violations = []

        # Check for whitelist comment
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return []

        # Check keyword arguments
        for keyword in node.keywords:
            if keyword.arg is None:
                continue

            param_name = keyword.arg.lower()

            # Check if parameter name suggests configuration
            is_config_param = any(config_name in param_name for config_name in self.CONFIG_PARAM_NAMES)

            if is_config_param and isinstance(keyword.value, ast.Constant):
                value = keyword.value.value

                # Check for hardcoded numeric values
                if isinstance(value, int | float) and value not in (0, 1, -1, True, False):
                    violations.append(
                        self._create_violation(
                            node,
                            file_path,
                            f"Hardcoded {param_name}={value} in function call",
                            str(value),
                            node.lineno,
                        ),
                    )

        return violations

    def _create_violation(
        self,
        node: ast.expr,
        file_path: Path,
        pattern: str,
        value: str,
        line_number: int,
    ) -> AntiPatternViolation:
        """Create a violation for detected pattern."""
        evidence = self._get_source_line(file_path, line_number)

        return AntiPatternViolation(
            file_path=file_path,
            line_number=line_number,
            category=self.category,
            message=f"Magic configuration: {pattern}",
            evidence=evidence,
            severity="warning",
            suggested_fix=self._generate_fix_suggestion(pattern, value),
            metadata={
                "pattern": pattern,
                "value": value,
            },
        )

    def _generate_fix_suggestion(self, pattern: str, value: str) -> str:
        """Generate a fix suggestion for the violation."""
        if "model" in pattern.lower():
            return f"""Externalize model name to configuration:
    from agentic_core.config.agent_defaults import AgentDefaults

    model = AgentDefaults.get("DEFAULT_MODEL", "{value}")"""

        if "timeout" in pattern.lower():
            return f"""Externalize timeout to configuration:
    from agentic_core.config.agent_defaults import AgentDefaults

    timeout = AgentDefaults.get_int("DEFAULT_TIMEOUT", {value})"""

        if "threshold" in pattern.lower():
            return f"""Externalize threshold to configuration:
    from agentic_core.config.agent_defaults import AgentDefaults

    threshold = AgentDefaults.get_float("THRESHOLD_NAME", {value})"""

        return f"""Externalize configuration value:
    import os

    # Use environment variable with fallback
    value = os.getenv("CONFIG_NAME", "{value}")

    # Or use AgentDefaults
    from agentic_core.config.agent_defaults import AgentDefaults
    value = AgentDefaults.get("CONFIG_NAME", "{value}")"""


__all__ = ["MagicConfigDetector"]
