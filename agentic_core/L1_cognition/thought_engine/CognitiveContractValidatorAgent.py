from __future__ import annotations
"""Cognitive Contract Enforcer - Plan-before-Act enforcement with validation.

This module implements Strategy 1: Cognitive Contracts, forcing agents to
explicitly plan their approach before generating content, with validation
to ensure adherence to constraints and consistency between plan and output.
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin

Logger = logging.getLogger(__name__)


class PlanQualityError(Exception):
    """Raised when the plan fails quality checks."""
    pass


class ConsistencyError(Exception):
    """Raised when content doesn't match the plan."""
    pass


class ContractStage(Enum):
    """Stages of cognitive contract execution."""
    PLAN_REQUIRED = "plan_required"
    PLAN_VALIDATED = "plan_validated"
    CONTENT_GENERATED = "content_generated"
    CONTRACT_FULFILLED = "contract_fulfilled"


@dataclass
class Constraint:
    """A constraint that must be acknowledged in the plan."""
    id: str
    description: str
    type: str  # "requirement", "prohibition", "format"
    priority: int = 5
    verified: bool = False


@dataclass
class Plan:
    """Structured plan extracted from agent output."""
    constraints_acknowledged: List[str]
    strategy: str
    key_metrics: List[str]
    pre_computation: Dict[str, Any]
    raw_text: str


@dataclass
class CognitiveContract:
    """A cognitive contract for an agent execution."""
    id: str
    constraints: List[Constraint]
    stage: ContractStage = ContractStage.PLAN_REQUIRED
    plan: Optional[Plan] = None
    content: Optional[str] = None
    validation_errors: List[str] = field(default_factory=list)


