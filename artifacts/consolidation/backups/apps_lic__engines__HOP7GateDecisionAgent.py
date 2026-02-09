"""
HOP-7: Gate Decision Agent (LIC Sovereign Architecture).

Acts as the 'Governor' by evaluating validation reports and
directing the workflow (Pass, Retry Research, or Retry Generation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry
from apps_lic.utils.hop_stage_capability import HOPStageCapability
from apps_lic.utils.LICAgentBase import LICAgentBase


@dataclass
class HOP7GateDecisionAgent(HOPStageCapability, SubatomicTestingMixin, LICAgentBase):
    """
    V2.5 Governor Agent.

    Classifies rule violations to trigger S6->S2 or S6->S5 loops.
    - Read hop6_validation_report from ImmutableStagingBuffer.
    - Classify failures based on GateConfig.
    - Write a decision record (PASS/FAIL_FACTUAL/FAIL_CREATIVE).
    """

    # HOPStageCapability configuration
    HOP_STAGE_NAME: ClassVar[str] = "hop7_gate_decision"
    REQUIRED_INPUTS: ClassVar[list[str]] = [
        "hop6_validation_report",
    ]

    # Sovereign Configuration
    gate_thresholds: dict[str, Any] = field(
        default_factory=lambda: {"max_factual_failures": 2, "max_creative_failures": 3},
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute specialist validation logic.

        1. Read Inputs with Sovereign Defensiveness.
        2. Specialist Classification Logic (LIC v13.0 / K.7 Validator).
        3. Calculate Report and Failure Classification.
        4. Map Failures for Orchestrator Back-Hop Routing.
        """
        # 1. Read Inputs via capability
        inputs = self.read_required_inputs(buffer, registry)
        report = inputs["hop6_validation_report"]
        config = self.config.gate_decision_agent

        registry.add_trace("PHASE_STEP", {"action": "evaluating_gate", "passed": report["passed"]})

        # Defensive Stagnation Check
        traces = registry.get_traces()
        factual_retry_count = sum(1 for t in traces if t.get("type") == "FACTUAL_LOOP_TRIGGERED")
        if factual_retry_count >= 2:
            registry.add_trace("STAGNATION_DETECTED", {"count": factual_retry_count})

        # 2. Specialist Classification Logic (LIC v13.0 / K.7 Validator)
        decision = "PASS"
        action = "PROCEED"
        reason = "All quality gates satisfied"

        if not report["passed"]:
            # Extract rules that failed
            failures = [r for r in report["validation_results"] if not r["passed"]]
            # Prioritize FACTUAL failures (S6->S2) over CREATIVE (S6->S5)
            factual_violations = [f for f in failures if f["rule_id"] in config.factual_failure_rules]

            if factual_violations:
                decision = "FAIL_FACTUAL"
                action = "RETRY_HOP2"  # Back-hop to Research
                reason = f"Factual gap detected: {factual_violations[0]['rule_id']}"
                registry.add_trace("FACTUAL_LOOP_TRIGGERED", {"rule": factual_violations[0]["rule_id"]})
            else:
                decision = "FAIL_CREATIVE"
                action = "RETRY_HOP5"  # Back-hop to Generation
                reason = f"Creative flaw detected: {failures[0]['rule_id']}"
                registry.add_trace("CREATIVE_LOOP_TRIGGERED", {"rule": failures[0]["rule_id"]})

        # 3. Write Decision via capability
        self.write_output(
            buffer,
            registry,
            {"decision": decision, "action": action, "reason": reason},
            decision_meta={"status": decision, "action": action},
        )
