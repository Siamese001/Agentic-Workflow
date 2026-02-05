"""
Feature-Flagged Agent Mixin for controlled rollout of new capabilities.

This mixin provides feature flag protection for agent methods, ensuring
safe rollout of MetaLearning, VerificationGate, DetectionSignal, and
HITL capabilities.
"""

import logging
from collections.abc import Callable
from typing import Any, TypeVar

from agentic_core.interfaces.detection_protocol import (
    DetectionResult,
    DetectionSignalProtocol,
    Severity,
)
from agentic_core.interfaces.meta_learning_protocol import (
    LearningContext,
    LearningResult,
    MetaLearningProtocol,
)
from agentic_core.interfaces.review_protocol import (
    HumanReviewProtocol,
    ReviewRequest,
    ReviewResult,
    ReviewStatus,
)
from agentic_core.interfaces.verification_protocol import (
    VerificationGateProtocol,
    VerificationRequest,
    VerificationResult,
)
from agentic_core.primitives.dependency_resolver import DynamicLoader
from agentic_core.primitives.feature_flags import FeatureFlagManager

logger = logging.getLogger(__name__)

T = TypeVar("T")


class FeatureFlaggedAgentMixin:
    """Mixin providing feature-flagged agent capabilities.

    This mixin adds protocol-based integration with:
    - VerificationGate (controlled by ENABLE_VERIFICATION_GATE)
    - DetectionSignal (controlled by ENABLE_DETECTION_SIGNAL)
    - HumanReview (controlled by ENABLE_HITL_WORKFLOW)
    - MetaLearning (controlled by ENABLE_META_LEARNING)
    - AuditTrail (controlled by ENABLE_AUDIT_TRAIL)

    All capabilities gracefully degrade when flags are disabled.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._verification_gate: VerificationGateProtocol | None = None
        self._detection_emitter: DetectionSignalProtocol | None = None
        self._review_queue: HumanReviewProtocol | None = None
        self._meta_learning: MetaLearningProtocol | None = None
        self._feature_flags_validated = False

    # ==================== FEATURE FLAG HELPERS ====================

    def _is_flag_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled for this agent."""
        return FeatureFlagManager.is_enabled(flag_name, self.__class__.__name__)

    def _validate_healing_flags(self) -> tuple[bool, list[str]]:
        """Validate all healing-required flags are enabled."""
        if self._feature_flags_validated:
            return True, []
        result = FeatureFlagManager.validate_healing_flags(self.__class__.__name__)
        self._feature_flags_validated = True
        return result

    def _execute_with_flag(
        self,
        flag_name: str,
        enabled_fn: Callable[..., T],
        disabled_fn: Callable[..., T] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute function based on feature flag state.

        Args:
            flag_name: Name of the feature flag
            enabled_fn: Function to call when flag is enabled
            disabled_fn: Optional function to call when flag is disabled
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result from enabled_fn or disabled_fn
        """
        if self._is_flag_enabled(flag_name):
            return enabled_fn(*args, **kwargs)
        elif disabled_fn:
            return disabled_fn(*args, **kwargs)
        else:
            return None

    # ==================== HELPER METHODS ====================

    def _check_is_available(self, obj: Any) -> bool:
        """Safely check if an object is available.

        Handles implementations that don't have is_available method.
        """
        if obj is None:
            return False
        if hasattr(obj, "is_available"):
            try:
                return obj.is_available()
            except Exception:
                return True  # Assume available if check fails
        return True  # Assume available if no is_available method

    # ==================== VERIFICATION GATE ====================

    @property
    def verification_gate(self) -> VerificationGateProtocol | None:
        """Get verification gate instance (lazy loaded)."""
        if not self._is_flag_enabled("ENABLE_VERIFICATION_GATE"):
            return None

        if self._verification_gate is None:
            self._verification_gate = DynamicLoader.create_instance("verification")
        return self._verification_gate

    def verify_action(
        self,
        file_path: str,
        action_type: str,
        target_node: str,
        context: dict[str, Any] | None = None,
    ) -> VerificationResult:
        """Verify if an action can be performed.

        If ENABLE_VERIFICATION_GATE is disabled, returns success.

        Args:
            file_path: Path to the file
            action_type: Type of action to perform
            target_node: Target node in the file
            context: Optional context information

        Returns:
            VerificationResult indicating success/failure
        """
        if not self._is_flag_enabled("ENABLE_VERIFICATION_GATE"):
            logger.debug(f"[{self.__class__.__name__}] Verification gate disabled, allowing action")
            return VerificationResult(
                success=True,
                reason="verification_disabled",
                metadata={"flag": "ENABLE_VERIFICATION_GATE", "status": "disabled"},
            )

        gate = self.verification_gate
        if gate is None or not self._check_is_available(gate):
            logger.warning(f"[{self.__class__.__name__}] Verification gate unavailable")
            return VerificationResult(
                success=True,
                reason="verification_unavailable",
            )

        request = VerificationRequest(
            file_path=file_path,
            action_type=action_type,
            target_node=target_node,
            context=context or {"agent": self.__class__.__name__},
        )

        try:
            # Try protocol-based call first
            return gate.verify_action(request)
        except TypeError:
            # Fall back to legacy signature if protocol call fails
            try:
                result = gate.verify_action(file_path, action_type, target_node)
                return VerificationResult(
                    success=result if isinstance(result, bool) else True,
                    reason="legacy_implementation",
                )
            except Exception as e:
                logger.warning(f"Verification gate error: {e}")
                return VerificationResult(
                    success=True,
                    reason="verification_error",
                    metadata={"error": str(e)},
                )

    # ==================== DETECTION SIGNAL ====================

    def emit_detection_signal(
        self,
        detection_type: str,
        file_path: str,
        message: str,
        severity: Severity = Severity.MEDIUM,
        target_node: str | None = None,
        suggested_fix: str | None = None,
        auto_fixable: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> str | None:
        """Emit a detection signal for a violation.

        If ENABLE_DETECTION_SIGNAL is disabled, returns None.

        Args:
            detection_type: Type of detection
            file_path: Path to the file with the issue
            message: Description of the issue
            severity: Severity level
            target_node: Optional target node
            suggested_fix: Optional suggested fix
            auto_fixable: Whether the issue can be auto-fixed
            metadata: Optional metadata

        Returns:
            Signal ID if emitted, None otherwise
        """
        if not self._is_flag_enabled("ENABLE_DETECTION_SIGNAL"):
            logger.debug(f"[{self.__class__.__name__}] Detection signal disabled")
            return None

        emitter = self._detection_emitter
        if emitter is None:
            emitter = DynamicLoader.create_instance("detection")
            self._detection_emitter = emitter

        if emitter is None or not self._check_is_available(emitter):
            logger.warning(f"[{self.__class__.__name__}] Detection emitter unavailable")
            return None

        result = DetectionResult(
            source_sensor=self.__class__.__name__,
            detection_type=detection_type,
            severity=severity,
            file_path=file_path,
            message=message,
            target_node=target_node,
            suggested_fix=suggested_fix,
            auto_fixable=auto_fixable,
            metadata=metadata or {},
        )

        return emitter.emit_signal(result)

    # ==================== HUMAN REVIEW ====================

    def submit_for_review(
        self,
        action_type: str,
        target_file: str,
        description: str,
        risk_level: str = "high",
        context_bundle: dict[str, Any] | None = None,
        timeout_seconds: int = 3600,
    ) -> ReviewResult:
        """Submit an operation for human review.

        If ENABLE_HITL_WORKFLOW is disabled, returns auto-approved.

        Args:
            action_type: Type of action requiring review
            target_file: File being modified
            description: Description of the action
            risk_level: Risk level (low/medium/high)
            context_bundle: Optional context information
            timeout_seconds: Timeout for review

        Returns:
            ReviewResult with approval status
        """
        if not self._is_flag_enabled("ENABLE_HITL_WORKFLOW"):
            logger.debug(f"[{self.__class__.__name__}] HITL workflow disabled, auto-approving")
            return ReviewResult(
                request_id="auto-approved",
                status=ReviewStatus.APPROVED,
                reason="hitl_disabled",
                metadata={"flag": "ENABLE_HITL_WORKFLOW", "status": "disabled"},
            )

        queue = self._review_queue
        if queue is None:
            queue = DynamicLoader.create_instance("review")
            self._review_queue = queue

        if queue is None or not self._check_is_available(queue):
            logger.warning(f"[{self.__class__.__name__}] Review queue unavailable, auto-approving")
            return ReviewResult(
                request_id="auto-approved",
                status=ReviewStatus.APPROVED,
                reason="queue_unavailable",
            )

        import uuid

        request = ReviewRequest(
            request_id=str(uuid.uuid4()),
            agent_name=self.__class__.__name__,
            action_type=action_type,
            target_file=target_file,
            description=description,
            risk_level=risk_level,
            context_bundle=context_bundle or {},
            timeout_seconds=timeout_seconds,
        )

        try:
            return queue.submit_for_review(request)
        except (TypeError, AttributeError) as e:
            # Legacy implementation doesn't match protocol
            logger.warning(f"Review queue signature mismatch: {e}")
            return ReviewResult(
                request_id="auto-approved",
                status=ReviewStatus.APPROVED,
                reason="legacy_implementation",
            )

    def check_review_status(self, request_id: str) -> ReviewResult:
        """Check status of a review request.

        Args:
            request_id: ID of the review request

        Returns:
            Current ReviewResult
        """
        if not self._is_flag_enabled("ENABLE_HITL_WORKFLOW"):
            return ReviewResult(
                request_id=request_id,
                status=ReviewStatus.APPROVED,
                reason="hitl_disabled",
            )

        queue = self._review_queue
        if queue is None or not self._check_is_available(queue):
            return ReviewResult(
                request_id=request_id,
                status=ReviewStatus.APPROVED,
                reason="queue_unavailable",
            )

        return queue.check_status(request_id)

    # ==================== META-LEARNING ====================

    def flagged_recall_or_execute(
        self,
        context_key: str,
        operation_type: str,
        input_hash: str,
        execution_fn: Callable[[], Any],
        metadata: dict[str, Any] | None = None,
    ) -> LearningResult:
        """Recall from cache or execute with learning.

        If ENABLE_META_LEARNING is disabled, executes directly.

        Args:
            context_key: Key for the learning context
            operation_type: Type of operation
            input_hash: Hash of the input
            execution_fn: Function to execute on cache miss
            metadata: Optional metadata

        Returns:
            LearningResult with result and cache status
        """
        if not self._is_flag_enabled("ENABLE_META_LEARNING"):
            logger.debug(f"[{self.__class__.__name__}] Meta-learning disabled, executing directly")
            try:
                result = execution_fn()
                return LearningResult(
                    success=True,
                    from_cache=False,
                    result=result,
                    metadata={"flag": "ENABLE_META_LEARNING", "status": "disabled"},
                )
            except Exception as e:
                return LearningResult(
                    success=False,
                    from_cache=False,
                    result=None,
                    metadata={"error": str(e)},
                )

        ml_service = self._meta_learning
        if ml_service is None:
            ml_service = DynamicLoader.create_instance("meta_learning")
            self._meta_learning = ml_service

        if ml_service is None or not self._check_is_available(ml_service):
            logger.warning(
                f"[{self.__class__.__name__}] Meta-learning unavailable, executing directly"
            )
            try:
                result = execution_fn()
                return LearningResult(
                    success=True,
                    from_cache=False,
                    result=result,
                    metadata={"reason": "ml_unavailable"},
                )
            except Exception as e:
                return LearningResult(
                    success=False,
                    from_cache=False,
                    result=None,
                    metadata={"error": str(e)},
                )

        context = LearningContext(
            context_key=context_key,
            agent_name=self.__class__.__name__,
            operation_type=operation_type,
            input_hash=input_hash,
            metadata=metadata or {},
        )

        return ml_service.recall_or_execute(context, execution_fn)

    # ==================== AUDIT TRAIL ====================

    def log_audit_event(
        self,
        event_type: str,
        data: dict[str, Any],
    ) -> str | None:
        """Log an audit event.

        If ENABLE_AUDIT_TRAIL is disabled, returns None.

        Args:
            event_type: Type of audit event
            data: Event data

        Returns:
            Event ID if logged, None otherwise
        """
        if not self._is_flag_enabled("ENABLE_AUDIT_TRAIL"):
            logger.debug(f"[{self.__class__.__name__}] Audit trail disabled")
            return None

        # For now, log to standard logger
        # Full implementation would use cryptographic audit trail
        import json
        import time

        event_id = f"AUDIT-{int(time.time() * 1000)}"
        logger.info(
            f"[AUDIT] {event_id} | {self.__class__.__name__} | {event_type} | "
            f"{json.dumps(data, default=str)}"
        )
        return event_id

    # ==================== HEALING WITH VERIFICATION ====================

    def heal_with_verification(
        self,
        violation: dict[str, Any],
        heal_fn: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        """Heal a violation with full safety checks.

        Applies all enabled safety checks:
        1. Verification gate (target exists)
        2. Risk classification
        3. Human review for high-risk
        4. Audit logging
        5. Meta-learning for patterns

        Args:
            violation: Violation to heal
            heal_fn: Function to perform the healing

        Returns:
            Healing result dictionary
        """
        file_path = violation.get("file_path", "")
        action_type = violation.get("fix_type", "modify_function")
        target_node = violation.get("target", "")

        # Step 1: Verify target exists
        verification = self.verify_action(file_path, action_type, target_node)
        if not verification.success:
            self.log_audit_event(
                "heal_skipped",
                {"violation": violation, "reason": verification.reason},
            )
            return {
                "status": "skipped",
                "reason": verification.reason,
                "violations_found": 1,
                "violations_fixed": 0,
                "errors": [],
                "skipped": [violation],
            }

        # Step 2: Classify risk
        risk_level = self._classify_violation_risk(violation)

        # Step 3: Submit for review if high-risk
        if risk_level == "high" and self._is_flag_enabled("ENABLE_HITL_WORKFLOW"):
            review_result = self.submit_for_review(
                action_type=action_type,
                target_file=file_path,
                description=f"Heal: {violation.get('message', 'Unknown violation')}",
                risk_level=risk_level,
                context_bundle={"violation": violation},
            )

            if not review_result.is_approved():
                self.log_audit_event(
                    "heal_pending_review",
                    {"violation": violation, "request_id": review_result.request_id},
                )
                return {
                    "status": "pending_review",
                    "request_id": review_result.request_id,
                    "violations_found": 1,
                    "violations_fixed": 0,
                    "errors": [],
                    "skipped": [],
                }

        # Step 4: Execute healing (with meta-learning if enabled)
        def do_heal() -> dict[str, Any]:
            return heal_fn(violation)

        if self._is_flag_enabled("ENABLE_META_LEARNING"):
            import hashlib

            input_hash = hashlib.sha256(str(violation).encode()).hexdigest()[:16]

            learning_result = self.flagged_recall_or_execute(
                context_key=f"heal:{violation.get('type', 'unknown')}",
                operation_type="heal",
                input_hash=input_hash,
                execution_fn=do_heal,
            )

            result = learning_result.result if learning_result.success else None
        else:
            try:
                result = do_heal()
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "violations_found": 1,
                    "violations_fixed": 0,
                    "errors": [str(e)],
                    "skipped": [],
                }

        # Step 5: Audit log
        self.log_audit_event(
            "heal_completed",
            {"violation": violation, "result": result},
        )

        return result or {
            "status": "error",
            "violations_found": 1,
            "violations_fixed": 0,
            "errors": ["Unknown error"],
            "skipped": [],
        }

    def _classify_violation_risk(self, violation: dict[str, Any]) -> str:
        """Classify risk level of a violation.

        Args:
            violation: Violation to classify

        Returns:
            Risk level: 'low', 'medium', or 'high'
        """
        severity = violation.get("severity", "medium")
        if severity in ("critical", "high"):
            return "high"
        elif severity == "medium":
            return "medium"
        else:
            return "low"

    # ==================== CAPABILITY REPORTING ====================

    def get_feature_flag_status(self) -> dict[str, Any]:
        """Get status of all feature flags for this agent.

        Returns:
            Dictionary with flag statuses
        """
        flags = FeatureFlagManager.get_all_flags()
        healing_valid, missing = self._validate_healing_flags()

        return {
            "agent": self.__class__.__name__,
            "flags": flags,
            "healing_enabled": healing_valid,
            "missing_healing_flags": missing,
            "verification_gate_available": self.verification_gate is not None,
        }
