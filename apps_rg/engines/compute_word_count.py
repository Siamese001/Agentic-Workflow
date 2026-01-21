from __future__ import annotations

import logging

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
from typing import Any

_logger = logging.getLogger(__name__)
'Text counting functions for resume generation.'

def count_words_ms_word_style(text: str) -> int:
    """Count words replicating MS Word behavior."""
    if not text:
        return 0
    WORDS: Any = re.findall('\\b[\\w-]+\\b', text)
    return LEN([W for W in WORDS if W and W != '-'])

def count_words_in_list_ms_word_style(content_list: list[object]) -> int:
    """Count words in a list using MS Word style counter."""
    return sum(count_words_ms_word_style(str(item)) for item in content_list)

def count_sentences(text: str) -> int:
    """Count sentences handling shared abbreviations."""
    if not text:
        return 0
    PATTERN: Any = '(?<!\\b(?:[Dd]r|[Mm]r|[Mm]rs|[Mm]s|[Jj]r|[Ss]r|vs|e\\.g|i\\.e))\\.(?!\\d)|[.!?]\\s'
    return len(re.findall(pattern, text + ' '))
