import pytest

from src.lic_agentic.core import LICCoreContext
from src.lic_agentic.reasoning.toggles import ReasoningToggles
from src.lic_agentic.stacks.outreach_stack import OutreachStack


@pytest.fixture()
def lic_context() -> LICCoreContext:
    """Return a bootstrapped LIC context for an individual test."""

    return LICCoreContext.bootstrap()


@pytest.fixture()
def outreach_stack(lic_context: LICCoreContext) -> OutreachStack:
    """Create a fresh OutreachStack wired to the shared context."""

    return OutreachStack(ReasoningToggles(), context=lic_context)
