"""W9 Boundary Hardening — Package-Driven Judge Runner (Core-Owned)

Core judge execution infrastructure that loads app-specific judge configs
from U0 runtime customization packages.

W9 Boundary Principle:
- Core owns judge execution (this module)
- Apps own judge config (rubrics, profiles, grader roster)
- No executable judge logic in apps_research/engines/judges/
"""
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from agentic_core.evaluation.judges.deterministic_graders import (
    DeterministicGraderRegistry,
    DeterministicGradeResult,
)
from agentic_core.evaluation.judges.gate_evidence_mapper import (
    GateEvidenceMapper,
    GateEvidence,
)


@dataclass(frozen=True)
class JudgeProfile:
    """App-specific judge configuration.
    
    Loaded from apps_research/config/domain_contract/judge_profile.*.yaml
    """
    profile_id: str
    dimensions: Tuple[str, ...]
    grader_roster_path: Optional[str] = None
    rubric_paths: Tuple[str, ...] = ()
    calibration_fixtures: Tuple[str, ...] = ()


@dataclass(frozen=True)
class JudgeRunResult:
    """Result from running judges on content."""
    profile_id: str
    dimensions_evaluated: Tuple[str, ...]
    gate_evidence: Tuple[GateEvidence, ...]
    overall_pass: bool
    any_fail: bool
    any_warn: bool


class PackageDrivenJudgeRunner:
    """Core judge runner that loads app configs from U0 package.
    
    Boundary: Core owns execution. App owns config via U0 package.
    """
    
    def __init__(self, judge_profile: JudgeProfile):
        """Initialize with app-specific judge profile.
        
        Args:
            judge_profile: Loaded from app's U0 runtime customization package
        """
        self._profile = judge_profile
    
    def run_deterministic_graders(
        self,
        content: str,
        context: Dict[str, Any],
        dimensions: Optional[List[str]] = None
    ) -> JudgeRunResult:
        """Run deterministic graders for configured dimensions.
        
        Args:
            content: The content to evaluate (e.g., company brief)
            context: Evaluation context (target_downstream, etc.)
            dimensions: Specific dimensions to run (defaults to profile.dimensions)
            
        Returns:
            JudgeRunResult with gate evidence for all dimensions
        """
        dims_to_run = dimensions or list(self._profile.dimensions)
        gate_evidence_list = []
        any_fail = False
        any_warn = False
        
        for dimension in dims_to_run:
            # Core-owned execution: grade via deterministic registry
            grade_result = DeterministicGraderRegistry.grade(
                dimension, content, context
            )
            
            # Core-owned mapping: grade result -> gate evidence
            gate_evidence = GateEvidenceMapper.map_grade_result(
                grade_result, dimension
            )
            gate_evidence_list.append(gate_evidence)
            
            # Track results
            if gate_evidence.result == "FAIL":
                any_fail = True
            elif gate_evidence.result == "WARN":
                any_warn = True
        
        overall_pass = not any_fail
        
        return JudgeRunResult(
            profile_id=self._profile.profile_id,
            dimensions_evaluated=tuple(dims_to_run),
            gate_evidence=tuple(gate_evidence_list),
            overall_pass=overall_pass,
            any_fail=any_fail,
            any_warn=any_warn,
        )
    
    @property
    def profile(self) -> JudgeProfile:
        """Access the loaded judge profile (app config)."""
        return self._profile


# ─────────────────────────────────────────────────────────────────────────────
# Factory: Load Runner from U0 Package
# ─────────────────────────────────────────────────────────────────────────────

def load_judge_runner_from_u0_package(
    u0_package: Dict[str, Any],
    profile_key: str = "judge_profile"
) -> PackageDrivenJudgeRunner:
    """Create a judge runner from U0 runtime customization package.
    
    Args:
        u0_package: The resolved U0 package dict
        profile_key: Key for judge profile in package
        
    Returns:
        PackageDrivenJudgeRunner configured from app U0 package
    """
    profile_data = u0_package.get(profile_key, {})
    
    profile = JudgeProfile(
        profile_id=profile_data.get("profile_id", "unknown"),
        dimensions=tuple(profile_data.get("dimensions", [])),
        grader_roster_path=profile_data.get("grader_roster_path"),
        rubric_paths=tuple(profile_data.get("rubric_paths", [])),
        calibration_fixtures=tuple(profile_data.get("calibration_fixtures", [])),
    )
    
    return PackageDrivenJudgeRunner(profile)
