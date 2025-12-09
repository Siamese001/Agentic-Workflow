# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
"""
Shared configuration constants and constraint classes.

This module contains configuration dataclasses for content constraints,
signal control, and other shared settings.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ContentConstraintsConfig:
    """Centralized configuration for content constraints like word counts."""

    # Overall Resume
    TOTAL_WORD_COUNT_MIN: int = 950
    TOTAL_WORD_COUNT_MAX: int = 1100
    MIN_JD_KEYWORDS: int = 5

    # K.0 Headline
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_MIN_CHARS: int = 60
    HEADLINE_MAX_CHARS: int = 90
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    # K.1 Executive Summary
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 5
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 6
    K1_MIN_DIFFERENTIATORS: int = 3

    # Experience Overviews
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 28
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 44
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 28
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 38
    EY_OVERVIEW_WORD_COUNT_MIN: int = 28
    EY_OVERVIEW_WORD_COUNT_MAX: int = 38
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MIN: int = 21
    EARLY_CAREER_OVERVIEW_WORD_COUNT_MAX: int = 33
    TRADERSENSE_OVERVIEW_WORD_COUNT_MIN: int = 20
    TRADERSENSE_OVERVIEW_WORD_COUNT_MAX: int = 33

    # Word Distribution (Experience)
    UNIFY_IBM_COMBINED_PERCENT_MIN: float = 35.0
    UNIFY_IBM_COMBINED_PERCENT_MAX: float = 45.0
    UNIFY_IBM_RATIO_MIN: float = 1.1
    UNIFY_IBM_RATIO_MAX: float = 1.3

    # K.13 Cover Letter
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 110
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 100
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 130
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 110
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35


@dataclass
class SignalControlConfig:
    """Configuration for signal quality control thresholds."""

    # K.1 Executive Summary
    K1_MAX_DIFFERENTIATORS: int = 4

    # Overall Resume
    RESUME_MAX_JD_KEYWORDS: int = 15

    # K.13 Cover Letter
    CL_MAX_JD_SIMILARITY: float = 0.75

    # QA Report (Section 1)
    SECTION_SIGNAL_SCORE_MAX: float = 0.95


# Default instances
CONTENT_CONSTRAINTS = ContentConstraintsConfig()
SIGNAL_CONTROL = SignalControlConfig()
