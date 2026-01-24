"""
apps_rg/shared/tools/text_utils.py - Stateless Text Utilities
"""
from typing import List
import re

def sanitize_campaign_text(text: str) -> str:
    """
    Remove forbidden characters from campaign copy.
    Moved from CampaignPlannerAgent to enforce separation of concerns.
    """
    if not text:
        return ""
    # Basic sanitization logic
    return re.sub(r'[^\w\s-]', '', text).strip()

def extract_keywords(text: str, max_words: int = 5) -> List[str]:
    """Extract top keywords from text blob."""
    return text.split()[:max_words]
