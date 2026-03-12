import contextvars
import logging
import uuid
import weakref
from functools import wraps
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
trace_id_var = contextvars.ContextVar('trace_id', default=None)
span_id_var = contextvars.ContextVar('span_id', default=None)

class ContextPropagationMixin:
    """
    Phase 3 Advanced Infrastructure: Context Propagation (Report 4.7).

    Enables distributed tracing by propagating request context across async calls.
    Features:
    - Thread/Async-safe ContextVars
    - Automatic Trace/Span ID generation
    - Integration with event_emission_mixin
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cp_logger = logging.getLogger(self.__class__.__name__)

    def set_context(self, trace_id: str, span_id: str | None=None):
        """Manually sets the tracing context for the current execution flow."""
        trace_id_var.set(trace_id)
        if span_id:
            span_id_var.set(span_id)
        self._cp_logger.debug(f'Context set: trace_id={trace_id}')

    def get_context(self) -> dict[str, str | None]:
        """Retrieves the current trace and span IDs."""
        return {'trace_id': trace_id_var.get(), 'span_id': span_id_var.get()}

    @staticmethod
    def _validate_context():
        if trace_id_var.get() is None:
            raise RuntimeError('Missing trace context in critical path')

    @staticmethod
    def trace_context(func):
        """Decorator to ensure trace context is captured and logged."""

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not trace_id_var.get():
                trace_id_var.set(str(uuid.uuid4()))
            old_span = span_id_var.get()
            new_span = str(uuid.uuid4())[:8]
            span_id_var.set(new_span)
            if weakref.getweakrefcount(self) > 10:
                self._cp_logger.warning('Potential context leak detected')
            if func.__name__.startswith('_critical'):
                ContextPropagationMixin._validate_context()
            self._cp_logger.debug(f'Entering {func.__name__} [Trace: {trace_id_var.get()}, Span: {new_span}]')
            try:
                result = await func(self, *args, **kwargs)
                return result
            finally:
                span_id_var.set(old_span)
        return wrapper
