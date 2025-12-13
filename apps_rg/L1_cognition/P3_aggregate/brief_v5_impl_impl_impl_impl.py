"""Implementation for brief_v5_impl_impl_impl."""


class CreativeBriefValidator:
    """Validator for creative brief compliance."""

    def __init__(self, brief: RGCreativeBrief) -> None:
        """Initialize with a creative brief."""
        self.brief = brief

    def validate_headline(self, text: str) -> Dict[str, object]:
        """Validate headline against brief."""
        result: Dict[str, object] = {'is_valid': True, 'violations': [], 'metrics': {}}
        is_valid, message = self.brief.headline.word_count.validate(text)
        result['metrics']['word_count'] = len(text.split())
        if not is_valid:
            result['is_valid'] = False
            result['violations'].append(message)
        if len(text) > self.brief.headline.char_count_max:
            result['is_valid'] = False
            result['violations'].append(f'Character count {len(text)} exceeds max {self.brief.headline.char_count_max}')
        result['metrics']['char_count'] = len(text)
        if '|' not in text:
            result['violations'].append(f'Missing structure separators. Expected: {self.brief.headline.structure}')
        return result

    def validate_executive_summary(self, text: str) -> Dict[str, object]:
        """Validate executive summary against brief."""
        result: Dict[str, object] = {'is_valid': True, 'violations': [], 'metrics': {}}
        is_valid, message = self.brief.executive_summary.word_count.validate(text)
        result['metrics']['word_count'] = len(text.split())
        if not is_valid:
            result['is_valid'] = False
            result['violations'].append(message)
        for pattern in self.brief.executive_summary.forbidden_patterns:
            if pattern.lower() in text.lower():
                result['is_valid'] = False
                result['violations'].append(f'Forbidden pattern found: {pattern}')
        if self.brief.executive_summary.voice == VoiceType.THIRD_PERSON_IMPLIED:
            first_person_markers = ['I ', "I'm", "I've", 'my ', 'me ']
            for marker in first_person_markers:
                if marker.lower() in text.lower():
                    result['violations'].append(f'First person marker found: {marker.strip()}')
        return result

    def validate_bullet(self, text: str, section_key: str='k6') -> Dict[str, object]:
        """Validate a bullet against brief."""
        result: Dict[str, object] = {'is_valid': True, 'violations': [], 'metrics': {}}
        if section_key == 'k6':
            constraint = self.brief.experience_bullets.k6_word_count
        else:
            constraint = self.brief.experience_bullets.k7_word_count
        is_valid, message = constraint.validate(text)
        result['metrics']['word_count'] = len(text.split())
        if not is_valid:
            result['is_valid'] = False
            result['violations'].append(message)
        return result

    def validate_cover_letter_paragraph(self, text: str) -> Dict[str, object]:
        """Validate a cover letter paragraph against brief."""
        result: Dict[str, object] = {'is_valid': True, 'violations': [], 'metrics': {}}
        is_valid, message = self.brief.cover_letter.word_count_per_para.validate(text)
        result['metrics']['word_count'] = len(text.split())
        if not is_valid:
            result['is_valid'] = False
            result['violations'].append(message)
        for pattern in self.brief.cover_letter.forbidden_patterns:
            if pattern.lower() in text.lower():
                result['is_valid'] = False
                result['violations'].append(f'Forbidden pattern found: {pattern}')
        return result

    def validate_competency(self, text: str) -> Dict[str, object]:
        """Validate a competency description against brief."""
        result: Dict[str, object] = {'is_valid': True, 'violations': [], 'metrics': {}}
        is_valid, message = self.brief.leadership_competencies.word_count_per_desc.validate(text)
        result['metrics']['word_count'] = len(text.split())
        if not is_valid:
            result['is_valid'] = False
            result['violations'].append(message)
        return result

def create_creative_brief() -> RGCreativeBrief:
    """builder function to create a default creative brief."""
    return RGCreativeBrief()

def create_brief_validator(brief: Optional[RGCreativeBrief]=None) -> CreativeBriefValidator:
    """builder function to create a brief validator."""
    if brief is None:
        brief = RGCreativeBrief()
    return CreativeBriefValidator(brief)

def get_headline_brief() -> HeadlineBrief:
    """Get default headline brief."""
    return HeadlineBrief()

def get_executive_summary_brief() -> ExecutiveSummaryBrief:
    """Get default executive summary brief."""
    return ExecutiveSummaryBrief()

def get_experience_bullets_brief() -> ExperienceBulletsBrief:
    """Get default experience bullets brief."""
    return ExperienceBulletsBrief()
