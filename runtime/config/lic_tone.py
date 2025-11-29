#!/usr/bin/env python3
"""
Outreach Engine Tone & Language - Lift & Shift + Enhanced from LIC
Tone rules, technical density scoring, and language matching
"""

from typing import Dict, List, Optional, Any, Tuple
import re
from collections import Counter

from ..models import (
    Archetype, ValidationResult, ValidationSeverity, ToneProfile
)


class TechnicalDensityScorer:
    """Technical density scoring - Enhanced from LIC"""
    
    def __init__(self, tone_rules: Dict[str, Any]):
        self.language_matcher = tone_rules.get("language_matcher", {})
        self.density_config = self.language_matcher.get("technical_density_scoring", {})
        
        # Technical term patterns
        self.technical_patterns = [
            r'\b(?:API|SDK|REST|GraphQL|SQL|NoSQL|JSON|XML|HTML|CSS|JavaScript|Python|Java|C\+\+|React|Vue|Angular|Node\.js|Django|Flask|Spring|\.NET|AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|CI\/CD|Agile|Scrum|DevOps|Microservices|Serverless|Lambda|Kafka|RabbitMQ|Redis|PostgreSQL|MongoDB|Elasticsearch|TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Apache|Nginx|Linux|Unix|Bash|PowerShell)\b',
            r'\b(?:algorithm|architecture|framework|library|database|middleware|frontend|backend|fullstack|authentication|authorization|encryption|deployment|scalability|performance|optimization|refactoring|debugging|testing|monitoring|logging|caching|load balancing|replication|sharding|indexing|query|schema|migration|backup|recovery)\b',
            r'\b\d+(?:\.\d+)?\s*(?:GB|TB|PB|MB|KB|ms|s|min|hrs|GHz|MHz|RAM|CPU|GPU|TPU|cores|threads|requests\/sec|queries\/sec|latency|throughput|uptime|availability|99\.9%|99\.99%|SLA|QPS|RPS)\b'
        ]
    
    def calculate_technical_density(self, text: str) -> float:
        """Calculate technical density score"""
        words = text.split()
        if not words:
            return 0.0
        
        technical_words = set()
        for pattern in self.technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            technical_words.update(match.lower() for match in matches)
        
        # Count technical terms in text
        text_lower = text.lower()
        technical_count = sum(1 for word in words if word.lower() in technical_words)
        
        density = technical_count / len(words)
        return density
    
    def classify_technical_level(self, density: float) -> str:
        """Classify technical density level"""
        high_threshold = self.density_config.get("high_technical", ">0.15").replace(">", "").replace("technical terms/total words", "")
        medium_threshold_range = self.density_config.get("medium_technical", "0.08-0.15").split("-")
        
        try:
            high_val = float(high_threshold)
            medium_min = float(medium_threshold_range[0])
            medium_max = float(medium_threshold_range[1])
            
            if density > high_val:
                return "high_technical"
            elif medium_min <= density <= medium_max:
                return "medium_technical"
            else:
                return "low_technical"
        except ValueError:
            # Fallback to hardcoded thresholds
            if density > 0.15:
                return "high_technical"
            elif 0.08 <= density <= 0.15:
                return "medium_technical"
            else:
                return "low_technical"


