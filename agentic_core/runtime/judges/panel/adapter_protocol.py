"""Judge provider adapter protocol (transport-only implementations)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from agentic_core.runtime.judges.panel.canonical_contract import CanonicalJudgeContract
from agentic_core.runtime.judges.panel.panel_types import PanelJudgeOutcome, TransportReceipt


@dataclass(frozen=True)
class DeclaredTransportPolicy:
    """Declared transport knobs — audited against TransportReceipt."""

    max_output_tokens: int
    json_output_lock: str
    temperature: float | None = None
    system_includes_score_schema: bool = True


class JudgeProviderAdapter(Protocol):
    """App-registered adapter for one panel provider key."""

    provider_key: str

    def declared_policy(self, *, attempt: int = 1) -> DeclaredTransportPolicy:
        """Declared transport policy for parity preflight."""

    def invoke(
        self,
        contract: CanonicalJudgeContract,
        *,
        attempt: int = 1,
    ) -> tuple[PanelJudgeOutcome, TransportReceipt]:
        """Grade contract; return normalized outcome + observed transport receipt."""


class AdapterInvokeError(Exception):
    """Transport or parse failure — not content-quality FAIL."""


__all__ = [
    "AdapterInvokeError",
    "DeclaredTransportPolicy",
    "JudgeProviderAdapter",
]
