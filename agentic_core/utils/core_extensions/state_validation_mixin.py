import logging
import inspect
import hashlib
import json
from functools import wraps
from typing import Callable, Any, Optional, Dict, List

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
        self._operation_ledger: Dict[str, Any] = {}

    def _generate_op_hash(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generates a unique deterministic hash for an operation call."""
        # Convert args/kwargs to sorted JSON string for consistency
        try:
            payload = {
                "func": func_name,
                "args": [str(a) for a in args], # Simplification for non-serializable objects
                "kwargs": {k: str(v) for k, v in kwargs.items()}
            }
            s = json.dumps(payload, sort_keys=True)
            return hashlib.sha256(s.encode()).hexdigest()
        except Exception as e:
            self._sv_logger.warning(f"Could not generate idempotency hash: {e}")
            return None

    @staticmethod
    def validate_state(pre: Optional[Callable[[Any], bool]] = None, 
                       post: Optional[Callable[[Any, Any], bool]] = None,
                       idempotent: bool = False):
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
                        for condition in pre_conditions:
                            if not condition(self):
                                raise StateValidationError(f"Pre-condition failed for {func.__name__}")
                    except Exception as e:
                        raise StateValidationError(f"Pre-condition error in {func.__name__}: {e}")

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

                # 5. Cache Result (if idempotent)
                if idempotent and op_hash:
                    self._operation_ledger[op_hash] = result

                return result
            return wrapper
        return decorator