class LanguageMatcher:
    """Language adaptation matrix - Lift & Shift from LIC"""
    
    def __init__(self, tone_rules: Dict[str, Any]):
        self.language_matcher = tone_rules.get("language_matcher", {})
        self.adaptation_matrix = self.language_matcher.get("adaptation_matrix", {})
        self.transformation_rules = self.language_matcher.get("transformation_rules", {})
        self.density_scorer = TechnicalDensityScorer(tone_rules)
    
    def determine_adaptation_strategy(self, recipient_type: str, technical_level: str) -> str:
        """Determine language adaptation strategy"""
        # Direct mapping from adaptation matrix
        if recipient_type in self.adaptation_matrix:
            recipient_rules = self.adaptation_matrix[recipient_type]
            for level_key, strategy in recipient_rules.items():
                if "any" in level_key or technical_level in level_key:
                    return strategy
        
        # Default fallback
        return "BUSINESS_OUTCOMES"
    
    def apply_transformation_rules(self, content: str, strategy: str) -> str:
        """Apply language transformation based on strategy"""
        if strategy not in self.transformation_rules:
            return content
        
        rule = self.transformation_rules[strategy]
        
        if strategy == "TECHNICAL_DETAIL":
            # Use sender technical terms as-is
            return content
        
        elif strategy == "BUSINESS_OUTCOMES":
            # Transform technical → business metrics
            return self._transform_to_business_outcomes(content)
        
        elif strategy == "STRATEGIC_VALUE":
            # Transform technical → strategic impact
            return self._transform_to_strategic_value(content)
        
        elif strategy == "LAYMAN_WITH_METRICS":
            # Simplify jargon, keep metrics
            return self._transform_to_layman_with_metrics(content)
        
        elif strategy == "BUSINESS_IMPACT_ONLY":
            # Strip technical, keep dollars/percentages
            return self._transform_to_business_impact_only(content)
        
        return content
    
    def _transform_to_business_outcomes(self, content: str) -> str:
        """Transform technical descriptions to business outcomes"""
        # Simple transformation rules
        transformations = {
            r'optimized\s+(\w+)': r'improved efficiency of \1, resulting in cost savings',
            r'implemented\s+(\w+)': r'deployed \1 solution that improved operational performance',
            r'built\s+(\w+)': r'created \1 system that enhanced business capabilities',
            r'architected\s+(\w+)': r'designed \1 infrastructure that scales with business growth',
            r'reduced\s+(latency|response\s+time)': r'improved system performance and user experience',
            r'scaled\s+(?:to\s+)?(\w+)': r'expanded capacity to support business growth',
            r'(\d+)%\s+(?:increase|improvement)': r'achieved \1% improvement in key business metrics',
            r'(\d+)x\s+(?:faster|improvement)': r'delivered \1 times better performance'
        }
        
        transformed = content
        for pattern, replacement in transformations.items():
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
        
        return transformed
    
    def _transform_to_strategic_value(self, content: str) -> str:
        """Transform technical descriptions to strategic impact"""
        transformations = {
            r'optimized\s+(\w+)': r'enhanced competitive advantage through \1 optimization',
            r'implemented\s+(\w+)': r'strategic \1 implementation aligned with business objectives',
            r'built\s+(\w+)': r'created \1 capability that drives strategic initiatives',
            r'architected\s+(\w+)': r'developed \1 architecture that supports long-term business strategy',
            r'reduced\s+(latency|response\s+time)': r'enhanced customer experience through performance optimization',
            r'scaled\s+(?:to\s+)?(\w+)': r'positioned for market leadership through scalable \1 solutions'
        }
        
        transformed = content
        for pattern, replacement in transformations.items():
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
        
        return transformed
    
    def _transform_to_layman_with_metrics(self, content: str) -> str:
        """Simplify technical jargon while keeping metrics"""
        # Simplify technical terms
        simplifications = {
            'API': 'application interface',
            'SDK': 'development toolkit',
            'microservices': 'small, independent services',
            'containerization': 'packaging applications for easy deployment',
            'load balancing': 'distributing work efficiently',
            'caching': 'storing frequently used data for fast access',
            'indexing': 'organizing data for quick retrieval',
            'replication': 'creating copies for reliability',
            'sharding': 'splitting large databases for better performance'
        }
        
        simplified = content
        for technical, simple in simplifications.items():
            simplified = re.sub(rf'\b{technical}\b', simple, simplified, flags=re.IGNORECASE)
        
        return simplified
    
    def _transform_to_business_impact_only(self, content: str) -> str:
        """Strip technical details, keep only business impact metrics"""
        # Extract business metrics and outcomes
        business_patterns = [
            r'(\d+)%\s+(?:increase|improvement|growth|reduction)',
            r'\$(?:\d+,?)+\.?\d*\s*(?:million|billion|thousand)',
            r'(\d+)x\s+(?:ROI|return|improvement|growth)',
            r'(?:saved|reduced|increased|improved)\s+(?:cost|time|efficiency|revenue)',
            r'(?:achieved|delivered|generated)\s+(?:significant|substantial|measurable)\s+(?:results|impact|value)'
        ]
        
        business_points = []
        for pattern in business_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    business_points.extend(match)
                else:
                    business_points.append(match)
        
        if business_points:
            return f"Delivered measurable business impact including: {', '.join(business_points[:3])}"
        else:
            return "Delivered significant business value and operational improvements"


