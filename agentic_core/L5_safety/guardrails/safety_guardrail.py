from __future__ import annotations

"""
L5 Safety: SafetyGuardrail
Enforces Zero-Loss principles during code mutation.
"""
import ast
from typing import Any


class SafetyGuardrail:
    """Enforces Zero-Loss principles during mutation."""

    def __init__(self, deletion_limit: int = 110):
        """
        Initialize SafetyGuardrail.

        Args:
            deletion_limit: Maximum number of lines that can be deleted in standard mode
        """
        self.deletion_limit = deletion_limit

    def verify_change(
        self, original_code: str, new_code: str, fission_active: bool = False
    ) -> tuple[bool, str]:
        """
        Verify that code changes are safe and don't violate zero-loss principles.

        Args:
            original_code: Original code before mutation
            new_code: New code after mutation
            fission_active: Whether atomic fission is active (allows mass deletion)

        Returns:
            Tuple of (is_safe, message)
        """
        if not new_code.strip():
            return (False, "Safety Block: Attempted to wipe file.")
        try:
            ast.parse(new_code)
        except SyntaxError as e:
            return (
                False,
                f"Safety Block: Mutation introduced syntax error: {e.msg} at line {e.lineno}",
            )
        orig_len: Any = len(original_code.splitlines())
        new_len: Any = len(new_code.splitlines())
        delta: Any = orig_len - new_len
        if delta == 0 and original_code == new_code and (not fission_active):
            return (
                False,
                "Safety Block: Mutation resulted in no change (possible engine failure).",
            )
        if fission_active:
            return (True, "Fission Whitelist: Mass deletion permitted for Facade.")
        if delta > self.deletion_limit:
            return (False, f"Safety Block: Mass deletion detected ({delta} lines).")
        return (True, "Safety Pass.")
