#!/usr/bin/env python3
"""
Message Mappers
Section 16: RAG Optimization - Data mapping utilities for outreach messages
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MessageMapper:
    """Mapper for outreach message data transformation and normalization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tone_mappings = self.config.get("tone_mappings", {})
        self.template_mappings = self.config.get("template_mappings", {})
    
    def map_message_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw message data to standardized format"""
        try:
            mapped_data = {}
            
            # Map basic message fields
            mapped_data["message_id"] = raw_data.get("id", "").strip()
            mapped_data["message_subject"] = raw_data.get("subject", "").strip()
            mapped_data["message_body"] = raw_data.get("body", "").strip()
            mapped_data["message_type"] = raw_data.get("type", "email").lower().strip()
            
            # Normalize message tone
            if "tone" in raw_data:
                mapped_data["message_tone"] = self._normalize_tone(raw_data["tone"])
            
            # Map recipient information
            if "recipient" in raw_data:
                mapped_data["recipient_info"] = self._normalize_recipient(raw_data["recipient"])
            
            # Map sender information
            if "sender" in raw_data:
                mapped_data["sender_info"] = self._normalize_sender(raw_data["sender"])
            
            # Map message metadata
            if "metadata" in raw_data:
                mapped_data["message_metadata"] = self._normalize_metadata(raw_data["metadata"])
            
            # Calculate message metrics
            mapped_data["message_metrics"] = self._calculate_message_metrics(mapped_data)
            
            # Add processing metadata
            mapped_data["_metadata"] = {
                "mapped_at": self._get_timestamp(),
                "mapper_version": "1.0",
                "source_fields": list(raw_data.keys())
            }
            
            logger.info(f"Successfully mapped message data: {mapped_data.get('message_id', 'Unknown')}")
            return mapped_data
            
        except Exception as e:
            logger.error(f"Message mapping failed: {e}")
            return {"error": str(e), "original_data": raw_data}
    
    def _normalize_tone(self, tone: str) -> str:
        """Normalize message tone classification"""
        tone_lower = tone.lower().strip()
        
        # Apply tone mappings
        for key, mapped_value in self.tone_mappings.items():
            if key.lower() in tone_lower:
                return mapped_value
        
        # Default tone normalization
        tone_synonyms = {
            "formal": "Formal",
            "professional": "Professional",
            "casual": "Casual",
            "friendly": "Friendly",
            "persuasive": "Persuasive",
            "urgent": "Urgent",
            "informative": "Informative"
        }
        
        for synonym, standard in tone_synonyms.items():
            if synonym in tone_lower:
                return standard
        
        return tone.title()
    
    def _normalize_recipient(self, recipient: Dict[str, Any]) -> Dict[str, str]:
        """Normalize recipient information"""
        normalized = {}
        
        if "name" in recipient:
            normalized["name"] = recipient["name"].strip().title()
        if "email" in recipient:
            normalized["email"] = recipient["email"].lower().strip()
        if "title" in recipient:
            normalized["title"] = recipient["title"].strip().title()
        if "company" in recipient:
            normalized["company"] = recipient["company"].strip()
        
        return normalized
    
    def _normalize_sender(self, sender: Dict[str, Any]) -> Dict[str, str]:
        """Normalize sender information"""
        normalized = {}
        
        if "name" in sender:
            normalized["name"] = sender["name"].strip().title()
        if "email" in sender:
            normalized["email"] = sender["email"].lower().strip()
        if "title" in sender:
            normalized["title"] = sender["title"].strip().title()
        if "company" in sender:
            normalized["company"] = sender["company"].strip()
        
        return normalized
    
    def _normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize message metadata"""
        normalized = {}
        
        # Normalize timestamps
        if "sent_at" in metadata:
            normalized["sent_at"] = str(metadata["sent_at"])
        if "created_at" in metadata:
            normalized["created_at"] = str(metadata["created_at"])
        
        # Normalize campaign information
        if "campaign" in metadata:
            normalized["campaign_id"] = str(metadata["campaign"])
        if "template" in metadata:
            normalized["template_id"] = str(metadata["template"])
        
        # Normalize status
        if "status" in metadata:
            normalized["status"] = metadata["status"].lower().strip()
        
        return normalized
    
    def _calculate_message_metrics(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate message metrics"""
        body = message_data.get("message_body", "")
        subject = message_data.get("message_subject", "")
        
        metrics = {
            "body_length": len(body),
            "subject_length": len(subject),
            "word_count": len(body.split()),
            "paragraph_count": len([p for p in body.split('\n') if p.strip()]),
            "has_personalization": self._has_personalization(body),
            "readability_score": self._calculate_readability(body)
        }
        
        return metrics
    
    def _has_personalization(self, text: str) -> bool:
        """Check if message contains personalization elements"""
        personalization_indicators = [
            "{{name}}", "[name]", "{name}",  # Name placeholders
            "{{company}}", "[company]", "{company}",  # Company placeholders
            "Dear", "Hi", "Hello"  # Personal greetings
        ]
        
        text_lower = text.lower()
        return any(indicator.lower() in text_lower for indicator in personalization_indicators)
    
    def _calculate_readability(self, text: str) -> str:
        """Calculate simple readability score"""
        if not text:
            return "No content"
        
        words = text.split()
        sentences = text.split('.')
        
        if not sentences:
            return "No sentences"
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        if avg_words_per_sentence < 10:
            return "Easy to read"
        elif avg_words_per_sentence < 15:
            return "Moderate readability"
        else:
            return "Complex readability"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import time
        return str(int(time.time()))
    
    def batch_map_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map multiple messages in batch"""
        results = []
        for message in messages:
            mapped = self.map_message_data(message)
            results.append(mapped)
        
        logger.info(f"Batch mapped {len(messages)} messages")
        return results
    
    def validate_mapped_message(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mapped message data"""
        if "error" in mapped_data:
            return {"valid": False, "errors": [mapped_data["error"]]}
        
        required_fields = ["message_id", "message_subject", "message_body"]
        missing_fields = [field for field in required_fields if not mapped_data.get(field)]
        
        if missing_fields:
            return {"valid": False, "errors": [f"Missing required fields: {missing_fields}"]}
        
        # Validate message body length
        body_length = len(mapped_data.get("message_body", ""))
        if body_length == 0:
            return {"valid": False, "errors": ["Message body cannot be empty"]}
        elif body_length > 50000:
            return {"valid": False, "errors": ["Message body too long"]}
        
        return {"valid": True, "errors": []}

def map_message_data(raw_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to map message data"""
    mapper = MessageMapper(config)
    return mapper.map_message_data(raw_data)

# Re-export components
__all__ = [
    'MessageMapper', 'map_message_data'
]





