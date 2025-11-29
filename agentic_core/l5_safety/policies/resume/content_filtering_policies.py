#!/usr/bin/env python3
"""
Content Filtering Policies
Section 14: Security Layer - Content filtering policies for resume data
"""

from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)

class ContentFilteringPolicy:
    """Policy manager for resume content filtering"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.blocked_content = self._load_blocked_content_patterns()
        self.filtering_enabled = self.config.get("filtering_enabled", True)
        self.strict_mode = self.config.get("strict_mode", False)
    
    def filter_resume_content(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter resume content for inappropriate material"""
        try:
            filtering_result = {
                "is_clean": True,
                "content_issues": [],
                "blocked_content": [],
                "filtered_data": resume_data.copy(),
                "recommendations": []
            }
            
            # Check for blocked content
            blocked_items = self._scan_for_blocked_content(resume_data)
            if blocked_items:
                filtering_result["blocked_content"] = blocked_items
                filtering_result["is_clean"] = False
                filtering_result["content_issues"].append("Inappropriate content detected")
            
            # Apply content filters
            if self.filtering_enabled:
                filtering_result["filtered_data"] = self._apply_content_filters(resume_data)
            
            # Generate recommendations
            filtering_result["recommendations"] = self._generate_filtering_recommendations(filtering_result)
            
            logger.info(f"Content filtering completed: {'Clean' if filtering_result['is_clean'] else 'Issues found'}")
            return filtering_result
            
        except Exception as e:
            logger.error(f"Content filtering failed: {e}")
            return {"is_clean": False, "error": str(e)}
    
    def _load_blocked_content_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for blocked content"""
        return [
            {
                "type": "discrimination",
                "patterns": [
                    r'\b(age|race|gender|religion|sexual orientation)\s+discrimination\b',
                    r'\b(discriminate|bias|prejudice)\s+against\b'
                ],
                "description": "Discriminatory language",
                "severity": "high"
            },
            {
                "type": "harassment",
                "patterns": [
                    r'\b(harass|threaten|intimidate|bully)\b',
                    r'\b(inappropriate|unwanted|unwelcome)\s+(contact|behavior)\b'
                ],
                "description": "Harassment content",
                "severity": "high"
            },
            {
                "type": "illegal_activity",
                "patterns": [
                    r'\b(illegal|unlawful|criminal)\s+(activity|behavior)\b',
                    r'\b(drug|fraud|theft|embezzlement)\b'
                ],
                "description": "Illegal activity references",
                "severity": "high"
            },
            {
                "type": "confidential_info",
                "patterns": [
                    r'\b(confidential|proprietary|trade secret)\s+(information|data)\b',
                    r'\b(nda|non-disclosure)\s+(agreement|contract)\b'
                ],
                "description": "Confidential information disclosure",
                "severity": "medium"
            },
            {
                "type": "inappropriate_language",
                "patterns": [
                    r'\b(curse|swear|profanity|vulgar)\b',
                    r'\b(inappropriate|offensive|unprofessional)\s+(language|content)\b'
                ],
                "description": "Inappropriate language",
                "severity": "medium"
            }
        ]
    
    def _scan_for_blocked_content(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan data for blocked content patterns"""
        blocked_items = []
        
        def scan_text(text: str, field_path: str):
            text_lower = text.lower()
            for pattern_info in self.blocked_content:
                for pattern in pattern_info["patterns"]:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    if matches:
                        blocked_items.append({
                            "type": pattern_info["type"],
                            "description": pattern_info["description"],
                            "severity": pattern_info["severity"],
                            "field": field_path,
                            "matches": matches[:3]  # Limit to first 3 matches
                        })
        
        def recursive_scan(obj: Any, path: str = ""):
            if isinstance(obj, str):
                scan_text(obj, path)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    recursive_scan(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]" if path else f"[{i}]"
                    recursive_scan(item, new_path)
        
        recursive_scan(data)
        return blocked_items
    
    def _apply_content_filters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply content filters to data"""
        def filter_text(text: str) -> str:
            filtered = text
            # Remove or mask problematic content
            for pattern_info in self.blocked_content:
                if pattern_info["severity"] in ["high"] or self.strict_mode:
                    for pattern in pattern_info["patterns"]:
                        filtered = re.sub(pattern, "[FILTERED]", filtered, flags=re.IGNORECASE)
            return filtered
        
        def recursive_filter(obj: Any):
            if isinstance(obj, str):
                return filter_text(obj)
            elif isinstance(obj, dict):
                return {key: recursive_filter(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [recursive_filter(item) for item in obj]
            else:
                return obj
        
        return recursive_filter(data)
    
    def _generate_filtering_recommendations(self, filtering_result: Dict[str, Any]) -> List[str]:
        """Generate content filtering recommendations"""
        recommendations = []
        
        if filtering_result["blocked_content"]:
            recommendations.append("Remove or revise inappropriate content")
            recommendations.append("Review content for compliance with professional standards")
        
        high_severity_items = [item for item in filtering_result["blocked_content"] if item.get("severity") == "high"]
        if high_severity_items:
            recommendations.append("Immediate attention required for high-severity content issues")
        
        if self.strict_mode:
            recommendations.append("Consider disabling strict mode if content filtering is too restrictive")
        else:
            recommendations.append("Enable strict mode for more thorough content filtering")
        
        # General recommendations
        recommendations.extend([
            "Implement content review process before submission",
            "Use professional language throughout resume",
            "Avoid including confidential or proprietary information"
        ])
        
        return recommendations
    
    def get_content_summary(self, filtering_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content filtering summary"""
        return {
            "content_status": "Clean" if filtering_result.get("is_clean", False) else "Issues detected",
            "issues_found": len(filtering_result.get("content_issues", [])),
            "blocked_items": len(filtering_result.get("blocked_content", [])),
            "high_severity_count": len([item for item in filtering_result.get("blocked_content", []) if item.get("severity") == "high"]),
            "filtering_applied": self.filtering_enabled,
            "strict_mode": self.strict_mode
        }
    
    def update_filtering_rules(self, new_patterns: List[Dict[str, Any]]) -> bool:
        """Update content filtering rules"""
        try:
            self.blocked_content.extend(new_patterns)
            logger.info(f"Updated filtering rules with {len(new_patterns)} new patterns")
            return True
        except Exception as e:
            logger.error(f"Failed to update filtering rules: {e}")
            return False

def filter_resume_content(resume_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to filter resume content"""
    policy = ContentFilteringPolicy(config)
    return policy.filter_resume_content(resume_data)

# Re-export components
__all__ = [
    'ContentFilteringPolicy', 'filter_resume_content'
]
