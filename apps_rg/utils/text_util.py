"""
apps_rg/shared/tools/text_utils.py - Stateless Text Utilities
"""

import re


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def sanitize_campaign_text(text: str) -> str:
    """
    Remove forbidden characters from campaign copy.
    Moved from CampaignPlannerAgent to enforce separation of concerns.
    """
    if not text:
        return ""
    # Basic sanitization logic
    return re.sub(r"[^\w\s-]", "", text).strip()


def extract_keywords(text: str, max_words: int = 5) -> list[str]:
    """Extract top keywords from text blob."""
    return text.split()[:max_words]
