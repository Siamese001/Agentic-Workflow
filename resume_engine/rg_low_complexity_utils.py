"""RG Low Complexity Utilities - Lightweight Enhancement Features

This module implements LOW complexity features from the functionality gaps:
- PII scrubbing utility with placeholder reinjection
- Bias auditor (lightweight NLP checks)
- Goal state injection into prompts
- HyDE-style single-pass expansion
- Lightweight reflection stub

These are designed as simple, patchable utilities that can be
integrated without architectural changes.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PIIResult:
    """Result of PII scrubbing operation."""
    scrubbed_content: str
    pii_detected: List[Dict[str, Any]]
    placeholders: Dict[str, str]


@dataclass
class BiasAuditResult:
    """Result of bias audit operation."""
    bias_score: float
    flagged_terms: List[str]
    suggestions: List[str]


class PIIScrubber:
    """Lightweight PII scrubbing utility with placeholder reinjection."""
    
    def __init__(self):
        # PII patterns for detection
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "address": r'\b\d+\s+([A-Z][a-z]*\s)+[A-Z][a-z]*,\s+[A-Z]{2}\s+\d{5}\b',
            "name": r'\b([A-Z][a-z]+\s)+[A-Z][a-z]+\b',  # Simple name pattern
        }
        
        self.placeholder_counter = 0
    
    def scrub_pii(self, content: str, preserve_placeholders: bool = True) -> PIIResult:
        """Scrub PII from content and replace with placeholders."""
        scrubbed_content = content
        pii_detected = []
        placeholders = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                original_value = match.group()
                placeholder = self._generate_placeholder(pii_type)
                
                pii_detected.append({
                    "type": pii_type,
                    "original": original_value,
                    "placeholder": placeholder,
                    "position": match.start()
                })
                
                placeholders[placeholder] = original_value
                scrubbed_content = scrubbed_content.replace(original_value, placeholder)
        
        logger.info(f"Scrubbed {len(pii_detected)} PII instances from content")
        return PIIResult(
            scrubbed_content=scrubbed_content,
            pii_detected=pii_detected,
            placeholders=placeholders
        )
    
    def _generate_placeholder(self, pii_type: str) -> str:
        """Generate appropriate placeholder for PII type."""
        self.placeholder_counter += 1
        
        placeholders_map = {
            "email": f"[EMAIL_{self.placeholder_counter}]",
            "phone": f"[PHONE_{self.placeholder_counter}]",
            "ssn": f"[SSN_{self.placeholder_counter}]",
            "address": f"[ADDRESS_{self.placeholder_counter}]",
            "name": f"[NAME_{self.placeholder_counter}]",
        }
        
        return placeholders_map.get(pii_type, f"[REDACTED_{self.placeholder_counter}]")


class BiasAuditor:
    """Lightweight bias detection using NLP-style pattern matching."""
    
    def __init__(self):
        # Bias indicators and problematic terms
        self.bias_indicators = {
            "age_bias": [r"\b(young|old|elderly|junior|senior)\s+(?:years?|age)\b"],
            "gender_bias": [r"\b(male|female|he|she|him|her)\s+(?:candidate|applicant|employee)\b"],
            "racial_bias": [r"\b([A-Z][a-z]+)\s+(?:american|asian|african|hispanic)\b"],
            "ability_bias": [r"\b(disabled|handicapped|abled)\s+(?:candidate|person|individual)\b"],
        }
        
        self.problematic_terms = [
            "naturally", "fit", "culture fit", "rockstar", "ninja", "guru", "diva"
        ]
    
    def audit_content(self, content: str) -> BiasAuditResult:
        """Audit content for potential bias indicators."""
        bias_score = 0.0
        flagged_terms = []
        suggestions = []
        
        content_lower = content.lower()
        
        # Check bias indicators
        for bias_type, patterns in self.bias_indicators.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    bias_score += 0.2
                    flagged_terms.extend(matches)
                    suggestions.append(f"Consider neutral language for {bias_type.replace('_', ' ')}")
        
        # Check problematic terms
        for term in self.problematic_terms:
            if term in content_lower:
                bias_score += 0.1
                flagged_terms.append(term)
                suggestions.append(f"Replace '{term}' with more specific, neutral language")
        
        bias_score = min(bias_score, 1.0)
        
        logger.info(f"Bias audit completed: score={bias_score:.2f}, flagged={len(flagged_terms)}")
        return BiasAuditResult(
            bias_score=bias_score,
            flagged_terms=flagged_terms,
            suggestions=suggestions
        )


class GoalStateInjector:
    """Simple goal state injection into prompts and content."""
    
    def __init__(self):
        self.goal_templates = {
            "professional_summary": "Create a compelling professional summary that highlights {goal} for {target_role}.",
            "achievement_focus": "Emphasize achievements that demonstrate {goal} with quantifiable results.",
            "skill_alignment": "Align skills and experiences to showcase {goal} in the context of {industry}.",
        }
    
    def inject_goal_state(self, content: str, goal_state: Dict[str, Any]) -> str:
        """Inject goal state into content templates."""
        if not goal_state:
            return content
        
        primary_goal = goal_state.get("primary_goal", "professional excellence")
        target_role = goal_state.get("target_role", "professional")
        industry = goal_state.get("industry", "general")
        
        enhanced_content = content
        
        # Replace goal placeholders if they exist
        enhanced_content = enhanced_content.replace("{GOAL_STATE}", primary_goal)
        enhanced_content = enhanced_content.replace("{TARGET_ROLE}", target_role)
        enhanced_content = enhanced_content.replace("{INDUSTRY}", industry)
        
        # Add goal-oriented prefixes to sections
        if "## Professional Summary" in enhanced_content:
            enhanced_content = enhanced_content.replace(
                "## Professional Summary",
                f"## Professional Summary\n\nFocus: {primary_goal} for {target_role} roles"
            )
        
        logger.debug(f"Injected goal state: {primary_goal} for {target_role}")
        return enhanced_content


class HyDESinglePass:
    """Lightweight HyDE-style single-pass expansion."""
    
    def __init__(self):
        self.expansion_templates = {
            "skill_enhancement": "Proficient in {skill} with demonstrated expertise in {context}",
            "achievement_expansion": "Achieved {result} through {action}, resulting in {impact}",
            "experience_elaboration": "Applied {knowledge} to solve {challenge} in {environment}"
        }
    
    def expand_content(self, content: str, context: Dict[str, Any]) -> str:
        """Perform single-pass content expansion using HyDE principles."""
        expanded_content = content
        
        # Extract skills from context
        skills = context.get("skills", [])
        if skills:
            for skill in skills[:3]:  # Limit to top 3 skills
                skill_pattern = f"\\b{skill.lower()}\\b"
                if re.search(skill_pattern, expanded_content, re.IGNORECASE):
                    enhancement = self.expansion_templates["skill_enhancement"].format(
                        skill=skill,
                        context=context.get("industry", "professional environments")
                    )
                    expanded_content += f"\n• {enhancement}"
        
        # Add quantifiable achievement templates
        if "experience" in context:
            achievement_template = self.expansion_templates["achievement_expansion"].format(
                result="measurable business impact",
                action="strategic initiatives",
                impact="improved efficiency and performance"
            )
            expanded_content += f"\n\n## Key Achievements\n• {achievement_template}"
        
        logger.debug(f"Expanded content by {len(expanded_content) - len(content)} characters")
        return expanded_content


class LightweightReflector:
    """Simple reflection stub for output validation and improvement."""
    
    def __init__(self):
        self.quality_indicators = {
            "has_metrics": r"\d+%|\$\d+|\d+\s+(?:years?|months?)",
            "has_action_verbs": r"\b(managed|led|developed|implemented|created|optimized)\b",
            "has_structure": r"##\s+\w+",
            "min_length": 100
        }
    
    def reflect_and_improve(self, content: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reflect on content and suggest improvements."""
        reflection_result = {
            "quality_score": 0.0,
            "improvements_suggested": [],
            "final_content": content
        }
        
        score = 0.0
        improvements = []
        
        # Check for metrics
        if re.search(self.quality_indicators["has_metrics"], content):
            score += 0.3
        else:
            improvements.append("Add quantifiable metrics (percentages, dollar amounts, time periods)")
        
        # Check for action verbs
        if re.search(self.quality_indicators["has_action_verbs"], content, re.IGNORECASE):
            score += 0.3
        else:
            improvements.append("Include stronger action verbs (managed, led, developed, implemented)")
        
        # Check for structure
        if re.search(self.quality_indicators["has_structure"], content):
            score += 0.2
        else:
            improvements.append("Add clear section headers with ## formatting")
        
        # Check length
        if len(content) >= self.quality_indicators["min_length"]:
            score += 0.2
        else:
            improvements.append("Expand content to provide more detail and substance")
        
        # Apply basic improvements automatically
        improved_content = content
        if "Add clear section headers" in improvements:
            if not improved_content.startswith("##"):
                improved_content = f"## Professional Summary\n\n{improved_content}"
        
        reflection_result.update({
            "quality_score": score,
            "improvements_suggested": improvements,
            "final_content": improved_content
        })
        
        logger.info(f"Reflection completed: quality_score={score:.2f}, improvements={len(improvements)}")
        return improved_content, reflection_result


