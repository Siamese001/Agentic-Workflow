"""
Diff Generator tool for L2 Execution.

Provides diff generation utilities.
"""
from typing import List, Optional
import difflib
import logging

logger = logging.getLogger(__name__)


class DiffGenerator:
    """Tool for generating diffs between code versions."""
    
    def __init__(self):
        pass
    
    def unified_diff(self, old: str, new: str, old_name: str = "old", new_name: str = "new") -> str:
        """Generate a unified diff between two strings."""
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        diff = difflib.unified_diff(old_lines, new_lines, fromfile=old_name, tofile=new_name)
        return ''.join(diff)
    
    def context_diff(self, old: str, new: str, old_name: str = "old", new_name: str = "new") -> str:
        """Generate a context diff between two strings."""
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        diff = difflib.context_diff(old_lines, new_lines, fromfile=old_name, tofile=new_name)
        return ''.join(diff)
    
    def html_diff(self, old: str, new: str) -> str:
        """Generate an HTML diff between two strings."""
        differ = difflib.HtmlDiff()
        return differ.make_file(old.splitlines(), new.splitlines())
    
    def get_changes(self, old: str, new: str) -> List[dict]:
        """Get a list of changes between two strings."""
        old_lines = old.splitlines()
        new_lines = new.splitlines()
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        
        changes = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                changes.append({
                    'type': tag,
                    'old_start': i1,
                    'old_end': i2,
                    'new_start': j1,
                    'new_end': j2,
                    'old_lines': old_lines[i1:i2],
                    'new_lines': new_lines[j1:j2]
                })
        return changes


__all__ = ['DiffGenerator']
