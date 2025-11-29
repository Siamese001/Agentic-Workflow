#!/usr/bin/env python3
"""
Contact Mappers
Section 16: RAG Optimization - Data mapping utilities for contact information
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ContactMapper:
    """Mapper for contact data transformation and normalization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.field_mappings = self.config.get("field_mappings", {})
        self.normalization_rules = self.config.get("normalization_rules", {})
    
    def map_contact_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw contact data to standardized format"""
        try:
            mapped_data = {}
            
            # Apply field mappings
            for target_field, source_field in self.field_mappings.items():
                if source_field in raw_data:
                    mapped_data[target_field] = raw_data[source_field]
            
            # Normalize common fields
            mapped_data.update(self._normalize_contact_fields(raw_data))
            
            # Add metadata
            mapped_data["_metadata"] = {
                "mapped_at": self._get_timestamp(),
                "mapper_version": "1.0",
                "source_fields": list(raw_data.keys())
            }
            
            logger.info(f"Successfully mapped contact data with {len(mapped_data)} fields")
            return mapped_data
            
        except Exception as e:
            logger.error(f"Contact mapping failed: {e}")
            return {"error": str(e), "original_data": raw_data}
    
    def _normalize_contact_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize common contact fields"""
        normalized = {}
        
        # Normalize email
        if "email" in data:
            normalized["email"] = data["email"].lower().strip()
        
        # Normalize phone
        if "phone" in data:
            normalized["phone"] = self._normalize_phone(data["phone"])
        
        # Normalize name
        if "name" in data:
            normalized["name"] = data["name"].strip().title()
        
        # Normalize company
        if "company" in data:
            normalized["company"] = data["company"].strip()
        
        return normalized
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format"""
        # Remove non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Simple US phone format normalization
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == '1':
            return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
        else:
            return phone  # Return original if format not recognized
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import time
        return str(int(time.time()))
    
    def batch_map_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map multiple contacts in batch"""
        results = []
        for contact in contacts:
            mapped = self.map_contact_data(contact)
            results.append(mapped)
        
        logger.info(f"Batch mapped {len(contacts)} contacts")
        return results
    
    def validate_mapped_contact(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mapped contact data"""
        if "error" in mapped_data:
            return {"valid": False, "errors": [mapped_data["error"]]}
        
        required_fields = ["name", "email"]
        missing_fields = [field for field in required_fields if field not in mapped_data]
        
        if missing_fields:
            return {"valid": False, "errors": [f"Missing required fields: {missing_fields}"]}
        
        # Validate email format
        if "@" not in mapped_data.get("email", ""):
            return {"valid": False, "errors": ["Invalid email format"]}
        
        return {"valid": True, "errors": []}

def map_contact_data(raw_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to map contact data"""
    mapper = ContactMapper(config)
    return mapper.map_contact_data(raw_data)

# Re-export components
__all__ = [
    'ContactMapper', 'map_contact_data'
]





