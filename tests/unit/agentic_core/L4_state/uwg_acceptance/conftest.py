"""L4 test fixtures."""

from __future__ import annotations

from typing import Generator

import pytest

from agentic_core.L4_state.audit.audit_ledger import (
    AuditLedger,
    reset_default_ledger,
)
from agentic_core.L4_state.otel.spans import reset_emitted_spans


@pytest.fixture(autouse=True)
def _reset_observability() -> Generator[None, None, None]:
    """Each test starts with a fresh span recorder + ledger."""
    reset_emitted_spans()
    reset_default_ledger()
    yield
    reset_emitted_spans()
    reset_default_ledger()


@pytest.fixture
def fresh_ledger() -> AuditLedger:
    """A fresh ledger isolated from the default one."""
    return AuditLedger()
