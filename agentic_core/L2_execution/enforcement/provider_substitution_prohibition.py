"""
Provider Substitution Prohibition (REQ-415)

Ensures SovereignLLMGateway MUST NOT substitute provider/model on failure.
Any failure MUST be fail-closed.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ProviderRequest:
    """Immutable record of original provider request."""
    provider: str
    model: str
    agent_id: str
    request_id: str

class ProviderSubstitutionViolation(Exception):
    """Raised when provider substitution is attempted."""
    pass

def validate_provider_request(original_request: ProviderRequest, actual_provider: str, actual_model: str, context: dict[str, Any] | None=None) -> None:
    """Validate that no provider/model substitution occurred (REQ-415).

    Args:
        original_request: The original request made by the agent
        actual_provider: The provider actually used
        actual_model: The model actually used
        context: Optional context for logging

    Raises:
        ProviderSubstitutionViolation: If substitution is detected
    """
    if actual_provider != original_request.provider:
        violation_msg = f"Provider substitution detected: agent '{original_request.agent_id}' requested provider '{original_request.provider}' but got '{actual_provider}'. Provider substitution is prohibited (REQ-415)."
        Logger.error(violation_msg)
        raise ProviderSubstitutionViolation(violation_msg)
    if actual_model != original_request.model:
        violation_msg = f"Model substitution detected: agent '{original_request.agent_id}' requested model '{original_request.model}' but got '{actual_model}'. Model substitution is prohibited (REQ-415)."
        Logger.error(violation_msg)
        raise ProviderSubstitutionViolation(violation_msg)
    Logger.debug(f"Provider request validated: agent '{original_request.agent_id}' using provider '{actual_provider}' with model '{actual_model}'")

def enforce_fail_closed_on_failure(original_request: ProviderRequest, error: Exception, attempted_substitution: dict[str, str] | None=None) -> None:
    """Ensure fail-closed behavior on provider failure (REQ-415).

    Args:
        original_request: The original request that failed
        error: The error that occurred
        attempted_substitution: Any attempted substitution (for logging)

    Raises:
        ProviderSubstitutionViolation: Always raises to ensure fail-closed
    """
    violation_msg = f"Provider request failed for agent '{original_request.agent_id}' with provider '{original_request.provider}' and model '{original_request.model}'. Error: {error}. Fail-closed enforced - no substitution allowed (REQ-415)."
    if attempted_substitution:
        violation_msg += f" Attempted substitution to provider '{attempted_substitution.get('provider', 'unknown')}' with model '{attempted_substitution.get('model', 'unknown')}' was blocked."
    Logger.error(violation_msg)
    raise ProviderSubstitutionViolation(violation_msg)

class ProviderSubstitutionGuard:
    """Guard to prevent provider/model substitution in SovereignLLMGateway."""

    def __init__(self):
        self._active_requests: dict[str, ProviderRequest] = {}

    def register_request(self, request_id: str, provider_request: ProviderRequest) -> None:
        """Register a provider request for tracking.

        Args:
            request_id: Unique request identifier
            provider_request: The provider request details
        """
        self._active_requests[request_id] = provider_request
        Logger.debug(f'Registered provider request {request_id} for agent {provider_request.agent_id}')

    def validate_response(self, request_id: str, actual_provider: str, actual_model: str) -> None:
        """Validate that the response matches the original request.

        Args:
            request_id: Request identifier
            actual_provider: Provider that actually responded
            actual_model: Model that actually responded

        Raises:
            ProviderSubstitutionViolation: If substitution is detected
        """
        if request_id not in self._active_requests:
            raise ProviderSubstitutionViolation(f'Unknown request ID {request_id}. Cannot validate provider substitution.')
        original_request = self._active_requests[request_id]
        validate_provider_request(original_request, actual_provider, actual_model)

    def handle_failure(self, request_id: str, error: Exception, attempted_substitution: dict[str, str] | None=None) -> None:
        """Handle provider failure with fail-closed enforcement.

        Args:
            request_id: Request identifier
            error: The error that occurred
            attempted_substitution: Any attempted substitution

        Raises:
            ProviderSubstitutionViolation: Always raises to ensure fail-closed
        """
        if request_id not in self._active_requests:
            raise ProviderSubstitutionViolation(f'Unknown request ID {request_id}. Cannot enforce fail-closed.')
        original_request = self._active_requests[request_id]
        enforce_fail_closed_on_failure(original_request, error, attempted_substitution)

    def clear_request(self, request_id: str) -> None:
        """Clear a completed request.

        Args:
            request_id: Request identifier to clear
        """
        self._active_requests.pop(request_id, None)
        Logger.debug(f'Cleared provider request {request_id}')
_substitution_guard = ProviderSubstitutionGuard()

def get_substitution_guard() -> ProviderSubstitutionGuard:
    """Get the global provider substitution guard.

    Returns:
        The global ProviderSubstitutionGuard instance
    """
    return _substitution_guard

def test_provider_substitution_prohibition() -> bool:
    """Test that provider substitution prohibition is working.

    Returns:
        True if prohibition is enforced, False otherwise
    """
    try:
        test_request = ProviderRequest(provider='openai', model='gpt-4', agent_id='test_agent', request_id='test_123')
        try:
            validate_provider_request(test_request, 'anthropic', 'claude-3-5-sonnet')
            return False
        except ProviderSubstitutionViolation:
            pass
        try:
            validate_provider_request(test_request, 'openai', 'gpt-3.5-turbo')
            return False
        except ProviderSubstitutionViolation:
            pass
        try:
            validate_provider_request(test_request, 'openai', 'gpt-4')
        except ProviderSubstitutionViolation:
            return False
        return True
    except Exception:
        return False