class ToneEngine:
    """Main tone engine - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.tone_rules = lic_capabilities.get("tone_rules", {})
        self.archetype_mappings = self.tone_rules.get("archetype_tone_mappings", {})
        self.language_matcher = LanguageMatcher(self.tone_rules)
        self.density_scorer = TechnicalDensityScorer(self.tone_rules)
    
    def get_tone_profile(self, archetype: Archetype) -> ToneProfile:
        """Get tone profile for archetype"""
        archetype_key = archetype.value
        if archetype_key in self.archetype_mappings:
            config = self.archetype_mappings[archetype_key]
            return ToneProfile(
                message_tone=config.get("message_tone", "professional"),
                verb_preference=config.get("verb_preference", []),
                jargon_level=config.get("jargon_level", "business"),
                formality=config.get("formality", "medium"),
                focus_area=config.get("focus", "value")
            )
        
        # Default fallback
        return ToneProfile(
            message_tone="professional",
            verb_preference=["collaborate", "discuss", "connect"],
            jargon_level="business",
            formality="medium",
            focus="value"
        )
    
    def adapt_language_for_recipient(
        self, 
        content: str, 
        recipient_type: str, 
        archetype: Archetype
    ) -> Tuple[str, List[ValidationResult]]:
        """Adapt language based on recipient type and technical density"""
        validation_results = []
        
        # Calculate technical density
        density = self.density_scorer.calculate_technical_density(content)
        technical_level = self.density_scorer.classify_technical_level(density)
        
        # Determine adaptation strategy
        strategy = self.language_matcher.determine_adaptation_strategy(recipient_type, technical_level)
        
        # Apply transformation
        adapted_content = self.language_matcher.apply_transformation_rules(content, strategy)
        
        # Add validation result for the adaptation
        validation_results.append(ValidationResult(
            rule_id="LANGUAGE_ADAPTATION",
            passed=True,
            severity=ValidationSeverity.LOW,
            message=f"Language adapted using {strategy} strategy",
            details={
                "original_density": density,
                "technical_level": technical_level,
                "strategy": strategy,
                "recipient_type": recipient_type
            }
        ))
        
        return adapted_content, validation_results
    
    def validate_tone_compliance(
        self, 
        content: str, 
        tone_profile: ToneProfile
    ) -> List[ValidationResult]:
        """Validate content against tone profile requirements"""
        validation_results = []
        
        # Check verb preference
        if tone_profile.verb_preference:
            content_lower = content.lower()
            preferred_verbs_found = [verb for verb in tone_profile.verb_preference if verb in content_lower]
            
            if not preferred_verbs_found:
                validation_results.append(ValidationResult(
                    rule_id="VERB_PREFERENCE_MISSING",
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"No preferred verbs found: {', '.join(tone_profile.verb_preference)}",
                    details={"preferred_verbs": tone_profile.verb_preference, "found_verbs": preferred_verbs_found}
                ))
        
        # Check formality level (simplified)
        if tone_profile.formality == "very high":
            informal_patterns = [r'\b(hi|hey|yo|what\'s up)\b', r'\b(couldn\'t|wouldn\'t|didn\'t)\b']
            for pattern in informal_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    validation_results.append(ValidationResult(
                        rule_id="FORMALITY_VIOLATION",
                        passed=False,
                        severity=ValidationSeverity.MEDIUM,
                        message="Informal language detected in high formality context",
                        details={"formality_level": tone_profile.formality}
                    ))
                    break
        
        return validation_results
    
    def get_tone_guidance(self, archetype: Archetype, route: str) -> Dict[str, Any]:
        """Get tone guidance for archetype and route"""
        tone_profile = self.get_tone_profile(archetype)
        
        return {
            "message_tone": tone_profile.message_tone,
            "verb_preference": tone_profile.verb_preference,
            "jargon_level": tone_profile.jargon_level,
            "formality": tone_profile.formality,
            "focus_area": tone_profile.focus_area,
            "route_considerations": self._get_route_tone_considerations(route)
        }
    
    def _get_route_tone_considerations(self, route: str) -> Dict[str, str]:
        """Get route-specific tone considerations"""
        route_considerations = {
            "CONNECTION_REQ": {
                "tone_adjustment": "Slightly more informal, direct",
                "length_guidance": "Keep concise and impactful"
            },
            "INMAIL": {
                "tone_adjustment": "Professional but warm",
                "length_guidance": "Can be more detailed with subject line"
            },
            "SHORT_NEW": {
                "tone_adjustment": "Balanced professional",
                "length_guidance": "Medium length with clear value proposition"
            },
            "LONG_NEW": {
                "tone_adjustment": "Comprehensive and strategic",
                "length_guidance": "Detailed with supporting evidence"
            },
            "FOLLOW_UP": {
                "tone_adjustment": "Context-aware and respectful",
                "length_guidance": "Reference prior conversation"
            }
        }
        
        return route_considerations.get(route, {
            "tone_adjustment": "Professional default",
            "length_guidance": "Follow route constraints"
        })
