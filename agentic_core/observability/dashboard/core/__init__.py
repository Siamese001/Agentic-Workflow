"""
Dashboard Core Components

This module contains the core dashboard generation logic:
- DashboardDataGenerator: Computes metrics and builds dashboard data
- DashboardRenderer: Renders HTML from templates and data

Moved from agentic_core.L5_safety.validators to correct observability layer.
"""
from .data_generator import DashboardDataGenerator
from .renderer import DashboardRenderer

__all__ = ['DashboardDataGenerator', 'DashboardRenderer']
