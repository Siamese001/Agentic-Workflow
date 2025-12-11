# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
"""
Reasoning configuration utilities.

function functions for converting ReasoningConfig to API parameters.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""

from __future__ import annotations

from typing import Dict, Tuple

from shared.reasoning_config import ReasoningConfig
from shared.reasoning_prompt import build_reasoning_prompt_addendum


def reasoning_config_to_api_params(reasoning_config: ReasoningConfig) -> dict:
    """Convert reasoning config to Gemini API parameters."""
    params = _get_normalized_reasoning_params(reasoning_config)
    intensity, level = _calculate_reasoning_intensity(params)
    params["intensity_score"] = intensity
    params["reasoning_level"] = level

    temperature = _get_generation_temperature()
    max_tokens = _allocate_tokens_from_depth(params["tot_d"], params["cot"], params["sc"])
    prompt_addendum = build_reasoning_prompt_addendum(params)

    return {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
        "system_prompt_addendum": prompt_addendum,
        **params,
    }


def _get_normalized_reasoning_params(config: ReasoningConfig) -> Dict:
    """Handle defaults and clamp reasoning config values."""
    config = config or ReasoningConfig.DEFAULT
    return {
        "cot": max(2, min(config.cot_min_paths or 3, 8)),
        "tot_b": max(2, min(config.tot_branches or 3, 6)),
        "tot_d": max(2, min(config.min_tot_depth or 3, 5)),
        "sc": max(1, min(config.self_consistency or 12, 30)),
        "reflexion": config.reflexion if config.reflexion is not None else True,
        "max_loops": max(1, min(config.max_reflexion_loops or 2, 5)),
    }


def _calculate_reasoning_intensity(params: Dict) -> Tuple[float, str]:
    """Calculate intensity score and qualitative level from parameters."""
    intensity = (params["cot"] * 2.0) + (params["tot_b"] * 2.0) + (params["tot_d"] * 2.0) + (params["sc"] / 5.0)

    if intensity >= 35:
        level = "VERY_HIGH"
    elif intensity >= 25:
        level = "HIGH"
    elif intensity >= 15:
        level = "MODERATE"
    elif intensity >= 8:
        level = "LOW"
    else:
        level = "MINIMAL"

    return intensity, level


def _get_generation_temperature() -> float:
    """Get generation temperature optimized for creativity."""
    return 0.9


def _allocate_tokens_from_depth(tot_d: int, cot: int, sc: int) -> int:
    """Allocate max_tokens based on reasoning depth and complexity."""
    if tot_d >= 4:
        max_tokens = 2500
    elif tot_d >= 3 and cot >= 5:
        max_tokens = 2700
    elif tot_d >= 3 or cot >= 5:
        max_tokens = 2600
    elif sc >= 15:
        max_tokens = 2500
    else:
        max_tokens = 1200
    return max(1200, min(max_tokens, 14000))


def enhance_system_prompt_with_reasoning(
    base_system_prompt: str,
    reasoning_config: ReasoningConfig,
    section_id: str = "UNKNOWN",
) -> str:
    """Enhance a system prompt with reasoning configuration directives."""
    api_params = reasoning_config_to_api_params(reasoning_config)
    return base_system_prompt + api_params["system_prompt_addendum"]
