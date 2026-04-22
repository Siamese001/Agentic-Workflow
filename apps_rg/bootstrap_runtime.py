from __future__ import annotations

import importlib
import inspect
import sys
import types
from typing import Any


def _ensure_module(name: str) -> types.ModuleType:
    """Return the module for ``name``, preferring the real package on disk.

    If the real package/module is importable, return it (keeps the
    ``__path__`` and sub-package machinery intact). Only fall back to a bare
    ``types.ModuleType`` stub when the real module does not exist at all —
    this preserves the shim behavior for genuinely-missing test helpers
    while not clobbering real packages.

    Previously this function unconditionally created bare modules for every
    parent of the requested dotted path. That replaced real packages like
    ``agentic_core`` with ``types.ModuleType`` objects having no
    ``__path__``, breaking every subsequent ``from agentic_core.X import Y``
    call with ``"agentic_core is not a package"``.
    """
    if name in sys.modules:
        return sys.modules[name]

    # Prefer the real module on disk so packages keep __path__ / submodule
    # resolution. ImportError signals a genuinely-absent module — in that
    # case we synthesize a stub for shim attachment.
    try:
        return importlib.import_module(name)
    except ImportError:  # guardian: allow-silent-swallow -- ImportError is the expected sentinel: module absent on disk, fall through to types.ModuleType stub synthesis below
        pass

    module = types.ModuleType(name)
    sys.modules[name] = module
    if "." in name:
        parent_name, child_name = name.rsplit(".", 1)
        parent = _ensure_module(parent_name)
        setattr(parent, child_name, module)
    return module


def _install_pydantic_compat() -> None:
    try:
        import pydantic
        from pydantic import BaseModel
    except Exception:  # guardian: allow-broad-exception -- pydantic may be absent entirely; bootstrap must not crash on missing optional dependency
        return

    if not hasattr(BaseModel, "model_dump"):
        BaseModel.model_dump = BaseModel.dict  # type: ignore[attr-defined]
    if not hasattr(BaseModel, "model_copy"):
        BaseModel.model_copy = BaseModel.copy  # type: ignore[attr-defined]
    if not hasattr(BaseModel, "model_dump_json"):
        BaseModel.model_dump_json = BaseModel.json  # type: ignore[attr-defined]

    if not hasattr(pydantic, "field_validator"):
        from pydantic import validator

        def field_validator(*fields: str, **kwargs: Any):
            kwargs.pop("mode", None)
            return validator(*fields, **kwargs)

        pydantic.field_validator = field_validator  # type: ignore[attr-defined]

    if not hasattr(pydantic, "model_validator"):
        from pydantic import root_validator

        def model_validator(*, mode: str = "after"):
            def decorator(fn):
                if mode == "before":
                    return root_validator(pre=True, allow_reuse=True)(fn)

                @root_validator(pre=False, skip_on_failure=True, allow_reuse=True)
                def _wrapped(cls, values):
                    instance = cls.construct(**values)
                    result = fn(instance)
                    return result.dict() if hasattr(result, "dict") else values

                return _wrapped

            return decorator

        pydantic.model_validator = model_validator  # type: ignore[attr-defined]


def _noop(*args: Any, **kwargs: Any) -> None:
    return None


class _LayerSegment:
    L0_ROUTING = "L0_ROUTING"
    L1_REASONING = "L1_REASONING"
    L2_EXECUTION = "L2_EXECUTION"
    L3_ORCHESTRATION = "L3_ORCHESTRATION"
    L4_STATE = "L4_STATE"
    L5_POLICY = "L5_POLICY"
    L6_OBSERVABILITY = "L6_OBSERVABILITY"


def _install_agentic_core_shims() -> None:
    lifecycle = _ensure_module("agentic_core.runtime.contracts.lifecycle_trace_contract")
    lifecycle.LayerSegment = _LayerSegment
    lifecycle.emit_determinism_digest = _noop
    lifecycle.emit_replay_key = _noop

    def __getattr__(name: str):
        if name == "LayerSegment":
            return _LayerSegment
        return _noop

    lifecycle.__getattr__ = __getattr__  # type: ignore[attr-defined]

    timeout_mod = _ensure_module("agentic_core.base_agents.timeout_decorator")
    timeout_util_mod = _ensure_module("agentic_core.utils.timeout_decorator_util")

    def timeout(*dargs: Any, **dkwargs: Any):
        if dargs and callable(dargs[0]) and not dkwargs:
            return dargs[0]

        def decorator(fn):
            if inspect.iscoroutinefunction(fn):

                async def _async_wrapped(*args: Any, **kwargs: Any):
                    return await fn(*args, **kwargs)

                return _async_wrapped

            def _wrapped(*args: Any, **kwargs: Any):
                return fn(*args, **kwargs)

            return _wrapped

        return decorator

    timeout_mod.timeout = timeout
    timeout_util_mod.timeout = timeout

    contracts = _ensure_module("agentic_core.interfaces.execution_contracts")

    class AgentOutputContract(dict):
        pass

    contracts.AgentOutputContract = AgentOutputContract
    contracts.get_current_secret = lambda *args, **kwargs: None
    contracts.wrap_output = lambda output, *args, **kwargs: output

    routing_mod = _ensure_module("agentic_core.L4_state.config.vllm_routing_predicates")

    class ProviderValue:
        def __init__(self, value: str) -> None:
            self.value = value

    class Provider:
        LOCAL_VLLM = ProviderValue("LOCAL_VLLM")
        OPUS = ProviderValue("OPUS")

    class RoutingDecision:
        def __init__(self, provider: ProviderValue, predicate_evaluation_hash: str = "shim") -> None:
            self.provider = provider
            self.predicate_evaluation_hash = predicate_evaluation_hash

    routing_mod.Provider = Provider
    routing_mod.evaluate = lambda _ctx: RoutingDecision(Provider.OPUS)


def install_runtime_shims() -> None:
    _install_pydantic_compat()
    _install_agentic_core_shims()