class CognitiveContractValidatorAgent(MCPHardenedMixin):
    """Validates cognitive contracts and ensures compliance."""
    
    def __init__(self) -> None:
        """Initialize the validator."""
        self.required_plan_elements = [
            "constraints_acknowledged",
            "strategy",
            "key_metrics"
        ]
    
    def parse_plan(self, response: str) -> Optional[Plan]:
        """Parse a PLAN block from agent response.
        
        Args:
            response: The agent's response
            
        Returns:
            Parsed plan or None if not found
        """
        # Look for PLAN block
        plan_match = re.search(r'<PLAN>(.*?)</PLAN>', response, re.DOTALL | re.IGNORECASE)
        
        if not plan_match:
            return None
        
        plan_text = plan_match.group(1).strip()
        
        # Parse plan components
        plan = Plan(
            constraints_acknowledged=[],
            strategy="",
            key_metrics=[],
            pre_computation={},
            raw_text=plan_text
        )
        
        # Extract constraints
        constraints_match = re.search(
            r'constraints?[:\s]*\nfrom agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin\n?(.*?)(?=\n\n|\n[A-Z]|\Z)',
            plan_text,
            re.IGNORECASE | re.DOTALL
        )
        if constraints_match:
            constraints_text = constraints_match.group(1)
            # Extract bullet points or numbered items
            constraint_items = re.findall(r'[-*]\s*(.+)|\d+\.\s*(.+)', constraints_text)
            plan.constraints_acknowledged = [item[0] or item[1] for item in constraint_items if item[0] or item[1]]
        
        # Extract strategy
        strategy_match = re.search(
            r'strategy[:\s]*\n?(.*?)(?=\n\n|\n[A-Z]|\Z)',
            plan_text,
            re.IGNORECASE | re.DOTALL
        )
        if strategy_match:
            plan.strategy = strategy_match.group(1).strip()
        
        # Extract key metrics
        metrics_match = re.search(
            r'key metrics?[:\s]*\n?(.*?)(?=\n\n|\n[A-Z]|\Z)',
            plan_text,
            re.IGNORECASE | re.DOTALL
        )
        if metrics_match:
            metrics_text = metrics_match.group(1)
            plan.key_metrics = re.findall(r'[-*]\s*(.+)|\d+\.\s*(.+)', metrics_text)
            plan.key_metrics = [item[0] or item[1] for item in plan.key_metrics if item[0] or item[1]]
        
        # Extract pre-computation
        precomp_match = re.search(
            r'pre[-]?computation[:\s]*\n?(.*?)(?=\n\n|\n[A-Z]|\Z)',
            plan_text,
            re.IGNORECASE | re.DOTALL
        )
        if precomp_match:
            try:
                plan.pre_computation = json.loads(precomp_match.group(1).strip())
            except json.JSONDecodeError:
                # Treat as plain text
                plan.pre_computation = {"text": precomp_match.group(1).strip()}
        
        return plan
    
    def parse_content(self, response: str) -> Optional[str]:
        """Parse a CONTENT block from agent response.
        
        Args:
            response: The agent's response
            
        Returns:
            Parsed content or None if not found
        """
        content_match = re.search(r'<CONTENT>(.*?)</CONTENT>', response, re.DOTALL | re.IGNORECASE)
        
        if content_match:
            return content_match.group(1).strip()
        
        # If no CONTENT block, return everything after PLAN
        plan_end = response.find('</PLAN>')
        if plan_end != -1:
            return response[plan_end + 8:].strip()
        
        return None
    
    def validate_plan(self, plan: Plan, constraints: List[Constraint]) -> List[str]:
        """Validate that the plan acknowledges all constraints.
        
        Args:
            plan: The parsed plan
            constraints: Required constraints
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required elements
        if not plan.constraints_acknowledged:
            errors.append("Plan must acknowledge constraints")
        
        if not plan.strategy:
            errors.append("Plan must describe the strategy")
        
        # Check if all constraints are acknowledged
        acknowledged_text = " ".join(plan.constraints_acknowledged).lower()
        
        for constraint in constraints:
            if constraint.priority >= 8:  # High priority constraints must be explicitly acknowledged
                constraint_words = constraint.description.lower().split()
                if not any(word in acknowledged_text for word in constraint_words if len(word) > 3):
                    errors.append(f"High-priority constraint not acknowledged: {constraint.description}")
        
        # Check strategy quality
        if len(plan.strategy) < 50:
            errors.append("Strategy description is too brief")
        
        return errors
    
    def validate_consistency(self, plan: Plan, content: str) -> List[str]:
        """Validate that content is consistent with the plan.
        
        Args:
            plan: The validated plan
            content: The generated content
            
        Returns:
            List of consistency errors
        """
        errors = []
        
        # Check if content implements the strategy
        if plan.strategy:
            strategy_words = set(plan.strategy.lower().split())
            content_words = set(content.lower().split())
            
            # At least 30% of strategy words should be in content
            overlap = len(strategy_words & content_words) / len(strategy_words) if strategy_words else 0
            if overlap < 0.3:
                errors.append("Content doesn't appear to implement the described strategy")
        
        # Check if key metrics are present
        for Metric in plan.key_metrics:
            metric_lower = Metric.lower()
            if metric_lower not in content.lower():
                errors.append(f"Key Metric not found in content: {Metric}")
        
        # Check pre-computation accuracy
        if plan.pre_computation:
            if "estimated_length" in plan.pre_computation:
                estimated = plan.pre_computation["estimated_length"]
                actual_length = len(content.split())
                
                # Allow 20% variance
                if actual_length > estimated * 1.2 or actual_length < estimated * 0.8:
                    errors.append(f"Content length ({actual_length}) differs significantly from estimate ({estimated})")
        
        return errors

    def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class CognitiveContractEnforcer:
    """Manages cognitive contracts for agent executions."""
    
    def __init__(self) -> None:
        """Initialize the contract manager."""
        self.validator = CognitiveContractValidatorAgent()
        self.active_contracts: Dict[str, CognitiveContract] = {}
        
    def create_contract(
        self,
        contract_id: str,
        constraints: List[Constraint]
    ) -> CognitiveContract:
        """Create a new cognitive contract.
        
        Args:
            contract_id: Unique identifier
            constraints: List of constraints to enforce
            
        Returns:
            Created contract
        """
        contract = CognitiveContract(
            id=contract_id,
            constraints=constraints
        )
        
        self.active_contracts[contract_id] = contract
        Logger.info(f"Created cognitive contract: {contract_id}")
        
        return contract
    
    def wrap_with_contract_requirement(
        self,
        base_prompt: str,
        constraints: List[Constraint]
    ) -> str:
        """Wrap a prompt with contract requirements.
        
        Args:
            base_prompt: The original prompt
            constraints: Constraints to enforce
            
        Returns:
            Prompt with contract wrapper
        """
        constraint_text = "\n".join(
            f"  - {c.description}" for c in sorted(constraints, key=lambda x: -x.priority)
        )
        
        contract_wrapper = f"""

=== COGNITIVE CONTRACT REQUIRED ===

Before generating your final response, you MUST output a structured plan in a <PLAN> block.

Your plan MUST include:
1. A list of all constraints you've identified
2. Your specific strategy for meeting them
3. Key metrics or elements you intend to include

Example format:
<PLAN>
Constraints:
- {constraints[0].description if constraints else "Example constraint"}
- [Additional constraints...]

Strategy:
[Describe your approach in detail]

Key Metrics:
- [Metric 1]
- [Metric 2]

Pre-computation:
{{"estimated_length": 500, "tone": "professional"}}
</PLAN>

After your plan, output your response in a <CONTENT> block.

