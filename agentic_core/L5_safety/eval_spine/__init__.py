"""L5 Eval Spine — v33 §5 EXIT EVAL & CONTROL primitives.

This subpackage implements the code listed as Open Items in ADR-036 … ADR-042
(see `.windsurf/plans/exit-eval-spine-code-fb2c19.md`).

Modules:
- tool_call_canonicalizer: ADR-037 §2.3 canonical tool-call shape.
- trajectory_metrics: ADR-037 §2.2 six Vertex trajectory metrics.
- budget_envelope: ADR-038 per-request budget envelope.
- claim_extractor: ADR-041 code-based claim extractor.
- output_contract_validator: ADR-039 output-contract validator.
- exit_decision: ExitDecision dataclass + schema validation.
- escalation_packet: EscalationPacket dataclass + factory.
- trace_grader: ADR-036 runtime trace-grader framework.
- kill_switch: ADR-042 exit kill-switch primitive.
- exit_eval: top-level orchestrator for §5.

All modules are read-only with respect to runtime state. Side-effect-free
imports. No agent or MCP coupling.
"""

from __future__ import annotations

__all__: list[str] = []
