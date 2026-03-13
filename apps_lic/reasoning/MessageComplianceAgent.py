"""CONSOLIDATED: MessageComplianceAgent → LICValidationExecutor (2026-03-11).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code:
    LICValidationExecutor(rule_set="message_compliance")
"""

from apps_lic.reasoning.LICValidationExecutor import LICValidationExecutor as MessageComplianceAgent

__all__ = ["MessageComplianceAgent"]
