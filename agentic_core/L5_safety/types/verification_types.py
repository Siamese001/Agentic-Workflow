"""
Verification Gate Protocol for decoupling base agents from L5 implementations.

This protocol allows SovereignBaseAgent to type-hint against verification
capabilities without importing concrete L5 implementations, preventing
circular dependencies.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass
class VerificationRequest:
    """Request for verification operation."""
    file_path: str
    action_type: str
    target_node: str
    context: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.context is None:
            self.context = {}

@dataclass
class VerificationResult:
    """Result of verification operation."""
    success: bool
    reason: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

class VerificationGateProtocol(ABC):
    """Protocol for verification gate implementations.

    Implementations must verify that target nodes exist before allowing
    modifications. This prevents hallucinated fixes from being executed.
    """
    SUPPORTED_ACTIONS: list[str] = ['delete_import', 'modify_function', 'remove_class', 'modify_method', 'modify_variable', 'add_import', 'rename_symbol']

    @abstractmethod
    def verify_action(self, request: VerificationRequest) -> VerificationResult:
        """Verify if an action can be performed.

        Args:
            request: Verification request with file path, action type, and target

        Returns:
            VerificationResult indicating success/failure with reason
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if verification gate is available and functional."""
        pass

    @abstractmethod
    def get_supported_actions(self) -> list[str]:
        """Get list of supported action types."""
        pass

    def validate_request(self, request: VerificationRequest) -> str | None:
        """Validate request parameters.

        Returns:
            Error message if invalid, None if valid
        """
        if not request.file_path:
            return 'file_path is required'
        if not request.action_type:
            return 'action_type is required'
        if request.action_type not in self.SUPPORTED_ACTIONS:
            return f'unsupported action_type: {request.action_type}'
        if not request.target_node:
            return 'target_node is required'
        return None
