# hops/hop_6_gate.py
"""
Hop 6: Gate Decision - HIGH-SIGNAL OVERWRITE

This is a risk-aware, dynamic decision engine.
1. It differentiates between deterministic (e.g., placeholder) and
   quality-based (e.g., thematic alignment) failures.
2. It reads the HOP-0 RAG signal quality (via HOP-5 results) to
   dynamically adjust its risk tolerance.
3. It outputs a "PROCEED_WITH_REVIEW" state for low-confidence runs.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ValidationResult, ValidationSeverity, GateDecision
)

# --- High-Signal Configuration ---

# Rules that, if failed, represent a non-negotiable HALT,
# regardless of any other scores.
DETERMINISTIC_HALT_RULES = {
    "PLACEHOLDER_DETECTED",
    "ENGINE_FAILURE" # Catches failures in the validation engine itself
}

# Default risk thresholds
DEFAULT_THRESHOLDS = {
    "risk_score_threshold": 15,
    "low_signal_threshold": 0.60,
    "low_signal_risk_adjustment": 10 # Add 10 to threshold (be more tolerant)
}

# Risk weights for quality-based failures
RISK_WEIGHTS = {
    ValidationSeverity.CRITICAL: 1000, # For any non-deterministic criticals
    ValidationSeverity.HIGH: 10,
    ValidationSeverity.MEDIUM: 3,
    ValidationSeverity.LOW: 1
}

# --- End Configuration ---

class RiskAwareGate:
    """Evaluates validation results using a dynamic, risk-based model."""
    
    def __init__(self, validation_results: List[ValidationResult], config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.validation_results = validation_results
        
        # Load configurable thresholds
        thresholds_config = config.get("validation_thresholds", DEFAULT_THRESHOLDS)
        self.base_risk_threshold = thresholds_config.get("risk_score_threshold", 15)
        self.low_signal_threshold = thresholds_config.get("low_signal_threshold", 0.60)
        self.low_signal_adjustment = thresholds_config.get("low_signal_risk_adjustment", 10)
        
        # Internal state
        self.input_rag_signal = 1.0 # Default to high signal
        self.deterministic_halt_found = False
        self.deterministic_reason = ""
        self.total_risk_score = 0
        self.failures_by_severity: Dict[ValidationSeverity, List] = {
            s: [] for s in ValidationSeverity
        }

    def _analyze_results(self):
        """First pass: categorize failures and find input signal quality."""
        self.logger.info("Analyzing validation results...")
        
        for vr in self.validation_results:
            # Check for input signal quality (which isn't a failure)
            if vr.rule_id == "INPUT_SIGNAL_QUALITY":
                self.input_rag_signal = vr.details.get("signal_quality", 1.0)
                self.logger.info(f"Detected HOP-0 RAG Signal Quality: {self.input_rag_signal:.2f}")
                continue

            if not vr.passed:
                # Store for summary
                self.failures_by_severity[vr.severity].append(vr)
                
                # Check for deterministic halts
                if any(rule_name in vr.rule_id for rule_name in DETERMINISTIC_HALT_RULES):
                    self.deterministic_halt_found = True
                    self.deterministic_reason = f"Deterministic HALT on rule: {vr.rule_id} ({vr.message})"
                    self.logger.critical(self.deterministic_reason)
                
                # Add to risk score
                self.total_risk_score += RISK_WEIGHTS.get(vr.severity, 0)

    def evaluate_decision(self) -> Tuple[GateDecision, Dict[str, Any]]:
        """
        Runs the full evaluation logic.
        Returns the final decision and a metadata dictionary.
        """
        # 1. Analyze all results
        self._analyze_results()
        
        # 2. Check for deterministic halts (e.g., placeholders)
        if self.deterministic_halt_found:
            decision = GateDecision.HALT
            metadata = self._build_metadata(decision, self.deterministic_reason)
            return decision, metadata

        # 3. Adjust risk threshold based on input RAG signal
        adjusted_risk_threshold = self.base_risk_threshold
        adjustment_reason = "Base threshold."
        
        if self.input_rag_signal < self.low_signal_threshold:
            adjusted_risk_threshold += self.low_signal_adjustment
            adjustment_reason = (f"Input RAG signal ({self.input_rag_signal:.2f}) "
                                 f"is below threshold ({self.low_signal_threshold}). "
                                 f"Risk tolerance increased to {adjusted_risk_threshold}.")
            self.logger.warning(adjustment_reason)

        # 4. Make quality-based decision
        if self.total_risk_score > adjusted_risk_threshold:
            decision = GateDecision.HALT
            reason = (f"Quality HALT: Risk score {self.total_risk_score} "
                      f"exceeds adjusted threshold {adjusted_risk_threshold}.")
            self.logger.warning(reason)
            metadata = self._build_metadata(decision, reason)
            return decision, metadata

        # 5. Check for low-signal "Proceed with Review"
        if self.input_rag_signal < self.low_signal_threshold:
            decision = GateDecision.PROCEED_WITH_REVIEW
            reason = (f"Proceeding, but manual review recommended due to "
                      f"low input RAG signal ({self.input_rag_signal:.2f}).")
            self.logger.warning(reason)
            metadata = self._build_metadata(decision, reason)
            return decision, metadata

        # 6. If all checks pass, proceed
        decision = GateDecision.PROCEED
        reason = "All validation checks passed within risk tolerance."
        self.logger.info(reason)
        metadata = self._build_metadata(decision, reason)
        return decision, metadata

    def _build_metadata(self, decision: GateDecision, reason: str) -> Dict[str, Any]:
        """Helper to assemble the final output metadata block."""
        return {
            "decision": decision.value,
            "reason": reason,
            "input_rag_signal": self.input_rag_signal,
            "total_risk_score": self.total_risk_score,
            "base_risk_threshold": self.base_risk_threshold,
            "adjusted_risk_threshold": (
                self.base_risk_threshold + self.low_signal_adjustment 
                if self.input_rag_signal < self.low_signal_threshold else self.base_risk_threshold
            ),
            "summary": {
                "total_validations": len(self.validation_results),
                "failed_validations": sum(len(v) for v in self.failures_by_severity.values()),
                "critical_failures": len(self.failures_by_severity[ValidationSeverity.CRITICAL]),
                "high_failures": len(self.failures_by_severity[ValidationSeverity.HIGH]),
                "medium_failures": len(self.failures_by_severity[ValidationSeverity.MEDIUM]),
            }
        }

def run_hop_6(args: argparse.Namespace):
    """Executes the HOP-6 gate decision logic."""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-6: Risk-Aware Gate Decision [v-HighSignal] ---")
    start_time = datetime.now()

    try:
        # Load validation results
        try:
            with open(args.input_path_validation_results, 'r', encoding='utf-8') as f:
                validation_data = json.load(f)
            validation_results = [
                ValidationResult.from_dict(vr_dict) 
                for vr_dict in validation_data.get("validation_results", [])
            ]
            logger.info(f"Loaded {len(validation_results)} validation results from {args.input_path_validation_results}")
            
        except Exception as e:
            raise HopExecutionError(f"Failed to load validation results: {e}") from e

        # Load config (mocked for this example)
        # In prod, this would load from args.config_path
        config = {} 
        logger.info("Loaded mock config. Using default thresholds.")
        
        # Instantiate and run the gate
        gate = RiskAwareGate(validation_results, config)
        decision, metadata = gate.evaluate_decision()
        
        logger.info(f"Gate decision: {decision.value}")

        # Prepare output
        output_data = {
            "gate_decision": decision.value,
            "decision_metadata": metadata
        }

        # Write output
        try:
            output_path = Path(args.output_path_gate_decision)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote gate decision to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output JSON: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-6 Finished Successfully ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        
        # Exit with non-zero if HALT to signal orchestrator
        if decision == GateDecision.HALT:
            logger.warning(f"Exiting with code 1 due to HALT decision: {metadata['reason']}")
            exit(1)

    except HopExecutionError as he:
        logger.error(f"HOP-6 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-6 Finished with HALT ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)
    except Exception as e:
        logger.error(f"HOP-6 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-6 Finished with FAILURE ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-6: Risk-Aware Gate Decision [v-HighSignal]")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--input-path-validation-results", required=True, help="Path to the validation results JSON")
    parser.add_argument("--output-path-gate-decision", required=True, help="Path to write the gate decision JSON")

    args = parser.parse_args()
    run_hop_6(args)