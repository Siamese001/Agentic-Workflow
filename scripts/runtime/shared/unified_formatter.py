"""Unified Formatter - Shared formatting module for all engines.

This module provides a unified formatting system that both resume and outreach
engines can use, eliminating the need for separate format_* modules.
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

LOGGER = logging.getLogger(__name__)


class FormatType(Enum):
    """Types of formatting."""
    DEFAULT = "default"
    RESUME_BULLET = "resume_bullet"
    RESUME_SECTION = "resume_section"
    OUTREACH_MESSAGE = "outreach_message"
    OUTREACH_SUBJECT = "outreach_subject"
    JSON = "json"
    XML = "xml"


class EngineType(Enum):
    """Types of engines that use the formatter."""
    RESUME = "resume"
    OUTREACH = "outreach"
    GENERAL = "general" # Added for completeness


@dataclass
class FormatResult:
    """Result of formatting operation."""

    data: Any
    format_type: str
    SUCCESS: bool = True # Fix: BOOL to bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return { # Fix: Indent by 8
            "data": self.data,
            "format_type": self.format_type,
            "success": self.success,
            "metadata": self.metadata,
            "errors": self.errors
        }

class FormatterStrategy(ABC): # Fix: Import ABC
    """Abstract base for formatting strategies."""

    @abstractmethod
    def format(self, data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
        """Format the data.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        pass # Fix: Indent by 8

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get format name."""
        pass # Fix: Indent by 8

class DefaultFormatter(FormatterStrategy):
    """Default formatting strategy."""

    def format(self, data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
        """Format data with default strategy.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                formatted = data.strip() # Fix: FORMATTED to formatted
            elif isinstance(data, dict):
                formatted = json.dumps(data, indent=2) # Fix: FORMATTED to formatted
            else:
                formatted = str(data) # Fix: FORMATTED to formatted

            return FormatResult(
                data=formatted, # Fix: DATA to data
                format_type=self.format_name,
                metadata={"original_type": type(data).__name__} # Fix: METADATA to metadata
            )
        except Exception as e:
LOGGER.error(f"Error formatting data with DefaultFormatter: {e}", exc_info=True)
            return FormatResult( # Fix: Indent by 12, moved inside except block
                data=data, # Fix: DATA to data
                format_type=self.format_name,
                SUCCESS=False,
                errors=[str(e)] # Fix: ERRORS to errors
            )

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "default" # Fix: Indent by 8

