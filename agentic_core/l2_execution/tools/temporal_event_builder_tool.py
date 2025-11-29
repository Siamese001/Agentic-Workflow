#!/usr/bin/env python3
"""
Temporal Event Builder Tool
Section 5: Tool Contracts - TEMPORAL tool family
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class TemporalEventBuilderTool:
    """Construct temporal event records"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.auto_chain = self.config.get("auto_chain", True)
        self.metadata_required = self.config.get("metadata_required", ["entity", "event_type"])
    
    def build_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a temporal event record"""
        try:
            # Validate required metadata
            missing_metadata = [field for field in self.metadata_required if field not in event_data]
            if missing_metadata:
                raise ValueError(f"Missing required metadata: {missing_metadata}")
            
            # Construct temporal event
            temporal_event = {
                "event_id": event_data.get("event_id", f"event_{uuid.uuid4().hex[:8]}"),
                "entity": event_data["entity"],
                "event_type": event_data["event_type"],
                "description": event_data.get("description", ""),
                "valid_at": event_data.get("timestamp", datetime.now().isoformat()),
                "invalid_at": event_data.get("invalid_at", None),  # Still valid by default
                "duration": event_data.get("duration", None),
                "metadata": event_data.get("metadata", {}),
                "created_at": datetime.now().isoformat(),
                "confidence": event_data.get("confidence", 1.0)
            }
            
            # Add chaining information if auto-chain is enabled
            if self.auto_chain:
                temporal_event["precedes_event"] = event_data.get("precedes_event", None)
                temporal_event["follows_event"] = event_data.get("follows_event", None)
            
            logger.info(f"Built temporal event {temporal_event['event_id']} for entity {temporal_event['entity']}")
            return temporal_event
            
        except Exception as e:
            logger.error(f"Temporal event construction failed: {e}")
            return {"error": str(e), "event_data": event_data}
    
    def build_event_sequence(self, events_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build a sequence of related temporal events"""
        try:
            events = []
            
            for i, event_data in enumerate(events_data):
                # Add chaining information
                if self.auto_chain and i > 0:
                    event_data["follows_event"] = events[i-1]["event_id"] if events else None
                
                if self.auto_chain and i < len(events_data) - 1:
                    # Will be updated when next event is created
                    event_data["precedes_event"] = None
                
                event = self.build_event(event_data)
                if "error" not in event:
                    events.append(event)
            
            # Update forward references
            if self.auto_chain:
                for i in range(len(events) - 1):
                    events[i]["precedes_event"] = events[i + 1]["event_id"]
            
            logger.info(f"Built event sequence with {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Event sequence construction failed: {e}")
            return []
    
    def build_resume_timeline(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build temporal timeline from resume data"""
        try:
            events = []
            
            # Education events
            education = resume_data.get("education", [])
            for edu in education:
                edu_event = {
                    "entity": resume_data.get("name", "Unknown"),
                    "event_type": "education",
                    "description": f"{edu.get('degree', '')} at {edu.get('institution', '')}",
                    "timestamp": edu.get("start_date", ""),
                    "duration": edu.get("duration", ""),
                    "metadata": {
                        "degree": edu.get("degree", ""),
                        "institution": edu.get("institution", ""),
                        "field": edu.get("field", "")
                    }
                }
                events.append(self.build_event(edu_event))
            
            # Work experience events
            experience = resume_data.get("experience", [])
            for exp in experience:
                exp_event = {
                    "entity": resume_data.get("name", "Unknown"),
                    "event_type": "employment",
                    "description": f"{exp.get('title', '')} at {exp.get('company', '')}",
                    "timestamp": exp.get("start_date", ""),
                    "duration": exp.get("duration", ""),
                    "metadata": {
                        "title": exp.get("title", ""),
                        "company": exp.get("company", ""),
                        "responsibilities": exp.get("responsibilities", [])
                    }
                }
                events.append(self.build_event(exp_event))
            
            # Skill acquisition events
            skills = resume_data.get("skills", [])
            for skill in skills:
                skill_event = {
                    "entity": resume_data.get("name", "Unknown"),
                    "event_type": "skill_acquisition",
                    "description": f"Acquired {skill.get('name', '')} skill",
                    "timestamp": skill.get("learned_date", ""),
                    "metadata": {
                        "skill_name": skill.get("name", ""),
                        "proficiency": skill.get("proficiency", ""),
                        "category": skill.get("category", "")
                    }
                }
                events.append(self.build_event(skill_event))
            
            # Sort events by timestamp
            events.sort(key=lambda x: x.get("valid_at", ""))
            
            logger.info(f"Built resume timeline with {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Resume timeline construction failed: {e}")
            return []
    
    def validate_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Validate temporal event structure"""
        try:
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check required fields
            required_fields = ["event_id", "entity", "event_type", "valid_at"]
            for field in required_fields:
                if field not in event or not event[field]:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["is_valid"] = False
            
            # Check timestamp format
            if "valid_at" in event:
                try:
                    # Simple timestamp validation
                    timestamp = event["valid_at"]
                    if not isinstance(timestamp, str):
                        validation_result["errors"].append("valid_at must be a string")
                        validation_result["is_valid"] = False
                except Exception:
                    validation_result["errors"].append("Invalid valid_at timestamp format")
                    validation_result["is_valid"] = False
            
            # Check logical consistency
            if event.get("valid_at") and event.get("invalid_at"):
                if event["valid_at"] >= event["invalid_at"]:
                    validation_result["errors"].append("valid_at must be before invalid_at")
                    validation_result["is_valid"] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Event validation failed: {e}")
            return {"is_valid": False, "errors": [str(e)]}
    
    def chain_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chain events temporally"""
        try:
            # Sort events by valid_at timestamp
            sorted_events = sorted(events, key=lambda x: x.get("valid_at", ""))
            
            # Update chaining references
            for i in range(len(sorted_events)):
                current_event = sorted_events[i]
                
                # Set follows_event (previous event)
                if i > 0:
                    current_event["follows_event"] = sorted_events[i-1]["event_id"]
                else:
                    current_event["follows_event"] = None
                
                # Set precedes_event (next event)
                if i < len(sorted_events) - 1:
                    current_event["precedes_event"] = sorted_events[i+1]["event_id"]
                else:
                    current_event["precedes_event"] = None
            
            logger.info(f"Chained {len(sorted_events)} events temporally")
            return sorted_events
            
        except Exception as e:
            logger.error(f"Event chaining failed: {e}")
            return events

def create_temporal_event_builder_tool(config: Optional[Dict[str, Any]] = None) -> TemporalEventBuilderTool:
    """Factory function to create temporal event builder tool instance"""
    return TemporalEventBuilderTool(config)

# Re-export components
__all__ = [
    'TemporalEventBuilderTool', 'create_temporal_event_builder_tool'
]