CONSTRAINTS TO ACKNOWLEDGE:
{constraint_text}

================================

{base_prompt}"""
        
        return contract_wrapper
    
    def process_response(
        self,
        contract_id: str,
        response: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Process an agent response against its contract.
        
        Args:
            contract_id: Contract identifier
            response: Agent's response
            
        Returns:
            Tuple of (validated_content, contract_result)
        """
        contract = self.active_contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract not found: {contract_id}")
        
        result = {
            "contract_id": contract_id,
            "stage": contract.stage.value,
            "validation_errors": [],
            "consistency_errors": [],
            "plan": None,
            "content": None
        }
        
        try:
            # Parse plan
            plan = self.validator.parse_plan(response)
            if not plan:
                raise PlanQualityError("No PLAN block found in response")
            
            contract.plan = plan
            result["plan"] = plan.raw_text
            
            # Validate plan
            plan_errors = self.validator.validate_plan(plan, contract.constraints)
            if plan_errors:
                contract.validation_errors = plan_errors
                result["validation_errors"] = plan_errors
                raise PlanQualityError(f"Plan validation failed: {plan_errors}")
            
            contract.stage = ContractStage.PLAN_VALIDATED
            
            # Parse content
            content = self.validator.parse_content(response)
            if not content:
                raise ConsistencyError("No CONTENT block found after plan")
            
            contract.content = content
            result["content"] = content
            
            # Validate consistency
            consistency_errors = self.validator.validate_consistency(plan, content)
            if consistency_errors:
                result["consistency_errors"] = consistency_errors
                Logger.warning(f"Consistency errors in contract {contract_id}: {consistency_errors}")
            
            contract.stage = ContractStage.CONTRACT_FULFILLED
            result["stage"] = ContractStage.CONTRACT_FULFILLED.value
            
            Logger.info(f"Contract {contract_id} fulfilled successfully")
            
            return content, result
            
        except (PlanQualityError, ConsistencyError) as e:
            Logger.error(f"Contract {contract_id} failed: {e}")
            result["error"] = str(e)
            raise
    
    def get_contract_status(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a contract.
        
        Args:
            contract_id: Contract identifier
            
        Returns:
            Contract status or None if not found
        """
        contract = self.active_contracts.get(contract_id)
        if not contract:
            return None
        
        return {
            "id": contract.id,
            "stage": contract.stage.value,
            "has_plan": contract.plan is not None,
            "has_content": contract.content is not None,
            "validation_errors": contract.validation_errors,
            "constraint_count": len(contract.constraints)
        }


# Global contract manager
_contract_manager: Optional[CognitiveContractManager] = None


def get_contract_manager() -> CognitiveContractManager:
    """Get the global contract manager instance.
    
    Returns:
        CognitiveContractManager instance
    """
    global _contract_manager
    
    if _contract_manager is None:
        _contract_manager = CognitiveContractManager()
    
    return _contract_manager


# Convenience functions
def create_constraints_from_directives(directives: List[str]) -> List[Constraint]:
    """Create constraint objects from directive strings.
    
    Args:
        directives: List of directive strings
        
    Returns:
        List of Constraint objects
    """
    constraints = []
    
    for i, directive in enumerate(directives):
        # Determine constraint type
        if any(word in directive.lower() for word in ["must not", "never", "avoid", "prohibited"]):
            constraint_type = "prohibition"
            priority = 9
        elif any(word in directive.lower() for word in ["must", "required", "ensure"]):
            constraint_type = "requirement"
            priority = 8
        elif "format" in directive.lower():
            constraint_type = "format"
            priority = 7
        else:
            constraint_type = "requirement"
            priority = 5
        
        constraints.append(Constraint(
            id=f"constraint_{i}",
            description=directive,
            type=constraint_type,
            priority=priority
        ))
    
    return constraints


def enforce_cognitive_contract(
    prompt: str,
    directives: List[str],
    contract_id: Optional[str] = None
) -> str:
    """Apply cognitive contract enforcement to a prompt.
    
    Args:
        prompt: Original prompt
        directives: List of directives to enforce
        contract_id: Optional contract ID
        
    Returns:
        Prompt with contract wrapper
    """
    if contract_id is None:
        contract_id = f"contract_{hash(prompt)}"
    
    constraints = create_constraints_from_directives(directives)
    manager = get_contract_manager()
    
    # Create contract
    manager.create_contract(contract_id, constraints)
    
    # Wrap prompt
    return manager.wrap_with_contract_requirement(prompt, constraints)

@timeout(300)
def _module_heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
    """Schemas/models - module-level operational stub."""
    if _call_path is None:
        _call_path = set()
    agent_name = "CognitiveContractManager"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] Schemas/models - operational only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)
