"""
Personalization Engine Service
LEVEL 5 - Service for personalizing outreach messages based on recipient data
"""

from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime
import logging
import re

@dataclass
class PersonalizationResult:
    """Result of personalization analysis"""
    personalization_score: float
    personalization_elements: List[str]
    recommendations: List[str]
    enriched_content: Dict[str, Any]
    metadata: Dict[str, Any]

class PersonalizationEngine:
    """Service for enriching outreach messages with personalization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Personalization strategies
        self.personalization_strategies = {
            "name_mention": {"weight": 0.2, "required": True},
            "company_reference": {"weight": 0.15, "required": False},
            "role_reference": {"weight": 0.15, "required": False},
            "industry_context": {"weight": 0.1, "required": False},
            "mutual_connections": {"weight": 0.15, "required": False},
            "shared_interests": {"weight": 0.1, "required": False},
            "recent_activity": {"weight": 0.1, "required": False},
            "background_alignment": {"weight": 0.05, "required": False}
        }
        
        # Personalization templates
        self.personalization_templates = {
            "name_mention": [
                "Hi {name},",
                "Hello {name},",
                "Dear {name},",
                "{name},"
            ],
            "company_reference": [
                "I've been following {company}'s work",
                "The innovations at {company} are impressive",
                "{company} is doing amazing work in {industry}",
                "I admire what {company} has accomplished"
            ],
            "role_reference": [
                "As a {role}, you understand the importance of",
                "Your experience as {role} would be valuable for",
                "Given your background as {role}",
                "With your expertise as {role}"
            ],
            "mutual_connections": [
                "I noticed we're both connected with {connection}",
                "We share a connection in {connection}",
                "Through our mutual connection {connection}",
                "{connection} suggested I reach out"
            ],
            "shared_interests": [
                "I see we share an interest in {interest}",
                "Our shared interest in {interest} caught my attention",
                "Given our mutual interest in {interest}",
                "I was excited to see we're both interested in {interest}"
            ]
        }
        
        # Industry-specific personalization data
        self.industry_contexts = {
            "technology": {
                "topics": ["innovation", "digital transformation", "scalability", "efficiency"],
                "challenges": ["talent acquisition", "technical debt", "scalability", "security"],
                "opportunities": ["automation", "AI integration", "cloud migration", "optimization"]
            },
            "healthcare": {
                "topics": ["patient care", "efficiency", "compliance", "innovation"],
                "challenges": ["regulatory compliance", "cost reduction", "patient outcomes"],
                "opportunities": ["digital health", "telemedicine", "data analytics", "automation"]
            },
            "finance": {
                "topics": ["risk management", "compliance", "efficiency", "security"],
                "challenges": ["regulatory changes", "cybersecurity", "customer experience"],
                "opportunities": ["fintech", "automation", "data analytics", "digital transformation"]
            },
            "education": {
                "topics": ["student outcomes", "efficiency", "accessibility", "innovation"],
                "challenges": ["budget constraints", "remote learning", "engagement"],
                "opportunities": ["edtech", "personalized learning", "analytics", "accessibility"]
            }
        }
    
    async def personalize_message(
        self,
        base_content: Dict[str, str],
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> PersonalizationResult:
        """
        Personalize outreach message based on recipient data
        
        Args:
            base_content: Base message content (subject, body, call_to_action)
            recipient_profile: Information about the recipient
            sender_profile: Information about the sender
            context: Additional context for personalization
            preferences: User preferences
            
        Returns:
            Personalization result with enriched content and metadata
        """
        try:
            self.logger.info("Personalizing outreach message")
            
            # Analyze available personalization data
            personalization_data = await self._analyze_personalization_data(recipient_profile, context)
            
            # Generate personalization elements
            personalization_elements = await self._generate_personalization_elements(
                personalization_data, recipient_profile, sender_profile
            )
            
            # Enrich content with personalization
            enriched_content = await self._enrich_content(
                base_content, personalization_elements, preferences
            )
            
            # Calculate personalization score
            personalization_score = await self._calculate_personalization_score(
                personalization_elements, personalization_data
            )
            
            # Generate recommendations
            recommendations = await self._generate_personalization_recommendations(
                personalization_data, personalization_elements
            )
            
            # Generate metadata
            metadata = await self._generate_personalization_metadata(
                personalization_data, personalization_elements, personalization_score
            )
            
            return PersonalizationResult(
                personalization_score=personalization_score,
                personalization_elements=personalization_elements,
                recommendations=recommendations,
                enriched_content=enriched_content,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error personalizing message: {e}")
            raise e
    
    async def _analyze_personalization_data(
        self,
        recipient_profile: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze available personalization data"""
        personalization_data = {}
        
        # Basic recipient information
        personalization_data["name"] = recipient_profile.get("name", "")
        personalization_data["company"] = recipient_profile.get("company", "")
        personalization_data["role"] = recipient_profile.get("role", "")
        personalization_data["industry"] = recipient_profile.get("industry", "")
        
        # Extended profile information
        background = recipient_profile.get("background", {})
        personalization_data["experience_years"] = background.get("experience_years", 0)
        personalization_data["education"] = background.get("education", "")
        personalization_data["skills"] = background.get("skills", [])
        personalization_data["achievements"] = background.get("achievements", [])
        
        # Context information
        if context:
            personalization_data["mutual_connections"] = context.get("mutual_connections", [])
            personalization_data["shared_interests"] = context.get("shared_interests", [])
            personalization_data["relationship"] = context.get("relationship", "stranger")
            personalization_data["previous_contact"] = context.get("previous_contact", {})
            personalization_data["purpose"] = context.get("purpose", "")
        
        # Calculate data quality score
        data_quality = await self._calculate_data_quality(personalization_data)
        personalization_data["data_quality_score"] = data_quality
        
        return personalization_data
    
    async def _generate_personalization_elements(
        self,
        personalization_data: Dict[str, Any],
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalization elements based on available data"""
        elements = []
        
        # Name mention (always include if available)
        if personalization_data.get("name"):
            elements.append({
                "type": "name_mention",
                "template": "Hi {name},",
                "value": personalization_data["name"],
                "weight": self.personalization_strategies["name_mention"]["weight"]
            })
        
        # Company reference
        if personalization_data.get("company"):
            company = personalization_data["company"]
            industry = personalization_data.get("industry", "")
            template = self._select_template("company_reference", company, industry)
            elements.append({
                "type": "company_reference",
                "template": template,
                "value": company,
                "weight": self.personalization_strategies["company_reference"]["weight"]
            })
        
        # Role reference
        if personalization_data.get("role"):
            role = personalization_data["role"]
            template = self._select_template("role_reference", role)
            elements.append({
                "type": "role_reference",
                "template": template,
                "value": role,
                "weight": self.personalization_strategies["role_reference"]["weight"]
            })
        
        # Mutual connections
        if personalization_data.get("mutual_connections"):
            connections = personalization_data["mutual_connections"][:2]  # Limit to 2
            for connection in connections:
                template = self._select_template("mutual_connections", connection)
                elements.append({
                    "type": "mutual_connections",
                    "template": template,
                    "value": connection,
                    "weight": self.personalization_strategies["mutual_connections"]["weight"]
                })
        
        # Shared interests
        if personalization_data.get("shared_interests"):
            interests = personalization_data["shared_interests"][:2]  # Limit to 2
            for interest in interests:
                template = self._select_template("shared_interests", interest)
                elements.append({
                    "type": "shared_interests",
                    "template": template,
                    "value": interest,
                    "weight": self.personalization_strategies["shared_interests"]["weight"]
                })
        
        # Industry context
        if personalization_data.get("industry"):
            industry = personalization_data["industry"]
            context_elements = await self._generate_industry_context(industry, personalization_data)
            elements.extend(context_elements)
        
        # Experience-based personalization
        if personalization_data.get("experience_years", 0) > 5:
            elements.append({
                "type": "experience_reference",
                "template": "With your extensive experience",
                "value": f"{personalization_data['experience_years']} years",
                "weight": 0.05
            })
        
        return elements
    
    def _select_template(self, element_type: str, value: str, context: str = "") -> str:
        """Select appropriate template for personalization element"""
        templates = self.personalization_templates.get(element_type, [])
        
        if not templates:
            return f"{value}"
        
        # Simple template selection - in production, this would be more sophisticated
        if element_type == "company_reference" and context:
            return templates[2].format(company=value, industry=context)
        else:
            return templates[0].format(name=value, company=value, role=value, 
                                    connection=value, interest=value)
    
    async def _generate_industry_context(
        self,
        industry: str,
        personalization_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate industry-specific personalization elements"""
        elements = []
        
        industry_data = self.industry_contexts.get(industry.lower(), {})
        if not industry_data:
            return elements
        
        # Add industry-specific topics
        topics = industry_data.get("topics", [])
        if topics:
            elements.append({
                "type": "industry_context",
                "template": f"Given the focus on {topics[0]} in the {industry} industry",
                "value": topics[0],
                "weight": 0.05
            })
        
        return elements
    
    async def _enrich_content(
        self,
        base_content: Dict[str, str],
        personalization_elements: List[Dict[str, Any]],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Enrich base content with personalization elements"""
        enriched_content = base_content.copy()
        
        # Get personalization level preference
        personalization_level = preferences.get("personalization_level", "moderate") if preferences else "moderate"
        
        # Determine how many elements to include
        if personalization_level == "minimal":
            max_elements = 1
        elif personalization_level == "moderate":
            max_elements = 3
        else:  # extensive
            max_elements = 5
        
        # Sort elements by weight and select top ones
        sorted_elements = sorted(personalization_elements, key=lambda x: x["weight"], reverse=True)
        selected_elements = sorted_elements[:max_elements]
        
        # Apply personalization to content
        enriched_content = await self._apply_personalization_to_content(
            enriched_content, selected_elements
        )
        
        return enriched_content
    
    async def _apply_personalization_to_content(
        self,
        content: Dict[str, str],
        elements: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Apply personalization elements to content"""
        enriched = content.copy()
        
        # Apply name to opening
        name_elements = [e for e in elements if e["type"] == "name_mention"]
        if name_elements:
            name_element = name_elements[0]
            if "body" in enriched:
                enriched["body"] = name_element["template"] + "\n\n" + enriched["body"]
        
        # Apply other elements to body
        other_elements = [e for e in elements if e["type"] != "name_mention"]
        for element in other_elements[:3]:  # Limit to 3 additional elements
            if "body" in enriched:
                enriched["body"] = element["template"] + " " + enriched["body"]
        
        # Update subject if needed
        if "subject" in enriched and other_elements:
            # Add personalization to subject
            subject = enriched["subject"]
            if len(subject) < 80:  # Only add if subject is short enough
                company_elements = [e for e in elements if e["type"] == "company_reference"]
                if company_elements:
                    enriched["subject"] = f"{subject} | {company_elements[0]['value']}"
        
        return enriched
    
    async def _calculate_personalization_score(
        self,
        personalization_elements: List[Dict[str, Any]],
        personalization_data: Dict[str, Any]
    ) -> float:
        """Calculate overall personalization score"""
        if not personalization_elements:
            return 0.0
        
        # Base score from elements
        element_score = sum(element["weight"] for element in personalization_elements)
        
        # Quality score from data
        quality_score = personalization_data.get("data_quality_score", 0.5)
        
        # Diversity score (different types of personalization)
        element_types = set(element["type"] for element in personalization_elements)
        diversity_score = len(element_types) / len(self.personalization_strategies)
        
        # Weighted combination
        overall_score = (element_score * 0.5 + quality_score * 0.3 + diversity_score * 0.2)
        
        return min(overall_score, 1.0)
    
    async def _generate_personalization_recommendations(
        self,
        personalization_data: Dict[str, Any],
        personalization_elements: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for improving personalization"""
        recommendations = []
        
        # Check for missing required elements
        element_types = set(element["type"] for element in personalization_elements)
        
        if "name_mention" not in element_types:
            recommendations.append("Add recipient's name for better personalization")
        
        if personalization_data.get("company") and "company_reference" not in element_types:
            recommendations.append("Reference recipient's company to show research")
        
        if personalization_data.get("role") and "role_reference" not in element_types:
            recommendations.append("Mention recipient's role to demonstrate relevance")
        
        if not personalization_data.get("mutual_connections") and "mutual_connections" not in element_types:
            recommendations.append("Look for mutual connections to strengthen rapport")
        
        if not personalization_data.get("shared_interests"):
            recommendations.append("Research shared interests or background for stronger connection")
        
        # Data quality recommendations
        if personalization_data.get("data_quality_score", 0) < 0.5:
            recommendations.append("Gather more detailed recipient information for better personalization")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _generate_personalization_metadata(
        self,
        personalization_data: Dict[str, Any],
        personalization_elements: List[Dict[str, Any]],
        personalization_score: float
    ) -> Dict[str, Any]:
        """Generate metadata for personalization process"""
        return {
            "personalization_score": personalization_score,
            "elements_used": len(personalization_elements),
            "element_types": [element["type"] for element in personalization_elements],
            "data_quality_score": personalization_data.get("data_quality_score", 0),
            "personalization_timestamp": datetime.utcnow().isoformat(),
            "available_data_fields": [key for key, value in personalization_data.items() if value],
            "personalization_strategies": list(self.personalization_strategies.keys())
        }
    
    async def _calculate_data_quality(self, personalization_data: Dict[str, Any]) -> float:
        """Calculate quality score of available personalization data"""
        quality_score = 0.0
        total_fields = 0
        
        # Essential fields
        essential_fields = ["name", "company", "role"]
        for field in essential_fields:
            total_fields += 1
            if personalization_data.get(field):
                quality_score += 0.3
        
        # Optional fields
        optional_fields = ["industry", "experience_years", "education", "skills", "achievements"]
        for field in optional_fields:
            total_fields += 1
            if personalization_data.get(field):
                quality_score += 0.1
        
        # Context fields
        context_fields = ["mutual_connections", "shared_interests", "purpose"]
        for field in context_fields:
            total_fields += 1
            if personalization_data.get(field):
                quality_score += 0.15
        
        return quality_score / total_fields if total_fields > 0 else 0.0

__all__ = ["PersonalizationEngine", "PersonalizationResult"]
