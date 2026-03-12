"""CONSOLIDATED: HOP6ValidationAgent → HOPPipelineExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""
from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor as HOP6ValidationAgent
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
__all__ = ['HOP6ValidationAgent']
