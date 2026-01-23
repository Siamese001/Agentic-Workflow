from __future__ import annotations

"""
ConfigurationSecurityGuardrail: Consolidated configuration and secrets management.
Merges: SecureConfigManager, SecureCheckpointManager, mcp_sovereign, l5_policy
"""

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.utils.core_extensions.decorators import standard_heal

logger = logging.getLogger(__name__)


@dataclass
class ConfigurationSecurityGuardrail(SovereignBaseAgent):
    """
    Consolidated configuration security with composable rules.
    Handles: Secret detection, config validation, policy enforcement.
    """

    debug_mode: bool = False
    enabled_rules: list[str] = field(
        default_factory=lambda: [
            "secret_detection",
            "config_validation",
            "policy_enforcement",
        ]
    )

    def __post_init__(self):
        self.name = "ConfigurationSecurityGuardrail"
        self.checks_executed = 0
        self.violations_found = 0

    async def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate configuration against security rules."""
        logger.info(f"[{self.name}] Validating configuration")

        result = {
            "valid": True,
            "violations": [],
            "rules_applied": [],
        }

        try:
            for rule in self.enabled_rules:
                rule_result = await self._apply_rule(rule, config)
                result["rules_applied"].append(rule)

                if not rule_result.get("valid"):
                    result["valid"] = False
                    result["violations"].extend(rule_result.get("violations", []))

            self.checks_executed += 1
            if not result["valid"]:
                self.violations_found += 1

            return result

        except Exception as e:
            logger.error(f"[{self.name}] Validation error: {e}")
            return {
                "valid": False,
                "violations": [{"type": "validation_error", "message": str(e)}],
                "error": str(e),
            }

    async def _apply_rule(self, rule: str, config: dict[str, Any]) -> dict[str, Any]:
        """Apply a specific validation rule."""
        if rule == "secret_detection":
            return self._detect_secrets(config)
        elif rule == "config_validation":
            return self._validate_config_structure(config)
        elif rule == "policy_enforcement":
            return self._enforce_policies(config)
        return {"valid": True}

    def _detect_secrets(self, config: dict[str, Any]) -> dict[str, Any]:
        """Detect exposed secrets in configuration."""
        violations = []
        secret_patterns = {
            r"password\s*[:=]": "password",
            r"api[_-]?key\s*[:=]": "api_key",
            r"secret\s*[:=]": "secret",
            r"token\s*[:=]": "token",
            r"aws[_-]?secret": "aws_secret",
        }

        config_str = str(config).lower()
        for pattern, secret_type in secret_patterns.items():
            if re.search(pattern, config_str, re.IGNORECASE):
                violations.append(
                    {
                        "type": f"exposed_{secret_type}",
                        "severity": "critical",
                        "message": f"Potential {secret_type} exposed in configuration",
                    }
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def _validate_config_structure(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate configuration structure and required fields."""
        violations = []

        if not isinstance(config, dict):
            violations.append(
                {
                    "type": "invalid_structure",
                    "severity": "high",
                    "message": "configuration must be a dictionary",
                }
            )

        required_fields = ["version", "environment"]
        for field in required_fields:
            if field not in config:
                violations.append(
                    {
                        "type": "missing_field",
                        "severity": "medium",
                        "message": f"Missing required field: {field}",
                    }
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def _enforce_policies(self, config: dict[str, Any]) -> dict[str, Any]:
        """Enforce security policies on configuration."""
        violations = []

        # Check for debug mode in production
        if config.get("environment") == "production" and config.get("debug_mode"):
            violations.append(
                {
                    "type": "debug_in_production",
                    "severity": "critical",
                    "message": "Debug mode enabled in production environment",
                }
            )

        # Check for insecure protocols
        if config.get("protocol") == "http" and config.get("environment") == "production":
            violations.append(
                {
                    "type": "insecure_protocol",
                    "severity": "high",
                    "message": "HTTP protocol used in production (should be HTTPS)",
                }
            )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def _run_self_tests(self) -> bool:
        """Validate agent structure."""
        assert hasattr(self, "name"), "Missing name"
        assert hasattr(self, "enabled_rules"), "Missing enabled_rules"
        return True

    @standard_heal
    def heal_repository(self, dry_run: bool = True, **kwargs) -> dict[str, Any]:
        """Repository healing with parent chain invocation."""
        result = super().heal_repository(dry_run=dry_run, **kwargs)
        return {"violations_fixed": 0, "skipped": 0, "parent": result}
