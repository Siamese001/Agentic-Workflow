"""PTC Tool Contracts — Contract [3] ToolCall and ToolResult types.

Spec: Contract [3] PTC Tool Contracts, L2 [STDOUT RULE], Guarantee #24.

Every tool invocation through the L2 sandbox MUST produce a ToolResult with:
  - exit_code: int in {0, 1} only
  - stdout: bytes with len(stdout) <= budget cap

ToolResult.__post_init__ validates both constraints at construction time.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class ToolContractViolation(ValueError):
    """Raised when a ToolResult violates exit_code or stdout_bytes contract."""

@dataclass(frozen=True)
class ToolCall:
    """Represents a single tool invocation request.

    Spec: Contract [3] PTC ToolCall.
    """
    id: str
    tool_name: str
    args: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ToolContractViolation('ToolCall.id must be non-empty')
        if not self.tool_name:
            raise ToolContractViolation('ToolCall.tool_name must be non-empty')

@dataclass(frozen=True)
class ToolResult:
    """Immutable result of a single tool invocation.

    Spec: Contract [3] PTC ToolResult — stdout-only, exit_code in {0, 1}.

    Constraints enforced at construction:
      - exit_code MUST be 0 or 1 (no other values permitted)
      - len(stdout) MUST be <= stdout_bytes_cap when cap is provided
    """
    exit_code: int
    stdout: bytes
    stdout_bytes_cap: int = 0

    def __post_init__(self) -> None:
        if self.exit_code not in (0, 1):
            raise ToolContractViolation(f'ToolResult.exit_code must be 0 or 1, got {self.exit_code}. Spec: Contract [3] L2 [STDOUT RULE].')
        if self.stdout_bytes_cap > 0 and len(self.stdout) > self.stdout_bytes_cap:
            raise ToolContractViolation(f'ToolResult.stdout exceeds cap: len={len(self.stdout)}, cap={self.stdout_bytes_cap}. Spec: Contract [3] Guarantee #24.')

    @classmethod
    def from_budget_enforcer(cls, exit_code: int, stdout_bytes: bytes, stdout_bytes_cap: int) -> 'ToolResult':
        """Construct and validate ToolResult from BudgetEnforcer output.

        Raises ToolContractViolation if exit_code or stdout length violates contract.
        """
        return cls(exit_code=exit_code, stdout=stdout_bytes, stdout_bytes_cap=stdout_bytes_cap)
