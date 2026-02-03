"""
Verification Gate Adapter - Protocol-compliant wrapper for legacy VerificationGate.

Wraps the existing VerificationGate to conform to VerificationGateProtocol,
enabling integration with the new feature-flagged agent system.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_core.interfaces.verification_protocol import (
    VerificationGateProtocol,
    VerificationRequest,
    VerificationResult,
)
from agentic_core.primitives.feature_flags import FeatureFlagManager

logger = logging.getLogger(__name__)


class VerificationGateAdapter(VerificationGateProtocol):
    """Protocol-compliant adapter for legacy VerificationGate.

    This adapter wraps the existing VerificationGate implementation to
    conform to the VerificationGateProtocol interface, enabling seamless
    integration with the FeatureFlaggedAgentMixin.
    """

    def __init__(self, legacy_gate: Optional[Any] = None):
        """Initialize adapter with optional legacy gate.

        Args:
            legacy_gate: Optional existing VerificationGate instance
        """
        self._legacy_gate = legacy_gate
        self._available = True

        if legacy_gate is None:
            self._initialize_legacy_gate()

    def _initialize_legacy_gate(self) -> None:
        """Lazy-load the legacy VerificationGate."""
        try:
            from agentic_core.L5_safety.security.verification_gate import (
                VerificationGate,
            )

            self._legacy_gate = VerificationGate()
            logger.debug("VerificationGateAdapter: Initialized legacy gate")
        except ImportError as e:
            logger.warning(f"VerificationGateAdapter: Failed to load legacy gate: {e}")
            self._available = False

    def verify_action(self, request: VerificationRequest) -> VerificationResult:
        """Verify if an action can be performed.

        Args:
            request: Verification request with file path, action type, and target

        Returns:
            VerificationResult indicating success/failure with reason
        """
        # Check feature flag first
        if not FeatureFlagManager.is_enabled("ENABLE_VERIFICATION_GATE"):
            return VerificationResult(
                success=True,
                reason="verification_disabled",
                metadata={"flag": "ENABLE_VERIFICATION_GATE", "status": "disabled"},
            )

        # Validate request
        validation_error = self.validate_request(request)
        if validation_error:
            return VerificationResult(
                success=False,
                reason=validation_error,
            )

        # Ensure legacy gate is available
        if self._legacy_gate is None:
            self._initialize_legacy_gate()

        if self._legacy_gate is None:
            return VerificationResult(
                success=True,
                reason="gate_unavailable",
            )

        # Convert file path to Path object
        file_path = Path(request.file_path)

        try:
            # Call legacy implementation
            result = self._legacy_gate.verify_action(
                file_path=file_path,
                action_type=request.action_type,
                target_node=request.target_node,
            )

            if result:
                return VerificationResult(
                    success=True,
                    reason="verified",
                    metadata={
                        "file_path": str(file_path),
                        "action_type": request.action_type,
                        "target_node": request.target_node,
                    },
                )
            else:
                return VerificationResult(
                    success=False,
                    reason="target_not_found",
                    metadata={
                        "file_path": str(file_path),
                        "action_type": request.action_type,
                        "target_node": request.target_node,
                        "message": f"Target '{request.target_node}' not found in file",
                    },
                )

        except Exception as e:
            logger.error(f"VerificationGateAdapter: Error verifying action: {e}")
            return VerificationResult(
                success=False,
                reason="verification_error",
                metadata={"error": str(e)},
            )

    def is_available(self) -> bool:
        """Check if verification gate is available and functional."""
        return self._available and self._legacy_gate is not None

    def get_supported_actions(self) -> List[str]:
        """Get list of supported action types."""
        return self.SUPPORTED_ACTIONS

    def clear_cache(self) -> None:
        """Clear the verification cache."""
        if self._legacy_gate and hasattr(self._legacy_gate, "clear_cache"):
            self._legacy_gate.clear_cache()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        if self._legacy_gate and hasattr(self._legacy_gate, "get_cache_stats"):
            return self._legacy_gate.get_cache_stats()
        return {"cache_size": 0, "cache_keys": []}