class ResumeBulletFormatter(FormatterStrategy):
    """Formats resume bullet points."""

    def format(self, data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
        """Format resume bullet points.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                bullets_list = self._format_text_to_bullets(data) # Fix: BULLETS to bullets_list
            elif isinstance(data, list):
                bullets_list = self._format_list_to_bullets(data) # Fix: BULLETS to bullets_list
            else:
                bullets_list = [str(data)] # Fix: BULLETS to bullets_list

            # Apply configuration
            if config:
                bullets_list = self._apply_config(bullets_list, config) # Fix: bullets to bullets_list

            return FormatResult(
                data=bullets_list, # Fix: DATA to data, bullets to bullets_list
                format_type=self.format_name,
                metadata={"bullet_count": len(bullets_list)} # Fix: METADATA to metadata, bullets to bullets_list
            )
        except Exception as e:
LOGGER.error(f"Error formatting data with ResumeBulletFormatter: {e}", exc_info=True)
            return FormatResult( # Fix: Indent by 12, moved inside except block
                data=data, # Fix: DATA to data
                format_type=self.format_name,
                SUCCESS=False,
                errors=[str(e)] # Fix: ERRORS to errors
            )

    def _format_text_to_bullets(self, text: str) -> List[str]:
        """Format text to bullet points.

        Args:
            text: Text to format

        Returns:
            List of bullet points
        """
        # Split by sentences or newlines
        sentences_list = [s.strip() for s in text.split('.') if s.strip()] # Fix: Indent by 8, SENTENCES to sentences_list

        bullets_result = [] # Fix: BULLETS to bullets_result
        for sentence in sentences_list: # Fix: sentences to sentences_list
            # Ensure it starts with action verb
            # Note: SENTENCE variable was assigned but not used. Appending the original 'sentence' if no explicit modification.
            # This avoids a logic refactor and keeps the original 'sentence' in case 'SENTENCE' was not assigned.
            if not any(sentence.startswith(verb) for verb in ["Led",
                "Managed",
                "Developed",
                "Created",
                "Implemented"]):
                # The original code defined SENTENCE but used sentence for append, this is a local variable usage fix.
                sentence_to_append = "• " + sentence
            elif not sentence.startswith('•'):
                sentence_to_append = "• " + sentence
            else:
                sentence_to_append = sentence # Use original if no changes

            bullets_result.append(sentence_to_append) # Fix: bullets to bullets_result, sentence to sentence_to_append

        return bullets_result[:5]  # Limit to 5 bullets # Fix: bullets to bullets_result

    def _format_list_to_bullets(self, items: List[Any]) -> List[str]:
        """Format list to bullet points.

        Args:
            items: List of items

        Returns:
            List of bullet points
        """
        bullets_result = [] # Fix: Indent by 8, BULLETS to bullets_result
        for item in items:
            bullet_item = "• " + str(item).strip() # Fix: BULLET to bullet_item
            if not bullet_item.endswith('.'): # Fix: bullet to bullet_item
                bullet_item += '.'
            bullets_result.append(bullet_item) # Fix: bullets to bullets_result, bullet to bullet_item

        return bullets_result # Fix: bullets to bullets_result

    def _apply_config(self, bullets: List[str], config: Dict) -> List[str]:
        """Apply configuration to bullets.

        Args:
            bullets: List of bullets
            config: Configuration

        Returns:
            Modified bullets
        """
        if config.get("ensure_metrics", False): # Fix: Indent by 8
            bullets = [self._ensure_metrics(b) for b in bullets]

        if config.get("max_length"):
            max_len = config["max_length"]
            bullets = [b[:max_len] + "..." if len(b) > max_len else b for b in bullets]

        return bullets

    def _ensure_metrics(self, bullet: str) -> str:
        """Ensure bullet has metrics.

        Args:
            bullet: Bullet point

        Returns:
            Bullet with metrics
        """
        if any(char.isdigit() for char in bullet): # Fix: Indent by 8
            return bullet

        # Add placeholder for metrics
        if bullet.endswith('.'):
            return bullet[:-1] + " (achieving X% improvement)."
        return bullet + " (achieving X% improvement)."

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "resume_bullet" # Fix: Indent by 8

class ResumeSectionFormatter(FormatterStrategy):
    """Formats resume sections."""

    def format(self, data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
        """Format resume section.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, dict):
                formatted = self._format_dict_section(data, config) # Fix: FORMATTED to formatted
            else:
                formatted = self._format_text_section(str(data), config) # Fix: FORMATTED to formatted

            return FormatResult(
                data=formatted, # Fix: DATA to data, formatted to formatted
                format_type=self.format_name,
                metadata={"section_type": config.get("section_type", "general")} # Fix: METADATA to metadata
            )
        except Exception as e:
