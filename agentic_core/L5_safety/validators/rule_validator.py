"""
Rule Validator for L5 Safety Layer

Validates content against specific safety rules.
"""

from typing import Dict, Any, List, Callable

class RuleValidator:
    """Validates content against specific safety rules."""

    def __init__(self):
        self.rules: Dict[str, Callable] = {}
        self.rule_descriptions: Dict[str, str] = {}
        self._setup_default_rules()

    def add_rule(self, name: str, rule_func: Callable, description: str = ""):
        """Add a validation rule."""
        self.rules[name] = rule_func
        self.rule_descriptions[name] = description

    def remove_rule(self, name: str):
        """Remove a validation rule."""
        if name in self.rules:
            del self.rules[name]
            del self.rule_descriptions[name]

    def validate_rules(self, content: str, rule_names: List[str] = None) -> Dict[str, Any]:
        """Validate content against specified rules or all rules."""
        if rule_names is None:
            rule_names = list(self.rules.keys())

        results = {
            "passed_rules": [],
            "failed_rules": [],
            "rule_details": {},
            "overall_pass": True
        }

        for rule_name in rule_names:
            if rule_name in self.rules:
                try:
                    rule_result = self.rules[rule_name](content)
                    results["rule_details"][rule_name] = {
                        "passed": rule_result,
                        "description": self.rule_descriptions.get(rule_name, "")
                    }

                    if rule_result:
                        results["passed_rules"].append(rule_name)
                    else:
                        results["failed_rules"].append(rule_name)
                        results["overall_pass"] = False
                except Exception as e:
                    results["failed_rules"].append(rule_name)
                    results["rule_details"][rule_name] = {
                        "passed": False,
                        "error": str(e),
                        "description": self.rule_descriptions.get(rule_name, "")
                    }
                    results["overall_pass"] = False

        return results

    def _setup_default_rules(self):
        """Setup default validation rules."""
        # No PII rule
        self.add_rule(
            "no_pii",
            lambda content: not self._contains_pii(content),
            "Content must not contain personally identifiable information"
        )

        # No secrets rule
        self.add_rule(
            "no_secrets",
            lambda content: not self._contains_secrets(content),
            "Content must not contain passwords, tokens, or secrets"
        )

        # Length limit rule
        self.add_rule(
            "length_limit",
            lambda content: len(content) <= 10000,
            "Content must not exceed 10,000 characters"
        )

    def _contains_pii(self, content: str) -> bool:
        """Check if content contains PII."""
        import re
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        phone_pattern = re.compile(r'\b\d{3}-\d{3}-\d{4}\b')
        return bool(email_pattern.search(content) or phone_pattern.search(content))

    def _contains_secrets(self, content: str) -> bool:
        """Check if content contains secrets."""
        secret_keywords = ["password", "secret", "token", "key", "credential"]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in secret_keywords)
