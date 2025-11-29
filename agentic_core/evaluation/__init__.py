#!/usr/bin/env python3
"""
Evaluation Framework
Section 17: Evaluation Framework - Golden datasets, LLM-as-Judge
"""

from .golden_datasets import GoldenDatasetManager, GoldenDataset, DatasetType
from .llm_judge import LLMJudge, EvaluationResult, JudgmentType

__all__ = [
    'GoldenDatasetManager', 'GoldenDataset', 'DatasetType',
    'LLMJudge', 'EvaluationResult', 'JudgmentType'
]
