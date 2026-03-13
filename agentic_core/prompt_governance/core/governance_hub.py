from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.prompt_governance.security.detectors.pii_scrubber import PIIScrubber


class GovernanceHub:
    """
    Main entry point for safety validation.
    Usage: hub.validate_input(user_prompt)
    """

    def __init__(self):
        self.pii_scrubber = PIIScrubber()
        self.injection_detector = InjectionDetector()

    def validate_input(self, text: str) -> str:
        """
        Runs injection checks first, then scrubs PII.
        Returns sanitized text.
        """
        self.injection_detector.scan(text)
        safe_text = self.pii_scrubber.scrub(text)
        return safe_text

    def validate_output(self, text: str) -> str:
        """
        Scans LLM output for data leaks (PII).
        """
        return self.pii_scrubber.scrub(text)
