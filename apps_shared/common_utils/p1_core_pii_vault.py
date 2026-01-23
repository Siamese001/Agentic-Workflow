"""PII Vault for protecting sensitive information.

Grafted from monolith with Presidio-based PII detection and redaction.
"""

import logging

LOGGER = logging.getLogger(__name__)

# pip install presidio-analyzer presidio-anonymizer
try:
    PRESIDIO_AVAILABLE = True
except ImportError:
    LOGGER.warning("Presidio not installed. PII detection will be limited.")
    PRESIDIO_AVAILABLE = False
    # Fallback implementations
    AnalyzerEngine = None
    AnonymizerEngine = None
    OperatorConfig = None


class PIIVault:
    """Vault for PII detection, redaction, and restoration."""

    def __init__(self):
        """Initialize the PII vault."""
        if PRESIDIO_AVAILABLE:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
        else:
            self.analyzer = None
            self.anonymizer = None

        self._mappings: dict[str, dict[str, str]] = {}
        LOGGER.info("PII Vault initialized")

    def redact(self, session_id: str, text: str) -> str:
        """Replace PII with tokens <ENTITY_TYPE>.

        Args:
            session_id: Unique session identifier
            text: Text to redact

        Returns:
            Redacted text with PII replaced by tokens
        """
        if not PRESIDIO_AVAILABLE or not self.analyzer or not self.anonymizer:
            # Fallback: simple regex-based redaction
            return self._fallback_redact(text)

        try:
            # Analyze text for PII
            results = self.analyzer.analyze(
                text=text,
                entities=[
                    "PERSON",
                    "EMAIL_ADDRESS",
                    "PHONE_NUMBER",
                    "US_SSN",
                    "CREDIT_CARD",
                    "IBAN_CODE",
                    "IP_ADDRESS",
                    "URL",
                ],
                language="en",
            )

            # Store original values for potential restoration
            if session_id not in self._mappings:
                self._mappings[session_id] = {}

            for result in results:
                original_value = text[result.start : result.end]
                self._mappings[session_id][str(result.start)] = {
                    "value": original_value,
                    "type": result.entity_type,
                }

            # Anonymize with custom operators
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators={
                    "DEFAULT": OperatorConfig("replace", {"new_value": f"<{result.entity_type}>"})
                },
            )

            return anonymized.text
        except Exception as e:
            LOGGER.error(f"PII redaction failed: {e}")
            return text

    def restore(self, session_id: str, text: str) -> str:
        """Restore redacted text to original form.

        Args:
            session_id: Session identifier for restoration
            text: Redacted text to restore

        Returns:
            Restored text if available, otherwise original text
        """
        if session_id not in self._mappings:
            LOGGER.warning(f"No PII mappings found for session {session_id}")
            return text

        try:
            restored = text
            mappings = self._mappings[session_id]

            # Replace tokens with original values
            for pos, info in mappings.items():
                token = f"<{info['type']}>"
                if token in restored:
                    restored = restored.replace(token, info["value"], 1)

            return restored
        except Exception as e:
            LOGGER.error(f"PII restoration failed: {e}")
            return text

    def _fallback_redact(self, text: str) -> str:
        """Fallback PII redaction using regex patterns."""
        import re

        # Simple email redaction
        text = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "<EMAIL_ADDRESS>", text
        )

        # Simple phone redaction
        text = re.sub(r"\b\d{3}-\d{3}-\d{4}\b", "<PHONE_NUMBER>", text)
        text = re.sub(r"\b\(\d{3}\)\s*\d{3}-\d{4}\b", "<PHONE_NUMBER>", text)

        # Simple SSN redaction
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "<US_SSN>", text)

        return text

    def clear_session(self, session_id: str):
        """Clear PII mappings for a session.

        Args:
            session_id: Session to clear
        """
        if session_id in self._mappings:
            del self._mappings[session_id]
            LOGGER.info(f"Cleared PII mappings for session {session_id}")

    def get_stats(self) -> dict[str, Any]:
        """Get vault statistics.

        Returns:
            Statistics about PII detection and redaction
        """
        return {
            "active_sessions": len(self._mappings),
            "presidio_available": PRESIDIO_AVAILABLE,
            "total_mappings": sum(len(m) for m in self._mappings.values()),
        }


def create_pii_vault() -> PIIVault:
    """Factory function to create PII vault instance."""
    return PIIVault()
