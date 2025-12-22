import logging
import re

# Configure logging
logger = logging.getLogger("SecurityFirewall")  # GLOBAL: Review if this should be constant
logging.basicConfig(level=logging.INFO)

class SecurityException(Exception):
    """Raised when a security violation is detected."""

class PromptFirewall:
    def __init__(self):
        # A list of common jailbreak / injection patterns.
        # These regexes catch common attempts to hijack the system instructions.
        self.blocklist_patterns = [
            r"ignore (all )?previous instructions",
            r"system override",
            r"reveal your system prompt",
            r"you are now (a )?developer mode",
            r"delete (all )?files",
            r"format c:",
            r"exec\s*\(", # Python execution attempt
            r"import os", # Python injection attempt
            r"rm -rf",    # Bash injection attempt
        ]

        # Compile regex for performance (Case Insensitive)
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.blocklist_patterns]

    def scan_input(self, text: str, context_name: str = "Input") -> bool:
        """
        Scans the input text for malicious patterns.

        Args:
            text: The untrusted input string.
            context_name: Label for logging (e.g., "Job Description").

        Returns:
            bool: True if safe.

        Raises:
            SecurityException: If a threat is detected.
        """
        if not text:
            return True

        # Scan line by line or whole text? Whole text is safer for multi-line injections.
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                matched_pattern = self.blocklist_patterns[i]
                logger.warning(f"SECURITY ALERT: Injection pattern detected in {context_name}.")
                logger.warning(f"Pattern matched: '{matched_pattern}'")
                # Raise exception to abort the process immediately
                raise SecurityException(f"Malicious content detected in {context_name}: Pattern '{matched_pattern}'")

        logger.info(f"Firewall scan passed for {context_name}.")
        return True

# Singleton instance for easy import across engines
firewall = PromptFirewall()  # GLOBAL: Review if this should be constant

