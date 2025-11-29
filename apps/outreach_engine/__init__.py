#!/usr/bin/env python3
"""
Outreach Engine Application Layer
Thin application wrapper for outreach generation workflows
"""

from .adapters.outreach_adapter import OutreachAdapter
from .pipelines.outreach_pipeline import OutreachPipeline

__all__ = ['OutreachAdapter', 'OutreachPipeline']





