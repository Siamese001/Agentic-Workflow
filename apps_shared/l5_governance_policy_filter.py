"""
L5 Governance Policy Filter
Implements security checks to block malicious instructions and adversarial patterns
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant

# Adversarial instruction patterns to block
ADVERSARIAL_PATTERNS = [
    r"#\s*NEW\s+INSTRUCTION:",
    r"//\s*NEW\s+INSTRUCTION:",
    r"#\s*OVERRIDE\s+POLICY:",
    r"//\s*OVERRIDE\s+POLICY:",
    r"#\s*IGNORE\s+ALL\s+RULES",
    r"//\s*IGNORE\s+ALL\s+RULES",
    r"#\s*TARGET_REPO:",  # Matches "# TARGET_REPO:" exactly
    r"//\s*TARGET_REPO:",
    r"#\s*TARGET\s+_REPO:",  # Alternative: "# TARGET _REPO:"
    r"//\s*TARGET\s+_REPO:",
    r"#\s*STEP\s+\d+:",
    r"//\s*STEP\s+\d+:",
    r"#\s*NEXT:",
    r"//\s*NEXT:",
    r"#\s*THEN:",
    r"//\s*THEN:",
    r"#\s*FOLLOWED\s+BY:",
    r"//\s*FOLLOWED\s+BY:",
]

# Comment-only threshold - if more than 80% of lines are comments/empty, block
COMMENT_ONLY_THRESHOLD = 0.8


class L5GovernancePolicyFilter:
    """L5 Governance Policy Filter for blocking malicious instructions"""

    def __init__(self):
        self.violations_log: List[Dict[str, Any]] = []

    def check_code(self, code_content: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Scans code for adversarial payloads or non-compliant content.

        Args:
            code_content: The code to check
            context: Optional context information

        Returns:
            The filtered, clean code string, or None if a violation is found (BLOCK)
        """
        if not isinstance(code_content, str):
            logger.error("L5 Policy: Code content must be a string")
            return None

        # 1. Adversarial Pattern Check
        for pattern in ADVERSARIAL_PATTERNS:
            if re.search(pattern, code_content, re.IGNORECASE | re.MULTILINE):
                violation = {
                    "type": "adversarial_pattern",
                    "pattern": pattern,
                    "severity": "CRITICAL",
                    "action": "BLOCK"
                }
                self.violations_log.append(violation)
                logger.critical(
                    f"L5 Policy Violation: Adversarial pattern detected - {pattern}")
                return None  # CRITICAL BLOCK

        # 2. Heuristic/Code Quality Check - too many comments
        lines = code_content.splitlines()
        total_lines = len(lines)

        if total_lines > 0:
            comment_lines = sum(1 for line in lines
                                if line.strip().startswith(('#', '//')) or not line.strip())
            comment_ratio = comment_lines / total_lines

            if total_lines > 5 and comment_ratio > COMMENT_ONLY_THRESHOLD:
                violation = {
                    "type": "suspicious_structure",
                    "comment_ratio": comment_ratio,
                    "severity": "HIGH",
                    "action": "BLOCK"
                }
                self.violations_log.append(violation)
                logger.warning(
                    f"L5 Policy Violation: Suspicious code structure - {comment_ratio:.2%} comments")
                return None  # BLOCK

        # 3. Check for potential credential leakage
        credential_patterns = [
            r"API_KEY\s*=\s*['\"][^'\"]+['\"]",
            r"PASSWORD\s*=\s*['\"][^'\"]+['\"]",
            r"SECRET\s*=\s*['\"][^'\"]+['\"]",
            r"TOKEN\s*=\s*['\"][^'\"]+['\"]",
        ]

        for pattern in credential_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                violation = {
                    "type": "credential_leakage",
                    "pattern": pattern,
                    "severity": "CRITICAL",
                    "action": "BLOCK"
                }
                self.violations_log.append(violation)
                logger.critical(
                    f"L5 Policy Violation: Potential credential leakage - {pattern}")
                return None  # CRITICAL BLOCK

        # If all checks pass, the code is considered safe
        logger.debug("L5 Policy: Code passed all security checks")
        return code_content

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get list of all violations detected"""
        return self.violations_log.copy()

    def clear_violations(self) -> None:
        """Clear the violations log"""
        self.violations_log.clear()


# Global instance for use across the application
_l5_filter = None


def get_l5_governance_filter() -> L5GovernancePolicyFilter:
    """Get the global L5 Governance Policy Filter instance"""
    global _l5_filter
    if _l5_filter is None:
        _l5_filter = L5GovernancePolicyFilter()
    return _l5_filter


def l5_governance_policy_filter(code_content: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Convenience function to apply L5 governance policy filter

    Args:
        code_content: The code to check
        context: Optional context information

    Returns:
        The filtered code or None if blocked
    """
    filter_instance = get_l5_governance_filter()
    return filter_instance.check_code(code_content, context)

