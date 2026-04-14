"""apps_rfp — AI Proposal / RFP Generator."""

from importlib import import_module
from types import ModuleType

__all__ = ["outputs", "reasoning", "services", "types", "integrations"]


def __getattr__(name: str) -> ModuleType:
    if name in __all__:
        module = import_module(f"apps_rfp.{name}")
        globals()[name] = module
        return module
    raise AttributeError(name)
