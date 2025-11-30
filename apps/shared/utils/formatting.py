"""
Shared Formatting Utilities
LEVEL 5 - Common formatting functions and classes shared across engines
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TextCase(Enum):
    """Text case options"""
    LOWER = "lower"
    UPPER = "upper"
    TITLE = "title"
    SENTENCE = "sentence"
    CAMEL = "camel"
    SNAKE = "snake"
    KEBAB = "kebab"
    PASCAL = "pascal"

class Alignment(Enum):
    """Text alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"

@dataclass
class FormattingOptions:
    """Options for text formatting"""
    max_line_length: int = 80
    preserve_paragraphs: bool = True
    remove_extra_whitespace: bool = True
    normalize_quotes: bool = True
    normalize_dashes: bool = True
    handle_urls: bool = True
    handle_emails: bool = True

class Formatter:
    """Shared formatting utilities for both engines"""
    
    def __init__(self, default_options: Optional[FormattingOptions] = None):
        self.logger = logging.getLogger(__name__)
        self.options = default_options or FormattingOptions()
        
        # Common patterns
        self.url_pattern = re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.whitespace_pattern = re.compile(r'\s+')
        self.paragraph_pattern = re.compile(r'\n\s*\n')
    
    async def clean_text(self, text: str, options: Optional[FormattingOptions] = None) -> str:
        """Clean and normalize text"""
        try:
            if not text:
                return ""
            
            opts = options or self.options
            cleaned = text
            
            # Normalize quotes
            if opts.normalize_quotes:
                cleaned = cleaned.replace('"', '"').replace('"', '"')
                cleaned = cleaned.replace(''', "'").replace(''', "'")
            
            # Normalize dashes
            if opts.normalize_dashes:
                cleaned = cleaned.replace('–', '-').replace('—', '--')
            
            # Remove extra whitespace
            if opts.remove_extra_whitespace:
                cleaned = self.whitespace_pattern.sub(' ', cleaned)
                cleaned = cleaned.strip()
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Error cleaning text: {e}")
            return text
    
    async def format_case(self, text: str, case_type: TextCase) -> str:
        """Format text case"""
        try:
            if not text:
                return ""
            
            if case_type == TextCase.LOWER:
                return text.lower()
            
            elif case_type == TextCase.UPPER:
                return text.upper()
            
            elif case_type == TextCase.TITLE:
                return text.title()
            
            elif case_type == TextCase.SENTENCE:
                sentences = re.split(r'[.!?]+', text)
                formatted_sentences = []
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence:
                        formatted_sentences.append(sentence[0].upper() + sentence[1:].lower())
                return '. '.join(formatted_sentences)
            
            elif case_type == TextCase.CAMEL:
                words = text.split()
                if not words:
                    return ""
                return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
            
            elif case_type == TextCase.SNAKE:
                return re.sub(r'[^a-zA-Z0-9]+', '_', text).lower().strip('_')
            
            elif case_type == TextCase.KEBAB:
                return re.sub(r'[^a-zA-Z0-9]+', '-', text).lower().strip('-')
            
            elif case_type == TextCase.PASCAL:
                words = text.split()
                return ''.join(word.capitalize() for word in words)
            
            else:
                return text
                
        except Exception as e:
            self.logger.error(f"Error formatting case: {e}")
            return text
    
    async def wrap_text(self, text: str, max_length: Optional[int] = None, 
                       preserve_paragraphs: Optional[bool] = None) -> str:
        """Wrap text to specified line length"""
        try:
            if not text:
                return ""
            
            opts = FormattingOptions(
                max_line_length=max_length or self.options.max_line_length,
                preserve_paragraphs=preserve_paragraphs if preserve_paragraphs is not None else self.options.preserve_paragraphs
            )
            
            if opts.preserve_paragraphs:
                paragraphs = self.paragraph_pattern.split(text)
                wrapped_paragraphs = []
                
                for paragraph in paragraphs:
                    if paragraph.strip():
                        wrapped = self._wrap_paragraph(paragraph.strip(), opts.max_line_length)
                        wrapped_paragraphs.append(wrapped)
                    else:
                        wrapped_paragraphs.append("")
                
                return '\n\n'.join(wrapped_paragraphs)
            else:
                return self._wrap_paragraph(text, opts.max_line_length)
                
        except Exception as e:
            self.logger.error(f"Error wrapping text: {e}")
            return text
    
    async def align_text(self, text: str, alignment: Alignment, 
                        width: Optional[int] = None) -> str:
        """Align text within specified width"""
        try:
            if not text:
                return ""
            
            target_width = width or self.options.max_line_length
            lines = text.split('\n')
            aligned_lines = []
            
            for line in lines:
                if len(line) >= target_width:
                    aligned_lines.append(line)
                    continue
                
                if alignment == Alignment.LEFT:
                    aligned_lines.append(line.ljust(target_width))
                
                elif alignment == Alignment.RIGHT:
                    aligned_lines.append(line.rjust(target_width))
                
                elif alignment == Alignment.CENTER:
                    aligned_lines.append(line.center(target_width))
                
                elif alignment == Alignment.JUSTIFY:
                    words = line.split()
                    if len(words) <= 1:
                        aligned_lines.append(line.ljust(target_width))
                    else:
                        total_spaces = target_width - len(''.join(words))
                        space_count = len(words) - 1
                        if space_count > 0:
                            base_spaces = total_spaces // space_count
                            extra_spaces = total_spaces % space_count
                            
                            justified_line = ""
                            for i, word in enumerate(words):
                                justified_line += word
                                if i < space_count:
                                    spaces = base_spaces + (1 if i < extra_spaces else 0)
                                    justified_line += ' ' * spaces
                            
                            aligned_lines.append(justified_line)
                        else:
                            aligned_lines.append(line.ljust(target_width))
            
            return '\n'.join(aligned_lines)
            
        except Exception as e:
            self.logger.error(f"Error aligning text: {e}")
            return text
    
    async def format_list(self, items: List[str], list_type: str = "bullet", 
                         indent: int = 0, prefix: str = "") -> str:
        """Format a list of items"""
        try:
            if not items:
                return ""
            
            indent_str = ' ' * indent
            
            if list_type == "bullet":
                bullet_chars = ['•', '○', '◦', '▪', '▫']
                formatted_items = []
                for i, item in enumerate(items):
                    bullet = bullet_chars[i % len(bullet_chars)]
                    formatted_items.append(f"{indent_str}{prefix}{bullet} {item}")
                return '\n'.join(formatted_items)
            
            elif list_type == "numbered":
                formatted_items = []
                for i, item in enumerate(items, 1):
                    formatted_items.append(f"{indent_str}{prefix}{i}. {item}")
                return '\n'.join(formatted_items)
            
            elif list_type == "lettered":
                formatted_items = []
                for i, item in enumerate(items):
                    letter = chr(ord('a') + (i % 26))
                    formatted_items.append(f"{indent_str}{prefix}{letter}) {item}")
                return '\n'.join(formatted_items)
            
            elif list_type == "roman":
                def to_roman(n):
                    roman_numerals = [
                        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
                        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
                        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
                    ]
                    result = ""
                    for value, numeral in roman_numerals:
                        while n >= value:
                            result += numeral
                            n -= value
                    return result.lower()
                
                formatted_items = []
                for i, item in enumerate(items, 1):
                    roman = to_roman(i)
                    formatted_items.append(f"{indent_str}{prefix}{roman}) {item}")
                return '\n'.join(formatted_items)
            
            else:
                # Simple list
                formatted_items = []
                for item in items:
                    formatted_items.append(f"{indent_str}{prefix}{item}")
                return '\n'.join(formatted_items)
                
        except Exception as e:
            self.logger.error(f"Error formatting list: {e}")
            return '\n'.join(items)
    
    async def format_table(self, data: List[List[str]], headers: Optional[List[str]] = None,
                          alignment: Optional[List[Alignment]] = None) -> str:
        """Format tabular data"""
        try:
            if not data:
                return ""
            
            # Calculate column widths
            all_rows = data.copy()
            if headers:
                all_rows.insert(0, headers)
            
            col_count = len(all_rows[0])
            col_widths = [0] * col_count
            
            for row in all_rows:
                for i, cell in enumerate(row):
                    if i < col_count:
                        col_widths[i] = max(col_widths[i], len(str(cell)))
            
            # Format rows
            formatted_rows = []
            
            # Format header row if provided
            if headers:
                header_cells = []
                for i, header in enumerate(headers):
                    cell_width = col_widths[i] if i < len(col_widths) else len(header)
                    cell_align = alignment[i] if alignment and i < len(alignment) else Alignment.LEFT
                    
                    if cell_align == Alignment.LEFT:
                        header_cells.append(str(header).ljust(cell_width))
                    elif cell_align == Alignment.RIGHT:
                        header_cells.append(str(header).rjust(cell_width))
                    else:
                        header_cells.append(str(header).center(cell_width))
                
                formatted_rows.append(' | '.join(header_cells))
                
                # Add separator
                separator_cells = []
                for width in col_widths:
                    separator_cells.append('-' * width)
                formatted_rows.append('-+-'.join(separator_cells))
            
            # Format data rows
            for row in data:
                row_cells = []
                for i, cell in enumerate(row):
                    cell_width = col_widths[i] if i < len(col_widths) else len(str(cell))
                    cell_align = alignment[i] if alignment and i < len(alignment) else Alignment.LEFT
                    
                    if cell_align == Alignment.LEFT:
                        row_cells.append(str(cell).ljust(cell_width))
                    elif cell_align == Alignment.RIGHT:
                        row_cells.append(str(cell).rjust(cell_width))
                    else:
                        row_cells.append(str(cell).center(cell_width))
                
                formatted_rows.append(' | '.join(row_cells))
            
            return '\n'.join(formatted_rows)
            
        except Exception as e:
            self.logger.error(f"Error formatting table: {e}")
            return '\n'.join([' | '.join(row) for row in data])
    
    async def format_contact_info(self, contact_data: Dict[str, str]) -> str:
        """Format contact information"""
        try:
            formatted_parts = []
            
            # Name
            if "name" in contact_data:
                formatted_parts.append(f"**{contact_data['name']}**")
            
            # Email
            if "email" in contact_data:
                formatted_parts.append(f"📧 {contact_data['email']}")
            
            # Phone
            if "phone" in contact_data:
                formatted_parts.append(f"📱 {contact_data['phone']}")
            
            # LinkedIn
            if "linkedin" in contact_data:
                formatted_parts.append(f"💼 {contact_data['linkedin']}")
            
            # GitHub
            if "github" in contact_data:
                formatted_parts.append(f"💻 {contact_data['github']}")
            
            # Location
            if "location" in contact_data:
                formatted_parts.append(f"📍 {contact_data['location']}")
            
            # Website
            if "website" in contact_data:
                formatted_parts.append(f"🌐 {contact_data['website']}")
            
            return '\n'.join(formatted_parts)
            
        except Exception as e:
            self.logger.error(f"Error formatting contact info: {e}")
            return str(contact_data)
    
    async def format_skills(self, skills: Dict[str, List[str]], 
                           format_type: str = "categorized") -> str:
        """Format skills by category"""
        try:
            if not skills:
                return ""
            
            if format_type == "categorized":
                formatted_parts = []
                
                for category, skill_list in skills.items():
                    if skill_list:
                        category_name = category.replace('_', ' ').title()
                        formatted_skills = ', '.join(skill_list)
                        formatted_parts.append(f"**{category_name}**: {formatted_skills}")
                
                return '\n'.join(formatted_parts)
            
            elif format_type == "flat":
                all_skills = []
                for skill_list in skills.values():
                    all_skills.extend(skill_list)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_skills = []
                for skill in all_skills:
                    if skill not in seen:
                        seen.add(skill)
                        unique_skills.append(skill)
                
                return ', '.join(unique_skills)
            
            elif format_type == "bulleted":
                formatted_parts = []
                
                for category, skill_list in skills.items():
                    if skill_list:
                        category_name = category.replace('_', ' ').title()
                        formatted_parts.append(f"**{category_name}**:")
                        
                        for skill in skill_list:
                            formatted_parts.append(f"  • {skill}")
                        
                        formatted_parts.append("")  # Add spacing
                
                return '\n'.join(formatted_parts).strip()
            
            else:
                return str(skills)
                
        except Exception as e:
            self.logger.error(f"Error formatting skills: {e}")
            return str(skills)
    
    async def format_experience_entry(self, experience: Dict[str, Any]) -> str:
        """Format a single experience entry"""
        try:
            formatted_parts = []
            
            # Title and Company
            title = experience.get("title", "")
            company = experience.get("company", "")
            if title and company:
                formatted_parts.append(f"**{title}** - {company}")
            elif title:
                formatted_parts.append(f"**{title}**")
            elif company:
                formatted_parts.append(f"**{company}**")
            
            # Location and Dates
            location = experience.get("location", "")
            start_date = experience.get("start_date", "")
            end_date = experience.get("end_date", "")
            
            details = []
            if location:
                details.append(location)
            if start_date and end_date:
                details.append(f"{start_date} - {end_date}")
            elif start_date:
                details.append(f"{start_date} - Present")
            
            if details:
                formatted_parts.append(" | ".join(details))
            
            # Description
            description = experience.get("description", "")
            if description:
                formatted_parts.append(f"\n{description}")
            
            # Achievements
            achievements = experience.get("achievements", [])
            if achievements:
                formatted_parts.append("\n**Key Achievements:**")
                for achievement in achievements:
                    formatted_parts.append(f"  • {achievement}")
            
            return '\n'.join(formatted_parts)
            
        except Exception as e:
            self.logger.error(f"Error formatting experience entry: {e}")
            return str(experience)
    
    async def format_resume_section(self, section_name: str, content: Union[str, List[Dict[str, Any]]],
                                   section_type: str = "text") -> str:
        """Format a resume section"""
        try:
            formatted_section = f"\n## {section_name}\n"
            
            if section_type == "text":
                formatted_section += f"\n{content}"
            
            elif section_type == "experience":
                if isinstance(content, list):
                    for item in content:
                        entry = await self.format_experience_entry(item)
                        formatted_section += f"\n{entry}\n"
            
            elif section_type == "skills":
                if isinstance(content, dict):
                    skills_formatted = await self.format_skills(content)
                    formatted_section += f"\n{skills_formatted}"
            
            elif section_type == "list":
                if isinstance(content, list):
                    list_formatted = await self.format_list(content, "bullet", 2)
                    formatted_section += f"\n{list_formatted}"
            
            return formatted_section
            
        except Exception as e:
            self.logger.error(f"Error formatting resume section: {e}")
            return f"\n## {section_name}\n{content}"
    
    def _wrap_paragraph(self, text: str, max_length: int) -> str:
        """Wrap a single paragraph"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + (1 if current_line else 0) <= max_length:
                current_line.append(word)
                current_length += len(word) + (1 if current_line else 0)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)

@dataclass
class FormattingResult:
    """Result of formatting operations"""
    original_text: str
    formatted_text: str
    formatting_options: FormattingOptions
    processing_timestamp: str
    processing_time_ms: float
