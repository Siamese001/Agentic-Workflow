#!/usr/bin/env python3
"""
Text Cleaning Tool
Section 5: Tool Contracts - Retrieval tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class TextCleaningTool:
    """Normalize and sanitize text for processing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.remove_html = self.config.get("remove_html", True)
        self.normalize_whitespace = self.config.get("normalize_whitespace", True)
        self.lowercase = self.config.get("lowercase", False)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        try:
            cleaned = text
            
            if self.remove_html:
                cleaned = self._remove_html(cleaned)
            
            if self.normalize_whitespace:
                cleaned = self._normalize_whitespace(cleaned)
            
            if self.lowercase:
                cleaned = cleaned.lower()
            
            return cleaned.strip()
            
        except Exception as e:
            logger.error(f"Text cleaning failed: {e}")
            return text
    
    def _remove_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        import re
        return re.sub(r'<[^>]+>', '', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        import re
        return re.sub(r'\s+', ' ', text)
    
    def batch_clean(self, texts: List[str]) -> List[str]:
        """Clean multiple texts"""
        return [self.clean_text(text) for text in texts]

def create_text_cleaning_tool(config: Optional[Dict[str, Any]] = None) -> TextCleaningTool:
    """Factory function to create text cleaning tool instance"""
    return TextCleaningTool(config)

# Re-export components
__all__ = [
    'TextCleaningTool', 'create_text_cleaning_tool'
]





