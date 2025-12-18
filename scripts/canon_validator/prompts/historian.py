"""
Historian memory recall few-shot patterns.
Used by Historian agent for memory-based fixes.
"""

FEW_SHOT_HISTORIAN = """
FEW-SHOT MEMORY RECALL USAGE (Historian):

EXAMPLE 1: Past Fix Recall
MEMORY: File apps/utils.py had SYNTAX_ERROR fixed by adding missing colon
Current: Same file, same error
GOOD: Apply exact same fix — do not reinvent

EXAMPLE 2: Failed Strategy
MEMORY: Inline extraction caused TEST_FAILURE → rolled back
Current: Similar monolith
GOOD: Try split-into-files instead

Always check recalled memories first.
"""