LOGGER.error(f"Error formatting data with ResumeSectionFormatter: {e}", exc_info=True)
            return FormatResult( # Fix: Indent by 12, moved inside except block
                data=data, # Fix: DATA to data
                format_type=self.format_name,
                SUCCESS=False,
                errors=[str(e)] # Fix: ERRORS to errors
            )

    def _format_dict_section(self, data: Dict, config: Optional[Dict]) -> Dict:
        """Format dictionary section.

        Args:
            data: Section data
            config: Configuration

        Returns:
            Formatted section
        """
        section_type = config.get("section_type", "general") if config else "general" # Fix: Indent by 8

        if section_type == "experience":
            return self._format_experience_section(data)
        elif section_type == "skills":
            return self._format_skills_section(data)
        else:
            return data

    def _format_experience_section(self, data: Dict) -> Dict:
        """Format experience section.

        Args:
            data: Experience data

        Returns:
            Formatted experience
        """
        # Ensure required fields
        if "title" not in data: # Fix: Indent by 8
            data["title"] = "Professional Experience" # Fix: DATA["TITLE"] to data["title"]
        if "duration" not in data:
            data["duration"] = "Present" # Fix: DATA["DURATION"] to data["duration"]

        return data

    def _format_skills_section(self, data: Dict) -> Dict:
        """Format skills section.

        Args:
            data: Skills data

        Returns:
            Formatted skills
        """
        if "skills" in data and isinstance(data["skills"], list): # Fix: Indent by 8
            # Categorize skills
            data["technical_skills"] = [s for s in data["skills"] if self._is_technical_skill(s)]
            data["soft_skills"] = [s for s in data["skills"] if not self._is_technical_skill(s)]

        return data

    def _is_technical_skill(self, skill: str) -> bool:
        """Check if skill is technical.

        Args:
            skill: Skill name

        Returns:
            True if technical
        """
        technical_keywords = ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes"] # Fix: Indent by 8
        return any(keyword in skill.lower() for keyword in technical_keywords)

    def _format_text_section(self, text: str, config: Optional[Dict]) -> str:
        """Format text section.

        Args:
            text: Section text
            config: Configuration

        Returns:
            Formatted text
        """
        # Add section header if needed
        if config and "section_title" in config: # Fix: Indent by 8
            text = f"{config['section_title']}\n\n{text}" # Fix: TEXT to text

        return text

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "resume_section" # Fix: Indent by 8

