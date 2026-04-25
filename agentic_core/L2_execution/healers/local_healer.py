"""C3 Local Healer - Deterministic rule-based repair.

10C-REQ-136: Attempt deterministic rule fix schema repair known type casting
flag for LLM path if exceeds local rules
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .failure_signal import FailureSignal


@dataclass
class HealResult:
    """Result of local healing attempt."""

    success: bool
    repair_applied: str
    original_error: str
    fixed_value: Any | None = None
    requires_llm: bool = False
    reason: str = ""


class LocalHealer:
    """C3 Local healer using deterministic rules.

    10C-REQ-136: Attempt deterministic rule fix schema repair known type casting.
    """

    def __init__(self) -> None:
        self._rules: list[tuple[str, Callable[[FailureSignal], HealResult]]] = []
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default healing rules."""
        self._rules.append(("schema_validation_error", self._heal_schema_error))
        self._rules.append(("type_mismatch", self._heal_type_mismatch))
        self._rules.append(("missing_required_field", self._heal_missing_field))

    def heal(self, signal: FailureSignal) -> HealResult:
        """Attempt local deterministic healing.

        10C-REQ-136: Returns success or flags for LLM path if exceeds local rules.
        """
        # Find matching rule
        for error_pattern, handler in self._rules:
            if error_pattern in signal.error_code:
                result = handler(signal)
                if result.success:
                    return result

        # No local rule could heal - flag for LLM path
        return HealResult(
            success=False,
            repair_applied="none",
            original_error=signal.error_code,
            requires_llm=True,
            reason="exceeds_local_rules_no_matching_pattern",
        )

    def _heal_schema_error(self, signal: FailureSignal) -> HealResult:
        """Heal schema validation errors."""
        context = signal.context_snapshot

        # Check if we have schema info in context
        if "schema" not in context:
            return HealResult(
                success=False,
                repair_applied="none",
                original_error=signal.error_code,
                requires_llm=True,
                reason="no_schema_in_context",
            )

        # Attempt schema repair by removing unknown fields
        data = context.get("data", {})
        schema = context.get("schema", {})
        allowed_fields = set(schema.get("required", [])) | set(schema.get("optional", []))

        repaired = {k: v for k, v in data.items() if k in allowed_fields}

        return HealResult(
            success=True,
            repair_applied="schema_prune_unknown_fields",
            original_error=signal.error_code,
            fixed_value=repaired,
            requires_llm=False,
            reason=f"pruned_to_allowed_fields:{allowed_fields}",
        )

    def _heal_type_mismatch(self, signal: FailureSignal) -> HealResult:
        """Heal type mismatch errors."""
        context = signal.context_snapshot
        field = context.get("field", "")
        expected_type = context.get("expected_type", "")
        actual_value = context.get("actual_value")

        # Attempt type casting
        try:
            if expected_type == "int":
                fixed_value = int(actual_value)
                return HealResult(
                    success=True,
                    repair_applied="type_cast_to_int",
                    original_error=signal.error_code,
                    fixed_value=fixed_value,
                    requires_llm=False,
                )
            elif expected_type == "str":
                fixed_value = str(actual_value)
                return HealResult(
                    success=True,
                    repair_applied="type_cast_to_str",
                    original_error=signal.error_code,
                    fixed_value=fixed_value,
                    requires_llm=False,
                )
            elif expected_type == "bool":
                fixed_value = bool(actual_value)
                return HealResult(
                    success=True,
                    repair_applied="type_cast_to_bool",
                    original_error=signal.error_code,
                    fixed_value=fixed_value,
                    requires_llm=False,
                )
        except (
            ValueError,
            TypeError,
        ):  # guardian: allow-silent-swallow -- value fix attempt: non-fatal, returns HealResult(success=False)
            pass

        return HealResult(
            success=False,
            repair_applied="none",
            original_error=signal.error_code,
            requires_llm=True,
            reason=f"cannot_cast_{actual_value}_to_{expected_type}",
        )

    def _heal_missing_field(self, signal: FailureSignal) -> HealResult:
        """Heal missing required field errors."""
        context = signal.context_snapshot
        field = context.get("missing_field", "")
        default_value = context.get("default_value")

        if default_value is not None:
            return HealResult(
                success=True,
                repair_applied="inject_default_value",
                original_error=signal.error_code,
                fixed_value={field: default_value},
                requires_llm=False,
            )

        return HealResult(
            success=False,
            repair_applied="none",
            original_error=signal.error_code,
            requires_llm=True,
            reason=f"no_default_for_field:{field}",
        )

    def register_rule(self, error_pattern: str, handler: Callable[[FailureSignal], HealResult]) -> None:
        """Register a healing rule."""
        self._rules.append((error_pattern, handler))
