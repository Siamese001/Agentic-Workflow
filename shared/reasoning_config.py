# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
"""
Reasoning configuration for LLM generation.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Optional


@dataclass
class ReasoningConfig:
    """Centralized reasoning configuration for LLM generation."""

    cot_min_paths: int = 3
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 6
    reflexion: bool = True
    max_reflexion_loops: int = 2

    # Section-specific configurations (ClassVars set after class definition)
    K0_HEADLINE_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K1_EXECUTIVE_SUMMARY_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K5_UNIFY_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K5_UNIFY_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K6_IBM_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K6_IBM_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K8_EY_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K8_EY_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K9_EARLY_CAREER_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K9_EARLY_CAREER_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K2_SKILLS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    K10_COMPETENCIES_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    DEFAULT: ClassVar[Optional[ReasoningConfig]] = None


# Initialize default config
ReasoningConfig.DEFAULT = ReasoningConfig()

# Section-specific configurations
_REASONING_CONFIGS = [
    ("K0_HEADLINE_CONFIG", {"cot_min_paths": 4, "tot_branches": 3, "min_tot_depth": 2, "self_consistency": 6, "reflexion": True}),
    ("K1_EXECUTIVE_SUMMARY_CONFIG", {"cot_min_paths": 3, "tot_branches": 3, "min_tot_depth": 3, "self_consistency": 12, "reflexion": True, "max_reflexion_loops": 2}),
    ("K5_UNIFY_BULLETS_CONFIG", {"cot_min_paths": 4, "tot_branches": 3, "min_tot_depth": 3, "self_consistency": 12, "reflexion": True}),
    ("K5_UNIFY_OVERVIEW_CONFIG", None),
    ("K6_IBM_BULLETS_CONFIG", {"cot_min_paths": 4, "tot_branches": 3, "min_tot_depth": 3, "self_consistency": 12, "reflexion": True}),
    ("K6_IBM_OVERVIEW_CONFIG", {"cot_min_paths": 2, "tot_branches": 2, "min_tot_depth": 2, "self_consistency": 4, "reflexion": False}),
    ("K8_EY_BULLETS_CONFIG", {"cot_min_paths": 2, "tot_branches": 2, "min_tot_depth": 2, "self_consistency": 4, "reflexion": False}),
    ("K8_EY_OVERVIEW_CONFIG", {"cot_min_paths": 2, "tot_branches": 2, "min_tot_depth": 2, "self_consistency": 4, "reflexion": False}),
    ("K9_EARLY_CAREER_BULLETS_CONFIG", {"cot_min_paths": 2, "tot_branches": 2, "min_tot_depth": 2, "self_consistency": 4, "reflexion": False}),
    ("K9_EARLY_CAREER_OVERVIEW_CONFIG", {"cot_min_paths": 2, "tot_branches": 2, "min_tot_depth": 2, "self_consistency": 4, "reflexion": False}),
    ("K2_SKILLS_CONFIG", {"cot_min_paths": 2, "tot_branches": 2, "min_tot_depth": 2, "self_consistency": 4, "reflexion": False}),
    ("K10_COMPETENCIES_CONFIG", {"cot_min_paths": 3, "tot_branches": 3, "min_tot_depth": 2, "self_consistency": 10, "reflexion": True}),
]

for _name, _cfg in _REASONING_CONFIGS:
    if _cfg is None:
        setattr(ReasoningConfig, _name, ReasoningConfig.DEFAULT)
    else:
        setattr(ReasoningConfig, _name, ReasoningConfig(**_cfg))
