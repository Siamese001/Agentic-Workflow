"""
Apps Research Runtime Customization Package Contract

U0-level contract for apps_research runtime customization.
All app-specific configuration enters through this package.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib
import json


class TaskClass(Enum):
    """Supported task classes for apps_research."""
    COMPANY_BRIEF = "company_brief"
    RESEARCH_SUBSTRATE = "research_substrate"
    UPLOADED_BRIEFING_NORMALIZATION = "uploaded_briefing_normalization"


@dataclass(frozen=True)
class RuntimeCustomizationPackage:
    """
    U0 Runtime Customization Package for apps_research.
    
    All apps_research customizations enter through U0 as declarative package refs.
    No runtime authority - only configuration pointers and policy refs.
    """
    # Package identity
    package_id: str
    package_version: str = "1.0.0"
    app_id: str = "apps_research"
    task_class: TaskClass = TaskClass.COMPANY_BRIEF
    
    # Spine profile refs (declarative only)
    spine_profile_ref: str = ""
    route_profile_ref: str = ""
    retrieval_profile_ref: str = ""
    cache_profile_ref: str = ""
    source_mix_policy_ref: str = ""
    freshness_policy_ref: str = ""
    
    # Runtime gate and exit profile refs
    runtime_gate_profile_ref: str = ""
    exit_profile_ref: str = ""
    
    # Judge and eval refs
    judge_profile_ref: str = ""
    grader_roster_ref: str = ""
    eval_rubric_ref: str = ""
    threshold_profile_ref: str = ""
    rubric_output_map_ref: str = ""
    negative_controls_ref: str = ""
    
    # Prompt and output schema refs
    prompt_profile_ref: str = ""
    prompt_bom_ref: str = ""
    output_schema_ref: str = ""
    research_substrate_schema_ref: str = ""
    
    # Learning and meta-feedback refs
    learning_profile_ref: str = ""
    meta_feedback_profile_ref: str = ""
    
    # Policy refs
    briefing_normalization_policy_ref: str = ""
    entity_resolution_policy_ref: str = ""
    capability_profile_ref: str = ""
    provider_profile_ref: str = ""
    
    # Runtime policies
    write_policy: str = "read_only"
    required_runtime_gates: List[str] = field(default_factory=list)
    required_exit_gates: List[str] = field(default_factory=list)
    conditional_exit_gates: List[str] = field(default_factory=list)
    
    # Execution policies
    judge_execution_policy: str = "core_only"
    eval_execution_policy: str = "core_only"
    meta_feedback_policy: str = "l6_only"
    l6_learning_policy: str = "future_run_only"
    
    # Cache policies
    semantic_cache_policy: str = "research_substrate_only"
    cross_app_reuse_policy: str = "delegated_only"
    
    # Package digest (computed)
    package_digest: str = ""
    
    def __post_init__(self):
        """Compute package digest if not provided; normalize task_class to enum."""
        # Normalize task_class to TaskClass enum if passed as string
        if isinstance(self.task_class, str):
            object.__setattr__(self, 'task_class', TaskClass(self.task_class))
        
        if not self.package_digest:
            digest = self._compute_digest()
            object.__setattr__(self, 'package_digest', digest)
    
    def _compute_digest(self) -> str:
        """Compute SHA-256 digest of package contents."""
        # Exclude package_digest from the digest computation
        data = {
            "package_id": self.package_id,
            "package_version": self.package_version,
            "app_id": self.app_id,
            "task_class": self.task_class.value,
            "spine_profile_ref": self.spine_profile_ref,
            "route_profile_ref": self.route_profile_ref,
            "retrieval_profile_ref": self.retrieval_profile_ref,
            "cache_profile_ref": self.cache_profile_ref,
            "source_mix_policy_ref": self.source_mix_policy_ref,
            "freshness_policy_ref": self.freshness_policy_ref,
            "runtime_gate_profile_ref": self.runtime_gate_profile_ref,
            "exit_profile_ref": self.exit_profile_ref,
            "judge_profile_ref": self.judge_profile_ref,
            "grader_roster_ref": self.grader_roster_ref,
            "eval_rubric_ref": self.eval_rubric_ref,
            "threshold_profile_ref": self.threshold_profile_ref,
            "rubric_output_map_ref": self.rubric_output_map_ref,
            "negative_controls_ref": self.negative_controls_ref,
            "prompt_profile_ref": self.prompt_profile_ref,
            "prompt_bom_ref": self.prompt_bom_ref,
            "output_schema_ref": self.output_schema_ref,
            "research_substrate_schema_ref": self.research_substrate_schema_ref,
            "learning_profile_ref": self.learning_profile_ref,
            "meta_feedback_profile_ref": self.meta_feedback_profile_ref,
            "briefing_normalization_policy_ref": self.briefing_normalization_policy_ref,
            "entity_resolution_policy_ref": self.entity_resolution_policy_ref,
            "capability_profile_ref": self.capability_profile_ref,
            "provider_profile_ref": self.provider_profile_ref,
            "write_policy": self.write_policy,
            "required_runtime_gates": sorted(self.required_runtime_gates),
            "required_exit_gates": sorted(self.required_exit_gates),
            "conditional_exit_gates": sorted(self.conditional_exit_gates),
            "judge_execution_policy": self.judge_execution_policy,
            "eval_execution_policy": self.eval_execution_policy,
            "meta_feedback_policy": self.meta_feedback_policy,
            "l6_learning_policy": self.l6_learning_policy,
            "semantic_cache_policy": self.semantic_cache_policy,
            "cross_app_reuse_policy": self.cross_app_reuse_policy,
        }
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    def verify_digest(self) -> bool:
        """Verify package digest matches contents."""
        return self.package_digest == self._compute_digest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "package_id": self.package_id,
            "package_version": self.package_version,
            "app_id": self.app_id,
            "task_class": self.task_class.value,
            "spine_profile_ref": self.spine_profile_ref,
            "route_profile_ref": self.route_profile_ref,
            "retrieval_profile_ref": self.retrieval_profile_ref,
            "cache_profile_ref": self.cache_profile_ref,
            "source_mix_policy_ref": self.source_mix_policy_ref,
            "freshness_policy_ref": self.freshness_policy_ref,
            "runtime_gate_profile_ref": self.runtime_gate_profile_ref,
            "exit_profile_ref": self.exit_profile_ref,
            "judge_profile_ref": self.judge_profile_ref,
            "grader_roster_ref": self.grader_roster_ref,
            "eval_rubric_ref": self.eval_rubric_ref,
            "threshold_profile_ref": self.threshold_profile_ref,
            "rubric_output_map_ref": self.rubric_output_map_ref,
            "negative_controls_ref": self.negative_controls_ref,
            "prompt_profile_ref": self.prompt_profile_ref,
            "prompt_bom_ref": self.prompt_bom_ref,
            "output_schema_ref": self.output_schema_ref,
            "research_substrate_schema_ref": self.research_substrate_schema_ref,
            "learning_profile_ref": self.learning_profile_ref,
            "meta_feedback_profile_ref": self.meta_feedback_profile_ref,
            "briefing_normalization_policy_ref": self.briefing_normalization_policy_ref,
            "entity_resolution_policy_ref": self.entity_resolution_policy_ref,
            "capability_profile_ref": self.capability_profile_ref,
            "provider_profile_ref": self.provider_profile_ref,
            "write_policy": self.write_policy,
            "required_runtime_gates": self.required_runtime_gates,
            "required_exit_gates": self.required_exit_gates,
            "conditional_exit_gates": self.conditional_exit_gates,
            "judge_execution_policy": self.judge_execution_policy,
            "eval_execution_policy": self.eval_execution_policy,
            "meta_feedback_policy": self.meta_feedback_policy,
            "l6_learning_policy": self.l6_learning_policy,
            "semantic_cache_policy": self.semantic_cache_policy,
            "cross_app_reuse_policy": self.cross_app_reuse_policy,
            "package_digest": self.package_digest,
        }


class UnknownPackageFieldError(Exception):
    """Raised when runtime_customization_package contains unknown fields."""
    
    def __init__(self, field: str, message: str = ""):
        self.field = field
        self.message = message or f"Unknown field in runtime customization package: {field}"
        super().__init__(self.message)


class PackageDigestMismatchError(Exception):
    """Raised when package digest verification fails."""
    
    def __init__(self, expected: str, actual: str):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Package digest mismatch: expected {expected[:16]}..., got {actual[:16]}...")


@dataclass(frozen=True)
class PackageValidationReceipt:
    """Receipt produced by U0 package validation."""
    
    package_id: str
    package_version: str
    task_class: str
    validation_passed: bool
    unknown_fields_found: List[str]
    digest_verified: bool
    timestamp_iso: str
    schema_version: str = "AG9.U0.PKG.1"


__all__ = [
    "RuntimeCustomizationPackage",
    "PackageValidationReceipt",
    "TaskClass",
    "UnknownPackageFieldError",
    "PackageDigestMismatchError",
]
