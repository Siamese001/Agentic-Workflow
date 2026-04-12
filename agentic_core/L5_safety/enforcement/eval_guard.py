"""Eval guard — prevents unauthorized use of eval()/exec() in production code.

Provides a mode-based guard (warn / enforce) that audits and optionally
blocks unsafe eval/exec calls in the agentic pipeline.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_signs_execution_trace

logger = logging.getLogger(__name__)

# Dangerous code patterns that should be flagged
_DANGEROUS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b__import__\b"),
    re.compile(r"\bimportlib\.import_module\b"),
    re.compile(r"\bos\.system\b"),
    re.compile(r"\bsubprocess\b"),
    re.compile(r"\bopen\s*\("),
    re.compile(r"\bsocket\b"),
    re.compile(r"\bctypes\b"),
    re.compile(r"\bshutil\.rmtree\b"),
    re.compile(r"\brmtree\b"),
    re.compile(r"\bdel\s+"),
    re.compile(r"\bglobals\s*\(\s*\)"),
    re.compile(r"\bsetattr\s*\("),
    re.compile(r"\bdelattr\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"\beval\s*\("),
    re.compile(r"\bcompile\s*\("),
    re.compile(r"__builtins__"),
    re.compile(r"__globals__"),
]


class EvalGuardViolation(RuntimeError):
    """Raised when an unauthorized eval/exec call is detected."""


class EvalExecutionDeniedError(EvalGuardViolation):
    """Raised in enforce mode when dangerous code is blocked."""


class EvalGuard:
    """Guard against unauthorized eval()/exec() usage.

    Modes:
        - ``warn``: log violations but allow execution (default)
        - ``enforce``: raise ``EvalExecutionDeniedError`` on violations
    """

    def __init__(self, mode: str = "warn") -> None:
        self._mode = mode
        self._log: list[dict[str, Any]] = []

    def check(self, operation: str = "eval", code: str = "", **kwargs: Any) -> dict[str, Any]:
        """Check if code is safe to eval/exec/compile.

        Returns a result dict with ``verdict`` ('allow' or 'deny') and
        optional ``violations`` list.
        """
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        violations = self._scan(code)
        verdict = "deny" if violations else "allow"

        entry: dict[str, Any] = {
            "operation": operation,
            "code": code,
            "verdict": verdict,
            "violations": violations,
            "metadata": kwargs.get("metadata", {}),
        }
        self._log.append(entry)

        # ADG edge emission
        logger.debug(
            "applies_guardrail: eval_guard check operation=%s verdict=%s",
            operation,
            verdict,
        )

        if violations and self._mode == "enforce":
            raise EvalExecutionDeniedError(
                f"Eval guard blocked {operation}: {violations}",
            )

        return {
            "verdict": verdict,
            "violations": violations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_execution_log(self) -> list[dict[str, Any]]:
        """Return the audit log of all checks."""
        return list(self._log)

    def clear_log(self) -> None:
        """Clear the audit log."""
        self._log.clear()

    @property
    def mode(self) -> str:
        return self._mode

    # ------------------------------------------------------------------
    @staticmethod
    def _scan(code: str) -> list[str]:
        """Return list of violation descriptions found in *code*."""
        if not code:
            return []
        found: list[str] = []
        for pat in _DANGEROUS_PATTERNS:
            if pat.search(code):
                found.append(pat.pattern)
        return found


def get_eval_guard() -> type[EvalGuard]:
    """Get the EvalGuard class."""
    return EvalGuard


__all__ = [
    "EvalExecutionDeniedError",
    "EvalGuard",
    "EvalGuardViolation",
    "get_eval_guard",
]