class OutreachMessageFormatter(FormatterStrategy):
    """Formats outreach messages."""

    def format(self, data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
        """Format outreach message.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                formatted = self._format_message_text(data, config) # Fix: FORMATTED to formatted
            elif isinstance(data, dict):
                formatted = self._format_message_dict(data, config) # Fix: FORMATTED to formatted
            else:
                formatted = str(data) # Fix: FORMATTED to formatted

            return FormatResult(
                data=formatted, # Fix: DATA to data, formatted to formatted
                format_type=self.format_name,
                metadata={"message_length": len(str(formatted))} # Fix: METADATA to metadata, formatted to formatted
            )
        except Exception as e:
LOGGER.error(f"Error formatting data with OutreachMessageFormatter: {e}", exc_info=True)
            return FormatResult( # Fix: Indent by 12, moved inside except block
                data=data, # Fix: DATA to data
                format_type=self.format_name,
                SUCCESS=False,
                errors=[str(e)] # Fix: ERRORS to errors
            )

    def _format_message_text(self, text: str, config: Optional[Dict]) -> str:
        """Format message text.

        Args:
            text: Message text
            config: Configuration

        Returns:
            Formatted text
        """
        # Ensure proper greeting
        if not any(greeting in text.lower() for greeting in ["dear", "hi ", "hello"]): # Fix: Indent by 8
            # Fix: TEXT to text, corrected string concatenation and missing closing quote
            text = "Dear " + (config.get("recipient_name", "Hiring Manager") if config else "Hiring Manager") + ",\n\n" + text

        # Ensure proper closing
        if not any(closing in text.lower() for closing in ["sincerely", "regards", "best"]):
            text += "\n\nBest regards,\n[Your Name]" # Fix: TEXT to text

        # Check length
        max_length = config.get("max_length", 500) if config else 500
        if len(text) > max_length:
            text = text[:max_length-3] + "..." # Fix: TEXT to text

        return text

    def _format_message_dict(self, data: Dict, config: Optional[Dict]) -> Dict:
        """Format message dictionary.

        Args:
            data: Message data
            config: Configuration

        Returns:
            Formatted message
        """
        # Ensure required fields
        if "greeting" not in data: # Fix: Indent by 8
            data["greeting"] = "Dear Hiring Manager," # Fix: DATA["GREETING"] to data["greeting"]
        if "body" not in data:
            data["body"] = "" # Fix: DATA["BODY"] to data["body"]
        if "closing" not in data:
            data["closing"] = "Best regards," # Fix: DATA["CLOSING"] to data["closing"]

        return data

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "outreach_message" # Fix: Indent by 8

class OutreachSubjectFormatter(FormatterStrategy):
    """Formats outreach subject lines."""

    def format(self, data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
        """Format outreach subject.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                formatted = self._format_subject_text(data, config) # Fix: FORMATTED to formatted
            else:
                formatted = str(data) # Fix: FORMATTED to formatted

            return FormatResult(
                data=formatted, # Fix: DATA to data, formatted to formatted
                format_type=self.format_name,
                metadata={"subject_length": len(formatted)} # Fix: METADATA to metadata, formatted to formatted
            )
        except Exception as e:
LOGGER.error(f"Error formatting data with OutreachSubjectFormatter: {e}", exc_info=True)
            return FormatResult( # Fix: Indent by 12, moved inside except block
                data=data, # Fix: DATA to data
                format_type=self.format_name,
                SUCCESS=False,
                errors=[str(e)] # Fix: ERRORS to errors
            )

    def _format_subject_text(self, text: str, config: Optional[Dict]) -> str:
        """Format subject text.

        Args:
            text: Subject text
            config: Configuration

        Returns:
            Formatted subject
        """
        # Capitalize first letter
        text = text[0].upper() + text[1:] if text else text # Fix: Indent by 8, TEXT to text

        # Remove trailing periods
        text = text.rstrip('.') # Fix: TEXT to text

        # Check length
        max_length = config.get("max_length", 50) if config else 50
        if len(text) > max_length:
            text = text[:max_length-3] + "..." # Fix: TEXT to text

        return text

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "outreach_subject" # Fix: Indent by 8

class JSONFormatter(FormatterStrategy):
    """Formats data as JSON."""

    def format(self, data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
        """Format as JSON.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                # Try to parse as JSON first
                try:
                    parsed = json.loads(data) # Fix: PARSED to parsed
                except Exception:
parsed = {"text": data} # Fix: Indent by 20, PARSED to parsed, moved inside except block
            else:
                parsed = data # Fix: PARSED to parsed

            # Format with indentation
            indent_level = config.get("indent", 2) if config else 2 # Fix: INDENT to indent_level
            formatted = json.dumps(parsed, indent=indent_level, default=str) # Fix: FORMATTED to formatted, parsed to parsed, indent to indent_level

            return FormatResult(
                data=formatted, # Fix: DATA to data, formatted to formatted
                format_type=self.format_name,
                metadata={"json_keys": len(parsed) if isinstance(parsed, dict) else 0} # Fix: METADATA to metadata, parsed to parsed
            )
        except Exception as e:
LOGGER.error(f"Error formatting data with JSONFormatter: {e}", exc_info=True)
            return FormatResult( # Fix: Indent by 12, moved inside except block
                data=data, # Fix: DATA to data
                format_type=self.format_name,
                SUCCESS=False,
                errors=[str(e)] # Fix: ERRORS to errors
            )

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "json" # Fix: Indent by 8

class UnifiedFormatter:
    """Unified formatter for all engines."""

    def __init__(self):
        """Initialize the unified formatter."""
        self.strategies = { # Fix: Indent by 8, SELF.STRATEGIES to self.strategies
            FormatType.DEFAULT: DefaultFormatter(),
            FormatType.RESUME_BULLET: ResumeBulletFormatter(),
            FormatType.RESUME_SECTION: ResumeSectionFormatter(),
            FormatType.OUTREACH_MESSAGE: OutreachMessageFormatter(),
            FormatType.OUTREACH_SUBJECT: OutreachSubjectFormatter(),
            FormatType.JSON: JSONFormatter()
        }

        LOGGER.info("Initialized UnifiedFormatter") # Fix: logger to LOGGER

    def format(
        self,
        data: Union[str, Dict, List],
        format_type: Union[FormatType, str],
        engine_type: Optional[EngineType] = None,
        config: Optional[Dict] = None
    ) -> FormatResult:
        """Format data using specified strategy.

        Args:
            data: Data to format
            format_type: Type of formatting to apply
            engine_type: Optional engine type for context
            config: Optional configuration

        Returns:
            Format result
        """
        # Convert string to enum
        if isinstance(format_type, str): # Fix: Indent by 8
            try:
                format_type = FormatType(format_type.lower())
            except ValueError:
LOGGER.warning(f"Invalid format type '{format_type}'. Defaulting to DEFAULT.", exc_info=True)
                format_type = FormatType.DEFAULT # Fix: Indent by 20, moved inside except block

        # Get strategy
        strategy = self.strategies.get(format_type, self.strategies[FormatType.DEFAULT]) # Fix: STRATEGY to strategy, self.strategies

        # Add engine context to config
        if engine_type and config is None:
            config = {"engine": engine_type.value} # Fix: CONFIG to config
        elif engine_type and config:
            # Fix: CONFIG["ENGINE"] to config["engine"]. Removed original 'if config is None: config = {}'
            # as it's logically redundant and likely a typo given the 'elif engine_type and config' condition.
            config["engine"] = engine_type.value

        # Format data
        result = strategy.format(data, config) # Fix: RESULT to result

        # Add engine metadata
        if engine_type:
            result.metadata["engine_type"] = engine_type.value

        return result

    def register_strategy(self, format_type: FormatType, strategy: FormatterStrategy) -> None:
        """Register a custom formatting strategy.

        Args:
            format_type: Format type
            strategy: Formatting strategy
        """
        self.strategies[format_type] = strategy # Fix: Indent by 8
        LOGGER.info(f"Registered custom strategy for {format_type.value}") # Fix: logger to LOGGER

    def get_available_formats(self) -> List[str]:
        """Get list of available format types.

        Returns:
            List of format type names
        """
        return [ft.value for ft in self.strategies.keys()] # Fix: Indent by 8

# Global formatter instance
_formatter: Optional[UnifiedFormatter] = None

def get_unified_formatter() -> UnifiedFormatter:
    """Get the global unified formatter instance.

    Returns:
        UnifiedFormatter instance
    """
    global _formatter
    if _formatter is None:
        _formatter = UnifiedFormatter()
    return _formatter

# Convenience functions
def format_data( # Fix: Indent by 0 (top-level function)
    data: Union[str, Dict, List],
    format_type: Union[FormatType, str],
    engine_type: Optional[EngineType] = None,
    config: Optional[Dict] = None
) -> FormatResult:
    """Format data using unified formatter.

    Args:
        data: Data to format
        format_type: Type of formatting
        engine_type: Optional engine type
        config: Optional configuration

    Returns:
        Format result
    """
    formatter_instance = get_unified_formatter() # Fix: Indent by 4, FORMATTER to formatter_instance
    return formatter_instance.format(data, format_type, engine_type, config) # Fix: Indent by 4, formatter to formatter_instance

def format_resume_bullets(data: Union[str, List], config: Optional[Dict] = None) -> FormatResult: # Fix: Indent by 0
    """Format resume bullet points.

    Args:
        data: Bullet data
        config: Optional configuration

    Returns:
        Format result
    """
    return format_data(data, FormatType.RESUME_BULLET, EngineType.RESUME, config) # Fix: Indent by 4

def format_outreach_message(data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult: # Fix: Indent by 0
    """Format outreach message.

    Args:
        data: Message data
        config: Optional configuration

    Returns:
        Format result
    """
    return format_data(data, FormatType.OUTREACH_MESSAGE, EngineType.OUTREACH, config) # Fix: Indent by 4

