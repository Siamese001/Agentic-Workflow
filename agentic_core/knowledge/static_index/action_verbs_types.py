"""
Action Verbs Taxonomy - High-Impact Resume/Outreach Verbs

Zero-Ambiguity Standard: Named with _types.py suffix
Category: TYPES (Static knowledge taxonomy)

Provides categorized action verbs for professional content generation.
"""

from typing import Final

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Action verbs categorized by impact domain
ACTION_VERBS: Final[dict[str, list[str]]] = {
    "Engineering": [
        "Architected",
        "Built",
        "Designed",
        "Developed",
        "Engineered",
        "Implemented",
        "Optimized",
        "Refactored",
        "Scaled",
        "Automated",
    ],
    "Leadership": [
        "Led",
        "Directed",
        "Managed",
        "Mentored",
        "Coached",
        "Supervised",
        "Coordinated",
        "Orchestrated",
        "Spearheaded",
        "Championed",
    ],
    "Analysis": [
        "Analyzed",
        "Assessed",
        "Evaluated",
        "Investigated",
        "Researched",
        "Diagnosed",
        "Identified",
        "Discovered",
        "Uncovered",
        "Quantified",
    ],
    "Communication": [
        "Presented",
        "Communicated",
        "Articulated",
        "Documented",
        "Published",
        "Reported",
        "Briefed",
        "Advocated",
        "Negotiated",
        "Collaborated",
    ],
    "Innovation": [
        "Pioneered",
        "Innovated",
        "Transformed",
        "Revolutionized",
        "Modernized",
        "Introduced",
        "Launched",
        "Created",
        "Invented",
        "Conceptualized",
    ],
    "Execution": [
        "Delivered",
        "Executed",
        "Completed",
        "Achieved",
        "Accomplished",
        "Fulfilled",
        "Realized",
        "Attained",
        "Succeeded",
        "Finalized",
    ],
    "Improvement": [
        "Improved",
        "Enhanced",
        "Streamlined",
        "Accelerated",
        "Reduced",
        "Increased",
        "Boosted",
        "Elevated",
        "Strengthened",
        "Upgraded",
    ],
}

# High-impact opener verbs (strongest first)
STRONG_VERBS: Final[list[str]] = [
    "Spearheaded",
    "Pioneered",
    "Architected",
    "Transformed",
    "Revolutionized",
    "Orchestrated",
    "Championed",
    "Engineered",
    "Delivered",
    "Scaled",
    "Accelerated",
    "Innovated",
    "Led",
    "Built",
    "Designed",
]
