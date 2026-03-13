"""
apps_rg/shared/tools/text_utils.py - Stateless Text Utilities
"""

import re


def sanitize_campaign_text(text: str) -> str:
    """
    Remove forbidden characters from campaign copy.
    Moved from CampaignPlannerAgent to enforce separation of concerns.
    """
    if not text:
        return ""
    return re.sub("[^\\w\\s-]", "", text).strip()


# guardian: allow-magic-config
def extract_keywords(text: str, max_words: int = 5) -> list[str]:
    """Extract top keywords from text blob."""
    return text.split()[:max_words]
