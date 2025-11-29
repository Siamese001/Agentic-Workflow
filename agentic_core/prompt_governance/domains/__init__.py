#!/usr/bin/env python3
"""
Prompt Domains
Section 3: Canonical Repository Tree - Prompt Governance Domains
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptDomain:
    """Domain-specific prompt specializations and configurations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.domain_id = self.config.get("domain_id", "")
        self.domain_name = self.config.get("domain_name", "")
        self.specialization = self.config.get("specialization", "")
    
    def create_domain(self, domain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prompt domain"""
        try:
            domain = {
                "domain_id": f"domain_{hash(str(domain_data)) % 10000}",
                "domain_name": domain_data.get("domain_name", ""),
                "specialization": domain_data.get("specialization", ""),
                "description": domain_data.get("description", ""),
                "prompt_templates": domain_data.get("prompt_templates", {}),
                "domain_parameters": domain_data.get("domain_parameters", {}),
                "validation_rules": domain_data.get("validation_rules", {}),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "active": True
            }
            
            logger.info(f"Created prompt domain: {domain['domain_name']}")
            return domain
            
        except Exception as e:
            logger.error(f"Failed to create prompt domain: {e}")
            return {"error": str(e)}
    
    def get_resume_domain_prompts(self) -> List[Dict[str, Any]]:
        """Get resume-specific domain prompts"""
        try:
            resume_prompts = [
                {
                    "prompt_id": "resume_summary",
                    "name": "Resume Summary Generator",
                    "template": "Generate a professional summary for a {role} with {experience_years} years of experience in {industry}. Key skills: {skills}.",
                    "parameters": {"role": "string", "experience_years": "integer", "industry": "string", "skills": "list"},
                    "domain": "resume",
                    "specialization": "summary_generation"
                },
                {
                    "prompt_id": "resume_skills",
                    "name": "Skills Section Formatter",
                    "template": "Format the following skills for a resume: {raw_skills}. Categorize into technical and soft skills for a {role} position.",
                    "parameters": {"raw_skills": "string", "role": "string"},
                    "domain": "resume",
                    "specialization": "skills_formatting"
                },
                {
                    "prompt_id": "resume_experience",
                    "name": "Experience Description Enhancer",
                    "template": "Enhance this experience description for a {role} resume: {basic_description}. Add quantifiable achievements and impact statements.",
                    "parameters": {"basic_description": "string", "role": "string"},
                    "domain": "resume",
                    "specialization": "experience_enhancement"
                }
            ]
            
            logger.info(f"Retrieved {len(resume_prompts)} resume domain prompts")
            return resume_prompts
            
        except Exception as e:
            logger.error(f"Failed to get resume domain prompts: {e}")
            return []
    
    def get_outreach_domain_prompts(self) -> List[Dict[str, Any]]:
        """Get outreach-specific domain prompts"""
        try:
            outreach_prompts = [
                {
                    "prompt_id": "outreach_initial",
                    "name": "Initial Outreach Message",
                    "template": "Write a professional outreach message to {recipient_name} at {company_name} for a {role} position. Mention {shared_interest} and highlight relevant experience in {relevant_skills}.",
                    "parameters": {"recipient_name": "string", "company_name": "string", "role": "string", "shared_interest": "string", "relevant_skills": "list"},
                    "domain": "outreach",
                    "specialization": "initial_contact"
                },
                {
                    "prompt_id": "outreach_followup",
                    "name": "Follow-up Message",
                    "template": "Write a follow-up message to {recipient_name} regarding the {role} position at {company_name}. Reference previous conversation about {previous_topic}.",
                    "parameters": {"recipient_name": "string", "company_name": "string", "role": "string", "previous_topic": "string"},
                    "domain": "outreach",
                    "specialization": "follow_up"
                },
                {
                    "prompt_id": "outreach_connection",
                    "name": "LinkedIn Connection Request",
                    "template": "Write a LinkedIn connection request to {recipient_name} who works at {company_name} as {their_role}. Mention {connection_reason} and shared background in {shared_background}.",
                    "parameters": {"recipient_name": "string", "company_name": "string", "their_role": "string", "connection_reason": "string", "shared_background": "string"},
                    "domain": "outreach",
                    "specialization": "social_networking"
                }
            ]
            
            logger.info(f"Retrieved {len(outreach_prompts)} outreach domain prompts")
            return outreach_prompts
            
        except Exception as e:
            logger.error(f"Failed to get outreach domain prompts: {e}")
            return []
    
    def get_domain_by_name(self, domain_name: str) -> Dict[str, Any]:
        """Get domain configuration by name"""
        try:
            domains = {
                "resume": {
                    "domain_id": "domain_resume",
                    "domain_name": "resume",
                    "specialization": "resume_generation_optimization",
                    "description": "Domain for resume generation, formatting, and optimization prompts",
                    "prompt_count": 15,
                    "active_templates": ["summary", "skills", "experience", "education"],
                    "validation_rules": {
                        "max_length": 500,
                        "required_sections": ["experience", "skills"],
                        "format": "professional"
                    }
                },
                "outreach": {
                    "domain_id": "domain_outreach",
                    "domain_name": "outreach",
                    "specialization": "professional_communication",
                    "description": "Domain for outreach, networking, and communication prompts",
                    "prompt_count": 12,
                    "active_templates": ["initial_contact", "follow_up", "networking"],
                    "validation_rules": {
                        "max_length": 300,
                        "tone": "professional",
                        "personalization_required": True
                    }
                }
            }
            
            domain = domains.get(domain_name, {})
            
            if not domain:
                return {"error": f"Domain '{domain_name}' not found"}
            
            logger.info(f"Retrieved domain configuration: {domain_name}")
            return domain
            
        except Exception as e:
            logger.error(f"Failed to get domain by name: {e}")
            return {"error": str(e)}
    
    def create_domain_specific_prompt(self, domain_name: str, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a prompt specific to a domain"""
        try:
            domain_config = self.get_domain_by_name(domain_name)
            
            if "error" in domain_config:
                return domain_config
            
            # Apply domain-specific validation rules
            validation_rules = domain_config.get("validation_rules", {})
            
            domain_prompt = {
                "prompt_id": f"{domain_name}_{hash(str(prompt_data)) % 1000}",
                "domain": domain_name,
                "name": prompt_data.get("name", ""),
                "template": prompt_data.get("template", ""),
                "parameters": prompt_data.get("parameters", {}),
                "validation_rules": validation_rules,
                "created_at": datetime.now().isoformat(),
                "specialization": domain_config.get("specialization", "")
            }
            
            logger.info(f"Created domain-specific prompt for {domain_name}")
            return domain_prompt
            
        except Exception as e:
            logger.error(f"Failed to create domain-specific prompt: {e}")
            return {"error": str(e)}
    
    def list_all_domains(self) -> List[Dict[str, Any]]:
        """List all available prompt domains"""
        try:
            all_domains = [
                {
                    "domain_id": "domain_resume",
                    "domain_name": "resume",
                    "specialization": "resume_generation_optimization",
                    "prompt_count": 15,
                    "active": True
                },
                {
                    "domain_id": "domain_outreach",
                    "domain_name": "outreach",
                    "specialization": "professional_communication",
                    "prompt_count": 12,
                    "active": True
                },
                {
                    "domain_id": "domain_general",
                    "domain_name": "general",
                    "specialization": "general_purpose",
                    "prompt_count": 8,
                    "active": True
                }
            ]
            
            logger.info(f"Listed {len(all_domains)} domains")
            return all_domains
            
        except Exception as e:
            logger.error(f"Failed to list domains: {e}")
            return []

def create_prompt_domain(config: Optional[Dict[str, Any]] = None) -> PromptDomain:
    """Factory function to create prompt domain instance"""
    return PromptDomain(config)

# Re-export components
__all__ = [
    'PromptDomain', 'create_prompt_domain'
]
