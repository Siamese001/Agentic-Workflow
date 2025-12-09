# -*- coding: utf-8 -*-
"""
Semantic Cache Operations for L4_memory/P1_retrieve.

This module provides semantic cache functionality for memory retrieval operations,
including index loading, history matching, and distance computation.

Required by SSoT v4.1 semantic_cache_rules.
"""

from .load_semantic_cache_index import *
from .match_semantic_history import *
from .compute_semantic_distance import *

__all__ = [
    "load_semantic_cache_index",
    "match_semantic_history",
    "compute_semantic_distance",
]
