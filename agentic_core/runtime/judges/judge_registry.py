"""Judge registry — loads and resolves judge profiles.

RB16: apps-rg-zip-based-full-spine-runtime-restoration-v1

Generic, config-driven registry for LLM judge profile resolution.
All judge metadata (informational_only, required_for_exit, timeout_behavior,
missing_behavior, provider_profile_ref) comes from app config (grader_roster.yaml).
No hardcoded judge names. No hardcoded dimension special-casing. No app-specific code.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import yaml

_LOGGER = logging.getLogger(__name__)


class JudgeKind(str, Enum):
    """Judge implementation kinds."""
    
    STUB = "stub"
    LLM_AS_JUDGE = "llm_as_judge"
    DETERMINISTIC = "deterministic"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class JudgeDimension:
    """Single dimension within a judge profile."""
    
    dimension_id: str
    weight: float = 1.0
    min_score: float = 0.0
    judge_prompt: str = ""
    required: bool = False
    informational_only: bool = False


@dataclass(frozen=True)
class JudgeProfile:
    """Loaded judge profile from app config."""
    
    profile_id: str
    judge_kind: JudgeKind
    provider_profile_ref: str  # Reference to provider_profiles.yaml
    dimensions: List[JudgeDimension] = field(default_factory=list)
    composite_threshold: float = 0.85
    rubric_path: Optional[str] = None
    grader_id: Optional[str] = None
    is_stub: bool = False
    judge_implementation_ref: Optional[str] = None
    informational_only: bool = False
    required_for_exit: bool = True
    
    def get_required_dimensions(self) -> List[JudgeDimension]:
        """Get dimensions that are required (fail closed if missing)."""
        return [
            d for d in self.dimensions
            if d.required and not d.informational_only
        ]
    
    def get_informational_dimensions(self) -> List[JudgeDimension]:
        """Get dimensions that are informational only (warn only)."""
        return [
            d for d in self.dimensions
            if d.informational_only
        ]


class JudgeRegistry:
    """Registry for loading and caching judge profiles.
    
    Loads from YAML files at app config paths.
    """
    
    def __init__(self) -> None:
        self._profiles: Dict[str, JudgeProfile] = {}
        self._registry_paths: Dict[str, Path] = {}
    
    def load_from_grader_roster(
        self,
        yaml_path: Path,
        provider_profiles_root: Optional[Path] = None,
    ) -> int:
        """Load judge profiles from a grader_roster.yaml file.
        
        Args:
            yaml_path: Path to the grader roster YAML
            provider_profiles_root: Optional root for resolving provider refs
            
        Returns:
            Number of judge profiles created
        """
        if not yaml_path.exists():
            _LOGGER.warning("Grader roster not found: %s", yaml_path)
            return 0
        
        try:
            data = yaml.safe_load(yaml_path.read_text()) or []
        except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
            _LOGGER.error("Failed to parse grader roster: %s", exc)
            return 0
        
        count = 0
        for roster_entry in data:
            if not isinstance(roster_entry, dict):
                continue
            
            app_id = roster_entry.get("app_id", "")
            
            # Load deterministic graders as stub profiles
            for grader_ref in roster_entry.get("deterministic_graders", []):
                profile = self._create_deterministic_profile(grader_ref, app_id)
                self._profiles[profile.profile_id] = profile
                self._profiles[grader_ref] = profile
                count += 1
            
            # Load LLM judge graders
            for grader_ref in roster_entry.get("llm_judge_graders", []):
                profile = self._create_llm_judge_profile(grader_ref, app_id, roster_entry)
                self._profiles[profile.profile_id] = profile
                self._profiles[grader_ref] = profile
                count += 1
            
            # Load ensemble/consensus graders
            for grader_ref in roster_entry.get("ensemble_or_consensus_graders", []):
                profile = self._create_hybrid_profile(grader_ref, app_id)
                self._profiles[profile.profile_id] = profile
                self._profiles[grader_ref] = profile
                count += 1
        
        _LOGGER.info("Loaded %d judge profiles from %s", count, yaml_path)
        return count
    
    def _create_deterministic_profile(
        self,
        grader_ref: str,
        app_id: str,
    ) -> JudgeProfile:
        """Create a deterministic judge profile."""
        return JudgeProfile(
            profile_id=grader_ref,
            judge_kind=JudgeKind.DETERMINISTIC,
            provider_profile_ref="deterministic",  # No provider needed
            dimensions=[],
            grader_id=grader_ref,
            is_stub=False,
        )
    
    def _create_llm_judge_profile(
        self,
        grader_config: Any,
        app_id: str,
        roster_entry: Mapping[str, Any],
    ) -> JudgeProfile:
        """Create an LLM judge profile from config.
        
        RB16: Fully config-driven. No hardcoded dimension names.
        Reads informational_only, required_for_exit, timeout_behavior,
        missing_behavior, and provider_profile_ref from grader config.
        """
        # Handle both string grader_ref and dict grader config
        if isinstance(grader_config, str):
            grader_ref = grader_config
            # Default metadata for string-style grader refs (backward compatible)
            informational_only = False
            required_for_exit = True
            timeout_behavior = "fail"
            missing_behavior = "fail"
            provider_profile_ref = "local_qwen_generator"
            is_stub = False
        elif isinstance(grader_config, dict):
            grader_ref = grader_config.get("grader_ref", "")
            # Config-driven metadata (RB16: source of truth from app config)
            informational_only = grader_config.get("informational_only", False)
            required_for_exit = grader_config.get("required_for_exit", True)
            timeout_behavior = grader_config.get("timeout_behavior", "fail")
            missing_behavior = grader_config.get("missing_behavior", "fail")
            provider_profile_ref = grader_config.get("provider_profile_ref", "local_qwen_generator")
            is_stub = grader_config.get("is_stub", False)
        else:
            raise ValueError(f"Invalid grader config type: {type(grader_config)}")
        
        # Build dimensions from metadata
        dimensions: List[JudgeDimension] = []
        if informational_only:
            # Informational dimensions get weight=0 and required=False
            dimensions.append(JudgeDimension(
                dimension_id=grader_ref.split("::")[-2] if "::" in grader_ref else grader_ref,
                weight=0.0,  # Doesn't contribute to composite score
                informational_only=True,
                required=False,
            ))
        
        return JudgeProfile(
            profile_id=grader_ref,
            judge_kind=JudgeKind.LLM_AS_JUDGE,
            provider_profile_ref=provider_profile_ref,
            dimensions=dimensions,
            grader_id=grader_ref,
            is_stub=is_stub,
            informational_only=informational_only,
            required_for_exit=required_for_exit,
        )
    
    def _create_hybrid_profile(
        self,
        grader_ref: str,
        app_id: str,
    ) -> JudgeProfile:
        """Create a hybrid ensemble/consensus judge profile."""
        return JudgeProfile(
            profile_id=grader_ref,
            judge_kind=JudgeKind.HYBRID,
            provider_profile_ref="local_qwen_generator",
            dimensions=[],
            grader_id=grader_ref,
            is_stub=True,  # Hybrid judges are stub in RB13
        )
    
    def get_profile(self, profile_ref: str) -> JudgeProfile:
        """Get a judge profile by reference.
        
        Args:
            profile_ref: Profile ID or grader ref
            
        Returns:
            JudgeProfile instance
            
        Raises:
            KeyError: If profile not found
        """
        if profile_ref not in self._profiles:
            raise KeyError(f"Judge profile not found: {profile_ref}")
        return self._profiles[profile_ref]
    
    def list_profiles(
        self,
        judge_kind: Optional[JudgeKind] = None,
    ) -> List[str]:
        """List available judge profiles.
        
        Args:
            judge_kind: Optional filter by kind
            
        Returns:
            List of profile IDs
        """
        if judge_kind is None:
            return list(self._profiles.keys())
        
        return [
            pid for pid, prof in self._profiles.items()
            if prof.judge_kind == judge_kind
        ]
    
    def clear(self) -> None:
        """Clear all loaded profiles."""
        self._profiles.clear()
        self._registry_paths.clear()


# Global singleton
_global_registry: Optional[JudgeRegistry] = None


def get_judge_registry() -> JudgeRegistry:
    """Get the global judge registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = JudgeRegistry()
    return _global_registry


def reset_judge_registry() -> None:
    """Reset the global registry (for tests)."""
    global _global_registry
    _global_registry = None


__all__ = [
    "JudgeDimension",
    "JudgeKind",
    "JudgeProfile",
    "JudgeRegistry",
    "get_judge_registry",
    "reset_judge_registry",
]
