"""RG K4 Rewrite - Resume Content Enhancement and Rewriting

Incorporated from historical agentic_workflow/l2/rg_k4_rewrite.py to execute
advanced resume content rewriting with enhancement and optimization.

This is the fourth execution phase in the resume generation pipeline:
K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class RewritingOperation:
    """Individual rewriting operation performed on content."""
    operation_id: str
    operation_type: str  # "enhancement", "restructuring", "optimization"
    original_text: str
    rewritten_text: str
    confidence_score: float
    improvement_score: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RewrittenSection:
    """Rewritten resume section with enhancements."""
    section_id: str
    section_name: str
    original_content: str
    rewritten_content: str
    rewriting_operations: List[RewritingOperation]
    enhancement_score: float
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RewritingMetrics:
    """Metrics from resume rewriting process."""
    total_operations: int
    sections_rewritten: int
    enhancements_applied: int
    restructures_performed: int
    optimizations_made: int
    average_improvement_score: float
    rewriting_confidence: float
    processing_time_ms: int


@dataclass
class RewritingOutput:
    """Complete output from K4 rewriting phase."""
    rewritten_sections: List[RewrittenSection]
    rewriting_operations: List[RewritingOperation]
    rewritten_content: str
    metrics: RewritingMetrics
    rewriting_plan: Dict[str, Any]
    success: bool
    error_message: str
    processing_trace: List[Dict[str, Any]] = field(default_factory=list)


class RGK4Rewrite:
    """K4 Resume Rewriter - Fourth hop in sequential processing pipeline.
    
    Executes advanced resume content rewriting with multiple strategies:
    - Content enhancement with stronger action verbs
    - Achievement restructuring for impact
    - ATS optimization and keyword enhancement
    - Professional tone and style improvements
    """
    
    def __init__(self, 
                 rewriting_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K4 resume rewriter."""
        self.rewriting_plan = rewriting_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Action verb enhancement mappings
        self.action_verb_enhancements = {
            "was responsible for": "managed",
            "helped": "collaborated",
            "worked on": "developed",
            "did": "executed",
            "made": "created",
            "participated in": "contributed to",
            "involved in": "engaged in",
            "handled": "oversaw",
            "dealt with": "addressed",
            "took care of": "managed",
            "oversaw": "directed",
            "ran": "led",
            "controlled": "governed",
            "kept track of": "monitored",
            "looked after": "maintained",
            "put together": "assembled",
            "came up with": "developed",
            "figured out": "solved",
            "thought of": "conceived",
            "brought about": "achieved",
            "got": "secured",
            "obtained": "acquired"
        }
        
        # Achievement enhancement patterns
        self.achievement_patterns = {
            "quantify_result": [
                (r'(\w+)\s+(?:improved|increased|enhanced)', r'\1 improved by'),
                (r'(\w+)\s+(?:reduced|decreased|cut)', r'\1 reduced by'),
                (r'(\w+)\s+(?:saved|eliminated)', r'\1 saved'),
            ],
            "add_impact": [
                (r'(managed|led|directed)\s+(\w+)', r'\1 \2, resulting in'),
                (r'(developed|created|built)\s+(\w+)', r'\1 \2, which improved'),
                (r'(implemented|launched)\s+(\w+)', r'\1 \2, achieving'),
            ],
            "strengthen_verbs": [
                (r'\b(improved|enhanced|optimized)\b', 'significantly \1'),
                (r'\b(increased|grew|expanded)\b', 'successfully \1'),
                (r'\b(reduced|decreased|eliminated)\b', 'effectively \1'),
            ]
        }
        
        # Professional tone improvements
        self.tone_improvements = {
            "remove_weak_phrases": [
                (r'\b(?:I think|I feel|I believe|I guess)\b', ''),
                (r'\b(?:sort of|kind of|perhaps|maybe)\b', ''),
                (r'\b(?:quite|rather|fairly)\s+(\w+)', r'\1'),
            ],
            "strengthen_language": [
                (r'\bgood\b', 'effective'),
                (r'\bbad\b', 'inadequate'),
                (r'\bfast\b', 'efficient'),
                (r'\bslow\b', 'methodical'),
                (r'\bbig\b', 'substantial'),
                (r'\bsmall\b', 'focused'),
            ],
            "add_professionalism": [
                (r'\b(?:helped|assisted)\b', 'supported'),
                (r'\b(?:showed|demonstrated)\b', 'exhibited'),
                (r'\b(?:got|obtained)\b', 'secured'),
                (r'\b(?:did|performed)\b', 'executed'),
            ]
        }
        
        # ATS optimization keywords
        self.ats_keywords = {
            "technology": [
                "developed", "implemented", "engineered", "architected", "designed",
                "optimized", "integrated", "deployed", "maintained", "troubleshooted"
            ],
            "management": [
                "led", "managed", "directed", "coordinated", "oversaw", "guided",
                "mentored", "trained", "supervised", "organized"
            ],
            "business": [
                "analyzed", "improved", "increased", "reduced", "optimized", "streamlined",
                "achieved", "delivered", "launched", "grew"
            ],
            "general": [
                "collaborated", "communicated", "presented", "documented", "researched",
                "evaluated", "assessed", "identified", "resolved", "solved"
            ]
        }
    
    def rewrite_resume_content(
        self,
        *,
        quantification_output: Any,  # From K3 quantification
        job_requirements: Optional[Dict[str, Any]] = None,  # Job context for goal alignment
        rewriting_params: Optional[Dict[str, Any]] = None
    ) -> RewritingOutput:
        """Execute resume content rewriting with goal-alignment.
        
        Args:
            quantification_output: Output from K3 quantification phase
            job_requirements: Target job requirements for goal-aligned rewriting
            rewriting_params: Rewriting strategy and parameters
            
        Returns:
            Complete rewriting output with enhanced content and metrics
        """
        rewriting_params = rewriting_params or {}
        processing_trace = []
        
        try:
            # 1. Initialize rewriting strategy with goal alignment
            strategy = self._initialize_rewriting_strategy(rewriting_params, job_requirements)
            processing_trace.append({
                "step": "strategy_initialization",
                "strategy": strategy,
                "timestamp": "2024-01-01T00:00:01Z"
            })
            
            # 2. Extract sections from K3 output
            sections = self._extract_sections_from_output(quantification_output)
            processing_trace.append({
                "step": "section_extraction",
                "sections_count": len(sections),
                "timestamp": "2024-01-01T00:00:02Z"
            })
            
            # 3. Apply goal-aligned rewriting operations to each section
            rewritten_sections = []
            all_operations = []
            
            for section in sections:
                rewritten_section, operations = self._rewrite_section_with_goals(section, strategy, job_requirements)
                rewritten_sections.append(rewritten_section)
                all_operations.extend(operations)
            
            processing_trace.append({
                "step": "section_rewriting",
                "operations_performed": len(all_operations),
                "timestamp": "2024-01-01T00:00:03Z"
            })
            
            # 4. Reassemble rewritten content
            rewritten_content = self._reassemble_rewritten_content(rewritten_sections)
            processing_trace.append({
                "step": "content_reassembly",
                "final_length": len(rewritten_content),
                "timestamp": "2024-01-01T00:00:04Z"
            })
            
            # 5. Calculate rewriting metrics
            metrics = self._calculate_rewriting_metrics(
                sections, rewritten_sections, all_operations
            )
            processing_trace.append({
                "step": "metrics_calculation",
                "average_improvement": metrics.average_improvement_score,
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 6. Build rewriting output
            rewriting_output = RewritingOutput(
                rewritten_sections=rewritten_sections,
                rewriting_operations=all_operations,
                rewritten_content=rewritten_content,
                metrics=metrics,
                rewriting_plan={
                    "strategy": strategy,
                    "parameters": rewriting_params,
                    "enhancement_types": ["action_verbs", "achievements", "tone", "ats_optimization"]
                },
                success=True,
                error_message="",
                processing_trace=processing_trace
            )
            
            # 7. Record telemetry (best-effort)
            self._safe_record_telemetry(rewriting_output)
            
            return rewriting_output
            
        except Exception as e:
            logger.error(f"Resume rewriting failed: {e}")
            
            error_output = RewritingOutput(
                rewritten_sections=[],
                rewriting_operations=[],
                rewritten_content="",
                metrics=RewritingMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0),
                rewriting_plan={},
                success=False,
                error_message=str(e),
                processing_trace=processing_trace + [{
                    "step": "error",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:06Z"
                }]
            )
            
            return error_output
    
    def _initialize_rewriting_strategy(self, params: Dict[str, Any], job_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize rewriting strategy with goal-alignment based on parameters and job requirements."""
        strategy = {
            "style": params.get("style", "professional"),
            "enhance_achievements": params.get("enhance_achievements", True),
            "optimize_for_ats": params.get("optimize_for_ats", True),
            "strengthen_verbs": params.get("strengthen_verbs", True),
            "improve_tone": params.get("improve_tone", True),
            "target_role": params.get("target_role", ""),
            "target_industry": params.get("target_industry", "technology"),
            "goal_alignment": params.get("goal_alignment", True)
        }
        
        # Add job-specific goal alignment if job requirements provided
        if job_requirements:
            strategy.update({
                "job_title": job_requirements.get("title", ""),
                "job_skills": job_requirements.get("skills", []),
                "job_requirements": job_requirements.get("requirements", []),
                "company_focus": job_requirements.get("company_focus", ""),
                "experience_level": job_requirements.get("experience_level", ""),
                "industry_keywords": self._extract_industry_keywords(job_requirements)
            })
        
        return strategy
    
    def _extract_industry_keywords(self, job_requirements: Dict[str, Any]) -> List[str]:
        """Extract industry-specific keywords from job requirements for goal alignment."""
        keywords = []
        
        # Extract from job title
        title = job_requirements.get("title", "").lower()
        if "software" in title or "developer" in title:
            keywords.extend(["developed", "implemented", "engineered", "coded", "programmed"])
        elif "manager" in title or "lead" in title:
            keywords.extend(["led", "managed", "directed", "coordinated", "oversaw"])
        elif "analyst" in title or "data" in title:
            keywords.extend(["analyzed", "interpreted", "modeled", "visualized", "reported"])
        
        # Extract from skills requirements
        skills = job_requirements.get("skills", [])
        for skill in skills:
            if isinstance(skill, str):
                # Convert skill names to action verbs
                skill_lower = skill.lower()
                if "python" in skill_lower:
                    keywords.append("developed")
                elif "aws" in skill_lower or "cloud" in skill_lower:
                    keywords.append("deployed")
                elif "sql" in skill_lower or "database" in skill_lower:
                    keywords.append("managed")
                elif "react" in skill_lower or "frontend" in skill_lower:
                    keywords.append("designed")
        
        # Extract from requirements text
        requirements_text = " ".join(job_requirements.get("requirements", [])).lower()
        if "team" in requirements_text:
            keywords.append("collaborated")
        if "project" in requirements_text:
            keywords.append("delivered")
        if "client" in requirements_text:
            keywords.append("supported")
        
        return list(set(keywords))  # Remove duplicates
    
    def _rewrite_section_with_goals(self, section: Dict[str, Any], strategy: Dict[str, Any], job_requirements: Optional[Dict[str, Any]] = None) -> Tuple[RewrittenSection, List[RewritingOperation]]:
        """Rewrite section with goal-alignment based on job requirements."""
        content = section["content"]
        operations: List[RewritingOperation] = []
        
        # 1. Apply standard rewriting operations
        enhanced_content, standard_ops = self._rewrite_section(section, strategy)
        operations.extend(standard_ops)
        content = enhanced_content.rewritten_content
        
        # 2. Apply goal-aligned enhancements if job requirements provided
        if job_requirements and strategy.get("goal_alignment", True):
            goal_aligned_content = self._apply_goal_alignment(content, strategy, job_requirements)
            if goal_aligned_content != content:
                goal_op = RewritingOperation(
                    operation_id=f"goal_align_{len(operations)}",
                    operation_type="goal_alignment",
                    original_text=content,
                    rewritten_text=goal_aligned_content,
                    confidence_score=0.85,
                    improvement_score=0.3,
                    metadata={
                        "job_title": strategy.get("job_title", ""),
                        "alignment_keywords": strategy.get("industry_keywords", [])
                    }
                )
                operations.append(goal_op)
                content = goal_aligned_content
        
        # 3. Build final rewritten section
        rewritten_section = RewrittenSection(
            section_id=section["section_id"],
            section_name=section["section_name"],
            original_content=section["content"],
            rewritten_content=content,
            rewriting_operations=operations,
            enhancement_score=self._calculate_enhancement_score(content, operations),
            confidence_score=self._calculate_rewriting_confidence(content, operations),
            metadata={
                "goal_aligned": job_requirements is not None,
                "job_title": strategy.get("job_title", "")
            }
        )
        
        return rewritten_section, operations
    
    def _apply_goal_alignment(self, content: str, strategy: Dict[str, Any], job_requirements: Dict[str, Any]) -> str:
        """Apply goal-aligned enhancements to content based on job requirements."""
        aligned_content = content
        
        # 1. Inject industry-specific keywords
        industry_keywords = strategy.get("industry_keywords", [])
        for keyword in industry_keywords:
            # Replace generic verbs with industry-specific ones
            generic_patterns = {
                "worked on": f"{keyword}",
                "responsible for": f"{keyword}",
                "handled": f"{keyword}",
                "did": f"{keyword}",
                "made": f"{keyword}",
            }
            
            for generic, specific in generic_patterns.items():
                aligned_content = re.sub(rf'\b{generic}\b', specific, aligned_content, flags=re.IGNORECASE)
        
        # 2. Emphasize skills mentioned in job requirements
        job_skills = strategy.get("job_skills", [])
        for skill in job_skills:
            if isinstance(skill, str) and len(skill) > 3:
                # Highlight existing mentions of required skills
                skill_pattern = rf'\b({skill.lower()})\b'
                aligned_content = re.sub(skill_pattern, r'**\1**', aligned_content, flags=re.IGNORECASE)
        
        # 3. Add job-specific achievement quantification
        if "senior" in strategy.get("job_title", "").lower():
            # Emphasize leadership and impact for senior roles
            aligned_content = re.sub(
                r'\b(managed|led|coordinated)\s+(\w+)',
                r'\1 \2, delivering measurable business impact',
                aligned_content,
                flags=re.IGNORECASE
            )
        
        # 4. Optimize for experience level
        experience_level = strategy.get("experience_level", "").lower()
        if "entry" in experience_level or "junior" in experience_level:
            # Emphasize learning and growth for junior roles
            aligned_content = re.sub(
                r'\b(developed|created|built)\s+(\w+)',
                r'\1 \2, rapidly acquiring new skills and best practices',
                aligned_content,
                flags=re.IGNORECASE
            )
        
        return aligned_content
    
    def _extract_sections_from_output(self, quantification_output: Any) -> List[Dict[str, Any]]:
        """Extract sections from K3 quantification output."""
        if hasattr(quantification_output, 'quantified_achievements'):
            # Extract from quantified achievements
            sections = []
            achievements = quantification_output.quantified_achievements
            
            # Group achievements by impact category
            by_category = {}
            for achievement in achievements:
                category = achievement.impact_category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(achievement.description)
            
            for category, descriptions in by_category.items():
                content = '\n'.join(f"• {desc}" for desc in descriptions)
                sections.append({
                    "section_id": f"{category}_section",
                    "section_name": category,
                    "content": content,
                    "confidence": 0.8
                })
            
            return sections
        elif isinstance(quantification_output, dict):
            return quantification_output.get("rewritten_sections", [])
        else:
            return []
    
    def _rewrite_section(self, section: Dict[str, Any], strategy: Dict[str, Any]) -> Tuple[RewrittenSection, List[RewritingOperation]]:
        """Rewrite individual section content."""
        content = section["content"]
        operations = []
        
        # 1. Enhance action verbs
        if strategy["strengthen_verbs"]:
            enhanced_content, verb_ops = self._enhance_action_verbs(content)
            operations.extend(verb_ops)
            content = enhanced_content
        
        # 2. Enhance achievements
        if strategy["enhance_achievements"]:
            enhanced_content, achievement_ops = self._enhance_achievements(content)
            operations.extend(achievement_ops)
            content = enhanced_content
        
        # 3. Improve tone
        if strategy["improve_tone"]:
            improved_content, tone_ops = self._improve_tone(content)
            operations.extend(tone_ops)
            content = improved_content
        
        # 4. ATS optimization
        if strategy["optimize_for_ats"]:
            optimized_content, ats_ops = self._optimize_for_ats(content, strategy)
            operations.extend(ats_ops)
            content = optimized_content
        
        # Build rewritten section
        rewritten_section = RewrittenSection(
            section_id=section["section_id"],
            section_name=section["section_name"],
            original_content=section["content"],
            rewritten_content=content,
            rewriting_operations=operations,
            enhancement_score=self._calculate_enhancement_score(content, operations),
            confidence_score=self._calculate_rewriting_confidence(content, operations),
            metadata={
                "original_confidence": section["confidence"],
                "operations_count": len(operations)
            }
        )
        
        return rewritten_section, operations
    
    def _enhance_action_verbs(self, content: str) -> Tuple[str, List[RewritingOperation]]:
        """Enhance action verbs in content."""
        operations = []
        enhanced_content = content
        
        for weak_phrase, strong_verb in self.action_verb_enhancements.items():
            pattern = re.compile(r'\b' + re.escape(weak_phrase) + r'\b', re.IGNORECASE)
            new_content = pattern.sub(strong_verb, enhanced_content)
            
            if new_content != enhanced_content:
                operation = RewritingOperation(
                    operation_id=f"verb_enhancement_{len(operations)}",
                    operation_type="enhancement",
                    original_text=enhanced_content,
                    rewritten_text=new_content,
                    confidence_score=0.85,
                    improvement_score=0.3,
                    metadata={
                        "weak_phrase": weak_phrase,
                        "strong_verb": strong_verb
                    }
                )
                operations.append(operation)
                enhanced_content = new_content
        
        return enhanced_content, operations
    
    def _enhance_achievements(self, content: str) -> Tuple[str, List[RewritingOperation]]:
        """Enhance achievement descriptions."""
        operations = []
        enhanced_content = content
        
        for enhancement_type, patterns in self.achievement_patterns.items():
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, enhanced_content, flags=re.IGNORECASE)
                
                if new_content != enhanced_content:
                    operation = RewritingOperation(
                        operation_id=f"achievement_{enhancement_type}_{len(operations)}",
                        operation_type="enhancement",
                        original_text=enhanced_content,
                        rewritten_text=new_content,
                        confidence_score=0.8,
                        improvement_score=0.25,
                        metadata={
                            "enhancement_type": enhancement_type,
                            "pattern": pattern
                        }
                    )
                    operations.append(operation)
                    enhanced_content = new_content
        
        return enhanced_content, operations
    
    def _improve_tone(self, content: str) -> Tuple[str, List[RewritingOperation]]:
        """Improve professional tone."""
        operations = []
        improved_content = content
        
        for improvement_type, patterns in self.tone_improvements.items():
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, improved_content, flags=re.IGNORECASE)
                
                if new_content != improved_content:
                    operation = RewritingOperation(
                        operation_id=f"tone_{improvement_type}_{len(operations)}",
                        operation_type="enhancement",
                        original_text=improved_content,
                        rewritten_text=new_content,
                        confidence_score=0.75,
                        improvement_score=0.2,
                        metadata={
                            "improvement_type": improvement_type,
                            "pattern": pattern
                        }
                    )
                    operations.append(operation)
                    improved_content = new_content
        
        return improved_content, operations
    
    def _optimize_for_ats(self, content: str, strategy: Dict[str, Any]) -> Tuple[str, List[RewritingOperation]]:
        """Optimize content for ATS systems."""
        operations = []
        optimized_content = content
        
        # Add relevant keywords based on target role/industry
        target_industry = strategy.get("target_industry", "general")
        keywords = self.ats_keywords.get(target_industry, self.ats_keywords["general"])
        
        # Check for existing keywords and suggest additions
        existing_keywords = set()
        for keyword in keywords:
            if keyword.lower() in content.lower():
                existing_keywords.add(keyword)
        
        # Add missing high-value keywords if appropriate
        missing_keywords = [kw for kw in keywords[:5] if kw not in existing_keywords]  # Top 5 keywords
        
        if missing_keywords and len(optimized_content.split()) > 50:  # Only add to substantial content
            # Add keywords naturally at the end
            keyword_text = f" utilizing {', '.join(missing_keywords[:3])}"
            new_content = optimized_content + keyword_text
            
            operation = RewritingOperation(
                operation_id=f"ats_optimization_{len(operations)}",
                operation_type="optimization",
                original_text=optimized_content,
                rewritten_text=new_content,
                confidence_score=0.7,
                improvement_score=0.15,
                metadata={
                    "keywords_added": missing_keywords[:3],
                    "target_industry": target_industry
                }
            )
            operations.append(operation)
            optimized_content = new_content
        
        return optimized_content, operations
    
    def _reassemble_rewritten_content(self, sections: List[RewrittenSection]) -> str:
        """Reassemble rewritten sections into final content."""
        content_parts = []
        
        # Sort sections by standard order
        section_order = [
            "contact_info", "summary", "experience", "education", 
            "skills", "projects", "certifications", "achievements"
        ]
        
        ordered_sections = {}
        for section in sections:
            section_name = section.section_name
            order_priority = section_order.index(section_name) if section_name in section_order else 99
            ordered_sections[order_priority] = section
        
        for priority in sorted(ordered_sections.keys()):
            section = ordered_sections[priority]
            content_parts.append(f"## {section.section_name.replace('_', ' ').title()}\n{section.rewritten_content}\n")
        
        return '\n'.join(content_parts)
    
    def _calculate_enhancement_score(self, content: str, operations: List[RewritingOperation]) -> float:
        """Calculate enhancement score for rewritten content."""
        base_score = 0.5
        
        # Factor in operations
        if operations:
            avg_improvement = sum(op.improvement_score for op in operations) / len(operations)
            base_score += avg_improvement * 0.3
        
        # Factor in content quality
        quality_score = self._assess_content_quality(content)
        base_score += quality_score * 0.2
        
        return min(base_score, 1.0)
    
    def _calculate_rewriting_confidence(self, content: str, operations: List[RewritingOperation]) -> float:
        """Calculate confidence score for rewritten content."""
        base_confidence = 0.7
        
        # Factor in operation confidence
        if operations:
            avg_operation_confidence = sum(op.confidence_score for op in operations) / len(operations)
            base_confidence += avg_operation_confidence * 0.2
        
        # Factor in content length and structure
        if len(content) > 100 and '##' in content:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _assess_content_quality(self, content: str) -> float:
        """Assess quality of rewritten content."""
        quality_score = 0.0
        
        # Check for strong action verbs
        strong_verbs = ['managed', 'developed', 'implemented', 'led', 'created', 'optimized']
        verb_count = sum(1 for verb in strong_verbs if verb in content.lower())
        quality_score += min(verb_count * 0.05, 0.3)
        
        # Check for professional language
        professional_words = ['strategic', 'analytical', 'collaborative', 'innovative', 'efficient']
        prof_count = sum(1 for word in professional_words if word in content.lower())
        quality_score += min(prof_count * 0.05, 0.2)
        
        # Check for quantification
        if re.search(r'\d+(?:%|\$|years?)', content):
            quality_score += 0.2
        
        # Structure factor
        if '##' in content and '•' in content:
            quality_score += 0.2
        
        # Length factor
        if len(content) > 200:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _calculate_rewriting_metrics(
        self, 
        original_sections: List[Dict[str, Any]], 
        rewritten_sections: List[RewrittenSection], 
        operations: List[RewritingOperation]
    ) -> RewritingMetrics:
        """Calculate rewriting performance metrics."""
        total_operations = len(operations)
        sections_rewritten = len(rewritten_sections)
        
        # Count operation types
        enhancements = sum(1 for op in operations if op.operation_type == "enhancement")
        restructures = sum(1 for op in operations if op.operation_type == "restructuring")
        optimizations = sum(1 for op in operations if op.operation_type == "optimization")
        
        # Calculate average improvement score
        if operations:
            avg_improvement = sum(op.improvement_score for op in operations) / len(operations)
        else:
            avg_improvement = 0.0
        
        # Calculate overall confidence
        if rewritten_sections:
            avg_confidence = sum(section.confidence_score for section in rewritten_sections) / len(rewritten_sections)
        else:
            avg_confidence = 0.0
        
        return RewritingMetrics(
            total_operations=total_operations,
            sections_rewritten=sections_rewritten,
            enhancements_applied=enhancements,
            restructures_performed=restructures,
            optimizations_made=optimizations,
            average_improvement_score=avg_improvement,
            rewriting_confidence=avg_confidence,
            processing_time_ms=250  # Placeholder
        )
    
    def _safe_record_telemetry(self, rewriting_output: RewritingOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_k4_rewrite_executed", {
                    "operations_performed": rewriting_output.metrics.total_operations,
                    "enhancements_applied": rewriting_output.metrics.enhancements_applied,
                    "average_improvement": rewriting_output.metrics.average_improvement_score,
                    "success": rewriting_output.success
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_rewriting_summary(self, rewriting_output: RewritingOutput) -> Dict[str, Any]:
        """Get a summary of the rewriting execution for debugging/telemetry."""
        return {
            "execution_id": "rg_k4_rewrite",
            "operations_performed": rewriting_output.metrics.total_operations,
            "sections_rewritten": rewriting_output.metrics.sections_rewritten,
            "enhancements_applied": rewriting_output.metrics.enhancements_applied,
            "average_improvement": rewriting_output.metrics.average_improvement_score,
            "success": rewriting_output.success
        }
