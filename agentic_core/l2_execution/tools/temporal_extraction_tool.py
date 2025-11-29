#!/usr/bin/env python3
"""
Temporal Extraction Tool
Section 5: Tool Contracts - TEMPORAL tool family
"""

from typing import Dict, Any, List, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class TemporalExtractionTool:
    """Extract temporal spans/events from text"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.date_formats = self.config.get("date_formats", ["%Y-%m", "%Y", "%B %Y"])
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
    
    def extract_temporal_spans(self, text: str) -> List[Dict[str, Any]]:
        """Extract temporal spans from text"""
        try:
            # Find date patterns
            date_patterns = [
                r'\b\d{4}\b',  # Years
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',  # Month Year
                r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',  # Abbreviated Month Year
                r'\b\d{4}-\d{2}\b',  # YYYY-MM format
                r'\b(from|since|until|to)\s+\d{4}\b',  # Temporal prepositions with year
            ]
            
            temporal_spans = []
            
            for pattern in date_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    span_text = match.group()
                    span_info = self._analyze_temporal_span(span_text, text, match.start(), match.end())
                    if span_info and span_info["confidence"] >= self.confidence_threshold:
                        temporal_spans.append(span_info)
            
            logger.info(f"Extracted {len(temporal_spans)} temporal spans")
            return temporal_spans
            
        except Exception as e:
            logger.error(f"Temporal span extraction failed: {e}")
            return []
    
    def extract_events(self, text: str) -> List[Dict[str, Any]]:
        """Extract temporal events from text"""
        try:
            # Event keywords
            event_keywords = [
                "graduated", "promoted", "hired", "started", "finished", "completed",
                "certified", "awarded", "published", "launched", "joined", "left"
            ]
            
            events = []
            
            for keyword in event_keywords:
                pattern = rf'\b{keyword}\b.*?(\d{{4}}|\b\d{{4}}-\d{{2}}\b)'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    event_text = match.group().strip()
                    event_info = self._analyze_event(event_text, keyword)
                    if event_info:
                        events.append(event_info)
            
            logger.info(f"Extracted {len(events)} temporal events")
            return events
            
        except Exception as e:
            logger.error(f"Event extraction failed: {e}")
            return []
    
    def _analyze_temporal_span(self, span_text: str, context: str, start: int, end: int) -> Optional[Dict[str, Any]]:
        """Analyze temporal span and extract structured information"""
        try:
            # Extract year
            year_match = re.search(r'\b\d{4}\b', span_text)
            if not year_match:
                return None
            
            year = int(year_match.group())
            current_year = datetime.now().year
            
            # Determine span type
            span_type = "year"
            if "from" in span_text.lower() or "to" in span_text.lower():
                span_type = "range"
            elif re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)', span_text, re.IGNORECASE):
                span_type = "month_year"
            
            # Calculate confidence
            confidence = 0.8 if span_type == "year" else 0.9
            
            # Extract entity context (words around the temporal span)
            context_start = max(0, start - 50)
            context_end = min(len(context), end + 50)
            entity_context = context[context_start:context_end].strip()
            
            return {
                "text": span_text,
                "type": span_type,
                "year": year,
                "confidence": confidence,
                "context": entity_context,
                "position": {"start": start, "end": end}
            }
            
        except Exception as e:
            logger.error(f"Temporal span analysis failed: {e}")
            return None
    
    def _analyze_event(self, event_text: str, keyword: str) -> Optional[Dict[str, Any]]:
        """Analyze temporal event"""
        try:
            # Extract date from event
            date_match = re.search(r'\b\d{4}\b', event_text)
            if not date_match:
                return None
            
            year = int(date_match.group())
            
            # Determine event type based on keyword
            event_type_mapping = {
                "graduated": "education",
                "promoted": "career",
                "hired": "career",
                "started": "career",
                "finished": "project",
                "completed": "project",
                "certified": "skill",
                "awarded": "achievement",
                "published": "achievement",
                "launched": "project",
                "joined": "career",
                "left": "career"
            }
            
            event_type = event_type_mapping.get(keyword, "general")
            
            return {
                "text": event_text,
                "type": event_type,
                "keyword": keyword,
                "year": year,
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Event analysis failed: {e}")
            return None

def create_temporal_extraction_tool(config: Optional[Dict[str, Any]] = None) -> TemporalExtractionTool:
    """Factory function to create temporal extraction tool instance"""
    return TemporalExtractionTool(config)

# Re-export components
__all__ = [
    'TemporalExtractionTool', 'create_temporal_extraction_tool'
]





