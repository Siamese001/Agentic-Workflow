import logging

_logger = logging.getLogger(__name__)
# -*- coding: utf-8 -*-
"""
08_scripts.cache_ops — Package initialization

This module provides caching utilities and data access caching for the Agentic-Workflow system.
It includes components for:
- Data access caching with intelligent invalidation
- Cache key generation and management
- Cache warming and preloading strategies
- Distributed cache coordination
- Cache performance monitoring and metrics

The caching system is designed to improve performance by reducing redundant data access
operations and providing fast retrieval of frequently used data.

Auto-generated to satisfy SSoT structure requirements.
"""


__version__ = "1.0.0"
__author__ = "Agentic-Workflow Team"

__all__: list = [
    "get_info",
    "get_info_request",
    "get_info_embedding",
]
