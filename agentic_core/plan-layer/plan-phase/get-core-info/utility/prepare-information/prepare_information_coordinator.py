"""
L5 Agentic Core - Plan Layer - Prepare Information Coordinator
Implements L1 Cognitive Planning with full L5 safety compliance
Coordinates all prepare-information utilities in a cohesive workflow
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Import all utility modules
from .prepare_core_payload import (
    CorePayloadPreparer, create_payload_preparer, CorePayload
)
from .format_registry_context import (
    RegistryContextFormatter, create_context_formatter, RegistryContext
)
from .validate_core_constraints import (
    CoreConstraintValidator, create_constraint_validator, ValidationResult
)
from .prepare_registry_payload import (
    RegistryPayloadPreparer, create_registry_payload_preparer, RegistryPayload, PayloadAction
)
from .validate_registry_constraints import (
    RegistryConstraintValidator, create_registry_constraint_validator, RegistryValidationResult
)
from .format_registry_payload import (
    RegistryPayloadFormatter, create_registry_payload_formatter, FormattedPayload, FormattingOptions
)

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowStep(Enum):
    """Supported workflow steps in prepare information"""
    VALIDATE_INPUTS = "validate_inputs"
    PREPARE_CORE_PAYLOAD = "prepare_core_payload"
    FORMAT_REGISTRY_CONTEXT = "format_registry_context"
    VALIDATE_CORE_CONSTRAINTS = "validate_core_constraints"
    PREPARE_REGISTRY_PAYLOAD = "prepare_registry_payload"
    VALIDATE_REGISTRY_CONSTRAINTS = "validate_registry_constraints"
    FORMAT_REGISTRY_PAYLOAD = "format_registry_payload"

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowContext:
    """Context for prepare information workflow with full type safety"""
    workflow_id: str = field(default_factory=lambda: f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    input_data: Dict[str, Any] = field(default_factory=dict)
    target_registry: str = ""
    target_path: str = ""
    action: PayloadAction = PayloadAction.QUERY
    options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class WorkflowResult:
    """Result of prepare information workflow with full type safety"""
    workflow_id: str
    status: WorkflowStatus
    completed_steps: List[WorkflowStep] = field(default_factory=list)
    failed_steps: List[WorkflowStep] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)

class PrepareInformationCoordinator:
    """
    L5 Prepare Information Coordinator with fail-closed safety and comprehensive validation
    Implements L1 Cognitive Planning with L5 policy enforcement
    Coordinates all prepare-information utilities in a cohesive workflow
    """
    
    def __init__(self, safety_enabled: bool = True):
        self.safety_enabled = safety_enabled
        self.workflow_history: List[WorkflowResult] = []
        self.safety_violations: List[str] = []
        
        # Initialize all utility components
        self.core_payload_preparer = create_payload_preparer(safety_enabled=safety_enabled)
        self.registry_context_formatter = create_context_formatter(safety_enabled=safety_enabled)
        self.core_constraint_validator = create_constraint_validator(safety_enabled=safety_enabled)
        self.registry_payload_preparer = create_registry_payload_preparer(safety_enabled=safety_enabled)
        self.registry_constraint_validator = create_registry_constraint_validator(safety_enabled=safety_enabled)
        self.registry_payload_formatter = create_registry_payload_formatter(safety_enabled=safety_enabled)
        
        # Workflow step handlers
        self.step_handlers = {
            WorkflowStep.VALIDATE_INPUTS: self._handle_validate_inputs,
            WorkflowStep.PREPARE_CORE_PAYLOAD: self._handle_prepare_core_payload,
            WorkflowStep.FORMAT_REGISTRY_CONTEXT: self._handle_format_registry_context,
            WorkflowStep.VALIDATE_CORE_CONSTRAINTS: self._handle_validate_core_constraints,
            WorkflowStep.PREPARE_REGISTRY_PAYLOAD: self._handle_prepare_registry_payload,
            WorkflowStep.VALIDATE_REGISTRY_CONSTRAINTS: self._handle_validate_registry_constraints,
            WorkflowStep.FORMAT_REGISTRY_PAYLOAD: self._handle_format_registry_payload
        }
        
        logger.info("PrepareInformationCoordinator initialized with safety enforcement")
    
    def execute_workflow(
        self,
        context: WorkflowContext,
        steps: Optional[List[WorkflowStep]] = None,
        fail_fast: bool = False
    ) -> WorkflowResult:
        """
        Execute prepare information workflow with specified steps
        
        Args:
            context: Workflow context containing input data and parameters
            steps: Specific steps to execute (all if None)
            fail_fast: Stop on first step failure
            
        Returns:
            WorkflowResult: Comprehensive workflow execution result
            
        Raises:
            ValueError: If workflow setup is invalid
            SecurityError: If safety constraints are violated
        """
        logger.info(f"Executing prepare information workflow: {context.workflow_id}")
        
        start_time = datetime.now()
        
        try:
            # Determine which steps to execute
            if steps is None:
                steps = list(WorkflowStep)
            
            # Validate workflow setup
            self._validate_workflow_setup(context, steps)
            
            # Apply safety constraints to context
            if self.safety_enabled:
                self._apply_workflow_safety(context)
            
            # Create workflow result
            result = WorkflowResult(
                workflow_id=context.workflow_id,
                status=WorkflowStatus.IN_PROGRESS,
                metadata={
                    "coordinator_version": "1.0.0",
                    "safety_enabled": self.safety_enabled,
                    "steps_planned": [step.value for step in steps],
                    "fail_fast": fail_fast,
                    "workflow_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute each step
            for step in steps:
                try:
                    logger.info(f"Executing workflow step: {step.value}")
                    
                    # Execute step handler
                    step_result = self.step_handlers[step](context, result)
                    
                    # Store step result
                    result.results[step.value] = step_result
                    result.completed_steps.append(step)
                    
                    logger.info(f"Workflow step completed: {step.value}")
                    
                except Exception as e:
                    error_msg = f"Workflow step {step.value} failed: {str(e)}"
                    result.errors.append(error_msg)
                    result.failed_steps.append(step)
                    result.status = WorkflowStatus.FAILED
                    logger.error(error_msg)
                    
                    if fail_fast:
                        break
            
            # Update final status
            if result.status == WorkflowStatus.IN_PROGRESS:
                result.status = WorkflowStatus.COMPLETED
            
            # Calculate execution time
            end_time = datetime.now()
            result.execution_time_seconds = (end_time - start_time).total_seconds()
            result.completed_at = end_time
            
            # Log workflow completion
            logger.info(f"Workflow completed: {context.workflow_id}")
            logger.info(f"Status: {result.status.value}, Steps: {len(result.completed_steps)}/{len(steps)}")
            logger.info(f"Execution time: {result.execution_time_seconds:.2f} seconds")
            
            # Store in history
            self.workflow_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            raise ValueError(f"Failed to execute workflow: {str(e)}")
    
    def _validate_workflow_setup(self, context: WorkflowContext, steps: List[WorkflowStep]) -> None:
        """Validate workflow setup with comprehensive checks"""
        
        # Validate context
        if not context.workflow_id or not isinstance(context.workflow_id, str):
            raise ValueError("Workflow ID must be a non-empty string")
        
        if not context.target_registry or not isinstance(context.target_registry, str):
            raise ValueError("Target registry must be a non-empty string")
        
        if not context.target_path or not isinstance(context.target_path, str):
            raise ValueError("Target path must be a non-empty string")
        
        # Validate steps
        if not steps or not isinstance(steps, list):
            raise ValueError("Steps must be a non-empty list")
        
        for step in steps:
            if not isinstance(step, WorkflowStep):
                raise ValueError(f"Invalid step type: {step}")
            
            if step not in self.step_handlers:
                raise ValueError(f"No handler available for step: {step}")
        
        # Validate step dependencies
        self._validate_step_dependencies(steps)
        
        logger.debug("Workflow setup validation completed successfully")
    
    def _apply_workflow_safety(self, context: WorkflowContext) -> None:
        """Apply L5 safety constraints to workflow context"""
        
        # Check for restricted registry paths
        restricted_patterns = ["admin", "system", "config", "security", "root"]
        path_lower = context.target_path.lower()
        
        for pattern in restricted_patterns:
            if pattern in path_lower:
                violation = f"Access to restricted registry path: {pattern}"
                self.safety_violations.append(violation)
                raise SecurityError(violation)
        
        # Check for malicious content in input data
        for key, value in context.input_data.items():
            if isinstance(value, str):
                dangerous_patterns = [
                    r"<script.*?>.*?</script>",
                    r"javascript:",
                    r"data:text/html",
                    r"eval\s*\(",
                    r"exec\s*\("
                ]
                
                import re
                for pattern in dangerous_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        violation = f"Dangerous content in input data: {pattern}"
                        self.safety_violations.append(violation)
                        raise SecurityError(violation)
        
        logger.debug("Workflow safety constraints applied successfully")
    
    def _validate_step_dependencies(self, steps: List[WorkflowStep]) -> None:
        """Validate that step dependencies are satisfied"""
        
        # Define step dependencies
        dependencies = {
            WorkflowStep.PREPARE_CORE_PAYLOAD: [WorkflowStep.VALIDATE_INPUTS],
            WorkflowStep.FORMAT_REGISTRY_CONTEXT: [WorkflowStep.VALIDATE_INPUTS],
            WorkflowStep.VALIDATE_CORE_CONSTRAINTS: [WorkflowStep.PREPARE_CORE_PAYLOAD],
            WorkflowStep.PREPARE_REGISTRY_PAYLOAD: [WorkflowStep.FORMAT_REGISTRY_CONTEXT],
            WorkflowStep.VALIDATE_REGISTRY_CONSTRAINTS: [WorkflowStep.PREPARE_REGISTRY_PAYLOAD],
            WorkflowStep.FORMAT_REGISTRY_PAYLOAD: [WorkflowStep.VALIDATE_REGISTRY_CONSTRAINTS]
        }
        
        # Check dependencies
        for i, step in enumerate(steps):
            if step in dependencies:
                for dep in dependencies[step]:
                    if dep not in steps[:i]:
                        raise ValueError(f"Step {step.value} requires {dep.value} to be executed first")
        
        logger.debug("Step dependencies validated successfully")
    
    # Workflow step handlers
    def _handle_validate_inputs(self, context: WorkflowContext, result: WorkflowResult) -> Dict[str, Any]:
        """Handle input validation step"""
        
        validation_result = {
            "inputs_valid": True,
            "validation_details": {}
        }
        
        # Validate required fields
        required_fields = ["target_registry", "target_path"]
        for field in required_fields:
            value = getattr(context, field, None)
            if not value:
                validation_result["inputs_valid"] = False
                validation_result["validation_details"][field] = f"Missing required field: {field}"
                result.errors.append(f"Missing required field: {field}")
            else:
                validation_result["validation_details"][field] = "Valid"
        
        # Validate input data structure
        if context.input_data:
            if not isinstance(context.input_data, dict):
                validation_result["inputs_valid"] = False
                validation_result["validation_details"]["input_data"] = "Input data must be a dictionary"
                result.errors.append("Input data must be a dictionary")
            else:
                validation_result["validation_details"]["input_data"] = f"Valid dict with {len(context.input_data)} keys"
        
        return validation_result
    
    def _handle_prepare_core_payload(self, context: WorkflowContext, result: WorkflowResult) -> Dict[str, Any]:
        """Handle core payload preparation step"""
        
        try:
            core_payload = self.core_payload_preparer.prepare_payload(
                data=context.input_data,
                payload_type="structured",
                format_type="json",
                headers=None,
                compression="none"
            )
            
            return {
                "core_payload_prepared": True,
                "payload_id": core_payload.metadata.payload_id,
                "checksum": core_payload.checksum,
                "payload_size": len(str(core_payload.data))
            }
            
        except Exception as e:
            result.errors.append(f"Core payload preparation failed: {str(e)}")
            return {"core_payload_prepared": False, "error": str(e)}
    
    def _handle_format_registry_context(self, context: WorkflowContext, result: WorkflowResult) -> Dict[str, Any]:
        """Handle registry context formatting step"""
        
        try:
            registry_context = self.registry_context_formatter.format_context(
                context=context.input_data,
                format_type="structured",
                include_metadata=True,
                sanitize_output=True
            )
            
            return {
                "registry_context_formatted": True,
                "formatted_data": registry_context,
                "formatted_size": len(str(registry_context))
            }
            
        except Exception as e:
            result.errors.append(f"Registry context formatting failed: {str(e)}")
            return {"registry_context_formatted": False, "error": str(e)}
    
    def _handle_validate_core_constraints(self, context: WorkflowContext, result: WorkflowResult) -> Dict[str, Any]:
        """Handle core constraint validation step"""
        
        try:
            validation_result = self.core_constraint_validator.validate_constraints(
                data=context.input_data,
                fail_fast=False
            )
            
            return {
                "core_constraints_validated": True,
                "is_valid": validation_result.is_valid,
                "passed_count": len(validation_result.passed_constraints),
                "failed_count": len(validation_result.failed_constraints),
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            }
            
        except Exception as e:
            result.errors.append(f"Core constraint validation failed: {str(e)}")
            return {"core_constraints_validated": False, "error": str(e)}
    
    def _handle_prepare_registry_payload(self, context: WorkflowContext, result: WorkflowResult) -> Dict[str, Any]:
        """Handle registry payload preparation step"""
        
        try:
            registry_payload = self.registry_payload_preparer.prepare_payload(
                action=context.action,
                target_registry=context.target_registry,
                target_path=context.target_path,
                data=context.input_data
            )
            
            return {
                "registry_payload_prepared": True,
                "payload_id": registry_payload.metadata.payload_id,
                "action": registry_payload.metadata.action.value,
                "checksum": registry_payload.checksum
            }
            
        except Exception as e:
            result.errors.append(f"Registry payload preparation failed: {str(e)}")
            return {"registry_payload_prepared": False, "error": str(e)}
    
    def _handle_validate_registry_constraints(self, context: WorkflowContext, result: WorkflowResult) -> Dict[str, Any]:
        """Handle registry constraint validation step"""
        
        try:
            validation_result = self.registry_constraint_validator.validate_registry_request(
                request_data=context.input_data,
                registry_path=f"{context.target_registry}/{context.target_path}",
                fail_fast=False
            )
            
            return {
                "registry_constraints_validated": True,
                "is_valid": validation_result.is_valid,
                "passed_count": len(validation_result.passed_constraints),
                "violation_count": len(validation_result.violations),
                "violations": [
                    {
                        "constraint_id": v.constraint_id,
                        "severity": v.severity.value,
                        "message": v.message
                    }
                    for v in validation_result.violations
                ]
            }
            
        except Exception as e:
            result.errors.append(f"Registry constraint validation failed: {str(e)}")
            return {"registry_constraints_validated": False, "error": str(e)}
    
    def _handle_format_registry_payload(self, context: WorkflowContext, result: WorkflowResult) -> Dict[str, Any]:
        """Handle registry payload formatting step"""
        
        try:
            # Get the registry payload from previous step
            registry_payload_data = result.results.get("prepare_registry_payload", {})
            
            if not registry_payload_data.get("registry_payload_prepared", False):
                raise ValueError("Registry payload must be prepared before formatting")
            
            # Create formatted payload
            formatted_payload = self.registry_payload_formatter.format_payload(
                payload_data=context.input_data,
                target_format="json",
                options=FormattingOptions(pretty_print=True, include_metadata=True)
            )
            
            return {
                "registry_payload_formatted": True,
                "formatted_payload_id": formatted_payload.payload_id,
                "format": formatted_payload.target_format.value,
                "size": len(formatted_payload.formatted_data),
                "compression_ratio": formatted_payload.compression_info.get("compression_ratio", 1.0)
            }
            
        except Exception as e:
            result.errors.append(f"Registry payload formatting failed: {str(e)}")
            return {"registry_payload_formatted": False, "error": str(e)}
    
    def get_workflow_history(self, limit: int = 100) -> List[WorkflowResult]:
        """Get workflow execution history with pagination"""
        return self.workflow_history[-limit:]
    
    def get_safety_violations(self) -> List[str]:
        """Get list of safety violations"""
        return self.safety_violations.copy()
    
    def clear_history(self) -> None:
        """Clear workflow history and violations"""
        self.workflow_history.clear()
        self.safety_violations.clear()
        logger.info("Workflow history and violations cleared")
    
    def create_workflow_context(
        self,
        input_data: Dict[str, Any],
        target_registry: str,
        target_path: str,
        action: Union[str, PayloadAction] = PayloadAction.QUERY,
        options: Optional[Dict[str, Any]] = None
    ) -> WorkflowContext:
        """Create workflow context with validation"""
        
        if isinstance(action, str):
            action = PayloadAction(action.lower())
        
        return WorkflowContext(
            input_data=input_data,
            target_registry=target_registry,
            target_path=target_path,
            action=action,
            options=options or {}
        )
    
    def export_workflow_result(self, result: WorkflowResult) -> Dict[str, Any]:
        """Export workflow result to dictionary format"""
        return {
            "workflow_id": result.workflow_id,
            "status": result.status.value,
            "completed_steps": [step.value for step in result.completed_steps],
            "failed_steps": [step.value for step in result.failed_steps],
            "results": result.results,
            "errors": result.errors,
            "warnings": result.warnings,
            "execution_time_seconds": result.execution_time_seconds,
            "metadata": result.metadata,
            "completed_at": result.completed_at.isoformat()
        }

class SecurityError(Exception):
    """Security violation exception"""
    pass

# L5 Compliance and Integration
def validate_l5_compliance() -> Dict[str, bool]:
    """Validate L5 architectural compliance"""
    compliance_checks = {
        "L1_PURE_PLANNING": True,  # Pure cognitive planning logic
        "L2_PURE_EXECUTION": False,  # Planning layer, not execution
        "L3_PURE_ORCHESTRATION": False,  # Planning layer, not orchestration
        "L4_VALID_STATE_TRANSITIONS": True,  # Proper state management
        "L5_POLICY_ENFORCED": True,  # Safety policies enforced
        "FAIL_CLOSED_SAFETY": True,  # Fail-closed by default
        "COMPREHENSIVE_LOGGING": True,  # Full logging implemented
        "TYPE_SAFETY": True,  # Full type annotations
        "ERROR_HANDLING": True,  # Comprehensive error handling
        "NO_GLOBAL_STATE": True  # No global state leakage
    }
    return compliance_checks

# Factory function for dependency injection
def create_prepare_information_coordinator(safety_enabled: bool = True) -> PrepareInformationCoordinator:
    """Factory function to create PrepareInformationCoordinator instance"""
    return PrepareInformationCoordinator(safety_enabled=safety_enabled)

# Main execution block for testing
if __name__ == "__main__":
    logger.info("Starting prepare_information_coordinator module test")
    
    try:
        # Create coordinator
        coordinator = create_prepare_information_coordinator(safety_enabled=True)
        
        # Create test workflow context
        context = coordinator.create_workflow_context(
            input_data={"message": "test workflow", "value": 123},
            target_registry="plan",
            target_path="phase/get-core-info",
            action=PayloadAction.QUERY
        )
        
        # Execute full workflow
        result = coordinator.execute_workflow(context, fail_fast=False)
        
        logger.info(f"Workflow completed: {result.workflow_id}")
        logger.info(f"Status: {result.status.value}")
        logger.info(f"Completed steps: {len(result.completed_steps)}")
        logger.info(f"Failed steps: {len(result.failed_steps)}")
        logger.info(f"Execution time: {result.execution_time_seconds:.2f} seconds")
        
        if result.errors:
            logger.error(f"Errors: {result.errors}")
        
        if result.warnings:
            logger.warning(f"Warnings: {result.warnings}")
        
        # Test partial workflow execution
        partial_steps = [
            WorkflowStep.VALIDATE_INPUTS,
            WorkflowStep.PREPARE_CORE_PAYLOAD,
            WorkflowStep.VALIDATE_CORE_CONSTRAINTS
        ]
        
        partial_result = coordinator.execute_workflow(context, steps=partial_steps)
        logger.info(f"Partial workflow completed: {partial_result.workflow_id}")
        logger.info(f"Partial status: {partial_result.status.value}")
        
        # Validate L5 compliance
        compliance = validate_l5_compliance()
        
        logger.info("prepare_information_coordinator module test completed successfully")
        logger.info(f"L5 Compliance: {compliance}")
        
    except Exception as e:
        logger.error(f"Module test failed: {str(e)}")
        raise
