import logging
import os
import re
import time


class SecretAccessError(Exception):
    """Raised when a secret cannot be retrieved or accessed."""

    pass


class SecretsManagementMixin:
    """
    Phase 1 Critical Infrastructure: Secrets Management (Report 4.4).

    Centralizes credential access with:
    - Environment isolation (DEV/STAGING/PROD)
    - Access auditing (who requested what, when)
    - Abstracted retrieval (env vars -> Vault migration path)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sm_logger = logging.getLogger(self.__class__.__name__)
        # Determine environment context
        self._env_context = os.getenv("SOVEREIGN_ENV", "DEV").upper()
        self._secret_cache: dict[str, tuple[str, float]] = {}
        self._CACHE_TTL = 600

    def _is_valid_secret_key(self, key: str) -> bool:
        return bool(re.match(r"^[A-Z][A-Z0-9_]{3,63}$", key))

    def _audit_access(self, secret_key: str, success: bool):
        """Internal: Log access attempts without revealing the secret value."""
        # In a real system, this might write to a separate secure audit log
        status = "ALLOWED" if success else "DENIED"
        self._sm_logger.info(
            f"AUDIT: Secret access | Key='{secret_key}' | "
            f"Agent='{self.__class__.__name__}' | "
            f"Env='{self._env_context}' | Status='{status}'"
        )

    async def get_secret(self, key: str, default: str | None = None) -> str:
        """
        Securely retrieve a secret value.

        Args:
            key: The identifier for the secret (e.g., 'OPENAI_API_KEY')
            default: Value to return if not found (discouraged for sensitive data)

        Returns:
            The secret string.

        Raises:
            SecretAccessError: If secret is missing and no default provided.
        """
        if not self._is_valid_secret_key(key):
            self._audit_access(key, success=False)
            raise SecretAccessError(f"Invalid secret key format: {key}")

        if key in self._secret_cache:
            value, expiry = self._secret_cache[key]
            if time.time() < expiry:
                self._audit_access(key, success=True)
                return value
            del self._secret_cache[key]

        # 1. Retrieval Strategy (Env Vars now, extensible to Vault later)
        value = os.getenv(key)

        # 2. Fallback handling
        if value is None:
            if default is not None:
                self._audit_access(key, success=True)  # Audit the default usage
                return default

            self._audit_access(key, success=False)
            raise SecretAccessError(
                f"Secret '{key}' not found for agent '{self.__class__.__name__}' "
                f"in environment '{self._env_context}'"
            )

        # 3. Success Audit
        self._audit_access(key, success=True)
        self._secret_cache[key] = (value, time.time() + self._CACHE_TTL)
        return value

    async def rotate_secret(self, key: str) -> bool:
        """
        Trigger a rotation for a compromised or expired secret.
        (Placeholder for future Vault integration)
        """
        self._sm_logger.warning(f"Secret rotation requested for '{key}' - Not implemented in EnvVar mode")
        return False
