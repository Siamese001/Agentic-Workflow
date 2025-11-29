#!/usr/bin/env python3
"""
Resume Engine Application Layer
Thin application wrapper for resume generation workflows
"""

from .adapters.resume_adapter import ResumeAdapter
from .pipelines.resume_pipeline import ResumePipeline

__all__ = ['ResumeAdapter', 'ResumePipeline']





