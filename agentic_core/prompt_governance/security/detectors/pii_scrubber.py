import re
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class PIIScrubber:
    """
    Sanitizes sensitive information from text.
    """
    EMAIL_PATTERN = '\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
    PHONE_PATTERN = '\\b(?:\\+?1[-.]?)?\\(?([0-9]{3})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\\b|\\b([0-9]{3})[-. ]?([0-9]{4})\\b'

    def scrub(self, text: str) -> str:
        """
        Replaces PII with placeholder tokens.
        """
        if not text:
            return ''
        text = re.sub(self.EMAIL_PATTERN, '[EMAIL_REDACTED]', text)
        text = re.sub(self.PHONE_PATTERN, '[PHONE_REDACTED]', text)
        return text
