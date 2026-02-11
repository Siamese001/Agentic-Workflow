"""
StateValidationMixin — Canonical location.

Relocated from agentic_core/L4_state/types/state_validation_types.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any


class StateValidationError(Exception):
    """Raised when a pre-condition or post-condition fails."""

    pass


class StateValidationMixin:
    """
    Phase 1 Critical Infrastructure: State Validation (Report 4.2).

    Ensures data consistency through:
    - Pre-condition checks (guard clauses)
    - Post-condition verification (invariants)
    - Idempotency guarantees via input hashing
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sv_logger = logging.getLogger(self.__class__.__name__)
        # Simple in-memory ledger for idempotency (could be backed by Redis in future)
        self._operation_ledger: dict[str, Any] = {}

    def _run_conditions(self, conditions: list[Callable[..., bool]], result: Any = None) -> None:
        for condition in conditions:
            sig = inspect.signature(condition)
            if len(sig.parameters) == 1:
                ok = condition(self)
            else:
                ok = condition(self, result)
            if not ok:
                raise StateValidationError(f"Condition failed: {getattr(condition, '__name__', 'condition')}")

    def _generate_op_hash(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generates a unique deterministic hash for an operation call."""
        if len(str(args)) + len(str(kwargs)) > 100_000:
            return None
        # Convert args/kwargs to sorted JSON string for consistency
        try:
            payload = {
                "func": func_name,
                "args": [str(a) for a in args],  # Simplification for non-serializable objects
                "kwargs": {k: str(v) for k, v in kwargs.items()},
            }
            s = json.dumps(payload, sort_keys=True)
            return hashlib.sha256(s.encode()).hexdigest()
        except Exception as e:
            self._sv_logger.warning(f"Could not generate idempotency hash: {e}")
            return None

    @staticmethod
    def validate_state(
        pre: Callable[[Any], bool] | None = None,
        post: Callable[[Any, Any], bool] | None = None,
        idempotent: bool = False,
    ):
        """
        Decorator to enforce state validity.

        Args:
            pre: Callable(self) -> bool. Runs BEFORE method. Raises if False.
            post: Callable(self, result) -> bool. Runs AFTER method. Raises if False.
            idempotent: If True, returns cached result for identical inputs.
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                if not isinstance(self, StateValidationMixin):
                    return await func(self, *args, **kwargs)

                # 1. Idempotency Check
                op_hash = None
                if idempotent:
                    op_hash = self._generate_op_hash(func.__name__, args, kwargs)
                    if op_hash and op_hash in self._operation_ledger:
                        self._sv_logger.info(f"Idempotent hit for {func.__name__} ({op_hash[:8]})")
                        return self._operation_ledger[op_hash]

                # 2. Pre-condition Check
                if pre:
                    try:
                        # Handle single function or list of functions
                        pre_conditions = pre if isinstance(pre, list) else [pre]
                        # guardian: allow-magic-config
                        await asyncio.wait_for(
                            asyncio.to_thread(lambda: self._run_conditions(pre_conditions, None)),
                            timeout=3.5,
                        )
                    except asyncio.TimeoutError:
                        raise StateValidationError(f"Pre-condition check timeout for {func.__name__}")
                    except Exception as e:
                        raise StateValidationError(f"Pre-condition failed: {e}")

                # 3. Execution
                result = await func(self, *args, **kwargs)

                # 4. Post-condition Check
                if post:
                    try:
                        # Handle single function or list of functions
                        post_conditions = post if isinstance(post, list) else [post]
                        for condition in post_conditions:
                            if not condition(self, result):
                                raise StateValidationError(f"Post-condition failed for {func.__name__}")
                    except Exception as e:
                        raise StateValidationError(f"Post-condition error in {func.__name__}: {e}")

                # 5. cache Result (if idempotent)
                if idempotent and op_hash:
                    self._operation_ledger[op_hash] = result

                if hasattr(self, "emit_event"):
                    self.emit_event(
                        "state_validation.success" if result is not None else "state_validation.failed",
                        {"method": func.__name__},
                        severity="INFO" if result is not None else "WARNING",
                    )

                return result

            return wrapper

        return decorator
