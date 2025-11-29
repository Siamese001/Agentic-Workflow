"""RG K7 Format - Resume Professional Formatting and Layout

Incorporated from historical agentic_workflow/l2/rg_k7_format.py to execute
advanced resume formatting with professional layout optimization.

This is the seventh execution phase in the resume generation pipeline:
K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class FormattingRule:
    """Individual formatting rule applied to content."""
    rule_id: str
    rule_type: str  # "layout", "typography", "structure", "ats_optimization"
    description: str
    applied_to: str  # Section or content area
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormattedSection:
    """Formatted resume section with layout optimization."""
    section_id: str
    section_name: str
    original_content: str
    formatted_content: str
    formatting_rules: List[FormattingRule]
    layout_score: float  # 0.0 to 1.0
    readability_score: float  # 0.0 to 1.0
    ats_compliance_score: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormattingMetrics:
    """Metrics from resume formatting process."""
    total_sections_formatted: int
    formatting_rules_applied: int
    layout_optimizations: int
    typography_improvements: int
    ats_optimizations: int
    average_readability_score: float
    overall_ats_compliance: float
    formatting_confidence: float
    processing_time_ms: int


@dataclass
class FormattingOutput:
    """Complete output from K7 formatting phase."""
    formatted_sections: List[FormattedSection]
    formatted_content: str
    formatting_rules: List[FormattingRule]
    metrics: FormattingMetrics
    formatting_plan: Dict[str, Any]
    success: bool
    error_message: str
    processing_trace: List[Dict[str, Any]] = field(default_factory=list)


class RGK7Format:
    """K7 Resume Formatter - Seventh hop in sequential processing pipeline.
    
    Executes advanced resume formatting with multiple strategies:
    - Professional layout optimization and structure
    - Typography improvements and consistency
    - ATS (Applicant Tracking System) compliance
    - Readability enhancement and visual hierarchy
    """
    
    def __init__(self, 
                 formatting_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K7 resume formatter."""
        self.formatting_plan = formatting_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Formatting standards and templates
        self.formatting_standards = {
            "ats_optimized": {
                "font_family": "Arial, Helvetica, sans-serif",
                "font_size": "11pt",
                "line_spacing": "1.0",
                "margins": "1 inch",
                "bullet_style": "standard",
                "date_format": "MM/YYYY",
                "section_headers": "bold",
                "no_columns": True,
                "no_tables": True,
                "no_images": True
            },
            "professional": {
                "font_family": "Calibri, Arial, sans-serif",
                "font_size": "11pt",
                "line_spacing": "1.15",
                "margins": "0.75 inch",
                "bullet_style": "modern",
                "date_format": "Month YYYY",
                "section_headers": "bold_caps",
                "columns_allowed": False,
                "simple_layout": True
            },
            "creative": {
                "font_family": "Helvetica, Arial, sans-serif",
                "font_size": "10.5pt",
                "line_spacing": "1.2",
                "margins": "0.5 inch",
                "bullet_style": "custom",
                "date_format": "Month YYYY",
                "section_headers": "styled",
                "columns_allowed": True,
                "visual_elements": True
            },
            "executive": {
                "font_family": "Times New Roman, serif",
                "font_size": "12pt",
                "line_spacing": "1.0",
                "margins": "1 inch",
                "bullet_style": "classic",
                "date_format": "Month YYYY",
                "section_headers": "centered_bold",
                "formal_layout": True,
                "conservative_style": True
            }
        }
        
        # Typography and layout rules
        self.typography_rules = {
            "consistency": [
                (r'\s+', ' '),  # Normalize whitespace
                (r'\n\s*\n', '\n\n'),  # Normalize paragraph breaks
                (r'([.!?])\s*([A-Z])', r'\1 \2'),  # Proper sentence spacing
            ],
            "capitalization": [
                (r'##\s*(.+)', lambda m: '## ' + m.group(1).title()),  # Title case headers
                (r'•\s*([a-z])', lambda m: '• ' + m.group(1).upper()),  # Capitalize bullet starts
            ],
            "punctuation": [
                (r'\s*([.,;:!?])\s*', r'\1 '),  # Space around punctuation
                (r'([a-z])([A-Z])', r'\1 \2'),  # Add space between words
            ]
        }
        
        # ATS optimization rules
        self.ats_rules = {
            "file_format": [
                "Use .docx or .pdf format",
                "Avoid .pages or other proprietary formats"
            ],
            "content_structure": [
                "Use standard section headers",
                "Avoid tables and columns",
                "Use standard bullet points (• or -)",
                "Avoid special characters and symbols"
            ],
            "contact_info": [
                "Include name, phone, email, LinkedIn",
                "Avoid embedded images or graphics",
                "Use standard date formats"
            ],
            "keywords": [
                "Include job-specific keywords",
                "Match terminology from job description",
                "Use industry-standard acronyms"
            ]
        }
        
        # Readability improvement rules
        self.readability_rules = {
            "sentence_length": {
                "target": 15-20,  # words per sentence
                "max": 25
            },
            "paragraph_length": {
                "target": 3-4,  # sentences per paragraph
                "max": 6
            },
            "bullet_points": {
                "max_per_section": 8,
                "ideal_length": "1-2 lines"
            },
            "section_length": {
                "max_words": 400,
                "min_words": 50
            }
        }
    
    def format_resume_content(
        self,
        *,
        assembly_output: Any,  # From K6 assembly
        formatting_params: Optional[Dict[str, Any]] = None
    ) -> FormattingOutput:
        """Execute resume formatting and layout optimization.
        
        Args:
            assembly_output: Output from K6 assembly phase
            formatting_params: Formatting strategy and parameters
            
        Returns:
            Complete formatting output with professional layout and metrics
        """
        formatting_params = formatting_params or {}
        processing_trace = []
        
        try:
            # 1. Initialize formatting strategy
            strategy = self._initialize_formatting_strategy(formatting_params)
            processing_trace.append({
                "step": "strategy_initialization",
                "strategy": strategy,
                "timestamp": "2024-01-01T00:00:01Z"
            })
            
            # 2. Extract assembled content
            content_sections = self._extract_assembled_sections(assembly_output)
            processing_trace.append({
                "step": "content_extraction",
                "sections_found": len(content_sections),
                "timestamp": "2024-01-01T00:00:02Z"
            })
            
            # 3. Apply typography improvements
            typography_improved = self._apply_typography_improvements(content_sections, strategy)
            processing_trace.append({
                "step": "typography_improvements",
                "improvements_applied": len(typography_improved),
                "timestamp": "2024-01-01T00:00:03Z"
            })
            
            # 4. Optimize layout and structure
            layout_optimized = self._optimize_layout_structure(typography_improved, strategy)
            processing_trace.append({
                "step": "layout_optimization",
                "optimizations_applied": len(layout_optimized),
                "timestamp": "2024-01-01T00:00:04Z"
            })
            
            # 5. Apply ATS compliance rules
            ats_optimized = self._apply_ats_compliance(layout_optimized, strategy)
            processing_trace.append({
                "step": "ats_optimization",
                "ats_rules_applied": len(ats_optimized),
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 6. Enhance readability
            readability_enhanced = self._enhance_readability(ats_optimized, strategy)
            processing_trace.append({
                "step": "readability_enhancement",
                "enhancements_applied": len(readability_enhanced),
                "timestamp": "2024-01-01T00:00:06Z"
            })
            
            # 7. Generate final formatted content
            formatted_content = self._generate_formatted_content(readability_enhanced)
            processing_trace.append({
                "step": "content_generation",
                "final_length": len(formatted_content),
                "timestamp": "2024-01-01T00:00:07Z"
            })
            
            # 8. Calculate formatting metrics
            metrics = self._calculate_formatting_metrics(readability_enhanced)
            processing_trace.append({
                "step": "metrics_calculation",
                "overall_ats_compliance": metrics.overall_ats_compliance,
                "timestamp": "2024-01-01T00:00:08Z"
            })
            
            # 9. Collect all formatting rules
            all_rules = self._collect_formatting_rules(readability_enhanced)
            
            # 10. Build formatting output
            formatting_output = FormattingOutput(
                formatted_sections=readability_enhanced,
                formatted_content=formatted_content,
                formatting_rules=all_rules,
                metrics=metrics,
                formatting_plan={
                    "strategy": strategy,
                    "parameters": formatting_params,
                    "standards_applied": strategy["standards"]
                },
                success=True,
                error_message="",
                processing_trace=processing_trace
            )
            
            # 11. Record telemetry (best-effort)
            self._safe_record_telemetry(formatting_output)
            
            return formatting_output
            
        except Exception as e:
            logger.error(f"Resume formatting failed: {e}")
            
            error_output = FormattingOutput(
                formatted_sections=[],
                formatted_content="",
                formatting_rules=[],
                metrics=FormattingMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0),
                formatting_plan={},
                success=False,
                error_message=str(e),
                processing_trace=processing_trace + [{
                    "step": "error",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:09Z"
                }]
            )
            
            return error_output
    
    def _initialize_formatting_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize formatting strategy based on parameters."""
        standards = params.get("standards", "ats_optimized")
        
        return {
            "standards": standards,
            "layout_optimization": params.get("layout_optimization", True),
            "readability_focus": params.get("readability_focus", True),
            "ats_compliance": params.get("ats_compliance", True),
            "target_role": params.get("target_role", ""),
            "target_industry": params.get("target_industry", "general"),
            "format_spec": self.formatting_standards.get(standards, self.formatting_standards["ats_optimized"])
        }
    
    def _extract_assembled_sections(self, assembly_output: Any) -> List[Dict[str, Any]]:
        """Extract assembled sections from K6 output."""
        sections = []
        
        if hasattr(assembly_output, 'assembled_sections'):
            for section in assembly_output.assembled_sections:
                sections.append({
                    "section_id": section.section_id,
                    "section_name": section.section_name,
                    "content": section.content,
                    "position": section.position,
                    "priority": section.priority
                })
        elif isinstance(assembly_output, dict):
            assembled_content = assembly_output.get("assembled_content", "")
            
            # Parse sections from content
            section_matches = re.findall(r'##\s*(.+?)\n(.*?)(?=##|\Z)', assembled_content, re.DOTALL)
            
            for i, (section_name, section_content) in enumerate(section_matches):
                sections.append({
                    "section_id": f"{section_name.lower().replace(' ', '_')}_section",
                    "section_name": section_name.lower().replace(' ', '_'),
                    "content": section_content.strip(),
                    "position": i + 1,
                    "priority": "medium"
                })
        
        return sections
    
    def _apply_typography_improvements(self, sections: List[Dict[str, Any]], strategy: Dict[str, Any]) -> List[FormattedSection]:
        """Apply typography improvements to sections."""
        formatted_sections = []
        
        for section in sections:
            content = section["content"]
            original_content = content
            applied_rules = []
            
            # Apply typography rules
            for rule_type, rules in self.typography_rules.items():
                for pattern, replacement in rules:
                    if callable(replacement):
                        new_content = re.sub(pattern, replacement, content)
                    else:
                        new_content = re.sub(pattern, replacement, content)
                    
                    if new_content != content:
                        rule = FormattingRule(
                            rule_id=f"typo_{rule_type}_{len(applied_rules)}",
                            rule_type="typography",
                            description=f"Applied {rule_type} rule",
                            applied_to=section["section_name"],
                            confidence_score=0.8,
                            metadata={"pattern": pattern, "rule_type": rule_type}
                        )
                        applied_rules.append(rule)
                        content = new_content
            
            formatted_section = FormattedSection(
                section_id=section["section_id"],
                section_name=section["section_name"],
                original_content=original_content,
                formatted_content=content,
                formatting_rules=applied_rules,
                layout_score=0.7,  # Will be calculated in layout optimization
                readability_score=0.7,  # Will be calculated in readability enhancement
                ats_compliance_score=0.7,  # Will be calculated in ATS optimization
                metadata={
                    "position": section["position"],
                    "priority": section["priority"]
                }
            )
            formatted_sections.append(formatted_section)
        
        return formatted_sections
    
    def _optimize_layout_structure(self, sections: List[FormattedSection], strategy: Dict[str, Any]) -> List[FormattedSection]:
        """Optimize layout and structure of sections."""
        optimized_sections = []
        
        for section in sections:
            content = section.formatted_content
            applied_rules = section.formatting_rules.copy()
            
            # Apply layout optimizations based on standards
            format_spec = strategy["format_spec"]
            
            # Ensure consistent section headers
            if format_spec.get("section_headers") == "bold":
                content = re.sub(r'##\s*(.+)', lambda m: f"## **{m.group(1)}**", content)
                applied_rules.append(FormattingRule(
                    rule_id=f"layout_bold_headers_{len(applied_rules)}",
                    rule_type="layout",
                    description="Applied bold section headers",
                    applied_to=section.section_name,
                    confidence_score=0.9
                ))
            elif format_spec.get("section_headers") == "bold_caps":
                content = re.sub(r'##\s*(.+)', lambda m: f"## **{m.group(1).upper()}**", content)
                applied_rules.append(FormattingRule(
                    rule_id=f"layout_bold_caps_headers_{len(applied_rules)}",
                    rule_type="layout",
                    description="Applied bold caps section headers",
                    applied_to=section.section_name,
                    confidence_score=0.9
                ))
            
            # Ensure consistent bullet points
            if format_spec.get("bullet_style") == "standard":
                content = re.sub(r'[·→\*]+', '•', content)
                content = re.sub(r'•\s*', '• ', content)
                applied_rules.append(FormattingRule(
                    rule_id=f"layout_standard_bullets_{len(applied_rules)}",
                    rule_type="layout",
                    description="Applied standard bullet points",
                    applied_to=section.section_name,
                    confidence_score=0.85
                ))
            
            # Update section with layout optimizations
            section.formatted_content = content
            section.formatting_rules = applied_rules
            section.layout_score = self._calculate_layout_score(content, format_spec)
            
            optimized_sections.append(section)
        
        return optimized_sections
    
    def _apply_ats_compliance(self, sections: List[FormattedSection], strategy: Dict[str, Any]) -> List[FormattedSection]:
        """Apply ATS compliance rules."""
        ats_compliant_sections = []
        
        for section in sections:
            content = section.formatted_content
            applied_rules = section.formatting_rules.copy()
            
            if strategy["ats_compliance"]:
                # Remove special characters that ATS systems might not parse
                content = re.sub(r'[^\w\s\-\.\,\;\:\!\?\n\#\•]', '', content)
                applied_rules.append(FormattingRule(
                    rule_id=f"ats_special_chars_{len(applied_rules)}",
                    rule_type="ats_optimization",
                    description="Removed special characters for ATS compatibility",
                    applied_to=section.section_name,
                    confidence_score=0.8
                ))
                
                # Ensure proper date format
                content = re.sub(r'(\d{1,2})/(\d{1,2})/(\d{4})', r'\1/\2/\3', content)
                applied_rules.append(FormattingRule(
                    rule_id=f"ats_date_format_{len(applied_rules)}",
                    rule_type="ats_optimization",
                    description="Standardized date format for ATS",
                    applied_to=section.section_name,
                    confidence_score=0.75
                ))
                
                # Check for standard section headers
                standard_headers = ["contact", "summary", "experience", "education", "skills"]
                section_name = section.section_name.lower()
                if section_name in standard_headers:
                    applied_rules.append(FormattingRule(
                        rule_id=f"ats_standard_header_{len(applied_rules)}",
                        rule_type="ats_optimization",
                        description="Using standard ATS-compatible section header",
                        applied_to=section.section_name,
                        confidence_score=0.9
                    ))
            
            # Update section with ATS optimizations
            section.formatted_content = content
            section.formatting_rules = applied_rules
            section.ats_compliance_score = self._calculate_ats_compliance_score(content, strategy)
            
            ats_compliant_sections.append(section)
        
        return ats_compliant_sections
    
    def _enhance_readability(self, sections: List[FormattedSection], strategy: Dict[str, Any]) -> List[FormattedSection]:
        """Enhance readability of sections."""
        readability_enhanced_sections = []
        
        for section in sections:
            content = section.formatted_content
            applied_rules = section.formatting_rules.copy()
            
            if strategy["readability_focus"]:
                # Break up long paragraphs
                paragraphs = content.split('\n\n')
                enhanced_paragraphs = []
                
                for paragraph in paragraphs:
                    sentences = re.split(r'[.!?]+', paragraph)
                    sentences = [s.strip() for s in sentences if s.strip()]
                    
                    # Group sentences into readable chunks
                    chunk_size = self.readability_rules["paragraph_length"]["max"]
                    for i in range(0, len(sentences), chunk_size):
                        chunk = sentences[i:i + chunk_size]
                        if chunk:
                            enhanced_paragraphs.append('. '.join(chunk) + '.')
                
                enhanced_content = '\n\n'.join(enhanced_paragraphs)
                
                if enhanced_content != content:
                    applied_rules.append(FormattingRule(
                        rule_id=f"read_paragraph_break_{len(applied_rules)}",
                        rule_type="structure",
                        description="Optimized paragraph length for readability",
                        applied_to=section.section_name,
                        confidence_score=0.8
                    ))
                    content = enhanced_content
                
                # Ensure consistent bullet point length
                bullet_points = re.findall(r'•\s*(.+?)(?=•|\n\n|$)', content, re.DOTALL)
                if bullet_points:
                    optimized_bullets = []
                    for bullet in bullet_points:
                        bullet = bullet.strip()
                        # Limit bullet point length
                        if len(bullet) > 200:  # characters
                            bullet = bullet[:197] + "..."
                        optimized_bullets.append(f"• {bullet}")
                    
                    # Replace bullet points in content
                    bullet_section = '\n'.join(optimized_bullets)
                    content = re.sub(r'•\s*.+(?=•|\n\n|$)', bullet_section, content, flags=re.DOTALL)
                    
                    applied_rules.append(FormattingRule(
                        rule_id=f"read_bullet_length_{len(applied_rules)}",
                        rule_type="structure",
                        description="Optimized bullet point length for readability",
                        applied_to=section.section_name,
                        confidence_score=0.75
                    ))
            
            # Update section with readability enhancements
            section.formatted_content = content
            section.formatting_rules = applied_rules
            section.readability_score = self._calculate_readability_score(content)
            
            readability_enhanced_sections.append(section)
        
        return readability_enhanced_sections
    
    def _calculate_layout_score(self, content: str, format_spec: Dict[str, Any]) -> float:
        """Calculate layout quality score."""
        score = 0.5
        
        # Check for consistent headers
        if '##' in content:
            score += 0.1
        
        # Check for consistent bullets
        if '•' in content and not any(char in content for char in ['·', '→', '*']):
            score += 0.1
        
        # Check for proper spacing
        if not re.search(r'\s{3,}', content):  # No excessive spaces
            score += 0.1
        
        # Check for structure
        if re.search(r'\n\n', content):  # Has paragraph breaks
            score += 0.1
        
        # Length appropriateness
        word_count = len(content.split())
        if 50 <= word_count <= 400:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_ats_compliance_score(self, content: str, strategy: Dict[str, Any]) -> float:
        """Calculate ATS compliance score."""
        score = 0.5
        
        # Check for special characters
        if not re.search(r'[^\w\s\-\.\,\;\:\!\?\n\#\•]', content):
            score += 0.2
        
        # Check for standard formatting
        if '##' in content and '•' in content:
            score += 0.1
        
        # Check for no tables/columns indicators
        if not any(indicator in content.lower() for indicator in ['table', 'column', '|']):
            score += 0.1
        
        # Check for contact info patterns
        if re.search(r'(email|phone|linkedin)', content.lower()):
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score."""
        score = 0.5
        
        # Sentence length analysis
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            target_length = (self.readability_rules["sentence_length"]["target"][0] + 
                           self.readability_rules["sentence_length"]["target"][1]) / 2
            
            if 10 <= avg_sentence_length <= 20:
                score += 0.2
            elif avg_sentence_length <= 25:
                score += 0.1
        
        # Paragraph length analysis
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            if avg_paragraph_length <= 100:  # words
                score += 0.2
        
        # Bullet point analysis
        bullet_points = re.findall(r'•\s*(.+)', content)
        if bullet_points:
            avg_bullet_length = sum(len(bp.split()) for bp in bullet_points) / len(bullet_points)
            if avg_bullet_length <= 15:  # words per bullet
                score += 0.1
        
        return min(score, 1.0)
    
    def _generate_formatted_content(self, sections: List[FormattedSection]) -> str:
        """Generate final formatted resume content."""
        content_parts = []
        
        # Sort sections by position
        sorted_sections = sorted(sections, key=lambda x: x.metadata.get("position", 0))
        
        for section in sorted_sections:
            if section.formatted_content.strip():
                content_parts.append(section.formatted_content)
        
        return '\n\n'.join(content_parts)
    
    def _collect_formatting_rules(self, sections: List[FormattedSection]) -> List[FormattingRule]:
        """Collect all formatting rules from sections."""
        all_rules = []
        
        for section in sections:
            all_rules.extend(section.formatting_rules)
        
        return all_rules
    
    def _calculate_formatting_metrics(self, sections: List[FormattedSection]) -> FormattingMetrics:
        """Calculate formatting performance metrics."""
        total_sections = len(sections)
        total_rules = sum(len(section.formatting_rules) for section in sections)
        
        # Count rule types
        layout_rules = sum(1 for section in sections 
                          for rule in section.formatting_rules 
                          if rule.rule_type == "layout")
        typography_rules = sum(1 for section in sections 
                             for rule in section.formatting_rules 
                             if rule.rule_type == "typography")
        ats_rules = sum(1 for section in sections 
                       for rule in section.formatting_rules 
                       if rule.rule_type == "ats_optimization")
        
        # Calculate average scores
        if sections:
            avg_readability = sum(section.readability_score for section in sections) / len(sections)
            avg_ats_compliance = sum(section.ats_compliance_score for section in sections) / len(sections)
            avg_confidence = sum(section.layout_score for section in sections) / len(sections)
        else:
            avg_readability = avg_ats_compliance = avg_confidence = 0.0
        
        return FormattingMetrics(
            total_sections_formatted=total_sections,
            formatting_rules_applied=total_rules,
            layout_optimizations=layout_rules,
            typography_improvements=typography_rules,
            ats_optimizations=ats_rules,
            average_readability_score=avg_readability,
            overall_ats_compliance=avg_ats_compliance,
            formatting_confidence=avg_confidence,
            processing_time_ms=400  # Placeholder
        )
    
    def _safe_record_telemetry(self, formatting_output: FormattingOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_k7_format_executed", {
                    "sections_formatted": formatting_output.metrics.total_sections_formatted,
                    "formatting_rules_applied": formatting_output.metrics.formatting_rules_applied,
                    "ats_compliance": formatting_output.metrics.overall_ats_compliance,
                    "success": formatting_output.success
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_formatting_summary(self, formatting_output: FormattingOutput) -> Dict[str, Any]:
        """Get a summary of the formatting execution for debugging/telemetry."""
        return {
            "execution_id": "rg_k7_format",
            "sections_formatted": formatting_output.metrics.total_sections_formatted,
            "formatting_rules_applied": formatting_output.metrics.formatting_rules_applied,
            "average_readability": formatting_output.metrics.average_readability_score,
            "ats_compliance": formatting_output.metrics.overall_ats_compliance,
            "success": formatting_output.success
        }





