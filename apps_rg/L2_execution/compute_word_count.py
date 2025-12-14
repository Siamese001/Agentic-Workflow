
# Ownership: apps_rg / L2_execution
# -*- coding: utf-8 -*-
"""Text counting functions for resume generation."""

from typing import List

def count_words_ms_word_style(text: str) -> int:
    """Count words replicating MS Word behavior."""
    if not text:
        return 0
    words = re.findall(r"\b[\w-]+\b", text)
    return len([w for w in words if w and w != "-"])

def count_words_in_list_ms_word_style(content_list: List[object]) -> int:
    """Count words in a list using MS Word style counter."""
    return sum(count_words_ms_word_style(str(item)) for item in content_list)

def count_sentences(text: str) -> int:
    """Count sentences handling shared abbreviations."""
    if not text:
        return 0
    pattern = r"(?<!\b(?:[Dd]r|[Mm]r|[Mm]rs|[Mm]s|[Jj]r|[Ss]r|vs|e\.g|i\.e))\.(?!\d)|[.!?]\s"
    return len(re.findall(pattern, text + " "))
