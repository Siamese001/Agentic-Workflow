"""RG K6 Assemble - Resume Section Assembly and Organization

Incorporated from historical agentic_workflow/l2/rg_k6_section_assembly.py to execute
advanced resume section assembly with intelligent organization.

This is the sixth execution phase in the resume generation pipeline:
K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class SectionAssembly:
    """Individual assembled resume section."""
    section_id: str
    section_name: str
    content: str
    position: int  # Order in resume
    priority: str  # "high", "medium", "low"
    word_count: int
    relevance_score: float  # 0.0 to 1.0
    assembly_confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssemblyMetrics:
    """Metrics from section assembly process."""
    total_sections_assembled: int
    total_word_count: int
    sections_by_priority: Dict[str, int]
    average_relevance_score: float
    assembly_confidence: float
    organization_quality: float  # 0.0 to 1.0
    processing_time_ms: int


@dataclass
class AssemblyOutput:
    """Complete output from K6 assembly phase."""
    assembled_sections: List[SectionAssembly]
    assembled_content: str
    metrics: AssemblyMetrics
    assembly_plan: Dict[str, Any]
    success: bool
    error_message: str
    processing_trace: List[Dict[str, Any]] = field(default_factory=list)


class RGK6Assemble:
    """K6 Resume Section Assembler - Sixth hop in sequential processing pipeline.
    
    Executes advanced resume section assembly and organization:
    - Organize sections by optimal order for target role
    - Prioritize content based on relevance to job requirements
    - Ensure logical flow and readability
    - Balance section lengths and content distribution
    """
    
    def __init__(self, 
                 assembly_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K6 resume section assembler."""
        self.assembly_plan = assembly_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Standard section order templates
        self.section_templates = {
            "chronological": [
                ("contact_info", 1, "high"),
                ("summary", 2, "high"),
                ("experience", 3, "high"),
                ("education", 4, "medium"),
                ("skills", 5, "high"),
                ("projects", 6, "medium"),
                ("certifications", 7, "low"),
                ("achievements", 8, "medium")
            ],
            "functional": [
                ("contact_info", 1, "high"),
                ("summary", 2, "high"),
                ("skills", 3, "high"),
                ("experience", 4, "high"),
                ("projects", 5, "medium"),
                ("education", 6, "medium"),
                ("certifications", 7, "low"),
                ("achievements", 8, "medium")
            ],
            "hybrid": [
                ("contact_info", 1, "high"),
                ("summary", 2, "high"),
                ("skills", 3, "high"),
                ("experience", 4, "high"),
                ("projects", 5, "medium"),
                ("education", 6, "medium"),
                ("certifications", 7, "low"),
                ("achievements", 8, "medium")
            ],
            "targeted": [
                ("contact_info", 1, "high"),
                ("summary", 2, "high"),
                ("experience", 3, "high"),
                ("skills", 4, "high"),
                ("projects", 5, "medium"),
                ("education", 6, "medium"),
                ("certifications", 7, "low"),
                ("achievements", 8, "medium")
            ]
        }
        
        # Section priority weights for different roles
        self.role_priorities = {
            "technical": {
                "skills": "high",
                "experience": "high",
                "projects": "high",
                "education": "medium",
                "certifications": "medium",
                "achievements": "medium"
            },
            "management": {
                "experience": "high",
                "summary": "high",
                "achievements": "high",
                "education": "medium",
                "skills": "medium",
                "projects": "low",
                "certifications": "low"
            },
            "executive": {
                "summary": "high",
                "experience": "high",
                "achievements": "high",
                "education": "medium",
                "skills": "medium",
                "certifications": "low",
                "projects": "low"
            },
            "entry_level": {
                "education": "high",
                "skills": "high",
                "projects": "high",
                "experience": "medium",
                "achievements": "medium",
                "certifications": "low",
                "summary": "medium"
            },
            "general": {
                "experience": "high",
                "skills": "high",
                "education": "medium",
                "summary": "high",
                "projects": "medium",
                "achievements": "medium",
                "certifications": "low"
            }
        }
        
        # Target word counts by section
        self.target_word_counts = {
            "contact_info": 50,
            "summary": 150,
            "experience": 400,
            "education": 150,
            "skills": 200,
            "projects": 250,
            "certifications": 100,
            "achievements": 150
        }
    
    def assemble_resume_sections(
        self,
        *,
        skill_mapping_output: Any,  # From K5 skill mapping
        job_requirements: Dict[str, Any],
        assembly_params: Optional[Dict[str, Any]] = None
    ) -> AssemblyOutput:
        """Execute resume section assembly and organization.
        
        Args:
            skill_mapping_output: Output from K5 skill mapping phase
            job_requirements: Target job requirements and specifications
            assembly_params: Assembly strategy and parameters
            
        Returns:
            Complete assembly output with organized sections and metrics
        """
        assembly_params = assembly_params or {}
        processing_trace = []
        
        try:
            # 1. Initialize assembly strategy
            strategy = self._initialize_assembly_strategy(assembly_params, job_requirements)
            processing_trace.append({
                "step": "strategy_initialization",
                "strategy": strategy,
                "timestamp": "2024-01-01T00:00:01Z"
            })
            
            # 2. Extract content from K5 output
            content_sections = self._extract_content_sections(skill_mapping_output)
            processing_trace.append({
                "step": "content_extraction",
                "sections_found": len(content_sections),
                "timestamp": "2024-01-01T00:00:02Z"
            })
            
            # 3. Determine optimal section organization
            organization = self._determine_section_organization(content_sections, strategy)
            processing_trace.append({
                "step": "organization_determination",
                "template": organization["template"],
                "timestamp": "2024-01-01T00:00:03Z"
            })
            
            # 4. Prioritize sections based on job relevance
            prioritized_sections = self._prioritize_sections(content_sections, strategy)
            processing_trace.append({
                "step": "section_prioritization",
                "prioritized_count": len(prioritized_sections),
                "timestamp": "2024-01-01T00:00:04Z"
            })
            
            # 5. Assemble sections in optimal order
            assembled_sections = self._assemble_sections(prioritized_sections, organization, strategy)
            processing_trace.append({
                "step": "section_assembly",
                "sections_assembled": len(assembled_sections),
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 6. Optimize content flow and balance
            optimized_sections = self._optimize_content_flow(assembled_sections, strategy)
            processing_trace.append({
                "step": "content_optimization",
                "optimizations_applied": len(assembled_sections) - len(optimized_sections),
                "timestamp": "2024-01-01T00:00:06Z"
            })
            
            # 7. Generate final assembled content
            assembled_content = self._generate_assembled_content(optimized_sections)
            processing_trace.append({
                "step": "content_generation",
                "final_length": len(assembled_content),
                "timestamp": "2024-01-01T00:00:07Z"
            })
            
            # 8. Calculate assembly metrics
            metrics = self._calculate_assembly_metrics(optimized_sections)
            processing_trace.append({
                "step": "metrics_calculation",
                "organization_quality": metrics.organization_quality,
                "timestamp": "2024-01-01T00:00:08Z"
            })
            
            # 9. Build assembly output
            assembly_output = AssemblyOutput(
                assembled_sections=optimized_sections,
                assembled_content=assembled_content,
                metrics=metrics,
                assembly_plan={
                    "strategy": strategy,
                    "parameters": assembly_params,
                    "organization": organization
                },
                success=True,
                error_message="",
                processing_trace=processing_trace
            )
            
            # 10. Record telemetry (best-effort)
            self._safe_record_telemetry(assembly_output)
            
            return assembly_output
            
        except Exception as e:
            logger.error(f"Resume section assembly failed: {e}")
            
            error_output = AssemblyOutput(
                assembled_sections=[],
                assembled_content="",
                metrics=AssemblyMetrics(0, 0, {}, 0.0, 0.0, 0.0, 0),
                assembly_plan={},
                success=False,
                error_message=str(e),
                processing_trace=processing_trace + [{
                    "step": "error",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:09Z"
                }]
            )
            
            return error_output
    
    def _initialize_assembly_strategy(self, params: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize assembly strategy based on parameters and job requirements."""
        return {
            "organization": params.get("organization", "targeted"),
            "prioritize_relevant": params.get("prioritize_relevant", True),
            "maintain_flow": params.get("maintain_flow", True),
            "balance_length": params.get("balance_length", True),
            "target_role": job_requirements.get("title", ""),
            "target_industry": job_requirements.get("industry", "general"),
            "experience_level": job_requirements.get("experience_level", "mid"),
            "max_total_words": params.get("max_total_words", 1000)
        }
    
    def _extract_content_sections(self, skill_mapping_output: Any) -> List[Dict[str, Any]]:
        """Extract content sections from K5 skill mapping output."""
        sections = []
        
        if hasattr(skill_mapping_output, 'skill_mappings'):
            # Extract from skill mappings
            mappings = skill_mapping_output.skill_mappings
            
            # Group by category
            by_category = {}
            for mapping in mappings:
                category = mapping.skill_category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(mapping)
            
            for category, category_mappings in by_category.items():
                content = "\n".join([
                    f"• {mapping.skill_name.title()} ({mapping.proficiency_level.title()})"
                    for mapping in sorted(category_mappings, key=lambda x: x.job_relevance_score, reverse=True)
                ])
                
                sections.append({
                    "section_id": f"{category}_section",
                    "section_name": category,
                    "content": content,
                    "source": "skill_mappings"
                })
        
        elif isinstance(skill_mapping_output, dict):
            # Extract from mapped content
            mapped_content = skill_mapping_output.get("mapped_content", "")
            
            # Parse sections from content
            section_matches = re.findall(r'##\s*(.+?)\n(.*?)(?=##|\Z)', mapped_content, re.DOTALL)
            
            for section_name, section_content in section_matches:
                sections.append({
                    "section_id": f"{section_name.lower().replace(' ', '_')}_section",
                    "section_name": section_name.lower().replace(' ', '_'),
                    "content": section_content.strip(),
                    "source": "mapped_content"
                })
        
        return sections
    
    def _determine_section_organization(self, sections: List[Dict[str, Any]], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal section organization template."""
        organization_type = strategy["organization"]
        experience_level = strategy["experience_level"]
        target_role = strategy["target_role"].lower()
        
        # Select base template
        if organization_type in self.section_templates:
            base_template = self.section_templates[organization_type]
        else:
            base_template = self.section_templates["targeted"]
        
        # Adjust based on experience level
        if experience_level == "entry_level":
            # Prioritize education and skills for entry level
            adjusted_template = []
            for section_name, position, priority in base_template:
                if section_name in ["education", "skills", "projects"]:
                    new_priority = "high"
                elif section_name == "experience":
                    new_priority = "medium"
                else:
                    new_priority = priority
                adjusted_template.append((section_name, position, new_priority))
            base_template = adjusted_template
        
        # Adjust based on role-specific priorities
        role_type = self._classify_role_type(target_role)
        if role_type in self.role_priorities:
            role_priorities = self.role_priorities[role_type]
            
            adjusted_template = []
            for section_name, position, base_priority in base_template:
                role_priority = role_priorities.get(section_name, base_priority)
                adjusted_template.append((section_name, position, role_priority))
            base_template = adjusted_template
        
        return {
            "template": organization_type,
            "section_order": base_template,
            "role_type": role_type,
            "experience_adjusted": experience_level == "entry_level"
        }
    
    def _classify_role_type(self, role_title: str) -> str:
        """Classify role type based on title keywords."""
        role_lower = role_title.lower()
        
        if any(keyword in role_lower for keyword in ["manager", "director", "head", "lead", "supervisor"]):
            return "management"
        elif any(keyword in role_lower for keyword in ["ceo", "cto", "cfo", "executive", "vp", "chief"]):
            return "executive"
        elif any(keyword in role_lower for keyword in ["developer", "engineer", "programmer", "technical", "software"]):
            return "technical"
        elif any(keyword in role_lower for keyword in ["junior", "entry", "associate", "intern", "graduate"]):
            return "entry_level"
        else:
            return "general"
    
    def _prioritize_sections(self, sections: List[Dict[str, Any]], strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize sections based on job relevance and strategy."""
        prioritized_sections = []
        
        for section in sections:
            section_name = section["section_name"]
            
            # Calculate relevance score
            relevance_score = self._calculate_section_relevance(section, strategy)
            
            # Determine priority
            role_type = self._classify_role_type(strategy["target_role"])
            role_priorities = self.role_priorities.get(role_type, self.role_priorities["general"])
            priority = role_priorities.get(section_name, "medium")
            
            prioritized_section = {
                **section,
                "relevance_score": relevance_score,
                "priority": priority,
                "word_count": len(section["content"].split())
            }
            prioritized_sections.append(prioritized_section)
        
        # Sort by priority and relevance
        priority_order = {"high": 3, "medium": 2, "low": 1}
        prioritized_sections.sort(
            key=lambda x: (priority_order.get(x["priority"], 1), x["relevance_score"]),
            reverse=True
        )
        
        return prioritized_sections
    
    def _calculate_section_relevance(self, section: Dict[str, Any], strategy: Dict[str, Any]) -> float:
        """Calculate relevance score for a section."""
        base_score = 0.5
        
        # Factor in content quality
        content = section.get("content", "")
        if len(content) > 50:
            base_score += 0.1
        
        # Factor in keywords relevant to target role
        target_role = strategy["target_role"].lower()
        role_keywords = {
            "technical": ["developed", "implemented", "engineered", "technical", "software"],
            "management": ["managed", "led", "directed", "team", "project"],
            "executive": ["strategic", "leadership", "executive", "business", "revenue"],
            "general": ["experience", "skills", "achieved", "results"]
        }
        
        role_type = self._classify_role_type(target_role)
        keywords = role_keywords.get(role_type, role_keywords["general"])
        
        keyword_matches = sum(1 for keyword in keywords if keyword in content.lower())
        base_score += min(keyword_matches * 0.1, 0.3)
        
        # Factor in section name importance
        section_name = section["section_name"]
        important_sections = ["experience", "skills", "summary", "education"]
        if section_name in important_sections:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _assemble_sections(self, sections: List[Dict[str, Any]], organization: Dict[str, Any], strategy: Dict[str, Any]) -> List[SectionAssembly]:
        """Assemble sections in optimal order."""
        assembled_sections = []
        section_order = organization["section_order"]
        
        # Create section lookup
        section_lookup = {section["section_name"]: section for section in sections}
        
        for position, (section_name, template_position, template_priority) in enumerate(section_order, 1):
            if section_name in section_lookup:
                section_data = section_lookup[section_name]
                
                assembled_section = SectionAssembly(
                    section_id=section_data["section_id"],
                    section_name=section_name,
                    content=section_data["content"],
                    position=position,
                    priority=section_data["priority"],
                    word_count=section_data["word_count"],
                    relevance_score=section_data["relevance_score"],
                    assembly_confidence=self._calculate_assembly_confidence(section_data, strategy),
                    metadata={
                        "template_position": template_position,
                        "template_priority": template_priority,
                        "source": section_data.get("source", "unknown")
                    }
                )
                assembled_sections.append(assembled_section)
        
        return assembled_sections
    
    def _calculate_assembly_confidence(self, section: Dict[str, Any], strategy: Dict[str, Any]) -> float:
        """Calculate confidence score for section assembly."""
        base_confidence = 0.7
        
        # Factor in relevance score
        relevance = section.get("relevance_score", 0.5)
        base_confidence += relevance * 0.2
        
        # Factor in content length
        word_count = section.get("word_count", 0)
        if word_count > 20:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _optimize_content_flow(self, sections: List[SectionAssembly], strategy: Dict[str, Any]) -> List[SectionAssembly]:
        """Optimize content flow and balance section lengths."""
        optimized_sections = sections.copy()
        
        if not strategy["balance_length"]:
            return optimized_sections
        
        # Calculate total words and target distribution
        total_words = sum(section.word_count for section in optimized_sections)
        max_words = strategy.get("max_total_words", 1000)
        
        if total_words > max_words:
            # Need to reduce content
            reduction_factor = max_words / total_words
            
            for section in optimized_sections:
                if section.priority != "high":  # Don't reduce high priority sections
                    target_words = int(section.word_count * reduction_factor)
                    section.content = self._truncate_content(section.content, target_words)
                    section.word_count = len(section.content.split())
        
        # Ensure logical flow
        if strategy["maintain_flow"]:
            optimized_sections = self._ensure_logical_flow(optimized_sections)
        
        return optimized_sections
    
    def _truncate_content(self, content: str, target_words: int) -> str:
        """Truncate content to target word count while preserving structure."""
        words = content.split()
        
        if len(words) <= target_words:
            return content
        
        # Keep bullet points intact
        lines = content.split('\n')
        result_lines = []
        current_words = 0
        
        for line in lines:
            line_words = len(line.split())
            if current_words + line_words <= target_words:
                result_lines.append(line)
                current_words += line_words
            else:
                # Truncate the line
                remaining_words = target_words - current_words
                if remaining_words > 0:
                    truncated_line = ' '.join(line.split()[:remaining_words])
                    result_lines.append(truncated_line)
                break
        
        return '\n'.join(result_lines)
    
    def _ensure_logical_flow(self, sections: List[SectionAssembly]) -> List[SectionAssembly]:
        """Ensure logical flow between sections."""
        # Simple flow optimization - ensure summary comes before experience
        summary_idx = None
        experience_idx = None
        
        for i, section in enumerate(sections):
            if section.section_name == "summary":
                summary_idx = i
            elif section.section_name == "experience":
                experience_idx = i
        
        # If summary comes after experience, swap them
        if summary_idx is not None and experience_idx is not None and summary_idx > experience_idx:
            sections[summary_idx], sections[experience_idx] = sections[experience_idx], sections[summary_idx]
            # Update positions
            sections[summary_idx].position = summary_idx + 1
            sections[experience_idx].position = experience_idx + 1
        
        return sections
    
    def _generate_assembled_content(self, sections: List[SectionAssembly]) -> str:
        """Generate final assembled resume content."""
        content_parts = []
        
        # Sort by position
        sorted_sections = sorted(sections, key=lambda x: x.position)
        
        for section in sorted_sections:
            if section.content.strip():  # Only include non-empty sections
                content_parts.append(f"## {section.section_name.replace('_', ' ').title()}\n{section.content}\n")
        
        return '\n'.join(content_parts)
    
    def _calculate_assembly_metrics(self, sections: List[SectionAssembly]) -> AssemblyMetrics:
        """Calculate assembly performance metrics."""
        total_sections = len(sections)
        total_words = sum(section.word_count for section in sections)
        
        # Count by priority
        sections_by_priority = {"high": 0, "medium": 0, "low": 0}
        for section in sections:
            priority = section.priority
            sections_by_priority[priority] = sections_by_priority.get(priority, 0) + 1
        
        # Calculate average relevance
        if sections:
            avg_relevance = sum(section.relevance_score for section in sections) / len(sections)
        else:
            avg_relevance = 0.0
        
        # Calculate overall confidence
        if sections:
            avg_confidence = sum(section.assembly_confidence for section in sections) / len(sections)
        else:
            avg_confidence = 0.0
        
        # Calculate organization quality
        organization_quality = self._calculate_organization_quality(sections)
        
        return AssemblyMetrics(
            total_sections_assembled=total_sections,
            total_word_count=total_words,
            sections_by_priority=sections_by_priority,
            average_relevance_score=avg_relevance,
            assembly_confidence=avg_confidence,
            organization_quality=organization_quality,
            processing_time_ms=350  # Placeholder
        )
    
    def _calculate_organization_quality(self, sections: List[SectionAssembly]) -> float:
        """Calculate organization quality score."""
        quality_score = 0.5
        
        # Check for proper section order
        section_names = [section.section_name for section in sections]
        
        # Summary should be early
        if "summary" in section_names and section_names.index("summary") <= 2:
            quality_score += 0.1
        
        # Contact info should be first
        if section_names and section_names[0] == "contact_info":
            quality_score += 0.1
        
        # Experience and skills should be present
        if "experience" in section_names and "skills" in section_names:
            quality_score += 0.1
        
        # Check for balanced content distribution
        word_counts = [section.word_count for section in sections]
        if word_counts:
            max_words = max(word_counts)
            min_words = min(word_counts)
            if max_words > 0:
                balance_ratio = min_words / max_words
                quality_score += min(balance_ratio, 0.2)
        
        return min(quality_score, 1.0)
    
    def _safe_record_telemetry(self, assembly_output: AssemblyOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_k6_assemble_executed", {
                    "sections_assembled": assembly_output.metrics.total_sections_assembled,
                    "total_word_count": assembly_output.metrics.total_word_count,
                    "organization_quality": assembly_output.metrics.organization_quality,
                    "success": assembly_output.success
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_assembly_summary(self, assembly_output: AssemblyOutput) -> Dict[str, Any]:
        """Get a summary of the assembly execution for debugging/telemetry."""
        return {
            "execution_id": "rg_k6_assemble",
            "sections_assembled": assembly_output.metrics.total_sections_assembled,
            "total_word_count": assembly_output.metrics.total_word_count,
            "average_relevance": assembly_output.metrics.average_relevance_score,
            "organization_quality": assembly_output.metrics.organization_quality,
            "success": assembly_output.success
        }





