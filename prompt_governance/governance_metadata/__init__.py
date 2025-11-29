#!/usr/bin/env python3
"""
Prompt Metadata
Section 3: Canonical Repository Tree - Prompt Governance Metadata
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptMetadata:
    """Prompt metadata and tagging system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metadata_id = self.config.get("metadata_id", "")
        self.prompt_id = self.config.get("prompt_id", "")
        self.tags = self.config.get("tags", [])
        self.attributes = self.config.get("attributes", {})
    
    def create_metadata(self, prompt_id: str, metadata_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for a prompt"""
        try:
            metadata = {
                "metadata_id": f"meta_{hash(prompt_id) % 10000}",
                "prompt_id": prompt_id,
                "tags": metadata_data.get("tags", []),
                "attributes": metadata_data.get("attributes", {}),
                "classification": metadata_data.get("classification", {}),
                "usage_stats": metadata_data.get("usage_stats", {}),
                "performance_metrics": metadata_data.get("performance_metrics", {}),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Created metadata for prompt: {prompt_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to create prompt metadata: {e}")
            return {"error": str(e)}
    
    def add_tags(self, metadata_id: str, new_tags: List[str]) -> Dict[str, Any]:
        """Add tags to prompt metadata"""
        try:
            # Simulate tag addition
            result = {
                "metadata_id": metadata_id,
                "added_tags": new_tags,
                "total_tags": len(new_tags) + 5,  # Mock existing tags
                "updated_at": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Added tags to metadata: {metadata_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add tags: {e}")
            return {"success": False, "error": str(e)}
    
    def search_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Search prompts by tags"""
        try:
            # Simulate tag-based search
            mock_prompts = [
                {
                    "prompt_id": "prompt_123",
                    "name": "Resume Generator",
                    "tags": ["resume", "generation", "professional"],
                    "metadata_id": "meta_123"
                },
                {
                    "prompt_id": "prompt_456", 
                    "name": "Outreach Message",
                    "tags": ["outreach", "email", "professional"],
                    "metadata_id": "meta_456"
                }
            ]
            
            # Filter by tags
            matching_prompts = []
            for prompt in mock_prompts:
                if any(tag in prompt["tags"] for tag in tags):
                    matching_prompts.append(prompt)
            
            logger.info(f"Found {len(matching_prompts)} prompts matching tags: {tags}")
            return matching_prompts
            
        except Exception as e:
            logger.error(f"Tag search failed: {e}")
            return []
    
    def update_attributes(self, metadata_id: str, new_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Update prompt attributes"""
        try:
            result = {
                "metadata_id": metadata_id,
                "updated_attributes": new_attributes,
                "updated_at": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Updated attributes for metadata: {metadata_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update attributes: {e}")
            return {"success": False, "error": str(e)}
    
    def get_metadata_summary(self, metadata_id: str) -> Dict[str, Any]:
        """Get summary of prompt metadata"""
        try:
            mock_metadata = {
                "meta_123": {
                    "prompt_id": "prompt_123",
                    "tags": ["resume", "generation", "professional"],
                    "attributes": {
                        "complexity": "medium",
                        "domain": "hr",
                        "language": "english"
                    },
                    "usage_stats": {
                        "usage_count": 150,
                        "success_rate": 0.92,
                        "avg_response_time": 2.3
                    }
                }
            }
            
            metadata = mock_metadata.get(metadata_id, {})
            
            if not metadata:
                return {"error": f"Metadata {metadata_id} not found"}
            
            summary = {
                "metadata_id": metadata_id,
                "prompt_id": metadata["prompt_id"],
                "tag_count": len(metadata["tags"]),
                "attribute_count": len(metadata["attributes"]),
                "usage_count": metadata["usage_stats"]["usage_count"],
                "success_rate": metadata["usage_stats"]["success_rate"],
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info(f"Retrieved metadata summary: {metadata_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get metadata summary: {e}")
            return {"error": str(e)}
    
    def classify_prompt(self, metadata_id: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Classify prompt with categories and labels"""
        try:
            result = {
                "metadata_id": metadata_id,
                "classification": {
                    "category": classification.get("category", "general"),
                    "sensitivity": classification.get("sensitivity", "low"),
                    "complexity": classification.get("complexity", "medium"),
                    "domain": classification.get("domain", "general"),
                    "risk_level": classification.get("risk_level", "low")
                },
                "classified_at": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Classified prompt metadata: {metadata_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to classify prompt: {e}")
            return {"success": False, "error": str(e)}
    
    def track_usage(self, metadata_id: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track prompt usage statistics"""
        try:
            result = {
                "metadata_id": metadata_id,
                "usage_record": {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": usage_data.get("user_id", "anonymous"),
                    "execution_time": usage_data.get("execution_time", 0),
                    "success": usage_data.get("success", True),
                    "tokens_used": usage_data.get("tokens_used", 0)
                },
                "updated_stats": {
                    "total_usage": 151,  # Mock incremented value
                    "avg_execution_time": 2.4,
                    "success_rate": 0.91
                },
                "success": True
            }
            
            logger.info(f"Tracked usage for metadata: {metadata_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
            return {"success": False, "error": str(e)}

def create_prompt_metadata(config: Optional[Dict[str, Any]] = None) -> PromptMetadata:
    """Factory function to create prompt metadata instance"""
    return PromptMetadata(config)

# Re-export components
__all__ = [
    'PromptMetadata', 'create_prompt_metadata'
]





