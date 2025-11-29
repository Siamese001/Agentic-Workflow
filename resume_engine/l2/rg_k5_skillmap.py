"""RG K5 Skillmap - Resume Skills Analysis and Job Alignment

Incorporated from historical agentic_workflow/l2/rg_k5_skillmap.py to execute
advanced resume skills analysis with job alignment mapping.

This is the fifth execution phase in the resume generation pipeline:
K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class SkillMapping:
    """Individual skill mapping with job alignment."""
    skill_id: str
    skill_name: str
    skill_category: str  # "technical", "soft", "domain", "certification"
    proficiency_level: str  # "expert", "advanced", "intermediate", "beginner"
    job_relevance_score: float  # 0.0 to 1.0
    alignment_confidence: float
    evidence_in_resume: List[str]
    job_requirements_met: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillGap:
    """Identified skill gap between resume and job requirements."""
    gap_id: str
    missing_skill: str
    skill_category: str
    importance_level: str  # "critical", "important", "nice_to_have"
    acquisition_suggestions: List[str]
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillMappingMetrics:
    """Metrics from skill mapping process."""
    total_skills_mapped: int
    skills_by_category: Dict[str, int]
    average_job_relevance: float
    skill_gaps_identified: int
    coverage_percentage: float  # How well resume covers job requirements
    mapping_confidence: float
    processing_time_ms: int


@dataclass
class SkillMappingOutput:
    """Complete output from K5 skill mapping phase."""
    skill_mappings: List[SkillMapping]
    skill_gaps: List[SkillGap]
    mapped_content: str
    metrics: SkillMappingMetrics
    mapping_plan: Dict[str, Any]
    success: bool
    error_message: str
    processing_trace: List[Dict[str, Any]] = field(default_factory=list)


class RGK5Skillmap:
    """K5 Resume Skill Mapper - Fifth hop in sequential processing pipeline.
    
    Executes advanced resume skills analysis and job alignment:
    - Extract and categorize skills from resume content
    - Map skills to job requirements
    - Identify skill gaps and provide suggestions
    - Calculate relevance and alignment scores
    """
    
    def __init__(self, 
                 mapping_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K5 resume skill mapper."""
        self.mapping_plan = mapping_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Skill category patterns
        self.skill_patterns = {
            "technical": [
                r'\b(python|java|javascript|typescript|c\+\+|go|rust|sql|nosql)\b',
                r'\b(react|vue|angular|node\.js|django|flask|spring)\b',
                r'\b(aws|azure|gcp|docker|kubernetes|terraform)\b',
                r'\b(machine learning|deep learning|ai|data science|analytics)\b',
                r'\b(git|github|gitlab|ci/cd|devops|agile|scrum)\b',
                r'\b(html|css|sass|webpack|babel|npm|yarn)\b',
                r'\b(mongodb|postgresql|mysql|redis|elasticsearch)\b',
                r'\b(apis|rest|graphql|microservices|soa)\b'
            ],
            "soft": [
                r'\b(leadership|management|communication|collaboration)\b',
                r'\b(teamwork|problem solving|critical thinking|analytical)\b',
                r'\b(project management|time management|organization)\b',
                r'\b(creativity|innovation|adaptability|flexibility)\b',
                r'\b(presentation|public speaking|negotiation|influencing)\b',
                r'\b(mentoring|coaching|training|development)\b',
                r'\b(strategic thinking|decision making|planning)\b'
            ],
            "domain": [
                r'\b(finance|banking|investment|accounting|budgeting)\b',
                r'\b(healthcare|medical|pharmaceutical|biotech)\b',
                r'\b(education|training|learning|academia)\b',
                r'\b(retail|ecommerce|sales|marketing)\b',
                r'\b(manufacturing|logistics|supply chain|operations)\b',
                r'\b(consulting|advisory|professional services)\b',
                r'\b(legal|compliance|risk|audit)\b'
            ],
            "certification": [
                r'\b(pmp|prince2|csm|csd|safe)\b',
                r'\b(aws certified|azure certified|gcp certified)\b',
                r'\b(cissp|cisa|cism|ceh)\b',
                r'\b(phr|sphr|shrm|hr certification)\b',
                r'\b(cpa|cfa|frm|cisa)\b',
                r'\b(scrum master|product owner|agile coach)\b'
            ]
        }
        
        # Proficiency indicators
        self.proficiency_indicators = {
            "expert": [
                "expert", "master", "specialist", "architect", "principal",
                "senior", "lead", "chief", "head of", "director"
            ],
            "advanced": [
                "advanced", "experienced", "proficient", "skilled",
                "strong", "deep knowledge", "extensive"
            ],
            "intermediate": [
                "intermediate", "moderate", "working knowledge", "familiar",
                "comfortable with", "good understanding"
            ],
            "beginner": [
                "beginner", "basic", "introductory", "learning", "novice",
                "familiarity", "exposure to", "some experience"
            ]
        }
        
        # Industry-specific skill mappings
        self.industry_mappings = {
            "technology": {
                "critical": ["python", "javascript", "aws", "docker", "git", "apis"],
                "important": ["react", "node.js", "sql", "machine learning", "agile"],
                "nice_to_have": ["kubernetes", "terraform", "graphql", "microservices"]
            },
            "finance": {
                "critical": ["financial analysis", "excel", "accounting", "risk management"],
                "important": ["sql", "python", "banking", "investment", "budgeting"],
                "nice_to_have": ["tableau", "power bi", "financial modeling", "crm"]
            },
            "healthcare": {
                "critical": ["healthcare", "medical", "patient care", "hipaa"],
                "important": ["electronic health records", "medical terminology", "clinical"],
                "nice_to_have": ["healthcare it", "medical devices", "pharmaceutical"]
            },
            "general": {
                "critical": ["communication", "teamwork", "problem solving"],
                "important": ["leadership", "project management", "analytical"],
                "nice_to_have": ["presentation", "creativity", "adaptability"]
            }
        }
    
    def map_resume_skills(
        self,
        *,
        rewriting_output: Any,  # From K4 rewriting
        job_requirements: Dict[str, Any],
        mapping_params: Optional[Dict[str, Any]] = None
    ) -> SkillMappingOutput:
        """Execute resume skills mapping and job alignment.
        
        Args:
            rewriting_output: Output from K4 rewriting phase
            job_requirements: Target job requirements and specifications
            mapping_params: Skill mapping strategy and parameters
            
        Returns:
            Complete skill mapping output with alignments and gaps
        """
        mapping_params = mapping_params or {}
        processing_trace = []
        
        try:
            # 1. Initialize mapping strategy
            strategy = self._initialize_mapping_strategy(mapping_params, job_requirements)
            processing_trace.append({
                "step": "strategy_initialization",
                "strategy": strategy,
                "timestamp": "2024-01-01T00:00:01Z"
            })
            
            # 2. Extract rewritten content
            content = self._extract_rewritten_content(rewriting_output)
            processing_trace.append({
                "step": "content_extraction",
                "content_length": len(content),
                "timestamp": "2024-01-01T00:00:02Z"
            })
            
            # 3. Extract skills from resume
            resume_skills = self._extract_resume_skills(content, strategy)
            processing_trace.append({
                "step": "skill_extraction",
                "skills_found": len(resume_skills),
                "timestamp": "2024-01-01T00:00:03Z"
            })
            
            # 4. Extract job requirements
            job_skills = self._extract_job_skills(job_requirements, strategy)
            processing_trace.append({
                "step": "job_requirements_extraction",
                "job_skills_count": len(job_skills),
                "timestamp": "2024-01-01T00:00:04Z"
            })
            
            # 5. Map skills to job requirements
            skill_mappings = self._map_skills_to_job(resume_skills, job_skills, strategy)
            processing_trace.append({
                "step": "skill_mapping",
                "mappings_created": len(skill_mappings),
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 6. Identify skill gaps
            skill_gaps = self._identify_skill_gaps(skill_mappings, job_skills, strategy)
            processing_trace.append({
                "step": "gap_identification",
                "gaps_found": len(skill_gaps),
                "timestamp": "2024-01-01T00:00:06Z"
            })
            
            # 7. Generate mapped content
            mapped_content = self._generate_mapped_content(skill_mappings, skill_gaps)
            processing_trace.append({
                "step": "content_generation",
                "mapped_length": len(mapped_content),
                "timestamp": "2024-01-01T00:00:07Z"
            })
            
            # 8. Calculate mapping metrics
            metrics = self._calculate_mapping_metrics(skill_mappings, skill_gaps, job_skills)
            processing_trace.append({
                "step": "metrics_calculation",
                "coverage_percentage": metrics.coverage_percentage,
                "timestamp": "2024-01-01T00:00:08Z"
            })
            
            # 9. Build skill mapping output
            mapping_output = SkillMappingOutput(
                skill_mappings=skill_mappings,
                skill_gaps=skill_gaps,
                mapped_content=mapped_content,
                metrics=metrics,
                mapping_plan={
                    "strategy": strategy,
                    "parameters": mapping_params,
                    "job_requirements": job_requirements
                },
                success=True,
                error_message="",
                processing_trace=processing_trace
            )
            
            # 10. Record telemetry (best-effort)
            self._safe_record_telemetry(mapping_output)
            
            return mapping_output
            
        except Exception as e:
            logger.error(f"Resume skill mapping failed: {e}")
            
            error_output = SkillMappingOutput(
                skill_mappings=[],
                skill_gaps=[],
                mapped_content="",
                metrics=SkillMappingMetrics(0, {}, 0.0, 0, 0.0, 0.0, 0),
                mapping_plan={},
                success=False,
                error_message=str(e),
                processing_trace=processing_trace + [{
                    "step": "error",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:09Z"
                }]
            )
            
            return error_output
    
    def _initialize_mapping_strategy(self, params: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize skill mapping strategy based on parameters and job requirements."""
        return {
            "method": params.get("method", "job_alignment"),
            "job_alignment": params.get("job_alignment", True),
            "industry_standards": params.get("industry_standards", True),
            "target_industry": job_requirements.get("industry", "general"),
            "target_role": job_requirements.get("title", ""),
            "confidence_threshold": params.get("confidence_threshold", 0.5),
            "min_relevance_score": params.get("min_relevance_score", 0.3)
        }
    
    def _extract_rewritten_content(self, rewriting_output: Any) -> str:
        """Extract rewritten content from K4 output."""
        logger.info(f"K5: Extracting content from K4 output type: {type(rewriting_output)}")
        
        if hasattr(rewriting_output, 'rewritten_content'):
            content = rewriting_output.rewritten_content
            logger.info(f"K5: Got rewritten_content: '{content[:100]}...' (length: {len(content)})")
            
            # If rewritten_content is empty, try to assemble from rewritten_sections
            if not content and hasattr(rewriting_output, 'rewritten_sections'):
                sections = rewriting_output.rewritten_sections
                logger.info(f"K5: rewritten_content empty, checking {len(sections)} rewritten_sections")
                if sections:
                    content_parts = []
                    for i, section in enumerate(sections):
                        logger.info(f"K5: Section {i}: {section.section_name} -> '{section.rewritten_content[:50]}...'")
                        if hasattr(section, 'rewritten_content') and section.rewritten_content.strip():
                            content_parts.append(section.rewritten_content)
                    content = '\n\n'.join(content_parts)
                    logger.info(f"K5: Assembled content from sections: '{content[:100]}...' (length: {len(content)})")
            return content
        elif isinstance(rewriting_output, dict):
            content = rewriting_output.get("rewritten_content", "")
            logger.info(f"K5: Got dict rewritten_content: '{content[:100]}...' (length: {len(content)})")
            
            # Fallback to sections if content is empty
            if not content and "rewritten_sections" in rewriting_output:
                sections = rewriting_output["rewritten_sections"]
                logger.info(f"K5: dict rewritten_content empty, checking {len(sections)} sections")
                if sections:
                    content_parts = []
                    for i, section in enumerate(sections):
                        section_content = section.get("rewritten_content", "") if isinstance(section, dict) else ""
                        logger.info(f"K5: Dict section {i}: '{section_content[:50]}...'")
                        if section_content.strip():
                            content_parts.append(section_content)
                    content = '\n\n'.join(content_parts)
                    logger.info(f"K5: Assembled dict content: '{content[:100]}...' (length: {len(content)})")
            return content
        else:
            logger.warning(f"K5: Unexpected output type: {type(rewriting_output)}")
            return ""
    
    def _extract_resume_skills(self, content: str, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract skills from resume content."""
        skills = []
        
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Determine proficiency level
                    proficiency = self._determine_proficiency_level(content, match)
                    
                    # Find evidence in content
                    evidence = self._find_skill_evidence(content, match)
                    
                    skill = {
                        "skill_name": match.lower(),
                        "skill_category": category,
                        "proficiency_level": proficiency,
                        "evidence": evidence,
                        "frequency": content.count(match.lower())
                    }
                    skills.append(skill)
        
        return self._deduplicate_skills(skills)
    
    def _extract_job_skills(self, job_requirements: Dict[str, Any], strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract skills from job requirements."""
        job_skills = []
        
        # Extract from requirements text
        requirements_text = job_requirements.get("description", "") + " " + " ".join(job_requirements.get("requirements", []))
        requirements_text += " " + " ".join(job_requirements.get("skills", []))
        
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, requirements_text, re.IGNORECASE)
                
                for match in matches:
                    # Determine importance based on industry mapping
                    importance = self._determine_skill_importance(match.lower(), strategy["target_industry"])
                    
                    skill = {
                        "skill_name": match.lower(),
                        "skill_category": category,
                        "importance_level": importance,
                        "mentioned_in_requirements": True
                    }
                    job_skills.append(skill)
        
        return self._deduplicate_skills(job_skills)
    
    def _map_skills_to_job(self, resume_skills: List[Dict[str, Any]], job_skills: List[Dict[str, Any]], strategy: Dict[str, Any]) -> List[SkillMapping]:
        """Map resume skills to job requirements."""
        mappings = []
        
        # Create job skill lookup
        job_skill_lookup = {skill["skill_name"]: skill for skill in job_skills}
        
        for resume_skill in resume_skills:
            skill_name = resume_skill["skill_name"]
            
            # Check if skill matches job requirements
            if skill_name in job_skill_lookup:
                job_skill = job_skill_lookup[skill_name]
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(resume_skill, job_skill, strategy)
                
                if relevance_score >= strategy["min_relevance_score"]:
                    mapping = SkillMapping(
                        skill_id=f"mapping_{len(mappings)}",
                        skill_name=skill_name,
                        skill_category=resume_skill["skill_category"],
                        proficiency_level=resume_skill["proficiency_level"],
                        job_relevance_score=relevance_score,
                        alignment_confidence=self._calculate_alignment_confidence(resume_skill, job_skill),
                        evidence_in_resume=resume_skill["evidence"],
                        job_requirements_met=[skill_name],
                        metadata={
                            "importance_level": job_skill.get("importance_level", "nice_to_have"),
                            "frequency": resume_skill["frequency"]
                        }
                    )
                    mappings.append(mapping)
            
            # Also check for partial matches and related skills
            elif strategy["industry_standards"]:
                related_mappings = self._find_related_skill_mappings(resume_skill, job_skills, strategy)
                mappings.extend(related_mappings)
        
        return mappings
    
    def _identify_skill_gaps(self, skill_mappings: List[SkillMapping], job_skills: List[Dict[str, Any]], strategy: Dict[str, Any]) -> List[SkillGap]:
        """Identify skill gaps between resume and job requirements."""
        gaps = []
        
        # Get mapped skill names
        mapped_skills = set(mapping.skill_name for mapping in skill_mappings)
        
        # Find required skills not in resume
        for job_skill in job_skills:
            skill_name = job_skill["skill_name"]
            importance_level = job_skill.get("importance_level", "nice_to_have")
            
            if skill_name not in mapped_skills and importance_level in ["critical", "important"]:
                gap = SkillGap(
                    gap_id=f"gap_{len(gaps)}",
                    missing_skill=skill_name,
                    skill_category=job_skill["skill_category"],
                    importance_level=importance_level,
                    acquisition_suggestions=self._generate_acquisition_suggestions(skill_name, job_skill["skill_category"]),
                    confidence_score=0.8,
                    metadata={
                        "reason": "not_found_in_resume",
                        "industry": strategy["target_industry"]
                    }
                )
                gaps.append(gap)
        
        return gaps
    
    def _determine_proficiency_level(self, content: str, skill: str) -> str:
        """Determine proficiency level based on context."""
        # Look for proficiency indicators near the skill
        skill_context = self._get_skill_context(content, skill)
        
        for proficiency, indicators in self.proficiency_indicators.items():
            for indicator in indicators:
                if indicator in skill_context:
                    return proficiency
        
        # Default to intermediate if no indicators found
        return "intermediate"
    
    def _find_skill_evidence(self, content: str, skill: str) -> List[str]:
        """Find evidence of skill usage in content."""
        evidence = []
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            if skill in sentence.lower():
                evidence.append(sentence.strip())
        
        return evidence[:3]  # Return top 3 evidence pieces
    
    def _get_skill_context(self, content: str, skill: str) -> str:
        """Get context around skill mention."""
        skill_pos = content.find(skill)
        if skill_pos == -1:
            return ""
        
        start = max(0, skill_pos - 50)
        end = min(len(content), skill_pos + 50)
        
        return content[start:end]
    
    def _determine_skill_importance(self, skill: str, industry: str) -> str:
        """Determine skill importance based on industry standards."""
        industry_mapping = self.industry_mappings.get(industry, self.industry_mappings["general"])
        
        if skill in industry_mapping["critical"]:
            return "critical"
        elif skill in industry_mapping["important"]:
            return "important"
        elif skill in industry_mapping["nice_to_have"]:
            return "nice_to_have"
        else:
            return "nice_to_have"
    
    def _calculate_relevance_score(self, resume_skill: Dict[str, Any], job_skill: Dict[str, Any], strategy: Dict[str, Any]) -> float:
        """Calculate relevance score for skill mapping."""
        base_score = 0.5
        
        # Factor in importance level
        importance = job_skill.get("importance_level", "nice_to_have")
        importance_scores = {"critical": 0.4, "important": 0.3, "nice_to_have": 0.1}
        base_score += importance_scores.get(importance, 0.1)
        
        # Factor in proficiency level
        proficiency = resume_skill.get("proficiency_level", "intermediate")
        proficiency_scores = {"expert": 0.3, "advanced": 0.2, "intermediate": 0.1, "beginner": 0.05}
        base_score += proficiency_scores.get(proficiency, 0.1)
        
        # Factor in frequency/evidence
        frequency = resume_skill.get("frequency", 1)
        evidence_count = len(resume_skill.get("evidence", []))
        base_score += min(frequency * 0.05, 0.2) + min(evidence_count * 0.1, 0.2)
        
        return min(base_score, 1.0)
    
    def _calculate_alignment_confidence(self, resume_skill: Dict[str, Any], job_skill: Dict[str, Any]) -> float:
        """Calculate confidence score for skill alignment."""
        base_confidence = 0.6
        
        # Factor in evidence quality
        evidence = resume_skill.get("evidence", [])
        if evidence:
            base_confidence += min(len(evidence) * 0.1, 0.3)
        
        # Factor in category match
        if resume_skill.get("skill_category") == job_skill.get("skill_category"):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _find_related_skill_mappings(self, resume_skill: Dict[str, Any], job_skills: List[Dict[str, Any]], strategy: Dict[str, Any]) -> List[SkillMapping]:
        """Find related skill mappings for partial matches."""
        mappings = []
        skill_name = resume_skill["skill_name"]
        
        # Simple related skill detection (could be enhanced with semantic similarity)
        for job_skill in job_skills:
            job_skill_name = job_skill["skill_name"]
            
            # Check for partial matches or related technologies
            if self._are_skills_related(skill_name, job_skill_name):
                relevance_score = 0.4  # Lower score for related skills
                
                if relevance_score >= strategy["min_relevance_score"]:
                    mapping = SkillMapping(
                        skill_id=f"related_mapping_{len(mappings)}",
                        skill_name=skill_name,
                        skill_category=resume_skill["skill_category"],
                        proficiency_level=resume_skill["proficiency_level"],
                        job_relevance_score=relevance_score,
                        alignment_confidence=0.6,
                        evidence_in_resume=resume_skill["evidence"],
                        job_requirements_met=[job_skill_name],
                        metadata={
                            "mapping_type": "related",
                            "related_to": job_skill_name
                        }
                    )
                    mappings.append(mapping)
        
        return mappings
    
    def _are_skills_related(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are related."""
        # Simple keyword-based relatedness (could be enhanced with NLP)
        related_groups = [
            ["python", "javascript", "typescript", "java", "c++"],  # Programming languages
            ["react", "vue", "angular"],  # Frontend frameworks
            ["aws", "azure", "gcp"],  # Cloud platforms
            ["docker", "kubernetes"],  # Container technologies
            ["sql", "nosql", "mongodb", "postgresql"],  # Databases
        ]
        
        for group in related_groups:
            if skill1 in group and skill2 in group:
                return True
        
        return False
    
    def _generate_acquisition_suggestions(self, skill: str, category: str) -> List[str]:
        """Generate suggestions for acquiring missing skills."""
        suggestions = []
        
        if category == "technical":
            suggestions.extend([
                f"Take online courses in {skill}",
                f"Build personal projects using {skill}",
                f"Get certified in {skill}",
                f"Contribute to open source {skill} projects"
            ])
        elif category == "soft":
            suggestions.extend([
                f"Practice {skill} in team projects",
                f"Take workshops on {skill}",
                f"Seek mentorship for {skill} development",
                f"Join professional groups focused on {skill}"
            ])
        elif category == "certification":
            suggestions.extend([
                f"Prepare for {skill} certification exam",
                f"Attend {skill} training programs",
                f"Join study groups for {skill}",
                f"Gain practical experience before certification"
            ])
        else:
            suggestions.extend([
                f"Learn {skill} through online resources",
                f"Attend industry workshops on {skill}",
                f"Network with professionals in {skill}",
                f"Read industry publications about {skill}"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _deduplicate_skills(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate skills, keeping highest frequency."""
        seen_skills = {}
        deduplicated = []
        
        for skill in skills:
            key = skill["skill_name"]
            if key not in seen_skills or skill.get("frequency", 0) > seen_skills[key].get("frequency", 0):
                seen_skills[key] = skill
        
        return list(seen_skills.values())
    
    def _generate_mapped_content(self, skill_mappings: List[SkillMapping], skill_gaps: List[SkillGap]) -> str:
        """Generate content with skill mappings and gaps highlighted."""
        content_parts = []
        
        # Add skill mappings summary
        if skill_mappings:
            content_parts.append("## Skills Mapped to Job Requirements\n")
            
            # Group by category
            by_category: Dict[str, List[SkillMapping]] = {}
            for mapping in skill_mappings:
                category = mapping.skill_category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(mapping)
            
            for category, mappings in by_category.items():
                content_parts.append(f"### {category.title()} Skills\n")
                for mapping in sorted(mappings, key=lambda x: x.job_relevance_score, reverse=True):
                    content_parts.append(f"• **{mapping.skill_name.title()}** ({mapping.proficiency_level.title()})")
                    content_parts.append(f"  - Relevance: {mapping.job_relevance_score:.2f}")
                    content_parts.append(f"  - Evidence: {len(mapping.evidence_in_resume)} instances found")
                content_parts.append("")
        
        # Add skill gaps summary
        if skill_gaps:
            content_parts.append("## Skill Gaps Identified\n")
            
            # Group by importance
            by_importance = {"critical": [], "important": []}
            for gap in skill_gaps:
                if gap.importance_level in by_importance:
                    by_importance[gap.importance_level].append(gap)
            
            for importance, gaps in by_importance.items():
                if gaps:
                    content_parts.append(f"### {importance.title()} Missing Skills\n")
                    for gap in gaps:
                        content_parts.append(f"• **{gap.missing_skill.title()}** ({gap.skill_category})")
                        content_parts.append(f"  - Suggestions: {', '.join(gap.acquisition_suggestions[:2])}")
                    content_parts.append("")
        
        return '\n'.join(content_parts)
    
    def _calculate_mapping_metrics(self, skill_mappings: List[SkillMapping], skill_gaps: List[SkillGap], job_skills: List[Dict[str, Any]]) -> SkillMappingMetrics:
        """Calculate skill mapping performance metrics."""
        total_skills = len(skill_mappings)
        
        # Count by category
        skills_by_category = {}
        for mapping in skill_mappings:
            category = mapping.skill_category
            skills_by_category[category] = skills_by_category.get(category, 0) + 1
        
        # Calculate average relevance
        if skill_mappings:
            avg_relevance = sum(mapping.job_relevance_score for mapping in skill_mappings) / len(skill_mappings)
        else:
            avg_relevance = 0.0
        
        # Calculate coverage percentage
        critical_important_jobs = [skill for skill in job_skills if skill.get("importance_level") in ["critical", "important"]]
        if critical_important_jobs:
            covered_skills = set(mapping.skill_name for mapping in skill_mappings)
            required_skills = set(skill["skill_name"] for skill in critical_important_jobs)
            coverage = len(covered_skills & required_skills) / len(required_skills) * 100
        else:
            coverage = 0.0
        
        # Calculate overall confidence
        if skill_mappings:
            avg_confidence = sum(mapping.alignment_confidence for mapping in skill_mappings) / len(skill_mappings)
        else:
            avg_confidence = 0.0
        
        return SkillMappingMetrics(
            total_skills_mapped=total_skills,
            skills_by_category=skills_by_category,
            average_job_relevance=avg_relevance,
            skill_gaps_identified=len(skill_gaps),
            coverage_percentage=coverage,
            mapping_confidence=avg_confidence,
            processing_time_ms=300  # Placeholder
        )
    
    def _safe_record_telemetry(self, mapping_output: SkillMappingOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_k5_skillmap_executed", {
                    "skills_mapped": mapping_output.metrics.total_skills_mapped,
                    "skill_gaps_identified": mapping_output.metrics.skill_gaps_identified,
                    "coverage_percentage": mapping_output.metrics.coverage_percentage,
                    "success": mapping_output.success
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_skill_mapping_summary(self, mapping_output: SkillMappingOutput) -> Dict[str, Any]:
        """Get a summary of the skill mapping execution for debugging/telemetry."""
        return {
            "execution_id": "rg_k5_skillmap",
            "skills_mapped": mapping_output.metrics.total_skills_mapped,
            "average_relevance": mapping_output.metrics.average_job_relevance,
            "skill_gaps_identified": mapping_output.metrics.skill_gaps_identified,
            "coverage_percentage": mapping_output.metrics.coverage_percentage,
            "success": mapping_output.success
        }
