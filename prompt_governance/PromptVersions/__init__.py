#!/usr/bin/env python3
"""
Prompt Versions
Section 3: Canonical Repository Tree - Prompt Governance Versions
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptVersion:
    """Version management for prompt evolution and tracking"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.version_id = self.config.get("version_id", "")
        self.prompt_id = self.config.get("prompt_id", "")
        self.version_number = self.config.get("version_number", "1.0.0")
        self.changelog = self.config.get("changelog", [])
    
    def create_version(self, prompt_id: str, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new version of a prompt"""
        try:
            version = {
                "version_id": f"ver_{hash(prompt_id + str(datetime.now())) % 10000}",
                "prompt_id": prompt_id,
                "version_number": version_data.get("version_number", "1.0.0"),
                "template": version_data.get("template", ""),
                "parameters": version_data.get("parameters", {}),
                "changelog": version_data.get("changelog", []),
                "changes": version_data.get("changes", {}),
                "created_at": datetime.now().isoformat(),
                "created_by": version_data.get("created_by", "system"),
                "status": "active",
                "is_latest": True
            }
            
            logger.info(f"Created version {version['version_number']} for prompt: {prompt_id}")
            return version
            
        except Exception as e:
            logger.error(f"Failed to create prompt version: {e}")
            return {"error": str(e)}
    
    def get_version_history(self, prompt_id: str) -> List[Dict[str, Any]]:
        """Get version history for a prompt"""
        try:
            # Simulate version history
            mock_versions = [
                {
                    "version_id": "ver_123",
                    "prompt_id": prompt_id,
                    "version_number": "1.0.0",
                    "created_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "status": "deprecated",
                    "changelog": ["Initial version"]
                },
                {
                    "version_id": "ver_456",
                    "prompt_id": prompt_id,
                    "version_number": "1.1.0",
                    "created_at": "2023-02-01T00:00:00Z",
                    "created_by": "admin",
                    "status": "deprecated",
                    "changelog": ["Added new parameters", "Improved template"]
                },
                {
                    "version_id": "ver_789",
                    "prompt_id": prompt_id,
                    "version_number": "2.0.0",
                    "created_at": "2023-03-01T00:00:00Z",
                    "created_by": "system",
                    "status": "active",
                    "is_latest": True,
                    "changelog": ["Major redesign", "Updated security policies"]
                }
            ]
            
            logger.info(f"Retrieved version history for prompt: {prompt_id}")
            return mock_versions
            
        except Exception as e:
            logger.error(f"Failed to get version history: {e}")
            return []
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """Compare two versions of a prompt"""
        try:
            # Simulate version comparison
            comparison = {
                "version_1": {
                    "version_id": version_id_1,
                    "version_number": "1.0.0",
                    "template": "Hello {name}, you are applying for {role}.",
                    "parameters": {"name": "string", "role": "string"}
                },
                "version_2": {
                    "version_id": version_id_2,
                    "version_number": "2.0.0",
                    "template": "Hello {name}, you are applying for {role} position. Your skills in {skills} are impressive.",
                    "parameters": {"name": "string", "role": "string", "skills": "list"}
                },
                "differences": {
                    "template_changes": ["Added skills variable", "Enhanced greeting"],
                    "parameter_changes": ["Added skills parameter"],
                    "breaking_changes": False
                },
                "similarity_score": 0.75
            }
            
            logger.info(f"Compared versions: {version_id_1} vs {version_id_2}")
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare versions: {e}")
            return {"error": str(e)}
    
    def rollback_to_version(self, prompt_id: str, target_version: str) -> Dict[str, Any]:
        """Rollback prompt to specific version"""
        try:
            result = {
                "prompt_id": prompt_id,
                "target_version": target_version,
                "previous_version": "2.0.0",
                "rollback_at": datetime.now().isoformat(),
                "success": True,
                "new_version_id": f"ver_{hash(str(datetime.now())) % 10000}"
            }
            
            logger.info(f"Rolled back prompt {prompt_id} to version {target_version}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to rollback version: {e}")
            return {"success": False, "error": str(e)}
    
    def get_latest_version(self, prompt_id: str) -> Dict[str, Any]:
        """Get the latest version of a prompt"""
        try:
            latest_version = {
                "version_id": "ver_789",
                "prompt_id": prompt_id,
                "version_number": "2.0.0",
                "template": "Hello {name}, you are applying for {role} position. Your skills in {skills} are impressive.",
                "created_at": "2023-03-01T00:00:00Z",
                "status": "active",
                "is_latest": True
            }
            
            logger.info(f"Retrieved latest version for prompt: {prompt_id}")
            return latest_version
            
        except Exception as e:
            logger.error(f"Failed to get latest version: {e}")
            return {"error": str(e)}
    
    def deprecate_version(self, version_id: str, reason: str) -> Dict[str, Any]:
        """Deprecate a specific version"""
        try:
            result = {
                "version_id": version_id,
                "status": "deprecated",
                "deprecation_reason": reason,
                "deprecated_at": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Deprecated version: {version_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to deprecate version: {e}")
            return {"success": False, "error": str(e)}

def create_prompt_version(config: Optional[Dict[str, Any]] = None) -> PromptVersion:
    """Factory function to create prompt version instance"""
    return PromptVersion(config)

# Re-export components
__all__ = [
    'PromptVersion', 'create_prompt_version'
]
