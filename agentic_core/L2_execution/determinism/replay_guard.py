"""C1.4: Replay Guard - Wrap tool/model invocations.

10C-REQ-120: Wrap every tool model invocation prevent leaks of non-deterministic data
intercept no wall clock no raw random no uuid4 no live network no mixed-state reads
"""

from __future__ import annotations

import functools
import hashlib
import time
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from .determinism_surface import DeterminismSurface


T = TypeVar('T')


@dataclass
class InvocationRecord:
    """Record of a guarded invocation."""
    function_name: str
    args_hash: str
    kwargs_hash: str
    timestamp: float
    result_hash: str
    was_intercepted: bool


class ReplayGuard:
    """Replay guard for tool/model invocations.
    
    10C-REQ-120: Wrap every tool/model invocation prevent non-deterministic
    data leaks intercept wall clock raw random uuid4 live network mixed-state reads.
    """
    
    INTERCEPTED_FUNCTIONS = {
        'time.time', 'time.monotonic', 'datetime.now', 'datetime.utcnow',
        'random.random', 'random.randint', 'random.choice', 'uuid.uuid4',
        'uuid.uuid1', 'os.urandom', 'secrets.token_bytes',
    }
    
    def __init__(self, surface: DeterminismSurface | None = None) -> None:
        self.surface = surface or DeterminismSurface()
        self.records: list[InvocationRecord] = []
        self.intercepted_count: int = 0
    
    def wrap(self, func: Callable[..., T]) -> Callable[..., T]:
        """Wrap a function with replay guard."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Check if this is a non-deterministic function
            func_name = f"{func.__module__}.{func.__name__}"
            
            if self._should_intercept(func_name):
                self.intercepted_count += 1
                # Return deterministic replacement
                return self._provide_deterministic_alternative(func_name, args, kwargs)  # type: ignore
            
            # Execute normally but record
            result = func(*args, **kwargs)
            self._record_invocation(func_name, args, kwargs, result)
            return result
        
        return wrapper
    
    def _should_intercept(self, func_name: str) -> bool:
        """Check if function should be intercepted."""
        # Check full module path
        if func_name in self.INTERCEPTED_FUNCTIONS:
            return True
        
        # Check just function name
        simple_name = func_name.split('.')[-1]
        for pattern in self.INTERCEPTED_FUNCTIONS:
            if pattern.endswith(simple_name):
                return True
        
        return False
    
    def _provide_deterministic_alternative(
        self, func_name: str, args: Any, kwargs: Any
    ) -> Any:
        """Provide deterministic alternative to intercepted function."""
        if 'time' in func_name:
            return self.surface.get_timestamp()
        elif 'random' in func_name:
            rand = self.surface.get_random()
            if 'random' in func_name:
                return rand.random()
            elif 'randint' in func_name:
                return rand.randint(args[0], args[1]) if len(args) >= 2 else 0
            elif 'choice' in func_name:
                return rand.choice(args[0]) if args else None
            return rand.random()
        elif 'uuid' in func_name:
            return self.surface.generate_id('id-')
        elif 'urandom' in func_name or 'token' in func_name:
            # Return deterministic bytes
            return b'\x00' * kwargs.get('nbytes', 32)
        
        return None
    
    def _record_invocation(
        self, func_name: str, args: Any, kwargs: Any, result: Any
    ) -> None:
        """Record an invocation for replay verification."""
        args_hash = hashlib.sha256(str(args).encode()).hexdigest()[:16]
        kwargs_hash = hashlib.sha256(str(kwargs).encode()).hexdigest()[:16]
        result_hash = hashlib.sha256(str(result).encode()).hexdigest()[:16]
        
        record = InvocationRecord(
            function_name=func_name,
            args_hash=args_hash,
            kwargs_hash=kwargs_hash,
            timestamp=time.time(),
            result_hash=result_hash,
            was_intercepted=False,
        )
        self.records.append(record)


class InvocationWrapper:
    """Wraps a callable with full replay guard instrumentation."""
    
    def __init__(self, func: Callable[..., T], guard: ReplayGuard) -> None:
        self.func = func
        self.guard = guard
        self.wrapped = guard.wrap(func)
    
    def __call__(self, *args: Any, **kwargs: Any) -> T:
        return self.wrapped(*args, **kwargs)
