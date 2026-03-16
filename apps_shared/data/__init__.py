from __future__ import annotations

from apps_shared.config.pipeline_constants_config import MAX_RETRIES  # noqa: F401
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Shared data files for Agentic Workflow.

Contains:
- master_resume.json: Sender profile data
- sender_knowledge_base.json: Grounding facts for validation

Migrated from archives/Reachout Engine Archive/Agentic LIC/
Date: 2026-01-01
"""
