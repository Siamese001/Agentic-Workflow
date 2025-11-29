#!/usr/bin/env python3
"""
Prompt Manifests
Section 3: Canonical Repository Tree - Prompt Governance Manifests
"""

from typing import Dict, Any, List, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptManifest:
    """Structured prompt manifest for governance and management"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.manifest_id = self.config.get("manifest_id", "")
        self.name = self.config.get("name", "")
        self.version = self.config.get("version", "1.0.0")
        self.domain = self.config.get("domain", "general")
        self.description = self.config.get("description", "")
        self.created_at = self.config.get("created_at", datetime.now().isoformat())
        self.updated_at = self.config.get("updated_at", datetime.now().isoformat())
    
    def create_manifest(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prompt manifest"""
        try:
            manifest = {
                "manifest_id": f"manifest_{hash(str(prompt_data)) % 10000}",
                "name": prompt_data.get("name", "Unnamed Prompt"),
                "version": prompt_data.get("version", "1.0.0"),
                "domain": prompt_data.get("domain", "general"),
                "description": prompt_data.get("description", ""),
                "prompt_template": prompt_data.get("template", ""),
                "parameters": prompt_data.get("parameters", {}),
                "metadata": prompt_data.get("metadata", {}),
                "security_policies": prompt_data.get("security_policies", []),
                "access_control": prompt_data.get("access_control", {}),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            logger.info(f"Created prompt manifest: {manifest['manifest_id']}")
            return manifest
            
        except Exception as e:
            logger.error(f"Failed to create prompt manifest: {e}")
            return {"error": str(e)}
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Validate prompt manifest structure"""
        try:
            required_fields = ["manifest_id", "name", "version", "domain", "prompt_template"]
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            for field in required_fields:
                if field not in manifest or not manifest[field]:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")
            
            # Validate version format
            version = manifest.get("version", "")
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                validation_result["warnings"].append(f"Invalid version format: {version}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Manifest validation failed: {e}")
            return {"is_valid": False, "errors": [str(e)]}
    
    def update_manifest(self, manifest_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing prompt manifest"""
        try:
            # Simulate manifest update
            updated_manifest = {
                "manifest_id": manifest_id,
                "updated_at": datetime.now().isoformat(),
                "changes": list(updates.keys()),
                "status": "updated"
            }
            
            logger.info(f"Updated prompt manifest: {manifest_id}")
            return updated_manifest
            
        except Exception as e:
            logger.error(f"Failed to update prompt manifest: {e}")
            return {"error": str(e)}

def create_prompt_manifest(config: Optional[Dict[str, Any]] = None) -> PromptManifest:
    """Factory function to create prompt manifest instance"""
    return PromptManifest(config)

# Re-export components
__all__ = [
    'PromptManifest', 'create_prompt_manifest'
]





