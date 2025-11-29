#!/usr/bin/env python3
"""
Company Mappers
Section 16: RAG Optimization - Data mapping utilities for company information
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class CompanyMapper:
    """Mapper for company data transformation and normalization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.industry_mappings = self.config.get("industry_mappings", {})
        self.size_mappings = self.config.get("size_mappings", {})
    
    def map_company_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw company data to standardized format"""
        try:
            mapped_data = {}
            
            # Map basic company fields
            mapped_data["company_name"] = raw_data.get("name", "").strip()
            mapped_data["company_domain"] = raw_data.get("domain", "").lower().strip()
            mapped_data["company_website"] = raw_data.get("website", "").strip()
            mapped_data["company_description"] = raw_data.get("description", "").strip()
            
            # Normalize industry
            if "industry" in raw_data:
                mapped_data["company_industry"] = self._normalize_industry(raw_data["industry"])
            
            # Normalize company size
            if "size" in raw_data or "employees" in raw_data:
                mapped_data["company_size"] = self._normalize_company_size(raw_data)
            
            # Map location data
            if "location" in raw_data:
                mapped_data["company_location"] = self._normalize_location(raw_data["location"])
            
            # Map contact information
            if "contact" in raw_data:
                mapped_data["company_contact"] = self._normalize_contact_info(raw_data["contact"])
            
            # Add metadata
            mapped_data["_metadata"] = {
                "mapped_at": self._get_timestamp(),
                "mapper_version": "1.0",
                "source_fields": list(raw_data.keys())
            }
            
            logger.info(f"Successfully mapped company data: {mapped_data.get('company_name', 'Unknown')}")
            return mapped_data
            
        except Exception as e:
            logger.error(f"Company mapping failed: {e}")
            return {"error": str(e), "original_data": raw_data}
    
    def _normalize_industry(self, industry: str) -> str:
        """Normalize industry classification"""
        industry_lower = industry.lower().strip()
        
        # Apply industry mappings
        for key, mapped_value in self.industry_mappings.items():
            if key.lower() in industry_lower:
                return mapped_value
        
        # Default normalization
        industry_synonyms = {
            "tech": "Technology",
            "software": "Software",
            "healthcare": "Healthcare",
            "finance": "Financial Services",
            "manufacturing": "Manufacturing",
            "retail": "Retail",
            "education": "Education"
        }
        
        for synonym, standard in industry_synonyms.items():
            if synonym in industry_lower:
                return standard
        
        return industry.title()
    
    def _normalize_company_size(self, data: Dict[str, Any]) -> str:
        """Normalize company size classification"""
        employees = data.get("employees", data.get("size", 0))
        
        if isinstance(employees, str):
            # Extract numeric value from string
            import re
            numbers = re.findall(r'\d+', employees)
            if numbers:
                employees = int(numbers[0])
            else:
                return employees.title()
        
        if isinstance(employees, int):
            if employees < 10:
                return "Startup (1-9)"
            elif employees < 50:
                return "Small (10-49)"
            elif employees < 200:
                return "Small-Medium (50-199)"
            elif employees < 1000:
                return "Medium (200-999)"
            elif employees < 5000:
                return "Large (1K-5K)"
            elif employees < 10000:
                return "Large (5K-10K)"
            else:
                return "Enterprise (10K+)"
        
        return str(employees).title()
    
    def _normalize_location(self, location: str) -> Dict[str, str]:
        """Normalize location data"""
        location_parts = location.split(",")
        
        normalized = {
            "full_address": location.strip(),
            "city": "",
            "state": "",
            "country": "",
            "postal_code": ""
        }
        
        if len(location_parts) >= 1:
            normalized["city"] = location_parts[0].strip()
        if len(location_parts) >= 2:
            normalized["state"] = location_parts[1].strip()
        if len(location_parts) >= 3:
            normalized["country"] = location_parts[2].strip()
        
        return normalized
    
    def _normalize_contact_info(self, contact: Dict[str, Any]) -> Dict[str, str]:
        """Normalize contact information"""
        normalized = {}
        
        if "email" in contact:
            normalized["email"] = contact["email"].lower().strip()
        if "phone" in contact:
            normalized["phone"] = self._normalize_phone(contact["phone"])
        if "address" in contact:
            normalized["address"] = contact["address"].strip()
        
        return normalized
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format"""
        digits_only = ''.join(filter(str.isdigit, phone))
        
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == '1':
            return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
        else:
            return phone
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import time
        return str(int(time.time()))
    
    def batch_map_companies(self, companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map multiple companies in batch"""
        results = []
        for company in companies:
            mapped = self.map_company_data(company)
            results.append(mapped)
        
        logger.info(f"Batch mapped {len(companies)} companies")
        return results
    
    def validate_mapped_company(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mapped company data"""
        if "error" in mapped_data:
            return {"valid": False, "errors": [mapped_data["error"]]}
        
        required_fields = ["company_name", "company_domain"]
        missing_fields = [field for field in required_fields if not mapped_data.get(field)]
        
        if missing_fields:
            return {"valid": False, "errors": [f"Missing required fields: {missing_fields}"]}
        
        # Validate domain format
        domain = mapped_data.get("company_domain", "")
        if "." not in domain:
            return {"valid": False, "errors": ["Invalid domain format"]}
        
        return {"valid": True, "errors": []}

def map_company_data(raw_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to map company data"""
    mapper = CompanyMapper(config)
    return mapper.map_company_data(raw_data)

# Re-export components
__all__ = [
    'CompanyMapper', 'map_company_data'
]





