"""
Resume Formatting Utilities
LEVEL 5 - Text formatting, layout, and presentation utilities
"""

from typing import Dict, List, Any
import re
from dataclasses import dataclass
from enum import Enum

class FormatType(Enum):
    """Supported resume formats"""
    CHRONOLOGICAL = "chronological"
    FUNCTIONAL = "functional"
    HYBRID = "hybrid"
    TARGETED = "targeted"

@dataclass
class FormattingOptions:
    """Options for resume formatting"""
    format_type: FormatType
    font_size: int = 12
    line_spacing: float = 1.15
    margin_inches: float = 1.0
    include_summary: bool = True
    max_bullet_points: int = 6
    action_verb_style: str = "past_tense"

class ResumeFormatter:
    """Handles resume formatting and layout optimization"""

    def __init__(self):
        self.section_order = {
            FormatType.CHRONOLOGICAL: ["summary", "experience", "education", "skills"],
            FormatType.FUNCTIONAL: ["summary", "skills", "experience", "education"],
            FormatType.HYBRID: ["summary", "skills", "experience", "education"],
            FormatType.TARGETED: ["summary", "skills", "experience", "education", "projects"]
        }

        self.formatting_rules = {
            "max_line_length": 80,
            "max_words_per_bullet": 25,
            "section_spacing": 2,
            "subsection_spacing": 1
        }

    async def format_resume(
        self,
        resume_content: Dict[str, Any],
        options: FormattingOptions
    ) -> Dict[str, Any]:
        """
        Format resume content according to specified options
        
        Args:
            resume_content: Raw resume content
            options: Formatting preferences
            
        Returns:
            Formatted resume with layout information
        """
        # Reorder sections based on format type
        ordered_content = await self._reorder_sections(resume_content, options.format_type)

        # Format each section
        formatted_sections = {}
        for section_name, section_content in ordered_content.items():
            formatted_section = await self._format_section(section_name, section_content, options)
            formatted_sections[section_name] = formatted_section

        # Apply global formatting
        formatted_resume = await self._apply_global_formatting(formatted_sections, options)

        # Add layout metadata
        layout_info = await self._generate_layout_info(formatted_resume, options)

        return {
            "content": formatted_resume,
            "layout": layout_info,
            "metadata": {
                "format_type": options.format_type.value,
                "word_count": await self._calculate_word_count(formatted_resume),
                "page_count": layout_info.get("estimated_pages", 1)
            }
        }

    async def _reorder_sections(
        self,
        resume_content: Dict[str, Any],
        format_type: FormatType
    ) -> Dict[str, Any]:
        """Reorder sections based on format type"""
        desired_order = self.section_order[format_type]
        ordered_content = {}

        # Add sections in desired order
        for section_name in desired_order:
            # Find matching section (case-insensitive)
            for existing_name, content in resume_content.items():
                if section_name.lower() in existing_name.lower():
                    ordered_content[existing_name] = content
                    break

        # Add any remaining sections
        for remaining_name, content in resume_content.items():
            if remaining_name not in ordered_content:
                ordered_content[remaining_name] = content

        return ordered_content

    async def _format_section(
        self,
        section_name: str,
        section_content: Dict[str, Any],
        options: FormattingOptions
    ) -> Dict[str, Any]:
        """Format individual section"""
        formatted_content = section_content.copy()
        content_items = section_content.get("content", [])

        if isinstance(content_items, list):
            formatted_items = []

            for item in content_items:
                # Format bullet points
                if item.strip().startswith("•"):
                    formatted_bullet = await self._format_bullet_point(item, options)
                    formatted_items.append(formatted_bullet)
                else:
                    # Format regular text
                    formatted_text = await self._format_text_line(item, options)
                    formatted_items.append(formatted_text)

            # Limit bullet points if specified
            if len(formatted_items) > options.max_bullet_points:
                formatted_items = formatted_items[:options.max_bullet_points]

            formatted_content["content"] = formatted_items

        return formatted_content

    async def _format_bullet_point(self, bullet: str, options: FormattingOptions) -> str:
        """Format individual bullet point"""
        # Remove existing bullet and clean up
        clean_bullet = bullet.strip()
        if clean_bullet.startswith("•"):
            clean_bullet = clean_bullet[1:].strip()

        # Ensure action verb (past tense)
        if options.action_verb_style == "past_tense":
            clean_bullet = await self._ensure_past_tense(clean_bullet)

        # Check word count
        words = clean_bullet.split()
        if len(words) > self.formatting_rules["max_words_per_bullet"]:
            # Truncate to last complete sentence
            sentences = re.split(r'[.!?]+', clean_bullet)
            if len(sentences) > 1:
                clean_bullet = sentences[0] + "."

        # Check line length
        if len(clean_bullet) > self.formatting_rules["max_line_length"]:
            # Try to break at logical points
            clean_bullet = await self._break_long_line(clean_bullet)

        return f"• {clean_bullet}"

    async def _format_text_line(self, text: str, options: FormattingOptions) -> str:
        """Format regular text line"""
        clean_text = text.strip()

        # Check line length
        if len(clean_text) > self.formatting_rules["max_line_length"]:
            clean_text = await self._break_long_line(clean_text)

        return clean_text

    async def _ensure_past_tense(self, text: str) -> str:
        """Ensure text starts with past tense action verb"""
        action_verbs_present = ["manages", "leads", "develops", "implements", "coordinates"]
        action_verbs_past = ["managed", "led", "developed", "implemented", "coordinated"]

        words = text.split()
        if words and words[0].lower() in action_verbs_present:
            verb_index = action_verbs_present.index(words[0].lower())
            words[0] = action_verbs_past[verb_index]
            return " ".join(words)

        return text

    async def _break_long_line(self, text: str) -> str:
        """Break long line at logical points"""
        if len(text) <= self.formatting_rules["max_line_length"]:
            return text

        # Try to break at commas or semicolons
        for separator in [",", ";", " and ", " or "]:
            if separator in text:
                parts = text.split(separator)
                if len(parts) >= 2:
                    # Find the best break point
                    for i in range(len(parts) - 1):
                        partial = separator.join(parts[:i+1]).strip()
                        if len(partial) <= self.formatting_rules["max_line_length"] - 3:
                            return partial + "..."

        # If no good break point, truncate with ellipsis
        max_len = self.formatting_rules["max_line_length"] - 3
        return text[:max_len] + "..."

    async def _apply_global_formatting(
        self,
        formatted_sections: Dict[str, Any],
        options: FormattingOptions
    ) -> Dict[str, Any]:
        """Apply global formatting rules"""
        formatted_resume = formatted_sections.copy()

        # Add section headers formatting
        for section_name in formatted_resume:
            if "title" not in formatted_resume[section_name]:
                # Create formatted title from section name
                formatted_title = section_name.replace("_", " ").title()
                formatted_resume[section_name]["title"] = formatted_title

        # Ensure consistent spacing
        formatted_resume = await self._ensure_consistent_spacing(formatted_resume)

        return formatted_resume

    async def _ensure_consistent_spacing(self, resume_content: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure consistent spacing between sections"""
        # This would handle spacing logic
        # For now, return as-is
        return resume_content

    async def _generate_layout_info(
        self,
        formatted_resume: Dict[str, Any],
        options: FormattingOptions
    ) -> Dict[str, Any]:
        """Generate layout information"""
        word_count = await self._calculate_word_count(formatted_resume)

        # Estimate page count based on word count and formatting
        words_per_page = 500  # Approximate
        estimated_pages = max(1, (word_count + words_per_page - 1) // words_per_page)

        return {
            "font_size": options.font_size,
            "line_spacing": options.line_spacing,
            "margins": options.margin_inches,
            "estimated_pages": estimated_pages,
            "section_count": len(formatted_resume),
            "format_optimized": True
        }

    async def _calculate_word_count(self, resume_content: Dict[str, Any]) -> int:
        """Calculate total word count"""
        total_words = 0

        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                for item in content:
                    total_words += len(item.split())
            else:
                total_words += len(str(content).split())

        return total_words

    async def convert_format(
        self,
        resume_content: Dict[str, Any],
        target_format: FormatType
    ) -> Dict[str, Any]:
        """Convert resume to different format type"""
        options = FormattingOptions(format_type=target_format)
        return await self.format_resume(resume_content, options)

    async def get_formatting_recommendations(
        self,
        resume_content: Dict[str, Any]
    ) -> List[str]:
        """Get recommendations for improving formatting"""
        recommendations = []

        # Check word count
        word_count = await self._calculate_word_count(resume_content)
        if word_count < 150:
            recommendations.append("Resume is too brief - consider expanding content")
        elif word_count > 600:
            recommendations.append("Resume may be too long - consider condensing content")

        # Check section balance
        section_counts = {}
        for section_name, section in resume_content.items():
            content = section.get("content", [])
            if isinstance(content, list):
                section_counts[section_name] = len(content)

        if section_counts.get("experience", 0) < 3:
            recommendations.append("Consider adding more experience details")

        return recommendations

__all__ = ["ResumeFormatter", "FormattingOptions", "FormatType"]
