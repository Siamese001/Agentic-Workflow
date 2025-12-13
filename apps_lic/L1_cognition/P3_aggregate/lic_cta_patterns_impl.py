"""Implementation for lic_cta_patterns."""

from typing import Any, Dict, List, Optional
from .lic_cta_patterns_types import *

class DateWindowEngine:
    """Engine for generating date windows for CTAs."""

    def __init__(self, config: Optional[DateWindowConfig]=None) -> None:
        """Initialize the date window engine."""
        self.config = config or DateWindowConfig()
        self._holidays = {h.date() for h in US_HOLIDAYS_2025}

    def generate_date_window(self, from_date: Optional[datetime]=None, num_dates: int=3) -> List[datetime]:
        """
        Generate a window of available dates.

        Args:
            from_date: Starting date (defaults to today)
            num_dates: Number of dates to generate

        Returns:
            List of available dates
        """
        if from_date is None:
            from_date = datetime.now()
        day_name = from_date.strftime('%A')
        buffer_config = DAY_BUFFER_MAP.get(day_name, DayBufferConfig(min_buffer_days=2, suggested_pattern=''))
        current_date = from_date + timedelta(days=buffer_config.min_buffer_days)
        available_dates: List[datetime] = []
        max_attempts = 14
        attempts = 0
        while len(available_dates) < num_dates and attempts < max_attempts:
            if self._is_available_date(current_date):
                available_dates.append(current_date)
            current_date += timedelta(days=1)
            attempts += 1
        return available_dates

    def format_date_window(self, dates: List[datetime], format_style: str='natural') -> str:
        """
        Format a date window as a string.

        Args:
            dates: List of dates
            format_style: "natural" or "numeric"

        Returns:
            Formatted date window string
        """
        if not dates:
            return 'next week'
        if format_style == 'numeric':
            formatted = [d.strftime('%m/%d') for d in dates]
        else:
            formatted = [d.strftime('%a %b %d') for d in dates]
        if len(formatted) == 1:
            return formatted[0]
        elif len(formatted) == 2:
            return f'{formatted[0]} or {formatted[1]}'
        else:
            return f"{', '.join(formatted[:-1])}, or {formatted[-1]}"

    def _is_available_date(self, date: datetime) -> bool:
        """Check if a date is available (not weekend or holiday)."""
        if self.config.avoid_weekends and date.weekday() >= 5:
            return False
        if self.config.avoid_holidays and date.date() in self._holidays:
            return False
        return True

class CTAGenerator:
    """Generator for call-to-action text."""

    def __init__(self) -> None:
        """Initialize the CTA generator."""
        self._patterns = CTA_PATTERNS
        self._templates = CTA_TEMPLATES
        self._date_engine = DateWindowEngine()

    def get_pattern(self, archetype: RecipientArchetype) -> CTAPattern:
        """Get CTA pattern for an archetype."""
        return self._patterns.get(archetype, self._patterns[RecipientArchetype.EXECUTIVE])

    def get_template(self, route: str) -> CTATemplate:
        """Get CTA template for a route."""
        return self._templates.get(route, self._templates['SHORT_NEW'])

    def generate_date_window(self, from_date: Optional[datetime]=None, num_dates: int=3) -> str:
        """Generate a formatted date window."""
        dates = self._date_engine.generate_date_window(from_date, num_dates)
        return self._date_engine.format_date_window(dates)

    def generate_cta(self, route: str, archetype: RecipientArchetype, topic: Optional[str]=None, include_date_window: bool=True) -> Dict[str, object]:
        """
        Generate a CTA based on route and archetype.

        Args:
            route: Message route
            archetype: Recipient archetype
            topic: Optional topic for the CTA
            include_date_window: Whether to include date window

        Returns:
            Dictionary with CTA components
        """
        template = self.get_template(route)
        pattern = self.get_pattern(archetype)
        result: Dict[str, object] = {'template': template.template, 'pattern': pattern, 'verbs': pattern.verbs, 'tone': pattern.tone, 'formality': pattern.formality}
        if include_date_window:
            result['date_window'] = self.generate_date_window()
        if topic:
            result['topic'] = topic
        if template.word_limit:
            result['word_limit'] = template.word_limit
        if template.examples:
            result['examples'] = template.examples
        return result

    def validate_cta(self, cta_text: str, route: str) -> Dict[str, object]:
        """
        Validate a CTA against route requirements.

        Args:
            cta_text: CTA text to validate
            route: Message route

        Returns:
            Validation result dictionary
        """
        template = self.get_template(route)
        result: Dict[str, object] = {'is_valid': True, 'violations': [], 'word_count': len(cta_text.split())}
        if template.word_limit:
            word_count = len(cta_text.split())
            if word_count > template.word_limit:
                result['is_valid'] = False
                result['violations'].append(f'Word count {word_count} exceeds limit {template.word_limit}')
        if '?' not in cta_text:
            result['violations'].append('CTA should end with a question mark')
        return result

def create_cta_generator() -> CTAGenerator:
    """builder function to create a CTA generator."""
    return CTAGenerator()

def create_date_window_engine(config: Optional[DateWindowConfig]=None) -> DateWindowEngine:
    """builder function to create a date window engine."""
    return DateWindowEngine(config)

def get_cta_pattern(archetype: RecipientArchetype) -> CTAPattern:
    """Get CTA pattern for an archetype."""
    return CTA_PATTERNS.get(archetype, CTA_PATTERNS[RecipientArchetype.EXECUTIVE])

