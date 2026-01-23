"""
HOP-7: Gate Decision Agent (V2 Architecture).

Acts as the 'Governor' by evaluating validation reports and 
directing the workflow (Pass, Retry Research, or Retry Generation).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from apps_lic.shared.v2_patterns.agent_base import V2AgentBase
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry

class HOP7GateDecisionAgent(V2AgentBase):
    """
    V2 Implementation of HOP-7.
    
    Responsibilities:
    - Read hop6_validation_report from ImmutableStagingBuffer.
    - Classify failures based on GateConfig.
    - Write a decision record (PASS/FAIL_FACTUAL/FAIL_CREATIVE).
    """

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute gate decision logic.
        
        1. Read validation report from HOP-6.
        2. Classify failures as factual or creative.
        3. Determine workflow action (PROCEED, RETRY_HOP2, RETRY_HOP5).
        4. Write immutable decision record.
        """
        # 1. Read Input
        report = buffer.read("hop6_validation_report")
        if not report:
            registry.add_trace("DATA_ERROR", {"msg": "Missing 'hop6_validation_report'"})
            raise ValueError("HOP-7 requires input from HOP-6")

        registry.add_trace("PHASE_STEP", {"action": "evaluating_gate", "passed": report["passed"]})

        # 2. Decision Logic
        decision = "PASS"
        action = "PROCEED"
        reason = "All validation checks passed."
        failure_type = None

        if not report["passed"]:
            # Prioritize Critical/High failures for classification
            failures = [
                r for r in report["validation_results"] 
                if not r["passed"] and r["severity"] in ("CRITICAL", "HIGH")
            ]
            
            if not failures:
                # Edge case: passed=False but no critical failures? Halt for safety.
                decision = "FAIL_UNKNOWN"
                action = "HALT"
                reason = "Validation failed but no critical/high issues found."
            else:
                primary_fail = failures[0]
                rule_id = primary_fail["rule_id"]
                config = self.config.gate_decision_agent
                
                # Failure Classification
                if rule_id in config.factual_failure_rules:
                    decision = "FAIL_FACTUAL"
                    action = "RETRY_HOP2"
                    failure_type = "FACTUAL"
                    reason = f"Factual failure detected: {rule_id}"
                else:
                    decision = "FAIL_CREATIVE"
                    action = "RETRY_HOP5"
                    failure_type = "CREATIVE"
                    reason = f"Creative/Compliance failure detected: {rule_id}"

        # 3. Write Output (Immutable)
        output_data = {
            "decision": decision,
            "action": action,
            "reason": reason,
            "failure_type": failure_type,
            "agent_version": "2.0.0"
        }
        
        buffer.write_once("hop7_gate_decision", output_data)
        
        registry.add_trace("DECISION_FINAL", {
            "decision": decision,
            "action": action,
            "reason": reason
        })
