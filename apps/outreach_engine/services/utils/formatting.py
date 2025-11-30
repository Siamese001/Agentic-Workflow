"""
Outreach Formatting Utilities
LEVEL 5 - Text formatting, layout, and presentation utilities for outreach messages
"""

from typing import Dict, Any
import logging
import re

class OutreachFormatter:
    """Utility class for formatting outreach message content"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Formatting configurations
        self.format_configs = {
            "email": {
                "max_line_length": 72,
                "paragraph_spacing": 2,
                "signature_format": "formal",
                "subject_style": "professional"
            },
            "linkedin": {
                "max_line_length": 80,
                "paragraph_spacing": 1,
                "signature_format": "casual",
                "subject_style": "engaging"
            },
            "cold_call": {
                "max_line_length": 60,
                "paragraph_spacing": 1,
                "signature_format": "brief",
                "subject_style": "direct"
            }
        }

        # Text cleaning patterns
        self.cleaning_patterns = {
            "extra_whitespace": r'\s+',
            "excessive_punctuation": r'([.!?])\1+',
            "multiple_newlines": r'\n{3,}',
            "trailing_whitespace": r'\s+$',
            "leading_whitespace": r'^\s+'
        }

        # Professional formatting rules
        self.formatting_rules = {
            "capitalization": {
                "sentence_start": True,
                "proper_nouns": True,
                "no_excessive_caps": True
            },
            "punctuation": {
                "proper_ending": True,
                "comma_usage": True,
                "no_double_spaces": True
            },
            "structure": {
                "proper_paragraphs": True,
                "logical_flow": True,
                "readability": True
            }
        }

    async def format_message(
        self,
        content: Dict[str, str],
        outreach_type: str,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Format outreach message content according to type and preferences
        
        Args:
            content: Raw message content
            outreach_type: Type of outreach message
            preferences: Formatting preferences
            
        Returns:
            Formatted message content
        """
        try:
            self.logger.info(f"Formatting {outreach_type} message")

            # Get format configuration
            config = self.format_configs.get(outreach_type, self.format_configs["email"])

            # Clean and format each section
            formatted_content = {}

            for section_name, section_content in content.items():
                if not section_content:
                    continue

                # Apply formatting pipeline
                formatted_section = await self._format_section(
                    section_content, section_name, config, preferences
                )
                formatted_content[section_name] = formatted_section

            # Apply cross-section formatting
            formatted_content = await self._apply_cross_section_formatting(
                formatted_content, config, preferences
            )

            return formatted_content

        except Exception as e:
            self.logger.error(f"Error formatting message: {e}")
            raise e

    async def _format_section(
        self,
        content: str,
        section_name: str,
        config: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> str:
        """Format a specific message section"""

        # Clean text
        cleaned_content = await self._clean_text(content)

        # Apply section-specific formatting
        if section_name == "subject":
            formatted = await self._format_subject(cleaned_content, config, preferences)
        elif section_name == "body":
            formatted = await self._format_body(cleaned_content, config, preferences)
        elif section_name == "call_to_action":
            formatted = await self._format_call_to_action(cleaned_content, config, preferences)
        elif section_name == "closing":
            formatted = await self._format_closing(cleaned_content, config, preferences)
        else:
            formatted = await self._format_generic_section(cleaned_content, config, preferences)

        return formatted

    async def _clean_text(self, text: str) -> str:
        """Clean text by removing formatting issues"""

        cleaned = text

        # Remove extra whitespace
        cleaned = re.sub(self.cleaning_patterns["extra_whitespace"], ' ', cleaned)

        # Fix excessive punctuation
        cleaned = re.sub(self.cleaning_patterns["excessive_punctuation"], r'\1', cleaned)

        # Fix multiple newlines
        cleaned = re.sub(self.cleaning_patterns["multiple_newlines"], '\n\n', cleaned)

        # Remove trailing and leading whitespace
        cleaned = re.sub(self.cleaning_patterns["trailing_whitespace"], '', cleaned)
        cleaned = re.sub(self.cleaning_patterns["leading_whitespace"], '', cleaned)

        return cleaned.strip()

    async def _format_subject(
        self,
        subject: str,
        config: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> str:
        """Format subject line"""

        formatted = subject

        # Apply capitalization
        formatted = await self._apply_capitalization(formatted, "sentence")

        # Ensure proper length
        max_length = 100  # Standard email subject limit
        if len(formatted) > max_length:
            formatted = formatted[:max_length - 3] + "..."

        # Apply style based on configuration
        style = config.get("subject_style", "professional")
        if style == "engaging":
            # Add engaging elements if appropriate
            if not any(char in formatted for char in ['?', '|']):
                formatted = formatted + " | Discussion"
        elif style == "direct":
            # Keep it concise and direct
            formatted = formatted.split("|")[0].strip()

        return formatted

    async def _format_body(
        self,
        body: str,
        config: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> str:
        """Format message body"""

        formatted = body

        # Apply paragraph formatting
        formatted = await self._format_paragraphs(formatted, config)

        # Apply line length limits
        max_line_length = config.get("max_line_length", 72)
        formatted = await self._apply_line_wrapping(formatted, max_line_length)

        # Apply capitalization rules
        formatted = await self._apply_capitalization(formatted, "paragraph")

        # Apply punctuation rules
        formatted = await self._apply_punctuation_rules(formatted)

        return formatted

    async def _format_call_to_action(
        self,
        cta: str,
        config: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> str:
        """Format call to action"""

        formatted = cta

        # Ensure it ends with question mark or period
        if not formatted.endswith(('.', '?')):
            if '?' in formatted:
                formatted = formatted.rstrip('.') + '?'
            else:
                formatted += '.'

        # Apply capitalization
        formatted = await self._apply_capitalization(formatted, "sentence")

        return formatted

    async def _format_closing(
        self,
        closing: str,
        config: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> str:
        """Format message closing"""

        formatted = closing

        # Apply signature format
        signature_format = config.get("signature_format", "formal")

        if signature_format == "formal":
            if not formatted.startswith("Best regards") and not formatted.startswith("Sincerely"):
                formatted = "Best regards,\n" + formatted
        elif signature_format == "casual":
            if not formatted.startswith("Best") and not formatted.startswith("Thanks"):
                formatted = "Best,\n" + formatted
        elif signature_format == "brief":
            # Keep as is, just ensure proper formatting
            pass

        return formatted

    async def _format_generic_section(
        self,
        content: str,
        config: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> str:
        """Format a generic message section"""

        formatted = content

        # Apply basic formatting
        formatted = await self._apply_capitalization(formatted, "sentence")
        formatted = await self._apply_punctuation_rules(formatted)

        return formatted

    async def _format_paragraphs(
        self,
        text: str,
        config: Dict[str, Any]
    ) -> str:
        """Format paragraphs with proper spacing"""

        paragraphs = text.split('\n\n')
        formatted_paragraphs = []

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Ensure paragraph starts with capital letter
                if paragraph and paragraph[0].islower():
                    paragraph = paragraph[0].upper() + paragraph[1:]

                formatted_paragraphs.append(paragraph)

        # Join with proper spacing
        spacing = config.get("paragraph_spacing", 2)
        separator = '\n' * spacing

        return separator.join(formatted_paragraphs)

    async def _apply_line_wrapping(self, text: str, max_length: int) -> str:
        """Apply line wrapping to respect max line length"""

        lines = text.split('\n')
        wrapped_lines = []

        for line in lines:
            if len(line) <= max_length:
                wrapped_lines.append(line)
            else:
                # Wrap long lines
                words = line.split(' ')
                current_line = []
                current_length = 0

                for word in words:
                    if current_length + len(word) + 1 <= max_length:
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        if current_line:
                            wrapped_lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)

                if current_line:
                    wrapped_lines.append(' '.join(current_line))

        return '\n'.join(wrapped_lines)

    async def _apply_capitalization(self, text: str, mode: str) -> str:
        """Apply capitalization rules"""

        if mode == "sentence":
            # Capitalize first letter of each sentence
            sentences = re.split(r'([.!?]\s+)', text)
            for i, sentence in enumerate(sentences):
                if i % 2 == 0 and sentence.strip():  # Actual sentences
                    sentence = sentence.strip()
                    if sentence:
                        sentence = sentence[0].upper() + sentence[1:]
                    sentences[i] = sentence
            return ''.join(sentences)

        elif mode == "paragraph":
            # Capitalize first letter of each paragraph
            paragraphs = text.split('\n\n')
            formatted_paragraphs = []

            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if paragraph:
                    paragraph = paragraph[0].upper() + paragraph[1:]
                formatted_paragraphs.append(paragraph)

            return '\n\n'.join(formatted_paragraphs)

        return text

    async def _apply_punctuation_rules(self, text: str) -> str:
        """Apply punctuation formatting rules"""

        formatted = text

        # Fix double spaces after punctuation
        formatted = re.sub(r'([.!?])\s{2,}', r'\1 ', formatted)

        # Ensure proper spacing around commas
        formatted = re.sub(r'\s*,\s*', ', ', formatted)

        # Fix spacing before parentheses
        formatted = re.sub(r'\s*\(\s*', ' (', formatted)
        formatted = re.sub(r'\s*\)\s*', ') ', formatted)

        return formatted.strip()

    async def _apply_cross_section_formatting(
        self,
        content: Dict[str, str],
        config: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Apply formatting that spans multiple sections"""

        formatted = content.copy()

        # Ensure tone consistency
        formatted = await self._ensure_tone_consistency(formatted)

        # Apply final formatting touches
        formatted = await self._apply_final_touches(formatted)

        return formatted

    async def _ensure_tone_consistency(self, content: Dict[str, str]) -> Dict[str, str]:
        """Ensure consistent tone across all sections"""

        formatted = content.copy()

        # Analyze tone from opening
        opening = formatted.get("opening", "").lower()

        is_formal = any(word in opening for word in ["dear", "regards", "sincerely"])
        is_casual = any(word in opening for word in ["hi", "hey", "hello"])

        # Adjust closing to match opening tone
        closing = formatted.get("closing", "")
        if closing:
            if is_formal and not any(word in closing.lower() for word in ["regards", "sincerely"]):
                closing = closing.replace("Best,", "Best regards,")
                closing = closing.replace("Thanks,", "Best regards,")
            elif is_casual and any(word in closing.lower() for word in ["regards", "sincerely"]):
                closing = closing.replace("Best regards,", "Best,")
                closing = closing.replace("Sincerely,", "Best,")

            formatted["closing"] = closing

        return formatted

    async def _apply_final_touches(self, content: Dict[str, str]) -> Dict[str, str]:
        """Apply final formatting touches"""

        formatted = content.copy()

        # Ensure no empty sections
        for section_name, section_content in formatted.items():
            if not section_content or not section_content.strip():
                # Provide default content for critical sections
                if section_name == "subject":
                    formatted[section_name] = "Professional Connection"
                elif section_name == "call_to_action":
                    formatted[section_name] = "I look forward to hearing from you."

        return formatted

    async def validate_formatting(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Validate formatting quality and identify issues"""

        issues = []
        suggestions = []

        for section_name, section_content in content.items():
            if not section_content:
                continue

            # Check line length
            lines = section_content.split('\n')
            for i, line in enumerate(lines):
                if len(line) > 100:  # Too long for most email clients
                    issues.append({
                        "section": section_name,
                        "type": "line_too_long",
                        "line": i + 1,
                        "length": len(line)
                    })
                    suggestions.append(f"Consider shortening line {i + 1} in {section_name}")

            # Check for formatting issues
            if section_content != section_content.strip():
                issues.append({
                    "section": section_name,
                    "type": "extra_whitespace",
                    "message": "Extra whitespace at beginning or end"
                })
                suggestions.append(f"Trim whitespace in {section_name}")

            # Check paragraph structure
            if section_name == "body":
                paragraphs = section_content.split('\n\n')
                for i, paragraph in enumerate(paragraphs):
                    if len(paragraph.strip()) < 20:  # Very short paragraph
                        issues.append({
                            "section": section_name,
                            "type": "short_paragraph",
                            "paragraph": i + 1,
                            "length": len(paragraph.strip())
                        })
                        suggestions.append(f"Consider expanding or merging paragraph {i + 1}")

        return {
            "issues": issues,
            "suggestions": suggestions,
            "formatting_score": max(0.0, 1.0 - len(issues) * 0.1)
        }

    async def get_formatting_preview(
        self,
        content: Dict[str, str],
        outreach_type: str
    ) -> Dict[str, str]:
        """Get a preview of formatted content"""

        formatted = await self.format_message(content, outreach_type)

        # Create preview version
        preview = {}

        for section_name, section_content in formatted.items():
            if section_name == "body":
                # Show first few lines of body
                lines = section_content.split('\n')
                preview[section_name] = '\n'.join(lines[:3]) + ("\n..." if len(lines) > 3 else "")
            else:
                preview[section_name] = section_content

        return preview

__all__ = ["OutreachFormatter"]
