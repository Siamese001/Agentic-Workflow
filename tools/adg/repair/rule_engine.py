"""Rule engine for ADG Repair Orchestrator.

Handles rule registration, matching, and conflict resolution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from tqdm import tqdm

if TYPE_CHECKING:
    from .base_rule import BaseRepairRule
    from .types import Deficiency, RuleMatch


# Global rule registry
_rule_registry: dict[str, type[BaseRepairRule]] = {}
_rule_instances: dict[str, BaseRepairRule] = {}


def repair_rule(rule_id: str, priority: int = 100) -> Callable:
    """Decorator to register a repair rule.

    Usage:
        @repair_rule("fix_missing_all", priority=10)
        class FixMissingAllRule(BaseRepairRule):
            ...

    Args:
        rule_id: Unique identifier for this rule
        priority: Priority (lower = higher priority, default 100)

    Returns:
        Decorator function
    """

    def decorator(cls: type[BaseRepairRule]) -> type[BaseRepairRule]:
        cls.rule_id = rule_id
        cls.rule_priority = priority
        _rule_registry[rule_id] = cls
        return cls

    return decorator


class RuleEngine:
    """Engine for managing and executing repair rules."""

    def __init__(self):
        """Initialize the rule engine with registered rules."""
        self._rules: dict[str, BaseRepairRule] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        """Load all registered rules."""
        global _rule_instances

        # Use cached instances if available
        if _rule_instances:
            self._rules = dict(_rule_instances)
            return

        # Create instances of all registered rules
        for rule_id, rule_class in _rule_registry.items():
            try:
                instance = rule_class()
                self._rules[rule_id] = instance
            except (TypeError, AttributeError, ImportError, ValueError) as e:
                print(f"[RuleEngine] Warning: Failed to load rule {rule_id}: {e}")

        # Cache for future use
        _rule_instances = dict(self._rules)

    def get_rule(self, rule_id: str) -> BaseRepairRule | None:
        """Get a rule by ID.

        Args:
            rule_id: The rule identifier

        Returns:
            The rule instance, or None if not found
        """
        return self._rules.get(rule_id)

    def list_rules(self) -> list[dict]:
        """List all available rules.

        Returns:
            List of rule info dictionaries
        """
        return [rule.get_info() for rule in self._rules.values()]

    def match_deficiency(self, deficiency: Deficiency) -> list[RuleMatch]:
        """Find all rules that match a deficiency.

        Args:
            deficiency: The deficiency to match

        Returns:
            List of RuleMatch objects, sorted by priority
        """
        matches = []

        for rule_id, rule in tqdm(self._rules.items(), desc="Processing", unit="item"):
            try:
                if rule.match(deficiency):
                    can_apply, _ = rule.can_fix(deficiency)
                    matches.append(
                        RuleMatch(
                            rule_id=rule_id,
                            rule_priority=rule.rule_priority,
                            can_apply=can_apply,
                            confidence_adjusted=deficiency.confidence,
                        ),
                    )
            except (TypeError, AttributeError, ValueError, KeyError) as e:
                print(f"[RuleEngine] Warning: Rule {rule_id} match failed: {e}")

        # Sort by priority (lower = higher priority)
        matches.sort(key=lambda m: m.rule_priority)
        return matches

    def find_best_rule(self, deficiency: Deficiency) -> BaseRepairRule | None:
        """Find the best rule for a deficiency.

        Args:
            deficiency: The deficiency to match

        Returns:
            Best matching rule, or None if no match
        """
        matches = self.match_deficiency(deficiency)

        # Filter to only rules that can apply
        applicable = [m for m in matches if m.can_apply]

        if not applicable:
            return None

        # Return the highest priority (lowest number) rule
        best_match = applicable[0]
        return self._rules.get(best_match.rule_id)

    def detect_conflicts(self, deficiencies: list[Deficiency]) -> list[tuple[str, str, str]]:
        """Detect conflicts between deficiencies and their assigned rules.

        Args:
            deficiencies: List of deficiencies to check

        Returns:
            List of conflict tuples (deficiency_id, rule_id, conflict_reason)
        """
        conflicts = []
        file_rules: dict[str, list[tuple[str, str]]] = {}

        for deficiency in tqdm(deficiencies, desc="Processing", unit="item"):
            matches = self.match_deficiency(deficiency)
            applicable = [m for m in matches if m.can_apply]

            if not applicable:
                continue

            # Track which rules want to modify which files
            file_path = deficiency.file_path
            if file_path not in file_rules:
                file_rules[file_path] = []

            for match in tqdm(applicable[:3], desc="Processing", unit="item"):  # Check top 3 rules
                rule_id = match.rule_id

                # Check for multiple rules modifying same file
                existing = [r for r in file_rules[file_path] if r[0] != rule_id]
                if existing:
                    conflicts.append(
                        (
                            deficiency.id,
                            rule_id,
                            f"Rule {rule_id} conflicts with {existing[0][0]} for file {file_path}",
                        ),
                    )

                file_rules[file_path].append((rule_id, deficiency.id))

        return conflicts

    def reload_rules(self) -> None:
        """Reload all rules (useful for dynamic rule updates)."""
        self._rules.clear()
        _rule_instances.clear()
        self._load_rules()


def register_builtin_rules() -> None:
    """Register all built-in repair rules.

    This function imports all rule modules to trigger their registration.
    """
    # Import will trigger @repair_rule decorators
    try:
        from . import rules  # noqa: F401
    except ImportError:
        pass  # Rules module may not exist yet
