"""CONSOLIDATED: MessageComplianceAgent → LICValidationExecutor (2026-03-11).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code:
    LICValidationExecutor(rule_set="message_compliance")
"""
from apps_lic.reasoning.LICValidationExecutor import LICValidationExecutor as MessageComplianceAgent
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
__all__ = ['MessageComplianceAgent']
