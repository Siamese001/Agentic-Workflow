"""
Template Generator Service
LEVEL 5 - Service for generating and managing outreach message templates
"""

from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime
import logging
import json

@dataclass
class Template:
    """Represents an outreach message template"""
    template_id: str
    template_type: str
    name: str
    description: str
    content: Dict[str, str]
    variables: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class TemplateGenerator:
    """Service for generating and managing outreach message templates"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Template categories and their characteristics
        self.template_categories = {
            "introduction": {
                "purpose": "Initial outreach to new contacts",
                "tone": "professional",
                "length": "medium",
                "required_sections": ["opening", "context", "call_to_action"]
            },
            "follow_up": {
                "purpose": "Following up on previous contact",
                "tone": "friendly",
                "length": "brief",
                "required_sections": ["opening", "reference", "call_to_action"]
            },
            "networking": {
                "purpose": "Building professional network",
                "tone": "casual",
                "length": "brief",
                "required_sections": ["opening", "connection", "call_to_action"]
            },
            "collaboration": {
                "purpose": "Proposing collaboration opportunities",
                "tone": "professional",
                "length": "detailed",
                "required_sections": ["opening", "value_proposition", "details", "call_to_action"]
            },
            "referral_request": {
                "purpose": "Requesting referrals or introductions",
                "tone": "respectful",
                "length": "medium",
                "required_sections": ["opening", "request", "context", "call_to_action"]
            }
        }
        
        # Base template library
        self.base_templates = {
            "professional_introduction": Template(
                template_id="prof_intro_001",
                template_type="introduction",
                name="Professional Introduction",
                description="Formal introduction for professional outreach",
                content={
                    "subject": "Professional Connection | {industry}",
                    "opening": "Dear {recipient_name},",
                    "body": "I hope this message finds you well. I am writing to you as a {sender_role} with expertise in {sender_expertise}. I came across your profile as {recipient_role} at {recipient_company} and was impressed by your work in the {industry} space.\n\nGiven our shared professional interests, I believe there could be valuable opportunities for us to connect and potentially collaborate on {topic}.",
                    "call_to_action": "Would you be open to a brief call next week to discuss potential synergies?",
                    "closing": "Best regards,\n{sender_name}"
                },
                variables=["recipient_name", "sender_role", "sender_expertise", "recipient_role", "recipient_company", "industry", "topic", "sender_name"],
                metadata={"tone": "formal", "length": "medium", "best_for": ["cold_outreach", "professional_networking"]},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            "friendly_networking": Template(
                template_id="friendly_net_001",
                template_type="networking",
                name="Friendly Networking",
                description="Casual networking message for building connections",
                content={
                    "subject": "Connection Request | {shared_interest}",
                    "opening": "Hi {recipient_name},",
                    "body": "I came across your profile and noticed we share an interest in {shared_interest}. As a {sender_role} working in {industry}, I'm always excited to connect with fellow professionals who are passionate about similar topics.\n\nI'd love to learn more about your work and share some insights from my experience in {sender_expertise}.",
                    "call_to_action": "Would you be open to connecting and discussing our shared interests?",
                    "closing": "Best,\n{sender_name}"
                },
                variables=["recipient_name", "shared_interest", "sender_role", "industry", "sender_expertise", "sender_name"],
                metadata={"tone": "friendly", "length": "brief", "best_for": ["networking", "linkedin"]},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            "collaboration_proposal": Template(
                template_id="collab_prop_001",
                template_type="collaboration",
                name="Collaboration Proposal",
                description="Detailed proposal for collaboration opportunities",
                content={
                    "subject": "Collaboration Opportunity: {project_type}",
                    "opening": "Dear {recipient_name},",
                    "body": "I am reaching out to you today with an exciting collaboration opportunity. As a {sender_role} with extensive experience in {sender_expertise}, I have been following the innovative work at {recipient_company}, particularly your contributions as {recipient_role}.\n\nI believe there is significant potential for us to collaborate on {project_type}. My background in {specific_expertise} complements your team's strengths in {recipient_strengths}, and together we could achieve {potential_outcome}.\n\nThe collaboration would involve {collaboration_details} and could benefit both our organizations through {mutual_benefits}.",
                    "call_to_action": "Would you be available for a detailed discussion next week to explore this collaboration further?",
                    "closing": "Looking forward to your response,\n{sender_name}"
                },
                variables=["recipient_name", "sender_role", "sender_expertise", "recipient_company", "recipient_role", "project_type", "specific_expertise", "recipient_strengths", "potential_outcome", "collaboration_details", "mutual_benefits", "sender_name"],
                metadata={"tone": "professional", "length": "detailed", "best_for": ["partnership", "business_development"]},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            "follow_up_connection": Template(
                template_id="follow_up_001",
                template_type="follow_up",
                name="Follow Up Connection",
                description="Follow-up message after initial contact",
                content={
                    "subject": "Following up on our conversation",
                    "opening": "Hi {recipient_name},",
                    "body": "I hope you're having a great week. I wanted to follow up on our recent discussion about {topic}. I've been thinking about the points we covered, particularly {specific_point}.\n\nI wanted to share that {additional_info} and see if you'd be interested in continuing our conversation.",
                    "call_to_action": "Would you have time for a brief follow-up call this week?",
                    "closing": "Best,\n{sender_name}"
                },
                variables=["recipient_name", "topic", "specific_point", "additional_info", "sender_name"],
                metadata={"tone": "friendly", "length": "brief", "best_for": ["follow_up", "relationship_building"]},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            "referral_request": Template(
                template_id="referral_req_001",
                template_type="referral_request",
                name="Referral Request",
                description="Request for referral or introduction",
                content={
                    "subject": "Introduction request | {target_company}",
                    "opening": "Hi {recipient_name},",
                    "body": "I hope this message finds you well. I'm reaching out because I'm currently exploring opportunities at {target_company}, and I noticed you might have connections there.\n\nGiven your experience in {industry} and our professional relationship, I was hoping you might be able to provide an introduction to {target_person} or someone in the {target_department} department.\n\nI'm particularly interested in {opportunity_details} and believe my background in {sender_expertise} would be valuable to their team.",
                    "call_to_action": "Would you be comfortable making an introduction or providing a referral?",
                    "closing": "Thank you for your consideration,\n{sender_name}"
                },
                variables=["recipient_name", "target_company", "industry", "target_person", "target_department", "opportunity_details", "sender_expertise", "sender_name"],
                metadata={"tone": "respectful", "length": "medium", "best_for": ["job_search", "business_development"]},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        }
    
    async def generate_template(
        self,
        template_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> Template:
        """
        Generate a new template based on type and context
        
        Args:
            template_type: Type of template to generate
            context: Context information for template generation
            preferences: User preferences for template style
            
        Returns:
            Generated template
        """
        try:
            self.logger.info(f"Generating template of type: {template_type}")
            
            # Get base template or create new one
            base_template = await self._get_base_template(template_type, context)
            
            # Customize template based on context
            customized_template = await self._customize_template(base_template, context, preferences)
            
            # Validate template
            validated_template = await self._validate_template(customized_template)
            
            return validated_template
            
        except Exception as e:
            self.logger.error(f"Error generating template: {e}")
            raise e
    
    async def get_template_by_id(self, template_id: str) -> Optional[Template]:
        """Get template by ID"""
        return self.base_templates.get(template_id)
    
    async def get_templates_by_type(self, template_type: str) -> List[Template]:
        """Get all templates of a specific type"""
        return [
            template for template in self.base_templates.values()
            if template.template_type == template_type
        ]
    
    async def get_templates_by_category(self, category: str) -> List[Template]:
        """Get templates by category"""
        # Map categories to template types
        category_mapping = {
            "introduction": ["introduction"],
            "networking": ["networking"],
            "collaboration": ["collaboration"],
            "follow_up": ["follow_up"],
            "referral": ["referral_request"]
        }
        
        template_types = category_mapping.get(category, [])
        return [
            template for template in self.base_templates.values()
            if template.template_type in template_types
        ]
    
    async def customize_template(
        self,
        template: Template,
        customizations: Dict[str, Any]
    ) -> Template:
        """Customize an existing template"""
        
        # Create a copy of the template
        customized = Template(
            template_id=f"{template.template_id}_custom_{datetime.utcnow().timestamp()}",
            template_type=template.template_type,
            name=f"{template.name} (Customized)",
            description=template.description,
            content=template.content.copy(),
            variables=template.variables.copy(),
            metadata=template.metadata.copy(),
            created_at=template.created_at,
            updated_at=datetime.utcnow()
        )
        
        # Apply customizations
        if "tone" in customizations:
            customized.metadata["tone"] = customizations["tone"]
            customized.content = await self._adjust_tone(customized.content, customizations["tone"])
        
        if "length" in customizations:
            customized.metadata["length"] = customizations["length"]
            customized.content = await self._adjust_length(customized.content, customizations["length"])
        
        if "additional_variables" in customizations:
            customized.variables.extend(customizations["additional_variables"])
        
        return customized
    
    async def _get_base_template(
        self,
        template_type: str,
        context: Dict[str, Any] = None
    ) -> Template:
        """Get base template for the given type"""
        
        # Find appropriate base template
        templates_of_type = [
            template for template in self.base_templates.values()
            if template.template_type == template_type
        ]
        
        if not templates_of_type:
            # Create a generic template if none exists
            return await self._create_generic_template(template_type, context)
        
        # Select best template based on context
        if context:
            best_template = await self._select_best_template(templates_of_type, context)
        else:
            best_template = templates_of_type[0]
        
        return best_template
    
    async def _create_generic_template(
        self,
        template_type: str,
        context: Dict[str, Any] = None
    ) -> Template:
        """Create a generic template for the given type"""
        
        category_config = self.template_categories.get(template_type, self.template_categories["introduction"])
        
        generic_content = {
            "subject": f"Professional Connection | {{industry}}",
            "opening": "Hi {recipient_name},",
            "body": f"I am reaching out as a {{sender_role}} with expertise in {{sender_expertise}}. I came across your profile and was interested in connecting regarding {{topic}}.",
            "call_to_action": "Would you be open to a discussion about this?",
            "closing": "Best,\n{sender_name}"
        }
        
        return Template(
            template_id=f"generic_{template_type}_{datetime.utcnow().timestamp()}",
            template_type=template_type,
            name=f"Generic {template_type.title()}",
            description=f"Generic template for {template_type}",
            content=generic_content,
            variables=["recipient_name", "sender_role", "sender_expertise", "topic", "sender_name", "industry"],
            metadata={
                "tone": category_config["tone"],
                "length": category_config["length"],
                "best_for": [template_type]
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    async def _select_best_template(
        self,
        templates: List[Template],
        context: Dict[str, Any]
    ) -> Template:
        """Select the best template based on context"""
        
        # Simple selection based on tone preference
        preferred_tone = context.get("tone", "professional")
        
        for template in templates:
            if template.metadata.get("tone") == preferred_tone:
                return template
        
        # If no exact match, return first template
        return templates[0]
    
    async def _customize_template(
        self,
        template: Template,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> Template:
        """Customize template based on context and preferences"""
        
        customized = Template(
            template_id=f"{template.template_id}_custom_{datetime.utcnow().timestamp()}",
            template_type=template.template_type,
            name=template.name,
            description=template.description,
            content=template.content.copy(),
            variables=template.variables.copy(),
            metadata=template.metadata.copy(),
            created_at=template.created_at,
            updated_at=datetime.utcnow()
        )
        
        # Apply context-based customizations
        if context:
            if "industry" in context:
                customized.content["subject"] = customized.content["subject"].replace("{industry}", context["industry"])
            
            if "urgency" in context and context["urgency"] == "high":
                customized.content["subject"] = "Urgent: " + customized.content["subject"]
        
        # Apply preference-based customizations
        if preferences:
            if "tone" in preferences:
                customized.content = await self._adjust_tone(customized.content, preferences["tone"])
                customized.metadata["tone"] = preferences["tone"]
            
            if "length" in preferences:
                customized.content = await self._adjust_length(customized.content, preferences["length"])
                customized.metadata["length"] = preferences["length"]
        
        return customized
    
    async def _adjust_tone(self, content: Dict[str, str], tone: str) -> Dict[str, str]:
        """Adjust content tone"""
        adjusted = content.copy()
        
        if tone == "formal":
            adjusted["opening"] = adjusted["opening"].replace("Hi", "Dear")
            adjusted["closing"] = adjusted["closing"].replace("Best,", "Best regards,")
        elif tone == "casual":
            adjusted["opening"] = adjusted["opening"].replace("Dear", "Hi")
            adjusted["closing"] = adjusted["closing"].replace("Best regards,", "Best,")
        
        return adjusted
    
    async def _adjust_length(self, content: Dict[str, str], length: str) -> Dict[str, str]:
        """Adjust content length"""
        adjusted = content.copy()
        
        if length == "brief":
            # Shorten body content
            body = adjusted["body"]
            sentences = body.split(". ")
            if len(sentences) > 2:
                adjusted["body"] = ". ".join(sentences[:2]) + "."
        
        elif length == "detailed":
            # Add more detail to body
            body = adjusted["body"]
            additional_detail = "\n\nI believe this collaboration could lead to significant mutual benefits and professional growth."
            adjusted["body"] = body + additional_detail
        
        return adjusted
    
    async def _validate_template(self, template: Template) -> Template:
        """Validate template structure and content"""
        
        # Check required sections
        category_config = self.template_categories.get(template.template_type, {})
        required_sections = category_config.get("required_sections", [])
        
        content = template.content
        
        # Map required sections to content keys
        section_mapping = {
            "opening": "opening",
            "context": "body",
            "value_proposition": "body",
            "reference": "body",
            "connection": "body",
            "details": "body",
            "request": "body",
            "call_to_action": "call_to_action"
        }
        
        for required_section in required_sections:
            content_key = section_mapping.get(required_section)
            if content_key and content_key not in content:
                raise ValueError(f"Template missing required section: {required_section}")
        
        # Validate variables
        content_text = " ".join(content.values())
        for variable in template.variables:
            if f"{{{variable}}}" not in content_text:
                self.logger.warning(f"Template variable {variable} not found in content")
        
        return template
    
    async def get_template_recommendations(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> List[Template]:
        """Get recommended templates based on profiles and context"""
        
        recommendations = []
        
        # Analyze context to determine best template types
        if context and context.get("purpose"):
            purpose = context["purpose"].lower()
            
            if "collaboration" in purpose:
                template_types = ["collaboration", "introduction"]
            elif "networking" in purpose:
                template_types = ["networking", "introduction"]
            elif "follow_up" in purpose:
                template_types = ["follow_up"]
            elif "referral" in purpose or "introduction" in purpose:
                template_types = ["referral_request"]
            else:
                template_types = ["introduction"]
        else:
            template_types = ["introduction", "networking"]
        
        # Get templates of recommended types
        for template_type in template_types:
            templates = await self.get_templates_by_type(template_type)
            recommendations.extend(templates)
        
        # Sort by relevance (simple heuristic)
        recommendations.sort(key=lambda t: len(t.variables), reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations

__all__ = ["TemplateGenerator", "Template"]
