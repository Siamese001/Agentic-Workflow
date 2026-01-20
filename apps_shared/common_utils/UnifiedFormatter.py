"""Unified Formatter - Shared formatting module for all engines.

This module provides a unified formatting system that both resume and outreach
engines can use, eliminating the need for separate format_* modules.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .signal_infrastructure import EngineType

logger = logging.getLogger(__name__)


class FormatType(Enum):
    """Types of formatting."""
    DEFAULT = "default"
    RESUME_BULLET = "resume_bullet"
    RESUME_SECTION = "resume_section"
    OUTREACH_MESSAGE = "outreach_message"
    OUTREACH_SUBJECT = "outreach_subject"
    JSON = "json"
    XML = "xml"


@dataclass
class FormatResult:
    """Result of formatting operation."""
    
    data: Any
    format_type: str
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "format_type": self.format_type,
            "success": self.success,
            "metadata": self.metadata,
            "errors": self.errors
        }


class FormatterStrategy(ABC):
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
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get format name."""
        pass


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
                formatted = data.strip()
            elif isinstance(data, dict):
                formatted = json.dumps(data, indent=2)
            else:
                formatted = str(data)
            
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"original_type": type(data).__name__}
            )
        except Exception as e:
            return FormatResult(
                data=data,
                format_type=self.format_name,
                success=False,
                errors=[str(e)]
            )
    
    @property
    def format_name(self) -> str:
        """Get format name."""
        return "default"


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
                bullets = self._format_text_to_bullets(data)
            elif isinstance(data, list):
                bullets = self._format_list_to_bullets(data)
            else:
                bullets = [str(data)]
            
            # Apply configuration
            if config:
                bullets = self._apply_config(bullets, config)
            
            return FormatResult(
                data=bullets,
                format_type=self.format_name,
                metadata={"bullet_count": len(bullets)}
            )
        except Exception as e:
            return FormatResult(
                data=data,
                format_type=self.format_name,
                success=False,
                errors=[str(e)]
            )
    
    def _format_text_to_bullets(self, text: str) -> List[str]:
        """Format text to bullet points.
        
        Args:
            text: Text to format
            
        Returns:
            List of bullet points
        """
        # Split by sentences or newlines
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        bullets = []
        for sentence in sentences:
            # Ensure it starts with action verb
            if not any(sentence.startswith(verb) for verb in ["Led", "Managed", "Developed", "Created", "Implemented"]):
                sentence = "• " + sentence
            elif not sentence.startswith('•'):
                sentence = "• " + sentence
            
            bullets.append(sentence)
        
        return bullets[:5]  # Limit to 5 bullets
    
    def _format_list_to_bullets(self, items: List[Any]) -> List[str]:
        """Format list to bullet points.
        
        Args:
            items: List of items
            
        Returns:
            List of bullet points
        """
        bullets = []
        for item in items:
            bullet = "• " + str(item).strip()
            if not bullet.endswith('.'):
                bullet += '.'
            bullets.append(bullet)
        
        return bullets
    
    def _apply_config(self, bullets: List[str], config: Dict) -> List[str]:
        """Apply configuration to bullets.
        
        Args:
            bullets: List of bullets
            config: Configuration
            
        Returns:
            Modified bullets
        """
        if config.get("ensure_metrics", False):
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
        if any(char.isdigit() for char in bullet):
            return bullet
        
        # Add placeholder for metrics
        if bullet.endswith('.'):
            return bullet[:-1] + " (achieving X% improvement)."
        return bullet + " (achieving X% improvement)."
    
    @property
    def format_name(self) -> str:
        """Get format name."""
        return "resume_bullet"


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
                formatted = self._format_dict_section(data, config)
            else:
                formatted = self._format_text_section(str(data), config)
            
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"section_type": config.get("section_type", "general")}
            )
        except Exception as e:
            return FormatResult(
                data=data,
                format_type=self.format_name,
                success=False,
                errors=[str(e)]
            )
    
    def _format_dict_section(self, data: Dict, config: Optional[Dict]) -> Dict:
        """Format dictionary section.
        
        Args:
            data: Section data
            config: Configuration
            
        Returns:
            Formatted section
        """
        section_type = config.get("section_type", "general") if config else "general"
        
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
        if "title" not in data:
            data["title"] = "Professional Experience"
        if "duration" not in data:
            data["duration"] = "Present"
        
        return data
    
    def _format_skills_section(self, data: Dict) -> Dict:
        """Format skills section.
        
        Args:
            data: Skills data
            
        Returns:
            Formatted skills
        """
        if "skills" in data and isinstance(data["skills"], list):
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
        technical_keywords = ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes"]
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
        if config and "section_title" in config:
            text = f"{config['section_title']}\n\n{text}"
        
        return text
    
    @property
    def format_name(self) -> str:
        """Get format name."""
        return "resume_section"


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
                formatted = self._format_message_text(data, config)
            elif isinstance(data, dict):
                formatted = self._format_message_dict(data, config)
            else:
                formatted = str(data)
            
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"message_length": len(str(formatted))}
            )
        except Exception as e:
            return FormatResult(
                data=data,
                format_type=self.format_name,
                success=False,
                errors=[str(e)]
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
        if not any(greeting in text.lower() for greeting in ["dear", "hi ", "hello"]):
            text = "Dear " + (config.get("recipient_name", "Hiring Manager") if config else "Hiring Manager") + ",\n\n" + text
        
        # Ensure proper closing
        if not any(closing in text.lower() for closing in ["sincerely", "regards", "best"]):
            text += "\n\nBest regards,\n[Your Name]"
        
        # Check length
        max_length = config.get("max_length", 500) if config else 500
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
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
        if "greeting" not in data:
            data["greeting"] = "Dear Hiring Manager,"
        if "body" not in data:
            data["body"] = ""
        if "closing" not in data:
            data["closing"] = "Best regards,"
        
        return data
    
    @property
    def format_name(self) -> str:
        """Get format name."""
        return "outreach_message"


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
                formatted = self._format_subject_text(data, config)
            else:
                formatted = str(data)
            
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"subject_length": len(formatted)}
            )
        except Exception as e:
            return FormatResult(
                data=data,
                format_type=self.format_name,
                success=False,
                errors=[str(e)]
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
        text = text[0].upper() + text[1:] if text else text
        
        # Remove trailing periods
        text = text.rstrip('.')
        
        # Check length
        max_length = config.get("max_length", 50) if config else 50
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text
    
    @property
    def format_name(self) -> str:
        """Get format name."""
        return "outreach_subject"


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
                    parsed = json.loads(data)
                except Exception:
                    parsed = {"text": data}
            else:
                parsed = data
            
            # Format with indentation
            indent = config.get("indent", 2) if config else 2
            formatted = json.dumps(parsed, indent=indent, default=str)
            
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"json_keys": len(parsed) if isinstance(parsed, dict) else 0}
            )
        except Exception as e:
            return FormatResult(
                data=data,
                format_type=self.format_name,
                success=False,
                errors=[str(e)]
            )
    
    @property
    def format_name(self) -> str:
        """Get format name."""
        return "json"


