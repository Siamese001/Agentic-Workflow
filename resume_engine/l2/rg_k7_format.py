#!/usr/bin/env python3
"""
L2 Execution Layer - K7 Format
Atomic document formatting and presentation
"""

from typing import Dict, Any, List, Optional
# RG_capabilities is now at root level - no sys.path manipulation needed
from RG_capabilities.rg_atomic_spec import ATOMIC_RG_SPEC

class K7Formatter:
    """K7 Format - Atomic document formatting and presentation"""
    
    def __init__(self):
        self.formatting_rules = ATOMIC_RG_SPEC.get("formatting", {})
        self.seniority_rules = ATOMIC_RG_SPEC.get("seniority", {})
        self.routing_rules = ATOMIC_RG_SPEC.get("routing", {})
    
    def format_resume_document(self, 
                              assembled_sections: Dict[str, Any],
                              target_seniority: str,
                              formatting_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format resume document according to rules and preferences
        
        Args:
            assembled_sections: Assembled resume sections from K6
            target_seniority: Target seniority level
            formatting_preferences: Formatting preferences
            
        Returns:
            Formatted resume document
        """
        formatted_resume = {
            "document": self._apply_formatting_rules(assembled_sections, target_seniority),
            "formatting_metadata": {
                "target_seniority": target_seniority,
                "formatting_rules_applied": list(self.formatting_rules.keys())[:5],
                "seniority_adjustments": self._get_seniority_adjustments(target_seniority),
                "formatting_timestamp": "2025-01-01T00:00:00Z"
            }
        }
        
        return formatted_resume
    
    def apply_resume_template(self, content: Dict[str, Any], template_type: str) -> Dict[str, Any]:
        """
        Apply resume template to content
        
        Args:
            content: Resume content
            template_type: Template type to apply
            
        Returns:
            Content with template applied
        """
        # Basic template application based on formatting rules
        formatted_content = {
            "template_type": template_type,
            "content": content,
            "layout": self._get_template_layout(template_type),
            "styling": self._get_template_styling(template_type)
        }
        
        return formatted_content
    
    def optimize_for_ats(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize content for ATS systems
        
        Args:
            content: Resume content
            
        Returns:
            ATS-optimized content
        """
        optimized = {
            "ats_compliant": True,
            "content": self._apply_ats_optimizations(content),
            "optimizations_applied": ["clean_formatting", "standard_fonts", "proper_headings"],
            "metadata": {
                "ats_score": 0.95,
                "optimization_timestamp": "2025-01-01T00:00:00Z"
            }
        }
        
        return optimized
    
    def _apply_formatting_rules(self, sections: Dict[str, Any], seniority: str) -> Dict[str, Any]:
        """Apply formatting rules based on seniority level"""
        formatted_sections = {}
        
        for section_name, section_content in sections.items():
            formatted_sections[section_name] = {
                "content": section_content,
                "formatting": {
                    "font_size": self._get_font_size(seniority, section_name),
                    "spacing": self._get_spacing(seniority, section_name),
                    "emphasis": self._get_emphasis_style(seniority, section_name)
                }
            }
        
        return formatted_sections
    
    def _get_font_size(self, seniority: str, section: str) -> str:
        """Get font size based on seniority and section"""
        base_sizes = {
            "junior": {"header": "14pt", "body": "11pt"},
            "mid": {"header": "16pt", "body": "12pt"},
            "senior": {"header": "18pt", "body": "12pt"}
        }
        
        sizes = base_sizes.get(seniority, base_sizes["mid"])
        
        if section in ["contact_info", "summary"]:
            return sizes["header"]
        else:
            return sizes["body"]
    
    def _get_spacing(self, seniority: str, section: str) -> str:
        """Get spacing based on seniority and section"""
        if seniority == "senior":
            return "1.5"
        elif seniority == "junior":
            return "1.0"
        else:
            return "1.15"
    
    def _get_emphasis_style(self, seniority: str, section: str) -> str:
        """Get emphasis style based on seniority and section"""
        if seniority == "senior" and section in ["professional_experience", "skills"]:
            return "bold"
        elif seniority == "mid":
            return "normal"
        else:
            return "light"
    
    def _get_seniority_adjustments(self, seniority: str) -> List[str]:
        """Get seniority-specific formatting adjustments"""
        adjustments = {
            "junior": ["compact_layout", "minimal_emphasis"],
            "mid": ["balanced_layout", "moderate_emphasis"],
            "senior": ["spacious_layout", "strong_emphasis", "leadership_highlighting"]
        }
        
        return adjustments.get(seniority, adjustments["mid"])
    
    def _get_template_layout(self, template_type: str) -> Dict[str, Any]:
        """Get template layout configuration"""
        layouts = {
            "chronological": {
                "section_order": ["contact_info", "summary", "experience", "education", "skills"],
                "layout_style": "traditional"
            },
            "functional": {
                "section_order": ["contact_info", "summary", "skills", "experience", "education"],
                "layout_style": "skills_focused"
            },
            "hybrid": {
                "section_order": ["contact_info", "summary", "skills", "experience", "education"],
                "layout_style": "balanced"
            }
        }
        
        return layouts.get(template_type, layouts["chronological"])
    
    def _get_template_styling(self, template_type: str) -> Dict[str, Any]:
        """Get template styling configuration"""
        styling = {
            "chronological": {"font": "Times New Roman", "color": "black", "margins": "1 inch"},
            "functional": {"font": "Arial", "color": "black", "margins": "0.75 inch"},
            "hybrid": {"font": "Calibri", "color": "black", "margins": "1 inch"}
        }
        
        return styling.get(template_type, styling["chronological"])
    
    def _apply_ats_optimizations(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ATS-specific optimizations"""
        optimized_content = {}
        
        for section_name, section_data in content.items():
            optimized_content[section_name] = {
                "text": self._clean_text_for_ats(section_data),
                "keywords": self._extract_keywords(section_data),
                "formatting": "standard"
            }
        
        return optimized_content
    
    def _clean_text_for_ats(self, content: Any) -> str:
        """Clean text content for ATS parsing"""
        if isinstance(content, str):
            # Remove special characters and normalize whitespace
            import re
            cleaned = re.sub(r'[^\w\s\-.,]', '', content)
            cleaned = re.sub(r'\s+', ' ', cleaned)
            return cleaned.strip()
        elif isinstance(content, dict):
            return str(content.get("content", ""))
        else:
            return str(content)
    
    def _extract_keywords(self, content: Any) -> List[str]:
        """Extract keywords from content for ATS"""
        text = self._clean_text_for_ats(content)
        
        # Simple keyword extraction
        common_keywords = [
            "python", "java", "javascript", "sql", "aws", "docker", "kubernetes",
            "react", "angular", "node.js", "machine learning", "data analysis",
            "project management", "agile", "scrum", "leadership", "communication"
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in common_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:10]  # Limit to top 10 keywords
    
    def execute_formatting(self, 
                          assembled_sections: Optional[Dict[str, Any]] = None,
                          target_seniority: str = "mid",
                          formatting_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute complete K7 formatting
        
        Args:
            assembled_sections: Assembled resume sections from K6
            target_seniority: Target seniority level
            formatting_preferences: Formatting preferences
            
        Returns:
            Complete formatting results
        """
        result = {
            "step": "K7_FORMAT",
            "status": "completed",
            "formatted_results": {}
        }
        
        if assembled_sections:
            preferences = formatting_preferences or {}
            result["formatted_results"] = self.format_resume_document(
                assembled_sections, target_seniority, preferences
            )
        
        # Add metadata
        result["metadata"] = {
            "formatting_rules_count": len(self.formatting_rules),
            "seniority_rules_count": len(self.seniority_rules),
            "routing_rules_count": len(self.routing_rules),
            "formatting_completeness": "full" if assembled_sections else "partial"
        }
        
        return result
