"""
Relationship Analyzer Service
LEVEL 5 - Service for analyzing and leveraging relationships in outreach
"""

from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

@dataclass
class RelationshipAnalysis:
    """Result of relationship analysis"""
    relationship_strength: float
    relationship_type: str
    connection_pathways: List[str]
    trust_indicators: List[str]
    engagement_recommendations: List[str]
    metadata: Dict[str, Any]

class RelationshipAnalyzer:
    """Service for analyzing relationships and optimizing outreach approach"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Relationship types and their characteristics
        self.relationship_types = {
            "stranger": {
                "strength_range": (0.0, 0.2),
                "approach": "formal_introduction",
                "trust_level": "low",
                "engagement_strategy": "value_first"
            },
            "acquaintance": {
                "strength_range": (0.2, 0.4),
                "approach": "contextual_reference",
                "trust_level": "medium_low",
                "engagement_strategy": "mutual_connection"
            },
            "colleague": {
                "strength_range": (0.4, 0.6),
                "approach": "professional_context",
                "trust_level": "medium",
                "engagement_strategy": "collaboration_focus"
            },
            "former_colleague": {
                "strength_range": (0.5, 0.7),
                "approach": "shared_experience",
                "trust_level": "medium_high",
                "engagement_strategy": "reconnection"
            },
            "friend": {
                "strength_range": (0.7, 0.9),
                "approach": "casual_friendly",
                "trust_level": "high",
                "engagement_strategy": "personal_connection"
            },
            "mentor": {
                "strength_range": (0.6, 0.8),
                "approach": "respectful_learning",
                "trust_level": "high",
                "engagement_strategy": "guidance_seeking"
            },
            "mentee": {
                "strength_range": (0.6, 0.8),
                "approach": "guidance_offering",
                "trust_level": "high",
                "engagement_strategy": "mentorship_opportunity"
            }
        }
        
        # Trust indicators
        self.trust_indicators = {
            "mutual_connections": {
                "weight": 0.3,
                "threshold": 1,
                "indicators": ["shared_network", "verified_connections"]
            },
            "shared_background": {
                "weight": 0.2,
                "threshold": 1,
                "indicators": ["same_company", "alumni", "industry_peer"]
            },
            "previous_interactions": {
                "weight": 0.25,
                "threshold": 1,
                "indicators": ["past_communication", "event_attendance", "project_collaboration"]
            },
            "endorsements": {
                "weight": 0.15,
                "threshold": 1,
                "indicators": ["recommendations", "skill_endorsements", "public_praise"]
            },
            "social_proof": {
                "weight": 0.1,
                "threshold": 1,
                "indicators": ["mutual_groups", "shared_interests", "industry_recognition"]
            }
        }
        
        # Connection pathways
        self.connection_pathways = {
            "direct": {
                "effectiveness": 0.9,
                "description": "Direct connection or previous interaction"
            },
            "mutual_connection": {
                "effectiveness": 0.7,
                "description": "Connection through mutual acquaintance"
            },
            "shared_background": {
                "effectiveness": 0.6,
                "description": "Shared company, school, or industry"
            },
            "professional_network": {
                "effectiveness": 0.5,
                "description": "Connection through professional associations"
            },
            "cold_outreach": {
                "effectiveness": 0.3,
                "description": "No prior connection or pathway"
            }
        }
    
    async def analyze_relationship(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None,
        interaction_history: List[Dict[str, Any]] = None
    ) -> RelationshipAnalysis:
        """
        Analyze relationship between sender and recipient
        
        Args:
            recipient_profile: Information about the recipient
            sender_profile: Information about the sender
            context: Additional context about the relationship
            interaction_history: History of previous interactions
            
        Returns:
            Comprehensive relationship analysis
        """
        try:
            self.logger.info("Analyzing sender-recipient relationship")
            
            # Determine relationship type and strength
            relationship_type, relationship_strength = await self._determine_relationship_type(
                recipient_profile, sender_profile, context, interaction_history
            )
            
            # Identify connection pathways
            connection_pathways = await self._identify_connection_pathways(
                recipient_profile, sender_profile, context
            )
            
            # Analyze trust indicators
            trust_indicators = await self._analyze_trust_indicators(
                recipient_profile, sender_profile, context, interaction_history
            )
            
            # Generate engagement recommendations
            engagement_recommendations = await self._generate_engagement_recommendations(
                relationship_type, relationship_strength, trust_indicators, connection_pathways
            )
            
            # Generate metadata
            metadata = await self._generate_relationship_metadata(
                relationship_type, relationship_strength, connection_pathways, trust_indicators
            )
            
            return RelationshipAnalysis(
                relationship_strength=relationship_strength,
                relationship_type=relationship_type,
                connection_pathways=connection_pathways,
                trust_indicators=trust_indicators,
                engagement_recommendations=engagement_recommendations,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing relationship: {e}")
            raise e
    
    async def _determine_relationship_type(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None,
        interaction_history: List[Dict[str, Any]] = None
    ) -> tuple[str, float]:
        """Determine relationship type and strength"""
        
        # Start with context-provided relationship
        if context and context.get("relationship"):
            stated_relationship = context["relationship"].lower()
            if stated_relationship in self.relationship_types:
                relationship_config = self.relationship_types[stated_relationship]
                strength_range = relationship_config["strength_range"]
                base_strength = sum(strength_range) / 2
                return stated_relationship, base_strength
        
        # Analyze from profiles and history
        strength_score = 0.0
        
        # Check for shared company
        if (recipient_profile.get("company") == sender_profile.get("company") and 
            recipient_profile.get("company")):
            strength_score += 0.3
        
        # Check for shared education
        recipient_education = recipient_profile.get("background", {}).get("education", "")
        sender_education = sender_profile.get("background", {}).get("education", "")
        if recipient_education and sender_education and recipient_education == sender_education:
            strength_score += 0.2
        
        # Check interaction history
        if interaction_history:
            recent_interactions = [
                interaction for interaction in interaction_history
                if self._is_recent_interaction(interaction)
            ]
            strength_score += min(len(recent_interactions) * 0.1, 0.3)
        
        # Check mutual connections
        if context and context.get("mutual_connections"):
            mutual_count = len(context["mutual_connections"])
            strength_score += min(mutual_count * 0.05, 0.2)
        
        # Determine relationship type based on strength
        if strength_score >= 0.7:
            return "friend", strength_score
        elif strength_score >= 0.6:
            if interaction_history:
                return "former_colleague", strength_score
            else:
                return "colleague", strength_score
        elif strength_score >= 0.4:
            return "acquaintance", strength_score
        else:
            return "stranger", strength_score
    
    async def _identify_connection_pathways(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> List[str]:
        """Identify available connection pathways"""
        pathways = []
        
        # Direct connection (previous interaction)
        if context and context.get("previous_contact"):
            pathways.append("direct")
        
        # Mutual connections
        if context and context.get("mutual_connections"):
            pathways.append("mutual_connection")
        
        # Shared background
        if (recipient_profile.get("company") == sender_profile.get("company") and 
            recipient_profile.get("company")):
            pathways.append("shared_background")
        
        # Shared education
        recipient_education = recipient_profile.get("background", {}).get("education", "")
        sender_education = sender_profile.get("background", {}).get("education", "")
        if recipient_education and sender_education and recipient_education == sender_education:
            pathways.append("shared_background")
        
        # Shared industry
        if (recipient_profile.get("industry") == sender_profile.get("industry") and 
            recipient_profile.get("industry")):
            pathways.append("professional_network")
        
        # Shared interests
        if context and context.get("shared_interests"):
            pathways.append("professional_network")
        
        # Default to cold outreach if no pathways found
        if not pathways:
            pathways.append("cold_outreach")
        
        return pathways
    
    async def _analyze_trust_indicators(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None,
        interaction_history: List[Dict[str, Any]] = None
    ) -> List[str]:
        """Analyze trust indicators for the relationship"""
        indicators = []
        
        # Mutual connections trust
        if context and context.get("mutual_connections"):
            mutual_count = len(context["mutual_connections"])
            if mutual_count >= 3:
                indicators.append("strong_mutual_network")
            elif mutual_count >= 1:
                indicators.append("verified_connections")
        
        # Shared background trust
        if (recipient_profile.get("company") == sender_profile.get("company") and 
            recipient_profile.get("company")):
            indicators.append("same_company")
        
        # Previous interactions trust
        if interaction_history:
            positive_interactions = [
                interaction for interaction in interaction_history
                if interaction.get("sentiment") == "positive"
            ]
            if len(positive_interactions) >= 2:
                indicators.append("positive_history")
            elif interaction_history:
                indicators.append("past_communication")
        
        # Professional credibility
        if recipient_profile.get("background", {}).get("achievements"):
            indicators.append("industry_recognition")
        
        if sender_profile.get("background", {}).get("achievements"):
            indicators.append("sender_credibility")
        
        # Social proof
        if context and context.get("shared_interests"):
            indicators.append("shared_interests")
        
        return indicators
    
    async def _generate_engagement_recommendations(
        self,
        relationship_type: str,
        relationship_strength: float,
        trust_indicators: List[str],
        connection_pathways: List[str]
    ) -> List[str]:
        """Generate recommendations for engaging based on relationship analysis"""
        recommendations = []
        
        # Base recommendations by relationship type
        relationship_config = self.relationship_types.get(relationship_type, {})
        engagement_strategy = relationship_config.get("engagement_strategy", "value_first")
        
        if engagement_strategy == "formal_introduction":
            recommendations.extend([
                "Start with formal introduction and clear purpose",
                "Focus on value proposition and mutual benefit",
                "Keep message concise and professional"
            ])
        elif engagement_strategy == "mutual_connection":
            recommendations.extend([
                "Lead with mutual connection reference",
                "Ask for introduction or warm introduction",
                "Emphasize shared network benefits"
            ])
        elif engagement_strategy == "collaboration_focus":
            recommendations.extend([
                "Reference shared professional context",
                "Focus on collaboration opportunities",
                "Use industry-specific language and insights"
            ])
        elif engagement_strategy == "reconnection":
            recommendations.extend([
                "Reference shared past experience positively",
                "Acknowledge time passed and express interest in reconnecting",
                "Focus on how you can help each other now"
            ])
        elif engagement_strategy == "personal_connection":
            recommendations.extend([
                "Use friendly, conversational tone",
                "Reference personal connection or shared experience",
                "Focus on relationship building first"
            ])
        
        # Add pathway-specific recommendations
        if "mutual_connection" in connection_pathways:
            recommendations.append("Request warm introduction through mutual connection")
        
        if "shared_background" in connection_pathways:
            recommendations.append("Leverage shared background as conversation starter")
        
        if "cold_outreach" in connection_pathways:
            recommendations.append("Provide clear, compelling reason for outreach")
            recommendations.append("Demonstrate research and personalization")
        
        # Add trust-based recommendations
        if "strong_mutual_network" in trust_indicators:
            recommendations.append("Leverage network credibility for stronger impact")
        
        if not trust_indicators:
            recommendations.append("Build trust through credibility and value demonstration")
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    async def _generate_relationship_metadata(
        self,
        relationship_type: str,
        relationship_strength: float,
        connection_pathways: List[str],
        trust_indicators: List[str]
    ) -> Dict[str, Any]:
        """Generate metadata for relationship analysis"""
        relationship_config = self.relationship_types.get(relationship_type, {})
        
        # Calculate pathway effectiveness
        pathway_effectiveness = 0.0
        for pathway in connection_pathways:
            pathway_config = self.connection_pathways.get(pathway, {})
            pathway_effectiveness += pathway_config.get("effectiveness", 0.5)
        
        if connection_pathways:
            pathway_effectiveness /= len(connection_pathways)
        
        return {
            "relationship_type": relationship_type,
            "relationship_strength": relationship_strength,
            "trust_level": relationship_config.get("trust_level", "unknown"),
            "approach_style": relationship_config.get("approach", "professional"),
            "connection_pathways": connection_pathways,
            "pathway_effectiveness": pathway_effectiveness,
            "trust_indicators_count": len(trust_indicators),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "engagement_strategy": relationship_config.get("engagement_strategy", "value_first")
        }
    
    def _is_recent_interaction(self, interaction: Dict[str, Any]) -> bool:
        """Check if interaction is recent (within last 6 months)"""
        if not interaction.get("date"):
            return False
        
        try:
            interaction_date = datetime.fromisoformat(interaction["date"])
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            return interaction_date > six_months_ago
        except:
            return False
    
    async def get_relationship_insights(
        self,
        relationship_analysis: RelationshipAnalysis
    ) -> Dict[str, Any]:
        """Get actionable insights from relationship analysis"""
        insights = {
            "optimal_approach": relationship_analysis.metadata.get("approach_style", "professional"),
            "trust_building_actions": [],
            "engagement_tactics": [],
            "success_probability": 0.0
        }
        
        # Calculate success probability
        strength_factor = relationship_analysis.relationship_strength
        pathway_factor = relationship_analysis.metadata.get("pathway_effectiveness", 0.5)
        trust_factor = len(relationship_analysis.trust_indicators) / 5.0  # Normalize to 0-1
        
        insights["success_probability"] = (strength_factor * 0.4 + pathway_factor * 0.4 + trust_factor * 0.2)
        
        # Trust building actions
        if not relationship_analysis.trust_indicators:
            insights["trust_building_actions"] = [
                "Seek warm introduction",
                "Find shared connections",
                "Research recipient's background thoroughly"
            ]
        else:
            insights["trust_building_actions"] = [
                "Leverage existing trust indicators",
                "Reference mutual connections explicitly",
                "Build on shared background"
            ]
        
        # Engagement tactics
        if relationship_analysis.relationship_strength < 0.4:
            insights["engagement_tactics"] = [
                "Focus on value proposition",
                "Keep message concise and professional",
                "Provide clear call to action"
            ]
        else:
            insights["engagement_tactics"] = [
                "Use relationship-appropriate tone",
                "Reference shared experience",
                "Emphasize mutual benefit"
            ]
        
        return insights

__all__ = ["RelationshipAnalyzer", "RelationshipAnalysis"]