class UnifiedFormatter:
    """Unified formatter for all engines."""
    
    def __init__(self):
        """Initialize the unified formatter."""
        self.strategies = {
            FormatType.DEFAULT: DefaultFormatter(),
            FormatType.RESUME_BULLET: ResumeBulletFormatter(),
            FormatType.RESUME_SECTION: ResumeSectionFormatter(),
            FormatType.OUTREACH_MESSAGE: OutreachMessageFormatter(),
            FormatType.OUTREACH_SUBJECT: OutreachSubjectFormatter(),
            FormatType.JSON: JSONFormatter()
        }
        
        logger.info("Initialized UnifiedFormatter")
    
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
        if isinstance(format_type, str):
            try:
                format_type = FormatType(format_type.lower())
            except ValueError:
                format_type = FormatType.DEFAULT
        
        # Get strategy
        strategy = self.strategies.get(format_type, self.strategies[FormatType.DEFAULT])
        
        # Add engine context to config
        if engine_type and config is None:
            config = {"engine": engine_type.value}
        elif engine_type and config:
            config["engine"] = engine_type.value
        
        # Format data
        result = strategy.format(data, config)
        
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
        self.strategies[format_type] = strategy
        logger.info(f"Registered custom strategy for {format_type.value}")
    
    def get_available_formats(self) -> List[str]:
        """Get list of available format types.
        
        Returns:
            List of format type names
        """
        return [ft.value for ft in self.strategies.keys()]


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
def format_data(
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
    formatter = get_unified_formatter()
    return formatter.format(data, format_type, engine_type, config)


def format_resume_bullets(data: Union[str, List], config: Optional[Dict] = None) -> FormatResult:
    """Format resume bullet points.
    
    Args:
        data: Bullet data
        config: Optional configuration
        
    Returns:
        Format result
    """
    return format_data(data, FormatType.RESUME_BULLET, EngineType.RESUME, config)


def format_outreach_message(data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
    """Format outreach message.
    
    Args:
        data: Message data
        config: Optional configuration
        
    Returns:
        Format result
    """
    return format_data(data, FormatType.OUTREACH_MESSAGE, EngineType.OUTREACH, config)