class LowComplexityUtils:
    """Main interface for all LOW complexity utilities."""
    
    def __init__(self):
        self.pii_scrubber = PIIScrubber()
        self.bias_auditor = BiasAuditor()
        self.goal_injector = GoalStateInjector()
        self.hyde_expander = HyDESinglePass()
        self.reflector = LightweightReflector()
    
    def process_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all LOW complexity enhancements to content."""
        results = {
            "original_content": content,
            "processed_content": content,
            "pii_result": None,
            "bias_result": None,
            "goal_injected": False,
            "hyde_expanded": False,
            "reflection_result": None
        }
        
        try:
            # 1. PII Scrubbing
            if context.get("scrub_pii", False):
                pii_result = self.pii_scrubber.scrub_pii(content)
                results["pii_result"] = pii_result
                content = pii_result.scrubbed_content
            
            # 2. Bias Audit
            if context.get("audit_bias", False):
                bias_result = self.bias_auditor.audit_content(content)
                results["bias_result"] = bias_result
            
            # 3. Goal State Injection
            if context.get("inject_goals", False) and context.get("goal_state"):
                content = self.goal_injector.inject_goal_state(content, context["goal_state"])
                results["goal_injected"] = True
            
            # 4. HyDE Single-Pass Expansion
            if context.get("hyde_expand", False):
                content = self.hyde_expander.expand_content(content, context)
                results["hyde_expanded"] = True
            
            # 5. Lightweight Reflection
            if context.get("reflect_improve", False):
                content, reflection_result = self.reflector.reflect_and_improve(content, context)
                results["reflection_result"] = reflection_result
            
            results["processed_content"] = content
            
        except Exception as e:
            logger.error(f"Error in LOW complexity processing: {e}")
            results["error"] = str(e)
        
        return results
