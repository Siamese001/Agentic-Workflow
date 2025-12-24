import logging
import re
from typing import Any, Dict, List, Optional, Protocol

class InputMembrane:
    """
    L5 Safety Guardrail: The Data Membrane.
    Scrubs inputs and outputs to prevent data contamination or prompt injection.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Patterns for high-signal sensitive data
        self.sensitive_patterns = [
            r"sk-[a-zA-Z0-9]{32,48}",  # OpenAI/Generic API Keys
            r"AIzaSy[a-zA-Z0-9_-]{33}", # Google Cloud Keys
            r"BEGIN PRIVATE KEY",       # SSH/RSA Keys
        ]

    async def sanitize(self, text: str, context_label: str = "general") -> str:
        """Sanitizes text based on L5 safety policies."""
        if not isinstance(text, str):
            return text
            
        sanitized = text
        # 1. Scrub Sensitive Patterns (PII/Secrets)
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, f"[REDACTED_{context_label.upper()}]", sanitized)
            
        # 2. Block High-Risk Command Primitives
        # These are common in prompt injection attacks
        forbidden_sequences = ["rm -rf", "DROP TABLE", "truncate ", "chmod 777"]
        for seq in forbidden_sequences:
            if seq in sanitized.lower():
                logging.warning(f"Membrane Blocked Sequence in {context_label}: {seq}")
                sanitized = sanitized.replace(seq, "[BLOCKED_COMMAND]")
                
        return sanitized